/*
 * PIC18F Christmas Tree LED Controller
 * Main entry point and application loop
 *
 * nko
 */

#include <xc.h>
#include "config.h"
#include "hal/timer.h"
#include "hal/button.h"
#include "core/led_buffer.h"
#include "core/effect_manager.h"

/* PIC18F Configuration Bits */
#pragma config FOSC = INTIO67   /* Internal oscillator, RA6/RA7 as GPIO */
#pragma config PLLCFG = ON      /* PLL enabled (for 64MHz) */
#pragma config PRICLKEN = ON    /* Primary clock enabled */
#pragma config FCMEN = OFF      /* Fail-safe clock monitor disabled */
#pragma config IESO = OFF       /* Internal/external switchover disabled */
#pragma config PWRTEN = ON      /* Power-up timer enabled */
#pragma config BOREN = SBORDIS  /* Brown-out reset enabled, hardware only */
#pragma config BORV = 285       /* Brown-out voltage 2.85V */
#pragma config WDTEN = OFF      /* Watchdog timer disabled */
#pragma config PBADEN = OFF     /* PORTB pins as digital I/O */
#pragma config LVP = OFF        /* Low voltage programming disabled */

void main(void)
{
    uint32_t last_frame = 0;

    /* Configure oscillator for 64MHz */
    OSCCONbits.IRCF = 0b111;    /* 16MHz HFINTOSC */
    OSCTUNEbits.PLLEN = 1;      /* Enable 4x PLL = 64MHz */

    /* Wait for oscillator to stabilize */
    while (!OSCCONbits.HFIOFS);

    /* Initialize hardware */
    timer_init();
    button_init();

    /* Initialize effect system */
    effect_manager_init();

    /* Brief startup flash (all LEDs white for 200ms) */
    {
        uint8_t i;
        color_brg_t* pixels = led_buffer_get();
        for (i = 0; i < LED_COUNT; i++) {
            pixels[i].r = 64;  /* Dim white */
            pixels[i].g = 64;
            pixels[i].b = 64;
        }
        led_buffer_show();
        delay_ms(200);
        led_buffer_clear();
        led_buffer_show();
    }

    /* Main loop */
    while (1) {
        uint32_t now = millis();

        /* Frame rate limiting */
        if (now - last_frame >= FRAME_TIME_MS) {
            last_frame = now;

            /* Update current effect */
            effect_manager_update();

            /* Show updated buffer */
            if (effect_manager_is_running()) {
                led_buffer_show();
            }
        }

        /* Button handling (Phase 9) */
        button_poll();

        if (button_was_short_press()) {
            effect_manager_next();
        }

        if (button_was_long_press()) {
            effect_manager_toggle_power();
        }
    }
}
