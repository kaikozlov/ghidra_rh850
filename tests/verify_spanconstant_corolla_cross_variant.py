#!/usr/bin/env python3
"""Verify Span's independent Corolla/Sienna transfer evidence and H equivalence."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.compare_variant_application_rx import compare as compare_rx  # noqa: E402
from tools.compare_variant_function_bodies import compare as compare_bodies  # noqa: E402
from tools.compare_variant_function_bodies import load_codeflash  # noqa: E402

SPAN_RAW = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511/dump_codeflash_00000000_00200000_20260821-152033.bin"
SIENNA = REPO / "firmware/RH850_P1M-E_CodeFlash.bin"
INVENTORY = REPO / "data/ghidra_project_inventory.baseline.jsonl"
GEN = REPO / "data/generated"

SPAN_BODY = GEN / "corolla_8965F1208000_function_body_transfer.json"
H_BODY = GEN / "corolla_8965H1202000_function_body_transfer.json"
SPAN_STRUCT = GEN / "corolla_8965F1208000_structural_function_transfer.json"
H_STRUCT = GEN / "corolla_8965H1202000_structural_function_transfer.json"
SPAN_LEDGER = GEN / "corolla_8965F1208000_named_function_transfer_ledger.json"
H_LEDGER = GEN / "corolla_8965H1202000_named_function_transfer_ledger.json"
SPAN_RX = GEN / "corolla_8965F1208000_application_rx_diff.json"
H_RX = GEN / "corolla_8965H1202000_application_rx_diff.json"
SPAN_GATE = GEN / "secoc_gate_resolution_8965F1208000_minimal.json"
H_GATE = GEN / "secoc_gate_resolution_8965H1202000_minimal.json"
SPAN_RUNTIME = GEN / "ephemeral_runtime_resolution_8965F1208000_minimal.json"
H_RUNTIME = GEN / "ephemeral_runtime_resolution_8965H1202000_minimal.json"
SPAN_MANIFEST = GEN / "ephemeral_runtime_target_manifest_8965F1208000.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def check(label: str, condition: object) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[ok] {label}")


span, source = load_codeflash(SPAN_RAW)
sienna = SIENNA.read_bytes()

print("== raw Sienna transfer regeneration ==")
fresh_body = compare_bodies(
    sienna,
    INVENTORY,
    span,
    target_source=source,
    reference_id="8965B4512000",
    target_id="8965F1208000",
)
span_body = load(SPAN_BODY)
check("Span Sienna exact-body report regenerates from raw firmware", fresh_body == span_body)
h_body = load(H_BODY)
check("Span and H exact-body per-function transfer rows are identical", span_body["functions"] == h_body["functions"])
check("Span and H relocation clusters are identical", span_body["relocation_clusters"] == h_body["relocation_clusters"])
check("Span and H exact-body summary is identical", span_body["summary"] == h_body["summary"])
check("Sienna census remains 6375 functions / 1113 named", span_body["summary"]["reference_codeflash_functions"] == 6375 and span_body["summary"]["named_reference_functions"] == 1113)
check("1017 Sienna bodies transfer exactly to Span", span_body["summary"]["exact_body_transfer_proven_functions"] == 1017)
check("288 named Sienna bodies transfer exactly to Span", span_body["summary"]["named_exact_body_transfer_proven_functions"] == 288)

print("\n== fresh target-native structural equivalence ==")
span_struct = load(SPAN_STRUCT)
h_struct = load(H_STRUCT)
check("fresh Span clean fingerprint SHA equals clean H fingerprint SHA", span_struct["target"]["sha256"] == h_struct["target"]["sha256"] == "b7acbb2265b97d3811652d75900850b48d799eb5f0e59b7e14d0e6d4952b3051")
check("fresh Span clean import recovers the same 5425 functions", span_struct["target"]["function_count"] == h_struct["target"]["function_count"] == 5425)
check("Span/H Sienna structural match rows are identical", span_struct["matches"] == h_struct["matches"])
check("Span/H Sienna structural summaries are identical", span_struct["summary"] == h_struct["summary"])
check("2542 unique complete instruction-shape homologs recur", span_struct["summary"]["unique_exact_shape_matches"] == 2542)

span_ledger = load(SPAN_LEDGER)
h_ledger = load(H_LEDGER)
check("all 1113 named transfer-ledger rows are identical", span_ledger["functions"] == h_ledger["functions"])
check("named transfer summary is identical", span_ledger["summary"] == h_ledger["summary"])

print("\n== application receive topology ==")
fresh_rx = compare_rx(
    sienna,
    span,
    reference_id="8965B4512000",
    target_id="8965F1208000",
    target_source=source,
)
span_rx = load(SPAN_RX)
check("Span application-Rx report regenerates from raw firmware", fresh_rx == span_rx)
h_rx = load(H_RX)
check("Span/H 40-entry target receive descriptor tables are identical", span_rx["target"]["descriptors"] == h_rx["target"]["descriptors"])
check("Span/H Sienna Rx delta summary is identical", span_rx["summary"] == h_rx["summary"])
check("Span removes the same eight Sienna descriptors", [x["can_id"] for x in span_rx["summary"]["removed"]] == ["0x2E4", "0x191", "0x131", "0x2FD", "0x132", "0x423", "0x020", "0x1DA"])
check("Span adds only FD 0x0B6", span_rx["summary"]["added"] == [{"index": 37, "software_id": "0x400000B6", "can_id": "0x0B6", "length": 32, "can_fd": True}])

print("\n== independent Gate-2/runtime resolution ==")
span_gate = load(SPAN_GATE)
h_gate = load(H_GATE)
sg = dict(span_gate); hg = dict(h_gate)
sg.pop("program_sha256"); hg.pop("program_sha256")
check("Span Gate-2 semantic resolution equals H apart from image SHA", sg == hg)
check("Span Gate-2 uniquely resolves patch 0x88C62 e0d1->e001", span_gate["candidate_count"] == 1 and span_gate["patch"] == {"address": "0x00088c62", "original": "e0d1", "replacement": "e001", "operation": "cmp-second-register-to-first-force-fallthrough"})
check("Span minimal runtime semantic skeleton equals H exactly", load(SPAN_RUNTIME) == load(H_RUNTIME))

manifest = load(SPAN_MANIFEST)
check("full Span runtime resolver remains steering-unsupported", manifest["status"] == "semantic-resolved-steering-unsupported" and not manifest["runtime_build_ready"])
check("Span Gate-2 queue is exactly 00F/D7/B6", [(r["can_id"], r["secured_length"]) for r in manifest["secoc_records"]["records"]] == [("0xF", 8), ("0xD7", 32), ("0xB6", 32)])
check("Span Gate-2 queue has no classic 2E4/131 steering profiles", manifest["secoc_records"]["steering_bridge_missing_ids"] == ["0x2E4", "0x131"] and not manifest["secoc_records"]["steering_bridge_applicable"])
profile = manifest["authenticated_bootstrap_profile"]
check("Span acquisition independently upgrades bootstrap profile to observed", profile is not None and profile["matched_evidence"][0]["software_id"] == "8965F1208000" and profile["matched_evidence"][0]["grade"] == "observed")
check("runtime RAM retention geometry remains separately unresolved", manifest["ram_execution_geometry"]["status"] == "unresolved")

print("\nSpan Corolla cross-variant verification passed.")
