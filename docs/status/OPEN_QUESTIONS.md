# Open questions

Unresolved questions only. Once resolved, findings move to
[FINDINGS.md](FINDINGS.md) (with their evidence grade) and any superseded
prior claim moves to [CORRECTIONS.md](CORRECTIONS.md).

## Bootloader

- **Payload provenance.** The two pinned public payload fixtures verify the
  gate, but the original payload-generation toolchain (who built them, against
  which secret distribution) is not established.
- **Bootloader DID `0203` semantics.** It ignores its five bytes and only arms
  state 0 → 1. Whether any field ever carried meaning in other calibrations is
  unknown.

## Application

- **`0xAB` service purpose.** Bounded: 13 RID callbacks traced, no direct
  crypto/NvM/SecOC references found. 'Calibration/flash control' remains a
  **hypothesis**, not proven. Indirect calls through wrappers or
  GP-displacement RAM access not yet traced remain a residual possibility.
- **97 configured-unresolved RX signals** (see `data/application_rx_signal_evidence.csv`).
  Bounds are known; exact runtime producers are not statically recovered.
- **Three configured TX signals without recovered runtime producers** (see
  [../communications/application-tx.md](../communications/application-tx.md)).
- **Motor-control calibration handlers.** Large OEM motor-control functions
  (`0x47C3C`, `0x32B80`, `0xB98BC` cluster) are mapped structurally but not
  behaviorally understood.

## SecOC

- **Live slot-4 behavior.** Static CodeFlash proves slot-4 verification but
  cannot determine the donor's protected key state because the `FF*16` KAT is
  compiled out. The recovered command-5 generation family still requires a
  dynamic slot-4 permission and generate/verify round-trip test. Dealer rekey
  and ICU-S reservation contents in pages 480–511 also remain unknown. The
  experiment is
  specified in
  [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).
- **Object-15 producer.** No static producer exists in this calibration.
  Where a provisioned unit writes object 15 from is unknown (dealer tool path
  hypothesis only).

## Variants

- **Corolla `8965F1208000`.** Essentially everything: MCU confirmation, SA
  levels, secret location, payload format, diagnostic endpoints, SecOC
  profile. See [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md).
- **TSS 3.0 family breadth.** Which Sienna findings generalize across the
  family (Camry, RAV4, etc.) is unmapped. See
  [../variants/tss3-family-comparison.md](../variants/tss3-family-comparison.md).

## Tooling

- **Semantic coverage.** 5,852 functions recovered; most remain evidence-grade
  `recovered` rather than behaviorally understood. Closing this is a
  long-tail effort, not a single task.
