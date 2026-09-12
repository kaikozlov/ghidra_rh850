# ghidra_rh850

Reverse engineering and openpilot integration research for Toyota/Denso
RH850/P1M-E EPS firmware and the surrounding TSS3 control stack. The repository
combines firmware analysis, Toyota GTS+/Techstream reverse engineering,
vehicle-bound captures, diagnostic tooling, and reproducible runtime experiments.

The Sienna EPS calibration **`8965B4512000`** remains the primary reference image
for deep P1M-E internals, but the project is no longer a single-firmware study.
The 2026 Camry F33 and two newer Corolla EPS calibrations are first-class analysis
targets with their own firmware, Ghidra projects, generated evidence, and live or
field evidence.

The evidence rule is unchanged: **firmware bytes and deterministic verification
are authoritative**. Generated artifacts, Ghidra annotations, captures, external
Toyota software, community evidence, and documentation are progressively more
contextual views of that source material and must retain their target/provenance
boundaries.

## Current state

The project has moved past broad static reconnaissance and into cross-target TSS3
control integration. The important current results are:

- **The P1M-E security/diagnostic substrate is deeply recovered.** On the Sienna
  reference image this includes the boot/application trust chain, SecurityAccess,
  authenticated RAM execution, application diagnostics, SecOC freshness and
  ICU-S command flows, key-update paths, and the major memory-safety / calibration
  surfaces used by later target work.
- **The newer Corolla H/F steering receiver is no longer a mystery message.** Exact
  firmware analysis recovers protected 32-byte CAN-FD `0x0B6`, its target-angle
  field, Target Lateral ID semantics, timing/loss behavior, `0x00F` freshness
  synchronization, CMAC28 construction, and the EPS-side SecOC state machine.
  H/F also provide target-native driver-torque, steering-state, and fault/status
  bridges needed by an openpilot port.
- **Openpilot lateral control has been observed on the exact 2026 Camry F33.** The
  retained primary route contains 167.289 s of lateral-active control. A clean
  36.105 s witness has target/measured steering correlation `r=0.989` at the
  tested 400 ms lag, low driver torque, no EPS steering fault, and native
  `0x08A`/`0x081` Target Lateral ID `0` throughout. The demonstrated development
  path is `CarController -> C7 sideband -> EPS resident -> native B6 rewrite ->
  ICU-S command-5 signing`; the exact route, runtime binaries, hashes, and working
  opendbc delta are preserved. The RAM resident is volatile, while that recorded
  drive still used the cumulative stage-5 development CodeFlash image.
- **TSS3 longitudinal work has a native request plane rather than a SecOC blocker.**
  The repository recovered and can deterministically generate the E2E-protected
  `0x160` FRC request family on the Camry. Independent Corolla field evidence then
  demonstrated live openpilot longitudinal control through its target-native
  `0x160` form. Scaling, ownership, standstill handoff, and stock-source
  suppression remain target-specific integration work rather than values to copy
  between cars.
- **Toyota's own software is now part of the analysis workflow.** GTS+/Techstream
  is used to recover OEM vocabulary, ECU identities, DIDs, recorder schemas,
  reprogramming routes, capability tables, and acquisition leads before names are
  projected onto otherwise stringless firmware.
- **The integration target is normal openpilot architecture.** Experimental RAM
  residents, patch stages, diagnostic oracles, and direct-Panda tools are evidence
  and bring-up machinery. Production work starts from current upstream
  openpilot/opendbc/Panda and keeps only target-specific wire/security facts that
  are actually required.

For the live execution queue, read
**[docs/status/PRIORITIES.md](docs/status/PRIORITIES.md)**. For the exact Camry
control result, start with
**[docs/variants/toyota-tss3-openpilot-bounty-evidence.md](docs/variants/toyota-tss3-openpilot-bounty-evidence.md)**.
The older Sienna-centric technical overview remains useful for the reference
firmware in **[docs/OVERVIEW.md](docs/OVERVIEW.md)**.

## Start here

| Goal | Read / run |
|---|---|
| Understand the Sienna reference firmware | [docs/OVERVIEW.md](docs/OVERVIEW.md) |
| Understand the TSS3/openpilot control result | [docs/variants/toyota-tss3-openpilot-bounty-evidence.md](docs/variants/toyota-tss3-openpilot-bounty-evidence.md) |
| See the exact 2026 Camry evidence and target history | [targets/camry-2026/README.md](targets/camry-2026/README.md) |
| See the minimal TSS3 runtime boundary | [docs/architecture/toyota-tss3-minimal-runtime.md](docs/architecture/toyota-tss3-minimal-runtime.md) |
| See the openpilot porting contract | [docs/architecture/toyota-openpilot-porting-contract.md](docs/architecture/toyota-openpilot-porting-contract.md) |
| See what to do next | [docs/status/PRIORITIES.md](docs/status/PRIORITIES.md) |
| Check whether a claim is established | [docs/status/FINDINGS.md](docs/status/FINDINGS.md) |
| Find prior research by ID or keyword | `tools/know QUERY` |
| Inspect unresolved questions | [docs/status/OPEN_QUESTIONS.md](docs/status/OPEN_QUESTIONS.md) |
| Operate the Ghidra/rebuild stack | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Use runtime / exploit tooling | [exploit/README.md](exploit/README.md) |
| Discover Toyota RE capabilities | `tools/toyota capabilities` |

