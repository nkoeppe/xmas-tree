/*
 * effect_manager.c - Effect Manager Implementation
 *
 * Manages effect lifecycle: registration, switching, and updates
 * Uses function pointers for polymorphic effect behavior
 *
 * nko
 */

#include "effect_manager.h"
#include "led_buffer.h"
#include "coords.h"
#include <string.h>  /* For memset */

/*
 * Effect registry - const array of effect pointers
 * Stored in flash to save RAM
 * Order determines cycling order
 */
static const effect_def_t* const effect_registry[EFFECT_COUNT] = {
    &effect_breathing,
    &effect_wave,
    &effect_sparkle,
    &effect_meteor,
    &effect_gradient
};

/* Current effect index */
static uint8_t g_current_index = 0;

/* Running state (true = effects active, false = LEDs off) */
static uint8_t g_running = 1;

/* Shared effect context */
static effect_context_t g_context;

/* Coordinate bounds (computed once at startup) */
static coord_bounds_t g_bounds;

/*
 * Internal: Setup context for an effect
 */
static void setup_context(void)
{
    g_context.pixels = led_buffer_get();
    g_context.coords = coords_get();
    g_context.led_count = LED_COUNT;

    g_context.min_x = g_bounds.min_x;
    g_context.max_x = g_bounds.max_x;
    g_context.min_y = g_bounds.min_y;
    g_context.max_y = g_bounds.max_y;
    g_context.min_z = g_bounds.min_z;
    g_context.max_z = g_bounds.max_z;

    g_context.center_x = g_bounds.center_x;
    g_context.center_y = g_bounds.center_y;
    g_context.center_z = g_bounds.center_z;

    g_context.frame_time_ms = FRAME_TIME_MS;
}

/*
 * Internal: Call cleanup on current effect if it has one
 */
static void call_cleanup(void)
{
    const effect_def_t* effect = effect_registry[g_current_index];
    if (effect->cleanup != NULL) {
        effect->cleanup(&g_context);
    }
}

/*
 * Internal: Clear effect state and call init on new effect
 */
static void start_effect(void)
{
    const effect_def_t* effect = effect_registry[g_current_index];

    /* Clear state union to zero */
    memset(&g_context.state, 0, sizeof(effect_state_t));

    /* Call effect's init function */
    if (effect->init != NULL) {
        effect->init(&g_context);
    }
}

void effect_manager_init(void)
{
    /* Initialize LED buffer */
    led_buffer_init();

    /* Compute coordinate bounds once */
    coords_compute_bounds(&g_bounds);

    /* Setup shared context */
    setup_context();

    /* Start first effect */
    g_current_index = 0;
    g_running = 1;
    start_effect();
}

void effect_manager_next(void)
{
    /* Cleanup current effect */
    call_cleanup();

    /* Move to next effect (wrap around) */
    g_current_index++;
    if (g_current_index >= EFFECT_COUNT) {
        g_current_index = 0;
    }

    /* Start new effect */
    start_effect();
}

void effect_manager_update(void)
{
    if (!g_running) {
        return;  /* Powered off, do nothing */
    }

    const effect_def_t* effect = effect_registry[g_current_index];

    if (effect->update != NULL) {
        effect->update(&g_context);
    }
}

void effect_manager_toggle_power(void)
{
    g_running = !g_running;

    if (!g_running) {
        /* Power off: clear all LEDs */
        led_buffer_clear();
        led_buffer_show();
    } else {
        /* Power on: restart current effect */
        start_effect();
    }
}

uint8_t effect_manager_is_running(void)
{
    return g_running;
}

const char* effect_manager_get_name(void)
{
    return effect_registry[g_current_index]->name;
}
