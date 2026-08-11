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
- [x] Stage 1 — fully reverse Vance `candidate-f05`
- [x] Stage 2 — recover the complete Techstream MACKey vehicle-side protocol
- [x] Stage 3 — close remaining high-value Techstream static leads
- [x] Stage 4 — complete the Renesas RV40F host-protocol static census
- [x] Stage 5 — close the application COM receive/transmit long tail
- [x] Stage 6 — tighten the motor-control and safety static boundary
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

- `cf07d4e79d7668abbcf455d072d36e66f1210289 docs: start comprehensive static-analysis sweep`

## Stage 1 — fully reverse Vance `candidate-f05`

### Starting state

- HEAD: `cf07d4e79d7668abbcf455d072d36e66f1210289`
- Relevant prior finding IDs: `SEC-BOOT-001`–`SEC-BOOT-006`, `SECOC-024`,
  `SECOC-030`
- Relevant artifacts: pinned Vance v1/v2/v3 deployment bundles; standard
  DataFlash payload; candidate-f05 ciphertext; committed CodeFlash secrets;
  pinned I-CAN-hack and Bk2ol shellcode sources
- Verification baseline: Stage 0 full and external gates pass; Ghidra daemon
  stopped and main working project clean

### Questions

1. Which key/authentication construction produces a valid candidate plaintext?
2. What are every function, basic block, absolute reference, memory range,
   loop, call, and terminal behavior in the changed code?
3. Does candidate-f05 dump, scan, probe, or expose a different result protocol?
4. Is any `f05` identifier present beyond payload authentication/filename?
5. What source family and exact provenance does retained history support?

### Work performed

- Commands/tools: independent OpenSSL AES-ECB/AES-CBC/CMAC reproduction;
  independent CRC32/diff census; raw `v850e3:LE:32:default` Ghidra imports at
  `0xFEBF0000`; full entry/trampoline/epilogue disassembly and decompilation;
  exact source/byte searches across all pinned community checkouts; Vance ZIP
  member/hash/time census and Git-history audit.
- Functions/files inspected: candidate `0xFEBF0000..0xFEBF01B1`; standard
  `0xFEBF0000..0xFEBF0189`; local reset trampoline `0xFEBF019C`; candidate
  return epilogue `0xFEBF01A0`; I-CAN-hack `shellcode/main.c`; Bk2ol
  `main_ff1ff000_ff209000.c`; all three Vance deployment archives and v3
  README/manifest.
- Generated artifacts: `data/generated/candidate_f05_payload.json`.

### Findings

- Candidate-f05 is a sequential full DataFlash dump over
  `0xFF200000..0xFF207FFF`, four bytes per iteration and 8,192 frames total —
  source: external payload bytes/Ghidra, grade: **verified** (SECOC-031).
- Its output is unchanged classic CAN `0x7A9` through RSCFD slot 16 with bytes
  `07 || address_low24_le || word_le32` — source: external payload bytes,
  grade: **verified**.
- It has no ICU-S, RAM/key-mirror, CodeFlash, special object-15, scan, or oracle
  path. Object-15 DataFlash is read only incidentally inside the full dump —
  source: complete body/reference/CFG census, grade: **verified**.
- The material control-flow delta is terminal behavior: candidate calls boot
  reset `0x157E`; standard spins forever. Saving `lp`, shifted stack locals,
  relocated branches, a call trampoline, and epilogue account for the broad
  byte churn — source: external payload bytes/Ghidra, grade: **verified**.
- Candidate-f05 authenticates only when `SEED_KEY_SECRET @ 0xBFE8` is used as
  the payload-build secret; it embeds no secret, derived key, ASCII `f05`, or
  runtime `f05` signature — source: committed firmware plus external payload,
  grade: **verified**.
- The statement-level source family is the pinned I-CAN-hack/Bk2ol RSCFD dump
  loop. Exact compiler/source revision, human author, build command, selection
  intent, and vehicle execution are not retained — source: pinned Git history,
  grade: **bounded**.

### Negative/bounded results

- The candidate is not an alternate RAM/CodeFlash/ICU-S dump or key-structure
  search; the prior mystery is closed as a DataFlash-dump build variant.
- Identical ciphertext occurs in all three Vance archives. ZIP metadata dates
  the member 2026-05-11 and Git attributes the three archive uploads to
  Vance425 on 2026-05-31, but neither establishes who built the inner payload.
- Filename prefix `f05` plus exclusive authentication under
  `f05f36b7...` makes deliberate key selection plausible, not provable. No
  exact build source or invocation exists in the pinned history.

### Documentation/tests changed

- Added canonical `docs/security/secoc/candidate-f05-payload.md` and linked it
  from the SecOC index and `4514000` variant summary.
- Added finding `SECOC-031`; narrowed the payload-provenance open question;
  recorded Stage 1 under completed static roadmap work. No prior material claim
  was disproved, so `CORRECTIONS.md` does not require a new entry.
- Added the immutable candidate fixture, deterministic 42-check verifier,
  generated semantic JSON, generator, Ghidra raw-payload seed helper, external
  fixture/source corroboration, and verification ownership mapping.

### Verification

- `uv run --locked python tools/generate_candidate_f05_semantics.py` -> pass
- `uv run --locked python tests/verify_candidate_f05_payload.py` -> pass
  (42/42)
- `make verify-one SUITE=candidate_f05` -> pass
- `make verify-external EXTERNAL_REPOS_DIR=/Users/kai/dev/inspect/repos` ->
  pass (175/175)
- `uv run --locked python tests/verify_icus_software_paths.py` -> pass
  (45/45); the first changed-suite run exposed that this older fixture census
  assumed every payload used `PAYLOAD_BUILD_SECRET`, so it now pins each
  fixture's actual build-secret source.
