import math

from abstracts.effect import Effect
from decoratos.register_effect import RegisterEffect
import json

from utils.get_tuple_from_json_array import get_tuple_from_json_array


@RegisterEffect()
class PlainRippleEffect(Effect):
    """
    Wavy planes that oscillate as they move.
    """
    effect_selector = 'plain-ripple'

    default_config = {
        "speed": 1,
        "plane_height": 5,
        "frequency": 0.1,
        "amplitude": 5,
        "color": (255, 255, 0),
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.speed = self.get_config('speed', float)
        self.plane_height = self.get_config('plane_height', float)
        self.frequency = self.get_config('frequency', float)
        self.amplitude = self.get_config('amplitude', float)
        self.color = self.get_config('color', get_tuple_from_json_array)

        self.plane_pos = self.min_y - self.plane_height / 2
        self.plane_direction = 1

    def get_wave_height(self, x):
        """Calculates the Y-offset for the wave based on X-coordinate."""
        return self.amplitude * math.sin(self.frequency * x)

    def update(self):
        for i, coord in enumerate(self.coords):
            wave_height = self.get_wave_height(coord[0])
            if self.plane_pos - self.plane_height / 2 + wave_height <= coord[2] <= self.plane_pos + self.plane_height / 2 + wave_height:
                self.pixels[i] = self.color
            else:
                self.pixels[i] = (0, 0, 0)

        if self.plane_pos - self.plane_height / 2 < self.min_y and self.plane_direction == -1:
            self.plane_direction = 1
        elif self.plane_pos + self.plane_height / 2 > self.max_y and self.plane_direction == 1:
            self.plane_direction = -1

        self.plane_pos += self.plane_direction * self.speed
