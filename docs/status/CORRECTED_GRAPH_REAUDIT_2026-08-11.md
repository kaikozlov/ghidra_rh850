# Corrected-graph whole-image re-audit — 2026-08-11

This is the canonical record of the Phase-I re-audit performed after recovering
the omitted direct-call and callback-table functions. It records the graph
boundary used to revisit prior caller/consumer negatives; it does not replace
the subsystem reports that own those findings.

## Rebuild identity

Two independent working projects were built with the unchanged four-stage
workflow plus calling-convention finalizer. Their normalized project
inventories were byte-identical:

| Metric | Rebuild A | Rebuild B |
|---|---:|---:|
| Functions | 6,037 | 6,037 |
| Instructions | 180,262 | 180,262 |
| Symbols | 38,069 | 38,069 |
| Memory sections | 14 | 14 |
| Inventory SHA-256 | `7b7873b64cf07470bda2903cd22dc1d37be0af1c1ac7e13eb224a0d2da2f7100` | same |

The guarded two-rebuild updater produced
`data/ghidra_project_inventory.baseline.jsonl`. Processor verification then
passed with 6,037 functions and zero undefined function bytes. The only
decompiler-baseline delta was `0x8B1F0`: its direct callee acquired the durable
seed name `direct_call_target_0008b1d4`; control flow was unchanged. Promotion
of the working project into committed `project/` remains deliberately deferred
to the final snapshot gate.

The regenerated outside-function inventory contains 2,091 conservative
candidates: 854 orphan decoded runs and 1,237 pointer-referenced code runs.
2,031 remain `unresolved`; 60 pointer targets at `0x74BC4..0x74E64` remain
`unresolved-reviewed`. Those 60 targets are not promoted to functions because
the image still provides no executable table walker or computed-call consumer
for the dense `0x27C88` pointer cluster. Plausible decoding and pointer shape
alone are insufficient.

## Corrected graph review

Exact live caller/callee and reference queries against rebuild A established
the following boundaries:

| Entry or family | Corrected-graph observation | Disposition |
|---|---|---|
| `0x17C8` | direct caller `0x1338`; no callees | retained in graph review |
| `0x64414` | direct caller `0x62232` | retained; semantics unresolved |
| `0xB603A` | callers `0xBEC4C` and `0xBF17E` | both full/reduced system-mode paths retained |
| `0x32868` | caller `0x33198` | retained; semantics unresolved |
| `0x35B86`, `0x35D1E` | three and two callers respectively | mirrored calibration-driven state-calculator interpretation retained |
| `0x5E572` | caller `0x57AC2`; 137 callees | high-fan-out dispatcher boundary retained |
| `0x5CEE6` | caller `0x5784C`; 107 callees | motor/control dispatcher boundary retained |
| `0x5B740` | caller `0x578DE` | reviewed; exact semantics unresolved |
| `0x5BEA6` | caller `0x57980` | bounded RAM snapshot/copy interpretation retained |
| `0xBE8E6` | caller `0xFDC8C` | bounded RAM snapshot/copy interpretation retained |
| `0x916E2`, `0x8FFCC` | `0x8FFCC` calls `0x916E2`; `0x916E2` has 34 callees; `0x8FFCC` is called by `0x8F4C4` and `0x8F656` | multi-state dispatcher boundary retained; service semantics unnamed |
| `0x9729A..0x976F4` | zero direct callers; exact data references from dispatch table `0x2B3F0` | seven computed-call XCP-shaped handlers retained |
| `0x74BC4..0x74E64` | pointer-shaped targets only; no evidenced executable consumer | remain `unresolved-reviewed`, not functions |

The XCP family's zero direct-caller count is expected: `0x97160` selects the
seven handlers from `0x2B3F0` and invokes them through computed `jarl`. Direct
caller count therefore cannot be used as an activation oracle for this family.

## Claim-family regression matrix

The affected whole-image conclusions were rerun with claim-specific tests, not
mere function-presence checks:

| Review class | Deterministic gate(s) | Assertions |
|---|---|---:|
| Boot trust and callback paths | `verify_boot_trust.py` | 54 |
| Application key/secret consumers | `verify_security_consumers.py` | 58 |
| Memory-safety reachability and destructive sensitivity | `verify_memory_safety.py`, `verify_memory_safety_mutations.py` | 59 |
| SecOC writers, consumers, and dormant paths | `verify_secoc_application.py`, `verify_secoc_nvm.py`, `verify_secoc_security_properties.py` | 189 |
| ICU-S Stage-7 paths and consumer boundaries | `verify_icus_key_recovery_surface.py`, `verify_icus_key_update.py`, `verify_icus_software_paths.py`, `verify_icus_stage7_static.py` | 167 |
| Motor/control joins | `verify_motor_actuation_boundary.py`, `verify_control_partition.py` | 114 |
| Diagnostic SID/RID/DID callbacks | `verify_application_diagnostics.py`, `verify_application_routine_id_callbacks.py`, `verify_did_model.py` | 417 |
| Scheduler, receive, transmit roots | `verify_scheduler_timing.py`, `verify_application_receive.py`, `verify_application_transmit.py` | 157 |
| Function-discovery floor and callback dispatch | `verify_function_discovery.py` | 24 |

All 1,239 Python assertions passed; the processor's Ghidra-side callback-table
and function-discovery assertions also passed. No reviewed whole-image negative was invalidated by
the corrected graph. Existing claims remain subject to their already-published
boundaries: representation-bounded byte searches are not runtime-absence
proofs, enumerated memory-safety negatives are not whole-image absence claims,
and the authenticated-command-to-motor join remains a bounded static negative.
No new `disproved` entry is therefore required for this phase.

## Reproducible semantic sweep

`data/generated/semantic_interest_ranking.csv` ranks all 6,037 functions using
the checked-in weighted formula. The selected cohort contains 100 functions:
the scalar top 40, structural strata, the five previously mandated stateful
routines, all starting functions above, and all seven XCP handlers. The exact
selected set and reasons are pinned by `tests/verify_semantic_interest_ranking.py`.

`tools/generate_semantic_sweep.py` decompiled all 100 entries from both
independent rebuilds. The two JSONL artifacts were byte-identical with SHA-256
`231c41d409e126eecee883b054f82494af7cfe9d4ee97a8942c83a1ea7480bc2`.
Every selected function has a curated disposition:

| Review state | Selected functions | Meaning |
|---|---:|---|
| `semantically_identified` | 9 | role supported by existing recovered evidence |
| `structurally_bounded` | 3 | structure constrained; exact semantics unnamed |
| `reviewed_unknown` | 88 | decompiled successfully; no independent semantic conclusion |

The 88 `reviewed_unknown` rows deliberately carry no evidence grade. Their
`generated_self_check` oracle proves reproducible selection and decompilation,
not semantic understanding. Whole-ledger totals are 109 reviewed functions,
21 with bounded or identified semantics, and 5,928 unreviewed functions.

## Result

Source: firmware-static plus generated-artifact. Confidence: **verified** for
the two-rebuild identity, selected-set/decompilation reproducibility, callback
dispatch structure, and regression execution; **bounded** for negative search
conclusions at their named scopes. Canonical subsystem meanings remain in the
linked `FINDINGS.md` reports.
