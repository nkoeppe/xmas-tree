#ifndef MATH_UTILS_H
#define MATH_UTILS_H

#include <stdint.h>

/*
 * Fixed-Point Math Utilities
 * Provides efficient sin/cos lookup for embedded use
 *
 * Q7 format: value = actual_value * 127
 * Input angles: 0-255 maps to 0-360 degrees
 *   0   = 0°
 *   64  = 90°
 *   128 = 180°
 *   192 = 270°
 *   255 = ~360°
 *
 * Output: Q7 fixed point (-128 to 127)
 *   sin(0°)   = 0
 *   sin(90°)  = 127  (represents 1.0)
 *   sin(180°) = 0
 *   sin(270°) = -128 (represents -1.0)
 */

/* 256-entry sine table (stored in flash) */
extern const int8_t sin_table[256];

/* Lookup sine value for angle (0-255 = 0-360°) */
int8_t sin_lookup(uint8_t angle);

/* Lookup cosine value (sin with 90° offset) */
int8_t cos_lookup(uint8_t angle);

/*
 * Fast approximate distance (Manhattan-based)
 * Returns approximate 3D distance, suitable for effects
 * More accurate than pure Manhattan, faster than sqrt
 */
uint8_t fast_distance_3d(int8_t dx, int8_t dy, int8_t dz);

/*
 * Linear interpolation (8-bit)
 * Returns a + (b - a) * t / 256
 * t=0 returns a, t=255 returns ~b
 */
uint8_t lerp8(uint8_t a, uint8_t b, uint8_t t);

/*
 * HSV to RGB conversion (fast approximation)
 * h: hue 0-255 (0=red, 85=green, 170=blue)
 * s: saturation 0-255
 * v: value (brightness) 0-255
 * Writes RGB values to r, g, b pointers
 */
void hsv_to_rgb(uint8_t h, uint8_t s, uint8_t v,
                uint8_t* r, uint8_t* g, uint8_t* b);

/*
 * Random number generator (PRNG)
 * Simple linear congruential generator
 */
void random_seed(uint16_t seed);
uint8_t random8(void);
uint16_t random16(void);

#endif /* MATH_UTILS_H */
