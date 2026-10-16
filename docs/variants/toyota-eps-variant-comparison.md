# Toyota EPS security/control variant comparison

> **Document type:** variant comparison
>
> **Status:** active evidence matrix
>
> **Evidence grade:** mixed (per-cell; see the CSV)

The machine-readable canonical matrix is
`data/toyota_eps_variant_matrix.csv`. The filename and schema deliberately avoid
calling every row TSS3: this table now tracks two independent properties for each
firmware specimen.

- `adas_generation` records the TSS/control generation **only when independently
  established**.
- `security_architecture` records SecOC/TSK/security evidence independently.

All three tracked firmware dump families (Sienna `8965B4512000`, Corolla
`8965H1202000`, Corolla `8965F1208000`) are SecOC/TSK cars. That does **not** make
SecOC synonymous with TSS3, and the Sienna donor does not acquire a TSS-generation
label from its security architecture. The old `tss3_eps_variant_matrix.csv` name
was therefore retired; see CORR-108.

## Current evidence-backed rows

| Specimen | ADAS/control generation | Security architecture | Firmware status | Main use in this repository |
|---|---|---|---|---|
| Sienna `8965B4512000` | not established by this matrix | SecOC/TSK | exact tracked image | deep security/diagnostic/control donor; protected `0x2E4/0x131` prior art |
| Sienna `8965B4514000` | externally reported TSS3; independent of SecOC evidence | SecOC/TSK external key-validation evidence | CodeFlash unavailable | external DataFlash/key boundary only |
| Corolla `8965H1202000` | TSS3 vehicle/P5 control context | SecOC/TSK | exact tracked image | exact newer-EPS receiver/state/control contract |
| Corolla `8965F1208000` | TSS3 vehicle/P5 control context | SecOC/TSK | exact tracked image | application-identical H/F transfer + 2025 field acquisition |

The old empty Camry/RAV4 placeholder rows were removed. Unacquired vehicles belong
in `OPEN_QUESTIONS.md` / the acquisition queue, not in a data table that can be
mistaken for observed evidence.

## What actually transfers

The Sienna and Corolla images share substantial Denso/RH850 security and software
infrastructure, but the **control generation is not portable by security profile**.
The exact H/F applications are byte-identical to each other and their active
SecOC queue is `0x00F/0x0D7/0x0B6`; they do not carry the Sienna `0x2E4/0x131`
steering profiles. H/F instead receive target-angle control on protected FD
`0x0B6` and use a different feedback/status surface. That is why the Sienna image
remains excellent SecOC/TSK prior art without being a template for the TSS3
Corolla wire contract.

Conversely, security findings transfer only when proved from bytes. H/F retain
the same static application/boot security roots as the tracked Sienna, but their
SecOC generated profile/configuration and vehicle-control message set differ.
Each matrix cell therefore records its own evidence source instead of using
"same family" as a proof shortcut.

## What "same software family" does and does not mean

Matching service tables, crypto roots, or diagnostic architecture are useful
Denso continuity evidence. They do **not** prove:

- the same TSS/control generation;
- the same SecOC protected-message set;
- the same lateral or longitudinal wire contract;
- the same MCU or bootloader bytes unless independently checked;
- the same stock command producer or Panda interception topology; or
- that a field observation on one vehicle belongs to another exact firmware image.

For the openpilot-specific cross-generation result, use
[toyota-openpilot-porting-contract.md](../architecture/toyota-openpilot-porting-contract.md)
and `data/generated/corolla_tss3_opendbc_readiness.json`.

## 2026-10-16 maintained request-signer transfer audit

The maintained `tss3-request-signer` uses one C resident/helper, with immutable dump-resolved configurations rather than copied Camry absolute addresses. Exact 1-MiB images of Camry `8965F3307000`, Crown `8965F3012000`, Corolla `8965F1208000` and Corolla H `8965H1202000` all resolve the complete runtime contract: app context and startup/shadow boundary, TAUJ0 5-ms foreground, classic functional `0x777` into native software Rx ring, signed freshness input, command-five wrapper, and exact CanIf primary `0x7A9` response route. Crown selects response handle 50 (Camry 53); both Corolla images select 50. Crown/Camry place private request state/scratch in the proven SID23-adjacent LocalRAM exclusion; Corolla H/F instead reclaim the resident's dead entry prefix as state and use GlobalRAM tail scratch. These differences are already represented in the universal config. Matching this contract establishes *CPU/software feasibility* only.

On the contributor Crown, September's native-B6 MAC equality and subsequent signed soaks establish that the stock ECU can execute a resident and use type1/slot4 command five. They do **not** prove the newer `0x008A` request-signer path's GlobalRAM helper execution, raw four-fragment receipt or `0x7A9` output. October 10–12 request-signer logs time out, but do not contain authenticated runtime counters or reliably verify the currently instrumented host; see `community/mruno/README.md`. A fresh current build and session readback are needed to discriminate stages before altering payload assumptions.

For Corolla H/F, the two exact application images are byte-identical at `0x17E00..0xFFFFF`, with specimen-specific low calibration and F181 secondary identity. The 2023 and Span 2025 moving captures independently contain native `0x08A/32` and `0x081/32` but **no active lateral ID11**; read-only DBC decode/re-encode reproduces the entire 28-byte `0x08A` application in all 4,755 observed requests, and stock-longitudinal cloning retains all other fields. This establishes a shared inactive request-plane wire image, not MAC equivalence or an active FRC/Brake/VMM handoff. Physical repin and sole-source replacement, active request ID11/result/steering correlation, CAN state and fault transitions, and target-specific stock PCS/ACC coexistence remain live gates. The maintained fork's TSS3 Panda angle safety parameter and per-vehicle dynamics must also be verified independently; Camry calibration and vehicle model are not universal.

**Verification boundary on this local checkout:** `tools/test tss3_request_signer`, `tss3_resident_control_ingress`, `crown_8965f3012000` and `corolla_hf_command5` passed at least once; the GNU CodeFlash suite completed universal fallback/idle simulation for all four images before an intermittent `helper embedding drift` during its optional optimized build. Repeated direct `-O2` builds passed, so that failure's cause is not established. The P1M-E scenario runner could not open the working Camry Ghidra project (`ReadOnlyException`) and therefore did not produce a fresh four-target machine verdict. The historical Span-vs-Sienna function-transfer verifier also fails against the newer Sienna canonical inventory (7,089 rows versus 6,375 retained), while the direct H/F equivalence checks pass; do not reuse the old transfer counts as current-corpus counts.

## Adding a variant

1. Add a row to `data/toyota_eps_variant_matrix.csv` only after a concrete
   firmware/field artifact exists.
2. Populate `adas_generation` and `security_architecture` independently; use
   `unknown` / `not established` rather than deriving one from the other.
3. If firmware is in hand, create a `variants/<name>-<partnumber>.md` and add
   target-native verification.
4. Keep unacquired family targets in `OPEN_QUESTIONS.md` instead of speculative
   all-unknown matrix rows.

For an unidentified newer-TSK target, first satisfy the identity/artifact contract
in [newer-tsk-target-evidence.md](newer-tsk-target-evidence.md).
