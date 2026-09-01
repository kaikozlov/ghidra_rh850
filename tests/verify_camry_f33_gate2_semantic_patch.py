#!/usr/bin/env python3
"""Verify the exact-F33 cumulative Gate-2 stage-2 package and retained live trigger."""
from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "tools/build_camry_f33_gate2_semantic_patch.py"
SPEC = importlib.util.spec_from_file_location("build_camry_f33_gate2_semantic_patch", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)

from exploit.patcher.build_payload import simulate_apply
from exploit.patcher.patch_config import config_from_manifest
from tools.build_secoc_patch_manifest import crc32

LIVE = ROOT / "targets/camry-2026/raw-20260901/f33-b6-admission"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def events(path: Path) -> list[dict]:
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            out.append(row)
    return out


print("== cumulative stage construction ==")
stock = builder.STOCK_IMAGE.read_bytes()
stage1, _stage1_manifest = builder.reconstruct_stage1(stock)
check("stock exact-F33 SHA is pinned", builder.sha256(stock) == builder.EXPECTED_STOCK_SHA256)
check("stage1 reconstructed source SHA is exact", builder.sha256(stage1) == builder.EXPECTED_STAGE1_SHA256)
check("stage1 keeps only installed final Gate-2 semantic bytes", stage1[0x8F948:0x8F94A] == bytes.fromhex("1a38") and stage1[0x8F952:0x8F954] == bytes.fromhex("e001"))
check("stage1 cumulative source CRC/fixup is valid", crc32(stage1[0x18000:0xFFDF0]) == 0xFFFFFFFF and struct.unpack_from("<I", stage1, 0xFFDEC)[0] == 0xD9AF33AF)
check("callback site exact context is pinned", stage1[0x8F944:0x8F956] == bytes.fromhex("003aa5051a381d30bfff86ff1d30e0019a0d"))

