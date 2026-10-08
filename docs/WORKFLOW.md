# Workflow: opening, verifying, and rebuilding the Ghidra project

This is the operating manual for the Ghidra side of the repository. For what
the firmware *is*, see [OVERVIEW.md](OVERVIEW.md).

## Prerequisites

- [Astral UV](https://docs.astral.sh/uv/) for the locked Python environment.
- Ghidra **12.1.4** (tested Homebrew location `/opt/homebrew/opt/ghidra/libexec`).
- Rust `ghidra` CLI **0.2.1** (`ghidra doctor` must pass). The CLI source is
  **vendored in-tree** at `ghidra/ghidra-cli/` (fork of
  `akiselev/ghidra-cli`). Run `make ghidra-cli` to build it into
  `build/cache/ghidra-cli/` (needs a Rust/cargo toolchain; when the vendored
  binary is missing or stale, the tool wrappers rebuild it automatically when
  cargo is available); the repo's tool scripts automatically prefer the
  vendored build over any `ghidra` on `PATH`. See
  `ghidra/ghidra-cli/README.md` and `PROVENANCE.json`. Use
  `make test-ghidra-cli` for the complete portable CLI compile/unit gate.
- The Renesas v850/RH850 processor module, **vendored in-tree** at
  `ghidra/ghidra_v850/` (fork of `esaulenka/ghidra_v850` at commit
  `14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
  `ghidra/ghidra_v850/README.md` and `PROVENANCE.json`).
- Docker for target-native RH850 payload compilation/execution testing — only
  the `tools/rh850` workflows need it; read-only Ghidra analysis does not.
  The single pinned GNU toolchain and compiled-in V850/RH850 GDB simulator are
  exposed through `tools/rh850`. On a clean machine run
  `tools/rh850 toolchain build`, then `tools/rh850 toolchain doctor` and
  `tools/rh850 toolchain self-test`. There is no compiler-profile selection or
  image override. See
  [RH850 build and execution testing](tooling/rh850-build-and-sim.md).

There is no separate processor install step. `tools/project/install_v850_extension.sh` (invoked
by `make verify-sleigh` and every project rebuild) compiles the vendored
`.slaspec` sources from a disposable copy under `build/cache/processor-extension-src/`
and installs into an isolated Ghidra user-home under `build/cache/ghidra-home/` via
`-Duser.home`. It does **not** generate files in the vendored tree or mutate
`$GHIDRA_HOME/Ghidra/Extensions`.

The in-tree `v850.cspec` models the firmware-observed RH850/G3 calling
convention (r6–r9 args, r10 return, callee-saved r20–r29, **volatile r30/ep**,
lp link register, `__interrupt` prototype). Exact Sienna/F33 code disproves the
standard CC-RH ep-preservation rule; the model is GHS-compatible without
claiming a specific Toyota compiler vendor/version. Processor audits:
[tooling/processor-module-audit.md](tooling/processor-module-audit.md).

## Python tooling

Run `uv sync --locked` to install the checkout in editable mode with its locked
dependencies. Public commands under `tools/` select this environment themselves.
For implementation-level use, run modules from the repository:

```bash
uv run --locked python -m tools.project.analysis_target --list
```

Python modules import through `tools.<subsystem>` and use `tools.REPO_ROOT` for
repository-owned files. Command-line input/output paths remain relative to the
caller's working directory unless the command explicitly documents otherwise.
`tools/artifact regen` and `tools/toyota` capability dispatch retain their existing
repository-root working directory; pass absolute paths for inputs outside the checkout.

### External openpilot rlog reducers

Some Camry evidence reducers read external comma rlog corpora and need
openpilot's reader/runtime. These are offline commands only: they never
perform vehicle operations. Run them from this repository root; the usual
runtime is the adjacent openpilot/opendbc checkout, selected through uv's
`--project` so `--no-sync` keeps its environment pinned:

```bash
# 2026-09-30 VMC status corpus pipeline (paths below are the documented example)
UV="uv run --no-sync --project ../kai-openpilot/opendbc_repo"
$UV python -m tools.targets.camry.analysis.extract_camry_20260930_vmc_corpus \
  --logs-root ~/dev/inspect/logs --openpilot-root ../kai-openpilot/openpilot \
  --output-dir build/cache/camry_20260930_vmc_corpus
$UV python -m tools.targets.camry.analysis.join_camry_20260930_vmc_corpus \
  --corpus-dir build/cache/camry_20260930_vmc_corpus
$UV python -m tools.targets.camry.analysis.analyze_camry_20260930_vmc_status \
  --corpus-dir build/cache/camry_20260930_vmc_corpus \
  --output-dir data/generated/camry_20260930_vmc_status
$UV python -m tools.targets.camry.analysis.plot_camry_20260930_vmc_status \
  --corpus-dir build/cache/camry_20260930_vmc_corpus \
  --output-dir data/generated/camry_20260930_vmc_status
```

- `--openpilot-root` points at a caller-supplied openpilot checkout containing
  `tools/lib/logreader.py` (the extraction example needs it). It is caller
  input; pass the default checkout explicitly rather than importing it as a
  repository dependency.
- Extraction/join intermediates are git-ignored caches under
  `build/cache/…`; only compact summaries under `data/generated/…` are
  committed. `--corpus-dir` explicitly accepts an existing extraction
  directory (for example `/tmp/tss3_vmc_corpus`) to reuse or analyze one
  extracted elsewhere.
- `matplotlib` is required only by the plot module. Analysis and joining need
  NumPy; only extraction needs the external openpilot reader/runtime.
- Modules accept narrowing flags such as `--routes`, `--primary`, `--missing`,
  and `--inventory` (see each module's `--help`) instead of any new wrapper
  script.

### Gear and READY evidence

Regenerate the controlled Camry selector evidence without external inputs:

```bash
tools/artifact regen camry_2026_ready_gear
tools/test plan camry_2026_engagement
tools/test camry_2026_engagement
```

With the installed GTS+ corpus, also check the original meter dictionary and
individual indicator bits against the observed Camry values:

```bash
tools/artifact regen camry_2026_ready_gear -- --check-gts
tools/gts did Meter_P5 0x2931 --json
```

`--check-gts` prints database identities and synthetic diagnostic decode results;
it does not add an external dependency to the tracked capture artifact.
Use `--gtsplus-root PATH` after `--` to select another installed corpus.
This check compares meanings; it does not equate diagnostic byte offsets with
CAN byte offsets or establish ECU runtime support.

The existing Corolla reducers also expose a read-only all-source gear/READY
census. With the external reader/runtime described above:

```bash
uv run --no-sync --project ../kai-openpilot/opendbc_repo python \
  -m tools.targets.corolla.extract.extract_corolla_2023_public_route_opendbc_evidence \
  --openpilot-root ../kai-openpilot \
  --rlog REFERENCE/public_route_corolla_2023_segment0_rlog.zst --gear-audit
uv run --no-sync --project ../kai-openpilot/opendbc_repo python \
  -m tools.targets.corolla.extract.extract_span_2025_discord_rlog_opendbc_evidence \
  --openpilot-root ../kai-openpilot --gear-audit
```

These commands print identity-bound JSON without replacing the default route
artifacts. The census retains `can`/`sendcan`, original sources, DLCs, received
traffic versus echoes, and per-source denominators. It does not filter to the
port's configured bus or require an eight-byte payload to count an ID.
The public-route rlog is an explicitly external input; Span's rlog is tracked.
Neither source numbering nor `harnessStatus=flipped` establishes a physical repin.
Conclusions belong in the [Camry report](variants/camry-2026-live-baseline.md#83-generation-native-0x3bf-gear-indication)
and [Corolla report](variants/corolla-h-f-openpilot-state-bridge.md).

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
`cache/` requires the explicit `tools/project/build_layout.py clean ... --force` path,
and destructive layout operations are restricted to this repository's own
`build/` root. `work/` and `cache/` cleanup refuse to run while an RH850 Ghidra
daemon is active.

Live-project assertions are `local` verification suites. Core verification uses
tracked firmware/evidence only; external proprietary/public source trees are
owned through explicit `requires_external` gates rather than `REFERENCE/` paths.

### Artifact, target, and repository-memory discovery

Use `tools/artifact list/show` instead of grepping for generator filenames. `tools/artifact regen` runs a derived producer. The catalog derives producers from tracked source references and declared outputs; it has no verification-ownership role.

Use `tools/know QUERY` when the question is "what did we already establish?" or "where is this owned?" It searches findings, corrections, open questions, generated artifacts, suites, and tracked docs in one pass. It is only a navigation layer; firmware/Ghidra and deterministic verification remain the evidence authority.

Use `tools/gtarget list` / `tools/gtarget show TARGET` before target-specific work. `data/analysis_targets.json` owns registered image identities, work/snapshot/corpus paths, function seeds, and target-specific rebuild stage scripts. The generic target rebuild/snapshot drivers consume those fields and intentionally contain no Camry-specific path/profile switch.

### External software corpus layout

Proprietary software distributions used as reverse-engineering inputs live only
under ignored `software/` corpus roots:

```text
software/Techstream/v18/       # Techstream V18 distribution
software/Techstream/gtsplus/   # current GTS+ distribution and local PE reconstructions
software/Techstream/cuw/       # Toyota CUW specimen corpus
software/Renesas/              # Renesas Flash Programmer distribution and CC-RH compiler docs
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

1. **Always `stop` before copying, staging, or committing the working project.**
   `ghidra ... stop` triggers the teardown commit that writes the durable
   snapshot. Copying or `git add` while a daemon runs captures an empty/stale
   DB. If a fresh daemon opens the project and reports 0 functions, this is
   why — `stop`, then re-copy.
2. **Ordinary repository commits may proceed while a daemon is running.** Live
   projects and their transient `.lock` / `*.lock~` / `tmp*` files are confined
   to git-ignored `build/` state. Before promoting a working project, stop that
   project's daemon and verify it is gone. Use the global
   `pgrep -f 'AnalyzeHeadless.*rh850'` check only when promoting multiple/default
   projects whose ownership is ambiguous.
3. **Opening compacts the DB** (`db.N.gbf` → `db.N+1`) on each clean stop.
   Harmless and expected; don't be alarmed the filename changes. It is also
   why the committed snapshot must never be daemon-opened.
4. **The `analyze` command's save is silently swallowed** by the bridge
   (the teardown commit races the JVM kill). Treat `stop` as the only reliable
   persist. For a guaranteed-durable rebuild, use a `tools/project/run_headless`
   `-process -commit` one-shot instead of the daemon.
   The persistent bridge itself owns an outer Ghidra transaction, so direct
   in-bridge `program save` is not an authoritative persistence boundary. Clean
   `stop` is authoritative. The vendored `script run --save` and compatibility
   `stop --save` spellings therefore persist by clean bridge teardown rather than
   calling `Program.save()` inside that transaction. One-shot headless jobs that
   need an explicit commit use `tools/project/run_headless ... -commit` instead.

## Working copy vs. committed snapshot

Every committed Ghidra snapshot lives in one namespace: `projects/<target>/`.
The snapshots store `.gpr.snapshot` / `.rep.snapshot` non-live names that raw
Ghidra cannot recognize, and `tools/g` / `run_headless` refuse the entire
committed `projects/` tree. All interactive work happens under registered,
gitignored `build/work/` paths. `data/analysis_targets.json` owns the target
priority and paths; the current default/primary target is the 2026 Camry F33.

- `make work-project` — materialize the registry-default Camry working project;
  add `TARGET=<target>` to select another registered target.
- `make rebuild-project` — fresh from-scratch rebuild using the selected target's
  registered rebuild path. The legacy Sienna keeps its mature specialized rebuild
  script, but it is selected because the target is Sienna, not because it is the
  default.
- `make verify-project-parity` — export the selected live project and compare it
  byte-for-byte to that target's tracked normalized inventory baseline.
- `make generate-decompiler-corpus` — regenerate the selected target's canonical
  corpus only after live inventory parity succeeds.
- `make snapshot-project` — the **only** path that promotes the selected working
  project into its committed non-live snapshot. First staged-target promotions
  require `PARITY_PROJECT_DIR` from an independent rebuild; later promotions
  compare directly to the tracked target baseline.
- `make finalize-project` — orchestrated end-of-session promotion: stops the
  selected target daemon, then promotes. The legacy Sienna orchestration
  verifies the working project, invokes the snapshot path, and prints the
  staged project diff summary; staged targets invoke the snapshot path directly
  (registry baseline parity, or first-promotion two-build parity, followed by
  canonical corpus regeneration, snapshot pack/validate, and git staging).

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
# Default / primary Camry F33
make work-project
tools/g decompile 0x4e848
tools/pseudo 0x4e848

# Explicit legacy Sienna
make work-project TARGET=sienna-8965B4512000
tools/gtarget sienna-8965B4512000 decompile 0x8db22

# Generic explicit-target spelling
tools/gtarget camry-8965F3307000 x-ref to 0xfebe66a8
```

For the common multi-command read paths, prefer the compound CLI operations:

```bash
# Both addresses are Camry F33 functions in the default working project; two or
# more targets return an ordered aggregate.
tools/g inspect 0x8549e 0x4e848 --decompile --callees --disasm 40

# Exact refs-to census, unique containing functions, and owner decompilations.
tools/g x-ref trace-to 0xfebe5504 --disasm 20

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
into the committed snapshot, run `make finalize-project` for the selected target
(daemon stop, target-specific verification, and snapshot promotion).

### Persistent mechanical annotations (legacy Sienna ledger)

Simple function renames, data labels, and listing comments for the legacy Sienna
image live in the tracked `data/annotations/annotation_ledger.jsonl` ledger and
are edited through `tools/annotations`; `apply` replays the ledger into the
registered Sienna working project (`build/work/project`), then cleanly stops and
persists:

```bash
tools/annotations add function 0x32d2 boot_memory_range_check_access --comment '...'
tools/annotations add label 0xfebef02a security_state
tools/annotations add comment 0x8db22 '...' --comment-type eol
tools/annotations apply              # replay into the registered Sienna work project, then cleanly stop/persist
```

The legacy Sienna rebuild validates and applies the complete ledger during its
annotate stage. The applier preflights the complete ledger before mutation and fails on missing
functions, symbol collisions, unmapped addresses, or malformed operations. Registered
first-class targets replay their own purpose-built seed/annotation scripts instead;
function discovery, signatures, types, overlays, and semantic recovery are never
ledger operations. See
[tooling/annotation-ledger.md](tooling/annotation-ledger.md).

## Persistent whole-image pseudocode

Every registered target has a tracked decompiler corpus at its registry
`decompiler_corpus` path. `tools/pseudo` reads the selected target's corpus and
defaults to the registry primary — the Camry F33 corpus at
`data/generated/camry-8965F3307000/decompilations.jsonl`; the legacy Sienna
corpus remains at `data/generated/decompilations.jsonl`. A corpus contains one
record for every recovered
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
# Default target: Camry F33
tools/pseudo 0x4e848                     # function entry (did_1c05_1c0c_asic_state_information) -> pseudocode
tools/pseudo 0x4e850                     # interior address -> containing function pseudocode
tools/pseudo steering_angle --list       # search function names
tools/pseudo rdbi_0103 --all             # emit all matching pseudocode
tools/pseudo --data-ref 0xfebef02a       # canonical function-owned RAM refs despite text aliases
tools/pseudo --data-ref 0xfebe8001 --list
tools/pseudo --target sienna-8965B4512000 0x6fec   # explicit legacy-Sienna corpus lookup
# IMPORTANT: --data-ref is a function-owned corpus query, not an exhaustive live-xref census.
# References at addresses outside Ghidra's current Function.body can be absent even when the
# decompiler follows that code (the legacy-Sienna boot send-key 0x54DC is a known example).
# For exhaustive security-state writer closure, confirm with `tools/g x-ref to <address>` in a
# disposable/live project and raw disassembly.
make pseudocode                          # rebuild the ignored build/out/pseudocode/*.c view for the selected target
rg 'ICUSCMD' build/out/pseudocode
rg 'f33_rdbi' build/out/pseudocode
```

## Task-oriented tooling discovery

Before writing a new one-file-per-surface script, check the consolidated
entry points below — several earlier one-off extractors and export wrappers are
now profiles or subcommands behind them, and new variants of the same operation
belong there rather than in a new top-level file:

| Operation | Entry point |
|---|---|
| Corolla target workflow discovery | `tools/toyota target list corolla` |
| Read-only exports from the selected working project (signals/consumers/producers/coverage/inventory) | `tools/project/export_ghidra_project.sh list` |
| Cross-variant image-bound evidence | `tools/toyota variant list` |
| Interactive GTS+ diagnostic / recorder schemas, OEM vocabulary and implementation routes | `tools/gts` |
| Repository knowledge across findings/corrections/OQs/artifacts/suites/docs | `tools/know QUERY` |

The three evidence/export runners expose a `list` discovery command. The
Corolla-H runner reports its profile inputs and tracked outputs; the
argument-driven variant runner reports mode purpose/input/selection semantics;
the exporter lists its profile names. `tools/gts` instead exposes task-shaped
subcommands such as `ecu`, `did`, `recorder`, `category` and `command`.
Start with the [schema-first workflow](tooling/gts-query-cli.md#schema-first-workflow)
to select the Data List or PCS recorder namespace before searching strings.
It is a discovery surface, not a proof generator. Target tests are split into
behavioral domains and selected through stable `tools/test` suite names.
Implementation locations and capability boundaries are documented in
[tooling/README.md](tooling/README.md#task-oriented-entry-points).

### RAM-resident TSS3 build and kit workflow

`data/analysis_targets.json` registers which exact firmware targets support a
maintained RAM payload. Discover that matrix instead of selecting a
vehicle-named builder:

```bash
tools/toyota ram list
tools/toyota ram list corolla
```

The maintained payload is `tss3-request-signer`. One self-selecting payload
binary implements the four-frame classic-CAN contract for every registered
Camry, Crown, and Corolla H/F target. Target builds retain separate metadata
for host bus/F181 binding, but their default payload SHA-256 is identical.

The shared resident services a pending private-ring record immediately only
while the foreground flag is clear and TAUJ0 channel 3 has more than 240,000
counts (3 ms of the 5-ms interval) remaining; it rechecks the flag before
helper entry. The complete stock foreground schedule and tick update remain
unchanged, followed by the ordinary signer call as the fallback. The builder
proves the common timer table, channel-3 reload stores, mode initializer, and
foreground machine shape in every registered CodeFlash image.

For a newly acquired 1-MiB EPS CodeFlash dump, use the dump-driven onboarding
command before adding registry metadata:

```bash
tools/toyota ram onboard path/to/CodeFlash.bin
```

The command recovers the runtime selector identity, boot transition, scheduler,
RX ring, signer ABI, private-memory layout, and MPU transit permission directly
from that dump. It reports whether the registered universal profile table
already contains the exact selector/config row; a missing row is inserted into
that candidate build before compilation. The compiled simulator ELF is reused
for separate clean-process fallback and timer-bounded idle executions against
the supplied image. The retained result contains `report.json`, the resolved
profile and build artifacts under `build/`, one simulator ELF, and per-scenario
output under a unique `build/out/ram-runtime/onboard/` directory.

Resolution is deliberately fail-closed. Missing or ambiguous machine evidence
means “not proven compatible,” not proof that the firmware can never support
the approach. CodeFlash cannot supply Panda logical-bus routing or prove
ICU-S/RSCFD, MPU enforcement, cache publication, interrupt, or timing behavior;
those remain registry/bench qualification inputs.

```bash
# Build one target. Without --out, output is under build/out/ram-runtime/TARGET/.
tools/toyota ram build camry-8965F3307000
tools/toyota ram build crown-8965F3012000 --out build/out/crown-request-signer

# Package one target, or compile once and bind target metadata for every kit.
tools/toyota ram kit corolla-8965H1202000 --out EMPTY_KIT_DIRECTORY
tools/toyota ram kit all --out EMPTY_KIT_SET_DIRECTORY
```

Explicit onboarding and kit output directories must be empty. Each kit contains
only the shared authenticated payload, host-consumed target metadata, the
common host runtime, peer recovery, and `./tss3-request-signer`; it does not
duplicate compiler intermediates or contain the historical direct-B6 runtime.
`doctor` is the explicit offline integrity/environment check; no live command
runs it implicitly. `recover-peers` keeps the kit's EPS identity exact and
binds each peer restart to the F181 observed at its topology-defined address
before reset; it does not impose Camry peer part numbers. The diagnostic bus
comes from the repinned kit metadata. Every kit also carries the UI bringup
backend (`ui-bringup`, `ui-resume`, `ui-worker`, `ui-resume-warm`) and the
startup race behind one target-neutral status protocol. Runtime buses are the
shared repinned topology (Panda bus 0) for every target; kit metadata binds
per-vehicle identity, and the registry's stock bus observations stay
provenance. The manual-arm race requires the exact `06 50 03 00 32 01 F4 00` frame constructed by every registered target's bootloader.

`install` records the application F181 once before helper activation, then
waits for a successful signer request/response. `status`, `self-test`, and the
benchmarks use that request/response path directly; post-activation EPS F181 or
SID23 availability is not required.

The optional `--codec compact` build is experimental and explicit. Omission
always selects the four-frame carrier that transports all 28 application
bytes. Run only the gate that owns the changed behavior:

```bash
# signer build, codecs, metadata consumer, and host protocol
tools/test tss3_request_signer

# complete RH850 offline pipeline: compiler ABI, generated device model,
# raw CodeFlash simulation, and exact registered-firmware scenarios
tools/test rh850

# ram_exec boot-identity transitions (transient F181, exact-boot handoff)
tools/test ram_exec_boot_transitions

# TSS3 startup-catch bringup (race matching, cancellation, native marker)
tools/test tss3_startup_bringup
```

Historical C7/B6 builders and the old Camry/Corolla packagers live only under
target `research/` namespaces. They are not alternate current build surfaces.

The `.c` tree is intentionally ignored; it can be reproduced from the tracked
JSONL without opening Ghidra. The JSONL is generated in one read-only headless
Ghidra pass rather than thousands of individual CLI calls.

Refresh the corpus only from a fresh rebuilt/disposable project whose exported
inventory is byte-for-byte equal to that target's tracked inventory baseline
(the registry `inventory_baseline`: e.g.
`data/targets/camry-8965F3307000/ghidra_project_inventory.baseline.jsonl` for
the default Camry, `data/ghidra_project_inventory.baseline.jsonl` for the legacy
Sienna). A project merely materialized
from the committed snapshot may carry Ghidra version-control state that
`analyzeHeadless -process` reports as hijacked, so use a fresh rebuild output:

```bash
make rebuild-project PROJECT_DIR="$PWD/build/work/corpus-rebuild"
make generate-decompiler-corpus PROJECT_DIR="$PWD/build/work/corpus-rebuild"
tools/test decompiler_corpus
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

Expected memory map after the common P1M-E device profile is applied:

```text
CodeFlash          00000000..000fffff  rx       imported user area
Extended user      01000000..01007fff  rx       architectural; unmapped when absent from dump
LocalRAM           febe0000..febfffff  rwx      PE1 view used by firmware
LocalRAM_self      fede0000..fedfffff  rwx      byte alias of LocalRAM
GlobalRAM_A        feef8000..feefffff  rwx
GlobalRAM_B        fef00000..fef07fff  rwx
DataFlash          ff200000..ff207fff  rw
SFR_FACI_ID        ffa08000..ffa0801f  rw volatile
SFR_FACI           ffa10000..ffa101ff  rw volatile
SFR_FACI_COMMAND   ffa20000..ffa20003  rw volatile
SFR_FACI_CONFIG    ffc59000..ffc590ff  rw volatile
SFR_ICUS           ffc5d000..ffc5dfff  rw volatile
SFR_CODEFLASH_ECC  ffc62000..ffc624ff  rw volatile
SFR_STAC           fff81000..fff81fff  rw volatile
SFR_RSCFD          ffd20000..ffd2ffff  rw volatile
SFR_ECM_*          ffd60000..ffd630ff  rw volatile, four mapped windows
SFR_TAUJ           ffe50000..ffe52fff  rw volatile
SFR_EIC            ffffb000..ffffbfff  rw volatile
```

The self Local-RAM range is a mapped alias, not a second physical allocation.
Executable flags describe architectural fetch capability; recovered MPU
permissions remain the authority for a particular runtime context. The full
high peripheral range `0xFF600000..0xFFFFFFFF` remains volatile in
`v850.pspec`, while FACI and other lower verified peripheral blocks are marked
volatile explicitly. Only evidence-backed windows are mapped: mapping every
possible SFR address makes CodeFlash immediates look like pointers and
collapses disassembly.

## Verification

Run the relevant named suite when changing executable behavior or a binary
invariant. Documentation and research notes do not need a test run.

```bash
uv sync --locked                  # one-time
tools/test                        # runs nothing; prints explicit-use guidance
tools/test <suite-or-prefix>      # run the smallest relevant suite
tools/test @exploit               # deliberate multi-suite bundle
tools/test list [query]           # discover suites
tools/test plan <query>           # preview an explicit selector
tools/test core                   # repository mechanics
tools/test full                   # explicit portable sweep
tools/test local                  # explicit external/live-project sweep
make verify                       # alias for core
make verify-sleigh                # SLEIGH compile + isolated install
make verify-processor             # processor fixtures + working-project audits
make verify-project-parity        # exact working-project inventory vs baseline
```

`verification.toml` lists suites and external prerequisites. It does not
assign tests to changed files. Broad sweeps and Ghidra rebuilds are release or
diagnostic tools, not a per-edit checklist.

A permanent test needs a plausible failure: wrong decoding, lost data,
incorrect state transitions, malformed-input handling, or a critical binary
invariant. Assertions about prose, source spelling, copied constants, incidental
counts, or a generator's own hash do not establish those properties.

## Rebuilding the complete project from firmware

The committed split images are the only firmware inputs. Every rebuild driver
checks the selected target's registered identity — `codeflash_sha256`,
`dataflash_sha256`, sizes, and bases from `data/analysis_targets.json` — and
aborts on drift before touching a project. The hashes below are the legacy
Sienna reference pair (registry target `sienna-8965B4512000`); every first-class
target carries its own committed identities in the same registry:

```text
Sienna DataFlash  81d87b678784bb2a07b1fdcb3d43dd40767d4f5ca1b56867b6575cd652a9ecb8
Sienna CodeFlash  21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde
Sienna Combined   0bba74d0e443f9dd3da33e3a28c3511ec31e35e8303acef7e0117fbdc91d5a86
```

The Sienna CodeFlash input is preserved exactly as published. SECOC-044
(Sienna-scoped) recovers a
unique one-bit inconsistency at VA `0xBB1C4` (`0xA2→0x82`) whose analysis-only
reconstruction restores the existing region-1 boot CRC and repairs the local
RH850 store semantics; reconstructed CodeFlash SHA-256 is
`b6f510662c324261dac6fc1504ec77c217d2055dc099096375a91f3fcf7e9916`.
Do **not** silently patch any committed firmware input or rebuild a canonical
project from a reconstructed derivative; use reconstructions only for
explicit CRC/semantic experiments.

```bash
make rebuild-project                                  # registry-default Camry work path
make rebuild-project PROJECT_DIR="$PWD/build/work/parity-project"  # disposable alternate
make rebuild-project TARGET=sienna-8965B4512000       # legacy Sienna, specialized script
```

Rebuild destinations are deliberately constrained to dedicated directories
below `build/work/`; this keeps `--force` incapable of deleting committed or
unrelated trees. The legacy Sienna keeps its mature specialized rebuild script;
direct invocation
`tools/project/rebuild_project.sh --project-dir "$PWD/build/work/project" --force`
is the `make rebuild-project TARGET=sienna-8965B4512000` path plus forced
replacement of an existing project. Never point any rebuild at committed
`projects/`; promote only with `make snapshot-project`.

The legacy Sienna rebuild consumes the tracked diagnostic-vocabulary artifact
by default; an ignored local Techstream tree is never an implicit input. To
deliberately refresh that artifact first, pass `--refresh-diagnostic-vocabulary`
and review its tracked diff before promotion. Registered first-class target
rebuilds do not consume the vocabulary artifact.

All repository one-shot Ghidra jobs go through `tools/project/run_headless`. It owns
the isolated environment, canonical project-path guard, canonical script path,
CPU/time limits, logs, and `REPORT SCRIPT ERROR` detection. Do not duplicate a
raw `analyzeHeadless` command in another script. The canonical script path
deliberately excludes `ghidra/scripts/investigate`: including that directory was
measured to change the recovered graph by 194 functions. Deterministic exporters
used by tooling live under `ghidra/scripts/verify` instead.

### The staged rebuild analyses (do not collapse)

The legacy Sienna rebuild script uses four staged durable analysis commits plus
a separate `-noanalysis` calling-convention finalizer. Staging matters: injecting every
seed before the first analysis pass produces a different graph and does not
reproduce the committed statistics.

1. Import CodeFlash without analysis, map DataFlash with `AddDataFlash.java`,
   apply `ApplyP1MDeviceProfile.java` (LocalRAM/SFR windows, GP/TP, SFR labels
   from `data/p1m_sfr_labels.csv`), `ApplyP1MSfrTypes.java` (EIC/RSCFD/ICU-S
   overlays), `ApplyRamTypes.java` (LocalRAM payload/SecOC/DID/checkpoint
   overlays from `data/checkpoint_payload_map.csv`).

Registered first-class rebuilds run the same common import — `AddDataFlash`,
the P1M-E device profile, and `ApplyP1MSfrTypes` — plus the target's registered
context script (`device_profile_script`, e.g. `ApplyCamryF33DeviceProfile.java`),
then stage their registered seed scripts (`entry_seed_script`,
`diagnostic_seed_script`, `recovered_seed_script`, plus the target's
`function_seeds` CSV) as their own durable analysis commits, and end with the
same `-noanalysis` `ApplyCallingConventions` finalizer. Exact-target scripts do
not maintain a second hardware map.

2. Run `SeedEntries.java`, then the base auto-analysis.
3. Run `SeedUdsServiceTable.java`, re-run analysis.
4. Seed remaining missed functions (`SeedCanTransportFunctions`,
   `SeedPayloadVerificationFunctions`, `SeedSecocNvmFunctions`,
   `SeedSecocApplicationFunctions`, `SeedDataFlashSemanticsFunctions`,
   `SeedApplicationDiagnosticFunctions`, `SeedDidCallbacks`,
   `SeedBootloaderDiagnosticFunctions`, `SeedArchitectureFunctions`,
   `SeedApplicationTransmitFunctions`, `SeedApplicationReceiveFunctions`,
   `SeedRecoveredCallbackTables`, `SeedDispatchProvenFunctionTables`,
   `SeedBoundedPointerWrappers`, `SeedDirectCallTargets`), re-run
   analysis, apply every annotation script (`AnnotateBootloaderSecrets`,
   `AnnotatePayloadGate`, `AnnotateSecocNvmCorrection`,
   `AnnotateSecocApplication`, `AnnotateDataFlashLayout`, `AnnotateDidModel`,
   `AnnotateCanTransport`, `AnnotateApplicationDiagnostics`,
   `ApplyDiagnosticVocabulary`/`AssertDiagnosticVocabulary` when a tracked
   vocabulary artifact exists, `AnnotateControlPartition`,
   `AnnotateBootloaderDiagnostics`, `RecoverVectorHandlers`,
   `RecoverSwitchTables`, `AnnotateArchitecture`,
   `AnnotateApplicationTransmit`, `AnnotateApplicationReceive`,
   `AnnotateLargeFunctions`, `ApplyCallingConventions`), then replay the
   tracked mechanical annotation ledger with `ApplyAnnotationLedger`.
5. `-noanalysis` convention finalizer: re-run `ApplyCallingConventions.java`.
   After the annotate-stage reopen, Ghidra surfaces two additional non-ISR
   bodies (`0x3b0be`, `0x6f0d0`) that stage 4 never saw; without the finalizer
   they stay `unknown`. The finalizer also covers explicitly seeded functions
   added by later subsystem work.
6. Open the result through the CLI, record statistics, cleanly stop the daemon.
7. Record the processor build used and check the recovered memory map.
8. Export canonical compact JSONL and compare every semantic record with that
   target's tracked baseline — for the legacy Sienna rebuild,
   `build/out/ghidra_project_inventory.jsonl` against
   `data/ghidra_project_inventory.baseline.jsonl`; for a first-class target,
   `build/out/targets/<target>/project_inventory.jsonl` against the registry
   `inventory_baseline`. The path-free inventory
   covers tool/program identity, memory mappings, complete function bodies and
   signatures/storage, user symbols, comments, bookmarks, and aggregate maps;
   it catches equal-count substitutions and annotation drift that floors miss.

When a deliberate seed/annotation change alters the inventory, run
`make update-project-baseline PROJECT_DIR_A=/abs/rebuild-a
PROJECT_DIR_B=/abs/rebuild-b`. The update fails unless two independent fresh
rebuilds produce byte-identical canonical inventories. Review the tracked diff,
then rerun `make verify-project-parity`. Ordinary verification never updates the
baseline.

The whole-image corpus is the decompilation source; use `tools/pseudo` to read
functions. `data/semantic_review_status.csv` retains human review conclusions.
The semantic coverage/ranking tools provide navigation, not additional proof.

## CI

Normal push/PR CI runs the small `make verify` core suite. The exhaustive
portable `make verify-full` sweep is scheduled/manual. Processor-path PRs run
SLEIGH, synthetic fixtures, and committed-project audits on macOS with pinned
Ghidra 12.1.4 / ghidra CLI 0.2.1; the processor/rebuild/CLI jobs also remain
available on scheduled/manual runs. Ordinary source, evidence, and documentation
commits do not trigger the four-stage Ghidra rebuild. The 12.1.3 -> 12.1.4
migration was verified by two independent clean rebuilds of every registered
target and changed no canonical semantic record; see
[the migration journal](history/2026-09/GHIDRA_12_1_4_MIGRATION_2026-09-21.md).
