import sys
import neopixel
import board
import time

# Configuration
PIXEL_PIN = board.D18  # GPIO pin where the NeoPixels are connected


def transition_color(strip, start_color, end_color, steps, delay):
    r_start, g_start, b_start = start_color
    r_end, g_end, b_end = end_color

    for step in range(steps):
        r = r_start + (r_end - r_start) * step // steps
        g = g_start + (g_end - g_start) * step // steps
        b = b_start + (b_end - b_start) * step // steps
        strip.fill((r, g, b))
        strip.show()
        time.sleep(delay)


def color_cycle(strip, num_leds, brightness, delay=0.1, transition_steps=50):
    colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (0, 255, 255),  # Cyan
        (255, 0, 255),  # Magenta
        (255, 255, 255)  # White
    ]

    while True:
        for i in range(len(colors)):
            start_color = colors[i]
            end_color = colors[(i + 1) % len(colors)]
            transition_color(strip, start_color, end_color, transition_steps, delay / transition_steps)


def main():

    num_leds = 4
    brightness = 1

    strip = neopixel.NeoPixel(PIXEL_PIN, num_leds, brightness=brightness, auto_write=True)
    color_cycle(strip, num_leds, brightness)


if __name__ == "__main__":
    main()
