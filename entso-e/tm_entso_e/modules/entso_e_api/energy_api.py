import logging
from logging import Logger
from typing import Optional, Dict

import requests
from xml.etree.ElementTree import Element, ElementTree, parse as parse_xml

from effi_onto_tools.db import TimeSpan
from pydantic import BaseModel

from tm_entso_e.modules.entso_e_api.rest import RESTClient


class MarketRequest(BaseModel):
    #
    document_type: str
    period_start: str
    period_end: str
    # [M] EIC code of a Bidding Zone
    out_domain: str
    # [M] EIC code of a Bidding Zone
    in_domain: str


# [M] Pattern yyyyMMddHHmm e.g. 201601010000
# out_Domain
#
# 10YAT-APG------L
#
# [M] EIC code of a Bidding Zone
# in_Domain
#
# 10YAT-APG------L
#
# [M] EIC code of a Bidding Zone (must be same as out_Domain)
# contract_MarketAgreement.type
#
# A01
#
# [O] A01 = Day-ahead ; A07 = Intraday
# classificationSequence_AttributeInstanceComponent.position
#
# 1
#
# [O] Integer
# offset
#
# 0
#
# [O] Integer (allows downloading more than 100 documents. The offset ∈ [0,4800] so that pagging is restricted to query for 4900 documents max., offset=n returns files in sequence between n+1 and n+100)
class MarketAPI(RESTClient):

    def __init__(self, logger: Optional[Logger] = None, **kwargs):
        super().__init__(logger=logger, **kwargs)

    def get_energy_prices(self, eic_code: str, ti: TimeSpan):
        MarketRequest(document_type="A44", in_domain=eic_code, out_domain=eic_code)
        args = {}
