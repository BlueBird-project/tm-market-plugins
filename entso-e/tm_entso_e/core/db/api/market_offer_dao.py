from abc import abstractmethod
from datetime import tzinfo, timezone
from typing import List, Union, Optional, Dict, Any, Tuple

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from schemas.market import MarketOfferDetails, MarketOffer


class MarketOfferDAO(DAO):
    def __init__(self, table_prefix: str):
        super(MarketOfferDAO, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def register_day_offer(self, offer_details: MarketOfferDetails) -> MarketOfferDetails:
        pass

    @abstractmethod
    def log_day_offer(self, market_offers: List[MarketOffer]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def clear_offer(self, offer_id: int) -> Any:
        pass

    @abstractmethod
    def get_recent_dayahead_details(self, market_id: Optional[int] = None) -> List[MarketOfferDetails]:
        pass

    @abstractmethod
    def get_recent_intraday_details(self, market_id: Optional[int] = None, sequence: Optional[int] = None) -> \
            List[MarketOfferDetails]:
        pass

    @abstractmethod
    def get_recent_dayahead(self, market_id: Optional[int] = None) -> List[MarketOffer]:
        pass

    @abstractmethod
    def get_recent_intraday(self, market_id: Optional[int] = None, sequence: Optional[int] = None) -> List[MarketOffer]:
        pass

    @abstractmethod
    def get_offer_details_by_id(self, offer_id: int) -> Optional[MarketOfferDetails]:
        pass

    @abstractmethod
    def get_offer_details(self, market_id: int, ts_start: int, sequence: Optional[int]) -> Optional[MarketOfferDetails]:
        pass

    @abstractmethod
    def get_offer(self, offer_id: int) -> List[MarketOffer]:
        pass

    @abstractmethod
    def list_offers(self, ts: TimeSpan, market_id: Optional[int] = None, sequence: Optional[int] = None) \
            -> List[MarketOffer]:
        pass
