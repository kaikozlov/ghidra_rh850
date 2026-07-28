# SecOC

Runtime CAN message authentication (AUTOSAR Secure Onboard Communication).

| Report | Scope |
|---|---|
| [application-chain.md](application-chain.md) | Application receive profile: six SecOC-bound RX PDUs, freshness, command-7 verify, disabled KAT, and command-5 generation family |
| [key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) | Corrected NvM object model, object 15, protected slot state, and command-8 provisioning |
| [key-recovery-assessment.md](key-recovery-assessment.md) | Ranked existing-key recovery routes: peer ECU, software command experiments, command permissions, side channels, provisioning capture, and fault injection |
| [software-path-assessment.md](software-path-assessment.md) | Software-first audit: diagnostic/CAN bounds, constructible bootloader code execution, dormant ICU state, and command-5/DID-1010 reuse templates |

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
Command 5 is substantially recovered as MAC generation and accepts selector 4
in software. Its sole configured caller is a dormant CAN-fed crypto-test bank;
the stock bank compares the result locally, has no recovered activation edge,
and is not a production SecOC transmit path. The generic command-1/3 wrapper
also accepts selectors `0..14`, but neither its slot-4 AES permission nor
command-5 generation permission is known.

For existing-key recovery, the best overall lead remains a weaker same-vehicle
producer ECU. The next direct step is now explicitly software-first: recovered
gate material can construct an authenticated 4 KiB bootloader callback, and the
existing CAN-dump payloads leave more than `0xE00` bytes for a direct ICU-S
command/status experiment. A negative bootloader-context result does not close
application lifecycle behavior; the same trust chain can in principle install a
restorable application hook because boot validity is CRC/marker consistency, not
a signature.

Command 13 remains unresolved: the stock application never invokes it and the
restricted ICU-S manual is unavailable, so selector-4 behavior and a possible
slot-4-to-`RAM_KEY` copy/alias are not statically established. Chosen-input
power/EM analysis remains a later characterized fallback, not the assumed next
step. See [software-path-assessment.md](software-path-assessment.md) and
[key-recovery-assessment.md](key-recovery-assessment.md).
