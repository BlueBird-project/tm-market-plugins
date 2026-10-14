from tests.unit.notification.modules.market import init_consumption_timeseries
from tm_capacity_pl.shared import POLAND_TZ
from tm_capacity_pl.shared.baseline import calc_reference_profile


def test_calc_reference_profile():
    consumption_data = init_consumption_timeseries(tz=POLAND_TZ)
    ref_profile=calc_reference_profile(power_history=consumption_data)
    print("")
