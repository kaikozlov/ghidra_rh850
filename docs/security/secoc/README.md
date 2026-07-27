# SecOC

Runtime CAN message authentication (AUTOSAR Secure Onboard Communication).

| Report | Scope |
|---|---|
| [application-chain.md](application-chain.md) | Application receive profile: the six SecOC-bound RX PDUs, freshness construction, CMAC verify path |
| [key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) | Corrected NvM object model, object 15, the unprovisioned/default key state, and the provisioned-unit experiment |

## Important distinction

The report's original proposed runtime-key command path (`0x65CD8 → 0x66E48 →
0x67590 → 0x72F58`) is **wrong** — those are AUTOSAR NvM
`ReadBlock`/`WriteBlock` and generic triplicate/checkpoint machinery, not CSM
key-set/MAC or an ICU command path. The correction is fully documented in
[key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) and recorded in
[../../status/CORRECTIONS.md](../../status/CORRECTIONS.md).

## Current state

This calibration's slot-4 known-answer vector equals CMAC of 16 zero bytes
under an erased `FF*16` key, and all three object-15 copies are invalid in
this exact snapshot. The leading explanation is an unprovisioned/default key
state. A provisioned unit must be tested dynamically — see the experiment in
[key-storage-and-lifecycle.md](key-storage-and-lifecycle.md).
