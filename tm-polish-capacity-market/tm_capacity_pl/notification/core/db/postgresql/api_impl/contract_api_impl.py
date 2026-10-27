from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.models.contract import FlexContract
from tm_capacity_pl.models.demand import AssetManager
from tm_capacity_pl.notification.core.db.api.contract_api import ContractAPI


class AssetManagerQueries(QueryObject):
    __TABLE_NAME__ = "asset_manager"
    __PROJECTION__ = """ ${table_alias}."asset_manager_id",${table_alias}."asset_manager_uri"   """
    LIST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}      """
    GET_URI = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        asset_manager_uri = :asset_manager_uri"""
    GET_ID = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        asset_manager_id = :asset_manager_id"""

    INSERT = """INSERT INTO "${table_prefix}${table_name}" 
    (   "asset_manager_id","asset_manager_uri" )  VALUES (  :asset_manager_id,:asset_manager_uri) 
    """


class FlexContractQueries(QueryObject):
    __TABLE_NAME__ = "flex_contract"
    __PROJECTION__ = """ ${table_alias}."asset_manager_id",  ${table_alias}."flex_request_uri",
     ${table_alias}."contract_uri",  ${table_alias}."market_uri",  ${table_alias}."flex_dp_uri",  
     ${table_alias}."cost_dp_uri",  ${table_alias}."flex_dpr_uri",  ${table_alias}."cost_dpr_uri",  
     ${table_alias}."flex_value",  ${table_alias}."cost_value",  ${table_alias}."period_uri_uri", 
      ${table_alias}."ts_date_from",  ${table_alias}."ts_date_to",  ${table_alias}."ts",  ${table_alias}."ack",
        ${table_alias}."ack_ts",  ${table_alias}."update_ts"  """
    LIST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}     
        WHERE COALESCE (  ${table_alias}.ts_date_to > :ts_from, TRUE ) AND 
         COALESCE (  ${table_alias}.ts_date_from < :ts_to, TRUE ) AND COALESCE ( ${table_alias}."ack" =:ack,TRUE)  """

    GET_MAX_TS = """SELECT max(ts) FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        COALESCE(ack = :ack,TRUE) """
    GET_CURRENT = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}     
        WHERE ts = :max_ts """
    GET = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}     
        WHERE contract_uri = :contract_uri """
    GET_ID = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        asset_manager_id = :asset_manager_id"""

    INSERT = """INSERT INTO "${table_prefix}${table_name}"  
    ( "asset_manager_id", "flex_request_uri", "contract_uri", "market_uri", "flex_dp_uri", "cost_dp_uri", 
    "flex_dpr_uri", "cost_dpr_uri", "flex_value", "cost_value", "period_uri_uri", "ts_date_from", "ts_date_to", 
    "ts", "ack", "ack_ts", "update_ts" ) 
    VALUES 
    ( :asset_manager_id, :flex_request_uri, :contract_uri, :market_uri, :flex_dp_uri, :cost_dp_uri,
     :flex_dpr_uri, :cost_dpr_uri, :flex_value, :cost_value, :period_uri_uri, :ts_date_from, :ts_date_to, 
     :ts, :ack, :ack_ts, EXTRACT(epoch FROM current_timestamp) *1000) );
   """
    UPDATE = """UPDATE "${table_prefix}${table_name}" SET  "ack" = :ack,
    "ack_ts" =  EXTRACT(epoch FROM current_timestamp) *1000) WHERE "contract_uri" = :contract_uri 
   """


class ContractAPIImpl(ContractAPI):
    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)
        self.asset_queries: AssetManagerQueries = self.build_queries(AssetManagerQueries)
        self.contract_queries: FlexContractQueries = self.build_queries(FlexContractQueries)

    def list_contracts(self, ts: TimeSpan, contract_ack: bool) -> List[FlexContract]:
        with ConnectionWrapper() as conn:
            contracts = conn.select(q=self.contract_queries.LIST,
                                    args={"ts_from": ts.ts_from, "ts_to": ts.ts_to, "ack": contract_ack},
                                    obj_type=FlexContract)
            return contracts

    def get_current(self, contract_ack: bool) -> List[FlexContract]:
        with ConnectionWrapper() as conn:
            max_ts = conn.get(q=self.contract_queries.GET_MAX_TS,
                              args={"ack": contract_ack},
                              obj_type=FlexContract)
            contracts = conn.select(q=self.contract_queries.GET_CURRENT,
                                    args={"max_ts": max_ts},
                                    obj_type=FlexContract)
            return contracts

    def add_contract(self, contract: FlexContract) -> FlexContract:
        with ConnectionWrapper() as conn:
            update_ts = conn.insert(q=self.contract_queries.INSERT, args=vars(contract),
                                    return_id_col=["update_ts"])
            contract.update_ts = update_ts
            return contract

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


    def ack_contract(self, contract_uri: str) -> FlexContract:
        with ConnectionWrapper() as conn:
            conn.update(q=self.contract_queries.UPDATE,
                        args={"contract_uri": contract_uri, "ack": True})
            contract = conn.get(q=self.contract_queries.GET, args={"contract_uri": contract_uri, },
                                obj_type=FlexContract)

            return contract

    def get_contract(self, contract_uri: str) -> Optional[FlexContract]:
        with ConnectionWrapper() as conn:
            contract = conn.get(q=self.contract_queries.GET, args={"contract_uri": contract_uri, },
                                obj_type=FlexContract)
            return contract