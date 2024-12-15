import random
import colorsys
from decoratos.register_effect import RegisterEffect
from abstracts.effect import Effect

@RegisterEffect()
class TwinklingSparkleEffect(Effect):
    """
    Adds random sparkles to LEDs with a soft, washed-out color gradient.
    """
    effect_selector = 'sparkle'

    default_config = {
        "sparkle_chance": 0.02,
        "pulse_speed": 0.1,
        "gradient_speed": 0.02,
    }

    def __init__(self,  **kwargs):
        super().__init__( **kwargs)
        self.sparkle_chance = float(self.config.get('sparkle_chance', self.default_config['sparkle_chance']))
        self.pulse_speed = float(self.config.get('pulse_speed', self.default_config['pulse_speed']))
        self.gradient_speed = float(self.config.get('gradient_speed', self.default_config['gradient_speed']))

        self.brightness = 0.5
        self.pulse_direction = 1

        # Initialize gradient parameters
        self.base_hue = random.random()  # Starting point for gradient
        self.gradient_shift = 0  # Gradient phase shift over time

    def generate_gradient_color(self, index, total, hue_shift):
        """
        Generate a soft gradient color for a given LED index.
        """
        hue = (self.base_hue + (index / total) * 0.1 + hue_shift) % 1.0
        saturation = 0.8
        value = self.brightness
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        return int(r * 255), int(g * 255), int(b * 255)

    def update(self):
        total_pixels = len(self.pixels)

        for i in range(total_pixels):
            # Decide sparkle or gradient
            if random.random() < self.sparkle_chance:
                self.pixels[i] = (255, 255, 255)  # Bright white sparkle
            else:
                # Generate gradient color for this LED
                self.pixels[i] = self.generate_gradient_color(i, total_pixels, self.gradient_shift)

        # Update brightness for pulsing effect
        self.brightness += self.pulse_direction * self.pulse_speed
        if self.brightness >= 1 or self.brightness <= 0.2:
            self.pulse_direction *= -1

        # Shift the gradient over time
        self.gradient_shift += self.gradient_speed
