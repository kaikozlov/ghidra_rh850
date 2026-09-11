#!/usr/bin/env python3
"""Build and verify the exact H/F split-resident B6 signer candidate."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BUILDER = REPO / "exploit/ephemeral_runtime/build_corolla_hf_b6_inline_signer.py"
sys.path.insert(0, str(REPO))
from exploit.ephemeral_runtime import corolla_hf_b6_inline_signer as installer


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[PASS] {label}")


def build(target: str, root: Path) -> dict[str, object]:
    out = root / target
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--target", target, "--output-dir", str(out)],
        cwd=REPO, check=True, capture_output=True, text=True,
    )
    meta = json.loads(result.stdout)
    meta["_out"] = out
    return meta


with tempfile.TemporaryDirectory(prefix="verify-corolla-hf-inline-signer-") as td:
    root = Path(td)
    h = build("8965H1202000", root)
    f = build("8965F1208000", root)

    check("H/F schemas", h["schema"] == f["schema"] == "corolla-hf-b6-inline-signer-build-v1")
    check("startup survival review boundary", h["review_status"] == "firmware-verified-startup-survival-live-command5-unvalidated")
    check("exact target identities differ", h["target"]["codeflash_sha256"] != f["target"]["codeflash_sha256"])
    check("application-identical H/F resident", h["resident"]["sha256"] == f["resident"]["sha256"])
    check("application-identical H/F helper", h["helper"]["sha256"] == f["helper"]["sha256"])
    check("application-identical H/F payload", h["authenticated_payload"]["sha256"] == f["authenticated_payload"]["sha256"])
    check("H/F startup-survival contract identical", h["startup_survival"] == f["startup_survival"])
    check("resident fits exact post-shadow tail", h["resident"]["size"] == 522 and h["resident"]["headroom"] == 2)
    check("helper fits exact low candidate", h["helper"]["size"] == 464 and h["helper"]["headroom"] == 0)
    survival = h["startup_survival"]
    check("startup survival is firmware-verified", survival["classification"] == "firmware-verified-startup-survival")
    check("low helper ends before first startup writer", survival["low_helper"] == {
        "range": ["0xFEBF0000", "0xFEBF01CF"],
        "first_recovered_startup_write": "0xFEBF0200",
        "startup_clear_gap": 48,
        "localram_initializer": "0x0006149A",
        "normalized_reference_count": 0,
    })
    check("high resident begins after exact shadow copy", survival["high_resident"] == {
        "range": ["0xFEBFF9F0", "0xFEBFFBFB"],
        "shadow_copy_function": "0x0005C992",
        "shadow_source": ["0x00010000", "0x00017DEF"],
        "shadow_destination": ["0xFEBF7C00", "0xFEBFF9EF"],
        "normalized_reference_count": 0,
    })
    check("runtime ownership boundary stays explicit", all(x in survival["boundary"] for x in ("computed pointers", "external XCP", "hardware writers")))
    mailbox = h["mailbox"]
    check("mailbox ends before recurring foreground", int(mailbox["base"], 16) + mailbox["size"] <= int(mailbox["foreground_entry"], 16))
    check("control reuses proven stock-Toyota-B C7 recipe", h["control"] == {
        "can_id": "0x1FDC0002", "extended": True, "bus": 1,
        "staging": "0xFEBE4B20", "magic": "00c7",
        "format": "00 C7 seq 00 target_hi target_lo 00 00",
    })
    check("hook is after drain and before SecOC", h["hook"] == {"receive_drain": "0x0007744A", "helper": "0xFEBF0000", "secoc_periodic": "0x000636C0"})
    check("exact Corolla B6 queue geometry", h["b6"]["queue_record"] == "0xFEBE5366" and h["b6"]["secured_buffer"] == "0xFEBE53C0")
    check("exact synchronous command5 wrapper", h["command5"]["synchronous_wrapper"] == "0x00082ED2")
    check("native pass-through failure", h["behavior"]["failure"] == "native B6 untouched")
    check("no direct CAN or verification bypass", not h["behavior"]["can_transmit"] and not h["behavior"]["secoc_result_override"])

    for meta in (h, f):
        out = meta["_out"]
        target = meta["target"]["software_id"]
        prefix = f"corolla_{target}_b6_inline_signer"
        bundle = installer.load_bundle(out / f"{prefix}_payload.bin", out / f"{prefix}.json")
        plan = installer.build_plan(bundle)
        check(f"{target} installer binds exact F181", plan["target"]["required_application_f181_hex"] == installer.APP_F181[target])
        check(f"{target} installer binds exact CodeFlash", plan["target"]["codeflash_sha256"] == installer.CODEFLASH_SHA256[target])
        check(f"{target} installer remains volatile", not plan["install"]["flash_writes"] and plan["install"]["removal"] == "full EPS power cycle")

    waiting = installer.decode_state(bytes.fromhex("423646530000000000000000000000001122334455667788"))
    verified = installer.decode_state(bytes.fromhex("423646530000000001000000000000001122334455667788"))
    check("installer state decoder distinguishes oracle gate", waiting["oracle_state_name"] == "awaiting-native-b6" and verified["oracle_state_name"] == "native-mac-verified")

print("Corolla H/F inline signer build verification passed.")
