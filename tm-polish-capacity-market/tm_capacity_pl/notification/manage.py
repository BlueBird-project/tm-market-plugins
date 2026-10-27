import logging

import tm_capacity_pl.core as core

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    import tm_capacity_pl.notification as notification_service

    app_args: core.AppArgs =  core.app_configure()
    core.set_logging()
    from tm_capacity_pl.core import service_settings
    from effi_onto_tools import utils

    utils.ENV_FILE = core.app_args.env_path
    logging.info(f"START {service_settings.name}")
    ###
    # setup DB TODO:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ###
    # from tm.core.db import setup_db
    #
    # setup_db()

    notification_service.init_service()
    notification_service.start_service()
