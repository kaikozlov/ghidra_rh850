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

from exploit.behavioral_proof.analyze_acceptance import analyze_acceptance
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
from exploit.patcher.build_payload import simulate_apply
from exploit.patcher.patch_config import config_from_manifest

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

print("\n== corrected semantic patch binding ==")
semantic_manifest = json.loads((REPO / "data" / "generated" / "secoc_patch_manifest_4512000.json").read_text(encoding="utf-8"))
semantic = semantic_manifest["semantic_resolution"]
check("behavioral proof is bound to resolver schema v2", semantic["schema"] == "toyota-secoc-semantic-target-v2")
check("behavioral proof uses zero-is-verified polarity", semantic["verify_result_polarity"] == "zero-is-verified-ok-nonzero-is-not-verified")
check("behavioral proof reconstructs CMP neutralization", semantic["patch"] == {"address": "0x0008e6c6", "original": "e0d1", "replacement": "e001", "operation": "cmp-second-register-to-first-force-fallthrough"})
check("behavioral proof preserves mismatch BNE", semantic["control_flow"]["bne_bytes"] == "9a0d" and semantic["control_flow"]["mismatch_branch_target"] == "0x0008e6da")
check("behavioral proof names verified fallthrough", semantic["control_flow"]["verified_delivery_fallthrough"] == "0x0008e6ca")

