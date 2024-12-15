import matplotlib
# Switch to WebAgg backend before pyplot import
matplotlib.use('webagg')
from matplotlib import rcParams
rcParams['webagg.address'] = '0.0.0.0'  # Listen on all interfaces
rcParams['webagg.port'] = 8888          # Set desired port

from controllers.led_controller import LEDController
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import paho.mqtt.client as mqtt
from utils.generate_xmas_tree_coords import generate_xmas_tree
from controllers.effect_controller import EffectController
from effects.register_effects import registered_effects

coords = None
min_z = None
max_z = None
print(f"Registered effects: {registered_effects}")

def plot_leds(controller, coords):
    """
    Main thread function for plotting LEDs with Matplotlib.
    Provides a zoomable and interactive 3D plot accessible via browser.
    """
    plt.ion()
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    x, y, z = zip(*coords)
    scatter = ax.scatter(x, y, z, c=[[0, 0, 0] for _ in coords], s=100)
    ax.set_xlim([-100, 100])
    ax.set_ylim([-100, 100])
    ax.set_zlim([-100, 100])
    ax.set_box_aspect([1, 1, 1])

    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")

    try:
        while controller.running:
            pixels = controller.get_plot_data()
            if pixels:
                colors = [tuple(np.clip(np.array([color[1], color[2], color[0]]) / 255, 0, 1)) for color in pixels]
                scatter.set_facecolor(colors)
                plt.draw()
            plt.pause(0.05)
    except Exception as e:
        print(f"Error in plotting loop: {e}")
    finally:
        controller.stop()

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D LED Effect Visualizer")
    parser.add_argument("--effect", choices=["wave", "test", "plane-sweep", "two-plain"], default="wave", help="Select the effect to visualize.")
    parser.add_argument('--render', help="Flag wether ro render a 3d plot.", action=argparse.BooleanOptionalAction)
    parser.add_argument('--dry', help="Run in dry run.", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    coords = generate_xmas_tree()

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
        print("Press Ctrl+C to exit.")
        if render_plot:
            plot_leds(controller, coords)
        else:
            while controller.running:
                pass
    except KeyboardInterrupt:
        controller.stop()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Exiting...")
