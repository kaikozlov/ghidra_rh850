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

- **`0xAB` service purpose.** Bounded: 13 RID callbacks traced, no direct
  crypto/NvM/SecOC references found. 'Calibration/flash control' remains a
  **hypothesis**, not proven. Indirect calls through wrappers or
  GP-displacement RAM access not yet traced remain a residual possibility.
- **97 configured-unresolved RX signals** (see `data/application_rx_signal_evidence.csv`).
  Bounds are known; exact runtime producers are not statically recovered.
- **Three configured TX signals without recovered runtime producers** (see
  [../communications/application-tx.md](../communications/application-tx.md)).
- **Motor-control calibration handlers.** Large OEM motor-control functions
  (`0x47C3C`, `0x32B80`, `0xB98BC` cluster) are mapped structurally but not
  behaviorally understood.

## SecOC

- **Live slot-4 operation permissions.** Static CodeFlash proves slot-4
  verification but cannot determine the provisioned usage flags. Command 5 and
  the generic command-1/3 AES wrapper accept software selectors `0..14`,
  including 4, but ICU-S may reject generation or encipher/decipher for this
  slot. Test command 7 good/bad controls and then command 5/1 after normal
  application initialization; record status, output, latency, jitter, and
  debug-attached behavior. See
  [../security/secoc/key-recovery-assessment.md](../security/secoc/key-recovery-assessment.md).
- **Command 13 and `RAM_KEY`.** The stock application never issues command 13,
  but that does not determine direct hardware behavior. Obtain the restricted
  ICU-S/ICUSE command specification or characterize a custom application-context
  harness: establish behavior with a known caller-loaded `RAM_KEY`, vary command
  selectors including 4, record raw status/output, and test whether any
  non-destructive operation copies or aliases slot 4 into `RAM_KEY`. The proposed
  copy-then-export chain is untested, not disproved.
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
  structurally usable and arbitrates the shared ICU driver, but there is no
  configured application upload/execution foothold, no stock output transport,
  and no production SecOC transmit path. A dynamic prototype must establish
  application-context execution, slot-4 permission, output transport,
  sender-side freshness, latency, and command-7 contention.
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

- **Semantic coverage.** 5,865 functions recovered; most remain evidence-grade
  `recovered` rather than behaviorally understood. Closing this is a
  long-tail effort, not a single task.
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
