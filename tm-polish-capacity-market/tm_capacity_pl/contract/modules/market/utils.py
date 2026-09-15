from datetime import datetime


def get_hour_offset():
    return datetime.now().astimezone().utcoffset().total_seconds() / 3600


def get_hour_from_ts(ts_ms: int, hour_offset: int) -> int:
    hour = int((ts_ms / 3600000)) % 24 + hour_offset
    return hour
