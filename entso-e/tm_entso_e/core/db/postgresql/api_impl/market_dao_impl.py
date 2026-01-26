from abc import ABC, abstractmethod
from datetime import tzinfo, timezone
from typing import List, Union, Optional, Dict, Any, Tuple

from effi_onto_tools.db import Pagination, TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper
from effi_onto_tools.utils import time_utils

from tm_entso_e.core.db.api.market_dao import MarketDAO
from schemas.market import Market


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
    # ON CONFLICT ("market_uri" ) DO UPDATE  todo:


class MarketDAOImpl(MarketDAO):

    def __init__(self, table_prefix: str):
        super(MarketDAO, self).__init__(table_prefix=table_prefix)
        self.queries: MarketQueries = self.build_queries(MarketQueries)

    def get_market(self, market_id: int) -> Optional[Market]:
        with ConnectionWrapper() as conn:
            args = {"market_id": market_id}
            market = conn.get(q=self.queries.SELECT_MARKET_BY_ID, args=args, obj_type=Market)
            return market

    def get_market_uri(self, market_uri: str) -> Optional[Market]:
        with ConnectionWrapper() as conn:
            args = {"market_uri": market_uri}
            market = conn.get(q=self.queries.SELECT_MARKET_BY_URI, args=args, obj_type=Market)
            return market

    def add_market(self, market: Market) -> Market:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_MARKET, args=vars(market),
                                      return_id_col="market_id")
            if inserted_id is None:
                raise ValueError(f"Market not saved: {market.__dict__}")
            market.market_id = inserted_id
            return market

    def list_market(self) -> List[Market]:
        with ConnectionWrapper() as conn:
            args = {}
            markets = conn.select(q=self.queries.LIST_MARKET, args=args, obj_type=Market)
            return markets
