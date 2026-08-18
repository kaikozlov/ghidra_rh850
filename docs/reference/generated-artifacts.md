# Generated artifacts

The CSV and JSON/JSONL files under `data/` are the machine-readable canonical
maps. The Markdown reports explain how to read them; the artifacts enumerate
exact rows or records.

There are **two classes** of `data/` CSV, with opposite editing rules:

- **Generated artifacts** — produced by a `tools/` generator or the rebuild /
  processor-verify scripts. **Regenerate, never hand-edit.** Hand edits are
  silently overwritten on the next run.
- **Curated evidence tables** — hand-maintained. **Edit intentionally** and
  validate with the associated test. These capture evidence (field probes,
  external sources, manual baselines) that no generator can produce.

This page inventories the committed analysis tables and their paired summaries.
If you are unsure which class an artifact belongs to, check whether a `tools/generate_*`
script or `tools/verify_processor.sh` writes it. If yes → generated. If no →
curated.

## Generated artifacts (regenerate; never hand-edit)

| Artifact | Contents | Generator | Verified by |
|---|---|---|---|
| `data/dataflash_nvm_records.csv` | All 122 physical DataFlash records with logical owners | `tools/generate_dataflash_layout.py` (`make generate-dataflash`) | `tests/verify_dataflash_layout.py` |
| `data/checkpoint_payload_map.csv` | All 32 checkpoint descriptors, direct writers, structural layouts, evidence limits | `tools/generate_checkpoint_payload_map.py` (`make generate-dataflash`) | `tests/verify_dataflash_semantics.py` |
| `data/application_diagnostic_map.csv` | Per-SID diagnostic routing, session policy, callbacks/subfunction tables, evidence status (17 SIDs) | `tools/generate_application_diagnostic_map.py` (`make generate-application-diagnostics`) | `tests/verify_application_diagnostics.py` |
| `data/application_proprietary_ba_surface.csv` | Application SID-`0xBA` ten-operation descriptor matrix, effective local gates, persistence class, and bounded downstream state | `tools/generate_application_proprietary_ba_surface.py` | `tests/verify_application_proprietary_ba.py`, `tests/verify_application_proprietary_ba_live.py` |
| `data/application_rx_map.csv` | 47 normal Rx I-PDUs, 242 COM signals | `tools/generate_application_rx_map.py` (`make generate-application-receive`) | `tests/verify_application_receive.py` |
| `data/application_rx_signal_evidence.csv` | Complete RX signal extraction/classification evidence (drives the RX map generator) | `tools/generate_application_rx_signal_evidence.sh` (`make generate-application-receive-evidence`) | `tests/verify_application_receive.py` |
| `data/application_tx_map.csv` | 58-row application TX signal map including post-packer/default-only closure | `tools/generate_application_tx_map.py` (`make generate-application-transmit`) | `tests/verify_application_transmit.py` |
| `data/outside_function_candidates.csv` | Conservative decoded-CodeFlash runs outside known functions, including evidence class and adjudication state | `tools/generate_outside_function_candidates.sh` (`make generate-function-discovery`) | `tests/verify_function_discovery.py` |
| `data/semantic_coverage_ledger.csv` | Whole-image structural function ledger (6,376 rows) with review state kept separate from evidence grade | `tools/generate_semantic_coverage_ledger.sh` (`make generate-semantic-coverage`) | `tests/verify_semantic_coverage.py`, `tests/verify_semantic_coverage_live.py` |
| `data/generated/semantic_interest_ranking.csv` | Deterministic all-function interest ranking plus exact selected sweep cohort and selection strata | `tools/generate_semantic_interest_ranking.py` | `tests/verify_semantic_interest_ranking.py` |
| `data/generated/semantic_sweep_decompilations.jsonl` | Normalized decompilations and selection provenance for all 100 selected functions | `tools/generate_semantic_sweep.py` (`make generate-semantic-sweep PROJECT_DIR=…`) | `tests/verify_semantic_sweep.py` |
| `data/generated/decompilations.jsonl` | Whole-image pseudocode for all 6,376 functions plus canonical non-flow instruction/data references for alias-resistant RAM lookup | `tools/generate_decompiler_corpus.py` (`make generate-decompiler-corpus PROJECT_DIR=…`) | `tests/verify_decompiler_corpus.py` |
| `data/generated/secoc_gate_resolution_4512000.json` | Strong semantic Gate-2 resolver result from the annotated Sienna working project, including program SHA, mapped MAC-result provenance, synthesized local CMP-neutralization patch, preserved BNE, and verified/mismatch convergence | `ResolveSecocAcceptanceGate.java` via `tools/g` | `tests/verify_secoc_semantic_patch_resolver.py` |
| `data/generated/secoc_gate_resolution_4512000_minimal.json` | Same semantic resolver run against a fresh unannotated CodeFlash-only Ghidra import; proves the target survives without repository annotations while explicitly leaving RAM provenance unmapped | `ResolveSecocAcceptanceGate.java` via `tools/run_headless --with-investigate` | `tests/verify_secoc_semantic_patch_resolver.py` |
| `data/generated/secoc_gate_resolution_8965H1202000_minimal.json` | First tracked foreign fresh-import Gate-2 result: Corolla `8965H1202000`, unique CMP neutralization at `0x88C62`, normalized-image SHA bound | `ResolveSecocAcceptanceGate.java` via `tools/resolve_ephemeral_runtime_image.sh` | `tests/verify_albinoelephant_corolla_codeflash.py`, `tests/verify_ephemeral_runtime_resolver.py` |
| `data/generated/ephemeral_runtime_resolution_4512000_minimal.json` | Fresh Sienna callback-free startup/scheduler semantic skeleton before raw completion | `ResolveEphemeralRuntime.java` via `tools/resolve_ephemeral_runtime_image.sh` | `tests/verify_ephemeral_runtime_resolver.py` |
| `data/generated/ephemeral_runtime_target_manifest_4512000.json` | Joined Sienna target contract: raw queue/table/COM completion, verified RAM geometry, bootstrap profile, build-ready `0x2E4/0x131` bridge profiles | `tools/build_ephemeral_runtime_manifest.py` | `tests/verify_ephemeral_runtime_resolver.py`, `tests/verify_ephemeral_runtime.py` |
| `data/generated/ephemeral_runtime_resolution_8965H1202000_minimal.json` | Fresh foreign callback-free startup/scheduler semantic skeleton for tracked Corolla CodeFlash | `ResolveEphemeralRuntime.java` via `tools/resolve_ephemeral_runtime_image.sh` | `tests/verify_ephemeral_runtime_resolver.py` |
| `data/generated/ephemeral_runtime_target_manifest_8965H1202000.json` | Joined foreign capability result: queue helper/table/count and `00F/D7/B6` records resolved; `2E4/131` absent, therefore `semantic-resolved-steering-unsupported` | `tools/build_ephemeral_runtime_manifest.py` | `tests/verify_ephemeral_runtime_resolver.py`, `tests/verify_albinoelephant_corolla_codeflash.py` |
| `data/generated/secoc_patch_manifest_4512000.json` | Exact-image patch manifest joining the semantic result to CodeFlash SHA/preimage and dynamically discovered boot-CRC descriptor/fixup/marker/FCU geometry | `tools/build_secoc_patch_manifest.py` | `tests/verify_secoc_semantic_patch_resolver.py` |
| `data/object15_reachability.csv` | Object-15 caller census | `tools/generate_object15_reachability.py` | `tests/verify_boot_trust.py` |
| `data/instruction_inventory.csv` | Whole-image instruction inventory emitted during processor verification | `tools/verify_processor.sh` (`make verify-processor`) | `make verify-processor` |
| `data/ghidra_project_inventory.baseline.jsonl` | Canonical path-free project identity: tool/program metadata, memory mappings, complete function signatures/storage, user symbols, comments, bookmarks, and totals | `tools/generate_project_inventory.sh`; two independent rebuilds required by `make update-project-baseline` | `make verify-project-parity` |
| `data/switch_table_inventory.csv` | Recovered RH850 `switch` jump-table inventory | `InventorySwitchTables.java` (via rebuild / `make verify-processor`) | `AssertSwitchTables.java` (`make verify-processor`) |
| `data/ram_overlay_map.csv` | LocalRAM overlay inventory | generated at import (`ApplyRamTypes.java`) | `make verify-processor` |

