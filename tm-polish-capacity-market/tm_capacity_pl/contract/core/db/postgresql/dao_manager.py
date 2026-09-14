from effi_onto_tools.db.app_settings_dao import AppSettingsDAO
from effi_onto_tools.db.postgresql.init_db import DBMeta

from tm_capacity_pl.contract.core.db.api.baseline_api import BaselineAPI
from tm_capacity_pl.contract.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.contract.core.db.api.power_usage_api import PowerUsageAPI
from tm_capacity_pl.core.db.api.service_log import ServiceLogAPI
from tm_capacity_pl.contract.core.db.postgresql.api_impl import contract_api_impl, baseline_api_impl,power_usage_api_impl
from tm_capacity_pl.core.db.postgresql.api_impl import service_log_impl

contract_api: ContractAPI
baseline_api: BaselineAPI
power_api: PowerUsageAPI
log_api: ServiceLogAPI
settings_api: AppSettingsDAO


def init_postgresql(db_meta: DBMeta):
    from effi_onto_tools.db.postgresql import dbconnection
    dbconnection.connection_manager.init(db_meta=db_meta)

    global contract_api, baseline_api, settings_api, log_api, power_api
    contract_api = contract_api_impl.ContractAPI(db_meta.db_table_prefix)
    baseline_api = baseline_api_impl.BaselineAPI(db_meta.db_table_prefix)
    power_api = power_usage_api_impl.PowerUsageAPI(db_meta.db_table_prefix)
    log_api = service_log_impl.ServiceLogAPIImpl(db_meta.db_table_prefix)

    from effi_onto_tools.db.postgresql.app_settings_dao_impl import AppSettingsImpl

    settings_api = AppSettingsImpl(db_meta.db_table_prefix, init_db=False)


def init() -> DBMeta:
    from tm_capacity_pl.contract.core.db.postgresql import api_impl
    db_meta = DBMeta(
        db_version=api_impl.__DB_VERSION__,
        db_version_hashmap=api_impl.__DB_HASH__,
        db_schema_name=api_impl.__SCHEMA_NAME__, )
    init_postgresql(db_meta=db_meta)
    return db_meta
