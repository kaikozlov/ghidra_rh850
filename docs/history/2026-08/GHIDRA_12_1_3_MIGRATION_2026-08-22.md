# Ghidra 12.1.3 migration — 2026-08-22

## Scope

The repository was pinned to Ghidra 12.1.2 while the supported local/Homebrew
installation had advanced to 12.1.3. This migration updates the complete Ghidra
execution boundary rather than relaxing one version check: CI, isolated user
home, processor extension metadata/fingerprint, FindCrypt packaging, project
snapshot provenance, normalized project inventory, and the persistent
decompiler corpus all move together.

The ghidra-cli pin remains 0.2.1.

## Processor compatibility

The vendored RH850/v850 SLEIGH sources were compiled independently under Ghidra
12.1.3. The resulting `v850e3.sla` is byte-identical to the 12.1.2 build:

```text
SHA-256 3501f46e4e60c0be94fbecd06090c08c004cde141085546db1eccb884c9c4bf8
```

The processor source fingerprint changes because the extension/provenance
metadata now declares Ghidra 12.1.3. The 12.1.3 manifest fingerprint is:

```text
6ffb84ef6cb5778d2c6242ce693c9c02ea1eab0d9f058f3cdc1fe9677ec7015e
```

## FindCrypt compatibility

Upstream GhidraFindcrypt v3.1.9 predates Ghidra 12.1.3. The exact v3.1.9 source
at commit `fcaa49e545b131e2cc631168c6c168c1aec862a6` was rebuilt locally against
Ghidra 12.1.3. The resulting extension artifact is pinned in
`ghidra/ghidra-findcrypt/PROVENANCE.json`.

The rebuilt 12.1.3 package has the same compiled analyzer JAR and signature
database as the previous official 12.1.2 v3.1.9 package:

```text
GhidraFindcrypt.jar SHA-256
  dc2e395b6dac463ed9191465ce43d5c6cea5002851515b06f0167c5464ee3aa3

data/database.json SHA-256
  8f7bdbc5f9bbe48a4ed93792adab67fca6f103384165ed1917d883870ee6f471
```

Only the Ghidra extension-version packaging changes.

## Independent rebuild proof

Two clean four-stage project rebuilds were produced under Ghidra 12.1.3:

- `build/rebuild-1213-a`
- `build/rebuild-1213-b`

Both finished with the same recovered project statistics:

```text
functions     6376
instructions 183240
symbols       38842
memory size  1376576
sections      14
```

Their complete `processor_manifest.json` files are byte-identical (SHA-256
`423a9464f298a55a7b626dfa04305cb64b7ffe191b71459c8505b70e1e31267b`).
The repository's two-rebuild baseline-update guard accepted the two normalized
inventories as identical.

Compared with the tracked 12.1.2 canonical project inventory, the 12.1.3
inventory changes exactly one field: the metadata `ghidra_version` value. No
memory block, function, body, signature/storage, user symbol, comment, bookmark,
or aggregate semantic record changes.

## Decompiler corpus proof

The persistent whole-image decompiler corpus was regenerated from the verified
12.1.3 rebuild. It still contains 6,376 functions and zero failures. Comparing
with the prior 12.1.2 corpus changes only the metadata record:

- `ghidra_version`: `12.1.2` -> `12.1.3`
- `project_inventory_sha256`: updated because the inventory metadata changed

All 6,376 function/decompilation/reference-graph records are byte-identical.
Therefore this Ghidra patch-level update does not change any persisted firmware
semantic conclusion.

During the migration audit, the full processor gate exposed seven stale strict
reference-census expectations. Re-running the same gate against the untouched
12.1.2 snapshot produced the same seven failures, proving they were pre-existing
verification drift rather than a 12.1.3 change. The missing references are
already present in the canonical instruction/reference graph and resolve to
three RDBI readers (`0x4D8B6`, `0x4D930`, `0x4D95A`), one routine-control
precondition reader (`0x4F500`), and two RDBI reads represented by instruction
references `0x4CF12` and `0x4CF86`. The strict censuses were updated to include
those byte-backed readers; no firmware analysis output changed.

The processor gate then exposed one additional stale derived baseline at
`0x8B1F0`: `data/decompiler_signatures.baseline.csv` still named the function
`application_ecu_reset_callback`, while both the pre-migration 12.1.2 canonical
inventory/corpus and the annotation source already identify it as
`application_clear_diagnostic_information_callback` (SID 0x14). The baseline
was refreshed to the existing canonical function name/body hash. This was also
pre-existing verification drift, not a 12.1.3 semantic change.

Finally, `verify-processor` regenerated `data/instruction_inventory.csv`. The
tracked inventory had also lagged the current 6,376-function snapshot: its
mnemonic counts summed to 180,262 instructions, while the canonical project has
183,240. The refreshed inventory covers all 183,240 instructions while keeping
the same 107 mnemonic classes and the same approved user-op set. This is a
baseline refresh to the already-committed graph, not an instruction-decoder
change caused by 12.1.3.

## Repository consequences

The migration updates:

- Ghidra environment and cache guards to require 12.1.3;
- CI processor/rebuild jobs to require 12.1.3;
- Renesas_v850 extension metadata/provenance;
- GhidraFindcrypt to a hash-pinned local 12.1.3 rebuild;
- committed project snapshot and processor manifest;
- processor and normalized-project baselines;
- persistent decompiler-corpus provenance.

A cache generated under 12.1.2 is explicitly treated as stale and rebuilt.

## ghidra-cli compatibility

The vendored ghidra-cli remains version 0.2.1. Under Ghidra 12.1.3 / JDK 26:

- `ghidra doctor` succeeds and compiles the embedded Java bridge;
- all 6 live `script_tests` pass;
- `cargo check --all-targets` passes, with only the pre-existing unused-import
  warning in `src/ghidra/setup.rs` tests;
- the project-management/live bridge tests run successfully through the full
  project lifecycle and daemon suites.

The monolithic Cargo run stops later in `readonly_tests` with 7 stale test
failures and 5 ignored snapshot tests. Running `readonly_tests` against an
untouched pre-migration checkout under genuine Ghidra 12.1.2 reproduces the
same 43 pass / 7 fail / 5 ignored result and the same failure shapes. The three
batch failures use CLI flags the current 0.2.1 parser no longer accepts; the
four disassembly failures target fixture address `0x00118B40`, which is not an
instruction in the analyzed fixture. These are pre-existing ghidra-cli test
suite drift and are not promoted as migration regressions.

## Final certification

The completed migration passed the repository's full Ghidra gate:

```text
make verify-ghidra
  verify-core:                  204 passed, 0 failed, 0 skipped
  verify-sleigh:                passed
  verify-processor:             passed
  verify-semantic-coverage-live passed
  verify-project-parity:        passed
```

`verify-processor` confirms 6,376 functions with zero undefined bytes in
function bodies, 324 named system-register operations, all 21 synthetic
processor cases, all strict application/SecOC/motor/ICU-S reference censuses,
all recovered switch tables, and the approved processor user-op set. The live
semantic-coverage export exactly matches the committed ledger/summary, and the
fresh canonical project inventory exactly matches the new 12.1.3 baseline.

The migration-specific changed-file gate also passes 64 suites with zero
failures or skips. `git diff --check` is clean.
