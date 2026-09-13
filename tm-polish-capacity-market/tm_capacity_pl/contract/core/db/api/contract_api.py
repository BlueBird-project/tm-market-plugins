from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import ContractDAO, BaselineDAO


class ContractAPI(DAO):
    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_contracts(self, ts: TimeSpan, contract_ack: bool) -> List[ContractDAO]:
        pass

    @abstractmethod
    def get_current(self, contract_ack: bool) -> Optional[ContractDAO]:
        pass

    @abstractmethod
    def add_contract(self, contract: ContractDAO) -> ContractDAO:
        pass

    @abstractmethod
    def ack_contract(self, contract: ContractDAO) -> ContractDAO:
        pass
