from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Optional

from ke_client.utils import time_utils

from tm_capacity_pl.models.contract import CapacityPowerDAO, CapacityPower, BaselineValue
from tm_capacity_pl.models.demand import PowerDemandDAO
from tm_capacity_pl.notification.modules.market.message_parser import CapacityMarketNotification
from tm_capacity_pl.shared import POLAND_TZ
from tm_capacity_pl.shared.baseline import ReferenceProfileStream


class PowerList:
    date_key: str
    data: List[CapacityPower]
    _sorted = False

    def __init__(self):
        self.data = []

    @property
    def value(self):
        if len(self.data) != 24:
            raise ValueError(f"missing power data for: {self.date_key}")
        if not self._sorted:
            self.data.sort(key=lambda x: x.ts)
            self._sorted = True
        return self.data


class NotificationList:
    date_key: str
    data: List[CapacityMarketNotification]
    _sorted = False

    def __init__(self):
        self.data = []

    @property
    def value(self):
        if len(self.data) != 24:
            raise ValueError(f"missing power data for: {self.date_key}")
        if not self._sorted:
            self.data.sort(key=lambda x: x.ts)
            self._sorted = True
        return self.data


def dt_key(dt: datetime):
    return int(datetime(year=dt.year, month=dt.month, day=dt.day).timestamp())


def calc_obligation(notification: List[CapacityMarketNotification], power_history: List[CapacityPower],
                    contracted_capacity: float = 0)->Dict[int, List[Optional[PowerDemandDAO]]]:
    notification_grouped: Dict[int, NotificationList] = defaultdict(NotificationList)
    power_history_grouped: Dict[int, PowerList] = defaultdict(PowerList)
    baseline_grouped: Dict[int, List[BaselineValue]] = defaultdict(list)
    demand_grouped: Dict[int, List[Optional[PowerDemandDAO]]] = defaultdict(lambda: [None] * 24)

    for n in notification:
        n.set_timezone(tzinfo=POLAND_TZ)
        notification_grouped[dt_key(dt=n.dt)].data.append(n)

    for p in power_history:
        if p.granularity_ms != 3600000:
            raise ValueError(f"Invalid granularity {p.granularity_ms}, accepted only 3600000 [ms] (1 [h])")
        p.set_timezone(tzinfo=POLAND_TZ)
        power_history_grouped[dt_key(dt=p.dt)].data.append(p)

    if len(notification_grouped) >= 0.2 * len(power_history_grouped):
        rps = ReferenceProfileStream()
        for k in sorted(power_history_grouped.keys()):
            for p in power_history_grouped[k].data:
                ref_value = rps.ref_value(p=p)
                if ref_value is not None:
                    baseline_grouped[k].append(ref_value)
    else:
        day_key = sorted(power_history_grouped.keys())
        for k, n in notification_grouped.items():
            i = day_key.index(k) - 1
            ref_value = None
            rps = ReferenceProfileStream()
            while i >= 0 and (ref_value is None or (not rps.profile_exists())):
                for p in power_history_grouped[day_key[i]].data:
                    ref_value = rps.ref_value(p=p)
                i -= 1
            baseline_grouped[k] = rps.ref_profile(time_utils.from_timestamp(ts_ms=k * 1000).replace(tzinfo=POLAND_TZ))

    dates = notification_grouped.keys() if len(notification_grouped) != 0 else power_history_grouped.keys()
    for d in dates:
        if d not in power_history_grouped:
            raise ValueError(f"missing power data for: {d}")
        p = power_history_grouped[d]
        ref_p = baseline_grouped[d]
        notifications = None
        if d in notification_grouped:
            notifications = notification_grouped[d]
            start_hour = notifications.data[0].start_time - 5
        else:
            start_hour = 2
        avg_ref = (ref_p[start_hour].baseline_value + ref_p[start_hour + 1].baseline_value + ref_p[
            start_hour + 2].baseline_value) / 3.0
        avg_real = (p.data[start_hour].value + p.data[start_hour + 1].value + p.data[start_hour + 2].value) / 3.0
        if notifications is not None:
            for n in notifications.data:
                ref_v = ref_p[n.start_time]
                correction = (avg_real - avg_ref)
                if correction > 0:
                    correction = min(0.2 * ref_v.baseline_value, correction)
                else:
                    correction = -1 * min(0.2 * ref_v.baseline_value, abs(correction))
                max_power = ref_v.baseline_value + correction - contracted_capacity
                demand_grouped[d][n.start_time] = PowerDemandDAO(ts=time_utils.to_timestamp(n.dt), demand_start=n.start_time,
                                                              demand_end=n.start_time + 1,
                                                              capacity_obligation_ratio=n.ratio,
                                                              max_power=max_power,
                                                              contracted_capacity=contracted_capacity)
        else:
            for k in range(7, 23):
                ref_v = ref_p[k]
                correction = (avg_real - avg_ref)
                if correction > 0:
                    correction = min(0.2 * ref_v.baseline_value, correction)
                else:
                    correction = -1 * min(0.2 * ref_v.baseline_value, abs(correction))
                max_power = ref_v.baseline_value + correction - contracted_capacity
                demand_grouped[d][k] = PowerDemandDAO(
                    ts=time_utils.to_timestamp(time_utils.from_timestamp(d).replace(hour=k, tzinfo=POLAND_TZ)),
                    demand_start=k,
                    demand_end=k + 1,
                    capacity_obligation_ratio=n.ratio,
                    max_power=max_power,
                    contracted_capacity=contracted_capacity)

    return demand_grouped
