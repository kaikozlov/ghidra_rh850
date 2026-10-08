# Analysis status matrix — Sienna processor refresh (2026-10-08)

Historical coverage notes for the Sienna `8965B4512000` analysis, originating
with the **2026-08-15 inventory snapshot** and including later corpus/variant
addenda. The tables are not one synchronized present-day census, a priority
order, or a live multi-target dashboard. Use [FINDINGS.md](FINDINGS.md) for
recorded claim scope/confidence, [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md) for
question references, [PRIORITIES.md](PRIORITIES.md) for the current queue, and
the [variant reports](../variants/README.md) for calibration-specific state.

Corrected normalized project-inventory SHA-256:
`c2accb82d1713565b695b75df916ca8ff62d14f6ef17f3afd244a00ad4bf027a`.
The inventory was produced byte-identically by two separately invoked four-stage
rebuilds. Committed-project promotion is a separate final lifecycle gate.

## Firmware and graph coverage

| Dimension | Snapshot value | Evidence boundary and source |
|---|---:|---|
| Firmware bytes mapped | CodeFlash 1,048,576 B; DataFlash 32,768 B | Exact published/committed binaries; SHA-256 `21140bbd…fde` and `81d87b67…ecb8`; SECOC-044 identifies a unique one-bit CodeFlash region-1 inconsistency at `0xBB1C4 A2→82` whose reconstruction restores the stock boot CRC and local instruction semantics. The committed artifact remains unchanged for provenance; project inventory records 14 memory blocks including mapped overlays |
| Decoded CodeFlash instructions | 197,726 | Ghidra listing total in `data/ghidra_project_inventory.baseline.jsonl`; this is decode coverage, not semantic coverage |
| Decoded instructions outside functions | 7,186 instructions / 18,138 bytes | `data/outside_function_summary.json`; conservative runs can include data decoded as instructions |
| Known function entries | 7,090 | Byte-identical two-rebuild project inventory; zero undefined bytes applies inside these function bodies only |
| Validated indirect callback tables | 12 tables / 456 nonzero target pointers | `AssertFunctionDiscoveryFloor.java` against firmware bytes; includes the prior XCP/RoutineControl/RDBI tables plus three dispatch-proven COM deadline-monitor callback tables at `0x28524`, `0x28558`, and `0x286D0` |
| Bounded pointer wrappers | 6 | Processor function-discovery assertion; structural wrapper references, not callback semantics |
| Unresolved outside-function candidates | 900 total: 281 orphan decoded runs, 619 pointer-referenced runs | `data/outside_function_summary.json`; all remain `unresolved` |
| Indirect-dispatch resolution | 456 nonzero pointers in the 12 proven tables resolve to exact function entries; direct-call gaps 0 and constant-veneer target gaps 0 | Processor assertion. This is not a denominator for every possible computed call in the image |
| Dense `0x27C88` pointer cluster | 60 exact pattern-recovered function entries | No executable walker/computed-call consumer is evidenced; function boundaries do not promote the array to a dispatch table |

## Semantic and verification coverage

`data/semantic_review_status.csv` records actual function-level conclusions;
`data/semantic_coverage_summary.json` summarizes their coverage. Most discovered
functions remain semantically unreviewed. Successful decompilation alone is not
a review, and the former automatic sweep rows have been removed.

Use `tools/pseudo --target sienna-8965B4512000` for this target's decompilations and
`data/generated/semantic_interest_ranking.csv` to navigate candidate functions.
Use `tools/test <suite>` to run the relevant executable or firmware check.
Neither ranking nor a passing unrelated suite establishes a function's meaning.

## Techstream and DDB coverage

