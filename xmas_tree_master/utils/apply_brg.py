def apply_brg(color, brightness = 1 ):
    """Adjusts color brightness and reorders to BRG."""
    r, g, b = color
    r, g, b = int(r * brightness), int(g * brightness), int(b * brightness)
    return b, r, g