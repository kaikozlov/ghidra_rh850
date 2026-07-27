# Documentation

Ghidra analysis of the China-market Sienna EPS firmware (`8965B4512000`,
RH850/P1M-E R7F701381).

The single source of truth is the firmware itself. These reports are
explanations reconstructed from it; every material claim is either checked by
a deterministic test in `tests/` or explicitly marked with an evidence grade
(see [status/FINDINGS.md](status/FINDINGS.md)).

## Where to start

| I want to… | Go here |
|---|---|
| Get the ten-minute picture of the firmware | [OVERVIEW.md](OVERVIEW.md) |
| Open, verify, or rebuild the Ghidra project | [WORKFLOW.md](WORKFLOW.md) |
| Look up whether a specific claim is proven | [status/FINDINGS.md](status/FINDINGS.md) |
| See what is still unresolved | [status/OPEN_QUESTIONS.md](status/OPEN_QUESTIONS.md) |
| See which old conclusions were wrong, and why | [status/CORRECTIONS.md](status/CORRECTIONS.md) |

## Sections

| Section | Scope |
|---|---|
| [architecture/](architecture/README.md) | Boot flow, execution architecture, control/safety partition, system-mode cluster |
| [diagnostics/](diagnostics/README.md) | Application and bootloader UDS stacks, DID model |
| [security/](security/README.md) | Application SecurityAccess, bootloader payload gate, SecOC |
| [communications/](communications/README.md) | CAN/ISO-TP transport, application Rx/Tx maps |
| [storage/](storage/README.md) | DataFlash layout and NvM semantics |
| [variants/](variants/README.md) | Sienna vs. Corolla and the wider TSS 3 EPS family |
| [tooling/](tooling/README.md) | Processor-module audit and analysis tooling |
| [reference/](reference/README.md) | Generated artifacts and address reference |

## Evidence vocabulary

Every report carries an evidence grade in its header. The grades are defined in
[status/FINDINGS.md](status/FINDINGS.md#evidence-grades):

- **verified** — directly asserted by a deterministic test;
- **recovered** — control/data flow substantially reconstructed;
- **bounded** — interpretation constrained, exact semantics unknown;
- **hypothesis** — plausible, explicitly unverified;
- **disproved** — retained only to prevent regression.
