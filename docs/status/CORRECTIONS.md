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
  (129 unique DTC IDs, 16 unique DIDs, 1257 monitor records), uses exhaustive
  explicit steering anchors for family-only `utility_string` vocabulary,
  removes duplicate exact/family monitor mappings, and fails closed on
  malformed LZSS, wrong file types, bad format-6 magic, and malformed section layouts.
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §6.1;
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
- **Canonical:** [../tooling/techstream.md](../tooling/techstream.md) §6.1;
  TMS-013; `tests/verify_diagnostic_vocabulary.py`.
