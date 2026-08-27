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
- **Consequence (refined by CORR-072):** for yc's reported stock Toyota-B
  CAN0/CAN1 repin experiment, `set_safety_mode(3,1)` plus UDS logical bus 1 is
  the static **direct-diagnostic-route** candidate. Changing only `BUS=1` while
  retaining implicit ELM param 0 exercises the OBD physical path. Official
  harness schematics later proved that neither software setting is a full
  equivalent of physically moving the vehicle network onto the CAN0/CAN2
  intercept-relay pair; see CORR-072.
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
  [historical corrected-graph re-audit](../history/2026-08/CORRECTED_GRAPH_REAUDIT_2026-08-11.md);
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

### CORR-042 — Published region-1 CRC mismatch was mistaken for a CRC-algorithm incompatibility

- **Wrong:** the published `8965B4512000` high-CodeFlash region has CRC residue
  `0x5AA2313A` with stock word `0x0962887F`; treating that artifact mismatch as
  a validator led to the incorrect conclusion that blurbdust's
  `crc32_flash_range()` did not match the RH850 boot CRC and that persistent
  deployment still needed a different DCRA-faithful implementation.
- **Right:** stock region 0 is already an exact in-image validation of the
  community construction: CRC(`0x10000..0x17DEB`) = `0xEC0CD6CF`, the stored
  terminal word is its complement `0x13F32930`, and the full region residue is
  `0xFFFFFFFF`. The boot routine at `0x47EA` clears DCRA control, seeds COUT,
  feeds 32-bit words to CIN, and returns complement(COUT), matching this
  CRC-32/Ethernet terminal-fixup scheme.
- **Artifact explanation:** CRC-syndrome analysis of the entire 949,744-byte
  region 1 finds **exactly one** single-bit change that makes the existing stock
  `0x0962887F` word validate: VA `0xBB1C4`, bit 5, `0xA2→0x82`. Independently,
  that byte is the displacement byte of `sst.b 0x22,ep,r1`; the correction gives
  `sst.b 0x2,ep,r1` and turns the six surrounding destination offsets from
  `1,0x22,0,4,5,3` into the exact permutation `1,2,0,4,5,3`. On the reconstructed
  image, CRC(prefix) = `0xF69D7780`, whose complement is exactly the already
  stored `0x0962887F`, and the full region residue is `0xFFFFFFFF`. The unique
  correction is verified; interpreting it as a one-bit acquisition/readout
  error in the public dump is a strong inference.
- **Gate-2 consequence (superseded by CORR-064):** this entry originally
  computed `0x6E967C79 / 0x91698386` for the then-assumed
  `0x8E6C8: 0x9A→0x95` patch. CORR-064 proves that patch forces the mismatch
  arm. The corrected `0x8E6C6: e0d1→e001` patch instead yields reconstructed-
  clean prefix/fixup `0xBE36F00D / 0x41C90FF2`. The underlying CRC algorithm
  conclusion of CORR-042 remains valid. blurbdust's live shellcode does not
  hardcode either value: it computes the prefix CRC from actual ECU CodeFlash
  after target-block RMW and writes its complement.
- **Canonical:** [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md) §1.7;
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md) §9.6;
  `tests/verify_codeflash_crc_reconstruction.py`; `tests/verify_community_tooling.py`;
  `tests/verify_secoc_bypass_patch_point.py`.

### CORR-043 — Runtime patch config was injected into the final 4 KiB upload artifact

- **Wrong:** the first exploit-engineering host implementation treated the
  bootloader upload as an ordinary flat 4 KiB linked image, reserved a config
  slot at final-payload offset `0xF80`, and injected the calibration-specific
  runtime block after linking. That model would mutate bytes *after* the Toyota
  EPS payload CRC/CMAC/encryption step and therefore produce an upload that
  cannot pass routine `0x10F0` authentication.
- **Right:** the config belongs in the **plaintext shellcode** below the
  bootloader-owned callback slot at `0xFD0`. The corrected generic shellcode
  template now reserves `0xF70..0xFCF` for the 96-byte config, ending at the
  callback boundary `0xFD0` (placement updated by CORR-050 after complete FCU
  error handling increased code size).
  After injection, the host reproduces the proven Bk2ol/Vance package: callback
  at `0xFD0`, authenticated descriptor at `0xFE0`, terminal CRC adjustment over
  `0x000..0xFEF`, CMAC at `0xFF0`, then AES-CBC encryption of all 4096 bytes.
- **Secret separation:** `PAYLOAD_BUILD_SECRET` at CodeFlash `0xBFD8` and
  `SEED_KEY_SECRET` at `0xBFE8` are distinct gates and now have separate host
  inputs. The former constructs/decrypts/authenticates the RAM image; the latter
  performs UDS SecurityAccess. Neither value is serialized into run metadata.
- **Mechanical proof:** `exploit/common/payload_package.py` decrypts the
  committed standard DataFlash-dump payload with `PAYLOAD_BUILD_SECRET`, verifies
  its `0xFFFFFFFF` CRC residue and CMAC, and repackages the recovered 0x18A-byte
  shellcode to the exact same ciphertext byte-for-byte. Regression tests reject
  post-package config mutation by construction because config injection occurs
  only in the plaintext template.
- **Canonical:** [../security/bootloader-payload-gate.md](../security/bootloader-payload-gate.md) §§2–8;
  `exploit/common/payload_package.py`; `exploit/patcher/build_payload.py`;
  `tests/verify_secoc_manifest_patcher.py`.

### CORR-044 — Dormant command-5 inputs/output required a new application runner

> **Superseded in part by CORR-052 (2026-08-13):** the CAN input mapping remains
> correct, but stock WDBI activation removes the activation patch and the host's
> full-window polling makes the status-source patch unnecessary.

- **Wrong:** treating the property-4 `0x01B` row as permanently opaque and the
  locally compared generated result as requiring a new CAN transmitter or a new
  standalone application command-5 runner for the first probe.
- **Right:** decompiler + raw metadata resolve signal 95 and 96 as exact 8-bit
  bytes at COM offsets `0x97/0x98`; selector 4 / mode 1 is therefore `0x01B =
  04 01 ...`, with the exact 16-byte message on `0x01C/0x01D`. Data alone still
  cannot activate the bank, but the missing activation is only the four-byte
  startup return at `0x680B2`: `40 06 3f 00 → 80 07 66 0f`, a verified tail
  `jr 0x69018` to the stock activator.
- **Observation correction:** existing application DID `0x1010` selector 3 can
  expose the generated result with only three diagnostic-only substitutions:
  `0x68EAE: a49f8598 → 849f6198` (status source → `FEBE5060`),
  `0x68ECA: fa05 → 0000` (unconditional copy), and
  `0x68EDE: 24963a9a → 2496aa99` (48-byte source → `FEBE51AA`). The first 16
  returned bytes are the generated result; the adjacent 32 bytes are not part of
  the CMAC.
- **Bound:** all four mutations total 14 bytes in FCU block `0x68000`; the stock
  cyclic state machine, command-5 submit/driver path, completion callback, and
  compare/finalize logic remain intact. Hardware execution remains required to
  prove selector-4 availability in initialized application context.
- **Canonical:** [../communications/application-rx.md](../communications/application-rx.md) §5.5;
  [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md) §7.5;
  `exploit/command5/build_experiment.py`; `exploit/command5/stimulus.py`;
  `tests/verify_secoc_command5_experiment.py`.

### CORR-045 — Toyota static-blocking source was misclassified as unavailable

- **Wrong:** the first Milestone-4 ablation audit concluded that modern Panda
  sourced Toyota safety from a separate unavailable `panda-safety` repository,
  so the requested `disable_static_blocking` experiment could not be completed
  locally. That conclusion came from searching only inside `panda/board/` for
  the hook implementation.
- **Right:** Panda `board/main.c` includes `opendbc/safety/safety.h`, and Panda's
  SCons build adds the local `opendbc_repo` include path. The exact Toyota safety
  source is therefore already present at
  `opendbc_repo/opendbc/safety/modes/toyota.h`; `safety_fwd_hook` lives in the
  same local opendbc safety tree. No external safety repository is required.
- **Consequence:** the one-off MAC28 experiment was completed locally on
  `experiment/mac28-ablation`: Panda commit `39e1836884cf275864db763c5945e9c72db498cc`,
  opendbc commit `1366249dfe44c18a5ea0c4157cdfb57f7449e158`, and superproject
  commit `6c9d4c27f18209f07124376c73dd7e633154b5d6`. The safety override is
  narrowed to SecOC Toyota profiles; non-SecOC Toyota forwarding policy remains
  stock.
- **Verification:** the Panda firmware builds against the modified local
  opendbc tree; both SecOC Toyota safety classes pass 62 tests (9 expected
  skips); the one-off source/scope regression passes 4/4.
- **Canonical:** `exploit/behavioral_proof/README.md`;
  `exploit/behavioral_proof/openpilot_ablation_audit.json`;
  `tests/verify_secoc_mac28_behavioral_proof.py`.

### CORR-046 — Command-5 live stimulus used diagnostic-only Panda safety

- **Wrong:** the initial application-context command-5 wrapper selected ordinary
  Panda ELM327 safety and then used raw `can_send()` calls for `0x01B..0x01F`.
  ELM327 safety accepts diagnostic address ranges, not those application PDUs,
  so the wrapper would record attempted sends while Panda blocked them.
- **Right:** the local experiment firmware now uses a bounded ELM327 parameter
  that adds only eight-byte `0x01B..0x01F` on the encoded diagnostic bus. The
  wrapper selects it only around stimulus, checks Panda's blocked-Tx counter,
  fails if any frame was rejected, and restores ordinary ELM327 mode before
  diagnostic result polling.
- **Verification:** opendbc's ELM327 suite proves exact ID/bus/DLC scope; the
  repository command-5 suite proves parameter encoding, blocked-Tx rejection,
  and mode restoration. External commits and patch provenance are pinned in
  `exploit/command5/kai-openpilot-command5-safety.json`.
- **Canonical:** [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md);
  `exploit/command5/stimulus.py`.

### CORR-047 — MAC28 proof trusted declared behavior instead of deriving acceptance

- **Wrong:** the initial three-phase validator treated exact
  `observed_behavior` strings as the acceptance/rejection predicate. Its raw CAN,
  steering, firmware, and APPLY references could be placeholder files as long as
  their hashes matched, so a syntactically complete bundle could claim bypass
  without causal evidence.
- **Right:** phase labels are now non-authoritative notes. The validator
  independently recomputes source→forward transport from raw CAN, derives EPS
  acceptance from timestamp-aligned stock command/torque, `0x262` LKA state,
  and fault evidence, validates read-only DTC/F181 snapshots, reproduces the
  exact patched image from the semantic manifest and stock bytes, and binds the
  completed APPLY run plus telemetry. Missing, malformed, ambiguous, or
  inconsistent evidence fails closed.
- **Verification:** the deterministic trial uses the real Sienna CodeFlash and
  semantic manifest and includes adversarial cases for relabeling, fake
  steering, forwarding-report unbinding, phase-image substitution, and patched
  image tampering.
- **Canonical:** [../security/secoc/application-chain.md](../security/secoc/application-chain.md);
  `exploit/behavioral_proof/README.md`; `validate_trial.py`.

### CORR-048 — RAM payload telemetry did not implement the full RSCFD Tx handshake

> **Superseded in part by CORR-065:** the ready/acknowledgement mechanics below
> remain correct, but the encoded result polarity stated here was itself reversed.

- **Wrong:** the patch runtime had an empty busy-status check, and both patcher
  and dumper treated any nonzero `CFDTMSTS` result as successful transmission.
  A busy slot could therefore be overwritten, while abort/error results could
  be acknowledged as if their frames were delivered.
- **Right:** firmware `rscfd_tx_buffer_submit @ 0x36DE` requires
  `status & 0x0E == 0`. Its confirmation path extracts
  `(status & 0x06) >> 1`, treats 2/3 as errors, and clears result bits with
  `& 0xF9` plus `syncp`; the only nonzero success is result 1. Both payloads now
  follow that order and service the watchdog while waiting. The dumper also
  bounds waits/retries and latches an unrecoverable transport fault; the compact
  patcher halts on a failed result so writes cannot continue without telemetry.
- **Verification:** the pinned V850 toolchain builds the corrected generic
  patcher at `0xF50` bytes (below config slot `0xF60`) and the read-only dumper at
  588 bytes; deterministic suites assert the register-operation ordering and
  status semantics against the firmware-backed transport tests.
- **Canonical:** [../communications/diagnostic-transport.md](../communications/diagnostic-transport.md);
  `exploit/patcher/README.md`; `exploit/dumper/README.md`.

### CORR-049 — Read-only wrapper accepted any caller-supplied shellcode

- **Wrong:** the live dumper authenticated and uploaded whatever `.text` path
  the caller supplied. Local CRC/CMAC validation proved packaging integrity but
  did not prove that the plaintext was the reviewed read-only implementation;
  its generated build hash was not pinned by a tracked audit.
- **Right:** `audited_build.json` pins exact `main.c` and builder hashes, Docker
  image content ID, entry offset, size, and the 588-byte executable SHA-256.
  The builder records matching source/toolchain metadata. The live wrapper
  checks all of those bindings before packaging or opening the UDS session and
  rejects missing/self-authored provenance, source drift, and altered bytes.
- **Verification:** the dumper suite exercises a complete matching provenance
  set and rejects executable and toolchain tampering; the pinned Docker rebuild
  reproduces executable SHA
  `e756229014ad27d62a4e7ab82e6af4d20cd6dfb261d3b3bff82424bd3a26cb3d`.
- **Canonical:** `exploit/dumper/README.md`;
  `exploit/dumper/audited_build.json`.

### CORR-050 — P1M-E backend accepted relocatable geometry and ignored FCU failures

- **Wrong:** config validation constrained blocks only relative to a
  caller-supplied `image_base/image_size`; it did not enforce the backend's
  absolute 1 MiB P1M-E CodeFlash window. The inherited FACI primitive also
  ignored error-clear, P/E-entry, and P/E-exit wait results and treated ready as
  sufficient without checking command-lock status after erase/program.
- **Right:** both host and payload require absolute CodeFlash
  `0x00000000..0x000FFFFF` plus 32 KiB blocks. FACI completion distinguishes
  timeout and command-lock/error, and failures are phase-coded across unlock,
  clear, entry, erase, program, and exit. Every failure after P/E-entry attempt
  runs exit/lock cleanup before returning.
- **Size correction:** complete status handling exceeded the former conservative
  config placement. The generic build now uses link-time size optimization and
  places the 96-byte config at aligned offset `0xF70..0xFCF`, ending exactly at
  but not overlapping the callback at `0xFD0`. The pinned build is `0xF6C`
  bytes, leaving four bytes before the config.
- **Verification:** host rejection tests cover shifted/oversized images;
  deterministic C-source checks cover every FACI phase and cleanup edge; the
  pinned Docker toolchain builds the complete template successfully.
- **Canonical:** `exploit/patcher/README.md`;
  `exploit/common/patch_config.h`; `exploit/patcher/flash_backend.c`.

### CORR-051 — Raw substitution requires a fresh short download per chunk

- **Wrong:** the MEM-SAFE-001 exploit sketch described one download of `N ≤ 15`
  followed by `ceil(N/15)` TransferData blocks, wording that became invalid for
  substitutions longer than 15 bytes. The handler requires a non-final chunk to
  be exactly `0x400`, so multiple short blocks cannot share one larger download.
- **Right:** each 1–15 byte chunk uses its own RequestDownload, block-counter-1
  TransferData, and RequestTransferExit; the next chunk reopens at the advanced
  address. The stale `0x10F0` authorization survives those transactions.
- **Verification:** `verify_exploit_followups.py` proves exact 15/15/10 chunking,
  transaction ordering, address advancement, reassembly, and RAM-window bounds.
- **Canonical:** [../security/memory-safety-audit.md](../security/memory-safety-audit.md);
  `exploit/followups/bootloader_primitives.py`.

### CORR-052 — Direct activator-pointer census missed a one-hop WDBI wrapper

- **Wrong:** SECOC-040 promoted two narrow facts—no raw CodeFlash pointer directly
  into `crypto_test_bank1_activate @ 0x69018`, and no alternate writer of active
  value `1`—into a whole-image claim that stock software could not reach the
  activator. That missed indirect dispatch through a wrapper.
- **Right:** the 19-row application WDBI callback table at `0x25804` row 8 is DID
  `0x100F`; its action pointer is `0x8A782`, and that wrapper directly calls
  `0x69018` at `0x8A786`. The paired precheck at `0x8A768` returns success,
  selector 1 is enabled with zero input fields, policy index 0 has zero configured
  SecurityAccess levels and session records 1/2/3, and the outer SID-`0x2E` gate
  permits programming/extended. Stock request `2E 01 10 0F` therefore arms bank
  1 in an allowed application session. CAN `0x01B..0x01F` alone still cannot arm
  it.
- **Experiment consequence:** CORR-044's activation tail-branch is unnecessary.
  Its status-source substitution is also unnecessary because the live host does
  not treat the status byte as completion; it polls the full observation window
  and compares generated-result bytes against the pre-stimulus baseline. The
  command-5 probe is reduced from four mutations / 14 bytes to two
  diagnostic-observation mutations / 6 bytes: `0x68ECA: fa05→0000` and
  `0x68EDE: 24963a9a→2496aa99`. A fresh application boot is required for each
  deterministic run because the stock activator only arms zero state and the
  finalizer leaves a terminal value.
- **Analysis consequence:** both WDBI callback columns are now seeded as
  dispatch-proven function tables. A clean four-stage Ghidra rebuild therefore
  recovers wrapper `0x8A782` and its call to `0x69018`, preventing recurrence of
  the direct-pointer false negative.
- **Canonical:** [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md);
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md);
  `ghidra/scripts/seed/SeedDispatchProvenFunctionTables.java`;
  `tests/verify_icus_stage7_static.py`;
  `tests/verify_secoc_command5_experiment.py`.

### CORR-053 — Application service objects were parsed eight bytes late

- **Wrong:** the application UDS table was parsed as 24-byte records beginning
  at `0x25E30`. That placed the direct callback at a synthetic `+0x10` field,
  shifting each non-subfunction callback onto the preceding SID. Consequences
  included `0x8B1F0` being called ECUReset, `0x948AA` being called RDBI,
  `0x93C62` being called CommunicationControl, `0x95DCE` being called WDBI,
  `0x8D344` being assigned to SID `0xAB`, and the 19-row `0x26AEC` table being
  classified as writable DIDs.
