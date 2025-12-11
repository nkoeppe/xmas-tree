# WS2812 Driver Implementation

## Overview

Bit-bang WS2812 LED driver for PIC18F microcontroller at 64MHz. Implements precise timing requirements for addressable RGB LED strips using assembly NOPs for cycle-accurate delays.

## Files Created

### HAL Layer (`src/hal/`)

**ws2812.h** - Driver interface
- `ws2812_init()` - Initialize data pin and send reset
- `ws2812_send_buffer()` - Transmit pixel data with critical section
- `ws2812_reset()` - Send >50μs reset/latch pulse

**ws2812.c** - Driver implementation
- Bit-bang protocol with inline assembly for timing
- Interrupt-safe transmission (disables all interrupts during send)
- GRB byte order per WS2812 specification

### Core Layer (`src/core/`)

**led_buffer.h** - Pixel buffer management interface
- `led_buffer_init()` - Initialize driver and clear buffer
- `led_buffer_get()` - Direct buffer access for effects
- `led_buffer_clear()` - Set all pixels to black
- `led_buffer_set_pixel()` - Set individual pixel with bounds checking
- `led_buffer_show()` - Transmit buffer to LED strip

**led_buffer.c** - Buffer implementation
- Static 100-pixel buffer in RAM (300 bytes)
- Bounds-checked pixel access
- Wraps WS2812 hardware driver

### Test Program

**test_ws2812.c** - Rainbow animation demo
- 30 FPS rainbow pattern across 100 LEDs
- Demonstrates buffer access and HSV color conversion
- Replace main.c contents to test driver

## Timing Analysis

### WS2812 Protocol Requirements

| Signal | Spec Time | Tolerance | Target Cycles | Actual Time |
|--------|-----------|-----------|---------------|-------------|
| T0H (0-bit high) | 400ns | ±150ns | 6-7 | ~375ns |
| T0L (0-bit low) | 850ns | ±150ns | 13-14 | ~850ns |
| T1H (1-bit high) | 800ns | ±150ns | 12-13 | ~750ns |
| T1L (1-bit low) | 450ns | ±150ns | 7-8 | ~450ns |
| Reset | >50μs | - | - | 60μs |

**Note:** At 64MHz, Fosc/4 = 16MHz instruction clock → 62.5ns per cycle

### Timing Implementation

```c
/* NOP macros for precise delays */
#define NOP() __asm("NOP")
#define NOP2() NOP(); NOP()
#define NOP4() NOP2(); NOP2()
#define NOP8() NOP4(); NOP4()

/* Send '1' bit */
LED_DATA_PIN = 1;
NOP8(); NOP4();     // 12 cycles ≈ 750ns high
LED_DATA_PIN = 0;
NOP4(); NOP2();     // 6 cycles + loop overhead ≈ 450ns low

/* Send '0' bit */
LED_DATA_PIN = 1;
NOP4(); NOP2();     // 6 cycles ≈ 375ns high
LED_DATA_PIN = 0;
NOP8(); NOP4();     // 12 cycles + loop overhead ≈ 850ns low
```

### Critical Section Management

Interrupts must be disabled during transmission to prevent timing glitches:

```c
uint8_t saved_intcon = INTCON;
INTCONbits.GIE = 0;   // Disable global interrupts
INTCONbits.GIEH = 0;  // Disable high-priority
INTCONbits.GIEL = 0;  // Disable low-priority

/* Transmit all pixels */
for (i = 0; i < count; i++) {
    ws2812_send_byte(buffer[i].g);  // Green first
    ws2812_send_byte(buffer[i].r);  // Red second
    ws2812_send_byte(buffer[i].b);  // Blue third
}

INTCON = saved_intcon;  // Restore interrupts
```

**Interrupt Lockout Time:** 100 LEDs × 24 bits × ~1.25μs = ~3ms per frame

## Color Order: BRG vs GRB

**Storage Format (BRG):** Struct layout optimizes memory alignment
```c
typedef struct {
    uint8_t b;  // Blue
    uint8_t r;  // Red
    uint8_t g;  // Green
} color_brg_t;
```

**Transmission Order (GRB):** WS2812 protocol expects Green-Red-Blue
```c
ws2812_send_byte(buffer[i].g);  // Green first
ws2812_send_byte(buffer[i].r);  // Red second
ws2812_send_byte(buffer[i].b);  // Blue third
```

This separation allows application code to use logical naming while the driver handles protocol requirements.

## Usage Examples

### Basic: Single Color Fill

```c
#include "core/led_buffer.h"

void main(void) {
    uint8_t i;
    color_brg_t red = {0, 255, 0};  // BRG format

    led_buffer_init();

    // Fill all LEDs with red
    for (i = 0; i < LED_COUNT; i++) {
        led_buffer_set_pixel(i, red);
    }

    led_buffer_show();

    while(1);
}
```

### Advanced: Direct Buffer Access

```c
#include "core/led_buffer.h"
#include "core/math_utils.h"

void rainbow_effect(void) {
    color_brg_t* pixels = led_buffer_get();
    uint8_t i, hue;

    for (i = 0; i < LED_COUNT; i++) {
        uint8_t r, g, b;
        hue = i * 256 / LED_COUNT;

        hsv_to_rgb(hue, 255, 128, &r, &g, &b);

        pixels[i].r = r;
        pixels[i].g = g;
        pixels[i].b = b;
    }

    led_buffer_show();
}
```