- `make verify-changed` -> pass (10 matched suites, 14 test files)

### Remaining blockers

- Exact human authorship, compiler/build invocation, reason for selecting
  `SEED_KEY_SECRET`, and live ECU acceptance are unavailable in retained static
  artifacts. These no longer block semantic recovery.

### Commit

- `ed7ba4fe67f60d49fa3d255f52d41d0025fbdca2 analysis: recover Vance candidate-f05 payload semantics`

## Stage 2 — recover the complete Techstream MACKey vehicle-side protocol

### Starting state

- HEAD: `ed7ba4fe67f60d49fa3d255f52d41d0025fbdca2`
- Relevant prior finding: `TMS-011`; firmware comparison: command-8 WDBI DID
  `0x1010` at `0x95DCE`/`0x6823C`/`0x86E62`/`0x8997A`
- Relevant artifacts: pinned `Techstream.exe`, `IT3UtilityNK.dll`,
  `IT3UtilityRevNK.dll`, `eVbBroker.dll`, `td3webapi.dll`, and newly joined
  `UtilityExNK2.dll`
- Verification baseline: Stage 1 gates pass; Techstream PE working project is
  disposable under `build/pe-project/`

### Questions

1. Which exact vehicle operations produce VIN, M1/M2/M3, and master/slave
   `SafekeyNumber` fields?
2. How are response records parsed, associated, and written back to ECUs?
3. Is `SafekeyNumber` demonstrably an MCU identity?
4. Does the recovered Techstream flow exactly invoke the Sienna WDBI DID
   `0x1010` command-8 contract?
5. What can be deterministically recovered across all 24 `CMAC_01_*` classes
   and their S324 procedure codes?

### Work performed

- Imported the pinned companion `UtilityExNK2.dll` into the disposable PE
  project through `tools/run_headless`; decompiled the twelve named
  `Ex2MAC_01_*` bridge exports, operation-selector dispatch, vehicle worker
  threads, diagnostic helpers, discovery routine, response parsers, and
  exchange-record decoder.
- Recovered the MSVC RTTI complete-object-locator chain and all 24 vtables
  directly from PE bytes; mapped all 51 distinct embedded S324 procedure/UI
  codes and class associations.
- Independently reopened the Sienna firmware through `tools/g` and inspected
  the WDBI service callback, 64/48-byte command-8 submission and staging, and
  literal ICU-S command-8 trigger before comparing contracts.
- Searched the pinned Techstream tree for MCU/MCUID naming and transformations;
  only the safe-key diagnostic path supplies the 16-byte identity.

### Findings

- The request producers are exact: `22 F1 90` -> VIN[17], `22 10 2E` ->
  M1[16]/M2[32]/M3[16], and `22 10 10` -> raw `SafekeyNumber[16]`. Update
  security uses `27 41/42`; topology uses DIDs `0x1033`, `0x1035`, and the
  `0x1100` family — source: external pinned PE bodies, grade: **verified**.
- Master endpoint `0x763` plus discovered slave endpoints populate up to eight
  ECU records. Returned records are matched by raw 16-byte `SafekeyNumber`, so
  one server transaction can carry master and multiple slave packages —
  source: external pinned PE bodies, grade: **recovered**.
- Native XML readers bound `ExchangeKeyList` iteration to 28 or 8 records,
  parse `SafekeyNumber`, M1, M2, M3, and MACK4, and hex-decode the matched
  record — source: external pinned PE parser bodies, grade: **verified**.
- Vehicle writes use `31 01 30 02 || M1[16] || M2[32] || M3[16]`; polling uses
  `31 03 30 02` and returns a 16-bit state plus M4[32]/M5[16] on completion —
  source: external pinned PE bodies, grade: **verified**.
- `SafekeyNumber` is exactly the unmodified DID-`0x1010` payload. Equivalence
  to a physical MCU ID is not present in the pinned artifacts; the missing
  semantic edge is target firmware or a legitimate capture — grade:
  **bounded**.
- Techstream and Sienna use the same M1–M5 envelope but no exact diagnostic
  join: Routine `0x3002` versus WDBI `2E 01/03 10 10`. Target-EPS/SecOC-slot
  applicability remains unproven — source: external PE plus firmware-static,
  grade: **verified comparison; bounded transfer**.

### Negative/bounded results

- The 51 S324 strings are distributed procedure/UI codes, not a serialized
  central state table. Class-local selectors and branches are recovered, while
  final cross-class successors are chosen by the outer UI/controller callback;
  the generated CSV localizes that bounded edge instead of imposing a false
  linear state order.
- No MCU/MCUID label or transformation proves a silicon-identity meaning for
  safe-key DID `0x1010`.
- The pinned Techstream path does not issue the analyzed Sienna's application
  WDBI command-8 request.

### Documentation/tests changed

- Replaced the bounded native section in canonical
  `docs/security/mackey-registration.md` with the recovered end-to-end flow.
- Updated `docs/tooling/techstream.md`, `TMS-011`, the open-question boundary,
  and completed-static roadmap.
- Added deterministic PE generator
  `tools/generate_techstream_mackey_protocol.py`, JSON/CSV evidence, companion
  hash, full RTTI/vtable census, critical function-body locks, and exact
  command/parser/field assertions to `verify_techstream_mackey.py`.

### Verification

- `uv run python tools/generate_techstream_mackey_protocol.py --check` -> pass
- `uv run python tests/verify_techstream_mackey.py` -> pass (51/51 after the
  complete 51-code census)
- `make verify-changed` -> pass (7 matched suites, 11 test files; rerun after
  stopping both disposable Ghidra daemons)
