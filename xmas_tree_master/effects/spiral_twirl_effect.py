import math

import numpy as np
from decoratos.register_effect import RegisterEffect
from abstracts.effect import Effect

from utils.get_tuple_from_json_array import get_tuple_from_json_array

from utils.apply_brg import apply_brg

"""
LEDs are BRG Ordered. Colors have to be set like x = (b, r, g). The update method gets called once per rendering frame.
"""
@RegisterEffect()
class SpiralTwirlEffect(Effect):
    """
    LEDs light up in a spiral pattern around the tree, moving from base to top.
    """
    effect_selector = 'spiral-twirl'
    default_config = {
        "speed": 1,
        "hue_shift": 0.01,
        "radius": 0.5,
        "color": (255, 0, 0),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = self.get_config('speed', float)
        self.hue_shift = self.get_config('hue_shift', float)
        self.radius = self.get_config('radius', float)
        self.color = self.get_config('color', get_tuple_from_json_array)
        self.angle_offset = 0

    def update(self):
        self.angle_offset += self.speed
        for i, coord in enumerate(self.coords):
            angle = math.atan2(coord[1], coord[0]) + self.angle_offset
            distance = math.sqrt(coord[0]**2 + coord[1]**2)
            brightness = max(0, 1 - abs(distance - self.radius))
            self.pixels[i] = apply_brg(self.color, brightness)
