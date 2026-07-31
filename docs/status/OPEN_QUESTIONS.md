# Open questions

Unresolved questions only. Once resolved, findings move to
[FINDINGS.md](FINDINGS.md) (with their evidence grade) and any superseded
prior claim moves to [CORRECTIONS.md](CORRECTIONS.md).

## Bootloader

- **Payload provenance.** The two pinned public payload fixtures verify the
  gate, but the original payload-generation toolchain (who built them, against
  which secret distribution) is not established.
- **Bootloader DID `0203` semantics.** It ignores its five bytes and only arms
  state 0 → 1. Whether any field ever carried meaning in other calibrations is
  unknown.

## Application

- **`0xAB` event-record naming.** The configured graph is closed and its
  list/per-ID/detail structure is recovered, but the OEM service name and exact
  meanings of the event catalogue's encoded upper ID bits and record-kind
  values remain unknown.
- **97 configured-unresolved RX signals** (see `data/application_rx_signal_evidence.csv`).
  Bounds are known; exact runtime producers are not statically recovered.
- **Three configured TX signals without recovered runtime producers** (see
  [../communications/application-tx.md](../communications/application-tx.md)).
- **Authenticated command to d/q current reference.** The high-rate
  phase-current-control-to-TSG3-PWM chain is recovered, and the d/q-reference
  producer cone is now enumerated clean two levels deep: `0x37712` builds
  `0xFEBE6D28/6D2A` from `0xFEBE6D4E/6D50/6D70/6D7E/6D52/6D54`, whose producers
  (`0x3795E/0x37B5A/0x37CD4`) reference only `0xFEBE5F**/6D**`. No
  command-derived location (`0xFEBEBF84/0xFEBEBF9A/0xFEBEBFA2/0xFEBEAE16` or
  snapshot copies) appears in the cone; the apparent `autosar_os_task_signal_dispatch`
  (entry `0x58404`) writer at instruction `0x5AE28` is a buffer-clear idiom, not a producer.
  So no static reader joins the conditioned command to the current references. If the join exists it is
  purely runtime/computed (AUTOSAR RTE outer-loop or function-pointer dispatch,
  invisible to the static call graph). Consequently a correctly signed `0x2E4` is
  SecOC-accepted and conditioned but not statically provable to reach motor
  actuation — signing is necessary but not statically sufficient; confirm on a bench.
- **Phase-sample acquisition peripheral names.** Firmware reads six indexed
  result locations in each `0xFEEF81E0` and `0xFEEF8A20` window and clears the
  consumed low halfwords. Their use as upstream phase-current samples is
  recovered; exact P1M-E module/register names remain bounded.
- **Remaining motor calibration cluster.** `0x47C3C` is behaviorally recovered
  as the steady phase-current conditioner. The separate `0x32B80` and
  `0xB98BC` calibration-transition handlers remain only structurally bounded.

## SecOC

- **Live slot-4 operation permissions.** Static CodeFlash proves slot-4
  verification (command 7). The AUTOSAR SHE spec governs usage by a single
  binary `KEY_USAGE` flag (enc/dec ⊕ MAC-generate+verify; no verify-only
  facility — SECOC-023, CORR-017), so under SHE a MAC-usage slot 4 *permits*
  command-5 generation and would *reject* command 1/3 enc/dec. The remaining
  open question is therefore narrower: does the Renesas ICU-S deviate from SHE
  (a non-standard verify-only restriction, or debug/lifecycle gating)? Bench-test
  command 7 good/bad controls then command 5 after normal application
  initialization; record status, output, latency, jitter, and debug-attached
  behavior. See
  [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md) §1.3.
- **Command 13 and `RAM_KEY`.** The SHE spec now disproves the slot-4→`RAM_KEY`→export
  extraction route (SECOC-025): `CMD_EXPORT_RAM_KEY` is `RAM_KEY`-only/plain-only and no
  non-volatile KEY has an export or copy command (§4.7). So command-13 opcode identity is
  moot for extraction — no SHE command can pull slot 4. The remaining value of characterizing
  command 13 is narrow (confirming the opcode table / Renesas deviation) and lower priority
  than the RAM-mirror check below. See
  [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md).
