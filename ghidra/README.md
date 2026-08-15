# Ghidra integration

This directory contains **both vendored upstream projects and repository-owned
analysis scripts**. They have different maintenance rules.

## Vendored components

| Path | Role |
|---|---|
| `ghidra-cli/` | Vendored/forked Rust Ghidra CLI |
| `ghidra_v850/` | Vendored/forked V850/RH850 processor module |
| `ghidra-findcrypt/` | Vendored/forked findcrypt database/tooling |

Each vendored tree carries provenance metadata. Treat changes there as vendor
fork maintenance, not ordinary analysis-script edits. Build outputs remain
untracked/ignored.

## Repository-owned scripts

`ghidra/scripts/` is ours and is organized by lifecycle role:

- `import/` — project/memory-map import;
- `seed/` — structural function/table seeds;
- `annotate/` — durable names/comments/types;
- `investigate/` — exploratory/manual analysis helpers;
- `verify/` — deterministic exporters/asserting audits.

Persistent project annotations should be represented in the appropriate seed or
annotation script before promotion to the committed `project/` snapshot.

For safe project operation, rebuild stages, and the daemon durability rules, see
[`../docs/WORKFLOW.md`](../docs/WORKFLOW.md).
