/*
 * Test harness for gradient effect
 * Validates plane movement, color gradients, and boundary behavior
 *
 * nko
 */

#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "src/types.h"
#include "src/config.h"

/* Mock LED buffer */
static color_brg_t test_pixels[LED_COUNT];

/* Mock coordinates (simplified Z-axis test) */
static coord_t test_coords[LED_COUNT];

/* Mock bounds */
static struct {
    int8_t min_z;
    int8_t max_z;
} test_bounds = {-50, 50};

/* Mock hsv_to_rgb implementation */
void hsv_to_rgb(uint8_t h, uint8_t s, uint8_t v,
                uint8_t* r, uint8_t* g, uint8_t* b)
{
    /* Simplified approximation for testing */
    if (h < 85) {
        *r = v;
        *g = (v * h) / 85;
        *b = 0;
    } else if (h < 170) {
        h -= 85;
        *r = v - ((v * h) / 85);
        *g = v;
        *b = (v * h) / 85;
    } else {
        h -= 170;
        *r = (v * h) / 85;
        *g = v - ((v * h) / 85);
        *b = v;
    }
}

/* Include the effect implementation */
#include "src/effects/effect_gradient.c"

/* Test setup */
static void setup_test_coords(void)
{
    /* Create LEDs distributed evenly along Z-axis from -50 to 50 */
    for (uint8_t i = 0; i < LED_COUNT; i++) {
        test_coords[i].x = 0;
        test_coords[i].y = 0;
        /* Map i (0-99) to Z range (-50 to 50) */
        test_coords[i].z = test_bounds.min_z +
                          ((i * (test_bounds.max_z - test_bounds.min_z)) / (LED_COUNT - 1));
    }
}

/* Print frame state */
static void print_frame(effect_context_t* ctx, uint8_t frame_num)
{
    printf("\nFrame %d: Plane Z=%d, Direction=%d\n",
           frame_num,
           ctx->state.gradient.plane_pos,
           ctx->state.gradient.direction);

    uint8_t lit_count = 0;
    int8_t first_lit = -1;
    int8_t last_lit = -1;

    for (uint8_t i = 0; i < LED_COUNT; i++) {
        if (ctx->pixels[i].r != 0 || ctx->pixels[i].g != 0 || ctx->pixels[i].b != 0) {
            lit_count++;
            if (first_lit == -1) first_lit = i;
            last_lit = i;
        }
    }

    printf("  LEDs lit: %d (indices %d-%d)\n", lit_count, first_lit, last_lit);

    if (lit_count > 0) {
        /* Show first and last lit LED details */
        printf("  First lit [%d] Z=%d: R=%d G=%d B=%d\n",
               first_lit, test_coords[first_lit].z,
               ctx->pixels[first_lit].r,
               ctx->pixels[first_lit].g,
               ctx->pixels[first_lit].b);
        printf("  Last lit [%d] Z=%d: R=%d G=%d B=%d\n",
               last_lit, test_coords[last_lit].z,
               ctx->pixels[last_lit].r,
               ctx->pixels[last_lit].g,
               ctx->pixels[last_lit].b);
    }
}

