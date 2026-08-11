# Research roadmap

What to investigate next, in rough priority order. Completed items move to
[FINDINGS.md](FINDINGS.md); newly-discovered unknowns move to
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

## Near-term (static, this repo)

1. **Resolve the command-to-current-reference edge.** The independent d/q
   current-control-to-TSG3-PWM path is recovered, but authenticated command
   exports and snapshots have no recovered static consumer in the current
   reference generator. Focus on computed/table-driven transfer and scheduler
   handoffs around `0x37712`, not broad arithmetic-function naming. Canonical:
   [../architecture/control-partition.md](../architecture/control-partition.md).
2. **Resolve exact phase-sample acquisition SFR names.** The indexed
   `0xFEEF81E0`/`0xFEEF8A20` result windows feed the current pipeline, but their
   exact P1M-E module/register identity is bounded.
3. **Semantic coverage long-tail.** Move `recovered` rows in
   `data/semantic_coverage_ledger.csv` toward behaviorally understood where
   they intersect security, diagnostics, or torque.

## Requires a provisioned Sienna (dynamic)

4. **Run the SecOC provisioned-unit experiment.** Filter NvM blocks 41/45/49,
   observe async completion, compare RAM mirror and post-write DataFlash,
   instrument ICU slot 4, validate candidates against synchronized CAN oracle
   data. Specified in
   [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

## Requires Corolla artifacts

5. **Confirm/deny the Sienna template on `8965F1208000` firmware.** MCU, SA
   implementation/secret location, payload format, and SecOC implementation.
   Direct field diagnostics are already mapped; do not repeat those probes.
   See [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md)
   for the structured checklist.
6. **Test the separate 2023-US public-route specimen's DataFlash.** The CAN
   oracle is already public and recovered (`0x00F` + protected-family
   `0x116`/`0x24D` on bus 1), and the complete offline analyzer is ready:
   all-window entropy ranking, known NvM physical validity, raw/XOR55/XORAA
   redundant-object consensus, object-15 geometry comparison, and independent
   sync/per-ID key-domain classification. Acquire only the already-reported
   completed 32 KiB DataFlash dump plus exact EPS `F181`; no new CAN trace is
   required for the initial cryptographic test. Canonical:
   [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md),
   [../tooling/toyota-dataflash-analysis.md](../tooling/toyota-dataflash-analysis.md).
7. **Populate the TSS 3.0 family matrix.** Extend
   `data/tss3_eps_variant_matrix.csv` as additional variant firmware becomes
   available. Canonical: [../variants/tss3-family-comparison.md](../variants/tss3-family-comparison.md).

## Tooling

8. **Documentation site** (optional, after this reorganization). Material for
   MkDocs: explicit navigation, section index pages, search. Do only after
   canonical ownership is stable — search over duplicated docs just makes the
   inconsistency easier to find.
9. ~~**Link checking** in CI for `docs/` internal cross-references.~~ **Done** —
   `tests/verify_doc_links.py` runs in `make verify`.

## Completed static investigations

- **Application COM long-tail closure (2026-08-10).** Classified all 242 Rx
  signal IDs (145 positive extractions + 97 deterministic no-COM-extraction
  rows), recovered the post-packer Toyota checksum producer for Tx signals
  9/37, closed signal 57 as default-only zero in this calibration, and joined
  the special class-5 Rx `0x7F7` / Tx `0x7F8` transport channel without
  inventing service semantics. Canonical: [../communications/application-rx.md](../communications/application-rx.md),
  [../communications/application-tx.md](../communications/application-tx.md).
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
- **Techstream Stage-3 static residuals (2026-08-10).** Recovered both shipped
  `ptshim32` J2534 log formats plus Techstream's timestamped save orchestration
  and added a cross-version parser; reconciled the DDB status so the complete
  type-2 structural corpus is no longer described as undecoded, bounded
  `Security_P4`'s previously suspicious high-value tables to alarm/security
  vocabulary, and isolated type-1 `Toyota.ddb` as the remaining master-schema
  residual; traced RKS `SeedValue` to uppercase-hex serialization of a
  pre-existing 16-byte native CUW input, with only its indirect upstream
  producer unresolved. A bounded local calibration/variant search still found
  no matching Sienna `.cuw`/`.cwe`, `4514000` CodeFlash, or Corolla firmware.
  Canonical: [../tooling/techstream.md](../tooling/techstream.md).
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
