from typing import List

from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_model import KECapacityNotification


async def sample_notification() -> List[KECapacityNotification]:
    from tm_capacity_pl.notification.modules.ke_interaction.service.capacity_market_service import init_message as init_ke_message
    from tm_capacity_pl.notification.modules.market.message_parser import process_message
    from tm_capacity_pl.notification.modules.market.message_generator import init_message
    msg = init_message(day=26, month=11, year=2026, time_from=17, time_to=18, ratio=0.555)
    market_notification = process_message(email=msg)
    return await init_ke_message(notification=market_notification)

async def post_sample_notification():
    from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_interactions import \
        post_notification
    notifications = await sample_notification()
    return post_notification(notifications=notifications)

def sample_email() ->str:
    from tm_capacity_pl.notification.modules.market.message_generator import init_message
    return init_message(day=26, month=11, year=2026, time_from=17, time_to=18, ratio=0.555)
