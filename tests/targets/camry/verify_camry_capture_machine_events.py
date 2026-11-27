#!/usr/bin/env python3
"""Verify capture parsing, event quantization, and candump output."""
from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tools import REPO_ROOT
from tools.emulation.p1me_machine import load_scenario
from tools.targets.camry.analysis.convert_camry_capture_machine_events import (
    CaptureFormatError,
    candump_line,
    decode_firmware_rules,
    load_capture,
    quantize,
)

MODULE = "tools.targets.camry.analysis.convert_camry_capture_machine_events"
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    ok = bool(cond)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def frame(t, addr, bus, data, length=None):
    payload = bytes.fromhex(data) if isinstance(data, str) else data
    return {"t": t, "addr": addr, "bus": bus, "data": payload.hex(),
            "len": len(payload) if length is None else length}


def write_capture(path: Path, frames, gz=True):
    duration = frames[-1]["t"] if frames and isinstance(frames[-1].get("t"), (int, float)) else 0
    raw = json.dumps({"capture": "synthetic", "duration_s": duration,
                      "frames": frames}, separators=(",", ":")).encode()
    if gz:
        with open(path, "wb") as stream:
            with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as body:
                body.write(raw)
    else:
        path.write_bytes(raw)
    return path


def run_converter(capture: Path, out: Path, *extra: str) -> dict:
    proc = subprocess.run([sys.executable, "-m", MODULE, str(capture),
                           "--output-dir", str(out), *extra],
                          cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise AssertionError(f"converter failed: {proc.stderr[-400:]}")
    return json.loads(proc.stdout)


with tempfile.TemporaryDirectory() as td:
    tmp = Path(td)
    out = tmp / "out"

    print("== exact-firmware rule tables ==")
    rx_rules, tx_rules = decode_firmware_rules()
    check("FD rule 0x025 carries descriptor DLC 32", rx_rules[0x25] == {
        "rule": 30, "label": 0x27, "fifo": 5, "fd": True, "extended": False, "dlc": 32})
    check("classic rule 0x127 carries label and FIFO 5", rx_rules[0x127]["label"] == 0x1D
          and rx_rules[0x127]["fifo"] == 5 and rx_rules[0x127]["dlc"] == 8)
    check("single-byte rule 0x490 keeps DLC 1", rx_rules[0x490]["dlc"] == 1)
    check("diagnostic 0x7A1 rule from GAFLFDP one-hot", rx_rules[0x7A1]["rule"] == 43
          and rx_rules[0x7A1]["label"] == 0x34 and rx_rules[0x7A1]["fifo"] == 5)
    check("diagnostic 0x777 rule follows 0x7A1", rx_rules[0x777]["rule"] == 44
          and rx_rules[0x777]["label"] == 0x35)
    check("EPS TX records split FD and classic buffers",
          tx_rules[0x30]["fd"] is True and tx_rules[0x30]["buffer"] == 16
          and tx_rules[0x351]["fd"] is False and tx_rules[0x351]["buffer"] == 19)
    check("diagnostic responses are EPS TX records",
          tx_rules[0x7A9]["buffer"] == 16 and tx_rules[0x7A8]["buffer"] == 19)

    print("== quantization boundaries ==")
    frames = [frame(0.010, 0x127, 1, "00" * 8), frame(0.009999, 0x127, 1, "01" * 8),
              frame(0.010001, 0x127, 1, "02" * 8)]
    ordered, moved = quantize(load_capture(write_capture(tmp / "bounds.json.gz", frames))["frames"], 1)
    check("frame exactly on a period boundary lands in the new period",
          ordered[1]["period"] == 2 and ordered[1]["t"] == 0.010)
    check("frames before and after the boundary stay in adjacent periods",
          ordered[0]["period"] == 1 and ordered[2]["period"] == 2)
    check("period-quantized stream keeps capture order inside one period",
          moved == 2 and [f["index"] for f in ordered] == [1, 0, 2])
    scaled, _ = quantize(load_capture(write_capture(tmp / "scaled.json.gz", frames))["frames"], 100)
    check("cycle-instruction scale multiplies the period index",
          scaled[1]["after_instructions"] == 200 and scaled[0]["after_instructions"] == 100)

    print("== same-period frames ==")
    frames = [frame(0.001, 0x127, 1, "0A" * 8), frame(0.002, 0x127, 1, "0B" * 8),
              frame(0.006, 0x127, 1, "0C" * 8)]
    capture = write_capture(tmp / "same-period.json.gz", frames)
    report = run_converter(capture, out)
    check("two frames of one identifier inside one period are both kept",
          report["per_id"]["0x127"]["can-rx"] == 3)
    check("additional frames in one period are counted per identifier",
          report["same_period_frames"] == {"0x127": 1})
    scenario = json.loads((out / "same-period.scenario.json").read_text())
    check("same-period events preserve payload order and keep a shared boundary",
          [(e["after_instructions"], e["data_hex"]) for e in scenario["events"]]
          == [(0, "0a" * 8), (0, "0b" * 8), (1, "0c" * 8)])

    frames = [frame(0.020, 0x127, 1, "0D" * 8), frame(0.001, 0x127, 1, "0E" * 8)]
    _, moved = quantize(load_capture(write_capture(tmp / "reorder.json.gz", frames))["frames"], 1)
    check("non-monotonic timestamps are reported as reordered frames", moved == 2)

    print("== capture parsing boundaries ==")
    frames = [frame(0.001, 0x127, 1, "00" * 8, length=7)]
    try:
        load_capture(write_capture(tmp / "badlen.json.gz", frames))
        check("recorded length must match payload bytes", False)
    except CaptureFormatError:
        check("recorded length must match payload bytes", True)
    frames = [frame(0.001, 0x127, 1, "00" * 8)]
    del frames[0]["t"]
    try:
        load_capture(write_capture(tmp / "missing.json.gz", frames))
        check("missing frame field fails parsing", False)
    except CaptureFormatError:
        check("missing frame field fails parsing", True)
    try:
        load_capture(write_capture(tmp / "empty.json.gz", []))
        check("empty capture fails parsing", False)
    except CaptureFormatError:
        check("empty capture fails parsing", True)
    plain = load_capture(write_capture(tmp / "plain.json", [frame(0.001, 0x127, 1, "00" * 8)], gz=False))
    check("plain (uncompressed) JSON captures parse", len(plain["frames"]) == 1)

    print("== conversion partition and scenario identity ==")
    frames = [
        frame(0.0012, 0x127, 1, "11" * 8),      # accepted classic rule, period 0
        frame(0.0062, 0x025, 1, "22" * 32),     # accepted FD rule, period 1
        frame(0.0113, 0x030, 1, "33" * 32),     # EPS FD transmit, period 2
        frame(0.0164, 0x7A8, 1, "065040003201f400"),  # EPS classic transmit, period 3
        frame(0.0040, 0x08A, 1, "44" * 8),      # on the EPS bus, acceptance-filtered
        frame(0.0050, 0x127, 0, "55" * 8),      # other bus
    ]
    capture = write_capture(tmp / "partition.json.gz", frames)
    report = run_converter(capture, out)
    check("accepted rules, EPS TX and filtered frames partition per identifier",
          report["per_id"] == {"0x25": {"can-rx": 1, "can-tx-complete": 0},
                               "0x30": {"can-rx": 0, "can-tx-complete": 1},
                               "0x127": {"can-rx": 1, "can-tx-complete": 0},
                               "0x7A8": {"can-rx": 0, "can-tx-complete": 1}}
          and report["frames_dropped"]["per_id"] == {"0x8A": 1}
          and report["frames_dropped"]["other_bus"] == {"0": 1})
    scenario = json.loads((out / "partition.scenario.json").read_text())
    check("FD rules carry the fd flag and label metadata",
          any(e.get("fd") is True and e.get("label") == 0x27 for e in scenario["events"]))
    check("EPS transmits become tx-complete events with the mapped buffers",
          [e["buffer"] for e in scenario["events"] if e["kind"] == "can-tx-complete"] == [16, 19])
    capture_source = {"kind": "capture", "path": str(capture),
                      "sha256": hashlib.sha256(capture.read_bytes()).hexdigest(), "bus": 1}
    check("capture identity travels in the scenario source object",
          scenario["source"] == capture_source)
    check("event schedule carries the quantized period index",
          [e["after_instructions"] for e in scenario["events"]] == [0, 1, 2, 3])

    print("== scenario loader acceptance ==")
    loaded = load_scenario(out / "partition.scenario.json")
    check("emitted scenario passes the machine scenario loader",
          len(loaded["events"]) == 4 and loaded["registers"]["sp"] == "0xfebe2000"
          and loaded["artifacts"][0]["address"] == "0xfebe0000")
    check("loader keeps rx FIFO and post-filter boundary",
          all(e["fifo"] == 5 and e["boundary"] == "post-filter"
              for e in loaded["events"] if e["kind"] == "can-rx"))
    check("loader passes the capture source object through unchanged",
          loaded["source"] == capture_source)

    print("== route NDJSON captures ==")
    rows = [
        [0, 16_400_000, 1, 0x127, "aa" * 8],
        [0, 16_400_000, 2, 0x127, "aa" * 8],   # same frame bridged on the other bus
        [1, 21_500_000, 1, 0x1FE00002, ""],    # extended id, zero length
        [1, 21_600_000, 1, 0x030, "bb" * 32],  # EPS FD transmit, > 8 bytes
    ]
    ndjson = tmp / "route.ndjson.gz"
    ndjson.write_bytes(gzip.compress(
        b"".join(json.dumps(row).encode() + b"\n" for row in rows), mtime=0,
    ))
    report = run_converter(ndjson, out, "--bus", "1")
    check("ndjson rows load and select one bus",
          report["capture"]["format"] == "route-can-ndjson"
          and report["per_id"] == {"0x30": {"can-rx": 0, "can-tx-complete": 1},
                                   "0x127": {"can-rx": 1, "can-tx-complete": 0}}
          and report["frames_dropped"]["per_id"] == {"0x1FE00002": 1})
    log = (out / "route.candump.log").read_text().splitlines()
    check("ndjson conversion keeps candump formatting boundaries",
          log == ["(000.016400) can1 127#" + "AA" * 8,
                  "(000.021600) can1 030##0" + "BB" * 32])
    scenario = json.loads((out / "route.scenario.json").read_text())
    check("ndjson source object identifies the compressed input and selected bus",
          scenario["source"] == {"kind": "capture", "path": str(ndjson),
                                 "sha256": hashlib.sha256(ndjson.read_bytes()).hexdigest(), "bus": 1})
    for bad, why in [([1, 2, 3], "short row"),
                     ([0, -5, 1, 0x127, "aa"], "negative timestamp"),
                     ([0, 5, 1, 0x127, "zz"], "bad hex")]:
        bad_path = tmp / "bad.ndjson"
        bad_path.write_text(json.dumps(bad) + "\n")
        try:
            load_capture(bad_path)
            check(f"ndjson {why} fails parsing", False)
        except CaptureFormatError:
            check(f"ndjson {why} fails parsing", True)

    print("== candump formatting ==")
    check("classic frame uses three-digit id and plain hash separator",
          candump_line(frame(1.5, 0x127, 1, "AA" * 8)) == "(001.500000) can1 127#" + "AA" * 8)
    check("FD frame uses ## with the unrecorded-flags digit",
          candump_line(frame(0.016697, 0x030, 1, "BB" * 32))
          == "(000.016697) can1 030##0" + "BB" * 32)
    check("extended identifier uses eight digits",
          candump_line(frame(0.0, 0x1FE00002, 1, "")) == "(000.000000) can1 1FE00002#")
    check("zero-length classic frame keeps the hash separator",
          candump_line(frame(0.0, 0x51E, 1, "")) == "(000.000000) can1 51E#")
    log = (out / "partition.candump.log").read_text().splitlines()
    check("candump log exports exactly the converted traffic",
          len(log) == 4 and log[2] == "(000.011300) can1 030##0" + "33" * 32
          and log[3] == "(000.016400) can1 7A8#065040003201F400")

print()
print(f"passed {passed} failed {failed}")
raise SystemExit(1 if failed else 0)
