import sys
import neopixel
import board

# Configuration
PIXEL_PIN = board.D18  # GPIO pin where the NeoPixels are connected


def set_leds(num_leds, r, g, b, brightness):
    # Create a NeoPixel object
    strip = neopixel.NeoPixel(PIXEL_PIN, num_leds, brightness=brightness, auto_write=True)

    # Set the color for all LEDs
    strip.fill((r, g, b))
    strip.show()  # Update the LEDs


def main():
    if len(sys.argv) != 6:
        print("Usage: python script.py <num_leds> <r> <g> <b> <brightness>")
        sys.exit(1)

    try:
        num_leds = int(sys.argv[1])
        r = int(sys.argv[2])
        g = int(sys.argv[3])
        b = int(sys.argv[4])
        brightness = float(sys.argv[5])

        if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
            raise ValueError("RGB values must be between 0 and 255.")
        if not (0.0 <= brightness <= 1.0):
            raise ValueError("Brightness must be between 0.0 and 1.0.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    set_leds(num_leds, r, g, b, brightness)
    print(f"LEDs set to RGB({r}, {g}, {b}) with brightness {brightness}.")


if __name__ == "__main__":
    main()
