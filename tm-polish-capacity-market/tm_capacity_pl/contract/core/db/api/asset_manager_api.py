from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.demand import AssetManager


class AssetManagerAPI(DAO):

    @abstractmethod
    def list_asset_managers(self, ) -> List[AssetManager]:
        pass

    @abstractmethod
    def get_asset_manager(self, asset_manager_uri: str, ) -> Optional[AssetManager]:
        pass

    @abstractmethod
    def get_or_init(self, asset_manager_uri: str, ) -> AssetManager:
        pass

    @abstractmethod
    def get_asset_manager_id(self, asset_manager_id: int, ) -> Optional[AssetManager]:
        pass

    @abstractmethod
    def add_asset_manager(self, asset_manager: AssetManager) -> AssetManager:
        pass
