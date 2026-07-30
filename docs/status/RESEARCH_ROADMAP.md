# Research roadmap

What to investigate next, in rough priority order. Completed items move to
[FINDINGS.md](FINDINGS.md); newly-discovered unknowns move to
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md).

## Near-term (static, this repo)

1. **Resolve the 97 configured-unresolved RX signals.** Bounded but not
   producer-mapped. Canonical: [../communications/application-rx.md](../communications/application-rx.md).
2. **Motor-control cluster behavioral analysis.** The `0x47C3C/0x32B80/0xB98BC`
   cluster is structurally mapped only. Relevant to openpilot torque-path
   understanding. Canonical: [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md).
3. **Semantic coverage long-tail.** Move `recovered` rows in
   `data/semantic_coverage_ledger.csv` toward behaviorally understood where
   they intersect security, diagnostics, or torque.

## Requires a provisioned Sienna (dynamic)

5. **Run the SecOC provisioned-unit experiment.** Filter NvM blocks 41/45/49,
   observe async completion, compare RAM mirror and post-write DataFlash,
   instrument ICU slot 4, validate candidates against synchronized CAN oracle
   data. Specified in
   [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

## Requires Corolla firmware

6. **Confirm/deny the Sienna template on `8965F1208000`.** MCU, SA levels,
   secret location, payload format, diagnostic endpoints, SecOC profile. See
   [../variants/corolla-8965F1208000.md](../variants/corolla-8965F1208000.md)
   for the structured checklist.
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

- **SID `0xAB` closure (2026-07-30).** Disproved the RID-based
  calibration/flash hypothesis. `0xAB` is an event-record service with a closed
  configured indirect graph; the separate 13-entry RID worker has no stock
  diagnostic entry. Canonical:
  [../diagnostics/application.md](../diagnostics/application.md).
