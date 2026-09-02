# Agent instructions

Operating contract for changing this repository. What the firmware *is*:
`docs/OVERVIEW.md`. How to run the tooling: `docs/WORKFLOW.md`.

## Source-of-truth hierarchy

1. **Firmware bytes and deterministic verification** (`firmware/`, `tests/`)
2. **Generated artifacts** (`data/` generated CSVs — regenerate, never hand-edit)
3. **Curated evidence tables** (`data/` hand-maintained CSVs — edit intentionally, validate with tests)
4. **Annotated Ghidra project** (`project/` committed snapshot)
5. **Narrative documentation** (`docs/`), then historical notes (`docs/status/CORRECTIONS.md`)

The firmware is the single source of truth; the docs are falsifiable
approximations. For firmware/vehicle-behavior questions, go to the Ghidra CLI
against the binary first (`tools/g`, `tools/pseudo`) — never read our own
docs/tests as primary sources. Naming a function without decompiling it is
slop; verify firmware claims from gate code, not spec knowledge.

For **openpilot/comma integration-design questions** the priority reverses:
current upstream openpilot/opendbc/Panda is the design reference. Firmware
evidence defines only what is genuinely target-specific (wire format, buses,
scaling, limits, capabilities, actual incompatibilities) — it is not an
invitation to add policy. -- The goal is native openpilot/comma integrattion.

## Non-negotiable hazards

- **Never open committed `project/` or `projects/` with a Ghidra daemon** — any
  open compacts the DB and dirties the tree. Work in `build/work/project/`
  (`make work-project`).
- **Never commit while a daemon runs** (it holds transient `.lock`/`tmp*`
  files), and always `tools/g stop` before copying or snapshotting the working
  project — only clean teardown persists edits durably. Confirm
  `pgrep -f 'AnalyzeHeadless.*rh850'` is empty before snapshotting.
- **Never point a rebuild at `project/` or `projects/`.** Promote only with
  `make snapshot-project` (end of session: `make finalize-project`).
- **SIENNA CodeFlash VA = file offset − `0x8000`** (DataFlash prefix).
- **`build/` is workspace state, never evidence authority.** Portable
  verification must pass without it; promote any input verification depends on
  to a tracked location first.
- **Do not collapse the four-stage rebuild** — seed timing changes Ghidra's
  recovered graph (docs/WORKFLOW.md §"The four-stage analysis").

## Snapshot policy

Direct CLI mutations are exploratory. Anything persistent — renames, function
creation, signatures, types, comments, overlays — must be represented in
tracked rebuild inputs before snapshotting: `tools/annotations` /
`data/annotations/annotation_ledger.jsonl` for mechanical renames, data
labels, and listing comments; seed/annotation scripts for semantic recovery.

## Tools

Remember task commands, not implementation files:

| Task | Command |
|---|---|
| Edit-loop tests | `tools/test` (dirty + untracked vs HEAD; clean tree exits 0) |
| Discover / preview suites | `tools/test list [query]`, `tools/test plan [changed\|branch\|query]` |
| Ghidra / pseudocode | `tools/g`, `tools/pseudo` |
| GTS+ / Toyota vocabulary / CUW routes | `tools/gts` |
| Repository knowledge (findings, corrections, open questions) | `tools/know QUERY` |
| Generated artifacts / producers / owners | `tools/artifact list/show/regen/check` |
| Registered analysis targets | `tools/gtarget list`, `tools/gtarget show TARGET` |
| Evidence compaction / variant extraction / project exports | `tools/extract_corolla_h_evidence.py list`, `tools/extract_variant_evidence.py list`, `tools/export_ghidra_project.sh list` |

`tools/gtarget TARGET ...` (and wrappers such as `tools/gcamry`) run Ghidra
commands against a configured target. Registered rebuild inputs, stage
scripts, image identities, and corpus paths live in
`data/analysis_targets.json`; generic target tooling must not bake in
vehicle-specific paths.

Daily commands: `uv sync --locked` (one-time), `tools/test`, `tools/test core`,
`make verify-core`. The full gate surface (`branch`, `@exploit`,
`verify-full`, `verify-local`, `verify-sleigh`, `verify-processor`, …) is
enumerated in `docs/WORKFLOW.md` §Verification — don't recreate it as Make
wrappers or new registries; `verification.toml` and the discovery commands
above are the source of truth.

### tools/g (interactive Ghidra)

`tools/g` is fully self-contained — it bootstraps the isolated processor
environment and materializes the working project itself. **Never** `source
build/cache/ghidra-processor.env` manually.

```bash
tools/g decompile 0x8db22
tools/g inspect 0xc853a --decompile --callers --callees --xrefs --disasm 40
tools/g x-ref trace-to 0xfebef02a --disasm 20
printf 'stats\nquery functions --count\n' | tools/g batch --read-only -
tools/g session-status   # daemon state, mutation marker, snapshot diff
tools/g stop             # persist working-copy edits (does NOT promote)
```

