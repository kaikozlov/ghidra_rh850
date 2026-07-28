# SecOC

Runtime CAN message authentication (AUTOSAR Secure Onboard Communication).

| Report | Scope |
|---|---|
| [application-chain.md](application-chain.md) | Application receive profile: six SecOC-bound RX PDUs, freshness, command-7 verify, disabled KAT, and command-5 generation family |
| [key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) | Corrected NvM object model, object 15, protected slot state, and command-8 provisioning |
| [key-recovery-assessment.md](key-recovery-assessment.md) | Ranked existing-key recovery routes: peer ECU, chosen-input power/EM analysis, command permissions, provisioning capture, and fault injection |

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

For existing-key recovery, the best overall lead is a weaker same-vehicle
producer ECU. A direct command-13 experiment is also unresolved: the stock
application never invokes it, but the restricted ICU-S manual is unavailable,
so selector-4 behavior and a possible slot-4-to-`RAM_KEY` copy/alias are not
statically disproved. The best characterized direct physical path remains
chosen-input power/EM analysis of repeated command-7 verification: CAN-FD
`0x090`/`0x0D7` place 14 chosen payload bytes in CMAC's first block. See
[key-recovery-assessment.md](key-recovery-assessment.md).
