import json

def load_coords():
    """
    Load coordinates from a JSON file.
    """
    with open("coords.json", "r") as file:
        coords = json.load(file)
    return [tuple(coord) for coord in coords]

