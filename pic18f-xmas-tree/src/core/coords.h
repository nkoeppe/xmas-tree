/*
 * coords.h - 3D LED Coordinate System
 *
 * Provides access to the 3D coordinates of all 100 LEDs on the tree.
 * Coordinates are stored in program flash to minimize RAM usage.
 *
 * Original coordinates from xmas_tree_master/coords.json
 * Scaled to fit int8_t range for efficient storage and computation.
 *
 * nko
 */

#ifndef COORDS_H
#define COORDS_H

#include "../types.h"
#include "../config.h"

/*
 * 3D LED Coordinates
 * Stored in program flash (const)
 *
 * Original Python ranges (mm):
 *   X: -142.0 to 105.0 (max abs: 142)
 *   Y: -77.5 to 76.0 (max abs: 77.5)
 *   Z: -342.0 to -136.0 (max abs: 342)
 *
 * Scaled by factor: 0.371345 (to fit int8_t while preserving aspect ratio)
 *
 * Scaled ranges:
 *   X: -53 to 39
 *   Y: -29 to 28
 *   Z: -127 to -51
 */

/* Coordinate data in flash */
extern const coord_t coords_data[LED_COUNT];

/* Get pointer to coordinate array */
const coord_t* coords_get(void);

/* Computed bounds structure */
typedef struct {
    int8_t min_x, max_x;
    int8_t min_y, max_y;
    int8_t min_z, max_z;
    int8_t center_x, center_y, center_z;
} coord_bounds_t;

/* Compute bounds from coordinate data (call once at startup) */
void coords_compute_bounds(coord_bounds_t* bounds);

#endif /* COORDS_H */
