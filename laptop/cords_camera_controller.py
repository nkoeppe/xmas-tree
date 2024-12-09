import paho.mqtt.client as mqtt
import cv2
import os
import json
import time

# Configuration
with open("config_laptop.json", "r") as config_file:
    config = json.load(config_file)

MQTT_BROKER = config["mqtt_broker"]
MQTT_LED_ON = config["mqtt_topics"]["led_on"]
MQTT_LED_OFF = config["mqtt_topics"]["led_off"]
MQTT_PHOTO_DONE = config["mqtt_topics"]["photo_done"]
MQTT_CYCLE_DONE = config["mqtt_topics"]["cycle_done"]
MQTT_READY_NEXT_ANGLE = config["mqtt_topics"]["ready_next_angle"]
CAMERA_INDEX = config["camera_index"]
OUTPUT_DIRECTORY = config["output_directory"]

client = mqtt.Client(client_id="Laptop", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
led_status = None
led_id = None
current_angle = 0
angles = [0, 90, 180, 270]
cycle_done_flag = False

def capture_image(status, led, angle):
    """Capture image and save it."""
    time.sleep(2)  # Ensure LED state is stable
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, f"angle_{angle}"), exist_ok=True)
    camera = cv2.VideoCapture(CAMERA_INDEX)
    ret, frame = camera.read()
    if ret:
        filename = os.path.join(OUTPUT_DIRECTORY, f"angle_{angle}", f"led_{status}_{led}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Captured image: {filename}")
    else:
        print(f"Error: Failed to capture image for LED {led}.")
        raise RuntimeError("Camera capture failed.")
    camera.release()

def on_message(client, userdata, message):
    global led_status, led_id, cycle_done_flag

    try:
        if message.topic in [MQTT_LED_ON, MQTT_LED_OFF]:
            led_id = int(message.payload.decode())
            led_status = "on" if message.topic == MQTT_LED_ON else "off"
            print(f"Received LED {led_status} signal for {led_id}")
            capture_image(led_status, led_id, current_angle)

            # Publish acknowledgment
            client.publish(MQTT_PHOTO_DONE, led_id)
            print(f"Published photo done for LED {led_id}")

        elif message.topic == MQTT_CYCLE_DONE:
            cycle_done_flag = True
            print("Cycle done received from Raspberry Pi.")

    except Exception as e:
        print(f"Error handling message {message.topic}: {e}")

def wait_for_flag(flag_name, timeout=30):
    """Wait for a flag to be set within a timeout."""
    global cycle_done_flag
    start_time = time.time()
    while not globals()[flag_name]:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout reached while waiting for {flag_name}.")
        time.sleep(0.1)
    globals()[flag_name] = False

def main():
    global current_angle

    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER)
        client.subscribe([(MQTT_LED_ON, 0), (MQTT_LED_OFF, 0), (MQTT_CYCLE_DONE, 0)])
        client.loop_start()

        for angle in angles:
            current_angle = angle
            print(f"Processing angle {angle}. Waiting for LED cycle to complete...")
            wait_for_flag("cycle_done_flag")

            input(f"Rotate the object to angle {angle}° and press Enter when ready...")
            client.publish(MQTT_READY_NEXT_ANGLE, "")
            print("Ready next angle command sent to Raspberry Pi.")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
