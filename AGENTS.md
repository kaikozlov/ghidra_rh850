# Agent instructions

Stable operating contract for this repository. Project scope and evidence model:
[docs/OVERVIEW.md](docs/OVERVIEW.md). Commands and lifecycle:
[docs/WORKFLOW.md](docs/WORKFLOW.md). Report navigation:
[docs/README.md](docs/README.md).

## Source-of-truth hierarchy

1. **Primary evidence and deterministic verification** — exact firmware bytes
   for firmware behavior; identity-bound captures for observed vehicle behavior;
   tests establish only the behavior or binary invariant they exercise.
2. **Generated artifacts** — regenerate from their inputs; never hand-edit.
3. **Curated evidence tables** — edit intentionally; validate relevant executable
   or binary invariants, not incidental prose or metadata.
4. **Annotated Ghidra projects** — committed snapshots for the selected target.
5. **Narrative documentation and historical ledgers** — interpretations, not proof.

For firmware questions, inspect the exact target through `tools/gtarget` /
`tools/pseudo` before making a claim. Decompile a function before naming its role;
verify important gates from disassembly/bytes and dataflow, not spec knowledge
or our own tests/docs. Static firmware analysis alone does not prove physical
vehicle behavior. Captured observations retain their software, harness, clock,
and operating-state boundaries.

For openpilot/comma integration design, **current upstream openpilot/opendbc/Panda**
is the reference. Firmware defines genuinely target-specific constraints, not
an invitation to add policy. A pinned historical comparison is not current upstream.

