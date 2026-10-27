from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import FlexContract

class ContractAPI(DAO):
    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_contracts(self, ts: TimeSpan, contract_ack: bool) -> List[FlexContract]:
        pass

    @abstractmethod
    def get_current(self, contract_ack: bool) -> Optional[FlexContract]:
        pass

    @abstractmethod
    def add_contract(self, contract: FlexContract) -> FlexContract:
        pass

    @abstractmethod
    def ack_contract(self, contract: FlexContract) -> FlexContract:
        pass

    @abstractmethod
    def get_contract(self, contract_uri: str) -> FlexContract:
        pass

