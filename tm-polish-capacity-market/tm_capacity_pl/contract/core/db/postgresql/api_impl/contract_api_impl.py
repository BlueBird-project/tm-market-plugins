from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.contract.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.contract.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.models.contract import ContractDAO


class ContractQueries(QueryObject):
    __TABLE_NAME__ = "capacity_market_contract_details"

    __PROJECTION__ = """ ${table_alias}."create_time", ${table_alias}."update_time", ${table_alias}."offer_mwh",
     ${table_alias}."capacity_obligation", ${table_alias}."offer_ack_mwh",, ${table_alias}."capacity_ack_obligation",
      ${table_alias}."current_baseline_id",  ${table_alias}."ack_ts",    ${table_alias}."ext"  """

    LIST_CONTRACT = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
    ( coalesce(:ts_from<=${table_alias}."create_time",TRUE) and  coalesce(:ts_to>=${table_alias}."create_time",TRUE))
    """
    LIST_CONTRACT_ACK = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
    ( coalesce(:ts_from<=${table_alias}."ack_ts",TRUE) and  coalesce(:ts_to>=${table_alias}."ack_ts",TRUE))
    """

    GET_CONTRACT = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}  
    WHERE ${table_alias}."create_time" = :ts
    """
    GET_CONTRACT_ACK = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}  
    WHERE COALESCE(${table_alias}."create_time" = :ts, TRUE) and ${table_alias}."ack_ts" =:ack_ts
    """

    GET_CURRENT_CONTRACT = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}  
    WHERE ${table_alias}."ack_ts" is NULL order by ${table_alias}."create_time" desc
    """

    GET_CURRENT_CONTRACT_ACK = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}  
    WHERE ${table_alias}."ack_ts" is not NULL order by ${table_alias}."ack_ts" desc
    """

    INIT_CONTRACT = """INSERT INTO "${table_prefix}${table_name}" 
    ("create_time",  "offer_mwh","capacity_obligation","current_baseline_id",   "update_time","ext"  ) 
    VALUES (:create_time,:offer_mwh,:capacity_obligation ,:current_baseline_id,  extract(epoch from now()) * 1000,NULL) 
    """

    ACK_CONTRACT = """UPDATE "${table_prefix}${table_name}" 
    SET "offer_ack_mwh" =  :offer_ack_mwh , "ack_ts" = :ack_ts, "capacity_ack_obligation" = :capacity_ack_obligation,
    "current_baseline_id" =:current_baseline_id, "update_time" =  extract(epoch from now()) * 1000 
    WHERE create_time = :create_time  
    """
    SET_BASELINE = """UPDATE "${table_prefix}${table_name}" 
    SET   "current_baseline_id" =:current_baseline_id, "update_time" =  extract(epoch from now()) * 1000 
    WHERE create_time = :create_time  
    """


class ContractAPIImpl(ContractAPI):

    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)
        self.queries: ContractQueries = self.build_queries(ContractQueries)

    def list_contracts(self, ts: TimeSpan, contract_ack: bool) -> List[ContractDAO]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to}
            q = self.queries.LIST_CONTRACT if contract_ack else self.queries.LIST_CONTRACT_ACK
            contracts = conn.get(q=q, args=args, obj_type=ContractDAO)
            return contracts

    def get_current(self, contract_ack: bool) -> Optional[ContractDAO]:

        with ConnectionWrapper() as conn:
            if contract_ack:
                contract = conn.get(q=self.queries.GET_CURRENT_CONTRACT_ACK, args={}, obj_type=ContractDAO)
            else:
                contract = conn.get(q=self.queries.GET_CURRENT_CONTRACT, args={}, obj_type=ContractDAO)
            return contract

    def add_contract(self, contract: ContractDAO) -> ContractDAO:
        with ConnectionWrapper() as conn:
            conn.insert(q=self.queries.INIT_CONTRACT, args=vars(contract))
            obj: ContractDAO = conn.get(q=self.queries.GET_CONTRACT, args={"ts": contract.create_time},
                                        obj_type=ContractDAO)
            if obj is None:
                raise ValueError(f"Contract not saved: {contract.__dict__}")

            return contract

    def ack_contract(self, contract: ContractDAO) -> ContractDAO:
        with ConnectionWrapper() as conn:
            conn.update(q=self.queries.ACK_CONTRACT, args=vars(contract))

            obj: ContractDAO = conn.get(q=self.queries.GET_CONTRACT_ACK,
                                        args={"ts": contract.create_time, "ack_ts": contract.ack_ts},
                                        obj_type=ContractDAO)
            # if obj is None:
            #     raise ValueError(f"Contract not updated: {contract.__dict__}")

            return obj

    def set_baseline(self, contract_id: int, baseline_id: int) -> ContractDAO:
        with ConnectionWrapper() as conn:
            conn.update(q=self.queries.SET_BASELINE,
                        args={"create_time": contract_id, "current_baseline_id": baseline_id})

            obj: ContractDAO = conn.get(q=self.queries.GET_CONTRACT,
                                        args={"ts": contract_id},
                                        obj_type=ContractDAO)

            return obj
