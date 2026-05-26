class JobError(RuntimeError):
    msg: str

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


class EntsoeError(Exception):
    msg: str

    def __init__(self, msg: str):
        self.msg = msg

    def __str__(self):
        return self.msg


NO_MATCHING_DATA=999