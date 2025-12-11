/*
 * button.h - Button Handler HAL
 *
 * Provides debounced button input with short/long press detection
 * Handles active-low button with internal pull-up resistor
 *
 * nko
 */

#ifndef BUTTON_H
#define BUTTON_H

#include <stdint.h>

/*
 * Button Handler
 * Provides debounced button input with short/long press detection
 *
 * Usage:
 *   1. Call button_init() once at startup
 *   2. Call button_poll() in main loop (or periodically)
 *   3. Check button_was_short_press() and button_was_long_press() for events
 */

/* Initialize button pin with pull-up */
void button_init(void);

/*
 * Poll button state (call frequently, e.g., every frame or every ms)
 * Handles debouncing and press duration tracking
 */
void button_poll(void);

/* Returns 1 once if short press detected (clears flag) */
uint8_t button_was_short_press(void);

/* Returns 1 once if long press detected (clears flag) */
uint8_t button_was_long_press(void);

/* Get current debounced button state (1 = pressed, 0 = released) */
uint8_t button_is_pressed(void);

#endif /* BUTTON_H */
