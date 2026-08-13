#!/usr/bin/env python3
"""Verify the MAC28-only transport/proof harness and vendored openpilot ablation."""

from __future__ import annotations

import hashlib
import json
import random
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from exploit.behavioral_proof.analyze_forwarding import analyze, iter_capture
from exploit.behavioral_proof.mac28 import (
    MAC28_IDS,
    STOCK_CAMERA_PROOF_IDS,
    CanFrame,
    changed_bit_positions,
    invalidate_mac28,
    validate_forward_pair,
)
from exploit.behavioral_proof.validate_trial import SCHEMA, validate_trial

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


print("== pure MAC28 transform ==")
rng = random.Random(0x28)
for index in range(64):
    source = bytes(rng.randrange(256) for _ in range(8))
    result = invalidate_mac28(source)
    check(f"random {index}: bytes0..3 unchanged", result[:4] == source[:4])
    check(f"random {index}: byte4 high nibble preserved", result[4] & 0xF0 == source[4] & 0xF0)
    check(f"random {index}: MAC28 exactly zero", result[4] & 0x0F == 0 and result[5:] == b"\x00\x00\x00")
    allowed = set(range(32, 36)) | set(range(40, 64))
    check(f"random {index}: no bit outside MAC28 changes", not (changed_bit_positions(source, result) - allowed))

try:
    invalidate_mac28(b"\x00" * 7)
except ValueError:
    check("non-8-byte protected frame is rejected", True)
else:
    check("non-8-byte protected frame is rejected", False)

print("\n== bounded four-ID forwarding model ==")
source_payloads = {
    0x191: bytes.fromhex("1122334455667788"),
    0x412: bytes.fromhex("8899aabbccddeeff"),
    0x2E4: bytes.fromhex("01020304af112233"),
    0x131: bytes.fromhex("1020304075445566"),
}
stock_frames = []
invalid_frames = []
for address in sorted(STOCK_CAMERA_PROOF_IDS):
    src = source_payloads[address]
    stock_frames.extend((CanFrame(address, 1, src), CanFrame(address, 2, src)))
    fwd = invalidate_mac28(src) if address in MAC28_IDS else src
    invalid_frames.extend((CanFrame(address, 1, src), CanFrame(address, 2, fwd)))
stock_report = analyze(stock_frames, source_bus=1, forward_bus=2, mode="stock")
invalid_report = analyze(invalid_frames, source_bus=1, forward_bus=2, mode="invalid-mac28")
check("stock-mode control requires byte-identical forwarding for all four IDs", stock_report["pass"])
check("invalid mode accepts exact MAC28-only transform", invalid_report["pass"])

bad = list(invalid_frames)
bad_index = next(i for i, frame in enumerate(bad) if frame.bus == 2 and frame.address == 0x2E4)
wrong = bytearray(bad[bad_index].data)
wrong[4] ^= 0x10
bad[bad_index] = CanFrame(0x2E4, 2, bytes(wrong))
bad_report = analyze(bad, source_bus=1, forward_bus=2, mode="invalid-mac28")
check("high-nibble/freshness mutation fails ablation analyzer", not bad_report["pass"] and any("high nibble" in item for item in bad_report["errors"]))

bad_control = list(invalid_frames)
control_index = next(i for i, frame in enumerate(bad_control) if frame.bus == 2 and frame.address == 0x191)
wrong_control = bytearray(bad_control[control_index].data)
wrong_control[0] ^= 1
bad_control[control_index] = CanFrame(0x191, 2, bytes(wrong_control))
check("non-protected control-frame mutation fails analyzer", not analyze(bad_control, source_bus=1, forward_bus=2, mode="invalid-mac28")["pass"])

