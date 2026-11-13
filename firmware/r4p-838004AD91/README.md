# 2024 RAV4 Prime meter `838004AD91`

Canonical reference inputs for the yc-contributed US meter. The raw identity
`838004AD9110` is at CodeFlash `0x156898`; the exact RH850 MCU part is unknown.

| Image | Size | Base | SHA-256 |
|---|---:|---:|---|
| `cflash.bin` | `0x200000` | `0x00000000` | `cc75cac2aaa4a648dadcad3d3d59d0c1bb293c53f1dbfcf9bc0fc88b4b6a4322` |
| `boot.bin` | `0x8000` | `0x01000000` | `e8c3058f637725ca9a32b3ec6e38eb9408cf76c18847139cac22b853da6225d9` |
| `dflash.bin` | `0x10000` | `0xFF200000` | `569ef4661fb2e98a156c698e3eba160d6389cd811b41a75cebb78baa681618eb` |

These are complete, byte-identical copies of
`community/yc/r4p/meter/r4p-us-2024-dash-{cflash,bootflash,dflash}.bin`.
No prefix removal, rebasing, or truncation is required. CodeFlash offset zero
contains the reset jump to `0xEE8`. Application data extends past `0x170000`,
code occupies `0x1FAFE0..0x1FCA87`, and metadata at `0x1FFFE0` contains the
application entry address `0x10634`. Truncating to 1 MiB would discard these.
The analysis profile marks erased gaps non-executable while preserving their
addresses and bytes.

`boot.bin` is the extended-user image. Startup relocation tables join its
segments with CodeFlash segments in RAM. The boot/reprogramming and application
stages have different GP/TP values and reuse RAM; the target profile models
those contexts separately.

Registry: [`data/analysis_targets.json`](../../data/analysis_targets.json).
Analysis: [R4P meter report](../../docs/variants/yc-r4p-2024-meter.md).
