#!/usr/bin/env python3
"""Build the exact TSS3 EPS resident-control ingress matrix.

This compares the two stock host->resident transports relevant to the volatile
B6 signer on the tracked Camry F33, Corolla H/F, and Crown F30 images:

* dedicated generated-COM/XCP-family extended CAN ingress; and
* the stock functional UDS endpoint on classic CAN 0x777.

The artifact intentionally separates raw/config facts from the integration
boundary. It does not claim live behavior for a target unless retained vehicle
evidence already establishes it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/tss3_resident_control_ingress_matrix.json"

PRIMARY_SERVICE_SIDS = [
    0x10, 0x11, 0x14, 0x19, 0x22, 0x23, 0x27, 0x28,
    0x2E, 0x31, 0x34, 0x36, 0x37, 0x3E, 0x85, 0xAB, 0xBA,
]
ALL_SERVICE_SIDS = PRIMARY_SERVICE_SIDS + [0x10, 0x10, 0x19, 0x22, 0x3E, 0xAB]
FUNCTIONAL_SERVICE_INDICES = [17, 2, 7, 9, 13, 14]
FUNCTIONAL_SERVICE_SIDS = [0x10, 0x14, 0x28, 0x31, 0x3E, 0x85]

TARGETS = {
    "camry-8965F3307000": {
        "vehicle": "2026 Toyota Camry Hybrid",
        "software_id": "8965F3307000",
        "codeflash": "firmware/camry-8965F3307000/CodeFlash.bin",
        "sha256": "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7",
        "corpus": "data/generated/camry-8965F3307000/decompilations.jsonl",
        "functions": {
            "service_lookup": 0x90F98,
            "response_selector": 0x911DA,
            "response_action": 0x91CE2,
            "response_machine": 0x933F8,
            "start_of_reception": 0x920BE,
            "copy_rx_data": 0x92152,
            "rx_indication": 0x921D2,
            "copy_engine": 0x93DE8,
            "receive_drain": 0x79EDE,
        },
        "xcp_staging": 0xFEBE4C34,
        "xcp_live_status": "live-proven-to-staging-and-road-proven-C7-steering",
    },
    "corolla-8965H1202000": {
        "vehicle": "2023 Toyota Corolla",
        "software_id": "8965H1202000",
        "codeflash": "firmware/corolla-8965H1202000/CodeFlash.bin",
        "sha256": "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f",
        "corpus": "data/generated/corolla-8965H1202000/decompilations.jsonl",
        "functions": {
            "service_lookup": 0x8A2A8,
            "response_selector": 0x8A4EA,
            "response_action": 0x8AFF2,
            "response_machine": 0x8C708,
            "start_of_reception": 0x8B3CE,
            "copy_rx_data": 0x8B462,
            "rx_indication": 0x8B4E2,
            "copy_engine": 0x8D0F8,
            "receive_drain": 0x7744A,
        },
        "xcp_staging": 0xFEBE4B20,
        "xcp_live_status": "firmware-configured-current-signer-carrier-live-command5-unvalidated",
    },
    "corolla-8965F1208000": {
        "vehicle": "2025 Toyota Corolla",
        "software_id": "8965F1208000",
        "codeflash": "firmware/corolla-8965F1208000/CodeFlash.bin",
        "sha256": "fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6",
        "corpus": "data/generated/corolla-8965F1208000/decompilations.jsonl",
        "functions": {
            "service_lookup": 0x8A2A8,
            "response_selector": 0x8A4EA,
            "response_action": 0x8AFF2,
            "response_machine": 0x8C708,
            "start_of_reception": 0x8B3CE,
            "copy_rx_data": 0x8B462,
            "rx_indication": 0x8B4E2,
            "copy_engine": 0x8D0F8,
            "receive_drain": 0x7744A,
        },
        "xcp_staging": 0xFEBE4B20,
        "xcp_live_status": "firmware-configured-current-signer-carrier-live-command5-unvalidated",
    },
    "crown-8965F3012000": {
        "vehicle": "2024 Toyota Crown Limited",
        "software_id": "8965F3012000",
        "codeflash": "firmware/crown-8965F3012000/CodeFlash.bin",
        "sha256": "5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273",
        "corpus": "data/generated/crown-8965F3012000/decompilations.jsonl",
        "functions": {
            "service_lookup": 0x8EA38,
            "response_selector": 0x8EC7A,
            "response_action": 0x8F782,
            "response_machine": 0x90E98,
            "start_of_reception": 0x8FB5E,
            "copy_rx_data": 0x8FBF2,
            "rx_indication": 0x8FC72,
            "copy_engine": 0x91888,
            "receive_drain": 0x792EE,
        },
        "xcp_staging": None,
        "xcp_live_status": "production-family5-disabled",
    },
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u16(data: bytes, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def hx(value: int) -> str:
    return f"0x{value:08X}"


def unique_search(data: bytes, needle: bytes, lo: int, hi: int, *, step: int = 1, label: str) -> int:
    hits = [off for off in range(lo, hi - len(needle) + 1, step) if data[off:off + len(needle)] == needle]
    if len(hits) != 1:
        raise ValueError(f"{label} not unique: {[hex(x) for x in hits]}")
    return hits[0]


def count_u32(data: bytes, value: int) -> int:
    needle = struct.pack("<I", value)
    count = 0
    start = 0
    while True:
        hit = data.find(needle, start)
        if hit < 0:
            return count
        count += 1
        start = hit + 1


def find_service_table(data: bytes) -> int:
    span = 24 * len(PRIMARY_SERVICE_SIDS)
    hits = []
    for off in range(0x24000, 0x27000 - span + 1, 4):
        if all(data[off + i * 24 + 16] == sid for i, sid in enumerate(PRIMARY_SERVICE_SIDS)):
            hits.append(off)
    if len(hits) != 1:
        raise ValueError(f"service table not unique: {[hex(x) for x in hits]}")
    return hits[0]


def find_functional_index_table(data: bytes) -> int:
    needle = b"".join(struct.pack("<H", x) for x in FUNCTIONAL_SERVICE_INDICES)
    return unique_search(data, needle, 0x24000, 0x27000, step=2, label="functional service index table")


def find_dcm_buffer_table(data: bytes) -> int:
    hits = []
    for off in range(0x24000, 0x27000, 4):
        if off + 20 > len(data):
            break
        a, b, c = u32(data, off), u32(data, off + 8), u32(data, off + 16)
        if 0xFEBE0000 <= a <= 0xFEBFFFFF and (b, c) == (a + 0x100, a + 0x200):
            hits.append(off)
    if len(hits) != 1:
        raise ValueError(f"DCM buffer table not unique: {[hex(x) for x in hits]}")
    return hits[0]


def find_diag_request_block(data: bytes) -> int:
    hits = []
    for off in range(0x21000, 0x22000, 4):
        if (u32(data, off), u32(data, off + 8), u32(data, off + 16)) == (0x7A1, 0x777, 0x7A0):
            hits.append(off)
    if len(hits) != 1:
        raise ValueError(f"diagnostic request block not unique: {[hex(x) for x in hits]}")
    return hits[0]


def find_cantp_functional_record(data: bytes) -> int:
    prefix = [0x0101, 0x0803, 0x0805, 0xFFFF, 0x0803, 0xFFFF, 0x0100]
    needle = b"".join(struct.pack("<H", x) for x in prefix)
    return unique_search(data, needle, 0x22000, 0x24000, step=2, label="functional CanTp record")


def find_xcp_family_routes(data: bytes, enabled: bool) -> int:
    expected = bytes([0, 0xFF, 2, 0xFF, 0xFF, 4 if enabled else 0xFF])
    return unique_search(data, expected, 0x21000, 0x21B00, label="generated-COM family routes")


def find_xcp_family_counts(data: bytes, enabled: bool) -> int:
    expected = [5, 0, 4, 0, 0, 1 if enabled else 0]
    needle = struct.pack("<6H", *expected)
    return unique_search(data, needle, 0x21000, 0x21B00, step=2, label="generated-COM family counts")


def load_corpus(path: Path) -> dict[int, dict]:
    out: dict[int, dict] = {}
    with path.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out[int(row["entry_addr"], 16)] = row
    return out


def normalized_decomp(rows: dict[int, dict], address: int) -> str:
    code = rows[address].get("decompiled_c", "")
    return re.sub(r"FUN_[0-9a-fA-F]+", "FUN_ADDR", code)


def require_tokens(rows: dict[int, dict], address: int, tokens: tuple[str, ...], label: str) -> str:
    if address not in rows:
        raise ValueError(f"{label} missing from decompiler corpus: {address:#x}")
    code = rows[address].get("decompiled_c", "")
    missing = [token for token in tokens if token not in code]
    if missing:
        raise ValueError(f"{label} semantic tokens missing at {address:#x}: {missing}")
    return rows[address]["decompiled_c_sha256"]


def request_types(data: bytes, buffer_table: int) -> tuple[list[int], list[int]]:
    # This generated DCM layout is stable across all four tracked TSS3 images:
    # buffer pointers, then +0x2c route-table roots, then +0x54 channel rows.
    config = buffer_table + 0x54
    route_roots = buffer_table + 0x2C
    upper_ids, result = [], []
    for channel in range(3):
        row = config + channel * 12
        group, route, config_index = u16(data, row), u16(data, row + 2), u16(data, row + 4)
        upper_ids.append(u16(data, row + 10))
        route_table = u32(data, route_roots + group * 20)
        protocol = u32(data, route_table + route * 4)
        service_config = u32(data, protocol + 4)
        result.append(data[service_config + config_index * 12 + 8])
    return upper_ids, result


def analyze_target(name: str, cfg: dict) -> dict:
    image = (REPO / cfg["codeflash"]).read_bytes()
    if len(image) != 0x100000 or sha256(image) != cfg["sha256"]:
        raise ValueError(f"{name} CodeFlash identity drift")
    corpus = load_corpus(REPO / cfg["corpus"])

    service_table = find_service_table(image)
    services = [image[service_table + i * 24 + 16] for i in range(len(ALL_SERVICE_SIDS))]
    if services != ALL_SERVICE_SIDS:
        raise ValueError(f"{name} service descriptor set drift: {services}")
    functional_indices = [u16(image, find_functional_index_table(image) + i * 2) for i in range(6)]
    functional_sids = [services[i] for i in functional_indices]
    if functional_indices != FUNCTIONAL_SERVICE_INDICES or functional_sids != FUNCTIONAL_SERVICE_SIDS:
        raise ValueError(f"{name} functional service set drift")

    buffer_table = find_dcm_buffer_table(image)
    buffers = [u32(image, buffer_table + i * 8) for i in range(3)]
    upper_ids, req_types = request_types(image, buffer_table)
    if upper_ids != [2, 3, 4] or req_types != [0, 1, 0]:
        raise ValueError(f"{name} DCM channel map drift: upper={upper_ids} request_types={req_types}")

    diag = find_diag_request_block(image)
    cantp = find_cantp_functional_record(image)
    cantp_words = [u16(image, cantp + i * 2) for i in range(16)]

    lookup_sha = require_tokens(
        corpus, cfg["functions"]["service_lookup"],
        ("*param_4 = 0x11", "return 1;"), f"{name} service lookup",
    )
    response_sha = require_tokens(
        corpus, cfg["functions"]["response_selector"],
        ("param_1 + 0x10", "cVar1 == '\\x11'", "uVar3 = 3"), f"{name} functional response selector",
    )
    action_sha = require_tokens(
        corpus, cfg["functions"]["response_action"],
        ("uStack_10 = (undefined2)*(undefined4 *)(param_1 + 0xc)",), f"{name} response action",
    )
    machine_sha = require_tokens(
        corpus, cfg["functions"]["response_machine"],
        ("uVar5 = extraout_r7 & 0xff", "if (uVar5 == 0)", "else if (uVar5 == 1)",
         "*(char *)(iVar3 + 0xc) = (char)extraout_r7"), f"{name} response machine",
    )
    copy_sha = require_tokens(
        corpus, cfg["functions"]["copy_engine"],
        ("*(undefined1 *)*piVar1 = uVar3",), f"{name} DCM copy engine",
    )

    enabled = cfg["xcp_staging"] is not None
    family_routes = find_xcp_family_routes(image, enabled)
    family_counts = find_xcp_family_counts(image, enabled)
    routes = list(image[family_routes:family_routes + 6])
    counts = list(struct.unpack_from("<6H", image, family_counts))
    request_words = count_u32(image, 0x9FDC0002)
    response_words = count_u32(image, 0x9FE00002)
    if enabled:
        if routes != [0, 0xFF, 2, 0xFF, 0xFF, 4] or counts != [5, 0, 4, 0, 0, 1]:
            raise ValueError(f"{name} enabled XCP family config drift")
        if (request_words, response_words) != (2, 1):
            raise ValueError(f"{name} XCP wire-word count drift: {(request_words, response_words)}")
    else:
        if routes != [0, 0xFF, 2, 0xFF, 0xFF, 0xFF] or counts != [5, 0, 4, 0, 0, 0]:
            raise ValueError(f"{name} disabled XCP family config drift")
        if request_words or response_words:
            raise ValueError(f"{name} unexpectedly carries Camry/Corolla XCP wire words")

    return {
        "vehicle": cfg["vehicle"],
        "software_id": cfg["software_id"],
        "codeflash_sha256": cfg["sha256"],
        "functional_diagnostic_ingress": {
            "can_id": "0x777",
            "format": "classic",
            "diagnostic_request_block": hx(diag),
            "physical_request": "0x7A1",
            "functional_request": "0x777",
            "secondary_request": "0x7A0",
            "cantp_record": hx(cantp),
            "cantp_first_words": [f"0x{x:04X}" for x in cantp_words[:7]],
            "cantp_rx_pdu": "0x0805",
            "pdur_rx_pdu": "0x0803",
            "dcm_buffer_table": hx(buffer_table),
            "dcm_buffers": [hx(x) for x in buffers],
            "functional_dcm_buffer": hx(buffers[1]),
            "dcm_upper_pdu_ids": upper_ids,
            "dcm_request_types": req_types,
            "functional_request_type": 1,
            "service_table": hx(service_table),
            "configured_service_ids": [f"0x{x:02X}" for x in services],
            "functional_service_indices": functional_indices,
            "functional_service_ids": [f"0x{x:02X}" for x in functional_sids],
            "c6_configured": 0xC6 in functional_sids,
            "c7_configured": 0xC7 in functional_sids,
            "unsupported_service_nrc": "0x11",
            "functional_nrc11_suppressed": True,
            "wire": {
                "loader": "07 C6 C6 index word_le32",
                "runtime": "07 C7 C7 seq target_hi target_lo 00 00",
                "tag_policy": "B0 is the UDS SID used for stock unsupported-service dispatch; duplicate C6/C7 in N-SDU B1 so recurring resident code can key on the durable tail after DCM teardown",
            },
            "functions": {k: hx(v) for k, v in cfg["functions"].items()},
            "decompiler_semantic_hashes": {
                "service_lookup": lookup_sha,
                "response_selector": response_sha,
                "response_action": action_sha,
                "response_machine": machine_sha,
                "copy_engine": copy_sha,
            },
            "resident_sampling_boundary": (
                f"after receive drain {hx(cfg['functions']['receive_drain'])}; complete N-SDU is already copied by the "
                "PduR/DCM receive callbacks, while service dispatch/unsupported-SID handling is a separate DCM-main path"
            ),
        },
        "dedicated_xcp_ingress": {
            "enabled": enabled,
            "family_routes_address": hx(family_routes),
            "family_routes": routes,
            "family_counts_address": hx(family_counts),
            "family_counts": counts,
            "family5_route": routes[5],
            "family5_count": counts[5],
            "request": "0x1FDC0002" if enabled else None,
            "response": "0x1FE00002" if enabled else None,
            "request_word_occurrences": request_words,
            "response_word_occurrences": response_words,
            "staging": hx(cfg["xcp_staging"]) if enabled else None,
            "status": cfg["xcp_live_status"],
        },
    }


def build() -> dict:
    targets = {name: analyze_target(name, cfg) for name, cfg in TARGETS.items()}
    h = (REPO / TARGETS["corolla-8965H1202000"]["codeflash"]).read_bytes()
    f = (REPO / TARGETS["corolla-8965F1208000"]["codeflash"]).read_bytes()
    hf_ranges = []
    for key, address in TARGETS["corolla-8965H1202000"]["functions"].items():
        row = load_corpus(REPO / TARGETS["corolla-8965H1202000"]["corpus"])[address]
        lo = int(row["body_ranges"][0]["min"], 16)
        hi = int(row["body_ranges"][-1]["max"], 16) + 1
        hf_ranges.append({"function": key, "start": hx(lo), "end_exclusive": hx(hi), "identical": h[lo:hi] == f[lo:hi]})
    if not all(row["identical"] for row in hf_ranges):
        raise ValueError(f"Corolla H/F diagnostic transport body drift: {hf_ranges}")

    normalized_response_actions = {
        name: normalized_decomp(load_corpus(REPO / cfg["corpus"]), cfg["functions"]["response_action"])
        for name, cfg in TARGETS.items()
    }
    normalized_response_machines = {
        name: normalized_decomp(load_corpus(REPO / cfg["corpus"]), cfg["functions"]["response_machine"])
        for name, cfg in TARGETS.items()
    }
    if len(set(normalized_response_actions.values())) != 1 or len(set(normalized_response_machines.values())) != 1:
        raise ValueError("functional response suppression machinery is not structurally identical across targets")

    return {
        "schema": "toyota-tss3-resident-control-ingress-matrix-v1",
        "targets": targets,
        "cross_variant": {
            "functional_0x777_present_all": all(t["functional_diagnostic_ingress"]["can_id"] == "0x777" for t in targets.values()),
            "functional_service_set_identical": len({tuple(t["functional_diagnostic_ingress"]["functional_service_ids"]) for t in targets.values()}) == 1,
            "functional_service_ids": [f"0x{x:02X}" for x in FUNCTIONAL_SERVICE_SIDS],
            "c6_c7_unconfigured_all": all(not t["functional_diagnostic_ingress"]["c6_configured"] and not t["functional_diagnostic_ingress"]["c7_configured"] for t in targets.values()),
            "functional_nrc11_suppressed_all": all(t["functional_diagnostic_ingress"]["functional_nrc11_suppressed"] for t in targets.values()),
            "response_action_structure_identical_all": True,
            "response_machine_structure_identical_all": True,
            "corolla_hf_diagnostic_functions_byte_identical": hf_ranges,
            "dedicated_xcp_enabled": [name for name, t in targets.items() if t["dedicated_xcp_ingress"]["enabled"]],
            "dedicated_xcp_disabled": [name for name, t in targets.items() if not t["dedicated_xcp_ingress"]["enabled"]],
        },
        "integration_boundary": {
            "common_fallback": "All four tracked TSS3 EPS images can stage C6/C7 through stock functional 0x777 without a firmware patch; only Crown is live-proven on this diagnostic carrier.",
            "dedicated_carrier": "Camry F33 and both Corolla H/F images already enable family5 extended 0x1FDC0002 with a dedicated staging buffer; Crown does not.",
            "runtime_shape": "Where family5 exists, retain the dedicated XCP-family C7 carrier unless a target-specific reason requires otherwise. Use functional 0x777 as the stock-firmware fallback for variants such as Crown that compile family5 out.",
            "safety_boundary": "0x777 is a functional diagnostic address rather than a dedicated signer transport. A normal driving integration must not grant arbitrary diagnostic TX merely to carry C7; any Panda allowance must remain payload/target scoped.",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    result = build()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    out = args.output if args.output.is_absolute() else REPO / args.output
    try:
        display = out.relative_to(REPO)
    except ValueError:
        display = out
    if args.check:
        if not out.is_file() or out.read_text(encoding="utf-8") != encoded:
            raise SystemExit(f"artifact drift: {out}")
        print(f"checked {display}")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(encoded, encoding="utf-8")
        print(f"wrote {display}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