print("\n== vendored one-off openpilot experiment provenance ==")
patch_path = REPO / "exploit" / "behavioral_proof" / "kai-openpilot-mac28-ablation.patch"
meta_path = REPO / "exploit" / "behavioral_proof" / "kai-openpilot-mac28-ablation.json"
audit_path = REPO / "exploit" / "behavioral_proof" / "openpilot_ablation_audit.json"
check("external openpilot commit patch is vendored", patch_path.is_file())
check("external openpilot commit provenance is vendored", meta_path.is_file())
meta = json.loads(meta_path.read_text(encoding="utf-8"))
check("external provenance pins full commit/parent SHAs", len(meta.get("commit", "")) == 40 and len(meta.get("parent", "")) == 40)
check("external provenance explicitly records not pushed", meta.get("pushed") is False)
check("vendored patch hash matches provenance", meta.get("patch", {}).get("sha256") == sha(patch_path))
patch = patch_path.read_text(encoding="utf-8")
for required in (
    "diff --git a/board/drivers/fdcan.h b/board/drivers/fdcan.h",
    "diff --git a/opendbc/safety/modes/toyota.h b/opendbc/safety/modes/toyota.h",
    "diff --git a/opendbc/car/toyota/carcontroller.py b/opendbc/car/toyota/carcontroller.py",
):
    check(f"external combined patch contains {required}", required in patch)
for address in ("0x191", "0x412", "0x2E4", "0x131"):
    check(f"external patch explicitly scopes proof ID {address}", address.lower() in patch.lower())
check("external patch contains MAC28 nibble mask", "0xf0" in patch.lower())
check("external patch references forwarding checksum ordering", "can_set_checksum" in patch)
check("machine audit from actual external diff exists", audit_path.is_file())
if audit_path.is_file():
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    text = json.dumps(audit, sort_keys=True).lower()
    check("audit pins same external commit", meta["commit"].lower() in text)
    check("audit records the four stock-camera proof IDs", all(value in text for value in ("0x191", "0x412", "0x2e4", "0x131")))
    check("audit records MAC28 high-nibble preservation", "high" in text and "nibble" in text)

print("\n== read-only evidence collectors ==")
capture_source = (REPO / "exploit" / "behavioral_proof" / "capture_can.py").read_text(encoding="utf-8").lower()
dtc_source = (REPO / "exploit" / "behavioral_proof" / "capture_eps_dtc.py").read_text(encoding="utf-8").lower()
steer_source = (REPO / "exploit" / "behavioral_proof" / "capture_steering_state.py").read_text(encoding="utf-8").lower()
check("raw CAN collector never calls can_send", "can_send" not in capture_source)
check("raw CAN collector never changes Panda safety mode", "set_safety_mode" not in capture_source)
check("DTC collector requests report-by-status without clear-DTC", "\\x02\\xff" in dtc_source and "clear_diagnostic" not in dtc_source and "clear_dtc" not in dtc_source)
check("steering evidence records EPS torque/fault fields", all(value in steer_source for value in ("steeringtorqueeps", "steerfaulttemporary", "steerfaultpermanent")))

