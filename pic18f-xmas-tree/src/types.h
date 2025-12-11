#ifndef TYPES_H
#define TYPES_H

#include <stdint.h>
#include <stdbool.h>

/* Color structure (BRG order for WS2812) */
typedef struct {
    uint8_t b;  /* Blue */
    uint8_t r;  /* Red */
    uint8_t g;  /* Green */
} color_brg_t;

/* 3D coordinate (scaled to int8_t range) */
typedef struct {
    int8_t x;
    int8_t y;
    int8_t z;
} coord_t;

/* Forward declaration */
struct effect_context;

/* Effect function pointer types */
typedef void (*effect_init_fn)(struct effect_context* ctx);
typedef void (*effect_update_fn)(struct effect_context* ctx);
typedef void (*effect_cleanup_fn)(struct effect_context* ctx);

/* Effect definition (stored in flash) */
typedef struct {
    const char* name;
    effect_init_fn init;
    effect_update_fn update;
    effect_cleanup_fn cleanup;  /* Can be NULL if no cleanup needed */
} effect_def_t;

/* Effect-specific state union (max 32 bytes) */
typedef union {
    struct {
        uint8_t brightness;
        int8_t direction;
    } breathing;

    struct {
        uint16_t time;
    } wave;

    struct {
        uint8_t base_hue;
        uint8_t brightness;
        int8_t pulse_direction;
        uint16_t gradient_shift;
    } sparkle;

    struct {
        int8_t meteor_x[4];
        int8_t meteor_y[4];
        int8_t meteor_z[4];
        uint8_t meteor_count;
    } meteor;  /* 13 bytes */

    struct {
        int8_t plane_pos;
        int8_t direction;
    } gradient;

    uint8_t raw[32];  /* Ensure 32 byte max */
} effect_state_t;

/* Runtime context passed to effects */
typedef struct effect_context {
    color_brg_t* pixels;        /* Pointer to LED buffer */
    const coord_t* coords;      /* Pointer to coordinate data */
    uint8_t led_count;

    /* Coordinate bounds (calculated at startup) */
    int8_t min_x, max_x;
    int8_t min_y, max_y;
    int8_t min_z, max_z;

    /* Center point */
    int8_t center_x, center_y, center_z;

    /* Frame timing */
    uint32_t frame_time_ms;

    /* Effect-specific state */
    effect_state_t state;
} effect_context_t;

#endif /* TYPES_H */
