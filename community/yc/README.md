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

The surrounding Discord discussion is specifically relevant to EPS recovery:
yc described `boot.bin` as an airbag-sensor boot-flash image that executes before
the ordinary CodeFlash bootloader at `0x00000000`, and suggested checking whether
this earlier stage contains an external boot-entry mechanism that may transfer to
the related RH850 EPS family. That possible transfer is a hypothesis until it is
established from the binaries themselves.

## Supplied artifacts

| File | Size | SHA-256 | Contributor interpretation |
|---|---:|---|---|
| `venza/boot.bin` | 32,768 | `943934abc9a5c676eff46f51f008baa39e4f533e66650ffcce54d7bfb6e6e6e2` | Airbag-sensor boot flash; reported to execute before the `0x0` CodeFlash bootloader. |
| `venza/cflash.bin` | 3,145,728 | `2dfaf7ce21cb04af1126192f574103f63802352f8717fa0f03986d5a11d067f9` | Airbag-sensor CodeFlash dump. |

No DataFlash, acquisition transcript, address map, part number, vehicle model
year, or coverage bitmap accompanied this import. In particular, the filename
`boot.bin` does not by itself establish the boot-flash mapping address; preserve
file offsets separately from any mapped virtual address inferred during reverse
engineering.
