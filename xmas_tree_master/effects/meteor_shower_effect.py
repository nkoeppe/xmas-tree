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
class MeteorShowerEffect(Effect):
    """
    Bright streaks of light fall from the top to the bottom.
    """
    effect_selector = 'meteor-shower'
    default_config = {
        "speed": 2,
        "trail_length": 10,
        "color": (0, 255, 255),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = self.get_config('speed', float)
        self.trail_length = self.get_config('trail_length', int)
        self.color = self.get_config('color', get_tuple_from_json_array)
        self.meteors = []

    def update(self):
        for meteor in self.meteors:
            meteor["z"] -= self.speed

        self.meteors = [m for m in self.meteors if m["z"] > self.min_z]

        if len(self.meteors) < 10 and random.random() > 0.7:
            self.meteors.append({"x": random.uniform(self.min_x, self.max_x),
                                 "y": random.uniform(self.min_y, self.max_y),
                                 "z": self.max_z})

        for i, coord in enumerate(self.coords):
            self.pixels[i] = (0, 0, 0)
            for meteor in self.meteors:
                dist = math.sqrt((coord[0] - meteor["x"])**2 +
                                 (coord[1] - meteor["y"])**2 +
                                 (coord[2] - meteor["z"])**2)
                if dist < self.trail_length:
                    brightness = max(0, 1 - (dist / self.trail_length))
                    self.pixels[i] = apply_brg(self.color, brightness)

