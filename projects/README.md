# Committed Ghidra snapshots

`projects/<target>/` is the single committed namespace for packed Ghidra
snapshots. Every target, including the legacy Sienna reference, uses the same
layout.

These trees are deliberately stored under non-openable `.gpr.snapshot` /
`.rep.snapshot` names. Never point Ghidra, `analyzeHeadless`, or `tools/g` at the
committed `projects/` namespace. Materialize a disposable working copy with
`make work-project [TARGET=<target>]`; target identity, priority, snapshot paths,
and working paths are defined by `data/analysis_targets.json`.

The registry default is the 2026 Camry F33 target. Use `tools/gtarget list` to see
all registered targets and `tools/gtarget <target> ...` for an explicit one.
