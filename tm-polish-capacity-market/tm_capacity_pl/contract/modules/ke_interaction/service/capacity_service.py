from datetime import timedelta, datetime
from typing import List

from isodate import duration_isoformat
from ke_client import SplitURIBase
from ke_client.utils import time_utils
from rdflib import Literal, URIRef

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import MarketPrice, \
    MarketOfferUri, MarketOfferDPUri, DurationURI, MarketOfferDPRUri, BaselineRequest, Baseline, \
    FlexRequestUri, FlexRequest, FlexOffer, FlexPriceOffer, FlexContractUri, FlexContract, FlexContractACK
from tm_capacity_pl.models.contract import ConsumptionPowerDAO
from tm_capacity_pl.shared import POLAND_TZ


def get_prices() -> List[MarketPrice]:
    from tm_capacity_pl.core import smart_client
    kb_id = smart_client.kb_id
    # todo: get data (capacity market prices)
    year = 0
    value = -1
    quarter = -1
    offer_uri = MarketOfferUri(prefix=kb_id).uri_ref
    timedelta()
    duration = Literal(
        duration_isoformat({"years": 1})
    )
    # duration=Literal(
    #     duration_isoformat({"months": 3})
    # )
    market_price = MarketPrice(offer_uri=offer_uri,
                               dp=MarketOfferDPUri(year=year, prefix=offer_uri).uri_ref,
                               dpr=MarketOfferDPRUri(year=year, prefix=offer_uri).uri_ref,
                               duration_uri=DurationURI(year=year), duration=duration, value=Literal(value)
                               )

    return [market_price]


#
# def process_contract(contracts: List[TMContract]):
#     # todo:
#     # intearact with market and post ACK
#     def publish_job():
#         # todo:
#         # market_contract_ack =
#         post_market_ack([])
#
#     return
#


def calc_baseline(bindings: List[BaselineRequest]) -> List[Baseline]:
    from tm_capacity_pl.shared.baseline import calc_reference_profile
    if len(bindings) < 1:
        return []
    # timeseries should be the same
    # todo: check if there another timeseries uri, group by timeseries
    ts_uri = bindings[0].ts_uri
    consumption_data = [ConsumptionPowerDAO(ts=br.ts_ms, granularity_ms=3600000, value=br.get_value())
                        for br in bindings]
    baseline = calc_reference_profile(power_history=consumption_data)
    baseline_bindings = [Baseline(ts_uri=ts_uri,
                                  dp_baseline=SplitURIBase.uri_append(ts_uri, "dp_baseline"),
                                  ts=time_utils.xsd_from_ts(ts=b.ts, tz=POLAND_TZ),
                                  dpr_baseline=SplitURIBase.uri_append(ts_uri, "dpr_baseline"),
                                  value_baseline=Literal(b.baseline_value)) for b in baseline]


def get_flex_request(kb_id):
    # todo get current flexrequest timestamp
    flex_uri = FlexRequestUri(ts=0, prefix=kb_id)
    ts_from = int(datetime.now().timestamp() * 1000)
    ts_to = int(datetime.fromtimestamp(datetime.now().timestamp() + 3600 * 24 * 30).timestamp() * 1000)
    return [FlexRequest(flex_request=flex_uri.uri_ref, offer_period=flex_uri.append_ref("interval"),
                        ts=time_utils.xsd_from_ts(ts=0, tz=POLAND_TZ),
                        ts_date_from=time_utils.xsd_from_ts(ts=ts_from, tz=POLAND_TZ),
                        ts_date_to=time_utils.xsd_from_ts(ts=ts_to, tz=POLAND_TZ), )]


def process_offer(offer: List[FlexOffer]):
    # todo: process flex offer
    pass


def process_price_offer(offer: List[FlexPriceOffer]):
    # todo: process price offer
    pass


def get_contracts(kb_id):
    # for contract in contracts: todo
    asset_manager_uri = URIRef("example.org/assetmanager")
    return get_contract(kb_id, asset_uri=asset_manager_uri)


def get_contract(kb_id, asset_uri: URIRef):
    flex_uri: str = FlexRequestUri(ts=0, prefix=kb_id).uri  # Todo: get current flex uri
    flex_value = 0.0
    cost_value = 0.0
    flex_uri: FlexRequestUri = FlexRequestUri.parse(flex_uri)
    # init contract timestamp ?
    fc_uri = FlexContractUri(ts=flex_uri.ts, prefix=kb_id)

    ts_from = int(datetime.now().timestamp() * 1000)
    ts_to = int(datetime.fromtimestamp(datetime.now().timestamp() + 3600 * 24 * 120).timestamp() * 1000)
    return [FlexContract(flex_request=flex_uri.uri_ref, contract=fc_uri.uri_ref,
                         asset_manager=asset_uri,
                         flex_dp=fc_uri.append_ref("flex_dp"), cost_dp=fc_uri.append_ref("cost_dp"),
                         flex_dpr=fc_uri.append_ref("flex_dpr"), cost_dpr=fc_uri.append_ref("cost_dpr"),
                         flex_value=Literal(flex_value), cost_value=Literal(cost_value),
                         period_uri=fc_uri.append_ref("period"),
                         ts_date_from=time_utils.xsd_from_ts(ts=ts_from, tz=POLAND_TZ),
                         ts_date_to=time_utils.xsd_from_ts(ts=ts_to, tz=POLAND_TZ), )]


def process_contract_ack(ack: List[FlexContractACK]):
    # todo: process ack
    return None
