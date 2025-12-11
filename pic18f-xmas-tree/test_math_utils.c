/*
 * Simple validation test for math_utils
 * Compile: gcc -o test_math_utils test_math_utils.c src/core/math_utils.c -Isrc/core
 */

#include <stdio.h>
#include <stdlib.h>
#include "math_utils.h"

#define TEST(name, condition) \
    do { \
        if (condition) { \
            printf("[PASS] %s\n", name); \
        } else { \
            printf("[FAIL] %s\n", name); \
            exit(1); \
        } \
    } while(0)

int main(void)
{
    printf("=== Math Utils Validation ===\n\n");

    /* Test sin_lookup */
    printf("Testing sin_lookup:\n");
    TEST("sin(0°) == 0", sin_lookup(0) == 0);
    TEST("sin(90°) == 127", sin_lookup(64) == 127);
    TEST("sin(180°) == 0", sin_lookup(128) == 0);
    TEST("sin(270°) == -127", sin_lookup(192) == -127);

    /* Test cos_lookup */
    printf("\nTesting cos_lookup:\n");
    TEST("cos(0°) == 127", cos_lookup(0) == 127);
    TEST("cos(90°) == 0", cos_lookup(64) == 0);
    TEST("cos(180°) == -127", cos_lookup(128) == -127);
    TEST("cos(270°) == 0", cos_lookup(192) == 0);

    /* Test fast_distance_3d */
    printf("\nTesting fast_distance_3d:\n");
    TEST("distance(0,0,0) == 0", fast_distance_3d(0, 0, 0) == 0);
    TEST("distance(10,0,0) == 10", fast_distance_3d(10, 0, 0) == 10);
    TEST("distance(-10,0,0) == 10", fast_distance_3d(-10, 0, 0) == 10);
    uint8_t dist = fast_distance_3d(10, 10, 10);
    TEST("distance(10,10,10) > 0", dist > 0);
    printf("  distance(10,10,10) = %u (expected ~17)\n", dist);

    /* Test lerp8 */
    printf("\nTesting lerp8:\n");
    TEST("lerp8(0, 255, 0) == 0", lerp8(0, 255, 0) == 0);
    TEST("lerp8(0, 255, 255) ~= 255", lerp8(0, 255, 255) >= 254);
    TEST("lerp8(0, 255, 128) ~= 127", abs(lerp8(0, 255, 128) - 127) <= 1);
    TEST("lerp8(100, 200, 128) ~= 150", abs(lerp8(100, 200, 128) - 150) <= 1);

    /* Test random_seed and random8 */
    printf("\nTesting random8:\n");
    random_seed(42);
    uint8_t r1 = random8();
    uint8_t r2 = random8();
    uint8_t r3 = random8();
    TEST("random8 produces different values", r1 != r2 && r2 != r3);
    printf("  Random sequence: %u, %u, %u\n", r1, r2, r3);

    random_seed(42);
    uint8_t r1_repeat = random8();
    TEST("random_seed produces same sequence", r1 == r1_repeat);

    /* Test random16 */
    printf("\nTesting random16:\n");
    random_seed(1234);
    uint16_t rand16 = random16();
    TEST("random16 produces non-zero", rand16 != 0);
    printf("  random16() = %u\n", rand16);

    /* Test HSV to RGB */
    printf("\nTesting hsv_to_rgb:\n");
    uint8_t r, g, b;

    /* Red (h=0) */
    hsv_to_rgb(0, 255, 255, &r, &g, &b);
    TEST("HSV(0,255,255) -> Red", r == 255 && g < 50 && b < 50);
    printf("  Red: R=%u, G=%u, B=%u\n", r, g, b);

    /* Green (h=85) */
    hsv_to_rgb(85, 255, 255, &r, &g, &b);
    TEST("HSV(85,255,255) -> Green", g == 255 && r < 50 && b < 50);
    printf("  Green: R=%u, G=%u, B=%u\n", r, g, b);

    /* Blue (h=170) */
    hsv_to_rgb(170, 255, 255, &r, &g, &b);
    TEST("HSV(170,255,255) -> Blue", b == 255 && r < 50 && g < 50);
    printf("  Blue: R=%u, G=%u, B=%u\n", r, g, b);

    /* Grayscale (s=0) */
    hsv_to_rgb(128, 0, 200, &r, &g, &b);
    TEST("HSV(x,0,200) -> Gray", r == 200 && g == 200 && b == 200);
    printf("  Gray: R=%u, G=%u, B=%u\n", r, g, b);

    printf("\n=== All tests passed! ===\n");
    return 0;
}
