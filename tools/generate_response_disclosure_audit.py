#!/usr/bin/env python3
"""Generate the generalized stale-response disclosure audit.

Extends the verified RDBI 48-DID stale-response mechanism (application.md
"Transport-layer stale-response disclosure") to every response-producing
surface in the image, using the same firmware-static criterion:

  A surface is disclosure-prone when its response length is *declared by
  configuration* while its *producer writes fewer bytes than declared* — and
  the transport reuses a response buffer that is never fully cleared between
  services.

Sources scanned (all tracked, verified evidence):
  1. Application RDBI DID table 0x2941C: per-DID declared length vs producer
     callback body shape (four-byte success stub => writes nothing).
  2. Application RoutineControl surface: per-RID declared output bytes vs
     action-callback result population (requestResults paths).
  3. Application WDBI callbacks: start/result declared sizes vs writers.
  4. XCP response builders: fixed eight-byte response frames fully written?
  5. Bootloader DID/read services: F181 placeholder is fully written by
     construction (02 || 32*0x21) — verified negative.

The audit reuses the RDBI producer-stub census technique: a producer whose
body is exactly `mov 0,r10; jmp lp` (bytes 00 52 40 06 3f 00) cannot have
written its declared output.
"""
from __future__ import annotations

import csv
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CF = (REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
OUT_JSON = REPO / "data" / "generated" / "response_disclosure_audit.json"
OUT_CSV = REPO / "data" / "generated" / "response_disclosure_audit.csv"

SUCCESS_STUB = bytes.fromhex("00527f00")  # mov 0,r10; jmp lp


def u16(addr: int) -> int:
    return struct.unpack_from("<H", CF, addr)[0]


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


def is_success_stub(addr: int) -> bool:
    return CF[addr:addr + 4] == SUCCESS_STUB


def rdbi_audit() -> list[dict]:
    """Re-derive the verified 48-DID census from the DID table."""
    table, count = 0x2941C, 0xF2
    findings = []
    for i in range(count):
        base = table + i * 16
        did = u16(base)
        declared = u16(base + 2)
        callback = u32(base + 4)
        if callback == 0:
            continue
        prone = is_success_stub(callback)
        findings.append({
            "surface": "application_rdbi",
            "selector": f"0x{did:04X}",
            "declared_response_bytes": declared,
            "producer": f"0x{callback:08x}",
            "producer_writes_declared": not prone,
            "criterion": "producer is four-byte success stub (mov 0,r10; jmp lp)",
            "evidence_grade": "verified (matches DIAG stale-response census)",
        })
    return findings


def routine_control_audit() -> list[dict]:
    """RoutineControl response-pack audit modeling packer 0x95966 exactly.

    The packer builds the response record at FEBE5DF8 from per-RID descriptor
    arrays selected by control type:
      kind 0x06 / 0x03 — byte ASSIGN from the parsed result slot (every byte
        written; the type-3 dispatcher status helpers own the value, e.g.
        0x960DE pre-initializes the out slot before dispatch);
      kind 0x07 — pointer copy of `(declared_bits + 7) >> 3` bytes from a
        routine-owned result buffer (only four RIDs: 0x1000/0x1001/0x1009
        32-byte bitmaps fully built by their helpers, 0x1010 the ICU-S
        key-update result whose length is authenticated-package-owned);
      kind 0x00 — OR bitfield into the response byte: can only *add* bits to a
        byte; stale only if that byte is never assigned/cleared first.

    This model deliberately does NOT use the action callback as the type-3
    producer (the dispatcher/status helpers are), so an immediate-success
    action stub is not by itself a disclosure.
    """
    from collections import Counter

    kind_names = {0x00: "or-bit", 0x03: "assign-byte", 0x06: "assign-byte",
                  0x07: "pointer-copy", 0x01: "assign-16", 0x04: "assign-16",
                  0x02: "assign-32"}
    rows = []
    rid_by_index = []
    # Firmware table index -> RID comes from the 19-row RID table at 0x26AEC
    # (stride 8: {rid, .., policy_ptr, ..}); CSV row order is sorted differently.
    for i in range(19):
        rid_by_index.append(f"0x{struct.unpack_from('<H', CF, 0x26AEC + i * 8)[0]:04x}")

    for idx in range(len(rid_by_index)):
        rid = rid_by_index[idx]
        # Response-pack descriptors per control type (packer 0x95966 table set).
        for label, count_at, arr_at in (
            ("type1_result", 0x26B95, 0x268BC),
            ("type2_pending", 0x26B9A, 0x269FC),
            ("type3_request_result", 0x26B90, 0x267CC),
        ):
            count = CF[count_at + idx * 0xF]
            if count == 0:
                continue
            arr = u32(arr_at + idx * 4)
            kinds = Counter()
            or_bits = []
            for i in range(count):
                d = arr + i * 6
                kind = CF[d + 1]
                bitfield = u16(d + 4)
                kinds[kind] += 1
                if kind == 0x00:
                    or_bits.append(bitfield)
            or_only = set(kinds) == {0x00}
            rows.append({
                "surface": "application_routine_control_pack",
                "selector": f"{rid}/{label}",
                "declared_response_bytes": count,
                "producer": f"0x95966 descriptors @ 0x{arr:08x}",
                "producer_writes_declared": not or_only,
                "criterion": (
                    ";".join(f"{kind_names.get(k, hex(k))}x{v}" for k, v in sorted(kinds.items()))
                    + ("; OR-only byte requires a prior assign/clear" if or_only else "")
                ),
                "evidence_grade": "recovered (packer descriptor census; kind-6 assigns and kind-7 routine-owned lengths are written by construction)",
            })
    return rows


def wdbi_audit() -> list[dict]:
    rows = []
    path = REPO / "data" / "application_wdbi_callbacks.csv"
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            result_size = int(row.get("result_size_bytes") or 0)
            cb = row.get("result_cb", "")
            cb_addr = int(cb, 16) if cb.startswith("0x") else 0
            prone = result_size > 0 and cb_addr != 0 and is_success_stub(cb_addr)
            rows.append({
                "surface": "application_wdbi",
                "selector": row["did"],
                "declared_response_bytes": result_size,
                "producer": cb,
                "producer_writes_declared": not prone,
                "criterion": "result callback is a success stub while result size >0",
                "evidence_grade": "recovered (structural census)",
            })
    return rows


def xcp_audit() -> list[dict]:
    """XCP response frames are eight bytes; check each configured builder writes a full frame."""
    path = REPO / "data" / "recovered_callback_tables.csv"
    rows = []
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if "XCP" not in row.get("structural_role", ""):
                continue
            target = int(row["target_addr"], 16)
            body_size = int(row["body_size"])
            # The shared response builder 0x9724E writes the full 8-byte frame at FEBE5E94;
            # handlers calling it produce a fully-written frame (COM-005 / dispatch doc).
            # Structural criterion: handler reaches 0x9724E (call target census in CSV callees).
            callees = row.get("direct_callees", "")
            uses_builder = "9724e" in callees.lower()
            rows.append({
                "surface": "xcp_command",
                "selector": row["selector"],
                "declared_response_bytes": 8,
                "producer": f"0x{target:08x}",
                "producer_writes_declared": uses_builder,
                "criterion": "handler routes through full-frame response builder 0x9724E",
                "evidence_grade": "recovered (callback-table census)",
                "note": "0x81FE4 clears the 8-byte Rx staging slot before copy; short-frame stale-tail closed (COM-005)",
            })
    return rows


def bootloader_audit() -> list[dict]:
    """Bootloader F181 writes its full placeholder (02 || 32*0x21) — pinned negative."""
    return [{
        "surface": "bootloader_rdbi",
        "selector": "0xF181",
        "declared_response_bytes": 33,
        "producer": "0x5FB8",
        "producer_writes_declared": True,
        "criterion": "producer synthesizes every declared byte (verified DID model)",
        "evidence_grade": "verified negative",
    }]


def main() -> int:
    findings = (
        rdbi_audit()
        + routine_control_audit()
        + wdbi_audit()
        + xcp_audit()
        + bootloader_audit()
    )
    prone = [f for f in findings if not f["producer_writes_declared"]]
    payload = {
        "schema": "response-disclosure-audit/1",
        "scope": "Sienna EPS 8965B4512000",
        "criterion": "declared-by-configuration response length vs producer writes; transport buffer reuse without full clear",
        "surfaces_scanned": ["application_rdbi", "application_routine_control_type3",
                             "application_wdbi", "xcp_command", "bootloader_rdbi"],
        "total_rows": len(findings),
        "prone_total": len(prone),
        "prone_by_surface": {
            surface: sum(1 for f in prone if f["surface"] == surface)
            for surface in sorted({f["surface"] for f in findings})
        },
        "findings": findings,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    with OUT_CSV.open("w", newline="") as handle:
        fieldnames = [k for k in findings[0]]
        for extra in ("note",):
            if any(extra in f for f in findings) and extra not in fieldnames:
                fieldnames.append(extra)
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(findings)
    print(f"rows={len(findings)} prone={len(prone)} by_surface={payload['prone_by_surface']}")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
