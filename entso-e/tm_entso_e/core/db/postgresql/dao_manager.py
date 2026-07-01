from effi_onto_tools.db.app_settings_dao import AppSettingsDAO
from effi_onto_tools.db.postgresql.init_db import DBMeta

from tm_entso_e.core.db.api.market_offer_dao import MarketOfferAPI
from tm_entso_e.core.db.api.market_dao import MarketAPI
from tm_entso_e.core.db.api.service_log import ServiceLogAPI
from tm_entso_e.core.db.postgresql.api_impl import market_api_impl, market_offer_api_impl,service_log_impl

market_api: MarketAPI
offer_api: MarketOfferAPI
log_api:ServiceLogAPI
settings_api: AppSettingsDAO


def init_postgresql(db_meta: DBMeta):
    from effi_onto_tools.db.postgresql import dbconnection
    dbconnection.connection_manager.init(db_meta=db_meta)

    global market_api, offer_api, settings_api,log_api
    market_api = market_api_impl.MarketAPIImpl(db_meta.db_table_prefix)
    offer_api = market_offer_api_impl.MarketOfferAPIImpl(db_meta.db_table_prefix)
    log_api = service_log_impl.ServiceLogAPIImpl(db_meta.db_table_prefix)
    from effi_onto_tools.db.postgresql.app_settings_dao_impl import AppSettingsImpl

    settings_api = AppSettingsImpl(db_meta.db_table_prefix, init_db=False)


def init() -> DBMeta:
    from tm_entso_e.core.db.postgresql import api_impl
    db_meta = DBMeta(
        db_version=api_impl.__DB_VERSION__,
        db_version_hashmap=api_impl.__DB_HASH__,
        db_schema_name=api_impl.__SCHEMA_NAME__, )
    init_postgresql(db_meta=db_meta)
    return db_meta
