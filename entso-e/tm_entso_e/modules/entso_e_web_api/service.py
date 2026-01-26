# import logging
# import os
# from datetime import datetime, timedelta
# from typing import List
# from zoneinfo import ZoneInfo
#
# from effi_onto_tools.utils import time_utils
#
# __MAX_DAYS__ = 60
# __DAY_MS__ = 24 * 3600 * 1000
# __TIME_ZONE__ = ZoneInfo("Europe/Warsaw")
#
# __LAST_UPDATE_HOUR__ = 20
# __LAST_UPDATE_DAY_OFFSET__ = __LAST_UPDATE_HOUR__ / 24
# __LAST_UPDATE_DAY_OFFSET_MS__ = (1 - __LAST_UPDATE_HOUR__ / 24) * __DAY_MS__
#
#
# # region utils
# def _check_last_date(date_str: str) -> int:
#     if date_str is None:
#         return 60
#     last_dt = time_utils.parse_date(date_str, dformat=time_utils.DATE_FORMAT, tz=__TIME_ZONE__)
#     current_ts = time_utils.current_timestamp()
#     df_days = int((current_ts - last_dt + __LAST_UPDATE_DAY_OFFSET_MS__) / __DAY_MS__ + __LAST_UPDATE_DAY_OFFSET__)
#     return min(df_days, __MAX_DAYS__)
#
#
# def check_last_primary_date() -> int:
#     from main.core.db.postgresql import dao_manager
#     last_date = dao_manager.tge_dao.last_date_primary_offer()
#     return _check_last_date(date_str=last_date)
#
#
# def check_last_date() -> int:
#     from main.core.db.postgresql import dao_manager
#     last_date = dao_manager.tge_dao.last_date_offer()
#     return _check_last_date(date_str=last_date)
#
#
# def _get_day_ahead_standard_offer(data: List[dict]):
#     def process_row(r: dict):
#         day_offer = {"ts": r["ts"], "date_str": r["date_str"], "cost_mwh": r["rdn_fixing_pln_mwh"],
#                      "isp_unit": r["granularity"],
#                      "isp_len": 1, "isp_start": r["day_offset"] / int(r["granularity"])}
#         return day_offer
#
#     return [process_row(row) for row in data]
#
#
# # endregion
#
# def check_data() -> int:
#     logging.info("Check day offer")
#     from main.modules.tge import webscrap_api
#     from effi_onto_tools.utils.time_utils import to_timestamp
#     from main.core.db.postgresql import dao_manager
#     days_behind = check_last_date()
#     days_behind = max(0, days_behind)
#     repeat_last_day = 1
#     for i in range(1, days_behind + 1 + repeat_last_day):
#         d = datetime.today() - timedelta(days=(days_behind - i - 1))
#         ts = to_timestamp(d)
#         # 1759269600 = 1 OCTOBER 2025
#         if ts >= 1759269600000:
#             date_str = time_utils.datetime_to_str(d)
#             try:
#                 logging.info(f"Get offer for {date_str}")
#                 market_data, headers = webscrap_api.get_data(ts)
#
#                 market_dict = [{k: v for k, v in zip(headers, row)} for row in market_data]
#                 day_offer = _get_day_ahead_standard_offer(market_dict)
#                 inserted = dao_manager.tge_dao.log_day_offer(offer=market_dict)
#                 dayhead_inserted = dao_manager.day_ahead_dao.log_day_offer(offer=day_offer)
#                 logging.info(f"Successfully acquired offer for: {date_str}.")
#
#             # tge_dao.log_day_offer(offer=tge_data_mapped)
#             except Exception as ex:
#                 print(f"error for {date_str}({i}): {ex}")
#     logging.info("TGE offers acquired")
#     return days_behind
#
