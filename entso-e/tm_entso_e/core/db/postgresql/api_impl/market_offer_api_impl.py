from typing import List, Optional, Dict, Any

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper

from tm_entso_e.core.db.api.market_offer_dao import MarketOfferAPI
from tm_entso_e.modules.entso_e_web_api.model import MarketAgreementTypeCode
from tm_entso_e.schemas.market import MarketOfferValues, MarketOfferValuesState
from tm_entso_e.schemas.market_dao import MarketOfferDAO, MarketOfferDetailsDAO
from tm_entso_e.utils import time_utils


class MarketOfferQueries:
    GET_MARKET_OFFER_DETAILS_ID = """SELECT  "offer_id",  "market_id", "offer_uri", "sequence", "currency_unit",
        "volume_unit",  "ts_start", "ts_end", "isp_unit", "created_ts", "update_ts", "ext"
         FROM "${table_prefix}market_offer_details" WHERE offer_id = :offer_id """
    GET_MARKET_OFFER_DETAILS_URI = """SELECT  "offer_id",  "market_id", "offer_uri", "sequence", "currency_unit",
        "volume_unit",  "ts_start", "ts_end", "isp_unit",  "created_ts",  "update_ts", "ext"
         FROM "${table_prefix}market_offer_details" WHERE "offer_uri" = :offer_uri """
    FIND_MARKET_OFFER_DETAILS = """SELECT offer_details."offer_id",offer_details."market_id",offer_details."offer_uri",
     offer_details."sequence",offer_details."currency_unit", offer_details."volume_unit", offer_details."ts_start", 
     offer_details."ts_end", offer_details."isp_unit", offer_details."created_ts",offer_details."update_ts",
      offer_details."ext" 
    FROM "${table_prefix}market_offer_details" as offer_details
    JOIN "${table_prefix}market_details" as md ON md.market_id = offer_details.market_id 
    WHERE COALESCE(:market_id =  md.market_id,TRUE) AND COALESCE(:market_type = md.market_type,TRUE)
        AND ( :sequence is NULL OR  :sequence =  offer_details.sequence )  
        AND ( coalesce(:ts_from<=offer_details."ts_end",TRUE) and  coalesce(:ts_to>=offer_details."ts_start",TRUE))
       """
    GET_MARKET_OFFER_DETAILS = """SELECT  "offer_id",  "market_id","offer_uri", "sequence", "currency_unit",
        "volume_unit",  "ts_start", "ts_end", "isp_unit",  "created_ts",  "update_ts", "ext"
         FROM "${table_prefix}market_offer_details" 
         WHERE market_id = :market_id AND ts_start=:ts_start and (sequence is null or sequence=:sequence) """

    LIST_MARKET_OFFER_DETAILS = """SELECT offer_details."offer_id",offer_details."market_id",offer_details."offer_uri",
     offer_details."sequence",offer_details."currency_unit", offer_details."volume_unit", offer_details."ts_start", 
     offer_details."ts_end", offer_details."isp_unit", offer_details."created_ts", offer_details."update_ts", offer_details."ext" 
    FROM "${table_prefix}market_offer_details" as offer_details
    JOIN "${table_prefix}market_details" as md ON md.market_id = offer_details.market_id 
     WHERE COALESCE(:market_id = md.market_id,TRUE) AND COALESCE(:market_type = md.market_type,TRUE)
      AND ( :sequence is NULL OR  :sequence = offer_details.sequence )  
      AND coalesce (:max_ts=offer_details."ts_end") """

    GET_MARKET_OFFER_DETAILS_LAST_TS = """SELECT  max(offer_details."ts_end") as max_ts
    FROM "${table_prefix}market_offer_details" as offer_details
    JOIN "${table_prefix}market_details" as md ON md.market_id = offer_details.market_id 
     WHERE COALESCE(:market_id = md.market_id,TRUE) AND COALESCE(:market_type = md.market_type,TRUE)
      AND ( :sequence is NULL OR  :sequence = offer_details.sequence )  """

    SELECT_MARKET_OFFER_BY_ID = """SELECT "ts","offer_id", "isp_start","isp_len", "cost"  ,"update_ts" 
    FROM "${table_prefix}market_offer" WHERE offer_id = :offer_id   """

    SELECT_MARKET_OFFER_VALUES = """ SELECT 
        mod.offer_id,mod.sequence,mod.currency_unit,mod.volume_unit,mod.isp_unit,mod.ts_start,
        mo.ts, mo.isp_start, mo.isp_len, mo.cost 
        FROM "${table_prefix}market_offer_details" mod 
        JOIN "${table_prefix}market_offer" mo on mod."offer_id"=mo."offer_id" 
        WHERE mod.market_id = :market_id 
        AND ( coalesce(:ts_from<=mod."ts_end",TRUE) and  coalesce(:ts_to>=mod."ts_start",TRUE))
        ORDER BY sequence, ts_start"""
    VERIFY_MARKET_OFFER_VALUES = """ SELECT "${table_prefix}market_offer".offer_id, 
       count(*) as data_points, (sum(isp_len) = 48 or sum(isp_len) = 96 ) as "state", sum(isp_len) as total_isp_span,
       "${table_prefix}market_offer_details".ts_start, "${table_prefix}market_offer_details".sequence,
       "${table_prefix}market_offer_details".market_id ,"${table_prefix}market_details"."market_location"
    FROM "${table_prefix}market_offer" 
    JOIN "${table_prefix}market_offer_details" 
    ON "${table_prefix}market_offer_details"."offer_id"="${table_prefix}market_offer".offer_id
    JOIN ${table_prefix}market_details 
    ON ${table_prefix}market_details."market_id" = ${table_prefix}market_offer_details."market_id"
    WHERE ${table_prefix}market_offer_details.ts_start < :ts_to
     AND ${table_prefix}market_offer_details.ts_end > :ts_from
     AND COALESCE("${table_prefix}market_offer_details".market_id = :market_id,TRUE )
     AND COALESCE("${table_prefix}market_details".market_location = :market_location,TRUE )
    GROUP BY "${table_prefix}market_offer".offer_id ,"${table_prefix}market_offer_details".ts_start,
    "${table_prefix}market_offer_details".sequence, "${table_prefix}market_offer_details".market_id ,
    "${table_prefix}market_details"."market_location"
    ORDER BY "${table_prefix}market_offer_details".market_id , "${table_prefix}market_offer_details".sequence,
      ${table_prefix}market_offer_details.ts_start  """

    INSERT_MARKET_OFFER_DETAILS = """  INSERT INTO "${table_prefix}market_offer_details" 
    ("market_id", "offer_uri","sequence", "currency_unit",  "volume_unit", "ts_start", "ts_end", "isp_unit",
     "created_ts","update_ts", "ext")
    VALUES (:market_id,:offer_uri, :sequence,:currency_unit,:volume_unit, :ts_start, :ts_end, :isp_unit,
       :created_ts, extract(epoch from now()) * 1000, :ext)   """
    #     TODO: on conflict

    INSERT_MARKET_OFFER = """  INSERT INTO "${table_prefix}market_offer" 
    ("ts","offer_id", "isp_start","isp_len", "cost"  ,"update_ts" )
    VALUES (:ts, :offer_id, :isp_start, :isp_len, :cost, extract(epoch from now()) * 1000 )   """
    DELETE_MARKET_OFFER = """  DELETE FROM "${table_prefix}market_offer" WHERE offer_id=:offer_id   """


