from abc import abstractmethod
from typing import List, Optional, Dict, Any

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_entso_e.schemas.market_dao import MarketOfferDetailsDAO, MarketOfferDAO


class MarketOfferAPI(DAO):
    def __init__(self, table_prefix: str):
        super(MarketOfferAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def register_day_offer(self, offer_details: MarketOfferDetailsDAO) -> MarketOfferDetailsDAO:
        pass

    @abstractmethod
    def log_day_offer(self, market_offers: List[MarketOfferDAO]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_offer_details_by_id(self, offer_id: int) -> Optional[MarketOfferDetailsDAO]:
        pass

    @abstractmethod
    def get_offer_details_by_uri(self, offer_uri: str) -> Optional[MarketOfferDetailsDAO]:
        pass

    @abstractmethod
    def clear_offer(self, offer_id: int) -> Any:
        pass

    @abstractmethod
    def get_recent_dayahead_details(self, sequence: Optional[str] = None) -> List[MarketOfferDetailsDAO]:
        pass

    @abstractmethod
    def get_recent_intraday_details(self, sequence: Optional[str] = None) -> List[MarketOfferDetailsDAO]:
        pass

    @abstractmethod
    def get_recent_market_details(self, market_id: Optional[int] = None, sequence: Optional[str] = None,
                                  market_type: Optional[str] = None) -> List[MarketOfferDetailsDAO]:
        pass

    @abstractmethod
    def get_recent_dayahead(self, sequence: Optional[str] = None) -> List[MarketOfferDAO]:
        pass

    @abstractmethod
    def get_recent_intraday(self, sequence: Optional[str] = None) -> List[MarketOfferDAO]:
        pass

    @abstractmethod
    def get_recent_market_offer(self, market_id: Optional[int] = None, sequence: Optional[str] = None) \
            -> List[MarketOfferDAO]:
        pass

    @abstractmethod
    def find_offer_details(self, ti: TimeSpan, market_id: Optional[int] = None, sequence: Optional[str] = None,
                           market_type: Optional[str] = None) -> List[MarketOfferDetailsDAO]:
        pass

    @abstractmethod
    def get_offer_details(self, market_id: int, ts_start: int, sequence: Optional[str]) -> Optional[MarketOfferDetailsDAO]:
        pass

    @abstractmethod
    def get_offer(self, offer_id: int) -> List[MarketOfferDAO]:
        pass

    @abstractmethod
    def list_offers(self, ts: TimeSpan, market_id: Optional[int] = None, sequence: Optional[str] = None) \
            -> List[MarketOfferDAO]:
        pass
