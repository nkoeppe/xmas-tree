/*
 * effect_breathing.c - Breathing Sphere Effect
 *
 * Simple brightness oscillation across all LEDs
 * Perfect for validating the effect system works
 *
 * Algorithm:
 * - Oscillates brightness from 0 to 255 and back
 * - Applies uniform color to all LEDs scaled by current brightness
 * - Direction reversal at bounds
 *
 * nko
 */

#include "../core/effect_manager.h"
#include "../types.h"
#include "../config.h"

/* Breathing configuration */
#define BREATHING_SPEED     3       /* Brightness increment per frame (0-255 scale) */
#define BREATHING_COLOR_B   255     /* Blue component */
#define BREATHING_COLOR_R   0       /* Red component (use 128 for purple-ish) */
#define BREATHING_COLOR_G   0       /* Green component */

/*
 * Initialize breathing effect state
 * Sets initial brightness to 0 with upward direction
 */
static void breathing_init(effect_context_t* ctx)
{
    ctx->state.breathing.brightness = 0;
    ctx->state.breathing.direction = 1;
}

/*
 * Update breathing effect (called once per frame)
 * Smoothly oscillates brightness from 0 to 255 and back
 */
static void breathing_update(effect_context_t* ctx)
{
    uint8_t i;
    int16_t new_brightness;
    color_brg_t color;

    /* Update brightness with direction */
    new_brightness = (int16_t)ctx->state.breathing.brightness +
                     (BREATHING_SPEED * ctx->state.breathing.direction);

    /* Reverse direction at bounds */
    if (new_brightness >= 255) {
        new_brightness = 255;
        ctx->state.breathing.direction = -1;
    } else if (new_brightness <= 0) {
        new_brightness = 0;
        ctx->state.breathing.direction = 1;
    }

    ctx->state.breathing.brightness = (uint8_t)new_brightness;

    /* Calculate color at current brightness */
    /* Scale each component by brightness/255 using right shift for efficiency */
    color.b = (uint8_t)((BREATHING_COLOR_B * new_brightness) >> 8);
    color.r = (uint8_t)((BREATHING_COLOR_R * new_brightness) >> 8);
    color.g = (uint8_t)((BREATHING_COLOR_G * new_brightness) >> 8);

    /* Apply to all LEDs uniformly */
    for (i = 0; i < ctx->led_count; i++) {
        ctx->pixels[i] = color;
    }
}

/*
 * Effect definition (const in flash)
 * No cleanup needed - effect maintains no dynamic resources
 */
const effect_def_t effect_breathing = {
    "Breathing",        /* name */
    breathing_init,     /* init function */
    breathing_update,   /* update function */
    NULL                /* no cleanup needed */
};