print("\n== complete causal-proof schema ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    # Reuse a real semantic Gate-2 manifest, copied under the synthetic trial so
    # every required artifact is local/SHA-bound like a hardware evidence bundle.
    source_manifest = REPO / "data" / "generated" / "secoc_patch_manifest_4512000.json"
    manifest = temp / "manifest.json"
    manifest.write_bytes(source_manifest.read_bytes())

    def artifact(name: str, content: str) -> dict:
        path = temp / name
        path.write_text(content, encoding="utf-8")
        return {"path": path.name, "sha256": sha(path)}

    f181_hex = "018965B451200000000000"

    def analysis_artifact(name: str, mode: str, raw_sha: str) -> dict:
        path = temp / name
        path.write_text(
            json.dumps(
                {
                    "schema": "toyota-secoc-mac28-forwarding-analysis-v1",
                    "mode": mode,
                    "pass": True,
                    "source_bus": 1,
                    "forward_bus": 2,
                    "capture": {"sha256": raw_sha},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return {"path": path.name, "sha256": sha(path)}

    def dtc_artifact(name: str) -> dict:
        path = temp / name
        path.write_text(
            json.dumps(
                {
                    "schema": "toyota-eps-dtc-snapshot-v1",
                    "f181_hex": f181_hex,
                    "request": "19 02 FF",
                    "response_payload_hex": "5902ff",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return {"path": path.name, "sha256": sha(path)}

    commit = meta["commit"]
    phases = {}
    for phase, behavior, firmware_sha, mode in (
        ("baseline_stock", "stock-steering-accepted", "11" * 32, "stock"),
        ("prepatch_invalid_mac28", "invalid-mac-rejected", "11" * 32, "invalid-mac28"),
        ("postpatch_invalid_mac28", "invalid-mac-accepted", "33" * 32, "invalid-mac28"),
    ):
        raw_can = artifact(f"{phase}.can", phase + " raw")
        phases[phase] = {
            "f181_hex": f181_hex,
            "firmware_sha256": firmware_sha,
            "openpilot_ablation_commit": commit if phase != "baseline_stock" else None,
            "observed_behavior": behavior,
            "raw_can": raw_can,
            "forwarding_analysis": analysis_artifact(
                f"{phase}.forward.json", mode, raw_can["sha256"]
            ),
            "dtc": dtc_artifact(f"{phase}.dtc.json"),
            "steering": artifact(f"{phase}.steer.ndjson", phase + " steering"),
        }
    trial = {
        "schema": SCHEMA,
        "f181_hex": f181_hex,
        "openpilot_ablation_commit": commit,
        "secoc_patch_manifest": {"path": manifest.name, "sha256": sha(manifest)},
        "phases": phases,
    }
    trial_path = temp / "trial.json"
    trial_path.write_text(json.dumps(trial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = validate_trial(trial_path)
    check("complete three-phase evidence bundle can establish proof", result["secoc_bypass_proven"] is True, repr(result["errors"]))

    bad_trial = json.loads(trial_path.read_text(encoding="utf-8"))
    bad_trial["phases"]["postpatch_invalid_mac28"]["observed_behavior"] = "write-and-reboot-succeeded"
    bad_trial_path = temp / "bad-trial.json"
    bad_trial_path.write_text(json.dumps(bad_trial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    bad_result = validate_trial(bad_trial_path)
    check("flash/reboot success cannot substitute for behavioral acceptance", bad_result["secoc_bypass_proven"] is False and any("invalid-mac-accepted" in item for item in bad_result["errors"]))

    missing = json.loads(trial_path.read_text(encoding="utf-8"))
    missing["phases"]["prepatch_invalid_mac28"].pop("dtc")
    missing_path = temp / "missing.json"
    missing_path.write_text(json.dumps(missing, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    missing_result = validate_trial(missing_path)
    check("missing DTC evidence prevents proof", missing_result["secoc_bypass_proven"] is False and any("prepatch_invalid_mac28.dtc" in item for item in missing_result["errors"]))

    wrong_stock = json.loads(trial_path.read_text(encoding="utf-8"))
    wrong_stock["phases"]["prepatch_invalid_mac28"]["firmware_sha256"] = "22" * 32
    wrong_stock_path = temp / "wrong-stock.json"
    wrong_stock_path.write_text(json.dumps(wrong_stock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    wrong_stock_result = validate_trial(wrong_stock_path)
    check("baseline and prepatch must use identical stock firmware", wrong_stock_result["secoc_bypass_proven"] is False and any("same stock firmware" in item for item in wrong_stock_result["errors"]))

    unbound = json.loads(trial_path.read_text(encoding="utf-8"))
    analysis_ref = unbound["phases"]["prepatch_invalid_mac28"]["forwarding_analysis"]
    analysis_path = temp / analysis_ref["path"]
    original_analysis = analysis_path.read_text(encoding="utf-8")
    analysis_obj = json.loads(original_analysis)
    analysis_obj["capture"]["sha256"] = "00" * 32
    analysis_path.write_text(json.dumps(analysis_obj) + "\n", encoding="utf-8")
    analysis_ref["sha256"] = sha(analysis_path)
    unbound_path = temp / "unbound.json"
    unbound_path.write_text(json.dumps(unbound, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    unbound_result = validate_trial(unbound_path)
    check("forwarding report must bind exact raw capture", unbound_result["secoc_bypass_proven"] is False and any("exact raw_can capture" in item for item in unbound_result["errors"]))
    analysis_path.write_text(original_analysis, encoding="utf-8")

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
