# Corrections

Superseded conclusions and why. Each entry names the wrong claim, the correct
one, and the canonical report that now owns the truth. These are retained so
the mistakes are not re-made.

## Evidence-grade: disproved

### CORR-001 — Flat firmware import

- **Wrong:** `RH850_P1M-E_Firmware.bin` is one flat block at VA `0x0`.
- **Right:** It is two regions — DataFlash (file `0x0–0x7FFF` →
  `0xFF200000`) followed by CodeFlash (file `0x8000–0x107FFF` → `0x0`).
  CodeFlash VA = file offset − `0x8000`.
- **Consequence of the error:** all CodeFlash addresses shifted `+0x8000`;
  only ~2,000 functions found; the false conclusion that the two bootloader
  secrets were unreferenced and lived in a separate image.
- **Canonical:** root `README.md` §"File layout";
  [../storage/dataflash.md](../storage/dataflash.md). The invalid analysis is
  preserved in `legacy/flat-import/` (do not use).

### CORR-002 — SecOC runtime-key command path

- **Wrong:** `0x65CD8 → 0x66E48 → 0x67590 → 0x72F58` is a SecOC runtime-key
  lifecycle (CSM key-set / MAC generation / ICU derivation).
- **Right:** `0x72F58`/`0x72F84` are AUTOSAR NvM `ReadBlock`/`WriteBlock`;
  `0x67590/0x67608/0x67C34` generically restore, persist, and reconcile
  raw/XOR55/XORAA objects; `0x758A0/0x785D2` are NvM/DataFlash service
  machinery. Not a key lifecycle at all.
- **Canonical:** [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md);
  `tests/verify_secoc_nvm.py`.

### CORR-003 — Application GP work-buffer root

- **Wrong:** application-GP work-buffer root `0xFEBFEB08`.
- **Right:** `0xFEBF0B08`.
- **Canonical:** [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

### CORR-004 — System-transition phase snapshot address

- **Wrong:** `GP+0x301F` evaluated using the boot GP.
- **Right:** `0xFEBEE81F` (application GP), snapshot of the non-Dcm
  system-transition phase at `0xFEBEB1A4`; phase `0x11` blocks programming
  handoff.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md).

### CORR-005 — Pages 468–479 as ICU key-slot pages / raw keys

- **Wrong:** pages 468–479 are 12 ICU key-slot pages holding raw AES keys or
  ICU derivation metadata.
- **Right:** pages 432–479 are the full 16-object SecOC raw/XOR55/XORAA
  triplicate bank; pages 468–479 decode to four structured state objects.
