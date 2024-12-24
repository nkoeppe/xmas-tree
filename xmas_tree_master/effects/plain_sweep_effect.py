from abstracts.effect import Effect
from decoratos.register_effect import RegisterEffect

from utils.get_tuple_from_json_array import get_tuple_from_json_array

"""
LEDs are BRG Ordered. Colors have to be set like x = (b, r, g). The update method gets called once per rendering frame.
"""

@RegisterEffect()
class PlaneSweepEffect(Effect):
    """
    A sweeping plane effect that moves from bottom to top, changing
    the color of all LEDs below its height.
    """
    effect_selector = 'plane-sweep'
    name = "Plane Sweep"

    default_config = {
        "speed": 0.1,
        "color": (0, 255, 0),
    }
    def __init__(self,  **kwargs):
        super().__init__( **kwargs)
        self.plane_height = 0
        self.speed = self.get_config('speed', float)
        self.color = self.get_config('color', get_tuple_from_json_array)


    def update(self):
        for i, coord in enumerate(self.coords):
            # Check if the LED is below the current plane height
            if coord[2] <= self.plane_height:
                self.pixels[i] = self.color  # Set to target color
            else:
                self.pixels[i] = (0, 0, 0)  # Reset LEDs above the plane

        # Increment the plane height and loop back if it exceeds the bounds
        self.plane_height += self.speed
        if self.plane_height > max(coord[2] for coord in self.coords):
            self.plane_height = 0
