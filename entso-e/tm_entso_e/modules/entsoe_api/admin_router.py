from effi_onto_tools.db import TimeSpan
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="")


@router.get("/get_data")
async def start_job(ts_from: int, ts_to: int) -> bool:
    from tm_entso_e.modules.entso_e_web_api.service import get_data
    from tm_entso_e.modules.entso_e_web_api.errors import JobError
    try:
        get_data(ti=TimeSpan(ts_from=ts_from, ts_to=ts_to))
        return True
    except JobError as ex:
        raise HTTPException(detail=ex.msg, status_code=429)


@router.get("/get_data/state")
async def job_state() -> bool:
    from tm_entso_e.modules.entso_e_web_api.service import get_data_job_running
    return get_data_job_running()