- **Canonical:** [../storage/dataflash.md](../storage/dataflash.md);
  [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

### CORR-006 — Dealer/FEBEF object-0 key-set capture design

- **Wrong:** hooking `0x72F58` alone captures a dealer key-set of object 0.
- **Right:** `0x72F58` is generic NvM `ReadBlock`. A capture must filter blocks
  41/45/49 and observe asynchronous completion on a provisioned variant; the
  call itself is not key-set.
- **Canonical:** [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

### CORR-007 — Large-function motor-control classifications

- **Wrong:** seven of the eight large functions in the motor cluster were
  annotated as motor-control state machines.
- **Right:** structural re-classification (several are RAM-init / glue); see
  the per-domain distribution. Commit `22279b5`.
- **Canonical:** [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) §9
  and the per-domain files.

### CORR-008 — Bootloader DID `F181` returns VIN / part number / `8965B4512000`

- **Wrong:** bootloader `F181` exposes VIN, part number, `BOOT INFO AREA`, or
  `8965B4512000`.
- **Right:** bootloader `F181` synthesizes `02 ‖ 32*0x21` — a placeholder. The
  real software ID comes from the *application* `F181` callback.
- **Canonical:** [../diagnostics/bootloader-dids.md](../diagnostics/bootloader-dids.md).

### CORR-009 — Slot-4 `FF*16` KAT proves an erased/default live key

- **Wrong:** the embedded `B290FA2E…E540` vector is an active slot-4
  known-answer test and, together with invalid objects 12–15, strongly
  indicates an erased/default live SecOC key.
- **Right:** both functions that reference the vector gate their crypto bodies
  on fixed `CodeFlash[0x30EF3] == 0x5A`. This calibration stores `0x00`, so
  both branch directly to report-only tails and never submit command 7. The
  `FF*16` vector is latent dead data and places no constraint on protected
  slot 4.
- **Physical check:** no production application path has been identified that
  reloads slot 4 on every boot. An unconditional `FF*16` KAT would therefore
  be incompatible with a personalized nonvolatile slot; compiling it out is
  consistent with either personalized or unprovisioned hardware state.
- **Canonical:** [../security/secoc/application-chain.md](../security/secoc/application-chain.md)
  §"Compiled-out slot-4 known-answer check"; `tests/verify_secoc_application.py`.

### CORR-010 — No SHE key-update path exists in the application

- **Wrong:** the production image contains no SHE M1–M5 parser, no ICU-S
  key-update command, and no application diagnostic route capable of
  provisioning a protected key slot.
- **Right:** enabled WDBI DID `0x1010` reaches literal `ICUSCMD=8`. The driver
  requires exactly 64 input bytes, stages them as `16+32+16`, and returns
  `32+16` bytes—the exact AUTOSAR SHE M1/M2/M3 → M4/M5 authenticated
  memory-update envelope. The DID's per-DID policy is extended session `0x03`
  with no Dcm SecurityAccess level; ICU-S package authentication and replay
  counter enforcement remain the security boundary.
- **Boundary:** the earlier rejection of `0x65CD8 → 0x72F58` as a key-set path
  remains correct; that chain is generic NvM. Command 8 is a separate driver
  and diagnostic subsystem. The package carries its target slot, so static
  firmware does not prove that Toyota dealer tooling uses DID `0x1010` or that
  a particular request targets slot 4.
- **Canonical:**
  [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md)
  §"Injection and refresh"; `tests/verify_icus_key_update.py`.

### CORR-011 — DID `0x1010` is one asynchronous WDBI exchange

- **Wrong:** one ordinary `2E 1010 || M1 || M2 || M3` request remains pending
  and eventually returns M4/M5 through the same transaction.
- **Right:** this application places an OEM selector before the DID. Selector
  `0x01` starts the operation with 64 package bytes and initially returns status
  `0x01`; selector `0x03` is a separate status/result read. Status `0x02`
  includes M4/M5, status `0xFF` reports failure, and reading either terminal
  state clears the diagnostic banks.
- **Wire forms:** `2E 01 10 10 || M1 || M2 || M3` and
  `2E 03 10 10`, with positive responses beginning `6E 01 10 10` and
  `6E 03 10 10`.
- **Canonical:**
  [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md)
  §"Exact diagnostic transport contract";
  `tests/verify_icus_key_update.py`, `tests/verify_icus_trace_decoder.py`.

### CORR-012 — Short classic-CAN SecOC frame bypass

- **Wrong:** because the SecOC worker checks only that the received length covers
  the trailer, a short `0x2E4`/`0x131`/`0x132` frame can reach CMAC verification
  and preserve stale authentic-payload bytes in COM.
- **Right:** the earlier CanIf callback at `0x7FF52` enforces configured minimum
  DLC and physical maximum DLC. All classic secured routes configure 8 and the
  classic maximum is 8, so they require exact DLC 8. FD routes configure 32,
  accept physical DLC 48/64, and are then clamped to 32; the suffix is ignored
  rather than delivered as stale authenticated payload.
- **Canonical:** [../security/secoc/application-chain.md](../security/secoc/application-chain.md)
  §"DLC canonicalization"; `tests/verify_secoc_security_properties.py`.

### CORR-013 — `0x6922C` as command-13 key-export completion

- **Wrong:** the historical Ghidra label `icus_command13_test_completion`
  identified `0x6922C` as completion of an ICU-S command-13/RAM-key-export
  path and therefore as a possible persistent-slot export lead.
- **Right:** `0x6922C` belongs to the neighboring command-1/3 AES test record.
  The low-level wrapper at `0x8954C` constrains its operation flag to literal
  command 1 or 3 and its selector to `0..14`. The complete nine-site
  `ICUSCMD` census contains no **stock application** command-13 invocation.
  That corrects the function label only: without the restricted Renesas ICU-S
  manual or a bench test, it does not establish direct command-13 semantics or
  disprove a slot-4-to-`RAM_KEY` copy/alias followed by export.
- **Canonical:**
  [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md)
  §"Complete application command-writer census";
  `tests/verify_icus_key_recovery_surface.py`.

### CORR-014 — SID `0xAB` as RID-based calibration/flash control

- **Wrong:** proprietary SID `0xAB` consumes the 13 RID callback pairs at
  `0x25768`; subfunction `02` resets its control block; the service may be
  calibration/flash control with unresolved indirect security paths.
- **Right:** `0xAB` is a structurally recovered event-record service. Its three
  selectors list active event IDs and query per-ID state/detail through the
  64-slot catalogue at `0x2AD10`. Selector `02` supplies one event ID; it does
  not invoke the reset helper. The configured indirect closure is 75 snapshot
  descriptors plus six detail descriptors, with no flash, NvM, crypto, ICU-S,
  SecOC, or security-policy target.
- **Separation:** the RID lookup at `0x8D3CC` has one direct caller at
  `0x8A50C`, in a separate routine worker. It has no function-pointer literal
  and no edge from `0xAB`. SID `0x31`, which would ordinarily host
  RoutineControl, has a null callback and is excluded from the application's
  subfunction path. The worker wrappers are instead structurally configured in
  generic SID `0x28` control ranges `0x0201..0x02FF` and
  `0x2001..0x20FF`; those ranges remain stock-wire gated because SID `0x28`
  admits only subfunctions `00/01/03`.
- **State-mediated boundary:** the RID callbacks have no direct sensitive
  target, but several result callbacks arm asynchronous namespace-`0x100` NvM
  persistence. RID `2001` submits object `0x101`, RID `2002` submits `0x102`,
  and RIDs `2005/2006/2007/2008/2009/200D` submit `0x103`, all through
  `0xFF09C → secoc_nvm_object_update @ 0x65CD8`. These are SecOC-associated
  state objects, not object 15 or a key/crypto operation.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md)
  §"Proprietary `AB` event-record service";
  `tests/verify_application_ab_service.py`,
  `tests/verify_application_routine_id_callbacks.py`.

### CORR-015 — Crypto-test cyclics misidentified as motor control

- **Wrong:** the foreground callees at `0x68C0C` and `0x68DE6` formed a
  motor-control state machine and continuation, while `0x57AC2` was only
  configuration/parameter management.
- **Right:** descendant decompilation identifies the `0x68C0C` and `0x68DE6`
  state cluster as the three dormant CAN-controlled crypto-test banks;
  `0x68BC2` and `0x68D0E` are the recovered bank-1 command-5 state/finalization
  paths. The actual foreground route into the steering-command conditioner is
  `0x57AC2 -> 0xFDD40 -> 0xBEC4C -> 0xBA43A -> 0xCBA72 -> 0xCB86E ->
  0xC853A/0xC85B6`.
- **Impact:** removes unsupported motor semantics from the dormant crypto-test
  harness and establishes the first firmware-backed protected `0x2E4`
  torque-command handoff without claiming a downstream current/PWM mapping.
- **Canonical:** [../architecture/control-partition.md](../architecture/control-partition.md);
  `tests/verify_control_partition.py`.

### CORR-016 — `0x47C3C` as calibration-transition-only conditioning

- **Wrong:** `0x47C3C` was a `motor_phase_conditioning_calib_handler` reached
  only when an E2E-protected calibration version changed, so it could not be a
  runtime actuator function.
- **Right:** the complete caller graph has both transition dispatcher
  `0x5CC08` and steady dispatcher `0x5CE0C` beneath TAUJ0 CH0. `0x47C3C`
  offset/gain-conditions two U/V/W phase-current sample sets every steady
  high-rate cycle, with saturation and missing-phase reconstruction. Its output
  reaches rotating-frame feedback, d/q current PI-like loops, inverse
  transforms, phase-duty staging, and TSG30/31 HT-PWM compare writes.
- **Boundary:** this correction proves a physical current-control/PWM chain but
  does not fill the separate data-flow gap from authenticated CAN `0x2E4`
  command state into the d/q current references.
- **Canonical:** [../architecture/control-partition.md](../architecture/control-partition.md)
  §"Independent phase-current control to physical PWM boundary";
  `tests/verify_motor_actuation_boundary.py`,
  `ghidra/scripts/verify/AssertMotorActuationBoundary.java`.

### CORR-017 — SHE "verify-only" slot-4 generation restriction

- **Wrong:** the key-recovery assessment stated that "in a SHE-like policy, a
  SecOC MAC key may permit MAC verification while generation is disabled," and
  treated command-5 generation on slot 4 as likely-denied (with command-1/3 raw
  AES as the fallback oracle).
- **Right:** the AUTOSAR SHE specification governs per-key usage by a single
  binary `KEY_USAGE` flag (§4.4.1.5 "Key usage determination", §4.4.2.4
  `KEY_<n>`): a key is either an encryption/decryption key or a MAC
  generation/verification key. There is no separate verify-only permission; the
  five provisionable flags (§4.9 `FID`) are
  `WRITE_PROTECTION | BOOT_PROTECTION | DEBUGGER_PROTECTION | KEY_USAGE |
  WILDCARD`, and a disallowed operation returns `ERC_KEY_INVALID` (§4.8.4).
  Slot 4 is MAC-usage (command-7 verify), so under SHE it permits command-5
  generation; command 1/3 (raw enc/dec) is the operation a MAC-usage slot would
  reject. The polarity of the earlier AES-oracle fallback was therefore
  reversed — command 5 is the spec-aligned oracle, not command 1.
- **Boundary:** this is the AUTOSAR SHE architectural reference (external
  source). The Renesas ICU-S is a vendor core and the restricted `ICUSE` manual
  is unobtained (SECOC-018), so ICU-S could in principle deviate. The default
  expectation is now "command 5 is permitted on slot 4"; denial would require a
  non-standard Renesas restriction, not standard SHE policy.
- **Canonical:**
  [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md)
  §1.3; `tests/verify_secoc_application.py`;
  `build/reference-text/AUTOSAR_TR_SecureHardwareExtensions.txt` §4.4.1.5/§4.4.2.4.

### CORR-018 — Techstream online portal as an "immobilizer/MAC" path

- **Wrong:** `docs/tooling/techstream.md` §5.1 and §8.3 stated the online
  portal (`ReprogrammingSecurity` / `MACKey_Login`) is "only invoked for
  immobilizer resets and MAC key management, not for routine ECU reflashing."
- **Right:** The portal is the RKS (Reprogramming Key System) reprogramming-key
  authorization — `CUWAccessRKS.dll` / `CUWAccessRKSWrapper.dll` (.NET) drive
  an embedded IE to the TIS portal to obtain a VIN+license-bound `Signature`,
  validated only by regex `^[0-9a-zA-Z]+$` (no client-side crypto; signing is
  server-side). There is no immobilizer code path in this installer (zero
  "immobilizer"/"theft" strings across the 6,826-file tree). The portal does
  not supply the ECU crypto key — Layer B's key remains in the calibration
  file.
- **Consequence of the error:** conflated the portal with immobilizer/SecOC
  provisioning, overstating its relationship to the firmware SecOC findings.
- **Canonical:**
  [../tooling/techstream.md](../tooling/techstream.md) §5.3; TMS-009;
  `tests/verify_techstream_rks.py`.

### CORR-019 — RKS offline mode and VIN usage imprecisely characterized

- **Wrong:** `docs/tooling/techstream.md` §5.3 (commit `00fb27a`) described the
  offline path as "`OfflineImportReproKey` imports a `Signature` obtained earlier
  on a connected machine (`.xml`)" and the VIN binding as just "mandatory, read
  from the vehicle."
- **Right:** The RKS authorization has **three modes** (from the English UI
  source strings in `locale/en/LC_MESSAGES/default.mo`): online (IE→TIS portal,
  downloads `Signature`), offline (a "Signature file" produced by a defined
  retrieve sequence on a separate internet-connected computer, then read/imported
  on the offline PC via `OfflineImportReproKey` + `CheckReproKeyFormat`), and a
  paperwork fallback ("process implementation report") when no internet-connected
  computer is possible. The ReproKey is a **Signature file**, not necessarily
  `.xml`. VIN is the **identity spine** with six uses: mandatory gate; read from
  vehicle (`CSilVinReader`); 17-char + check-digit validation; cross-ECU
  consistency check (`ErrorVINMismatch`); written to the reflashed ECU
  (`RequestWriteVINForRKS`); and sent to the portal in the `<ReproKeyRequest>`
  XML. Also: `Cuw.exe` is CodeGear C++Builder 2007, not Borland Delphi.
- **Consequence of the error:** understated the offline mechanism (a three-mode
  authorization, not a single import) and the VIN's role (it gates, validates,
  consistency-checks across ECUs, is written to the ECU, and is bound into the
  portal request — not merely "read").