### Integration with Frame Timer

```c
#include "hal/timer.h"
#include "core/led_buffer.h"

void main(void) {
    uint32_t last_frame = 0;

    timer_init();
    led_buffer_init();

    while (1) {
        uint32_t now = millis();

        if (now - last_frame >= FRAME_TIME_MS) {
            last_frame = now;

            // Update animation
            update_effect();

            // Send to LEDs
            led_buffer_show();
        }
    }
}
```

## Performance Characteristics

### Memory Usage
- Static buffer: 300 bytes (100 LEDs × 3 bytes)
- Code size: ~400 bytes (driver + buffer management)
- Stack usage: Minimal (<20 bytes)

### Timing
- Single LED: 24 bits × 1.25μs ≈ 30μs
- 100 LEDs: ~3ms (includes 60μs reset)
- Maximum frame rate: ~330 FPS (limited by protocol)
- Target frame rate: 30 FPS (33ms period)

### Power Consumption
- Data pin: ~1mA at 5V (negligible)
- LEDs: 60mA per LED at full white (6A total for 100 LEDs)
- Recommend external 5V 10A power supply for full brightness

## Hardware Configuration

### Pin Assignment (config.h)
```c
#define LED_DATA_PIN        LATCbits.LATC0
#define LED_DATA_TRIS       TRISCbits.TRISC0
```

### Electrical Requirements
- Data line: 5V logic (PIC18F output is 3.3V - may need level shifter)
- LED supply: 5V regulated (separate from microcontroller)
- Data capacitor: 1000μF near LED strip
- Data resistor: 220Ω-470Ω in series with data line

### Level Shifting (if needed)
```
PIC18F RC0 (3.3V) ──[74HCT125]── WS2812 DIN (5V)
                         |
                        GND
```

## Testing Procedure

1. **Hardware Verification**
   - Connect oscilloscope to data pin
   - Verify 400ns/800ns high pulses
   - Check low pulse timing
   - Confirm >50μs reset pulse

2. **Single LED Test**
   - Set LED_COUNT to 1
   - Send solid color (red, green, blue)
   - Verify correct color output
   - Check for color swap (indicates GRB order issue)

3. **Multi-LED Test**
   - Set LED_COUNT to 10
   - Send alternating colors
   - Verify pixel addressing
   - Check for color bleed or glitches

4. **Full Strip Test**
   - Use test_ws2812.c rainbow demo
   - Verify smooth animation
   - Check for flicker at 30 FPS
   - Measure frame update time with logic analyzer

## Troubleshooting

### Wrong Colors
- **Symptom:** Red shows as green, etc.
- **Cause:** Incorrect byte order
- **Fix:** Verify GRB transmission order in ws2812_send_buffer()

### Flickering LEDs
- **Symptom:** Random color changes
- **Cause:** Timing violations or interrupt conflicts
- **Fix:**
  - Check NOP counts match timing spec
  - Verify interrupts disabled during transmission
  - Measure actual pulse widths with oscilloscope

### No Output
- **Symptom:** LEDs stay off
- **Cause:** Hardware or initialization issue
- **Fix:**
  - Check power supply (5V at LED strip)
  - Verify data pin configuration (output mode)
  - Check level shifter if using 3.3V logic
  - Confirm reset pulse duration

### First LED Wrong, Rest OK
- **Symptom:** LED 0 glitches, others work
- **Cause:** Insufficient setup time after reset
- **Fix:** Increase reset pulse duration in ws2812_reset()

### Intermittent Glitches
- **Symptom:** Occasional wrong colors
- **Cause:** Interrupt timing interference
- **Fix:**
  - Verify critical section implementation
  - Check interrupt priority configuration
  - Reduce interrupt frequency if possible

## Integration Notes

### Effect System Integration
```c
/* In effect update function */
void effect_update(effect_context_t* ctx) {
    // ctx->pixels points to LED buffer
    // Modify pixels directly
    ctx->pixels[0].r = 255;
    ctx->pixels[0].g = 0;
    ctx->pixels[0].b = 0;

    // No need to call led_buffer_show() here
    // Main loop handles transmission
}
```

### Frame Rate Considerations
- WS2812 transmission: ~3ms for 100 LEDs
- Effect computation: Budget 30ms - 3ms = 27ms
- Timer ISR overhead: ~50μs per ms = 1.5ms total
- Available for effects: ~25ms per frame

### Interrupt Guidelines
- Keep Timer0 ISR fast (<50μs)
- Use low-priority for non-critical interrupts
- Expect 3ms delay in interrupt response during LED update
- Plan button debouncing around this constraint

## Next Steps (Phase 4)

1. **Button Handler** - Mode switching and long-press detection
2. **Effect Manager** - Effect selection and state management
3. **Effect Implementations** - Rainbow, sparkle, meteor shower, etc.
4. **Persistence** - EEPROM storage for last-used effect

## References

- WS2812 Datasheet: https://cdn-shop.adafruit.com/datasheets/WS2812.pdf
- PIC18F47Q10 Datasheet: Microchip DS40002043
- Timing analysis: 64MHz = 62.5ns per instruction cycle