class MarketOfferAPIImpl(MarketOfferAPI):

    def __init__(self, table_prefix: str):
        super(MarketOfferAPI, self).__init__(table_prefix=table_prefix)
        self.queries: MarketOfferQueries = self.build_queries(MarketOfferQueries)

    def get_recent_dayahead_details(self, sequence: Optional[str] = None) \
            -> List[MarketOfferDetailsDAO]:
        return self.get_recent_market_details(market_id=None, sequence=sequence,
                                              market_type=MarketAgreementTypeCode.DAY_AHEAD.name)

    def get_recent_intraday_details(self, sequence: Optional[str] = None) -> List[MarketOfferDetailsDAO]:
        return self.get_recent_market_details(market_id=None, sequence=sequence,
                                              market_type=MarketAgreementTypeCode.INTRADAY.name)

    def get_recent_market_details(self, market_id: Optional[int] = None, sequence: Optional[str] = None,
                                  market_type: Optional[str] = None) -> List[MarketOfferDetailsDAO]:
        with ConnectionWrapper() as conn:
            args = {"market_id": market_id, "sequence": sequence, "market_type": None}
            max_ts = conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS_LAST_TS, args=args)
            max_ts = max_ts.max_ts if max_ts is not None else None
            if max_ts is None or max_ts < time_utils.current_timestamp():
                return []
            args["max_ts"] = max_ts
            offers = conn.select(q=self.queries.LIST_MARKET_OFFER_DETAILS, args=args, obj_type=MarketOfferDetailsDAO)
            return offers

    def get_recent_dayahead(self, sequence: Optional[str] = None) -> List[MarketOfferDAO]:
        offers_details = self.get_recent_dayahead_details(sequence=sequence)
        res = []
        with ConnectionWrapper() as conn:
            for od in offers_details:
                res += conn.select(q=self.queries.SELECT_MARKET_OFFER_BY_ID, args={"offer_id": od.offer_id},
                                   obj_type=MarketOfferDAO)

        return res

    def get_recent_intraday(self, sequence: Optional[str] = None) -> List[MarketOfferDAO]:
        offers_details = self.get_recent_intraday_details(sequence=sequence)
        res = []
        with ConnectionWrapper() as conn:
            for od in offers_details:
                res += conn.select(q=self.queries.SELECT_MARKET_OFFER_BY_ID, args={"offer_id": od.offer_id},
                                   obj_type=MarketOfferDAO)

        return res

    def get_recent_market_offer(self, market_id: Optional[int] = None, sequence: Optional[str] = None) \
            -> List[MarketOfferDAO]:
        offers_details = self.get_recent_market_details(market_id=market_id, sequence=sequence)
        res = []
        with ConnectionWrapper() as conn:
            for od in offers_details:
                res += conn.select(q=self.queries.SELECT_MARKET_OFFER_BY_ID, args={"offer_id": od.offer_id},
                                   obj_type=MarketOfferDAO)

        return res

    def get_offer_details_by_id(self, offer_id: int) -> Optional[MarketOfferDetailsDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS_ID, args={"offer_id": offer_id},
                            obj_type=MarketOfferDetailsDAO)

    def get_offer_details_by_uri(self, offer_uri: str) -> Optional[MarketOfferDetailsDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS_URI, args={"offer_uri": offer_uri},
                            obj_type=MarketOfferDetailsDAO)

    def find_offer_details(self, ti: TimeSpan, market_id: Optional[int] = None, sequence: Optional[str] = None,
                           market_type: Optional[str] = None) -> List[MarketOfferDetailsDAO]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.FIND_MARKET_OFFER_DETAILS,
                               args={"market_id": market_id, "sequence": sequence, "market_type": market_type,
                                     "ts_from": ti.ts_from, "ts_to": ti.ts_to},
                               obj_type=MarketOfferDetailsDAO)

    def get_offer_details(self, market_id: int, ts_start: int, sequence: Optional[str]) -> Optional[
        MarketOfferDetailsDAO]:
        with ConnectionWrapper() as conn:
            return conn.get(q=self.queries.GET_MARKET_OFFER_DETAILS,
                            args={"market_id": market_id, "ts_start": ts_start, "sequence": sequence},
                            obj_type=MarketOfferDetailsDAO)

    def get_offer(self, offer_id: int) -> List[MarketOfferDAO]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.SELECT_MARKET_OFFER_BY_ID, args={"offer_id": offer_id},
                               obj_type=MarketOfferDAO)

    def list_offers(self, ts: TimeSpan, market_id: Optional[int] = None, sequence: Optional[str] = None) \
            -> List[MarketOfferDAO]:
        # TODO: impelements
        pass

    def register_day_offer(self, offer_details: MarketOfferDetailsDAO) -> MarketOfferDetailsDAO:
        with ConnectionWrapper() as conn:
            inserted_id = conn.insert(q=self.queries.INSERT_MARKET_OFFER_DETAILS, args=vars(offer_details),
                                      return_id_col="offer_id")
            if inserted_id is None:
                raise ValueError(f"Market not saved: {offer_details.__dict__}")
            offer_details.offer_id = inserted_id
            return offer_details

    def log_day_offer(self, market_offers: List[MarketOfferDAO]) -> List[Dict[str, Any]]:
        with ConnectionWrapper() as conn:
            inserted = conn.insert_batch(q=self.queries.INSERT_MARKET_OFFER,
                                         arg_list=[vars(mo) for mo in market_offers],
                                         return_id_col=["ts", "isp_start", "update_ts"], fail_safe=False)
            return [{k: v for k, v in zip(["ts", "isp_start", "update_ts"], r)} for r in inserted]

    def clear_offer(self, offer_id: int) -> int:
        with ConnectionWrapper() as conn:
            deleted = conn.update(q=self.queries.DELETE_MARKET_OFFER,
                                  args={"offer_id": offer_id}, )
            return deleted

    def get_offer_values(self, ti: TimeSpan, market_id: Optional[int] = None) -> List[MarketOfferValues]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.SELECT_MARKET_OFFER_VALUES,
                               args={"market_id": market_id, "ts_from": ti.ts_from, "ts_to": ti.ts_to},
                               obj_type=MarketOfferValues)

    def verify_stored_offers(self, ti: TimeSpan, market_id: Optional[int] = None,
                             market_location: Optional[str] = None) -> List[MarketOfferValuesState]:
        with ConnectionWrapper() as conn:
            return conn.select(q=self.queries.VERIFY_MARKET_OFFER_VALUES,
                               args={"market_id": market_id, "market_location": market_location, "ts_from": ti.ts_from,
                                     "ts_to": ti.ts_to},
                               obj_type=MarketOfferValuesState)
