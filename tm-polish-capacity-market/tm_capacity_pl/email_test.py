from tm_capacity_pl.notification.modules.market.message_generator import init_message
from tm_capacity_pl.notification.modules.market import process_message

# with open("../resources/sample_email.eml", "rb") as f:
#     msg = BytesParser(policy=policy.default).parse(f)


msg = init_message(day=26, month=11, year=2026, time_from=17, time_to=18, ratio=0.555)
market_notification = process_message(email=msg)
print(market_notification)
exit()
#
# msg = Parser(policy=policy.default).parsestr(msg)

print("From:", msg["From"])
print("To:", msg["To"])
print("Subject:", msg["Subject"])

if msg.is_multipart():
    for part in msg.walk():
        content_type = part.get_content_type()
        print(content_type)
        if content_type == "text/plain":
            print("\n--- TEXT ---")
            print(part.get_content())

        elif content_type == "text/html":
            print("\n--- HTML ---")
            bs_page = BeautifulSoup(part.get_content(), features="lxml")
            # print(get_time(bs_page=bs_page))
            # print(get_ratio(bs_page=bs_page))
            print("")
            # print(part.get_content())
else:
    print(msg.get_content())
