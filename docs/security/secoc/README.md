# SecOC

Runtime CAN authentication and ICU-S behavior for the Sienna
`8965B4512000` application.

## Current state in one page

Six receive profiles are SecOC-protected through **ICU-S slot 4**. Command 7 is
the recovered verification primitive; command 5 is the paired MAC-generation
primitive. The application contains stock command-5 test plumbing and two
separate command-8 authenticated-update clients, but no recovered production
SecOC transmit path.

What is established:

- protected receive IDs are `0x00F`, `0x2E4`, `0x131`, `0x132`, `0x090`, and
  `0x0D7`, with downstream roles individually classified;
- freshness/synchronization and classic sender construction are recovered;
- slot 4 is used for verification;
- stock RID `0x100F` activates the command-5 bank-1 test path;
- command-5 terminal failure/mismatch state has a no-SA DTC side channel, but
  the generated 16-byte result remains private without the bounded observation
  patch;
- RID `0x1010` carries a 64-byte SHE-shaped command-8 request and 48-byte
  result;
- RID `0x100E` arms a second command-8 client assembled from CAN
  `0x13..0x1A`;
- the two command-8 clients share a completion-attribution bug (SECOC-048),
  which can produce false diagnostic success but **does not bypass ICU-S
  package authentication**;
- object 15 and the compiled-out `FF*16` KAT do not establish the live slot-4
  key in this dump.

The highest-value remaining direct question is dynamic: **does live slot 4
permit command 5 generation, and at what latency under normal command-7 load?**
See [../../status/PRIORITIES.md](../../status/PRIORITIES.md).

## Reports

| Report | Canonical scope |
|---|---|
| [application-chain.md](application-chain.md) | Six receive profiles, freshness, command-7 verification, crypto-test banks, command-8 composition |
| [sender-implementation.md](sender-implementation.md) | Classic sender/freshness construction and minimum application-resident signing-proxy architecture |
| [software-path-assessment.md](software-path-assessment.md) | Software attack surface, command-5/8 experiments, diagnostic/XCP intersections |
| [key-storage-and-lifecycle.md](key-storage-and-lifecycle.md) | NvM/object-15 model, ICU-S lifecycle, command-8 provisioning semantics |
| [key-recovery-assessment.md](key-recovery-assessment.md) | Existing-key recovery routes and their evidence boundaries |
| [candidate-f05-payload.md](candidate-f05-payload.md) | Vance candidate-f05 DataFlash-dump payload semantics/provenance |

## Important boundaries

- The old proposed `0x65CD8 → 0x66E48 → 0x67590 → 0x72F58` “runtime-key” path
  was wrong; it is generic NvM/checkpoint machinery. See
  [../../status/CORRECTIONS.md](../../status/CORRECTIONS.md).
- A command-8 submission path is **not** a raw-key-write primitive. ICU-S still
  authenticates AuthID/counter/M3 and keeps plaintext key material outside the
  CPU-visible MainPE path.
- Standard SHE does not provide a nonvolatile-slot export route through command
  13/RAM_KEY; a Renesas-specific deviation remains only a lower-priority
  hardware question.
- Findings from `8965B4514000`, Corolla, F3/F4, or other TSS3 targets are not
  facts about this calibration unless separately validated.

For claim IDs and confidence grades, use
[../../status/FINDINGS.md](../../status/FINDINGS.md). For all unresolved details,
use [../../status/OPEN_QUESTIONS.md](../../status/OPEN_QUESTIONS.md).
