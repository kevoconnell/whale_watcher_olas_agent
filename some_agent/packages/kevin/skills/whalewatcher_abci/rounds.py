# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025 Valory AG
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

"""This package contains the rounds of WhaleWatcherAbciApp."""

from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Set, Tuple

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    AppState,
    BaseSynchronizedData,
    DegenerateRound,
    EventToTimeout,
)

from packages.kevin.skills.whalewatcher_abci.payloads import (
    AlertPayload,
    BlockReceivedPayload,
    IdlePayload,
)


class Event(Enum):
    """WhaleWatcherAbciApp Events"""

    BLOCK_RECEIVED = "block_received"
    DONE = "done"
    TX_OVER_THRESHOLD = "tx_over_threshold"
    TIMEOUT = "timeout"
    TX_UNDER_THRESHOLD = "tx_under_threshold"


class SynchronizedData(BaseSynchronizedData):
    """
    Class to represent the synchronized data.

    This data is replicated by the tendermint application.
    """


class AlertRound(AbstractRound):
    """AlertRound"""

    payload_class = AlertPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: AlertPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: AlertPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class BlockReceivedRound(AbstractRound):
    """BlockReceivedRound"""

    payload_class = BlockReceivedPayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: BlockReceivedPayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: BlockReceivedPayload) -> None:
        """Process payload."""
        raise NotImplementedError


class IdleRound(AbstractRound):
    """IdleRound"""

    payload_class = IdlePayload
    payload_attribute = ""  # TODO: update
    synchronized_data_class = SynchronizedData

    # TODO: replace AbstractRound with one of CollectDifferentUntilAllRound,
    # CollectSameUntilAllRound, CollectSameUntilThresholdRound,
    # CollectDifferentUntilThresholdRound, OnlyKeeperSendsRound, VotingRound,
    # from packages/valory/skills/abstract_round_abci/base.py
    # or implement the methods

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Enum]]:
        """Process the end of the block."""
        raise NotImplementedError

    def check_payload(self, payload: IdlePayload) -> None:
        """Check payload."""
        raise NotImplementedError

    def process_payload(self, payload: IdlePayload) -> None:
        """Process payload."""
        raise NotImplementedError


class DoneRound(DegenerateRound):
    """DoneRound"""


class ErrorRound(DegenerateRound):
    """ErrorRound"""


class WhaleWatcherAbciApp(AbciApp[Event]):
    """WhaleWatcherAbciApp"""

    initial_round_cls: AppState = IdleRound
    initial_states: Set[AppState] = {IdleRound}
    transition_function: AbciAppTransitionFunction = {
        IdleRound: {
            Event.BLOCK_RECEIVED: BlockReceivedRound
        },
        BlockReceivedRound: {
            Event.TX_OVER_THRESHOLD: AlertRound,
            Event.TX_UNDER_THRESHOLD: BlockReceivedRound,
            Event.DONE: DoneRound,
            Event.TIMEOUT: ErrorRound
        },
        AlertRound: {
            Event.DONE: DoneRound,
            Event.TIMEOUT: ErrorRound
        },
        DoneRound: {},
        ErrorRound: {}
    }
    final_states: Set[AppState] = {ErrorRound, DoneRound}
    event_to_timeout: EventToTimeout = {}
    cross_period_persisted_keys: FrozenSet[str] = frozenset()
    db_pre_conditions: Dict[AppState, Set[str]] = {
        IdleRound: [],
    }
    db_post_conditions: Dict[AppState, Set[str]] = {
        ErrorRound: [],
    	DoneRound: [],
    }
