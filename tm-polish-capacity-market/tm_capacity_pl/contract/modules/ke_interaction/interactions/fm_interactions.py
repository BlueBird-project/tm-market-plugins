import logging
from typing import List, Tuple

from ke_client import KIHolder
from ke_client.ki_model import KIAskResponse, KIPostResponse

from tm_capacity_pl.contract.modules.ke_interaction.interactions.fm_model import *
from tm_capacity_pl.utils import TimeSpan

ki = KIHolder()


@ki.ask("fm-ts-info-request")
def _ask_request_flexibility_info(request: FMTSRequest):
    return [request]


@ki.ask("fm-ts")
def _request_data(ts_uris: List[FMPntQuery]):
    return ts_uris


@ki.post("flex-request")
def _post_flex_request(flex_request: List[BaselineFlexibilityRequest]):
    return flex_request


@ki.answer("flex-request")
def _post_flex_request(ki_id: str, ):
    from tm_capacity_pl.contract.modules.ke_interaction.service import fm_service
    flex_request = fm_service.get_flex_request(kb_id=ki.get_kb_id())
    return flex_request


def request_data(ts: TimeSpan) -> Tuple[List[FMTSResponse], List[FMPnt]]:
    logging.info("request power info")
    resp_bindings: KIAskResponse = _ask_request_flexibility_info(FMTSRequest(
        ts_interval_uri=KETimeIntervalUri(ts_from=ts.ts_from, ts_to=ts.ts_to).n3(),
        ts_date_from=Literal(time_utils.xsd_from_ts(ts.ts_from)),
        ts_date_to=Literal(time_utils.xsd_from_ts(ts.ts_to)),
    ))
    fm_info: List[FMTSResponse] = [FMTSResponse(**b) for b in resp_bindings.binding_set]
    ts_uris = [b.ts_uri for b in fm_info]
    ts_uri_refs = [FMPntQuery(ts_uri=URIRef(ts_uri)) for ts_uri in ts_uris]
    logging.info("request power timeseries")
    bindings: KIAskResponse = _request_data(ts_uris=ts_uri_refs)
    return fm_info, [FMPnt(**b) for b in bindings.binding_set]


def post_flex_request( ):
    logging.info("request flex")
    from tm_capacity_pl.contract.modules.ke_interaction.service import fm_service
    flex_request = fm_service.get_flex_request(kb_id=ki.get_kb_id())
    resp_bindings: KIPostResponse = _post_flex_request(flex_request=flex_request)
    return
