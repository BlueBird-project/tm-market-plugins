from collections import defaultdict
from datetime import timedelta, datetime
from typing import List, Dict

from isodate import duration_isoformat
from tm_capacity_pl.shared.baseline import baseline_requirements
from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import *
from tm_capacity_pl.models.contract import ConsumptionPowerDAO, FlexAssetContract
from tm_capacity_pl.shared import POLAND_TZ
from tm_capacity_pl.shared.ke_interaction.contract import KEFlexContractQuery, KEFlexContract
from tm_capacity_pl.shared.ke_interaction.ke_model import KETimeIntervalUri
from tm_capacity_pl.utils import TimeSpan


def get_flex_request(kb_id):
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    request = dao_manager.contract_api.current_request()
    if request is not None:
        return [KEFlexRequest.init(request=request)]
    else:
        # TODO: remove sample request
        flex_uri = FlexRequestUri(ts=0, prefix=kb_id)
        ts_from = int(datetime.now().timestamp() * 1000)
        ts_to = int(datetime.fromtimestamp(datetime.now().timestamp() + 3600 * 24 * 30).timestamp() * 1000)
        return [KEFlexRequest(flex_request=flex_uri.uri_ref, offer_period=flex_uri.append_ref("interval"),
                              ts=time_utils.xsd_from_ts(ts=0, tz=POLAND_TZ),
                              ts_date_from=time_utils.xsd_from_ts(ts=ts_from, tz=POLAND_TZ),
                              ts_date_to=time_utils.xsd_from_ts(ts=ts_to, tz=POLAND_TZ), )]


def get_baseline_required_dates(kb_id: str, bindings: List[BaselineDateRequest]) -> List[BaselineDateResponse]:
    reqs = []
    for b in bindings:
        req = baseline_requirements(ts=TimeSpan(ts_from=b.baseline_from_ts, ts_to=b.baseline_to_ts))
        bdr = BaselineDateResponse(**vars(b),
                                   baseline_ts_uri=BaselineUri(ts_from=b.baseline_from_ts, ts_to=b.baseline_to_ts,
                                                               prefix=kb_id).uri_ref,
                                   day_interval_uri=KETimeIntervalUri(ts_from=req.ts_from, ts_to=req.ts_to).n3(),
                                   ts_day_from=Literal(time_utils.xsd_from_ts(req.ts_from)),
                                   ts_day_to=Literal(time_utils.xsd_from_ts(req.ts_to)))
        reqs.append(bdr)
    return reqs


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
                                  ts=Literal(time_utils.xsd_from_ts(ts=b.ts, tz=POLAND_TZ)),
                                  dpr_baseline=SplitURIBase.uri_append(ts_uri, "dpr_baseline"),
                                  value_baseline=Literal(b.baseline_value)) for b in baseline]
    return baseline_bindings


def process_offer(offers: List[KEFlexOffer]):
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    grouped_offers: Dict[str, List[FlexOffer]] = defaultdict(list)
    for offer in offers:
        parsed_offer = offer.rdf_parse()
        dao_manager.asset_api.get_or_init(asset_manager_uri=parsed_offer.asset_manager_uri)
        grouped_offers[offer.asset_manager].append(parsed_offer)
    for asset_uri, parsed_offers in grouped_offers.items():
        dao_manager.contract_api.add_offer(offers=parsed_offers)


def process_price_offer(offers: List[KEFlexPriceOffer]):
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    dao_manager.contract_api.add_offer_price(offers=[o.rdf_parse() for o in offers])


def get_contracts(query: Optional[List[KEFlexContractQuery]] = None) -> List[KEFlexContract]:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    acc: List[FlexAssetContract] = []
    if query is None:
        acc = dao_manager.contract_api.get_current_contracts()
    for q in query:
        acc += dao_manager.contract_api.get_current_contracts(asset_manager_uri=q.asset_manager.n3())

    res = [KEFlexContract.init(flex_request=URIRef(c.flex_request_uri),
                               contract_uri=URIRef(c.contract_uri),
                               asset_manager=URIRef(c.asset_manager_uri),
                               flex_value=Literal(c.flex_value),
                               price_value=Literal(c.price_value),
                               ts_from=c.ts_from, ts_to=c.ts_to) for c in acc]
    return res


def get_contract(kb_id, asset_uri: URIRef):
    flex_uri: str = FlexRequestUri(ts=0, prefix=kb_id).uri  # Todo: get current flex uri
    flex_value = 0.0
    cost_value = 0.0
    flex_uri: FlexRequestUri = FlexRequestUri.parse(flex_uri)
    # init contract timestamp ?
    fc_uri = FlexContractUri(ts=flex_uri.ts, prefix=kb_id)

    ts_from = int(datetime.now().timestamp() * 1000)
    ts_to = int(datetime.fromtimestamp(datetime.now().timestamp() + 3600 * 24 * 120).timestamp() * 1000)
    return [KEFlexContract(flex_request=flex_uri.uri_ref, contract=fc_uri.uri_ref,
                           asset_manager=asset_uri,
                           flex_dp=fc_uri.append_ref("flex_dp"), cost_dp=fc_uri.append_ref("cost_dp"),
                           flex_dpr=fc_uri.append_ref("flex_dpr"), cost_dpr=fc_uri.append_ref("cost_dpr"),
                           flex_value=Literal(flex_value), cost_value=Literal(cost_value),
                           period_uri=fc_uri.append_ref("period"),
                           ts_date_from=time_utils.xsd_from_ts(ts=ts_from, tz=POLAND_TZ),
                           ts_date_to=time_utils.xsd_from_ts(ts=ts_to, tz=POLAND_TZ), )]


########################
########################
########################

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
