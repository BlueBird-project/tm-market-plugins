template_path = "../resources/template_email.eml"


def _validate_time(t: int):
    assert 0 <= t <= 23
    return t


def _validate_ratio(f: float):
    assert 0 < f <= 1.0
    return f


def init_message(day: int, month: int, year: int, time_from: int, time_to: int, ratio: float) -> str:
    from string import Template
    assert time_to > time_from or (time_from == 23 and time_to == 0)
    with open(template_path, encoding="utf-8") as f:
        template = Template(f.read())
        date = f"{day}.{month}.{year}"
        time_from = f"{_validate_time(time_from)}:00"
        time_to = f"{_validate_time(time_to)}:00"
        ratio = str(_validate_ratio(ratio)).replace(".", ",")
        email_to = "tm@bluebird.com"
        result = template.substitute(
            date=date,
            time_from=time_from,
            time_to=time_to,
            ratio=ratio,
            email_to=email_to,
        )
        return result
