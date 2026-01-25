import logging
from logging import Logger
from typing import Optional, Dict

import requests
from xml.etree.ElementTree import Element, ElementTree, parse as parse_xml

from pydantic import BaseModel

from tm_entso_e.modules.entso_e_api import ApiKeys
from tm_entso_e.modules.entso_e_api.api_model import MarketDocument
from tm_entso_e.modules.entso_e_api.model import SubscribedEIC
from tm_entso_e.modules.entso_e_api.rest import RESTClient, _get_ns
from tm_entso_e.utils import TimeSpan


class MarketRequest(BaseModel):
    #
    document_type: str
    period_start: str
    period_end: str
    # [M] EIC code of a Bidding Zone
    out_domain: str
    # [M] EIC code of a Bidding Zone
    in_domain: str
    market_contract_type: str
    offset: int = 0

    @property
    def api_args(self) -> Dict[str, str]:
        return {ApiKeys.__dict__[k]: v for k, v in self.__dict__.items()}


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

    def get_energy_prices(self, eic: SubscribedEIC, ti: TimeSpan):
        # TODO: move 'A44' to some constant object
        # classificationSequence_AttributeInstanceComponent.position
        # TODO: eic.market_codes -> if empty log warning
        res = {}
        for market_code in eic.market_codes:
            mr = MarketRequest(document_type="A44", in_domain=eic.code, out_domain=eic.code, offset=0,
                               market_contract_type=market_code, period_start=self.parse_time(ti.ts_from),
                               period_end=self.parse_time(ti.ts_to))

            resp_content = self.send_request(parameters=mr.api_args)
            ns = _get_ns(resp_content)
            md: MarketDocument = MarketDocument.from_xml(root_ele=resp_content, namespace_len=len(ns) + 2,
                                                         skip_fields=True)
            # TODO: xml nod
            res[market_code] = md
        return res
