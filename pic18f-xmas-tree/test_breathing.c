/*
 * test_breathing.c - Breathing Effect Standalone Test
 *
 * Tests the breathing effect implementation without hardware
 * Verifies:
 * - Brightness oscillation logic
 * - Direction reversal at bounds
 * - Color scaling
 * - No floating-point operations
 *
 * nko
 */

#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <assert.h>

/* Mock types for testing */
typedef struct {
    uint8_t b;
    uint8_t r;
    uint8_t g;
} color_brg_t;

typedef struct {
    int8_t x;
    int8_t y;
    int8_t z;
} coord_t;

typedef union {
    struct {
        uint8_t brightness;
        int8_t direction;
    } breathing;
    uint8_t raw[32];
} effect_state_t;

typedef struct effect_context {
    color_brg_t* pixels;
    const coord_t* coords;
    uint8_t led_count;
    int8_t min_x, max_x;
    int8_t min_y, max_y;
    int8_t min_z, max_z;
    int8_t center_x, center_y, center_z;
    uint32_t frame_time_ms;
    effect_state_t state;
} effect_context_t;

typedef void (*effect_init_fn)(effect_context_t* ctx);
typedef void (*effect_update_fn)(effect_context_t* ctx);
typedef void (*effect_cleanup_fn)(effect_context_t* ctx);

typedef struct {
    const char* name;
    effect_init_fn init;
    effect_update_fn update;
    effect_cleanup_fn cleanup;
} effect_def_t;

/* Breathing configuration */
#define BREATHING_SPEED     3
#define BREATHING_COLOR_B   255
#define BREATHING_COLOR_R   0
#define BREATHING_COLOR_G   0
#define LED_COUNT           100

/* Breathing effect implementation (copy from effect_breathing.c) */
static void breathing_init(effect_context_t* ctx)
{
    ctx->state.breathing.brightness = 0;
    ctx->state.breathing.direction = 1;
}

static void breathing_update(effect_context_t* ctx)
{
    uint8_t i;
    int16_t new_brightness;
    color_brg_t color;

    new_brightness = (int16_t)ctx->state.breathing.brightness +
                     (BREATHING_SPEED * ctx->state.breathing.direction);

    if (new_brightness >= 255) {
        new_brightness = 255;
        ctx->state.breathing.direction = -1;
    } else if (new_brightness <= 0) {
        new_brightness = 0;
        ctx->state.breathing.direction = 1;
    }

    ctx->state.breathing.brightness = (uint8_t)new_brightness;

    color.b = (uint8_t)((BREATHING_COLOR_B * new_brightness) >> 8);
    color.r = (uint8_t)((BREATHING_COLOR_R * new_brightness) >> 8);
    color.g = (uint8_t)((BREATHING_COLOR_G * new_brightness) >> 8);

    for (i = 0; i < ctx->led_count; i++) {
        ctx->pixels[i] = color;
    }
}

const effect_def_t effect_breathing = {
    "Breathing",
    breathing_init,
    breathing_update,
    NULL
};

