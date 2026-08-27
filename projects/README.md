# First-class non-default Ghidra snapshots

`projects/` contains packed, **non-openable** committed Ghidra snapshots for
first-class analysis targets other than the legacy primary Sienna snapshot in
`project/`. Never point Ghidra or `analyzeHeadless` at these committed trees.
Materialize a working copy with `make work-project TARGET=<target>` and promote a
verified copy with `make snapshot-project TARGET=<target>`. Target identity and
paths are defined by `data/analysis_targets.json`.
