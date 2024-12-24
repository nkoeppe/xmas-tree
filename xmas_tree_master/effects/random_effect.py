from abstracts.effect import Effect
import random

from decoratos.register_effect import RegisterEffect

"""
LEDs are BRG Ordered. Colors have to be set like x = (b, r, g). The update method gets called once per rendering frame.
"""
@RegisterEffect()
class RandomEffect(Effect):
    """
    Random effect that cycles through predefined colors.
    """
    effect_selector = 'random'
    default_config = None
    name = "Random"
    def __init__(self,  **kwargs):
        super().__init__( **kwargs)
        self.colors = [
            (0, 255, 0),   # Green
            (255, 0, 0),   # Red
            (0, 0, 255),   # Blue
            (255, 255, 0), # Yellow
            (0, 255, 255), # Cyan
            (255, 0, 255), # Magenta
            (255, 255, 255), # White
            (128, 128, 128), # Gray
        ]
        self.current_colors = [random.choice(self.colors) for _ in range(len(self.pixels))]

    def update(self):
        for i in range(len(self.pixels)):
            # Randomly cycle to a new color from the predefined list
            if random.random() < 0.1:  # Adjust probability as needed
                self.current_colors[i] = random.choice(self.colors)
            self.pixels[i] = self.current_colors[i]
