import logging
import time

from ke_client.utils.enum_utils import BaseEnum


class KIVars(BaseEnum):
    ISP_UNIT = "ISP_UNIT"
    DAY_DURATION = "DAY_DURATION"


def setup_ke():
    import ke_client
    from tm_capacity_pl import app_args
    ke_client.VERIFY_SERVER_CERT = False
    from ke_client import configure_ke_client
    configure_ke_client(app_args.config_path)

    from ke_client import ke_settings
    ki_vars = ke_settings.get_ki_vars()
    for k in KIVars.names():
        if k not in ki_vars:
            raise KeyError(f"{k} isn't defined in ki_vars")
        setattr(KIVars, k, ki_vars[k])


from ke_client import KEClient


# smart_: KEClient = KEClient.build(logger=logging.getLogger())
# ki_client.include(ki_holder=ki)


# from tm_entso_e.utils.enum_utils import BaseEnum


# class KIVars(BaseEnum):
#     ISP_UNIT = "ISP_UNIT"
#     DAY_DURATION = "DAY_DURATION"


def _set_ke_client(bg_mode=False) -> KEClient:
    # from tm_entso_e.modules.ke_interaction.interactions import ki_client as ke_ki_client
    ki_client: KEClient = KEClient.build(logger=logging.getLogger())
    setup_ke()
    # ke_client.KE_CONFIG_PATH = ke_config_path
    MAX_ATTEMPTS = 20

    def try_register():
        cur_attempt = 0
        wait_time = 30
        is_registered = False
        while not is_registered:
            try:
                ki_client.register()
                timeout_attempt = 0
                # TODO: register should return TRUE on success
                while not is_registered:
                    time.sleep(1)
                    is_registered = ki_client.is_registered
                    if is_registered:
                        logging.info("KE client registered")
                    else:
                        logging.warning(f"KE client is not registered, wait for all KI to be registered.")
                        time.sleep(10)
                    if timeout_attempt > 10:
                        raise TimeoutError("Registration timeout")
                    else:
                        timeout_attempt += 1

            except Exception as ex:
                logging.error(f"Registered on start failed: {ex}, another attempt in {wait_time}s.")
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, 600)
                if cur_attempt > MAX_ATTEMPTS:
                    raise ConnectionError("Can't register to knowledge engine.")
                cur_attempt += 1

    def try_bg_register():
        try_register()
        ki_client.start()

    if bg_mode:
        # background start

        import threading
        t = threading.Thread(target=try_bg_register)
        t.start()
        return ki_client
    else:
        try_register()
        # ki.ke_client.register()
        ki_client.start_sync()
        return ki_client


def set_bg_ke_client() -> KEClient:
    # from tm.modules.ke_interaction.interactions import ki_client
    ki_client = _set_ke_client(bg_mode=True)
    while not ki_client.is_registered:
        # TODO: stop service id can't register
        logging.info(f"KE client is not registered, wait for all KI to be registered.")
        time.sleep(3)
    return ki_client


def set_sync_ke_client():
    _set_ke_client(bg_mode=False)


def init_client():
    from tm_capacity_pl.core import app_settings
    if app_settings.use_scheduler or app_settings.use_rest_api:


        logging.info("Running BG KE client")
        return set_bg_ke_client()
    else:
        return set_sync_ke_client()
