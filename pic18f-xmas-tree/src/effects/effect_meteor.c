/*
 * Meteor Shower Effect
 * Falling particles with distance-based brightness trails
 * Uses 3D coordinates for realistic meteor positioning
 *
 * Algorithm:
 * - Up to 4 meteors fall simultaneously along Z axis
 * - Each LED's brightness is based on distance to nearest meteor
 * - Trail length defines glow radius around meteor center
 * - Random spawning at top of tree
 *
 * nko
 */

#include "../core/effect_manager.h"
#include "../core/math_utils.h"
#include "../types.h"
#include "../config.h"

/* Meteor configuration */
#define METEOR_SPEED        2       /* Z-axis movement per frame */
#define METEOR_TRAIL        30      /* Trail length (distance units) */
#define METEOR_SPAWN_CHANCE 25      /* Out of 255 (~10% per frame) */
#define METEOR_COLOR_B      180     /* Blue-white color */
#define METEOR_COLOR_R      220
#define METEOR_COLOR_G      255

/*
 * Initialize meteor effect state
 */
static void meteor_init(effect_context_t* ctx)
{
    uint8_t i;

    /* Clear all meteor slots */
    for (i = 0; i < MAX_METEORS; i++) {
        ctx->state.meteor.meteor_x[i] = 0;
        ctx->state.meteor.meteor_y[i] = 0;
        ctx->state.meteor.meteor_z[i] = ctx->min_z - 10;  /* Off-screen */
    }
    ctx->state.meteor.meteor_count = 0;

    /* Seed random for meteor spawning */
    random_seed(12345);
}

/*
 * Spawn a new meteor at random XY, top Z
 */
static void spawn_meteor(effect_context_t* ctx, uint8_t slot)
{
    /* Random X position within bounds */
    uint8_t range_x = ctx->max_x - ctx->min_x;
    if (range_x == 0) range_x = 1;  /* Guard against div/mod by zero */
    ctx->state.meteor.meteor_x[slot] = ctx->min_x + (random8() % range_x);

    /* Random Y position within bounds */
    uint8_t range_y = ctx->max_y - ctx->min_y;
    if (range_y == 0) range_y = 1;  /* Guard against div/mod by zero */
    ctx->state.meteor.meteor_y[slot] = ctx->min_y + (random8() % range_y);

    /* Start at top */
    ctx->state.meteor.meteor_z[slot] = ctx->max_z;
}

/*
 * Check if meteor is active (within visible Z range)
 */
static uint8_t meteor_is_active(effect_context_t* ctx, uint8_t slot)
{
    return ctx->state.meteor.meteor_z[slot] >= ctx->min_z;
}

/*
 * Update meteor effect
 * Moves meteors down Z axis, spawns new ones randomly,
 * calculates LED brightness based on distance to nearest meteor
 */
static void meteor_update(effect_context_t* ctx)
{
    uint8_t i, m;
    uint8_t active_count = 0;

    /* Move all meteors down (decrease Z) */
    for (m = 0; m < MAX_METEORS; m++) {
        if (meteor_is_active(ctx, m)) {
            int8_t current_z = ctx->state.meteor.meteor_z[m];
            /* Guard against signed overflow */
            if (current_z > ctx->min_z + METEOR_SPEED) {
                ctx->state.meteor.meteor_z[m] = current_z - METEOR_SPEED;
            } else {
                ctx->state.meteor.meteor_z[m] = ctx->min_z - 10;  /* Deactivate */
            }
            if (meteor_is_active(ctx, m)) {
                active_count++;
            }
        }
    }

    /* Try to spawn new meteor if we have room */
    if (active_count < MAX_METEORS && random8() < METEOR_SPAWN_CHANCE) {
        /* Find empty slot */
        for (m = 0; m < MAX_METEORS; m++) {
            if (!meteor_is_active(ctx, m)) {
                spawn_meteor(ctx, m);
                active_count++;
                break;
            }
        }
    }

    /* Clear all pixels */
    for (i = 0; i < ctx->led_count; i++) {
        ctx->pixels[i].b = 0;
        ctx->pixels[i].r = 0;
        ctx->pixels[i].g = 0;
    }

    /* For each LED, check distance to all active meteors */
    for (i = 0; i < ctx->led_count; i++) {
        const coord_t* led = &ctx->coords[i];
        uint8_t best_brightness = 0;

        for (m = 0; m < MAX_METEORS; m++) {
            if (meteor_is_active(ctx, m)) {
                /* Calculate distance from LED to meteor */
                int8_t dx = led->x - ctx->state.meteor.meteor_x[m];
                int8_t dy = led->y - ctx->state.meteor.meteor_y[m];
                int8_t dz = led->z - ctx->state.meteor.meteor_z[m];

                uint8_t dist = fast_distance_3d(dx, dy, dz);

                /* Calculate brightness based on distance (closer = brighter) */
                if (dist < METEOR_TRAIL) {
                    /* Brightness = 255 * (1 - dist/trail) */
                    uint8_t brightness = 255 - ((uint16_t)dist * 255 / METEOR_TRAIL);

                    if (brightness > best_brightness) {
                        best_brightness = brightness;
                    }
                }
            }
        }

        /* Apply brightest meteor to this LED */
        if (best_brightness > 0) {
            ctx->pixels[i].b = (uint8_t)(((uint16_t)METEOR_COLOR_B * best_brightness) >> 8);
            ctx->pixels[i].r = (uint8_t)(((uint16_t)METEOR_COLOR_R * best_brightness) >> 8);
            ctx->pixels[i].g = (uint8_t)(((uint16_t)METEOR_COLOR_G * best_brightness) >> 8);
        }
    }

    ctx->state.meteor.meteor_count = active_count;
}

/*
 * Effect definition (stored in flash)
 * No cleanup needed - effect maintains no dynamic resources
 */
const effect_def_t effect_meteor = {
    "Meteor",           /* name */
    meteor_init,        /* init function */
    meteor_update,      /* update function */
    NULL                /* no cleanup needed */
};
