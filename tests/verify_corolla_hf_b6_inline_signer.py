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
    check("static-only review boundary", h["review_status"] == "static-candidate-not-live-validated")
    check("exact target identities differ", h["target"]["codeflash_sha256"] != f["target"]["codeflash_sha256"])
    check("application-identical H/F resident", h["resident"]["sha256"] == f["resident"]["sha256"])
    check("application-identical H/F helper", h["helper"]["sha256"] == f["helper"]["sha256"])
    check("application-identical H/F payload", h["authenticated_payload"]["sha256"] == f["authenticated_payload"]["sha256"])
    check("resident fits exact post-shadow tail", h["resident"]["size"] == 522 and h["resident"]["headroom"] == 2)
    check("helper fits exact low candidate", h["helper"]["size"] == 456 and h["helper"]["headroom"] == 8)
    mailbox = h["mailbox"]
    check("mailbox ends before recurring foreground", int(mailbox["base"], 16) + mailbox["size"] <= int(mailbox["foreground_entry"], 16))
    check("hook is after drain and before SecOC", h["hook"] == {"receive_drain": "0x0007744A", "helper": "0xFEBF0000", "secoc_periodic": "0x000636C0"})
    check("exact Corolla B6 queue geometry", h["b6"]["queue_record"] == "0xFEBE5366" and h["b6"]["secured_buffer"] == "0xFEBE53C0")
    check("exact synchronous command5 wrapper", h["command5"]["synchronous_wrapper"] == "0x00082ED2")
    check("native pass-through failure", h["behavior"]["failure"] == "native B6 untouched")
    check("no direct CAN or verification bypass", not h["behavior"]["can_transmit"] and not h["behavior"]["secoc_result_override"])

print("Corolla H/F inline signer build verification passed.")
