/*
 * button.c - Button Handler with IOC (Interrupt-on-Change)
 *
 * True interrupt-based button handling using PORTB IOC
 * ISR fires on pin change, debounce handled via timer
 *
 * nko
 */

#include "button.h"
#include "../config.h"
#include "timer.h"
#include <xc.h>

/* Button state */
static volatile uint8_t g_edge_detected = 0;    /* IOC fired */
static volatile uint32_t g_edge_time = 0;       /* When edge occurred */
static volatile uint8_t g_debounced_state = 0;  /* Stable state after debounce */
static volatile uint32_t g_press_start = 0;     /* When press started */

/* Event flags */
static volatile uint8_t g_short_press_flag = 0;
static volatile uint8_t g_long_press_flag = 0;
static volatile uint8_t g_long_fired = 0;       /* Prevent double-fire */

void button_init(void)
{
    /* Configure RB0 as input */
    BUTTON_TRIS = 1;

    /* Enable weak pull-up on PORTB */
    INTCON2bits.nRBPU = 0;  /* Enable PORTB pull-ups globally */
    BUTTON_WPU = 1;         /* Enable pull-up on RB0 */

    /* Configure IOC on RB0 */
    BUTTON_IOC = 1;         /* Enable IOC on RB0 */

    /* Read PORTB to clear mismatch */
    (void)PORTB;

    /* Enable PORTB IOC interrupt (low priority) */
    INTCONbits.RBIF = 0;    /* Clear flag */
    INTCONbits.RBIE = 1;    /* Enable IOC interrupt */
    INTCON2bits.RBIP = 0;   /* Low priority */
    INTCONbits.GIEL = 1;    /* Enable low-priority interrupts */

    /* Initialize state */
    g_edge_detected = 0;
    g_debounced_state = !BUTTON_PIN;  /* Read initial state */
    g_press_start = 0;
    g_short_press_flag = 0;
    g_long_press_flag = 0;
    g_long_fired = 0;
}

/*
 * IOC Interrupt Handler - called when RB0 changes state
 * Just records the edge, debounce handled elsewhere
 */
void button_ioc_isr(void)
{
    /* Read PORTB to clear mismatch condition */
    (void)PORTB;

    /* Record edge event */
    g_edge_detected = 1;
    g_edge_time = millis_raw();  /* Get raw millis without disabling interrupts */

    /* Clear IOC flag */
    INTCONbits.RBIF = 0;
}

/*
 * Process button state - call from main loop
 * Handles debounce timing and press detection
 */
void button_poll(void)
{
    uint32_t now = millis();
    uint8_t current_state = !BUTTON_PIN;  /* Active low */

    /* Check if we have a pending edge to debounce */
    if (g_edge_detected) {
        if ((now - g_edge_time) >= DEBOUNCE_MS) {
            /* Debounce period passed - check stable state */
            uint8_t old_state = g_debounced_state;
            g_debounced_state = current_state;
            g_edge_detected = 0;

            /* Detect press (rising edge of debounced state) */
            if (g_debounced_state && !old_state) {
                g_press_start = now;
                g_long_fired = 0;
            }

            /* Detect release (falling edge of debounced state) */
            if (!g_debounced_state && old_state) {
                if (!g_long_fired) {
                    g_short_press_flag = 1;
                }
            }
        }
    }

    /* Check for long press while held */
    if (g_debounced_state && !g_long_fired && g_press_start > 0) {
        if ((now - g_press_start) >= LONG_PRESS_MS) {
            g_long_press_flag = 1;
            g_long_fired = 1;
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
    return g_debounced_state;
}