- **Canonical:**
  [../tooling/techstream.md](../tooling/techstream.md) §5.3; TMS-009.

### CORR-020 — `SendNonceAndSeedKey` misread as a SecurityAccess transmission

- **Wrong:** `docs/tooling/techstream.md` §4.6 / FINDINGS TMS-010 (commit
  `a2412ae`) characterized `CCanCommonFlashWriter::SendNonceAndSeedKey` as the
  "EPS/VFOREST SA transmission" building a "two-frame `0x37`/`0x38` exchange,"
  and flagged a `0x27`-vs-`0x37` reconciliation with SEC-BOOT-003 as open.
- **Right:** A clean decompile (typed `PASSTHRU_MSG`) shows
  `SendNonce`/`SendSeedKey`/`SendNonceAndSeedKey` are the VFOREST **flash
  key-material transfer**, not SA: six sequenced frames (`0x37`→`0x3c`) where
  the byte is a per-frame block sequence at `Data[4]`, not a UDS SID
  (`0x39`–`0x3c` are not UDS services at all). Each frame is
  `[4-byte nonce][1-byte block-seq][6-byte key chunk]` shipped via J2534
  `WriteMsgs`+`Sleep`+`ReceiveAck`; two 16-byte keys (from
  `CalibrationFile::GetSeedKey`, verbatim) feed the firmware payload gate
  (SEC-BOOT-005/006/007), not the SA. There is **no `0x27`-vs-`0x37`
  conflict**; the reconciliation is resolved.
