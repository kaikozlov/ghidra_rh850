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
generated artifacts. The catalog covers tracked files under `data/generated/`
and derives producers/consumers from repository source; those files do not need
a verification owner.

Some top-level CSVs are generated through `make` targets rather than the
artifact catalog: `make generate-dataflash` rewrites `dataflash_nvm_records.csv`
and `checkpoint_payload_map.csv`, `make generate-application-receive` rewrites
`application_rx_map.csv`, `make generate-application-diagnostics` rewrites
`application_diagnostic_map.csv`, and `make generate-semantic-coverage`
rewrites `semantic_coverage_ledger.csv`. Other top-level tables are curated:
do not overwrite them as though every CSV were a generator output. Their
placement alone does not determine their evidence role.

`data/generated/` is the preferred destination for new derived artifacts unless
an existing subsystem convention requires a stable top-level data path.
