from abstracts.effect import Effect
import numpy as np

class Wave3DEffect(Effect):
    """
    3D Wave Effect using sine waves to create a dynamic flow of colors.
    """

    def __init__(self, pixels, coords):
        super().__init__(pixels, coords)
        self.time = 0  # Keeps track of time for animation

    def update(self):
        for i, coord in enumerate(self.coords):
            # Calculate wave effect based on time and pixel coordinates
            wave = 0.5 * (np.sin(coord[0] * 2.0 + self.time) +
                          np.sin(coord[1] * 3.0 + self.time) +
                          np.sin(coord[2] * 1.5 + self.time))

            # Map the wave value to RGB channels
            red = int((0.5 + 0.5 * np.sin(wave + self.time)) * 255)
            green = int((0.5 + 0.5 * np.sin(wave * 1.2 + self.time)) * 255)
            blue = int((0.5 + 0.5 * np.sin(wave * 0.8 + self.time)) * 255)

            self.pixels[i] = [red, green, blue]

        self.time += 0.1  # Increment time for smooth animation
