# Breathing Sphere Effect - Implementation Summary

## Overview

The Breathing Sphere effect is the first and simplest LED effect for the PIC18F Christmas tree controller. It creates a smooth, rhythmic brightness oscillation across all LEDs simultaneously.

## Implementation

**File:** `src/effects/effect_breathing.c`

### Algorithm

1. **State Management:**
   - `brightness`: Current brightness level (0-255)
   - `direction`: +1 (increasing) or -1 (decreasing)

2. **Update Cycle:**
   - Add `BREATHING_SPEED * direction` to brightness
   - Clamp brightness to [0, 255] range
   - Reverse direction when bounds are reached
   - Scale base color by brightness using fixed-point math
   - Apply uniform color to all LEDs

3. **Color Scaling:**
   - Uses fixed-point multiplication and right shift: `(color * brightness) >> 8`
   - Avoids floating-point operations (critical for PIC18F)
   - Produces smooth brightness transitions

### Configuration

```c
#define BREATHING_SPEED     3       /* Brightness increment per frame */
#define BREATHING_COLOR_B   255     /* Blue component (BRG order) */
#define BREATHING_COLOR_R   0       /* Red component */
#define BREATHING_COLOR_G   0       /* Green component */
```

### Performance Characteristics

- **Cycle Period:** 170 frames (85 up, 85 down)
- **Cycle Time:** ~5.7 seconds at 30 FPS
- **Memory Usage:** 2 bytes state (brightness + direction)
- **CPU Usage:** Minimal (simple arithmetic, no floating-point)

## Testing

**Test Suite:** `test_breathing.c`

Comprehensive validation covering:
- ✓ Initialization state
- ✓ Brightness ramp up
- ✓ Direction reversal at maximum (255)
- ✓ Brightness ramp down
- ✓ Direction reversal at minimum (0)
- ✓ Full cycle symmetry
- ✓ Color scaling accuracy at 0%, 50%, 100%
- ✓ Uniform application to all LEDs

**Test Results:** All 7 test suites passed.

### Key Test Findings

1. **Direction Reversal Timing:**
   - Reversal occurs in the **same frame** as reaching the bound
   - When brightness reaches 255, direction immediately becomes -1
   - Next frame starts decreasing from 252 (255 - 3)

2. **Color Scaling Precision:**
   - At brightness 128 (50%): produces color value 127
   - At brightness 255 (100%): produces 254 (not 255 due to >>8 rounding)
   - This is expected behavior for fixed-point math

3. **Cycle Symmetry:**
   - Frames to max: 85
   - Frames to min: 85
   - Perfect symmetry verified

## Hardware Integration

The effect is already registered in `effect_manager.c`:

```c
static const effect_def_t* const effect_registry[EFFECT_COUNT] = {
    &effect_breathing,  /* Index 0 - default effect */
    // ... other effects
};
```

### Effect Definition

```c
const effect_def_t effect_breathing = {
    "Breathing",        /* Display name */
    breathing_init,     /* Initialization function */
    breathing_update,   /* Frame update function */
    NULL                /* No cleanup required */
};
```

## Usage

The effect automatically starts when the device powers on (as the first effect in the registry). Users can cycle to it using the button interface.

### Button Controls

- **Short press:** Cycle to next effect
- **Long press (2s):** Toggle power on/off

## Technical Notes

### Fixed-Point Math

The color scaling uses integer arithmetic to avoid floating-point:

```c
/* Python reference: apply_brg(color, brightness) where brightness ∈ [0, 1] */
/* C implementation: (color * brightness_uint8) >> 8 where brightness ∈ [0, 255] */
color.b = (uint8_t)((BREATHING_COLOR_B * new_brightness) >> 8);
```

**Equivalence:**
- Python: `color * 0.5` (50% brightness)
- C: `(color * 128) >> 8 = (color * 128) / 256 ≈ color * 0.5`

### Memory Efficiency

- Effect state: 2 bytes (within 32-byte union)
- No dynamic allocation
- Const data stored in flash (not RAM)

### PIC18F Considerations

1. **No Floating-Point:** All calculations use integer math
2. **Minimal RAM:** State fits in 2 bytes
3. **Fast Execution:** Simple arithmetic operations only
4. **Deterministic Timing:** No variable-time operations

## Future Enhancements

Potential configuration options (currently compile-time constants):

- Adjustable speed via button interface
- Configurable color via button sequences
- Different waveforms (ease-in/ease-out)

These would require adding runtime configuration state.

## Validation Status

- ✅ Algorithm implementation complete
- ✅ Unit tests passing (7/7)
- ✅ Effect registered in manager
- ✅ No floating-point operations
- ✅ Memory footprint within limits
- ✅ Ready for hardware testing

## Next Steps

1. Flash firmware to PIC18F device
2. Verify visual appearance on hardware
3. Measure actual frame timing
4. Proceed to next effect (Wave)

---

**Author:** nko
**Date:** 2025-12-08
**Phase:** 6 (LED Effects - Effect #1 of 5)
