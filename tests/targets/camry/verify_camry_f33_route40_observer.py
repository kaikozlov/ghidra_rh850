"""Verify the one-boot exact-F33 0x090 signer/route40 experiment."""
from __future__ import annotations

import json
import subprocess
import sys

import tools.targets.camry.research.ram_runtime.routing.build_camry_f33_route40_observer as build
import tools.targets.camry.research.ram_runtime.routing.camry_f33_route40_observer as observer
from tools import REPO_ROOT

ROOT = REPO_ROOT
passed = failed = 0


def check(name: str, value: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(value)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


run = subprocess.run(
    [sys.executable, str(build.BUILDER)],
    cwd=ROOT,
    capture_output=True,
    check=False,
    text=True,
)
check("one-boot builder succeeds", run.returncode == 0, run.stderr[-400:])
out = build.DEFAULT_OUTPUT_DIR
meta = json.loads((out / "camry_f33_route40_observer.json").read_text())
resident = (out / meta["resident"]["path"]).read_bytes()
helper = (out / meta["helper"]["path"]).read_bytes()
payload = (out / meta["authenticated_payload"]["path"]).read_bytes()
check(
    "current resident/helper bounds",
    len(resident) == observer.RESIDENT_SIZE == 338 and len(helper) == observer.HELPER_SIZE == 368,
)
check("current authenticated payload is exact 4KiB", len(payload) == 4096)

plan = observer.plan(None)
check(
    "plan uses only physical ignition transitions",
    plan["field_sequence"] == [
        "OFF -> NRTD; install one signer/observer carrier",
        "NRTD -> READY/Park/stationary without OFF",
        "run: capture native 0x090, sign future message2, arm, transmit once, read latch",
        "READY -> OFF to remove resident",
    ]
    and plan["impossible_transitions_required"] is False,
)
check(
    "control protocol separates signing and observer arm",
    observer.command_frame(1, 0x30, 0x44332211) == bytes.fromhex("00f5013011223344")
    and observer.command_frame(2, 0x10, bytes.fromhex("81234567"))
    == bytes.fromhex("00f5021081234567"),
)

raw = bytearray(observer.MAILBOX_SIZE)
raw[:4] = observer.MAILBOX_MAGIC.to_bytes(4, "little")
raw[4] = 1
raw[5:8] = bytes((7, 2, 0))
raw[8:10] = (0x1FF).to_bytes(2, "little")
raw[0x0A:0x0C] = bytes((0, 1))
raw[0x0C:0x10] = (16).to_bytes(4, "little")
raw[0x44:0x47] = bytes((0, 1, 42))
raw[0x48:0x4C] = (1).to_bytes(4, "little")
raw[0x4C:0x50] = (4).to_bytes(4, "little")
raw[0x50:0x54] = bytes.fromhex("81234567")
raw[0x54:0x74] = bytes(range(32))
state = observer.decode_mailbox(bytes(raw))
check(
    "mailbox binds command5 completion and sticky full-frame latch",
    state["magic_ok"]
    and state["version_ok"]
    and state["input_bitmap"] == 0x1FF
    and state["done_flag"] == 1
    and state["matched"]
    and not state["armed"]
    and state["generation_at_match"] == 42
    and state["latched_frame_hex"] == bytes(range(32)).hex(),
)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