print("\n== complete causal-proof schema ==")
with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    source_manifest = REPO / "data" / "generated" / "secoc_patch_manifest_4512000.json"
    manifest = temp / "manifest.json"
    manifest.write_bytes(source_manifest.read_bytes())
    manifest_obj = json.loads(manifest.read_text(encoding="utf-8"))

    stock = temp / "stock.bin"
    stock.write_bytes((REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes())
    config = config_from_manifest(manifest_obj, mode="apply")
    patched_bytes, expected_fixup, expected_residue = simulate_apply(stock.read_bytes(), config)
    patched = temp / "patched.bin"
    patched.write_bytes(patched_bytes)

    def text_artifact(name: str, content: str) -> dict:
        path = temp / name
        path.write_text(content, encoding="utf-8")
        return {"path": path.name, "sha256": sha(path)}

    def file_artifact(path: Path) -> dict:
        return {"path": path.name, "sha256": sha(path)}

    f181_hex = "018965B451200000000000"

    def dtc_artifact(name: str) -> dict:
        return text_artifact(
            name,
            json.dumps(
                {
                    "schema": "toyota-eps-dtc-snapshot-v1",
                    "f181_hex": f181_hex,
                    "request": "19 02 FF",
                    "response_payload_hex": "5902ff",
                }
            )
            + "\n",
        )

    def phase_artifacts(name: str, mode: str, accepted: bool) -> dict:
        raw_path = temp / f"{name}.can.ndjson"
        steer_path = temp / f"{name}.steer.ndjson"
        rows = []
        steering_rows = []
        for index in range(30):
            timestamp = 1_000_000_000 + index * 10_000_000
            command = (index - 15) * 100
            payloads = {
                0x191: bytes((index, 0x22, 0x33, 0x44, 0x50 | (index & 0xF), 0x66, 0x77, 0x88)),
                0x412: bytes((0x88, index, 0xAA, 0xBB, 0xC0 | (index & 0xF), 0xDD, 0xEE, 0xFF)),
                0x2E4: bytes((1,)) + command.to_bytes(2, "big", signed=True)
                + bytes((index, 0xA0 | (index & 0xF), 0x11, 0x22, 0x33)),
                0x131: bytes((0x10, 0x20, index, 0x40, 0x70 | (index & 0xF), 0x44, 0x55, 0x66)),
            }
            for offset, address in enumerate(sorted(STOCK_CAMERA_PROOF_IDS)):
                source = payloads[address]
                forwarded = (
                    invalidate_mac28(source)
                    if mode == "invalid-mac28" and address in MAC28_IDS
                    else source
                )
                for bus, data, tick in ((1, source, 2 * offset), (2, forwarded, 2 * offset + 1)):
                    rows.append(
                        {
                            "timestamp_ns": timestamp + tick,
                            "address": f"0x{address:X}",
                            "bus": bus,
                            "data": data.hex(),
                        }
                    )
            eps_status = bytearray(8)
            eps_status[3] = 5 if accepted else 0
            rows.append(
                {
                    "timestamp_ns": timestamp + 9,
                    "address": "0x262",
                    "bus": 2,
                    "data": bytes(eps_status).hex(),
                }
            )
            steering_rows.append(
                {
                    "timestamp_ns": timestamp,
                    "steeringTorqueEps": command / 10 if accepted else 0,
                    "steerFaultTemporary": not accepted,
                    "steerFaultPermanent": False,
                }
            )
        raw_path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")
        steer_path.write_text(
            "".join(json.dumps(row) + "\n" for row in steering_rows), encoding="utf-8"
        )

        forward_path = temp / f"{name}.forward.json"
        forward_report = analyze(iter_capture(raw_path), source_bus=1, forward_bus=2, mode=mode)
        forward_report["capture"] = {"path": raw_path.name, "sha256": sha(raw_path)}
        forward_path.write_text(json.dumps(forward_report, sort_keys=True) + "\n", encoding="utf-8")

        acceptance_path = temp / f"{name}.acceptance.json"
        acceptance_report = analyze_acceptance(raw_path, steer_path, source_bus=1, eps_bus=2)
        acceptance_path.write_text(
            json.dumps(acceptance_report, sort_keys=True) + "\n", encoding="utf-8"
        )
        return {
            "raw_can": file_artifact(raw_path),
            "forwarding_analysis": file_artifact(forward_path),
            "acceptance_analysis": file_artifact(acceptance_path),
            "steering": file_artifact(steer_path),
        }

    telemetry = temp / "apply.telemetry.ndjson"
    telemetry.write_text(json.dumps({"event": "payload-complete", "success": True}) + "\n")
    apply_run = temp / "apply.run.json"
    apply_run.write_text(
        json.dumps(
            {
                "schema": "secoc-patch-run-v1",
                "mode": "apply",
                "execute": True,
                "status": "payload-complete",
                "image": {"sha256": sha(stock)},
                "manifest": {"sha256": sha(manifest)},
                "telemetry": {
                    "path": telemetry.name,
                    "sha256": sha(telemetry),
                    "payload_success": True,
                },
                "apply": {
                    "write_crc_sequence_complete": True,
                    "expected_post_image_sha256": sha(patched),
                    "expected_fixup": f"0x{expected_fixup:08X}",
                    "expected_residue": f"0x{expected_residue:08X}",
                },
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    commit = meta["commit"]
    phases = {}
    for phase, behavior, firmware_sha, mode, accepted in (
        ("baseline_stock", "human-note-only", sha(stock), "stock", True),
        ("prepatch_invalid_mac28", "human-note-only", sha(stock), "invalid-mac28", False),
        ("postpatch_invalid_mac28", "human-note-only", sha(patched), "invalid-mac28", True),
    ):
        phases[phase] = {
            "f181_hex": f181_hex,
            "firmware_sha256": firmware_sha,
            "openpilot_ablation_commit": commit if phase != "baseline_stock" else None,
            "observed_behavior": behavior,
            "dtc": dtc_artifact(f"{phase}.dtc.json"),
            **phase_artifacts(phase, mode, accepted),
        }
    trial = {
        "schema": SCHEMA,
        "f181_hex": f181_hex,
        "openpilot_ablation_commit": commit,
        "stock_image": file_artifact(stock),
        "patched_image": file_artifact(patched),
        "apply_run": file_artifact(apply_run),
        "secoc_patch_manifest": {"path": manifest.name, "sha256": sha(manifest)},
        "phases": phases,
    }
    trial_path = temp / "trial.json"
    trial_path.write_text(json.dumps(trial, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    result = validate_trial(trial_path)
    check("complete three-phase evidence bundle can establish proof", result["secoc_bypass_proven"] is True, repr(result["errors"]))

    relabeled = json.loads(trial_path.read_text(encoding="utf-8"))
    relabeled["phases"]["postpatch_invalid_mac28"]["observed_behavior"] = "write-and-reboot-only"
    relabeled_path = temp / "relabeled.json"
    relabeled_path.write_text(json.dumps(relabeled, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    relabeled_result = validate_trial(relabeled_path)
    check("human behavior labels are non-authoritative", relabeled_result["secoc_bypass_proven"] is True)

    fake_acceptance = json.loads(trial_path.read_text(encoding="utf-8"))
    fake_steering = temp / "fake-accepted.steer.ndjson"
    fake_steering.write_text("declared accepted\n", encoding="utf-8")
    fake_acceptance["phases"]["postpatch_invalid_mac28"]["steering"] = file_artifact(fake_steering)
    fake_acceptance_path = temp / "fake-acceptance.json"
    fake_acceptance_path.write_text(
        json.dumps(fake_acceptance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    fake_acceptance_result = validate_trial(fake_acceptance_path)
    check(
        "declared acceptance cannot substitute for parseable causal evidence",
        fake_acceptance_result["secoc_bypass_proven"] is False
        and any("malformed evidence" in item for item in fake_acceptance_result["errors"]),
    )

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
    check("phase firmware must bind the exact stock artifact", wrong_stock_result["secoc_bypass_proven"] is False and any("exact phase artifact" in item for item in wrong_stock_result["errors"]))

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
    check("forwarding report must bind exact raw capture", unbound_result["secoc_bypass_proven"] is False and any("exact raw CAN" in item for item in unbound_result["errors"]))
    analysis_path.write_text(original_analysis, encoding="utf-8")

    wrong_patch = json.loads(trial_path.read_text(encoding="utf-8"))
    tampered_patch = temp / "tampered-patched.bin"
    tampered = bytearray(patched.read_bytes())
    tampered[0] ^= 1
    tampered_patch.write_bytes(tampered)
    wrong_patch["patched_image"] = file_artifact(tampered_patch)
    wrong_patch["phases"]["postpatch_invalid_mac28"]["firmware_sha256"] = sha(tampered_patch)
    wrong_patch_path = temp / "wrong-patch.json"
    wrong_patch_path.write_text(json.dumps(wrong_patch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    wrong_patch_result = validate_trial(wrong_patch_path)
    check(
        "patched artifact must be the exact semantic patch plus CRC fixup",
        wrong_patch_result["secoc_bypass_proven"] is False
        and any("exact manifest patch" in item for item in wrong_patch_result["errors"]),
    )

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
