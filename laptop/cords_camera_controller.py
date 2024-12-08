import paho.mqtt.client as mqtt
import cv2
import os
import json

# Configuration
with open("config_laptop.json", "r") as config_file:
    config = json.load(config_file)

MQTT_BROKER = config["mqtt_broker"]
MQTT_LED_ON = config["mqtt_topics"]["led_on"]
MQTT_LED_OFF = config["mqtt_topics"]["led_off"]
MQTT_PHOTO_DONE = config["mqtt_topics"]["photo_done"]
CAMERA_INDEX = config["camera_index"]
OUTPUT_DIRECTORY = config["output_directory"]

# MQTT Client
client = mqtt.Client("Laptop")

# State
led_status = None
led_id = None


def capture_image(status, led):
    """Capture image and save it."""
    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    camera = cv2.VideoCapture(CAMERA_INDEX)
    ret, frame = camera.read()
    if ret:
        filename = os.path.join(OUTPUT_DIRECTORY, f"led_{status}_{led}.jpg")
        cv2.imwrite(filename, frame)
        print(f"Captured image: {filename}")
    else:
        print(f"Error: Failed to capture image for LED {led}.")
        raise RuntimeError("Camera capture failed.")
    camera.release()


def on_message(client, userdata, message):
    """Handle incoming MQTT messages."""
    global led_status, led_id

    try:
        if message.topic in [MQTT_LED_ON, MQTT_LED_OFF]:
            led_id = int(message.payload.decode())
            led_status = "on" if message.topic == MQTT_LED_ON else "off"
            print(f"Received LED {led_status} signal for {led_id}")

            # Take a photo
            capture_image(led_status, led_id)

            # Publish acknowledgment
            client.publish(MQTT_PHOTO_DONE, led_id)
            print(f"Published photo done for LED {led_id}")

    except Exception as e:
        print(f"Error handling message {message.topic}: {e}")


def main():
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER)
        client.subscribe([(MQTT_LED_ON, 0), (MQTT_LED_OFF, 0)])
        client.loop_forever()

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
