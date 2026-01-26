import logging

from ke_client.client import KEClient

#
# from main.utils.ke_client.ke_properties import tge_ke_conf
#
# ke_client = KEClient(kb_id=ke_settings.knowledge_base_id, kb_name=tge_ke_conf.kb_name,
#                      ke_rest_endpoint=ke_settings.rest_endpoint, kb_description=tge_ke_conf.kb_description)
ki_client = KEClient.build(logger=logging.getLogger())
