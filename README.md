# ghidra_rh850

Ghidra reverse-engineering of the China-market Sienna EPS firmware
(`8965B4512000`, RH850/P1M-E R7F701381). The repository holds the corrected
split firmware images, the analysis scripts, pinned payload fixtures, the
pre-built annotated Ghidra project, and deterministic verification suites.
The firmware bytes are the single source of truth; the docs are falsifiable
explanations reconstructed from them.

## Scope and status

- **Firmware:** `8965B4512000`, MCU `R7F701381` (1 MiB CodeFlash + 32 KiB DataFlash).
- **Image:** `RH850_P1M-E_Firmware.bin` (`0x108000` bytes, two flash regions —
  see "File layout" below).
- **Recovery:** 5,852 functions / 178,516 instructions / 37,634 symbols on the
  last annotated rebuild. Most functions are structurally recovered but not
  behaviorally understood — see the evidence policy below.
- **Calibration caveat:** findings are specific to this Sienna calibration.
  The Corolla (`8965F1208000`) is a different calibration; nothing transfers
  automatically. See [docs/variants/](docs/variants/README.md).

## Major results

- **Corrected firmware layout.** The image is two flash regions, not one flat
  block; the original flat import was invalid (all addresses shifted
  `+0x8000`, ~2,000 functions, falsely "unreferenced" secrets).
- **Bootloader payload gate fully traced.** AES-CBC decrypt into RAM, CRC32 +
  CMAC authentication, flash-driver callback replacement for execution.
  `SEED_KEY_SECRET` (`0xBFE8`) and `PAYLOAD_BUILD_SECRET` (`0xBFD8`) recovered.
  → [docs/security/bootloader-payload-gate.md](docs/security/bootloader-payload-gate.md)
- **Application SecurityAccess level 2 functional.** Secret at `0x20840`;
  level 1 is a compiled stub; keygen is deterministic and attacker-controlled;
  this calibration has **no configured Dcm security gating**.
  → [docs/security/application-security-access.md](docs/security/application-security-access.md)
- **SecOC receive profile recovered.** Six RX PDUs; this calibration is
  consistent with an unprovisioned/default key state.
  → [docs/security/secoc/](docs/security/secoc/README.md)
- **Complete DataFlash map.** 122 physical records; triplicate bank +
  checkpoint ring; pages 432–479 are the SecOC object bank.
  → [docs/storage/dataflash.md](docs/storage/dataflash.md)
- **Two independent UDS stacks.** Bootloader (placeholder `F181`, strict
  `0203→0201→0202` write sequence) and application (17 services, 242 readable
  DIDs, real `F181`/`F186`/`F18C`, programming-handoff gate).
  → [docs/diagnostics/](docs/diagnostics/README.md)

The canonical claim-by-claim ledger with evidence grades is
[docs/status/FINDINGS.md](docs/status/FINDINGS.md). Superseded conclusions are
in [docs/status/CORRECTIONS.md](docs/status/CORRECTIONS.md).

## Start here

### Explore the committed project

The annotated Ghidra project is committed under `project/` — you can explore
it without rebuilding. **Never open `project/` directly with a daemon**;
materialize a working copy first:

```bash
make work-project   # one-time: copy snapshot -> build/project
ghidra --projects-dir "$PWD/build/project" --project rh850_p1me_mapped \
       --program RH850_P1M-E_CodeFlash.bin stats
```

### Run verification

```bash
uv sync --locked
make verify            # twenty-two firmware suites (no Ghidra)
```

### Rebuild from firmware

```bash
make rebuild-project   # fresh four-stage rebuild into build/project/
```

The full operating manual — durability trap, working copy vs. committed
snapshot, four-stage rebuild, CI — is [docs/WORKFLOW.md](docs/WORKFLOW.md).

## Documentation map

| Goal | Document |
|---|---|
| Ten-minute firmware overview | [docs/OVERVIEW.md](docs/OVERVIEW.md) |
| Open / verify / rebuild the project | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Claim-by-claim evidence ledger | [docs/status/FINDINGS.md](docs/status/FINDINGS.md) |
| Boot flow and execution architecture | [docs/architecture/](docs/architecture/README.md) |
| UDS diagnostics (bootloader + application) | [docs/diagnostics/](docs/diagnostics/README.md) |
| SecurityAccess, payload gate, SecOC | [docs/security/](docs/security/README.md) |
| CAN transport, Rx/Tx maps | [docs/communications/](docs/communications/README.md) |
| DataFlash / NvM storage | [docs/storage/](docs/storage/README.md) |
| Sienna vs. Corolla vs. TSS 3 family | [docs/variants/](docs/variants/README.md) |
| Processor-module audit | [docs/tooling/](docs/tooling/README.md) |
| Address and artifact lookup | [docs/reference/](docs/reference/README.md) |

## File layout

`RH850_P1M-E_Firmware.bin` (`0x108000` bytes) is **two flash regions**, not
one flat block. Always split before importing:

| File range | Size | Virtual range | Region |
|---|---:|---|---|
| `0x000000–0x007fff` | `0x8000` | `0xFF200000–0xFF207FFF` | DataFlash |
| `0x008000–0x107fff` | `0x100000` | `0x00000000–0x000FFFFF` | CodeFlash |

CodeFlash VA = file offset − `0x8000`. The committed images under `firmware/`
are already split; `tests/verify_findings.py` re-checks their hashes,
reconstructs the combined image in memory, and verifies every base finding.

## Repository layout

| Path | Contents |
|---|---|
| `docs/` | Subsystem analysis reports (see map above) |
| `firmware/` | Committed CodeFlash/DataFlash split images |
| `data/` | Generated analysis artifacts (CSVs — machine-readable canonical maps) |
| `ghidra/scripts/` | Import, seed, annotate, investigate, verify scripts |
| `project/` | Committed Ghidra project snapshot — **never daemon-open directly** |
| `tests/` | Self-contained verification suites plus optional external corroboration |
| `tools/` | Data generators and the durable project rebuild workflow |
| `legacy/flat-import/` | Preserved invalid original analysis — do not use |

## Evidence policy

Every material claim has one canonical home in a subsystem report and an
evidence grade: **verified** (deterministic test), **recovered** (control/data
flow reconstructed), **bounded** (interpretation constrained), **hypothesis**
(plausible, unverified), **disproved** (retained to prevent regression).
Definitions and the full ledger: [docs/status/FINDINGS.md](docs/status/FINDINGS.md).
