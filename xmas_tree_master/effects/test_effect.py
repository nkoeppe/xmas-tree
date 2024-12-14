from abstracts.effect import Effect
import numpy as np



class TestEffect(Effect):
    """
    Simple effect that cycles through colors.
    """

    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.angle = 0
        self.index = 0

    def update(self):
        for i in range(len(self.pixels)):
            self.pixels[i] = [
                (self.index + i * 30) % 255,
                (self.index + i * 60) % 255,
                (self.index + i * 90) % 255,
            ]
        self.index += 10
