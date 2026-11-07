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

Keep acquisition requirements in the relevant target report and
[execution queue](../status/PRIORITIES.md).

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

## 2026-10-28 maintained request-signer transfer audit

The maintained `tss3-request-signer` uses one C resident/helper, with immutable dump-resolved configurations. Exact 1-MiB images of Camry `8965F3307000`, Crown `8965F3012000`, Corolla `8965F1208000`, Corolla H `8965H1202000`, and Sienna `8965B4512000` all resolve the complete runtime contract: application F181 records, app context and startup/shadow boundary, TAUJ0 5-ms foreground, classic functional `0x777` into the native software Rx ring, signed freshness input, command-five wrapper, and exact CanIf primary `0x7A9` response route. The F181 callback supplies either one or two records; firmware addresses inside the callback, foreground timing flag, freshness initializer, and transmit-resource table contents are resolved rather than selected by vehicle family. Response handles are Camry 53, Crown 50, both Corolla images 50, and Sienna 57. All five use the resident's dead entry prefix as private state and GlobalRAM tail scratch; payload-owned memory has one invariant ABI rather than a vehicle-specific configuration.

On the contributor Crown, September's native-B6 MAC equality and subsequent signed soaks establish that the stock ECU can execute a resident and use type1/slot4 command five. October 10–12 request-signer logs record timeouts; see `community/mruno/README.md`.

For Corolla H/F, the two exact application images are byte-identical at `0x17E00..0xFFFFF`, with specimen-specific low calibration and F181 secondary identity. The 2023 and Span 2025 moving captures independently contain native `0x08A/32` and `0x081/32` but **no active lateral ID11**; read-only DBC decode/re-encode reproduces the entire 28-byte `0x08A` application in all 4,755 observed requests, and stock-longitudinal cloning retains all other fields. This establishes a shared inactive request-plane wire image.

**2026-10-28 verification:** `tools/test tss3_request_signer` built the common payload, matched host and on-device resolver output across the four deployment-registered images plus exact Sienna CodeFlash, and exercised the compiled helper core. `tools/toyota ram onboard firmware/RH850_P1M-E_CodeFlash.bin` resolved all nine components, passed fallback and idle-fast GNU simulation, and passed all 16 exact-firmware P1M-E machine scenarios on `sienna-8965B4512000`.

After canonical inventory regeneration, `tools/test spanconstant_corolla_codeflash`
passes all five verification paths, including the Span-vs-Sienna transfer check.

## XCP and communication-stack split

XCP presence lines up with one CanTp integration, and XCP absence does not
line up with a single alternative. The XCP-present images use a
32-bit-length CanTp behind 16-bit adapters, a fixed configuration pointer,
and shared transmit scratch. Crown and Tundra CPU11 use native 16-bit
descriptors, a voted runtime configuration pointer, and stack-local
transmit frames. Tundra CPU12's CanTp init slot is `jmp lp`. These are firmware
implementation fingerprints, not OEM release names.

| Exact image | XCP | CanTp receive adapter / PCI dispatcher | Single-frame transmit builder |
|---|---|---|---|
| Sienna `8965B4512000` | present, gated | `794EA / 79454`: widen to 32 bits | `7A506`: shared `FEBE4EF0` |
| Corolla H/F | present, gated | `7388A / 737F4`: widen to 32 bits | `748A6`: shared `FEBE4DE8` |
| Camry `8965F3307000` | present, gated | `7A57A / 7A4E4`: widen to 32 bits | `7B596`: shared `FEBE4EFC` |
| Crown `8965F3012000` | absent | `81D7A / 81CE4`: native 16 bits | `82D26`: stack-local eight-byte frame |
| Tundra `8965F3401200` (CPU11) | absent | `7CB1A / 7CA84`: native 16 bits | `7DAC6`: stack-local eight-byte frame |
| Tundra `8965F3402200` (CPU12) | absent | `77C88` calls `78CC8` (`jmp lp`) | — |

