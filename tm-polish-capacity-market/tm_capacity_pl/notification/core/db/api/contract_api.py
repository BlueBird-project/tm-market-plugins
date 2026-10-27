from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import FlexContract
from tm_capacity_pl.models.demand import AssetManager


class ContractAPI(DAO):
    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_contracts(self, ts: TimeSpan, contract_ack: bool) -> List[FlexContract]:
        pass

    @abstractmethod
    def get_current(self, contract_ack: bool) -> List[FlexContract]:
        pass

    @abstractmethod
    def add_contract(self, contract: FlexContract) -> FlexContract:
        pass

    @abstractmethod
    def list_asset_managers(self, ) -> List[AssetManager]:
        pass

    @abstractmethod
    def get_asset_manager(self, asset_manager_uri: str, ) -> Optional[AssetManager]:
        pass

    @abstractmethod
    def get_asset_manager_id(self, asset_manager_id: int, ) -> Optional[AssetManager]:
        pass

    @abstractmethod
    def add_asset_manager(self, asset_manager: AssetManager) -> AssetManager:
        pass

    @abstractmethod
    def ack_contract(self, contract: FlexContract) -> FlexContract:
        pass

    @abstractmethod
    def get_contract(self, contract_uri: str) -> Optional[FlexContract]:
        pass
