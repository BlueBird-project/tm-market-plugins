from typing import Optional

from effi_onto_tools.db import TimeSpan
from fastapi import APIRouter

from tm_entso_e.core.healthcheck import service

router = APIRouter(prefix="")


@router.get("/", description="check if service is responding")
async def status():
    from effi_onto_tools.utils import time_utils
    return time_utils.current_timestamp()


@router.get("/state", description="Determine service state")
async def state():
    return service.get_service_state()


@router.get("/report", description="Detailed service state")
async def report():
    return service.get_service_report()


@router.get("/log", description="List service logs")
async def state(ts_from: Optional[int] = None, ts_to: Optional[int] = None):
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    ts.assert_max_length(time_interval_ms=3600 * 24 * 7*1000)
    return service.list_log(ts=ts)


@router.get("/log/error", description="Check if there are any service errors")
async def state(ts_from: Optional[int] = None, ts_to: Optional[int] = None):
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    ts.assert_max_length(time_interval_ms=3600 * 24 * 7*1000)
    return service.check_error(ts=ts)


@router.get("/log/job/error", description="List ENTSO-E scheduler job errors ")
async def state(ts_from: Optional[int] = None, ts_to: Optional[int] = None):
    ts = TimeSpan(ts_from=ts_from, ts_to=ts_to)
    ts.assert_max_length(time_interval_ms=3600 * 24 * 7*1000)
    return service.job_error(ts=ts)
