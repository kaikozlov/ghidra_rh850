# Variant and target reports

Use this index to select evidence for a **specific specimen or calibration**.
Registry roles describe analysis ownership.

## Registered analysis targets

`tools/gtarget list` and
[data/analysis_targets.json](../../data/analysis_targets.json) are authoritative
for target IDs, images, snapshots, corpora, and working paths.

| Target | Role / specimen | Report |
|---|---|---|
| `camry-8965F3307000` | Primary/default; maintainer's 2026 Camry Hybrid | [Capability matrix](camry-2026-capability-matrix.md) · [field evidence](camry-2026-live-baseline.md) |
| `crown-8965F3012000` | First-class; mruno's reported 2024 Crown Limited | [Crown report](crown-8965F3012000.md) |
| `corolla-8965F1208000` | First-class; Span's reported 2025 Corolla | [Corolla F report](corolla-8965F1208000.md) |
| `corolla-8965H1202000` | First-class; albinoelephant's reported 2023 US Corolla; historical auxiliary-identity label | [Corpus and public-route report](corolla-2023-us-public-route.md) |
| `sienna-8965B4512000` | Legacy deep-reference calibration | [Sienna report](sienna-8965B4512000.md) · [reference overview](sienna-8965B4512000-overview.md) |

**Corolla identity trap:** both retained specimens report primary application
F181 `8965F1208000`. Their secondary records differ: `8A3111202000` for
albinoelephant and `8A3111213000` for Span. The former registry ID retains the
historical `8965H1202000` auxiliary identity. Do not merge these specimens or
rename their source evidence based on the shared primary string.

## Camry evidence owners

| Question | Report |
|---|---|
| What does the maintained port implement and use? | [Capability matrix](camry-2026-capability-matrix.md) |
| What supports vehicle-model, radar, fault and cancellation interpretations? | [Evidence review](camry-2026-port-evidence-review.md) |
| Where are the dated field observations? | [Live baseline](camry-2026-live-baseline.md) · [bounty evidence](toyota-tss3-openpilot-bounty-evidence.md) |
| How does the port integrate, and what do native request/state captures show? | [Port report](camry-2026-tss3-opendbc-port.md) |
| What does the longitudinal evidence establish? | [Longitudinal report](camry-2026-longitudinal-evidence.md) |
| What does the exact EPS publish? | [EPS transmit report](camry-f33-eps-tx.md) |
| How are fault observations bounded? | [Fault/status report](camry-2026-tss3-fault-status.md) |
| What is the normal software ownership contract? | [Native openpilot contract](../architecture/toyota-openpilot-porting-contract.md) |

Capture and recovery reports retain their rack, software, harness and date.

## Corolla comparison and qualification

- [Pre-TSS3 interface comparison](corolla-pre-tss3-openpilot-message-comparison.md)
  separates EPS-local behavior from camera, cruise, and UI roles.
- [H/F state bridge](corolla-h-f-openpilot-state-bridge.md) owns the
  calibration-specific state analysis.
- [September-16 offline audit](corolla-tss3-offline-audit-2026-09-16.md) and
  [tester-handoff audit](corolla-tss3-tester-handoff-audit-2026-09-16.md) are
  revision-bound reviews.

## Other evidence outside the registered full analysis targets

| Evidence | Scope / report |
|---|---|
| Sienna `8965B4514000` | [External field report](sienna-8965B4514000.md) |
| Tundra `8965F3401200` | [Partial application-image provenance](../../firmware/tundra-8965F3401200/README.md) |
| TSS3 Front Recognition Camera | [Acquisition and evidence boundaries](tss3-frc-firmware-acquisition.md) |
| RAV4 Prime | [Historical field experiments](rav4-prime-forced-secoc-profile.md) |
| Venza airbag sensor | [September-14 specimen report](yc-venza-airbag-reprogramming-2026-09-14.md) |
| Newer TSK target | [Evidence contract](newer-tsk-target-evidence.md) |
| Cross-vehicle comparison | [Evidence-graded comparison](toyota-eps-variant-comparison.md) and `data/toyota_eps_variant_matrix.csv` |

