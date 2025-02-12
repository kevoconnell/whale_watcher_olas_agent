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

"""Serialization module for pubsub protocol."""

# pylint: disable=too-many-statements,too-many-locals,no-member,too-few-public-methods,redefined-builtin
from typing import cast

from aea.mail.base_pb2 import DialogueMessage
from aea.mail.base_pb2 import Message as ProtobufMessage
from aea.protocols.base import Message, Serializer

from packages.eightballer.protocols.pubsub import pubsub_pb2
from packages.eightballer.protocols.pubsub.message import PubsubMessage


class PubsubSerializer(Serializer):
    """Serialization for the 'pubsub' protocol."""

    @staticmethod
    def encode(msg: Message) -> bytes:
        """
        Encode a 'Pubsub' message into bytes.

        :param msg: the message object.
        :return: the bytes.
        """
        msg = cast(PubsubMessage, msg)
        message_pb = ProtobufMessage()
        dialogue_message_pb = DialogueMessage()
        pubsub_msg = pubsub_pb2.PubsubMessage()

        dialogue_message_pb.message_id = msg.message_id
        dialogue_reference = msg.dialogue_reference
        dialogue_message_pb.dialogue_starter_reference = dialogue_reference[0]
        dialogue_message_pb.dialogue_responder_reference = dialogue_reference[1]
        dialogue_message_pb.target = msg.target

        performative_id = msg.performative
        if performative_id == PubsubMessage.Performative.SUBSCRIBE:
            performative = pubsub_pb2.PubsubMessage.Subscribe_Performative()  # type: ignore
            channels = msg.channels
            performative.channels.extend(channels)
            pubsub_msg.subscribe.CopyFrom(performative)
        elif performative_id == PubsubMessage.Performative.UNSUBSCRIBE:
            performative = pubsub_pb2.PubsubMessage.Unsubscribe_Performative()  # type: ignore
            channels = msg.channels
            performative.channels.extend(channels)
            pubsub_msg.unsubscribe.CopyFrom(performative)
        elif performative_id == PubsubMessage.Performative.PUBLISH:
            performative = pubsub_pb2.PubsubMessage.Publish_Performative()  # type: ignore
            channel = msg.channel
            performative.channel = channel
            message = msg.message
            performative.message = message
            pubsub_msg.publish.CopyFrom(performative)
        elif performative_id == PubsubMessage.Performative.SUBSCRIBED:
            performative = pubsub_pb2.PubsubMessage.Subscribed_Performative()  # type: ignore
            channel = msg.channel
            performative.channel = channel
            success = msg.success
            performative.success = success
            if msg.is_set("info"):
                performative.info_is_set = True
                info = msg.info
                performative.info = info
            pubsub_msg.subscribed.CopyFrom(performative)
        elif performative_id == PubsubMessage.Performative.UNSUBSCRIBED:
            performative = pubsub_pb2.PubsubMessage.Unsubscribed_Performative()  # type: ignore
            channel = msg.channel
            performative.channel = channel
            success = msg.success
            performative.success = success
            if msg.is_set("info"):
                performative.info_is_set = True
                info = msg.info
                performative.info = info
            pubsub_msg.unsubscribed.CopyFrom(performative)
        elif performative_id == PubsubMessage.Performative.MESSAGE:
            performative = pubsub_pb2.PubsubMessage.Message_Performative()  # type: ignore
            channel = msg.channel
            performative.channel = channel
            data = msg.data
            performative.data = data
            pubsub_msg.message.CopyFrom(performative)
        elif performative_id == PubsubMessage.Performative.ERROR:
            performative = pubsub_pb2.PubsubMessage.Error_Performative()  # type: ignore
            data = msg.data
            performative.data = data
            pubsub_msg.error.CopyFrom(performative)
        else:
            raise ValueError("Performative not valid: {}".format(performative_id))

        dialogue_message_pb.content = pubsub_msg.SerializeToString()

        message_pb.dialogue_message.CopyFrom(dialogue_message_pb)
        message_bytes = message_pb.SerializeToString()
        return message_bytes

    @staticmethod
    def decode(obj: bytes) -> Message:
        """
        Decode bytes into a 'Pubsub' message.

        :param obj: the bytes object.
        :return: the 'Pubsub' message.
        """
        message_pb = ProtobufMessage()
        pubsub_pb = pubsub_pb2.PubsubMessage()
        message_pb.ParseFromString(obj)
        message_id = message_pb.dialogue_message.message_id
        dialogue_reference = (
            message_pb.dialogue_message.dialogue_starter_reference,
            message_pb.dialogue_message.dialogue_responder_reference,
        )
        target = message_pb.dialogue_message.target

        pubsub_pb.ParseFromString(message_pb.dialogue_message.content)
        performative = pubsub_pb.WhichOneof("performative")
        performative_id = PubsubMessage.Performative(str(performative))
        performative_content = dict()  # type: Dict[str, Any]
        if performative_id == PubsubMessage.Performative.SUBSCRIBE:
            channels = pubsub_pb.subscribe.channels
            channels_tuple = tuple(channels)
            performative_content["channels"] = channels_tuple
        elif performative_id == PubsubMessage.Performative.UNSUBSCRIBE:
            channels = pubsub_pb.unsubscribe.channels
            channels_tuple = tuple(channels)
            performative_content["channels"] = channels_tuple
        elif performative_id == PubsubMessage.Performative.PUBLISH:
            channel = pubsub_pb.publish.channel
            performative_content["channel"] = channel
            message = pubsub_pb.publish.message
            performative_content["message"] = message
        elif performative_id == PubsubMessage.Performative.SUBSCRIBED:
            channel = pubsub_pb.subscribed.channel
            performative_content["channel"] = channel
            success = pubsub_pb.subscribed.success
            performative_content["success"] = success
            if pubsub_pb.subscribed.info_is_set:
                info = pubsub_pb.subscribed.info
                performative_content["info"] = info
        elif performative_id == PubsubMessage.Performative.UNSUBSCRIBED:
            channel = pubsub_pb.unsubscribed.channel
            performative_content["channel"] = channel
            success = pubsub_pb.unsubscribed.success
            performative_content["success"] = success
            if pubsub_pb.unsubscribed.info_is_set:
                info = pubsub_pb.unsubscribed.info
                performative_content["info"] = info
        elif performative_id == PubsubMessage.Performative.MESSAGE:
            channel = pubsub_pb.message.channel
            performative_content["channel"] = channel
            data = pubsub_pb.message.data
            performative_content["data"] = data
        elif performative_id == PubsubMessage.Performative.ERROR:
            data = pubsub_pb.error.data
            performative_content["data"] = data
        else:
            raise ValueError("Performative not valid: {}.".format(performative_id))

        return PubsubMessage(
            message_id=message_id,
            dialogue_reference=dialogue_reference,
            target=target,
            performative=performative,
            **performative_content,
        )
