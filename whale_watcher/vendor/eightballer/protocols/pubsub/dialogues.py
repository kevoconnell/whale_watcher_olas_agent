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

"""This module contains the classes required for pubsub dialogue management.

- PubsubDialogue: The dialogue class maintains state of a dialogue and manages it.
- PubsubDialogues: The dialogues class keeps track of all dialogues.
"""

from abc import ABC
from typing import cast
from collections.abc import Callable

from aea.common import Address
from aea.skills.base import Model
from aea.protocols.base import Message
from aea.protocols.dialogue.base import Dialogue, Dialogues, DialogueLabel

from packages.eightballer.protocols.pubsub.message import PubsubMessage


class PubsubDialogue(Dialogue):
    """The pubsub dialogue class maintains state of a dialogue and manages it."""

    INITIAL_PERFORMATIVES: frozenset[Message.Performative] = frozenset(
        {
            PubsubMessage.Performative.SUBSCRIBE,
            PubsubMessage.Performative.UNSUBSCRIBE,
            PubsubMessage.Performative.PUBLISH,
        }
    )
    TERMINAL_PERFORMATIVES: frozenset[Message.Performative] = frozenset(
        {
            PubsubMessage.Performative.SUBSCRIBED,
            PubsubMessage.Performative.UNSUBSCRIBED,
            PubsubMessage.Performative.ERROR,
        }
    )
    VALID_REPLIES: dict[Message.Performative, frozenset[Message.Performative]] = {
        PubsubMessage.Performative.ERROR: frozenset(),
        PubsubMessage.Performative.MESSAGE: frozenset(
            {PubsubMessage.Performative.MESSAGE, PubsubMessage.Performative.ERROR}
        ),
        PubsubMessage.Performative.PUBLISH: frozenset({PubsubMessage.Performative.ERROR}),
        PubsubMessage.Performative.SUBSCRIBE: frozenset(
            {PubsubMessage.Performative.SUBSCRIBED, PubsubMessage.Performative.ERROR}
        ),
        PubsubMessage.Performative.SUBSCRIBED: frozenset(),
        PubsubMessage.Performative.UNSUBSCRIBE: frozenset(
            {PubsubMessage.Performative.UNSUBSCRIBED, PubsubMessage.Performative.ERROR}
        ),
        PubsubMessage.Performative.UNSUBSCRIBED: frozenset(),
    }

    class Role(Dialogue.Role):
        """This class defines the agent's role in a pubsub dialogue."""

        PUBLISHER = "publisher"
        SUBSCRIBER = "subscriber"

    class EndState(Dialogue.EndState):
        """This class defines the end states of a pubsub dialogue."""

        SUBSCRIBED = 0
        UNSUBSCRIBED = 1
        ERROR = 2

    def __init__(
        self,
        dialogue_label: DialogueLabel,
        self_address: Address,
        role: Dialogue.Role,
        message_class: type[PubsubMessage] = PubsubMessage,
    ) -> None:
        """Initialize a dialogue.

        :param dialogue_label: the identifier of the dialogue
        :param self_address: the address of the entity for whom this dialogue is maintained
        :param role: the role of the agent this dialogue is maintained for
        :param message_class: the message class used
        """
        Dialogue.__init__(
            self,
            dialogue_label=dialogue_label,
            message_class=message_class,
            self_address=self_address,
            role=role,
        )


class BasePubsubDialogues(Dialogues, ABC):
    """This class keeps track of all pubsub dialogues."""

    END_STATES = frozenset(
        {
            PubsubDialogue.EndState.SUBSCRIBED,
            PubsubDialogue.EndState.UNSUBSCRIBED,
            PubsubDialogue.EndState.ERROR,
        }
    )

    _keep_terminal_state_dialogues = False

    def __init__(
        self,
        self_address: Address,
        role_from_first_message: Callable[[Message, Address], Dialogue.Role],
        dialogue_class: type[PubsubDialogue] = PubsubDialogue,
        default_role: Dialogue.Role = PubsubDialogue.Role.SUBSCRIBER,
    ) -> None:
        """Initialize dialogues.

        :param self_address: the address of the entity for whom dialogues are maintained
        :param dialogue_class: the dialogue class used
        :param role_from_first_message: the callable determining role from first message
        """
        del role_from_first_message

        def _role_from_first_message(message: Message, sender: Address) -> Dialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message."""
            del sender, message
            return default_role

        Dialogues.__init__(
            self,
            self_address=self_address,
            end_states=cast(frozenset[Dialogue.EndState], self.END_STATES),
            message_class=PubsubMessage,
            dialogue_class=dialogue_class,
            role_from_first_message=_role_from_first_message,
        )


class PubsubDialogues(Model, BasePubsubDialogues):
    """This class keeps track of all pubsub dialogues."""

    def __init__(self, **kwargs):
        """Initialize the dialogues."""

        def _role_from_first_message(message: Message, sender: Address) -> Dialogue.Role:
            """Infer the role of the agent from an incoming/outgoing first message."""
            del sender, message

            return PubsubDialogue.Role.SUBSCRIBER

        Model.__init__(self, keep_terminal_state_dialogues=False, **kwargs)
        BasePubsubDialogues.__init__(
            self,
            role_from_first_message=_role_from_first_message,
            self_address=str(self.context.skill_id),
        )