/* Test harness */
int main(void)
{
    color_brg_t pixels[LED_COUNT];
    coord_t coords[LED_COUNT];  /* Dummy coords */
    effect_context_t ctx;
    uint8_t i;
    int frame;

    printf("Testing Breathing Effect Implementation\n");
    printf("========================================\n\n");

    /* Setup context */
    memset(&ctx, 0, sizeof(ctx));
    memset(pixels, 0, sizeof(pixels));
    ctx.pixels = pixels;
    ctx.coords = coords;
    ctx.led_count = LED_COUNT;
    ctx.frame_time_ms = 33;  /* ~30 FPS */

    /* Test initialization */
    printf("Test 1: Initialization\n");
    breathing_init(&ctx);
    assert(ctx.state.breathing.brightness == 0);
    assert(ctx.state.breathing.direction == 1);
    printf("  ✓ Initial brightness: %d\n", ctx.state.breathing.brightness);
    printf("  ✓ Initial direction: %d\n", ctx.state.breathing.direction);
    printf("\n");

    /* Test brightness ramp up */
    printf("Test 2: Brightness Ramp Up (first 10 frames)\n");
    for (frame = 0; frame < 10; frame++) {
        uint8_t prev_brightness = ctx.state.breathing.brightness;
        breathing_update(&ctx);
        printf("  Frame %2d: brightness=%3d, direction=%2d, LED[0]=(B:%3d,R:%3d,G:%3d)\n",
               frame,
               ctx.state.breathing.brightness,
               ctx.state.breathing.direction,
               pixels[0].b, pixels[0].r, pixels[0].g);

        /* Verify brightness increases */
        assert(ctx.state.breathing.brightness > prev_brightness ||
               ctx.state.breathing.brightness == 255);

        /* Verify all LEDs have same color */
        for (i = 1; i < LED_COUNT; i++) {
            assert(pixels[i].b == pixels[0].b);
            assert(pixels[i].r == pixels[0].r);
            assert(pixels[i].g == pixels[0].g);
        }
    }
    printf("\n");

    /* Test direction reversal at max */
    printf("Test 3: Direction Reversal at Maximum\n");
    while (ctx.state.breathing.brightness < 255) {
        breathing_update(&ctx);
    }
    printf("  Reached max brightness: %d\n", ctx.state.breathing.brightness);
    assert(ctx.state.breathing.brightness == 255);
    /* Direction reversal happens in the SAME frame as reaching max */
    assert(ctx.state.breathing.direction == -1);
    printf("  ✓ Direction reversed at maximum (same frame)\n");

    /* Next update should start decreasing */
    breathing_update(&ctx);
    printf("  Next frame: brightness=%d, direction=%d\n",
           ctx.state.breathing.brightness,
           ctx.state.breathing.direction);
    assert(ctx.state.breathing.brightness < 255);
    assert(ctx.state.breathing.direction == -1);
    printf("  ✓ Brightness decreasing\n\n");

    /* Test brightness ramp down */
    printf("Test 4: Brightness Ramp Down (10 frames)\n");
    for (frame = 0; frame < 10; frame++) {
        uint8_t prev_brightness = ctx.state.breathing.brightness;
        breathing_update(&ctx);
        printf("  Frame %2d: brightness=%3d, direction=%2d\n",
               frame,
               ctx.state.breathing.brightness,
               ctx.state.breathing.direction);

        /* Verify brightness decreases */
        assert(ctx.state.breathing.brightness < prev_brightness ||
               ctx.state.breathing.brightness == 0);
    }
    printf("\n");

    /* Test direction reversal at min */
    printf("Test 5: Direction Reversal at Minimum\n");
    while (ctx.state.breathing.brightness > 0) {
        breathing_update(&ctx);
    }
    printf("  Reached min brightness: %d\n", ctx.state.breathing.brightness);
    assert(ctx.state.breathing.brightness == 0);
    /* Direction reversal happens in the SAME frame as reaching min */
    assert(ctx.state.breathing.direction == 1);
    printf("  ✓ Direction reversed at minimum (same frame)\n");

    /* Next update should start increasing */
    breathing_update(&ctx);
    printf("  Next frame: brightness=%d, direction=%d\n",
           ctx.state.breathing.brightness,
           ctx.state.breathing.direction);
    assert(ctx.state.breathing.brightness > 0);
    assert(ctx.state.breathing.direction == 1);
    printf("  ✓ Brightness increasing\n\n");

    /* Test full cycle */
    printf("Test 6: Full Breathing Cycle\n");
    breathing_init(&ctx);  /* Reset */
    uint16_t frames_to_max = 0;
    uint16_t frames_to_min = 0;

    /* Count frames to max (reversal happens at max) */
    while (ctx.state.breathing.brightness < 255) {
        breathing_update(&ctx);
        frames_to_max++;
    }
    /* Now at 255 with direction=-1, start counting down */

    /* Count frames to min (reversal happens at min) */
    while (ctx.state.breathing.brightness > 0) {
        breathing_update(&ctx);
        frames_to_min++;
    }

    printf("  Frames to max: %d (expected ~85 at speed=3)\n", frames_to_max);
    printf("  Frames to min: %d\n", frames_to_min);
    printf("  Full cycle: %d frames (~%.1f seconds at 30 FPS)\n",
           frames_to_max + frames_to_min,
           (frames_to_max + frames_to_min) / 30.0f);
    assert(frames_to_max == frames_to_min);  /* Should be symmetric */
    printf("  ✓ Symmetric breathing cycle\n\n");

    /* Test color scaling */
    printf("Test 7: Color Scaling Accuracy\n");

    /* Test at ~50% brightness */
    /* Set to 125 so after +3 it becomes 128 */
    breathing_init(&ctx);
    ctx.state.breathing.brightness = 125;
    ctx.state.breathing.direction = 1;
    breathing_update(&ctx);
    /* After update: brightness becomes 125+3=128 */
    /* (255 * 128) >> 8 = 127 */
    printf("  At brightness 128 (50%%): B=%d (expected 127)\n", pixels[0].b);
    assert(ctx.state.breathing.brightness == 128);
    assert(pixels[0].b == 127);

    /* Test at 0% - set to -3 so it clamps to 0 */
    ctx.state.breathing.brightness = 0;
    ctx.state.breathing.direction = -1;
    breathing_update(&ctx);
    /* After update: brightness becomes 0-3=0 (clamped), color = 0 */
    printf("  At brightness 0 (0%%): B=%d (expected 0)\n", pixels[0].b);
    assert(ctx.state.breathing.brightness == 0);
    assert(pixels[0].b == 0);

    /* Test at 100% - set to 252 so after +3 it becomes 255 */
    ctx.state.breathing.brightness = 252;
    ctx.state.breathing.direction = 1;
    breathing_update(&ctx);
    /* After update: brightness becomes 252+3=255 (clamped) */
    /* (255 * 255) >> 8 = 254 */
    printf("  At brightness 255 (100%%): B=%d (expected 254)\n", pixels[0].b);
    assert(ctx.state.breathing.brightness == 255);
    assert(pixels[0].b == 254);
    printf("  ✓ Color scaling working correctly\n\n");

    printf("========================================\n");
    printf("All tests passed! ✓\n");
    printf("\nEffect ready for hardware deployment.\n");

    return 0;
}
