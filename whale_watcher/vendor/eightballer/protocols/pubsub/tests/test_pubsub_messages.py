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

"""Test messages module for pubsub protocol."""

# pylint: disable=too-many-statements,too-many-locals,no-member,too-few-public-methods,redefined-builtin

from aea.test_tools.test_protocol import BaseProtocolMessagesTestCase

from packages.eightballer.protocols.pubsub.message import PubsubMessage


class TestMessagePubsub(BaseProtocolMessagesTestCase):
    """Test for the 'pubsub' protocol message."""

    MESSAGE_CLASS = PubsubMessage

    def build_messages(self) -> list[PubsubMessage]:  # type: ignore[override]
        """Build the messages to be used for testing."""
        return [
            PubsubMessage(
                performative=PubsubMessage.Performative.SUBSCRIBE,
                channels=("some str",),
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.UNSUBSCRIBE,
                channels=("some str",),
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.PUBLISH,
                channel="some str",
                message=b"some_bytes",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.SUBSCRIBED,
                channel="some str",
                success=True,
                info="some str",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.UNSUBSCRIBED,
                channel="some str",
                success=True,
                info="some str",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.MESSAGE,
                channel="some str",
                data=b"some_bytes",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.ERROR,
                data=b"some_bytes",
            ),
        ]

    def build_inconsistent(self) -> list[PubsubMessage]:  # type: ignore[override]
        """Build inconsistent messages to be used for testing."""
        return [
            PubsubMessage(
                performative=PubsubMessage.Performative.SUBSCRIBE,
                # skip content: channels
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.UNSUBSCRIBE,
                # skip content: channels
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.PUBLISH,
                # skip content: channel
                message=b"some_bytes",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.SUBSCRIBED,
                # skip content: channel
                success=True,
                info="some str",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.UNSUBSCRIBED,
                # skip content: channel
                success=True,
                info="some str",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.MESSAGE,
                # skip content: channel
                data=b"some_bytes",
            ),
            PubsubMessage(
                performative=PubsubMessage.Performative.ERROR,
                # skip content: data
            ),
        ]
