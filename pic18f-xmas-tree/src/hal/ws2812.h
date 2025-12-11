#ifndef WS2812_H
#define WS2812_H

#include "../types.h"

/*
 * WS2812 LED Driver
 * Bit-bang implementation for precise timing
 *
 * Timing (at 64MHz = 62.5ns per instruction):
 *   T0H: 400ns (6-7 cycles)
 *   T0L: 850ns (13-14 cycles)
 *   T1H: 800ns (12-13 cycles)
 *   T1L: 450ns (7-8 cycles)
 *   Reset: >50us low
 */

/* Initialize WS2812 data pin */
void ws2812_init(void);

/* Send entire pixel buffer to LED strip */
void ws2812_send_buffer(const color_brg_t* buffer, uint8_t count);

/* Send reset pulse (>50us) */
void ws2812_reset(void);

#endif /* WS2812_H */