- `EXTERNAL_REPOS_DIR=/Users/kai/dev/inspect/repos uv run --locked python
  tests/verify_external_corroboration.py` -> pass (175/175)
- firmware evidence independently inspected through `tools/g`; main working
  project snapshot is unchanged

### Remaining blockers

- Physical MCU-ID semantics of DID `0x1010`, actual product applicability, and
  live retry/timing behavior require target firmware or a legitimate capture.
  They do not block the recovered pinned-Techstream protocol.

### Commit

- `c440d272efee7afbc91890f93892eb4758aed644 analysis: recover Techstream MACKey vehicle protocol`
- Follow-up evidence correction before Stage 3 resumed:
  `1b244ebe62c89346c8be1b76cb7eacb033036ea2 analysis: correct Techstream MACKey state evidence`

## Stage 3 — close remaining high-value Techstream static leads

### Starting state

- HEAD: `73392f38991278c58191e6c2a86c72b7d1dd0588`
- Relevant prior finding IDs: `TMS-005`, `TMS-009`, `TMS-013`–`TMS-015`
- Relevant artifacts: pinned `ptshim32.dll`, `ptshim32_0500.dll`,
  `J2534Ctrl.dll`, native `Cuw.exe`, `CUWAccessRKS*.dll`, `Security_P4.ddb`,
  the complete regional steering DDB corpus, and type-1 `Toyota.ddb`
- Verification baseline: the repository had accumulated a separate, fully
  committed Discord-derived static follow-up after Stage 2. Those commits were
  preserved. The only uncommitted Stage-3 work at resumption was the interrupted
  `ptshim` parser/verifier/fixture set; the full repository gate at current HEAD
  was 448 assertions, 0 failures.

### Questions

1. What exact record, timing, encoding, save-path, and cross-version contracts
   define the shipped `ptshim32` log files?
2. Which DDB questions are genuinely still open after the later complete
   directory/corpus work, and do `Security_P4` unknowns hide identity or key
   provisioning material?
3. What exactly becomes RKS `SeedValue`, and is it generated in the request
   path or merely forwarded?
4. Has a matching Sienna calibration/variant artifact appeared in the bounded
   local research corpus since Stage 0?

### Work performed

- Decompiled both pinned shim variants plus `J2534Ctrl.dll` in the disposable
  PE project, traced `PassThruSaveLog`, timestamp helpers, buffer drains,
  controller save-event handling, and exact path construction.
- Completed `tools/techstream/parse_ptshim_log.py` and synthetic v04/v05
  fixtures; added body/hash/string locks against the pinned external binaries.
- Re-audited the complete 35-file steering DDB corpus and performed a targeted
  semantic pass over the previously suspicious high-value `Security_P4`
  sections. Kept the separate type-1 `Toyota.ddb` schema bounded rather than
  expanding into generic format archaeology.
- Decompiled the native CUW RKS request builder and hex encoder and joined them
  to the managed `SetDataForReproKey` field offsets.
- Repeated the bounded artifact search below `/Users/kai/dev/inspect/repos` for
  Sienna/`8965B4512*`/`8965B4514*` calibration or firmware-shaped files.

### Findings

- The shipped ptshim log format is line-oriented text. Both versions record
  API elapsed time/direction/name/arguments, ChannelID where applicable,
  per-message protocol/index/size/flags, Rx message timestamps, raw `\\__`
  bytes, summary counts, and final status. v05 adds a decimal per-message
  handle and uses `PTQueueMsgs` where v04 uses `PTWriteMsgs` — source: pinned
  PE bodies/format strings, grade: **verified** (`TMS-005`).
- Both shims derive elapsed seconds from `QueryPerformanceCounter /
  QueryPerformanceFrequency` relative to the first initialized counter.
  Explicit `PassThruSaveLog` drains wide-character buffered text to UTF-8;
  v04 opens append mode and v05 opens truncate/write mode — source: pinned PE
  bodies, grade: **verified** (`TMS-005`).
- `J2534Ctrl.dll` owns normal Techstream filename/save orchestration. It uses
  local wall-clock time and the exact pattern
  `...\\Techstream\\ErrorReport\\j2534_MMDDYYYYhhmmss.log`, with named SAVE and
  FINISH events around the shim save call. No size-based rotation grammar or
  separate session-record marker was recovered — source: pinned PE body/string
  evidence, grade: **recovered/bounded** (`TMS-005`).
- The old broad DDB-open-question wording is stale. All 35 steering type-2
  databases are structurally parsed through their complete section-type union.
  A targeted `Security_P4` pass resolves type 35 as `Security Alarm Operation`
  and type 37 as a 50-record alarm-condition table rather than a
  Safekey/MACKey provisioning structure — source: pinned DDB bytes/string DB,
  grade: **verified** (`TMS-013`).
- The distinct type-1 `Toyota.ddb` master-enumeration schema remains a real
  format residual, but the recovered MACKey flow no longer depends on decoding
  it. It is now a targeted future identity/routing artifact rather than a
  blocker to Techstream protocol recovery — source: pinned DDB bytes, grade:
  **bounded**.
- Managed `SetDataForReproKey` maps native request buffer `+0x78` directly to
  `SeedValue`. Native `Cuw.exe` passes a pre-existing 16-byte input to the RKS
  request builder and serializes it as 32 uppercase hexadecimal characters
  plus NUL; no RNG/time transform occurs in that request-building edge —
  source: pinned native PE + managed IL, grade: **verified structure / bounded
  provenance** (`TMS-009`).

### Negative/bounded results

- The producer of the 16-byte RKS `SeedValue` input remains one indirect
  controller edge upstream of the recovered request builder. Continuing would
  fan into unrelated native UI/registration machinery, satisfying the handoff's
  bounded-pass stop condition; Layer A still never reaches the ECU.
