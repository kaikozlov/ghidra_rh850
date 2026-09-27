# Documentation map

Start with the task below. The repository contains operating guides, evolving
target reports, and historical evidence; **a file's directory does not certify
that every paragraph is current**.

## Find the right entry point

| Task | Read |
|---|---|
| Understand repository scope and evidence | [OVERVIEW.md](OVERVIEW.md) |
| Install tools, select a target, use Ghidra, or verify a change | [WORKFLOW.md](WORKFLOW.md) |
| Find a command or artifact producer | [Tooling](tooling/README.md) |
| Find a calibration or vehicle report | [Variants](variants/README.md) |
| Review Camry capability and qualification boundaries | [Capability matrix](variants/camry-2026-capability-matrix.md) |
| Understand normal openpilot ownership | [Porting contract](architecture/toyota-openpilot-porting-contract.md) |
| Choose the next investigation | [Priorities](status/PRIORITIES.md) |
| Find an earlier claim, question, or correction | [Status reference](status/README.md), or `tools/know QUERY` |

## Reading reports without mixing checkpoints

1. Check the **target, software revision, capture date, and evidence source**.
   Sienna reference findings do not silently transfer to the default Camry.
2. Use the report's conclusion and stated supersessions. Long Camry/Corolla
   reports preserve dated investigations; “current” inside an old checkpoint
   refers to that checkpoint, not today's installation.
3. Follow the actual evidence. Generated artifacts are regenerated, not
   hand-edited; `build/` and `REFERENCE/` material is local context, not portable
   authority.
4. Keep successful software checks, observed vehicle behavior, and outstanding
   qualification separate. Historical integration audits are not deployment
   instructions or a claim about current upstream support.

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

## Status and history

| Document | Meaning |
|---|---|
| [PRIORITIES.md](status/PRIORITIES.md) | Short execution queue, not a completion diary |
| [FINDINGS.md](status/FINDINGS.md) | Claim IDs, evidence grades, and links; not a complete or always-current status mirror |
| [OPEN_QUESTIONS.md](status/OPEN_QUESTIONS.md) | Reference questions and recorded closure boundaries; owning reports may be newer |
| [CORRECTIONS.md](status/CORRECTIONS.md) | Prior interpretations retained so mistakes are not repeated |
| [ANALYSIS_STATUS.md](status/ANALYSIS_STATUS.md) | Historical Sienna coverage snapshot, not whole-project progress |
| [history/](history/README.md) | Dated investigation journals and migrations |

Historical sections also remain inside variant and subsystem reports where
their provenance is useful. Retain observations and source identities; correct
their interpretation in the owning report rather than rewriting a capture.

## Maintaining this documentation

Keep each conclusion in its existing target/subsystem report and link to it
from indexes. Update operating instructions when commands or ownership change.
Do not duplicate runtime state across README, overview, priorities, and several
reports, or turn every research update into a required ledger transaction.

For firmware questions, inspect the exact target bytes/decompilation first.
For integration design, consult current upstream and the porting contract.
Documentation-only changes do not require tests; exercise changed command
examples and check navigation where applicable.
