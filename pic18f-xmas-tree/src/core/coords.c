/*
 * coords.c - 3D LED Coordinate System Implementation
 *
 * Contains the actual coordinate data for all 100 LEDs.
 * Data stored in program flash (const) to save RAM.
 *
 * Coordinates converted from xmas_tree_master/coords.json
 * and scaled by factor 1.028 to fit int8_t range.
 *
 * nko
 */

#include "coords.h"

/*
 * LED coordinate data - stored in program flash
 *
 * Each entry is {x, y, z} in int8_t format.
 * Scaled from original floating-point coordinates by factor 0.371345
 * to preserve the tree's 3D structure while fitting in 8-bit signed integers.
 */
const coord_t coords_data[LED_COUNT] = {
    /* LED  0- 4 */
    {  -14,   12,  -97 }, {  -15,    1,  -90 }, {    1,    3,  -90 },
    {    1,    1,  -89 }, {    6,  -12,  -91 },

    /* LED  5- 9 */
    {    0,    7,  -95 }, {  -12,   -5,  -97 }, {  -16,  -14,  -97 },
    {   -6,  -16,  -84 }, {   -6,  -24,  -92 },

    /* LED 10-14 */
    {    3,  -26,  -97 }, {    7,  -13,  -95 }, {   17,  -14,  -95 },
    {   19,  -29,  -96 }, {   26,  -27,  -95 },

    /* LED 15-19 */
    {   34,  -27,  -98 }, {   38,  -18,  -96 }, {   36,   14, -103 },
    {   38,   17, -110 }, {   33,  -20, -124 },

    /* LED 20-24 */
    {   31,  -16, -127 }, {   35,   14, -126 }, {   39,   23, -117 },
    {   36,   27, -109 }, {   34,   28, -110 },

    /* LED 25-29 */
    {   35,   14,  -97 }, {   38,   19,  -95 }, {   30,   22,  -92 },
    {   26,   25,  -96 }, {   16,   24,  -93 },

    /* LED 30-34 */
    {   16,   14,  -94 }, {    9,   12,  -96 }, {   -1,    6,  -95 },
    {    0,   15,  -85 }, {  -11,   12,  -98 },

    /* LED 35-39 */
    {  -14,   15,  -85 }, {  -16,   20,  -85 }, {  -28,   19,  -88 },
    {  -30,   13,  -85 }, {  -33,    5,  -78 },

    /* LED 40-44 */
    {  -27,   16,  -65 }, {  -26,   17,  -64 }, {  -38,   15,  -55 },
    {  -38,   18,  -51 }, {  -49,   18,  -54 },

    /* LED 45-49 */
    {  -52,   18,  -63 }, {  -50,   20,  -67 }, {  -53,   21,  -77 },
    {  -37,   19,  -81 }, {  -37,   19,  -88 },

    /* LED 50-54 */
    {  -35,   20,  -96 }, {  -51,   17,  -98 }, {  -52,   14, -101 },
    {  -47,    7, -106 }, {  -49,   -2, -104 },

    /* LED 55-59 */
    {  -46,   -7,  -99 }, {  -42,   -7,  -92 }, {  -40,    8,  -88 },
    {  -37,   -4,  -85 }, {  -32,  -12,  -82 },

    /* LED 60-64 */
    {  -33,   -1,  -78 }, {  -41,    2,  -72 }, {  -50,   -2,  -66 },
    {  -48,   -4,  -56 }, {  -44,   -5,  -52 },

    /* LED 65-69 */
    {  -35,   -6,  -51 }, {  -36,    9,  -60 }, {  -32,  -10,  -66 },
    {  -37,  -17,  -71 }, {  -30,  -10,  -76 },

    /* LED 70-74 */
    {  -27,    2,  -79 }, {  -28,   -2,  -93 }, {  -42,    0,  -87 },
    {  -38,    1,  -77 }, {  -31,   -2,  -71 },

    /* LED 75-79 */
    {  -22,   -1,  -79 }, {  -42,    0,  -87 }, {  -29,  -12,  -97 },
    {  -27,   -8,  -98 }, {  -26,    4,  -97 },

    /* LED 80-84 */
    {  -13,    3,  -97 }, {  -21,  -11,  -97 }, {  -17,   -8,  -88 },
    {  -12,  -14,  -96 }, {   -3,   -6,  -95 },

    /* LED 85-89 */
    {  -10,    6,  -97 }, {   -5,  -12,  -85 }, {    3,    2,  -94 },
    {    6,   -6,  -86 }, {    4,  -14,  -87 },

    /* LED 90-94 */
    {   14,  -15,  -95 }, {   19,   -7,  -95 }, {   18,    3,  -95 },
    {   16,    5,  -94 }, {   -1,    1,  -94 },

    /* LED 95-99 */
    {    6,   11,  -96 }, {   -1,   -4,  -95 }, {  -10,    9,  -97 },
    {   -8,   16,  -97 }, {   10,   18,  -96 }
};

const coord_t* coords_get(void)
{
    return coords_data;
}

void coords_compute_bounds(coord_bounds_t* bounds)
{
    int8_t min_x = 127, max_x = -128;
    int8_t min_y = 127, max_y = -128;
    int8_t min_z = 127, max_z = -128;
    int16_t sum_x = 0, sum_y = 0, sum_z = 0;
    uint8_t i;

    for (i = 0; i < LED_COUNT; i++) {
        const coord_t* c = &coords_data[i];

        if (c->x < min_x) min_x = c->x;
        if (c->x > max_x) max_x = c->x;
        if (c->y < min_y) min_y = c->y;
        if (c->y > max_y) max_y = c->y;
        if (c->z < min_z) min_z = c->z;
        if (c->z > max_z) max_z = c->z;

        sum_x += c->x;
        sum_y += c->y;
        sum_z += c->z;
    }

    bounds->min_x = min_x;
    bounds->max_x = max_x;
    bounds->min_y = min_y;
    bounds->max_y = max_y;
    bounds->min_z = min_z;
    bounds->max_z = max_z;

    /* Compute center as average of all coordinates */
    bounds->center_x = (int8_t)(sum_x / LED_COUNT);
    bounds->center_y = (int8_t)(sum_y / LED_COUNT);
    bounds->center_z = (int8_t)(sum_z / LED_COUNT);
}
