# Agent instructions

Operating contract for changing this repository. For what the firmware *is*,
read `docs/OVERVIEW.md`. For how to run the tooling, read `docs/WORKFLOW.md`.
This file is only what an agent must **obey** while working here.

## Source-of-truth hierarchy

1. **Firmware bytes and deterministic verification** (`firmware/`, `tests/`)
2. **Generated artifacts** (`data/` generated CSVs — regenerate, never hand-edit)
3. **Curated evidence tables** (`data/` hand-maintained CSVs — edit intentionally, validate with tests)
4. **Annotated Ghidra project** (`project/` committed snapshot)
5. **Narrative documentation** (`docs/` subsystem reports)
6. **Historical notes** (`legacy/`, superseded claims in `docs/status/CORRECTIONS.md`)

THE DOCS ARE NOT A PRIMARY SOURCE. THEY ARE AN APPROXIMATE EXPLANATION BASED
ON FINDINGS UP TO THIS POINT. THEY ARE FALSIFIABLE. THE FIRMWARE IS THE SINGLE
SOURCE OF TRUTH.

Use Ghidra CLI tools against the binary FIRST — never read our own docs/tests
as primary sources. `query functions --count`/`--sort -size` for census;
`decompile`/`x-ref`/`disasm` for analysis. Heuristic function naming without
decompiling is slop. Verify claims from firmware gate code, not spec knowledge.

## Non-negotiable repository hazards

- **Never open committed `project/` with a `ghidra` daemon.** Any open
  compacts its DB and dirties the tree even with no analysis change. Use
  `build/work/project/` (via `make work-project`).
- **Always `ghidra ... stop` before copying or committing the working
  project.** The daemon holds edits in memory; only teardown commits durably.
  Confirm `pgrep -f 'AnalyzeHeadless.*rh850'` is empty before snapshotting.
- **Never commit while a daemon is running** — it holds transient `.lock` /
  `tmp*` files.
- **Never infer CodeFlash VA without accounting for the DataFlash prefix.**
  CodeFlash VA = file offset − `0x8000`.
- **Never point a rebuild at committed `project/`.** Promote only with
  `make snapshot-project`.
- **`build/` is workspace state, never evidence authority.** Core `make verify`
  must pass without it. Use only `build/cache/`, `build/work/`, `build/out/`,
  `build/logs/`, and `build/tmp/`; promote any input that verification depends on
  into a tracked repository location first.
- **Do not collapse the four-stage rebuild.** Seed timing changes Ghidra's
  recovered graph. See `docs/WORKFLOW.md` §"The four-stage analysis".
- **`legacy/flat-import/` is historical only.** Do not use it for current
  results.

## Snapshot policy

Direct CLI mutations are exploratory. Any persistent rename, function
creation, signature, type, comment, or overlay must be represented in a
seed/annotation script before snapshotting. Only the designated integration
task updates `project/` (via `make snapshot-project`).

## Standard commands

```bash
uv sync --locked          # one-time environment
make verify               # firmware evidence, no Ghidra — run this first
make verify-one SUITE=control_partition  # one subsystem suite (fast iteration)
make verify-changed       # suites matching git changes only
make verify-agent         # all suites, compact JSON summary
make verify-required-external # require the pinned Techstream corpus
make ghidra-cli           # build the vendored ghidra CLI into build/cache/ghidra-cli/
make verify-sleigh        # SLEIGH compile + isolated install
make verify-processor     # fixtures + asserting audits on build/work/project/
make snapshot-project     # the ONLY path that mutates committed project/
make finalize-project     # stop daemon, verify, snapshot, print diff (end-of-session)
make build-status         # namespace sizes + legacy top-level build entries
make clean-build          # safe cleanup: build/logs + build/tmp only
# Explicit legacy quarantine (dry-run first):
uv run --locked python tools/build_layout.py migrate-legacy
```

### Interactive Ghidra via tools/g

`tools/g` is fully self-contained — it bootstraps the isolated processor
environment internally. **Never** `source build/cache/ghidra-processor.env` manually;
the wrapper handles it.

```bash
tools/g decompile 0x8db22
tools/g x-ref to 0x8db22
tools/g inspect 0xc853a --decompile --callers --callees --xrefs --disasm 40
tools/g script run ghidra/scripts/investigate/Foo.java -- arg1
tools/g session-status
tools/g stop
```

`tools/g` resolves the repo root, bootstraps the isolated Ghidra environment
(processor extension, Java options, fingerprint check), materializes the
working project if absent, selects the pinned CLI binary, and injects
`--projects-dir/--project/--program`. It refuses to operate against committed
`project/`. Set `GHIDRA_AGENT=1` for compact JSON output.

