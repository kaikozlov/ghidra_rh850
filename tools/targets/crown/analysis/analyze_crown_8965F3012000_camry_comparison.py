#!/usr/bin/env python3
"""Build an exact-byte Crown 8965F3012000 vs Camry 8965F3307000 comparison."""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CROWN_PATH = REPO / "firmware/crown-8965F3012000/CodeFlash.bin"
CAMRY_PATH = REPO / "firmware/camry-8965F3307000/CodeFlash.bin"
DEFAULT_OUT = REPO / "data/generated/crown_8965F3012000_camry_comparison.json"

CROWN_SHA = "5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273"
CAMRY_SHA = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

# Function bodies independently established in the first-class projects. These
# checks intentionally compare raw CodeFlash bytes, not decompiler text.
EXACT_BODY_MAPPINGS = {
    "startup_shadow_copy": (0x636D4, 0x62AD4, 36),
    "command5_sync_wrapper": (0x89BC2, 0x87662, 138),
    "command5_dispatcher": (0x89440, 0x86EE0, 150),
    "freshness48_packer": (0x90566, 0x8E006, 120),
}

REGIONS = (
    ("boot_core", 0x000000, 0x009200),
    ("low_calibration", 0x009200, 0x010000),
    ("shadow_source", 0x010000, 0x018000),
    ("low_identity_tail", 0x018000, 0x020000),
    ("application_early", 0x020000, 0x060000),
    ("application_mid", 0x060000, 0x085000),
    ("application_high", 0x085000, 0x100000),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def did_table(data: bytes, base: int, count: int = 241) -> tuple[list[int], list[int]]:
    dids, callbacks = [], []
    for i in range(count):
        row = base + i * 16
        dids.append(struct.unpack_from("<H", data, row)[0])
        callbacks.append(u32(data, row + 4))
    return dids, callbacks


def count_word(data: bytes, value: int) -> int:
    needle = struct.pack("<I", value)
    total = 0
    start = 0
    while True:
        hit = data.find(needle, start)
        if hit < 0:
            return total
        total += 1
        start = hit + 1


def build() -> dict:
    crown = CROWN_PATH.read_bytes()
    camry = CAMRY_PATH.read_bytes()
    if len(crown) != 0x100000 or sha256(crown) != CROWN_SHA:
        raise SystemExit("Crown canonical CodeFlash identity drift")
    if len(camry) != 0x100000 or sha256(camry) != CAMRY_SHA:
        raise SystemExit("Camry canonical CodeFlash identity drift")

    first_diff = next((i for i, (a, b) in enumerate(zip(crown, camry)) if a != b), len(crown))
    total_diff = sum(a != b for a, b in zip(crown, camry))
    regions = []
    for name, start, end in REGIONS:
        diff = sum(a != b for a, b in zip(crown[start:end], camry[start:end]))
        regions.append({"name": name, "start": f"0x{start:06X}", "end": f"0x{end:06X}", "size": end-start, "differing_bytes": diff})

    body_mappings = {}
    for name, (camry_addr, crown_addr, size) in EXACT_BODY_MAPPINGS.items():
        a = camry[camry_addr:camry_addr+size]
        b = crown[crown_addr:crown_addr+size]
        if a != b:
            raise SystemExit(f"exact body mapping drift: {name}")
        body_mappings[name] = {
            "camry": f"0x{camry_addr:08X}",
            "crown": f"0x{crown_addr:08X}",
            "size": size,
            "sha256": sha256(a),
            "delta": crown_addr - camry_addr,
        }

    # Context loader is otherwise byte-identical; the target-pointer immediate is
    # the only two-byte delta inside its 44-byte body.
    camry_ctx = camry[0x715B4:0x715B4+44]
    crown_ctx = crown[0x709E4:0x709E4+44]
    ctx_diffs = [i for i, (a, b) in enumerate(zip(camry_ctx, crown_ctx)) if a != b]
    if ctx_diffs != [32, 33]:
        raise SystemExit(f"context-loader delta drift: {ctx_diffs}")
    camry_tp = struct.unpack_from("<I", camry_ctx, 32)[0]
    crown_tp = struct.unpack_from("<I", crown_ctx, 32)[0]

    crown_dids, crown_callbacks = did_table(crown, 0x28FA8)
    camry_dids, camry_callbacks = did_table(camry, 0x2928C)
    if crown_dids != camry_dids or crown_dids[0] != 0x0101 or crown_dids[-1] != 0xF18C:
        raise SystemExit("Crown/Camry RDBI DID membership drift")
    deltas = collections.Counter(c - f for c, f in zip(crown_callbacks, camry_callbacks))

    roots = {}
    for name, off in (("payload_build_secret", 0xBFD8), ("boot_sa_secret", 0xBFE8), ("application_sa_secret", 0x20840)):
        cb, fb = crown[off:off+16], camry[off:off+16]
        roots[name] = {"address": f"0x{off:08X}", "identical": cb == fb, "sha256": sha256(cb)}

    return {
        "schema": "crown-8965f3012000-camry-f33-comparison-v1",
        "crown": {"software_id": "8965F3012000", "codeflash_sha256": CROWN_SHA, "mcu": "R7F701381"},
        "camry": {"software_id": "8965F3307000", "codeflash_sha256": CAMRY_SHA, "mcu": "R7F701381"},
        "raw_identity": {
            "first_differing_offset": f"0x{first_diff:06X}",
            "common_prefix_bytes": first_diff,
            "total_differing_bytes": total_diff,
            "regions": regions,
            "boot_core_0_9200_identical": crown[:0x9200] == camry[:0x9200],
            "application_entry_pointer": f"0x{u32(crown, 0xFFDB8):08X}",
            "application_entry_pointer_same": u32(crown, 0xFFDB8) == u32(camry, 0xFFDB8) == 0x20880,
        },
        "identity_records": {
            "primary_f181": {"address": "0x00020860", "value": crown[0x20860:0x2086C].decode("ascii")},
            "secondary_f181": {"address": "0x00017DC0", "value": crown[0x17DC0:0x17DCC].decode("ascii")},
            "auxiliary_id": {"address": "0x00017D80", "value": crown[0x17D80:0x17D8C].decode("ascii")},
            "boot_info_mcu": {"address": "0x00000190", "value": crown[0x190:0x19A].decode("ascii")},
        },
        "crypto_roots": roots,
        "application_context": {
            "camry_function": "0x000715B4",
            "crown_function": "0x000709E4",
            "body_size": 44,
            "differing_byte_offsets": ctx_diffs,
            "gp": "0xFEBEB800",
            "sp": "0xFEBE2000",
            "camry_tp": f"0x{camry_tp:08X}",
            "crown_tp": f"0x{crown_tp:08X}",
        },
        "exact_body_mappings": body_mappings,
        "rdbi": {
            "count": len(crown_dids),
            "unique_callbacks": len(set(crown_callbacks)),
            "crown_table": "0x00028FA8",
            "camry_table": "0x0002928C",
            "did_membership_identical": True,
            "callback_delta_histogram": {str(k): v for k, v in sorted(deltas.items(), key=lambda kv: (-kv[1], kv[0]))},
        },
        "c7_ingress_boundary": {
            "camry_hardware_extended_id_word": "0x9FDC0002",
            "camry_raw_occurrences": count_word(camry, 0x9FDC0002),
            "crown_raw_occurrences": count_word(crown, 0x9FDC0002),
            "interpretation": "The Camry C7/XCP ingress identifier is not a raw Crown CodeFlash constant; Crown control ingress must be resolved target-natively before porting the resident.",
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
    if args.check:
        if not out.is_file() or out.read_text() != encoded:
            raise SystemExit(f"comparison artifact drift: {out}")
        print(f"checked {out.relative_to(REPO)}")
    else:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(encoded)
        print(f"wrote {out.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
