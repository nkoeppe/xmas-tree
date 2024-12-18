import time

import matplotlib

from utils.load_coords import load_coords

matplotlib.use('webagg')
from matplotlib.animation import FuncAnimation

from matplotlib import rcParams
rcParams['webagg.address'] = '0.0.0.0'
rcParams['webagg.port'] = 8888
rcParams['webagg.open_in_browser'] = False

from controllers.led_controller import LEDController
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import paho.mqtt.client as mqtt
from utils.generate_xmas_tree_coords import generate_xmas_tree
from controllers.effect_controller import EffectController
from utils.register_effects import registered_effects


coords = None
min_z = None
max_z = None
print(f"Registered effects: {registered_effects}")

def on_message(client, userdata, message):
    """
    Callback for handling MQTT messages to update effects with configurations.
    """
    global effect_controller
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        effect_name = payload.get("effect_name", "").lower()
        config = payload.get("config", {})
        print(f"Received effect: {effect_name} with config: {config}")
        effect_controller.change_effect(effect_name, **config)
    except Exception as e:
        print(f"Error handling MQTT message: {e}")

def plot_leds(controller, coords):
    """
    Live-updating 3D LED plot using Matplotlib's FuncAnimation.
    """
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Extract coordinates
    x, y, z = zip(*coords)
    scatter = ax.scatter(x, y, z, c=[[0, 0, 0] for _ in coords], s=100)

    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
    ax.set_zlim([-100, 100])
    ax.set_box_aspect([1, 1, 1])

    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")

    def update(frame):
        """
        Animation update function.
        """
        pixels = controller.get_plot_data()
        if pixels:
            # Normalize colors for Matplotlib
            colors = [tuple(np.array([c[0], c[1], c[2]]) / 255) for c in pixels]
            scatter.set_color(colors)

    # Use FuncAnimation to update the plot
    ani = FuncAnimation(fig, update, interval=0.3, cache_frame_data=False)

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D LED Effect Visualizer")
    parser.add_argument("--effect", choices=["wave", "test", "plane-sweep", "two-plain"], default="wave", help="Select the effect to visualize.")
    parser.add_argument('--render', help="Flag whether to render a 3D plot.", action=argparse.BooleanOptionalAction)
    parser.add_argument('--dry', help="Run in dry run.", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    # coords = generate_xmas_tree()
    coords = load_coords()
    render_plot = args.render or False
    dry_mode = args.dry or False

    controller = LEDController(coords, pixel_count=len(coords), drymode=dry_mode)
    effect_controller = EffectController(controller)

    if args.effect:
        effect_controller.change_effect(args.effect)

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_message = on_message
    mqtt_client.connect("fancyguysdev.de")
    mqtt_client.subscribe("led/effect")
    mqtt_client.loop_start()

    controller.start()

    try:
        if render_plot:
            plot_leds(controller, coords)
        else:
            while controller.running:
                time.sleep(1)

    except KeyboardInterrupt:
        print("Stopping...")
        controller.stop()

    finally:
        print("Exiting...")
