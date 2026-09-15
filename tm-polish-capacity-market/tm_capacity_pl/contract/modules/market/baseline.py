from collections import defaultdict
from typing import List, Dict

from tm_capacity_pl.contract.modules.market.utils import get_hour_offset, get_hour_from_ts
from tm_capacity_pl.models.contract import CapacityPowerDAO, BaselineDAO, ContractDAO


def calc_baseline(contract_id: int, power_history: List[CapacityPowerDAO]) -> List[BaselineDAO]:
    hour_offset = get_hour_offset()
    grouped_power: Dict[int, List[CapacityPowerDAO]] = defaultdict(list)

    for p in power_history:
        grouped_power[get_hour_from_ts(p.ts, hour_offset=hour_offset)].append(p)
    # TODO: make proper calculations according to the market 'algorithm'
    avg_pow = {h: (sum(p.value for p in p_list) / len(p_list)) for h, p_list in grouped_power.items()}
    baseline = [BaselineDAO(contract_id=contract_id, baseline_isp=h, isp_len=60, baseline_value=p) for h, p in
                avg_pow.items()]

    return baseline