- **What stands:** the "no AES S-box in any CUW DLL/EXE; AES only in the
  diagnostic-app DLLs (TMS-008) + `Cuw.exe` Windows CryptoAPI (§4.5)"
  sub-claim is unchanged and correct.
- **Canonical:**
  [../tooling/techstream.md](../tooling/techstream.md) §4.6; TMS-010.

### CORR-021 — VFOREST writer assumed to reflash the Sienna EPS

- **Wrong:** TMS-010 / §4.6 (commits `a2412ae`/`1b3a42a`/`a261e7e`) framed the
  CUW `TCUWCanSecurityVFORESTFlashWriter` `SendNonceAndSeedKey` path as
  delivering "payload-gate key material (SEC-BOOT-005/006/007)" to the Sienna
  EPS — implicitly assuming VFOREST = the Sienna's reflash writer.
- **Right:** Firmware verification shows the Sienna `8965B4512000` bootloader
  speaks **standard UDS only**. The service table at `0x8E54` (walked by
  `uds_service_dispatch @ 0x5222`) implements
  `0x10/0x11/0x22/0x27/0x28/0x2E/0x31/0x34/0x36/0x37/0x3E/0x85`; eight more SIDs
  (`0x14/0x19/0x23/0x2C/0x2F/0xAB/0xBA/0xBB`) map to
  `uds_unsupported_service_handler @ 0x69B0`; every other SID returns NRC `0x11`.
  There is **no proprietary/VFOREST SID handler**, and the payload-gate key
  storage (`DID 0x201` @ `0xFEBF2D08`, `DID 0x202` @ `0xFEBF2CF8`) is written
  **only** by `bootloader_did_direct_ram_copy @ 0x6D3A` (the `0x2E` path — sole
  writer, x-ref confirmed). The VFOREST `0x37`–`0x3c` proprietary frames would
  be rejected (NRC 0x11). The VFOREST writer therefore targets a **different**
  RH850 ECU; the Sienna is reflashed via standard UDS (`0x2E` DID zeros +
  `0x34/0x36/0x37` + `0x31`).
- **What stands:** the CUW-side mechanism (key-material transfer, not SA;
  `0x37`–`0x3c` are block-seq bytes at `Data[4]`; `arg3=GetNonce`,
  `arg4=GetSeedKey`; no AES in any CUW DLL/EXE) is unchanged and correct — only
  its attribution to the Sienna is corrected.
- **Canonical:**
  [../tooling/techstream.md](../tooling/techstream.md) §4.6; TMS-010.

### CORR-022 — Techstream version and build date

- **Wrong:** Techstream version "V18.00.008" with build date "2015-09-14".
- **Right:** Internal module version is **V18.00.003** (VerApp.ini dated
  2022/11/22, VerCmd.ini dated 2022/12/08). The "008" in the installer
  filename is the Flexera IS wrapper build number, not the application
  version. The "2015-09-14" was the Flexera IS toolchain version, not the
  software build date. DDB files are dated 2022-12-07/08. VehicleData.ini
  was last modified 2022/10/07. Model-year coverage extends to 2022 — the
  database predates both the 2023 Sienna and the 2025 Corolla.
- **Consequence of the error:** the "newer generation" framing of P4DK4
  was built on the false premise that the database might temporally
  bracket the Corolla. It does not — both vehicles postdate it.
- **Canonical:**
  [../tooling/techstream.md](../tooling/techstream.md) §1;
  `techstream.lock.json` `version_provenance`.

### CORR-023 — Techstream DDB pipeline coverage and U_English ownership

- **Wrong:** the generated Sienna catalog was treated as a broad EPS corpus,
  and 122 keyword hits in `U_English.ddb` were labeled "utility procedures."
- **Right:** the calibration catalog loaded only two NA EPS databases while the
  pinned distribution contains 35 regional `EPS*`/`EMPS*` files representing
  25 full-section semantic variants. The old parser stopped at directory slot
  16 and dropped 10,659 of 25,361 type-2 sections. The utility extractor used raw substring
  search (`eps` matched `steps`), broad unscoped terms such as "initial
  setting," and a 20-hit limit per term. `U_English` has 25,957 aligned
  resource identifiers that group UI text, but no encoded ECU ownership or
  firmware routine linkage, so those hits were not recovered procedures.
- **Fix:** the pipeline now emits a complete deterministic steering corpus
  (129 unique DTC IDs and 1,257 freeze-data monitor records), uses exhaustive
  explicit steering anchors for family-only `utility_string` vocabulary,
  removes duplicate exact/family monitor mappings, and fails closed on
  malformed LZSS, wrong file types, bad format-6 magic, and malformed section layouts.
- **Later refinement:** CORR-031 corrects section 3 from DIDs to
  `CDbSupPidTable`; the regional corpus has one actual type-7 DID row.
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §6.2;
  TMS-013; `tests/verify_diagnostic_vocabulary.py`.

