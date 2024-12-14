from abstracts.effect import Effect
import numpy as np

class PlaneSweepEffect(Effect):
    """
    A sweeping plane effect that moves from bottom to top, changing
    the color of all LEDs below its height.
    """

    def __init__(self, pixels, coords, speed=0.5, color=(255, 0, 0)):
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
                self.pixels[i] = [0, 0, 0]  # Reset LEDs above the plane

        # Increment the plane height and loop back if it exceeds the bounds
        self.plane_height += self.speed
        if self.plane_height > max(coord[2] for coord in self.coords):
            self.plane_height = 0
