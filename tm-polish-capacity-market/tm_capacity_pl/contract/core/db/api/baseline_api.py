from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import ContractDAO, BaselineDAO


class BaselineAPI(DAO):
    def __init__(self, table_prefix: str):
        super(BaselineAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def get_baseline(self, contract_id: int) -> List[BaselineDAO]:
        pass

    @abstractmethod
    def set_baseline(self, baseline: List[BaselineDAO]):
        pass

    @abstractmethod
    def set_capacity(self, baseline: List[BaselineDAO])  :
        pass
