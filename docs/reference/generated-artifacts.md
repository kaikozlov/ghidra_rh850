# Generated artifacts

The CSVs under `data/` are the machine-readable canonical maps. The Markdown
reports explain how to read them; the CSVs enumerate exact rows.

There are **two classes** of `data/` CSV, with opposite editing rules:

- **Generated artifacts** — produced by a `tools/` generator. **Regenerate,
  never hand-edit.** Hand edits are silently overwritten on the next
  regeneration.
- **Curated evidence tables** — hand-maintained. **Edit intentionally** and
  validate with the associated test. These capture evidence (field probes,
  external sources) that no generator can produce.

## Generated artifacts (regenerate; never hand-edit)

| Artifact | Contents | Generator | Verified by |
|---|---|---|---|
| `data/dataflash_nvm_records.csv` | All 122 physical DataFlash records with logical owners | `tools/generate_dataflash_layout.py` (`make generate-dataflash`) | `tests/verify_dataflash_layout.py` |
| `data/checkpoint_payload_map.csv` | All 32 checkpoint descriptors, direct writers, structural layouts, evidence limits | `tools/generate_checkpoint_payload_map.py` (`make generate-dataflash`) | `tests/verify_dataflash_semantics.py` |
| `data/application_diagnostic_map.csv` | Per-SID diagnostic routing, session policy, callbacks/subfunction tables, evidence status (17 SIDs) | `tools/generate_application_diagnostic_map.py` (`make generate-application-diagnostics`) | `tests/verify_application_diagnostics.py` |
| `data/application_rx_map.csv` | 47 normal Rx I-PDUs, 242 COM signals | `tools/generate_application_rx_map.py` (`make generate-application-receive`) | `tests/verify_application_receive.py` |
| `data/application_rx_signal_evidence.csv` | RX signal extraction evidence (drives the RX map generator) | `tools/generate_application_rx_signal_evidence.sh` (`make generate-application-receive-evidence`) | `tests/verify_application_receive.py` |
| `data/semantic_coverage_ledger.csv` | Whole-image recovered-function ledger (5,845 rows) with evidence grades | `make generate-semantic-coverage` | `make verify-processor` floors |
| `data/ram_overlay_map.csv` | LocalRAM overlay inventory | generated at import | `make verify-processor` |
| `data/object15_reachability.csv` | Object-15 caller census | `tools/generate_object15_reachability.py` | `tests/verify_boot_trust.py` |

## Curated evidence tables (edit intentionally; validate with tests)

| Artifact | Contents | Verified by |
|---|---|---|
| `data/tss3_eps_variant_matrix.csv` | Sienna/Corolla and TSS 3 EPS variant comparison (evidence-graded; `unknown` for unobserved) | `tests/verify_tss3_variant_matrix.py` |
| `data/control_partition.csv` | Control/safety cyclic-partition map | `tests/verify_control_partition.py` |
| `data/p1m_sfr_labels.csv` | P1M-E SFR labels used by the device profile | `make verify-processor` |

## Rule

CSVs enumerate. Reports explain. Tests prove. If a Markdown table duplicates
hundreds of CSV rows, the CSV is canonical and the Markdown should be
regenerated or trimmed to orientation.

If you are unsure which class a CSV belongs to, check whether a
`tools/generate_*` script writes it. If yes → generated. If no → curated.
