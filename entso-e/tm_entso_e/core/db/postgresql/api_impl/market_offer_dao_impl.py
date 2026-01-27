from typing import List, Optional, Dict, Any

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_entso_e.core.db.api.market_offer_dao import MarketOfferDAO
from tm_entso_e.modules.entso_e_web_api.model import MarketAgreementTypeCode
from tm_entso_e.schemas.market import MarketOffer, MarketOfferDetails


class MarketOfferQueries:
    GET_MARKET_OFFER_DETAILS_ID = """SELECT  "offer_id",  "market_id", "sequence", "currency_unit",
        "volume_unit",  "ts_start", "ts_end", "isp_unit",  "update_ts", "ext"
         FROM "${table_prefix}market_offer_details" WHERE offer_id = :offer_id """
    GET_MARKET_OFFER_DETAILS = """SELECT  "offer_id",  "market_id", "sequence", "currency_unit",
        "volume_unit",  "ts_start", "ts_end", "isp_unit",  "update_ts", "ext"
         FROM "${table_prefix}market_offer_details" 
         WHERE market_id = :market_id AND ts_start=:ts_start and (sequence is null or sequence=:sequence) """

    LIST_MARKET_OFFER_DETAILS = """SELECT offer_details."offer_id", offer_details."market_id",offer_details."sequence",
     offer_details."currency_unit", offer_details."volume_unit", offer_details."ts_start", offer_details."ts_end",
      offer_details."isp_unit", offer_details."update_ts", offer_details."ext" 
      FROM "${table_prefix}market_offer_details" as offer_details
    JOIN "${table_prefix}market_details as md ON md.market_id = offer_details.market_id 
     WHERE COALESCE(:market_id = md.market_id,TRUE) AND COALESCE(:market_type = md.market_type,TRUE)
      AND ( :sequence is NULL OR  :sequence = offer_details.sequence )  
      AND coalesce (:max_ts=offer_details."ts_end") """

    GET_MARKET_OFFER_DETAILS_LAST_TS = """SELECT  max(offer_details."ts_end") as ts_end
    FROM "${table_prefix}market_offer_details" as offer_details
    JOIN "${table_prefix}market_details as md ON md.market_id = offer_details.market_id 
     WHERE COALESCE(:market_id = md.market_id,TRUE) AND COALESCE(:market_type = md.market_type,TRUE)
      AND ( :sequence is NULL OR  :sequence = offer_details.sequence )  """

    SELECT_MARKET_OFFER_BY_ID = """SELECT "ts","offer_id", "isp_start","isp_len", "cost"  ,"update_ts" 
    FROM "${table_prefix}market_offer" WHERE offer_id = :offer_id   """

    INSERT_MARKET_OFFER_DETAILS = """  INSERT INTO "${table_prefix}market_offer_details" 
    ("market_id", "sequence", "currency_unit",  "volume_unit", "ts_start", "ts_end", "isp_unit",  "update_ts", "ext")
    VALUES (:market_id, :sequence,:currency_unit,:volume_unit, :ts_start, :ts_end, :isp_unit,   extract(epoch from now()) * 1000, :ext)   """
    #     TODO: on conflict

    INSERT_MARKET_OFFER = """  INSERT INTO "${table_prefix}market_offer" 
    ("ts","offer_id", "isp_start","isp_len", "cost"  ,"update_ts" )
    VALUES (:ts, :offer_id, :isp_start, :isp_len, :cost, extract(epoch from now()) * 1000 )   """
    DELETE_MARKET_OFFER = """  DELETE FROM "${table_prefix}market_offer" WHERE offer_id=:offer_id   """