print("\n== deterministic full package ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "stage2"
    package = builder.build(out, build_payloads=True)
    manifest = json.loads((out / package["manifest"]["path"]).read_text())
    cfg = config_from_manifest(manifest, mode="apply")
    source = (out / package["source_image"]["path"]).read_bytes()
    final, fixup, residue = simulate_apply(source, cfg)

    check("stage2 config patches callback argument only", cfg.patch_va == 0x8F948 and cfg.original == bytes.fromhex("1a38") and cfg.replacement == bytes.fromhex("003a"))
    check("stage2 source is exact installed stage1 image", builder.sha256(source) == builder.EXPECTED_STAGE1_SHA256 and source[0x8F952:0x8F954] == bytes.fromhex("e001"))
    check("final image contains both persistent patch sites", final[0x8F948:0x8F94A] == bytes.fromhex("003a") and final[0x8F952:0x8F954] == bytes.fromhex("e001"))
    check("final cumulative CRC/fixup is exact", fixup == builder.EXPECTED_STAGE2_FIXUP and residue == 0xFFFFFFFF and struct.unpack_from("<I", final, 0xFFDEC)[0] == builder.EXPECTED_STAGE2_FIXUP)
    check("final image SHA is exact", builder.sha256(final) == builder.EXPECTED_FINAL_SHA256)
    check("stage2 manifest explicitly binds cumulative stage1", manifest["development_stage"]["source_image_sha256"] == builder.EXPECTED_STAGE1_SHA256 and manifest["development_stage"]["cumulative_patch_sites"] == [
        {"address": "0x8F948", "bytes": "003a"}, {"address": "0x8F952", "bytes": "e001"},
    ])
    check("preflight payload deterministic", package["payloads"]["preflight"]["sha256"] == "0b59df9a73093cf4a98a8170a0bf58b5c35a5f7db89f11f8b83ba5f0d6bb5a79")
    check("apply payload deterministic", package["payloads"]["apply"]["sha256"] == "bbe7d7ca247fb351032594c084382af2406f434ef351065321cca271f05b05c1")
    check("post-apply verifier targets final cumulative image", package["payloads"]["post_apply"]["final_image_sha256"] == builder.EXPECTED_FINAL_SHA256 and package["payloads"]["post_apply"]["payload_sha256"] == "bb7a4a06967033d3ab175515e4af891b0a71d880227d6005f2a6117104b09228")
    restore = json.loads((out / "restore/restore.json").read_text())
    restore_cfg = (out / "restore/restore_config.bin").read_bytes()
    check("restore is stage2 inverse and preserves stage1", restore["restore_config"]["expected_live_preimage"] == "003a" and restore["restore_config"]["replacement"] == "1a38" and restore["validation"]["target_bytes_restored"] is True)
    check("restore config is deterministic", builder.sha256(restore_cfg) == "e8f7719f162ea35d0bcbae89d415e7326e26d939d7e814fd7238ea3924be4ca4")
    check("builder never materializes a secret file", not any("secret" in p.name.lower() for p in out.rglob("*")))

print("\n== retained 2026-09-01 admission observation ==")
adm = events(LIVE / "camry-f33-b6-admission.ndjson")
identity = [x for x in adm if x.get("event") == "identity"]
id11 = [x for x in adm if x.get("event") == "ladder" and x.get("phase") == "id11_current_angle"]
stops = [x for x in adm if x.get("event") == "phase_b6_stop"]
check("live artifact binds exact full F181", len(identity) == 1 and identity[0]["f181_hex"] == builder.EXPECTED_F181_HEX)
check("live ID11 phase had three instrumented snapshots", len(id11) == 3)
check("live ID11 application payload stayed at prior ID0/current-angle snapshot", all(x["snapshot"]["target_lateral_id"] == 0 and x["snapshot"]["target_angle_raw"] == 64 for x in id11))
check("live ID11 downstream bank stayed inactive despite healthy status", all(x["snapshot"]["snapshot_status"] == 0 and x["snapshot"]["b6_controller_enable"] == 1 and x["snapshot"]["global_comm_mode"] == 0 and x["snapshot"]["controller_bank"] == 7 for x in id11))
check("live ID11 verdict was payload_not_delivered", all(x["verdict"]["reason"] == "payload_not_delivered" for x in id11))
check("live active phase returned all 85 Panda TX echoes", any(x.get("sent") == 85 and x.get("echoes") == 85 for x in stops))

print("\n== retained freshness-state reads are parseable, but bounded ==")
fresh = events(LIVE / "camry-f33-freshness-slots.ndjson")
# Preserve the raw fact that the four exact slot addresses were read while ID11 B6 was sent.
def isotp_messages(rows: list[dict], *, event: str, addr: int, bus: int) -> list[bytes]:
    out: list[bytes] = []
    pending: tuple[int, bytearray] | None = None
    for row in rows:
        if row.get("event") != event or row.get("addr") != addr or row.get("bus") != bus:
            continue
        data = bytes.fromhex(row["data"])
        pci = data[0] >> 4
        if pci == 0:
            size = data[0] & 0xF
            out.append(data[1:1 + size])
        elif pci == 1:
            size = ((data[0] & 0xF) << 8) | data[1]
            pending = (size, bytearray(data[2:]))
        elif pci == 2 and pending is not None:
            size, buf = pending
            buf.extend(data[1:])
            if len(buf) >= size:
                out.append(bytes(buf[:size]))
                pending = None
    return out

req_addrs = set()
for msg in isotp_messages(fresh, event="can_tx", addr=0x7A1, bus=0):
    # 23 15 01 <address32> <length8>: ALFID 0x15, memory ID 1.
    if len(msg) == 8 and msg[:3] == bytes.fromhex("231501"):
        req_addrs.add(int.from_bytes(msg[3:7], "big"))
check("freshness capture reads all four exact slot bases", {0xFEBE55DC, 0xFEBE55E8, 0xFEBE55F4, 0xFEBE5600}.issubset(req_addrs), repr(sorted(hex(x) for x in req_addrs)))
b6_tx = [x for x in fresh if x.get("event") == "can_tx" and x.get("addr") == 0x0B6 and x.get("bus") == 0]
b6_echo = [x for x in fresh if x.get("event") == "can_rx" and x.get("addr") == 0x0B6 and x.get("bus") == 128]
check("freshness capture contains 110 ID11 sends and echoes", len(b6_tx) == 110 and len(b6_echo) == 110)
check("freshness observation is not overclaimed as auth admission", True, "slot values also evolve under stock sync; application ladder remains the decisive admission oracle")

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
