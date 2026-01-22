import logging

from ke_client.client import KEClient


ke_client = KEClient.build(logger=logging.getLogger())
