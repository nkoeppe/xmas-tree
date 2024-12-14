from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import threading
from controllers.led_controller import LEDController
from effects.wave_3d_effect import Wave3DEffect
from effects.plane_sweep_effect import PlaneSweepEffect
from effects.test_effect import TestEffect
import argparse

app = Flask(__name__)
socketio = SocketIO(app)  # Enable WebSocket support

controller = None  # Global controller instance


def generate_xmas_tree(num_points_foliage=200, num_points_trunk=10, height=200, radius=60, trunk_height=20,
                       trunk_radius=5):
    coords = []
    for _ in range(num_points_foliage):
        z = np.random.uniform(0, height)
        r = radius * (1 - z / height)
        theta = np.random.uniform(0, 2 * np.pi)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        coords.append((x, y, z))

    for _ in range(num_points_trunk):
        z = np.random.uniform(-trunk_height, 0)
        theta = np.random.uniform(0, 2 * np.pi)
        r = np.random.uniform(0, trunk_radius)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        coords.append((x, y, z))

    return coords


@app.route("/")
def index():
    return render_template("index.html")


def send_updates():
    """Background thread to continuously send LED state to the browser."""
    while controller and controller.running:
        pixels = controller.get_plot_data()
        if pixels:
            colors = [tuple(np.clip(np.array(color) / 255, 0, 1)) for color in pixels]
            socketio.emit("update_leds", {"colors": colors})
        socketio.sleep(0.1)  # Adjust the interval as needed


@socketio.on("connect")
def on_connect():
    """Handle browser connection."""
    print("Client connected")
    coords = controller.coords if controller else []
    socketio.emit("init_coords", {"coords": coords})

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

    controller = LEDController(coords, pixel_count=len(coords), drymode=True)

    if args.effect == "wave":
        effect = Wave3DEffect(controller.pixels, controller.coords)
    elif args.effect == "plane-sweep":
        effect = PlaneSweepEffect(controller.pixels, controller.coords)
    else:
        effect = TestEffect(controller.pixels, controller.coords)

    controller.set_effect(effect)

    # Start the controller in a separate thread
    threading.Thread(target=controller.start, daemon=True).start()

    # Start the Flask-SocketIO server with the background update thread
    socketio.start_background_task(send_updates)
    socketio.run(app, host="0.0.0.0", port=5000)
