# -*- coding: utf-8 -*-
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

"""This module contains pubsub's message definition."""

# pylint: disable=too-many-statements,too-many-locals,no-member,too-few-public-methods,too-many-branches,not-an-iterable,unidiomatic-typecheck,unsubscriptable-object
import logging
from typing import Any, Optional, Set, Tuple, cast

from aea.configurations.base import PublicId
from aea.exceptions import AEAEnforceError, enforce
from aea.protocols.base import Message

_default_logger = logging.getLogger("aea.packages.eightballer.protocols.pubsub.message")

DEFAULT_BODY_SIZE = 4


class PubsubMessage(Message):
    """A protocol for Publish/Subscribe messaging systems, enabling message distribution through channel-based subscription and publishing."""

    protocol_id = PublicId.from_str("eightballer/pubsub:0.1.0")
    protocol_specification_id = PublicId.from_str("eightballer/pubsub:0.1.0")

    class Performative(Message.Performative):
        """Performatives for the pubsub protocol."""

        ERROR = "error"
        MESSAGE = "message"
        PUBLISH = "publish"
        SUBSCRIBE = "subscribe"
        SUBSCRIBED = "subscribed"
        UNSUBSCRIBE = "unsubscribe"
        UNSUBSCRIBED = "unsubscribed"

        def __str__(self) -> str:
            """Get the string representation."""
            return str(self.value)

    _performatives = {
        "error",
        "message",
        "publish",
        "subscribe",
        "subscribed",
        "unsubscribe",
        "unsubscribed",
    }
    __slots__: Tuple[str, ...] = tuple()

    class _SlotsCls:
        __slots__ = (
            "channel",
            "channels",
            "data",
            "dialogue_reference",
            "info",
            "message",
            "message_id",
            "performative",
            "success",
            "target",
        )

    def __init__(
        self,
        performative: Performative,
        dialogue_reference: Tuple[str, str] = ("", ""),
        message_id: int = 1,
        target: int = 0,
        **kwargs: Any,
    ):
        """
        Initialise an instance of PubsubMessage.

        :param message_id: the message id.
        :param dialogue_reference: the dialogue reference.
        :param target: the message target.
        :param performative: the message performative.
        :param **kwargs: extra options.
        """
        super().__init__(
            dialogue_reference=dialogue_reference,
            message_id=message_id,
            target=target,
            performative=PubsubMessage.Performative(performative),
            **kwargs,
        )

    @property
    def valid_performatives(self) -> Set[str]:
        """Get valid performatives."""
        return self._performatives

    @property
    def dialogue_reference(self) -> Tuple[str, str]:
        """Get the dialogue_reference of the message."""
        enforce(self.is_set("dialogue_reference"), "dialogue_reference is not set.")
        return cast(Tuple[str, str], self.get("dialogue_reference"))

    @property
    def message_id(self) -> int:
        """Get the message_id of the message."""
        enforce(self.is_set("message_id"), "message_id is not set.")
        return cast(int, self.get("message_id"))

    @property
    def performative(self) -> Performative:  # type: ignore # noqa: F821
        """Get the performative of the message."""
        enforce(self.is_set("performative"), "performative is not set.")
        return cast(PubsubMessage.Performative, self.get("performative"))

    @property
    def target(self) -> int:
        """Get the target of the message."""
        enforce(self.is_set("target"), "target is not set.")
        return cast(int, self.get("target"))

    @property
    def channel(self) -> str:
        """Get the 'channel' content from the message."""
        enforce(self.is_set("channel"), "'channel' content is not set.")
        return cast(str, self.get("channel"))

    @property
    def channels(self) -> Tuple[str, ...]:
        """Get the 'channels' content from the message."""
        enforce(self.is_set("channels"), "'channels' content is not set.")
        return cast(Tuple[str, ...], self.get("channels"))

    @property
    def data(self) -> bytes:
        """Get the 'data' content from the message."""
        enforce(self.is_set("data"), "'data' content is not set.")
        return cast(bytes, self.get("data"))

    @property
    def info(self) -> Optional[str]:
        """Get the 'info' content from the message."""
        return cast(Optional[str], self.get("info"))

    @property
    def message(self) -> bytes:
        """Get the 'message' content from the message."""
        enforce(self.is_set("message"), "'message' content is not set.")
        return cast(bytes, self.get("message"))

    @property
    def success(self) -> bool:
        """Get the 'success' content from the message."""
        enforce(self.is_set("success"), "'success' content is not set.")
        return cast(bool, self.get("success"))

    def _is_consistent(self) -> bool:
        """Check that the message follows the pubsub protocol."""
        try:
            enforce(
                isinstance(self.dialogue_reference, tuple),
                "Invalid type for 'dialogue_reference'. Expected 'tuple'. Found '{}'.".format(
                    type(self.dialogue_reference)
                ),
            )
            enforce(
                isinstance(self.dialogue_reference[0], str),
                "Invalid type for 'dialogue_reference[0]'. Expected 'str'. Found '{}'.".format(
                    type(self.dialogue_reference[0])
                ),
            )
            enforce(
                isinstance(self.dialogue_reference[1], str),
                "Invalid type for 'dialogue_reference[1]'. Expected 'str'. Found '{}'.".format(
                    type(self.dialogue_reference[1])
                ),
            )
            enforce(
                type(self.message_id) is int,
                "Invalid type for 'message_id'. Expected 'int'. Found '{}'.".format(
                    type(self.message_id)
                ),
            )
            enforce(
                type(self.target) is int,
                "Invalid type for 'target'. Expected 'int'. Found '{}'.".format(
                    type(self.target)
                ),
            )

            # Light Protocol Rule 2
            # Check correct performative
            enforce(
                isinstance(self.performative, PubsubMessage.Performative),
                "Invalid 'performative'. Expected either of '{}'. Found '{}'.".format(
                    self.valid_performatives, self.performative
                ),
            )

            # Check correct contents
            actual_nb_of_contents = len(self._body) - DEFAULT_BODY_SIZE
            expected_nb_of_contents = 0
            if self.performative == PubsubMessage.Performative.SUBSCRIBE:
                expected_nb_of_contents = 1
                enforce(
                    isinstance(self.channels, tuple),
                    "Invalid type for content 'channels'. Expected 'tuple'. Found '{}'.".format(
                        type(self.channels)
                    ),
                )
                enforce(
                    all(isinstance(element, str) for element in self.channels),
                    "Invalid type for tuple elements in content 'channels'. Expected 'str'.",
                )
            elif self.performative == PubsubMessage.Performative.UNSUBSCRIBE:
                expected_nb_of_contents = 1
                enforce(
                    isinstance(self.channels, tuple),
                    "Invalid type for content 'channels'. Expected 'tuple'. Found '{}'.".format(
                        type(self.channels)
                    ),
                )
                enforce(
                    all(isinstance(element, str) for element in self.channels),
                    "Invalid type for tuple elements in content 'channels'. Expected 'str'.",
                )
            elif self.performative == PubsubMessage.Performative.PUBLISH:
                expected_nb_of_contents = 2
                enforce(
                    isinstance(self.channel, str),
                    "Invalid type for content 'channel'. Expected 'str'. Found '{}'.".format(
                        type(self.channel)
                    ),
                )
                enforce(
                    isinstance(self.message, bytes),
                    "Invalid type for content 'message'. Expected 'bytes'. Found '{}'.".format(
                        type(self.message)
                    ),
                )
            elif self.performative == PubsubMessage.Performative.SUBSCRIBED:
                expected_nb_of_contents = 2
                enforce(
                    isinstance(self.channel, str),
                    "Invalid type for content 'channel'. Expected 'str'. Found '{}'.".format(
                        type(self.channel)
                    ),
                )
                enforce(
                    isinstance(self.success, bool),
                    "Invalid type for content 'success'. Expected 'bool'. Found '{}'.".format(
                        type(self.success)
                    ),
                )
                if self.is_set("info"):
                    expected_nb_of_contents += 1
                    info = cast(str, self.info)
                    enforce(
                        isinstance(info, str),
                        "Invalid type for content 'info'. Expected 'str'. Found '{}'.".format(
                            type(info)
                        ),
                    )
            elif self.performative == PubsubMessage.Performative.UNSUBSCRIBED:
                expected_nb_of_contents = 2
                enforce(
                    isinstance(self.channel, str),
                    "Invalid type for content 'channel'. Expected 'str'. Found '{}'.".format(
                        type(self.channel)
                    ),
                )
                enforce(
                    isinstance(self.success, bool),
                    "Invalid type for content 'success'. Expected 'bool'. Found '{}'.".format(
                        type(self.success)
                    ),
                )
                if self.is_set("info"):
                    expected_nb_of_contents += 1
                    info = cast(str, self.info)
                    enforce(
                        isinstance(info, str),
                        "Invalid type for content 'info'. Expected 'str'. Found '{}'.".format(
                            type(info)
                        ),
                    )
            elif self.performative == PubsubMessage.Performative.MESSAGE:
                expected_nb_of_contents = 2
                enforce(
                    isinstance(self.channel, str),
                    "Invalid type for content 'channel'. Expected 'str'. Found '{}'.".format(
                        type(self.channel)
                    ),
                )
                enforce(
                    isinstance(self.data, bytes),
                    "Invalid type for content 'data'. Expected 'bytes'. Found '{}'.".format(
                        type(self.data)
                    ),
                )
            elif self.performative == PubsubMessage.Performative.ERROR:
                expected_nb_of_contents = 1
                enforce(
                    isinstance(self.data, bytes),
                    "Invalid type for content 'data'. Expected 'bytes'. Found '{}'.".format(
                        type(self.data)
                    ),
                )

            # Check correct content count
            enforce(
                expected_nb_of_contents == actual_nb_of_contents,
                "Incorrect number of contents. Expected {}. Found {}".format(
                    expected_nb_of_contents, actual_nb_of_contents
                ),
            )

            # Light Protocol Rule 3
            if self.message_id == 1:
                enforce(
                    self.target == 0,
                    "Invalid 'target'. Expected 0 (because 'message_id' is 1). Found {}.".format(
                        self.target
                    ),
                )
        except (AEAEnforceError, ValueError, KeyError) as e:
            _default_logger.error(str(e))
            return False

        return True
