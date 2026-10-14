from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from ke_client.utils import time_utils

from tm_capacity_pl.models.contract import CapacityPower
from tm_capacity_pl.notification.modules.market.message_parser import CapacityMarketNotification

sample_consumption_data = {
    "2021-01-05": [9.300, 9.580, 9.500, 9.880, 9.400, 9.880, 9.200, 9.080, 9.400, 9.480, 9.300, 9.080,
                   9.700, 9.780, 9.600, 9.680, 9.200, 9.480, 9.700, 9.580, 8.900, 8.880, 9.000, 9.480],
    "2021-01-06": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None, None, None, None, None],
    "2021-01-07": [9.500, 9.580, 9.800, 9.380, 9.600, 9.480, 9.900, 8.880, 8.900, 9.680, 9.800, 9.580,
                   9.800, 9.380, 9.400, 9.380, 9.900, 9.080, 9.700, 9.180, 9.200, 9.080, 9.400, 9.780],
    "2021-01-08": [9.800, 9.680, 9.000, 9.780, 9.100, 9.580, 9.200, 8.880, 9.700, 9.280, 9.100,
                   9.780, 9.900, 9.480, 9.400, 9.780, 9.500, 9.680, 9.500, 9.680, 9.500, 9.680, 9.300, 9.880],
    "2021-01-09": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None, None, None, None, None],
    "2021-01-10": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None, None, None, None, None],
    "2021-01-11": [9.000, 9.180, 9.700, 9.680, 9.500, 9.080, 9.400, 9.780, 9.700, 9.680, 9.400, 9.680, 9.500, 8.880,
                   8.900, 9.480, 9.400, 9.580, 9.700, 9.480, 9.600, 9.580, 9.700, 9.380],
    "2021-01-12": [9.000, 9.680, 9.800, 9.680, 9.800, 9.580, 9.900, 9.580, 9.500, 9.280, 9.100, 9.380, 9.500,
                   9.580, 9.400, 9.580, 9.300, 8.980, 9.000, 8.980, 9.400, 9.280, 9.300, 8.980],
    "2021-01-13": [9.300, 9.580, 9.100, 8.980, 9.900, 9.180, 9.800, 9.680, 8.900, 9.480, 9.500, 9.780, 9.800, 9.580,
                   9.300, 9.480, 9.100, 9.780, 9.100, 9.380, 9.700, 8.980, 8.900, 8.980],
    "2021-01-14": [9.500, 9.480, 9.100, 9.880, 9.800, 9.880, 9.100, 9.780, 9.700, 8.980, 9.600, 9.180, 9.300, 9.680,
                   9.200, 8.880, 9.500, 9.480, 9.600, 9.380, 9.100, 9.080, 9.800, 9.380],
    "2021-01-15": [9.900, 8.980, 9.100, 14.880, 9.800, 8.880, 9.000, 9.080, 8.900, 9.080, 9.600, 9.580, 9.600, 9.380,
                   9.300, 8.880, 9.100, 9.280, 9.800, 9.480, 9.200, 9.380, 9.600, 9.180],
    "2021-01-16": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None, None, None, None],
    "2021-01-17": [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None, None, None, None, None],
    "2021-01-18": [9.100, 9.780, 9.000, 9.180, 9.600, 9.880, 9.100, 9.780, 8.900, 9.480, 9.000, 9.680, 9.000, 9.180,
                   9.900, 9.080, 9.900, 9.380, 9.800, 9.880, 9.200, 9.180, 9.700, 9.480],
    "2021-01-19": [9.700, 9.380, 9.600, 9.780, 9.800, 9.080, 9.100, 8.980, 8.900, 9.180, 9.300, 8.880, 9.300, 9.380,
                   9.400, 9.080, 8.900, 8.880, 9.700, 9.280, 9.400, 9.680, 9.600, 9.580],
    "2021-01-20": [9.400, 9.820, 10.100, 9.020, 9.600, 7.820, 8.400, 9.520, 7.900, 6.820, 5.900, 1.820, 3.900, 6.820,
                   10.810, 10.350, 10.100, 10.310, 10.420, 10.570, 10.780, 10.380, 10.430, 10.190]

}
sample_notifications = [CapacityMarketNotification(date="2021-01-20", start_time=11, end_time=12, ratio=1.0)]


def init_consumption_timeseries(tz: ZoneInfo) -> List[CapacityPower]:
    d = {datetime.strptime(k, "%Y-%m-%d").replace(tzinfo=tz): v for k, v in sample_consumption_data.items()}
    res = []
    for k in sorted(d.keys()):
        res += [CapacityPower(ts=time_utils.to_timestamp(k.replace(hour=h))
                              , granularity_ms=3600000, value=v).set_timezone(tzinfo=tz) for h, v in enumerate(d[k])]

    return res
