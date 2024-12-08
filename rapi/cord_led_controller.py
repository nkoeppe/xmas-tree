import paho.mqtt.client as mqtt
import neopixel
import time
import json

# Configuration
with open("config_pi.json", "r") as config_file:
    config = json.load(config_file)

MQTT_BROKER = config["mqtt_broker"]
NUM_LEDS = config["num_leds"]
PIXEL_PIN = config["gpio_pin"]
MQTT_LED_ON = config["mqtt_topics"]["led_on"]
MQTT_LED_OFF = config["mqtt_topics"]["led_off"]
MQTT_PHOTO_DONE = config["mqtt_topics"]["photo_done"]

# Setup for NeoPixel LEDs
strip = neopixel.NeoPixel(PIXEL_PIN, NUM_LEDS)

# MQTT Client
client = mqtt.Client("RaspberryPi")

# MQTT Flags
photo_done_flag = False


def on_message(client, userdata, message):
    global photo_done_flag
    if message.topic == MQTT_PHOTO_DONE:
        photo_done_flag = True
        print(f"Photo done received for LED: {message.payload.decode()}")


def wait_for_ack(timeout=30):
    """Wait for acknowledgment with a timeout."""
    global photo_done_flag
    start_time = time.time()
    while not photo_done_flag:
        if time.time() - start_time > timeout:
            raise TimeoutError("Acknowledgment timeout reached.")
        time.sleep(0.1)
    photo_done_flag = False


def main():
    global photo_done_flag

    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER)
        client.loop_start()

        for led in range(NUM_LEDS):
            # Turn off all LEDs
            strip.fill((0, 0, 0))
            strip.show()
            client.publish(MQTT_LED_OFF, led)
            print(f"Published LED off for {led}")

            try:
                wait_for_ack()
            except TimeoutError as e:
                print(f"Error: {e} for LED {led}. Skipping.")
                continue

            # Turn on specific LED
            strip.fill((0, 0, 0))
            strip[led] = (255, 255, 255)  # Full brightness
            strip.show()
            client.publish(MQTT_LED_ON, led)
            print(f"Published LED on for {led}")

            try:
                wait_for_ack()
            except TimeoutError as e:
                print(f"Error: {e} for LED {led}. Skipping.")
                continue

        strip.fill((0, 0, 0))
        strip.show()
        print("LED cycling complete.")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    main()
