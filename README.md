# Toyota RH850 firmware analysis

Reverse engineering and evidence tooling for Toyota/Denso RH850/P1M-E ECUs,
Toyota diagnostic software, and TSS3 vehicle integration research.

The primary analysis target is the **2026 Camry Hybrid EPS `8965F3307000`**.
This checkout contains firmware, analysis projects, captured evidence, and
research tooling. It is **not an openpilot distribution or a production vehicle
installation guide**. Target registration, a passing offline check, and a
recorded vehicle demonstration establish different things.

## Start here

| Goal | Entry point |
|---|---|
| Find the right report | [Documentation map](docs/README.md) |
| Understand project scope and evidence | [Project overview](docs/OVERVIEW.md) |
| Set up tools or work with Ghidra | [Workflow](docs/WORKFLOW.md) |
| Find target-specific conclusions | [Variant reports](docs/variants/README.md) |
| Review Camry capabilities and remaining qualification | [Capability matrix](docs/variants/camry-2026-capability-matrix.md) |
| Choose the next investigation | [Priorities](docs/status/PRIORITIES.md) |
| Look up a prior claim or correction | `tools/know QUERY` |

Detailed integration state belongs in the target reports, not in a second
summary here. Dated checkpoints and old experiments are retained evidence;
their commands, bus assignments, and software revisions are not automatically
current instructions.

## Quick start: offline discovery

Install [uv](https://docs.astral.sh/uv/), then run from the checkout:

```bash
uv sync --locked
tools/gtarget list
tools/gtarget show camry-8965F3307000
tools/pseudo --target camry-8965F3307000 --stats
tools/test list analysis_targets
tools/test plan analysis_targets
```

`uv sync` installs the repository in editable mode with locked dependencies.
No `PYTHONPATH` setup is needed. These discovery commands use tracked metadata
and the decompiler corpus; they do not open Ghidra or access a vehicle.
Interactive analysis/rebuilds need the Ghidra prerequisites in
[WORKFLOW.md](docs/WORKFLOW.md); external-software analyses have their own
corpus requirements.

The short commands under `tools/` are the public interface:

| Task | Command |
|---|---|
| Registered target identity and paths | `tools/gtarget list`, `tools/gtarget show TARGET` |
| Read the tracked decompiler corpus | `tools/pseudo --target TARGET --help` |
| Interactive Ghidra for a selected target | `tools/gtarget TARGET ...` |
| Toyota/GTS+ vocabulary and software evidence | `tools/gts --help`, `tools/toyota capabilities` |
| Find evidence and its producer | `tools/know QUERY`, `tools/artifact list` |
| Discover, preview, run selected verification | `tools/test list QUERY`, `tools/test plan SELECTOR`, `tools/test SELECTOR` |

Bare `tools/test` runs nothing. Select checks for the code or evidence being
changed; documentation-only edits do not need tests. `full`, `local`, and
processor/SLEIGH gates are deliberate milestone tools, not the edit loop.

## Registered analysis targets

[data/analysis_targets.json](data/analysis_targets.json) owns target selection,
image identities, working-project paths, committed snapshots, and corpus paths.
Use `tools/gtarget show TARGET` for those details instead of inferring them from
a directory or copying an address from another calibration.

| Target | Registry role |
|---|---|
| `camry-8965F3307000` | Primary/default — 2026 Camry Hybrid |
| `crown-8965F3012000` | First-class — 2024 Crown Limited |
| `corolla-8965F1208000` | First-class — 2025 Corolla specimen |
| `corolla-8965H1202000` | First-class — 2023 Corolla specimen; historical auxiliary-identity label |
| `sienna-8965B4512000` | Legacy reference — Sienna |

The Corolla labels identify separate retained specimens; the
[variant index](docs/variants/README.md) explains their application identities.
Additional partial images and external reports do not imply registered targets
or supported vehicles.

## Repository map

| Path | Role |
|---|---|
| `firmware/` | Canonical full or explicitly bounded partial firmware inputs |
| `projects/` | Committed Ghidra snapshots; never open these with Ghidra |
| `targets/`, `community/` | Target-bound captures, manifests, and attributed external evidence |
| `data/` | Curated evidence tables and generated artifacts; regenerate generated files |
| `tools/` | Public commands and capability/target-scoped implementations |
| `tests/`, `verification.toml` | Subsystem/target checks and their public suite selectors |
| `ghidra/` | Vendored processor/CLI and analysis scripts |
| `tsk/`, `exploit/` | Diagnostic support and experimental research implementations, not port qualification |
| `docs/` | Guides, scoped reports, status references, and historical journals |
| `software/` | Tracked corpus identities plus ignored local vendor inputs |
| `REFERENCE/`, `build/` | Ignored reference material and mutable workspace; never evidence authority |

Ghidra works only in the selected target's registered `build/work/` path.
Stop its daemon before snapshot promotion; use the documented four-stage
rebuild and promotion workflow rather than copying a live database.

For firmware claims, return to the exact target bytes and deterministic
verification. For integration design, use current upstream openpilot/opendbc
and the [native-shape contract](docs/architecture/toyota-openpilot-porting-contract.md).
Read [AGENTS.md](AGENTS.md) before changing the repository.