- **Runtime RAM key-slot mirror on `8965B4512000` (resolved negative).** Traced and
  closed (SECOC-027): the ICU-S driver is a selector-based hardware-accelerator
  interface (key SELECTOR to `0xFFC5D004`, never a key value; register footprint exactly
  `0xFFC5D000-0xFFC5D0FF`, no key-RAM window), the sibling mirror addresses `0xFEBE6E**`
  hold motor-signal data here, and per SHE (SECOC-025) the firmware has no command to read
  a non-volatile slot key to cache. Community Technique A does not transfer. Residual
  (non-static): a hardware-only key-RAM window not referenced by firmware, or a transient
  runtime copy, can only be excluded by a wide bench RAM dump — low priority given the
  selector-based driver and the SHE read-prohibition.
- **Same-vehicle producer key storage.** Identify the physical producers of the
  protected IDs, beginning with but not assuming the forward camera, then dump
  exact-part peers and validate all 16-byte candidates against synchronized
  stock frames. A producer must have the shared key or equivalent signing
  capability, but its MCU, HSM, slot, and CPU-visible storage are unknown.
- **Command-7 power/EM leakage.** FD IDs `0x090`/`0x0D7` provide 14 chosen bytes
  in CMAC's first AES block. Run fixed-vs-random leakage detection, establish a
  stable trigger, attempt CPA for key bytes 2..15, and complete the two fixed
  Data-ID-aligned bytes by `2^16` search against multiple stock tags. ICU-S
  masking, byte order, trace count, and attainable SNR are unobserved.
- **Physical power topology.** Confirm the chip marking and measure the actual
  core rail before power analysis or glitching. Renesas lists `R7F701381` as a
  DPS part with VDD pins 11/66/98, while a public same-part-number report
  describes VCL/eVR pins 11/66.
- **Protected-tail serial read.** Determine whether a faulted serial read of
  `0x1007800..0x1007FFF` bypasses only a mask-ROM range check or also exposes
  nonblank ICU-S storage. The current CPU-visible dump contains only `00/FF`;
  public P1M-E fault injection proves ordinary flash readout, not key-array
  access.
- **Application-resident signing proxy.** The initialized command-5 wrapper is
  structurally usable and arbitrates the shared ICU driver. There is no
  configured **application diagnostic** upload path, stock output transport, or
  production SecOC transmit path; however, repository-known bootloader gate
  material provides a constructible callback and an authorized bridge to a
  possible persistent/restorable application hook. Authenticated-input and
  trailer packing are no longer open questions: pinned opendbc code and the
  independent local stateless signer reproduce them. A dynamic prototype must
  still establish key availability, application-context execution, slot-4
  permission, output transport, runtime freshness scheduling, latency, and
  command-7 contention. See
  [../security/secoc/sender-implementation.md](../security/secoc/sender-implementation.md).
- **Dormant crypto-test activation.** CAN `0x01B..0x01F` provide the test
  selector/message/expected result only after bank activator `0x69018` runs.
  No caller or function-pointer entry reaches that activator in the recovered
  graph; whether an unrecovered lifecycle or external debug path can arm it is
  unknown.
- **Object-15 producer.** No static producer exists in this calibration.
  Where a provisioned unit writes object 15 from is unknown (dealer tool path
  hypothesis only).
- **Reset-window replay.** Receiver freshness is zeroed at SecOC initialization,
  so a captured positive synchronization value is structurally forward after
  reset. A cold-boot bench capture must determine sync cadence, whether an old
  authenticated sync can win the startup race, which early ordinary frames can
  then replay, and how quickly legitimate sync closes the window.
- **Tag-guess and saturation rate.** The static profile exposes 28 CMAC bits,
  does not advance freshness on failure, and has no recovered authentication
  failure lockout. Measure command-7 throughput, queue replacement, `0xE07`
  polling latency, watchdog load, legitimate-frame loss, and whether bus error
  behavior makes online guessing or only denial of service practical.
- **Future-sync recovery.** A valid sync can jump arbitrarily forward. Verify on
  a bench whether a far-future signed sync blocks lower legitimate epochs until
  receiver reset, whether any external freshness manager repairs it, and which
  diagnostic/status signals expose the desynchronization.
- **FD ignored-suffix behavior.** CAN-FD DLC 48/64 is accepted then clamped to 32.
  Confirm whether gateways or peer ECUs interpret the suffix differently; the
  Sienna EPS itself does not pass it to SecOC/COM.

## Variants

- **Corolla `8965F1208000`.** Essentially everything: MCU confirmation, SA
  levels, secret location, payload format, diagnostic endpoints, SecOC
  profile. See [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md).
