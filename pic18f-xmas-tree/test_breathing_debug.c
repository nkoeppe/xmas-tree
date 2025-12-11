/*
 * Debug breathing reversal logic
 */

#include <stdio.h>
#include <stdint.h>

int main(void)
{
    uint8_t brightness = 252;
    int8_t direction = 1;
    int16_t new_brightness;

    printf("Initial: brightness=%d, direction=%d\n", brightness, direction);

    /* Frame 1 */
    new_brightness = (int16_t)brightness + (3 * direction);
    printf("Frame 1: new_brightness=%d (252 + 3*1 = 255)\n", new_brightness);

    if (new_brightness >= 255) {
        new_brightness = 255;
        direction = -1;
        printf("  Hit max! Set new_brightness=255, direction=-1\n");
    }

    brightness = (uint8_t)new_brightness;
    printf("  Result: brightness=%d, direction=%d\n\n", brightness, direction);

    /* Frame 2 */
    new_brightness = (int16_t)brightness + (3 * direction);
    printf("Frame 2: new_brightness=%d (255 + 3*(-1) = 252)\n", new_brightness);

    if (new_brightness >= 255) {
        new_brightness = 255;
        direction = -1;
        printf("  Hit max! Set new_brightness=255, direction=-1\n");
    } else if (new_brightness <= 0) {
        new_brightness = 0;
        direction = 1;
        printf("  Hit min! Set new_brightness=0, direction=1\n");
    }

    brightness = (uint8_t)new_brightness;
    printf("  Result: brightness=%d, direction=%d\n", brightness, direction);

    return 0;
}
