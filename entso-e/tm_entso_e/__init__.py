import argparse
import logging
import os
from typing import Optional

if __name__ == "__main__":
    # ke_endpoint = os.environ.get( "KE_ENDPOINT")
    os.environ.setdefault("SERVICE_LOG_DIR", "d:/tmp/logs/")

from pydantic import BaseModel


class AppArgs(BaseModel):
    config_path: Optional[str]
    env: Optional[str] = None

    @property
    def env_path(self) -> str:
        return self.env if self.env is not None else ".env"

    # hash_pg_schema: bool = False

    def __init__(self, args):
        super().__init__(**args)


def get_args() -> AppArgs:
    parser = argparse.ArgumentParser()
    # parser.add_argument('-d', '--debug', help='enable debug logs', action='store_true')
    parser.add_argument('-c', '--config-path', help='config path', default='./resources/config.yml')
    parser.add_argument('--env', help='env path', default='.env')
    # parser.add_argument('--hash-pg-schema', help='generate db hash', default=False, action='store_true')
    parsed_args = parser.parse_args()
    return AppArgs(args=parsed_args.__dict__)


#
app_args: Optional[AppArgs] = None


def init_args() -> AppArgs:
    global app_args
    app_args = get_args()
    return app_args


def set_logging():
    global app_args
    from io import StringIO
    import logging.config
    from tm_entso_e.core import app_settings

    with open(app_settings.logging_conf_path) as f:
        ini_text = os.path.expandvars(f.read())
        config_fp = StringIO(ini_text)
        logging.config.fileConfig(config_fp)
        # for key, value in config.items():
        #     expanded = expanded.replace(f"${{{key}}}", str(value))
    # # logging.config.fileConfig(app_settings.logging_path,)
    #
