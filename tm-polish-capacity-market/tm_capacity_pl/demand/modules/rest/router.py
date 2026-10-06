from typing import Optional, List

from fastapi import APIRouter

from tm_capacity_pl.demand.modules.ke_interaction.interactions.capacity_market_model import TMNotification
from tm_capacity_pl.models.contract import ContractDAO

router = APIRouter(prefix="notification")


@router.post("/init")
@router.get("/init")  #remove GET: TODO:
async def init_sample_message() -> List[TMNotification]:

    from tm_capacity_pl.demand.modules.rest import service
    return service.sample_notification()


@router.post("/send")
@router.get("/send")  #remove GET: TODO:
async def send_sample_message() :
    # TODO start contract background job
    from tm_capacity_pl.demand.modules.rest import service
    service.sample_notification()
