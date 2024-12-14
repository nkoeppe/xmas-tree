from xmas_tree_master.abstracts.effect import Effect


# Example effect: Rotating Wave
class RotatingWaveEffect(Effect):
    def __init__(self, pixels, coords, color_a, color_b, inc=0.1, buffer=200):
        super().__init__(pixels, coords)
        self.color_a = color_a
        self.color_b = color_b
        self.inc = inc
        self.buffer = buffer
        self.angle = 0
        self.c = 100
        self.direction = -1
        self.min_alt = min(coord[2] for coord in coords)
        self.max_alt = max(coord[2] for coord in coords)

    def apply(self):
        for i, coord in enumerate(self.coords):
            if math.tan(self.angle) * coord[1] <= coord[2] + self.c:
                self.pixels[i] = self.color_a
            else:
                self.pixels[i] = self.color_b

        self.pixels.show()

        self.angle += self.inc
        if self.angle > 2 * math.pi:
            self.angle -= 2 * math.pi

        self.c += self.direction
        if self.c <= self.min_alt + self.buffer:
            self.direction = 1
        elif self.c >= self.max_alt - self.buffer:
            self.direction = -1
