from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.contract import FlexRequest, FlexOffer, FlexPriceOffer, FlexContract


class ContractAPI(DAO):
    def __init__(self, table_prefix: str):
        super(ContractAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list_request(self, ts: TimeSpan) -> List[FlexRequest]:
        pass

    @abstractmethod
    def current_request(self, ) -> Optional[FlexRequest]:
        pass

    @abstractmethod
    def add_request(self, request: FlexRequest) -> FlexRequest:
        pass

    @abstractmethod
    def list_offer(self, ) -> List[FlexOffer]:
        pass

    @abstractmethod
    def list_flex_offer(self, flex_request_uri: str) -> List[FlexOffer]:
        pass

    @abstractmethod
    def add_offer(self, offers: List[FlexOffer]) -> List[FlexOffer]:
        pass

    @abstractmethod
    def list_price_offer(self, flex_request_uri: str) -> List[FlexPriceOffer]:
        pass

    @abstractmethod
    def add_offer_price(self, offers: List[FlexPriceOffer]) -> List[FlexPriceOffer]:
        pass

    @abstractmethod
    def get_current(self, asset_manager_uri: Optional[str] = None) -> List[FlexContract]:
        pass

    @abstractmethod
    def add_contract(self, contract: FlexContract) -> FlexContract:
        pass
