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
- `investigate/` — exploratory/manual analysis helpers; excluded from the
  canonical `tools/project/run_headless` script path by default (measured to
  change the recovered graph), opt back in with `--with-investigate` only for
  one-off investigations;
- `verify/` — deterministic exporters/asserting audits.

Mechanical function renames, data labels, and listing comments do not need a
new Java class: the tracked `data/annotations/annotation_ledger.jsonl` ledger,
curated through `tools/annotations`, is replayed by `ApplyAnnotationLedger.java`
during the legacy Sienna rebuild. Persistent semantic annotations beyond the
ledger's scope belong in the appropriate seed or annotation script before
promotion to the committed `projects/<target>/` snapshot.

For safe project operation, rebuild stages, and the daemon durability rules, see
[`../docs/WORKFLOW.md`](../docs/WORKFLOW.md).
