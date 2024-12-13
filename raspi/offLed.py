import sys
import neopixel
import board
import time

# Configuration
PIXEL_PIN = board.D18  # GPIO pin where the NeoPixels are connected

def turn_off_leds(num_leds):
    strip = neopixel.NeoPixel(PIXEL_PIN, num_leds, brightness=0.0, auto_write=True)
    strip.fill((0, 0, 0))  # Turn all LEDs off
    strip.show()           # Update the LEDs

def main():
    if len(sys.argv) != 2:
        print("Usage: python turnOff.py <num_leds>")
        sys.exit(1)

    try:
        num_leds = int(sys.argv[1])
    except ValueError:
        print("Error: Delay must be an integer.")
        sys.exit(1)

    turn_off_leds(num_leds)
    print("All LEDs are off.")

if __name__ == "__main__":
    main()
