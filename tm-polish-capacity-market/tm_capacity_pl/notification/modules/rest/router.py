from typing import Optional, List, Dict, Any

from fastapi import APIRouter
from starlette.responses import PlainTextResponse

from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_model import KECapacityNotification
from tm_capacity_pl.models.contract import ContractDAO

router = APIRouter(prefix="/notification")


@router.post("/init")
@router.get("/init")  # remove GET: TODO:
async def init_sample_message() -> List:
    from tm_capacity_pl.notification.modules.rest import service
    return await service.sample_notification()


@router.post("/send")
@router.get("/send")  # remove GET: TODO:
async def send_sample_message() -> Any:
    # TODO start contract background job
    from tm_capacity_pl.notification.modules.rest import service
    return await service.post_sample_notification()


@router.post("/start_sample")
@router.get("/start_sample")  # remove GET: TODO:
async def send_sample_message() -> Any:
    # TODO start contract background job
    from tm_capacity_pl.notification.modules.rest import service
    email = service.sample_email()
    from tm_capacity_pl.notification.modules.market.service import message_handler
    await message_handler(email=email)


@router.post("/sample/email",response_class=PlainTextResponse)
@router.get("/sample/email",response_class=PlainTextResponse)
async def send_sample_message() -> Any:
    from tm_capacity_pl.notification.modules.rest import service
    return service.sample_email()
