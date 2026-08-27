# Workflow: opening, verifying, and rebuilding the Ghidra project

This is the operating manual for the Ghidra side of the repository. For what
the firmware *is*, see [OVERVIEW.md](OVERVIEW.md).

## Prerequisites

- [Astral UV](https://docs.astral.sh/uv/) for the locked Python environment.
- Ghidra **12.1.3** (tested Homebrew location `/opt/homebrew/opt/ghidra/libexec`).
- Rust `ghidra` CLI **0.2.1** (`ghidra doctor` must pass). The CLI source is
  **vendored in-tree** at `ghidra/ghidra-cli/` (fork of
  `akiselev/ghidra-cli`). Run `make ghidra-cli` to build it into
  `build/cache/ghidra-cli/`; the repo's tool scripts automatically prefer the
  vendored build over any `ghidra` on `PATH`. See
  `ghidra/ghidra-cli/README.md` and `PROVENANCE.json`. Use
  `make test-ghidra-cli` for the complete portable CLI compile/unit gate.
- The Renesas v850/RH850 processor module, **vendored in-tree** at
  `ghidra/ghidra_v850/` (fork of `esaulenka/ghidra_v850` at commit
  `14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
  `ghidra/ghidra_v850/README.md` and `PROVENANCE.json`).

There is no separate install step. `tools/install_v850_extension.sh` (invoked
by `make verify-sleigh` and every project rebuild) compiles the vendored
`.slaspec` sources from a disposable copy under `build/cache/processor-extension-src/`
and installs into an isolated Ghidra user-home under `build/cache/ghidra-home/` via
`-Duser.home`. It does **not** generate files in the vendored tree or mutate
`$GHIDRA_HOME/Ghidra/Extensions`.

The in-tree `v850.cspec` models the RH850/G3 calling convention (r6–r9 args,
r10 return, callee-saved r20–r29, lp link register, `__interrupt` prototype).
Processor audits: [tooling/processor-module-audit.md](tooling/processor-module-audit.md).

## Build workspace contract

`build/` is ignored **workspace state**, not a source of repository truth. A
clean clone must be able to run `make verify` and `make verify-full` without any
pre-existing build files. If a deterministic/core verifier needs bytes or compact
facts, promote them to a tracked location (`community/`, `data/`, `exploit/.../audited/`, etc.)
and bind their provenance there instead of reading an ignored file.

Only five top-level namespaces are valid:

- `build/cache/` — expensive reproducible caches: vendored CLI binary, its Cargo
  target directory, isolated Ghidra home/extensions, and toolchain material. Safe
  to delete, expensive to rebuild. Vendored source trees remain source-only.
- `build/work/` — mutable persistent workspaces: live Ghidra projects, disposable
  target projects, and full decompiler corpora used while promoting compact evidence.
- `build/out/` — reproducible reviewable outputs that are not yet promoted: reports,
  manifests, rebuilt shellcode, pseudocode, inventories.
- `build/logs/` — execution logs.
- `build/tmp/` — short-lived intermediates.

Use `make build-status` to see category sizes and any legacy pre-layout
entries. `make clean-build` removes only `logs/` and `tmp/`; deleting `work/` or
`cache/` requires the explicit `tools/build_layout.py clean ... --force` path,
and destructive layout operations are restricted to this repository's own
`build/` root. `work/` and `cache/` cleanup refuse to run while an RH850 Ghidra
daemon is active.

Migration is explicit and non-destructive. `tools/build_layout.py migrate-known`
dry-runs the recognized reusable cache/work/output moves; add `--apply` to
perform them. `tools/build_layout.py migrate-legacy` dry-runs quarantine of any
remaining pre-layout top-level entries under `build/work/legacy-root/`; add
`--apply` only after review. Migration never deletes those opaque analysis
artifacts, and canonical tools do not consume `legacy-root/` implicitly.

Live-project assertions are `local` verification suites. Core verification uses
tracked firmware/evidence only; external proprietary/public source trees are
owned through explicit `requires_external` gates rather than `REFERENCE/` paths.

### External software corpus layout

Proprietary software distributions used as reverse-engineering inputs live only
under ignored `software/` corpus roots:

```text
software/Techstream/v18/       # Techstream V18 distribution
software/Techstream/gtsplus/   # current GTS+ distribution and local PE reconstructions
software/Techstream/cuw/       # Toyota CUW specimen corpus
software/Renesas/              # Renesas Flash Programmer distribution
```

Tracked source identities/provenance live under `software/locks/`. Our analysis
products remain normal repository content under `tools/`, `tests/`, `docs/`, and
`data/generated/`. Never commit a vendor archive, DLL/EXE, calibration package,
or reconstructed near-copy of one simply to make a verifier portable. Portable
verification consumes the tracked derived evidence; `local` / `required-external`
verification rechecks it against the ignored source corpus.

## The durability trap (read this first)

The `ghidra` CLI runs a long-lived bridge (TCP server inside Ghidra) that keeps
the program **in memory**. Edits from `analyze` / `script run` are **not
durable on disk until the daemon shuts down cleanly**.

1. **Always `stop` before copying or committing the working project.**
   `ghidra ... stop` triggers the teardown commit that writes the durable
   snapshot. Copying or `git add` while a daemon runs captures an empty/stale
   DB. If a fresh daemon opens the project and reports 0 functions, this is
   why — `stop`, then re-copy.
2. **Never commit while a daemon is running.** It holds transient `.lock` /
   `*.lock~` / `tmp*` files (git-ignored). Confirm
   `pgrep -f 'AnalyzeHeadless.*rh850'` is empty before snapshotting.
3. **Opening compacts the DB** (`db.N.gbf` → `db.N+1`) on each clean stop.
   Harmless and expected; don't be alarmed the filename changes. It is also
   why the committed snapshot must never be daemon-opened.
4. **The `analyze` command's save is silently swallowed** by the bridge
   (the teardown commit races the JVM kill). Treat `stop` as the only reliable
   persist. For a guaranteed-durable rebuild, use a `tools/run_headless`
   `-process -commit` one-shot instead of the daemon.
   The persistent bridge itself owns an outer Ghidra transaction, so direct
   in-bridge `program save` is not an authoritative persistence boundary. Clean
   `stop` is authoritative. The vendored `script run --save` and compatibility
   `stop --save` spellings therefore persist by clean bridge teardown rather than
   calling `Program.save()` inside that transaction. One-shot headless jobs that
   need an explicit commit use `tools/run_headless ... -commit` instead.

## Working copy vs. committed snapshot

The legacy primary Sienna lives in committed snapshot `project/`. Additional
first-class targets live in independent committed `projects/<target>/` snapshots;
this separation is intentional because Sienna snapshot promotion uses an exact
`rsync --delete` mirror. Every snapshot stores `.gpr.snapshot` / `.rep.snapshot`
non-live names that raw Ghidra cannot recognize. `tools/g` refuses both committed
snapshot namespaces. All interactive work happens under registered gitignored
`build/work/` paths:

- `make work-project` — materialize the default Sienna into `build/work/project/`;
  add `TARGET=camry-8965F3307000` (or another registered target) to materialize
  that target's registered work path and snapshot.
- `make rebuild-project` — fresh from-scratch rebuild using the selected target's
  staged rebuild profile.
- `make verify-project-parity` — export the selected live project and compare it
  byte-for-byte to that target's tracked normalized inventory baseline.
- `make generate-decompiler-corpus` — regenerate the selected target's canonical
  corpus only after live inventory parity succeeds.
- `make snapshot-project` — the **only** path that promotes the selected working
  project into its committed non-live snapshot. Non-default first promotions
  require `PARITY_PROJECT_DIR` from an independent rebuild; later promotions
  compare directly to the tracked target baseline.
- `make finalize-project` — orchestrated end-of-session promotion: stops the
  daemon, waits for exit, verifies the working project, invokes the snapshot
  path, and prints the staged project diff summary. This is an explicit
  promotion command: it always verifies and snapshots the selected working
  project, even if no mutation marker exists. Use this instead of
  manually running `tools/g stop` + `make snapshot-project`.

Mutation markers are project-affine records under
`build/work/ghidra-session-dirty/`; each records the canonical working-project path.
`GHIDRA_PROJECT=/path/to/build-copy tools/g ...` therefore cannot mark or clear
another working project, and finalization propagates its `PROJECT_DIR` to the
daemon stop and snapshot steps. Markers are warnings about mutation-capable
commands, not the authority for deciding whether a rebuilt project needs
promotion.

## Opening the working project

`tools/g` is fully self-contained. It validates the cached isolated Ghidra
environment (processor extension, Java options, fingerprint) and rebuilds it
only when missing or stale — you never need to source
`build/cache/ghidra-processor.env`.

```bash
# Legacy/default Sienna
make work-project
tools/g decompile 0x8db22

# First-class Camry F33
make work-project TARGET=camry-8965F3307000
tools/gcamry decompile 0x4e848
make verify-project-parity TARGET=camry-8965F3307000
make generate-decompiler-corpus TARGET=camry-8965F3307000

# Generic registered-target spelling
tools/gtarget camry-8965F3307000 x-ref to 0xfebe66a8
```

For the common multi-command read paths, prefer the compound CLI operations:

```bash
# Single-target output is unchanged; two or more targets return an ordered aggregate.
tools/g inspect 0xc853a 0x8db22 --decompile --callees --disasm 40

# Exact refs-to census, unique containing functions, and owner decompilations.
tools/g x-ref trace-to 0xfebef02a --disasm 20

# No temporary batch file; every command is parsed and checked before command 1 runs.
printf 'stats\nquery functions --count\n' | tools/g batch --read-only -
```

These paths are deliberately bounded and fail closed. `inspect` and `x-ref
trace-to` default to at most 20 targets/source functions; `batch` defaults to
100 commands. They abort rather than truncate, and the bound can be raised only
with the corresponding `--max-targets`, `--max-functions`, or `--max-commands`
option. Multi-target inspection resolves every target before decompiling any of
them. `batch --read-only` preflights the complete batch against a conservative
allowlist and rejects mutation-capable commands, nested batches, lifecycle
operations, and executable scripts before its first command. Without
`--read-only`, batch retains its existing mutation-capable behavior and
`tools/g` conservatively marks the working session potentially mutated.

If you re-run `analyze` or any `script run` and want to keep the result in the
working copy, run `tools/g stop` afterward. To promote a finished working copy
into the committed snapshot, run `make finalize-project` (which orchestrates
daemon stop, verification, snapshot, and diff).

### Persistent mechanical annotations

Do not transcribe every rename or comment into another one-off Java class. Simple
function renames, data labels, and listing comments live in the tracked
`data/annotations/annotation_ledger.jsonl` ledger and are edited through
`tools/annotations`:

```bash
tools/annotations add function 0x8db22 uds_security_access_handler --comment '...'
tools/annotations add label 0xfebef02a security_state
tools/annotations add comment 0x8db36 '...' --comment-type eol
tools/annotations apply              # replay into build/work/project, then cleanly stop/persist
```

The canonical rebuild validates and applies the complete ledger at the end of
stage 4. The applier preflights the complete ledger before mutation and fails on missing
functions, symbol collisions, unmapped addresses, or malformed operations. Function discovery, signatures, types, overlays, and semantic
recovery remain purpose-built seed/annotation scripts. See
[tooling/annotation-ledger.md](tooling/annotation-ledger.md).

## Persistent whole-image pseudocode

The canonical project has a tracked decompiler corpus at
`data/generated/decompilations.jsonl`. It contains one record for every recovered
function, including entry address, name, signature, calling convention, body
size, decompiler status, SHA-256 of the rendered C, the complete decompiled C,
and the canonical non-flow instruction/data references exported by Ghidra. The
reference graph is deliberately stored separately from the rendered C so a RAM
byte remains discoverable even when the decompiler spells it as a structured
interior field (`DAT_base._n_m_`) or a base-relative expression (`LAB_base +
offset`). Its metadata pins the exact canonical project-inventory hash,
Ghidra/program identity, and the exporter/generator source hashes.

Use it as the first cognitive/search surface for broad static analysis. Address
lookup accepts either a function entry or any address inside an exact body range
from the provenance-matched project inventory:

```bash
tools/pseudo 0x6fec                     # function entry -> pseudocode
tools/pseudo 0x6fee                     # interior address -> containing function pseudocode
tools/pseudo security_access --list    # search function names
tools/pseudo secoc --all               # emit all matching pseudocode
tools/pseudo --data-ref 0xfebef02a    # canonical function-owned RAM refs despite text aliases
tools/pseudo --data-ref 0xfebe8001 --list
# IMPORTANT: --data-ref is a function-owned corpus query, not an exhaustive live-xref census.
# References at addresses outside Ghidra's current Function.body can be absent even when the
# decompiler follows that code (boot send-key 0x54DC is a known example). For exhaustive
# security-state writer closure, confirm with `tools/g x-ref to <address>` in a disposable/live
# project and raw disassembly.
make pseudocode                        # rebuild ignored build/out/pseudocode/*.c view
rg 'ICUSCMD' build/out/pseudocode
rg 'nvm_object_15' build/out/pseudocode
```

## Task-oriented tooling discovery

Before writing a new one-file-per-surface script, check the three consolidated
entry points — several earlier one-off extractors and export wrappers are now
profiles or subcommands behind them, and new variants of the same operation
belong there rather than in a new top-level file:

| Operation | Entry point |
|---|---|
| Corolla-H surface evidence compaction (fixed known targets, one/two JSONL corpora) | `uv run --locked python tools/extract_corolla_h_evidence.py list` |
| Read-only exports from `build/work/project` (signals/consumers/producers/coverage/inventory) | `tools/export_ghidra_project.sh list` |
| Cross-variant image-bound evidence (structural fingerprints, decompilation, callback-table selection, substring census) | `uv run --locked python tools/extract_variant_evidence.py list` |

All three expose a `list` discovery command. The Corolla-H runner reports its
profile inputs and tracked outputs; the argument-driven variant runner reports
mode purpose/input/selection semantics; the exporter lists its profile names,
with defaults documented in the tooling guide. Their scope boundaries — which
extractors stay separate and why — are documented in
[tooling/README.md](tooling/README.md#task-oriented-entry-points).

The `.c` tree is intentionally ignored; it can be reproduced from the tracked
JSONL without opening Ghidra. The JSONL is generated in one read-only headless
Ghidra pass rather than thousands of individual CLI calls.

Refresh the corpus only from a fresh rebuilt/disposable project whose exported
inventory is byte-for-byte equal to
`data/ghidra_project_inventory.baseline.jsonl`. A project merely materialized
from the committed snapshot may carry Ghidra version-control state that
`analyzeHeadless -process` reports as hijacked, so use a fresh rebuild output:

```bash
make rebuild-project PROJECT_DIR="$PWD/build/work/corpus-rebuild"
make generate-decompiler-corpus PROJECT_DIR="$PWD/build/work/corpus-rebuild"
uv run --locked python tests/verify_decompiler_corpus.py
```

The generator stops the selected project's daemon, exports and compares its
live inventory first, then performs the decompiler pass. Any missing function,
identity drift, timeout, failed decompilation, or empty C aborts the refresh
instead of silently publishing a partial corpus.

The evidence boundary is deliberate: **pseudocode for understanding ->
canonical persisted xrefs/dataflow for tracing -> disassembly/firmware bytes for
proof**. `--data-ref` is the preferred persisted-xref entry point for RAM state;
it avoids treating decompiler alias spelling as an address census. Decompiled C
and the exported reference graph are generated evidence, not the source of truth.

Expected memory map after the P1M-E device profile is applied:

```text
CodeFlash   00000000..000fffff  rx
DataFlash   ff200000..ff207fff  rw
LocalRAM    febe0000..febfffff  rw
SFR_EIC     ffffb000..ffffbfff  rw volatile
SFR_RSCFD   ffd20000..ffd2ffff  rw volatile
SFR_ICUS    ffc5d000..ffc5dfff  rw volatile
```

The full peripheral window `0xFF600000..0xFFFFFFFF` stays volatile in
`v850.pspec`. Only the verified windows above are mapped as blocks — mapping
the entire 10 MiB SFR range makes CodeFlash immediates look like valid
pointers and collapses disassembly.

## Verification

```bash
uv sync --locked              # one-time
make verify                   # fast tracked-only edit-loop gate
make verify-full              # exhaustive portable/tracked-repository gate
make verify-changed           # suites owning the current git diff, regardless of tier
make verify-local             # full + available proprietary/external + live-project suites
make verify-required-external # require every pinned external prerequisite
make verify-agent             # fast core as compact JSON with timings/oracle counts
make verify-sleigh            # SLEIGH compile + isolated install
make verify-processor         # fixtures + working-project audits
make verify-project-parity    # exact working-project inventory vs baseline
make verify-ghidra            # portable full + Ghidra gates
```

`verification.toml` is the sole suite manifest. It owns each
`tests/verify_*.py` gate exactly once, records changed-file routing, suite tier,
external prerequisites, and the default evidence-oracle class. Suites without
an explicit `modes` entry are in `core`, `full`, and `local`. Expensive but fully
tracked exhaustive checks can be `full`/`local`; suites backed by ignored or
proprietary corpora are `local` only. `--required-external` selects every suite
with a declared external prerequisite independently of tier.

The core and full modes deliberately set `RH850_VERIFY_EXTERNAL=0` in verifier
children. This prevents a nominally portable gate from silently doing extra work
just because an ignored `software/` corpus happens to exist on one developer
machine. Local and required-external modes enable those optional
raw-source cross-checks. Exit code 77 remains the explicit artifact-level skip
code; required-external mode turns the same absence into a concise failure.
Runner summaries keep pass/fail/skip separate, report assertion counts by
evidence oracle, and print the slowest test durations.

The edit-loop tier is intentionally broad but not exhaustive. In particular, the
32-KiB Corolla DataFlash all-window cryptographic domain scan remains in
`full`/`local`: it tests 23,277 unique 16-byte candidates and is valuable evidence,
but recomputing millions of CMAC probes after unrelated edits is not useful.
`make verify-changed` still routes directly to that suite when its owned inputs or
verifier change, so tiering does not hide relevant failures during focused work.

The machine summary keeps `identity_hash`, `documentation_lint`, and
`generated_self_check` counts separate from `raw_bytes`, `instruction_semantics`,
`cfg_dataflow`, `dynamic_trace`, and `independent_external_artifact`, so a drift or
report-only gate cannot be reported as semantic verification.

Optional checks against pinned public repositories remain separate:

```bash
make verify-external EXTERNAL_REPOS_DIR=/path/containing/the/checkouts
```

`external-references.lock.json` records exact commits, expected checkout
directory names, artifact hashes, and payload-fixture provenance. The optional
suite fails on a missing checkout, a commit mismatch, or changed artifact
bytes.

## Rebuilding the complete project from firmware

The committed split images are the only firmware inputs. SHA-256:

```text
DataFlash  81d87b678784bb2a07b1fdcb3d43dd40767d4f5ca1b56867b6575cd652a9ecb8
CodeFlash  21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde
Combined   0bba74d0e443f9dd3da33e3a28c3511ec31e35e8303acef7e0117fbdc91d5a86
```

The CodeFlash input is preserved exactly as published. SECOC-044 recovers a
unique one-bit inconsistency at VA `0xBB1C4` (`0xA2→0x82`) whose analysis-only
reconstruction restores the existing region-1 boot CRC and repairs the local
RH850 store semantics; reconstructed CodeFlash SHA-256 is
`b6f510662c324261dac6fc1504ec77c217d2055dc099096375a91f3fcf7e9916`.
Do **not** silently patch the committed firmware input or rebuild the canonical
project from the reconstructed derivative; use the reconstruction only for
explicit CRC/semantic experiments.

```bash
make rebuild-project                                  # into build/work/project/
make rebuild-project PROJECT_DIR="$PWD/build/work/parity-project"  # disposable sibling
```

Rebuild destinations are deliberately constrained to dedicated directories
below `build/work/`; this keeps `--force` incapable of deleting committed or
unrelated trees. To replace an existing disposable working build:
`tools/rebuild_project.sh --project-dir "$PWD/build/work/project" --force`.
Never point the rebuild at committed `project/`; promote only with
`make snapshot-project`.

Rebuilds consume the tracked diagnostic-vocabulary artifact by default; an
ignored local Techstream tree is never an implicit input. To deliberately
refresh that artifact first, pass `--refresh-diagnostic-vocabulary` and review
its tracked diff before promotion.

All repository one-shot Ghidra jobs go through `tools/run_headless`. It owns
the isolated environment, canonical project-path guard, canonical script path,
CPU/time limits, logs, and `REPORT SCRIPT ERROR` detection. Do not duplicate a
raw `analyzeHeadless` command in another script. The canonical script path
deliberately excludes `ghidra/scripts/investigate`: including that directory was
measured to change the recovered graph by 194 functions. Deterministic exporters
used by tooling live under `ghidra/scripts/verify` instead.

### The four-stage analysis (do not collapse)

The script uses four staged durable analysis commits plus a separate
`-noanalysis` calling-convention finalizer. Staging matters: injecting every
seed before the first analysis pass produces a different graph and does not
reproduce the committed statistics.

1. Import CodeFlash without analysis, map DataFlash with `AddDataFlash.java`,
   apply `ApplyP1MDeviceProfile.java` (LocalRAM/SFR windows, GP/TP, SFR labels
   from `data/p1m_sfr_labels.csv`), `ApplyP1MSfrTypes.java` (EIC/RSCFD/ICU-S
   overlays), `ApplyRamTypes.java` (LocalRAM payload/SecOC/DID/checkpoint
   overlays from `data/checkpoint_payload_map.csv`).
2. Run `SeedEntries.java`, then the base auto-analysis.
3. Run `SeedUdsServiceTable.java`, re-run analysis.
4. Seed remaining missed functions (`SeedCanTransportFunctions`,
   `SeedPayloadVerificationFunctions`, `SeedSecocNvmFunctions`,
   `SeedSecocApplicationFunctions`, `SeedDataFlashSemanticsFunctions`,
   `SeedApplicationDiagnosticFunctions`, `SeedBootloaderDiagnosticFunctions`,
   `SeedArchitectureFunctions`, `SeedApplicationTransmitFunctions`), re-run
   analysis, apply every annotation script (`AnnotateBootloaderSecrets`,
   `AnnotatePayloadGate`, `AnnotateSecocNvmCorrection`,
   `AnnotateSecocApplication`, `AnnotateDataFlashLayout`, `AnnotateDidModel`,
   `AnnotateCanTransport`, `AnnotateApplicationDiagnostics`,
   `AnnotateBootloaderDiagnostics`, `RecoverVectorHandlers`,
   `RecoverSwitchTables`, `AnnotateArchitecture`,
   `AnnotateApplicationTransmit`, `ApplyCallingConventions`), then replay the
   tracked mechanical annotation ledger with `ApplyAnnotationLedger`.
5. `-noanalysis` convention finalizer: re-run `ApplyCallingConventions.java`.
   After the annotate-stage reopen, Ghidra surfaces two additional non-ISR
   bodies (`0x3b0be`, `0x6f0d0`) that stage 4 never saw; without the finalizer
   they stay `unknown`. The finalizer also covers explicitly seeded functions
   added by later subsystem work.
6. Open the result through the CLI, record statistics, cleanly stop the daemon.
7. Write `processor_manifest.json` beside the working project and require
   function/instruction/symbol floors plus the nine-block memory map.
8. Export canonical compact JSONL to `build/out/ghidra_project_inventory.jsonl`
   and compare every semantic record with
   `data/ghidra_project_inventory.baseline.jsonl`. The path-free inventory
   covers tool/program identity, memory mappings, complete function bodies and
   signatures/storage, user symbols, comments, bookmarks, and aggregate maps;
   it catches equal-count substitutions and annotation drift that floors miss.

When a deliberate seed/annotation change alters the inventory, run
`make update-project-baseline PROJECT_DIR_A=/abs/rebuild-a
PROJECT_DIR_B=/abs/rebuild-b`. The update fails unless two independent fresh
rebuilds produce byte-identical canonical inventories. Review the tracked diff,
then rerun `make verify-project-parity`. Ordinary verification never updates the
baseline.

Corrected rebuild stats after WDBI callback-table seeding (2026-08-13): **6,094
functions, 181,203 instructions, 38,300 CLI-reported symbols** (floors are
collapse detectors; semantic checks live in
`make verify-processor`, exact identity in `make verify-project-parity`).

After a graph-changing rebuild, regenerate the structural semantic ledger and
the reproducible review cohort from a disposable project:

```bash
PROJECT_DIR=build/work/rebuild-a make generate-semantic-coverage
uv run --locked python tools/generate_semantic_interest_ranking.py
make generate-semantic-sweep PROJECT_DIR=build/work/rebuild-a
uv run --locked python tests/verify_semantic_sweep.py
```

The semantic sweep records selection and decompilation, not semantic proof.
Rows that remain `reviewed_unknown` carry no evidence grade.

## CI

CI (`.github/workflows/ci.yml`) always runs `make verify-full`, so moving a slow
portable check out of the edit-loop core does not reduce CI evidence coverage.
Processor-path changes run SLEIGH, synthetic fixtures, and committed-project
audits on macOS with pinned Ghidra 12.1.3 / ghidra CLI 0.2.1. Processor, script,
and snapshot changes — plus `main`, manual, and nightly runs — execute the full
four-stage rebuild (plus convention finalizer), project invariants, and exact
normalized inventory comparison. The 12.1.2 -> 12.1.3 migration was verified by
two independent clean rebuilds and changed no canonical semantic record; see
[the migration journal](history/2026-08/GHIDRA_12_1_3_MIGRATION_2026-08-22.md).