- **TSS 3.0 family breadth.** Which Sienna findings generalize across the
  family (Camry, RAV4, etc.) is unmapped. See
  [../variants/tss3-family-comparison.md](../variants/tss3-family-comparison.md).

## Tooling

- **Semantic coverage.** 5,913 functions recovered; most remain evidence-grade
  `recovered` rather than behaviorally understood. A systematic interest-scored
  sweep (40 highest-signal functions decompiled, call graphs traced) found no
  additional subsystems in its sample, bounded the crypto surface to the two
  known AES consumers of `0x23E28` (SWEEP-001), and confirmed the nine-site
  `ICUSCMD` store-encoding census (SWEEP-002). These are sample- and
  pattern-bounded results, not whole-image negatives: the sweep does not
  exclude ciphers on different tables, stores through other addressing modes,
  or subsystems in unsampled functions. The sampled functions cluster into
  seven clear subsystem bands. The highest-value remaining unknown is the
  motor-control/safety cluster at `0x30000`–`0x4C000` and
  `0xB0000`–`0xC0000` — the d/q current-reference join and the isolated safety
  interlocks (`0x43A78`/`0x43716`/`0x438C6`) called via function-pointer tables.
  Closing this is a long-tail effort, not a single task.
- **RFP/P1M-E serial-protocol transfer.** The pinned Renesas host library
  substantially exposes the RV40F protocol, but a live R7F701381 signature and
  capability query has not yet shown which commands the P1M-E mask ROM accepts.
  Remaining static work includes the complete RV40F command census,
  mode-entry/reset sequence, capability-field parser (including feature
  `0x1106`), exact `SetICUM` field meanings, and the preconditions/effect of
  payload-free `ValidateICU_S`. See
  [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md).
- **DID `0x1010` production use and slot-4 package.** Static firmware now
  recovers a SHE-compatible command-8 key-update service behind WDBI DID
  `0x1010`; selector `01` starts the 64-byte M1–M3 update and selector `03`
  reads status `01/02/FF` plus M4/M5 on success. Capture a legitimate
  provisioning/rekey session and process it with
  `tools/decode_icus_key_update_trace.py` to determine whether Toyota/Denso
  actually invokes this DID, whether M1 targets slot 4, observed polling
  cadence/deadlines, and which lifecycle preconditions exist beyond the
  recovered extended-session/no-Dcm-SA policy. RFP's `ValidateICU_S` remains a
  separate lifecycle-validation operation, not this application request.
- **Techstream live-session capture.** `ptshim32.dll` (TMS-005) is a J2534
  PassThru interceptor/logger that can capture a complete Techstream↔EPS UDS
  transcript. Install it as the J2534 DLL shim on a Windows machine connected
  to a bench Sienna EPS, perform a diagnostic or reflash session, and compare
  the captured SA seed/key exchange, DID reads, session transitions, and
  programming handoff against the static firmware findings (SEC-BOOT-003,
  SEC-APP-001, DIAG-APP-001/003). The log format is unknown (export/PDB
  analysis only); reverse the writer or capture empirically. See
  [../tooling/techstream.md](../tooling/techstream.md) §6.
- **Techstream `.ddb` format.** The diagnostic databases (`EPS_P4DK3.ddb`,
  `Security_P4.ddb`, `Toyota.ddb`) use a proprietary `DiagTool DataCtrl` binary
  format with a 32-byte header and offset tables. The record structures
  (DID definitions, DTC mappings, SA level configurations, ECU enumeration
  data) are not decoded. Full parsing would extract the complete ECU-specific
  diagnostic vocabulary that Techstream applies at runtime. See
  [../tooling/techstream.md](../tooling/techstream.md) §7.
- **`CSecurityAccessAES128` key is for ADS/PCS, not EPS.** Resolved (TMS-007):
  the dispatch tree shows EPS uses `CCanEMPS_V850E_PS2FlashWriter` in the CUW
  reflash path, which reads seed/key from `CalibrationFile::GetSeedKey()` —
  data embedded in the `.cuw` calibration file, not hardcoded in any DLL. The
  `FUKUMORIYOSIYAMA` key is only for runtime ADS/PCS FFD access. To recover
  the actual EPS reflash key, obtain a Sienna EPS `.cuw` calibration file from
  Toyota's TechInfo portal and extract the `SeedKey`/`ServiceAuthKey` fields.