`tools/g session-status` reports daemon state, project path, processor
fingerprint, mutation marker, and snapshot diff — useful before deciding
whether to promote.

`tools/g stop` persists working-copy edits only. To deliberately promote a
finished working copy into the committed snapshot, use `make finalize-project`.

### Persistent pseudocode corpus

Use the tracked whole-image decompiler corpus for broad reading, search, and
cross-function reasoning before dropping to individual CLI calls:

```bash
tools/pseudo 0x6fec
tools/pseudo security_access --list
tools/pseudo secoc --all
tools/pseudo --data-ref 0xfebef02a # canonical RAM xrefs, independent of decompiler aliases
make pseudocode                    # materialize build/out/pseudocode/*.c from the tracked corpus
rg 'ICUSCMD' build/out/pseudocode
```

`data/generated/decompilations.jsonl` is derived evidence, provenance-locked to
`data/ghidra_project_inventory.baseline.jsonl`. Each function also carries the
canonical non-flow instruction/data-reference graph exported by Ghidra. Use
`tools/pseudo --data-ref ADDRESS` instead of grepping decompiler spelling when a
RAM byte may appear as `DAT_base._n_m_` or `LAB_base + offset`. It is not firmware
truth. Use pseudocode for understanding, xrefs/dataflow for tracing, and
disassembly/bytes for proof. After any graph, naming, type, calling-convention, or processor
semantic change, regenerate it with `make generate-decompiler-corpus` against a
fresh rebuilt project that exactly matches the canonical inventory (not merely
a snapshot-materialized project that Ghidra may report as hijacked).

All repository one-shot Ghidra execution goes through `tools/run_headless`,
which owns environment setup, path rejection, script paths, logging, and script
error detection. The only intentional raw `analyzeHeadless` call is the
negative regression in `tools/verify_sleigh.sh` proving `project/` cannot open.

## Evidence language

Use these confidence grades in any finding you record (definitions and full
ledger in `docs/status/FINDINGS.md`). Evidence also carries a **source**
(`firmware-static` / `dynamic-probe` / `generated-artifact` /
`external-source`) — keep it distinct from confidence:

- **verified** — directly asserted by a deterministic test;
- **observed** — directly observed (e.g. a field probe) but not reproduced by a repository test;
- **recovered** — control/data flow substantially reconstructed;
- **bounded** — interpretation constrained, exact semantics unknown;
- **hypothesis** — plausible, explicitly unverified;
- **disproved** — retained only to prevent regression.

## Documentation requirements

When you produce a material conclusion:

1. **Update the canonical subsystem report** — every claim has exactly one
   home. Other documents summarize it in one sentence and link there.
2. **Update `docs/status/FINDINGS.md`** with the claim, scope, grade, and
   verifying test.
3. **Add or update a deterministic test** in `tests/` where possible.
4. **Record any disproved prior claim** in `docs/status/CORRECTIONS.md`.
5. **Keep this file slim** — never duplicate long findings lists here. Link to
   the canonical report instead.
6. **When the requested task includes updating the repository**, persist durable
   findings in the appropriate report and tests before reporting completion.
   Do not modify or commit files during review-only tasks.

## Scope discipline

- Findings are specific to the Sienna `8965B4512000` calibration. Do not
  project them onto the Corolla or the wider TSS 3 family as fact — record
  transfers as **hypothesis** in `docs/variants/`.
- Do not project application-mode or related-variant probe expectations onto
  the bootloader DID table (or vice versa).
- CAN `0x344` is absent from this image. Do not re-introduce it from
  related-variant expectations.
- Do not invent OEM field names unavailable in the firmware; use bounded
  structural names.
- Don't prematurely declare a path "not security-relevant" — thorough
  reference analysis serves all future RH850 vehicles.

## Navigation

- Operating manual: [docs/WORKFLOW.md](docs/WORKFLOW.md)
- Documentation map: [docs/README.md](docs/README.md)
- Current priorities: [docs/status/PRIORITIES.md](docs/status/PRIORITIES.md)
- Findings ledger: [docs/status/FINDINGS.md](docs/status/FINDINGS.md)
- Open questions: [docs/status/OPEN_QUESTIONS.md](docs/status/OPEN_QUESTIONS.md)
- Corrections: [docs/status/CORRECTIONS.md](docs/status/CORRECTIONS.md)
- Historical journals: [docs/history/README.md](docs/history/README.md)
