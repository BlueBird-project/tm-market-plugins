import argparse
import os
from typing import Optional, Tuple

from fastapi import FastAPI


rest_app: FastAPI


#
# def set_logging():
#     from io import StringIO
#     import logging.config
#     from logging.handlers import RotatingFileHandler
#
#     from tm_capacity_pl.core import app_settings
#     with open(app_settings.logging_conf_path) as f:
#         ini_text = os.path.expandvars(f.read())
#         config_fp = StringIO(ini_text)
#         logging.config.fileConfig(config_fp)
#
#     root_logger = logging.getLogger()
#
#     for handler in root_logger.handlers:
#         if isinstance(handler, RotatingFileHandler):
#             handler.doRollover()
#

def init_service():
    # if ke is enabled
    import logging
    global rest_app  # TODO move to rest api python package
    from tm_capacity_pl.core import app_settings
    if app_settings.use_ke_api:
        logging.info("INIT KI")

        from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_interactions import \
            ki as cm_ki
        from tm_capacity_pl.core import init_sc
        from tm_capacity_pl.core import app_args
        smart_client = init_sc(ke_config_path=app_args.config_path, env_path=app_args.env_path)
        smart_client.include(cm_ki)
    if app_settings.use_scheduler:
        # from tm.core import task_manager

        from tm_capacity_pl.core import task_manager
        task_manager.setup_scheduler()
    if app_settings.use_rest_api:
        # from main.modules.tge_api.admin_router import router as admin_router
        from tm_capacity_pl.notification.modules.rest.router import router as notification_router

        rest_app = FastAPI(docs_url="/api",
                      openapi_url="/openapi.json", redoc_url="/redoc")
        rest_app.include_router(router=notification_router, prefix="/api")
        # rest_app.include_router(router=ki_router, prefix="/ki")

        # healthcheck_app = FastAPI(docs_url="/docs",
        #                           openapi_url="/openapi.json", redoc_url="/redoc")

        # healthcheck_app.include_router(router=healthcheck_router, prefix="")
        # app.mount("/healthcheck", healthcheck_app)
        # admin_app = FastAPI(docs_url="/docs",
        #                     openapi_url="/openapi.json", redoc_url="/redoc")
        # admin_app.include_router(router=admin_router, prefix="")
        # app.mount("/admin", admin_app)


def start_service():
    from tm_capacity_pl.core.task_manager import start_scheduler
    from tm_capacity_pl.core import start_sc
    from tm_capacity_pl.core import app_settings
    if app_settings.use_ke_api:
        start_sc()
    if app_settings.use_scheduler:
        start_scheduler()

    if app_settings.use_rest_api:
        import uvicorn
        from tm_capacity_pl.core import service_settings
        uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path,
                    log_config=None)
