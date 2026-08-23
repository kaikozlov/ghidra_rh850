# Analysis status matrix

Current multidimensional status for the Sienna `8965B4512000` analysis. This
page is a denominator/index, not a claim ledger or priority order: use
[FINDINGS.md](FINDINGS.md) for claim scope/confidence,
[OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) for the exhaustive unresolved ledger,
[PRIORITIES.md](PRIORITIES.md) for the current execution queue, and subsystem
reports for interpretation.

Snapshot date: **2026-08-15**. Corrected normalized project-inventory SHA-256:
`19d5a7fc1c0465b6ab62936e5f12fc95f130197ee3e095f77215c982b11f02c8`.
The inventory was produced byte-identically by two separately invoked four-stage
rebuilds. Committed-project promotion is a separate final lifecycle gate.

## Firmware and graph coverage

| Dimension | Current value | Evidence boundary and source |
|---|---:|---|
| Firmware bytes mapped | CodeFlash 1,048,576 B; DataFlash 32,768 B | Exact published/committed binaries; SHA-256 `21140bbd…fde` and `81d87b67…ecb8`; SECOC-044 identifies a unique one-bit CodeFlash region-1 inconsistency at `0xBB1C4 A2→82` whose reconstruction restores the stock boot CRC and local instruction semantics. The committed artifact remains unchanged for provenance; project inventory records 14 memory blocks including mapped overlays |
| Decoded CodeFlash instructions | 183,240 | Ghidra listing total in `data/ghidra_project_inventory.baseline.jsonl`; this is decode coverage, not semantic coverage |
| Decoded instructions outside functions | 17,147 instructions / 48,164 bytes | `data/outside_function_summary.json`; conservative runs can include data decoded as instructions |
| Known function entries | 6,376 | Byte-identical two-rebuild project inventory; zero undefined bytes applies inside these function bodies only |
| Validated indirect callback tables | 12 tables / 456 nonzero target pointers | `AssertFunctionDiscoveryFloor.java` against firmware bytes; includes the prior XCP/RoutineControl/RDBI tables plus three dispatch-proven COM deadline-monitor callback tables at `0x28524`, `0x28558`, and `0x286D0` |
| Bounded pointer wrappers | 6 | Processor function-discovery assertion; structural wrapper references, not callback semantics |
| Unresolved outside-function candidates | 1,665 total: 703 orphan decoded runs, 962 pointer-referenced runs | `data/outside_function_summary.json`; adjudication is 1,605 `unresolved` plus 60 `unresolved-reviewed` |
| Indirect-dispatch resolution | 456 nonzero pointers in the 12 proven tables resolve to exact function entries; direct-call gaps 0 and constant-veneer target gaps 0 | Processor assertion. This is not a denominator for every possible computed call in the image |
| Dense `0x27C88` pointer cluster | 60 targets remain unresolved-reviewed | No executable walker/computed-call consumer is evidenced; they are not promoted from pointer shape alone |

## Semantic and verification coverage

| Dimension | Current value | Evidence boundary and source |
|---|---:|---|
| Functions reviewed | 119 / 6,376 | `data/semantic_coverage_summary.json`; review does not imply understanding |
| Functions semantically identified | 29 | Curated `semantically_identified` state; 3 more are `structurally_bounded` |
| Functions with a semantic evidence grade | 32 | 3 bounded, 11 recovered, 18 verified; 6,344 carry no semantic grade |
| Functions still unreviewed | 6,257 | Structural denominator from the semantic coverage ledger |
| Reproducible selected sweep | 100 functions | Scalar top 40 plus structural strata and mandatory graph families; two decompilation artifacts are byte-identical |
| Selected sweep without semantic conclusion | 87 | `reviewed_unknown`, no evidence grade; successful decompilation is a generated self-check only |
| Per-function claim execution status | 114 `passed`, 5 `unavailable`, 0 `failed` | `data/semantic_review_status.csv`; `unavailable` marks manual CFG reviews with no automated execution gate |
| Strongest independent oracle per reviewed function | 28 CFG/data-flow, 3 instruction semantics, 1 raw-byte oracle, 87 none | The 87 have only a generated self-check, which is recorded separately and confers no semantic grade |
| Findings with exact `verified` grade | 90 | Exact-grade rows in `FINDINGS.md`; qualified/mixed/partial-grade rows are not included in this scalar |
| Findings dynamically observed | 2 | SECOC-030 external partner observation and VAR-001 Corolla field probes; neither is promoted to Sienna `4512000` firmware fact |

