/*
 * effect_manager.h - Effect Manager Core
 *
 * Handles effect registration, switching, and update dispatch
 * Uses strategy pattern with function pointers for extensibility
 *
 * nko
 */

#ifndef EFFECT_MANAGER_H
#define EFFECT_MANAGER_H

#include "../types.h"
#include "../config.h"

/* Forward declarations for effects (add more as implemented) */
extern const effect_def_t effect_breathing;
extern const effect_def_t effect_wave;
extern const effect_def_t effect_sparkle;
extern const effect_def_t effect_meteor;
extern const effect_def_t effect_gradient;

/*
 * Initialize effect manager
 * Sets up context with LED buffer and coordinates
 * Starts the first (default) effect
 */
void effect_manager_init(void);

/*
 * Switch to the next effect in the registry
 * Calls cleanup on current effect, init on new effect
 */
void effect_manager_next(void);

/*
 * Update current effect (call once per frame)
 * Dispatches to the active effect's update function
 */
void effect_manager_update(void);

/*
 * Toggle power state (on/off)
 * When off, all LEDs are turned off
 * When on, continues with current effect
 */
void effect_manager_toggle_power(void);

/*
 * Check if effects are running
 * Returns false when powered off
 */
uint8_t effect_manager_is_running(void);

/*
 * Get name of current effect
 * Returns pointer to effect name string in flash
 */
const char* effect_manager_get_name(void);

#endif /* EFFECT_MANAGER_H */
