from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import ContractDAO


class ContractAPI(DAO):
    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_contracts(self, ts: TimeSpan) -> List[ContractDAO]:
        pass

    @abstractmethod
    def get_current(self,contract_ack:bool) -> Optional[ContractDAO]:
        pass

    @abstractmethod
    def set_current(self, contract: ContractDAO) -> ContractDAO:
        pass
