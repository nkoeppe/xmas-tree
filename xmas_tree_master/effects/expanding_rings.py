from abstracts.effect import Effect


class ExpandingRingsEffect(Effect):
    """
    Circular rings that expand and contract from the center.
    """
    def __init__(self, pixels, coords, center, speed=1, max_radius=50, color=(255, 0, 0)):
        super().__init__(pixels, coords)
        self.center = center
        self.radius = 0
        self.radius_direction = 1
        self.speed = speed
        self.max_radius = max_radius
        self.color = color

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
