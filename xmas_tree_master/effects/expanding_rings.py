import math

from abstracts.effect import Effect
from decoratos.register_effect import RegisterEffect
from utils.get_tuple_from_json_array import get_tuple_from_json_array


@RegisterEffect()
class ExpandingRingsEffect(Effect):
    """
    Circular rings that expand and contract from the center.
    """
    effect_selector = 'expanding-rings'
    name = "Expanding Rings"
    default_config = {
        "speed": 1,
        "max_radius": 100,
        "color": (255, 255, 0),
    }

    def __init__(self, **kwargs):
        super().__init__( **kwargs)

        self.radius = 0
        self.radius_direction = 1
        self.speed = self.get_config('speed', float)
        self.max_radius = self.get_config('max_radius', float)
        self.color = self.get_config('color', get_tuple_from_json_array)

    def update(self):
        for i, coord in enumerate(self.coords):
            distance = math.sqrt((coord[0] - self.center[0])**2 + (coord[2] - self.center[2])**2)
            if abs(distance - self.radius) <= self.max_radius / 10:  # Allow a small thickness for the ring
                self.pixels[i] = self.color
            else:
                self.pixels[i] = (0, 0, 0)

        if self.radius >= self.max_radius and self.radius_direction == 1:
            self.radius_direction = -1
        elif self.radius <= 0 and self.radius_direction == -1:
            self.radius_direction = 1

        self.radius += self.radius_direction * self.speed
