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

- **Live slot-4 behavior.** Static CodeFlash proves slot-4 verification but
  cannot determine the donor's protected key state because the `FF*16` KAT is
  compiled out. Command 5 accepts software selectors `0..14`, including 4, but
  the protected slot's generation permission still requires a dynamic
  generate/verify round trip. Dealer rekey and ICU-S reservation contents in
  pages 480–511 also remain unknown. The experiment is
  specified in
  [../security/secoc/application-chain.md](../security/secoc/application-chain.md).
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

## Variants

- **Corolla `8965F1208000`.** Essentially everything: MCU confirmation, SA
  levels, secret location, payload format, diagnostic endpoints, SecOC
  profile. See [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md).
- **TSS 3.0 family breadth.** Which Sienna findings generalize across the
  family (Camry, RAV4, etc.) is unmapped. See
  [../variants/tss3-family-comparison.md](../variants/tss3-family-comparison.md).

## Tooling

- **Semantic coverage.** 5,858 functions recovered; most remain evidence-grade
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
  `0x1010`; the package carries target slot/AuthID/counter and the ICU returns
  M4/M5 proof. Capture a legitimate provisioning/rekey session to determine
  whether Toyota/Denso actually invokes this DID, whether M1 targets slot 4,
  and which lifecycle/session preconditions exist beyond the recovered
  extended-session/no-Dcm-SA policy. RFP's `ValidateICU_S` remains a separate
  lifecycle-validation operation, not this application request.
