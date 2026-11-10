from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.contract.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.contract.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.models.contract import ContractDAO, FlexRequest, FlexOffer, FlexPriceOffer


class FlexRequestQueries(QueryObject):
    __TABLE_NAME__ = "flex_request"

    __PROJECTION__ = """ ${table_alias}."create_time", ${table_alias}."update_time", ${table_alias}."offer_mwh",
     ${table_alias}."capacity_obligation", ${table_alias}."offer_ack_mwh",, ${table_alias}."capacity_ack_obligation",
      ${table_alias}."current_baseline_id",  ${table_alias}."ack_ts",    ${table_alias}."ext"  """

    LIST_REQUEST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
    ( coalesce(:ts_from<=${table_alias}."create_time",TRUE) and  coalesce(:ts_to>=${table_alias}."create_time",TRUE))
    """
    # GET_REQUEST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
    #  ${table_alias}."create_ts" = :create_ts
    # """
    CURRENT_REQUEST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
      ${table_alias}."create_ts" = (SELECT MAX( ${table_alias}."create_ts") as max_create_ts 
      FROM "${table_prefix}${table_name}" as ${table_alias}  ) 
    """
    INSERT_REQUEST = """
    INSERT INTO "${table_prefix}${table_name}" (flex_request_uri, offer_period_uri, create_ts, ts_from, ts_to)
     VALUES (:flex_request_uri, :offer_period_uri, :create_ts, :ts_from, :ts_to)    """


class FlexOfferQueries(QueryObject):
    __TABLE_NAME__ = "flex_request"

    __PROJECTION__ = """${table_alias}.flex_request_uri, ${table_alias}.asset_manager_uri,
     ${table_alias}.flex_profile_uri, ${table_alias}.profile_price_uri, ${table_alias}.flex_price,
      ${table_alias}.ts, ${table_alias}.flex_value,${table_alias}.price_value,
      ${table_alias}.update_ts, ${table_alias}.cost_update_ts"""

    LIST_OFFER = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}   """
    LIST_REQUEST_OFFER = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
     ${table_alias}."flex_request_uri" = :flex_request_uri
    """

    GET_REQUEST_OFFER = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
     ${table_alias}."flex_request_uri" = :flex_request_uri AND ${table_alias}.cost_update_ts IS NOT NULL
      AND ${table_alias}.asset_manager_uri  =:asset_manager_uri """

    LIST_PRICE_OFFER = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE 
     ${table_alias}."flex_request_uri" = :flex_request_uri AND ${table_alias}.cost_update_ts IS NOT NULL """

    INSERT_OFFER = """INSERT INTO ${table_prefix}${table_name} 
    (flex_request_uri, asset_manager_uri, flex_profile_uri, profile_price_uri, flex_price, ts, flex_value, update_ts)
    VALUES
     (:flex_request_uri, :asset_manager_uri, :flex_profile_uri, :profile_price_uri, :flex_price, :ts, :flex_value, 
     extract(epoch from now()) * 1000) """

    UPDATE_OFFER_PRICE = """UPDATE "${table_prefix}${table_name}" 
    SET price_value = :price_value AND cost_update_ts EXTRACT(epoch FROM current_timestamp) *1000) 
    WHERE flex_request_uri = :flex_request_uri and asset_manager_uri = :asset_manager_uri """


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
        self.flex_request_query: FlexRequestQueries = self.build_queries(FlexRequestQueries)
        self.flex_offer_queries: FlexOfferQueries = self.build_queries(FlexOfferQueries)

    def list_request(self, ts: TimeSpan) -> List[FlexRequest]:
        with ConnectionWrapper() as conn:
            args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to}
            q = self.flex_request_query.LIST_REQUEST
            requests = conn.select(q=q, args=args, obj_type=FlexRequest)
            return requests

    def current_request(self, ) -> Optional[FlexRequest]:
        with ConnectionWrapper() as conn:
            q = self.flex_request_query.CURRENT_REQUEST
            return conn.get(q=q, args={}, obj_type=FlexRequest)

    def add_request(self, request: FlexRequest) -> FlexRequest:
        with ConnectionWrapper() as conn:
            q = self.flex_request_query.INSERT_REQUEST
            create_ts = conn.insert(q=q, args=vars(request), return_id_col="create_ts")
            assert create_ts == request.create_ts
            return request

    def list_offer(self, ) -> List[FlexOffer]:
        with ConnectionWrapper() as conn:
            # args = {"ts_from": ts.ts_from, "ts_to": ts.ts_to}
            q = self.flex_offer_queries.LIST_OFFER
            requests = conn.select(q=q, args={}, obj_type=FlexOffer)
            return requests

    def list_flex_offer(self, flex_request_uri: str) -> List[FlexOffer]:
        with ConnectionWrapper() as conn:
            q = self.flex_offer_queries.LIST_REQUEST_OFFER
            return conn.select(q=q, args={"flex_request_uri": flex_request_uri}, obj_type=FlexOffer)

    def add_offer(self, offers: List[FlexOffer]) -> List[FlexOffer]:
        with ConnectionWrapper() as conn:
            q = self.flex_offer_queries.INSERT_OFFER
            update_ts = conn.insert_batch(q=q, arg_list=[vars(offer) for offer in offers], return_id_col="update_ts")
            for i, u_ts in enumerate(update_ts):
                offers[i].update_ts = u_ts
            return offers

    def list_price_offer(self, flex_request_uri: str) -> List[FlexPriceOffer]:
        with ConnectionWrapper() as conn:
            q = self.flex_offer_queries.LIST_PRICE_OFFER
            return conn.select(q=q, args={"flex_request_uri": flex_request_uri}, obj_type=FlexPriceOffer)

    def add_offer_price(self, offers: List[FlexPriceOffer]) -> List[FlexPriceOffer]:
        with ConnectionWrapper() as conn:
            for o in offers:
                flex_offer: Optional[FlexPriceOffer] = conn.get(q=self.flex_offer_queries.GET_REQUEST_OFFER,
                                                                args={"flex_request_uri": o.flex_request_uri,
                                                                      "asset_manager_uri": o.asset_manager_uri},
                                                                obj_type=FlexPriceOffer)
                if flex_offer is None:
                    raise ValueError(f"Offer for {o.flex_request_uri}:{o.asset_manager_uri} not found")
                assert flex_offer.flex_value == o.flex_value
                conn.update(q=self.flex_offer_queries.UPDATE_OFFER_PRICE,
                            args={"price_value": o.price_value})
                cost_update_ts = conn.get(q=self.flex_offer_queries.GET_REQUEST_OFFER,
                                          args={"flex_request_uri": o.flex_request_uri,
                                                "asset_manager_uri": o.asset_manager_uri},
                                          obj_type=FlexPriceOffer).cost_update_ts
                o.cost_update_ts = cost_update_ts
            return offers

    ###########

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