### CORR-024 — MACKey `$36` interpreted as a diagnostic identifier

- **Wrong:** `$36` in a previously quoted login URL was treated as DID
  `0x0036`, and the untracked query-parameter name `ecuMacId` was promoted to a
  pinned-artifact fact.
- **Right:** managed
  `MAC_01_020_bgDoWork_UserType2_3` calls
  `GetMacKeyResId_FromRev`, converts the returned pointer to a string, and
  immediately executes `login_url.Replace("$36", returned_id)`. `$36` is a
  URL-template token for the server request ID, not a DID. The exact parameter
  name and former literal endpoint are absent from the currently pinned tree,
  so they remain unverified rather than being repeated.
- **Consequence:** MACKey Registration is still a real online ECU exchange-key
  workflow, but the old `ecuMacId`/DID rationale was false. Its relationship to
  SecOC remains open until the native `CMAC_01_*` write path is recovered.
- **Canonical:**
  [../security/mackey-registration.md](../security/mackey-registration.md);
  TMS-011; `tests/verify_techstream_mackey.py`.

### CORR-025 — Application DID and service record fields misnamed

- **Wrong:** `tools/diagnostics/firmware_tables.py` treated the second DID
  halfword as read/write access flags and service-record byte 9 as the session
  count. It also resolved session bytes by rereading the global Sienna image,
  even when the caller supplied different firmware bytes.
- **Right:** callback response widths identify the DID halfword as length/size
  metadata (`F181/F186/F18C = 0x11/0x01/0x14`); service byte 11 contains the
  session count, while byte 9 is a separate subfunction-routing attribute.
  Session lists now resolve from the supplied image.
- **Consequence:** generated vocabulary no longer emits the false
  `firmware_flags` field, and alternate-image analysis cannot silently mix in
  Sienna session policy.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md);
  DIAG-APP-007; `tests/verify_diagnostic_vocabulary.py`.

### CORR-026 — Firmware DTC-table correlation range truncated

- **Wrong (2026-08-01, same-day pipeline pass):** Scan only
  `0x30A28..0x30C40` and grade seven of 54 Techstream DTC rows exact.
- **Right:** each record is `[u8 flags][u16 DTC][u8 zero][u32 enabled]` at base
  `0x309DC`. `FUN_0005159e` reads the enabled dwords from `0x309E0 + i*8`, and
  `FUN_000517b4` reads identifiers from `0x309DC + i*8`; the table ends at
  `0x30EDC`. The old scanner was both partial and rotated four bytes early.
- **Evidence:** both decompilations show the paired bases, stride 8, bound
  `0xA0`, and `enabled == 1`; raw-byte verification confirms 160 aligned
  records, 127 enabled entries, and zero pad bytes. Regenerated correlation now
  finds 12 exact Techstream DTC rows, including `U0100`, `U0126`, `U023A`,
  `U0293`, and `U1103`.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md);
  DIAG-APP-008; `tests/verify_diagnostic_vocabulary.py`.

### CORR-027 — Format-6 magic treated the English language tag as fixed

- **Wrong (2026-08-01, same-day parser hardening):** Require the full English
  header `39 00 0C 16 0B 15 0F 16` for every format-6 string database.
- **Right:** the common prefix is seven bytes (`39 00 0C 16 0B 15 0F`); byte 7
  is a language tag from `0x16` through `0x1A` in the pinned corpus.
- **Evidence:** all 13 regional/language `U_*.ddb` files decode to 25,957
  strings plus 25,957 aligned metadata records. The deterministic suite now
  parses all 13 and asserts the complete observed language-tag set.
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §6.2;
  TMS-013; `tests/verify_diagnostic_vocabulary.py`.

### CORR-028 — Phase-sample rings misclassified as peripheral/SFR windows

- **Wrong:** `0xFEEF81E0` and `0xFEEF8A20` were treated as indexed peripheral
  result/SFR windows whose exact P1M-E module identity remained unknown.
- **Right:** the P1M-E hardware manual maps `0xFEEF8000..0xFEEFFFFF` as 32 KiB
  **Global RAM Bank A**. Firmware DMA descriptors at `0x312B0/0x312C0` pair
  `ADCG0DIR00 @ 0xFFF91200` with destination `0xFEEF81E0`; descriptors at
  `0x31378/0x31388` pair `ADCG1DIR00 @ 0xFFF92200` with `0xFEEF8A20`.
  `0x5F5E0/0x5F68A` consume those 432-entry x32-bit rings. The adjacent DMAC
  setup uses channel-master registers including `DM00CM @ 0xFFFF8100` and
  `DM10CM @ 0xFFFF8120`.
- **Impact:** closes the acquisition peripheral/source question and corrects the
  address-space model. The exact external ADC pins represented by DIR00 remain
  outside the static evidence.
- **Canonical:** [../architecture/control-partition.md](../architecture/control-partition.md)
  §9.1; `tests/verify_motor_actuation_boundary.py`;
  `ghidra/scripts/verify/AssertMotorActuationBoundary.java`.

### CORR-029 — Three "isolated safety interlocks" are registered monitor callbacks

- **Wrong:** `0x43A78`, `0x43716`, and `0x438C6` were fully isolated
  no-caller/no-callee safety interlocks, probably reached by an unrecovered RTE
  function-pointer table; `0x43716/0x438C6` were described as following the
  `0x11/0x22/0x33` return pattern of `0x43A78`.
- **Right:** concrete CodeFlash callback tables are recovered. `0x43784` from
  table `0x289EC` calls `0x43716`; `0x43934` from `0x28A20` calls `0x438C6`;
  `0x43B16` from `0x28A54` calls `0x43A78` twice. They are three members of a
  **nine-channel** family using `com_signal_deadline_monitor_c @ 0x69DEC` and
  publishing `FEBE797C..7984`. `0x43716/0x438C6` return `0/0x5A`; their
  wrappers translate into the monitor lifecycle vocabulary. Aggregate
  `0x43F28` reaches event/status bookkeeping and debounced monitor `0xB9D36`;
  no direct d/q or PWM write is recovered.
