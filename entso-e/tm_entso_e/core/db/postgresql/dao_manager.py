# from effi_onto_tools.db.app_settings_dao import AppSettingsDAO
from effi_onto_tools.db.postgresql.init_db import DBMeta


from tm_entso_e.core.db.api.market_dao import MarketDAO
from tm_entso_e.core.db.postgresql.api_impl import market_dao_impl  # ,market_offer_dao_impl

market_dao: MarketDAO


# offer_dao: MarketOfferDAO


# app_settings_dao: AppSettingsDAO


def init_postgresql(db_meta: DBMeta):
    from effi_onto_tools.db.postgresql import dbconnection
    dbconnection.connection_manager.init(db_meta=db_meta)

    global market_dao  # , offer_dao
    market_dao = market_dao_impl.MarketDAOImpl(db_meta.db_table_prefix)
    # offer_dao = market_offer_dao_impl.MarketOfferDAOImpl(db_meta.db_table_prefix)
    # todo: settings table in db
    # from effi_onto_tools.db.postgresql.app_settings_dao_impl import AppSettingsImpl
    # app_settings_dao = AppSettingsImpl(db_meta.db_table_prefix, init_db=False)


# TODO: make in configurable
def init() -> DBMeta:
    from core.db.postgresql import api_impl
    db_meta = DBMeta(
        db_version=api_impl.__DB_VERSION__,
        db_version_hashmap=api_impl.__DB_HASH__,
        db_schema_name=api_impl.__SCHEMA_NAME__, )
    init_postgresql(db_meta=db_meta)
    return db_meta
