# Research roadmap

What to investigate next, in rough priority order. Completed items move to
[FINDINGS.md](FINDINGS.md); newly-discovered unknowns move to
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

## Near-term (static, this repo)

1. **Resolve the 97 configured-unresolved RX signals.** Bounded but not
   producer-mapped. Canonical: [../communications/application-rx.md](../communications/application-rx.md).
2. **Resolve the command-to-current-reference edge.** The independent d/q
   current-control-to-TSG3-PWM path is recovered, but authenticated command
   exports and snapshots have no recovered static consumer in the current
   reference generator. Focus on computed/table-driven transfer and scheduler
   handoffs around `0x37712`, not broad arithmetic-function naming. Canonical:
   [../architecture/control-partition.md](../architecture/control-partition.md).
3. **Resolve exact phase-sample acquisition SFR names.** The indexed
   `0xFEEF81E0`/`0xFEEF8A20` result windows feed the current pipeline, but their
   exact P1M-E module/register identity is bounded.
4. **Semantic coverage long-tail.** Move `recovered` rows in
   `data/semantic_coverage_ledger.csv` toward behaviorally understood where
   they intersect security, diagnostics, or torque.

## Requires a provisioned Sienna (dynamic)

5. **Run the SecOC provisioned-unit experiment.** Filter NvM blocks 41/45/49,
   observe async completion, compare RAM mirror and post-write DataFlash,
   instrument ICU slot 4, validate candidates against synchronized CAN oracle
   data. Specified in
   [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

## Requires Corolla artifacts

6. **Confirm/deny the Sienna template on `8965F1208000` firmware.** MCU, SA
   implementation/secret location, payload format, and SecOC implementation.
   Direct field diagnostics are already mapped; do not repeat those probes.
   See [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md)
   for the structured checklist.
7. **Test the separate 2023-US public-route specimen's DataFlash.** The CAN
   oracle is already public and recovered (`0x00F` + protected-family
   `0x116`/`0x24D` on bus 1). Acquire only the already-reported completed 32 KiB
   DataFlash dump plus exact EPS `F181`, then run the generic sliding-window
   oracle rather than collecting another CAN trace. Canonical:
   [../variants/corolla-2023-us-public-route.md](../variants/corolla-2023-us-public-route.md).
8. **Populate the TSS 3.0 family matrix.** Extend
   `data/tss3_eps_variant_matrix.csv` as additional variant firmware becomes
   available. Canonical: [../variants/tss3-family-comparison.md](../variants/tss3-family-comparison.md).

## Tooling

9. **Documentation site** (optional, after this reorganization). Material for
   MkDocs: explicit navigation, section index pages, search. Do only after
   canonical ownership is stable — search over duplicated docs just makes the
   inconsistency easier to find.
10. ~~**Link checking** in CI for `docs/` internal cross-references.~~ **Done** —
   `tests/verify_doc_links.py` runs in `make verify`.

## Completed static investigations

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
