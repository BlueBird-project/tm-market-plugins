from abc import abstractmethod
from typing import List, Optional

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.db.dao import DAO

from tm_capacity_pl.models.demand import MarketNotificationEntity

from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_model import KECapacityNotification


class NotificationAPI(DAO):
    def __init__(self, table_prefix: str):
        super(NotificationAPI, self).__init__(table_prefix=table_prefix)

    @abstractmethod
    def list(self, ts: Optional[TimeSpan] = None) -> List[MarketNotificationEntity]:
        pass

    @abstractmethod
    def get_by_date(self, date: str) -> List[MarketNotificationEntity]:
        pass

    @abstractmethod
    def get_current(self, ) -> List[MarketNotificationEntity]:
        pass

    @abstractmethod
    def add(self, notification: MarketNotificationEntity) -> MarketNotificationEntity:
        pass

    @abstractmethod
    def add_ke_notification(self, ke_notification: KECapacityNotification) -> KECapacityNotification:
        pass

    @abstractmethod
    def list_ke_notification(self, ts: Optional[TimeSpan] = None) -> List[KECapacityNotification]:
        pass
