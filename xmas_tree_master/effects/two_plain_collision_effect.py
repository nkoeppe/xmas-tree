from abstracts.effect import Effect
from decoratos.register_effect import RegisterEffect
import json

from utils.get_tuple_from_json_array import get_tuple_from_json_array

"""
LEDs are BRG ordered. Colors should be set as tuples, e.g., x = (b, r, g). 
The update method is called once per rendering frame.
"""

@RegisterEffect()
class TwoPlainCollisionEffect(Effect):
    """
    A sweeping plane effect that moves from bottom to top (and vice versa),
    changing the color of all LEDs within each plane's height.
    """

    effect_selector = 'two-plain'

    default_config = {
        "speed": 1,
        "color1": (255, 0, 0),
        "color2": (0, 255, 0),
        "plane_height": 5,

    }
    def __init__(self, **kwargs): #pixels, coords, min_max_y, speed=1, color1=(0, 255, 0), color2=(255, 0, 0), plane_height=10):
        """
        Initializes the effect with given parameters.

        :param pixels: LED pixel array
        :param coords: Coordinates of the LEDs
        :param speed: Speed of plane movement
        :param color1: Color for the first plane
        :param color2: Color for the second plane
        :param plane_height: Height of each plane
        """

        super().__init__(**kwargs)

        self.speed = self.get_config('speed', float)
        self.plane_height = self.get_config('plane_height', float)

        self.color1 = self.get_config('color1', get_tuple_from_json_array)
        self.color2 = self.get_config('color2', get_tuple_from_json_array)

        # Initialize planes' positions and directions
        self.plane_1_y = self.min_y - self.plane_height / 2
        self.plane_2_y = self.max_y + self.plane_height / 2
        self.plane_1_direction = 1
        self.plane_2_direction = -1


        # Set all LEDs to off initially
        self.clear_pixels()

    def clear_pixels(self):
        """Turns off all LEDs."""
        for i in range(len(self.pixels)):
            self.pixels[i] = (0, 0, 0)

    def is_within_plane(self, coord_z, plane_y):
        """
        Checks if the Z-coordinate is within the range of the plane.

        :param coord_z: Z-coordinate of the LED
        :param plane_y: Y-coordinate of the plane center
        :return: True if within range, False otherwise
        """
        return plane_y - self.plane_height / 2 <= coord_z <= plane_y + self.plane_height / 2

    def update(self):
        """Updates the LED colors and plane positions for the current frame."""
        # Update pixel colors based on proximity to planes
        for i, coord in enumerate(self.coords):
            if self.is_within_plane(coord[2], self.plane_1_y):
                self.pixels[i] = self.color1
            elif self.is_within_plane(coord[2], self.plane_2_y):
                self.pixels[i] = self.color2
            else:
                self.pixels[i] = (0, 0, 0)

        # Update plane directions based on boundary collisions
        self.update_plane_directions()

        # Update plane positions
        self.plane_1_y += self.plane_1_direction * self.speed
        self.plane_2_y += self.plane_2_direction * self.speed

    def update_plane_directions(self):
        """Handles plane boundary collisions and crossover logic."""
        # Boundary collision for plane 1
        if self.plane_1_y - self.plane_height / 2 < self.min_y and self.plane_1_direction == -1:
            self.plane_1_direction = 1
        elif self.plane_1_y + self.plane_height / 2 > self.max_y and self.plane_1_direction == 1:
            self.plane_1_direction = -1

        # Boundary collision for plane 2
        if self.plane_2_y - self.plane_height / 2 < self.min_y and self.plane_2_direction == -1:
            self.plane_2_direction = 1
        elif self.plane_2_y + self.plane_height / 2 > self.max_y and self.plane_2_direction == 1:
            self.plane_2_direction = -1

        # Reverse directions if planes overlap
        if abs(self.plane_1_y - self.plane_2_y) <= self.plane_height:
            self.plane_1_direction *= -1
            self.plane_2_direction *= -1
