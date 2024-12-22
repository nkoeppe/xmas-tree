import numpy as np
from decoratos.register_effect import RegisterEffect
from abstracts.effect import Effect

"""
LEDs are BRG Ordered. Colors have to be set like x = (b, r, g). The update method gets called once per rendering frame.
"""
@RegisterEffect()
class Wave3DEffect(Effect):
    """
    3D Wave Effect using sine waves to create a dynamic flow of colors.
    """
    effect_selector = 'wave'
    default_config = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time = 0  # Keeps track of time for animation


    def update(self):
        for i, coord in enumerate(self.coords):
            # Calculate wave effect with individual variations for x, y, z
            wave_x = np.sin(coord[0] * 2.0 + self.time)
            wave_y = np.sin(coord[1] * 3.0 + self.time)
            wave_z = np.sin(coord[2] * 1.5 + self.time)

            # Combine wave components to create more variation
            wave = 0.5 * (wave_x + wave_y + wave_z)

            # Map the wave value to RGB channels with unique adjustments
            red = int((0.5 + 0.5 * np.sin(wave + self.time)) * 255)
            green = int((0.5 + 0.5 * np.sin(wave * 1.3 + self.time + 2)) * 255)  # Phase shift for green
            blue = int((0.5 + 0.5 * np.sin(wave * 0.8 + self.time + 4)) * 255)  # Different phase for blue

            # Assign RGB values to pixel
            self.pixels[i] = (green, red, blue)

        self.time += 0.1  # Increment time for smooth animation