For material findings, `FINDINGS.md` identifies the claim-specific gate in its
`Checked by` column; `verification.toml` supplies that gate's oracle class, and
`make verify-agent` reports current `pass`/`fail`/`skip` execution status.
Execution status and confidence are deliberately separate: a passing identity,
documentation, or generated-self-check suite cannot independently justify a
semantic `verified` grade. External suites report `skip` when their pinned
artifact is absent and `required-external` converts that absence to failure.

## Techstream and DDB coverage

| Dimension | Current value | Evidence boundary and source |
|---|---:|---|
| Techstream artifacts pinned/analyzed | 45 | `techstream.lock.json`, distribution V18.00.003; proprietary files remain ignored and are never committed |
| DDB directories structurally parsed | 3 regional type-1 master directories: 67 NA / 67 EU / 76 JP sections | `parse_master_db()` boundary in `docs/tooling/techstream-ddb-pipeline.md` |
| ECU DDB sections structurally parsed | 25,361 sections across 1,368 format-2 databases | Complete type-2 directory walk; structural parsing does not name every field |
| Steering corpus structurally inventoried | 35 files / 25 structural payload variants | `data/generated/techstream_v18/steering_diagnostic_corpus.json`; “variant” is raw structural identity, not semantic identity |
| Priority section classes with consumer-backed fields | 11 classes; 76 section instances / 6,521 records | `data/generated/techstream_v18/priority_steering_ddb_semantics.json`; unknown bytes remain in `raw_hex` |
| Factory identities recovered | 89 format-1 and 151 format-2 cases | `data/generated/techstream_v18/ddb_factory_table_map.json`, independently extracted from executable switch targets |
| Priority steering master routes recovered | 3 named families | `EPS_P4DK3` record 294/category 317, `EMPS_P5` record 374/category 405/generation 20, `EPS_CAN_P4DK` record 496/category 581; exact DLL/function/detail joins in `toyota_master_routes.json` |
| Targeted application-interface correlations | 1 accepted / 1 ambiguous / 1 rejected-direct-name | `application_interface_correlations.json`: monitor 402 `Command Value Torque` accepted for command-domain corroboration; monitor 60 ambiguous; monitor 403 rejected as a direct CAN-field name |
| Live official Techstream↔`8965B4512000` flows captured | 0 | Matching vehicle/calibration session unavailable; static host/firmware intersections are bounded, not a transcript |
| Exact cross-variant/target-generation transfers verified | 2 tracked foreign CodeFlash regressions (`8965H1202000`, Span 2026-08-21) | `8965H1202000` independently transfers the Gate-2 semantic/CRC resolver, crypto roots, boot-SA shape, runtime control discovery, CAN1 continuity, and asynchronous PROGRAMMING architecture while correctly failing the Sienna steering-profile capability check. Span's persisted third specimen independently verifies the no-auth XCP high-LocalRAM write geometry plus live application→boot retention path and corrected direct `(bus1,param1)` PROGRAMMING acquisition. `4514000` and newer F3/F4 targets remain artifact/evidence bounded |

## Interpretation

The largest remaining gap is semantic, not disassembly: 6,376 function entries
are known, but 6,257 have no curated review and only 32 have a semantic grade.
The outside-function ledger also prevents the known-function count from being
presented as a complete executable denominator. On the external side, static
Techstream and DDB coverage is broad and reproducible when the pinned corpus is
available. One command-domain correlation now exceeds family-name similarity by
matching master route, 16-bit width, `Nm` unit, public DBC geometry, and recovered
firmware data flow; it remains external corroboration rather than a live target
transcript. Exact live target transcripts remain absent, but exact static transfer is no longer
zero: tracked `8965H1202000` is the first foreign CodeFlash regression. A second
foreign target with applicable `0x2E4/0x131` steering profiles is still missing.
