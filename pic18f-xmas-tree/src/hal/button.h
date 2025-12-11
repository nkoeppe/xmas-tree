/*
 * button.h - Button Handler with IOC (Interrupt-on-Change)
 *
 * True interrupt-based button handling using PORTB IOC
 * ISR fires on pin change, debounce handled in main loop
 *
 * nko
 */

#ifndef BUTTON_H
#define BUTTON_H

#include <stdint.h>

/*
 * Button Handler
 *
 * Usage:
 *   1. Call button_init() once at startup
 *   2. Call button_poll() in main loop
 *   3. Check button_was_short_press() and button_was_long_press() for events
 *
 * IOC fires on RB0 change, sets flag with timestamp.
 * button_poll() handles debounce timing and press detection.
 */

/* Initialize button pin with pull-up and IOC */
void button_init(void);

/* IOC ISR handler - called from low-priority ISR when RBIF set */
void button_ioc_isr(void);

/* Process button state - call from main loop */
void button_poll(void);

/* Returns 1 once if short press detected (clears flag) */
uint8_t button_was_short_press(void);

/* Returns 1 once if long press detected (clears flag) */
uint8_t button_was_long_press(void);

/* Get current debounced button state (1 = pressed, 0 = released) */
uint8_t button_is_pressed(void);

#endif /* BUTTON_H */
