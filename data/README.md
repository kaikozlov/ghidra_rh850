# Analysis data

Machine-readable evidence used by generators, tests, and subsystem reports.

There are two classes of files here:

1. **Generated artifacts** — reproducible outputs of repository tooling. Most
   newer/larger outputs live under `data/generated/`; some older generated CSVs
   remain at the top level because their paths are deeply integrated into tests
   and reports.
2. **Curated evidence tables** — hand-maintained mappings/dispositions whose
   rows are intentionally reviewed and verified by tests.

Do not infer authority from directory depth. The source-of-truth order is in
[`../AGENTS.md`](../AGENTS.md): firmware/tests first, then generated artifacts,
then curated tables, then the Ghidra snapshot and narrative docs.

## Finding the producer of a file

Use `tools/artifact list [query]` and `tools/artifact show ARTIFACT` for tracked
generated artifacts. The catalog derives producers/consumers from repository
source; generated files do not need a verification owner.

Examples of generated top-level compatibility paths include
`application_rx_map.csv`, `application_diagnostic_map.csv`, and
`semantic_coverage_ledger.csv`; moving them merely to make the directory look
purer would create large path churn without changing their evidence role.

`data/generated/` is the preferred destination for new derived artifacts unless
an existing subsystem convention requires a stable top-level data path.
