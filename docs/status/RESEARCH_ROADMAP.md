# Research roadmap

What to investigate next, in rough priority order. Completed items move to
[FINDINGS.md](FINDINGS.md); newly-discovered unknowns move to
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

## Near-term exploit engineering

1. **Complete the first live read-only CodeFlash acquisition with the generic
   pipeline.** The local host/reassembler, authenticated RAM wrapper, and
   424-byte P1M-E read-only payload are implemented and pinned-toolchain verified.
   The next missing observation is hardware-only: record `F181`/routing, acquire
   all 262,144 addressed words, preserve the exact SHA-bound dump, run boot-CRC
   sanity, and feed it unchanged to the semantic resolver. No live APPLY should
   precede this acquisition/recovery source. Canonical:
   `exploit/dumper/README.md` and
   [EXPLOIT_ENGINEERING_2026-08-12.md](EXPLOIT_ENGINEERING_2026-08-12.md).
2. **Validate the unchanged semantic resolver on a foreign calibration.** No
   local `8965F4207000`, `8965F4201000`, `8965F3401200`, or `8965F1208000`
   CodeFlash artifact is currently present. When one arrives, freeze F181/CPU/SHA
   provenance, run `tools/resolve_secoc_patch_image.sh` unchanged, and classify
   the semantic target against the blurbdust egg. Zero/multiple candidates must
   strengthen semantic matching rather than introduce an SWID→offset table.
3. **Prepare and then run the MAC28-only behavioral proof.** The deployment
   pipeline can only establish target/CRC persistence. The exploit claim still
   requires otherwise-stock camera traffic with only the protected `0x2E4/0x131`
   MAC28 invalidated, compared before/after the semantic Gate-2 patch with raw CAN,
   DTC, and steering-state evidence.
4. **Finish the targeted application-context command-5 harness depth pass now.**
   This remains locally actionable and should not wait for a foreign image or
   bench vehicle: recover the smallest reversible activation/input/output change
   around `0x69018 → 0x68B42 → 0x88350 → 0x87CCC`, plus cyclic/finalize behavior
   at `0x68C0C/0x68DE6`. Only the eventual selector-4 execution result is
   hardware-gated. Canonical:
   [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md).

## Near-term (static, this repo)

5. **Semantic coverage long-tail.** Move `recovered` rows in
   `data/semantic_coverage_ledger.csv` toward behaviorally understood only when
   they intersect a concrete security, diagnostics, or torque lead. Stage 6
   closed the previously named motor/safety static cluster; do not repeat a
   broad command→d/q or phase-SFR search without new evidence.

## Requires a provisioned Sienna (dynamic)

