#include "ws2812.h"
#include "../config.h"
#include <xc.h>

/*
 * WS2812 Bit-Bang Driver
 * Critical: Interrupts must be disabled during transmission
 *
 * At 64MHz, Fosc/4 = 16MHz instruction clock = 62.5ns per cycle
 * Target timing (adjusted for loop overhead):
 *   T0H: ~400ns = 6-7 cycles (including BSF instruction)
 *   T0L: ~850ns = 13-14 cycles (including BCF, branch)
 *   T1H: ~800ns = 12-13 cycles
 *   T1L: ~450ns = 7-8 cycles
 */

/* NOP macros for timing adjustment */
#define NOP() __asm("NOP")
#define NOP2() NOP(); NOP()
#define NOP4() NOP2(); NOP2()
#define NOP8() NOP4(); NOP4()

void ws2812_init(void)
{
    /* Configure data pin as output, initially low */
    LED_DATA_TRIS = 0;  /* Output */
    LED_DATA_PIN = 0;   /* Low (idle state) */

    /* Send reset pulse to ensure LEDs are ready */
    ws2812_reset();
}

/*
 * Send a single byte, MSB first
 * Inline for performance (avoid call overhead in tight loop)
 */
static inline void ws2812_send_byte(uint8_t byte)
{
    uint8_t bit;

    for (bit = 0x80; bit != 0; bit >>= 1) {
        if (byte & bit) {
            /* Send '1' bit: T1H (~800ns), T1L (~450ns) */
            LED_DATA_PIN = 1;
            NOP8();
            NOP4();
            /* ~12 cycles high = ~750ns */
            LED_DATA_PIN = 0;
            NOP4();
            NOP2();
            /* ~6 cycles low + loop overhead = ~450ns */
        } else {
            /* Send '0' bit: T0H (~400ns), T0L (~850ns) */
            LED_DATA_PIN = 1;
            NOP4();
            NOP2();
            /* ~6 cycles high = ~375ns */
            LED_DATA_PIN = 0;
            NOP8();
            NOP4();
            /* ~12 cycles low + loop overhead = ~850ns */
        }
    }
}

void ws2812_send_buffer(const color_brg_t* buffer, uint8_t count)
{
    uint8_t i;
    uint8_t saved_intcon;

    /* Guard against null buffer */
    if (buffer == NULL || count == 0) {
        return;
    }

    /* Critical section - disable all interrupts */
    saved_intcon = INTCON;
    INTCONbits.GIE = 0;
    INTCONbits.GIEH = 0;
    INTCONbits.GIEL = 0;

    /* Send all pixels in GRB order (WS2812 protocol) */
    for (i = 0; i < count; i++) {
        ws2812_send_byte(buffer[i].g);  /* Green first */
        ws2812_send_byte(buffer[i].r);  /* Red second */
        ws2812_send_byte(buffer[i].b);  /* Blue third */
    }

    /* Restore interrupts */
    INTCON = saved_intcon;

    /* Reset/latch pulse (>50us low) */
    ws2812_reset();
}

void ws2812_reset(void)
{
    LED_DATA_PIN = 0;
    __delay_us(60);  /* 60us > 50us required */
}
