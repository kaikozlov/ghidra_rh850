#!/usr/bin/env python3
"""Verify the 2026-09-04 Camry stock-steering reducer: decodes, separation,
time base, qualification, and original-log witness reproduction (WP1).

The decode expectations below are hand-derived from the pinned wire geometry
(port report §1.3/§1.4, live-baseline §4.2), and the witness/ID4 expectations
are pinned from the *original* September 2026-09-04 reducer outputs published
in docs/variants/camry-2026-tss3-opendbc-port.md §4.6 and its review-aid CSV —
never from the decoder under test. Full-corpus regeneration needs the
external driving logs; this suite runs entirely on tracked fixtures.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools.analyze_camry_20260904_stock_steering import (
    WITNESS_WINDOW_S,
    SegmentReducer,
    be_signal,
    id4_episodes,
    load_fixture,
    median,
    reduce_fixture,
    signed_be16,
    steering_angle_deg,
    torque_invalid,
    torque_nm,
)


def med(values):
    out = median(values)
    assert out is not None
    return out


FIXTURES = REPO / "tests/fixtures/camry_20260904"

passed = failed = 0


def check(name, condition, detail=""):
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def z32(*mutations: tuple[int, int]) -> bytes:
    d = bytearray(32)
    for off, val in mutations:
        d[off] = val
    return bytes(d)


print("== decode primitives (hand-derived expectations) ==")
# be_signal start_bit 3, size 12: bits d0.b3..d0.b0 then d1.b7..d0.b0.
# d0=0x01,d1=0xF0 -> 0b0001_1111_0000 = 496; d0=0x08,d1=0x00 -> 0x800 = -2048 signed.
check("be_signal positive", be_signal(z32((0, 0x01), (1, 0xF0)), 3, 12) == 496)
check("be_signal negative", be_signal(z32((0, 0x08), (1, 0x00)), 3, 12) == -2048)
# torque: B8 signed *0.1 + B17 low nibble signed *0.01.
# B8=0xFB -> -5 -> -0.5; B17=0x0B -> nibble 0xB -> -5 -> -0.05; total -0.55.
check("torque negative decode", torque_nm(z32((8, 0xFB), (17, 0x0B))) == -0.55)
# B8=0x2A -> 42 -> 4.2; B17=0x03 -> +3 -> +0.03; total 4.23 (real route-3d frame byte geometry).
check("torque positive decode", torque_nm(z32((8, 0x2A), (17, 0x03))) == 4.23)
# angle: coarse signed12 @1.5 + fraction signed4 @0.1.
# d0=0x08,d1=0x00 -> coarse bits 100000000000 -> -2048 -> -3072.0;
# d4=0xF0 -> fraction nibble 0b1111 = 15 -> signed4 wraps to -1 -> -0.1.
check("angle negative decode", steering_angle_deg(z32((0, 0x08), (1, 0x00), (4, 0xF0))) == -3072.1,
      str(steering_angle_deg(z32((0, 0x08), (1, 0x00), (4, 0xF0)))))
check("motor proxy negative", signed_be16(z32((22, 0xFF), (23, 0x9C)), 22) == -100)
check("torque invalid bit is B6[0]", torque_invalid(z32((6, 0x01))) and not torque_invalid(z32((6, 0x02))))


def can(t, src, addr, dat):
    return ("can", t, src, addr, dat.hex())


def sendcan(t, addr, dat):
    return ("sendcan", t, 0, addr, dat.hex())


def car_state(t, v_ego=25.0, left=False, right=False):
    return ("carState", t, v_ego, left, right, 0.0, False, 0.0)


def eps(t, b8=0x00, b17=0x00, b6=0x00, motor=(0, 0)):
    d = bytearray(32)
    d[6] = b6
    d[8] = b8
    d[17] = b17
    d[22], d[23] = motor
    return can(t, 0, 0x030, bytes(d))


def angle_msg(t, d0=0x00, d1=0x00, d4=0x00):
    d = bytearray(32)
    d[0], d[1], d[4] = d0, d1, d4
    return can(t, 0, 0x025, bytes(d))


def ref081(t, raw):
    d = bytearray(32)
    d[16], d[17] = (raw >> 8) & 0xFF, raw & 0xFF
    return can(t, 0, 0x081, bytes(d))


def req08a(t, b21, raw, level=100):
    d = bytearray(32)
    d[18], d[19] = (raw >> 8) & 0xFF, raw & 0xFF
    d[21] = b21
    d[24] = level
    return can(t, 2, 0x08A, bytes(d))


def b6(t, tlid, raw):
    d = bytearray(32)
    d[3] = tlid
    d[4], d[5] = (raw >> 8) & 0xFF, raw & 0xFF
    return sendcan(t, 0x0B6, bytes(d))


print("== native vs echo vs reject vs sendcan separation ==")
t0 = 10_000_000_000
red = SegmentReducer("r", 0, keep_qualified=True)
ev = [
    car_state(t0),
    angle_msg(t0), eps(t0), ref081(t0, 5), req08a(t0, 11, 7),
    can(t0 + 5_000_000, 0, 0x123, z32()),          # native bus 0
    can(t0 + 6_000_000, 1, 0x123, z32()),          # native bus 1
    can(t0 + 7_000_000, 2, 0x123, z32()),          # native bus 2
    can(t0 + 8_000_000, 130, 0x025, z32((0, 0x08))),  # TX echo bus 2: never native
    can(t0 + 9_000_000, 192, 0x0B6, z32()),        # rejected TX bus 0: never native
    can(t0 + 10_000_000, 128, 0x0B6, z32()),       # returned B6 echo
    b6(t0 + 11_000_000, 11, 100),
]
for rec in ev:
    red.feed(rec)
res = red.finish()
check("native counted per bus 0/1/2 only", res.census["native_by_bus"] == {"0": 4, "1": 1, "2": 2},
      str(res.census["native_by_bus"]))
check("echo separated from native", res.census["returned_echo_by_bus"] == {"0": 1, "2": 1},
      str(res.census["returned_echo_by_bus"]))
check("rejected separated", res.census["rejected_by_bus"] == {"0": 1})
check("sendcan counted separately", res.census["sendcan_by_addr"] == {"0x0B6": 1})
check("native 0x0B6 stays zero in census", res.census["native_absent_addresses"]["0x0B6"] == 0)
check("returned_b6 counted once", res.census["returned_b6"] == 1)
check("rejected_b6 counted once", res.census["rejected_b6"] == 1)

print("== Panda health/state retention ==")
red = SegmentReducer("r", 0, keep_qualified=False)
# Normalized pandaState tuple: blocked, controlsAllowed, rxInvalid, heartbeatLost,
# faultStatus, faultCount, REC/TEC for buses 0/1/2, then per-bus
# busOffCnt/coreResetCnt/canfdEnabled.
red.feed(("pandaState", t0, 3, True, False, False, "none", 0, 1, 2, 3, 4, 5, 6,
          0, 0, True, 0, 0, True, 0, 0, True))
red.feed(("pandaState", t0 + 1_000_000_000, 5, False, True, True, "faulted", 2,
          7, 8, 9, 10, 11, 12, 13, 1, False, 14, 2, True, 15, 3, False))
res = red.finish()
health = res.census["panda_health"]
check("Panda health samples retained", health["samples"] == 2)
check("Panda controlsAllowed false retained", health["controls_allowed_false_samples"] == 1)
check("Panda RX-invalid/heartbeat state retained",
      health["safety_rx_checks_invalid_samples"] == 1 and health["heartbeat_lost_samples"] == 1)
check("Panda fault status/count retained",
      health["fault_status_counts"] == {"faulted": 1, "none": 1} and health["fault_count_max"] == 2)
check("Panda bus health maxima retained",
      health["bus_error_max"]["2"] == {
          "receive_error_cnt": 11, "transmit_error_cnt": 12,
          "bus_off_cnt": 15, "can_core_reset_cnt": 3, "canfd_disabled_samples": 1,
      })
check("Panda safetyTxBlocked delta retained",
      res.census["safety_tx_blocked"] == {"samples": 2, "first": 3, "last": 5, "delta": 2})

print("== segment time origin, staleness, and zero-vs-missing ==")
red = SegmentReducer("r", 1, keep_qualified=True)
ev = [
    ("initData", t0 - 500_000_000),                 # metadata before any live event
    car_state(t0, v_ego=25.0),
    angle_msg(t0, 0x01, 0x2C, 0x30),                # coarse (d0&0xF)<<8|d1 = 0x12C = 300 -> 450.0 deg
    eps(t0, b8=0x05),                               # +0.5 N.m (excluded by threshold)
    ref081(t0, 9),
    req08a(t0, 11, 9),
    b6(t0, 11, 18),
    ("initData", t0 + 10_000_000),                  # repeated startup metadata
    car_state(t0 + 100_000_000, v_ego=25.0),
]
for rec in ev:
    red.feed(rec)
res = red.finish()
check("origin anchored at first live event, not metadata",
      res.first_live_ns == t0)
check("repeated metadata never resets origin", res.last_live_ns == t0 + 100_000_000)
check("grid spans live window only", res.grid_samples == 3, str(res.grid_samples))
# grid rows at t0+100/150/200 ms sample CAN observations last made at t0, so
# beyond the 75 ms freshness window they are stale, not zero.
red2 = SegmentReducer("r", 1, keep_qualified=True)
for rec in ev[:7]:
    red2.feed(rec)
red2.feed(car_state(t0 + 200_000_000, v_ego=25.0))
# at t0+200 ms deliver a fully fresh clean set with torque 0.0 (b8=0x00):
red2.feed(angle_msg(t0 + 200_000_000))
red2.feed(eps(t0 + 200_000_000))
red2.feed(ref081(t0 + 200_000_000, 9))
red2.feed(req08a(t0 + 200_000_000, 11, 9))
red2.feed(b6(t0 + 200_000_000, 11, 18))
res2 = red2.finish()
check("stale signals excluded, not zero-filled",
      res2.exclusions.get("torque_stale", 0) > 0 and res2.exclusions.get("measured_stale", 0) > 0,
      str(res2.exclusions))
check("fresh numeric zero stays a value",
      len(res2.qualified) == 1 and res2.qualified[0].torque_nm == 0.0,
      str([(r.grid_ns, r.torque_nm) for r in res2.qualified]))
check("0.5 N.m exactly is excluded (strictly-below rule)",
      res2.exclusions.get("torque_ge_0p5nm", 0) == 2, str(res2.exclusions.get("torque_ge_0p5nm")))

print("== qualification funnel and invalid-torque exclusion ==")
red = SegmentReducer("r", 2, keep_qualified=True)
ev = [
    car_state(t0, v_ego=25.0), angle_msg(t0), eps(t0), ref081(t0, 5), req08a(t0, 11, 5), b6(t0, 11, 10),
    # grid at t0 qualifies (all fresh, torque 0.0)
    car_state(t0 + 50_000_000, v_ego=5.0),          # speed drop -> speed_le_10mps
    car_state(t0 + 100_000_000, v_ego=25.0, left=True),  # blinker
    car_state(t0 + 150_000_000, v_ego=25.0),
    # torque invalid at 150ms
    angle_msg(t0 + 150_000_000), eps(t0 + 150_000_000, b6=0x01),
    ref081(t0 + 150_000_000, 5), req08a(t0 + 150_000_000, 11, 5), b6(t0 + 150_000_000, 11, 10),
    # native ID 4 at 200ms: base-qualified with a non-11 ID retained
    car_state(t0 + 200_000_000, v_ego=25.0),
    angle_msg(t0 + 200_000_000), eps(t0 + 200_000_000),
    ref081(t0 + 200_000_000, 5), req08a(t0 + 200_000_000, 4, 5), b6(t0 + 200_000_000, 11, 10),
]
for rec in ev:
    red.feed(rec)
res = red.finish()
check("clean ID11 sample qualified", len(res.qualified) == 2 and res.qualified[0].native_id == 11,
      str([r.native_id for r in res.qualified]))
check("ID4 base sample qualified with ID retained", res.qualified[-1].native_id == 4)
check("speed exclusion counted", res.exclusions.get("speed_le_10mps", 0) == 1)
check("blinker exclusion counted", res.exclusions.get("blinker_active", 0) == 1)
check("invalid torque excluded", res.exclusions.get("torque_invalid", 0) == 1)
check("non-11 native ID counted by reason", res.exclusions.get("native_id_not_11", 0) >= 1)

print("== ID4 episode preservation (synthetic) ==")
red = SegmentReducer("r", 3, keep_qualified=True)
ev = [car_state(t0)]
for k in range(4):
    t = t0 + k * 30_000_000
    ev += [req08a(t, 4, -20 + k, level=100), angle_msg(t), eps(t), ref081(t, 1), b6(t, 0, 1)]
# 700ms gap then a fifth frame -> separate episode
t = t0 + 4 * 30_000_000 + 700_000_000
ev += [req08a(t, 4, 0, level=100)]
# non-ID4 frames nearby (B21=0x84 has the same low bits but differs as a full byte)
ev += [req08a(t + 10_000_000, 0x84, 3)]
for rec in ev:
    red.feed(rec)
res = red.finish()
eps_ = id4_episodes([res])
check("two ID4 episodes split on gap", len(eps_) == 2 and [e["frames"] for e in eps_] == [4, 1])
check("full B21 byte equality (0x84 is not ID4)", all(r["byte21"] == 4 for r in res.id4_rows)
      and len(res.id4_rows) == 5)
check("request level retained", all(r["request_level"] == 100 for r in res.id4_rows))
check("negative angle word preserved", res.id4_rows[0]["angle_word_hex"] == "ffec")

print("== original-log fixtures (independent pinned expectations) ==")
PINNED_SOURCE_SHA = {
    "3b-seg6": "4395189b7f8f24f4085f978447951a401b34be63907bae180688e57d8e1e0512",
    "3c-seg40": "73b946a8487c9d8f43d7ffe69287655775beaf595ec1099b6138f885ecb68902",
    "3c-seg43": "ab6b4fbe4d14227919a022dbc2c3091467446262d6896d26ea021ecc5d54c356",
    "3c-seg56": "ab3bf83295f653416567b75c770a8af83a847554968015f4fed4f650d6025d15",
    "3d-seg1-torque": "1437f8c6214274348c0be61e453d9c00626da43135b4872a0a1f76b74e54ddc3",
    "3d-seg56": "a02430cf010867fa3486a6d964dc8d832667ad666f2f0c96fe94a2588c8cf3a8",
    "3d-seg57": "e13dd3880d08c827240017c76119038a65371a7d96149ebc44f4639b5319a793",
}
for stem, sha in sorted(PINNED_SOURCE_SHA.items()):
    path = FIXTURES / f"{stem}.jsonl"
    if not path.exists():
        check(f"fixture {stem} present", False)
        continue
    prov, _events = load_fixture(path)
    check(f"{stem} provenance pins the original source", prov["source_sha256"] == sha)
    # The fixture format explicitly preserves payload byte count (DLC-equivalent
    # for these loggerd CANData records) instead of requiring reviewers to
    # infer it from a hex string.
    first_frame = next(obj for obj in path.read_text().splitlines()[1:] if '"dat"' in obj)
    frame_obj = json.loads(first_frame)
    check(f"{stem} fixture preserves DLC", frame_obj["dlc"] * 2 == len(frame_obj["dat"]))

# Witness reproduction: every expectation is pinned from the ORIGINAL reducer
# outputs still present under build/out/camry-stock-steering-20260904. The
# tracked reducer now reproduces the original absolute-50ms grid and exact
# live-origin definition, so no grid-phase tolerance is necessary.
wres = reduce_fixture(FIXTURES / "3c-seg43.jsonl", witness=True, witness_window_s=WITNESS_WINDOW_S)
rows = wres.witness_rows
check("witness sample count exact", len(rows) == 17, str(len(rows)))
check("witness first timestamp exact", rows[0].seg_s == 34.458562074, str(rows[0].seg_s))
check("witness last timestamp exact", rows[-1].seg_s == 35.258562074, str(rows[-1].seg_s))
check("witness measured median exact", med([r.measured_deg for r in rows]) == 3.2)
check("witness reference median exact", med([r.reference_deg for r in rows]) == 3.266256,
      str(med([r.reference_deg for r in rows])))
check("witness native-request median exact", med([r.native_req_deg for r in rows]) == 3.266256,
      str(med([r.native_req_deg for r in rows])))
check("witness openpilot median exact", med([r.op_target_deg for r in rows]) == 6.532513,
      str(med([r.op_target_deg for r in rows])))
check("witness driver torque maximum exact", max(abs(r.torque_nm) for r in rows) == 0.46)
check("witness all dual-active ID11",
      all(r.native_id == 11 and r.op_id == 11 and r.control_lat_active is True for r in rows))
check("witness requested actuator output retained",
      all(r.requested_steering_angle_deg is not None for r in rows))

# ID4 episodes: expected values pinned from the published §4.6 table.
PINNED_ID4 = {
    "3b-seg6": (28.626, 28.907, 12, False),
    "3c-seg40": (16.211, 18.741, 102, True),
    "3c-seg56": (43.964, 45.441, 60, False),
    "3d-seg56": (59.294, 59.969, 28, False),
    "3d-seg57": (19.884, 21.012, 46, False),
}
results = []
for stem in sorted(PINNED_ID4):
    path = FIXTURES / f"{stem}.jsonl"
    if path.exists():
        results.append(reduce_fixture(path))
eps_all = id4_episodes(results)
check("fixture episodes reproduce the published table",
      len(eps_all) == 5,
      str([(e["route_short"], e["frames"]) for e in eps_all]))
for ep in eps_all:
    key = f"{ep['route_short']}-seg{ep['segment']}"
    lo, hi, frames, active = PINNED_ID4[key]
    ok = (ep["frames"] == frames
          and abs(ep["first_segment_s"] - lo) <= 0.005
          and abs(ep["last_segment_s"] - hi) <= 0.005
          and ep["openpilot_lateral_active"] == active
          and ep["request_level_values"] == [100])
    check(f"ID4 {key} matches published episode", ok,
          f"frames={ep['frames']} span={ep['first_segment_s']}..{ep['last_segment_s']}")

print("== tracked full-corpus report (independent original-output expectations) ==")
report_path = REPO / "data/generated/camry_20260904_stock_steering_report.json"
manifest_path = REPO / "data/generated/camry_20260904_stock_steering_manifest.json"
report = json.loads(report_path.read_text())
manifest = json.loads(manifest_path.read_text())
check("full report covers exactly 253 source segments", report["totals"]["segments"] == 253)
check("native bus0/1/2 census exact", report["totals"]["native_can_records_buses_012"] == 27_173_143)
check("B6 send/return/reject census exact",
      report["totals"]["sendcan_b6"] == 751_664
      and report["totals"]["returned_b6"] == 751_628
      and report["totals"]["rejected_b6"] == 33)
check("native B6/0x131/0x2E4 absent exactly",
      report["totals"]["native_absent_addresses"] == {"0x0B6": 0, "0x131": 0, "0x2E4": 0})
check("Panda safetyTxBlocked corpus delta exact", report["totals"]["safety_tx_blocked_delta"] == 19)
check("all Panda health samples retained",
      sum(rr["census"]["panda_health"]["samples"] for rr in report["routes"]) == 150_642
      and [rr["census"]["panda_health"]["samples"] for rr in report["routes"]] == [65_524, 48_136, 36_982])
check("Panda health has no logged fault/heartbeat/RX-check-invalid samples",
      all(rr["census"]["panda_health"]["fault_status_counts"] == {"none": rr["census"]["panda_health"]["samples"]}
              and rr["census"]["panda_health"]["fault_count_max"] == 0
              and rr["census"]["panda_health"]["heartbeat_lost_samples"] == 0
              and rr["census"]["panda_health"]["safety_rx_checks_invalid_samples"] == 0
              for rr in report["routes"]))
route3d_health = next(rr["census"]["panda_health"] for rr in report["routes"] if rr["route_short"] == "3d")
check("route 3d bus0 transport endpoint exact",
      route3d_health["bus_error_max"]["0"] == {
          "receive_error_cnt": 127, "transmit_error_cnt": 0,
          "bus_off_cnt": 56, "can_core_reset_cnt": 1, "canfd_disabled_samples": 2,
      })

PINNED_ROUTE_STATS = {
    "3b": {"stock": (40_789, 0.998655, 1.0), "dual": 40_782, "divergent": 59},
    "3c": {"stock": (21_990, 0.999381, 2.0), "dual": 21_980, "divergent": 318},
    "3d": {"stock": (31_607, 0.996073, 1.0), "dual": 31_606, "divergent": 22},
}
for rr in report["routes"]:
    expected = PINNED_ROUTE_STATS[rr["route_short"]]
    stock = rr["comparison"]["stock_id11"]["reference081_vs_stock_raw"]
    dual = rr["comparison"]["dual_active"]["reference081_vs_stock_raw"]
    divergent = rr["comparison"]["divergent"]["reference081_vs_stock_raw"]
    check(f"route {rr['route_short']} stock-ID11 population/correlation/p90 exact",
          (stock["samples"], stock["correlation"], stock["p90_absolute"]) == expected["stock"],
          str(stock))
    check(f"route {rr['route_short']} dual-active population exact", dual["samples"] == expected["dual"])
    check(f"route {rr['route_short']} divergent population exact", divergent["samples"] == expected["divergent"])

w = report["witness"]
check("full report witness exact",
      w["samples"] == 17
      and w["first_sample_s"] == 34.458562074
      and w["last_sample_s"] == 35.258562074
      and w["median_measured_deg"] == 3.2
      and w["median_native_08a_request_deg"] == 3.266256
      and w["median_native_081_reference_deg"] == 3.266256
      and w["median_openpilot_target_deg"] == 6.532513)
check("full report ID4 count exact", report["id4_total_frames"] == 248 and len(report["id4_episodes"]) == 5)

quality = manifest["input_quality"]
check("manifest inventories exactly 253 source files", len(manifest["routes"]) == 253)
check("all source files readable", not quality["unreadable"] and all(e["status"] == "readable" for e in manifest["routes"]))
check("no missing/duplicate/gapped source inputs",
      not quality["missing_route_dirs"]
      and not quality["duplicates"]
      and all(not gaps for gaps in quality["segment_gaps"].values())
      and all(not dups for dups in quality["duplicate_segment_numbers"].values()))
check("all three expected route populations inventoried",
      {r: sum(e["route"] == r for e in manifest["routes"]) for r in (
          "0000003b--62262eb7a1", "0000003c--97b9e7a69a", "0000003d--0e812cecba"
      )} == {
          "0000003b--62262eb7a1": 110,
          "0000003c--97b9e7a69a": 81,
          "0000003d--0e812cecba": 62,
      })
check("source-order timestamp regressions are explicitly reported",
      len(quality["out_of_order_segments"]) == 253
      and all(e["events"] > 0 and e["max_timestamp_regression_ns"] > 0
              for e in quality["out_of_order_segments"]))
check("manifest pins parser schema identity",
      manifest["parser"]["log_schema_sha256"] == "f839ceeb3041dac6aea4b2f68f5afd52db0e8c3367dd1fe53eb83a2be7ad01cc"
      and manifest["parser"]["sampling_revision"] == "original-build-tmp-extractor-compatible:absolute-50ms-grid-v1")
check("every source inventory entry has identity and event bounds",
      all(e["bytes"] > 0 and len(e["sha256"]) == 64 and e["events_total"] > 0
              and e["first_live_ns"] is not None and e["last_live_ns"] is not None
              and e["service_event_counts"] for e in manifest["routes"]))
check("current-cereal pandaStates normalize one-for-one in this corpus",
      sum(e["event_counts"].get("pandaState", 0) for e in manifest["routes"]) == 150_642
      == sum(e["service_event_counts"].get("pandaStates", 0) for e in manifest["routes"]))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
