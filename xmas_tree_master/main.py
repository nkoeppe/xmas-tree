from controllers.led_controller import LEDController
from effects.wave_3d_effect import  Wave3DEffect
import numpy as np
import matplotlib.pyplot as plt

from effects.test_effect import TestEffect

PIXEL_COUNT = 200

def plot_leds(controller, coords):
    """
    Main thread function for plotting LEDs with Matplotlib.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    x, y, z = zip(*coords)
    scatter = ax.scatter(x, y, z, c=[[0, 0, 0] for _ in coords], s=100)
    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
    ax.set_zlim([-100, 100])

    while controller.running:
        # Fetch the latest LED data
        pixels = controller.get_plot_data()
        if pixels:
            colors = [tuple(np.array(color) / 255) for color in pixels]
            scatter.set_color(colors)
            plt.draw()
        plt.pause(0.05)  # Refresh plot


# Main entry point
if __name__ == "__main__":
    # Example 3D coordinates for 500 LEDs
    np.random.seed(42)
    coords = np.random.randint(-100, 100, (PIXEL_COUNT, 3)).tolist()

    # Initialize controller
    controller = LEDController(coords, pixel_count=PIXEL_COUNT)

    # Set and start an example effect
    effect = Wave3DEffect(controller.pixels, controller.coords)
    controller.set_effect(effect)
    # effect = TestEffect(controller.pixels, controller.coords)
    # controller.set_effect(effect)

    # Start the controller
    controller.start()

    # Start the plot (in the main thread)
    try:
        print("Press Ctrl+C to exit.")
        plot_leds(controller, coords)
    except KeyboardInterrupt:
        controller.stop()
        print("Exiting...")