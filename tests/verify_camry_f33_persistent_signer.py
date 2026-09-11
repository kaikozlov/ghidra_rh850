#!/usr/bin/env python3
"""Verify the exact-F33 normal-boot persistent C7/B6 signer package."""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.common.payload_package import inspect_payload
from exploit.common.ram_exec import TOYOTA_P1ME_PAYLOAD_BUILD_SECRET
from exploit.ephemeral_runtime import build_camry_f33_b6_persistent_signer as signer
from exploit.ephemeral_runtime import camry_f33_persistent_signer as host
from tools.security.build_secoc_patch_manifest import crc32
from tools.targets.camry.builders import build_camry_f33_persistent_signer_patch as patch

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


stock = signer.IMAGE.read_bytes()
check("exact stock firmware identity", signer.sha256(stock) == signer.IMAGE_SHA256)
check("both persistent spans are erased", all(
    stock[address:limit] == b"\xFF" * (limit - address)
    for _, _, address, limit in signer.PERSISTENT_SEGMENTS
))
check("OEM tail marker words are exact", stock[0xFFE00:0xFFE04].hex() == "5aa5a55a" and stock[0xFFF00:0xFFF04].hex() == "01000000")

with tempfile.TemporaryDirectory(prefix="verify-f33-persistent-") as td:
    out = Path(td)
    package = patch.build(out)
    stage5 = (out / package["stage5_source"]["path"]).read_bytes()
    stage6 = (out / package["stage6_resident"]["path"]).read_bytes()
    stage7 = (out / package["stage7_hook"]["path"]).read_bytes()
    metadata = package["signer"]
    blobs = [
        (out / f"camry_f33_b6_persistent_signer_{name}.bin").read_bytes()
        for name, _, _, _ in signer.PERSISTENT_SEGMENTS
    ]
    erased = [b"\xFF" * len(blob) for blob in blobs]

    check("split signer fits both exact tail spans", [len(blob) for blob in blobs] == [240, 250] and metadata["persistent"]["size"] == 490)
    check("split signer has no relocation and enters first span", metadata["persistent"]["relocations"] == 0 and metadata["persistent"]["entry"] == "0x000FFE04")
    check("resident stage changes only declared segment bytes", {
        i for i, (a, b) in enumerate(zip(stage5, stage6, strict=True)) if a != b
    } == {
        address + offset
        for blob, (_, _, address, _) in zip(blobs, signer.PERSISTENT_SEGMENTS, strict=True)
        for offset in range(len(blob)) if blob[offset] != 0xFF
    })
    check("resident bytes are exact", all(
        stage6[address:address + len(blob)] == blob
        for blob, (_, _, address, _) in zip(blobs, signer.PERSISTENT_SEGMENTS, strict=True)
    ))
    check("resident stage preserves both OEM markers", stage6[0xFFE00:0xFFE04] == stage5[0xFFE00:0xFFE04] and stage6[0xFFF00:0xFFF04] == stage5[0xFFF00:0xFFF04])
    check("resident lies outside and preserves application CRC", stage6[0xFFDEC:0xFFDF0] == stage5[0xFFDEC:0xFFDF0] and crc32(stage6[0x18000:0xFFDF0]) == 0xFFFFFFFF)

    restored = patch.apply_uncovered_segments(
        stage6, expected=blobs, replacement=erased, crc_start=0x18000, crc_end=0xFFDF0,
    )
    check("resident removal restores exact stage 5", restored == stage5)

    hook_diff = {i for i, (a, b) in enumerate(zip(stage6, stage7, strict=True)) if a != b}
    check("hook stage changes only hook and CRC fixup", hook_diff <= set(range(0x7A272, 0x7A276)) | set(range(0xFFDEC, 0xFFDF0)) and set(range(0x7A272, 0x7A276)) <= hook_diff)
    check("hook stage has valid CRC", crc32(stage7[0x18000:0xFFDF0]) == 0xFFFFFFFF)
    check("hook replays stock call through wrapper", metadata["behavior"]["displaced_stock_call_preserved"] is True and metadata["hook"]["displaced_target"] == "0x0007BF60")
    check("runtime failure is native pass-through", metadata["behavior"]["no_control_or_stale_sequence"] == "native B6 untouched" and metadata["behavior"]["command5_failure"] == "native B6 untouched")

    payloads = package["stage6_resident"]["payloads"]
    payload_ok = True
    for record in payloads.values():
        raw = (out / record["payload"]["path"]).read_bytes()
        inspection = inspect_payload(raw, secret=TOYOTA_P1ME_PAYLOAD_BUILD_SECRET)
        payload_ok &= len(raw) == 0x1000 and inspection.cmac_valid and inspection.crc_residue == 0xFFFFFFFF
        payload_ok &= record["shellcode"]["size"] <= 0xFF0 and record["shellcode"]["relocations"] == 0
    check("all resident install/remove payloads authenticate and fit", payload_ok)

    plan = json.loads((out / "package.json").read_text())
    check("package order forbids removing a live hook target", plan["ordering"]["never_remove_blob_while_hook_active"] is True and plan["ordering"]["remove"][0] == "stage7 restore")
    check("request/result and longitudinal frames remain stock", all(plan["boundaries"][key] is False for key in (
        "stock_08a_modified", "stock_081_modified", "longitudinal_0ca_modified",
    )))

    loaded = host.load_package(out)
    host_plan = host.plan(out, loaded)
    check("host validates every image, payload, segment, and restore artifact",
          host_plan["stage6_resident"]["sha256"] == package["stage6_resident"]["sha256"])
    payload_path = out / package["stage6_resident"]["payloads"]["stage6-preflight"]["payload"]["path"]
    payload_raw = payload_path.read_bytes()
    payload_path.write_bytes(bytes([payload_raw[0] ^ 1]) + payload_raw[1:])
    try:
        host.load_package(out)
    except host.PersistentSignerError:
        tamper_rejected = True
    else:
        tamper_rejected = False
    finally:
        payload_path.write_bytes(payload_raw)
    check("host rejects a tampered resident payload before vehicle access", tamper_rejected)

source = signer.SOURCE.read_text()
launcher = (ROOT / "exploit/ephemeral_runtime/camry_f33_persistent_signer_launcher.sh").read_text()
check("resident has no CAN transmitter", "can_send" not in source and "transmit" not in source.lower())
check("launcher makes passive native verification an explicit prerequisite", "verify-native-08a" in launcher)
check("launcher enforces reverse removal order in operator help",
      launcher.index("  ./f33-persist hook-remove") <
      launcher.index("  ./f33-persist resident-remove-preflight") <
      launcher.index("  ./f33-persist resident-remove\n"))

print(f"Results: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
