#include "led_buffer.h"
#include "../config.h"
#include "../hal/ws2812.h"

/* Static pixel buffer in RAM */
static color_brg_t g_pixels[LED_COUNT];

void led_buffer_init(void)
{
    ws2812_init();
    led_buffer_clear();
}

color_brg_t* led_buffer_get(void)
{
    return g_pixels;
}

void led_buffer_clear(void)
{
    uint8_t i;
    for (i = 0; i < LED_COUNT; i++) {
        g_pixels[i].b = 0;
        g_pixels[i].r = 0;
        g_pixels[i].g = 0;
    }
}

void led_buffer_set_pixel(uint8_t index, color_brg_t color)
{
    if (index < LED_COUNT) {
        g_pixels[index] = color;
    }
}

void led_buffer_show(void)
{
    ws2812_send_buffer(g_pixels, LED_COUNT);
}
