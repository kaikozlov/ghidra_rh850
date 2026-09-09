#!/usr/bin/env python3
"""Reduce the 2026-09-08 exact-F33 generic-monitor field session."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "targets/camry-2026/raw-20260908/runtime-monitor-session/files"
DEFAULT_OUT = ROOT / "data/generated/camry_f33_runtime_monitor_20260908.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prefixed_json(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start = text.find("{")
    if start < 0:
        raise ValueError(f"no JSON object in {path}")
    return json.loads(text[start:])


def value_map(command_result: dict) -> dict[int, bytes]:
    state = command_result["state"]
    return {int(row["address"], 16): bytes.fromhex(row["bytes_le"]) for row in state["values"]}


def raw_route_core(command_result: dict) -> dict:
    vals = value_map(command_result)
    b1_b4 = vals[0xFEBE4C00]
    b5_b8 = vals[0xFEBE4C04]
    b9_b12 = vals.get(0xFEBE4C08, b"\x00" * 4)
    b = b"\x00" + b1_b4 + b5_b8 + b9_b12
    return {
        "b1_b12_hex": b[1:13].hex(),
        "target_lateral_id": b[3] & 0x3F,
        "target_angle_raw": int.from_bytes(b[4:6], "big", signed=True),
        "companion_b6": b[6],
        "sequence": b[7] & 0x3F,
        "contribution_pct_1": b[8],
        "contribution_pct_2": b[9],
    }


RATE_RE = re.compile(
    r"^bus (?P<bus>None|\d+) dt (?P<dt>[0-9.]+) sent (?P<sent>\d+) echo (?P<echo>\d+) "
    r"route_delta (?P<delta>\d+) rate (?P<rate>[0-9.]+) b3 (?P<b30>\d+) -> (?P<b31>\d+) "
    r"adb (?P<a0>\d+) -> (?P<a1>\d+) err \[\]$"
)
MARKER_RE = re.compile(
    r"^marker100 bus (?P<bus>\d+) elapsed (?P<dt>[0-9.]+) sent (?P<sent>\d+) echo (?P<echo>\d+) "
    r"route_delta (?P<delta>\d+) raw63_reads (?P<raw63>\d+) genID63_reads (?P<gen63>\d+) "
    r"ADB63_reads (?P<adb63>\d+) reads (?P<reads>\d+) b3uniq \{0: (?P<zero_reads>\d+)\} err \[\]$"
)


def parse_rate(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = RATE_RE.match(line)
        if not m:
            continue
        g = m.groupdict()
        out.append({
            "bus": None if g["bus"] == "None" else int(g["bus"]),
            "duration_s": float(g["dt"]), "sent": int(g["sent"]), "echo": int(g["echo"]),
            "route44_generation_delta_mod256": int(g["delta"]), "apparent_generation_rate_hz": float(g["rate"]),
            "raw_target_id_before": int(g["b30"]), "raw_target_id_after": int(g["b31"]),
            "adb0_before": int(g["a0"]), "adb0_after": int(g["a1"]),
        })
    if len(out) != 6:
        raise ValueError(f"expected six controlled rate segments, got {len(out)}")
    return out


def parse_markers(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = MARKER_RE.match(line)
        if not m:
            continue
        g = m.groupdict()
        out.append({k: int(v) if k not in {"dt"} else float(v) for k, v in g.items()})
    if len(out) != 3:
        raise ValueError(f"expected three marker-bus segments, got {len(out)}")
    return out


def build() -> dict:
    paths = {
        "phase_a": RAW / "f33-phase-A-corrected.json",
        "phase_b": RAW / "f33-phase-B.json",
        "phase_c": RAW / "f33-phase-C.json",
        "phase_k": RAW / "f33-phase-K.json",
        "rate": RAW / "f33_rate.out",
        "marker": RAW / "f33_marker.out",
    }
    for p in paths.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    a, b, c, k = (prefixed_json(paths[x]) for x in ("phase_a", "phase_b", "phase_c", "phase_k"))
    rate = parse_rate(paths["rate"])
    markers = parse_markers(paths["marker"])

    for row, name in ((a, "A"), (b, "B"), (c, "C"), (k, "K")):
        if row["verdict"] != "phase_complete" or row["b6"]["tx_count"] != row["b6"]["tx_echo_delta"]:
            raise ValueError(f"phase {name} was not a complete echoed field phase")

    tx = bytes.fromhex(a["b6"]["first_frame_hex"])
    if not (len(tx) == 32 and (tx[3] & 0x3F) == 11 and tx[8] == tx[9] == 100):
        raise ValueError("phase A is not current-shape active ID11 B6")
    a_post = raw_route_core(a["post"])
    k_post = raw_route_core(k["post"])

    bpost = value_map(b["post"])
    cpost = value_map(c["post"])
    generated_id = bpost[0xFEBE80BC][0] & 0x3F
    generated_angle = int.from_bytes(bpost[0xFEBE80B8][0:2], "little", signed=True)
    adb0 = cpost[0xFEBEADB0][0] & 0x3F
    ae90 = int.from_bytes(cpost[0xFEBEAE90][0:2], "little", signed=True)
    acbd = cpost[0xFEBEACBC][1]
    cafc, cafd, cafe, caff = cpost[0xFEBECAFC]

    idle = [x for x in rate if x["bus"] is None]
    b0 = next(x for x in rate if x["bus"] == 0)
    b2 = next(x for x in rate if x["bus"] == 2)
    b1 = next(x for x in rate if x["bus"] == 1)
    if not (all(x["route44_generation_delta_mod256"] == 0 for x in idle) and
            b0["route44_generation_delta_mod256"] != 0 and b2["route44_generation_delta_mod256"] != 0 and
            b1["route44_generation_delta_mod256"] == 0):
        raise ValueError("controlled route44 causal/bus discriminator drift")
    if not all(x["raw63"] == x["gen63"] == x["adb63"] == 0 and x["zero_reads"] == x["reads"] for x in markers):
        raise ValueError("ID63 marker observation drift")

    return {
        "schema": "camry-f33-runtime-monitor-20260908-v1",
        "target": "8965F3307000",
        "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in paths.items()},
        "controlled_route44_activity": {
            "segments": rate,
            "idle_segments_quiescent": True,
            "bus0_and_bus2_injection_associated_with_generation": True,
            "bus1_injection_not_associated_with_generation": True,
            "scope": "causal association between host B6 injection on the relay-correct EPS segment and route44 publication generation; not proof that a particular echoed frame is the published PDU",
        },
        "current_shape_phase_a": {
            "tx_count": a["b6"]["tx_count"], "tx_echo_delta": a["b6"]["tx_echo_delta"],
            "first_frame_hex": tx.hex(), "sent_target_lateral_id": tx[3] & 0x3F,
            "sent_target_angle_raw": int.from_bytes(tx[4:6], "big", signed=True),
            "sent_contribution_pct_1": tx[8], "sent_contribution_pct_2": tx[9],
            "raw_route44_post": a_post,
        },
        "full_raw_phase_k_post": k_post,
        "downstream_post": {
            "generated_target_lateral_id": generated_id,
            "generated_target_angle_raw": generated_angle,
            "adb0": adb0, "ae90": ae90, "acbd": acbd,
            "cafc": cafc, "cafd": cafd, "cafe": cafe, "caff": caff,
        },
        "id63_marker": {
            "segments": markers,
            "all_sampled_raw_generated_snapshot_ids_remained_zero": True,
        },
        "observations": {
            "host_current_shape_id11_echoed": True,
            "route44_target_id_remained_zero": a_post["target_lateral_id"] == k_post["target_lateral_id"] == 0,
            "route44_contribution_percentages_zero_in_full_raw_capture": k_post["contribution_pct_1"] == k_post["contribution_pct_2"] == 0,
            "generated_and_snapshot_target_id_zero": generated_id == adb0 == 0,
            "route_health_snapshot": {"acbd": acbd, "cafc": cafc, "cafd": cafd, "cafe": cafe, "caff": caff},
        },
        "boundary": {
            "closed": "the earlier apparent background/native route44 publisher is disproved by controlled idle/send/idle timing; route44 activity is injection-associated on bus0/bus2, while generated/application state faithfully follows the zero-ID route44 image",
            "open": "the first byte-identity divergence between Panda TX and F33 route44 remains before/at profile-2 queue publication; post-aggregate sampling cannot observe FEBE54D4 before cleanup",
            "next": "sticky pre-aggregate monitor: latch FEBE547A/FEBE54D4..54DC/FEBE54F0 immediately before fg_aggregate and compare the queued signature against every transmitted phase frame",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
