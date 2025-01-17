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

"""This module contains the transaction payloads of the WhaleWatcherAbciApp."""

from dataclasses import dataclass

from packages.valory.skills.abstract_round_abci.base import BaseTxPayload


@dataclass(frozen=True)
class AlertPayload(BaseTxPayload):
    """Represent a transaction payload for the AlertRound."""

    # TODO: define your attributes


@dataclass(frozen=True)
class BlockReceivedPayload(BaseTxPayload):
    """Represent a transaction payload for the BlockReceivedRound."""

    # TODO: define your attributes


@dataclass(frozen=True)
class IdlePayload(BaseTxPayload):
    """Represent a transaction payload for the IdleRound."""

    # TODO: define your attributes

