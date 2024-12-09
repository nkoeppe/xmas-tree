import paho.mqtt.client as mqtt
import neopixel
import json
import time

# Configuration
with open("config_pi.json", "r") as config_file:
    config = json.load(config_file)

MQTT_BROKER = config["mqtt_broker"]
NUM_LEDS = config["num_leds"]
PIXEL_PIN = config["gpio_pin"]
MQTT_LED_ON = config["mqtt_topics"]["led_on"]
MQTT_LED_OFF = config["mqtt_topics"]["led_off"]
MQTT_PHOTO_DONE = config["mqtt_topics"]["photo_done"]
MQTT_READY_NEXT_ANGLE = config["mqtt_topics"]["ready_next_angle"]
MQTT_CYCLE_DONE = config["mqtt_topics"]["cycle_done"]

# Setup for NeoPixel LEDs
strip = neopixel.NeoPixel(PIXEL_PIN, NUM_LEDS)

# MQTT Client
client = mqtt.Client(client_id="RaspberryPi", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

photo_done_flag = False
ready_next_angle_flag = False

def on_message(client, userdata, message):
    global photo_done_flag, ready_next_angle_flag
    if message.topic == MQTT_PHOTO_DONE:
        photo_done_flag = True
        print(f"Photo done received for LED: {message.payload.decode()}")
    elif message.topic == MQTT_READY_NEXT_ANGLE:
        ready_next_angle_flag = True
        print("Ready next angle command received from Laptop.")

def wait_for_ack(flag_name, timeout=30):
    """Wait for a flag to be set within a timeout."""
    global photo_done_flag, ready_next_angle_flag
    start_time = time.time()
    while not globals()[flag_name]:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout reached while waiting for {flag_name}.")
        time.sleep(0.1)
    globals()[flag_name] = False

def main():
    global photo_done_flag, ready_next_angle_flag

    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER)
        client.subscribe([(MQTT_PHOTO_DONE, 0), (MQTT_READY_NEXT_ANGLE, 0)])
        client.loop_start()

        while True:  # Infinite loop for multiple angles
            for led in range(NUM_LEDS):
                # Turn off all LEDs
                strip.fill((0, 0, 0))
                strip.show()
                client.publish(MQTT_LED_OFF, led)
                print(f"Published LED off for {led}")
                wait_for_ack("photo_done_flag")

                # Turn on specific LED
                strip.fill((0, 0, 0))
                strip[led] = (255, 255, 255)  # Full brightness
                strip.show()
                client.publish(MQTT_LED_ON, led)
                print(f"Published LED on for {led}")
                wait_for_ack("photo_done_flag")

            # Notify the laptop that the LED cycle is complete
            client.publish(MQTT_CYCLE_DONE, "")
            print("Published cycle done for current angle. Waiting for Laptop to be ready for the next angle.")
            wait_for_ack("ready_next_angle_flag")

    except Exception as e:
        print(f"Unexpected error: {e}")

    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
