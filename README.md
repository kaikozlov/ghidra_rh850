# ghidra_rh850

Reverse engineering and openpilot integration research for Toyota/Denso
RH850/P1M-E ECUs and the surrounding TSS3 control/security stack. The repository
combines firmware analysis, Toyota GTS+/Techstream reverse engineering,
vehicle-bound captures, diagnostic/programming tooling, and reproducible RAM
runtime experiments.

The maintainer's **2026 Toyota Camry Hybrid EPS `8965F3307000`** is the
primary/default analysis target. The older Sienna `8965B4512000` is retained as
a legacy reference for deep P1M-E, diagnostic, ICU-S, and SecOC internals. The
2024 Crown and two Corolla calibrations are first-class comparison targets with
their own firmware, Ghidra projects, generated evidence, and field results.

The core evidence rule is simple: **firmware bytes and deterministic
verification are authoritative**. Generated artifacts, Ghidra annotations,
captures, Toyota software, community evidence, and documentation are
progressively more contextual views and must retain their target/provenance
boundaries.

## Current technical picture

The project is now centered on the complete TSS3 request/arbitration/actuator
path rather than a single steering message.

- **Lateral control is demonstrated on the exact Camry F33.** Toyota's protected
  `0x08A` is the TSS application-request plane, Brake/VMM-owned `0x081` is the
  corresponding result/reference plane, and protected `0x0B6` is the final
  steering-controller instruction received by the EPS. The working development
  path sends a bounded C7 target through normal Toyota safety, lets native B6
  complete the stock receive/SecOC path, then takes ownership **post-auth** at
  route44 raw COM in volatile RAM before the cooperative controller consumes the
  application fields. Native freshness/MAC state, the B6 SecOC trailer, and the
  ICU-S result are left untouched; command-5 re-signing is no longer part of the
  Camry field backend. Persistent receiver-bypass patches remain historical
  bring-up artifacts, not the intended architecture.
- **The TSS3 RAM runtime keeps one cross-target host contract, with target-native
  post-install backends.** Camry F33, Crown F30, and Corolla H/F use the same
  authenticated 4-KiB bootstrap/profile selection and the same recurring
  functional-`0x777` C7 control contract. Camry F33 now qualifies native authenticated
  route44 publication and installs a post-auth raw-COM override helper; Crown and
  Corolla retain their command-5/native-MAC signer paths. Target-local addresses
  and RAM geometry stay behind the shared host interface, so openpilot does not
  need a different steering protocol per vehicle.
- **The exact F33 EPS has a real production SecOC transmit stack.** `0x030` is an
  EPS-origin 32-byte CAN-FD PDU protected by sender freshness plus Toyota
  `FV4 || MAC28`; the firmware constructs
  `DataID || payload || full_freshness`, invokes ICU-S command 5 with selector 4,
  appends the trailer, and routes the result through PduR/CanIf to CAN. This is
  important beyond `0x030`: the EPS is demonstrably capable of native SecOC
  generation, not merely verification or the RAM-resident B6 signing experiment.
  Which EPS-origin PDUs are forwarded across the EBU/Brake-domain junction is
  still being recovered.
- **`0x08A`, not `0x160`, is the current native-longitudinal control surface.**
  `0x08A` carries the selected upper/lower longitudinal request packages as well
  as the lateral request tuple; `0x081` carries the corresponding employed
  result/reference state. The earlier Camry/Corolla `0x160` replacement work is
  retained as historical field evidence, but `0x160` is now treated as an
  FRC-origin state/evidence PDU rather than a demonstrated actuator ingress.
  Current TSS3 ports therefore keep Toyota stock longitudinal while source
  ownership/suppression, upper/lower ordering, and the remaining request-policy
  fields are closed.
- **Toyota GTS+/Techstream is part of the primary RE workflow.** It supplies OEM
  ECU identities, DIDs, recorder schemas, active-test vocabulary, topology,
  reprogramming routes, and security-key workflows that can then be joined to
  otherwise stringless firmware and vehicle captures.
- **The older Sienna image remains the low-level reference, not the default
  vehicle model.** Much of the boot, SecurityAccess, NvM, ICU-S, SecOC, and
  memory-safety substrate was first recovered there. Target-specific Camry,
  Crown, and Corolla behavior must still be proved against those exact images.

For the live execution queue, read
**[docs/status/PRIORITIES.md](docs/status/PRIORITIES.md)**. For the current
project-level picture, start with **[docs/OVERVIEW.md](docs/OVERVIEW.md)**.

## Start here

| Goal | Read / run |
|---|---|
| Current project / primary Camry orientation | [docs/OVERVIEW.md](docs/OVERVIEW.md) |
| Current Camry capability and qualification boundary | [docs/variants/camry-2026-capability-matrix.md](docs/variants/camry-2026-capability-matrix.md) |
| Exact Camry TSS3/openpilot integration | [docs/variants/camry-2026-tss3-opendbc-port.md](docs/variants/camry-2026-tss3-opendbc-port.md) |
| Working lateral-control evidence | [docs/variants/toyota-tss3-openpilot-bounty-evidence.md](docs/variants/toyota-tss3-openpilot-bounty-evidence.md) |
| Minimal/current RAM runtime | [docs/architecture/toyota-tss3-minimal-runtime.md](docs/architecture/toyota-tss3-minimal-runtime.md) |
| Toyota request/arbitration architecture | [docs/architecture/toyota-tss3-vehicle-movement-arbitration.md](docs/architecture/toyota-tss3-vehicle-movement-arbitration.md) |
| Exact F33 EPS transmit / SecOC-Tx surface | [docs/variants/camry-f33-eps-tx.md](docs/variants/camry-f33-eps-tx.md) |
| Current longitudinal evidence | [docs/variants/camry-2026-longitudinal-evidence.md](docs/variants/camry-2026-longitudinal-evidence.md) |
| Legacy Sienna reference firmware | [docs/variants/sienna-8965B4512000-overview.md](docs/variants/sienna-8965B4512000-overview.md) |
| Current execution priorities | [docs/status/PRIORITIES.md](docs/status/PRIORITIES.md) |
| Claim/evidence lookup | [docs/status/FINDINGS.md](docs/status/FINDINGS.md) or `tools/know QUERY` |
| Unresolved questions | [docs/status/OPEN_QUESTIONS.md](docs/status/OPEN_QUESTIONS.md) |
| Ghidra/rebuild workflow | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Runtime / exploit tooling | [exploit/README.md](exploit/README.md) |
| Toyota RE capabilities | `tools/toyota capabilities` |

