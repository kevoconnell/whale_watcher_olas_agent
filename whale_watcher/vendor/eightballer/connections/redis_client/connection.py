# ------------------------------------------------------------------------------
#
#   Copyright 2024 eightballer
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------

"""Redis connection and channel."""

import asyncio
import logging
from abc import abstractmethod
from typing import Any, Optional, cast
from asyncio.events import AbstractEventLoop
from collections.abc import Callable

import redis.asyncio as redis
from aea.common import Address
from aea.mail.base import Message, Envelope
from aea.connections.base import Connection, ConnectionStates
from aea.configurations.base import PublicId
from aea.protocols.dialogue.base import Dialogue

from packages.eightballer.protocols.pubsub.message import PubsubMessage
from packages.eightballer.protocols.pubsub.dialogues import (
    PubsubDialogue,
    BasePubsubDialogues,
)


CONNECTION_ID = PublicId.from_str("eightballer/redis_client:0.1.0")


_default_logger = logging.getLogger("aea.packages.eightballer.connections.redis_client")


class PubsubDialogues(BasePubsubDialogues):
    """The dialogues class keeps track of all redis dialogues."""

    def __init__(self, self_address: Address, **kwargs) -> None:
        """Initialize dialogues.

        :param self_address: self address
        :param kwargs: keyword arguments
        """

        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> Dialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message.

            :param message: an incoming/outgoing first message
            :param receiver_address: the address of the receiving agent
            :return: The role of the agent
            """
            assert message, receiver_address
            return PubsubDialogue.Role.PUBLISHER  # TODO: check  # noqa

        BasePubsubDialogues.__init__(
            self,
            self_address=self_address,
            role_from_first_message=role_from_first_message,
            **kwargs,
        )


class BaseAsyncChannel:
    """BaseAsyncChannel."""

    def __init__(
        self,
        agent_address: Address,
        connection_id: PublicId,
        message_type: Message,
    ):
        """Initialize the BaseAsyncChannel channel.

        :param agent_address: the address of the agent.
        :param connection_id: the id of the connection.
        :param message_type: the associated message type.
        """

        self.agent_address = agent_address
        self.connection_id = connection_id
        self.message_type = message_type

        self.is_stopped = True
        self._connection = None
        self._tasks: set[asyncio.Task] = set()
        self._in_queue: asyncio.Queue | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self.logger = _default_logger
        self._subscriptions = {}
        self._dialogues = None
        self._pubsub = None
        self.target_skill_id = None

    @property
    @abstractmethod
    def performative_handlers(
        self,
    ) -> dict[Message.Performative, Callable[[Message, Dialogue], Message]]:
        """Performative to message handler mapping."""

    @abstractmethod
    async def connect(self, loop: AbstractEventLoop) -> None:
        """Connect channel using loop."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect channel."""

    async def send(self, envelope: Envelope) -> None:
        """Send an envelope with a protocol message.

        It sends the envelope, waits for and receives the result.
        The result is translated into a response envelope.
        Finally, the response envelope is sent to the in-queue.

        :param query_envelope: The envelope containing a protocol message.
        """

        if not (self._loop and self._connection):
            msg = "{self.__class__.__name__} not connected, call connect first!"
            raise ConnectionError(msg)

        if not isinstance(envelope.message, self.message_type):
            msg = f"Message not of type {self.message_type}"
            raise TypeError(msg)

        message = envelope.message

        if message.performative not in self.performative_handlers:
            log_msg = "Message with unexpected performative `{message.performative}` received."
            self.logger.error(log_msg)
            return

        handler = self.performative_handlers[message.performative]

        dialogue = cast(Dialogue, self._dialogues.update(message))
        if dialogue is None:
            self.logger.warning(f"Could not create dialogue for message={message}")
            return

        response_message = await handler(message, dialogue)
        if not response_message:
            return
        self.logger.info(f"returning message: {response_message}")

        response_envelope = Envelope(
            to=str(envelope.sender),
            sender=str(self.connection_id),
            message=response_message,
            protocol_specification_id=self.message_type.protocol_specification_id,
        )

        await self._in_queue.put(response_envelope)

    async def get_message(self) -> Envelope | None:
        """Check the in-queue for envelopes."""

        if self.is_stopped:
            return None
        try:
            if not self._pubsub.subscribed:
                return None
            res = await self._pubsub.get_message(ignore_subscribe_messages=True)
            if res is None:
                return None
            channel = res["channel"].decode("utf-8")
            return Envelope(
                to=self.target_skill_id,
                sender=str(self.connection_id),
                message=PubsubMessage(
                    performative=PubsubMessage.Performative.MESSAGE,
                    channel=channel,
                    data=res["data"],
                ),
            )
        except asyncio.QueueEmpty:
            return None

    async def _cancel_tasks(self) -> None:
        """Cancel all requests tasks pending."""

        for task in list(self._tasks):
            if task.done():  # pragma: nocover
                continue
            task.cancel()

        for task in list(self._tasks):
            try:
                await task
            except KeyboardInterrupt:
                raise
            except BaseException:  # noqa
                pass