Keep confidence separate from evidence source. Use **verified**, **observed**,
**recovered**, **bounded**, **hypothesis**, and **disproved** as defined in
[FINDINGS.md](docs/status/FINDINGS.md#evidence-model).
Code implemented, offline checks passed, software deployed, and vehicle behavior
observed are different claims; never use one as a substitute for another.

## Non-negotiable hazards

- **Never open committed `projects/` with Ghidra.** Opening compacts the database.
  Work only in the selected target's registered `build/work/` path.
- **Stop the relevant daemon before copying or promoting its working project.**
  Only clean teardown persists in-memory edits durably. Ordinary source/docs
  commits are safe while daemons run: working databases and locks are ignored.
  Confirm each promoted project's daemon has stopped; use the global
  `pgrep -f 'AnalyzeHeadless.*rh850'` check only when ownership is ambiguous.
- **Never rebuild into `projects/`.** Use the documented `make work-project`,
  `make rebuild-project`, and `make snapshot-project` / `make finalize-project`
  lifecycle for the selected target.
- **Do not collapse the four-stage rebuild.** Seed timing changes Ghidra's
  recovered graph; follow [the workflow](docs/WORKFLOW.md).
- **Sienna's `−0x8000` offset applies only to its DataFlash-prefixed combined
  image.** The split CodeFlash file starts at CodeFlash VA zero. Other targets
  use their own registered bases and image layouts.
- **`build/` and `REFERENCE/` are workspace/context, never evidence authority.**
  Portable checks must not require pre-existing ignored inputs. Promote required
  evidence deliberately; keep external-corpus checks explicitly gated.
- Preserve committed firmware and raw captures. Correct an interpretation or
  create an explicitly identified derivative; never silently repair source bytes.

## Target selection and tools

`data/analysis_targets.json` owns the default target, image identities, paths,
rebuild inputs, inventories, and decompiler corpora. Discover before selecting
an address; never assume the default is Sienna or transfer an address by family
name. Name the target explicitly in address-based documentation examples.

| Task | Public command |
|---|---|
| Discover target identity and paths | `tools/gtarget list`, `tools/gtarget show TARGET` |
| Ghidra against the default target | `tools/g decompile ADDR`, `tools/g inspect ADDR --decompile --callers --disasm 40`, `tools/g session-status`, `tools/g stop` |
| Ghidra against an explicit target | `tools/gtarget TARGET ...` |
| Read a tracked corpus | `tools/pseudo --target TARGET QUERY`, `tools/pseudo --target TARGET --stats` |
| Discover / preview verification | `tools/test list [query]`, `tools/test plan SELECTOR` |
| Run selected verification | `tools/test SELECTOR` |
| RH850 compilation / instruction simulation | `tools/rh850` |
| GTS+ / Toyota vocabulary / CUW evidence | `tools/gts` |
| Toyota capability / workflow discovery | `tools/toyota capabilities`, `tools/toyota target list FAMILY`, `tools/toyota variant list` |
| Findings, questions, and report lookup | `tools/know QUERY` |
| Generated artifact / producer discovery | `tools/artifact list`, `tools/artifact show ARTIFACT`, `tools/artifact regen ARTIFACT` |

`TARGET`, `QUERY`, `SELECTOR`, `FAMILY`, and `ARTIFACT` above are arguments, not
literal example values. Prefer these task commands over implementation filenames.
`tools/know` is navigation, not an evidence oracle.

Run `uv sync --locked` for the editable Python installation. Use normal package
imports and `tools.REPO_ROOT` for repository-owned files; do not add `sys.path`,
`PYTHONPATH`, or fixed-file dynamic-import bootstraps to packaged tooling/tests.
Keep caller-relative paths distinct from repository-owned inputs; a one-off
analysis script loading an explicitly passed external checkout (e.g. an
openpilot root) through `sys.path` is caller input, not repository-owned
importing. The documented
repository-root dispatch behavior of `tools/toyota` and `tools/artifact regen`
is intentional.

`tools/g` bootstraps the isolated Ghidra environment and working project itself.
Never manually source `build/cache/ghidra-processor.env`. `GHIDRA_AGENT=1` selects
compact JSON. Use the target's session status and clean `stop` before promotion.
All one-shot Ghidra execution goes through `tools/project/run_headless`.

The registered decompiler corpus is derived evidence: pseudocode for understanding,
xrefs/dataflow for tracing, disassembly/bytes for proof. Prefer `--data-ref` to
grepping decompiler spelling, but it is not an exhaustive live-xref census.
After graph, naming, type, calling-convention, or processor-semantic changes,
regenerate the selected target's corpus from a fresh rebuild matching its
canonical inventory. Commands and prerequisites belong in `docs/WORKFLOW.md`.

## GTS+ schema-first investigation

Start with the [schema-first workflow](docs/tooling/gts-query-cli.md#schema-first-workflow)
and `tools/gts --help`, before broad string/PE searches.

- Use `ecu` / `category` / `command` for table and consumer routing, and `did`
  for ECU Data List/alternate snapshot rows, reference keys, scaling and enums.
- Use `recorder` for the recovered PCS TSS3/ADU field schemas. An empty `did`
  lookup does not establish that a recorder field is unknown.
- Follow existing schema producers and decoder consumers before proposing a
  new parser or declaring a recovery gap. Inspect support bits, invalid values
  and source identity along with the field name.
- Keep diagnostic, recorder and CAN namespaces distinct. A matching name or
  number is not a wire join. Check whether focus lists affect decoding,
  acquisition, or both.

## Snapshot policy

Direct CLI mutations are exploratory. Persistent renames, functions, signatures,
types, comments, and overlays must be represented in tracked rebuild inputs
before snapshotting.

- The existing `tools/annotations` / `data/annotations/annotation_ledger.jsonl`
  mechanism is **legacy-Sienna-only**: mechanical renames, labels, and listing
  comments. It is not a generic multi-target annotation service.
- Other registered targets use their target-specific seed/annotation scripts.
  Semantic recovery belongs in those scripts, not a mechanical ledger.

See [annotation ownership](docs/tooling/annotation-ledger.md) and the
[project lifecycle](docs/WORKFLOW.md) before recording or promoting edits.

## Testing

Verification is **explicit and narrow**. Bare `tools/test` runs nothing.
Discover and preview the smallest selector that exercises the changed code or
evidence. `verification.toml` owns suite selection and prerequisites; do not
create another registry or Make wrapper layer.

- Permanent tests protect plausible consumer-visible failures, parsing boundaries,
  state transitions, artifact regeneration, or fragile machine-level invariants.
- Do not test Markdown wording, ledger IDs, source spelling, copied constants,
  incidental counts, import wiring, or mock echoes. Remove obsolete checks rather
  than repinning them to a refactor.
- Exercise changed behavior, not merely compilation or a mocked success path.
  Use a bounded offline/throwaway smoke when a permanent regression adds no value.
  Do not turn verification into an unrequested live vehicle experiment.
- Documentation-only, ledger, provenance-metadata, and research-note edits need
  **no test suites**. Check changed links and benign command examples instead.
- `full`, `local`, processor/SLEIGH gates, and external-corpus sweeps are deliberate
  milestone/debugging tools, not the edit loop.

Report only checks actually run and their evidence limits. A passing suite is
not whole-project correctness, a hardware result, or production qualification.

## Implementation discipline

- Find the existing owner before adding a file, helper, command, or abstraction.
  Reuse capability/target namespaces; preserve the short public command surface.
- Consolidate repeated mechanics where they are genuinely shared. Keep calibration
  addresses, scaling, timing, and interpretation local. Do not replace duplication
  with a giant utility module, plugin system, or speculative framework.
- Use the existing target registry, verification configuration, and derived artifact
  catalog. Do not create parallel manifests or manually maintained copies of facts
  already available from code or evidence.
- Make the requested change, not adjacent retries, guards, telemetry, policy, or
  future-proofing. A new abstraction needs a concrete responsibility or real reuse.
- On a cutover, migrate callers and remove obsolete code, aliases, forwarding
  modules, comments, and instructions. Do not retain compatibility scaffolding
  without an actual supported consumer.
- Trace consumers before deleting dated experiments or outputs. Age is not
  redundancy; distinct evidence must not disappear in a cosmetic cleanup.

## Openpilot integration: native-shape rule

Follow [the porting contract](docs/architecture/toyota-openpilot-porting-contract.md).
Before adding a target-specific branch, find how current upstream implements
the same feature; use that mechanism when it works.

- Make the smallest demonstrated target-specific change. The burden of proof is
  on a deviation from upstream, not on re-proving upstream behavior from firmware.
- `controlsd` owns engagement and `CC.latActive`; `CarInterface`/`CarParams`
  describe the vehicle; `CarState` decodes; `CarController` encodes; Panda applies
  the ordinary safety model and TX whitelist.
- No second permission system, controller-side steering veto, or Panda replica
  of receiver behavior. Do not promote a request/status bit to authority without proof.
- Unknown semantics stay unmapped or use the normal upstream mechanism. Do not
  invent a guard, timer, threshold, interlock, Param, or alternate state machine
  “just to be safe.”
- Experimental arming, fake capability flags, and debug-only safety paths are
  not architecture. Do not promote bring-up scaffolding into the normal driving path.

## Documentation and scope discipline

- Keep one owner for each conclusion: the existing target/subsystem report.
  README is onboarding/navigation; OVERVIEW is scope/evidence; WORKFLOW owns
  commands; PRIORITIES is a short queue. Do not copy runtime status into all four.
- Identify the target and relevant revision/capture checkpoint when recording an
  implementation or result. “Current” inside an old audit is not today's software.
  An architecture change does not inherit the previous configuration's road result.
- When a conclusion or interface is superseded, replace competing present-tense
  summaries and repair incoming links. Retain useful historical observations with
  explicit scope; do not append another contradictory “current-state” paragraph.
- Do not create a new report, checklist, handoff, provenance manifest, or progress
  journal when an existing owner suffices. Keep source hashes/commits when required
  to reproduce a result, not as incidental decoration.
- FINDINGS, CORRECTIONS, and OPEN_QUESTIONS are historical/navigation aids, not a
  transaction log or a guaranteed-current mirror. Do not interrupt active RE to
  manufacture ledger rows, verification owners, cross-reference footers, or prose tests.
- Findings remain calibration-specific; transfers start as **hypothesis**.
  Keep bootloader/application modes separate and use bounded structural names
  rather than inventing OEM field names. Do not declare a path “not security-relevant”
  without the reference analysis needed to support that boundary.
- Keep this file a stable contract. Revise or remove stale rules instead of
  accumulating session-specific exceptions, completion notes, or runtime inventories.
