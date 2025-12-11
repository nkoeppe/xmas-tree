/*
 * button.c - Button Handler HAL Implementation
 *
 * Implements debounced button input with short/long press detection
 * Active-low button with internal pull-up, following existing timer.c patterns
 *
 * nko
 */

#include "button.h"
#include "../config.h"
#include "timer.h"
#include <xc.h>

/* Button state */
static uint8_t g_last_raw = 0;          /* Last raw reading */
static uint8_t g_debounced = 0;         /* Current debounced state */
static uint32_t g_debounce_start = 0;   /* Time when raw changed */
static uint32_t g_press_start = 0;      /* Time when press started */

/* Event flags (cleared after read) */
static volatile uint8_t g_short_press_flag = 0;
static volatile uint8_t g_long_press_flag = 0;
static uint8_t g_long_press_fired = 0;  /* Prevent multiple long press events */

void button_init(void)
{
    /* Configure button pin as input */
    BUTTON_TRIS = 1;

    /* Enable internal weak pull-up on PORTB if using RB0 */
    /* Note: May need INTCON2bits.nRBPU = 0 to enable weak pull-ups */
    INTCON2bits.nRBPU = 0;  /* Enable PORTB weak pull-ups */
    WPUBbits.WPUB0 = 1;     /* Enable pull-up on RB0 specifically */

    /* Initialize state */
    g_last_raw = 0;
    g_debounced = 0;
    g_debounce_start = millis();
    g_press_start = 0;
    g_short_press_flag = 0;
    g_long_press_flag = 0;
    g_long_press_fired = 0;
}

void button_poll(void)
{
    /* Read raw button state (active low: 0 when pressed) */
    uint8_t raw = !BUTTON_PIN;  /* Invert: 1 when pressed */
    uint32_t now = millis();

    /* Debounce: require stable state for DEBOUNCE_MS */
    if (raw != g_last_raw) {
        /* State changed, restart debounce timer */
        g_last_raw = raw;
        g_debounce_start = now;
    }

    /* Check if debounce period has elapsed */
    if ((now - g_debounce_start) >= DEBOUNCE_MS) {
        uint8_t old_debounced = g_debounced;
        g_debounced = g_last_raw;

        /* Detect press start (rising edge) */
        if (g_debounced && !old_debounced) {
            g_press_start = now;
            g_long_press_fired = 0;
        }

        /* Detect release (falling edge) */
        if (!g_debounced && old_debounced) {
            /* Only fire short press if long press wasn't already fired */
            if (!g_long_press_fired) {
                g_short_press_flag = 1;
            }
        }
    }

    /* Check for long press while button is still held */
    if (g_debounced && !g_long_press_fired) {
        if ((now - g_press_start) >= LONG_PRESS_MS) {
            g_long_press_flag = 1;
            g_long_press_fired = 1;  /* Prevent short press on release */
        }
    }
}

uint8_t button_was_short_press(void)
{
    if (g_short_press_flag) {
        g_short_press_flag = 0;
        return 1;
    }
    return 0;
}

uint8_t button_was_long_press(void)
{
    if (g_long_press_flag) {
        g_long_press_flag = 0;
        return 1;
    }
    return 0;
}

uint8_t button_is_pressed(void)
{
    return g_debounced;
}
