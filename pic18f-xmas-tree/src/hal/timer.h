#ifndef TIMER_H
#define TIMER_H

#include <stdint.h>

/*
 * Timer HAL - Provides millisecond timing services
 * Uses Timer0 with high-priority interrupt for 1ms tick
 */

/* Initialize Timer0 for 1ms interrupt */
void timer_init(void);

/* Get current millisecond count (wraps at ~49 days) */
uint32_t millis(void);

/* Get raw millis - for use in ISR context (no interrupt disable) */
uint32_t millis_raw(void);

/* Blocking delay (use sparingly - prefer non-blocking patterns) */
void delay_ms(uint16_t ms);

#endif /* TIMER_H */
