# Variants

Sienna `8965B4512000` is the primary analyzed calibration. Related variants do
not inherit its findings automatically: each transfer remains a hypothesis until
checked against that variant's own evidence. The tracked 2023-Corolla
`8965H1202000` CodeFlash is now the first exact foreign image used for such
checks; Span's `8965F1208000` now has a persisted corpus, while `8965B4514000` and the wider TSS 3.0 family keep
their own narrower evidence boundaries.

| Variant | Firmware | Status | Report |
|---|---|---|---|
| Sienna (China) | `8965B4512000` | Fully analyzed (this repo) | [sienna-8965B4512000.md](sienna-8965B4512000.md) |
| Sienna (Vance partner) | `8965B4514000` | External field report pinned; firmware/raw outputs unavailable | [sienna-8965B4514000.md](sienna-8965B4514000.md) |
| Corolla | `8965F1208000` | Field probes + persisted 2026-08-21 full memory corpus; comparative static application analysis closed against `8965H1202000` and Sienna, low calibration/hardware-only questions bounded | [corolla-8965F1208000.md](corolla-8965F1208000.md) |
| Corolla (reported 2023 US / albinoelephant) | `8965H1202000` / `8A3111202000` from tracked CodeFlash live-ID blocks | Complete memory corpus retained; first foreign Gate/runtime resolver regression; queue `00F/D7/B6` has no `2E4/131`; app/boot CAN1 continuity and async PROGRAMMING handoff verified; Toyota-B pin-swap function bounded against official harness topology; direct UDS F181 transcript still absent | [corolla-2023-us-public-route.md](corolla-2023-us-public-route.md) |
| RAV4 Prime (2024 field experiments) | exact F181 pending | Earlier failure statically bounded; 2026-08-16 corrected compare-neutralization externally reported with ~1.5 days working lateral; strict MAC28-only proof still pending | [rav4-prime-forced-secoc-profile.md](rav4-prime-forced-secoc-profile.md) |
| TSS 3.0 family | various | Partial comparison matrix | [tss3-family-comparison.md](tss3-family-comparison.md) |
| Newer TSK target | exact part pending | Artifact/capture contract only; all transfer claims remain hypothesis | [newer-tsk-target-evidence.md](newer-tsk-target-evidence.md) |

## The transfer rule

Matching application DID/service tables in a related EPS are strong
software-family evidence. They do **not** prove the related MCU, byte-identical
bootloader contents, retained secrets/payload routines, or that a PROGRAMMING
timeout must be external to the EPS. Every transferred claim starts at grade
**hypothesis** until checked against the variant's own bytes.

The machine-readable comparison data lives in
`data/tss3_eps_variant_matrix.csv`.
