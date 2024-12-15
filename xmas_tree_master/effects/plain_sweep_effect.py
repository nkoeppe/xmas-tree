from abstracts.effect import Effect

from abstracts.effect import Effect

from decoratos.register_effect import RegisterEffect

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

    def __init__(self, pixels, coords, speed=0.1, color=(0,255, 0)):
        super().__init__(pixels, coords)
        self.plane_height = 0  # Tracks the current height of the plane
        self.speed = speed  # Speed of the plane's movement
        self.color = color  # Color applied to LEDs below the plane

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
