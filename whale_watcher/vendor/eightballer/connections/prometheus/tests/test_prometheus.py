# noqa: INP001
# ------------------------------------------------------------------------------
#
#   Copyright 2022 Valory AG
#   Copyright 2018-2021 Fetch.AI Limited
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
"""Tests for the HTTP Client and Server connections together."""

# pylint: disable=W0201
import asyncio
import logging
from unittest.mock import MagicMock

from aea.common import Address
from aea.mail.base import Message
from aea.identity.base import Identity
from aea.configurations.base import ConnectionConfig
from aea.protocols.dialogue.base import Dialogue as BaseDialogue

from packages.eightballer.protocols.prometheus.dialogues import PrometheusDialogue, PrometheusDialogues
from packages.eightballer.connections.prometheus.connection import PrometheusConnection


logger = logging.getLogger(__name__)

SKILL_ID_STR = "some_author/some_skill:0.1.0"


class TestPrometheus:
    """Client-Server end-to-end test."""

    def setup_client(self):
        """Set up client connection."""
        self.client_agent_address = "client_agent_address"
        self.client_agent_public_key = "client_agent_public_key"
        self.client_agent_skill_id = "some/skill:0.1.0"
        self.client_agent_identity = Identity(
            "agent_running_client",
            address=self.client_agent_address,
            public_key=self.client_agent_public_key,
        )
        configuration = ConnectionConfig(
            host="localhost",
            port="8888",
            connection_id=PrometheusConnection.connection_id,
        )
        self.client = PrometheusConnection(
            configuration=configuration,
            data_dir=MagicMock(),
            identity=self.client_agent_identity,
        )
        self.loop.run_until_complete(self.client.connect())

        # skill side dialogues
        def role_from_first_message(  # pylint: disable=unused-argument
            message: Message, receiver_address: Address
        ) -> BaseDialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message.

            :param message: an incoming/outgoing first message
            :param receiver_address: the address of the receiving agent
            :return: The role of the agent
            """
            del receiver_address, message
            return PrometheusDialogue.Role.SERVER

        self._client_dialogues = PrometheusDialogues(
            self.client_agent_skill_id, role_from_first_message=role_from_first_message
        )

    def test_setup(self):
        """Set up test case."""
        self.loop = asyncio.get_event_loop()
        self.setup_client()
