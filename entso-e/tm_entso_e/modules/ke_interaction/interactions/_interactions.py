import logging

from ke_client.client import KEClient


#
# from main.utils.ke_client.ke_properties import tge_ke_conf
#
# ke_client = KEClient(kb_id=ke_settings.knowledge_base_id, kb_name=tge_ke_conf.kb_name,
#                      ke_rest_endpoint=ke_settings.rest_endpoint, kb_description=tge_ke_conf.kb_description)
def setup_ke():
    import ke_client
    ke_client.VERIFY_SERVER_CERT = False
    from ke_client import configure_ke_client
    from tm_entso_e import app_args
    configure_ke_client(app_args.config_path)

    from ke_client import ke_settings
    ki_vars = ke_settings.get_ki_vars()
    from modules.ke_interaction import KIVars
    for k in KIVars.names():
        if k not in ki_vars:
            raise KeyError(f"{k} isn't defined in ki_vars")
        setattr(KIVars, k, ki_vars[k])


setup_ke()
ki_client = KEClient.build(logger=logging.getLogger())
