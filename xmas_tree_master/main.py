from controllers.led_controller import LEDController
from effects.wave_3d_effect import Wave3DEffect
from effects.test_effect import TestEffect
import numpy as np
import matplotlib.pyplot as plt
import argparse
import json
import paho.mqtt.client as mqtt

from effects.plane_sweep_effect import PlaneSweepEffect
from utils import load_coords, generate_xmas_tree


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
                colors = [tuple(np.clip(np.array([color[1], color[2], color[0]]) / 255, 0, 1)) for color in pixels]
                scatter.set_facecolor(colors)  # Correctly update scatter face colors
                plt.draw()
            plt.pause(0.05)
    except Exception as e:
        print(f"Error in plotting loop: {e}")
    finally:
        controller.stop()

def on_message(client, userdata, message):
    """
    Callback function triggered when an MQTT message is received.
    Dynamically updates the LED effect based on the message payload.
    """
    global controller
    try:
        payload = json.loads(message.payload.decode("utf-8"))
        effect_name = payload.get("effect", "").lower()
        print(f"Received effect: {effect_name}")
        # Select the effect based on the payload
        if effect_name == "wave":
            new_effect = Wave3DEffect(controller.pixels, controller.coords)
        elif effect_name == "plane-sweep":
            new_effect = PlaneSweepEffect(controller.pixels, controller.coords)
        elif effect_name == "test":
            new_effect = TestEffect(controller.pixels, controller.coords)
        else:
            print(f"Unknown effect: {effect_name}")
            return

        controller.set_effect(new_effect)
        print(f"Effect updated to: {effect_name}")
    except Exception as e:
        print(f"Error handling MQTT message: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D LED Effect Visualizer")
    parser.add_argument("--effect", choices=["wave", "test", "plane-sweep"], default="wave", help="Select the effect to visualize.")
    parser.add_argument('--render', help="Flag wether ro render a 3d plot.", action=argparse.BooleanOptionalAction)
    parser.add_argument('--dry', help="Run in dry run.", action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    coords = generate_xmas_tree()
    # coords = load_coords()
    render_plot = False
    dry_mode = False

    if args.render:
        render_plot = True
    if args.dry:
        dry_mode = True

    # Initialize controller
    controller = LEDController(coords, pixel_count=len(coords),drymode=dry_mode)
    # Set and start the selected effect
    if args.effect == "wave":
        effect = Wave3DEffect(controller.pixels, controller.coords)
    elif args.effect == "plane-sweep":
        effect = PlaneSweepEffect(controller.pixels, controller.coords)
    else:
        effect = TestEffect(controller.pixels, controller.coords)


    controller.set_effect(effect)
    mqtt_client = mqtt.Client( mqtt.CallbackAPIVersion.VERSION2)
    mqtt_client.on_message = on_message
    mqtt_client.connect("fancyguysdev.de")
    mqtt_client.subscribe("led/effect")
    mqtt_client.loop_start()

    # Start the controller
    controller.start()

    # Start the plot (in the main thread)
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
