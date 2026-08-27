#!/usr/bin/env python3
"""Build the exact-8965F3307000 static command-5 runtime-carrier contract.

This artifact preserves the original low-RAM static carrier analysis and the
audited compiler-reproduced canary/proxy binaries, then joins the later live
result that disproves FEBF0000 as a retained post-startup carrier and verifies
the separate high tail FEBFF9F0..FEBFFBFB as retained/executable.  The audited
low-linked binaries remain historical static construction evidence; they are not
a production post-startup loader.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from camry_f33_corpus import IMAGE, IMAGE_SHA256

REPO = Path(__file__).resolve().parents[1]
CODEFLASH_ART = REPO / "data/generated/camry_8965F3307000_codeflash.json"
RUNTIME_BUILDER = REPO / "exploit/ephemeral_runtime/build_camry_f33_command5_carrier.py"
PROXY_SOURCE = REPO / "exploit/ephemeral_runtime/corolla_hf_command5_proxy.c"
CANARY_SOURCE = REPO / "exploit/ephemeral_runtime/corolla_hf_canary.c"
PROXY_AUDIT = REPO / "exploit/ephemeral_runtime/audited_camry_f33_command5_proxy_build.json"
CANARY_AUDIT = REPO / "exploit/ephemeral_runtime/audited_camry_f33_runtime_canary_build.json"
PROXY_BIN = REPO / "exploit/ephemeral_runtime/audited/camry_f33_command5_proxy.bin"
CANARY_BIN = REPO / "exploit/ephemeral_runtime/audited/camry_f33_runtime_canary.bin"
RAMREQ = REPO / "data/variant_ram_exec_requirements.json"
HIGH_TAIL = REPO / "targets/camry-2026/raw-20260826/high-tail-20260826.json"
LOW_RETENTION = REPO / "targets/camry-2026/raw-20260826/stock-retention-20260826.json"
OUT = REPO / "data/generated/camry_8965F3307000_command5_runtime_carrier.json"

EXPECTED_APP_F181_HEX = "023839363546333330373030300000000038413331313333303331303000000000"
EXPECTED_BOOT_F181_HEX = "022121212121212121212121212121212121212121212121212121212121212121"
PAYLOAD_BUILD_ROOT = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
BOOT_SA_ROOT = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")
APP_SA_ROOT = bytes.fromhex("893e08418c741ffa2a9c044bffa55813")

CANARY_SIZE = 334
CANARY_SHA256 = "facd4f590581f7422dab0fc4fcea21f6d73e4c361b1f4d54960d7001e89bdbb0"
PROXY_SIZE = 464
PROXY_SHA256 = "0ea9b9d460c3678ad4341817ae606d720bb2a13f4d14ec7dc1e0c8f569db94d3"
CANONICAL_REFERENCE_SHA256 = "273202dc591810b2f587ab8fac044599b57b4e07a24ff61d36b7131b97c00660"

# Exact raw-byte ranges recovered/decompiled from the F33 image.  These hashes
# intentionally bind the semantic map to firmware bytes without making build/tmp
# Ghidra workspace state part of the portable verification contract.
RANGES = {
    "boot_init_0": (0x00000C9A, 64, "cb996af672e23393a6a1311d2c98c33922d44726e5b0b1197cf9fca5546aa293"),
    "boot_init_1": (0x00000E54, 64, "74a17a539f17fa7b26162ad15a908100725c2f3b0d5a03d3f55011f3ea793dd6"),
    "boot_init_2": (0x00000F80, 64, "9a55cbac5d39c176f86ed3bb14c086cf118dafd42a4718647bde9618364e4017"),
    "boot_init_3": (0x000010C6, 64, "e14419b0de73fa89e0c2f3ff5bd84751743a88d18f8ac928aaa7b8f3967b1451"),
    "boot_validity_check": (0x0000119E, 128, "4c6428f5b1a5fa68e9e34cf2a86f93a2de1af91a9aac8778394f744c3a002cf1"),
    "application_context_init_window": (0x000715B4, 128, "5a90237343869ccc5095e706aeda223a6987e84ec93d85bf1651c2b1768d1554"),
    "startup_jarl_region": (0x000637F6, 84, "955f380b52dfd46171c5db106aa3f7b6f3e7c9a7c7896e30c5da1a318f8a1826"),
    "startup_final_init": (0x000701EA, 30, "1da9533414b05ccbcdb6a10f67dfd5f7a89a21e0bf055568539401ee3d4e7d08"),
    "foreground_loop": (0x00066062, 92, "b08f13a1f1d02c86eb0f461268b1ffd0ee6196907e31201c4b045bf8990f83dc"),
    "command5_record0": (0x00027DA4, 32, "195635fcd081cfc253d3e69b6c7b39688bd5b1e17f6118b26c317637ce62b07e"),
    "command5_adapter": (0x00088DBC, 260, "42456c97c69c6646f851c80ab90f090e7d598a53c1e5f803132732bb6f346a2e"),
    "command5_worker": (0x00088EC0, 186, "ed65ceae78ed91987a3b27847dffaba9118143e0f94734ffc9aedca5fc9c45f9"),
    "command5_dispatcher": (0x00089440, 150, "dca5252efba4bfee3cc2a509050d088b280771ce58b1d4134d3ead290545d4e4"),
    "command5_callback": (0x00089C4C, 14, "ad851b94e1d4e5d1addd4211a68fdc70401832071161bd779b00f957001085f6"),
    "command5_lower": (0x0008A720, 274, "501ee449dd5e92408f288114572445e7d0619a2408309845c402091e61914d67"),
    "application_mpu_table": (0x00031688, 256, "41f9ab0cf792bb169d4a5e59f0317a27b47d223f2478959790c085e5c6587142"),
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha(path.read_bytes())


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def u32(image: bytes, address: int) -> int:
    return struct.unpack_from("<I", image, address)[0]


def validate_audit(audit: dict, binary: Path, source: Path, *, kind: str, size: int, digest: str) -> None:
    need(audit["schema"] == "camry-f33-command5-carrier-build-v1", f"{kind} audit schema drift")
    need(audit["kind"] == kind, f"{kind} audit kind drift")
    need(audit["review_status"] == "static-carrier-candidate-not-live-validated", f"{kind} review status drift")
    need(audit["target"] == {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256}, f"{kind} target binding drift")
    shell = audit["shellcode"]
    need(shell["size"] == size and shell["sha256"] == digest and shell["headroom"] == 776 - size, f"{kind} shell identity drift")
    need(binary.stat().st_size == size and sha_file(binary) == digest, f"{kind} audited binary drift")
    need(audit["source"] == {"path": str(source.relative_to(REPO)), "sha256": sha_file(source)}, f"{kind} source binding drift")
    need(audit["builder"] == {"path": str(RUNTIME_BUILDER.relative_to(REPO)), "sha256": sha_file(RUNTIME_BUILDER)}, f"{kind} builder binding drift")
    cc = audit["compile_contract"]
    need(cc["architecture"] == "v850e3v5" and cc["entry_offset"] == 0 and cc["relocations"] == 0, f"{kind} entry/relocation drift")
    need(cc["candidate_base"] == "0xFEBF0000" and cc["candidate_end_exclusive"] == "0xFEBF0308" and cc["candidate_limit"] == 776, f"{kind} carrier geometry drift")
    tc = audit["toolchain"]
    need(tc.get("reproduced_byte_exact") is True and tc.get("reference_sha256") == CANONICAL_REFERENCE_SHA256, f"{kind} compiler-equivalence drift")


def range_sources(image: bytes) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for name, (address, size, expected_sha) in RANGES.items():
        body = image[address:address + size]
        need(len(body) == size, f"{name} raw range truncated")
        digest = sha(body)
        need(digest == expected_sha, f"{name} raw-byte identity drift")
        out[name] = {"address": f"0x{address:08X}", "size": size, "sha256": digest}
    return out


def build() -> dict:
    image = IMAGE.read_bytes()
    need(sha(image) == IMAGE_SHA256 and len(image) == 0x100000, "exact F33 CodeFlash identity drift")
    codeflash = load(CODEFLASH_ART)
    proxy = load(PROXY_AUDIT)
    canary = load(CANARY_AUDIT)
    ramreq = load(RAMREQ)
    high_tail = load(HIGH_TAIL)
    low_retention = load(LOW_RETENTION)

    route = codeflash["acquisition"]["route"]
    need(route["application_f181_hex"] == EXPECTED_APP_F181_HEX, "application F181 evidence drift")
    need(route["boot_f181_hex"] == EXPECTED_BOOT_F181_HEX, "boot F181 evidence drift")
    need(route["tx"] == "0x7a1" and route["rx"] == "0x7a9", "Camry route evidence drift")
    need(route["bus"] == 1 and route["elm327_param"] == 1, "Camry bus/ELM evidence drift")
    need(codeflash["acquisition"]["uds_variant"] == "old", "Camry UDS-stack evidence drift")

    need(image[0xBFD8:0xBFE8] == PAYLOAD_BUILD_ROOT, "payload-build root drift")
    need(image[0xBFE8:0xBFF8] == BOOT_SA_ROOT, "boot SecurityAccess root drift")
    need(image[0x20840:0x20850] == APP_SA_ROOT, "application SecurityAccess root drift")
    need(image[0x20860:0x2086C] == b"8965F3307000", "embedded primary F181 drift")

    ranges = range_sources(image)

    # MPU table layout: 16 lower/upper pairs, then 16 ctx0 MPAT words, then 16 ctx1 words.
    mpu = 0x31688
    bounds = [(u32(image, mpu + i * 8), u32(image, mpu + i * 8 + 4)) for i in range(16)]
    ctx0 = [u32(image, mpu + 0x80 + i * 4) for i in range(16)]
    ctx1 = [u32(image, mpu + 0xC0 + i * 4) for i in range(16)]
    need(bounds[1] == (0xFEBF7C00, 0xFEBFFBFC) and ctx0[1] == 0xB8 and ctx1[1] == 0xA8, "mailbox MPU region1 drift")
    need(bounds[5] == (0xFEBEF400, 0xFEBF33FC) and ctx0[5] == ctx1[5] == 0xB8, "carrier MPU region5 drift")

    # Target-native command-5 record 0: header/callback then adapter/worker pointers.
    record_words = [u32(image, 0x27DA4 + i * 4) for i in range(8)]
    need(record_words == [0xFFFF0000, 0x00089C4C, 0, 0, 0, 0x00088DBC, 0x00088EC0, 0x00027DA0], "command-5 record0 layout drift")

    validate_audit(proxy, PROXY_BIN, PROXY_SOURCE, kind="command5-proxy", size=PROXY_SIZE, digest=PROXY_SHA256)
    validate_audit(canary, CANARY_BIN, CANARY_SOURCE, kind="runtime-canary", size=CANARY_SIZE, digest=CANARY_SHA256)

    runtime = proxy["runtime_contract"]
    need(runtime["application_context_init"] == "0x000715B4", "F33 application context init drift")
    need(runtime["startup_jarl_first"] == "0x000637F6" and runtime["startup_jarl_after"] == "0x0006384A" and runtime["startup_jarl_count"] == 21, "F33 startup replay drift")
    need(runtime["startup_final_init"] == "0x000701EA" and runtime["foreground_loop"] == "0x00066062", "F33 foreground ownership drift")
    need(runtime["foreground_tick_counter"] == "0xFEBE39DB", "F33 foreground tick counter drift")
    need(runtime["command5_dispatcher"] == "0x00089440" and runtime["command5_driver_record"] == 0 and runtime["command5_key_selector"] == 4, "F33 command5 dispatcher route drift")
    need(runtime["command5_done_flag"] == "0xFEBF13BC" and runtime["command5_status_flag"] == "0xFEBF13BD", "F33 command5 completion cells drift")
    need(runtime["fixed_command5_input_length"] == 36 and runtime["mailbox_address"] == "0xFEBFFB80" and runtime["mailbox_size"] == 60, "F33 fixed-36/mailbox contract drift")

    need(high_tail["schema"] == "camry-f33-high-tail-exec-retention-v1", "F33 high-tail evidence schema drift")
    need(high_tail["result"]["tail_524_byte_exact"] is True and high_tail["result"]["tail_marker_executed"] is True, "F33 high-tail live result drift")
    need(high_tail["result"]["retained_sha256"] == "89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c", "F33 high-tail retained bytes drift")
    need(low_retention["result"]["prefix_648_byte_exact"] is False and low_retention["result"]["shell_retained"] is False, "F33 low-carrier live rejection drift")
    f33_rows = [row for row in ramreq.get("variants", []) if row.get("id") == "camry-2026-8965f3307000-high-tail"]
    need(len(f33_rows) == 1, "F33 verified high-tail geometry row missing")
    f33 = f33_rows[0]
    need(f33["retained_application_rwx_base"] == "0xFEBFF9F0" and f33["retained_application_rwx_end_exclusive"] == "0xFEBFFBFC", "F33 verified high-tail geometry drift")

    return {
        "schema": "camry-8965f3307000-command5-runtime-carrier-v1",
        "applies_to": ["8965F3307000"],
        "identity": {
            "application_f181_hex": EXPECTED_APP_F181_HEX,
            "application_records": ["8965F3307000", "8A3113303100"],
            "boot_f181_hex": EXPECTED_BOOT_F181_HEX,
            "route": {"tx": "0x7A1", "rx": "0x7A9", "bus": 1, "elm327_param": 1, "uds_variant": "old", "cpu_index": 0},
        },
        "sources": {
            "codeflash": {"path": str(IMAGE.relative_to(REPO)), "sha256": IMAGE_SHA256},
            "codeflash_analysis": {"path": str(CODEFLASH_ART.relative_to(REPO)), "sha256": sha_file(CODEFLASH_ART)},
            "runtime_builder": {"path": str(RUNTIME_BUILDER.relative_to(REPO)), "sha256": sha_file(RUNTIME_BUILDER)},
            "canary_audit": {"path": str(CANARY_AUDIT.relative_to(REPO)), "sha256": sha_file(CANARY_AUDIT)},
            "proxy_audit": {"path": str(PROXY_AUDIT.relative_to(REPO)), "sha256": sha_file(PROXY_AUDIT)},
            "ram_exec_requirements": {"path": str(RAMREQ.relative_to(REPO)), "sha256": sha_file(RAMREQ)},
            "high_tail_live_evidence": {"path": str(HIGH_TAIL.relative_to(REPO)), "sha256": sha_file(HIGH_TAIL)},
            "low_retention_live_evidence": {"path": str(LOW_RETENTION.relative_to(REPO)), "sha256": sha_file(LOW_RETENTION)},
            "raw_function_ranges": ranges,
        },
        "bootstrap_contract": {
            "download_base": "0xFEBF0000",
            "download_size": 0x1000,
            "callback_base": "0xFEBF0000",
            "verify_routine": "0x10F0",
            "callback_routine": "0xFF00",
            "did_0203": "0000000000",
            "did_0201": "00" * 16,
            "did_0202": "00" * 16,
            "payload_build_root_source": "exact CodeFlash @ 0x0000BFD8",
            "boot_security_access_root_source": "exact CodeFlash @ 0x0000BFE8",
            "secret_values_recorded_in_artifact": False,
        },
        "static_low_carrier_geometry": {
            "base": "0xFEBF0000",
            "end_inclusive": "0xFEBF0307",
            "end_exclusive": "0xFEBF0308",
            "size": 776,
            "first_recovered_normalized_direct_or_simple_gp_reference": "0xFEBF0308",
            "mpu_region_index": 5,
            "mpu_bounds": ["0xFEBEF400", "0xFEBF33FC"],
            "ctx0_mpat": "0x000000B8",
            "ctx1_mpat": "0x000000B8",
            "permissions": "supervisor read/write/execute in both recovered application contexts",
            "static_boundary": "The first normalized direct/simple-GP reference is FEBF0308, but the real stock application startup live test overwrites this pocket; it is not a retained production carrier.",
        },
        "verified_high_tail_carrier": {
            "base": "0xFEBFF9F0",
            "end_inclusive": "0xFEBFFBFB",
            "end_exclusive": "0xFEBFFBFC",
            "size": 524,
            "retained_sha256": "89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c",
            "live_exact_after_stock_startup": True,
            "live_execution_proven": True,
            "stock_application_reappeared": True,
            "safety_tx_blocked_delta": 0,
            "mpu_region_index": 1,
            "mpu_bounds": ["0xFEBF7C00", "0xFEBFFBFC"],
            "ctx0_mpat": "0x000000B8",
            "ctx1_mpat": "0x000000A8",
            "production_boundary": "Carrier lifetime/execution is closed; application-mode byte placement and control transfer are assessed separately by camry_8965F3307000_application_ram_loader_assessment.json.",
        },
        "mailbox_geometry": {
            "base": "0xFEBFFB80",
            "end_inclusive": "0xFEBFFBBB",
            "end_exclusive": "0xFEBFFBBC",
            "size": 60,
            "normalized_direct_or_simple_gp_reference_count": 0,
            "mpu_region_index": 1,
            "mpu_bounds": ["0xFEBF7C00", "0xFEBFFBFC"],
            "ctx0_mpat": "0x000000B8",
            "ctx1_mpat": "0x000000A8",
            "intended_write_context": "ctx0; target-native foreground sequence returns through 0x71398 before canary/signer insertion",
            "host_read_transport": "application SID 0x23 ALFID 0x15 memory-id 1; Camry XCP 0x7F7/0x7F8 is not assumed",
            "historical_only": True,
            "production_note": "This mailbox was paired with low-linked startup-replay candidates. A post-startup high-tail service must allocate its own non-overlapping mailbox layout.",
        },
        "scheduler_transfer": {
            "boot_transition_calls": ["0x00000C9A", "0x00000E54", "0x00000F80", "0x000010C6"],
            "boot_validity_check": "0x0000119E",
            "application_context_init": "0x000715B4",
            "startup_jarl_first": "0x000637F6",
            "startup_jarl_after": "0x0006384A",
            "startup_jarl_count": 21,
            "startup_final_init": "0x000701EA",
            "foreground_loop": "0x00066062",
            "tick_poll": {"address": "0xFFFFB111", "bit": 4, "clear_mask": "0xEF"},
            "timing_flag": "0x00031910",
            "foreground_calls": ["0x00065442", "0x00071378", "0x00066FF2", "0x00071398", "0x000667E6", "0x00071378", "0x00066CF6", "0x00071398"],
            "foreground_tick_counter": "0xFEBE39DB",
        },
        "command5_contract": {
            "driver_record_table": "0x00027DA4",
            "driver_record": 0,
            "adapter": "0x00088DBC",
            "worker": "0x00088EC0",
            "dispatcher": "0x00089440",
            "completion_callback": "0x00089C4C",
            "lower_engine": "0x0008A720",
            "key_selector": 4,
            "done_flag": "0xFEBF13BC",
            "status_flag": "0xFEBF13BD",
            "fixed_input_length": 36,
            "output_length": 16,
            "serialized_with_command7": True,
            "busy_behavior": "dispatcher result 2 is defer/retry; proxy never uses the command-7 abort path",
        },
        "runtime_candidates": {
            "inert_canary": {
                "binary": str(CANARY_BIN.relative_to(REPO)),
                "size": CANARY_SIZE,
                "headroom": 776 - CANARY_SIZE,
                "sha256": CANARY_SHA256,
                "entry_offset": 0,
                "relocations": 0,
                "heartbeat_address": "0xFEBFFB80",
                "command5_calls": False,
                "production_poststartup_usable": False,
            },
            "fixed_36_command5_proxy": {
                "binary": str(PROXY_BIN.relative_to(REPO)),
                "size": PROXY_SIZE,
                "headroom": 776 - PROXY_SIZE,
                "sha256": PROXY_SHA256,
                "entry_offset": 0,
                "relocations": 0,
                "input_length": 36,
                "key_selector": 4,
                "production_poststartup_usable": False,
            },
        },
        "historical_low_carrier_live_sequence": [
            {"stage": 1, "name": "low-pocket application-retention canary", "result": "superseded/disproved: real stock startup overwrites FEBF0000"},
            {"stage": 2, "name": "high-tail retention marker", "result": "closed: FEBFF9F0..FEBFFBFB retained byte-for-byte and executed before stock application return"},
        ],
        "boundary": {
            "static_low_carrier_candidate_closed": True,
            "low_carrier_live_retention_closed": False,
            "low_carrier_disproved": True,
            "verified_high_tail_live_retention_closed": True,
            "live_slot4_command5_permission_closed": False,
            "command5_latency_jitter_closed": False,
            "production_b6_signer_closed": False,
            "vehicle_actuation_authorized": False,
            "flash_write_used": False,
            "steering_can_transmit_used": False,
            "verified_variant_ram_exec_requirement_promoted": True,
            "application_mode_execution_pivot_closed": False,
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
