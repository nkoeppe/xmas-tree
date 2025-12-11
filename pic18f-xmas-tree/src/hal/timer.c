#include "timer.h"
#include "../config.h"
#include <xc.h>

/* Volatile millisecond counter - incremented by ISR */
static volatile uint32_t g_millis = 0;

/*
 * Timer0 reload value calculation for 1ms interrupt
 * At 64MHz with 4:1 prescaler: Fosc/4 = 16MHz
 * Timer counts: 16000000 / 1000 = 16000 counts per ms
 * Using 16-bit mode: reload = 65536 - 16000 = 49536
 */
#define TIMER0_RELOAD_H  ((49536 >> 8) & 0xFF)
#define TIMER0_RELOAD_L  (49536 & 0xFF)

void timer_init(void)
{
    /* Configure Timer0:
     * - 16-bit mode
     * - Internal clock (Fosc/4)
     * - 1:4 prescaler
     * - Enable interrupt
     */
    T0CON = 0x00;        /* Stop timer, clear config */
    T0CONbits.T08BIT = 0; /* 16-bit mode */
    T0CONbits.T0CS = 0;   /* Internal clock (Fosc/4) */
    T0CONbits.PSA = 0;    /* Prescaler assigned */
    T0CONbits.T0PS = 0b001; /* 1:4 prescaler */

    /* Load initial count */
    TMR0H = TIMER0_RELOAD_H;
    TMR0L = TIMER0_RELOAD_L;

    /* Enable Timer0 interrupt */
    INTCONbits.TMR0IF = 0;  /* Clear interrupt flag */
    INTCONbits.TMR0IE = 1;  /* Enable interrupt */

    /* Enable high-priority interrupts */
    RCONbits.IPEN = 1;      /* Enable priority levels */
    INTCON2bits.TMR0IP = 1; /* Timer0 high priority */
    INTCONbits.GIEH = 1;    /* Enable high-priority interrupts */

    /* Start timer */
    T0CONbits.TMR0ON = 1;
}

uint32_t millis(void)
{
    uint32_t m;

    /* Disable interrupts briefly to read 32-bit value atomically */
    INTCONbits.GIEH = 0;
    m = g_millis;
    INTCONbits.GIEH = 1;

    return m;
}

void delay_ms(uint16_t ms)
{
    uint32_t start = millis();
    while ((millis() - start) < ms) {
        /* Busy wait - use sparingly */
    }
}

/*
 * High-priority interrupt service routine
 * Called every 1ms by Timer0 overflow
 */
void __interrupt(high_priority) timer0_isr(void)
{
    if (INTCONbits.TMR0IF) {
        INTCONbits.TMR0IF = 0;  /* Clear flag */

        /* Reload timer for next 1ms */
        TMR0H = TIMER0_RELOAD_H;
        TMR0L = TIMER0_RELOAD_L;

        g_millis++;
    }
}
