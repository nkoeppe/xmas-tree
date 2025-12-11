/*
 * Debug color scaling
 */

#include <stdio.h>
#include <stdint.h>

int main(void)
{
    uint8_t brightness;
    uint8_t color_b;

    /* Test at 128 (50%) */
    brightness = 128;
    color_b = (uint8_t)((255 * brightness) >> 8);
    printf("At brightness=%d: (255 * %d) >> 8 = %d\n", brightness, brightness, color_b);

    /* Test calculation step by step */
    uint16_t product = 255 * brightness;
    printf("  255 * 128 = %u (0x%04X)\n", product, product);
    printf("  >> 8 = %u\n", product >> 8);

    /* Test at 0 */
    brightness = 0;
    color_b = (uint8_t)((255 * brightness) >> 8);
    printf("\nAt brightness=%d: color_b=%d\n", brightness, color_b);

    /* Test at 255 */
    brightness = 255;
    color_b = (uint8_t)((255 * brightness) >> 8);
    printf("\nAt brightness=%d: color_b=%d\n", brightness, color_b);

    /* Alternative: multiply brightness by color, shift */
    brightness = 128;
    uint8_t base_color = 255;
    color_b = (uint8_t)((base_color * brightness) >> 8);
    printf("\nAlternative at brightness=%d: (%d * %d) >> 8 = %d\n",
           brightness, base_color, brightness, color_b);

    return 0;
}
