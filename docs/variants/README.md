# Variants

Sienna `8965B4512000` is the primary analyzed calibration. Related variants do
not inherit its findings automatically: each transfer remains a hypothesis until
checked against that variant's own evidence. The tracked 2023-Corolla corpus historically labelled `8965H1202000` is now
the first exact foreign image used for such checks; its later direct application
F181 is `8965F1208000/8A3111202000`, while `8965H1202000` belongs to the
auxiliary DID-2032 identity. Span's distinct physical `8965F1208000` specimen has
a persisted corpus with secondary F181 `8A3111213000`; `8965B4514000` and the
wider TSS 3.0 family keep their own narrower evidence boundaries.

| Variant | Firmware | Status | Report |
|---|---|---|---|
| Sienna (China) | `8965B4512000` | Fully analyzed (this repo) | [sienna-8965B4512000.md](sienna-8965B4512000.md) |
| Sienna (Vance partner) | `8965B4514000` | External field report pinned; firmware/raw outputs unavailable | [sienna-8965B4514000.md](sienna-8965B4514000.md) |
| Corolla | `8965F1208000` | Field probes + persisted 2026-08-21 full memory corpus; comparative static application analysis closed against `8965H1202000` and Sienna; active `0xA000` unit calibration closed, structured shadow/hardware-only questions bounded | [corolla-8965F1208000.md](corolla-8965F1208000.md) |
| Corolla (reported 2023 US / albinoelephant) | direct app F181 `8965F1208000` / `8A3111202000`; auxiliary DID2032 `8965H1202000` | Complete memory corpus + same-car eps-telescope probe retained; direct F181/MCU/live Gate-2/boot-RAM-exec joins verified; queue `00F/D7/B6` has no `2E4/131`; app/boot CAN1 continuity and async PROGRAMMING handoff verified | [corolla-2023-us-public-route.md](corolla-2023-us-public-route.md) |
| Camry (first-class maintainer target) | EPS F181 `8965F3307000` / `8A3113303100`; exact 1-MiB CodeFlash SHA-256 `42dce8ef…d9b0e7`; canonical 6,065-function Ghidra corpus; FRC `8646F3315000`; Brake/EPB `F152633K0000` | First-class firmware/DataFlash/project snapshot with two-build inventory parity; target-native B6/SecOC receiver, timing, limits, Ready/gear/cruise state and authenticated boot RAM path closed; `FEBFF9F0..FEBFFBFB` is live-proven retained/executable; application XCP can statically place arbitrary bytes there, while non-disruptive application-mode control transfer remains the signer-loader blocker | [camry-2026-live-baseline.md](camry-2026-live-baseline.md) |
| Camry F33 TSS3 fault/status contract | `8965F3307000` | Exact target-native `0x394` classifier/DEM/DTC/aging closure; openpilot temp/permanent mapping remains live-policy bounded | [camry-2026-tss3-fault-status.md](camry-2026-tss3-fault-status.md) |
| Camry openpilot integration (completion plan deliverables) | software revisions pinned in-doc | WP2 replay audit + field contract (recorded vs proposed CarState on identical September input); WP3 bench-validation specification and interface inventory; WP4 longitudinal evidence matrix (`0x160`/B12 hypothesis); WP6 capability matrix and qualification handoff | [camry-2026-tss3-integration-audit.md](camry-2026-tss3-integration-audit.md) · [camry-2026-bench-validation-spec.md](camry-2026-bench-validation-spec.md) · [camry-2026-longitudinal-evidence.md](camry-2026-longitudinal-evidence.md) · [camry-2026-capability-matrix.md](camry-2026-capability-matrix.md) |
| RAV4 Prime (2024 field experiments) | exact F181 pending | Earlier failure statically bounded; 2026-08-16 corrected compare-neutralization externally reported with ~1.5 days working lateral; strict MAC28-only proof still pending | [rav4-prime-forced-secoc-profile.md](rav4-prime-forced-secoc-profile.md) |
| Toyota EPS security/control variants | various | Evidence-graded matrix with independent ADAS-generation and SecOC/TSK axes | [toyota-eps-variant-comparison.md](toyota-eps-variant-comparison.md) |
| Newer TSK target | exact part pending | Artifact/capture contract only; all transfer claims remain hypothesis | [newer-tsk-target-evidence.md](newer-tsk-target-evidence.md) |

For the control-interface migration specifically, see
[corolla-pre-tss3-openpilot-message-comparison.md](corolla-pre-tss3-openpilot-message-comparison.md).
It compares the exact message roles used by current pre-TSS3 Corolla openpilot
support against both tracked H/F applications and separates EPS-local migrations
from camera/ACC/UI roles that an EPS dump cannot resolve.

The deeper H/F state recovery is in
[corolla-h-f-openpilot-state-bridge.md](corolla-h-f-openpilot-state-bridge.md).
It recovers target-native `0x4A3`, `0x351`, and `0x394` state roles, reframes
`0x030`, and records the complete generated-COM command-ingress boundary.

## The transfer rule

Matching application DID/service tables in a related EPS are strong
software-family evidence. They do **not** prove the related MCU, byte-identical
bootloader contents, retained secrets/payload routines, or that a PROGRAMMING
timeout must be external to the EPS. Every transferred claim starts at grade
**hypothesis** until checked against the variant's own bytes.

The machine-readable comparison data lives in
`data/toyota_eps_variant_matrix.csv`.
