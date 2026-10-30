import logging
from typing import List, Dict, Optional

from ke_client.utils import time_utils
from rdflib import Literal

from tm_capacity_pl.models.demand import PowerDemandDAO, MarketNotificationEntity, AssetManager
from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_model import \
    KECapacityNotification, FlexContract
from tm_capacity_pl.notification.modules.market.message_parser import CapacityMarketNotification
from tm_capacity_pl.shared import POLAND_TZ
from tm_capacity_pl.utils import TimeSpan


def get_current_notifications(email: str) -> List[CapacityMarketNotification]:
    from tm_capacity_pl.notification.modules.market.message_parser import process_message
    from tm_capacity_pl.notification.core.db.postgresql import dao_manager

    current_notification: CapacityMarketNotification = process_message(email=email, tz=POLAND_TZ)

    dao_manager.notification_api.add(
        notification=MarketNotificationEntity(email=email, date=current_notification.date,
                                              isp=current_notification.start_time,
                                              ratio=current_notification.ratio,
                                              ts=current_notification.start_ts))
    notification_entities = dao_manager.notification_api.get_by_date(date=current_notification.date)
    notifications = [ne.convert_to_notification(tz_info=POLAND_TZ) for ne in notification_entities]
    return notifications
    # return [current_notification]


async def calc_power_obligation(notifications: List[CapacityMarketNotification]) \
        -> Dict[int, List[Optional[PowerDemandDAO]]]:
    if len(notifications) == 0:
        return {}
    from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_interactions import \
        request_consumption
    from tm_capacity_pl.notification.modules.market.power_obligation import calc_obligation
    x: CapacityMarketNotification
    notifications.sort(key=lambda x: x.start_time)
    current_notification = notifications[0]
    # Todo list work days and return min //max timestamp
    current_consumption = request_consumption(
        ts=TimeSpan(ts_from=(current_notification.end_ts - 24 * 25 * 3600000), ts_to=current_notification.end_ts))
    from tm_capacity_pl.models.contract import ConsumptionPower
    power_history = [ConsumptionPower(ts=cc.ts_ms, granularity_ms=3600000, value=cc.get_value()) for cc in
                     current_consumption]

    power_obligation: Dict[int, List[Optional[PowerDemandDAO]]]
    power_obligation = calc_obligation(notification=[current_notification], power_history=power_history,
                                       contracted_capacity=0)
    return power_obligation


def init_ke_notification(day_ts: int, demands: List[PowerDemandDAO]):
    from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_model import \
        FlexInstructionUri
    from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_model import \
        KECapacityNotification
    logging.info("Sending KE notification ")
    ke_notifications: List[KECapacityNotification] = []
    from tm_capacity_pl.notification.core.db.postgresql import dao_manager
    contracts = dao_manager.contract_api.get_current(contract_ack=True)
    for contract in contracts:
        flex_offer_uri = contract.flex_request_uri
        asset_manager_uri = contract.asset_manager_uri
        asset_manager_id = dao_manager.contract_api.get_asset_manager(
            asset_manager_uri=contract.asset_manager_uri).asset_manager_id
        for demand in demands:
            if demand is not None:
                fi = FlexInstructionUri(asset_manager_id=asset_manager_id, ts=day_ts)
                # TODO: verify timestamp
                n = KECapacityNotification(asset_manager=asset_manager_uri, flex_instruction=fi.uri_ref,
                                           flex_offer=flex_offer_uri,
                                           flex_profile=fi.profile_uri(), power_limit=fi.power_limit_uri(),
                                           ts=Literal(
                                               time_utils.xsd_from_ts(ts=demand.demand_start_ts_ms, tz=POLAND_TZ)),
                                           max_consumption=fi.power_limit_max_uri(),
                                           max_consumption_value=Literal(demand.max_power))
                ke_notifications.append(n)
    #     TODO: check if KE server filters by bindings , e.g. we want notifications only for our asset and not for other
    return ke_notifications


async def init_message(notification: CapacityMarketNotification) -> List[KECapacityNotification]:
    power_obligation: Dict[int, List[Optional[PowerDemandDAO]]] = await calc_power_obligation(
        notifications=[notification])
    for d, demands in power_obligation.items():
        ke_notifications = init_ke_notification(day_ts=d, demands=[dem for dem in demands if dem is not None])
        return ke_notifications


def store_contract(contract: FlexContract):
    from tm_capacity_pl.notification.core.db.postgresql import dao_manager
    dao_manager.contract_api.add_asset_manager(asset_manager=AssetManager(asset_manager_uri=contract.asset_manager))

    dao_manager.contract_api.add_contract(contract=contract)
