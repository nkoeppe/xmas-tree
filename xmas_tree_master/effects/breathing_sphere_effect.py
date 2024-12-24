import math
import random

import numpy as np
from decoratos.register_effect import RegisterEffect
from abstracts.effect import Effect

from utils.get_tuple_from_json_array import get_tuple_from_json_array

from utils.apply_brg import apply_brg

"""
LEDs are BRG Ordered. Colors have to be set like x = (b, r, g). The update method gets called once per rendering frame.
"""
@RegisterEffect()
class BreathingSphereEffect(Effect):
    """
    The whole tree glows and dims cyclically as if it's breathing.
    """
    effect_selector = 'breathing-sphere'
    default_config = {
        "speed": 0.05,
        "color": (0, 0, 255),
    }
    name = "Breathing Sphere"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = self.get_config('speed', float)
        self.color = self.get_config('color', get_tuple_from_json_array)
        self.brightness = 0
        self.direction = 1

    def update(self):
        self.brightness += self.speed * self.direction
        if self.brightness >= 1 or self.brightness <= 0:
            self.direction *= -1
        for i, _ in enumerate(self.coords):
            self.pixels[i] = apply_brg(self.color, abs(self.brightness))

