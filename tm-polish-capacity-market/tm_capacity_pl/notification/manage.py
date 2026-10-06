import logging

from tm_capacity_pl.core import service_settings

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    import tm_capacity_pl.notification as notification_service

    notification_service.init_args()
    from effi_onto_tools import utils

    utils.ENV_FILE = notification_service.app_args.env_path
    notification_service.set_logging()
    logging.info(f"START {service_settings.name}")
    ###
    # setup DB TODO:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ###
    # from tm.core.db import setup_db
    #
    # setup_db()

    from tm_capacity_pl.core import app_settings

    notification_service.init_service()
    notification_service.start_service()
