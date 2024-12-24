from abstracts.effect import Effect
import colorsys
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
    name = "Color Gradient"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.plane_height = self.get_config('plane_height', float)
        self.speed = self.get_config('speed', float)

        # Initialize plane position and direction
        self.plane_pos = self.min_y - self.plane_height / 2
        self.plane_direction = 1

    def get_gradient_color(self, coord_z):
        """
        Returns a gradient color based on the Z-coordinate.
        Maps Z to a hue (0-360) and converts it to RGB.
        """
        hue = (coord_z - self.min_y) / (self.max_y - self.min_y) * 360  # Map Z to 0-360 hue
        r, g, b = colorsys.hsv_to_rgb(hue / 360, 1, 1)  # HSV to RGB
        return int(r * 255), int(g * 255), int(b * 255)

    def update(self):
        """
        Updates the LED colors based on the moving plane position.
        """
        for i, coord in enumerate(self.coords):
            if self.plane_pos - self.plane_height / 2 <= coord[2] <= self.plane_pos + self.plane_height / 2:
                self.pixels[i] = self.get_gradient_color(coord[2])
            else:
                self.pixels[i] = (0, 0, 0)  # Turn off LEDs outside the plane

        # Reverse direction if the plane hits the boundaries
        if self.plane_pos - self.plane_height / 2 < self.min_y and self.plane_direction == -1:
            self.plane_direction = 1
        elif self.plane_pos + self.plane_height / 2 > self.max_y and self.plane_direction == 1:
            self.plane_direction = -1

        # Move the plane
        self.plane_pos += self.plane_direction * self.speed
