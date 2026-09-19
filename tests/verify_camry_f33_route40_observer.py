#!/usr/bin/env python3
"""Verify the one-boot exact-F33 0x090 signer/route40 experiment."""
from __future__ import annotations
import hashlib, json, subprocess, sys, tempfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from exploit.ephemeral_runtime import build_camry_f33_route40_observer as build  # noqa: E402
from exploit.ephemeral_runtime import camry_f33_route40_observer as observer  # noqa: E402
from tools.targets.camry.builders import build_camry_f33_car_kit as car_kit  # noqa: E402

passed = failed = 0
def check(name, value, detail=""):
    global passed, failed
    ok=bool(value); passed+=ok; failed+=not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))
def sha(value): return hashlib.sha256(value).hexdigest()

run=subprocess.run([sys.executable,str(build.BUILDER)],cwd=ROOT,capture_output=True,text=True)
check("one-boot builder succeeds",run.returncode==0,run.stderr[-400:])
out=build.DEFAULT_OUTPUT_DIR
meta=json.loads((out/"camry_f33_route40_observer.json").read_text())
resident=(out/meta["resident"]["path"]).read_bytes(); helper=(out/meta["helper"]["path"]).read_bytes()
stage=(out/meta["staging"]["path"]).read_bytes(); payload=(out/meta["authenticated_payload"]["path"]).read_bytes()
audit=json.loads((ROOT/"exploit/ephemeral_runtime/audited_camry_f33_route40_observer_build.json").read_text())
audited=(ROOT/"exploit/ephemeral_runtime/audited/camry_f33_route40_observer.bin").read_bytes()
check("audited artifacts reproduce exactly",meta==audit and stage==audited)
check("resident/helper identities and bounds are exact",
      len(resident)==observer.RESIDENT_SIZE==338 and len(helper)==observer.HELPER_SIZE==368 and
      sha(resident)==observer.EXPECTED_RESIDENT_SHA256 and sha(helper)==observer.EXPECTED_HELPER_SHA256 and
      meta["resident"]["headroom"]==186 and meta["helper"]["headroom"]==656)
check("authenticated payload is exact",len(payload)==4096 and sha(stage)==observer.EXPECTED_STAGING_SHA256 and
      sha(payload)==observer.EXPECTED_PAYLOAD_SHA256)
check("plan uses only physical ignition transitions",observer.plan(None)["field_sequence"]==[
      "OFF -> NRTD; install one signer/observer carrier",
      "NRTD -> READY/Park/stationary without OFF",
      "run: capture native 0x090, sign future message2, arm, transmit once, read latch",
      "READY -> OFF to remove resident"] and observer.plan(None)["impossible_transitions_required"] is False)
check("control protocol separates signing and observer arm",
      observer.command_frame(1,0x30,0x44332211)==bytes.fromhex("00f5013011223344") and
      observer.command_frame(2,0x10,bytes.fromhex("81234567"))==bytes.fromhex("00f5021081234567"))
raw=bytearray(observer.MAILBOX_SIZE); raw[:4]=observer.MAILBOX_MAGIC.to_bytes(4,"little"); raw[4]=1
raw[5:8]=bytes((7,2,0)); raw[8:10]=(0x1ff).to_bytes(2,"little"); raw[0x0a:0x0c]=bytes((0,1))
raw[0x0c:0x10]=(16).to_bytes(4,"little"); raw[0x44:0x47]=bytes((0,1,42))
raw[0x48:0x4c]=(1).to_bytes(4,"little"); raw[0x4c:0x50]=(4).to_bytes(4,"little")
raw[0x50:0x54]=bytes.fromhex("81234567"); raw[0x54:0x74]=bytes(range(32))
state=observer.decode_mailbox(bytes(raw))
check("mailbox binds command5 completion and sticky full-frame latch",
      state["magic_ok"] and state["version_ok"] and state["input_bitmap"]==0x1ff and
      state["done_flag"]==1 and state["matched"] and not state["armed"] and
      state["generation_at_match"]==42 and state["latched_frame_hex"]==bytes(range(32)).hex())
source=(ROOT/"exploit/ephemeral_runtime/camry_f33_route40_observer.S").read_text()
helper_source=(ROOT/"exploit/ephemeral_runtime/camry_f33_route40_observer_helper.S").read_text()
check("helper is live in the stock inter-tick wait after tick224",
      source.index("jarl32 helper_entry, lp") < source.index("tst1 4, -0x4eef[r0]") and
      "tst1 7, 0[ep]" in source and "jarl32 command5_sync, lp" in helper_source)
launcher=(ROOT/"exploit/ephemeral_runtime/camry_f33_route40_observer_launcher.sh").read_text()
runbook=(ROOT/"exploit/ephemeral_runtime/camry_f33_090_route40_experiment.md").read_text()
check("launcher/runbook contain no impossible transition or prepared artifact",
      "run PREPARED_JSON" not in launcher and "--prepared" not in launcher and
      "does **not** permit `READY -> NRTD`" in runbook and "NRTD -> READY" in runbook and
      "pre-READY message generation" in runbook)
with tempfile.TemporaryDirectory() as td:
    kit=Path(td)/"kit"; manifest=car_kit.build(kit,ROOT.parent/"kai-openpilot")
    experiment=manifest["ram_experiments"]["valid_090_route40_experiment"]
    check("car kit packages one-boot experiment",sha((kit/"ram_payloads/camry_f33_route40_observer_payload.bin").read_bytes())==observer.EXPECTED_PAYLOAD_SHA256 and
          experiment["payload_sha256"]==observer.EXPECTED_PAYLOAD_SHA256 and
          (kit/"f33-route40").is_file() and (kit/"090_ROUTE40_EXPERIMENT.md").is_file())

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
