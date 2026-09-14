# yc Venza airbag-sensor firmware artifacts

**Contributor:** yc (`@yc`, comma Discord)
**Received:** 2026-09-14
**Vehicle attribution:** contributor-provided Toyota Venza airbag sensor
**ECU family:** contributor reports RH850; exact MCU/airbag ECU identity is not yet established from the supplied metadata

This directory preserves two raw firmware artifacts supplied by yc after a
hardware-glitch extraction of a Toyota Venza airbag sensor. The contributor
reports that the extraction method is similar to Willem's prior RH850 glitching
work. The files are retained byte-for-byte and should be treated as immutable
source evidence.

The surrounding Discord discussion was motivated by EPS recovery. yc described
`boot.bin` as an airbag-sensor boot-flash image that might execute before the
ordinary CodeFlash bootloader and suggested checking for an external
stay-in-boot mechanism. Reverse engineering now narrows that interpretation:
the airbag CodeFlash maps `boot.bin` at `0x01000000..0x01007FFF`, copies its
executable portion into RAM as an `AUBIST_RPRG_201902` reprogramming component,
and enters programming through a normal policy-gated `10 02` DCM transition plus
a retained RAM handoff. It is not evidence of an immutable pre-CodeFlash boot
stage or a power-up `10 02` shortcut.

See
[`docs/variants/yc-venza-airbag-reprogramming-2026-09-14.md`](../../docs/variants/yc-venza-airbag-reprogramming-2026-09-14.md)
for the recovered relocation, DCM and startup chain.

## Supplied artifacts

| File | Size | SHA-256 | Current interpretation |
|---|---:|---|---|
| `venza/boot.bin` | 32,768 | `943934abc9a5c676eff46f51f008baa39e4f533e66650ffcce54d7bfb6e6e6e2` | Extended-user-area image at `0x01000000..0x01007FFF`; executable payload is relocated into RAM as part of the RPRG runtime. |
| `venza/cflash.bin` | 3,145,728 | `2dfaf7ce21cb04af1126192f574103f63802352f8717fa0f03986d5a11d067f9` | Airbag-sensor CodeFlash dump; meaningful/non-fill content is concentrated below `0x180000`. |

No DataFlash, acquisition transcript, part number, vehicle model year, or
coverage bitmap accompanied this import. Raw CodeFlash identity strings include
`8917048E30` and `8917F48692`; adding Toyota punctuation/part-number semantics to
those strings remains interpretation rather than contributor metadata.
