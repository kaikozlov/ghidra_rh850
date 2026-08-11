# Generated artifacts

The CSVs under `data/` are the machine-readable canonical maps. The Markdown
reports explain how to read them; the CSVs enumerate exact rows.

There are **two classes** of `data/` CSV, with opposite editing rules:

- **Generated artifacts** — produced by a `tools/` generator or the rebuild /
  processor-verify scripts. **Regenerate, never hand-edit.** Hand edits are
  silently overwritten on the next run.
- **Curated evidence tables** — hand-maintained. **Edit intentionally** and
  validate with the associated test. These capture evidence (field probes,
  external sources, manual baselines) that no generator can produce.

This page is an exhaustive inventory of every committed `data/` CSV. If you
are unsure which class a CSV belongs to, check whether a `tools/generate_*`
script or `tools/verify_processor.sh` writes it. If yes → generated. If no →
curated.

## Generated artifacts (regenerate; never hand-edit)

| Artifact | Contents | Generator | Verified by |
|---|---|---|---|
| `data/dataflash_nvm_records.csv` | All 122 physical DataFlash records with logical owners | `tools/generate_dataflash_layout.py` (`make generate-dataflash`) | `tests/verify_dataflash_layout.py` |
| `data/checkpoint_payload_map.csv` | All 32 checkpoint descriptors, direct writers, structural layouts, evidence limits | `tools/generate_checkpoint_payload_map.py` (`make generate-dataflash`) | `tests/verify_dataflash_semantics.py` |
| `data/application_diagnostic_map.csv` | Per-SID diagnostic routing, session policy, callbacks/subfunction tables, evidence status (17 SIDs) | `tools/generate_application_diagnostic_map.py` (`make generate-application-diagnostics`) | `tests/verify_application_diagnostics.py` |
| `data/application_rx_map.csv` | 47 normal Rx I-PDUs, 242 COM signals | `tools/generate_application_rx_map.py` (`make generate-application-receive`) | `tests/verify_application_receive.py` |
| `data/application_rx_signal_evidence.csv` | RX signal extraction evidence (drives the RX map generator) | `tools/generate_application_rx_signal_evidence.sh` (`make generate-application-receive-evidence`) | `tests/verify_application_receive.py` |
| `data/semantic_coverage_ledger.csv` | Whole-image recovered-function ledger (5,921 rows) with evidence grades | `tools/generate_semantic_coverage_ledger.sh` (`make generate-semantic-coverage`) | `tests/verify_semantic_coverage.py` |
| `data/object15_reachability.csv` | Object-15 caller census | `tools/generate_object15_reachability.py` | `tests/verify_boot_trust.py` |
| `data/instruction_inventory.csv` | Whole-image instruction inventory emitted during processor verification | `tools/verify_processor.sh` (`make verify-processor`) | `make verify-processor` |
| `data/ghidra_project_inventory.baseline.jsonl` | Canonical path-free project identity: tool/program metadata, memory mappings, complete function signatures/storage, user symbols, comments, bookmarks, and totals | `tools/generate_project_inventory.sh`; two independent rebuilds required by `make update-project-baseline` | `make verify-project-parity` |
| `data/switch_table_inventory.csv` | Recovered RH850 `switch` jump-table inventory | `InventorySwitchTables.java` (via rebuild / `make verify-processor`) | `AssertSwitchTables.java` (`make verify-processor`) |
| `data/ram_overlay_map.csv` | LocalRAM overlay inventory | generated at import (`ApplyRamTypes.java`) | `make verify-processor` |

## Curated evidence tables (edit intentionally; validate with tests)

| Artifact | Contents | Verified by |
|---|---|---|
| `data/application_tx_map.csv` | 58-row application TX signal map | `tests/verify_application_transmit.py` |
| `data/application_security_consumers.csv` | Application security-consumer scan results backing the "no configured gating" finding | `tests/verify_security_consumers.py` |
| `data/application_routine_id_callbacks.csv` | The 13-entry stock-gated control-ID subset, direct-target census, and state-mediated object-`0x101/102/103` persistence boundary; distinct from SID `0xAB` | `tests/verify_application_routine_id_callbacks.py` |
| `data/control_partition.csv` | Control/safety cyclic-partition map | `tests/verify_control_partition.py` |
| `data/tss3_eps_variant_matrix.csv` | Sienna/Corolla and TSS 3 EPS variant comparison (evidence-graded; `unknown` for unobserved) | `tests/verify_tss3_variant_matrix.py` |
| `data/p1m_sfr_labels.csv` | P1M-E SFR labels used by the device profile | `make verify-processor` |
| `data/scheduler_periods.csv` | Cyclic-task scheduler period evidence | `tests/verify_scheduler_timing.py` |
| `data/decompiler_signatures.baseline.csv` | Decompiler-signature baseline diffed against the working project | `tools/verify_processor.sh` (`make verify-processor`) |
| `data/renesas_rfp_rv40f_commands.csv` | Complete 52-ID RV40F host-command census: request/response layouts, callers, preconditions, and result handling | `tests/verify_renesas_rfp.py` |
| `data/renesas_rfp_rv40f_capabilities.csv` | Structural decoder for the 8-byte `GetDeviceType` capability/type-code vector and internal `0x1001..0x1212` keys | `tests/verify_renesas_rfp.py` |

## Rule

CSVs enumerate. Reports explain. Tests prove. If a Markdown table duplicates
hundreds of CSV rows, the CSV is canonical and the Markdown should be
regenerated or trimmed to orientation.
