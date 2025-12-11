#include "math_utils.h"

/*
 * 256-entry sine lookup table
 * Values are Q7 fixed point: actual = value / 127
 * Generated: round(sin(i * 2 * PI / 256) * 127)
 *
 * Index 0   = 0°   → sin = 0
 * Index 64  = 90°  → sin = 127
 * Index 128 = 180° → sin = 0
 * Index 192 = 270° → sin = -127
 */
const int8_t sin_table[256] = {
    /* 0-15 */
    0, 3, 6, 9, 12, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46,
    /* 16-31 */
    49, 51, 54, 57, 60, 63, 65, 68, 71, 73, 76, 78, 81, 83, 85, 88,
    /* 32-47 */
    90, 92, 94, 96, 98, 100, 102, 104, 106, 107, 109, 111, 112, 113, 115, 116,
    /* 48-63 */
    117, 118, 120, 121, 122, 122, 123, 124, 125, 125, 126, 126, 126, 127, 127, 127,
    /* 64-79 (peak at 64 = 90°) */
    127, 127, 127, 127, 126, 126, 126, 125, 125, 124, 123, 122, 122, 121, 120, 118,
    /* 80-95 */
    117, 116, 115, 113, 112, 111, 109, 107, 106, 104, 102, 100, 98, 96, 94, 92,
    /* 96-111 */
    90, 88, 85, 83, 81, 78, 76, 73, 71, 68, 65, 63, 60, 57, 54, 51,
    /* 112-127 */
    49, 46, 43, 40, 37, 34, 31, 28, 25, 22, 19, 16, 12, 9, 6, 3,
    /* 128-143 (zero crossing, going negative) */
    0, -3, -6, -9, -12, -16, -19, -22, -25, -28, -31, -34, -37, -40, -43, -46,
    /* 144-159 */
    -49, -51, -54, -57, -60, -63, -65, -68, -71, -73, -76, -78, -81, -83, -85, -88,
    /* 160-175 */
    -90, -92, -94, -96, -98, -100, -102, -104, -106, -107, -109, -111, -112, -113, -115, -116,
    /* 176-191 */
    -117, -118, -120, -121, -122, -122, -123, -124, -125, -125, -126, -126, -126, -127, -127, -127,
    /* 192-207 (trough at 192 = 270°) */
    -127, -127, -127, -127, -126, -126, -126, -125, -125, -124, -123, -122, -122, -121, -120, -118,
    /* 208-223 */
    -117, -116, -115, -113, -112, -111, -109, -107, -106, -104, -102, -100, -98, -96, -94, -92,
    /* 224-239 */
    -90, -88, -85, -83, -81, -78, -76, -73, -71, -68, -65, -63, -60, -57, -54, -51,
    /* 240-255 */
    -49, -46, -43, -40, -37, -34, -31, -28, -25, -22, -19, -16, -12, -9, -6, -3
};

int8_t sin_lookup(uint8_t angle)
{
    return sin_table[angle];
}

int8_t cos_lookup(uint8_t angle)
{
    /* cos(x) = sin(x + 90°) = sin(x + 64) */
    return sin_table[(uint8_t)(angle + 64)];
}

uint8_t fast_distance_3d(int8_t dx, int8_t dy, int8_t dz)
{
    /* Get absolute values */
    uint8_t ax = (dx < 0) ? -dx : dx;
    uint8_t ay = (dy < 0) ? -dy : dy;
    uint8_t az = (dz < 0) ? -dz : dz;

    /* Approximation: max + (sum of others) * 0.5 */
    /* This is roughly within 10% of true Euclidean distance */
    uint8_t max_val = ax;
    uint8_t sum_others = ay + az;

    if (ay > max_val) {
        sum_others = ax + az;
        max_val = ay;
    }
    if (az > max_val) {
        sum_others = ax + ay;
        max_val = az;
    }

    return max_val + (sum_others >> 1);
}

uint8_t lerp8(uint8_t a, uint8_t b, uint8_t t)
{
    /* a + (b - a) * t / 256 */
    int16_t diff = (int16_t)b - (int16_t)a;
    return (uint8_t)(a + ((diff * t) >> 8));
}

/* PRNG state */
static uint16_t g_random_seed = 1;

void random_seed(uint16_t seed)
{
    g_random_seed = seed ? seed : 1;  /* Avoid zero seed */
}

uint8_t random8(void)
{
    /* Linear congruential generator */
    g_random_seed = g_random_seed * 25173u + 13849u;
    return (uint8_t)(g_random_seed >> 8);
}

uint16_t random16(void)
{
    /* Two calls for 16-bit random */
    uint16_t result = random8();
    result = (result << 8) | random8();
    return result;
}

void hsv_to_rgb(uint8_t h, uint8_t s, uint8_t v,
                uint8_t* r, uint8_t* g, uint8_t* b)
{
    uint8_t region, remainder, p, q, t;

    if (s == 0) {
        /* Grayscale */
        *r = *g = *b = v;
        return;
    }

    region = h / 43;
    remainder = (h - (region * 43)) * 6;

    p = (v * (255 - s)) >> 8;
    q = (v * (255 - ((s * remainder) >> 8))) >> 8;
    t = (v * (255 - ((s * (255 - remainder)) >> 8))) >> 8;

    switch (region) {
        case 0:
            *r = v; *g = t; *b = p;
            break;
        case 1:
            *r = q; *g = v; *b = p;
            break;
        case 2:
            *r = p; *g = v; *b = t;
            break;
        case 3:
            *r = p; *g = q; *b = v;
            break;
        case 4:
            *r = t; *g = p; *b = v;
            break;
        default:
            *r = v; *g = p; *b = q;
            break;
    }
}
