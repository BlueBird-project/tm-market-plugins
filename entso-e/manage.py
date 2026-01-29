import logging
from time import sleep

import tm_entso_e

from tm_entso_e.utils import TimeSpan

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    tm_entso_e.init_args()
    from tm_entso_e.core import service_settings, app_settings

    # utils.ENV_FILE = main.app_args.env_path
    tm_entso_e.set_logging()
    logging.info(f"START {service_settings.name}")
    ###
    # setup DB
    ###
    from tm_entso_e.core.db import setup_db

    setup_db()

if app_settings.use_ke_api:
    #   setup ke
    # import ke_client
    # ke_client.ENV_FILE = tm_entso_e.app_args.env_path
    from tm_entso_e.modules.ke_interaction import set_bg_ke_client, set_sync_ke_client

    if app_settings.use_scheduler or app_settings.use_rest_api:
        logging.info("Running BG KE client")
        market_prefix = set_bg_ke_client().kb_id

    else:
        set_sync_ke_client()
        exit()
else:
    market_prefix = "https://entsoe.bluebird.com"
if __name__ == "__main__" and app_settings:
    # configure entsoe
    from tm_entso_e.modules.entso_e_web_api.config import configure_api

    api_settings = configure_api()
    from tm_entso_e.modules.entso_e_web_api.service import init_service, subscribe_data

    init_service(market_prefix=market_prefix)
    subscribe_data(ti=TimeSpan.last_day())
    subscribe_data(ti=TimeSpan(ts_from=1768957200000, ts_to=1769130000000))
    ########################################################
    from tm_entso_e.modules.ke_interaction.interactions import publish_market_information, \
    publish_market_offer_information, publish_market_offer

    success=False
    # while not success:
    #     try:
    #         print("publish")
    #         publish_market_information()
    #         success=True
    #         sleep(5)
    #     except Exception as ex:
    #         print(ex)
    while not success:
        try:
            # print("publish details")
            res=publish_market_offer_information()
            print(res)
            publish_market_offer()
            success=True
            sleep(5)
        except Exception as ex:
            sleep(5)
            print(ex)
    # from tm_entso_e.modules.entso_e_web_api.energy_api import MarketAPI
    # market_api = MarketAPI(market_uri_prefix=market_prefix)
    # s_eic_area = api_settings.subscribed_eic[1]
    # result = market_api.get_energy_prices(eic=s_eic_area, ti=TimeSpan.last_day())
    # result = market_api.get_energy_prices(eic=s_eic_area, ti=TimeSpan(ts_from=1768957200000, ts_to=1769130000000))
    # # market_api.get_market_uri
    # for market_code, market_offer in result.items():
    #     market_uri = market_api.get_market_uri(eic_area_code=s_eic_area.code, market_code=market_code)
    #     # result = market_api.get_energy_prices(eic=eic_area, ti=TimeSpan.last_48h())
    #     from modules.entso_e_web_api.service import store_offers
    #
    #     store_offers(market_uri=market_uri, market_offer=market_offer)
    # print(result)
    ##########################################################33
if __name__ == "__main__" and app_settings:
    if app_settings.use_scheduler:
        from tm_entso_e.core import task_manager

        task_manager.setup_scheduler()

# if __name__ == "__main__":
#     if app_settings.use_rest_api:
#         import uvicorn
#         from tm_entso_e.modules.day_ahead_api.router import router as dayahead_router
#         from tm_entso_e.core.healthcheck.router import router as healthcheck_router
#         from tm_entso_e.modules.admin.admin_router import router as admin_router
#         from fastapi import FastAPI
#
#         app = FastAPI(docs_url="/docs",
#                       openapi_url="/docs/openapi.json", redoc_url="/redoc")
#         app.include_router(router=dayahead_router, prefix="/api")
#
#         healthcheck_app = FastAPI(docs_url="/docs",
#                                   openapi_url="/openapi.json", redoc_url="/redoc")
#
#         healthcheck_app.include_router(router=healthcheck_router, prefix="")
#         app.mount("/healthcheck", healthcheck_app)
#         admin_app = FastAPI(docs_url="/docs",
#                             openapi_url="/openapi.json", redoc_url="/redoc")
#         admin_app.include_router(router=admin_router, prefix="")
#         app.mount("/admin", admin_app)
#         uvicorn.run(app, port=service_settings.port, host=service_settings.host, root_path=service_settings.root_path)
