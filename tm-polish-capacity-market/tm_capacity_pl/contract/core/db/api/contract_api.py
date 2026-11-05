from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import ContractDAO, BaselineDAO, FlexRequest


class ContractAPI(DAO):
    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_request(self, ts: TimeSpan) -> List[FlexRequest]:
        pass

    @abstractmethod
    def current_request(self, ) -> Optional[FlexRequest]:
        pass

    @abstractmethod
    def add_request(self, request: FlexRequest) -> FlexRequest:
        pass

    @abstractmethod
    def list_contracts(self, ts: TimeSpan, contract_ack: bool) -> List[ContractDAO]:
        pass

    @abstractmethod
    def get_current(self, contract_ack: bool) -> List[ContractDAO]:
        pass

    @abstractmethod
    def add_contract(self, contract: ContractDAO) -> ContractDAO:
        pass

    @abstractmethod
    def ack_contract(self, contract: ContractDAO) -> ContractDAO:
        pass

    @abstractmethod
    def set_baseline(self, contract_id: int, baseline_id: int) -> ContractDAO:
        pass
