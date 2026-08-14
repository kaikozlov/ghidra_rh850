# SecOC

Runtime CAN message authentication (AUTOSAR Secure Onboard Communication).

| Report | Scope |
|---|---|
| [application-chain.md](application-chain.md) | Application receive profile: six SecOC-bound RX PDUs, freshness, command-7 verify, disabled KAT, and command-5 generation family |
| [sender-implementation.md](sender-implementation.md) | Pinned opendbc sender analysis, direction/ID boundaries, and the independent local classic-CAN signer |
| [key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) | Corrected NvM object model, object 15, protected slot state, and command-8 provisioning |
| [key-recovery-assessment.md](key-recovery-assessment.md) | Ranked existing-key recovery routes: peer ECU, software command experiments, command permissions, side channels, provisioning capture, and fault injection |
| [software-path-assessment.md](software-path-assessment.md) | Software-first audit: diagnostic/CAN bounds, constructible bootloader code execution, dormant ICU state, and command-5/RoutineControl-RID-1010 reuse templates |
| [candidate-f05-payload.md](candidate-f05-payload.md) | Vance candidate-f05 DataFlash-dump semantics, standard-payload diff, reset behavior, and provenance boundary |

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
in software. Its sole configured stock caller is a CAN-fed crypto-test bank;
stock application RoutineControl RID `0x100F` startRoutine activates bank 1 through wrapper
`0x8A782 -> crypto_test_bank1_activate @ 0x69018`. The stock bank compares the
result locally and is not a production SecOC transmit path. The earlier Stage-7
"no recovered activation edge" conclusion was corrected on 2026-08-13: its
direct-pointer census missed this one-hop RoutineControl wrapper. The active-state writer
census remains useful only for showing that CAN input alone cannot arm the bank.
Separately, the initialized application exposes serialized
command-5 plumbing suitable for a foreground signing proxy. Live slot-4
command-5 permission and performance remain dynamic.

For existing-key recovery, the best overall lead remains a weaker same-vehicle
producer ECU. The next direct step is now explicitly software-first: recovered
gate material can construct an authenticated 4 KiB bootloader callback, and the
existing CAN-dump payloads leave more than `0xE00` bytes for a direct ICU-S
command/status experiment. A negative bootloader-context result does not close
application lifecycle behavior; the same trust chain can in principle install a
restorable application hook because boot validity is CRC/marker consistency, not
a signature.

Command 13's exact Renesas opcode semantics remain unresolved, but its value for
standard SHE key extraction is now sharply bounded. SHE exposes only a
caller-loaded volatile `RAM_KEY`; its export primitive is RAM_KEY-only and
provides no nonvolatile-key copy/export operation, so the former
`slot 4 -> RAM_KEY -> export` route is disproved under SHE (SECOC-025). A direct
command-13 experiment is therefore useful only to characterize a Renesas-specific
undocumented deviation, not as the default extraction path. Chosen-input
power/EM analysis remains a characterized fallback. See
[software-path-assessment.md](software-path-assessment.md) and
[key-recovery-assessment.md](key-recovery-assessment.md).
