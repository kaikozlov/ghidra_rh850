# Documentation map

This directory is organized by **document role**, not by chronology. If a page
looks like a current-state source but is actually a dated investigation journal,
that is a documentation bug.

The firmware and deterministic tests remain authoritative. Documentation exists
to make the evidence legible.

## Read these first

1. **[OVERVIEW.md](OVERVIEW.md)** — the current technical picture.
2. **[status/PRIORITIES.md](status/PRIORITIES.md)** — the short execution queue.
3. **[status/README.md](status/README.md)** — how to use the live status ledgers.
4. **[WORKFLOW.md](WORKFLOW.md)** — how to operate the Ghidra/tooling stack.

If you are looking up one specific assertion, skip the prose and go straight to
[status/FINDINGS.md](status/FINDINGS.md). If you are following a lead, open question,
or the relationship between a finding, its canonical report, and the tests that
assert it, use the generated [reference/index.md](reference/index.md).

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

## Evidence vocabulary

Confidence grades are defined centrally in
[status/FINDINGS.md](status/FINDINGS.md#evidence-model):

- **verified** — directly asserted by a deterministic repository test;
- **observed** — directly observed dynamically/externally but not reproduced by
  a repository test;
- **recovered** — control/data flow substantially reconstructed;
- **bounded** — interpretation constrained but incomplete;
- **hypothesis** — plausible and explicitly unverified;
- **disproved** — retained to prevent the old claim from returning.

Evidence source and confidence are separate dimensions. A third-party field
observation can be genuinely observed while still not being a firmware-static
fact for `8965B4512000`.

## Canonical ownership rule

To keep this tree from becoming confusing again:

- subsystem reports own the detailed argument;
- `FINDINGS.md` owns the compact claim/evidence index;
- `OPEN_QUESTIONS.md` owns unresolved detail;
- `PRIORITIES.md` owns only the short execution queue;
- `OVERVIEW.md` summarizes and links;
- dated investigation narratives go to `history/`.

Do not copy multi-paragraph findings between documents. Link to the canonical
home instead.
