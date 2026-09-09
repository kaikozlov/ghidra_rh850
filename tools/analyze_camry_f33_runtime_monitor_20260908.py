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
    return json.JSONDecoder().raw_decode(text[start:])[0]


def state_value_map(state: dict) -> dict[int, bytes]:
    return {int(row["address"], 16): bytes.fromhex(row["bytes_le"]) for row in state["values"]}


def value_map(command_result: dict) -> dict[int, bytes]:
    return state_value_map(command_result["state"])


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


def parse_ndjson(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


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
        "idle_raw": RAW / "f33-idle-raw.json",
        "idle_raw_ndjson": RAW / "f33-idle-raw.ndjson",
        "preaggregate_phase_p": ROOT / "targets/camry-2026/raw-20260908/preaggregate-phase-p/f33-preaggregate-P2-console.log",
    }
    for p in paths.values():
        if not p.is_file():
            raise FileNotFoundError(p)

    a, b, c, k = (prefixed_json(paths[x]) for x in ("phase_a", "phase_b", "phase_c", "phase_k"))
    phase_p = prefixed_json(paths["preaggregate_phase_p"])
    idle_raw = prefixed_json(paths["idle_raw"])
    idle_rows = parse_ndjson(paths["idle_raw_ndjson"])
    rate = parse_rate(paths["rate"])
    markers = parse_markers(paths["marker"])
    if not (phase_p["verdict"] == "phase_complete" and phase_p["b6"]["tx_count"] == phase_p["b6"]["tx_echo_delta"] == 188 and
            phase_p["preaggregate_ingress"]["verdict"] == "no_profile2_queue_hit_latched"):
        raise ValueError("live pre-aggregate Phase P result drift")

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

    # The retained three-second idle capture is the decisive control for route44
    # background activity. It contains no Panda B6 TX echoes, yet the exact
    # route44 generation byte changes repeatedly while raw Target Lateral ID
    # remains zero. This supersedes the earlier inference from two much shorter
    # rate-test idle windows whose host-visible snapshot happened not to move.
    if idle_raw.get("b6_echo_delta") != 0 or not idle_rows:
        raise ValueError("idle raw control is not a zero-host-B6 capture")
    idle_generation = []
    idle_target_ids = []
    for row in idle_rows:
        vals = state_value_map(row)
        idle_generation.append(vals[0xFEBE5364][0])
        raw_b1_b4 = vals[0xFEBE4C00]
        idle_target_ids.append(raw_b1_b4[2] & 0x3F)  # route44 base is FEBE4BFF, so +4C00 byte2 == B3
    idle_transitions = sum(a != b for a, b in zip(idle_generation, idle_generation[1:]))
    if len(set(idle_generation)) <= 1 or idle_transitions == 0 or any(idle_target_ids):
        raise ValueError("native/background route44 idle observation drift")

    if not all(x["raw63"] == x["gen63"] == x["adb63"] == 0 and x["zero_reads"] == x["reads"] for x in markers):
        raise ValueError("ID63 marker observation drift")

    return {
        "schema": "camry-f33-runtime-monitor-20260908-v1",
        "target": "8965F3307000",
        "inputs": {name: {"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for name, path in paths.items()},
        "route44_background_control": {
            "host_b6_echo_delta": idle_raw["b6_echo_delta"],
            "capture_samples": len(idle_rows),
            "capture_generation_low_unique": sorted(set(idle_generation)),
            "capture_generation_low_transitions": idle_transitions,
            "all_sampled_target_lateral_ids_zero": all(v == 0 for v in idle_target_ids),
            "baseline_generation_window_hex": value_map(idle_raw["baseline"])[0xFEBE5364].hex(),
            "post_generation_window_hex": value_map(idle_raw["post"])[0xFEBE5364].hex(),
            "observation": "exact route44 publishes changing ID0 data while Panda reports zero B6 TX echoes; a native/background route44 producer exists in the stationary state",
        },
        "short_window_rate_segments": {
            "segments": rate,
            "interpretation": "retained as raw timing observations only; zero/nonzero modulo-256 deltas in these short host-sampled windows do not establish injection causality because the longer zero-echo idle control independently shows background route44 publication and resident snapshots can remain stale between foreground updates",
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
            "interpretation": "post-aggregate snapshots remained on the native/background ID0 image; this does not prove the injected ID63 frame failed to reach an earlier hardware/CanIf stage",
        },
        "preaggregate_phase_p": {
            "tx_count": phase_p["b6"]["tx_count"],
            "tx_echo_delta": phase_p["b6"]["tx_echo_delta"],
            "freshness_reset_reanchors": phase_p["b6"]["freshness_reset_reanchors"],
            "queue_length_at_latched_sample": phase_p["preaggregate_ingress"]["queue_length"],
            "preaggregate_verdict": phase_p["preaggregate_ingress"]["verdict"],
            "sample_generation": phase_p["preaggregate_ingress"]["sample_generation"],
            "interpretation": "queue was zero at the immediately-pre-0x667E6 foreground sample point; this does not exclude asynchronous enqueue between foreground samples followed by consumption inside 0x667E6",
        },
        "exact_scheduler_correction": {
            "foreground_loop": "0x66062",
            "foreground_aggregate": "0x667E6",
            "aggregate_contains_secoc_consumer_chain": "0x667E6 -> 0x7A254 -> 0x6A410 -> 0x8EFF8 -> 0x8EF84 -> 0x8F98C -> 0x8F746",
            "implication": "a queue-positive interval can begin after one foreground sample and end inside the next aggregate; one sample immediately before aggregate is not a proof of no enqueue",
        },
        "observations": {
            "host_current_shape_id11_echoed": True,
            "route44_target_id_remained_zero_in_host_phase_snapshots": a_post["target_lateral_id"] == k_post["target_lateral_id"] == 0,
            "route44_contribution_percentages_zero_in_full_raw_capture": k_post["contribution_pct_1"] == k_post["contribution_pct_2"] == 0,
            "generated_and_snapshot_target_id_zero": generated_id == adb0 == 0,
            "native_background_route44_present_without_host_b6": True,
            "route_health_snapshot": {"acbd": acbd, "cafc": cafc, "cafd": cafd, "cafe": cafe, "caff": caff},
        },
        "boundary": {
            "closed": "the sampled route44/generated/ADB0 ID0 image is a real native/background publication state and cannot be attributed to transformation of the Panda ID11 frame merely because it was observed during injection",
            "open": "whether the Panda-transmitted marker reaches the exact profile-2 secured queue after physical/CanIf/PduR admission and before SecOC consumption",
            "next": "marker-filtered inter-tick Phase Q: send non-command Target Lateral ID63 with additive contribution suppressed and latch only when FEBE547A == 32 and FEBE54D7 low6 == 63; native/background stationary ID0 cannot satisfy the marker filter",
            "rejected_probe": {
                "candidate": "foreground active-RSCFD polling at controller1 FFD200DC/FFD23080/FFD2308C",
                "reason": "exact receive drain is interrupt-context 0x71508 -> 0x66026 -> 0x667B6 -> 0x7A232 -> 0x79EBA -> 0x83CE4 -> 0x83E0C, not the 0x66062 foreground loop; a foreground poll is not proven to run before the interrupt drains the hardware head",
            },
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
