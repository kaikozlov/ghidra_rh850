# SecOC

Runtime CAN message authentication (AUTOSAR Secure Onboard Communication).

| Report | Scope |
|---|---|
| [application-chain.md](application-chain.md) | Application receive profile: six SecOC-bound RX PDUs, freshness, command-7 verify, disabled KAT, and command-5 generation family |
| [key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) | Corrected NvM object model, object 15, unresolved live slot state, and the provisioned-unit experiment |

## Important distinction

The report's original proposed runtime-key command path (`0x65CD8 → 0x66E48 →
0x67590 → 0x72F58`) is **wrong** — those are AUTOSAR NvM
`ReadBlock`/`WriteBlock` and generic triplicate/checkpoint machinery, not CSM
key-set/MAC or an ICU command path. The correction is fully documented in
[key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) and recorded in
[../../status/CORRECTIONS.md](../../status/CORRECTIONS.md).

## Current state

All three object-15 copies are invalid in this exact snapshot, while the live
SecOC receive path selects protected ICU-S slot 4 without reading object 15.
The embedded `FF*16` KAT is compiled out and says nothing about the live slot.
Command 5 is substantially recovered as MAC generation, but slot-4 permission
requires dynamic testing — see
[application-chain.md](application-chain.md).