It refuses committed `project/`/`projects/` namespaces. `GHIDRA_AGENT=1`
gives compact JSON output. To promote a finished working copy into the
committed snapshot, use `make finalize-project`.

### tools/pseudo (persistent decompiler corpus)

Use the tracked whole-image corpus for broad reading, search, and
cross-function reasoning before dropping to individual CLI calls:

```bash
tools/pseudo 0x6fec
tools/pseudo security_access --list
tools/pseudo --data-ref 0xfebef02a   # canonical RAM xrefs, alias-independent
make pseudocode                      # materialize build/out/pseudocode/*.c
```

`data/generated/decompilations.jsonl` is derived evidence, not firmware
truth: pseudocode for understanding, xrefs/dataflow for tracing,
disassembly/bytes for proof. Prefer `--data-ref` over grepping decompiler
spelling. After any graph, naming, type, calling-convention, or processor
semantic change, regenerate with `make generate-decompiler-corpus` against a
fresh rebuilt project that exactly matches the canonical inventory.

All one-shot Ghidra execution goes through `tools/run_headless`.

## Evidence language

Grades (full definitions and ledger in `docs/status/FINDINGS.md`):
**verified** (asserted by a deterministic test), **observed** (directly
observed, not test-reproduced), **recovered** (flow substantially
reconstructed), **bounded** (interpretation constrained, exact semantics
unknown), **hypothesis** (plausible, unverified), **disproved** (retained to
prevent regression). Keep the evidence **source** (`firmware-static` /
`dynamic-probe` / `generated-artifact` / `external-source`) distinct from
confidence.

## Openpilot integration: native-shape rule

Canonical contract: [docs/architecture/toyota-openpilot-porting-contract.md](docs/architecture/toyota-openpilot-porting-contract.md).
Operating summary:

- Start from current upstream comma/openpilot and make the **smallest
  target-specific change** required to support the car. The burden of proof is
  on a deviation from upstream, never on re-proving upstream behavior from
  firmware.
- Keep normal ownership boundaries: `controlsd` owns engagement and
  `CC.latActive`; `CarInterface`/`CarParams` describe the vehicle;
  `CarState` decodes; `CarController` encodes; Panda applies the ordinary
  safety model and TX whitelist. No second permission system, no
  controller-side steering vetoes, no Panda enforcement of receiver behavior,
  no request/status bit promoted to an authority signal without proof.
- No speculative safety policy: unknown target semantics stay unmapped or use
  the normal upstream mechanism — never a guard, timer, threshold, interlock,
  special Param, debug mode, or alternate state machine "just to be safe."
- The F33 bring-up experiments (private lateral-arming Params, fake SecOC-key
  availability, diagnostic/oracle arming, `ALLOW_DEBUG` shadow-safety modes,
  dynamic harness modes, controller-side permission vetoes, Panda `0x00F`/B6
  sequence/`0x08A` gates, template-wide required-zero checks, global Toyota
  changes for this one target) were scaffolding, not architecture. Keep them
  out of the normal driving path unless an actual upstream-equivalent
  requirement is later proven.

Before adding any Camry/TSS3-specific runtime branch, search current upstream
for how the same feature is normally implemented; if the normal mechanism
works, use it.

## Documentation

A **material new RE conclusion** (firmware, vehicle protocol, observed target
behavior) gets exactly one home: update the canonical subsystem report, and
record the claim — scope, grade, verifying test when established — in
`docs/status/FINDINGS.md`. Disproved prior durable claims go to
`docs/status/CORRECTIONS.md`. Add a deterministic test only when it protects
a real recovered fact worth preserving.

Routine work — refactors, upstream-shape alignment, deleting experimental
scaffolding, ordinary fixes — requires no manufactured finding or proof
artifact. Document it where normal software work would be: code, tests that
protect actual behavior, and the commit message.

## Scope discipline

- Findings are specific to their individual calibration until proven
  otherwise; record transfers as **hypothesis** in `docs/variants/`.
- Do not project application-mode or related-variant probe expectations onto
  the bootloader DID table (or vice versa).
- Do not invent OEM field names unavailable in the firmware; use bounded
  structural names.
- Don't prematurely declare a path "not security-relevant" — thorough
  reference analysis serves all future RH850 vehicles.

## Navigation

- Operating manual: [docs/WORKFLOW.md](docs/WORKFLOW.md)
- Documentation map: [docs/README.md](docs/README.md)
- Current priorities: [docs/status/PRIORITIES.md](docs/status/PRIORITIES.md)
- Ledgers: [docs/status/FINDINGS.md](docs/status/FINDINGS.md) · [docs/status/CORRECTIONS.md](docs/status/CORRECTIONS.md) · [docs/status/OPEN_QUESTIONS.md](docs/status/OPEN_QUESTIONS.md)
- Cross-reference index: [docs/reference/index.md](docs/reference/index.md)
- Historical journals: [docs/history/README.md](docs/history/README.md)
