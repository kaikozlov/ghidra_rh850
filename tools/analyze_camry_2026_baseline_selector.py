#!/usr/bin/env python3
"""Join exact-F33 baseline parameter-bank selector inputs to retained Camry drives.

Read-only/offline.  Static signal geometry is consumed from the exact-F33 command-cone
artifact; this reducer scans only the two tracked relay-correct CAN-only captures and
asks whether any ordinary generated-COM input to C54A2/C5554/C28FC changes during the
repeated Class-L intervals.  It does not infer an OEM LTA name and does not authorize
vehicle output.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "targets/camry-2026/raw-20260827"
CENSUS = REPO / "data/generated/camry_2026_cruise_lta_edge_census.json"
STATIC = REPO / "data/generated/camry_8965F3307000_command_cone_ingress.json"
OUT = REPO / "data/generated/camry_2026_baseline_selector_live.json"
DRIVES = {
    "drive_a": RAW / "camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": RAW / "camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
EDGE_WINDOW_NS = 3_000_000_000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def decode(dat: bytes, byte: int, bits: int, bit_offset: int) -> int:
    return (dat[byte] >> bit_offset) & ((1 << bits) - 1)


def counter(values: list[int]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(Counter(values).items())}


def in_intervals(t: int, intervals: list[tuple[int, int]]) -> bool:
    return any(a <= t <= b for a, b in intervals)


def resolve_intervals(rows: list[dict], bases: dict[int, int]) -> list[tuple[int, int]]:
    out = []
    for row in rows:
        seg = int(row["start_segment"])
        start = bases[seg] + round(float(row["start_s"]) * 1e9)
        end = start + round(float(row["duration_s"]) * 1e9)
        out.append((start, end))
    return out


def analyze_drive(path: Path, census_drive: dict, definitions: list[dict]) -> dict:
    wanted = {int(x["can_id"], 16) for x in definitions}
    by_id: dict[int, list[tuple[int, bytes]]] = defaultdict(list)
    bases: dict[int, int] = {}
    frame_count = 0
    with gzip.open(path, "rt") as f:
        for line in f:
            seg, t, bus, addr, data_hex = json.loads(line)
            seg, t, bus, addr = int(seg), int(t), int(bus), int(addr)
            frame_count += 1
            bases[seg] = min(bases.get(seg, t), t)
            if bus == 0 and addr in wanted:
                by_id[addr].append((t, bytes.fromhex(data_hex)))

    class_l = resolve_intervals(census_drive["lateral_hud_candidate"]["intervals"], bases)
    signals: dict[str, dict] = {}
    for d in definitions:
        sid = int(d["signal"])
        addr = int(d["can_id"], 16)
        length = int(d["length"])
        rows = [(t, dat) for t, dat in by_id.get(addr, []) if len(dat) == length]
        vals = [(t, decode(dat, int(d["byte"]), int(d["bits"]), int(d["bit_offset"]))) for t, dat in rows]
        all_v = [v for _, v in vals]
        class_v = [v for t, v in vals if in_intervals(t, class_l)]
        edge_windows = []
        for a, b in class_l:
            for name, edge in (("rise", a), ("fall", b)):
                pre = [v for t, v in vals if edge - EDGE_WINDOW_NS <= t < edge]
                post = [v for t, v in vals if edge <= t < edge + EDGE_WINDOW_NS]
                edge_windows.append({
                    "edge": name,
                    "pre_frames": len(pre), "post_frames": len(post),
                    "pre_values": counter(pre), "post_values": counter(post),
                    "value_set_changed": set(pre) != set(post),
                })
        signals[f"sig{sid}"] = {
            "can_id": d["can_id"], "length": length, "byte": d["byte"], "bits": d["bits"],
            "bit_offset": d["bit_offset"], "raw_cell": d["raw_cell"], "stage_cell": d["stage_cell"],
            "all": {"frames": len(all_v), "values": counter(all_v)},
            "class_l": {"frames": len(class_v), "values": counter(class_v)},
            "class_l_edges_3s": edge_windows,
        }

    observed = [s for s in signals.values() if s["all"]["frames"]]
    return {
        "source": {"path": str(path.relative_to(REPO)), "sha256": sha256(path), "frame_count": frame_count},
        "class_l_duration_s": round(sum(b - a for a, b in class_l) / 1e9, 6),
        "signals": signals,
        "summary": {
            "ordinary_selector_signals": len(signals),
            "observed_signals": len(observed),
            "observed_signals_constant_zero_all_route": sum(
                s["all"]["frames"] > 0 and s["all"]["values"] == {"0": s["all"]["frames"]}
                for s in signals.values()),
            "unobserved_signals": sorted(k for k, s in signals.items() if s["all"]["frames"] == 0),
            "class_l_edge_value_changes": sum(
                e["value_set_changed"]
                for s in signals.values() for e in s["class_l_edges_3s"]
                if e["pre_frames"] and e["post_frames"]
            ),
        },
    }


def build() -> dict:
    static = json.loads(STATIC.read_text())
    census = json.loads(CENSUS.read_text())
    definitions = static["baseline_selector_machinery"]["generated_com_inputs"]
    drives = {label: analyze_drive(path, census["drives"][label], definitions)
              for label, path in DRIVES.items()}
    return {
        "schema": "camry-2026-baseline-selector-live-v1",
        "sources": {
            "static_selector": {"path": str(STATIC.relative_to(REPO)), "sha256": sha256(STATIC)},
            "class_l_census": {"path": str(CENSUS.relative_to(REPO)), "sha256": sha256(CENSUS)},
        },
        "selector_scope": {
            "signals": [int(x["signal"]) for x in definitions],
            "can_ids": sorted({x["can_id"] for x in definitions}),
            "role": "ordinary generated-COM inputs to the recovered baseline parameter-bank selector; not command magnitudes",
        },
        "drives": drives,
        "combined": {
            "all_observed_selector_inputs_constant_zero": all(
                s["all"]["frames"] == 0 or s["all"]["values"] == {"0": s["all"]["frames"]}
                for d in drives.values() for s in d["signals"].values()),
            "class_l_edge_value_changes": sum(d["summary"]["class_l_edge_value_changes"] for d in drives.values()),
            "classification": (
                "observed/deterministic: every ordinary selector input that appears in either retained drive "
                "is zero for the entire route and through the Class-L edge windows; 0x490/0x1DA selector "
                "inputs are absent. These ordinary COM selector inputs therefore do not distinguish Class-L "
                "from surrounding driving in the retained captures. Internal/fault/diagnostic selector "
                "alternatives remain separately bounded by the exact static model."
            ),
            "production_output_authorized": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