- `Security_P4`'s targeted high-value unknowns do not expose Safekey, MCU-ID,
  MACM*, MACK4, or keypair vocabulary. Unknown low-value DDB section semantics
  remain intentionally unnamed.
- No matching Sienna EPS `.cuw`/`.cwe`, `4514000` CodeFlash, or named
  Sienna/`8965B4512*`/`8965B4514*` firmware-shaped artifact appeared in the
  bounded local search. This is a local-availability result, not a global
  public-availability claim.

### Documentation/tests changed

- Added the cross-version `ptshim` parser and synthetic fixtures; expanded the
  verifier to pin both shim versions and `J2534Ctrl.dll` save/timestamp logic.
- Added a focused DDB residual verifier covering the complete steering section
  census, `Security_P4` alarm-domain interpretation, and type-1 `Toyota.ddb`
  boundary.
- Extended the existing RKS verifier with managed/native `SeedValue` field,
  width, body-hash, and uppercase-hex assertions.
- Updated canonical Techstream/DDB tooling docs, FINDINGS, OPEN_QUESTIONS,
  ROADMAP, lock metadata, verification ownership, and this journal.
- No `CORRECTIONS.md` entry is required: the superseded DDB and SeedValue
  statements were explicitly unresolved/bounded rather than false promoted
  findings.

### Verification

- `uv run python tests/verify_techstream_ptshim.py` -> pass (35/35)
- `uv run python tests/verify_techstream_ddb_residuals.py` -> pass (14/14)
- `uv run python tests/verify_techstream_rks.py` -> pass (54/54)
- `make verify-changed` -> pass (8 matched suites, 12 test files)
- `make verify` -> pass (449 assertions, 0 failures); the tracked ptshim
  synthetic-fixture verifier is now part of the core gate, while the DDB/RKS
  external-tree checks are additionally pinned by their focused runs above

### Remaining blockers

- A legitimate Techstream↔EPS capture remains dynamic-only; the log parser is
  now ready for it.
- The exact upstream producer of RKS's 16-byte SeedValue input is bounded and
  low priority.
- Type-1 `Toyota.ddb` is available but only worth deeper decoding for a future
  concrete master-enumeration/identity/routing question.
- Matching Sienna `.cuw` and `4514000` CodeFlash remain unavailable locally.

### Commit

- `ee0a460d3f1050853e3272dc0cffb7fcbfdeec79 analysis: close remaining high-value Techstream static leads`

## Stage 4 — complete the Renesas RV40F host-protocol static census

### Starting state

- HEAD: `ee0a460d3f1050853e3272dc0cffb7fcbfdeec79`
- Relevant prior finding IDs: `RFP-001`–`RFP-006`
- Relevant artifacts: pinned RFP V3.24.00 `macos-arm64` package,
  `libRFP.dylib`, `Devices.xml`, CLI documentation, existing six-command ICU
  table, and the package/resource lock
- Static boundary: this stage analyzes the retained **host library**. It does
  not promote generic RV40F support into a claim about the R7F701381/P1M-E
  mask ROM without target evidence.

### Questions

1. What is the complete `BootRV40F` ordinary command-ID surface, including
   methods that manually build frames instead of calling `ProcessCommand`?
2. What exact host connection/setup sequence reaches device type, inquiry,
   authentication, signature/area discovery, baud/frequency, and ICU checks?
3. Where does internal capability key `0x1106` come from, and what does the
   neighboring capability/size-key parser actually compute?
4. What is the exact structural layout and dispatch condition of legacy
   `SetICUM`?
5. What are the host-side preconditions, fallback, retries, and state handling
   around `CheckICUMode` and `ValidateICU_S`?
6. Does the **complete retained standard RV40F host surface** expose a dedicated
   arbitrary 16-byte ICU key load or a 64-byte SHE M1/M2/M3 request?

### Work performed

- Enumerated all 61 retained `BootRV40F` symbols from the pinned ARM64 Mach-O
  and cross-referenced every call from the RV40F task layer.
- Disassembled the entire library and separately modeled both command-construction
  styles: the common `ProcessCommand` helper and older/manual `SendRecvFrame`
  constructors/data phases.
- Recovered request/response shapes, calling tasks, capability/precondition
  gates, and result handling for every distinct ordinary command ID.
- Traced generic serial-mode family routing into `_ConnectRV40F`, both
  `Task_SetupBaudrate_RV40F` variants, clock/password setup, and the
  signature/area-discovery branches.
- Recovered the 8-byte capability vector source and fully decoded
  `UtilityRV40F::GetRV40FInfo` plus its phase-2 fallback.
- Traced every branch of `SetOptionByteEx`, the legacy `SetICUM` record, and
  the `CheckICUMode`/`ValidateICU_S` lifecycle sequence.
- Replaced the six-row ICU-only artifact with a complete command table and a
  separate capability-decoder table; added body locks for the newly critical
  connection/setup/parser functions.

### Findings

- The retained protocol contains **52 distinct ordinary command IDs** across
  the 61-symbol `BootRV40F` surface. The machine-readable census spans inquiry,
  memory read/write/verify/erase, checksum, protection/authentication, option
  data, frequency/baud, device/signature discovery, configuration, area/OCD,
  ICU, password, and CCC-config families — source: pinned Mach-O constructors
  and task callers, grade: **verified** (`RFP-002`).
- Normal requests use `01 || length_be16 || command || payload || checksum ||
  03`; responses begin `0x81`. `SendRecvFrame` bounds/validates the packet and
  `ProcessCommand` additionally enforces the exact expected response-payload
  size before copying output — grade: **verified** (`RFP-001`).
