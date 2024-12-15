from abstracts.effect import Effect
import sys

from decoratos.register_effect import RegisterEffect


@RegisterEffect()
class ColorGradientSweepEffect(Effect):
    """
    Sweeping gradient colors through the LEDs within moving planes.
    """
    effect_selector = 'color-gradient'

    default_config = {
        "speed": 1,
        "plane_height": 5,
    }
    def __init__(self,  **kwargs):

        super().__init__(**kwargs)
        self.plane_height = self.get_config('plane_height', float)
        self.speed = self.get_config('speed', float)

        self.plane_pos = self.min_y - self.plane_height / 2
        self.plane_direction = 1

    def get_gradient_color(self, coord_z):
        """Returns a gradient color based on the Z-coordinate."""
        hue = (coord_z - self.min_y) / (self.max_y - self.min_y) * 360  # Map Z to 0-360 hue
        r, g, b = sys.hsv_to_rgb(hue / 360, 1, 1)  # HSV to RGB
        return int(b * 255), int(r * 255), int(g * 255)

    def update(self):
        for i, coord in enumerate(self.coords):
            if self.plane_pos - self.plane_height / 2 <= coord[2] <= self.plane_pos + self.plane_height / 2:
                self.pixels[i] = self.get_gradient_color(coord[2])
            else:
                self.pixels[i] = (0, 0, 0)

        if self.plane_pos - self.plane_height / 2 < self.min_y and self.plane_direction == -1:
            self.plane_direction = 1
        elif self.plane_pos + self.plane_height / 2 > self.max_y and self.plane_direction == 1:
            self.plane_direction = -1

        self.plane_pos += self.plane_direction * self.speed
