import logging
from typing import Dict, Any, List

from effi_onto_tools.db import TimeSpan
from effi_onto_tools.utils import time_utils

__DAY_MS__ = 24 * 3600 * 1000

from tm_capacity_pl.models.service_log import ServiceLogDAO, ERROR_TAG


def check_ke(report: Dict) -> Dict:
    from tm_capacity_pl.core import app_settings
    report["knowledge_engine_api_available"] = app_settings.use_ke_api
    if app_settings.use_ke_api:
        from tm_capacity_pl.core import smart_client
        report["knowledge_engine_api_state"] = smart_client.state()
        report["knowledge_engine_api_registered"] = smart_client.is_registered
    return report


def ke_state() -> bool:
    from tm_capacity_pl.core import app_settings
    if app_settings.use_ke_api:
        from tm_capacity_pl.core import smart_client
        return smart_client.state()
    else:
        return True


def check_scheduler(report: Dict) -> Dict:
    from tm_capacity_pl.core import app_settings
    report["bg_scheduler_available"] = app_settings.use_scheduler
    if app_settings.use_ke_api:
        from apscheduler.schedulers.base import STATE_RUNNING
        from tm_capacity_pl.core.task_manager import service_job_scheduler
        report["bg_scheduler_state"] = service_job_scheduler.state == STATE_RUNNING
        report["bg_scheduler_state_value"] = service_job_scheduler.state
    return report


def scheduler_state() -> bool:
    from tm_capacity_pl.core import app_settings
    from tm_capacity_pl.core.task_manager import service_job_scheduler
    if app_settings.use_ke_api:
        from apscheduler.schedulers.base import STATE_RUNNING
        return service_job_scheduler.state == STATE_RUNNING
    else:
        return True


def check_log(report: Dict) -> Dict:
    ts_to = time_utils.current_timestamp()
    last_hour = TimeSpan(ts_from=ts_to - 3600000, ts_to=ts_to)
    report["service_error"] = check_error(ts=last_hour)
    report["job_error"] = len(job_error(ts=TimeSpan.last_day()))
    return report


def log_state() -> bool:
    ts_to = time_utils.current_timestamp()
    last_hour = TimeSpan(ts_from=ts_to - 3600000, ts_to=ts_to)
    return check_error(ts=last_hour) == 0 and len(job_error(ts=last_hour)) == 0


def check_db(report: Dict) -> Dict:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    try:
        prev, current = dao_manager.settings_api.set("app_healthcheck", time_utils.current_timestamp())
    except Exception as ex:
        prev = None
        current = None
        logging.error(f"db health check failed {ex}")

    report["db_state"] = current is not None
    report["db_healthcheck"] = current
    return report


def db_state() -> Dict:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    try:
        prev, current = dao_manager.settings_api.set("app_healthcheck", time_utils.current_timestamp())

    except Exception as ex:
        prev = None
        current = None
        logging.error(f"db health check failed {ex}")
    return current is not None


def get_service_report() -> Dict[str, Any]:
    report = {"check_start_ts": time_utils.current_timestamp()}

    report = check_ke(report=report)
    report = check_db(report=report)
    report = check_scheduler(report=report)
    report = check_log(report=report)
    report["check_end_ts"] = time_utils.current_timestamp()
    return report


def get_service_state() -> bool:
    return ke_state() and db_state() and scheduler_state() and log_state()


def list_log(ts: TimeSpan) -> List[ServiceLogDAO]:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    return dao_manager.log_api.list(ts=ts, tag=None)


def check_error(ts: TimeSpan) -> int:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    return dao_manager.log_api.has_tag(ts=ts, tag=ERROR_TAG)


def job_error(ts: TimeSpan) -> List[ServiceLogDAO]:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    return dao_manager.log_api.list_job_state(ts=ts, tag=ERROR_TAG)