- `_ConnectRV40F` begins with `GetDeviceType (0x38)`. Its 24-byte response is
  split into an **8-byte TypeCode/capability vector** plus four BE32 frequency
  range fields. The capability vector is copied into `DeviceInfo+0x30` and is
  the exact input to `UtilityRV40F::GetRV40FInfo` — grade: **verified**.
- Internal key `0x1106` is true iff packed capability-word bits `48..50` are
  `1` or `4`; neighboring `0x110x` keys are explicit bit projections and
  `0x120x` keys are derived widths/sizes. `GetSignature (0x3A)` is a separate
  58/72-byte device/memory descriptor consulted **alongside** that preloaded
  capability vector, not its source — grade: **verified** (`RFP-007`).
- Generic serial entry is now bounded precisely before RV40F family routing:
  a configuration-selected `uint16` pattern is passed to the driver's named
  `RunModeEntry`, then entry selector 1/2 selects 9600 baud + 1 ms +
  `ZeroTransmission(true/false)`, selector 3 selects 10000 baud, selector 4 has
  no extra serial action, and selector 5 selects 250000 baud before
  `GetBootCode`. Concrete reset/boot-pin electrical behavior remains behind the
  driver/configuration. The classic RV40F setup then performs `GetDeviceType`,
  optional target+host baud change, `Inquiry`, `GetIDAuth`, bounded
  `CheckIDAuth` retry, signature discovery, and capability-dependent
  version/T-memory/ICU checks. The RV40F2 variant substitutes
  `GetAreaNum/GetAreaInfo` for signature memory discovery; clock setup
  separately performs password checks and `SetFrequency` when required —
  grade: **recovered/verified host sequence; target entry bounded** (`RFP-008`).
- `SetICUM` is only the legacy fallback when capability predicates `0x1002` and
  `0x1109` are both false. Its 20-byte source record has byte 0 unused by this
  routine, three threshold-normalized flag bytes, three raw u32 fields, and one
  raw u32 auxiliary field; `0x75` sends the auxiliary four bytes first and
  `0x74` sends the reordered 15-byte main record. No retained label supports a
  slot/key semantic — grade: **recovered structural semantics** (`RFP-003`).
- `CheckICUMode` sends `0x71 FF`; **only** result `0xE1000010` causes a fallback
  `0x71 00`. Successful first/fallback requests cache host mode `FF`/`00`.
  `ValidateICU_S` sends payload-free `0x70` once with no internal retry or key
  material; the high-level ICU-S option task calls it only when cached state
  says validation remains necessary — grade: **verified host sequence / target
  effect bounded** (`RFP-006`).
- Across the complete security/configuration subset there is **no dedicated
  fixed 64-byte request with SHE M1[16]/M2[32]/M3[16] shape and no ICU
  `slot || arbitrary_key[16]` primitive**. `CheckPassword` is 65 bytes
  (`selector+32+32`), `WriteConfig`/`VerifyConfig` are 20 (`BE32+16`), and
  legacy `SetICUM` is 4+15. Generic flash/config data phases can carry arbitrary
  bytes and are intentionally excluded from this dedicated-key negative —
  grade: **verified host-surface negative; target transfer bounded** (`RFP-004`).

### Negative/bounded results

- The four integer fields and three flags in the legacy `SetICUM` record have
  no retained human-readable enum names; they remain structural rather than
  guessed.
- `ValidateICU_S` host behavior does not reveal the target-side lifecycle
  transition, permanence, or mask-ROM checks.
- `Devices.xml` still has no P1M-E/R7F701381-specific route. A live target or
  legitimate capture is required to prove which of the 52 commands and
  capability bits apply to the Toyota/Denso MCU.
- Package triage remains negative for an RH850 provisioning agent: all 68
  `Firmwares/*.bin` files are SEGGER probe firmware; explicit target resources
  are DA/RA-only; the sole provisioning payload is RA6B1-only.

### Documentation/tests changed

- Replaced `data/renesas_rfp_rv40f_icu_commands.csv` with the complete
  `data/renesas_rfp_rv40f_commands.csv` and added
  `data/renesas_rfp_rv40f_capabilities.csv`.
- Rewrote the canonical RFP report around the complete protocol/state-machine
  boundary and strengthened `RFP-001`–`RFP-006`; added `RFP-007`/`RFP-008`.
- Updated `OPEN_QUESTIONS` so RFP generic static work is closed and only
  target/capture transfer remains; added this stage to completed-static roadmap.
- Expanded `renesas-rfp.lock.json` with critical setup/parser body locks and
  the completed 52-command/61-symbol analysis scope.
- Expanded `verify_renesas_rfp.py` to assert the exact command-ID set,
  capability projections, security/configuration negative, wire fixtures, and
  all newly pinned function bodies.
- No `CORRECTIONS.md` entry is required: prior RFP rows explicitly said
  “recovered so far”/bounded. The intermediate analysis assumption that the
  capability vector came from `GetSignature` was corrected before being
  promoted into repository evidence; the bytes prove it comes from
  `GetDeviceType`.

### Verification

- `make verify-rfp` -> pass (145/145 against the pinned local package)
- `make verify-changed` -> pass (3 matched suites, 7 test files)
- `make verify` -> pass (all core suites green; final doc-link suite 451/451)

### Remaining blockers

- A legitimate P1M-E serial-boot capture/bench query is required to establish
  the target's actual `GetDeviceType`/capability response and accepted command
  subset.
- The target-side effect and reversibility of `ValidateICU_S` cannot be learned
  from the host library alone.
- Any manufacturing-only ICU key-provisioning agent outside this standard RFP
  distribution remains a possible external artifact, not a static lead in the
  current package.

### Commit

- `64e2d46734154bfbadab91960480bf48eff853c8 analysis: complete Renesas RV40F host protocol census`


