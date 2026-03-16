from fastapi import APIRouter

from tm_entso_e.core.healthcheck import service

router = APIRouter(prefix="")


@router.get("/", description="check if service is responding")
async def status():
    from effi_onto_tools.utils import time_utils
    return time_utils.current_timestamp()


@router.get("/state",description="Determine service state")
async def state():
    return service.get_service_state()


@router.get("/report",description="Detailed service state")
async def report():
    return service.get_service_report()
