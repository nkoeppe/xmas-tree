# PIC18F Christmas Tree LED Controller

A bare-metal C implementation of LED effects for WS2812 LED strips running on PIC18F microcontrollers.

## Overview

This project ports the Python-based Christmas tree LED effects to a standalone PIC18F microcontroller, enabling the tree to run without a Raspberry Pi.

## Features

- 5 Built-in effects:
  - **Breathing** - Smooth brightness oscillation
  - **Wave 3D** - Flowing sine waves using 3D coordinates
  - **Sparkle** - Random white sparkles over gradient
  - **Meteor** - Falling particles with trails
  - **Gradient** - Moving rainbow plane
- Single-button control:
  - Short press: Cycle to next effect
  - Long press (2s): Toggle power on/off
- 30 FPS smooth animation
- Low memory footprint (~510 bytes RAM)

## Hardware Requirements

- PIC18F4520 (or similar PIC18F with 1.5KB+ RAM, 32KB+ flash)
- WS2812 LED strip (100 LEDs)
- Single push button (optional, for control)

### Pin Connections

| Function | PIC Pin | Notes |
|----------|---------|-------|
| LED Data | RC0 | Connect to WS2812 DIN |
| Button | RB0 | Active low, internal pull-up |

## Building

### Prerequisites

- MPLAB X IDE (v5.x or later)
- XC8 Compiler (v2.x or later)

### Steps

1. Open MPLAB X
2. Create new project for PIC18F4520
3. Add all files from `src/` directory
4. Set optimization level (e.g., 2 for speed)
5. Build → Make and Program Device

## Project Structure

```
src/
├── main.c                    # Entry point, main loop
├── config.h                  # Hardware configuration
├── types.h                   # Core type definitions
├── hal/
│   ├── timer.h/c            # Millisecond timing
│   ├── button.h/c           # Debounced button input
│   └── ws2812.h/c           # LED strip driver
├── core/
│   ├── effect_manager.h/c   # Effect switching
│   ├── led_buffer.h/c       # Pixel buffer
│   ├── coords.h/c           # 3D LED coordinates
│   └── math_utils.h/c       # Sin tables, HSV, PRNG
└── effects/
    ├── effect_breathing.c
    ├── effect_wave.c
    ├── effect_sparkle.c
    ├── effect_meteor.c
    └── effect_gradient.c
```

## Adding New Effects

1. Create `src/effects/effect_myeffect.c`
2. Implement init and update functions
3. Define effect_def_t const
4. Add extern declaration in `effect_manager.h`
5. Add to registry array in `effect_manager.c`
6. Update `EFFECT_COUNT` in `config.h`

### Effect Template

```c
#include "../core/effect_manager.h"
#include "../types.h"

static void myeffect_init(effect_context_t* ctx) {
    /* Initialize effect state */
}

static void myeffect_update(effect_context_t* ctx) {
    /* Called 30x per second */
    /* Write to: ctx->pixels[i] = (color_brg_t){b, r, g}; */
    /* Read from: ctx->coords[i].x, .y, .z */
}

const effect_def_t effect_myeffect = {
    "My Effect",
    myeffect_init,
    myeffect_update,
    NULL  /* cleanup - optional */
};
```

## Memory Usage

| Component | RAM | Flash |
|-----------|-----|-------|
| Pixel buffer | 300B | - |
| Effect state | 32B | - |
| Coordinates | - | 300B |
| Sin table | - | 256B |
| Code | - | ~15KB |
| **Total** | ~510B | ~15KB |

## License

This project is part of the xmas-tree project.