## Stage 5 — close the application COM receive/transmit long tail

### Starting state

- HEAD: `64e2d46734154bfbadab91960480bf48eff853c8`
- Relevant prior finding IDs: `COM-001`–`COM-003`
- Relevant artifacts: `data/application_rx_map.csv`,
  `data/application_rx_signal_evidence.csv`, `data/application_tx_map.csv`, the
  read-only Ghidra Rx exporter, six generated COM Tx packers, and the complete
  CanIf/PduR tables
- Static boundary: classify configured COM signal IDs and their stock firmware
  extraction/production paths. Absence of a configured COM extraction is not
  promoted into a claim that every corresponding wire bit is globally unused.

### Questions

1. Are the 97 Rx `configured-unresolved` rows missed ordinary bitfields,
   opaque/group paths, special/security-only configuration, indirect helpers,
   or configured-but-not-extracted IDs?
2. What produces Tx signal 9 (`0x260 B7`), signal 37 (`0x262 B7`), and signal
   57 (`0x4C8 B4..B7`) after the generated packers omit them?
3. Does the special acceptance rule for CAN `0x7F7` join the active class-5 Tx
   route on `0x7F8`, and if so how far can that channel be named statically?

### Work performed

- Enumerated every code reader of the 300-entry signal-to-PDU table at
  `0x224E4` and every direct xref to `application_com_receive_signal @ 0x7C03E`
  and `application_com_receive_signal_group_bytes @ 0x7D63E`.
- Extended the read-only Ghidra Rx exporter to emit one evidence/classification
  row for every configured Rx signal ID `58..299`, including negative rows
  anchored to the raw signal map and containing-PDU class.
- Regenerated both Rx evidence and final Rx map; updated the generator to reject
  any configured signal lacking an evidence/classification row.
- Traced the complete Tx path below COM packing through PduR, CanIf enqueue,
  controller pre-enqueue hooks, software queue, RSCFD writer, and confirmation.
- Recovered the controller-0 post-packer callback at `0x7FEAC`, its route flags,
  body hash, and final-byte checksum algorithm.
- Performed a complete transform/writer boundary for PDU 5 / CAN `0x4C8` and
  recovered signal 57 as initial/default-only zero in this calibration.
- Added a deterministic Tx-map generator that validates the six packer bodies,
  COM descriptor flags, CanIf route flags/pointers, checksum callback body, and
  PDU-5 initial bytes before emitting the 58-row map.
- Traced class-5 receive configuration (`0x7F7`) and special protocol receive
  callbacks into the same state/callback family whose Tx wrapper emits PduR
  class `0xF800`, resolving the sole active class-5 Tx record to `0x7F8`.

### Findings

- All **242/242 configured Rx signal IDs are now classified**. Positive
  extraction evidence remains 145 signals: 131 direct bitfields plus 14
  group/opaque byte signals. The former 97 residuals are deterministic
  no-COM-extraction rows: **93** are omitted by otherwise-active generated PDU
  handlers; **84/85/86** belong to no-COM-unpacker SecOC sync CAN `0x00F`; and
  **217** is the sole ordinary no-unpacker signal on CAN `0x2E8` — source:
  signal-map reader census + complete receive API callers + generated tables,
  grade: **verified positive / bounded-negative classification** (`COM-002`).
- The signal-map table has only four code readers. On Rx, only
  `application_com_receive_signal` and the group-byte helper resolve configured
  signal IDs. `receive_signal` has 133 direct call refs: 131 ordinary generated
  bitfield calls plus two table-driven calls inside the already-modeled crypto
  test collector. The group-byte helper has exactly 12 callers, all inside the
  two known opaque/test collectors. No third generic stock COM extraction path
  remains — grade: **verified structural negative**.
- Tx signals **9** and **37** are final-byte checksums, not dead configured
  fields. COM PDU route flags are `1,1,0,0,0,0`; PDU 0/1 pass through
  `0x800D2 -> 0x7FEAC` after packing and before queueing. `0x7FEAC` sums DLC,
  CAN-ID bytes, and payload bytes except the final byte, then writes the low
  byte of the sum to `payload[DLC-1]`. Pinned opendbc independently implements
  the same Toyota checksum — grade: **verified firmware-static; externally
  corroborated** (`COM-003`).
- Tx signal **57** is **default-only zero in this calibration**. Packer
  `0x4BC54` writes only signals 54..56; all six COM descriptors use flags
  `0x03` (no `0x10/0x20` COM transform); PDU-5's CanIf post-packer flag is zero;
  lower Tx layers only copy; and initial `0x4C8 B4..B7` are zero — grade:
  **verified bounded negative** (`COM-003`).
- The special class is a paired bidirectional channel: acceptance CAN `0x7F7`
  selects class-5 descriptor `0x21AC4` and upper callback `0x82042`, which
  reaches the special receive protocol path; the same protocol state family
  transmits through `0x8206C`, which explicitly creates class `0xF800`, and the
  sole active class-5 Tx record is CAN `0x7F8`. The service/protocol name is not
  retained and remains intentionally unnamed — grade: **recovered/verified
  routing join** (`COM-003`).

### Negative/bounded results

- The 97 negative Rx rows do not identify wire bit positions, scaling, or OEM
  semantics. They establish absence of a stock configured COM signal extraction
  for those IDs only.
- Signal 57's default-zero result is calibration-specific; another image could
  enable a producer or transform for the same generated field.
- The `0x7F7/0x7F8` channel is paired by generated routing/state flow, but no
  retained semantic name justifies labeling its upper protocol.

### Documentation/tests changed

- Extended `ExportApplicationRxSignalEvidence.java` and regenerated
  `data/application_rx_signal_evidence.csv` / `data/application_rx_map.csv`.