- **Impact:** replaces an inferred safety-actuation role with the proved
  plausibility/deadline/fault-monitor architecture. This does not claim the
  monitor states can never participate indirectly in safety policy.
- **Canonical:** [../architecture/control-partition.md](../architecture/control-partition.md)
  §9.5; `data/motor_safety_monitors.csv`;
  `tests/verify_motor_safety_monitors.py`.

### CORR-030 — Remaining motor calibration handlers were called transition-only

- **Wrong:** `0x32B80` and `0xB98BC` remained generic
  calibration-transition-only handlers with unresolved runtime context.
- **Right:** `0x32B80` is state `0x33` of the `0x33198` six-channel calibration
  state machine and is reached through both CH0 transition (`0x5CC08`) and
  steady (`0x5CE0C`) dispatch for version domains `0x512`/`0x600`.
  `0xB98BC` is reached in TAUJ0 CH2 for current versions `0x200..0x522` through
  transition wrapper `0xBEB44` and steady wrapper `0xBEBF6`, under outer cached
  version/complement dispatcher `0x579B4`.
- **Impact:** the two handlers now have concrete state/version/execution-domain
  bounds. Their OEM calibration names and any relation to the missing
  authenticated-command→d/q join are not invented.
- **Canonical:** [../architecture/control-partition.md](../architecture/control-partition.md)
  §9.6; `data/motor_calibration_handlers.csv`;
  `tests/verify_motor_calibration_handlers.py`.

### CORR-031 — Techstream supported-PID rows were mislabeled as DIDs

- **Wrong:** type-2 DDB section 3 was described and generated as a DID table;
  its bytes at offsets 4–5 produced 11 selected-catalog “DIDs,” an alleged
  exact `0x0100` firmware join, 16 regional unique DIDs, and P4DK4
  “subfunctions” from section 6.
- **Right:** the pinned `KgpDataCtrl.dll` format-2 factory at `0x1001ECCB`
  constructs `CDbSupPidTable` for section 3, `CDbPidTable` for section 6,
  `CDbDidTable` for section 7, and `CDbFreezeTable` for section 10. The two
  selected P4 EPS files have no section 7, so the direct DDB→firmware DID
  correlation count is zero. Across all 35 steering files there is exactly one
  real section-7 row (EU `EPS_PSA`); the former 146 “DID” rows are supported-PID
  records with 16 unique raw keys. Section-10 names remain useful freeze-data
  monitor vocabulary because its record API exposes `GetDataMonitorName`, but
  the seq-derived firmware DID bridge is structural/semantic—not a DID-table
  identity join. P4DK4 section 6 contains 85 PID records, not subfunctions.
- **Additional closure:** the companion format-1 factory classifies the
  high-value `Toyota.ddb` master tables, and `parse_master_db()` structurally
  covers all three regional directories (67 NA, 67 EU, and 76 JP sections).
  Compressed EU payloads remain explicitly undecoded. Exact `8965B4512000` is
  absent.
- **Canonical:** [../tooling/techstream-ddb-pipeline.md](../tooling/techstream-ddb-pipeline.md);
  TMS-013; `tests/verify_diagnostic_vocabulary.py`;
  `tests/verify_techstream_ddb_residuals.py`.

### CORR-032 — ELM Toyota-B routing was described as active 0↔2 software forwarding

- **Wrong (2026-08-10, initial SECOC-033 routing pass):** describe the successful
  physical repin primarily as moving EPS onto a "relay-backed" bus-0/2 path and
  leave the impression that ELM diagnostics depend on Panda's generic 0↔2
  software forwarder.
- **Right:** `SAFETY_ELM327` explicitly calls `set_intercept_relay(false,false)`,
  while its `nooutput_init` returns `disable_forwarding=true`. The harness is
  therefore physically pass-through in ELM mode and generic 0↔2 software
  forwarding is inactive. The decisive missing state is instead the independent
  FDCAN2 physical mux: ELM param 0 routes logical bus 1/FDCAN2 to OBD, while
  param 1 routes it to the normal harness. Comma 4/Cuatro inherits the exact
  Tres GPIO/transceiver mux. `UdsClient.bus` selects only the logical queue.
- **Consequence:** for yc's reported stock Toyota-B CAN0/CAN1 repin experiment,
  the static software-equivalence candidate is `set_safety_mode(3,1)` plus UDS
  logical bus 1. Changing only `BUS=1` while retaining implicit ELM param 0
  exercises the OBD physical path and is not an equivalent test. Live
  programming-session confirmation remains required.
- **Canonical:** [../tooling/panda-toyota-routing.md](../tooling/panda-toyota-routing.md);
  SECOC-033; `tests/verify_toyota_eps_bus_probe.py`; optional
  `tests/verify_external_corroboration.py`.

### CORR-033 — Memory-safety “verified” grades were backed by vacuous checks

- **Wrong:** MEM-SAFE-001–005 were labeled `verified` while
  `tests/verify_memory_safety.py` mostly checked that bytes existed at named
  addresses; two advertised semantic checks were literal `True`. The suite
  still passed after zeroing its load-bearing function bodies. MEM-SAFE-005
  also presented an enumerated negative as an unqualified verified absence.
- **Right:** the raw-byte verifier now asserts 36 decisive arithmetic, branch,
  table, data-flow, and reachability propositions; an independent Ghidra script
  asserts 107 instruction/edge/census propositions; and destructive/focused
  mutation tests prove sensitivity. MEM-SAFE-001–004 retain `verified` only for
  their statically asserted propositions. MEM-SAFE-005 is `bounded` to the
  named CAN/ISO-TP/SecOC/application-copy/range-check graph.
