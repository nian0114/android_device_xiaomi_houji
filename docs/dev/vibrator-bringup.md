# Vibrator waveform capabilities

Houji selects `libqtivibratoreffect.houji` through the existing QTI vibrator
`effect_lib` option. The device implementation derives from the Xiaomi effect
loader and uses the shared QTI `effect_stream` header; the common HAL is unchanged.

The extracted stock FIFO data provides the six `effect_0.bin` through
`effect_5.bin` effects at 24 kHz. No verified `primitive_effect_*.bin` data is
available in the current extraction. Missing primitive files must return null,
so QTI's `getSupportedPrimitives()` and `CAP_COMPOSE_EFFECTS` reflect that absence.
The previous loader fell back to CLICK for missing primitive IDs, falsely
advertising all primitives and playing every one as CLICK.

Regular effects retain their existing waveform and fallback behavior. The
framework can choose its non-composition fallback when composition is unsupported.
This change corrects capability reporting; it does not supply or tune missing
primitive waveforms. Only add primitive data after validating its identity,
24 kHz signed sample format and timing on this device.

After installing a build, inspect `dumpsys vibrator_manager` and verify that
composition support is absent while click, tick, heavy click and on/off vibration
still complete. These device checks remain pending; no ROM build was started as
part of the source change.