- Added `tools/generate_application_tx_map.py` and regenerated
  `data/application_tx_map.csv`; moved the Tx map from curated to generated
  artifact ownership.
- Expanded `verify_application_receive.py` to enforce the exact
  `131+14+93+3+1` classification partition and zero unresolved extraction rows.
- Expanded `verify_application_transmit.py` with raw route/pointer/body checks,
  checksum/default-only closure, class-5 `0x7F7/0x7F8` routing join, and
  byte-for-byte Tx generator determinism.
- Updated canonical Rx/Tx reports, FINDINGS, OPEN_QUESTIONS, ROADMAP, generated
  artifact ownership, Makefile generation targets, verification ownership, and
  this journal.
- No `CORRECTIONS.md` entry is required: the old Rx/Tx rows were explicitly
  `configured-unresolved`/bounded, not promoted false findings.

### Verification

- `uv run --locked python tests/verify_application_receive.py` -> pass (55/55)
- `uv run --locked python tests/verify_application_transmit.py` -> pass (58/58)
- `uv run --locked python tests/verify_control_partition.py` -> pass (98/98) after
  replacing its stale pre-Stage-5 unresolved-signal assertions with the proved
  checksum/default-only classifications
- `make verify-changed` -> pass for every affected application/CAN/docs/lifecycle suite
- `make verify` -> pass (all core suites green; final doc-link suite 451/451)
- `EXTERNAL_REPOS_DIR=/Users/kai/dev/inspect/repos uv run --locked python
  tests/verify_external_corroboration.py` -> pass (280/280), including the pinned
  opendbc Toyota checksum arithmetic

### Remaining blockers

- None for the Stage-5 COM extraction/production census.
- Downstream behavioral semantics of anonymous recovered RAM-backed signals are
  a separate semantic-coverage problem, not an unresolved COM mapping problem.
- The special `0x7F7/0x7F8` channel's OEM protocol/service name remains unknown
  and is not needed to close its routing relationship.

### Commit

- `a01bc5f9ae32dd574f6fbf296ef7d2c3a6cebf40 analysis: close application COM signal long tail`


## Stage 6 — tighten the motor-control and safety static boundary

### Starting state

- HEAD: `a01bc5f9ae32dd574f6fbf296ef7d2c3a6cebf40`
- Relevant prior finding IDs: `ARCH-007`–`ARCH-009`, `SWEEP-004`,
  `SWEEP-006`, `CORR-015`, `CORR-016`
- Relevant artifacts: `data/motor_actuation_path.csv`, the existing control
  partition report/Ghidra audit, retained P1M-E hardware manual, and the
  previously bounded `0x32B80` / `0xB98BC` calibration handlers
- Static boundary: exhaust plausible hidden transfer classes around the
  authenticated-command→d/q gap, resolve the phase-sample acquisition source,
  recover registration/output semantics for the alleged safety interlocks, and
  bound the remaining named motor-calibration handlers without inventing OEM
  semantics.

### Questions

1. Does a table-driven, pointer/struct-copy, computed-GP, RTE, scheduler, or
   function-pointer handoff join conditioned `0x2E4` command state to the
   `0x37712` d/q-reference cone?
2. What exactly are `0xFEEF81E0` and `0xFEEF8A20`, and what hardware source
   feeds them?
3. How are `0x43A78`, `0x43716`, and `0x438C6` actually registered and what do
   their outputs control?
4. When do `0x32B80` and `0xB98BC` execute, beyond the old generic
   "calibration-transition" label?

### Work performed

- Reconstructed the complete direct producer cone for `FEBE6D28/6D2A` and
  performed a whole-`FEBE6D00..6DFF` static xref/writer census.
- Searched CodeFlash bytewise for absolute pointers into the d/q state page,
  censused every direct caller of generic `memcpy @ 0x153A`, checked RTE copy
  direction, and reclassified `0x58404` d/q writes as startup/version-reset
  clearing rather than command transfer.
- Followed the previously missed command branch
  `BFA2 → C144 → C170 → C1B8/C1B4/C1BC` and the `AE16/AE6E` export path to
  their bounded snapshot/foreground consumers.
- Resolved the phase-sample addresses against the retained Renesas P1M-E
  hardware manual, then traced firmware DMA descriptors and sample-ring
  consumers back to ADCG0/ADCG1 and DMAC.
- Expanded the P1M-E device profile with only the manual-backed Global-RAM,
  ADCG0/1, and DMAC-channel-master windows needed by this proved path; added
  exact SFR/ring labels and rebuilt the project twice independently.
- Recovered all nine monitor setup records, callback tables, status indices,
  aggregate path, and final debounced event/status consumer around the three
  former SWEEP-006 candidates.
- Traced the CH0/CH2 cached-version dispatchers around `0x32B80` and `0xB98BC`,
  including transition and steady wrappers and their concrete version domains.
- Updated the reproducible Ghidra annotations and strengthened the project audit
  so future rebuilds preserve these boundaries.

### Findings

- **Phase acquisition is ADCG→DMAC→Global RAM, not SFR-window polling.** The
  P1M-E manual maps `0xFEEF8000..0xFEEFFFFF` as 32 KiB Global RAM A. Firmware
  descriptors `0x312B0/0x312C0` pair `ADCG0DIR00 @ 0xFFF91200` with ring
  `0xFEEF81E0`; `0x31378/0x31388` pair `ADCG1DIR00 @ 0xFFF92200` with ring
  `0xFEEF8A20`. `0x5F5E0/0x5F68A` consume 432-entry x32-bit rings and feed the
  CH0 sample snapshot. DMAC channel-master setup includes `DM00CM @ 0xFFFF8100`
  and `DM10CM @ 0xFFFF8120` — source: P1M-E manual + CodeFlash descriptors,
  grade: **verified** (`ARCH-008`, `CORR-028`).
