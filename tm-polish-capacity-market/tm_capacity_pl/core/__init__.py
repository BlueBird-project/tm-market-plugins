import argparse
import os
from typing import Optional

from ke_client import KEClient
from pydantic import BaseModel

from tm_capacity_pl.core.config import APPSettings, ServiceSettings


class AppArgs(BaseModel):
    config_path: Optional[str]
    env: Optional[str] = None
    hash_pg_schema: bool = False

    @property
    def env_path(self) -> str:
        return self.env if self.env is not None else ".env"

    # hash_pg_schema: bool = False

    def __init__(self, args):
        super().__init__(**args)


def get_args() -> AppArgs:
    parser = argparse.ArgumentParser()
    # parser.add_argument('-d', '--debug', help='enable debug logs', action='store_true')
    parser.add_argument('-c', '--config-path', help='YAML config path', default='./resources/config.yaml')
    parser.add_argument('--env', help='env path', default='.env')
    # parser.add_argument('--hash-pg-schema', help='generate db hash', default=False, action='store_true')
    parsed_args = parser.parse_args()
    return AppArgs(args=parsed_args.__dict__)


app_args: AppArgs
app_settings: APPSettings

service_settings: ServiceSettings
smart_client: KEClient
_smart_client_initialized = False


def app_configure() -> AppArgs:
    global app_args
    global app_settings
    global service_settings
    app_args = get_args()
    app_settings = APPSettings.load()
    service_settings  = ServiceSettings.load()
    return app_args


def set_logging():
    global app_settings
    os.environ.setdefault("SERVICE_LOG_DIR", "d:/tmp/logs/")
    from io import StringIO
    import logging.config
    from logging.handlers import RotatingFileHandler

    with open(app_settings.logging_conf_path) as f:
        ini_text = os.path.expandvars(f.read())
        config_fp = StringIO(ini_text)
        logging.config.fileConfig(config_fp)

    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()


def init_sc( env_path: str = ".env"):
    global smart_client
    global _smart_client_initialized
    if _smart_client_initialized:
        return smart_client
    import ke_client

    ke_client.VERIFY_SERVER_CERT = False
    ke_client.ENV_FILE = env_path
    from tm_capacity_pl.core.smart_client import setup_ke
    setup_ke( )
    from ke_client import KEClient
    import logging
    ki_client: KEClient = KEClient.build(logger=logging.getLogger())
    smart_client = ki_client
    _smart_client_initialized = True
    return smart_client


def start_sc():
    global smart_client
    from tm_capacity_pl.core.smart_client import start_client

    start_client(ki_client=smart_client)