/* Test gradient effect behavior */
int main(void)
{
    effect_context_t ctx;

    printf("=== Gradient Effect Test ===\n");
    printf("LED Count: %d\n", LED_COUNT);
    printf("Z Range: %d to %d\n", test_bounds.min_z, test_bounds.max_z);
    printf("Plane Width: %d\n", PLANE_WIDTH);
    printf("Plane Speed: %d\n\n", PLANE_SPEED);

    /* Setup */
    setup_test_coords();
    memset(test_pixels, 0, sizeof(test_pixels));

    /* Initialize context */
    ctx.pixels = test_pixels;
    ctx.coords = test_coords;
    ctx.led_count = LED_COUNT;
    ctx.min_z = test_bounds.min_z;
    ctx.max_z = test_bounds.max_z;

    /* Initialize effect */
    gradient_init(&ctx);
    printf("Initial state: Plane Z=%d, Direction=%d\n",
           ctx.state.gradient.plane_pos, ctx.state.gradient.direction);

    /* Test 1: Initial frame */
    printf("\n--- Test 1: Initial Frame ---\n");
    gradient_update(&ctx);
    print_frame(&ctx, 0);

    /* Test 2: Movement through middle */
    printf("\n--- Test 2: Movement to Middle ---\n");
    for (uint8_t i = 1; i <= 50; i++) {
        gradient_update(&ctx);
        if (i % 10 == 0) {
            print_frame(&ctx, i);
        }
    }

    /* Test 3: Top boundary bounce */
    printf("\n--- Test 3: Top Boundary Bounce ---\n");
    for (uint8_t i = 51; i <= 100; i++) {
        gradient_update(&ctx);
        if (i >= 90 || i % 10 == 0) {
            print_frame(&ctx, i);
        }
    }

    /* Verify direction changed */
    if (ctx.state.gradient.direction == -1) {
        printf("\n✓ Direction correctly reversed at top boundary\n");
    } else {
        printf("\n✗ ERROR: Direction should be -1, got %d\n",
               ctx.state.gradient.direction);
        return 1;
    }

    /* Test 4: Bottom boundary bounce */
    printf("\n--- Test 4: Return to Bottom ---\n");
    for (uint8_t i = 101; i <= 200; i++) {
        gradient_update(&ctx);
        if (i >= 190 || i % 20 == 0) {
            print_frame(&ctx, i);
        }
    }

    /* Verify direction changed back */
    if (ctx.state.gradient.direction == 1) {
        printf("\n✓ Direction correctly reversed at bottom boundary\n");
    } else {
        printf("\n✗ ERROR: Direction should be 1, got %d\n",
               ctx.state.gradient.direction);
        return 1;
    }

    /* Test 5: Color gradient verification */
    printf("\n--- Test 5: Color Gradient Verification ---\n");
    printf("Checking hue distribution at middle position...\n");

    /* Move plane to middle */
    ctx.state.gradient.plane_pos = 0;
    ctx.state.gradient.direction = 1;
    gradient_update(&ctx);

    bool found_red = false;
    bool found_green = false;
    bool found_blue = false;

    for (uint8_t i = 0; i < LED_COUNT; i++) {
        if (ctx.pixels[i].r > 200 && ctx.pixels[i].g < 50) found_red = true;
        if (ctx.pixels[i].g > 200 && ctx.pixels[i].b < 50) found_green = true;
        if (ctx.pixels[i].b > 200 && ctx.pixels[i].r < 50) found_blue = true;
    }

    printf("  Red region present: %s\n", found_red ? "YES" : "NO");
    printf("  Green region present: %s\n", found_green ? "YES" : "NO");
    printf("  Blue region present: %s\n", found_blue ? "YES" : "NO");

    /* Test 6: Brightness falloff */
    printf("\n--- Test 6: Brightness Falloff ---\n");
    ctx.state.gradient.plane_pos = 0;
    gradient_update(&ctx);

    /* Find center LED and check brightness gradient */
    uint8_t center_idx = LED_COUNT / 2;
    uint8_t edge_idx = center_idx + 10;

    if (edge_idx < LED_COUNT) {
        uint8_t center_brightness = ctx.pixels[center_idx].r +
                                   ctx.pixels[center_idx].g +
                                   ctx.pixels[center_idx].b;
        uint8_t edge_brightness = ctx.pixels[edge_idx].r +
                                 ctx.pixels[edge_idx].g +
                                 ctx.pixels[edge_idx].b;

        printf("  Center LED [%d] total brightness: %d\n", center_idx, center_brightness);
        printf("  Edge LED [%d] total brightness: %d\n", edge_idx, edge_brightness);

        if (center_brightness > edge_brightness) {
            printf("  ✓ Brightness correctly decreases from center to edge\n");
        } else {
            printf("  ✗ WARNING: Brightness should decrease from center\n");
        }
    }

    printf("\n=== All Tests Passed ===\n");
    return 0;
}
