# Project overview

This is the scope and evidence model for the Toyota/Denso RH850 analysis
repository. Use the [documentation map](README.md) for navigation,
[WORKFLOW.md](WORKFLOW.md) for commands, and
[variant reports](variants/README.md) for technical conclusions. This page does
not duplicate the changing integration checkpoint.

## What is maintained here

- Exact firmware inputs and target-specific Ghidra snapshots and decompiler
  corpora.
- Reproducible analysis of firmware, Toyota GTS+/Techstream software, and
  retained vehicle captures.
- Curated evidence tables, generated reports, and narrowly selected
  verification.
- Openpilot integration research, including dated experiments and their
  limitations. The openpilot/opendbc implementation lives in separate
  repositories; a revision quoted here is the revision used for that result.

The primary/default registered target is **2026 Camry Hybrid EPS
`8965F3307000`**. Crown and both Corolla specimens have independent registered
inputs. Sienna `8965B4512000` remains the legacy reference for much of the
low-level research. Its addresses, signal meanings, and conclusions do not
become Camry facts because it was analyzed first.

The authoritative registry is
[data/analysis_targets.json](../data/analysis_targets.json). It distinguishes
registered full analysis targets from partial images and external observations.
The [variant index](variants/README.md) routes each specimen to its own report
and explains the historical Corolla naming.

## Where the current questions belong

| Question | Owner |
|---|---|
| What does the maintained Camry port implement and use? | [Capability matrix](variants/camry-2026-capability-matrix.md) |
| What supports vehicle-state and field observations? | [Evidence review](variants/camry-2026-port-evidence-review.md) and [field baseline](variants/camry-2026-live-baseline.md) |
| What is the integration design contract? | [Native openpilot ownership](architecture/toyota-openpilot-porting-contract.md) |
| What is the target-specific longitudinal evidence? | [Longitudinal report](variants/camry-2026-longitudinal-evidence.md) |
| What is the next investigation? | [Priorities](status/PRIORITIES.md) |
| What was established for Sienna? | [Sienna reference overview](variants/sienna-8965B4512000-overview.md) and scoped subsystem reports |

The capability matrix records the maintained implementation and its source
identities.

## Evidence boundaries

For firmware facts, the order is firmware bytes and deterministic verification,
generated artifacts, curated evidence tables, annotated projects, then
narrative documentation. A decompilation helps explain a path; disassembly,
bytes, and dataflow are the proof. A capture establishes an observation only
for its recorded vehicle, software, harness, and operating state.

For openpilot design, start from current upstream openpilot/opendbc/Panda.
Firmware establishes target-specific constraints.

## Evidence model

Record evidence source separately from confidence. A field observation and a
firmware reconstruction answer different questions.

| Source | Meaning |
|---|---|
| **firmware-static** | Recovered from committed firmware bytes |
| **dynamic-probe** | Observed on a live vehicle or bus |
| **generated-artifact** | Produced by a tracked generator from identified inputs |
| **external-source** | Attributed to an outside document, report, or third party |

| Grade | Meaning |
|---|---|
| **verified** | The stated behavior or invariant is asserted by a deterministic test |
| **observed** | Directly observed within the recorded target and operating conditions |
| **recovered** | Control/data flow reconstructed to the stated extent |
| **bounded** | Evidence constrains the interpretation; specified semantics remain unknown |
| **hypothesis** | Plausible and explicitly unverified |

The variant CSV's `definitive`, `inference`, and `none` grades summarize rows.
Individual fields retain their own source and confidence in the target report;
an observed software identity does not establish an inferred MCU identity.
Keep unresolved questions beside the evidence in their owning report. Replace
disproved conclusions there rather than preserving a separate error ledger.

## Working state is not evidence

Committed projects use non-openable snapshot names under `projects/<target>/`.
Interactive analysis uses registered `build/work/` paths. Generated material
under `build/` and local references under `REFERENCE/` are not portable inputs;
promote required evidence deliberately and preserve its scope.

See [WORKFLOW.md](WORKFLOW.md) for safe project materialization, durable edits,
rebuilds, explicit verification, and snapshot promotion.
