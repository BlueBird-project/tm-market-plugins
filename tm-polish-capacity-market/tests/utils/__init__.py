import math


def round_math(x, n=0):
    factor = 10 ** n
    y = x * factor
    return (math.floor(y + 0.5) if y >= 0 else math.ceil(y - 0.5)) / factor