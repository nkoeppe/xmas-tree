/*
 * effect_gradient.c - Color Gradient Sweep Effect
 *
 * Creates a moving horizontal plane that illuminates LEDs based on Z-position proximity
 * Hue varies along the Z-axis creating a rainbow gradient
 * Brightness falls off based on distance from plane center
 *
 * Algorithm:
 * - Plane sweeps along Z-axis (bottom to top, then top to bottom)
 * - LEDs within plane width are illuminated
 * - Hue based on LED's Z position (rainbow along tree height)
 * - Brightness based on distance from plane center
 * - Direction reversal at bounds
 *
 * nko
 */

#include "../core/effect_manager.h"
#include "../core/math_utils.h"
#include "../types.h"
#include "../config.h"
#include <stddef.h>  /* For NULL */

/* Gradient configuration */
#define PLANE_SPEED         1       /* Movement per frame */
#define PLANE_WIDTH         30      /* Width of the illuminated band */

/*
 * Initialize gradient effect state
 * Starts plane at bottom of tree moving upward
 */
static void gradient_init(effect_context_t* ctx)
{
    ctx->state.gradient.plane_pos = ctx->min_z;
    ctx->state.gradient.direction = 1;  /* Start moving up */
}

/*
 * Update gradient effect (called once per frame)
 * Creates a moving horizontal plane with hue-based coloring
 *
 * Color mapping:
 * - Hue varies with Z position: min_z = red, max_z = violet (full rainbow)
 * - Brightness varies with distance from plane center
 * - LEDs outside plane width are turned off
 */
static void gradient_update(effect_context_t* ctx)
{
    uint8_t i;
    int8_t plane_z = ctx->state.gradient.plane_pos;
    int8_t half_width = PLANE_WIDTH >> 1;

    /* Calculate Z range for this frame */
    int8_t plane_min = plane_z - half_width;
    int8_t plane_max = plane_z + half_width;

    for (i = 0; i < ctx->led_count; i++) {
        int8_t led_z = ctx->coords[i].z;

        /* Check if LED is within the plane band */
        if (led_z >= plane_min && led_z <= plane_max) {
            /* LED is in the plane - calculate hue based on global Z position */
            /* Map Z position to hue: min_z → hue 0 (red), max_z → hue 255 (violet) */
            uint8_t z_range = (uint8_t)(ctx->max_z - ctx->min_z);
            uint8_t hue;
            uint8_t brightness;
            int8_t dist;
            uint8_t r, g, b;

            /* Avoid division by zero if all LEDs have same Z */
            if (z_range == 0) {
                hue = 0;
            } else {
                hue = (uint8_t)(((led_z - ctx->min_z) * 255) / z_range);
            }

            /* Calculate brightness based on distance from plane center */
            dist = led_z - plane_z;
            if (dist < 0) dist = -dist;  /* abs() */

            /* Brightness falls off from center: 255 at center, 0 at edge */
            /* Avoid division by zero */
            if (half_width == 0) {
                brightness = 255;
            } else {
                brightness = 255 - ((uint8_t)dist * 255) / (uint8_t)half_width;
            }

            /* Convert HSV to RGB */
            hsv_to_rgb(hue, 255, brightness, &r, &g, &b);

            /* Set pixel (BRG order for WS2812) */
            ctx->pixels[i].b = b;
            ctx->pixels[i].r = r;
            ctx->pixels[i].g = g;
        } else {
            /* LED outside plane - turn off */
            ctx->pixels[i].b = 0;
            ctx->pixels[i].r = 0;
            ctx->pixels[i].g = 0;
        }
    }

    /* Move plane - check bounds BEFORE modifying to avoid overflow */
    {
        int8_t new_pos = plane_z;
        if (ctx->state.gradient.direction > 0) {
            if (plane_z < ctx->max_z - half_width) {
                new_pos = plane_z + PLANE_SPEED;
            } else {
                new_pos = ctx->max_z - half_width;
                ctx->state.gradient.direction = -1;
            }
        } else {
            if (plane_z > ctx->min_z + half_width) {
                new_pos = plane_z - PLANE_SPEED;
            } else {
                new_pos = ctx->min_z + half_width;
                ctx->state.gradient.direction = 1;
            }
        }
        ctx->state.gradient.plane_pos = new_pos;
    }
}

/*
 * Effect definition (const in flash)
 * No cleanup needed - effect maintains no dynamic resources
 */
const effect_def_t effect_gradient = {
    "Gradient",         /* name */
    gradient_init,      /* init function */
    gradient_update,    /* update function */
    NULL                /* no cleanup needed */
};