Target-native decompilation verifies each row. Instruction-shape matching
locates the homologs; it does not establish their semantics. Camry
`7A4EE: 27 0F 05 00` is `ld.w 4[r7],r1`; Crown
`81CEE: E7 0F 05 00` is `ld.hu 4[r7],r1`. Exact-image GNU execution with
descriptor word `00010000` observes Camry read `65536` and Crown read `0`,
taking different length-test branches.

Configuration binding independently follows the split. Getters Sienna
`7929E`, Corolla `7363E`, and Camry `7A32E` return constant CodeFlash
configuration addresses `22D50`, `22B94`, and `22C70`. Crown initializer
`82A8A` publishes pointer/inverse/duplicate at `FEBE4AEC/4AF0/4AF4`;
getter `81AF2` votes and repairs that triplet under interrupt guards.
GNU execution of its voting interval `81AFA..81B32` repairs a corrupted
first pointer using the other two. The full getter encounters an unsupported
privileged instruction in the GNU simulator's interrupt guard.
Tundra CPU11 getter `7C892` votes the same pointer, inverse, and duplicate
at `gp-6338`, `gp-6334`, and `gp-6330`. CPU11 init `7AE90` calls `7BFF2`,
which writes `FFFF` into the channel-state halfwords. CPU12 init `77C88`
calls `78CC8`, whose only instruction is `jmp lp`. CPU11's PCI dispatcher
`7CA84` reads the length with `ld.hu 4[r7], r1` (`E7 0F 05 00`).

The shared higher layers make this a matched comparison: all 17
service-level SID policies have the same session/security/count shape across
Sienna, Corolla, Camry and Crown; Camry and Crown also have identical
242-record DID metadata. Crown retains SID23's zero-count range-security
allowlist and the RAM-copy backend `4F184 -> 4F0DE -> 4F122`. Exact-image
execution reads `FEBF7C00` through that backend. The identical startup shadow
copy and MPU window also remain. In the code section holding Camry's XCP,
Crown has 98,640 bytes of contiguous padding to `AEB00`; Camry has 87,552.

XCP is present and gated on Sienna, Corolla H/F, and Camry, and absent on
Crown and the four Tundra application images. Descriptor width does not
decide inclusion: CPU11 keeps the 16-bit CanTp integration without XCP, and
CPU12 ships no CanTp at all. The bytes show compile-time bundle selection.
Flash capacity, the shared diagnostic tables, and the `FEBF7C00` window are
present on the XCP-absent Crown image.

### Wire identities and rejected tooling explanation

Sienna uses standard `7F7/7F8`. Corolla H/F and Camry use extended
`1FDC0002/1FE00002`: `9FDC0002/9FE00002` include hardware IDE bit 31.
The exact Sienna `836B4` and Corolla `7DAB4` filter loaders write the
respective request words directly to GAFLID; both were executed in GNU
simulation. The [scanner](../tooling/rh850-codeflash-structure-scanner.md)
now reports these identities separately.

The Sep-10 Camry C7 steering-request consumer was our injected helper.
Its use of the stock receive mailbox establishes reachability.

The Unified-writer post-reset tail is a different identifier from Sienna's
`7F7` route. V18 and the unprotected GTS+ builds of
`TCUWCanUnifiedFlashWriter.dll` and
`TCUWCanUnifiedFlashWriterEachArea.dll` emit `777` data `10 81` and `77F`
data `FE 10 81` (second frame length 7, TxFlags `80`). None of those four
binaries contains a `7F7` immediate. `T-0035-22` (`8965F3401200/2200`) and
`T-0036-22` (`8965F3403200/4200`) select `P5-Unified`, which resolves to the
normal writer. Those application images have no `7F7` acceptance rule.

## Adding a variant

1. Add a row to `data/toyota_eps_variant_matrix.csv` only after a concrete
   firmware/field artifact exists.
2. Populate `adas_generation` and `security_architecture` independently. Use
   `unknown` / `not established` when evidence for either field is missing.
3. If firmware is in hand, create a `variants/<name>-<partnumber>.md` and add
   target-native verification.
4. Keep unacquired family-target requirements in the relevant target report.
   Matrix rows require observed evidence.

For an unidentified newer-TSK target, first satisfy the identity/artifact contract
in [newer-tsk-target-evidence.md](newer-tsk-target-evidence.md).
