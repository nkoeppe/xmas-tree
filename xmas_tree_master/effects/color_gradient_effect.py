from abstracts.effect import Effect
import sys

class ColorGradientSweepEffect(Effect):
    """
    Sweeping gradient colors through the LEDs within moving planes.
    """
    def __init__(self, **kwargs):
        pixels = kwargs['pixels']
        coords = kwargs['coords']
        min_max_y = kwargs['min_max_y']
        plane_height = kwargs['plane_height']
        speed = kwargs['speed']


        super().__init__(pixels, coords)
        self.min_y, self.max_y = min_max_y
        self.plane_height = plane_height
        self.plane_pos = self.min_y - plane_height / 2
        self.plane_direction = 1
        self.speed = speed

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