## Registered firmware targets

`tools/gtarget list` is the machine-readable entry point. The current first-class
set is:

| Target | Role | Vehicle / calibration |
|---|---|---|
| `sienna-8965B4512000` | primary reference | Toyota Sienna `8965B4512000` |
| `camry-8965F3307000` | first-class | 2026 Toyota Camry Hybrid `8965F3307000` |
| `corolla-8965H1202000` | first-class | 2023 Toyota Corolla `8965H1202000` |
| `corolla-8965F1208000` | first-class | 2025 Toyota Corolla `8965F1208000` |

Do not infer equivalence from the common P1M-E/SecOC architecture. A signal,
address, secret, freshness slot, diagnostic route, or control behavior belongs to
its calibration until target-native evidence transfers it.

The original Sienna inputs are split as `firmware/RH850_P1M-E_CodeFlash.bin`
and `firmware/RH850_P1M-E_DataFlash.bin`. Historical/public tooling sometimes
uses their `0x108000` concatenation with DataFlash first; **for that Sienna
representation only, CodeFlash VA = file offset - `0x8000`**. Other registered
targets use their own target manifests and layout rules.

## Working with the repository

One-time environment setup and narrow verification:

```bash
uv sync --locked
tools/test <suite-or-prefix>   # run only what exercises the changed evidence/code
tools/test list [query]        # discover suites
tools/test plan <query>        # preview a suite/prefix/group
```

Documentation-only edits do not require tests. `full`, `local`, processor, SLEIGH,
and external-corpus sweeps are deliberate milestone/debugging tools, not the
normal edit loop.

Explore firmware through the target-aware analysis surface:

```bash
tools/gtarget list
tools/gtarget show camry-8965F3307000
tools/g inspect 0x8db22 --decompile --callers --callees --xrefs --disasm 40
tools/pseudo security_access --list
tools/gts search LTA
tools/toyota capabilities
```

For the primary Sienna project, `tools/g` materializes the safe working copy
itself. **Never daemon-open committed `project/` or `projects/` directly.** Those
are snapshots; mutable analysis belongs under ignored `build/`. Read
[AGENTS.md](AGENTS.md) before changing the repository and
[docs/WORKFLOW.md](docs/WORKFLOW.md) for the full lifecycle.

## Repository map

| Path | Role |
|---|---|
| `firmware/` | Exact committed firmware inputs — highest evidence authority |
| `project/` | Committed Sienna Ghidra snapshot |
| `projects/` | Committed first-class variant Ghidra snapshots |
| `targets/` | Vehicle-bound captures, manifests, runtime evidence, and target-local provenance |
| `tests/` | Deterministic binary/tooling verification |
| `data/` | Curated and generated machine-readable evidence |
| `ghidra/` | RH850 processor/CLI plus analysis and verification scripts |
| `tools/` | Target-aware RE, Toyota/GTS+, generation, acquisition, and analysis tooling |
| `exploit/` | Bounded diagnostic, RAM-runtime, signer, and behavioral-proof tooling |
| `docs/` | Current architecture/status reports plus historical investigation journals |
| `community/` | In-tree community artifacts and attributed external evidence |
| `software/` | Tracked provenance/locks for external Toyota/Renesas software corpora |
| `REFERENCE/` | Ignored local context/reference material; never project truth |
| `build/` | Ignored mutable workspace, generated output, logs, and scratch state |

Large licensed/local corpora such as Techstream V18, GTS+, Toyota CUW packages,
and Renesas RFP stay under ignored software/reference storage. Tracked locks,
derived parsers, generated evidence, and reproducible conclusions remain in git.

## Scope and evidence discipline

Use the vocabulary in [docs/status/FINDINGS.md](docs/status/FINDINGS.md):
**verified**, **observed**, **recovered**, **bounded**, **hypothesis**, and
**disproved**. Keep evidence source separate from confidence: a live route can be
strong observed evidence without becoming a firmware-static fact, and a community
field result can validate an architecture without transferring its exact bytes to
another Toyota.

For firmware behavior, inspect the relevant target bytes/decompilation before
naming a function or asserting a path. For openpilot integration, start from
current upstream behavior and add only the smallest target-specific deviation
that the vehicle actually requires. See [AGENTS.md](AGENTS.md) for the operating
contract and [docs/README.md](docs/README.md) for the documentation map.
