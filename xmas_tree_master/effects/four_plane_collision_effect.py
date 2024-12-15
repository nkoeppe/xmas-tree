from abstracts.effect import Effect

from utils.get_tuple_from_json_array import get_tuple_from_json_array

from decoratos.register_effect import RegisterEffect


@RegisterEffect()
class FourPlaneCollisionEffect(Effect):
    """
    Four planes move vertically and horizontally, creating a crisscrossing effect.
    """
    effect_selector = 'four-plain-collision'
    default_config = {
        "speed": 1,
        "plane_height": 5,
        "color_1": (255, 255, 0),
        "color_2": (255, 0, 0),
        "color_3": (255, 0,255),
        "color_4": (0, 0, 255),
    }


    def __init__(self, **kwargs): # min_max_y, min_max_x, speed=1, colors=((0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)), plane_height=10):
        super().__init__(**kwargs)
        self.speed = self.get_config('speed', float)
        self.plane_height = self.get_config('plane_height', float)
        self.color_1 = self.get_config('color_1', get_tuple_from_json_array)
        self.color_2 = self.get_config('color_2', get_tuple_from_json_array)
        self.color_3 = self.get_config('color_3', get_tuple_from_json_array)
        self.color_4 = self.get_config('color_4', get_tuple_from_json_array)

        # Initialize plane positions and directions
        self.planes = [
            {"pos": self.min_y - self.plane_height / 2, "direction": 1, "axis": "y", "color": self.color_1},
            {"pos": self.max_y + self.plane_height / 2, "direction": -1, "axis": "y", "color": self.color_2},
            {"pos": self.min_x - self.plane_height / 2, "direction": 1, "axis": "x", "color": self.color_3},
            {"pos": self.max_x + self.plane_height / 2, "direction": -1, "axis": "x", "color": self.color_4},
        ]

    def update(self):
        for i, coord in enumerate(self.coords):
            self.pixels[i] = (0, 0, 0)  # Default to off
            for plane in self.planes:
                axis_value = coord[0] if plane["axis"] == "x" else coord[2]
                if plane["pos"] - self.plane_height / 2 <= axis_value <= plane["pos"] + self.plane_height / 2:
                    self.pixels[i] = plane["color"]

        for plane in self.planes:
            if plane["axis"] == "y":
                if plane["pos"] - self.plane_height / 2 < self.min_y and plane["direction"] == -1:
                    plane["direction"] = 1
                elif plane["pos"] + self.plane_height / 2 > self.max_y and plane["direction"] == 1:
                    plane["direction"] = -1
            elif plane["axis"] == "x":
                if plane["pos"] - self.plane_height / 2 < self.min_x and plane["direction"] == -1:
                    plane["direction"] = 1
                elif plane["pos"] + self.plane_height / 2 > self.max_x and plane["direction"] == 1:
                    plane["direction"] = -1

            plane["pos"] += plane["direction"] * self.speed
