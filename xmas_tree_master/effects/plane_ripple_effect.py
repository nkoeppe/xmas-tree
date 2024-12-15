
from abstracts.effect import Effect

class PlaneRippleEffect(Effect):
    """
    Wavy planes that oscillate as they move.
    """
    def __init__(self, pixels, coords, min_max_y, speed=1, plane_height=10, frequency=0.1, amplitude=5, color=(255, 255, 0)):
        super().__init__(pixels, coords)
        self.min_y, self.max_y = min_max_y
        self.plane_height = plane_height
        self.plane_pos = self.min_y - plane_height / 2
        self.plane_direction = 1
        self.speed = speed
        self.frequency = frequency
        self.amplitude = amplitude
        self.color = color

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
