from typing import List, Optional

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.contract.core.db.api.asset_manager_api import AssetManagerAPI
from tm_capacity_pl.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.models.demand import AssetManager


class AssetManagerQueries(QueryObject):
    __TABLE_NAME__ = "asset_manager"
    __PROJECTION__ = """ ${table_alias}."asset_manager_id",${table_alias}."asset_manager_uri"   """
    LIST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}      """
    GET_URI = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        asset_manager_uri = :asset_manager_uri"""
    GET_ID = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        asset_manager_id = :asset_manager_id"""

    INSERT = """INSERT INTO "${table_prefix}${table_name}" 
    ( "asset_manager_uri" )  VALUES (  :asset_manager_uri) 
    """


class AssetManagerAPIImpl(AssetManagerAPI):
    def __init__(self, table_prefix: str):
        super(AssetManagerAPI, self).__init__(table_prefix=table_prefix)
        self.asset_queries: AssetManagerQueries = AssetManagerQueries.build(table_prefix=table_prefix)

    def list_asset_managers(self, ) -> List[AssetManager]:
        with ConnectionWrapper() as conn:
            baselines = conn.select(q=self.asset_queries.LIST, args={}, obj_type=AssetManager)
            return baselines

    def get_asset_manager(self, asset_manager_uri: str, ) -> Optional[AssetManager]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.asset_queries.GET_URI, args={"asset_manager_uri": asset_manager_uri},
                            obj_type=AssetManager)

    def get_asset_manager_id(self, asset_manager_id: int, ) -> Optional[AssetManager]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.asset_queries.GET_URI, args={"asset_manager_id": asset_manager_id},
                            obj_type=AssetManager)

    def add_asset_manager(self, asset_manager: AssetManager) -> AssetManager:
        with ConnectionWrapper() as conn:
            asset_manager_id = conn.insert(q=self.asset_queries.INSERT, args=vars(asset_manager),
                                           return_id_col=["asset_manager_id"])
            asset_manager.asset_manager_id = asset_manager_id
            return asset_manager

    def get_or_init(self, asset_manager_uri: str, ) -> AssetManager:
        am: AssetManager = self.get_asset_manager(asset_manager_uri=asset_manager_uri)
        if am is None:
            am = self.add_asset_manager(asset_manager=AssetManager(asset_manager_uri=asset_manager_uri))
            assert am.asset_manager_id is not None
        return am
