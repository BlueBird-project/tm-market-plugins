from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_entso_e.core.db.api.market_dao import MarketAPI
from tm_entso_e.schemas.market_dao import MarketDAO


class MarketQueries:
    # TODO: list columns instead of *
    LIST_MARKET = """SELECT "market_id","market_uri", "market_name", "market_type", 
    "market_description", "market_location",  "subscribe", "update_ts", "ext"
    FROM "${table_prefix}market_details"    """
    LIST_SUBSCRIBED_MARKET = """SELECT "market_id","market_uri", "market_name", "market_type", 
    "market_description", "market_location",  "subscribe", "update_ts", "ext"
    FROM "${table_prefix}market_details"  WHERE "subscribe"   """
    SELECT_MARKET_BY_URI = """SELECT "market_id","market_uri", "market_name", "market_type", 
    "market_description", "market_location",  "subscribe", "update_ts", "ext"
    FROM "${table_prefix}market_details" WHERE market_uri = :market_uri   """

    SELECT_MARKET_BY_ID = """SELECT "market_id","market_uri", "market_name", "market_type", 
    "market_description", "market_location",  "subscribe", "update_ts", "ext"
    FROM "${table_prefix}market_details" WHERE market_id = :market_id   """

    INSERT_MARKET = """INSERT INTO "${table_prefix}market_details" 
    ("market_uri", "market_name", "market_type", "market_description", "market_location","subscribe",
      "update_ts", "ext") 
    VALUES (:market_uri,:market_name,:market_type, :market_description, :market_location, :subscribe ,
       extract(epoch from now()) * 1000,:ext) 
        """

    UPDATE_MARKET = """UPDATE "${table_prefix}market_details" 
    SET "market_name" =  :market_name , "market_type" = :market_type, "market_description" = :market_description,
    "market_location" =  :market_location, "subscribe" = :subscribe , "update_ts" =  extract(epoch from now()) * 1000 ,
    ext = :ext 
    WHERE market_id = :market_id and "market_uri" = :market_uri
    """
    # ON CONFLICT ("market_uri" ) DO UPDATE  todo:
    SET_MARKET_SUBSCRIBE = """UPDATE "${table_prefix}market_details"  set "subscribe" = :subscribe
     WHERE "market_id" = :market_id"""


class MarketAPIImpl(MarketAPI):

    def __init__(self, table_prefix: str):
        super(MarketAPI, self).__init__(table_prefix=table_prefix)
        self.queries: MarketQueries = self.build_queries(MarketQueries)

    def get_market(self, market_id: int) -> Optional[MarketDAO]:
        with ConnectionWrapper() as conn:
            args = {"market_id": market_id}
            market = conn.get(q=self.queries.SELECT_MARKET_BY_ID, args=args, obj_type=MarketDAO)
            return market

    def get_market_uri(self, market_uri: str) -> Optional[MarketDAO]:
        with ConnectionWrapper() as conn:
            args = {"market_uri": market_uri}
            market = conn.get(q=self.queries.SELECT_MARKET_BY_URI, args=args, obj_type=MarketDAO)
            return market

    def add_market(self, market: MarketDAO) -> MarketDAO:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_MARKET, args=vars(market),
                                      return_id_col="market_id")
            if inserted_id is None:
                raise ValueError(f"Market not saved: {market.__dict__}")
            market.market_id = inserted_id
            return market

    def update_market(self, market: MarketDAO):
        with ConnectionWrapper() as conn:
            inserted = conn.update(q=self.queries.UPDATE_MARKET, args=vars(market))
            if inserted == 0:
                raise ValueError(f"Market not updated: {market.__dict__}")

    def list_market(self) -> List[MarketDAO]:
        with ConnectionWrapper() as conn:
            args = {}
            markets = conn.select(q=self.queries.LIST_MARKET, args=args, obj_type=MarketDAO)
            return markets

    def set_subscribe(self, market_id: int, subscribe: bool) -> bool:
        with ConnectionWrapper() as conn:
            return conn.update(self.queries.SET_MARKET_SUBSCRIBE, {'market_id': market_id, "subscribe": subscribe}) == 1