## Registered firmware targets

`data/analysis_targets.json` is authoritative and `tools/gtarget list` is the
human/machine entry point.

| Target | Role | Vehicle / calibration |
|---|---|---|
| `camry-8965F3307000` | **primary/default** | 2026 Toyota Camry Hybrid `8965F3307000` |
| `crown-8965F3012000` | first-class | 2024 Toyota Crown Limited `8965F3012000` |
| `corolla-8965F1208000` | first-class | 2025 Toyota Corolla `8965F1208000` |
| `corolla-8965H1202000` | first-class | 2023 Toyota Corolla `8965H1202000` |
| `sienna-8965B4512000` | legacy reference | Toyota Sienna `8965B4512000` |

Plain `tools/g`, `tools/pseudo`, and `make work-project` resolve to the registered
primary target, currently the Camry. Use `tools/gtarget TARGET ...` or an
explicit target option when working on another calibration. This matters because
the same virtual address can name completely different code across images.

Do not infer cross-target equivalence from the common P1M-E/SecOC architecture.
A signal, address, key slot, freshness slot, diagnostic route, or control
behavior belongs to its calibration until target-native evidence transfers it.

The legacy Sienna inputs are split as `firmware/RH850_P1M-E_CodeFlash.bin` and
`firmware/RH850_P1M-E_DataFlash.bin`. Historical/public tooling sometimes uses
their `0x108000` concatenation with DataFlash first; **for that Sienna
representation only, CodeFlash VA = file offset - `0x8000`**. Other registered
targets use their own manifests and layout rules.

## Working with the repository

One-time environment setup and narrow verification:

```bash
uv sync --locked
tools/test <suite-or-prefix>   # run only what exercises the changed code/evidence
tools/test list [query]        # discover suites
tools/test plan <query>        # preview a suite/prefix/group
```

Documentation-only edits do not require tests. `full`, `local`, processor,
SLEIGH, and external-corpus sweeps are deliberate milestone/debugging tools, not
the normal edit loop.

Explore the primary Camry target:

```bash
tools/gtarget list
tools/gtarget show camry-8965F3307000
tools/g inspect 0x8549e --decompile --callers --callees --xrefs --disasm 40
tools/pseudo 0x8549e
tools/gts search LTA
tools/toyota capabilities
```

Explore a non-primary target explicitly:

```bash
tools/gtarget sienna-8965B4512000 decompile 0x8db22
tools/gtarget crown-8965F3012000 inspect 0x8549e --decompile --callers
```

`tools/g` materializes the selected safe working project under ignored `build/`
state. **Never daemon-open committed `projects/<target>/` snapshots directly.**
Read [AGENTS.md](AGENTS.md) before changing the repository and
[docs/WORKFLOW.md](docs/WORKFLOW.md) for the full lifecycle.

## Repository map

| Path | Role |
|---|---|
| `firmware/` | Exact committed firmware inputs — highest evidence authority |
| `projects/` | Committed packed Ghidra snapshots for registered targets |
| `targets/` | Vehicle-bound captures, manifests, runtime evidence, and target-local provenance |
| `tests/` | Deterministic binary/tooling verification |
| `data/` | Curated and generated machine-readable evidence |
| `ghidra/` | RH850 processor/CLI plus analysis and verification scripts |
| `tools/` | Target-aware RE, Toyota/GTS+, acquisition, generation, and analysis tooling |
| `tsk/` | Shared Toyota diagnostic/programming support code |
| `exploit/` | Bounded diagnostic, RAM-runtime, signer, and behavioral-proof tooling |
| `docs/` | Current architecture/status reports plus historical investigation journals |
| `community/` | In-tree community artifacts and attributed external evidence |
| `software/` | Tracked provenance/locks for external Toyota/Renesas software corpora |
| `REFERENCE/` | Ignored local context/reference material; never project truth |
| `build/` | Ignored mutable workspace, generated output, logs, and scratch state |

Large licensed/local corpora such as Techstream, GTS+, Toyota CUW packages, and
Renesas tooling stay under ignored software/reference storage. Tracked locks,
parsers, generated evidence, and reproducible conclusions remain in git.

## Evidence and integration discipline

Use the confidence vocabulary in
[docs/status/FINDINGS.md](docs/status/FINDINGS.md): **verified**, **observed**,
**recovered**, **bounded**, **hypothesis**, and **disproved**. Evidence source and
confidence are separate dimensions: a live route can be strong observed evidence
without becoming a firmware-static fact, and a result on one calibration does not
silently transfer to another.

For firmware behavior, inspect the relevant target bytes/decompilation before
naming a function or asserting a path. For openpilot integration, start from
current upstream behavior and add only the smallest target-specific deviation
the vehicle actually requires. Experimental patches, diagnostic oracles, and RAM
residents are evidence/bring-up mechanisms, not permission to create a parallel
openpilot control architecture.

See [docs/README.md](docs/README.md) for the full documentation map.
