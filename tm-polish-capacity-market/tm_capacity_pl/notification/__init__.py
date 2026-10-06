import argparse
import os
from typing import Optional, Tuple


if __name__ == "__main__":
    # ke_endpoint = os.environ.get( "KE_ENDPOINT")
    os.environ.setdefault("SERVICE_LOG_DIR", "d:/tmp/logs/")

from pydantic import BaseModel


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


app_args: Optional[AppArgs] = None


def init_args() -> AppArgs:
    global app_args
    app_args = get_args()
    return app_args


def set_logging():
    global app_args
    from io import StringIO
    import logging.config
    from logging.handlers import RotatingFileHandler

    from tm_capacity_pl.core import app_settings
    with open(app_settings.logging_conf_path) as f:
        ini_text = os.path.expandvars(f.read())
        config_fp = StringIO(ini_text)
        logging.config.fileConfig(config_fp)

    root_logger = logging.getLogger()

    for handler in root_logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()


def init_service():
    # if ke is enabled
    import logging
    from tm_capacity_pl.core import app_settings
    if app_settings.use_ke_api:
        logging.info("INIT KI")

        from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_interactions import \
            ki as cm_ki
        from tm_capacity_pl.core import init_sc
        smart_client = init_sc(env_path=app_args.env_path)
        smart_client.include(cm_ki)
    if app_settings.use_scheduler:
        # from tm.core import task_manager

        from tm_capacity_pl.core import task_manager
        task_manager.setup_scheduler()
    if app_settings.use_rest_api:
        import uvicorn

        # from main.modules.tge_api.admin_router import router as admin_router
        from fastapi import FastAPI
        from tm_capacity_pl.notification.modules.rest.router import router as notification_router

        app = FastAPI(docs_url="/api",
                      openapi_url="/openapi.json", redoc_url="/redoc")
        app.include_router(router=notification_router, prefix="/api")
        # app.include_router(router=ki_router, prefix="/ki")

        # healthcheck_app = FastAPI(docs_url="/docs",
        #                           openapi_url="/openapi.json", redoc_url="/redoc")

        # healthcheck_app.include_router(router=healthcheck_router, prefix="")
        # app.mount("/healthcheck", healthcheck_app)
        # admin_app = FastAPI(docs_url="/docs",
        #                     openapi_url="/openapi.json", redoc_url="/redoc")
        # admin_app.include_router(router=admin_router, prefix="")
        # app.mount("/admin", admin_app)
        from tm_capacity_pl.core import service_settings
        uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path,
                    log_config=None)



def start_service():
    from tm_capacity_pl.core.task_manager import start_scheduler
    from tm_capacity_pl.core import start_sc
    start_sc()
    start_scheduler()