Generated JSON summaries paired with the tables above include
`data/outside_function_summary.json` and
`data/semantic_coverage_summary.json`; their corresponding table verifiers
check both files.

## Curated evidence tables (edit intentionally; validate with tests)

| Artifact | Contents | Verified by |
|---|---|---|
| `data/application_security_consumers.csv` | Application security-consumer scan results backing the "no configured gating" finding | `tests/verify_security_consumers.py` |
| `data/application_wdbi_callbacks.csv` | The 13-entry active SID-`0x2E` callback table, direct-target census, and state-mediated object-`0x101/102/103` persistence boundary | `tests/verify_application_wdbi_callbacks.py` |
| `data/application_wdbi_surface.csv` | WDBI membership, payload width, session/SA/speed gates, callback pairs, persistence class, and live-state side effects | `tests/verify_application_wdbi_surface.py`, `tests/verify_application_wdbi_surface_live.py` |
| `data/control_partition.csv` | Control/safety cyclic-partition map | `tests/verify_control_partition.py` |
| `data/motor_actuation_path.csv` | Motor acquisition/current/PWM path and bounded authenticated-command→d/q join census | `tests/verify_motor_actuation_boundary.py` |
| `data/motor_safety_monitors.csv` | Nine-channel plausibility/deadline monitor registration and status-vector map | `tests/verify_motor_safety_monitors.py` |
| `data/motor_calibration_handlers.csv` | CH0/CH2 calibration-handler version-domain map | `tests/verify_motor_calibration_handlers.py` |
| `data/tss3_eps_variant_matrix.csv` | Sienna/Corolla and TSS 3 EPS variant comparison (evidence-graded; `unknown` for unobserved) | `tests/verify_tss3_variant_matrix.py` |
| `data/p1m_sfr_labels.csv` | P1M-E SFR labels used by the device profile | `make verify-processor` |
| `data/scheduler_periods.csv` | Cyclic-task scheduler period evidence | `tests/verify_scheduler_timing.py` |
| `data/decompiler_signatures.baseline.csv` | Decompiler-signature baseline diffed against the working project | `tools/verify_processor.sh` (`make verify-processor`) |
| `data/semantic_review_status.csv` | Per-function curated semantic dispositions; `reviewed_unknown` records review without conferring an evidence grade | `tests/verify_semantic_coverage.py`, `tests/verify_semantic_sweep.py` |
| `data/renesas_rfp_rv40f_commands.csv` | Complete 52-ID RV40F host-command census: request/response layouts, callers, preconditions, and result handling | `tests/verify_renesas_rfp.py` |
| `data/renesas_rfp_rv40f_capabilities.csv` | Structural decoder for the 8-byte `GetDeviceType` capability/type-code vector and internal `0x1001..0x1212` keys | `tests/verify_renesas_rfp.py` |

## Rule

CSVs enumerate. Reports explain. Tests prove. If a Markdown table duplicates
hundreds of CSV rows, the CSV is canonical and the Markdown should be
regenerated or trimmed to orientation.
