# Agent instructions

Operating contract for changing this repository. For what the firmware *is*,
read `docs/OVERVIEW.md`. For how to run the tooling, read `docs/WORKFLOW.md`.
This file is only what an agent must **obey** while working here.

## Source-of-truth hierarchy

1. **Firmware bytes and deterministic verification** (`firmware/`, `tests/`)
2. **Generated artifacts** (`data/` CSVs — regenerate, never hand-edit)
3. **Annotated Ghidra project** (`project/` committed snapshot)
4. **Narrative documentation** (`docs/` subsystem reports)
5. **Historical notes** (`legacy/`, superseded claims in `docs/status/CORRECTIONS.md`)

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
  `build/project/` (via `make work-project`).
- **Always `ghidra ... stop` before copying or committing the working
  project.** The daemon holds edits in memory; only teardown commits durably.
  Confirm `pgrep -f 'AnalyzeHeadless.*rh850'` is empty before snapshotting.
- **Never commit while a daemon is running** — it holds transient `.lock` /
  `tmp*` files.
- **Never infer CodeFlash VA without accounting for the DataFlash prefix.**
  CodeFlash VA = file offset − `0x8000`.
- **Never point a rebuild at committed `project/`.** Promote only with
  `make snapshot-project`.
- **Do not collapse the four-stage rebuild.** Seed timing changes Ghidra's
  recovered graph. See `docs/WORKFLOW.md` §"The four-stage analysis".
- **`legacy/flat-import/` is historical only.** Do not use it for current
  results.

## Standard commands

```bash
uv sync --locked          # one-time environment
make verify               # firmware evidence, no Ghidra — run this first
make verify-sleigh        # SLEIGH compile + isolated install
make work-project         # materialize build/project/ from committed snapshot
make verify-processor     # fixtures + asserting audits on build/project/
make snapshot-project     # the ONLY path that mutates committed project/
```

Interactive work only against `$PWD/build/project` with an **absolute**
`--projects-dir` (Ghidra 12.1+ rejects path components starting with `.`).

## Evidence language

Use these grades in any finding you record (definitions and full ledger in
`docs/status/FINDINGS.md`):

- **verified** — directly asserted by a deterministic test;
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
6. **Persist findings to the repo before delivering them** in chat.

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
- Findings ledger: [docs/status/FINDINGS.md](docs/status/FINDINGS.md)
- Open questions: [docs/status/OPEN_QUESTIONS.md](docs/status/OPEN_QUESTIONS.md)
- Corrections: [docs/status/CORRECTIONS.md](docs/status/CORRECTIONS.md)
- Subsystem indexes: [docs/README.md](docs/README.md)
