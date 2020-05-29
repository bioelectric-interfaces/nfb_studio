def clamp(x, lowest, highest):
    """Clamps value x between lowest and highest.
    If lowest <= x <= highest, x is returned.
    If x < lowest, lowest is returned.
    If x > highest, highest is returned.
    """
    return lowest if x < lowest else highest if x > highest else x
