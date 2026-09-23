from abc import abstractmethod
from typing import List
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import BaselineDAO, CertifiedBaseline, Baseline, BaselineValueDAO


class BaselineAPI(DAO):
    def __init__(self, table_prefix: str):
        super(BaselineAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list(self, contract_id: int) -> List[CertifiedBaseline]:
        pass

    @abstractmethod
    def get_baseline(self, baseline_id: int) -> Baseline:
        pass

    @abstractmethod
    def init_baseline(self) -> BaselineDAO:
        pass

    @abstractmethod
    def set_baseline(self, baseline_values: List[BaselineValueDAO]):
        pass
