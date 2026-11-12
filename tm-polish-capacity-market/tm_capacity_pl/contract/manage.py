import logging

import tm_capacity_pl.core as core

if __name__ == "__main__":
    ###
    # setup configurations
    ###
    import tm_capacity_pl.contract as contract_service

    app_args: core.AppArgs = core.app_configure()
    import tm_capacity_pl.contract.config as config
    config.configure()
    core.set_logging()
    from tm_capacity_pl.core import service_settings
    from effi_onto_tools import utils

    utils.ENV_FILE = core.app_args.env_path
    logging.info(f"START {service_settings.name}")
    contract_service.init_service()
    contract_service.start_service()
