#ifndef CONFIG_H
#define CONFIG_H

/* Oscillator frequency (64MHz internal) */
#define _XTAL_FREQ          64000000UL

/* LED Strip Configuration */
#define LED_COUNT           100

/* Compile-time validation */
#if LED_COUNT == 0
    #error "LED_COUNT must be greater than 0"
#endif

#define LED_DATA_PIN        LATCbits.LATC0
#define LED_DATA_TRIS       TRISCbits.TRISC0

/* Button Configuration (active low with pull-up) */
#define BUTTON_PIN          PORTBbits.RB0
#define BUTTON_TRIS         TRISBbits.TRISB0

/* Timing */
#define FRAME_RATE_HZ       30
#define FRAME_TIME_MS       (1000 / FRAME_RATE_HZ)

/* Button timing */
#define DEBOUNCE_MS         50
#define LONG_PRESS_MS       2000

/* Effect configuration */
#define EFFECT_COUNT        5
#define MAX_METEORS         4

/* State union max size (bytes) */
#define STATE_SIZE_MAX      32

#endif /* CONFIG_H */