6. **Run the SecOC provisioned-unit experiment.** Filter NvM blocks 41/45/49,
   observe async completion, compare RAM mirror and post-write DataFlash,
   instrument ICU slot 4, validate candidates against synchronized CAN oracle
   data. Specified in
   [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

## Requires Corolla artifacts

7. **Confirm/deny the Sienna template on `8965F1208000` firmware.** MCU, SA
   implementation/secret location, payload format, and SecOC implementation.
   Direct field diagnostics are already mapped; do not repeat those probes.
   See [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md)
   for the structured checklist.
8. **Close the remaining identity/runtime-key boundary on the separate 2023-US
   public-route specimen.** The completed 32 KiB DataFlash is now analyzed: no
   raw key matches the local TSKM `0x00F` oracle, no public-route protected-domain
   raw key matches, 60 committed records fit the reference physical map, and an
   active 117/118 checkpoint ring occupies a `4512000`-disabled slot. The local
   capture (`TRIP 0xD0D`) and dump are separate TSKM jobs, and the dump performs
   a programming/SecurityAccess/RAM-exec transition; the older public route is
   `TRIP 0xCE9`. Acquire exact EPS `F181` and CodeFlash; if revisiting the car,
   capture full-bus sync/protected traffic immediately before the dump transition
   and again after recovery/reset to establish key continuity. Canonical:
   [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md),
   [../tooling/toyota-dataflash-analysis.md](../tooling/toyota-dataflash-analysis.md).
9. **Populate the TSS 3.0 family matrix.** Extend
   `data/tss3_eps_variant_matrix.csv` as additional variant firmware becomes
   available. Canonical: [../variants/tss3-family-comparison.md](../variants/tss3-family-comparison.md).

## Tooling

10. **Documentation site** (optional, after this reorganization). Material for
   MkDocs: explicit navigation, section index pages, search. Do only after
   canonical ownership is stable — search over duplicated docs just makes the
   inconsistency easier to find.
11. ~~**Link checking** in CI for `docs/` internal cross-references.~~ **Done** —
   `tests/verify_doc_links.py` runs in `make verify`.

## Completed static investigations

- **Corrected-graph whole-image re-audit (2026-08-11).** Two independent
  four-stage rebuilds agree exactly on the 6,037-function graph. All named
  caller/consumer negative families were rerun, the 100-function semantic
  cohort is reproducible, and 88 selected entries remain honestly
  `reviewed_unknown`. Canonical:
  [CORRECTED_GRAPH_REAUDIT_2026-08-11.md](CORRECTED_GRAPH_REAUDIT_2026-08-11.md).
- **Historical comprehensive sweep reconciliation (Stage 9, 2026-08-10).** At
  that snapshot, regenerated artifacts reported 533 annotated / 5,302 default
  recovered / 86 thunks across 5,921 functions. Those historical dimensions
  and the then-current “no further promotion” conclusion are superseded by the
  corrected-graph entry above. Run journal:
  [STATIC_ANALYSIS_SWEEP_2026-08-10.md](STATIC_ANALYSIS_SWEEP_2026-08-10.md).
- **External-reference / missing-artifact refresh (Stage 8, 2026-08-10).** Fetched and compared every named pinned research source, filtered the 51-commit `opendbc` delta to confirm no SecOC core/DBC change, inspected high-signal non-default branches/releases/forks, and re-ran exact public searches for `8965B4514000` CodeFlash, completed partner outputs, `8965F1208000` firmware, a Sienna EPS `.cuw`, and a physical `0x344` producer artifact. None surfaced. Newly pinned `optskug/docs @ 2c718412...` adds one useful refinement: an official Toyota rekey flow reportedly requires both MCU ID and VIN, independently establishing MCU identity as a required input but not proving Techstream DID `0x1010` `SafekeyNumber == MCU ID` (TMS-016). Canonical: [EXTERNAL_REFERENCE_REFRESH_2026-08-10.md](EXTERNAL_REFERENCE_REFRESH_2026-08-10.md).
- **SecOC software-path closure (Stage 7, 2026-08-10).** Closed the ICU stale-result/FIFO software surface as a bounded negative, strengthened dormant crypto-test activation from "no caller" to a whole-image entry/interior-pointer/state-writer negative, specified the minimum application-context selector-4 command-5 signing-proxy architecture including command-7 arbitration/freshness/Tx/teardown, and bounded candidate-f05 provenance to its earliest public Vance artifact plus later source-family corroboration. Remaining slot-4 permission, latency, command behavior, and physical/fault questions are dynamic/hardware-only. Canonical: [../security/secoc/software-path-assessment.md](../security/secoc/software-path-assessment.md), [../security/secoc/sender-implementation.md](../security/secoc/sender-implementation.md) §5.
- **Motor-control/safety boundary (Stage 6, 2026-08-10).** Resolved the
  phase-sample source as `ADCG0/1 DIR00 → DMAC → Global RAM A` rings, hardened
  the authenticated-command→d/q search into a bounded static negative after
  pointer/memcpy/RTE/hidden-command-branch censuses, recovered the former three
  "isolated interlocks" as members of a nine-channel registered
  plausibility/deadline monitor family, and bounded `0x32B80`/`0xB98BC` to their
  CH0/CH2 version domains. Canonical: [../architecture/control-partition.md](../architecture/control-partition.md) §9.
- **Application interface semantic closure (2026-08-11).** Extended the prior
  COM inventory into producer/consumer semantics. All 50 RAM-backed Tx signals
  now have an exact non-default producer census; CAN `0x260`, `0x262`, `0x351`,
  `0x394`, `0x4A3`, and `0x4C8` are producer-closed with bounded structural
  roles. The former 25 unresolved Rx-consumer rows split deterministically into
  7 unpacker-local post-process inputs and 18 store-only scalar destinations,
  with a whole-bank pointer census closing normal memcpy/RTE alias forms.
  Cross-interface joins now include `0x025/0x64F -> 0x4A3` and authenticated
  `0x2E4` command state contributing to `0x262 LKA_STATE` bit4. Techstream
  `EMPS_P5` monitor 402 `Command Value Torque` adds verified 16-bit/`Nm`
  corroboration for the command domain while monitor 60 remains ambiguous and
  monitor 403 is rejected as a direct CAN-field name. Canonical:
  [../communications/application-rx.md](../communications/application-rx.md),
  [../communications/application-tx.md](../communications/application-tx.md),
  [../architecture/control-partition.md](../architecture/control-partition.md),
  [../tooling/techstream.md](../tooling/techstream.md) §6.2.1.
- **Renesas RFP RV40F host protocol (2026-08-10).** Completed the retained
  `BootRV40F` host-side static census at 52 ordinary command IDs / 61 symbols,
  recovered the generic connection and both setup variants, traced the 8-byte
  `GetDeviceType` capability word including `0x1106`, bounded legacy `SetICUM`
  to its exact structural 20-byte option record, and pinned
  `CheckICUMode`/`ValidateICU_S` host sequencing. The complete security/config
  surface contains no dedicated 64-byte SHE M1/M2/M3 request or ICU
  `slot || key[16]` primitive; remaining applicability/lifecycle questions now
  require a P1M-E target or legitimate serial-boot capture. Canonical:
  [../tooling/renesas-rfp-rv40f.md](../tooling/renesas-rfp-rv40f.md).
- **Techstream Stage-3/static route residuals (2026-08-10 through 2026-08-11).**
  Recovered both shipped `ptshim32` J2534 log formats plus Techstream's
  timestamped save orchestration and added a cross-version parser; reconciled
  the DDB status so the complete type-2 structural corpus is no longer described
  as undecoded; bounded `Security_P4` to alarm/security vocabulary; and decoded
  priority type-1 master routes for `EPS_P4DK3`, `EPS_CAN_P4DK`, and now
  `EMPS_P5` (record 374 / category 405 / generation 20) with exact DLL/function
  joins. The targeted P5 signal-info consumer further recovers monitor
  physical-data, bit-range, unit, and pattern-display metadata used by the
  application-interface correlation. Communication-DID/RID category ownership,
  exact `8965B4512000` master/calibration identity, and matching `.cuw/.cal`
  payload remain unresolved. RKS `SeedValue` is still bounded to uppercase-hex
  serialization of a pre-existing 16-byte native CUW input. Canonical:
  [../tooling/techstream.md](../tooling/techstream.md).
- **Techstream MACKey vehicle protocol (2026-08-10).** Recovered the VIN,
  MAC-tuple, safe-key identity, master/slave discovery, response association,
  Routine-`0x3002` M1–M3 write, and M4/M5 poll. It shares the Sienna command-8
  envelope but is not an exact WDBI-DID-`0x1010` join. Canonical:
  [../security/mackey-registration.md](../security/mackey-registration.md).
- **Vance candidate-f05 payload (2026-08-10).** Recovered as a full 32 KiB
  DataFlash dump with unchanged CAN `0x7A9` word-frame transport and a post-dump
  reset call, not an ICU-S/key-slot probe. Canonical:
  [../security/secoc/candidate-f05-payload.md](../security/secoc/candidate-f05-payload.md).
- **SID `0xAB` closure (2026-07-30).** Disproved the RID-based
  calibration/flash hypothesis. `0xAB` is an event-record service with a closed
  configured indirect graph; the separate 13-entry RID worker has no stock
  diagnostic entry. Canonical:
  [../diagnostics/application.md](../diagnostics/application.md).
