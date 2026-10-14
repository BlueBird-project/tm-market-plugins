import math


def round_math(x, n=0):
    factor = 10 ** (n+3)
    y = x * factor
    v= (math.floor(y + 0.5) if y >= 0 else math.ceil(y - 0.5)) / factor
    factor = 10 ** n
    y = v * factor
    return (math.floor(y + 0.5) if y >= 0 else math.ceil(y - 0.5)) / factor