- The authenticated-command branch is deeper than previously documented:
  `FEBEBFA2 → 0xCA6B8/FEBEC144 → 0xCA75E/FEBEC170`, then either
  `0xCB700 → FEBEAE16/FEBEAE6E` or `0xCAC14/0xCAC6A →
  FEBEC1B8/C1B4/C1BC`. None of those states writes the `FEBE6Dxx` motor block —
  grade: **recovered**.
- The **static command→d/q search is closed as a bounded negative**. The direct
  feeder cone is motor-internal; every recovered write in `FEBE6D00..6DFF` is
  motor-control or explicit init/reinit; RTE staging is read-only for the block;
  CodeFlash contains zero absolute 32-bit pointers into the block; generic
  `memcpy @ 0x153A` has only bootloader caller `0x4F84`; and no recovered
  computed-GP access in the producer cone reaches conditioned command state.
  This does not prove physical independence; dynamic bench observation remains
  the discriminator — grade: **bounded static negative** (`ARCH-008`).
- SWEEP-006 is corrected: `0x43A78`, `0x43716`, and `0x438C6` are not isolated
  interlocks. They are helpers inside a **nine-channel registered
  plausibility/deadline monitor family** using `com_signal_deadline_monitor_c @
  0x69DEC`, callback tables `0x28984..0x28B24`, and status vector
  `FEBE797C..7984`. Concrete edges include `0x43784→0x43716`,
  `0x43934→0x438C6`, and `0x43B16→0x43A78×2`. Aggregate `0x43F28` feeds
  event/status machinery and debounced monitor `0xB9D36`; no direct d/q/PWM
  write is recovered — grade: **recovered/verified registration, bounded
  downstream safety role** (`SWEEP-006`, `CORR-029`).
- `0x43716`/`0x438C6` return `0/0x5A`; the old statement that they followed
  `0x43A78`'s `0x11/0x22/0x33` lifecycle pattern was false. Their wrappers
  translate predicate results into the monitor-state vocabulary.
- `motor_coord_transform_calib_handler @ 0x32B80` is state `0x33` of the
  six-channel `0x33198` calibration state machine and is reached in CH0 through
  transition and steady dispatch for version domains `0x512`/`0x600`.
  `motor_rotor_observer_calib_handler @ 0xB98BC` is reached in CH2 through
  transition `0xBEB44` and steady `0xBEBF6` wrappers for current version
  `0x200..0x522` — grade: **recovered execution/version domains** (`CORR-030`).

### Negative/bounded results

- No static transfer from valid-command state to the d/q reference cone was
  recovered even after exhausting the named hidden-transfer classes. This is
  deliberately not promoted to "CAN command cannot actuate"; a runtime-only
  coupling remains logically possible.
- The nine-channel monitor family reaches fault/event bookkeeping in the
  recovered downstream trace, not direct motor output. This does not prove its
  state can never participate indirectly in a broader safety policy.
- ADCG `DIR00` source-register identity is exact; the external analog pins or
  physical current-sensor channel assignment are not claimed.
- The calibration handlers now have precise execution/version domains, but OEM
  calibration names and higher-level physical meanings remain unnamed.

### Documentation/tests changed

- Added `data/motor_safety_monitors.csv` and
  `tests/verify_motor_safety_monitors.py`.
- Added `data/motor_calibration_handlers.csv` and
  `tests/verify_motor_calibration_handlers.py`.
- Expanded `data/motor_actuation_path.csv` and
  `tests/verify_motor_actuation_boundary.py` for exact ADCG/DMAC acquisition,
  hidden command staging, pointer/memcpy negatives, and the bounded join.
- Expanded the P1M-E device profile, SFR labels, stats invariant, and project
  audit; regenerated two independent projects and updated normalized project
  inventory through the guarded two-rebuild path.
- Rewrote the canonical control-partition §9 and reconciled firmware
  architecture, application Rx, FINDINGS, OPEN_QUESTIONS, ROADMAP, generated
  artifact ownership, and `CORRECTIONS.md` (`CORR-028`–`CORR-030`).
- Rebuilt and promoted the annotated Ghidra snapshot through the verified
  `snapshot-project` lifecycle; no committed snapshot was daemon-opened.

### Verification

- `uv run --locked python tests/verify_motor_actuation_boundary.py` -> pass (58/58)
- `uv run --locked python tests/verify_motor_safety_monitors.py` -> pass (56/56)
- `uv run --locked python tests/verify_motor_calibration_handlers.py` -> pass (26/26)
- `uv run --locked python tests/verify_p1m_device_profile.py` -> pass (317/317)
- two independent full Ghidra rebuilds -> identical normalized inventories;
  both exact at 5,921 functions / 179,223 instructions / 37,818 symbols /
  1,376,576 mapped bytes / 14 memory blocks
- `make verify-processor` -> pass; Stage-6 motor audit reports 16 call edges,
  20 exact reference censuses, 0 failures
- `make verify-project-parity` -> pass before snapshot promotion
- `make verify-changed` -> pass (10 matched suites, including all new Stage-6 motor/profile suites)
- `make verify-ghidra` -> pass (core + SLEIGH + processor audits + exact project parity; final doc-link suite 455/455)

### Remaining blockers

- None for the named Stage-6 static questions.
- Proving how a valid authenticated steering command affects physical actuation
  now requires dynamic correlation on an isolated provisioned bench; repeating
  the same broad static join search without a new lead is low value.
- External ADC pin/current-sensor assignment and OEM names for the monitor and
  calibration channels remain outside the recovered static evidence.

### Commit

- Pending Stage 6 commit; immutable SHA will be recorded after final verification.