- **Canonical:** [../security/memory-safety-audit.md](../security/memory-safety-audit.md);
  `data/memory_safety_proof_matrix.csv`; `tests/verify_memory_safety.py`;
  `tests/verify_memory_safety_mutations.py`;
  `ghidra/scripts/verify/AssertMemorySafetyPaths.java`.

### CORR-034 — IT3ACNK was wrongly called keyless and host-key maps were incomplete

- **Wrong:** TMS-008 said `IT3ACNK.dll` had an AES S-box but no recoverable
  key, mapped `FUKUMORIYOSIYAMA` only to CommandCommon/UtilityEx2TY, and mapped
  `bCVaAQnA3fNdDgdl` only to IT3UtilityNeoNK. TMS-012 called the limited raw
  sweep exhaustive and the host maps complete.
- **Right:** pinned IT3ACNK bytes contain raw `bCVaAQnA3fNdDgdl` at
  file offset/RVA `0x8020` and hex-ASCII `FUKUMORIYOSIYAMA` at `0x834C`.
  `EncryptAds @ 0x2BB0` directly pushes the latter at `0x2BE1`, hex-decodes it,
  and reaches the software block-cipher helper. The bCVa constant has no direct
  IT3ACNK reference and is therefore recorded as bounded presence, not proven
  key use. TMS-012 is now limited to fourteen enumerated representation classes
  plus known x86 constructions/direct references; it makes no general
  constant-propagation or complete-absence claim.
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §§4.5, 7.1;
  `data/generated/techstream_v18/crypto_inventory.json`;
  `tests/verify_techstream_crypto_inventory.py`.

### CORR-035 — Sienna CUW writer selection was inferred from class names

- **Wrong:** TMS-007 assigned EPS reflashing to the older
  `CCanEMPS_V850E_PS2FlashWriter`/`CollateSeedKey` symbol family, while TMS-010
  promoted the Sienna firmware's UDS table into a specific host transcript
  with zero-valued DID writes. Neither claim followed the V18 factory edge.
- **Right:** all 201 encoded parameter INIs decode to 196 factory rows.
  `TCUWControlCommPhase.dll` selects one from `CalibrationFile` kind/contact/CPU
  metadata, loads the named DLL pair, and resolves its exported phase entry
  points. Standard and unified request builders are recovered independently;
  unified WDBI uses calibration-derived `OffsetAddress`, `SeedKey`, and `Nonce`,
  not intrinsic zeros. The local tree has no `.cuw`/`.cal`, so the exact Sienna
  row, values, address ranges, and routine choices remain unresolved. Firmware
  tables prove protocol compatibility and exclude VFOREST, not factory choice.
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §§5.1–5.2;
  `data/generated/techstream_v18/cuw_writer_inventory.json`;
  `tests/verify_techstream_cuw_writer_routes.py`.

### CORR-036 — DDB structural hashes and the P5 tail word were overnamed

- **Wrong:** TMS-013 and the steering corpus called raw full-section hashes
  “semantic variants” even though many included sections were only
  structurally inventoried. TMS-015 called the type-65 word at `+0x40`
  “enabled” without a pinned consumer proving that attribution.
- **Right:** the schema now says `structural_payload_sha256` and
  `structural_payload_variants`. Priority sections name only fields used by
  pinned lookup/string/variable/sort consumers and retain every raw byte. For
  type 65, exported consumers prove packed code `+0x2C` and string indices
  `+0x30/+0x34`; `+0x40` remains a deterministic `tail_word`. The 20 relevant
  `U023A87` rows are therefore described as nonzero-tail records, not enabled
  records. The `0x87 = Missing Message` mapping is unchanged.
- **Canonical:** [../tooling/techstream-ddb-pipeline.md](../tooling/techstream-ddb-pipeline.md);
  `data/generated/techstream_v18/priority_steering_ddb_semantics.json`;
  `tests/verify_techstream_priority_ddb_semantics.py`;
  `tests/verify_techstream_dtc_failure_types.py`.

### CORR-037 — In-function decode coverage was presented as an executable census

- **Wrong:** zero undefined bytes inside Ghidra's then-known functions was
  summarized as though every compiler-emitted instruction, callback, and
  executable body had been discovered. Naming provenance was also used as a
  proxy for semantic understanding.
- **Right:** the corrected function-discovery pass recovered omitted
  direct-call and dispatch-proven callback functions, increasing the
  reproducible graph from 5,921 to 6,037 functions. A separate conservative
  outside-function inventory still contains 22,514 decoded instructions in
  2,061 candidate runs; 2,001 remain unresolved and 60 pointer-referenced
  targets remain explicitly reviewed-unresolved. Zero undefined bytes is now
  claimed only inside the 6,037 current function bodies. Structural discovery,
  review state, semantic grade, oracle class, and execution status are separate
  fields; 5,927 functions remain unreviewed.
- **Canonical:** [../tooling/processor-module-audit.md](../tooling/processor-module-audit.md);
  [CORRECTED_GRAPH_REAUDIT_2026-08-11.md](CORRECTED_GRAPH_REAUDIT_2026-08-11.md);
  `data/outside_function_candidates.csv`;
  `data/semantic_coverage_summary.json`;
  `tests/verify_function_discovery.py`;
  `tests/verify_semantic_coverage.py`.

### CORR-038 — Bootloader SID 0x31 was a one-byte function shell and the FF00 gate was attributed to its worker

- **Wrong:** the durable UDS seed named `uds_routine_control @ 0x567E`, but the
  committed Ghidra graph contained only the single byte at `0x567E`; stage-2
  analysis had already decoded `0x5680`, splitting the four-byte RH850
  `prepare 8A 07 E1 70`. The resulting Bad Instruction bookmark left
  `0x5680..0x5935` outside every function. MEM-SAFE-001 consequently described
  the `0x58A2..0x58CC` FF00 authorization/erase-start logic as belonging to
  `routine_erase_task @ 0x5B70`.
