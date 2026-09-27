# Documentation map

Use the subsystem reports for conclusions, the status pages for navigation,
and `WORKFLOW.md` for commands. Firmware and captured observations are the
underlying evidence; tests check particular behaviors or binary facts.

## Read these first

1. **[OVERVIEW.md](OVERVIEW.md)** — the current technical picture.
2. **[status/PRIORITIES.md](status/PRIORITIES.md)** — the short execution queue.
3. **[status/README.md](status/README.md)** — how to use the live status ledgers.
4. **[WORKFLOW.md](WORKFLOW.md)** — how to operate the Ghidra/tooling stack.

If you are looking up prior research by ID or keyword, use `tools/know QUERY` or
read [status/FINDINGS.md](status/FINDINGS.md) directly. The status ledgers are
navigation/history aids; they are not required to mirror every report or test.

## Document classes

### Current orientation

| Document | Purpose |
|---|---|
| [OVERVIEW.md](OVERVIEW.md) | Human-scale summary of architecture, attack surface, exploit status, and current blockers |
| [WORKFLOW.md](WORKFLOW.md) | Project lifecycle, Ghidra durability rules, verification, and rebuild procedure |

### Live project status

Everything under [status/](status/README.md) is current unless explicitly
marked otherwise:

| Document | Use it for |
|---|---|
| [status/PRIORITIES.md](status/PRIORITIES.md) | What to do next, in priority order |
| [status/FINDINGS.md](status/FINDINGS.md) | Canonical claim IDs, scope, confidence, and verification |
| [status/OPEN_QUESTIONS.md](status/OPEN_QUESTIONS.md) | Exhaustive unresolved-question ledger |
| [status/ANALYSIS_STATUS.md](status/ANALYSIS_STATUS.md) | Coverage/denominator snapshot |
| [status/CORRECTIONS.md](status/CORRECTIONS.md) | Superseded or disproved prior claims |

### Canonical subsystem reports

A material conclusion should have exactly one canonical report in these trees:

| Section | Scope |
|---|---|
| [architecture/](architecture/README.md) | Boot/execution architecture, control partition, system modes |
| [communications/](communications/README.md) | CAN/ISO-TP, application Rx/Tx, XCP |
| [diagnostics/](diagnostics/README.md) | Bootloader/application UDS and configured service surfaces |
| [security/](security/README.md) | SecurityAccess, payload gate, memory safety, SecOC, provisioning |
| [storage/](storage/README.md) | DataFlash/NvM layout and semantics |
| [variants/](variants/README.md) | Cross-calibration/vehicle evidence and transfer boundaries |
| [tooling/](tooling/README.md) | Analysis, Techstream/RFP, cross-calibration, and acquisition tooling |
| [reference/](reference/README.md) | Address/artifact lookup tables |

### Historical research journals

[history/](history/README.md) contains dated investigation reports. They are
useful for chronology, methodology, and why a correction happened, but **they
are not the place to determine current project state**. Current conclusions
must be taken from the live status ledgers and canonical subsystem reports.

Confidence grades are defined in
[status/FINDINGS.md](status/FINDINGS.md#evidence-model).
Keep detailed conclusions in the relevant subsystem report and link to them
from status pages rather than copying the argument.
