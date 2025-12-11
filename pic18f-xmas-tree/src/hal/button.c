/*
 * button.c - Button Handler with Interrupt-Based Debouncing
 *
 * Uses timer ISR for debounce timing - button state checked in ISR context
 * Active-low button (pressed = connected to ground)
 *
 * nko
 */

#include "button.h"
#include "../config.h"
#include "timer.h"
#include <xc.h>

/* Debounce state machine */
typedef enum {
    BTN_IDLE,           /* Waiting for press */
    BTN_DEBOUNCING,     /* Waiting for stable state */
    BTN_PRESSED,        /* Button confirmed pressed */
    BTN_WAIT_RELEASE    /* Long press fired, waiting for release */
} button_state_t;

/* Button state - accessed from ISR */
static volatile button_state_t g_state = BTN_IDLE;
static volatile uint8_t g_debounce_count = 0;
static volatile uint16_t g_press_count = 0;

/* Event flags */
static volatile uint8_t g_short_press_flag = 0;
static volatile uint8_t g_long_press_flag = 0;

/* Debounce counts (called every 1ms from timer ISR) */
#define DEBOUNCE_COUNT      (DEBOUNCE_MS)
#define LONG_PRESS_COUNT    (LONG_PRESS_MS)

void button_init(void)
{
    /* Configure button pin as input */
    BUTTON_TRIS = 1;

    /* Note: RC0 doesn't have internal pull-up on most PIC18F
     * External pull-up resistor required (10K to VCC) */

    /* Initialize state */
    g_state = BTN_IDLE;
    g_debounce_count = 0;
    g_press_count = 0;
    g_short_press_flag = 0;
    g_long_press_flag = 0;
}

/*
 * Button ISR handler - call this from timer ISR every 1ms
 * Handles all debouncing and press detection in interrupt context
 */
void button_isr_handler(void)
{
    uint8_t btn_pressed = !BUTTON_PIN;  /* Active low: 0 = pressed */

    switch (g_state) {
        case BTN_IDLE:
            if (btn_pressed) {
                /* Button went low, start debounce */
                g_state = BTN_DEBOUNCING;
                g_debounce_count = 0;
            }
            break;

        case BTN_DEBOUNCING:
            g_debounce_count++;
            if (g_debounce_count >= DEBOUNCE_COUNT) {
                if (btn_pressed) {
                    /* Still pressed after debounce - confirmed press */
                    g_state = BTN_PRESSED;
                    g_press_count = 0;
                } else {
                    /* Released during debounce - was noise */
                    g_state = BTN_IDLE;
                }
            }
            break;

        case BTN_PRESSED:
            if (!btn_pressed) {
                /* Released - short press */
                g_short_press_flag = 1;
                g_state = BTN_IDLE;
            } else {
                /* Still pressed - count for long press */
                g_press_count++;
                if (g_press_count >= LONG_PRESS_COUNT) {
                    /* Long press detected */
                    g_long_press_flag = 1;
                    g_state = BTN_WAIT_RELEASE;
                }
            }
            break;

        case BTN_WAIT_RELEASE:
            if (!btn_pressed) {
                /* Released after long press - back to idle */
                g_state = BTN_IDLE;
            }
            break;
    }
}

/*
 * Poll function - now just a stub for compatibility
 * Actual work is done in button_isr_handler() called from timer ISR
 */
void button_poll(void)
{
    /* Nothing to do - handled in ISR */
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
    return (g_state == BTN_PRESSED || g_state == BTN_WAIT_RELEASE);
}
