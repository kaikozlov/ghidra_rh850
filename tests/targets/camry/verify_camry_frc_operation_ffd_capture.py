#!/usr/bin/env python3
"""Verify the read-only exact-Camry FRC Operation-FFD acquisition tool."""
from __future__ import annotations

import io
import json
import tempfile
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from tools.targets.camry.live import camry_frc_operation_ffd_capture as cap
from tools.targets.camry.live.camry_frc_lta_capture import iter_canbin_records

passed = failed = 0


def check(label: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][camry_frc_operation_ffd_capture] {label}" +
          (f" ({detail})" if detail else ""))


check("AB11 builder", cap.build_ab11() == bytes.fromhex("ab11"))
check("AB12 builder", cap.build_ab12(0x2845) == bytes.fromhex("ab122845"))
check("AB13 builder", cap.build_ab13(0x2845, 0x1234) == bytes.fromhex("ab1328451234"))

robs = cap.parse_eb11(bytes.fromhex("eb11209d28182845240f"))
check("EB11 parser", robs == [0x209D, 0x2818, 0x2845, 0x240F])
records = cap.parse_eb12(bytes.fromhex("eb122845000100020010"), 0x2845)
check("EB12 parser + behavior echo", records == [1, 2, 0x10])

check("UDS negative parser", cap.negative_response(bytes.fromhex("7fab31")) == {
    "request_sid": "0xAB", "nrc": "0x31", "raw": "7fab31"
})


class FakePanda:
    """USB boundary only: exercise the real transport and on-disk capture."""

    def __init__(self, fail_capture=False, fail_reset=False):
        self.fail_capture = fail_capture
        self.fail_reset = fail_reset
        self.batches = []
        self.safety_mode = None

    def set_safety_mode(self, mode, *_args):
        self.safety_mode = mode

    def can_send(self, address, frame, bus):
        assert (address, bus) == (0x792, 0)
        if frame[0] == 0x30:
            return
        request = frame[1:1 + frame[0]]
        if request == bytes.fromhex("1001") and self.fail_reset:
            self.batches.append([(0x123, b"\xaa\xbb", 2)])
            raise OSError("reset send failed")
        response = {
            bytes.fromhex("22f181"): bytes.fromhex("62f181") + b"8646F3315000",
            bytes.fromhex("1003"): bytes.fromhex("5003"),
            bytes.fromhex("ab11"): bytes.fromhex("7fab31" if self.fail_capture else "eb112845"),
            bytes.fromhex("ab122845"): bytes.fromhex("eb1228450001"),
            bytes.fromhex("ab1328450001"): bytes.fromhex("eb13284500010157db02ffce"),
            bytes.fromhex("1001"): bytes.fromhex("5001"),
        }[request]
        if len(response) <= 7:
            frames = [(bytes([len(response)]) + response).ljust(8, b"\0")]
        else:
            frames = [bytes([0x10 | len(response) >> 8, len(response) & 0xFF]) + response[:6]]
            for sequence, offset in enumerate(range(6, len(response), 7), 1):
                frames.append((bytes([0x20 | sequence & 0xF]) + response[offset:offset + 7]).ljust(8, b"\0"))
        self.batches.append([(0x79A, frame, 0) for frame in frames])
        if request == bytes.fromhex("1001"):
            # This arrives after the reset response, during the final drain.
            self.batches.append([(0x123, b"\xaa\xbb", 2)])

    def can_recv(self):
        return self.batches.pop(0) if self.batches else []


for label, fail_capture, fail_reset in (
    ("normal capture", False, False),
    ("acquisition failure", True, False),
    ("acquisition and reset failure", True, True),
):
    panda = FakePanda(fail_capture, fail_reset)
    panda_class = Mock(return_value=panda)
    panda_class.list.return_value = ["offline-fixture"]
    opened = {}
    original_open = Path.open

    def track_open(path, *args, _open=original_open, _opened=opened, **kwargs):
        stream = _open(path, *args, **kwargs)
        if path.name in ("can.bin", "records.ndjson"):
            _opened[path.name] = stream
        return stream

    with tempfile.TemporaryDirectory() as directory:
        out_dir = Path(directory) / "capture"
        caught = None
        with patch.object(cap, "load_panda_class", return_value=panda_class), \
                patch.object(cap, "find_pandad_processes", return_value=[]), \
                patch.object(Path, "open", track_open), redirect_stdout(io.StringIO()):
            try:
                cap.execute(out_dir, requested_robs=[0x2845], all_robs=False, max_records_per_rob=1)
            except cap.ProtocolError as exc:
                caught = exc

        result = json.loads((out_dir / "operation_ffd.json").read_text())
        with (out_dir / "can.bin").open("rb") as stream:
            frames = [(bus, address, data) for _, bus, address, data in iter_canbin_records(stream)]

        check(f"{label}: both output streams close",
              opened["can.bin"].closed and opened["records.ndjson"].closed)
        check(f"{label}: final CAN drain is persisted",
              frames[-1] == (2, 0x123, b"\xaa\xbb") and result["frames_by_bus"]["2"] == 1)
        check(f"{label}: silent safety restored", panda.safety_mode == cap.SILENT_SAFETY_MODEL)
        if fail_capture:
            check(f"{label}: primary acquisition error survives cleanup",
                  caught is not None and "AB11 rejected" in str(caught) and "AB11 rejected" in result["error"])
        else:
            check(f"{label}: record remains readable after cleanup",
                  caught is None and result["error"] is None and
                  json.loads((out_dir / "records.ndjson").read_text())["blocks"][0]["decoded"][0]["physical"] == "-0.050")
        if fail_reset:
            check(f"{label}: reset failure remains separate",
                  result.get("default_session_error") == "OSError: reset send failed" and
                  "default_session_response" not in result)
        else:
            check(f"{label}: reset response is confirmed and recorded",
                  result.get("default_session_response") == "5001" and
                  "default_session_error" not in result and
                  (0, 0x79A, bytes.fromhex("0250010000000000")) in frames)


print(f"\nSummary: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
