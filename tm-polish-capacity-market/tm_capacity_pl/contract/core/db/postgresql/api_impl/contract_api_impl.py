from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_capacity_pl.contract.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.contract.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.contract.core.db.postgresql.api_impl.asset_manager_api_impl import AssetManagerQueries
from tm_capacity_pl.models.contract import FlexRequest, FlexOffer, FlexPriceOffer, FlexContract, FlexAssetContract


class FlexRequestQueries(QueryObject):
    __TABLE_NAME__ = "flex_request"

    __PROJECTION__ = """ ${table_alias}."flex_request_uri", ${table_alias}."offer_period_uri",
     ${table_alias}."create_ts",    ${table_alias}."create_ts", ${table_alias}."ts_from",${table_alias}."ts_to"  """
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


# FlexAssetContract

class ContractQueries(QueryObject):
    __TABLE_NAME__ = "flex_contract"

    __PROJECTION__ = """ ${table_alias}."contract_uri", ${table_alias}."flex_request_uri", ${table_alias}."ack_ts",
     ${table_alias}."update_ts", ${table_alias}."flex_value", ${table_alias}."price_value" """

    FIND_CURRENT_CONTRACT = """SELECT ${projection} , asset_table.asset_manager_uri  ,asset_table.asset_manager_id
        FROM "${table_prefix}${table_name}" as ${table_alias} , request_table.ts_from, request_table.ts_to
        LEFT JOIN  "${table_prefix}""" + AssetManagerQueries.__TABLE_NAME__ + """ as asset_table 
        on ${table_prefix}.asset_manager_id = asset_table.asset_manager_id = 
        LEFT JOIN  "${table_prefix}""" + FlexRequestQueries.__TABLE_NAME__ + """ as request_table 
        on request_table.flex_request_uri =  ${table_alias}."flex_request_uri"
        LEFT JOIN ( SELECT MAX("create_ts") as max_create_ts FROM
            "${table_prefix}""" + FlexRequestQueries.__TABLE_NAME__ + """" ) _t
             on _t.max_create_ts = request_table.create_ts 
        WHERE     coalesce(  asset_table.asset_manager_uri =:asset_manager_uri,TRUE)
    """

    INSERT_CONTRACT = """INSERT INTO ${table_prefix}${table_name} 
    (contract_uri, flex_request_uri,asset_manager_id ack_ts, flex_value, price_value,  update_ts)
    VALUES
     (:contract_uri, :flex_request_uri,:asset_manager_id, :ack_ts, :flex_value, :price_value,
     extract(epoch from now()) * 1000) """


class ContractAPIImpl(ContractAPI):

    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)
        self.flex_request_query: FlexRequestQueries = self.build_queries(FlexRequestQueries)
        self.flex_offer_queries: FlexOfferQueries = self.build_queries(FlexOfferQueries)
        self.contract_queries: ContractQueries = self.build_queries(ContractQueries)

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

    def get_current_contracts(self, asset_manager_uri: Optional[str] = None) -> List[FlexAssetContract]:
        with ConnectionWrapper() as conn:
            contract = conn.get(q=self.contract_queries.FIND_CURRENT_CONTRACT,
                                args={"asset_manager_uri": asset_manager_uri}, obj_type=FlexAssetContract)

            return contract

    def add_contract(self, contract: FlexContract) -> FlexContract:
        with ConnectionWrapper() as conn:
            update_ts = conn.insert(q=self.contract_queries.INSERT_CONTRACT, args=vars(contract),
                                    return_id_col=["update_ts"])
            contract.update_ts = update_ts

            return contract
