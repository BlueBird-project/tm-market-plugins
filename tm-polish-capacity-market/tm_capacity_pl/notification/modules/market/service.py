from typing import Optional, List, Dict

from tm_capacity_pl.models.demand import PowerDemandDAO


async def message_handler(email: str):
    from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_interactions import \
        post_notification
    from tm_capacity_pl.notification.modules.ke_interaction.service.capacity_market_service import \
        init_ke_notification
    from tm_capacity_pl.notification.modules.ke_interaction.service.capacity_market_service import \
        get_current_notifications
    from tm_capacity_pl.notification.modules.ke_interaction.service.capacity_market_service import calc_power_obligation
    notifications = get_current_notifications(email)
    power_obligation: Dict[int, List[Optional[PowerDemandDAO]]] = \
        await calc_power_obligation(notifications=notifications)
    for d, demands in power_obligation.items():
        ke_notifications = init_ke_notification(day_ts=d, demands=[dem for dem in demands if dem is not None])
        print(ke_notifications)
        # todo log sending attempt
        post_notification(notifications=ke_notifications)
