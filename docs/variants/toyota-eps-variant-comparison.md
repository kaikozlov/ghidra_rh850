# Toyota EPS security/control variant comparison

> **Document type:** variant comparison
>
> **Status:** active evidence matrix
>
> **Evidence grade:** mixed (per-cell; see the CSV)

The machine-readable matrix is `data/toyota_eps_variant_matrix.csv`. Each firmware
specimen has two classifications:

- `adas_generation` records the TSS/control generation.
- `security_architecture` records SecOC/TSK/security evidence.


## Current evidence-backed rows

| Specimen | ADAS/control generation | Security architecture | Firmware status | Main use in this repository |
|---|---|---|---|---|
| Sienna `8965B4512000` | unknown | SecOC/TSK | exact tracked image | deep security/diagnostic/control donor; protected `0x2E4/0x131` prior art |
| Sienna `8965B4514000` | externally reported TSS3 | SecOC/TSK external key-validation evidence | CodeFlash unavailable | external DataFlash/key validation |
| Corolla `8965H1202000` | TSS3 vehicle/P5 control context | SecOC/TSK | exact tracked image | exact newer-EPS receiver/state/control contract |
| Corolla `8965F1208000` | TSS3 vehicle/P5 control context | SecOC/TSK | exact tracked image | application-identical H/F transfer + 2025 field acquisition |

The old empty Camry/RAV4 placeholder rows were removed. Keep unacquired vehicles
in `OPEN_QUESTIONS.md` / the acquisition queue.

## What actually transfers

The Sienna and Corolla images share substantial Denso/RH850 security and software infrastructure.
The exact H/F applications are byte-identical to each other and their active
SecOC queue is `0x00F/0x0D7/0x0B6`; they do not carry the Sienna `0x2E4/0x131`
steering profiles. H/F instead receive target-angle control on protected FD
`0x0B6` and use a different feedback/status surface. H/F retain the same static
application/boot security roots as the tracked Sienna, but their SecOC generated
profile/configuration and vehicle-control message set differ. Each matrix cell
records its own evidence source.

The H/F raw-body transfer reports use the registered canonical Sienna inventory,
`data/ghidra_project_inventory.baseline.jsonl`: 7,089 CodeFlash function ranges
and 634 user-named functions. Both targets have 1,194 exact-body transfers.
The structural inputs are tracked alongside their target data; regeneration
commands are in [the workflow](../WORKFLOW.md#cross-variant-structural-fingerprints).


For the openpilot-specific cross-generation result, use
[toyota-openpilot-porting-contract.md](../architecture/toyota-openpilot-porting-contract.md)
and `data/generated/corolla_tss3_opendbc_readiness.json`.

## 2026-10-16 maintained request-signer transfer audit

The maintained `tss3-request-signer` uses one C resident/helper, with immutable dump-resolved configurations. Exact 1-MiB images of Camry `8965F3307000`, Crown `8965F3012000`, Corolla `8965F1208000` and Corolla H `8965H1202000` all resolve the complete runtime contract: app context and startup/shadow boundary, TAUJ0 5-ms foreground, classic functional `0x777` into native software Rx ring, signed freshness input, command-five wrapper, and exact CanIf primary `0x7A9` response route. Crown selects response handle 50 (Camry 53); both Corolla images select 50. Crown/Camry place private request state/scratch in the proven SID23-adjacent LocalRAM exclusion; Corolla H/F reclaim the resident's dead entry prefix as state and use GlobalRAM tail scratch. These differences are represented in the universal config.

On the contributor Crown, September's native-B6 MAC equality and subsequent signed soaks establish that the stock ECU can execute a resident and use type1/slot4 command five. October 10–12 request-signer logs record timeouts; see `community/mruno/README.md`.

For Corolla H/F, the two exact application images are byte-identical at `0x17E00..0xFFFFF`, with specimen-specific low calibration and F181 secondary identity. The 2023 and Span 2025 moving captures independently contain native `0x08A/32` and `0x081/32` but **no active lateral ID11**; read-only DBC decode/re-encode reproduces the entire 28-byte `0x08A` application in all 4,755 observed requests, and stock-longitudinal cloning retains all other fields. This establishes a shared inactive request-plane wire image.

**2026-10-16 verification:** `tools/test tss3_request_signer`, `tss3_resident_control_ingress`, `crown_8965f3012000` and `corolla_hf_command5` passed at least once; the GNU CodeFlash suite completed universal fallback/idle simulation for all four images before an intermittent `helper embedding drift` during its optional optimized build. Repeated direct `-O2` builds passed; that failure's cause remains unresolved. The P1M-E scenario runner stopped at `ReadOnlyException` while opening the working Camry Ghidra project.

After canonical inventory regeneration, `tools/test spanconstant_corolla_codeflash`
passes all five verification paths, including the Span-vs-Sienna transfer check.

## Adding a variant

1. Add a row to `data/toyota_eps_variant_matrix.csv` only after a concrete
   firmware/field artifact exists.
2. Populate `adas_generation` and `security_architecture` independently. Use
   `unknown` / `not established` when evidence for either field is missing.
3. If firmware is in hand, create a `variants/<name>-<partnumber>.md` and add
   target-native verification.
4. Keep unacquired family targets in `OPEN_QUESTIONS.md`. Matrix rows require
   observed evidence.

For an unidentified newer-TSK target, first satisfy the identity/artifact contract
in [newer-tsk-target-evidence.md](newer-tsk-target-evidence.md).
