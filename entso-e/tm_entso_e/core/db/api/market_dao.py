from abc import abstractmethod
from datetime import tzinfo, timezone
from typing import List, Union, Optional, Dict, Any, Tuple

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from schemas.market import Market


class MarketDAO(DAO):
    def __init__(self, table_prefix: str):
        super(MarketDAO, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_market(self) -> List[Market]:
        pass

    @abstractmethod
    def get_market(self, market_id: int) -> Optional[Market]:
        pass

    @abstractmethod
    def get_market_uri(self, market_uri: str) -> Optional[Market]:
        pass

    @abstractmethod
    def add_market(self, market: Market) -> Market:
        pass
