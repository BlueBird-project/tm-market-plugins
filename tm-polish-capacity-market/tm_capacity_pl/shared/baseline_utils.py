from typing import List
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def sample_power_data(years: List[int], tzinfo: ZoneInfo):
    res = []
    r = random.Random()

    for year in years:

        if 2024 < year < (datetime.now().year + 50):
            current = datetime(year, 1, 1, tzinfo=tzinfo)
            end = datetime(year + 1, 1, 1, tzinfo=tzinfo)

            while current < end:

                for hour in range(24):
                    timestamp = current.replace(hour=hour, tzinfo=tzinfo)
                    res.append((timestamp, r.random() * 200 + 500))
                current += timedelta(days=1)

    return res
