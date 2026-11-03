# Documentation map

Start with the task below. Target and subsystem reports own current conclusions;
captures and cited source revisions establish the scope of their evidence.

## Find the right entry point

| Task | Read |
|---|---|
| Understand repository scope and evidence | [OVERVIEW.md](OVERVIEW.md) |
| Install tools, select a target, use Ghidra, or verify a change | [WORKFLOW.md](WORKFLOW.md) |
| Build or package a registered RAM-resident TSS3 runtime | [RAM-resident TSS3 workflow](WORKFLOW.md#ram-resident-tss3-build-and-kit-workflow) |
| Find a command or artifact producer | [Tooling](tooling/README.md) |
| Find a calibration or vehicle report | [Variants](variants/README.md) |
| Find the current Camry port and its evidence | [Capability matrix](variants/camry-2026-capability-matrix.md) |
| Understand normal openpilot ownership | [Porting contract](architecture/toyota-openpilot-porting-contract.md) |
| Choose the next investigation | [Priorities](status/PRIORITIES.md) |
| Locate a conclusion, evidence source, or open question | The owning target/subsystem report, or `tools/know QUERY` |

## Reading evidence

1. Check the **target, software revision, capture date, and evidence source**.
2. Use the owning report for the conclusion and its unresolved questions.
3. Follow the actual evidence. Regenerate artifacts from their inputs;
   `build/` and `REFERENCE/` are local context, not portable evidence.
4. Keep software checks, capture measurements and attributed use distinct.

## Subsystem reports

| Section | Scope |
|---|---|
| [architecture/](architecture/README.md) | Boot/execution, control partition, system modes, integration contracts |
| [communications/](communications/README.md) | CAN/ISO-TP and target-specific application Rx/Tx |
| [diagnostics/](diagnostics/README.md) | Separate bootloader/application diagnostic surfaces |
| [security/](security/README.md) | Security analysis and its target-specific evidence boundaries |
| [storage/](storage/README.md) | DataFlash/NvM layout and semantics |
| [variants/](variants/README.md) | Calibration-specific conclusions and cross-target transfer limits |
| [tooling/](tooling/README.md) | Operating interfaces and software-analysis reports |
| [reference/](reference/README.md) | Address and artifact lookup tables |

These sections include legacy Sienna reference material as well as newer
multi-target reports. Their indexes identify that distinction.

## Current work and evidence

[PRIORITIES.md](status/PRIORITIES.md) is the execution queue.
The [evidence model](OVERVIEW.md#evidence-model) defines source and confidence.
Keep useful observations and source identities in their owning reports.
Delete superseded documents after integrating unique current material and
repairing their references. Git preserves change history.

## Maintaining this documentation

Keep each conclusion in its existing target/subsystem report and link to it
from indexes. Update operating instructions when commands or ownership change.
Do not duplicate runtime state across README, overview, priorities, and several
reports, or turn every research update into a required ledger transaction.

For firmware questions, inspect the exact target bytes/decompilation first.
For integration design, consult current upstream and the porting contract.
Documentation-only changes do not require tests; exercise changed command
examples and check navigation where applicable.
