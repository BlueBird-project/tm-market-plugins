from tests.unit.notification.modules.market import init_consumption_timeseries
from tests.utils import round_math
from tm_capacity_pl.shared import POLAND_TZ
from tm_capacity_pl.shared.baseline import calc_reference_profile


def test_calc_reference_profile():
    consumption_data = init_consumption_timeseries(tz=POLAND_TZ)
    ref_profile = calc_reference_profile(power_history=consumption_data)
    assert_values = [9.400, 9.518, 9.363, 9.655, 9.663, 9.468, 9.350, 9.355, 9.238, 9.368,
                     9.363, 9.493, 9.563, 9.455, 9.375, 9.330, 9.375, 9.368, 9.600, 9.430,
                     9.325, 9.280, 9.450, 9.405]
    for i, v in enumerate(assert_values):
        assert  round_math(ref_profile[i].baseline_value ,3) == v
