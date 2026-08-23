# ghidra_rh850

Reverse engineering and exploit engineering for Toyota/Denso RH850/P1M-E EPS
firmware, centered on Sienna calibration **`8965B4512000`** (`R7F701381`). The
project exists to understand the firmware deeply enough to reason about Toyota
TSS3 SecOC/TSK behavior and build reproducible experiments for openpilot/comma.

The repository is evidence-first: **firmware bytes and deterministic tests are
the source of truth**. Ghidra annotations, generated artifacts, and documentation
are derived views and can be corrected when stronger evidence appears.

## Current state

The broad reverse-engineering phase is mature. We have a reproducible 6,376
function project, a whole-image pseudocode/reference corpus, canonical finding
and correction ledgers, exploit-interest ranking, and bounded host tooling for
the highest-value live experiments.

The most important current conclusions are:

- **Boot trust is CRC/marker based, not signature based.** The bootloader's
  SecurityAccess and authenticated RAM-exec path are recovered, including the
  relevant AES secrets and payload format.
- **Application diagnostics expose substantial attack surface.** This includes
  SecurityAccess, unauthenticated ReadMemoryByAddress disclosure, persistent BA
  authorization state, RoutineControl state changes, and several verified
  memory-safety findings/closures.
- **SecOC receive verification uses ICU-S slot 4.** The six protected receive
  profiles, freshness flow, command-7 verification, command-5 MAC-generation
  plumbing, and command-8 provisioning paths are recovered. The live slot-4 key
  itself is still not extracted.
- **Two stock command-8 clients exist.** RID `0x1010` is diagnostic; RID
  `0x100E` arms a CAN-fed bank assembled from `0x13..0x1A`. Their shared
  completion callback has a verified cross-bank attribution bug
  (SECOC-047/048), but ICU-S authentication still prevents an unauthenticated
  key update.
- **XCP is a serious unauthenticated surface if physically reachable.** The
  application implements `0x7F7/0x7F8` reads, DAQ, and a direct 32 KiB
  LocalRAM write window. That RAM is supervisor-executable on hardware, but no
  recovered control-transfer consumer currently turns the write into RCE.
- **The practical blockers are now mostly dynamic or artifact-dependent.** The
  highest-value next answers are live slot-4 command-5 permission, XCP physical
  reachability, the Gate-2 causal hardware proof, and another calibration for
  transfer testing.

For the short execution queue, read
**[docs/status/PRIORITIES.md](docs/status/PRIORITIES.md)**. For the technical
picture, read **[docs/OVERVIEW.md](docs/OVERVIEW.md)**.

## Start here

| Goal | Read / run |
|---|---|
| Understand the project in 10–15 minutes | [docs/OVERVIEW.md](docs/OVERVIEW.md) |
| See what we should do next | [docs/status/PRIORITIES.md](docs/status/PRIORITIES.md) |
| Check whether a claim is actually established | [docs/status/FINDINGS.md](docs/status/FINDINGS.md) |
| See unresolved questions in full detail | [docs/status/OPEN_QUESTIONS.md](docs/status/OPEN_QUESTIONS.md) |
| Open/rebuild/use the Ghidra project | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Understand the documentation structure | [docs/README.md](docs/README.md) |
| Use exploit / bench tooling | [exploit/README.md](exploit/README.md) |

Quick verification:

```bash
uv sync --locked
make verify       # fast tracked-only edit-loop gate
make verify-full  # exhaustive portable gate (also used by CI)
```

Explore the committed analysis safely:

```bash
make work-project
tools/g inspect 0x8db22 --decompile --callers --callees --xrefs --disasm 40
```

**Never daemon-open `project/` directly.** `project/` is a committed snapshot;
interactive work belongs in `build/work/project/`. `build/` is ignored workspace
state only, split into `cache/`, `work/`, `out/`, `logs/`, and `tmp/`; run
`make build-status` to inspect it. The operating contract is in
[AGENTS.md](AGENTS.md) and the full mechanics are in
[docs/WORKFLOW.md](docs/WORKFLOW.md).

## Repository map

The top level is intentionally split by evidence role:

| Path | Role |
|---|---|
| `firmware/` | Exact committed CodeFlash/DataFlash inputs — highest authority |
| `tests/` | Deterministic claim verification |
| `data/` | Curated and generated machine-readable evidence; generated material lives under `data/generated/` where practical |
| `ghidra/` | Vendored processor/CLI plus import, annotation, investigation, and verification scripts |
| `project/` | Committed non-live Ghidra snapshot; never open directly |
| `tools/` | Rebuild, generation, analysis, and acquisition tooling |
| `exploit/` | Bounded host/live tooling derived from established findings |
| `docs/` | Human-readable current documentation and historical research journals |
| `community/` | In-tree community artifacts/tooling with provenance |
| `REFERENCE/` | External/reference material; context only, not project truth |
| `legacy/` | Superseded analysis retained only for history |

Large licensed/local corpora are intentionally outside the tracked source tree:
`Techstream/` is pinned by `techstream.lock.json`, `Renesas/` by
`renesas-rfp.lock.json`, and the optional local `REFERENCE/` tree is ignored
context material. `external-references.lock.json` pins public/community inputs.

Generated scratch/output belongs in ignored `build/`, not in the committed
analysis tree.

## Documentation model

There are four document classes; keeping them distinct is deliberate:

1. **Orientation** — `docs/OVERVIEW.md`, `docs/README.md`.
2. **Live status** — `docs/status/`: current priorities, findings, open
   questions, coverage status, and corrections.
3. **Canonical subsystem reports** — `docs/architecture/`, `communications/`,
   `diagnostics/`, `security/`, `storage/`, `variants/`, and `tooling/`.
4. **Historical journals** — `docs/history/`. These preserve investigation
   chronology but are not current-state documentation.

A material claim should have exactly one canonical subsystem home and one row in
`docs/status/FINDINGS.md`; other documents summarize and link instead of
repeating the full argument.

## Target / firmware layout

The committed inputs are already split:

| File | Size | Virtual range |
|---|---:|---|
| `firmware/RH850_P1M-E_DataFlash.bin` | `0x8000` | `0xFF200000..0xFF207FFF` |
| `firmware/RH850_P1M-E_CodeFlash.bin` | `0x100000` | `0x00000000..0x000FFFFF` |

Some historical/public tooling uses a concatenated `0x108000` image with
DataFlash first. For that representation, **CodeFlash VA = file offset −
`0x8000`**. Do not import the concatenation as one flat address space.

## Scope discipline

Unless a finding explicitly says otherwise, firmware-static claims apply to the
Sienna **`8965B4512000`** image only. Corolla, `4514000`, F3/F4, RAV4 Prime,
and other TSS3 targets are transfer hypotheses until their own firmware or live
evidence validates them. See [docs/variants/](docs/variants/README.md).
