This repo analyzes Toyota/Denso firmware for Renesas RH850/P1M-E ECUs.

The primary analysis target is the **2026 Camry Hybrid EPS `8965F3307000`**.

Read preexisting documentation to guide your work. @./docs/

For firmware claims, inspect the exact target through `tools/gtarget` / `tools/pseudo`; For the camry, we also have the significantly more mature decompilation corpus under `./decomp/`, with tooling at `tools/toyota decomp` (try this before pseudo for the camry target).
Decompile a function before naming its role; verify important gates from disassembly, bytes, and dataflow.

As this repo matures, we must do our absolute best to keep it tidy.
This is not a museum, and we aren't doing archaeology. If something we previously recorded is incorrect, delete it.
Every recorded fact should be accurate and up-to-date with our current knowledge.
Keeping false or stale claims is not rigorous, it's actively destructive to all future work -- we cannot build a cathedral on a foundation of shit.

This work is iterative by nature. With every change, we build on top of existing work, refining the overall project instead of creating disparate pieces of work.

We are cultivating an ecosystem.

## Tools

Everything you need lives under `tools/`, and each command has `--help`. Reach for these before writing a script.

- `tools/gtarget list` / `show TARGET` -- what targets exist, and where their images, projects, and corpora live. Targets are named like `camry-8965F3307000`; the bare part number is rejected. `tools/gtarget TARGET ...` runs Ghidra commands against that target, and bare `tools/g` runs against the registry default (currently the Camry).
- `tools/g decompile ADDR`, `tools/g inspect ADDR --decompile --callers --disasm 40` -- live Ghidra. It bootstraps its own environment and working project; don't source env files by hand. `tools/g session-status` shows the daemon, `tools/g stop` shuts it down cleanly.
- `tools/pseudo --target TARGET QUERY` -- search the tracked decompilation corpus. `--data-ref ADDR` finds functions that reference an address, which beats grepping decompiler spelling. Pseudocode is not proof; confirm in disassembly.
- `tools/know QUERY` -- find what we've already written down about a topic. It's navigation, not an oracle.
- `tools/gts` -- Toyota GTS+/Techstream data: ECU tables, DIDs, recorder schemas. Start with `--help` and the schema-first workflow in `docs/tooling/gts-query-cli.md` instead of grepping strings.
- `tools/toyota` -- Toyota capabilities and per-target workflows. `tools/toyota decomp source` shows the Camry's reconstructed C.
- `tools/rh850` -- `toolchain` builds RH850 code; `test` and `csplus` run payloads or firmware scenarios in simulation.
- `tools/artifact list` / `regen NAME` -- generated artifacts and what produces them.
- `tools/test list` / `plan SELECTOR` / `SELECTOR` -- verification.

Python is an editable install (`uv sync --locked`). Import `tools.*` and use `tools.REPO_ROOT`; don't add `sys.path` or `PYTHONPATH` tricks to packaged tooling or tests.

## Evidence

Bytes are the ground truth; docs and our own earlier notes are leads. When you write something down, say how we know it: read from firmware, observed in a capture, or inferred. Code that exists or a test that passes doesn't tell us how the car behaves. Name things for what they do, and don't invent OEM field names.

## Sharp edges

- Committed firmware and raw captures don't change. If the bytes look wrong, our interpretation is wrong.
- Opening a committed `projects/` database in Ghidra compacts it. Work in the target's `build/work/` copy.
- In-memory Ghidra edits only persist on a clean daemon stop, so stop it before copying or promoting a project. [WORKFLOW.md](docs/WORKFLOW.md) has the lifecycle, including the order of the rebuild stages.
- The decompilation corpus is derived. After graph, naming, or type changes, regenerate it from a fresh rebuild.
- `build/` and `REFERENCE/` are local workspace and aren't in a fresh checkout. Don't make a check depend on them, and don't treat what's in them as evidence. If something is needed, promote it deliberately.
- Some public dumps are DataFlash+CodeFlash concatenated, and the 0x8000-byte prefix shifts every CodeFlash address by -0x8000. Our registered CodeFlash images are bare and start at VA zero; `tools/gtarget show` gives each target's base.

## Building things

Look for what already owns a thing before adding something new, and reuse it. Do what was asked, and when you replace something, migrate its callers and delete the old path.

Tests are for things that can break: behavior, parsing boundaries, fragile binary invariants. Docs and notes need none. Bare `tools/test` runs nothing; `verification.toml` has the selectors.

## Writing it down

Each conclusion lives in one place, the target or subsystem report. Rewrite in place when we learn better, and fix the links. FINDINGS, CORRECTIONS, and OPEN_QUESTIONS are archives, so don't stop investigating to feed them.

## Across targets

These ECUs share a software family, so most of what we learn on one carries to the others. Treat a finding from another target as a strong lead: addresses and calibrations differ, but structure and logic usually line up, so go find the counterpart in the target you're on and see. `tools/gtarget list` shows what's registered.

## Openpilot

Follow the [porting contract](docs/architecture/toyota-openpilot-porting-contract.md). Do it the way upstream openpilot, opendbc, and Panda already do, and deviate only when the firmware gives you a reason. Unknown semantics stay unmapped, and we don't add guards, timers, or state machines "just to be safe".
