import paho.mqtt.client as mqtt
import neopixel
import json
import time
import board

# Configuration
with open("config_pi.json", "r") as config_file:
    config = json.load(config_file)

MQTT_BROKER = config["mqtt_broker"]
NUM_LEDS = config["num_leds"]
PIXEL_PIN = board.D18
MQTT_LED_ON = config["mqtt_topics"]["led_on"]
MQTT_LED_OFF = config["mqtt_topics"]["led_off"]
MQTT_PHOTO_DONE = config["mqtt_topics"]["photo_done"]
MQTT_READY_NEXT_ANGLE = config["mqtt_topics"]["ready_next_angle"]
MQTT_CYCLE_DONE = config["mqtt_topics"]["cycle_done"]

# Setup for NeoPixel LEDs
strip = neopixel.NeoPixel(PIXEL_PIN, NUM_LEDS,  brightness=0.5, auto_write=True)

# MQTT Client
client = mqtt.Client(client_id="RaspberryPi", callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

photo_done_flag = False
ready_next_angle_flag = False

def log_debug(message):
    """Utility to log debug messages."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[DEBUG] {timestamp}: {message}")

def on_message(client, userdata, message):
    global photo_done_flag, ready_next_angle_flag
    log_debug(f"Message received on topic {message.topic}: {message.payload.decode()}")
    if message.topic == MQTT_PHOTO_DONE:
        photo_done_flag = True
        log_debug(f"Photo done flag set for LED: {message.payload.decode()}")
    elif message.topic == MQTT_READY_NEXT_ANGLE:
        ready_next_angle_flag = True
        log_debug("Ready next angle flag set.")

def wait_for_ack(flag_name, timeout=120):
    """Wait for a flag to be set within a timeout."""
    global photo_done_flag, ready_next_angle_flag
    log_debug(f"Waiting for {flag_name} to be set. Timeout: {timeout}s.")
    start_time = time.time()
    while not globals()[flag_name]:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Timeout reached while waiting for {flag_name}.")
        time.sleep(0.1)
    globals()[flag_name] = False
    log_debug(f"{flag_name} acknowledged.")

def main():
    strip.fill((0, 0, 0))

    global photo_done_flag, ready_next_angle_flag

    client.on_message = on_message
    try:
        log_debug("Connecting to MQTT broker.")
        client.connect(MQTT_BROKER)
        client.subscribe([(MQTT_PHOTO_DONE, 0), (MQTT_READY_NEXT_ANGLE, 0)])
        log_debug(f"Subscribed to topics: {MQTT_PHOTO_DONE}, {MQTT_READY_NEXT_ANGLE}.")
        client.loop_start()
        log_debug("MQTT loop started.")

        while True:  # Infinite loop for multiple angles
            for led in range(NUM_LEDS):
                # Turn off all LEDs
                strip.fill((0, 0, 0))
                strip.show()
                client.publish(MQTT_LED_OFF, led)
                log_debug(f"Published LED off command for LED {led}.")
                wait_for_ack("photo_done_flag")

                # Turn on specific LED
                strip.fill((0, 0, 0))
                strip[led] = (255, 255, 255)  # Full brightness
                strip.show()
                client.publish(MQTT_LED_ON, led)
                log_debug(f"Published LED on command for LED {led}.")
                wait_for_ack("photo_done_flag")

            # Notify the laptop that the LED cycle is complete
            client.publish(MQTT_CYCLE_DONE, "")
            log_debug("Published cycle done. Waiting for laptop to be ready for the next angle.")
            wait_for_ack("ready_next_angle_flag")

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
    log_debug("Starting the LED control script.")
    main()
