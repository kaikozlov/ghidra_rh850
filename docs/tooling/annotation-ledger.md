# Declarative Ghidra annotation ledger

Simple persistent Ghidra edits no longer need a one-off Java script. The tracked
`data/annotations/annotation_ledger.jsonl` ledger owns mechanical function
renames, data labels, and listing comments. `ghidra/scripts/annotate/ApplyAnnotationLedger.java`
applies the complete ledger as the final annotation operation in stage 4 of the
canonical rebuild.

This is deliberately narrow. Function creation/recovery, signatures, types,
overlays, table discovery, control-flow recovery, and any edit whose correctness
depends on program semantics still belong in purpose-built seed/annotation
scripts. The ledger removes transcription boilerplate; it does not replace those
scripts.

## Daily use

```bash
# Record a durable edit only.
tools/annotations add function 0x8db22 uds_security_access_handler \
  --comment 'SecurityAccess dispatcher.'
tools/annotations add label 0xfebef02a security_state
tools/annotations add comment 0x8db36 'Result gate.' --comment-type eol

# Validate/review the tracked recipe.
tools/annotations validate
tools/annotations list

# Replay the complete ledger into build/work/project and durably save it.
tools/annotations apply

# Or record + replay in one command.
tools/annotations add function 0x8db22 uds_security_access_handler --apply
```

`--apply` and `apply` always go through `tools/g`, then cleanly stop the bridge so
the working-copy edit is durable. The committed `project/` snapshot remains
non-openable and protected by the normal lifecycle guard. A
working-project replay is for the edit loop; the canonical proof remains a fresh
`make rebuild-project` followed by project-parity verification and normal
snapshot promotion.

## Ledger contract

The ledger is canonical JSONL. Addresses are normalized to lowercase 32-bit
`0x????????` form and records are sorted by address. The supported operations are:

- `function`: exact-entry function rename, with an optional listing comment.
- `label`: data label creation/rename, with an optional listing comment. A label
  record targeting a function entry is rejected by the Ghidra applier.
- `comment`: listing comment only.

Comment types are `eol`, `pre`, `post`, `plate`, and `repeatable`.
`tools/annotations` rejects unknown fields, malformed addresses, duplicate/conflicting symbol ownership, and
multiple writers for the same `(address, comment type)`. Writes are atomic and
adding an identical existing record is a no-op. `remove` edits the tracked recipe;
it does not attempt to undo an overlay already present in an open/materialized
working project. Use a fresh rebuild to prove removals and then promote that
result normally.

The Ghidra applier parses and preflights the complete ledger before making any
program mutation. This is intentional: the persistent Ghidra bridge owns an outer
transaction, so nested transaction rollback is not an isolation boundary. Missing
functions, invalid targets, symbol collisions, and unsupported operations are
therefore rejected during pass 1; pass 2 applies only a fully validated plan. `tools/rebuild_project.sh`
validates the tracked ledger before starting stage 4, then runs the applier after
the existing annotation and calling-convention scripts so these mechanical edits
cannot perturb discovery or analysis staging.
