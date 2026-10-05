import re
from dataclasses import dataclass
from datetime import datetime, time
from email import policy
from email.message import EmailMessage, Message
from email.parser import Parser
from typing import Optional, Tuple

from bs4 import BeautifulSoup
from rdflib import Literal, XSD

time_pattern = r"(\d{1,2}\.\d{1,2}\.\d{4})\s+od godziny\s+(\d{1,2}:\d{2})\s+do godziny\s+(\d{1,2}:\d{2})"
ratio_pattern = r"SOMi\s*=\s*([0-9]+,[0-9]+)\s*\*\s*OMi"


def _get_time(bs_page: BeautifulSoup) -> Optional[Tuple[str, int, int]]:
    span_list = bs_page.select("span")
    for span in span_list:
        span_matched = re.search(time_pattern,  span.text)
        if span_matched:
            date, start_time, end_time = span_matched.groups()
            return date, int(start_time.split(":")[0]), int(end_time.split(":")[0])
    return None


def _get_ratio(bs_page: BeautifulSoup) -> Optional[float]:
    td_list = bs_page.select("td")

    for td in td_list:
        td_matched = re.search(
            ratio_pattern,
            td.text)
        if td_matched:
            number = float(td_matched.group(1).replace(",", "."))
            return number
    return None


@dataclass
class CapacityMarketNotification:
    date: str
    start_time: int
    end_time: int
    ratio: float

    @property
    def xsd_date(self):
        value = self.date.strip().strip("*")
        dt = datetime.strptime(value, "%d.%m.%Y")

        return Literal(dt.isoformat(), datatype=XSD.dateTime)

    @property
    def xsd_start_time(self):
        t = time(self.start_time, 0).isoformat()
        return Literal(t, datatype=XSD.time)

    @property
    def xsd_end_time(self):
        t = time(self.end_time, 0).isoformat()
        return Literal(t, datatype=XSD.time)

    @property
    def xsd_ratio(self):
        return Literal(self.ratio, datatype=XSD.float)


def get_html_content(email: str):
    parsed_msg: Message = Parser(policy=policy.default).parsestr(email)
    # print("From:", parsed_msg["From"])
    # print("To:", parsed_msg["To"])
    # print("Subject:", parsed_msg["Subject"])

    if parsed_msg.is_multipart() and isinstance(parsed_msg, EmailMessage):
        for part in parsed_msg.walk():
            content_type = part.get_content_type()
            print(content_type)
            if content_type == "text/plain":
                pass
                # print("\n--- TEXT ---")
                # print(part.get_content())

            elif content_type == "text/html":
                return part.get_content()
                # print(part.get_content())
    else:
        # TODO:
        raise Exception("TODO:")


def process_message(email: str) -> CapacityMarketNotification:
    html_content = get_html_content(email=email)
    bs_page = BeautifulSoup(html_content, features="lxml")
    date, start_time, end_time = _get_time(bs_page=bs_page)
    ratio = _get_ratio(bs_page=bs_page)
    return CapacityMarketNotification(date=date, start_time=start_time, end_time=end_time, ratio=ratio)
