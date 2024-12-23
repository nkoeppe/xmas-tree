# main.py
import time
import json
import argparse
import paho.mqtt.client as mqtt
import matplotlib
from matplotlib import rcParams
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt

from utils.load_coords import load_coords
from controllers.led_controller import LEDController
from controllers.effect_controller import EffectController
from registry.effect_registry import EffectRegistry
from utils.register_effects import registered_effects

matplotlib.use('webagg')
rcParams['webagg.address'] = '0.0.0.0'

with open("configs/config_master.json") as f:
    config_data = json.load(f)

default_client_id = config_data.get("client_id", "unknown")

coords = None
effect_controller = None

def publish_available_effects(client, client_id):
    """
    Publishes the list of available effects and their default configs for this client.
    """
    effects_list = EffectRegistry.list_effects()
    data = {
        "client_id": client_id,
        "effects": effects_list
    }
    print(f"Publishing available effects: {data}")

    client.publish(f"led/effects/{client_id}", json.dumps(data))

def on_connect(client, userdata, flags, rc, properties):
    print(rc)
    if rc == 0:
        print("Connected to MQTT broker")
        client.publish("led/clients", json.dumps({"client_id": my_client_id, "status": "connected"}))

        publish_available_effects(client, my_client_id)

def on_disconnect(client, userdata, flags, rc, properties):
    print("Disconnected from MQTT broker")
    client.publish("led/clients", json.dumps({"client_id": my_client_id, "status": "disconnected"}))

def on_message(client, userdata, message):
    try:
        if message.topic == "led/effect":
            payload = json.loads(message.payload.decode("utf-8"))
            if payload.get("client_id") == my_client_id:
                selector = payload.get("effect_name", "").lower()
                config = payload.get("config", {})
                print(f"Received effect for this client ({my_client_id}): {selector} with config {config}")
                effect_controller.change_effect(selector, client_id=my_client_id, **config)

        elif message.topic == "led/effect/save-default":
            payload = json.loads(message.payload.decode("utf-8"))
            if payload.get("client_id") == my_client_id:
                effect_name = payload.get("effect_name")
                config = payload.get("config", {})
                effect_controller.save_default_config(my_client_id, effect_name, config)
                print(f"Saved default config for {effect_name}")
    except Exception as e:
        print(f"Error handling MQTT message: {e}")

def plot_leds(controller, coords):
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
    ax.set_title(f"3D LED Visualizer - Client ID: {my_client_id}")

    def update(frame):
        pixels = controller.get_plot_data()
        if pixels:
            colors = [tuple(np.array([c[0], c[1], c[2]]) / 255) for c in pixels]
            scatter.set_color(colors)

    anim = FuncAnimation(fig, update, interval=0.3, cache_frame_data=False)
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="3D LED Effect Visualizer")
    parser.add_argument("--effect", choices=["wave", "test", "plane-sweep", "two-plain"], default="wave")
    parser.add_argument('--render', action=argparse.BooleanOptionalAction)
    parser.add_argument('--dry', action=argparse.BooleanOptionalAction)
    parser.add_argument('--client-id', default=default_client_id)
    parser.add_argument('--port', type=int, default=8888)
    args = parser.parse_args()

    my_client_id = args.client_id
    webagg_port = args.port
    rcParams['webagg.port'] = webagg_port

    coords = load_coords()
    controller = LEDController(coords, pixel_count=len(coords), drymode=(args.dry or False))
    effect_controller = EffectController(controller)
    if args.effect:
        effect_controller.change_effect(args.effect, client_id=my_client_id)

    mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=my_client_id, clean_session=True)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    mqtt_client.connect("fancyguysdev.de")
    mqtt_client.subscribe("led/effect")
    mqtt_client.subscribe("led/effect/save-default")
    mqtt_client.loop_start()

    controller.start()

    try:
        if args.render:
            plot_leds(controller, coords)
        else:
            while controller.running:
                time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        controller.stop()
    finally:
        mqtt_client.publish("led/clients", json.dumps({"client_id": my_client_id, "status": "disconnected"}))
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Exiting...")
