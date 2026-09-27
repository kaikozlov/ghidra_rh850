# Current priorities

Short execution queue only. This page answers **what should we do next?** It is
not a roadmap and must not become a completion diary. Detailed unresolved state
belongs in [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md); claim history lives in
[FINDINGS.md](FINDINGS.md) / [CORRECTIONS.md](CORRECTIONS.md); procedures,
evidence, and closure narratives live in the canonical reports linked below.

This is a research queue, not deployment qualification or an installation
procedure. The [Camry capability matrix](../variants/camry-2026-capability-matrix.md)
owns the distinction between retained demonstrations and remaining qualification.

## Active queue

1. **Camry native producer contract — [OQ-054](OPEN_QUESTIONS.md).** Recover the
   FRC-internal feature-selection → protected `0x08A` egress implementation and
   downstream Brake request-arbitration/result → B6 handoff.
   Missing evidence includes synchronized FRC recorder/CAN observations and
   matched Brake/FRC firmware (item 2). Do not replace those with another
   summary of already-retained EPS experiments. Preserve the demonstrated
   development evidence and use the
   [capability matrix](../variants/camry-2026-capability-matrix.md) for remaining
   override, cancel, lifecycle, and deployment qualification. Detailed chronology:
   [the port report](../variants/camry-2026-tss3-opendbc-port.md) and
   [the field baseline](../variants/camry-2026-live-baseline.md);
   canonical topology:
   [../architecture/toyota-tss3-vehicle-movement-arbitration.md](../architecture/toyota-tss3-vehicle-movement-arbitration.md).
2. **Missing target-native software.** (a) Exact-Camry Brake/EPB
   `F152633K0000` / assembly `8954147040` (`0x7B0`) is deterministically absent
   from the local corpus (VAR-069); the provenance-safe route is the
   authenticated Toyota/TIS ECU-supply-change query for the exact VIN (host
   flow closed by TMS-045..050). (b) FRC side: the 23TC01 Corolla `0792`
   package family is already local (TMS-052); what remains is FRC
   bootloader/programming-decoder firmware or a full raw NOR dump from a
   matching/sacrificial camera — package key-guessing is a bounded dead end
   (TMS-088) and the diagnostic-core → HSM Cortex-M3 service ABI is the missing
   software boundary. Canonical:
   [../variants/tss3-frc-firmware-acquisition.md](../variants/tss3-frc-firmware-acquisition.md)
   · [../tooling/techstream.md](../tooling/techstream.md) §6.2.2.
3. **H/F live capture.** A firmware-identified, relay-correct Corolla H/F
   target with stock LTA and cruise transitions: `0x4A3/0x351/0x394`
   asserted/recovery correlation, `0x51E` Ready transitions, synchronized FRC
   P5 cruise Data IDs, an independent gear oracle, and — only if stock B6
   appears — protected `0x0B6` stock-sender cadence/bounds. Checklist:
   `data/generated/corolla_tss3_opendbc_readiness.json`. Canonical:
   [../variants/corolla-h-f-openpilot-state-bridge.md](../variants/corolla-h-f-openpilot-state-bridge.md)
   ·
   [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md)
   §§7.34–7.36.
4. **Target-specific hardware questions.** Sienna command-5 permission and
   related retention questions are indexed by [OQ-012](OPEN_QUESTIONS.md) and
   [OQ-021](OPEN_QUESTIONS.md). Read each question's calibration and later
   evidence before treating it as an unresolved Camry/Crown/Corolla blocker.
   These are not one cross-target sender-qualification state.
5. **Sienna XCP evidence boundary — [OQ-004](OPEN_QUESTIONS.md).** Keep this
   legacy target's physical-reachability question separate from later
   target-specific results. Canonical:
   [XCP report](../communications/xcp-command-dispatch.md).
6. **Applicable comparison image — [OQ-006](OPEN_QUESTIONS.md).** Additional
   acquisition should answer a specific transfer question, not the obsolete
   “first foreign image” milestone. Existing Crown, Camry, and Corolla inputs
   are discoverable through [the target index](../variants/README.md).
7. **Capture-preservation add-ons during a real GTS+ session:** preserve raw
   true-TSS3 PCS Operation/Image FFD `.TSE` before GTSE conversion and, if
   exported, the `.vdas` ZIP (TMS-086/087). Canonical:
   [../tooling/gtsplus-tse-gtse-saved-session.md](../tooling/gtsplus-tse-gtse-saved-session.md)
   · [../tooling/gtsplus-vdas-pcs-data.md](../tooling/gtsplus-vdas-pcs-data.md).
8. **Longitudinal — [OQ-052](OPEN_QUESTIONS.md).** The wire/auth/arbitration
   execution contract is still open and must close before any production
   longitudinal support. Canonical:
   [../variants/camry-2026-longitudinal-evidence.md](../variants/camry-2026-longitudinal-evidence.md).

## Deferred / opportunistic

Work only when the specific dependency appears: bench-only SecOC behavior
trials ([OQ-023](OPEN_QUESTIONS.md)..[OQ-026](OPEN_QUESTIONS.md)) · stale-RDBI
confirmation ([OQ-003](OPEN_QUESTIONS.md)) · CommunicationControl availability
([OQ-049](OPEN_QUESTIONS.md)) · command-13 SHE-deviation check
([OQ-013](OPEN_QUESTIONS.md)) · RFP serial-protocol transfer
([OQ-033](OPEN_QUESTIONS.md)) · power/EM and fault-injection fallbacks
([OQ-017](OPEN_QUESTIONS.md)/[OQ-018](OPEN_QUESTIONS.md)).

## Closed queues — do not reopen without new evidence

- **Pre-GTS static-only pass** (TMS-024..034, TMS-042): closed. Remaining
  blockers all require genuinely new evidence — a matching modern-EPS
  `.cuw`/`.cal` package, a retained labeled GTS+/J2534 session, newer GTS+/CUW+
  host material, other steering-controller firmware, or missing target
  CodeFlash. Capture requirements:
  [../tooling/techstream-capture-procedure.md](../tooling/techstream-capture-procedure.md).
- **Directed FRC_P5 producer static exception** (TMS-040..053): closed. The
  category-435 Active-Test catalog (TMS-044), `SearchCal` (TMS-048), and the
  `0x18A` heatmap lead (COM-013) are bounded negatives — do not re-search them.
- **GTS+ recorder host-static boundary** (TMS-079..087): no generic
  protected-host decoder or ownership sweep remains; next value is
  target-native dynamic/firmware correlation (items 1–2).
- **Exact-F33/EPS static command-path closure** (VAR-065..085,
  CORR-127..138): no more blind bus-traffic mining, ordinary-COM searches, or
  DDB publisher hunts; the remaining discriminators are items 1 and 4.
- **`8965H1202000` comparative sweep** ([OQ-029](OPEN_QUESTIONS.md)): closed
  target-natively. New static work needs a concrete target-native semantic,
  externally reachable sink, or variant-transfer question;
  `data/exploit_interest_reviewed_candidates.csv` prevents re-audit.
- Historical negative guidance — generic whole-image sweeps, `FF*16` KAT as a
  live key, object-15 as live-key proof, command-13 as key export, software-ID
  offset tables — is retained in [CORRECTIONS.md](CORRECTIONS.md).

## When this page changes

Update only when the **execution order** changes. Keep completed conclusions in
the owning subsystem report; update ledger navigation when useful, not as a
mandatory transaction. Never append a completion diary here.
