#ifndef LED_BUFFER_H
#define LED_BUFFER_H

#include "../types.h"

/*
 * LED Pixel Buffer
 * Manages the frame buffer for LED colors
 */

/* Initialize buffer (clear to black) */
void led_buffer_init(void);

/* Get pointer to pixel buffer for direct access */
color_brg_t* led_buffer_get(void);

/* Clear all pixels to black */
void led_buffer_clear(void);

/* Set a single pixel */
void led_buffer_set_pixel(uint8_t index, color_brg_t color);

/* Show buffer (send to LED strip) */
void led_buffer_show(void);

#endif /* LED_BUFFER_H */
