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
class ColorExplosionEffect(Effect):
    """
    Colors radiate outward from the center of the tree.
    """
    effect_selector = 'color-explosion'
    default_config = {
        "speed": 2,
        "base_color": (255, 0, 255),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = self.get_config('speed', float)
        self.base_color = self.get_config('base_color', get_tuple_from_json_array)
        self.explosion_radius = 0

    def update(self):
        self.explosion_radius += self.speed
        if self.explosion_radius > max(self.max_x, self.max_y, self.max_z):
            self.explosion_radius = 0

        for i, coord in enumerate(self.coords):
            distance = math.sqrt(coord[0]**2 + coord[1]**2 + coord[2]**2)
            brightness = max(0, 1 - abs(distance - self.explosion_radius) / 10)
            self.pixels[i] = apply_brg(self.base_color, brightness)

