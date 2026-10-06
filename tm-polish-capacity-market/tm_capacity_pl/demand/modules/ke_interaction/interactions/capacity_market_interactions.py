from typing import List

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse

from tm_capacity_pl.demand.modules.ke_interaction.interactions.capacity_market_model import TMNotification

ki = KIHolder()


@ki.post("flex-demand")
def _post_notification(notifications: List[TMNotification]):
    return notifications


def post_notification(notifications: List[TMNotification]):
    resp_bindings: KIPostResponse = _post_notification(notifications)
    # resp_bindings.exchangeInfo[0].knowledgeBaseId
    # todo: verify if all have acknowledged notifications
