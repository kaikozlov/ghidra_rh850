# Workflow: opening, verifying, and rebuilding the Ghidra project

This is the operating manual for the Ghidra side of the repository. For what
the firmware *is*, see [OVERVIEW.md](OVERVIEW.md).

## Prerequisites

- [Astral UV](https://docs.astral.sh/uv/) for the locked Python environment.
- Ghidra **12.1.2** (tested Homebrew location `/opt/homebrew/opt/ghidra/libexec`).
- Rust `ghidra` CLI **0.2.1** (`ghidra doctor` must pass). The CLI source is
  **vendored in-tree** at `ghidra/ghidra-cli/` (fork of
  `akiselev/ghidra-cli`). Run `make ghidra-cli` to build it into
  `build/ghidra-cli/`; the repo's tool scripts automatically prefer the
  vendored build over any `ghidra` on `PATH`. See
  `ghidra/ghidra-cli/README.md` and `PROVENANCE.json`.
- The Renesas v850/RH850 processor module, **vendored in-tree** at
  `ghidra/ghidra_v850/` (fork of `esaulenka/ghidra_v850` at commit
  `14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
  `ghidra/ghidra_v850/README.md` and `PROVENANCE.json`).

There is no separate install step. `tools/install_v850_extension.sh` (invoked
by `make verify-sleigh` and every project rebuild) compiles the vendored
`.slaspec` sources from a disposable copy under `build/processor-extension-src/`
and installs into an isolated Ghidra user-home under `build/ghidra-home/` via
`-Duser.home`. It does **not** generate files in the vendored tree or mutate
`$GHIDRA_HOME/Ghidra/Extensions`.

The in-tree `v850.cspec` models the RH850/G3 calling convention (r6–r9 args,
r10 return, callee-saved r20–r29, lp link register, `__interrupt` prototype).
Processor audits: [tooling/processor-module-audit.md](tooling/processor-module-audit.md).

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
   The vendored CLI adds `program save --message` and `stop --save` for explicit
   persistence boundaries (see `ghidra program save --help`). Until save-and-
   reopen tests exist for this project, continue to treat `stop` as the
   authoritative boundary and use explicit `program save` as a belt-and-suspenders
   extra commit.

## Working copy vs. committed snapshot

`project/` is a **committed snapshot** — a durable annotated reference. Its
database is physically stored as `rh850_p1me_mapped.gpr.snapshot` and
`rh850_p1me_mapped.rep.snapshot`; raw Ghidra cannot recognize those names.
`make verify-sleigh` asserts that a direct `analyzeHeadless` open fails. All
interactive work happens in the gitignored working copy at `build/project/`:

- `make work-project` — materialize live `.gpr` / `.rep` names under
  `build/project/` from the committed non-live snapshot.
- `make rebuild-project` — fresh from-scratch rebuild into `build/project/`.
- `make snapshot-project` — the **only** path that mutates committed
  `project/`. Verifies floors, processor fingerprint, and exact normalized
  inventory; packs the working project back to non-live snapshot names; stages
  it.
- `make finalize-project` — orchestrated end-of-session promotion: stops the
  daemon, waits for exit, verifies the working project, invokes the snapshot
  path, and prints the staged project diff summary. Use this instead of
  manually running `tools/g stop` + `make snapshot-project`.

## Opening the working project

`tools/g` is fully self-contained. It validates the cached isolated Ghidra
environment (processor extension, Java options, fingerprint) and rebuilds it
only when missing or stale — you never need to source
`build/ghidra-processor.env`.

```bash
make work-project   # one-time: copy snapshot -> build/project
tools/g decompile 0x8db22
tools/g x-ref to 0x8db22
# e.g. ... stats | decompile 0x6fec | x-ref to 0xbfe8 | symbol list
```

If you re-run `analyze` or any `script run` and want to keep the result in the
working copy, run `tools/g stop` afterward. To promote a finished working copy
into the committed snapshot, run `make finalize-project` (which orchestrates
daemon stop, verification, snapshot, and diff).

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
uv sync --locked      # one-time
make verify           # deterministic firmware suites (no Ghidra)
make verify-sleigh    # SLEIGH compile + isolated install
make verify-processor # fixtures + working-project audits
make verify-project-parity # exact working-project inventory vs baseline
make verify-ghidra    # all of the above
```

`make verify` reads only tracked files. Optional checks against pinned public
repositories are separate:

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

```bash
make rebuild-project                                  # into build/project/
make rebuild-project PROJECT_DIR="$PWD/build/parity-project"  # disposable sibling
```

Rebuild destinations are deliberately constrained to dedicated directories
below `build/`; this keeps `--force` incapable of deleting committed or
unrelated trees. To replace an existing disposable working build:
`tools/rebuild_project.sh --project-dir "$PWD/build/project" --force`.
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
   `AnnotateApplicationTransmit`, `ApplyCallingConventions`).
5. `-noanalysis` convention finalizer: re-run `ApplyCallingConventions.java`.
   After the annotate-stage reopen, Ghidra surfaces two additional non-ISR
   bodies (`0x3b0be`, `0x6f0d0`) that stage 4 never saw; without the finalizer
   they stay `unknown`. The finalizer also covers explicitly seeded functions
   added by later subsystem work.
6. Open the result through the CLI, record statistics, cleanly stop the daemon.
7. Write `processor_manifest.json` beside the working project and require
   function/instruction/symbol floors plus the nine-block memory map.
8. Export canonical compact JSONL to `build/ghidra_project_inventory.jsonl`
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

Landmark rebuild stats: **5,921 functions, 179,223 instructions, 37,785
symbols** (floors for gates; semantic checks in `make verify-processor`).

## CI

CI (`.github/workflows/ci.yml`) always runs `make verify`. Processor-path
changes run SLEIGH, synthetic fixtures, and committed-project audits on macOS
with pinned Ghidra 12.1.2 / ghidra CLI 0.2.1. Processor, script, and snapshot
changes — plus `main`, manual, and nightly runs — execute the full four-stage
rebuild (plus convention finalizer), project invariants, and exact normalized
inventory comparison, then upload the generated inventory and audit artifacts.