class RedisAsyncChannel(BaseAsyncChannel):  # pylint: disable=too-many-instance-attributes
    """A channel handling incomming communication from the Redis connection."""

    _pubsub: redis.client.PubSub

    def __init__(
        self,
        agent_address: Address,
        connection_id: PublicId,
        **kwargs,
    ):
        """Initialize the Redis channel.

        :param agent_address: the address of the agent.
        :param connection_id: the id of the connection.
        """

        super().__init__(agent_address, connection_id, message_type=PubsubMessage)

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._dialogues = PubsubDialogues(str(RedisConnection.connection_id))
        self.logger.debug("Initialised the Redis channel")

    async def connect(self, loop: AbstractEventLoop) -> None:
        """Connect channel using loop.

        :param loop: asyncio event loop to use
        """

        if self.is_stopped:
            self._loop = loop
            self._in_queue = asyncio.Queue()
            self.is_stopped = False
            try:
                self._connection = redis.Redis(
                    host=self.host,
                    port=self.port,
                )
                self._pubsub = self._connection.pubsub()
                self.logger.info("Redis has connected.")
            except Exception as err:
                self.is_stopped = True
                self._in_queue = None
                msg = f"Failed to start Redis: {err}"
                raise ConnectionError(msg) from err

    async def disconnect(self) -> None:
        """Disconnect channel."""

        if self.is_stopped:
            return

        await self._cancel_tasks()
        await self._pubsub.close()
        await self._connection.close()
        self.is_stopped = True
        self.logger.info("Redis has shutdown.")

    @property
    def performative_handlers(
        self,
    ) -> dict[
        PubsubMessage.Performative,
        Callable[[PubsubMessage, PubsubDialogue], PubsubMessage],
    ]:
        """Map performative handlers."""
        return {
            PubsubMessage.Performative.SUBSCRIBE: self.subscribe,
            PubsubMessage.Performative.UNSUBSCRIBE: self.unsubscribe,
            PubsubMessage.Performative.PUBLISH: self.publish,
            PubsubMessage.Performative.MESSAGE: self.message,
        }

    async def subscribe(self, message: PubsubMessage, dialogue: PubsubDialogue) -> PubsubMessage:
        """Handle PubsubMessage with SUBSCRIBE Perfomative."""

        await self._pubsub.subscribe(",".join(message.channels))

        for channel in message.channels:
            self.logger.info(f"Subscribed to channel {channel}")
            self._subscriptions[channel] = dialogue
        return dialogue.reply(
            performative=PubsubMessage.Performative.SUBSCRIBED,
            channel=str(message.channels),
            success=True,
            info="Subscribed to channel",
        )

    def unsubscribe(self, message: PubsubMessage, dialogue: PubsubDialogue) -> PubsubMessage:
        """Handle PubsubMessage with UNSUBSCRIBE Perfomative."""

        message.channels  # noqa

        dialogue.reply(
            performative=PubsubMessage.Performative.UNSUBSCRIBED,
            channel=...,
            success=...,
            info=...,
        )

        return dialogue.reply(
            performative=PubsubMessage.Performative.ERROR,
            data=...,
        )

    async def publish(
        self,
        message: PubsubMessage,
        dialogue: PubsubDialogue,  # pylint: disable=unused-argument
    ) -> PubsubMessage:
        """Handle PubsubMessage with PUBLISH Perfomative."""

        del dialogue  # this needs to be fixed
        channel = message.channel
        data = message.message
        await self._connection.publish(channel, data)

    def message(self, message: PubsubMessage, dialogue: PubsubDialogue) -> PubsubMessage:
        """Handle PubsubMessage with MESSAGE Perfomative."""

        message.channel  # noqa
        message.data  # noqa

        # TODO: Implement the necessary logic required for the response message  # noqa

        dialogue.reply(
            performative=PubsubMessage.Performative.MESSAGE,
            channel=...,
            data=...,
        )

        return dialogue.reply(
            performative=PubsubMessage.Performative.ERROR,
            data=...,
        )


class RedisConnection(Connection):
    """Proxy to the functionality of a Redis connection."""

    connection_id = CONNECTION_ID

    def __init__(self, **kwargs: Any) -> None:
        """Initialize a Redis connection.

        :param kwargs: keyword arguments
        """

        keys = [
            "host",
            "port",
            "target_skill_id",
        ]  # TODO: pop your custom kwargs  # noqa
        config = kwargs["configuration"].config
        custom_kwargs = {key: config.pop(key) for key in keys}
        super().__init__(**kwargs)

        self.channel = RedisAsyncChannel(
            self.address,
            connection_id=self.connection_id,
            **custom_kwargs,
        )

    async def connect(self) -> None:
        """Connect to a Redis."""

        if self.is_connected:  # pragma: nocover
            return

        with self._connect_context():
            self.channel.logger = self.logger
            await self.channel.connect(self.loop)

    async def disconnect(self) -> None:
        """Disconnect from a Redis."""

        if self.is_disconnected:
            return  # pragma: nocover
        self.state = ConnectionStates.disconnecting
        await self.channel.disconnect()
        self.state = ConnectionStates.disconnected

    async def send(self, envelope: Envelope) -> None:
        """Send an envelope.

        :param envelope: the envelope to send.
        """

        self._ensure_connected()
        return await self.channel.send(envelope)

    async def receive(self, *args, **kwargs: Any) -> Optional[Envelope]:  # noqa
        """Receive an envelope. Blocking.

        :param args: arguments to receive
        :param kwargs: keyword arguments to receive
        :return: the envelope received, if present.  # noqa: DAR202
        """

        self._ensure_connected()
        try:
            if self.channel.is_stopped:
                return None
            return await self.channel.get_message()
        except Exception as err:  # noqa
            self.logger.info(f"Exception on receive {err}")
            return None
