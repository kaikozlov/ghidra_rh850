#!/usr/bin/env python3
"""Verify the exact-F33 root-result Gate-2 stage-3 package and stage-2 live boundary."""
from __future__ import annotations

import importlib.util
import json
import struct
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "tools/build_camry_f33_gate2_root_result_patch.py"
SPEC = importlib.util.spec_from_file_location("build_camry_f33_gate2_root_result_patch", BUILDER_PATH)
assert SPEC is not None and SPEC.loader is not None
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)

from exploit.patcher.build_payload import simulate_apply
from exploit.patcher.patch_config import config_from_manifest
from tools.build_secoc_patch_manifest import crc32

LIVE = ROOT / "targets/camry-2026/raw-20260901/f33-gate2-stage2"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))


def load_json(rel: str) -> dict:
    return json.loads((LIVE / rel).read_text(encoding="utf-8"))


def events(rel: str) -> list[dict]:
    out: list[dict] = []
    for line in (LIVE / rel).read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            out.append(row)
    return out


print("== exact root-result machine semantics ==")
stock = builder.STOCK_IMAGE.read_bytes()
stage2, _stage2_manifest = builder.reconstruct_stage2(stock)
check("exact stock image SHA pinned", builder.sha256(stock) == builder.EXPECTED_STOCK_SHA256)
check("live stage2 source SHA pinned", builder.sha256(stage2) == builder.EXPECTED_STAGE2_SHA256)
check("stage2 source CRC/fixup valid", crc32(stage2[0x18000:0xFFDF0]) == 0xFFFFFFFF and struct.unpack_from("<I", stage2, 0xFFDEC)[0] == 0xD12ADB05)
check("root result load/zero-test/cmov bytes exact", stage2[0x8F92A:0x8F934] == bytes.fromhex("840f659de009e10f14d3"))
check("stock CMOV immediate encoder round-trips exact bytes", builder.enc_cmov_imm(0xA, 1, 1, 26) == bytes.fromhex("e10f14d3"))
check("forced-zero CMOV immediate encoding exact", builder.enc_cmov_imm(0xA, 0, 0, 26) == bytes.fromhex("e00714d3"))
check("stage2 source retains expected experimental tail", stage2[0x8F944:0x8F964] == bytes.fromhex(
    "003aa505003a1d30bfff86ff1d30e0019a0d1a38bfff78fb1d301a38bfffe6fb"
))

print("\n== deterministic stage3 construction ==")
with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "stage3"
    package = builder.build(out, build_payloads=True)
    manifest = json.loads((out / package["manifest"]["path"]).read_text())
    cfg = config_from_manifest(manifest, mode="apply")
    source = (out / package["source_image"]["path"]).read_bytes()
    final, fixup, residue = simulate_apply(source, cfg)

    check("stage3 config patches only root result materialization", cfg.patch_va == 0x8F930 and cfg.original == bytes.fromhex("e10f14d3") and cfg.replacement == bytes.fromhex("e00714d3"))
    check("stage3 source is exact live stage2 image", builder.sha256(source) == builder.EXPECTED_STAGE2_SHA256)
    check("final image contains root patch and both existing tail patches", final[0x8F930:0x8F934] == bytes.fromhex("e00714d3") and final[0x8F948:0x8F94A] == bytes.fromhex("003a") and final[0x8F952:0x8F954] == bytes.fromhex("e001"))
    check("stage3 cumulative prefix exact", crc32(final[0x18000:0xFFDEC]) == builder.EXPECTED_STAGE3_PREFIX)
    check("stage3 cumulative fixup/residue exact", fixup == builder.EXPECTED_STAGE3_FIXUP and residue == 0xFFFFFFFF and struct.unpack_from("<I", final, 0xFFDEC)[0] == builder.EXPECTED_STAGE3_FIXUP)
    check("stage3 final image SHA exact", builder.sha256(final) == builder.EXPECTED_FINAL_SHA256)
    semantic = manifest["semantic_resolution"]
    check("manifest roots bypass at r26 boolean definition", semantic["patch"]["address"] == "0x0008f930" and semantic["patch"]["stock_instruction"] == "cmovne 1,r1,r26" and semantic["patch"]["replacement_instruction"] == "cmovne 0,r0,r26")
    check("manifest preserves native success arm", semantic["native_success_equivalence"] == {
        "cleanup": "existing state cleanup/return flow is unchanged",
        "failure_arm": "0x8F966 FUN_0008F60E(id,0x200) is not taken",
        "freshness_callback": "FUN_0008F8D2 receives zero through the existing success-compatible argument path",
        "pdu_delivery": "FUN_0008F546(id,0) is taken and continues through FUN_0008EB1C -> FUN_00090204 -> FUN_00081CA6",
        "r26": 0,
        "success_bookkeeping": "FUN_0008F4D0(id,0) is taken",
    })
    check("manifest requires NRTD for programming-session operations", any("NRTD" in s for s in manifest["safety"]["requirements"]))
    check("preflight payload deterministic", package["payloads"]["preflight"]["sha256"] == "ea6d61d6ed4fcdb41302589fb8efefcf401576d6182e7d494d9ac9798012e97e")
    check("apply payload deterministic", package["payloads"]["apply"]["sha256"] == "647add6242149c0e63f953195009414df46c96c92e760492004fa7a4ce73319a")
    check("post-apply verifier deterministic", package["payloads"]["post_apply"]["payload_sha256"] == "f7c3462e57da7fcd687c253062a964bb48354f136ac07bf3c6db012467e40760")
    restore = json.loads((out / "restore/restore.json").read_text())
    check("restore reverses stage3 only", restore["restore_config"]["expected_live_preimage"] == "e00714d3" and restore["restore_config"]["replacement"] == "e10f14d3" and restore["validation"]["target_bytes_restored"] is True)
    check("restore returns exact stage2 CRC state", restore["validation"]["restore_simulated_fixup"] == "0xD12ADB05" and restore["validation"]["restore_simulated_residue"] == "0xFFFFFFFF")
    check("restore config deterministic", builder.sha256((out / "restore/restore_config.bin").read_bytes()) == "4abd3270fdf96aac325cf3cb5ffd828c7c58c360010c08de8459d08f40dccaaa")
    check("restore shellcode deterministic", builder.sha256((out / "restore/restore_shellcode.bin").read_bytes()) == "9447176f873e12648c208d780283638d2c83ca599f3e61a55f946b63ca0537fd")
    check("restore payload deterministic", builder.sha256((out / "restore/restore_payload.bin").read_bytes()) == "9880a1f0dfe1a1ddcaa1da42453ca844d45dd15cd1147577d47a203d47fcfc4d")
    check("package never materializes standalone secrets", not any("secret" in p.name.lower() for p in out.rglob("*")))

