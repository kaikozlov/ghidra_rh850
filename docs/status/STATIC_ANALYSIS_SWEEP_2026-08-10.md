# Comprehensive static-analysis sweep — 2026-08-10

Living execution journal for the staged sweep defined by
`REFERENCE/ghidra_rh850_codex_static_analysis_handoff.md`. Firmware bytes and
the pinned external artifacts are the evidence sources; existing narrative
documents are used only for navigation.

## Run identity

- Branch: `main`
- Starting commit: `0e97e8a2ad1d093f5a6f12f4e928f404a0f55b24`
  (`test: characterize Vance candidate f05 payload`)
- Starting worktree: clean
- Ghidra working project: `build/project/`
- Committed `project/` opened by daemon: no

## Baseline verification

| Command | Result |
|---|---|
| `uv sync --locked` | pass; 5 locked packages resolved, 4 checked |
| `make verify` | pass; all deterministic firmware, generated-artifact, external-artifact, lifecycle, project-layout, and documentation suites completed with zero failures |
| `make verify-external EXTERNAL_REPOS_DIR=/Users/kai/dev/inspect/repos` | pass; 162 checks, 0 failures |
| `make ghidra-cli` | pass; vendored CLI `v0.2.1` built under `build/ghidra-cli/` |
| `make verify-sleigh` | pass; processor manifest `5274c7d09d222e6d7f7d4b91750d8b549c7e9ace465bd05493652de6b944fbe9` |
| `make work-project` | pass; existing `build/project/` retained |
| `tools/g session-status` | daemon stopped; processor fingerprint matching; working session clean; snapshot unchanged |

## Artifact availability matrix

The local search covered the repository, ignored repository paths, and the
adjacent checkouts below `/Users/kai/dev/inspect/repos`. It pruned only VCS
metadata, dependency caches, and build-tool caches. The ignored Techstream tree
was searched separately. No search traversed unrelated personal storage.

| Artifact | State | Primary evidence / boundary |
|---|---|---|
| `firmware/RH850_P1M-E_CodeFlash.bin` | available | 1 MiB; SHA-256 `21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde` |
| `firmware/RH850_P1M-E_DataFlash.bin` | available | 32 KiB; SHA-256 `81d87b678784bb2a07b1fdcb3d43dd40767d4f5ca1b56867b6575cd652a9ecb8` |
| Original combined `4512000` image | available | pinned checkout `RH850_P1m-E` at `b8c6bcf6b84763a9c5288fc8fa6766ebfe66ce4a`; reconstructed SHA-256 `0bba74d0e443f9dd3da33e3a28c3511ec31e35e8303acef7e0117fbdc91d5a86` |
| Vance Sienna checkout | available | `/Users/kai/dev/inspect/repos/ToyotaSienna2024OpenpilotAnalysis-_Note` at locked `3333453f10c09a27df265156458ce976cc9ce25a` |
| Vance v3 deployment bundle | available | `scripts/secoc/20260531_othersienna_secoc_bundle_v3.zip`; 29,707 bytes; SHA-256 `dea6d6e0b242f287725b117231d39dcddbc8823680cbc628ab17cd2bbdb3e4e4`; contains both standard and candidate-f05 payloads |
| Vance completed partner dump/capture outputs | unavailable | v3 archive census and `verify_external_corroboration.py` prove the bundle contains no completed partner outputs |
| Bk2ol DataFlash checkout | available | `/Users/kai/dev/inspect/repos/tsk_extraction_by_can_log` at locked `db453752beeb7cdd024a1a9c38c6711c981e75ad` |
| I-CAN-hack SecOC checkout | available | `/Users/kai/dev/inspect/repos/secoc` at locked `4ce19cc31ff560b697bcd59cc3db55711f50b7b3` |
| Calvin Park openpilot checkout | available | `/Users/kai/dev/inspect/repos/calvinpark-openpilot` at locked `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822` |
| Pinned opendbc checkout | available | `/Users/kai/dev/inspect/repos/opendbc` at locked `c9b31d21bc396e8958891e271936bdbdf1a6ca93`; all pinned sender/DBC hashes pass |
| Additional reference opendbc checkout | available, not the locked evidence checkout | `REFERENCE/opendbc` at `a0febba355168a5cb6168b535144c8c41a5ce323` |
| Unpacked Techstream V18 tree | available | ignored `Techstream/unpacked/toyota/Toyota Diagnostics/`; `Techstream.exe`, `IT3UtilityNK.dll`, `IT3UtilityRevNK.dll`, `eVbBroker.dll`, `td3webapi.dll`, both `ptshim32` variants, and `Cuw.exe` present; pinned artifact tests pass |
| Existing Techstream PE-analysis projects | available | `build/pe-project/techstream_exe.gpr`, `build/pe-project/pe_dlls.gpr`, and nested `pe_dlls/rh850_p1me_mapped.gpr` |
| Renesas RFP V3.24.00 | available | ignored `Renesas/renesas_flash_programmer_macos-arm64/`; locked `libRFP.dylib`, `rfp-cli`, `Devices.xml`, docs, and RA6B1 provisioning image all pass `verify_renesas_rfp.py` |
| P1M-E datasheet | available | `REFERENCE/r01ds0505ed0100-rh850p1m-e.pdf`; SHA-256 `71b80cf05abf256f4047c7c2d6fa706438f70440e5e2959f1ce83d18c7822aad` |
| Retained RH850 manuals | available | `REFERENCE/r01uh0585ej0120_manual.pdf` SHA-256 `aaea89a7f5d9b029776945868d21728465d372223c41db05cbd728a0499a6e34`; `REFERENCE/r01us0001ej0100_v850e2m.pdf` SHA-256 `6bd1265ff3e6c94ab63809708569b623b18459706ea1c7111852abc4b59dda24` |
| Retained AUTOSAR SHE sources | available | `REFERENCE/AUTOSAR-4.2.2.json`, `4.3.1`, `4.4`, `R19-11`, and `R20-11` |
| Matching Sienna EPS `.cuw`/`.cwe`/HEX/MOT/S-record | unavailable | bounded filename search across repository, ignored Techstream tree, and adjacent repository checkouts found only unrelated Renesas RA external-memory HEX files |
| `8965B4514000` CodeFlash | unavailable | bounded filename and firmware-shaped-binary search found no candidate; only reports and the Vance DataFlash-payload bundle are present |
| Corolla `8965F1208000` firmware | unavailable | bounded filename and firmware-shaped-binary search found no candidate; only the repository variant report is present |
| Same-vehicle protected-traffic producer firmware | unavailable | no newly identified ADAS/PCS/camera/radar firmware artifact in the bounded local corpus |

