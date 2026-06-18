__DB_VERSION__ = "0.2"
__SCHEMA_NAME__ = 'public'
# __TABLE_PREFIX__ = "tm_"
__DB_HASH__ = {}

from tm_entso_e.core.db.postgresql.api_impl.db_updates.schema_updates_0 import db_0_2_update

__DB_UPDATE_CHAIN__ = {
    "0.1":   db_0_2_update
}