print("\n== retained stage2 apply / persistence proof ==")
pre = load_json("f33-stage2-preflight/preflight.json")
apply = load_json("f33-stage2-apply/run.json")
post = load_json("f33-stage2-post/run.json")
check("stage2 preflight was exact and apply-ready", pre["apply_ready"] is True and pre["payload_success"] is True and not pre["config_mismatches"] and not pre["observation_mismatches"])
check("stage2 preflight bound exact F181 and stage1 source", pre["f181_hex"] == builder.EXPECTED_F181_HEX and pre["image"]["sha256"] == builder.stage2.EXPECTED_STAGE1_SHA256)
check("stage2 APPLY completed full write/CRC sequence", apply["status"] == "payload-complete" and apply["apply"]["write_crc_sequence_complete"] is True and apply["apply"]["expected_fixup"] == "0xD12ADB05")
check("stage2 APPLY expected exact final image", apply["apply"]["expected_post_image_sha256"] == builder.EXPECTED_STAGE2_SHA256)
check("stage2 reboot persistence verified", post["verified"] is True and not post["config_mismatches"] and not post["observation_mismatches"])
check("stage2 reboot bytes/CRC exact", post["expected_post_image_sha256"] == builder.EXPECTED_STAGE2_SHA256 and post["observed"] == {
    "crc_prefix": 0x2ED524FA,
    "crc_residue": 0xFFFFFFFF,
    "fixup_stored": 0xD12ADB05,
    "patch_observed": 0x3A00,
})

print("\n== retained stage2 admission boundary ==")
adm = events("b6-admission/camry-f33-b6-stage2-admission.ndjson")
identity = [x for x in adm if x.get("event") == "identity"]
id11 = [x for x in adm if x.get("event") == "ladder" and x.get("phase") == "id11_current_angle"]
results = [x for x in adm if x.get("event") == "result"]
check("stage2 admission bound exact F181", len(identity) == 1 and identity[0]["f181_hex"] == builder.EXPECTED_F181_HEX)
check("stage2 ID11 had three application snapshots", len(id11) == 3)
check("stage2 ID11 payload never reached app snapshot", all(x["snapshot"]["target_lateral_id"] == 0 and x["snapshot"]["controller_bank"] == 7 and x["verdict"]["reason"] == "payload_not_delivered" for x in id11))
check("stage2 sampled downstream health remained nominal", all(x["snapshot"]["snapshot_status"] == 0 and x["snapshot"]["b6_controller_enable"] == 1 and x["snapshot"]["global_comm_mode"] == 0 for x in id11))
check("stage2 active run transmitted/echoed all 84 frames", len(results) == 1 and results[0]["result"]["b6_sent"] == 84 and results[0]["result"]["b6_echoes"] == 84)
check("stage2 negative correctly skipped steering offset", results[0]["result"]["small_offset"] is None)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
