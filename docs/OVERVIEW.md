# Project overview

This repository reverse-engineers Toyota/Denso RH850/P1M-E firmware and the
surrounding Toyota TSS3 control/security stack for openpilot integration.
Firmware bytes and deterministic verification remain the source of truth; Ghidra
projects, generated artifacts, captures, Toyota diagnostic software, community
evidence, and documentation are progressively more contextual views of that
evidence.

## Primary target

The primary analysis target is the maintainer's **2026 Toyota Camry Hybrid EPS
`8965F3307000`**. `data/analysis_targets.json` is authoritative, and plain
`tools/g`, `tools/pseudo`, and `make work-project` resolve to this target unless an
explicit target is supplied.

Current Camry work spans the complete TSS3 control path rather than only the EPS:

- native lateral control is demonstrated through the volatile EPS-resident
  **post-auth** route44 raw-COM path: stock B6 completes SecOC verification
  unchanged, then the application control fields are overridden before the
  cooperative controller consumes them; the current Camry backend does not
  re-sign B6 or invoke command 5 at runtime;
- `0x08A` is the FRC-side TSS application request plane and `0x081` the
  Brake/VMM result/status plane;
- protected `0x0B6` is the downstream steering-controller instruction received by
  the EPS;
- the exact F33 EPS has a real production SecOC transmit stack for protected
  `0x030`, including sender freshness, ICU-S command 5 / selector 4, trailer
  construction, PduR/CanIf routing, and CAN-FD transmission;
- current RE is closing driver-attention behavior, Brake/EBU routing, longitudinal
  request ownership, and the smallest native openpilot integration boundary.

Start with:

- [variants/camry-2026-tss3-opendbc-port.md](variants/camry-2026-tss3-opendbc-port.md)
- [variants/camry-2026-live-baseline.md](variants/camry-2026-live-baseline.md)
- [variants/camry-f33-eps-tx.md](variants/camry-f33-eps-tx.md)
- [architecture/toyota-tss3-vehicle-movement-arbitration.md](architecture/toyota-tss3-vehicle-movement-arbitration.md)
- [status/PRIORITIES.md](status/PRIORITIES.md)

## Other registered targets

| Target | Role |
|---|---|
| `camry-8965F3307000` | **primary** — exact maintained vehicle and current integration target |
| `crown-8965F3012000` | first-class TSS3 comparison / live field target |
| `corolla-8965F1208000` | first-class newer Corolla target |
| `corolla-8965H1202000` | first-class Corolla comparison target |
| `sienna-8965B4512000` | **legacy reference** — deep P1M-E/SecOC/diagnostic substrate |

The Sienna remains valuable because much of the low-level boot, diagnostic,
ICU-S, storage, and SecOC machinery was first recovered there. It is no longer
the default project or the authority for target-specific Camry behavior. Its
former overview is retained at
[variants/sienna-8965B4512000-overview.md](variants/sienna-8965B4512000-overview.md).

## Analysis workflow

All committed Ghidra snapshots live under `projects/<target>/` using deliberately
non-openable `.gpr.snapshot` / `.rep.snapshot` names. Never open those trees with
Ghidra. Interactive and headless analysis uses registered paths under
`build/work/`.

Useful entry points:

```bash
tools/g inspect 0x4e848 --decompile --callers --callees --xrefs --disasm 40
tools/pseudo 0x4e848
tools/gtarget list
tools/gtarget sienna-8965B4512000 decompile 0x8db22
make work-project
```

See [WORKFLOW.md](WORKFLOW.md) for lifecycle rules and
[architecture/toyota-openpilot-porting-contract.md](architecture/toyota-openpilot-porting-contract.md)
for the integration design contract.
