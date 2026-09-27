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
  repositories; a revision quoted here is the revision used for that result,
  not a claim about today's upstream or deployed software.

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
| What does the retained Camry evidence demonstrate, and what is still unqualified? | [Capability matrix](variants/camry-2026-capability-matrix.md) |
| How were those conclusions reached or corrected? | [Port evidence review](variants/camry-2026-port-evidence-review.md) and [field baseline](variants/camry-2026-live-baseline.md), read by checkpoint |
| What is the integration design contract? | [Native openpilot ownership](architecture/toyota-openpilot-porting-contract.md) |
| What is the target-specific longitudinal evidence? | [Longitudinal report](variants/camry-2026-longitudinal-evidence.md) |
| What is the next investigation? | [Priorities](status/PRIORITIES.md) |
| What was established for Sienna? | [Sienna reference overview](variants/sienna-8965B4512000-overview.md) and scoped subsystem reports |

The capability matrix distinguishes demonstrations, software validation, and
remaining qualification. Neither an older successful experiment nor an older
failure should be read as the status of every later configuration.

## Evidence boundaries

For firmware facts, the order is firmware bytes and deterministic verification,
generated artifacts, curated evidence tables, annotated projects, then
narrative documentation. A decompilation helps explain a path; disassembly,
bytes, and dataflow are the proof. A capture establishes an observation only
for its recorded vehicle, software, harness, and operating state.

For openpilot design, start from current upstream openpilot/opendbc/Panda.
Firmware establishes genuinely target-specific constraints, not a second
engagement or permission architecture.

Keep evidence source separate from confidence. The
[evidence model](status/FINDINGS.md#evidence-model) defines **verified**,
**observed**, **recovered**, **bounded**, **hypothesis**, and **disproved**.
Discovery counts, offline test results, field observations, and production
qualification are not interchangeable.

Status ledgers are lookup aids and may lag the owning reports.
[ANALYSIS_STATUS.md](status/ANALYSIS_STATUS.md) is a historical Sienna coverage
snapshot, not a current multi-target dashboard. Dated sections inside a
subsystem or variant report are historical checkpoints even when they are not
stored under `history/`.

## Working state is not evidence

Committed projects use non-openable snapshot names under `projects/<target>/`.
Interactive analysis uses registered `build/work/` paths. Generated material
under `build/` and local references under `REFERENCE/` are not portable inputs;
promote required evidence deliberately and preserve its scope.

See [WORKFLOW.md](WORKFLOW.md) for safe project materialization, durable edits,
rebuilds, explicit verification, and snapshot promotion.
