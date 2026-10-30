import logging
from datetime import datetime, timedelta
from typing import List, Optional

from ke_client import KIHolder
from ke_client.ki_model import KIPostResponse, KIAskResponse
from ke_client.utils import time_utils
from rdflib import Literal, URIRef

from tm_capacity_pl.shared.ke_interaction.fm_model import KETimeIntervalUri, FMPntQuery, FMPnt, FMTSResponse, \
    FMTSRequest
from tm_capacity_pl.notification.modules.ke_interaction.interactions.capacity_market_model import \
    KECapacityNotification, \
    FlexContract
from tm_capacity_pl.utils import TimeSpan

ki = KIHolder()


# region contract
@ki.react("contract")
def _on_contract(ki_id: str, bindings: List[FlexContract]):
    # if len(bindings) != 1:
    #     raise ValueError("Invalid amount of contracts, only one contract can be used at same time")
    from tm_capacity_pl.notification.modules.ke_interaction.service.capacity_market_service import store_contract
    for b in bindings:
        store_contract(contract=b)
    return []


@ki.ask("contract")
def _ask_contract() -> List[FlexContract]:
    return []


def get_contract() -> Optional[FlexContract]:
    resp: KIAskResponse = _ask_contract()
    if len(resp.binding_set) > 1:
        raise ValueError("Invalid amount of contracts, only one contract can be used at same time")
    if len(resp.binding_set) == 0:
        return None
    return FlexContract(**resp.binding_set[0])


# endregion

# region current power interactions
@ki.ask("fm-ts-info-request")
def _ask_request_flexibility_info(request: FMTSRequest):
    return [request]


@ki.ask("fm-ts")
def _request_data(ts_uris: List[FMPntQuery]):
    return ts_uris


def _request_consumption_ts(ts_uris: List[str]) -> List[FMPnt]:
    ts_uri_refs = [FMPntQuery(ts_uri=URIRef(ts_uri)) for ts_uri in ts_uris]
    bindings: KIAskResponse = _request_data(ts_uris=ts_uri_refs)
    return [FMPnt(**b) for b in bindings.binding_set]


def request_consumption(ts: TimeSpan) -> List[FMPnt]:
    # from tm_capacity_pl.shared import POLAND_TZ
    # ts_from = int(ts.ts_from / 3600000) * 3600000
    # cur_dt: datetime = time_utils.from_timestamp(ts_ms=ts_from).replace(tzinfo=POLAND_TZ)
    # accu: List[FMPnt] = []
    # while cur_dt.timestamp() * 1000 < ts.ts_to:
    #     pnt = FMPnt(ts_uri=URIRef("www.example.org"), dp=URIRef("www.example.org"),
    #                 ts=Literal(time_utils.xsd_from_ts(int(cur_dt.timestamp() * 1000))),
    #                 dpr=URIRef("www.example.org"), value=Literal(1000.0))
    #     accu.append(pnt)
    #     cur_dt += timedelta(hours=1)
    # return accu
    """

    :return: sorted power consumption timeseries
    """
    resp_bindings: KIAskResponse = _ask_request_flexibility_info(FMTSRequest(
        ts_interval_uri=KETimeIntervalUri(ts_from=ts.ts_from, ts_to=ts.ts_to).n3(),
        ts_date_from=Literal(time_utils.xsd_from_ts(ts.ts_from)),
        ts_date_to=Literal(time_utils.xsd_from_ts(ts.ts_to)),
    ))
    ts_info = [FMTSResponse(**b) for b in resp_bindings.binding_set]
    accu: List[FMPnt] = []
    for uri in ts_info:
        ts = _request_consumption_ts(ts_uris=[uri.ts_uri])
        # logging.info(f"received flexibility timeseries , length: {len(ts)} , for {uri.ts_uri}")
        accu += ts
    accu.sort(key=lambda x: x.ts_ms)
    return accu


# endregion

# region flex demand interactions

@ki.post("flex-demand")
def _post_notification(notifications: List[KECapacityNotification]):
    return notifications


def post_notification(notifications: List[KECapacityNotification]):
    resp_bindings: KIPostResponse = _post_notification(notifications)
    return resp_bindings
    # resp_bindings.exchangeInfo[0].knowledgeBaseId
    # todo: verify if all have acknowledged notifications

# endregion
