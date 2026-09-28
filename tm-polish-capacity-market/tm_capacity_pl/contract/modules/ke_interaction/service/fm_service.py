from collections import defaultdict
from typing import List, Dict, Callable, Union

from effi_onto_tools.utils import time_utils
from rdflib import URIRef, Literal

from tm_capacity_pl.contract.modules.ke_interaction.interactions.capacity_market_model import FlexRequestUri, \
    BaselineUri, BaselineDPUri, BaselineDPRUri
from tm_capacity_pl.contract.modules.ke_interaction.interactions.fm_model import FMPnt, BaselineFlexibilityRequest
from tm_capacity_pl.models.contract import CapacityPowerDAO, ContractDAO


def process_data_points(granularity_ms: int, power_ts: List[FMPnt]):
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    # sorted_power_list=  sorted(power_ts, key=lambda x: x.ts_ms)
    # p:FMPnt
    power_history = [CapacityPowerDAO(ts=p.ts_ms, granularity_ms=granularity_ms, value=p.get_value(), )
                     for p in power_ts]
    inserted = dao_manager.power_api.log_power(power_history=power_history)
    assert inserted == len(power_history)


def get_flex_request(kb_id: str) -> List[BaselineFlexibilityRequest]:
    from tm_capacity_pl.contract.core.db.postgresql import dao_manager
    contract: ContractDAO = dao_manager.contract_api.get_current(contract_ack=True)
    if contract is not None:
        if contract.current_baseline_id is None:
            return []
            # todo: log exception:

        baseline = dao_manager.baseline_api.get_baseline(baseline_id=contract.current_baseline_id)
        # market_uri = URIRef(value="market", base=kb_id)
        flex_request_uri = FlexRequestUri(ts=baseline.update_time, prefix=kb_id).uri_ref
        baseline_uri = BaselineUri(ts=baseline.update_time, prefix=kb_id).uri_ref
        flex_request = [
            BaselineFlexibilityRequest(flex_request=flex_request_uri,  baseline_uri=baseline_uri,
                                       dp=BaselineDPUri(isp=bv.baseline_isp, prefix=baseline_uri).uri_ref,
                                       dpr=BaselineDPRUri(isp=bv.baseline_isp, prefix=baseline_uri).uri_ref,
                                       ts=Literal(time_utils.xsd_from_ts(contract.create_time)),
                                       value=Literal(bv.baseline_value)
                                       )

            for bv in baseline.values]
        return flex_request
    return []
