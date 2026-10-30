from abc import abstractmethod
from typing import List, Optional
from zoneinfo import ZoneInfo

from effi_onto_tools.db import TimeSpan

from effi_onto_tools.db.postgresql.connection_wrapper import ConnectionWrapper
from tm_capacity_pl.core.db.postgresql.api_impl import QueryObject
from tm_capacity_pl.models.demand import MarketNotificationEntity, KECapacityNotification
from tm_capacity_pl.notification.core.db.api.notification_api import NotificationAPI


class KeNotificationQueries(QueryObject):
    __TABLE_NAME__ = "ke_notification"
    __PROJECTION__ = """ ${table_alias}."asset_manager_id",${table_alias}."flex_instruction_uri" ,
    ${table_alias}."flex_offer_uri"  ,${table_alias}."flex_profile_uri"  , 
    ${table_alias}."power_limit_uri",  ${table_alias}."ts"  ,  ${table_alias}."max_consumption_uri"   , 
     ${table_alias}."max_consumption_value" ,  ${table_alias}."update_ts"    """
    LIST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}  WHERE
     COALESCE(ts >= :ts_from, TRUE) and COALESCE(ts <= :ts_to, TRUE)      """

    INSERT = """INSERT INTO ${table_prefix}ke_notification 
    (asset_manager_id, flex_instruction_uri, flex_offer_uri, flex_profile_uri, power_limit_uri, ts,
     max_consumption_uri, max_consumption_value, update_ts)
    VALUES 
    (:asset_manager_id, :flex_instruction_uri, :flex_offer_uri, :flex_profile_uri,  :power_limit_uri, :ts, 
    :max_consumption_uri, :max_consumption_value, EXTRACT(epoch FROM current_timestamp) *1000))   """


class MarketNotificationQueries(QueryObject):
    __TABLE_NAME__ = "market_notification"
    __PROJECTION__ = """ ${table_alias}."notification_id",${table_alias}."email" ,
    ${table_alias}."date"  ,${table_alias}."isp"  ,   ${table_alias}."ts" ,   ${table_alias}."ratio"     """
    LIST = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias}  WHERE
     COALESCE(ts >= :ts_from, TRUE) and COALESCE(ts <= :ts_to, TRUE) order by ts ASC ,isp ASC     """
    GET_BY_DATE = """SELECT ${projection} FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        date = :date"""
    GET_CURRENT_DATE = """SELECT  ${table_alias}."date"  FROM "${table_prefix}${table_name}" as ${table_alias} WHERE
        ts = (SELECT  max("ts") FROM "${table_prefix}${table_name}") """

    INSERT = """INSERT INTO "${table_prefix}${table_name}" (email,  date,    isp, ratio,  ts) 
     VALUES (  :email,  :date,  :isp,  :ratio,   :ts )    """


class NotificationAPIImpl(NotificationAPI):
    def __init__(self, table_prefix: str):
        super(NotificationAPI, self).__init__(table_prefix=table_prefix)
        self.queries: KeNotificationQueries = self.build_queries(KeNotificationQueries)
        self.market_queries: MarketNotificationQueries = self.build_queries(MarketNotificationQueries)

    def list(self, ts: Optional[TimeSpan] = None) -> List[MarketNotificationEntity]:
        with ConnectionWrapper() as conn:
            notifications = conn.select(q=self.market_queries.LIST, args={"ts_from": ts.ts_from, "ts_to": ts.ts_to},
                                        obj_type=MarketNotificationEntity)
            return notifications

    def get_by_date(self, date: str) -> List[MarketNotificationEntity]:
        with ConnectionWrapper() as conn:
            notifications = conn.select(q=self.market_queries.LIST, args={"date": date}, obj_type=MarketNotificationEntity)
            return notifications

    def get_current(self, ) -> List[MarketNotificationEntity]:
        with ConnectionWrapper() as conn:
            max_date = conn.get(q=self.market_queries.GET_CURRENT_DATE, args={}, obj_type=MarketNotificationEntity)
            return self.get_by_date(date=max_date)

    def add(self, notification: MarketNotificationEntity) -> MarketNotificationEntity:
        with ConnectionWrapper() as conn:
            notification_id = conn.insert(q=self.market_queries.INSERT, args=vars(notification),
                                          return_id_col=["notification_id"])
            notification.notification_id = notification_id
            return notification

    def add_ke_notification(self, ke_notification: KECapacityNotification) -> KECapacityNotification:
        with ConnectionWrapper() as conn:
            update_ts = conn.insert(q=self.queries.INSERT, args=vars(ke_notification),
                                    return_id_col=["update_ts"])
            ke_notification.update_ts = update_ts
            return ke_notification

    def list_ke_notification(self, ts: Optional[TimeSpan] = None) -> List[KECapacityNotification]:
        with ConnectionWrapper() as conn:
            notifications = conn.select(q=self.queries.LIST, args={"ts_from": ts.ts_from, "ts_to": ts.ts_to},
                                        obj_type=KECapacityNotification)
            return notifications
