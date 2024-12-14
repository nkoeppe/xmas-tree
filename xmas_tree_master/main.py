from controllers.led_controller import LEDController
from effects.wave_3d_effect import Wave3DEffect
from effects.test_effect import TestEffect
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json


from effects.plane_sweep_effect import PlaneSweepEffect


def plot_leds(controller, coords):
    """
    Main thread function for plotting LEDs with Matplotlib.
    Provides a zoomable and interactive 3D plot.
    """
    plt.ion()  # Enable interactive mode
    fig = plt.figure(figsize=(12, 8))  # Increase figure size
    ax = fig.add_subplot(111, projection="3d")

    x, y, z = zip(*coords)
    scatter = ax.scatter(x, y, z, c=[[0, 0, 0] for _ in coords], s=100)
    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
    ax.set_zlim([-100, 100])
    ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

    # Add labels for clarity
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")

    # Enable mouse rotation and zooming
    fig.canvas.mpl_connect("scroll_event", lambda event: None)

    try:
        while controller.running:
            pixels = controller.get_plot_data()
            if pixels:
                colors = [tuple(np.clip(np.array(color) / 255, 0, 1)) for color in pixels]
                scatter.set_facecolor(colors)  # Correctly update scatter face colors
                plt.draw()
            plt.pause(0.05)
    except Exception as e:
        print(f"Error in plotting loop: {e}")
    finally:
        controller.stop()

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
        coords = json.load(file)  # Load the JSON array directly
    return [tuple(coord) for coord in coords]  # Convert each coordinate to a tuple



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D LED Effect Visualizer")
    parser.add_argument("--effect", choices=["wave", "test", "plane-sweep"], default="wave", help="Select the effect to visualize.")
    args = parser.parse_args()

    coords = generate_xmas_tree()
    # coords = load_coords()

    # Initialize controller
    controller = LEDController(coords, pixel_count=len(coords),drymode=True)

    # Set and start the selected effect
    if args.effect == "wave":
        effect = Wave3DEffect(controller.pixels, controller.coords)
    elif args.effect == "plane-sweep":
        effect = PlaneSweepEffect(controller.pixels, controller.coords)
    else:
        effect = TestEffect(controller.pixels, controller.coords)


    controller.set_effect(effect)

    # Start the controller
    controller.start()

    # Start the plot (in the main thread)
    try:
        print("Press Ctrl+C to exit.")
        plot_leds(controller, coords)
    except KeyboardInterrupt:
        controller.stop()
        print("Exiting...")