- **Right:** runtime instructions in `FUN_8F282`, `FUN_8F6FA`, and `FUN_8F750`
  index **24-byte service objects from `0x25E28`**. The object layout is direct
  callback `+0x00`, security-list pointer `+0x04`, session-list pointer `+0x08`,
  subfunction-table pointer `+0x0C`, SID `+0x10`, subfunction flag `+0x11`, and
  security/session/subfunction counts `+0x12/+0x13/+0x14`. The corrected direct
  ownership is `SID 14 -> 0x8B1F0` (ClearDiagnosticInformation),
  `22 -> 0x945DC` (ReadDataByIdentifier), `23 -> 0x948AA`
  (ReadMemoryByAddress), `2E -> 0x93C62` (WriteDataByIdentifier),
  `31 -> 0x95DCE` (RoutineControl), and `BA -> 0x8D344`; SID `AB` uses its
  three-entry subfunction table at `0x25CD0`. Secondary object `0x26008`
  independently binds SID `22` to `0x945DC`.
- **Security consequence:** `0x26AEC` is the **19-entry RoutineControl RID
  surface**, not a WDBI DID table. Eighteen policy-0 RIDs have no configured
  SecurityAccess levels and are reachable under the corrected SID-`0x31` outer
  session set `1/2/3`; RID `0x1010` remains policy-1 / extended-only and still
  relies on ICU-S package authentication. Bank-1 activation is therefore
  `31 01 10 0F` with positive response `71 01 10 0F`, and RID-`0x1010` result
  readback is `31 03 10 10` / `71 03 10 10`. The lower lifecycle/service-mode,
  command-5 activation, and command-8 cryptographic behaviors remain valid;
  their UDS service framing and effective session boundary were wrong.
- **Supersedes the framing portions of:** CORR-010, CORR-011, CORR-014, and
  CORR-052. Their lower-function findings remain useful where not dependent on
  the shifted service-object interpretation.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md);
  [../diagnostics/application-routine-control-surface.md](../diagnostics/application-routine-control-surface.md);
  [../security/application-security-access.md](../security/application-security-access.md);
  `tests/verify_application_diagnostics.py`;
  `tests/verify_application_routine_control_surface.py`;
  `tests/verify_icus_key_update.py`;
  `tests/verify_secoc_command5_experiment.py`.

### CORR-054 — Application SID `0x23` is a real bounded memory-read service

- **Wrong:** Stage-7 software-path analysis treated SIDs `0x23/0x34/0x36/0x37`
  as the same null-callback/simple-response class and concluded that the
  application had no arbitrary-address memory-read implementation (old
  SECOC-020 wording).
- **Right:** CORR-053's runtime object boundary maps SID `0x23` to direct callback
  `0x948AA`. `0x9479A` parses address/length format; the only configured ALFID is
  `0x15`, encoding memory identifier + four-byte address and one-byte size.
  Memory ID `1` reads `FEBE0000..FEBFFFFF`; memory ID `2` reads
  `FF200000..FF207FFF`; both read-range records have zero SecurityAccess entries
  and no write-range configuration. Compiled exclusion checks leave 107,924 RAM
  bytes and 29,952 DataFlash bytes readable. SIDs `0x34/0x36/0x37` remain null.
- **Security boundary:** exclusions cover the command-5/key-update result region,
  application SecurityAccess state, object-15 RAM, DataFlash `0xFF206C00..6EFF`,
  and the `0xFF207800..7FFF` ICU-S tail. The bootloader payload-derivation buffer
  `FEBF2D08..2D17` is not excluded, but useful live residue there is not statically
  proven to survive the required reset/session sequence.
- **Canonical:** [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md);
  `tests/verify_application_read_memory_by_address.py`;
  `exploit/followups/application_rmba_probe.py`.

### CORR-055 — RDBI stale-response disclosure affects 48 DIDs, not only the 15 45-byte rows

- **Wrong:** DIAG-APP-015 initially scoped the stale Dcm response-buffer leak to
  the visually conspicuous 15-row `1CF4..1CFF,1D01..1D03` family because those
  rows all declared 45 bytes and formed one contiguous callback-stub block.
- **Right:** an exhaustive scan of all 242 RDBI table rows finds **48 rows** whose
  configured producer begins with the exact complete four-byte body
  `mov 0,r10; jmp lp`. Their declared widths are 13×1, 12×2, 1×4, 4×7, 2×16,
  1×17, and 15×45 bytes. The exact DID set is `0111`; `1066/106A`;
  `10C7..10C9`; `10F7..10F9`; `1124..1129`; `112F..1131`; `11BC/11C8`;
  `1C99..1CA0`; `1CF4..1CFF`; `1D01..1D03`; `1F03/1F04`; `2030..2032`.
- **Why all 48 are live producer paths:** the rows occupy DID classes 0, 2, and
  3. Each class advertises direct-read capability and its record-operation
  wrapper (`0x935BA`, `0x9361A`, `0x9364A`) calls `0x8A374`. The generic
  dynamic/element override that could bypass the primary callback is disabled by
  zero configuration at `0x261E8` and `0x261EC` in this calibration.
- **Security consequence:** DIAG-APP-015 remains valid but broader. A request can
  disclose the configured row width (1..45 bytes) from persistent response
  buffer `FEBE59F8`; 45 bytes remains the maximum per request. The default bench
  oracle for DID `1CF4` is unchanged.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md);
  [../security/application-security-access.md](../security/application-security-access.md);
  `tests/verify_application_rdbi_stale_response.py`;
  `exploit/followups/application_rdbi_stale_probe.py`.


### CORR-056 — `0x25768` is the active 13-entry WDBI callback table, not a dormant 32-entry routine table

- **Wrong:** the post-AB audit described `0x25768` as a 32-entry internal
  RoutineControl/control-ID table structurally associated with SID `0x28` but
  stock-wire gated. The firmware-table vocabulary parser reinforced the same
  model by reading 32 rows past the real table and by decoding service objects
  from the pre-CORR-053 `0x25E30/0x25FC8` bases.
- **Right:** lookup `0x8D3CC` explicitly stops after index `0x0C`; `0x25768`
  therefore contains **13** valid 12-byte records. Its caller chain is unique:
  `0x8D3CC/0x8D416 <- 0x8A482/0x8A542 <- 0x8A630 <- 0x936AA/0x936D6`.
  Those wrappers occupy the write-operation slots of DID classes
  `0x0201..0x02FF` and `0x2001..0x20FF`, and the active SID-`0x2E` path reaches
  them through `0x9395E -> 0x92A70`. No SID-`0x28`, SID-`0x31`, or SID-`0xAB`
  edge enters this chain. SID `0x31` independently uses callback `0x95DCE` and
  the 19-RID table at `0x26AEC`.
- **Secondary correction:** `tools/diagnostics/firmware_tables.py` now decodes
  service objects from runtime bases `0x25E28/0x25FC0` with the corrected
  24-byte layout. Its generated vocabulary no longer shifts direct callback
  ownership by one service and now reports `wdbi_callback_table=0x25768/13`
  and `routine_control_table=0x26AEC/19`.
- **Consequence:** the previously recovered object-`0x101/0x102/0x103`
  persistence paths are not dormant internal possibilities; they are reachable
  through real SID `0x2E`, subject to its session and callback-local gates.
  DIAG-APP-016 records the corrected WDBI security surface.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md);
  [../security/application-security-access.md](../security/application-security-access.md);
  `data/application_wdbi_surface.csv`; `tests/verify_application_wdbi_surface.py`;
  `tests/verify_application_wdbi_callbacks.py`.

### CORR-057 — WDBI DID `0x2010` writes diagnostic residue, not live runtime command state

- **Wrong:** the initial true-WDBI surface matrix described DID `0x2010` as
  updating a “live runtime command-state block” at `FEBEB48E/49C/4A0`.
- **Right:** `application_wdbi_2010_result @ 0x4EF04` maps valid payload `00` to
  `0x55AAAA55/0x55AAAA55` and payloads `01/02` to
  `0xAA5555AA/0x55AAAA55`, then calls `FE09C -> B7C0E`. `B7C0E` writes marker
  `0x44` plus those two words and returns fixed status `0`. Exact live Ghidra
  xrefs for all three RAM cells contain only their initialization write and the
  `B7C0E` write; none has a runtime READ/PARAM reference.
- **Async-status boundary:** invalid payloads bypass `B7C0E` with status `-12`.
  Generic mapper `0x4C4A4` maps `0 -> 0` and `-12 -> 4`; only `-1 -> 2`. The
  callback's `result==2` branch is therefore unreachable and cannot set shared
  `FEBE816A=0x2E10`; DID `2010` always clears that word to zero. `FEBE816A` is
  generic diagnostic service bookkeeping: dispatcher `0x4C3CA` recognizes
  high-byte service tags `0x14/0x2E/0xBA`, and ClearDiagnosticInformation uses
  the same word with `0x1410`.
- **Consequence:** no live application-state consumer or direct d/q/PI/PWM join
  is recovered for DID `2010`. This is a static dead/write-only-state result for
  the current calibration, not a claim about all related Toyota EPS variants.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md);
  [../security/application-security-access.md](../security/application-security-access.md);
  `data/application_wdbi_surface.csv`;
  `tests/verify_application_wdbi_2010_dead_state.py`;
  `tests/verify_application_wdbi_2010_dead_state_live.py`.


### CORR-058 — `sec_count=0` does not eliminate callback-local SecurityAccess checks; SID `0xBA` F7 requires level 2

- **Wrong:** SEC-APP-004 and the initial proprietary-service audit generalized the
  empty Dcm service/DID/RoutineControl security-policy tables into “no configured
  SecurityAccess gating in this calibration,” and bounded SID `0xBA` only through
  its first operation.
- **Right:** the policy-table statement remains true, but it is layer-specific.
  The full ten-operation BA table at `0x28098` contains F7/`BAENA`; its start
  callback `0x34DAE` calls `0x34D96 -> 0x8C8C6 -> 0x8FDCA`, and `0x34D96`
  requires security-mask bit `0x02`. Setter `0x9075A` defines the mask as bit
  `(level-1)`, making `0x02` application SecurityAccess level 2 (`27 03/04`).
- **Persistent boundary:** successful F7 persists ordinary object 24 (`0x18`)
  plus redundant object 5 (`0x105`) and establishes `FEBE5F27=0x5A` with a
  30-invocation countdown. Restore helper `0x347B0` reconstructs that marker
  from NvM, and generic BA dispatcher `0x348B4` accepts registered operations
  while the marker is active without a fresh SA read. F6/`BADIS` clears it.
- **Community patch consequence:** blurbdust's `0x3485A` egg is the BA shared
  token comparator, not SecOC acceptance logic. Forcing it true removes BA token
  comparisons but does not bypass the independent F7 SA2 check; therefore it is
  neither an initial application-SA bypass nor a SecOC bypass.
- **Canonical:** [../diagnostics/application-proprietary-ba.md](../diagnostics/application-proprietary-ba.md);
  [../security/application-security-access.md](../security/application-security-access.md);
  `data/application_proprietary_ba_surface.csv`;
  `tests/verify_application_proprietary_ba.py`;
  `tests/verify_application_proprietary_ba_live.py`.


### CORR-059 — XCP generic writes are direct arbitrary 32 KiB LocalRAM writes, not merely a shadow-window configuration

- **Wrong:** COM-005 described `0xFEBF7C00..0xFEBFFBFF` primarily as a
  "calibration-shadow" write window and left the existence/impact of generic
  writes bundled with the open consumer question.
- **Right:** configured XCP-shaped command `F0 DOWNLOAD @ 0x80F12` directly
  copies 1–6 tester bytes to the current MTA after exact LocalRAM and shadow
  range validation, then advances MTA. Repeated requests can overwrite the full
  32 KiB interval. `EC MODIFY_BITS @ 0x80FD8` separately performs aligned
  32-bit masked read-modify-write in the same range. GET_SEED/UNLOCK are absent
  from the command map, so the firmware-static write primitive itself is
  unauthenticated.
- **Impact boundary:** this does not establish RCE or steering control. The
  containing LocalRAM block is non-executable, and exhaustive live-project
  function-owned references into the interval are exactly three WRITEs to
  `FEBF7C00`, with zero READ/PARAM/call refs and zero function entries. No direct
  callback, persistent-flash, or motor consumer is recovered. Runtime/computed
  aliasing remains a bounded unknown.
- **Dynamic boundary:** external forwarding of CAN `0x7F7/0x7F8` remains
  unobserved; the default live probe stays read-only.
- **Canonical:** [../communications/xcp-command-dispatch.md](../communications/xcp-command-dispatch.md);
  `tests/verify_xcp_security.py`; `tests/verify_xcp_shadow_write_live.py`;
  `AssertXcpShadowWriteBoundary.java`.

### CORR-060 — The XCP write window is supervisor-executable by hardware MPU configuration; "non-executable" was Ghidra analysis metadata

- **Wrong:** COM-005 and CORR-059 stated the containing LocalRAM block is
  "non-executable", citing the Ghidra program database's LocalRAM
  `MemoryBlock` attribute `execute=false`. That attribute describes the
  imported analysis program, not the deployed hardware.
