from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db.dao import DAO

from tm_entso_e.schemas.market_dao import MarketDAO


class MarketAPI(DAO):
    def __init__(self, table_prefix: str):
        super(MarketAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_market(self) -> List[MarketDAO]:
        pass

    @abstractmethod
    def get_market(self, market_id: int) -> Optional[MarketDAO]:
        pass

    @abstractmethod
    def get_market_uri(self, market_uri: str) -> Optional[MarketDAO]:
        pass

    @abstractmethod
    def add_market(self, market: MarketDAO) -> MarketDAO:
        pass

    @abstractmethod
    def set_subscribe(self, market_id: int, subscribe: bool) -> bool:
        pass
