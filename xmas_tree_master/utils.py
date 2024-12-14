import numpy as np
import json

def generate_xmas_tree(num_points_foliage=200, num_points_trunk=10, height=200, radius=60, trunk_height=20,
                       trunk_radius=5):
    """
    Generate 3D coordinates for a Christmas tree.

    :param num_points_foliage: Number of points for the foliage (cone shape).
    :param num_points_trunk: Number of points for the trunk (cylinder shape).
    :param height: Height of the tree.
    :param radius: Base radius of the foliage cone.
    :param trunk_height: Height of the trunk.
    :param trunk_radius: Radius of the trunk cylinder.
    :return: List of (x, y, z) tuples representing the tree.
    """
    coords = []

    # Generate foliage (cone shape)
    for _ in range(num_points_foliage):
        z = np.random.uniform(0, height)  # Height along the tree
        r = radius * (1 - z / height)  # Radius decreases as we go up
        theta = np.random.uniform(0, 2 * np.pi)  # Random angle around the cone
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        coords.append((x, y, z))

    # Generate trunk (cylinder shape)
    for _ in range(num_points_trunk):
        z = np.random.uniform(-trunk_height, 0)  # Trunk is below foliage
        theta = np.random.uniform(0, 2 * np.pi)  # Random angle around the cylinder
        r = np.random.uniform(0, trunk_radius)  # Random distance from center (circular cross-section)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        coords.append((x, y, z))

    return coords


def load_coords():
    """
    Load coordinates from a JSON file.
    """
    with open("coords.json", "r") as file:
        coords = json.load(file)
    return [tuple(coord) for coord in coords]