- **Right:** the raw CodeFlash MPU tables cover exactly the XCP write window.
  MPU region-1 bounds at `0x3181C/0x31820` are `FEBF7C00..FEBFFBFC`;
  the initial application selector `0x3180F=0x00` loads context 0;
  `0x31810=0x01` selects context 1 for foreground/flash-end entry, while
  `0x31811=0x00` selects context 0 for both CAN1 Tx/Rx ISR wrappers. Reset
  startup explicitly clears `ASID=0`, and application MPU init loads `MPM=3`
  (MPE+SVP enabled). Per Renesas P1M-E manual Table 3.49, context-0 attribute `MPAT1 @ 0x31898 = 0xB8` grants
  supervisor read/write/**execute**, and context-1 `MPAT1 @ 0x318D8 = 0xA8`
  grants supervisor read/**execute**. Neither context grants user-mode
  access (bits 0..2 are zero).
- **Impact boundary (unchanged in substance):** this correction does **not**
  upgrade COM-005 to RCE. The exhaustive consumer census still finds exactly
  three direct WRITE references to the window base (`0x142E`, `0x62652`,
  `0x976E4`) and zero READ/PARAM/call/jump references, zero function entries
  inside the window, and no recovered callback, pointer, flash, or motor
  consumer. The four executable-code materializations of `FEBF7C00` are pinned
  to startup clear `0x1426`, application page copy `0x6263E`, XCP range helper
  `0x974D0`, and E4 copy `0x976D0`; the suspicious adjacent initializer at
  `0x6266E` starts at `FEBF7BB0` and its fixed 0x40-byte loop ends at
  `FEBF7BEF`, so it cannot enter the attacker-write window. The corrected
  statement is: the window is attacker-writable
  **supervisor-executable** RAM with **no recovered control-transfer
  consumer** — write capability verified, execution path not recovered.
- **Deterministic check:** `tests/verify_xcp_window_mpu_permissions.py` pins
  hardware MPU permissions; `AssertXcpShadowWriteBoundary.java` additionally
  pins direct-reference topology, all four recovered write-window base
  materializers, and the bounded-below `FEBF7BB0..FEBF7BEF` adjacent loop.
- **Canonical:** [../communications/xcp-command-dispatch.md](../communications/xcp-command-dispatch.md);
  [FINDINGS.md](FINDINGS.md) COM-005;
  `tests/verify_xcp_window_mpu_permissions.py`.

### CORR-061 — Command-5 bank output bytes remain private, but the terminal negative state is stock-DTC observable

- **Wrong:** the prior command-5 assessment treated the stock bank as fully
  locally compared and effectively required a fresh application boot after each
  terminal state, leaving `FEBE51AA` observation as the only stock-side
  discriminator.
- **Right:** the generated 16-byte result still has no recovered stock byte-output
  route, but terminal failure is externally observable. Completion callback
  `0x6926A` maps both command-5 execution failure and successful-generation/full-
  result mismatch to state `0x44`; finalizer `0x68D0E` sets `FEBE5097=0x5A`;
  monitor `0x55F1C` reports Dem event `0xCC,0x32`. Event `0xCC` maps to enabled
  DTC-table index 133 / DTC `0x00D317` / failure type `0x57`, and the application
  SID `19 02` path is available in sessions `1/3` with zero configured
  SecurityAccess entries. Its supported status mask is `0xB9`, and the normal Dem
  aggregator makes the event visible to that enumeration path.
- **Boundary:** this is a terminal **negative-outcome** side channel, not direct
  MAC disclosure. The DTC cannot distinguish command execution failure from a
  wrong chosen expected value. Only after successful command execution is known
  independently can it serve as a full expected-result equality discriminator.
  The direct-reference census still finds no DTC/snapshot/UDS reader of
  `FEBE51AA..FEBE51B9` beyond local comparator `0x69068`.
- **Re-arm correction:** the finalizer still leaves bank active state `0x02/0xFF`,
  so a fresh application boot is the deterministic baseline. But runtime reset is
  not impossible: transition helper `0x4F93C` can request `0xA5`, cyclic
  `0x68C0C` then invokes full reset `0x67FCE`, and that reset clears bank active
  state to zero. Deliberate external control of that transition is unproved.
- **Operationalization:** `exploit/command5/stimulus.py` records read-only
  `19 02 FF` DTC snapshots before and after the existing bounded experiment and
  never issues ClearDiagnosticInformation.
- **Canonical:** [FINDINGS.md](FINDINGS.md) SECOC-046;
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md);
  `tests/verify_command5_dtc_side_channel.py`;
  `tests/verify_secoc_command5_experiment.py`.

### CORR-062 — RID 0x1010 status 0x02 does not prove the diagnostic's own envelope executed

- **Wrong (implicit sufficiency reading):** the §8.1 transport contract
  presented selector-`03` status `0x02` with 48 proof bytes as evidence that
  *the submitted RID `0x1010` package* completed: "`0x02` | complete |
  M4[32] + M5[16]". Application-chain §5.4 similarly described the
  diagnostic state machine as the sole application command-8 submitter whose
  completion drives `0x44`.
- **Right:** `icus_key_update_completion_callback @ 0x6920A` routes its next
  state solely by reading diagnostic-active `FEBE5085` at completion time; it
  does not track which bank submitted the in-flight job, and
  `icus_key_update_diagnostic_start @ 0x68E16` never checks bank-0
  `FEBE508A`. If the RID-`0x100E` bank-0 crypto test (SECOC-047) has a
  command-8 job in flight, a diagnostic start between submit and completion
  receives that completion as its own: it walks `0x44 -> 0x46 -> 0x55`,
  terminalizes status `0x02`, and `31 03 10 10` returns 48 **zero** bytes from
  `FEBE523A` while the real M4/M5 sit unread at `FEBE526A` until bank-0's
  1200-tick timeout scrubs them.
- **Consequence of the error:** any dealer/tooling workflow or trace analysis
  that treats status `0x02` (with zero proof bytes) as confirmation of its own
  rekey request can be fooled by an interleaved bank-0 run; conversely, a
  captured trace cannot attribute a command-8 completion to a specific
  envelope without excluding concurrent bank-0 activity. The race is a
  state-machine misattribution/false-success oracle, **not** a key bypass and
  **not** key disclosure (no stock reader of `FEBE526A`; RMBA/XCP exclude the
  region).
- **Canonical:** [FINDINGS.md](FINDINGS.md) SECOC-047/SECOC-048;
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md) §5.10;
  `tests/verify_crypto_test_bank0_composition.py`.

### CORR-063 — RMBA lower-reader size rejection was imprecisely stated

- **Wrong:** the earlier application memory/read boundary said the lower reader
  "rejects values above 256", implying 256 was accepted and omitting zero.
- **Right:** `0x4EB1C` performs unsigned `(size - 1) < 0xFF`, rejecting size
  `0` and every size `>=256`. With the one-byte SID-`0x23` size field and the
  upper remaining-capacity gate, the effective domain is
  `1..min(255, remaining response capacity)`.
- **Consequence:** no host-tool impact; the correction closes the off-by-one
  boundary needed by the RMBA memory-safety audit.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md);
  [FINDINGS.md](FINDINGS.md) MEM-SAFE-007;
  `tests/verify_application_rmba_memory_safety.py`.

### CORR-064 — Gate-2 result polarity and bypass branch direction were inverted

- **Wrong:** SECOC-029/043/045 previously described `FEBE555C != 0` as a MAC
  match, labeled the `0x8E6DA -> FUN_0008E382` BNE target as authenticated
  delivery, and labeled the fallthrough through `FUN_0008E2BA` as a
  failure/release path. The derived patch `0x8E6C8: 9a0d -> 950d` therefore
  changed the BNE into an unconditional branch to what was incorrectly called
  the success arm. Its reconstructed-clean offline fixup was `0x91698386`.
- **Right:** the synchronous command-7 slot-4 KAT at `0x680F8` initializes its
  result cell to `1` and reports pass only when command 7 leaves that cell equal
  to **zero**. Gate 2 materializes `(FEBE555C != 0)` into `r26`; consequently
  `0x8E6C6 cmp r0,r26; 0x8E6C8 bne 0x8E6DA` falls through on verified result
  zero and branches on nonzero/not-verified. The fallthrough calls
  `FUN_0008E2BA`, which extracts the queued PDU and reaches
  `FUN_0008E7C6 -> FUN_00080BBA`, the bounds-checked PduR/COM routing
  dispatcher. The taken arm calls `FUN_0008E382`, which performs
  failure/retry/state bookkeeping and has no recovered PDU route.
- **Correct patch:** `0x8E6C6: e0d1 -> e001`, changing `cmp r0,r26` to
  `cmp r0,r0` while preserving the following `9a0d` BNE. This makes the
  mismatch branch impossible and forces the verified-delivery fallthrough.
  On the reconstructed-clean `8965B4512000` image the corrected patch yields
  prefix CRC `0xBE36F00D` and fixup `0x41C90FF2`; on the committed published
  artifact it yields `0x23247E0C` / `0xDCDB81F3`. Live code must recompute the
  adjustment from live CodeFlash.
- **Why this was caught:** yc's 2026-08-16 external field report used exactly
  the compare neutralization (`e0d19a0d... -> e0019a0d...`) and reported
  working lateral on a 2024 RAV4 Prime. Re-reading the firmware against that
  observation exposed the arm-label contradiction already latent in the
  `FUN_0008E2BA -> PduR/COM` call chain. The command-7 KAT then independently
  pinned the result polarity from firmware bytes.
- **Regression coverage:** the old `9a0d -> 950d` encoding is retained only as
  a negative test proving that it forces the mismatch arm. The semantic
  manifest builder rejects both the old operation and the old branch bytes
  masquerading as CMP neutralization.
- **Canonical:** [FINDINGS.md](FINDINGS.md) SECOC-029/043/045/049;
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md) §9;
  `tests/verify_secoc_acceptance_gate.py`;
  `tests/verify_secoc_bypass_patch_point.py`;
  `tests/verify_secoc_semantic_patch_resolver.py`.

### CORR-065 — RSCFD Tx completion result polarity was still reversed

- **Wrong (CORR-048):** after correctly recovering the full busy/completion/ack
  handshake, the repository stopped treating every nonzero `CFDTMSTS` result
  as success but then classified encoded result `1` as the sole success and
  results `2/3` as errors. `exploit/common/runtime.c`, the CodeFlash dumper,
  SEC-EXP-003, and the transport documentation all inherited that mapping.
- **Right:** `direct_call_target_00003e48 @ 0x3E48` does extract
  `(CFDTMSTSn & 0x06) >> 1`, but that extractor alone does not define success.
  Its caller preserves the extracted value across the `&0xF9`/`syncp`
  acknowledgement and ID read, then executes `0x3ED6 add -2`, `0x3EE0 cmp 1`,
  `0x3EE2 bh`. Original result `1` therefore takes `0x3EEA -> 0x475C`, whose
  wrapper passes CanIf status `2`; original results `2/3` take
  `0x3EE4 -> 0x4744`, whose wrapper passes CanIf status `0`.
  `cantp_tx_confirmation_callback @ 0x1F0C` invokes `CanTp_TxConfirmation` only
  for status `0`. Thus **encoded result 1 is the firmware error path and
  results 2/3 are the successful-completion set**.
- **Tooling correction:** patcher telemetry and the read-only dumper now wait
  for a nonzero result and accept the set with bit 2 asserted (`status & 0x04`),
  exactly encoded results `{2,3}`. The dumper retries result `1`; the patcher
  refuses to continue its evidence channel on result `1`. The audited dumper
  was rebuilt under the same pinned Docker V850 toolchain; its reviewed binary
  is now 592 bytes.
- **Why this survived CORR-048:** the earlier test proved the result extraction,
  acknowledgement, and a host-side constant but did not prove the downstream
  wrapper/status consumer. It therefore verified implementation consistency
  around an incorrectly labeled enum. `verify_exploit_predicate_semantics.py`
  now makes producer convention, downstream arm meaning, host predicate, and
  opposite-direction regressions explicit across exploit-critical decisions.
- **Related audit:** the same pass re-proved that the command-5 `0x68ECA: fa05->0000` observer mutation is in the correct direction: stock status `!=2`
  branches to zero-fill while status `2` falls through to the selected-source
  copy path, so NOPing the BNE forces copying. RID1010 status `0x02` remains a
  known ownership/misattribution false-success condition (CORR-062), not a new
  completion-success oracle. The Sienna community egg really does force its BA
  comparator to return match, but its SecOC ownership remains disproved. Boot
  application validity remains zero-success/nonzero-failure.
- **Canonical:** [FINDINGS.md](FINDINGS.md) SEC-EXP-001/003;
  [../communications/diagnostic-transport.md](../communications/diagnostic-transport.md);
  [../tooling/exploit-predicate-semantics.md](../tooling/exploit-predicate-semantics.md);
  `tests/verify_can_transport.py`;
  `tests/verify_exploit_predicate_semantics.py`;
  `tests/verify_secoc_command5_experiment.py`.

### CORR-066 — Lochuan `0x664E6: 0x31→0x10` is checkpoint fail-open, not SecOC MAC acceptance

- **External historical model:** the pinned `lochuan/RH850_P1m-E` report labels
  `0x66374` as `secoc_mac_job_scheduler`, `0x674A8` as
  `secoc_mac_generate_submit`, and checkpoint objects 5/6 as likely CAN
  `0x131/0x2E4` MAC objects. The later pinned
  `lochuan/8965B4512000-FW-PATCH` consequently treats `0x664E6: 31→10` as the
  reviewed persistent control-flow target.
- **Right:** `0x664E6` is only the immediate byte inside
  `0x664E4 movea 0x31,r0,r28` in ordinary checkpoint completion worker
  `FUN_00066446`. Stock status is already `0x10` on lower completion result
  `0x5A`. On lower failure the worker changes the public object status to
  `0x31` **and independently stores `0x5A` to `FEBF067C`**. Replacing only the
  `0x31` byte with `0x10` therefore lies to the checkpoint consumer while
  leaving the lower failure indication intact; it does not alter ICU-S command
  7 or Gate-2 delivery.
- **Fault consequence:** `FUN_000667DE` consumes/clears `FEBF067C/FEBF067D`,
  and `FUN_000556DC` reports them as Dem `0x94/0x93`. Both event records map to
  enabled DTC index 3, raw DTC record `46 d6 45 00 01 00 00 00` (failure type
  `0x46`, identifier `0x45D6`). The public status array `FEBF0308[]` has no
  direct reference from the `0x8E6xx` SecOC acceptance worker in the canonical
  graph.
- **Activation boundary:** both ordinary queue states `0x22` and `0x33`
  converge on write completion state `0x33`; successful NvM service-`0x07`
  completion produces lower result `0x5A` and branches around `0x664E4`. The
  patched immediate is therefore semantically dormant unless an ordinary write
  completion has already been classified non-success. The exact service-7
  backend is now pinned too: lower operation class 2 selects completion adapter
  `0x72DFA`, which commits request result only for write-device state 0/1. The
  mode-2 report table maps key `1` to raw `0`/terminal success, maps
  `FFFF/FFFE/FFFD/FFFB/FFFA/FFFF0000` to terminal failure codes, and maps
  `FFFC` to raw `0x83`/device state 4, which remains nonterminal. `0xFFFD` is
  concretely produced by lower record-verification mismatches and `0xFFFB` by
  invalid state/range/setup paths. Stock `0x31` is therefore a terminal
  ordinary-write failure (or defensive unexpected-ring completion), not a
  pending/retry state and not necessarily only a physical program-pulse error.
  The same failure raises Dem `0x94` in stock and patched firmware, so DTC
  `0x45D6` is a witness to the storage failure rather than the patch-specific
  behavioral delta.
- **Ring-mismatch boundary:** `FUN_00067BC8` also reports lower failure when a
  nominally successful service-7 callback names a physical ring block other than
  the object's expected next slot. Normal ordinary writes are single-flight;
  triplicate callbacks route elsewhere. Submission sets public status `0x20/21`
  and `FEBF0690=0xFF`, while the only coordinator persistence-reinit path is
  gated by `FUN_00065E88`, which rejects both public `0x2x` status and ordinary
  wait byte `0xFF`. The callback router itself only dispatches an object still
  marked waiting and clears `FEBF0690` after `FUN_67BC8` records terminal state.
  No recovered normal overlap/reset path therefore produces a ring mismatch; it
  is a defensive unexpected/stale-completion guard. Duplicate/corrupt/unmodeled
  callbacks remain outside the static bound.
- **Concrete flakiness path:** object 6's 56-byte learned-state checkpoint stores
  `FEBEB592` through snapshot `FEBEE8AC` at payload `+0x30`. `FUN_000B9054`
  later trusts that field only when public object status is `0x10`; otherwise it
  substitutes sentinel `0x7F80`. The namespace-0 restore API copies the current
  RAM mirror before returning status, so a failed object-6 write plus the patch
  makes unpersisted RAM look valid within the same boot. On entry into the
  `>=0x200` mode band the foreground dispatcher can reload this state, and
  derived `FEBEB594/596 -> FEBEAC6E/6C` values enter the normal steering-command
  plausibility/adaptation model. This proves a real conditional steering-model
  consequence, but not that object 6 failed in the reported drive or that the
  model reaches one explicit LKAS-inhibit bit. Runtime object/status + `0x262`
  capture remains required for that last causal attribution.
- **Coupled persistence family:** objects 5/6/8 are explicitly committed together
  by `FUN_000B19D2`. Object 5 supplies restored reference values used by multiple
  object-6 acceptance validators, while object 8 seeds the same steering-learning
  partition. The `0x700..0x702` high-level sequence commits 5/6/8 before the
  recovered `0x800` final-shutdown sequence; a separate transition-phase worker
  commits 5/6/13 after a static 0-or-100 foreground-tick dwell. This broadens the
  fail-open blast radius without creating any MAC predicate.
- **Captured-storage negative:** all six source-ECU checkpoint records for object
  5, all six for object 6, and both records for object 8 are valid with valid
  generation/complement pairs. The supplied ECU therefore does not show an
  ongoing checkpoint-failure condition that would make `0x664E6` continuously
  active; a new failed ordinary NvM write is required.
- **Other patch-sensitive state:** object 7's exact-success restore feeds phase
  byte `FEBEAF44`, which participates in protected-`0x0D7` fault monitoring and
  system-mode event `0x2D`/substate `0x522`. This is a real mode/fault consequence
  of forged checkpoint success, not an ICU-S acceptance path.
- **Public-status bound:** none of the five dynamic `0x262 LKA_STATE` producer
  functions directly reads the object-6-sensitive model state, and CAN `0x351`
  comes from a separate debounce/fault family. No direct `object6 -> public
  LKAS-off` edge is recovered.
- **Complete object census:** all 32 ordinary descriptor slots now have an
  explicit patch-sensitivity disposition in
  `data/lochuan_patch_object_census.csv`. Enabled sensitive objects are
  `0,1,2,3,4,5,6,7,8,10,13,17,18,19,20,21,23,24`; enabled recovered-unaffected
  objects are `9,11,12,14,15,27`; the rest are disabled. The only recovered
  steering-adaptation family is 5/6/8, with object 7 on a separate protected
  status/mode fault path. Object 13 is bounded to snapshot/DID/monitor consumers;
  0..4/10/17..23 are monitor/event history, and 24 is the unrelated BA countdown.
- **External validation boundary:** Lochuan's public README explicitly says Flash
  `PASS` does not prove RX SecOC bypass. Deleted-but-reachable history does record
  real hardware work: a failed read-only DCRA probe, a rejected 32-KiB
  `RequestDownload`, and—most importantly—an audited target-sector transaction
  in which `0x60000` was prechecked, armed, written, and fully read back as the
  candidate. A subsequent live read still showed target=candidate while the CRC
  sector remained source; the later CRC trigger failed with raw
  `03 7F 31 31 00 00 00 00` / NRC `0x31`. The subsequent recovery release was
  explicitly offline-only and repository history contains no later hardware CRC
  commit/final PASS or stationary invalid-MAC steering proof. Core tests also
  reproduce the published target original/candidate SHA pins directly from the
  local source sector plus the single `0x664E6` mutation, so those hashes are
  identity pins rather than independent semantic evidence. The hardware record
  proves deployment/target-write mechanics, not SecOC acceptance.
- **Lineage boundary:** Lochuan's deleted CRC-route design explicitly cites
  `secoc-icanhack/extract_keys.py` and an independent friend
  `disable-secoc-script/flash_patcher.py` as the reviewed authenticated-upload /
  fixed-FF00 references. The first public payload commit says its patch payloads
  were migrated reviewed sources and its patch-era headers mechanically migrated
  from the old private `sienna-b4512000-rx-secoc` tree. This supports a shared
  I-CAN-hack -> blurbdust/@yc -> private-Lochuan deployment lineage. Neither
  upstream reference contains `0x664E6`/`0x664E4` or the `31 -> 10` instruction;
  blurbdust's semantic egg is different and already disproved on `4512000`.
  Therefore the deployment architecture can be attributed to the same community
  lineage while the fixed `4512000` semantic target must be treated as a
  separate private-tree input. Exact line-level FACI authorship is not recoverable.
- **Historical-rationale bound:** Lochuan's first report commit on 2026-07-20
  already labels the `0x66374/0x674A8` NvM cone as SecOC MAC
  scheduling/generation and maps objects 5/6 to likely `0x131/0x2E4`; the
  2026-07-24 edit leaves those labels intact. This repository independently
  corrected that exact cone on 2026-07-25 (`8cfd55d...`) to ordinary checkpoint
  `NvM_WriteBlock` persistence with no CMAC operation. Lochuan's Aug-17 public
  patch repo then begins as a migration of an existing reviewed fixed patch,
  with `0x664E6` first appearing in `0f0c3ef...` under the commit message
  `migrate reviewed eps patch primitives`. The July report never names
  `0x66446/0x664E4/0x664E6` or the `31 -> 10` branch, so the private-tree target
  derivation itself remains missing. The older misclassification is a strong
  candidate origin, not direct proof of why that exact byte was selected.
- **Rejected alternate explanation:** the F7/`BAENA` persistent authorization
  state does have a 30-worker-invocation countdown, but its marker is consumed
  only by the proprietary SID-`0xBA` operation gateway and has no recovered edge
  into SecOC Gate 2.
- **Canonical:** [FINDINGS.md](FINDINGS.md) SECOC-050;
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md) §9.7;
  `tests/verify_lochuan_patch_semantics.py`;
  `external-references.lock.json`.

### CORR-067 — `0x1426` is a zero-trip clear-shaped loop, not an XCP-window startup clear

- **Wrong:** COM-005 and `xcp-command-dispatch.md` described `0x1426` as a
  startup clear of the `FEBF7C00..` XCP/shadow window.
- **Right:** `0x1426` loads `FEBF7C00` as the candidate start, while `0x1432`
  loads `FEBE7000` as the endpoint. The loop uses `cmp endpoint,start` followed
  by the same unsigned-lower `bc` form used by the real copy/clear loops. Since
  `FEBF7C00 > FEBE7000`, control does not enter the `0x142E st.w r0,[ep]` body.
  The effective reset-time upper-LocalRAM clear begins separately at `0x143C`
  with `FEBE8000` and runs to the `FEC00000` boundary.
- **Impact:** this correction does not make the XCP write window persist across
  application initialization: `FUN_0006263E` still overwrites
  `FEBF7C00..FEBFF9EF` from CodeFlash `0x10000..0x17DEF`. It does clarify the
  exact reset/lifetime model used by the ephemeral SecOC investigation.
- **Canonical:** [../communications/xcp-command-dispatch.md](../communications/xcp-command-dispatch.md);
  [../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md);
  `tests/verify_ephemeral_secoc_bypass.py`.

### CORR-068 — a post-init stock callback is not required for ephemeral residency

- **Prior boundary:** ARCH-013/SECOC-060 correctly found no stock callback,
  exception pointer, scheduler slot, or request-derived function pointer that
  survives application startup and then transfers control into retained
  `FEBF0000..FEBF0307`. The initial architecture therefore treated a new
  post-initialization control-transfer primitive as the remaining blocker.
- **Right:** that negative remains true for **stock re-entry**, but it is not an
  end-to-end architectural blocker. `application_cpu_context_init @ 0x70524`
  returns through `lp` after installing application `EBASE/INTBP/GP/TP/SP`; the
  remainder of stock startup is 21 consecutive `jarl disp22` calls plus final
  init and `ei`; and `application_foreground_cyclic_loop @ 0x64FCC` is a small
  top-level cooperative scheduler. A boot-context RAM payload can reproduce
  those stock transitions and remain the foreground scheduler owner instead of
  ever entering `0x64FCC`.
- **SecOC consequence:** `FUN_65750` provides a natural bridge boundary. The RAM
  scheduler can snapshot a newly queued marked `0x2E4`/`0x131` secured record,
  run stock communication/SecOC verification and cleanup, then conditionally
  call stock `application_com_rx_indication @ 0x7C640` before the later
  COM/system-mode/control task. No stock callback into RAM is needed.
- **Constructibility:** the pinned RH850 build is 704 bytes with zero
  relocations, fitting the verified 776-byte retained application-RWX pocket
  with 72 bytes headroom.
- **Evidence boundary:** this corrects the *architectural conclusion*, not the
  earlier callback-negative firmware facts. The scheduler bridge remains
  unobserved on hardware.
- **Canonical:** [../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md);
  [FINDINGS.md](FINDINGS.md) ARCH-014 / SECOC-061;
  `tests/verify_ephemeral_runtime.py`;
  `exploit/ephemeral_runtime/audited_build.json`.

### CORR-069 — a matching CUW/payload is not a Sienna bootstrap dependency

- **Prior boundary:** the ephemeral-runtime plan treated an absent matching
  `8965B4512000` CUW/factory payload as the remaining artifact needed before one
  legitimate authenticated `0x10F0` could unlock MEM-SAFE-001.
- **Right:** the repository already contains two pinned public 4 KiB encrypted
  payload fixtures that are accepted by this exact Sienna bootloader gate.
  `tests/verify_payload_gate.py` decrypts them with the recovered construction
  using tester-controlled `DID 0x0201 = 00*16` and `0x0202 = 00*16`, then proves
  callback `FEBF0FD0→FEBF0000`, the embedded CRC descriptor, CRC32 residue,
  CMAC, and exact AES-CBC round trip. The shared RAM-exec host already writes
  those zero DID values.
- **SecurityAccess distinction:** bootloader SecurityAccess remains mandatory and
  uses the separately recovered SEC-BOOT-002/003 secret. Replaying the already
  encrypted fixture does not require knowing `PAYLOAD_BUILD_SECRET` and does not
  require the missing CUW credential pair.
- **Scope:** the deterministic byte-for-byte proof for the repository's pinned
  fixture is specific to Sienna `8965B4512000`. This does **not** make the
  authenticated-RAM bootstrap Sienna-only: SECOC-024/028 already carry
  external-source evidence for the same SA/DID/download/routine and public
  payload family across multiple B4/F3/F4 EPS calibrations. Preserve those
  evidence grades separately; do not silently upgrade external operation reports
  to local cryptographic verification of the exact Sienna fixture bytes.
- **Canonical:** [../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md) §8;
  [FINDINGS.md](FINDINGS.md) SECOC-062;
  `tests/verify_payload_gate.py`;
  `exploit/ephemeral_runtime/build_substitution_plan.py`.

### CORR-070 — the albinoelephant 2023-Corolla firmware is no longer calibration-unknown

- **Obsolete boundary:** the route/DataFlash-era documentation described the
  reported 2023-US-Corolla specimen as having unknown exact EPS identity and no
  CodeFlash artifact.
- **New evidence:** the contributor's 2026-08-18 memory corpus contains a
  2 MiB CodeFlash range dump whose upper 1 MiB is entirely `0xFF`; the first
  1 MiB is a valid RH850/P1M-E CodeFlash image with SHA-256
  `0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f`.
  Its boot-info identifies `R7F701383`; the ECU serial is
  `8965012N50A05G310920`; its live-ID blocks are `8965H1202000` and
  `8A3111202000`.
- **Important non-join:** the same image contains `8965F1208000` at
  `0x20860`, but that is a table entry, not the unit's primary live-ID block.
  It must not be used to identify this artifact as Span's distinct
  `8965F1208000` Corolla.
- **Remaining boundary:** there is still no retained direct UDS `F181`
  transcript or stock `carFw` route inventory. The public route remains forced
  `TOYOTA_COROLLA_TSS2`, so the route-to-image/model-year join is contributor
  attribution rather than route-contained identity.

**Later supersession:** CORR-118 preserves CORR-070's acquisition/CodeFlash
closure but supersedes its identity interpretation and missing-F181 boundary: direct
same-car telescope F181 is `8965F1208000 / 8A3111202000`, while
`8965H1202000` is DID `0x2032`'s separate one-record identity.

Checked by `tests/verify_albinoelephant_corolla_codeflash.py`; canonical report:
[`../variants/corolla-2023-us-public-route.md`](../variants/corolla-2023-us-public-route.md).

### CORR-071 — the first runtime target resolver overfit Sienna's queue layout and CAN-ID order

- **Wrong implementation assumption:** the initial cross-calibration runtime
  manifest builder recognized one exact Sienna queue-helper byte sequence and
  then searched raw CodeFlash for the exact six-record ID order
  `00F/2E4/131/132/090/0D7`. This made Sienna's *configuration* part of the
  supposedly calibration-independent discovery signature.
- **Disproving image:** fresh `8965H1202000` analysis recovered the same
  startup/foreground/SecOC architecture and a unique Gate-2, but the generated
  queue helper uses a slightly different compiler layout and queue 1 contains
  exactly three records: `00F/D7/B6`. The old builder therefore failed with
  `expected one raw SecOC-queue-storage-helper candidate, found 0` even though
  the target architecture was resolvable.
- **Corrected contract:** the builder now derives GP and TP from application
  context setup; recognizes the queue-1 output contract rather than one exact
  instruction schedule; recovers descriptor/head/raw bases and record count;
  derives the record-table base from Gate-2's own TP-relative `index*0x50`
  access; and validates each generated record structurally. `0x2E4/0x131` are
  checked only afterward as steering-bridge capabilities.
- **Fail-closed result:** a target with a valid SecOC queue but no steering
  records now returns `semantic-resolved-steering-unsupported`. It does not
  inherit Sienna records or RAM geometry and is not runtime-build-ready.
- **Related parser fix:** software-ID extraction now requires alphanumeric token
  boundaries; the old regex incorrectly accepted `8965012N50A0`, the first 12
  characters of the longer ECU serial, as a software ID.

The generalized implementation still reproduces Sienna's exact queue geometry
and audited runtime builds. The tracked H image is the permanent foreign
regression. Checked by `tests/verify_ephemeral_runtime_resolver.py` and
`tests/verify_albinoelephant_corolla_codeflash.py`; canonical tooling report:
[`../tooling/ephemeral-runtime-semantic-resolver.md`](../tooling/ephemeral-runtime-semantic-resolver.md).

### CORR-072 — `ELM param 1 + bus 1` is a direct diagnostic route, not a full Toyota-B repin equivalent

- **Earlier wording:** the Panda routing analysis called `SAFETY_ELM327` parameter
  1 plus logical bus 1 a "software-equivalence candidate" for the reported
  Toyota-B CAN0/CAN1 physical repin.
- **Missing hardware dimension:** official comma `Harness_Box.pdf` defines
  `CAN0 = CAR`, `CAN1 = RADAR`, `CAN2 = CAMERA`, `CAN3 = COMMA POWER` and places
  the solid-state intercept relay specifically between CAN0 and CAN2. Official
  `Toyota_B_Harness.pdf` puts CAN2+CAN1 on the camera side and CAN0+CAN1 on the
  car side. The pinned field report that the relevant network "ends up on bus 1
  instead of bus 0/2" therefore describes a real network-to-relay assignment
  mismatch, not merely a Panda logical-bus naming mismatch.
- **Corrected split:** `param=1,bus=1` attaches Panda FDCAN2 directly to the
  stock harness CAN1 wires and is the correct static **direct-diagnostic-route**
  candidate. It does not move that vehicle network onto the CAN0/CAN2 split,
  insert the intercept relay around it, or make generic 0↔2 forwarding represent
  its two sides. A physical repin/corrected adapter may therefore still be
  required for ordinary openpilot interception even if direct diagnostics can
  avoid it.
- **Foreign firmware closure:** exact `8965H1202000` CodeFlash independently
  eliminates an EPS application→boot bus switch. Application and boot use RSCFD
  channel 1; boot retains `0x7A1/0x777 -> 0x7A9`; the application RSCFD
  register/config tables transfer exactly; boot initialization is byte-identical
  and the core CAN/CanIf region differs only in three relocation bytes. Its
  PROGRAMMING session also transfers the asynchronous reset handoff, so a
  `10 02` timeout alone is not a rejection discriminator.
- **Remaining boundary:** why the indirect OBD route fails to survive or observe
  the transition is still outside the EPS evidence set. Gateway forwarding,
  response timing, ACK/bus-off, and wake/topology remain candidates; none is
  promoted without gateway firmware or a dual-segment transition capture.

Checked by `tests/verify_toyota_b_programming_topology.py`,
`tests/verify_toyota_eps_bus_probe.py`, and optional
`tests/verify_external_corroboration.py`. Canonical report:
[`../tooling/panda-toyota-routing.md`](../tooling/panda-toyota-routing.md).

### CORR-073 — absence of plain `0x7F7/0x7F8` literals does not mean H lost the XCP-shaped CAN route

- **Wrong first-pass inference:** `8965H1202000` contains no plain little-endian
  `0x000007F7` / `0x000007F8` application literals, so the Sienna XCP-shaped
  command family may have survived without its physical CAN ingress.
- **Right:** H stores the same standard IDs in its target-specific packed
  descriptor representation:
  `0x9FDC0002 = 0x80000000 | (0x7F7 << 18) | 2` and
  `0x9FE00002 = 0x80000000 | (0x7F8 << 18) | 2`. Descriptor references lead to
  the H receive callback, and the generic opcode map, callback family, LocalRAM
  envelope, 32-KiB shadow, and target-native read/write semantics independently
  recover the same command architecture.
- **Tooling fix:** `tools/analyze_rh850_codeflash_structure.py` now reports both
  plain-u32 and packed-standard-ID representations. A synthetic packed fixture
  prevents this encoding change from becoming another route false negative.
- **Boundary:** descriptor encoding equivalence does not make the H LocalRAM
  exclusion ranges identical; those were recovered separately and differ from
  Sienna.

Checked by `tests/verify_rh850_codeflash_structure_scanner.py` and
`tests/verify_albinoelephant_corolla_codeflash.py`. Canonical report:
[`../variants/corolla-2023-us-public-route.md`](../variants/corolla-2023-us-public-route.md) §7.7.

### CORR-074 — foreign Ghidra projects must recover target GP/TP; canonical Sienna context is not portable

- **Unsafe workflow:** a disposable foreign import could inherit the canonical
  device-profile GP/TP context. H happens to retain application GP
  `0xFEBEB800`, which made many GP-relative results look credible, but its
  application TP is `0x23D6C`, not Sienna `0x23EE4`; boot TP likewise moves
  `0x869C -> 0x867C`. TP-relative generated-table references could therefore be
  decoded against the wrong absolute address even when nearby pseudocode looked
  plausible.
- **Right:** recover the target context from the firmware's own repeated startup
  idiom `mov immediate,gp` followed by `mov immediate,tp`, apply it before
  foreign semantic analysis, and independently require the raw-machine resolver
  to agree. H recovers boot `FEBF9800/867C` and application
  `FEBEB800/23D6C`; Sienna independently recovers `FEBF9800/869C` and
  `FEBEB800/23EE4`.
- **Tooling fix:** `ApplyRecoveredGpTpContext.java` is now the first post-import
  pass in `tools/resolve_ephemeral_runtime_image.sh`. It deliberately does not
  select the most common write to `tp`, because RH850 also uses that register as
  ordinary scratch state. `ApplyVariantGpTpContext.java` remains an explicit
  exact-image override for review/debugging.
- **Consequence:** corrected H TP resolves the generated COM layout exactly:
  274 signals ending at the 45-entry PDU table, which in turn exposes the real
  `2E4/131 -> 0B6` receive-generation change and `260/262 -> 030` transmit
  consolidation. Existing H GP-relative steering/dataflow conclusions remain
  valid because application GP did not change.

The one-command H resolver reproduces the tracked semantic manifest after this
fix (apart from the caller-selected output-path string). Canonical reports:
[`../tooling/ephemeral-runtime-semantic-resolver.md`](../tooling/ephemeral-runtime-semantic-resolver.md)
and [`../variants/corolla-2023-us-public-route.md`](../variants/corolla-2023-us-public-route.md) §7.9.

### CORR-105 — H `FEBEAE20` is not the retained torque-clamp input

- **Earlier provisional transfer:** the first H steering pass followed Sienna's
  `2E4` staging geometry far enough to identify H `FEBE6D7A -> FEBEF156 ->
  FEBEAE20` and treated the nearby transferred clamp/rate stages as part of the
  same command chain.
- **Correct target-native result:** H `0xC91B6` reads **`FEBEAE12`**, not
  `FEBEAE20`. `FEBEAE12` comes from `FEBEF166`; the complete recovered direct
  writer set for that staging word is H `0x5262C` and `0x5389C`, and both write
  zero. Fixed helper `0xCF12A(...,0x100,100,...)` preserves zero. The separate
  `FEBEAE20` path is fed by H-internal controller state `FEBE6D7A` and consumed
  by `0xC80C4` as a threshold/plausibility predicate.
- **Consequence:** the Sienna external-torque clamp branch is retained as
  framework code but is zero-fed in this H calibration under the direct-writer
  evidence. This does not imply the entire EPS motor/assist system is inactive.
- **Canonical:**
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  §7.11; `tests/verify_corolla_8965H1202000_fd_control.py`.

### CORR-106 — H `0xCEDAE` is 534 bytes, not 533

- **Earlier provisional count:** the first target-native steering pass described
  H `0xCEDAE` as a 533-byte supervisor body.
- **Correct:** the exact Ghidra/raw function boundary is `0x216` bytes = **534
  bytes**. The new complete supervisor-stage ledger binds that body to 123 direct
  stage calls.
- **Consequence:** semantic conclusions from the earlier pass are unchanged;
  this corrects the body-size denominator before it becomes a cross-variant
  invariant.
- **Canonical:**
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  §7.12; `tests/verify_corolla_8965H1202000_steering_supervisor.py`.

### CORR-075 — H `00F/D7/B6` do not select three independent SecOC keys

- **Earlier shorthand:** remaining H work referred to the "three H SecOC runtime
  keys," using the three configured authentication profiles as if each implied a
  separate key.
- **Correct:** all three H queue records carry SecOC crypto-config ID `0` and
  CryptoIf job handle `0`. Config 0 is `{type=1, selector=4}`. The recovered
  CryptoIf/command-7 path copies selector `4` into the ICU request and writes
  `(4 << 16) | 7` to `ICUSCMD`. The application therefore selects **one shared
  protected ICU-S slot 4** for `00F/D7/B6`.
- **Boundary:** this identifies the selected protected slot, not the raw AES key
  value or undocumented ICU-S-internal storage/derivation. DataFlash raw-key
  negatives retain their capture-epoch caveat.
- **Canonical:**
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  §7.13; `tests/verify_corolla_8965H1202000_secoc_key_provenance.py`.


### CORR-076 — Techstream monitor 402 is an internal commanded-torque observable, not intrinsically the external `0x2E4` field

- **Earlier Sienna-only reading:** TMS-017 accepted `EMPS_P5` monitor 402
  `Command Value Torque` as corroboration for the authenticated `0x2E4` steering
  command domain. Its stated boundary already avoided claiming a direct COM-cell
  read, but the surrounding comparison could still be read as if monitor 402
  semantically named that wire field.
- **Foreign-image discriminator:** tracked Corolla `8965H1202000` has no
  configured SecOC or normal-COM `0x2E4/0x131`, yet Techstream's recovered
  primary Data ID for monitor 402 is `0x1C02`, which H implements as live RDBI
  callback `0x495A0`. H-native dataflow traces the diagnostic source through
  `FEBE65F2 <- FEBEE40A <- FEBEAC56 <- FEBEC3D2 <- FEBEC3C0`; active steering
  pipeline `0xCE974` executes the upstream `CD55A -> CD5DC -> CE928` synthesis.
- **Correct interpretation:** monitor 402 labels an **internal EPS command-value
  torque observable**. On Sienna, authenticated `0x2E4` is one recovered upstream
  external command source; that source association is calibration-specific and
  must not be transferred to H or another variant without independent ingress
  evidence.
- **Consequence:** H now has an exact live discriminator for stock-LTA work: read
  DID `0x1C02` together with commanded q/d-current DIDs `0x1152/0x1154` and
  internal d/q/PWM state instead of searching blindly for a relocated 16-bit CAN
  torque field.
- **Canonical:**
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  §7.34; `tests/verify_corolla_8965H1202000_techstream_correlations.py`.

### CORR-077 — H's internal Command Value Torque reaches the closed-loop Q-current controller

- **Earlier boundary:** the firmware-only steering pass correctly found no direct
  Sienna-style external `0x2E4/0x131` transfer into the identified H motor state
  and therefore left command→actuation as a dynamic discriminator.
- **New semantic anchor:** Techstream maps H DIDs `0x1151..0x1156` to actual-Q,
  command-Q, actual-D, command-D, motor angle, and final-Q-current-limit
  observables. `FEBEC3D2` (behind `1C02 Command Value Torque`) reaches
  `FEBE6C1A`; `3322E` publishes that as Techstream-visible base Q command
  `FEBE6BC0` **and** adds it to compensation term `FEBE6BE4` to form
  `FEBE6BB8`. `33160` publishes raw Q feedback aggregate `FEBE6BB4`; `32934`
  computes bounded `6BB8-6BB4`; `32958/329A0` drive the Q-current PI/integrator
  in high-rate motor worker `58226`, which continues into the already-mapped
  transform/PWM pipeline.
- **Correct boundary:** `6BC0` is the OEM diagnostic **base** Q-current command,
  not itself the final PI-error cell. The downstream closed-loop consequence of
  the **general internal H command-value state** is nevertheless statically
  recovered. This does not resurrect a Sienna wire protocol or make `1C02`
  LTA-specific.
- **Canonical:**
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  §7.34; `tests/verify_corolla_8965H1202000_techstream_correlations.py`.

### CORR-079 — CUW routine IDs were displayed in x86 immediate order; standard is not a Sienna-compatible route

- **Earlier wording:** CUW standard routines were written as `F510/00FF/F610`,
  unified routines as `F010/00FF/F110/F210`, and the standard/unified families
  were both described as vocabulary-compatible with the Sienna bootloader.
- **Wire-order correction:** the writer stores 16-bit x86 immediates directly into
  the request buffer. Raw instruction bytes therefore prove the actual wire IDs
  are standard `10F5/FF00/10F6` and unified `10F0/FF00/10F1/10F2`. The earlier
  rendering accidentally read the numeric little-endian immediate as network
  byte order.
- **SecurityAccess correction:** ReproStd sets its request length to transport
  prefix `+2` and emits bare `27 01`. Unified copies 16 bytes from
  `GetECUAuthKey` and sets length to prefix `+0x12`. Sienna
  `uds_security_access_request_seed @ 0x5328` requires exact request length
  `0x12`; other lengths return NRC `0x13`.
- **Correct target join:** Sienna's boot routine table is exactly
  `10F0/10F1/10F2/10F3/FF00`. Standard therefore fails both at request-seed and
  later at `10F5/10F6`; Unified is the sole recovered byte-compatible **family**.
  CORR-081 later closes both of that family's V18 row variants (normal and
  EachArea) as byte-compatible. A matching calibration artifact is still
  required to prove which row Toyota selected and to recover its actual
  credentials/ranges.
- **Canonical:** `tests/verify_techstream_cuw_writer_protocol_grammar.py`;
  `data/generated/techstream_v18/cuw_writer_protocol_grammar.json`;
  [../tooling/techstream.md](../tooling/techstream.md) §5.

### CORR-085 — the outer `.cuw` envelope was described as unrecoverable; its framing is statically pinned

- **Earlier wording (TMS-026/OPEN_QUESTIONS):** the V18 tree contains no
  specimen, so the outer package envelope/extraction framing "cannot be
  fixture-validated locally" and was listed as a package-artifact blocker.
- **Correction:** static analysis of `Cuw.exe` (`0x413BF0`/`0x412F9C`/
  `0x412C98`) recovers the exact outer framing — magic `"\0CALIBRATION\0"`, BE
  type/CRC/total fields, first-member length-prefixed record with per-payload
  CRC32, CRC coverage `[18, declaredTotal)`, and a consumed==total size check.
  `tools/techstream/parse_cuw_container.py` implements it and is validated
  against a synthetic fixture built independently from the grammar.
- **Later closure (TMS-037):** external `T-0087-17.cuw` validates that recovered
  framing byte-for-byte and closes Format Version 4 specifically as
  `cpuImageCount:u8 || member[count]`. The remaining boundary is now narrower:
  other format-tail variants and **matching modern EPS** package values/route
  selection remain specimen-bound. Membership-only enforcement for the other
  table values is still not promoted to per-value meaning.
- **Canonical:** TMS-034/TMS-037;
  `tests/verify_techstream_cuw_calibration_schema.py`;
  `tests/verify_techstream_cuw_legacy.py`;
  [../tooling/techstream.md](../tooling/techstream.md) §5.2.1.

### CORR-084 — the RKS SeedValue producer was called an unresolved upstream edge; it is fully static `Cuw.exe` code

- **Earlier wording (§5.3/TMS-009/TMS-028):** `FUN_0049BCFE` is reached through
  an indirect path "with no recovered direct static caller", leaving who
  produces the 16 bytes unresolved.
- **Correction:** the whole chain is recovered and raw-byte anchored
  (TMS-033): CentralGW P5-CAN SecurityAccess `27 21` response seed → global
  `0x629CDC` → thunk `0x590858` → callback `0x49BCF8` → SeedValue; the portal
  token returns to the ECU as `27 22 || token[256]`.
- **Preserved boundary:** only the live gateway seed value and the server
  signing key remain external.
- **Canonical:** TMS-033; `tests/verify_techstream_rks_client_state.py`;
  [../tooling/techstream.md](../tooling/techstream.md) §5.3.

### CORR-083 — `SecurityProperty2` was not an ASCII character selector; it is hex-decoded key material

- **Earlier wording:** §5.2 discussed `SecurityProperty2=98` as flash metadata
  whose transfer-format semantics remained route-specific, with no decoding
  rule.
- **Correction:** the writer builds `CBytes(const char*)` from the string, i.e.
  ordinary hex decoding (`98` → byte `0x98`), and bit 3 of the first decoded
  byte becomes the Unified RequestDownload `dataFormatIdentifier`
  (`shr dl,3 / and dl,1` in the pinned EachArea step). The public example
  yields `0x98 → 1`.
- **Rule:** never reinterpret the decoded byte as its ASCII character value.
- **Canonical:** TMS-032; `tests/verify_techstream_cuw_writer_protocol_grammar.py`;
  [../tooling/techstream.md](../tooling/techstream.md) §5.2.3.

### CORR-082 — the Unified RequestDownload field order was transposed

- **Earlier wording (§5.2 bullet 2, TMS-026/TMS-029 route reasons):**
  `34 || compressionFlag || areaFlag || 46 || …`, i.e. the `0x46` format byte
  placed after both flag bytes.
- **Correction:** the pinned builders emit `34 || dataFormatIdentifier || 46 ||
  addressSpaceByte || address || length` — `0x46` is byte 2 and the second
  flag (address-space selector) follows it. The corrected order is now the
  single source of truth in `route_verdict` and is regenerated into the
  grammar, matrix, and calibration-schema artifacts.
- **Also corrected:** the "size" operand is the area Length field's raw bytes
  transmitted verbatim, not a parsed integer, and the field is named
  `areaLength`/`length` rather than the ambiguous `areaSize`.
- **Canonical:** TMS-032; `tests/verify_techstream_cuw_writer_protocol_grammar.py`;
  [../tooling/techstream.md](../tooling/techstream.md) §5.2/§5.2.3.

### CORR-081 — the first CUW route census stopped one pass too early; all 196 rows are statically classifiable

- **Earlier boundary:** TMS-029 initially left 30 factory rows as bounded-rejected,
  two MMC rows unresolved, and UnifiedEachArea compatible-but-bounded because
  exact request builders for those families had not been decompiled.
- **Focused closure:** isolated-Ghidra decompilation pins the decisive bodies.
  P5 PowerTrain/Solar and P4/P5 PowerTrain use bare `27 01` with 4-byte seed/key; BodyMicon uses bare
  `27 01` with 6-byte seed/key; SecurityChassisShrink sends
  `27 01 || selector[1] || ECUAuthKey[16]`; MMC uses `27 41/42` and RIDs
  `0301/0304`; CentralGW's paired P4 BodyFlash delegates the legacy raw
  `CCanCommonFlashWriter` protocol. Each has an exact Sienna/H boot-grammar
  mismatch.
- **EachArea correction:** `TCUWCanUnifiedFlashWriterEachArea` is not merely
  vocabulary-compatible. It exactly performs `0203→0201→0202`, per-area
  RequestDownload, block cap `0x0FFF`, RIDs `10F0/FF00/10F1/10F2`, and
  `11 01`; it is byte-compatible. (The RequestDownload field order printed
  here was later transposed-corrected by CORR-082.)
- **Correct census:** all 196 rows are now statically disposed as **194 rejected
  + 2 byte-compatible Unified rows**, with zero unresolved/bounded route rows.
  A matching package is still required to choose between the two compatible
  rows and recover calibration values.
- **Canonical:** `tests/verify_techstream_cuw_writer_protocol_grammar.py`;
  `data/generated/techstream_v18/cuw_writer_protocol_grammar.json`;
  [../tooling/techstream.md](../tooling/techstream.md) §5.2.2.

### CORR-080 — CUW timing ownership and `CANCommunicationSpeedAddress` were over-attributed

- **Earlier wording:** timing parameters were described as configured/owned by `TCUWControlCommPhase.dll`, and `CANCommunicationSpeedAddress` was described as a baud-rate register address.
- **Reference-level correction:** the controller contains the timing-key strings but has no executable absolute reference to `WaitTimeAfterSeedData` or `WaitTimeAfterSeedKey`; the P4/P5 prepare writer references those keys at `0x100019F0` and `0x10001F2F`. The controller's executable references instead cover the retry/IG-off subset such as `PrepareRetryFlag`, `IGOffRetriableFlag`, and `ReceiveTimeoutBeforePrepareRetry`.
- **Bus-speed correction:** `TCUWCanCommonPrepareWriter::GetBusTypeFromCPUImage @ 0x10001630` reads `CANCommunicationSpeedAddress` as a byte location in the downloaded CPU image and maps that byte to a bus/speed mode. It is not a hardware register address.
- **Correct model:** the encoded factory/system parameter tables are shared configuration consumed by different CUW components; ownership must be assigned at actual code references, not string presence.
- **Canonical:** `tests/verify_techstream_cuw_timing_recovery.py`; `data/generated/techstream_v18/cuw_timing_recovery.json`; [../tooling/techstream.md](../tooling/techstream.md) §5.4.

### CORR-078 — the retained H Sienna-homolog LTA branch is direct-write inactive; B6 nonscalar rows are not a recovered hidden command

**Superseded:** CORR-107 corrects the direct-write-inactive portion after the GP-relative writer audit; the D7/B6 nonscalar and shared-`0x025` closures below remain valid.

- **Earlier residual possibilities:** after scalar COM closure, two static escape
  hatches remained: the retained `C9C16 -> CB8BA -> CB9B6` LTA conditioner might
  be fed through an overlooked alias, or B6 configured-but-nonscalar IDs
  `252/253/266/267` might represent an opaque command payload.
- **Direct-writer closure:** `FEBEC17C/C17E/C184` each have exactly one recovered
  direct writer (`C97A8`, zero) plus consumer `C9C16`, and no raw absolute pointer
  literal. Mode source `FEBEC26D` likewise has one zero writer (`CB1C8`) plus two
  readers; cyclic decoder `CBE6E` requires `C26D==1`. Under recovered direct
  writes, decoded mode state never activates and the retained `C2A8` contribution
  stays inactive.
- **D7 companion closure:** protected D7 has configured IDs `240..247` but scalar
  reads only `240/243/246`; the only 16-bit scalar is signal 243 at `FEBE7D82`,
  exact H DID `0x1185`, which `EMPS_P5` names `CAN Vehicle Speed (SP1)`. Its
  nonscalar IDs have no recovered block/group/full-PDU/direct-literal consumer.
- **B6 opaque-surface closure:** B6 is 32 secured bytes with 28-bit MAC + 4-bit
  transmitted freshness, hence 28 authenticated application bytes. Its configured
  IDs are `252..267`; scalar receives are `254..265`. The four remainder IDs are
  absent from every resolved block/group receive (only `89..96,99..102`), every
  full-PDU copy (PDU0 only), and raw absolute pointers to B6 buffer `FEBE4AF4`.
  Sienna `2E4` itself has nonscalar configured IDs `64/65`, proving table
  membership alone is not a hidden-field semantic.
- **Techstream source-domain corroboration:** H communication-monitor row 5 maps
  slot `0x18` / PDU42 / CAN `0x0B6` to Dem event `0x0143`, DTC index 82, packed
  `0xC12987`; exact `EMPS_P5` type-65 data names it **U012987 Lost Communication
  with Brake System Control Module / Missing Message**. D7 and D5 share the same
  DTC. B6 is therefore OEM-classified brake-system traffic rather than an
  Image-Processing-Module-A/camera replacement by inference from its H-only ID.
- **Old camera surface is disabled residue:** H DTC index 93 still contains
  packed `0xC23A87`, exact Techstream **U023A87 Lost Communication with Image
  Processing Module "A" / Missing Message**, but its enable word is zero. Sienna's
  active monitor rows for `2E4/131/191/2FD` all pointed to that DTC; H retains the
  corresponding Dem event records but none appears in its six-row active
  communication-monitor table. The classic direct camera/IPM-A path was therefore
  disabled/removed in this calibration rather than merely renamed B6.
- **Shared-shape adversarial closure:** the only supervisor-reaching fields at
  least 12 bits wide that were excluded from the changed-field denominator are
  CAN `0x025` signals 184 and 186. With signal185 between them, their exact wire
  shape matches pinned Toyota `STEER_ANGLE_SENSOR` (`STEER_ANGLE`, fractional
  nibble, `STEER_RATE`). H independently reconstructs `184*15 + 185` as angle
  (`C2176`) and thresholds absolute signal186 as rate (`CB2E0`), so these are
  sensor measurements rather than a semantically repurposed hidden command.
- **Correct boundary:** this closes the broad recovered static ingress surfaces,
  including unchanged-shape command-sized scalars, not arbitrary computed
  aliases/DMA/hardware writers or a command generated by another ECU. The exact
  H image therefore has **no statically identified stock autonomous-lateral
  ingress** despite retaining downstream steering framework.
- **Canonical:**
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  §7.35; `tests/verify_corolla_8965H1202000_lta_command_provenance.py`.

### CORR-086 — the persistent patcher's FACI pacing/status model inherited obsolete community code

- **Earlier wording/implementation:** `exploit/patcher/flash_backend.c` was
  described as retaining the reviewed P1M-E FACI primitive with full checked
  completion. Its per-halfword program loop actually polled FSTATR bit 21
  (`0x00200000`), and `faci_result()` checked only ready bit 15 plus FASTAT
  command-lock bit 4. This came from the older blurbdust-derived writer lineage.
- **External correction:** refreshed `lochuan/8965B4512000-FW-PATCH` commit
  `390ddb730ca24265c7935989e251f45545909d65` says its comparison against Toyota
  CUW `8965F3... *_erase.pt.bin` requires FSTATR bit 11 (`0x00000800`) for the
  program pacing loop, FSTATR error mask `0x00007040`, FASTAT command-lock bit 4,
  and the manufacturer register identities `FSTATR=FFA10080`, `FASTAT=FFA10010`,
  `FENTRYR=FFA10084`, `FPROTR=FFA10088`. The referenced CUW payload is not
  retained locally, so the byte-identical CUW comparison remains
  **external-source**, not independently verified here.
- **Local firmware cross-check:** the Sienna image independently contradicts the
  old command-lock-only model. `FUN_00077B6A` uses FSTATR bit 15 as ready;
  `FUN_00077BA0/FUN_00077C56` issue Status Clear `0x50` and Forced Stop `0xB3`;
  `FUN_00077D9A` checks low FSTATR status bit `0x400` while feeding program data;
  and `FUN_00077F96` tests mask `0x24068`. These do not prove Lochuan's exact CUW
  mask, but they do prove that the old local abstraction omitted relevant FSTATR
  state.
- **Correct implementation:** the backend now uses the corrected register names,
  bounded bit-11 pacing, `0x7040` FSTATR status checking, FASTAT command-lock,
  Forced Stop/Status Clear recovery, and a checked P/E exit even after partial
  entry failure. `tests/verify_secoc_manifest_patcher.py` pins those source-level
  invariants and rejects the old bit-21 poll.
- **Canonical:** `exploit/patcher/flash_backend.c`;
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md)
  §9.7; `tests/verify_secoc_manifest_patcher.py`.

### CORR-087 — the blurbdust Discord bundle was misclassified as source-less independent tooling

- **Earlier wording/provenance:** the August-2026 import described all three
  `community/blurbdust_secoc_flash_patcher/` files as Discord attachments with
  "no canonical git source" and called the bundle an independently developed
  implementation that independently corroborated the I-CAN-hack authenticated
  RAM-exec bootstrap.
- **Public lineage:** `blurbdust/secoc` is a public fork of
  `I-CAN-hack/secoc`; GitHub records its creation on 2026-04-28. Blurbdust's
  `dbfd991bc817deca0c5c94e2fb5171d1142682c1` added `flash_patcher.py` and
  `shellcode/main_flash_patch.c`, followed by `846866d...` and pinned
  `47d2824...`. The retained community `main.c` is byte-identical to public
  `shellcode/main_flash_patch.c @ 47d2824`. The retained `flash_patcher.py`
  differs only in the two `decode_frame` `struct.unpack` endian format strings
  (`<I` in the Discord attachment, `>I` in public Git). Therefore the inherited
  SA/DID/download/routine-control bootstrap is same-lineage corroboration, not
  independent evidence.
- **What remains source-less:** `decrypt.T-0035-22.py` does not occur anywhere
  in the public `blurbdust/secoc` reachable history. Its behavior and filename
  do, however, match blurbdust's Discord message `1496150355224952995`
  (2026-04-21 14:07:21 UTC), where he said he had a TechInfo `.cuw` flash-driver
  extractor that computes `0x201` and `0x202`. No April attachment hash survives,
  so the retained August file is strongly consistent with that private tool but
  cannot be proved byte-identical to it.
- **Provenance consequence:** the exact F340 target/new-UDS plumbing is older
  than blurbdust's writer: pinned I-CAN-hack `tundra @ b80d9104...` (2025-07-13)
  already carries the `8965F3401200/8965F3402200` record, CPU0 DID-`0x0203`
  offset, and `45 01` routine grammar later generalized by blurbdust. Seven days
  after blurbdust's 2026-04-21 CUW-extractor statement, his first public commit
  adds the persistent writer and carries nearly the full raw OEM-shaped FACI
  command sequence. Its shifted register names,
  wrong bit-21 pacing, and incomplete status recovery prevent claiming a direct
  source translation. The evidence supports a **plausible CUW-informed writer
  lineage**, not proven line-level derivation; inherited target identity is not
  counted as independent provenance evidence. Exact proof still requires the
  original CUW/plaintext Toyota `*_erase.pt.bin`.
- **Canonical:** [../../community/README.md](../../community/README.md)
  `blurbdust_secoc_flash_patcher` provenance section;
  [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md)
  §1.7; `tests/verify_community_tooling.py`; optional
  `tests/verify_external_corroboration.py`.

### CORR-088 — normal PROGRAMMING replay clears the initializer delay; it does not disprove the 10-second bad-key backoff

- **Bad intermediate interpretation:** the first Calvin `dump` archaeology pass
  treated successful SecurityAccess roughly one second after PROGRAMMING as a
  contradiction of the firmware's 10-second delay and withdrew the wall-clock
  conversion. That merged two distinct delay lifecycles.
- **Anti-bruteforce path:** `uds_security_access_send_key @ 0x53F2` permits one
  bad key (NRC `0x35`), then the second consecutive mismatch stores
  `200000000`, records the current timer, sets `FEBF2B56`, clears the attempt
  counter, and returns NRC `0x36`. `27 01` returns NRC `0x37` while that flag is
  active; `0x5584` clears it only after the counter delta exceeds the duration.
- **Clock proof:** `FUN_00001D24 @ 0x1D24` reads `TAUJ1CNT0` at `0xFFE51010`.
  `FUN_00001C60` programs `TAUJ1TPS=0xFFF2` (`PRS0=2`, CK0=`PCLK/4`) and
  `TAUJ1CMOR0=0x0156` (CK0 count clock). The retained P1M-E datasheet places
  this peripheral/P-Bus domain at 80 MHz, so TAUJ1 channel 0 counts at 20 MHz.
  Thus `200000000 / 20000000 = 10` seconds. The generic `0x1D2C` scheduler's
  `delay * 20000` arithmetic is consistent with 20,000 ticks/ms.
- **Separate initializer path:** `FUN_000055AA` also arms the same delay while
  boot diagnostics initialize. The normal application-to-PROGRAMMING retained
  handoff at CodeFlash `0x31914` is `{kind=0, diagnostic_id=0x7A1,
  requested_session=2}`. Its boot replay executes `0x6504 -> 0x5148 -> 0x562A`;
  `0x562A` explicitly writes `FEBF2B56=0` before the synthetic bootloader
  `10 02`.
- **Why Calvin does not contradict it:** the range-dump ladder reaches
  SecurityAccess about one second after the normal PROGRAMMING handoff. Those
  successes are consistent with, and externally corroborate, the explicit
  handoff-clear path. They do not exercise the two-bad-key backoff.
- **Correct disposition:** the 10-second anti-bruteforce delay is verified. Do
  not impose a fixed ten-second sleep after every normal PROGRAMMING transition;
  request SecurityAccess normally. If NRC `0x37` is actually returned, respect
  the active 10-second backoff. Hard-reset/failure lifecycles that do not replay
  the normal retained handoff remain distinct from this ordinary path.
- **Canonical:** [../diagnostics/bootloader.md](../diagnostics/bootloader.md) §2.1;
  [../security/ephemeral-secoc-bypass.md](../security/ephemeral-secoc-bypass.md)
  §19.5; `tests/verify_bootloader_diagnostics.py`;
  `data/p1me_product_memory.json`.

### CORR-089 — degraded boot and normal PROGRAMMING share the runtime, not the entry session

- **Wrong:** SEC-BOOT-011 initially said a failed-validity ECU boots into a
  "fully armed reprogramming runtime" equivalent to the normal retained
  application-to-PROGRAMMING handoff.
- **Right:** both paths arm the same bootloader DCM/flash-worker runtime, but
  `FUN_00006A22 -> FUN_00005086` initializes `uds_current_session=1` first.
  Only retained word0 `0x00` runs `FUN_00006504`; its pre-hook
  `FUN_00005148 -> FUN_0000630C` installs session 3 and clears the initializer
  delay before injecting the retained synthetic `10 02`. Failed-validity
  word0 `0xFF` does not enter that arm and stays in default session 1.
- **Consequence:** `uds_diagnostic_session_control @ 0x614A` rejects a direct
  default-session `10 02` with NRC `0x7E`. The same SID table and SA2 mutation
  gates are present, so the security conclusion does not become an
  unauthenticated programming path; only the entry-state equivalence is
  withdrawn.
- **Canonical:** [../architecture/boot-validity-and-flash-lifecycle.md](../architecture/boot-validity-and-flash-lifecycle.md)
  §4.1; `tests/verify_bootloader_diagnostics.py`.

### CORR-090 — SecOC limits are per-queued-PDU / CryptoIf retry budgets, not persistent wrong-MAC caps

- **Wrong:** SECOC-068 initially described `FEBE550E` as a one-time per-profile
  wrong-MAC attempt cap with no runtime reset, described `FEBE550C/+0x2E` as a
  second authentication-attempt cap, and grouped global callbacks
  `6911C/69116/691EA` together as the ordinary wrong-MAC notification set.
- **Right:** `FUN_0008E382` uses `FEBE550E` against record `+0x10` as a retry
  budget for the current queued PDU. For ordinary profiles `+0x10=1`, so one
  failed verification may be retried once. When a fresh PDU enters state
  `0xD2`, `FUN_0008E166` transitions it to `0xC3` and explicitly zeroes both
  `FEBE550C` and `FEBE550E`; every newly admitted frame starts fresh.
  `FUN_0008E426` separately uses `FEBE550C` against `+0x2E=2` only when
  `secoc_submit_cmac_verify()` returns result `2`, making it a CryptoIf-submit
  retry budget rather than another wrong-MAC limit.
- **Callback correction:** ordinary mismatch status uses global
  `0x25940->0x6911C`. Global `0x25944->0x69116` is reached separately for
  freshness callback result `0x24`. Generic cap-exceeded failure
  `FUN_0008E30A` reaches `0x6911C`, the per-profile `+0x4C` callback
  (`0x69182` for all six records), and global `0x25948->0x691EA`.
- **Security consequence:** the old mechanism description was wrong, but the
  MAC28 conclusion survives for a stronger reason: distinct newly received
  guesses are not throttled across frames because admission resets the retry
  counters.
- **Canonical:** [../security/secoc/application-chain.md](../security/secoc/application-chain.md)
  §5.7; `tests/verify_findings.py`; `tests/verify_secoc_acceptance_gate.py`.

### CORR-091 — NeoNK AES-256 result stands; the prior PKCS#7-gate description did not

- **Wrong:** the first NeoNK write-up called `0x10023F26` a "PKCS#7 gate".
- **Right:** `0x10023F26` only enforces ciphertext length divisible by 16 before
  decryption. The wrapper still `strlen`s the exact 32-byte
  `bCVaAQnA3fNdDgdls2Cjar5er8iwP4Xz` literal, feeds length 32 to the
  16/24/32-byte key-schedule dispatcher, and therefore selects AES-256. Its
  block loop calls the AES primitive once per 16-byte block, so ECB composition
  is unchanged.
- **Tail handling:** optional trimming at `0x10024001` reads only the final
  plaintext byte as a count, bounds it against total length, and zeroes that
  many trailing bytes. It does not compare every padding byte, so it is not a
  strict PKCS#7 validator.
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §4.5;
  `tests/verify_techstream_crypto_inventory.py`.

### CORR-092 — generic RFP all-FF ID examples do not prove P1M-E blank-ID state

- **Overstatement:** the pre-capture plan initially called all-FF
  `CheckIDAuth 0x30` a P1M-E "blank-ID convention" and elevated it to the first
  authentication probe as though target state were known.
- **Right:** shipped RFP documentation includes an all-FF ID authentication
  example, and retained generic RFP configuration strings include
  `UserID=0xFFFFFFFF`. That is valid evidence for a generic RFP convention, not
  for R7F701381/P1M-E specifically. The analyzed distribution has no specific
  P1M-E device record proving its mask-ROM authentication state.
- **Correct disposition:** an all-FF `CheckIDAuth` remains a reasonable
  hypothesis-grade first probe after read-only fingerprinting. Acceptance or
  rejection must be recorded as target observation; `ValidateICU_S 0x70` and
  `DisableSerialProgramming 0x29` remain deferred until their silicon effects
  are understood.
- **Canonical:** [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) RFP/P1M-E entry;
  [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md).

### CORR-093 — the stock command-5 bank is a fixed-16 CMAC test, not an arbitrary SecOC signer

- **Overstatement:** shorthand such as "full CMAC oracle if slot policy permits"
  and "signing oracle" blurred the stock RID-`0x100F` diagnostic bank together
  with the lower variable-length command-5 API. That wording could be read to
  mean an unauthenticated tester can already request a valid MAC for any
  production SecOC message using unmodified firmware.
- **Right:** mode 1 at `icus_crypto_test_submit @ 0x68B42` passes literal input
  length `0x10`; the tester controls exactly 16 message bytes through CAN
  `0x01C/0x01D`. This image's configured authenticated inputs are 7 bytes for
  sync, 12 bytes for classic `0x2E4/0x131/0x132`, and 36 bytes for FD
  `0x090/0x0D7`. AES-CMAC padding/final-subkey selection depends on message
  length, so a 16-byte CMAC query is not a transformable substitute for the
  12- or 36-byte target CMAC.
- **Lower capability:** `icus_command5_mac_generate_prepare @ 0x87A94` accepts
  byte lengths below `0x51` and supplies `len<<3` to ICU-S, so application-context
  code can request the real 12/36-byte domains. Stock result-copy worker
  `0x87B46` preserves output capacities up to 16.
- **Bounded classic adaptation:** changing `0x68B8A` from
  `20 4E 10 00` (`movea 0x10`) to `20 4E 0C 00` (`movea 0x0C`) makes the
  existing chosen-message path 12 bytes and leaves 12 returned MAC bytes—more
  than enough for MAC28. Combined with the existing observation shim, that is a
  true classic-domain signing experiment *if* live slot 4 accepts command 5.
- **Policy nuance:** standard AUTOSAR SHE makes a MAC-use key eligible for MAC
  generation and verification, and Renesas public P1M ICU-S material lists both
  services. But vendor extensions exist in the ecosystem: Vector documents an
  additional `CMAC USAGE` flag capable of making a MAC key verification-only.
  This does not prove P1M-E has that flag; it reinforces that live slot-4 policy
  must be measured rather than inferred from the base SHE FID alone.
- **Canonical:**
  [../security/secoc/command5-oracle-assessment.md](../security/secoc/command5-oracle-assessment.md);
  `tests/verify_secoc_command5_oracle_assessment.py`; SECOC-069.

### CORR-094 — the programming handoff preserves XCP-window bytes, but its 36-byte state-copy source is fixed

- **Wrong investigation hypotheses:** treating application `10 02` as though it
  necessarily reset/cleared the `FEBF7C00..FEBFFBFF` XCP window, or treating
  the `r6` source consumed by `0x148E` as potentially tester-selected.
- **Right:** application `FUN_00064EC8 @ 0x64EE6` loads literal
  `r6 = 0x31914` immediately before calling `0x9F00`. `0x9F00` enters the boot
  context live, touches no XCP-window byte, clears `MPM`, and calls `0x148E`;
  `0x148E` copies nine fixed CodeFlash dwords into `FEBF2908` and enters
  `0x1398`. The subsequent `0x1338` runtime initializer does not call `0x1404`.
  `0x1404` is reset-startup-only, and its apparent `FEBF7C00` clear remains the
  CORR-067 zero-trip loop. Tester bytes written to the XCP window immediately
  before `10 02` therefore remain resident in boot, but the handoff-copy itself
  is not an arbitrary-write primitive.
- **Impact:** this creates cross-lifecycle code placement/retention, not a
  complete RCE. A separate boot control-transfer primitive is still required.
- **Canonical:**
  [../architecture/boot-validity-and-flash-lifecycle.md](../architecture/boot-validity-and-flash-lifecycle.md) §4.1;
  `tests/verify_xcp_boot_handoff_retention.py`; SEC-BOOT-012.

### CORR-095 — Span direct PROGRAMMING was no longer unmeasured after the corrected 2026-08-21 preflight

- **Stale claim:** VAR-039 and the Span variant record said PROGRAMMING on
  `(bus1,param1)` remained unmeasured because the 2026-08-19 preflight selected
  `(bus1,param0)` by array order.
- **Right:** the corrected 2026-08-21 preflight selected `(bus1,param1)` by
  actual PROGRAMMING reachability, opened PROGRAMMING, received a SecurityAccess
  seed, accepted the key, and completed the requested CodeFlash/DataFlash/RAM
  range dumps. The old timeout remains useful only as evidence about the wrong
  gateway/OBD route.
- **Evidence boundary:** the source ZIP is now tracked byte-for-byte at
  `community/spanconstant/spanconstant_tsk.zip` with SHA-256
  `a5744b4c4627d3e5c20d590bb882d25b9b40c0679cbc3e9660140c7f2ef5262b`;
  the corrected preflight, route record, SecurityAccess log, and normalized
  memory corpus are independently pinned by
  `tests/verify_spanconstant_corolla_codeflash.py`.
- **Canonical:** [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md);
  VAR-039.

### CORR-096 — Span `0x17D80` is not the F181 primary software-ID record

- **Stale ambiguity:** the first Span write-up left the relationship between raw
  `8965H1213000 @ 0x17D80` and live F181 `8965F1208000` unresolved, because all
  three nearby identity strings were visible before the target producer was
  joined.
- **Right:** the byte-identical H/Span F181 producer `FUN_0004a328` emits two
  16-byte records from CodeFlash `0x20860` and `0x17DC0`. On Span those are
  exactly `8965F1208000` and `8A3111213000`. `FUN_0004a2e0` separately reads
  `0x17D80`, so `8965H1213000` belongs to a distinct one-record identity path.
- **Impact:** the live F181 and raw firmware are internally consistent; no
  `F12080`/`H12130` identity contradiction remains.
- **Canonical:** [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md) §3;
  VAR-042; `tests/verify_spanconstant_corolla_equivalence.py`.

### CORR-097 — vehicle-bus `2E4/131/344` observations are not Span EPS SecOC/Rx configuration

- **Wrong implication:** the preliminary Span record listed historically
  observed secured `0x2E4/0x131/0x344` traffic alongside EPS facts in a way that
  could be read as the EPS's configured protected receive set.
- **Right:** direct firmware resolution gives Span the same normal-Rx and SecOC
  configuration as H. Its Gate-2 queue is exactly `0x00F/0x0D7/0x0B6`, and the
  normal-Rx diff explicitly removes Sienna `0x2E4` and `0x131`; neither is a
  Span Gate-2 profile. The persisted 2026-08-21 `can_oracle.ndjson` is empty and
  its READY capture does not provide a same-session protected-frame oracle that
  overrides the static census.
- **Impact:** bus presence proves network traffic, not destination ECU
  acceptance. The Sienna `2E4/131` steering bridge must not be transplanted to
  Span by ID.
- **Canonical:** [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md) §7;
  VAR-043; `tests/verify_spanconstant_corolla_cross_variant.py`.

### CORR-098 — the first Span low-delta pass missed indirect A000 calibration consumers

- **Stale wording:** the initial Span/H comparison said the changed low tables had
  no simple application consumer beyond identity and an `0xA240` numeric false
  positive, leaving `0xA0C0..0xA3C3` as an undifferentiated calibration caveat.
- **Right:** the application reaches the `0xA000` bank indirectly through
  `FUN_00050e6a`, which returns base `0xA000`. A **u16 count 9 at `0x2A974`**
  selects a nine-entry descriptor family at `0x2AB8C`. Fixed-index readers plus explicit staging→live copy/gate paths load
  records 0/2/3 into working calibration state, while `0x42C42 -> 0x42B98`
  directly indexes three changed 256-byte signed motor-rotation-angle correction
  LUTs in record 5. `0x42D28` separately indexes record-6 payload+8, which is a
  256-byte zero table in both specimens.
- **What remains bounded:** this proves active **specimen/unit calibration**
  differences, not a 2023-to-2025 tuning revision. The separate
  `0x10000..0x17DEF` shadow-copy bank is structurally variant-specific but still
  lacks a recovered semantic CPU dereference, and `0x17DF0..0x17DFF` remains an
  opaque post-CRC field.
- **Canonical:**
  [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md) §4.2;
  VAR-045; `tests/verify_spanconstant_low_calibration_delta.py`.

### CORR-099 — `0x17DF0..0x17DFF` is the region-0 AES-CMAC tag, not an opaque field

- **Stale wording:** CORR-098 and the first low-delta report retained the final
  16 changed bytes at `0x17DF0..0x17DFF` as an "opaque post-CRC field" whose
  algorithm was "unresolved".
- **Right:** the boot integrity-region table at `0x8DE0` (3 rows x 28 bytes,
  byte-identical H/Span) defines region 0 as `0x10000..0x17DFF` with its CMAC
  tag address at field +8 = `0x17DF0` and validity marker at +0xC = `0x17E00`.
  `boot_memory_region_get_cmac_tag @0x3376` returns that field;
  `routine_verify_crc_cmac_task @0x591A` -> `payload_cmac_verify_enqueue
  @0x6E9E` -> `payload_cmac_verify_setup @0x7106` initializes the AES-CMAC
  session over `0x10000..0x17DEF` (end = start+len-0x10, tag excluded);
  `payload_cmac_verify_step @0x7154` byte-compares all 16 generated CMAC bytes
  against the stored tag on the final block. The complete 16/16-byte change
  between H and Span is expected cryptographic integrity fallout of the changed
  calibration page, not independent tuning data.
- **Boundary preserved:** the verification role and code path are proven; the
  exact DID 0x201 key material and DID 0x202 IV/build-time inputs that produced
  the factory-stored tag are not recovered from this static image/session, and
  zero-valued DID material used by public RAM fixtures does not reproduce the
  stored tag. The boot payload-build root at `0xBFD8` is present in the image;
  non-reproduction with zero inputs is an input-recovery boundary, not proof of
  key absence. Region 1 (`0x18000..0xFFDFF`, tag `0xFFDF0`) is byte-identical
  between specimens and does not enter this delta; whether its tag slot is
  programmed on this generation is not asserted.
- **Canonical:**
  [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md) §4.2.3;
  VAR-045/VAR-046; `tests/verify_spanconstant_low_calibration_delta.py`.

### CORR-100 — the low-delta semantic boundary is closed: consumers, bank role, record-8 reader, and CMAC KDF recovered

- **Stale wording (four superseded claims):**
  1. The high `0x18000..0x1FDEF` block was described as an inert
     "template/reference-like region" whose factory/default/manufacturing role
     was "not proven".
  2. The `0x10000+` shadow was described as having "no recovered semantic CPU
     dereference beyond the startup/E4 copies and XCP calibration-page
     bookkeeping".
  3. Record 8 was described as having "no recovered fixed-index consumer".
  4. The region-0 CMAC was described only as using a "boot-derived key"; the
     exact KDF and authenticated-message construction had not yet been recovered.
     The historical DID 0x201/0x202 values themselves remain genuinely absent.
- **Right:**
  1. The application contains a **seven-pair high/default + low/vehicle pointer table at `0xB022C`** (every high twin exactly
     `+0x8000` above its low twin). `0x5C032` compares low-page identity
     (`JA112001` @ `0x17DA0`, `8A311` @ `0x17DC0`) against application
     identity (`0x20850`/`0x20870`); the selector chain `0xB5D0A` ->
     `0xB5D12` -> `0xB8D62`/`0xBD56C` fans the one-bit selector to
     `FEBEAC3C`/`FEBEAFE0`. All five retained runtime captures hold both
     selectors `= 1` with compatibility status `0`, so the captured vehicles
     ran the low/vehicle bank. The high block is therefore the **compiled
     fallback/default calibration bank** used on reset/mismatch — an inert
     template it is not.
  2. Semantic CPU consumers of the `0x10000+` low bank are recovered: Bank B
     rows are live vehicle-speed-dependent linear-interpolation maps
     (`0xC6E68`/`0xC6ECE` over selected low base `0x10100`, interpolator
     `0xCE6A2`, axis `FEBEADE8` = conditioned/clamped DID `0x1185` `CAN
     Vehicle Speed (SP1)` via `0xBB22A`/`0xBB362`/`0xB8EEC`), and the
     `0x13E46` u16 feeds `0xB5DBC` -> `B33C` -> `0xC3AC8` as a dual-channel
     plausibility-center coefficient, with retained H/Span `B33C` values
     exactly matching the low-bank formula.
  3. Record 8 is the persistent object returned by **H RDBI DID `0x010B`** ->
     callback `0x4869C` -> `0x6009E(0x208)`, joined at object level to
     Techstream `Output of torque sensor 2` (legacy KWP `TRQ1 Zero Point
     Value`).
  4. The region-0 CMAC construction is fully recovered:
     `K = AES-128-ECB-ENC(PAYLOAD_BUILD_SECRET @0xBFD8, DID0201[16])`
     (derivation at `0x704C`) and
     `tag = AES-CMAC(K, DID0202[16] || CodeFlash[0x10000:0x17DF0])`. Zero
     boot-session inputs deterministically reproduce the retained derived key
     `80d221a05622b4f9d4f287922e6c78d1` but neither stored factory tag.
- **What remains bounded (not reverted):** exact OEM names/units for the
  Bank-B map outputs and the `0x13E46` coefficient; the record-8 inner-u32's
  exact subfield/endianness-presentation/unit (the DDB carries no
  field-level scaling); the historical 16-byte DID0201 SeedKey / DID0202
  Nonce used by the factory/package (volatile inputs absent from the
  retained corpus — a matching Corolla CUW/calibration package or reflash
  transcript would supply them); and XCP page-state
  (`FEBE5DB0/5DB1`) remains separate from the application compatibility
  selector, with no XCP high-page route.
- **Canonical:**
  [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md)
  §4.2.2–§4.2.3; VAR-048;
  `tests/verify_spanconstant_low_calibration_delta.py`;
  `data/generated/corolla_8965F1208000_low_calibration_delta.json`.

### CORR-101 — mechanism-specific keyless closures do not exhaust software-visible static work

- **Overstatement:** after KEYLESS-015..018, the analysis was summarized as if
  further progress necessarily required a new firmware generation,
  undocumented hardware/ROM behavior, runtime-only corruption, or physical
  fault/debug evidence.
- **Right:** those findings close only the mechanisms they actually enumerate.
  They do not prove that every parser, copy sink, state-machine composition,
  indirect-control path, or target-native variant delta has been statically
  reviewed. The exploit-interest ranking is itself explicitly a candidate
  generator rather than an absence proof.
- **Fresh counterexample to the methodology:** reopening the software-only
  search immediately exposed two previously unpinned application surfaces.
  CanTp accepts First-Frame totals up to `0x0FFF`, but DCM independently bounds
  the three receive buffers to 256 bytes and checks every segmented copy
  (KEYLESS-019). The event snapshot formatter `0x54910` / Corolla `0x50038`
  has no in-loop capacity check; its current event-mask configuration keeps the
  reachable two-bank output at 414 bytes on Sienna and 404 bytes on H/F versus
  a 768-byte staging area (KEYLESS-020). The latter is configuration-safe, not
  structurally safe.
- **Reviewed-ledger cleanup:** the three rows that were still explicitly
  `open` (`0x539A8`, `0x58404`, `0x7C7C2`) now have direct bounded-negative
  firmware explanations. Zero `open` rows in that curated ledger remains a
  statement about reviewed rows only, not global static coverage.
- **Canonical:**
  [../security/keyless-exec-surface-assessment.md](../security/keyless-exec-surface-assessment.md)
  §§20.1–20.3; `tests/verify_keyless_application_diagnostic_transport.py`;
  `tests/verify_keyless_application_event_formatter.py`;
  `tests/verify_exploit_interest_reviewed_candidates.py`.

### CORR-102 — the legacy CUW software password was not one generic value with an unknown wire consumer

- **Earlier wording (TMS-037 / T-0087 history):** `79EF38FF` was described as
  the selected legacy software password without distinguishing source versus
  new-image state; `SelectRetryPassword` was known only as a selector mutation,
  the ECU-facing password request was left bounded, and the downstream
  S-record body-coding path was left open.
- **Correction:** the real descriptor's `TargetData` fields encode the three
  **old/source** passwords. `Cuw.exe:0x4B3880` hex-decodes each eight-byte value
  and subtracts output-byte indices `0..7`; the uint-reader path parses the
  resulting ASCII hex as `A5CD46B3`, `AC8C4F0D`, and `727D3713`. The archived
  `79EF38FF` at `0x1FFF00` is instead the **new-image** password selected by
  `GetNewPassword` fallback for `302U1300`.
- **Wire closure:** `CCanCommonFlashWriter::CheckIDWithWaitOfSFs @ 0x45C86C`
  sends exactly five payloads after the common four-byte CAN/J2534 prefix:
  `00`, `00`, `LocationID[7,6,3,2,1,0]`, `LocationID[5,4]`, and the selected
  password in little-endian order. For this package's new password the payloads
  are `00 / 00 / 200701000200 / 0300 / FF38EF79`. This raw CheckID exchange is
  distinct from UDS `27 01/27 02` SecurityAccess. `SelectRetryPassword @
  0x46CAB0` explicitly selects new on true, toggles on false when writer status
  `+0x78 == 7`, and otherwise selects old; the semantic name of status `7` is
  still unclaimed.
- **Body-path closure:** the selected S-record parser/materializer
  (`0x4A9A9C`/`0x4AB2D4`) and CCanFlashWriter sender `0x45C700` copy the
  materialized image bytes into the J2534 transmit path without host-side
  crypto/recode. What `A1DFE103` and the encoded-looking representation mean to
  the ECU remains bounded; an ECU-side decoding algorithm is not inferred.
- **Canonical:** TMS-037; `tests/verify_techstream_cuw_legacy.py`;
  `data/generated/techstream_v18/cuw_t0087_17_specimen.json`;
  [../tooling/techstream.md](../tooling/techstream.md) §4.5.0/§5.2.1;
  [../history/2026-08/T0087_17_CUW_ANALYSIS_2026-08-22.md](../history/2026-08/T0087_17_CUW_ANALYSIS_2026-08-22.md).

### CORR-103 — `VFOREST` is not an RH850 synonym, and its security orchestration is route-specific

- **Earlier shorthand:** Techstream notes labeled `CCanVFORESTFlashWriter` as
  `FOREST/RH850` and summarized VFOREST SecurityAccess as if every VFOREST
  writer necessarily belonged to the separate prepare+flash architecture.
- **Correction from a real package:** external `T-0011-21 - 04C21.cuw` selects
  `CPUType=86 -> VFOREST_2_0M`, `FORESTTypeFlag=1`, route `0P5-CAN86`, and
  `FlagToUseCIDGetterAndFlashWriterDLL=0`. `Cuw.exe` therefore constructs its
  **integrated** VFOREST writer. Shared `CCanFlashWriter::Execute` calls
  `ChangeReprogrammingForECU @ 0x464254` before its direct
  `0x461F42 -> CCanVFORESTFlashWriter::FlashWrite @ 0x587AD4` dispatch, so this
  real route uses the legacy four-byte `27 01/02` SecurityAccess path. The
  dynamic Security-VFOREST family of TMS-010 is a different factory route with
  its own prepare/key-material-transfer architecture.
- **Architecture label:** Toyota's V18 export table explicitly names
  `VFOREST_2_0M` while separately naming several `V850...` CPU types. Third-party
  exact-software/tooling evidence places `89663-04C21 / 304C2100` in the Denso
  Gen2/newGen D76F0xxx 2-MiB ecosystem, but sources disagree on the exact
  D76F0xxx suffix. The CUW itself does not establish an RH850 core, exact MCU
  suffix, or instruction set. `VFOREST` must therefore remain the recovered
  Toyota/Techstream family name unless stronger target-native evidence exists.
- **Canonical:** TMS-038;
  `tests/verify_techstream_cuw_vforest.py`;
  `data/generated/techstream_v18/cuw_t0011_21_04c21_specimen.json`;
  [../tooling/techstream.md](../tooling/techstream.md) §4.5.2;
  [../history/2026-08/T0011_21_04C21_CUW_ANALYSIS_2026-08-23.md](../history/2026-08/T0011_21_04C21_CUW_ANALYSIS_2026-08-23.md).

### CORR-104 — the FRC `.xx` payload is not plaintext, `.datx` is not "decrypted ECU-side", and `IsControlledBySCC` does not select RKS

- **Earlier interim framing (session working notes, never promoted to a
  canonical report):** the FRC `.xx` member was described as "plain Motorola
  S-records / no encryption", the delta `write.datx` as "decrypted ECU-side",
  and `IsControlledBySCC=1` as the gate that "makes the reprogramming state
  machine require the ReprogrammingKey (RKS) workflow".
- **Correction from the packages and the modern unpacked host (TMS-042):**
  only the Motorola S-record **framing** is plaintext — the decoded flash body
  is high-entropy with unknown encoding (global 7.9999977 bits/byte, minimum
  complete 4-KiB window 7.93098, no plaintext island). The `write.datx`
  member is downloaded with RequestDownload DFI `0x21` — Toyota's own P6
  writer names `0x21` the delta-data DFI (`DeltaReproPhase6 → 0x21`,
  `CompressionReproPhase6 → 0x11` by string comparison) — and is a compact
  delta representation consumed ECU-side as its delta input; the exact
  transform is unknown and "decrypted" is not claimed. `IsControlledBySCC` is stored at
  calibration `+0x24` from `[KindOfCal]` and, when set with `IsBlankECU`
  clear, invokes `FUN_100115E0`, which consumes the `VehicleForNA`/
  `VehicleForEUOT` descriptor sections; RKS selection is instead the runtime
  `JudgeReproGWNodeForP4AndP5` probe result.
- **Canonical:** TMS-042;
  `tests/verify_techstream_cuw_frc_corpus.py`;
  `data/generated/techstream_v18/cuw_frc_corpus.json`;
  [../tooling/techstream.md](../tooling/techstream.md) §5.2.4.

### CORR-107 — H has a live B6 target-angle command; direct-symbol/fixed-map census missed GP-relative writers and copies

- **Superseded wording (CORR-078 / VAR-014 / VAR-017 / VAR-036 / COM-008):**
  the retained `C9C16 -> CB8BA -> CB9B6 -> C2A8` branch was described as
  direct-write inactive, and B6 signed16 signal255 was described as staged-only
  with no command-sized H-only wire ingress.
- **Root cause:** the earlier census matched named Ghidra RAM-symbol assignments
  and direct references. H also emits steering-state stores/copies through the
  fixed application GP base `0xFEBEB800` plus constant offsets. Those accesses do
  not necessarily spell the absolute RAM symbols in decompiler text, so the
  representation omitted both live writers and the B6 stage→snapshot alias.
- **Mode/branch correction:** `CC7F8` writes `GP+0xA6D = FEBEC26D` from
  communication-health selectors `0x10/0x18` plus B6 validity `FEBEADB9`.
  `CC2EC -> CAD62` writes replicated magnitude `FEBEC17C/C17E/C184`; B6
  signals262/263 percentage-modulate internal contributor families through
  `CC442/CBFCE`. The retained conditioner is therefore live.
- **B6 fixed-map correction:** generated unpacker `46A10` reads signal255 as
  signed16 from protected FD `0x0B6` B4:B5 into `FEBE7D94`; `5262C` stages it at
  `FEBEF1CC`; and `B8EEC` performs `GP+0x39CC -> GP-0x97E`, exactly
  `FEBEF1CC -> FEBEAE82`. The same fixed map resolves signal254 B3[5:0] through
  `FEBE7D96 -> FEBEF127 -> FEBEADB0`.
- **Target-angle proof:** `C9DB0/C9E54` turn `FEBEAE82` into replicated target
  state. Independently, `CBD7E/CB096` reconstruct the measured steering-angle
  domain from FD `0x025` signals184/185/186. `CA138` applies the same
  `0xB76/0x400` gain to both and forms target-minus-measured error before the
  active controller. This is target-native evidence that B6 signal255 is a
  **target steering-angle command**, not torque and not a staged-only value.
- **Mode/control companion:** `CBE6E` decodes signal254 values `1/4/10/11/19`
  into five mutually exclusive cooperative-control profile flags plus a common
  active flag when communication/validity gates permit. `C9CEA/C9FAE/CB72A/CB900`
  and later helpers select distinct calibration banks from those profile flags;
  `C825A` also treats raw IDs `25/27` as a special state/monitor pair, with only
  `25` in the accepted steering-controller set. Techstream's byte-anchored
  `Target Lateral ID` pattern dictionary now closes the exact numeric labels:
  `1=PCS`, `4=LDA`, `10=Hands Off LTA`, `11=LTA/LCA`, `19=PDA`, while H-special
  `25/27` are `AP/Remote Parking`. This is an exact value-domain join even though
  H itself does not expose the literal wire-field name.
- **Downstream command bridge:** the B6-derived controller contribution reaches
  `C2A8 -> CD3CC` and the general torque composition. Under the recovered normal
  selection/current gates it propagates to DID `0x1C02 Command Value Torque` and
  DID `0x1152 Command Value Current (Q Axis)`. Those DIDs observe the general
  multi-contributor command/current path; they do not rename signal255 itself.
- **What remains negative:** D7's 16-bit scalar is still exact `CAN Vehicle Speed
  (SP1)`; B6/D7 nonscalar block/group/full-PDU escape routes remain negative; the
  only shared command-sized generated-COM fields are target-native `0x025`
  angle/rate sensor state; and the classic active camera/IPM-A
  `2E4/131/191/2FD` monitor family remains removed/disabled.
- **Physical-scale closure:** H `4636A` unpacks FD025 signal184 as signed12 and
  signal185 as signed4. `42676 -> 488A8` carries signal184 unchanged into DID
  `0x1037 Steering Angle`; Techstream P5 physical-data key 3 is byte/code-bound as
  `Mul=15`, `Div=1`, `Offset=0`, signed, one decimal place, unit `deg`, proving
  1.5 deg/count. `B24D0` recombines `15*signal184 + signal185`, while `B23A2`
  divides that value by 3600 for a full revolution, proving signal185 is a signed
  0.1-degree fraction. In the matched controller, target begins at `2*signal255`
  and measured angle is `trunc((15*coarse+fraction)*1787/512)`, so signal255 is
  controller-equivalent to exactly `1024/17870 deg/count` =
  `1.000121519... mrad/count`. The literal OEM B6 engineering-unit name is not
  directly recovered; calling it nominal 1 mrad/count remains an interpretation,
  not a string/name join.
- **Correct boundary:** H/F EPS ingress and controller-equivalent physical scale are
  identified as protected FD `0x0B6` signal255 target angle with signal254
  Target-Lateral request selection. COM-012 now additionally closes the receiver
  liveness/sequence side: PDU42 reloads to seven TAUJ0-CH3 foreground ticks,
  first expiry propagates through slot18 -> `FEBEADB9` and disables `C26D`, and
  signal261 is a modulo-64 rolling sequence counter with effective-gap cap 8.
  Still open: the exact OEM signal255 unit label, sender wall-clock cadence, exact
  secondary-field names and live **SecOC** freshness/key/source behavior. TMS-043
  now closes the module-level FRC/Brake/EPS dependency topology and identifies Corolla
  category 435 exactly as `ABS_P5` / Brake-EPB; the still-open part is the byte-level
  planner→B6 forwarding/transformation and SecOC sender ownership. Arbitrary unrelated computed
  aliases or undocumented hardware/DMA writers remain bounded, but no second
  command-sized path was recovered in the audited surfaces.
- **Canonical:**
  `data/generated/corolla_8965H1202000_b6_target_angle_ingress.json` v4;
  `data/generated/corolla_8965H1202000_b6_receiver_contract.json` v1;
  `data/generated/corolla_8965H1202000_lta_command_provenance.json` v8;
  `tests/verify_corolla_8965H1202000_b6_target_angle_ingress.py`;
  `tests/verify_corolla_8965H1202000_b6_receiver_contract.py`;
  `tests/verify_corolla_8965H1202000_lta_command_provenance.py`;
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
  §§7.11, 7.14, 7.35.

### CORR-108 — SecOC/TSK is not a TSS-generation classifier

- **Wrong model:** the former `data/tss3_eps_variant_matrix.csv` and its
  `tss3-family-comparison.md` orientation put the SecOC/TSK Sienna donor, true-TSS3
  Corolla targets, and empty speculative Camry/RAV4 rows under one "TSS3 EPS"
  umbrella. Even where individual cells were qualified, that schema invited the
  false inference **SecOC/TSK car ⇒ TSS3 car** and blurred security prior art with
  ADAS/control-generation evidence.
- **Right:** TSS/TSS2/TSS3 is the **ADAS/control architecture** axis; SecOC/TSK is
  the **security/authentication** axis. They are independent. All three tracked
  firmware dump families (Sienna `8965B4512000`, Corolla H, Corolla F) are
  SecOC/TSK evidence, but `8965B4512000` now explicitly carries
  `adas_generation=not established by retained evidence; do not infer from SecOC`.
  H/F carry separate TSS3 vehicle/P5 control-generation evidence. The external
  `8965B4514000` row retains its reported-TSS3 label as an external claim that is
  explicitly independent of its SecOC evidence.
- **Data-model fix:** the matrix is renamed
  `data/toyota_eps_variant_matrix.csv`, adds separate `adas_generation` and
  `security_architecture` columns, and removes the all-unknown Camry/RAV4
  placeholders. Unacquired family targets remain in the open-question/acquisition
  queue instead of masquerading as populated evidence rows.
- **Porting consequence:** a TSS3 opendbc platform must not acquire the `SECOC`
  flag merely because it is TSS3, and a SecOC-capable Sienna command path must not
  be treated as a TSS3 wire/API template. Reuse security plumbing only where the
  target independently proves SecOC; recover command/state/ownership by TSS
  generation from target-native bytes/captures.
- **Canonical:** [../variants/toyota-eps-variant-comparison.md](../variants/toyota-eps-variant-comparison.md);
  [../architecture/toyota-openpilot-porting-contract.md](../architecture/toyota-openpilot-porting-contract.md);
  `tests/verify_toyota_eps_variant_matrix.py`; COM-013.


### CORR-109 — eleven H `0x030` fields were not default-only; GP-relative writers carry live torque and status

- **Superseded wording:** the first H FD `0x030` producer census classified eleven
  packed signals (`0,1,10,14,16,17,18,27,28,31,34`) as
  `default-init-only-direct-writer-census` because no non-default named-symbol
  assignment was found. The state-bridge roadmap consequently treated `0x4A3` as
  the only usable H/F driver-torque carrier and left most `0x030` telemetry for a
  later generic decode.
- **Root cause:** the negative used a direct textual RAM-symbol census. H
  `0x47188` and `0x47430` write these staging cells as constant offsets from the
  fixed application GP base `0xFEBEB800`. As in CORR-107, those stores do not spell
  the absolute RAM symbol in decompiler text, so the representation produced false
  negatives.
- **Exact correction:** `0x47188` writes signals `0/1/10/14/16/17/27/28/31/34`;
  `0x47430` writes signal `18`. The FD-control artifact now carries a dedicated
  `runtime-produced-gp-relative` class and exact-image-bound positive evidence for
  all eleven. Across directly packed signal IDs `0..34`, **zero** fields remain in
  the former default-init-only class. Four explicitly runtime-zero fields and the
  computed B7 additive field remain separately classified.
- **Driver-torque consequence:** signals `0/10/31` use the same native
  `FEBE6554` source as Techstream DID `0x1035 Steering Wheel Torque` and `0x4A3`
  B5. Firmware arithmetic plus the Techstream conversion closes
  `torque_Nm = signed(B8)*0.1 + signed4(B17[3:0])*0.01`; B0 is a separate
  truncation-toward-zero 0.1-N·m view. Span's tracked moving rlog exercises 6,000
  frames, 536 reconstructed values, and -8.23..+2.85 N·m; the two coarse views
  differ only by the expected `-1/0/+1` rounding count. Driver torque is therefore
  a **live `0x030` state input**, not dependent on observing `0x4A3`.
- **Other corrected fields:** signal34 is a runtime signed16 derivative of the
  DID `0x1151 Motor Actual Current (Q Axis)` source, but its separate packet
  calibration is not promoted to an engineering scale. The remaining corrected
  bits are positively runtime-produced while their literal OEM meanings stay
  bounded.
- **Boundary:** this fixes eleven specific GP-relative false negatives. It does not
  turn the old direct-reference census into a proof against arbitrary computed
  aliases, DMA, or peripheral writers. It also does not justify a
  temporary/permanent steering-fault mapping or a production driver-override
  threshold.
- **Canonical:**
  `data/generated/corolla_8965H1202000_fd_control_interface.json` v2;
  `data/generated/corolla_8965H1202000_openpilot_state_bridge.json` v7;
  `data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json`;
  `tests/verify_corolla_8965H1202000_fd_control.py`;
  `tests/verify_corolla_8965H1202000_openpilot_state_bridge.py`;
  `tests/verify_span_2025_discord_rlog_opendbc_evidence_external.py`;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md) §6.


### CORR-110 — `FEBEAE16` supervisor thresholds are internal command state, not measured Q-current response limits

- **Superseded framing:** the first non-enabling Panda contract left an
  `actuator_response_fault_threshold` open next to the statically decoded `0x4A3`
  Q-current observable and the recovered `CB394/CB59A` thresholds. That wording
  could be read as though the EPS's cooperative supervisor already contained a
  measured-Q-current comparator whose numeric limit merely remained to be found.
- **Exact correction:** the physical Q-current chain is
  `0x33160: FEBE6BAE -> 0x5722E: FEBE6592 -> 0x46C4C: 0x4A3 B6:B7`.
  A promoted complete exact-symbol census of the target-native H decompiler corpus
  finds `FEBE6592` only at the snapshot and telemetry stages (`0x5722E`, `0x46C4C`).
  The cooperative `CB394` and `CB59A` monitors instead consume `FEBEAE16`, an
  internal command-derived state. Their 512/1280 thresholds are therefore **not
  measured-Q-current limits**.
- **Safety consequence:** no OEM measured-Q-current response threshold is recovered
  in the cooperative B6 supervisor under the exact-symbol census boundary. A Panda
  actuator-response limit may still be desirable, but it must be a separately
  designed and relay-correctly validated safety policy rather than an EPS constant
  transplanted by analogy. Likewise the recovered ~±8.238 N.m driver-torque
  acquisition clamp and ±10 N.m telemetry saturation are representation limits,
  not physical driver-override thresholds.
- **Boundary:** the reference census is complete for direct textual symbol
  references and explicitly does not exclude arbitrary computed-pointer/alias-only
  accesses. The correction is therefore a bounded static negative, not a claim that
  no other firmware layer or upstream sender can implement driver/response policy.
- **Canonical:**
  `data/generated/corolla_hf_steering_limits.json`;
  `data/generated/corolla_8965H1202000_steering_limits_reference_census.json`;
  `tests/verify_corolla_hf_steering_limits.py`;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md).


### CORR-111 — B6 verification failure is not universally non-delivering

- **Superseded framing:** SECOC-071 and the first H/F B6 verification artifact
  correctly proved that CMAC mismatch never commits pending freshness, but then
  overextended the normal verified-delivery gate into the unconditional claim that
  mismatch/hard freshness failure could never release PDU42 to COM.
- **Exact correction:** target-native H functions close a generated
  verification-failure forwarding policy. `0x8857C` zeros global counter
  `FEBE5408`; receive-main chain `0x88308→0x88288→0x886DA` increments it while it
  is below raw configured limit **204** (`0x25726`), and `0x886FC` can reset it.
  B6 profile byte `+0x09` is 0. Generic failure handler `0x888A6` routes the queued
  PDU through `0x88856` when either global state `FEBE53EE` is D2 (`0x88512`) or
  profile `+0x09 != 1` and `FEBE5408 < 204`. Hard freshness result `0x22` enters
  A5 and calls `0x888A6` without submitting command7; a CMAC mismatch first uses
  B6's one retry, then retry exhaustion enters state `0x96` and calls the same
  handler. Under the forwarding condition, the failed queued B6 can therefore reach
  PDU42/COM.
- **What remains unchanged:** verification failure never commits the pending B6
  freshness slot. The forwarded PDU is **not** an authenticated success. Once the
  counter is >=204 and the global D2 mode is inactive, the recovered failure handler
  does not route failed B6 through `0x88856`.
- **Boundary:** the wall-clock duration of the 204-count interval and the OEM name/
  activation policy of global D2 mode remain unrecovered. This correction does not
  authorize unauthenticated injection; it strengthens the requirement for exclusive,
  deterministic B6 authority during production control.
- **Canonical:**
  `data/generated/corolla_8965H1202000_b6_secoc_verification.json`;
  `data/generated/corolla_hf_b6_competing_sender_arbitration.json`;
  `tests/verify_corolla_8965H1202000_b6_secoc_verification.py`;
  `tests/verify_corolla_hf_b6_competing_sender_arbitration.py`;
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §7.36;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md).


### CORR-112 — H/F `Ready Status` is an incoming `0x51E B0[7]` field, not diagnostic-only

- **Superseded framing:** COM-009 and the first H/F state-bridge pass correctly
  recovered Techstream DID `0x1033 Ready Status` through
  `FEBE7D1B -> FEBEF052 -> FEBEB5A8 -> FEBEE811`, but stopped one generated-COM
  layer early and described it as a diagnostic oracle with no proved CAN-field join.
- **Exact correction:** exact H Rx PDU29 is classic CAN `0x51E/8`; generated
  signal154 at `0x46144` extracts **B0[7]** directly into `FEBE7D1B`. The complete
  proved ingress is therefore
  `0x51E B0[7] -> FEBE7D1B -> FEBEF052 -> FEBEB5A8 -> FEBEE811 -> DID 0x1033`.
  `FEBEF052 -> FEBEB5A8` has two operational copy sites (`0xBAB58`, `0xBAC16`),
  and the RAM nodes also have initialization/reset writers, so this is a dataflow
  proof rather than an exclusive-writer claim.
- **Dynamic corroboration:** the public 2023 route carries 59/59 `0x51E` samples
  with B0[7]=1; Span's 2025 moving rlog carries 60/60. Neither capture exercises
  Ready=0, so the transition/policy meaning remains bounded.
- **Boundary:** this proves an **incoming Ready Status field**. It does not prove
  that `0x030/0x351/0x394/0x4A3` republishes the same boolean, and it does not by
  itself justify mapping Ready=0 to an openpilot temporary/permanent fault class.
- **Canonical:**
  `data/generated/corolla_hf_nonsteering_engagement_state.json`;
  `data/generated/corolla_8965H1202000_openpilot_state_bridge.json`;
  `tests/verify_corolla_hf_nonsteering_engagement_state.py`;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md) §6.4.


### CORR-113 — H/F TAUJ0-CH3 is a 5-ms steady foreground tick; B6's seven-tick cutout is nominally 35 ms

- **Superseded framing:** the first H/F B6 receiver and Panda contracts correctly
  proved a seven-foreground-tick primary loss cutoff but stated that the TAUJ0-CH3
  wall-clock period could not be recovered and therefore prohibited a millisecond
  conversion.
- **Exact correction:** exact H timer initialization `0x5F660` loads CH3 from the
  table pair `400000 + 8000 - 1`, producing a one-time 5.1-ms first interval, while
  steady foreground path `0x5F812` rewrites CH3 to `400000 - 1`. The recovered
  timer clock therefore yields a **5.0-ms steady foreground tick**. PDU42 reloads
  its deadline to seven ticks after each successful B6 reception, so the primary
  steady-state loss cutoff is nominally **35 ms**.
- **Dynamic corroboration:** Span's moving rlog contains 6,000 exact-H/F `0x030`
  frames. Its mean inter-frame period is `10.0000121147 ms`; the exact H/F Tx
  descriptor uses two foreground ticks, independently yielding
  `5.0000060573 ms/tick`. Zero/minimum timestamp deltas caused by batched logging
  are not used as the cadence estimator.
- **Boundary:** this closes the EPS foreground scheduler period and receiver timeout,
  not Toyota's stock B6 transmit cadence.
- **Canonical:**
  `data/generated/corolla_8965H1202000_b6_receiver_contract.json`;
  `data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json`;
  `tests/verify_corolla_8965H1202000_b6_receiver_contract.py`;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md).


### CORR-114 — B6 signal258=1 suppresses the recovered CBEEE additive term; it does not enable it

- **Superseded framing:** the first B6 companion-field summary described signal258
  (`B6 bit2`, snapshot `FEBEADBB`) as requiring value 1 for a profile-dependent
  controller contribution.
- **Exact correction:** exact H `CBEEE` calls the recovered additive contribution
  only when an active profile exists **and** `signal258 != 1` **and** the staged
  direction/mode condition mismatches. Therefore `signal258=1` unconditionally
  suppresses that recovered extra term; value 1 is not an enable value for this
  consumer.
- **Related bounded defaults:** exact consumers also make signal260 values 0 and 3
  equivalent in the recovered selector family; zero 262/263 removes their recovered
  percentage contributions; 264=0 and 265=0 are conservative EPS-consumer candidate
  values. These are not promoted to a proven stock active-LTA payload template.
- **Boundary:** the P5 phrase `Cooperative Control in Progress Flag` remains family
  vocabulary only; no literal OEM field-name join for signal258 is claimed.
- **Canonical:**
  `data/generated/corolla_8965H1202000_b6_receiver_contract.json`;
  `tests/verify_corolla_8965H1202000_b6_receiver_contract.py`;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md).


### CORR-115 — Sienna command-5 software semantics transfer to H/F; its verified resident-RAM geometry does not

- **Superseded framing:** the existence of a working Sienna command-5 RAM proxy and
  strong H/F software homology could be read as though the same single-stage
  `FEBF0xxx` resident placement were portable to Corolla H/F.
- **Exact correction:** exact H record0 at `0x27C88` points to completion
  `0x82F5C`, adapter `0x820CC`, worker `0x821D0`, and config `0x27C84`; dispatcher
  `0x82750`, variable-length prepare `0x81E94`, and lower command-5 engine `0x83A30`
  provide the software machinery for a caller-selected 36-byte B6 authenticated
  input, and the relevant application bytes are identical on F. However H startup
  `0x6149A` clears `FEBF05CC..FEBF09CB` and `FEBF0B4C..FEBF0F4B`, while H-owned
  structures occupy the lower page. The verified Sienna resident placement must
  therefore **not** be copied by address.
- **Consequence:** no H/F verified row is added to
  `data/variant_ram_exec_requirements.json`. The recovered H XCP shadow
  `FEBF7C00..FEBFFBFF` is only a two-stage carrier hypothesis until a target-native
  execution route is proved. Live provisioned-slot4 command-5 permission also remains
  a hardware test.
- **Canonical:**
  `data/generated/corolla_hf_command5_portability.json`;
  `tests/verify_corolla_hf_command5_portability.py`;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md).


### CORR-116 — H/F driver override is now a Panda/openpilot policy problem, not an unrecovered Toyota comparator

- **Superseded framing:** after the physical `0x030` torque carrier was decoded, the
  remaining safety checklist still described a generation-native physical
  driver-override **threshold** as something to recover from the H/F cooperative
  steering supervisor.
- **Exact correction:** TMS-053 expands the exact-H census to named and fixed-GP
  references for the physical `FEBE7B08 -> FEBE6554` torque source/snapshot family.
  Thirteen direct source/snapshot references are recovered and **zero** lie inside
  the C8xxx–CExxx target-to-motor control cone. The previously recovered ±2109
  acquisition clamp (~8.2383 N.m) and ±10.00 N.m telemetry saturation remain
  representation limits, not override comparators.
- **Boundary:** this is a bounded static negative over direct named/fixed-GP textual
  references; arbitrary computed-pointer/value-set aliases and DMA are outside the
  proof. It does not prescribe a numeric openpilot threshold. A conservative Panda/
  openpilot driver-override policy must still be chosen and dynamically validated.
- **Canonical:**
  `data/generated/corolla_hf_steering_limits.json`;
  `tests/verify_corolla_hf_steering_limits.py`;
  [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md).


### CORR-117 — The selected FRC_P5 cruise Data IDs are direct SID-0x22 RDBI requests in current GTS+

- **Superseded framing:** the first non-steering engagement closure correctly treated
  `0x1901/0x1905/0x1906/0x1912/0x1914` as exact P5 diagnostic Data-ID oracles but
  left their live service mapping bounded and therefore instructed captures to use
  the Techstream/GTS+ data-monitor UI unless direct `0x22` support was separately
  recovered.
- **Exact correction:** current GTS+ `DataListIF.dll` now byte-proves
  `CCommEventPhase5DM::DataidSetup` constructs `22 || DID_hi || DID_lo` for each
  selected Data ID. `CheckRcvFrame` requires positive service `0x62`, strips the
  first three response bytes, and copies the remaining data up to the runtime
  expected DID length. The five cruise oracles can therefore be polled directly as
  `22 19 01/05/06/12/14`.
- **Capture boundary:** the GTS+ receive worker does not itself compare returned DID
  bytes 1/2 with the queued DID before stripping them. Independent tooling should
  require `62 || requested_DID` before decoding. No named outer DiagnosticSessionControl
  or SecurityAccess prerequisite is inferred from this path.
- **Canonical:** `data/generated/techstream_v18/tss3_cruise_live_transport.json`;
  `tests/verify_tss3_cruise_live_transport_external.py`;
  [../tooling/techstream.md](../tooling/techstream.md) §6.3.

### CORR-118 — `8965H1202000` is not Albino's application-F181 primary

- **Wrong:** the retained 2026-08-18 corpus was described as having live software
  IDs `8965H1202000 / 8A3111202000`, while `8965F1208000 @ 0x20860` was called
  only a table entry and not the unit's live identity. CORR-070 inherited that
  wording from the contributor manifest before a direct F181 transcript existed.
- **Right:** Albino's same-car 2026-08-26 eps-telescope probe directly reads
  application F181 as count `2` with records `8965F1208000` and
  `8A3111202000`. Exact target-native callback `0x4A328` independently copies
  those records from CodeFlash `0x20860` and `0x17DC0`. The distinct
  `8965H1202000 @ 0x17D80` record is returned by callback `0x4A2E0`, configured
  for the separate one-record DID `0x2032` path.
- **Consequence:** Albino and Span share application-F181 primary
  `8965F1208000`; they remain distinct physical/calibration specimens through
  the F181 secondary and auxiliary identities (`8A3111202000` /
  `8965H1202000` versus `8A3111213000` / `8965H1213000`) and their low
  calibration data. Existing filenames and generated artifact IDs containing
  `8965H1202000` are retained as stable historical corpus labels rather than
  mechanically renamed.
- **Provenance boundary:** the contributor-supplied 2026-08-18 `MANIFEST.txt`
  remains immutable even though its identity interpretation is superseded. The
  public comma route still has forced old `carParams` and no passive `carFw`, so
  this correction joins the later telescope run to the tracked firmware, not the
  route itself.
- **Canonical:**
  `data/generated/corolla_2023_albino_telescope_analysis.json`;
  `tests/verify_albinoelephant_telescope_probe.py`;
  [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md) §7.39.

### CORR-119 — F33 `FEBF0000` is not a retained stock-application carrier

- **Wrong:** VAR-056 / the original exact-F33 runtime-carrier artifact treated
  `FEBF0000..FEBF0307` as the best production resident carrier candidate because
  the static direct/simple-GP census did not find a consumer before `FEBF0308`.
  The associated audited canary/proxy were therefore linked against that low
  pocket and retention was left as an untested live gate.
- **Right:** the real stock application startup live probe overwrites the low
  pocket (`prefix_648_byte_exact=false`, `shell_retained=false`). A separate
  exact-target live probe proves **`FEBFF9F0..FEBFFBFB` (524 bytes)** survives
  stock startup byte-for-byte, executes, and returns to stock application F181;
  retained SHA-256 is
  `89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c`
  and Panda `safety_tx_blocked_delta=0`.
- **Consequence:** `FEBF0000` remains valid authenticated **boot staging** but is
  no longer a production application-resident VMA. Exact F33 geometry is promoted
  in `data/variant_ram_exec_requirements.json` with retained VMA
  `FEBFF9F0..FEBFFBFC`. The old low-linked audited binaries remain reproducible
  historical/static construction evidence only.
- **Additional closure:** target-native application XCP maps SET_MTA `0x82C62`
  and DOWNLOAD `0x81FFE` into the configured `FEBF7C00..FEBFFBFF` software write
  window, so the verified high tail has a stock application-mode placement
  primitive if the `0x7F7/0x7F8` transport can be reached. A target-native
  22-record / 88-endpoint fixed-DMAC census has zero endpoints in the XCP window,
  closing the obvious recovered DMA composition as a hidden pivot. The remaining
  production blocker is a safe already-running-application control-transfer pivot,
  not RAM lifetime.
- **Canonical:**
  `data/generated/camry_8965F3307000_application_ram_loader_assessment.json`;
  `tests/verify_camry_8965F3307000_application_ram_loader.py`;
  [../variants/camry-2026-live-baseline.md](../variants/camry-2026-live-baseline.md) §§12.6–13.

### CORR-120 — VAR-056's four-user F33 torque-source census was incomplete; `0x4C000` is the fifth recovered direct user

- **Superseded framing:** VAR-056's then-recovered whole-function corpus reported
  four direct/fixed-GP users of the F33 physical driver-torque source `GP-0x5158`:
  `0x35A06`, `0x4DB70`, `0x54244`, and `0x564CE`.
- **Exact correction:** forcing the exact F33 generated-COM status/telemetry island
  recovers `0x4C000`, the native `0x4A3` source producer. It directly reads
  `GP-0x5158`, bringing the recovered direct/fixed-GP set to **five**:
  `0x35A06`, `0x4C000`, `0x4DB70`, `0x54244`, `0x564CE`.
- **Consequence:** the safety-relevant bounded negative is unchanged. `0x4C000` is
  a generated telemetry Tx producer outside the cooperative `C8xxx–D1xxx`
  target-to-motor control cone. The census still recovers zero direct/fixed-GP
  torque-source users inside that cone; computed aliases, DMA, and unrecovered
  functions remain outside the proof.
- **Related F33 correction:** the same target-native `0x4A3` producer uses
  `GP-0x50E8` for its B6:B7 current-like packed integer, while exact DID `0x1151`
  Motor Actual Current (Q Axis) reads `GP-0x50F2`. The passive DBC therefore keeps
  the F33 packet field structurally named `MOTOR_CURRENT_ALT_RAW` with no physical
  unit instead of transferring the H/F Q-current name.
- **Canonical:**
  [../variants/camry-2026-tss3-opendbc-port.md](../variants/camry-2026-tss3-opendbc-port.md);
  `data/generated/camry_8965F3307000_tss3_opendbc_port.json`;
  `tests/verify_camry_8965F3307000_tss3_opendbc_port.py`.