class MarketOfferDAOImpl(MarketOfferDAO):
    def __init__(self, table_prefix: str):
        super(MarketOfferDAO, self).__init__(table_prefix=table_prefix)
        self.queries: MarketOfferQueries = self.build_queries(MarketOfferQueries)

    def get_recent_dayahead_details(self, market_id: Optional[int] = None) -> List[MarketOfferDetails]:
        with ConnectionWrapper() as conn:
            args = {"market_id": market_id, "sequence": None, "market_type": None}
            max_ts = conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS_LAST_TS, args=args)
            max_ts = max_ts[0] if max_ts is not None else None
            args["max_ts"] = max_ts
            offers = conn.select(q=self.queries.LIST_MARKET_OFFER_DETAILS, args=args, obj_type=MarketOfferDetails)
            return offers

    def get_recent_intraday_details(self, market_id: Optional[int] = None, sequence: Optional[int] = None) -> \
            List[MarketOfferDetails]:
        with ConnectionWrapper() as conn:
            args = {"market_id": market_id, "sequence": None, "market_type": MarketAgreementTypeCode.INTRADAY}
            max_ts = conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS_LAST_TS, args=args)
            max_ts = max_ts[0] if max_ts is not None else None
            args["max_ts"] = max_ts
            offers = conn.select(q=self.queries.LIST_MARKET_OFFER_DETAILS, args=args, obj_type=MarketOfferDetails)
            return offers

    def get_recent_dayahead(self, market_id: Optional[int] = None) -> List[MarketOffer]:
        offers_details = self.get_recent_dayahead_details(market_id=market_id)
        res = []
        with ConnectionWrapper() as conn:
            for od in offers_details:
                res += conn.select(q=self.queries.SELECT_MARKET_OFFER_BY_ID, args={"offer_id": od.offer_id},
                                   obj_type=MarketOffer)

        return res

    def get_recent_intraday(self, market_id: Optional[int] = None, sequence: Optional[int] = None) -> List[MarketOffer]:
        offers_details = self.get_recent_intraday_details(market_id=market_id, sequence=sequence)
        res = []
        with ConnectionWrapper() as conn:
            for od in offers_details:
                res += conn.select(q=self.queries.SELECT_MARKET_OFFER_BY_ID, args={"offer_id": od.offer_id},
                                   obj_type=MarketOffer)

        return res

    def get_offer_details_by_id(self, offer_id: int) -> Optional[MarketOfferDetails]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS_ID, args={"offer_id": offer_id},
                            obj_type=MarketOfferDetails)

    def get_offer_details(self, market_id: int, ts_start: int, sequence: Optional[int]) -> Optional[MarketOfferDetails]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS,
                            args={"market_id": market_id, "ts_start": ts_start, "sequence": sequence},
                            obj_type=MarketOfferDetails)

    def get_offer(self, offer_id: int) -> List[MarketOffer]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.SELECT_MARKET_OFFER_BY_ID, args={"offer_id": offer_id},
                               obj_type=MarketOffer)

    def list_offers(self, ts: TimeSpan, market_id: Optional[int] = None, sequence: Optional[int] = None) \
            -> List[MarketOffer]:
        # TODO: impelements
        pass

    def register_day_offer(self, offer_details: MarketOfferDetails) -> MarketOfferDetails:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_MARKET_OFFER_DETAILS, args=vars(offer_details),
                                      return_id_col="offer_id")
            if inserted_id is None:
                raise ValueError(f"Market not saved: {offer_details.__dict__}")
            offer_details.offer_id = inserted_id
            return offer_details

    def log_day_offer(self, market_offers: List[MarketOffer]) -> List[Dict[str, Any]]:
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.queries.INSERT_MARKET_OFFER,
                                         arg_list=[vars(mo) for mo in market_offers],
                                         return_id_col=["ts", "isp_start", "update_ts"], fail_safe=False)
            return [{k: v for k, v in zip(["ts", "isp_start", "update_ts"], r)} for r in inserted]

    def clear_offer(self, offer_id: int) -> int:
        with ConnectionWrapper() as conn:
            deleted = conn.update(q=self.queries.DELETE_MARKET_OFFER,
                                         args={"offer_id":offer_id},  )
            return deleted
