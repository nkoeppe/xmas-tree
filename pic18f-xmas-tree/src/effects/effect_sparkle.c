/*
 * effect_sparkle.c - Twinkling Sparkle Effect
 *
 * Random white sparkles over a pulsing rainbow gradient background
 * Creates a magical twinkling appearance with smooth color transitions
 *
 * Algorithm:
 * - Each LED has a random chance to become a white sparkle
 * - Non-sparkle LEDs display a gradient background using HSV
 * - Background brightness pulses between min and max values
 * - Gradient slowly shifts over time for visual interest
 *
 * Performance:
 * - Random decision per LED (100 calls to random8 per frame)
 * - HSV to RGB conversion for ~94 LEDs per frame (6% become sparkles)
 * - Target: 30 FPS maintained on PIC18F
 *
 * nko
 */

#include "../core/effect_manager.h"
#include "../core/math_utils.h"
#include "../hal/timer.h"
#include "../types.h"
#include "../config.h"

/* Sparkle configuration */
#define SPARKLE_CHANCE      15      /* Out of 255 (~6% chance per LED per frame) */
#define BRIGHTNESS_MIN      51      /* Minimum brightness (0.2 * 255) */
#define BRIGHTNESS_MAX      255     /* Maximum brightness */
#define PULSE_SPEED         2       /* Brightness change per frame */
#define GRADIENT_SPEED      1       /* Gradient shift per frame */
#define SATURATION          204     /* 80% saturation for vibrant colors */

/*
 * Initialize sparkle effect state
 * Seeds random generator with current time for entropy
 */
static void sparkle_init(effect_context_t* ctx)
{
    ctx->state.sparkle.base_hue = 0;
    ctx->state.sparkle.brightness = BRIGHTNESS_MIN;
    ctx->state.sparkle.pulse_direction = 1;
    ctx->state.sparkle.gradient_shift = 0;

    /* Seed random generator with current millisecond count for entropy */
    random_seed((uint16_t)millis());
}

/*
 * Update sparkle effect
 * Creates gradient background with random white sparkles
 *
 * Performance note: This function calls random8() once per LED (100 calls)
 * and hsv_to_rgb() for ~94 non-sparkle LEDs per frame.
 */
static void sparkle_update(effect_context_t* ctx)
{
    uint8_t i;
    uint8_t brightness = ctx->state.sparkle.brightness;
    uint16_t gradient_shift = ctx->state.sparkle.gradient_shift;
    int16_t new_brightness;
    uint8_t led_count = ctx->led_count;

    /* Guard against division by zero */
    if (led_count == 0) led_count = 1;

    for (i = 0; i < ctx->led_count; i++) {
        /* Check for sparkle (random decision each frame) */
        if (random8() < SPARKLE_CHANCE) {
            /* White sparkle - full brightness on all channels */
            ctx->pixels[i].b = 255;
            ctx->pixels[i].r = 255;
            ctx->pixels[i].g = 255;
        } else {
            /*
             * Gradient background
             * Calculate hue based on:
             * - base_hue: overall color tone (currently fixed at 0)
             * - position: LED index creates gradient spread (~10% of hue wheel)
             * - gradient_shift: slow drift for animation
             *
             * Formula mirrors Python:
             * hue = (base_hue + (i / total) * 0.1 + gradient_shift) % 1.0
             *
             * Our mapping:
             * - Python 0.1 = 10% of hue wheel = 26 on 0-255 scale
             * - Divide position term by led_count for proportional spread
             * - gradient_shift >> 4 to slow down the drift (shift right = divide by 16)
             */
            uint8_t hue = (uint8_t)(ctx->state.sparkle.base_hue +
                                   ((uint16_t)i * 26 / led_count) +
                                   (gradient_shift >> 4));

            uint8_t r, g, b;

            /* Convert HSV to RGB with current pulsing brightness */
            hsv_to_rgb(hue, SATURATION, brightness, &r, &g, &b);

            /* Set pixel (BRG order for WS2812) */
            ctx->pixels[i].b = b;
            ctx->pixels[i].r = r;
            ctx->pixels[i].g = g;
        }
    }

    /*
     * Update brightness for pulsing effect
     * Oscillates between BRIGHTNESS_MIN and BRIGHTNESS_MAX
     * Direction reverses at bounds
     */
    new_brightness = (int16_t)brightness +
                     (PULSE_SPEED * ctx->state.sparkle.pulse_direction);

    if (new_brightness >= BRIGHTNESS_MAX) {
        new_brightness = BRIGHTNESS_MAX;
        ctx->state.sparkle.pulse_direction = -1;
    } else if (new_brightness <= BRIGHTNESS_MIN) {
        new_brightness = BRIGHTNESS_MIN;
        ctx->state.sparkle.pulse_direction = 1;
    }

    ctx->state.sparkle.brightness = (uint8_t)new_brightness;

    /*
     * Slowly shift gradient for visual interest
     * Increment wraps naturally at uint16_t overflow
     * Right-shift by 4 in hue calculation slows the visible drift
     */
    ctx->state.sparkle.gradient_shift += GRADIENT_SPEED;
}

/*
 * Effect definition (const in flash)
 * No cleanup needed - effect maintains no dynamic resources
 */
const effect_def_t effect_sparkle = {
    "Sparkle",          /* name */
    sparkle_init,       /* init function */
    sparkle_update,     /* update function */
    NULL                /* no cleanup needed */
};
