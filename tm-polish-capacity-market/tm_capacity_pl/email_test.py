import re
from email import policy
from email.parser import BytesParser, Parser

from bs4 import BeautifulSoup
from bs4 import BeautifulSoup, ResultSet, Tag

with open("../resources/sample_email", "rb") as f:
    msg = BytesParser(policy=policy.default).parse(f)


def process_template():
    from string import Template

    with open("../resources/template_email.eml", encoding="utf-8") as f:
        template = Template(f.read())
        date = "06.08.2026"
        time_from = "18:00"
        time_to = "18:00"
        ratio = "0,88888"
        email_to="tm@bluebird.com"
        result = template.substitute(
            date=date,
            time_from=time_from,
            time_to=time_to,
            ratio=ratio,
            email_to=email_to,
        )
        return Parser(policy=policy.default).parsestr(result)


msg = process_template()

print("From:", msg["From"])
print("To:", msg["To"])
print("Subject:", msg["Subject"])
time_pattern = r"(\d{2}\.\d{2}\.\d{4})\s+od godziny\s+(\d{2}:\d{2})\s+do godziny\s+(\d{2}:\d{2})"


def get_time(bs_page: BeautifulSoup):
    span_list = bs_page.select("span")
    for span in span_list:
        span_matched = re.search(
            time_pattern,
            span.text)
        if span_matched:
            date, start_time, end_time = span_matched.groups()
            return date, start_time, end_time
    return None


ratio_pattern = r"SOMi\s*=\s*([0-9]+,[0-9]+)\s*\*\s*OMi"


def get_ratio(bs_page: BeautifulSoup):
    td_list = bs_page.select("td")

    for td in td_list:
        td_matched = re.search(
            ratio_pattern,
            td.text)
        if td_matched:
            number = float(td_matched.group(1).replace(",", "."))
            return number


if msg.is_multipart():
    for part in msg.walk():
        content_type = part.get_content_type()
        print(content_type)
        if content_type == "text/plain":
            print("\n--- TEXT ---")
            # print(part.get_content())

        elif content_type == "text/html":
            print("\n--- HTML ---")
            bs_page = BeautifulSoup(part.get_content(), features="lxml")
            print(get_time(bs_page=bs_page))
            print(get_ratio(bs_page=bs_page))
            print("")
            # print(part.get_content())
else:
    print(msg.get_content())
