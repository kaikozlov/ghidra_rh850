# Ghidra 12.1.4 migration — 2026-09-21

## Scope

Homebrew advanced the supported local Ghidra installation from 12.1.3 to
12.1.4. The repository moved the complete fail-closed execution boundary:
environment/cache guards, isolated extension paths, CI assertions, extension
metadata and provenance, every registered project snapshot, normalized
inventories, and persistent decompiler corpora. The vendored `ghidra-cli` pin
remains 0.2.1.

## Extension compatibility

The vendored RH850 SLEIGH sources compile under 12.1.4 to the same `v850e3.sla`
as 12.1.3:

```text
SHA-256 3501f46e4e60c0be94fbecd06090c08c004cde141085546db1eccb884c9c4bf8
```

The new full processor source fingerprint, including 12.1.4 extension metadata,
is `a8f9538abf0b4fbab1655bcc3d641caf58d69aaf179bf6582de8753e7f55413f`.

GhidraFindcrypt v3.1.9 was rebuilt from pinned upstream commit
`fcaa49e545b131e2cc631168c6c168c1aec862a6`. The 12.1.4 package hash is
`c10023384658968dee94ccc24fd5f9e1ee75088ddd2b7264d71e53ad4e236391`.
Its analyzer JAR and database remain byte-identical to the prior package:

```text
GhidraFindcrypt.jar  dc2e395b6dac463ed9191465ce43d5c6cea5002851515b06f0167c5464ee3aa3
database.json        8f7bdbc5f9bbe48a4ed93792adab67fca6f103384165ed1917d883870ee6f471
```

The `ghidra-cli` 0.2.1 doctor also compiles its bridge successfully against
Ghidra 12.1.4 and JDK 27.

## Independent rebuild proof

Every registered target received two independent clean four-stage rebuilds:

| Target | Functions | Inventory result |
|---|---:|---|
| Camry `8965F3307000` | 6,065 | byte-identical pair |
| Crown `8965F3012000` | 5,874 | byte-identical pair |
| Corolla `8965F1208000` | 5,811 | byte-identical pair |
| Corolla `8965H1202000` | 5,811 | byte-identical pair |
| Sienna `8965B4512000` | 6,376 | byte-identical pair |

For all five targets, comparison with the 12.1.3 normalized inventory changes
only the `ghidra_version` metadata field. Sienna retains 183,240 instructions,
38,842 symbols, 14 memory sections, and the 1,376,576-byte mapped size.

The regenerated corpora contain 29,937 total function records and zero
decompilation failures. Every function/decompilation/reference-graph record is
byte-identical to its prior canonical record; only corpus metadata changed.
The first Corolla-F rebuild assigned operand index 2 rather than 0 to one
otherwise-identical `PARAM` reference at `0x4348e`. The second independent
rebuild reproduced the prior canonical index 0 on two consecutive exports, so
that parity-preserving rebuild was promoted. This is bounded rebuild-order
variation, not a firmware or decompiler-semantic change.

## Lifecycle correction

The migration exposed daemon checks that matched only the common project name.
Unrelated Ghidra projects can also be named `rh850_p1me_mapped`, so rebuild and
snapshot lifecycle checks now bind both the canonical project path and project
name. This preserves the fail-closed promotion rule without stopping or
blocking on unrelated Ghidra sessions.

## Verification

- isolated SLEIGH compile and language-resolution gate passed;
- `ghidra-cli` doctor passed against 12.1.4;
- lifecycle, FindCrypt, and persistent decompiler-corpus suites passed;
- all 21 synthetic processor cases passed;
- the full Sienna processor/project semantic audit passed;
- exact normalized project parity passed for all five registered targets.
