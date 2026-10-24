This repo analyzes Toyota/Denso firmware for Renesas RH850/P1M-E ECUs.

The primary analysis target is the **2026 Camry Hybrid EPS `8965F3307000`**.

Read preexisting documentation to guide your work. @./docs/

For firmware claims, inspect the exact target through `tools/gtarget` / `tools/pseudo`; For the camry, we also have the significantly more mature decompilation corpus under `./decomp/`, with tooling at `tools/toyota decomp`.
Decompile a function before naming its role; verify important gates from disassembly, bytes, and dataflow.

As this repo matures, we must do our absolute best to keep it tidy.
This is not a museum, and we aren't doing archaeology. If something we previously recorded is incorrect, delete it.
Every recorded fact should be accurate and up-to-date with our current knowledge.
Keeping false or stale claims is not rigorous, it's actively destructive to all future work -- we cannot build a cathedral on a foundation of shit.

This work is iterative by nature. With every change, we build on top of existing work, refining the overall project instead of creating disparate pieces of work.

We are cultivating an ecosystem.

## Evidence

Bytes are the ground truth; docs and our own earlier notes are leads. When you write something down, say how we know it: read from firmware, observed in a capture, or inferred. Code that exists or a test that passes doesn't tell us how the car behaves. Name things for what they do, and don't invent OEM field names.

## Sharp edges

- Committed firmware and raw captures don't change. If the bytes look wrong, our interpretation is wrong.
- Opening a committed `projects/` database in Ghidra compacts it. Work in the target's `build/work/` copy.
- In-memory Ghidra edits only persist on a clean daemon stop, so stop it before copying or promoting a project. [WORKFLOW.md](docs/WORKFLOW.md) has the lifecycle, including the order of the rebuild stages.
- The decompilation corpus is derived. After graph, naming, or type changes, regenerate it from a fresh rebuild.

## Building things

Look for what already owns a thing before adding something new, and reuse it. Do what was asked, and when you replace something, migrate its callers and delete the old path.

Tests are for things that can break: behavior, parsing boundaries, fragile binary invariants. Docs and notes need none. Bare `tools/test` runs nothing; `verification.toml` has the selectors.

## Writing it down

Each conclusion lives in one place, the target or subsystem report. Rewrite in place when we learn better, and fix the links. FINDINGS, CORRECTIONS, and OPEN_QUESTIONS are archives, so don't stop investigating to feed them.

## Across targets

These ECUs share a software family, so most of what we learn on one carries to the others. Treat a finding from another target as a strong lead: addresses and calibrations differ, but structure and logic usually line up, so go find the counterpart in the target you're on and see. `tools/gtarget list` shows what's registered, and the default isn't always the one you want.

## Openpilot

Follow the [porting contract](docs/architecture/toyota-openpilot-porting-contract.md). Do it the way upstream openpilot, opendbc, and Panda already do, and deviate only when the firmware gives you a reason. Unknown semantics stay unmapped, and we don't add guards, timers, or state machines "just to be safe".
