from typing import List, Optional

from tests.unit.notification.modules.market import init_consumption_timeseries, sample_notifications, init_notification
from tests.utils import round_math
from tm_capacity_pl.models.demand import PowerDemandDAO
from tm_capacity_pl.shared import POLAND_TZ


def test_calc_obligation():
    from tm_capacity_pl.notification.modules.market.power_obligation import calc_obligation
    consumption_data = init_consumption_timeseries(tz=POLAND_TZ)
    res = calc_obligation(notification=init_notification(POLAND_TZ),
                          power_history=consumption_data, contracted_capacity=0)
    assert len(res.keys()) == 1
    demands: List[Optional[PowerDemandDAO]] = res[[*res.keys()][0]]
    for i, d in enumerate(demands):
        if i != 11:
            assert d is None
        else:
            assert d.max_power == 8.785
            assert d.demand_start == 11
            assert d.demand_end == 12
        # else:
        #     d.
    print("")


def test_calc_obligation_sim():
    from tm_capacity_pl.notification.modules.market.power_obligation import calc_obligation
    consumption_data = init_consumption_timeseries(tz=POLAND_TZ)
    res = calc_obligation(notification=[],
                          power_history=consumption_data, contracted_capacity=0)
    assert len(res) == 1
    demands: List[Optional[PowerDemandDAO]] = res[[*res.keys()][0]]
    assert_max_power = [9.368, 9.251, 9.381, 9.376, 9.506, 9.576, 9.468, 9.388, 9.343, 9.388, 9.381, 9.613, 9.443,
                        9.338, 9.293]
    for i, d in enumerate(demands):
        if i < 7 or i > 21:
            assert d is None
        else:
            assert round_math(d.max_power, 3) == assert_max_power[i - 7]
            assert d.demand_start == i
            assert d.demand_end == i + 1
    # TODO: do asserts
    print("")