- **Right:** the bootloader service-table pointer at `0x8EC0` independently fixes
  SID `0x31` to entry `0x567E`. The UDS seed now resolves the competing `+2`
  code unit before disassembly and fails closed if the authoritative target
  cannot decode. Two fresh four-stage rebuilds recover a 696-byte
  `uds_routine_control @ 0x567E..0x5935`. Its FF00 branch accepts authorization
  `0x01` or `0x81`, calls `flash_erase_start @ 0x41E0`, then records state
  `0x81/0x02`; `routine_erase_task @ 0x5B70` is only the later asynchronous
  completion worker. Recovering the body removes 30 conservative
  outside-function candidate runs.
- **Canonical:** [../security/memory-safety-audit.md](../security/memory-safety-audit.md);
  [../tooling/processor-module-audit.md](../tooling/processor-module-audit.md);
  `ghidra/scripts/seed/SeedUdsServiceTable.java`;
  `ghidra/scripts/verify/AssertMemorySafetyPaths.java`;
  `tests/verify_bootloader_diagnostics.py`;
  `tests/verify_function_discovery.py`.

### CORR-039 — Techstream was said to have no torque-command information

- **Wrong:** TMS-006 and the Techstream executive summary said the entire
  `0x2E4` torque-command control path was "invisible to Techstream." The narrow
  claim that Techstream does not send/receive SecOC runtime frames was valid,
  but the wording incorrectly excluded diagnostic visibility of the same
  steering-command domain.
- **Right:** Techstream V18 `EMPS_P5.ddb` is master-routed as category 405 /
  generation 20 and contains monitor 402 **`Command Value Torque`**. The P5
  signal-info consumer proves its field is 16 bits wide; its physical-data →
  unit-table chain resolves to **`Nm`**; and the exact metadata is identical in
  NA/EU/JP. Combined with the independently recovered authenticated signed-16
  CAN `0x2E4` command chain and pinned public Toyota DBC
  `STEER_TORQUE_CMD`, this is strong external corroboration for the steering-
  command domain. Techstream still does not prove that monitor 402 reads the
  CAN COM destination directly, does not participate in SecOC MAC/freshness
  handling, and provides no new command→d/q-current edge.
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §6.2.1;
  [../architecture/control-partition.md](../architecture/control-partition.md) §8;
  `data/generated/techstream_v18/application_interface_correlations.json`;
  `tests/verify_application_interface_correlations.py`.

### CORR-040 — Stage-6 steering-command tracing stopped before the real common cone and omitted the protected LTA mode

- **Wrong/incomplete:** the Stage-6 bounded-negative actuation audit described
  `BFA2 -> C144 -> C170 -> C1B8/C1B4/C1BC` plus `AE16/AE6E` exports as the
  deeper authenticated-command branch. That frontier was sufficient for the
  then-stated direct-xref negative but was not the end of the foreground
  steering command graph. It also treated `0x131` primarily as another
  protected verification stream rather than tracing its command semantics.
- **Right:** the whole-image pseudocode corpus exposed both missing dimensions.
  Protected `0x131` is the pinned Toyota `STEERING_LTA_2` command; its signed
  angle runs through `AE60 -> C8DE0 -> BFF0 -> C96D2/C97B2/C8D62 -> C0D6`.
  Its request bits and the protected `0x2E4` request are arbitrated by
  `CA354/CA47A`: LTA mode reaches `C13A`, torque mode reaches `C13D`, and
  `CA6B8` converges `C0D6` or `BFA2` at `C144`. The common command cone then
  continues beyond the old `C1BC` frontier through `C1D4 -> B788 -> B87E` and
  monitor/adaptation/fault consumers. Exhausting those consumers still finds no
  writer into the independently recovered `FEBE6Dxx` d/q-reference cone.
  Protected `0x132` was checked in parallel; its six recovered post-snapshot
  scalar destinations have zero runtime readers in this calibration. The prior
  **conclusion** (no recovered static command-to-d/q transfer) survives, but its
  evidence boundary is replaced by this larger dual-mode/common-cone audit.
- **Canonical:** [../architecture/control-partition.md](../architecture/control-partition.md) §9.3;
  `data/motor_actuation_path.csv`; `tests/verify_motor_actuation_boundary.py`;
  `ghidra/scripts/verify/AssertMotorActuationBoundary.java`.

### CORR-041 — `0x0D7` signal 280 inherited signal 284's GP destination in generated Rx evidence

- **Wrong:** `application_rx_signal_evidence.csv` and the derived Rx map assigned
  both SecOC CAN-FD `0x0D7` signals 280 and 284 to `FEBE8072`. The evidence
  exporter remembered the last `movea imm,gp,r1` seen before a receive call and
  therefore carried signal 284's direct GP pointer into signal 280.
- **Right:** signal 280 is the sole generated `application_com_receive_signal`
  call in this calibration whose destination is a stack temporary. `0x4B402`
  forms `SP+0x0B`, that pointer is passed in stack argument slot +4, and after
  the call `0x4B450` reloads the byte and `0x4B45C` stores it to
  `FEBE8076`. Signal 284 independently owns `FEBE8072`. The exporter now binds
  the destination only when `r1` is actually placed into the receive API's
  destination argument and, for an SP-relative destination, recovers a uniquely
  matching post-call stack-load → GP-store persistence edge. Independent raw
  CodeFlash tests pin both instruction sequences; the Ghidra ownership verifier
  bounds all direct `FEBE8076` readers. This correction exposes signal 280's
  real downstream path `FEBE8076 -> FEBEF094 -> B6396`, where it participates
  in protected invalidity/fault handling.
- **Canonical:** [../communications/application-rx.md](../communications/application-rx.md) §5.4;
  `ghidra/scripts/verify/ExportApplicationRxSignalEvidence.java`;
  `tests/verify_application_receive.py`; `AssertApplicationReceiveMap.java`;
  `data/secoc_rx_control_surface.csv`.
