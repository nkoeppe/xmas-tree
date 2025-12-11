/*
 * Wave 3D Effect
 * Creates flowing sinusoidal color waves using 3D coordinates
 * Each axis contributes independently to the wave pattern
 *
 * Based on the Python reference implementation:
 * - Multiple wave components (x, y, z) with different frequencies
 * - Combined wave value drives color oscillations
 * - Three color channels with different phase offsets
 *
 * nko
 */

#include "../core/effect_manager.h"
#include "../core/math_utils.h"
#include "../types.h"
#include "../config.h"

/* Wave configuration */
#define WAVE_SPEED          2       /* Time increment per frame */

/*
 * Initialize wave effect state
 */
static void wave_init(effect_context_t* ctx)
{
    ctx->state.wave.time = 0;
}

/*
 * Update wave effect
 * Creates multi-axis sine wave color pattern
 *
 * Algorithm:
 * 1. For each LED, calculate wave contribution from x, y, z coordinates
 * 2. Combine wave components into single wave value
 * 3. Use combined wave to drive RGB color oscillations with phase offsets
 * 4. Advance time for animation
 */
static void wave_update(effect_context_t* ctx)
{
    uint8_t i;
    uint16_t time = ctx->state.wave.time;
    uint8_t time_byte = (uint8_t)(time & 0xFF);

    for (i = 0; i < ctx->led_count; i++) {
        const coord_t* coord = &ctx->coords[i];
        int16_t wave_sum;
        int8_t combined_wave;
        int16_t color_val;
        uint8_t r, g, b;
        uint8_t angle;
        int8_t wave_component;

        /*
         * Calculate wave contribution from each axis
         * Python reference: sin(coord.x * 2.0 + time)
         *
         * Our approach:
         * - coord values are int8_t (-128 to 127)
         * - Multiply by scaling factor (simulating Python's 2.0, 3.0, 1.5)
         * - Add time offset
         * - sin_lookup expects 0-255 (representing 0-360°)
         * - Returns -128 to 127 (Q7 fixed point)
         */

        /* wave_x = sin(coord.x * 2 + time) */
        angle = (uint8_t)((coord->x << 1) + time_byte);
        wave_component = sin_lookup(angle);
        wave_sum = wave_component;

        /* wave_y = sin(coord.y * 3 + time) */
        angle = (uint8_t)((int16_t)coord->y * 3 + time_byte);
        wave_component = sin_lookup(angle);
        wave_sum += wave_component;

        /* wave_z = sin(coord.z * 1.5 + time) */
        /* Approximate 1.5x as: z + (z >> 1) */
        angle = (uint8_t)(coord->z + (coord->z >> 1) + time_byte);
        wave_component = sin_lookup(angle);
        wave_sum += wave_component;

        /*
         * Combine waves: average of three components
         * wave_sum range: -384 to 381 (three components, each -128 to 127)
         * Divide by 3 to get -128 to 127 range
         */
        combined_wave = (int8_t)(wave_sum / 3);

        /*
         * Convert combined wave to RGB colors
         * Python reference: r = 0.5 + 0.5 * sin(wave + time)
         * This maps sin output (-1 to 1) to (0 to 1)
         *
         * Our approach:
         * - sin_lookup returns -128 to 127
         * - Map to 0-255: (128 + sin_value) gives 0-255
         * - Need to scale sin_value by 0.5, so divide by 2
         * - Result: 128 + (sin_lookup() / 2)
         */

        /* Red channel: sin(combined_wave + time) */
        angle = (uint8_t)(combined_wave + time_byte);
        color_val = 128 + (sin_lookup(angle) >> 1);
        r = (uint8_t)color_val;

        /*
         * Green channel: sin(combined_wave * 1.3 + time + phase_offset)
         * Phase offset of ~85 (1/3 of 256) for color variety
         * 1.3x approximation: (wave * 83) >> 6  (83/64 = 1.296875)
         */
        angle = (uint8_t)(((int16_t)combined_wave * 83 >> 6) + time_byte + 85);
        color_val = 128 + (sin_lookup(angle) >> 1);
        g = (uint8_t)color_val;

        /*
         * Blue channel: sin(combined_wave * 0.8 + time + phase_offset)
         * Phase offset of ~170 (2/3 of 256)
         * 0.8x approximation: (wave * 51) >> 6  (51/64 = 0.796875)
         */
        angle = (uint8_t)(((int16_t)combined_wave * 51 >> 6) + time_byte + 170);
        color_val = 128 + (sin_lookup(angle) >> 1);
        b = (uint8_t)color_val;

        /* Set pixel (BRG order for WS2812) */
        ctx->pixels[i].b = b;
        ctx->pixels[i].r = r;
        ctx->pixels[i].g = g;
    }

    /* Advance time (simulates Python's time += 0.1) */
    ctx->state.wave.time += WAVE_SPEED;
}

/*
 * Effect definition (stored in flash)
 */
const effect_def_t effect_wave = {
    "Wave 3D",          /* name */
    wave_init,          /* init function */
    wave_update,        /* update function */
    NULL                /* no cleanup needed */
};
