from abstracts.effect import Effect

class FourPlaneCollisionEffect(Effect):
    """
    Four planes move vertically and horizontally, creating a crisscrossing effect.
    """
    def __init__(self, pixels, coords, min_max_y, min_max_x, speed=1, colors=((0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)), plane_height=10):
        super().__init__(pixels, coords)
        self.min_y, self.max_y = min_max_y
        self.min_x, self.max_x = min_max_x
        self.plane_height = plane_height
        self.speed = speed

        # Initialize plane positions and directions
        self.planes = [
            {"pos": self.min_y - plane_height / 2, "direction": 1, "axis": "y", "color": colors[0]},
            {"pos": self.max_y + plane_height / 2, "direction": -1, "axis": "y", "color": colors[1]},
            {"pos": self.min_x - plane_height / 2, "direction": 1, "axis": "x", "color": colors[2]},
            {"pos": self.max_x + plane_height / 2, "direction": -1, "axis": "x", "color": colors[3]},
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