| Dimension | Snapshot value | Evidence boundary and source |
|---|---:|---|
| Techstream artifacts pinned/analyzed | 45 | `software/locks/techstream-v18.json`, distribution V18.00.003; proprietary files remain ignored and are never committed |
| GTS+ source/reconstruction anchors pinned | 17 CUWPlus artifacts + source archive | `software/locks/gtsplus.json`; vendor archive/containers and reconstructed PE intermediates remain ignored, while derived evidence is tracked |
| Toyota CUW external corpus pinned | 26 packages | `software/locks/toyota-cuw-corpus.json`; package bytes remain ignored, generated corpus analysis is tracked under `data/generated/techstream_v18/` |
| DDB directories structurally parsed | 3 regional type-1 master directories: 67 NA / 67 EU / 76 JP sections | `parse_master_db()` boundary in `docs/tooling/techstream-ddb-pipeline.md` |
| ECU DDB sections structurally parsed | 25,361 sections across 1,368 format-2 databases | Complete type-2 directory walk; structural parsing does not name every field |
| Steering corpus structurally inventoried | 35 files / 25 structural payload variants | `data/generated/techstream_v18/steering_diagnostic_corpus.json`; “variant” is raw structural identity, not semantic identity |
| Priority section classes with consumer-backed fields | 11 classes; 76 section instances / 6,521 records | `data/generated/techstream_v18/priority_steering_ddb_semantics.json`; unknown bytes remain in `raw_hex` |
| Factory identities recovered | 89 format-1 and 151 format-2 cases | `data/generated/techstream_v18/ddb_factory_table_map.json`, independently extracted from executable switch targets |
| Priority steering master routes recovered | 3 named families | `EPS_P4DK3` record 294/category 317, `EMPS_P5` record 374/category 405/generation 20, `EPS_CAN_P4DK` record 496/category 581; exact DLL/function/detail joins in `toyota_master_routes.json` |
| Targeted application-interface correlations | 1 accepted / 1 ambiguous / 1 rejected-direct-name | `application_interface_correlations.json`: monitor 402 `Command Value Torque` accepted for command-domain corroboration; monitor 60 ambiguous; monitor 403 rejected as a direct CAN-field name |
| Live official Techstream↔`8965B4512000` flows captured | 0 | Matching vehicle/calibration session unavailable; static host/firmware intersections are bounded, not a transcript |
| Exact cross-variant/target-generation transfers verified | 2 tracked foreign CodeFlash regressions (`8965H1202000`, Span 2026-08-21) | the Albino corpus (historically labelled `8965H1202000`, direct app F181 `8965F1208000/8A3111202000`) independently transfers the Gate-2 semantic/CRC resolver, crypto roots, boot-SA shape, runtime control discovery, CAN1 continuity, and asynchronous PROGRAMMING architecture while correctly failing the Sienna steering-profile capability check; its 2026-08-26 telescope run independently replays the already field-observed boot SA/authenticated-RAM path while directly closing F181, PRDNAME, exact payload terminal state and Gate-2 relocation. Span's persisted third specimen independently verifies the no-auth XCP high-LocalRAM write geometry plus live application→boot retention path and corrected direct `(bus1,param1)` PROGRAMMING acquisition. `4514000` and newer F3/F4 targets remain artifact/evidence bounded |

## Interpretation (at the 2026-08-15 snapshot)

The largest remaining gap is semantic, not disassembly: 6,376 function entries
are known, but 6,257 have no curated review and only 32 have a semantic grade.
The outside-function ledger also prevents the known-function count from being
presented as a complete executable denominator. On the external side, static
Techstream and DDB coverage is broad and reproducible when the pinned corpus is
available. One command-domain correlation now exceeds family-name similarity by
matching master route, 16-bit width, `Nm` unit, public DBC geometry, and recovered
firmware data flow; it remains external corroboration rather than a live target
transcript. A direct same-car application/boot F181 transcript and authenticated-RAM probe are
now retained for the Albino specimen; live Techstream monitor/session transcripts
remain absent. Exact static transfer is also no longer zero: the tracked historical
`8965H1202000` corpus remains the first foreign CodeFlash regression. A second
foreign target with applicable `0x2E4/0x131` steering profiles is still missing.
