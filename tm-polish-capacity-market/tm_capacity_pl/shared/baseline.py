from collections import defaultdict, deque
from typing import List, Dict, Union
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from ke_client.utils import time_utils

from tm_capacity_pl.contract.modules.market.utils import get_hour_offset, get_hour_from_ts
from tm_capacity_pl.models.contract import ConsumptionPowerDAO, BaselineValueDAO, BaselineValue, ConsumptionPower

import holidays

from tm_capacity_pl.shared import POLAND_TZ

PL_HOLIDAYS = holidays.country_holidays("PL")


def is_working_day(dt: datetime) -> bool:
    # Convert aware timestamps to Polish local time.
    if dt.tzinfo is not None:
        dt = dt.astimezone(POLAND_TZ)
    if dt.tzinfo is None:
        raise Exception(f"missing time zone in : {dt}")
    day = dt.date()

    # Monday = 0, Sunday = 6
    return day.weekday() < 5 and day not in PL_HOLIDAYS


class BaselineBuffer:
    min_q: deque  # Indices, values increasing
    max_q: deque  # Indices, values decreasing
    window_sum: int
    data: List
    value_counter: int
    i: int
    n: int

    def __init__(self):
        self.min_q = deque()
        self.max_q = deque()
        self.n = 10
        self.data = [None] * self.n
        self.i = 0
        self.window_sum = 0
        self.value_counter = 0

    def next(self, value: float):
        """

        :param value:
        :return: reference profile value, or None if there is not enough data
        """
        i = self.i
        n = self.n
        # Remove indices outside the current window
        if self.min_q and self.min_q[0] == i:
            self.min_q.popleft()
        while self.max_q and self.max_q[0] == i:
            self.max_q.popleft()

        # Maintain increasing order for minimum
        while self.min_q and self.data[self.min_q[-1]] >= value:
            self.min_q.pop()
        self.min_q.append(i)

        # Maintain decreasing order for maximum
        while self.max_q and self.data[self.max_q[-1]] <= value:
            self.max_q.pop()
        self.max_q.append(i)

        self.window_sum += value
        if self.data[i] is None:
            self.data[i] = value
            if (i + 1) == n:
                smallest = self.data[self.min_q[0]]
                biggest = self.data[self.max_q[0]]

                result = (self.window_sum - smallest - biggest) / (n - 2)
            else:
                result = None
        else:
            self.window_sum -= self.data[i]
            self.data[i] = value

            # Calculate trimmed average for complete windows

            smallest = self.data[self.min_q[0]]
            biggest = self.data[self.max_q[0]]

            result = (self.window_sum - smallest - biggest) / (n - 2)

        self.i = (i + 1) % n
        self.value_counter += 1
        return result

    def cur(self, ):
        """
        :return:
        """
        if self.value_counter < self.n:
            return None
        smallest = self.data[self.min_q[0]]
        biggest = self.data[self.max_q[0]]
        return (self.window_sum - smallest - biggest) / (self.n - 2)

    # def calc_reference_profile(baseline_id: int, power_history: List[CapacityPowerDAO]) -> List[BaselineValueDAO]:


#     hour_offset = get_hour_offset()
#     grouped_power: Dict[int, List[CapacityPowerDAO]] = defaultdict(list)
#
#     for p in power_history:
#         grouped_power[get_hour_from_ts(p.ts, hour_offset=hour_offset)].append(p)
#     # TODO: make proper calculations according to the market 'algorithm'
#     avg_pow = {h: (sum(p.value for p in p_list) / len(p_list)) for h, p_list in grouped_power.items()}
#     baseline = [BaselineValueDAO(baseline_id=baseline_id, baseline_isp=h, isp_len=60, baseline_value=p) for h, p in
#                 avg_pow.items()]
#
#     return baseline


def calc_reference_profile(power_history: List[ConsumptionPowerDAO]) -> List[BaselineValue]:
    # result: List[BaselineValue] = []
    # value_buffer: Dict[int, BaselineBuffer] = defaultdict(BaselineBuffer)
    # for p in power_history:
    #     if p.granularity_ms != 3600000:
    #         raise ValueError(f"Invalid granularity {p.granularity_ms}, accepted only 3600000 [ms] (1 [h])")
    #     dt = datetime.fromtimestamp(timestamp=p.ts / 1000.0, tz=POLAND_TZ)
    #     if is_working_day(dt):
    #         ref_v = value_buffer[dt.hour].next(p.value)
    #         if ref_v is not None:
    #             result.append(BaselineValue(ts=time_utils.to_timestamp(dt), baseline_value=ref_v, baseline_isp=dt.hour,
    #                                         isp_len=60))
    #
    # return result
    rps = ReferenceProfileStream()
    result: List[BaselineValue] = []
    for p in power_history:
        ref_v = rps.ref_value(p)
        if ref_v is not None:
            result.append(ref_v)
    return result


class ReferenceProfileStream:
    # value_buffer: Dict[int, BaselineBuffer]
    value_buffer: List[BaselineBuffer]

    def __init__(self):
        # self.value_buffer = defaultdict(BaselineBuffer)
        self.value_buffer = [BaselineBuffer() for _ in range(24)]

    def ref_value(self, p: Union[ConsumptionPowerDAO, ConsumptionPower]):
        if p.granularity_ms != 3600000:
            raise ValueError(f"Invalid granularity {p.granularity_ms}, accepted only 3600000 [ms] (1 [h])")
        if type(p) is ConsumptionPowerDAO:
            dt = datetime.fromtimestamp(timestamp=p.ts / 1000.0, tz=POLAND_TZ)
        else:
            dt = p.dt
        if is_working_day(dt):
            ref_v = self.value_buffer[dt.hour].cur()
            self.value_buffer[dt.hour].next(p.value)
            if ref_v is not None:
                return BaselineValue(ts=time_utils.to_timestamp(dt), baseline_value=ref_v, baseline_isp=dt.hour,
                                     isp_len=60)

        return None

    def ref_profile(self,dt:datetime):
        assert all(v is not None for v in self.value_buffer)
        return [ BaselineValue(ts=time_utils.to_timestamp(dt.replace(hour=i)), baseline_value=b.cur(), baseline_isp=i,
                               isp_len=60) for i, b in enumerate(self.value_buffer)]

    def profile_exists(self):
        return all(v is not None for v in self.value_buffer)
