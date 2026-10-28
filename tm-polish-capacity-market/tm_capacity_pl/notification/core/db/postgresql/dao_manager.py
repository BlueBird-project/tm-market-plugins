from effi_onto_tools.db.app_settings_dao import AppSettingsDAO
from effi_onto_tools.db.postgresql.init_db import DBMeta

from tm_capacity_pl.notification.core.db.api.notification_api import NotificationAPI
from tm_capacity_pl.notification.core.db.api.contract_api import ContractAPI
from tm_capacity_pl.notification.core.db.postgresql.api_impl import contract_api_impl ,notification_api_impl
# from tm_capacity_pl.core.db.postgresql.api_impl import service_log_impl

contract_api: ContractAPI
notification_api: NotificationAPI
settings_api: AppSettingsDAO


def init_postgresql(db_meta: DBMeta):
    from effi_onto_tools.db.postgresql import dbconnection
    dbconnection.connection_manager.init(db_meta=db_meta)

    global contract_api,  settings_api,notification_api
    contract_api = contract_api_impl.ContractAPIImpl(db_meta.db_table_prefix)
    notification_api = notification_api_impl.NotificationAPIImpl(db_meta.db_table_prefix)

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
