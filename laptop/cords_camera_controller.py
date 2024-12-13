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
MQTT_PHOTO_SAMPLE_DONE = config["mqtt_topics"]["photo_sample_done"]
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

def log_debug(message):
    """Utility to log debug messages with a timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[DEBUG] {timestamp}: {message}")

def capture_image(status, led, angle):
    """Capture image and save it."""
    log_debug(f"Starting image capture for LED {led} at angle {angle}. Status: {status}")
    os.makedirs(os.path.join(OUTPUT_DIRECTORY, f"angle_{angle}"), exist_ok=True)
    camera = cv2.VideoCapture(CAMERA_INDEX)
    ret, frame = camera.read()
    if ret:
        filename = os.path.join(OUTPUT_DIRECTORY, f"angle_{angle}", f"led_{status}_{led}.jpg")
        cv2.imwrite(filename, frame)
        log_debug(f"Captured image: {filename}")
    else:
        log_debug(f"Error: Failed to capture image for LED {led}.")
        raise RuntimeError("Camera capture failed.")
    camera.release()
    log_debug(f"Image capture complete for LED {led}.")

def on_message(client, userdata, message):
    global led_status, led_id, cycle_done_flag

    try:
        log_debug(f"Message received on topic {message.topic}: {message.payload.decode()}")
        if message.topic in [MQTT_LED_ON, MQTT_LED_OFF]:
            led_id = int(message.payload.decode())
            led_status = "on" if message.topic == MQTT_LED_ON else "off"
            log_debug(f"Processing LED {led_status} signal for LED {led_id}.")
            capture_image(led_status, led_id, current_angle)

            # Publish acknowledgment
            client.publish(MQTT_PHOTO_DONE, led_id)
            log_debug(f"Published photo done for LED {led_id}.")

        elif message.topic == MQTT_CYCLE_DONE:
            cycle_done_flag = True
            log_debug("Cycle done signal received from Raspberry Pi.")

    except Exception as e:
        log_debug(f"Error handling message on topic {message.topic}: {e}")

def wait_for_flag(flag_name, timeout=600):
    """Wait for a flag to be set within a timeout."""
    log_debug(f"Waiting for {flag_name} to be set. Timeout: {timeout}s.")
    start_time = time.time()
    while not globals()[flag_name]:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout reached while waiting for {flag_name}.")
        time.sleep(0.1)
    globals()[flag_name] = False
    log_debug(f"{flag_name} acknowledged.")

def take_sample_pic(angle):
        log_debug(f"Taking sample image at angle {angle}. Make sure the room light is on.")
        input(f"[INFO] Turn the light on and press Enter when ready...")
        capture_image("sample", -1, angle)
        input(f"[INFO] Turn the light off and press Enter when ready...")
        client.publish(MQTT_PHOTO_SAMPLE_DONE, "")


def main():
    global current_angle

    client.on_message = on_message
    try:
        log_debug("Connecting to MQTT broker.")
        client.connect(MQTT_BROKER)
        client.subscribe([(MQTT_LED_ON, 0), (MQTT_LED_OFF, 0), (MQTT_CYCLE_DONE, 0)])
        log_debug(f"Subscribed to topics: {MQTT_LED_ON}, {MQTT_LED_OFF}, {MQTT_CYCLE_DONE}.")
        client.loop_start()
        log_debug("MQTT loop started.")

        for angle in angles:
            take_sample_pic(angle)

            current_angle = angle
            log_debug(f"Processing angle {angle}. Waiting for LED cycle to complete.")
            wait_for_flag("cycle_done_flag")

            input(f"[INFO] Rotate the object to angle {angle}° and press Enter when ready...")
            log_debug(f"User confirmed readiness for angle {angle}. Sending ready signal to Raspberry Pi.")
            client.publish(MQTT_READY_NEXT_ANGLE, "")
            log_debug("Ready next angle command sent to Raspberry Pi.")

    except TimeoutError as te:
        log_debug(f"Timeout error: {te}")
    except Exception as e:
        log_debug(f"Unexpected error: {e}")

    finally:
        log_debug("Stopping MQTT loop and disconnecting client.")
        client.loop_stop()
        client.disconnect()
        log_debug("Disconnected from MQTT broker.")

if __name__ == "__main__":
    log_debug("Starting the Laptop control script.")
    main()
