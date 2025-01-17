# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2025 eightballer
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

"""This module contains the scaffold contract definition."""

from typing import Any

from aea.common import JSONLike
from packages.eightballer.contracts.erc20 import PUBLIC_ID
from aea.contracts.base import Contract
from aea.crypto.base import LedgerApi, Address


class Erc20(Contract):
    """The scaffold contract class for a smart contract."""

    contract_id = PUBLIC_ID

    @classmethod
    def get_raw_transaction(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs: Any
    ) -> JSONLike:
        """
        Handler method for the 'GET_RAW_TRANSACTION' requests.

        Implement this method in the sub class if you want
        to handle the contract requests manually.

        :param ledger_api: the ledger apis.
        :param contract_address: the contract address.
        :param kwargs: the keyword arguments.
        :return: the tx  # noqa: DAR202
        """
        raise NotImplementedError

    @classmethod
    def get_raw_message(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs: Any
    ) -> bytes:
        """
        Handler method for the 'GET_RAW_MESSAGE' requests.

        Implement this method in the sub class if you want
        to handle the contract requests manually.

        :param ledger_api: the ledger apis.
        :param contract_address: the contract address.
        :param kwargs: the keyword arguments.
        :return: the tx  # noqa: DAR202
        """
        raise NotImplementedError

    @classmethod
    def get_state(
        cls, ledger_api: LedgerApi, contract_address: str, **kwargs: Any
    ) -> JSONLike:
        """
        Handler method for the 'GET_STATE' requests.

        Implement this method in the sub class if you want
        to handle the contract requests manually.

        :param ledger_api: the ledger apis.
        :param contract_address: the contract address.
        :param kwargs: the keyword arguments.
        :return: the tx  # noqa: DAR202
        """
        raise NotImplementedError

    @classmethod
    def name(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        
        ) -> JSONLike:
        """Handler method for the 'name' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.name().call()
        return {
            'str': result
        }



    @classmethod
    def total_supply(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        
        ) -> JSONLike:
        """Handler method for the 'total_supply' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.totalSupply().call()
        return {
            'int': result
        }



    @classmethod
    def decimals(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        
        ) -> JSONLike:
        """Handler method for the 'decimals' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.decimals().call()
        return {
            'int': result
        }



    @classmethod
    def symbol(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        
        ) -> JSONLike:
        """Handler method for the 'symbol' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.symbol().call()
        return {
            'str': result
        }



    @classmethod
    def balance_of(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        account: Address
        ) -> JSONLike:
        """Handler method for the 'balance_of' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.balanceOf(account=account).call()
        return {
            'int': result
        }



    @classmethod
    def allowance(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        owner: Address,
        spender: Address
        ) -> JSONLike:
        """Handler method for the 'allowance' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        result = instance.functions.allowance(owner=owner,
        spender=spender).call()
        return {
            'int': result
        }


    @classmethod
    def approve(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        spender: Address,
        amount: int
        ) -> JSONLike:
        """Handler method for the 'approve' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.approve(spender=spender,
        amount=amount)
        return tx


    @classmethod
    def transfer(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        to: Address,
        amount: int
        ) -> JSONLike:
        """Handler method for the 'transfer' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.transfer(to=to,
        amount=amount)
        return tx


    @classmethod
    def transfer_from(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        from_: Address,
        to: Address,
        amount: int
        ) -> JSONLike:
        """Handler method for the 'transfer_from' requests."""
        instance = cls.get_instance(ledger_api, contract_address)
        tx = instance.functions.transferFrom(from_=from_,
        to=to,
        amount=amount)
        return tx

    @classmethod
    def get_approval_events(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        owner: Address=None,spender: Address=None,value: int=None,
        look_back: int=1000,
        to_block: str="latest",
        from_block: int=None
        ) -> JSONLike:
        """Handler method for the 'Approval' events ."""

        instance = cls.get_instance(ledger_api, contract_address)
        arg_filters = {
            key: value for key, value in (('owner', owner), ('spender', spender), ('value', value))
            if value is not None
        }
        to_block = to_block or "latest"
        if to_block == "latest":
            to_block = ledger_api.api.eth.block_number
        from_block = from_block or (to_block - look_back)
        result = instance.events.Approval().get_logs(
            fromBlock=from_block,
            toBlock=to_block,
            argument_filters=arg_filters
        )
        return {
            "events": result,
            "from_block": from_block,
            "to_block": to_block,
        }


    @classmethod
    def get_transfer_events(
        cls,
        ledger_api: LedgerApi,
        contract_address: str,
        from_: Address=None,to: Address=None,value: int=None,
        look_back: int=1000,
        to_block: str="latest",
        from_block: int=None
        ) -> JSONLike:
        """Handler method for the 'Transfer' events ."""

        instance = cls.get_instance(ledger_api, contract_address)
        arg_filters = {
            key: value for key, value in (('from_', from_), ('to', to), ('value', value))
            if value is not None
        }
        to_block = to_block or "latest"
        if to_block == "latest":
            to_block = ledger_api.api.eth.block_number
        from_block = from_block or (to_block - look_back)
        result = instance.events.Transfer().get_logs(
            fromBlock=from_block,
            toBlock=to_block,
            argument_filters=arg_filters
        )
        return {
            "events": result,
            "from_block": from_block,
            "to_block": to_block,
        }