## Stage checklist

- [x] Stage 0 — bootstrap, baseline verification, and living sweep journal
- [ ] Stage 1 — fully reverse Vance `candidate-f05`
- [ ] Stage 2 — recover the complete Techstream MACKey vehicle-side protocol
- [ ] Stage 3 — close remaining high-value Techstream static leads
- [ ] Stage 4 — complete the Renesas RV40F host-protocol static census
- [ ] Stage 5 — close the application COM receive/transmit long tail
- [ ] Stage 6 — tighten the motor-control and safety static boundary
- [ ] Stage 7 — close remaining useful security-side static questions
- [ ] Stage 8 — bounded external-reference and missing-artifact acquisition sweep
- [ ] Stage 9 — status reconciliation and final Ghidra project integration

## Stage 0 — bootstrap, baseline verification, and living sweep journal

### Starting state

- HEAD: `0e97e8a2ad1d093f5a6f12f4e928f404a0f55b24`
- Relevant prior finding IDs: `SECOC-030`, `SECOC-031`, `TMS-011`,
  `TMS-013`, `RFP-001`–`RFP-006`, `COM-002`, `COM-003`, `ARCH-007`–`ARCH-009`
- Relevant artifacts: firmware pair, all six locked public repositories, Vance
  v3 bundle, Techstream V18 tree and PE projects, RFP V3.24.00, retained P1M-E
  and AUTOSAR source material
- Verification baseline: clean worktree; all required baseline commands pass

### Questions

1. Does the checkout match the handoff baseline without pre-existing changes?
2. Are all locally retained primary and pinned external artifacts actually
   present and hash/revision correct?
3. Have any formerly missing calibration or variant firmware artifacts appeared
   in the bounded local research corpus?

### Work performed

- Commands/tools: `git status`, `git rev-parse`, `git log`, `uv sync --locked`,
  `make verify`, `make verify-external`, `make ghidra-cli`,
  `make verify-sleigh`, `make work-project`, `tools/g session-status`, bounded
  `find`/`rg`/hash/revision census, and ZIP member census.
- Functions/files inspected: repository operating contract and workflow;
  overview; findings, open-questions, and roadmap ledgers; all three lock files;
  firmware hashes; external checkout revisions; Vance v3 member list;
  Techstream/RFP/manual and PE-project paths.
- Generated artifacts: none. This journal is curated run metadata.

### Findings

- The repository exactly matches the handoff's expected clean baseline —
  source: repository state, grade: **verified**.
- Every locked external repository and locked artifact required for Stages 1–4
  is locally available and revision/hash correct — source: external artifacts,
  grade: **verified** by `verify_external_corroboration.py` and the Techstream/RFP
  deterministic suites.
- No matching Sienna calibration file, `4514000` CodeFlash, Corolla
  `8965F1208000` firmware, completed Vance partner output, or protected-traffic
  producer firmware is present in the bounded local corpus — source: local
  artifact census, grade: **bounded**.

### Negative/bounded results

- Filename/content-shaped local acquisition remains blocked for the three
  named missing high-value binaries. This is a current local-availability
  result, not a claim that no public artifact exists; Stage 8 will inspect
  upstream deltas and public availability.
- The extra `REFERENCE/opendbc` checkout is newer/different than the locked
  evidence revision and is not used as primary evidence unless separately
  pinned later.

### Documentation/tests changed

- Added this living sweep journal only. No later-stage finding or stale-status
  reconciliation is mixed into the bootstrap boundary.

### Verification

- `uv sync --locked` -> pass
- `make verify` -> pass
- `make verify-external EXTERNAL_REPOS_DIR=/Users/kai/dev/inspect/repos` ->
  pass (162/162)
- `make ghidra-cli` -> pass
- `make verify-sleigh` -> pass
- `make work-project` -> pass
- `tools/g session-status` -> daemon stopped, clean, fingerprint matching,
  snapshot unchanged

### Remaining blockers

- Matching Sienna `.cuw`, `4514000` CodeFlash, Corolla `8965F1208000`
  firmware, same-vehicle producer firmware, and completed Vance partner output
  remain unavailable locally.

### Commit

- Pending Stage 0 commit; its immutable SHA will be recorded at the next
  journal update because a commit cannot contain its own final object ID.

