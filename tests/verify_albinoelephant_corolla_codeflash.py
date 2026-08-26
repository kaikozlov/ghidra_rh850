#!/usr/bin/env python3
"""Verify the 2023 Corolla 8965H1202000 CodeFlash corpus and cross-image findings."""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
import tempfile
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_ephemeral_runtime_manifest import load_codeflash  # noqa: E402
from tools.build_secoc_patch_manifest import build_manifest as build_patch_manifest  # noqa: E402
from tools.compare_variant_function_bodies import compare as compare_function_bodies  # noqa: E402
from tools.compare_variant_application_rx import compare as compare_application_rx  # noqa: E402
from tools.build_variant_named_transfer_ledger import build as build_named_transfer_ledger  # noqa: E402
from tools.analyze_rh850_codeflash_structure import analyze as analyze_codeflash_structure  # noqa: E402

RAW_DIR = REPO / "community/albinoelephant/raw-20260818"
SESSION = RAW_DIR / "albinoelephant-corolla-2023.20260814-0023"
RANGE = SESSION / "dump_codeflash_00000000_00200000_20260814-025814.bin"
MANIFEST_TXT = RAW_DIR / "MANIFEST.txt"
SIENNA = (REPO / "firmware/RH850_P1M-E_CodeFlash.bin").read_bytes()
GATE = REPO / "data/generated/secoc_gate_resolution_8965H1202000_minimal.json"
RUNTIME = REPO / "data/generated/ephemeral_runtime_target_manifest_8965H1202000.json"
FUNCTION_TRANSFER = REPO / "data/generated/corolla_8965H1202000_function_body_transfer.json"
STRUCTURAL_TRANSFER = REPO / "data/generated/corolla_8965H1202000_structural_function_transfer.json"
NAMED_TRANSFER_LEDGER = REPO / "data/generated/corolla_8965H1202000_named_function_transfer_ledger.json"
APPLICATION_RX_DIFF = REPO / "data/generated/corolla_8965H1202000_application_rx_diff.json"
REFERENCE_INVENTORY = REPO / "data/ghidra_project_inventory.baseline.jsonl"

SOURCE_SHA = "97f9d42d936b97a99e7ab3d3ef20c6fb4c1fc3cc2ba199f6b158675a1709aee6"
CODEFLASH_SHA = "0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f"

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}{suffix}")


def occurrences(blob: bytes, needle: bytes) -> list[int]:
    out: list[int] = []
    pos = 0
    while True:
        pos = blob.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1


print("== immutable acquisition and normalization ==")
raw = RANGE.read_bytes()
check("tracked range dump is exactly 2 MiB", len(raw) == 0x200000)
check("tracked range dump SHA-256 matches contributor manifest", hashlib.sha256(raw).hexdigest() == SOURCE_SHA)
codeflash, source = load_codeflash(RANGE)
check("upper 1 MiB is acquisition padding", raw[0x100000:] == b"\xFF" * 0x100000)
check("normalization returns exact first 1 MiB", codeflash == raw[:0x100000] and len(codeflash) == 0x100000)
check("normalized CodeFlash SHA-256 is pinned", hashlib.sha256(codeflash).hexdigest() == CODEFLASH_SHA)
check("tracked canonical normalized image is exact", (REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin").read_bytes() == codeflash)
check("normalization preserves source provenance", source["sha256"] == SOURCE_SHA and source["size"] == 0x200000)
manifest_text = MANIFEST_TXT.read_text(encoding="utf-8")
check("contributor manifest identifies no-glitch owner-side acquisition", "No glitching, no bench work, no module removal" in manifest_text)

print("\n== embedded ECU identity ==")
check("MCU boot-info string is exact", codeflash[0x180:0x180 + 40] == b"BOOT INFO AREA  R7F701383       72114350")
check("ECU serial is exact", codeflash[0xA4DC:0xA4DC + 20] == b"8965012N50A05G310920")
check("application F181 primary record source is exact", codeflash[0x20860:0x20860 + 12] == b"8965F1208000")
check("application F181 secondary record source is exact", codeflash[0x17DC0:0x17DC0 + 12] == b"8A3111202000")
check("auxiliary one-record DID2032 identity is exact", codeflash[0x17D80:0x17D80 + 12] == b"8965H1202000")
check("auxiliary H1202000 identity stays distinct from F181 primary", codeflash[0x17D80:0x17D8C] != codeflash[0x20860:0x2086C])

print("\n== cross-calibration crypto roots ==")
for address, label in (
    (0xBFD8, "payload-build secret"),
    (0xBFE8, "boot SecurityAccess secret"),
    (0x20840, "application SecurityAccess secret"),
):
    check(f"{label} is byte-identical to 4512000 at {address:#x}", codeflash[address:address + 16] == SIENNA[address:address + 16])
check("payload-build secret exact value", codeflash[0xBFD8:0xBFE8].hex() == "ba052435f8843f985fd1329d2b6117b0")
check("boot SA secret exact value", codeflash[0xBFE8:0xBFF8].hex() == "f05f36b7d78c03e24ab4faef2a57d044")
check("application SA secret exact value", codeflash[0x20840:0x20850].hex() == "893e08418c741ffa2a9c044bffa55813")
check("boot SA stage-1 routine transfers byte-for-byte", codeflash[0x6FD0:0x6FD0 + 50] == SIENNA[0x6FEC:0x6FEC + 50])
check("complete boot SA request/key/lockout/init state machine transfers at -0x1c",
      codeflash[0x530C:0x5612] == SIENNA[0x5328:0x562E])

print("\n== foreign Gate-2 and CRC-resigning manifest ==")
gate = json.loads(GATE.read_text(encoding="utf-8"))
check("foreign Gate-2 resolver is unique and SHA-bound", gate["resolution"] == "unique" and gate["candidate_count"] == 1 and gate["program_sha256"] == CODEFLASH_SHA)
check("foreign Gate-2 CMP neutralization is exact", gate["patch"] == {
    "address": "0x00088c62",
    "original": "e0d1",
    "replacement": "e001",
    "operation": "cmp-second-register-to-first-force-fallthrough",
})
check("foreign Gate-2 preserves BNE topology", gate["control_flow"]["bne"] == "0x00088c64" and gate["control_flow"]["bne_bytes"] == "9a0d" and gate["control_flow"]["verified_delivery_fallthrough"] == "0x00088c66")
with tempfile.TemporaryDirectory(prefix="corolla-codeflash-") as td:
    normalized = Path(td) / "8965H1202000_CodeFlash.bin"
    normalized.write_bytes(codeflash)
    patch_manifest = build_patch_manifest(gate, normalized, 0)
check("foreign stock region-1 CRC validates", patch_manifest["boot_crc"]["stock_region_valid"] is True and patch_manifest["boot_crc"]["stock_residue"] == "0xFFFFFFFF")
check("foreign region-1 geometry matches discovered P1M-E layout", patch_manifest["boot_crc"]["start"] == "0x18000" and patch_manifest["boot_crc"]["end"] == "0xFFDF0" and patch_manifest["boot_crc"]["fixup_va"] == "0xFFDEC")
check("foreign stock CRC fixup is exact", patch_manifest["boot_crc"]["stored_fixup"] == "0xAD59D70C")
check("foreign Gate patch resigns to exact fixup", patch_manifest["boot_crc"]["patched_fixup_for_supplied_image"] == "0xDD5F1477" and patch_manifest["boot_crc"]["patched_residue_for_supplied_image"] == "0xFFFFFFFF")

print("\n== Lochuan checkpoint-patch homolog ==")
# SECOC-050/CORR-066: use surrounding bytes, not the one-byte immediate alone.
sienna_lochuan_context = SIENNA[0x664E2:0x664EA]
hits = occurrences(codeflash, sienna_lochuan_context)
check("Sienna Lochuan-patch context has one foreign homolog", hits == [0x6081A], repr([hex(x) for x in hits]))
check("foreign homolog has the same 0x31 failure-status byte", codeflash[0x6081E] == 0x31)

print("\n== foreign ephemeral-runtime capability result ==")
runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
check("runtime manifest is bound to normalized and source hashes", runtime["image"]["sha256"] == CODEFLASH_SHA and runtime["image"]["source_sha256"] == SOURCE_SHA)
check("runtime manifest records only exact 12-character software IDs", runtime["image"]["software_ids"] == ["8965F1208000", "8965H1202000"])
records = runtime["secoc_records"]["records"]
check("Gate-2 queue has exactly three configured records", runtime["secoc_records"]["record_count"] == 3 and len(records) == 3)
check("foreign Gate-2 queue IDs are 00F/D7/B6", [r["can_id"] for r in records] == ["0xF", "0xD7", "0xB6"])
check("foreign Gate-2 queue omits steering 2E4/131", runtime["secoc_records"]["steering_bridge_missing_ids"] == ["0x2E4", "0x131"] and runtime["secoc_records"]["steering_bridge_profiles"] == [])
check("missing steering profiles are a successful fail-closed capability result", runtime["status"] == "semantic-resolved-steering-unsupported" and runtime["runtime_build_ready"] is False)

print("\n== target-native GP/TP context and generated COM layout ==")
# These are the literal MOV-immediate pairs recovered from H startup/context-init code.
check("H boot context loads GP FEBF9800 / TP 867C",
      codeflash[0x9F4A:0x9F56] == bytes.fromhex("24060098bffe25067c860000"))
check("H application context loads GP FEBEB800 / TP 23D6C",
      codeflash[0x6A8DC:0x6A8E8] == bytes.fromhex("240600b8befe25066c3d0200"))
check("H repeats the application GP/TP pair in a second context-init path",
      codeflash[0x6AD94:0x6ADA0] == bytes.fromhex("240600b8befe25066c3d0200"))
check("application GP is unchanged from Sienna but TP moves by -0x178",
      struct.unpack_from("<I", codeflash, 0x6A8DE)[0] == 0xFEBEB800
      and struct.unpack_from("<I", codeflash, 0x6A8E4)[0] == 0x00023D6C
      and 0x23D6C == 0x23EE4 - 0x178)

tracked_rx = json.loads(APPLICATION_RX_DIFF.read_text(encoding="utf-8"))
fresh_rx = compare_application_rx(
    SIENNA,
    codeflash,
    reference_id="8965B4512000",
    target_id="8965H1202000",
    target_source=source,
)
check("tracked application-Rx diff regenerates exactly", fresh_rx == tracked_rx)
check("normal application Rx table shrinks 47 -> 40 with 39 shared descriptors",
      tracked_rx["reference"]["descriptor_count"] == 47
      and tracked_rx["target"]["descriptor_count"] == 40
      and tracked_rx["summary"]["shared_descriptor_count"] == 39)
check("H normal Rx table is at 0x21F94",
      tracked_rx["target"]["table_start"] == "0x00021F94")
removed_rx = [row["can_id"] for row in tracked_rx["summary"]["removed"]]
added_rx = [row["can_id"] for row in tracked_rx["summary"]["added"]]
check("H removes the Sienna 2E4/191/131/2FD/132/423/020/1DA descriptor set",
      removed_rx == ["0x2E4", "0x191", "0x131", "0x2FD", "0x132", "0x423", "0x020", "0x1DA"],
      repr(removed_rx))
check("H adds one 32-byte CAN-FD 0B6 normal-Rx descriptor",
      added_rx == ["0x0B6"] and tracked_rx["summary"]["added"][0]["length"] == 32
      and tracked_rx["summary"]["added"][0]["can_fd"] is True)

# Correct H TP=0x23D6C resolves the generated COM tables without overlap.
h_tp = 0x23D6C
h_signal_properties = h_tp - 0x1A84
h_signal_to_pdu = h_tp - 0x1970
h_pdu_table = 0x22620
h_signal_count = (h_pdu_table - h_signal_to_pdu) // 2
check("corrected H TP resolves 274 configured COM signal IDs",
      h_signal_properties == 0x222E8 and h_signal_to_pdu == 0x223FC
      and h_signal_count == 274 and h_signal_to_pdu + h_signal_count * 2 == h_pdu_table)
h_sig_to_pdu = [struct.unpack_from("<H", codeflash, h_signal_to_pdu + 2 * i)[0]
                for i in range(h_signal_count)]
check("all 274 signal-to-PDU entries reference the 45-PDU H table",
      max(h_sig_to_pdu) == 44 and min(h_sig_to_pdu) == 0)
check("H has 55 transmit-side signals before the first Rx PDU",
      next(i for i, pdu in enumerate(h_sig_to_pdu) if pdu >= 5) == 55)
check("H secured B6 PDU 42 owns signal IDs 252..267",
      [i for i, pdu in enumerate(h_sig_to_pdu) if pdu == 42] == list(range(252, 268)))

# Five H Tx CanIf descriptors: legacy 260/262 collapse out; FD 030 appears.
h_tx_canif = [struct.unpack_from("<IBBH", codeflash, 0x21F04 + 8 * i) for i in range(5)]
check("H Tx CanIf IDs are FD030/351/394/4A3/4C8",
      [(row[0] & 0x7FF, bool(row[0] & 0x40000000)) for row in h_tx_canif]
      == [(0x030, True), (0x351, False), (0x394, False), (0x4A3, False), (0x4C8, False)])
h_tx_pdu = [struct.unpack_from("<HBBHBB", codeflash, h_pdu_table + 8 * i) for i in range(5)]
check("H Tx PDU0 is 32-byte cycle-2 and remaining four keep Sienna periods/lengths",
      h_tx_pdu == [
          (2, 0, 0, 32, 0, 3),
          (200, 0, 0, 4, 0, 3),
          (60, 0, 0, 3, 0, 3),
          (100, 0, 0, 8, 0, 3),
          (196, 0, 0, 8, 0, 3),
      ])
check("H Tx signal allocation is 37/2/4/8/4 across its five PDUs",
      [h_sig_to_pdu[:55].count(i) for i in range(5)] == [37, 2, 4, 8, 4])

s_signal_to_pdu = 0x224E4
s_pdu_table = 0x2273C
s_signal_count = (s_pdu_table - s_signal_to_pdu) // 2
s_sig_to_pdu = [struct.unpack_from("<H", SIENNA, s_signal_to_pdu + 2 * i)[0]
                for i in range(s_signal_count)]
s_tx_signal_count = next(i for i, pdu in enumerate(s_sig_to_pdu) if pdu >= 6)
check("Sienna has 300 COM signals / 58 Tx versus H 274 / 55",
      s_signal_count == 300 and s_tx_signal_count == 58
      and h_signal_count == 274 and 55 == next(i for i, pdu in enumerate(h_sig_to_pdu) if pdu >= 5))
check("Sienna 260/262 own 10+28 signals while H FD030 owns 37",
      [s_sig_to_pdu[:58].count(i) for i in range(6)] == [10, 28, 2, 6, 8, 4]
      and [h_sig_to_pdu[:55].count(i) for i in range(5)] == [37, 2, 4, 8, 4])

# Count configured scalar/group signals per normal Rx PDU for the 39 shared descriptors.
s_pdu_signal_counts = Counter(s_sig_to_pdu)
h_pdu_signal_counts = Counter(h_sig_to_pdu)
s_rx_rows = []
for i in range(47):
    software_id, length = struct.unpack_from("<II", SIENNA, 0x22018 + 8 * i)
    s_rx_rows.append(((software_id & 0x7FF, length, bool(software_id & 0x40000000)), 6 + i))
h_rx_rows = []
for i in range(40):
    software_id, length = struct.unpack_from("<II", codeflash, 0x21F94 + 8 * i)
    h_rx_rows.append(((software_id & 0x7FF, length, bool(software_id & 0x40000000)), 5 + i))
h_rx_by_key = dict(h_rx_rows)
shared_signal_count_pairs = [
    (s_pdu_signal_counts[s_pdu], h_pdu_signal_counts[h_rx_by_key[key]])
    for key, s_pdu in s_rx_rows if key in h_rx_by_key
]
check("28/39 shared normal Rx PDUs retain the same configured signal count",
      sum(a == b for a, b in shared_signal_count_pairs) == 28
      and len(shared_signal_count_pairs) == 39)
check("11 shared normal Rx PDUs change configured signal count",
      sum(a != b for a, b in shared_signal_count_pairs) == 11)

print("\n== whole-image cross-calibration function-body census ==")
tracked_transfer = json.loads(FUNCTION_TRANSFER.read_text(encoding="utf-8"))
fresh_transfer = compare_function_bodies(
    SIENNA,
    REFERENCE_INVENTORY,
    codeflash,
    target_source=source,
    reference_id="8965B4512000",
    target_id="8965H1202000",
)
check("tracked whole-image transfer artifact regenerates exactly", fresh_transfer == tracked_transfer)
summary = tracked_transfer["summary"]
check("function census is exact-image bound",
      tracked_transfer["reference"]["codeflash_sha256"] == hashlib.sha256(SIENNA).hexdigest()
      and tracked_transfer["target"]["normalized_codeflash_sha256"] == CODEFLASH_SHA
      and tracked_transfer["target"]["source_sha256"] == SOURCE_SHA)
check("census covers every canonical CodeFlash function",
      summary["reference_codeflash_functions"] == 6375 and summary["named_reference_functions"] == 1113)
check("exact complete-body transfer is proved for 1017 canonical functions",
      summary["exact_body_transfer_proven_functions"] == 1017)
check("exact complete-body transfer is proved for 288 named canonical functions",
      summary["named_exact_body_transfer_proven_functions"] == 288)

transfer_by_name = {
    row["name"]: row for row in tracked_transfer["functions"] if row.get("name")
}
transfer_by_reference_entry = {
    int(row["reference_entry"], 16): row for row in tracked_transfer["functions"]
}
for name, target in (
    ("boot_peripheral_init", "0x00000C7E"),
    ("boot_validity_check", "0x00001182"),
    ("boot_application_handoff", "0x00001394"),
    ("uds_request_download", "0x00005D4C"),
    ("security_access_derive_stage1_key", "0x00006FD0"),
    ("payload_build_derive_key", "0x0000704C"),
):
    row = transfer_by_name[name]
    check(f"{name} transfers byte-for-byte at the -0x1C boot relocation",
          row["classification"] == "exact-unique-relocated"
          and row["target_entry"] == target and row["delta"] == "-0x1C")

boot_family = [
    row for row in tracked_transfer["functions"]
    if row.get("name") and re.search(
        r"^(boot_|bootloader_|uds_|security_access_|payload_|aes128_|aes_cmac_|"
        r"cantp_|CanTp_|CanIf_|Dcm_|PduR_)", row["name"]
    )
]
boot_exact = [
    row for row in boot_family
    if row["classification"] in {"exact-same-va", "exact-unique-relocated"}
]
check("named boot/trust/UDS/crypto cohort is overwhelmingly exact",
      len(boot_family) == 126 and len(boot_exact) == 119,
      f"{len(boot_exact)}/{len(boot_family)}")

clusters = {row["delta"]: row for row in tracked_transfer["relocation_clusters"]}
check("dominant boot relocation has 292 >=16-byte exact anchors",
      clusters["-0x1C"]["function_count"] == 292
      and clusters["-0x1C"]["named_function_count"] == 161)
check("application/framework relocation islands are independently present",
      clusters["-0x5C60"]["function_count"] == 191
      and clusters["-0x5C00"]["function_count"] == 97
      and clusters["-0x4FDA"]["function_count"] == 108)

print("\n== target-native unique structural homolog inventory ==")
structural = json.loads(STRUCTURAL_TRANSFER.read_text(encoding="utf-8"))
check("structural artifact records the target-native uniqueness evidence boundary",
      structural["schema"] == "rh850-cross-image-structural-function-match-v1"
      and "operands" in structural["evidence_boundary"].lower())
check("clean Ghidra structural inventories cover S 6376 / H 5425 functions",
      structural["reference"]["function_count"] == 6376
      and structural["target"]["function_count"] == 5425)
check("2542 complete instruction-shape pairs are unique on both images",
      structural["summary"]["unique_exact_shape_matches"] == 2542)
check("2324 unique shape pairs contain at least eight instructions",
      structural["summary"]["unique_exact_shape_matches_min_8_instructions"] == 2324)
structural_by_name = {
    row["reference_name"]: row
    for row in structural["matches"] if row.get("reference_name")
}
for name, target, instructions in (
    ("secoc_build_authenticated_input", "0x00087fc2", 39),
    ("secoc_rx_verify_worker", "0x00088a56", 132),
    ("dq_current_pi_axis_a", "0x000324d4", 113),
    ("dual_motor_dq_current_reference", "0x0003322e", 40),
    ("tsg3_pwm_compare_commit", "0x0005b9ae", 23),
    ("steering_torque_command_clamp_gain", "0x000c91b6", 39),
    ("steering_torque_command_rate_limit", "0x000c9232", 77),
):
    row = structural_by_name[name]
    check(f"{name} has one unique complete instruction-shape H candidate",
          row["classification"] == "unique-exact-shape"
          and row["target_entry"] == target
          and row["instruction_count"] == instructions)

print("\n== joined named-function transfer ledger ==")
tracked_ledger = json.loads(NAMED_TRANSFER_LEDGER.read_text(encoding="utf-8"))
fresh_ledger = build_named_transfer_ledger(tracked_transfer, structural)
check("tracked named-function ledger regenerates exactly", fresh_ledger == tracked_ledger)
check("ledger classifies all 1113 named canonical CodeFlash functions",
      tracked_ledger["summary"]["named_function_count"] == 1113)
check("ledger preserves 288 exact-byte named transfers",
      tracked_ledger["summary"]["status_counts"]["exact-byte-transfer"] == 288)
ledger_by_name = {row["reference_name"]: row for row in tracked_ledger["functions"]}
check("boot_validity_check is promoted only to exact-byte transfer",
      ledger_by_name["boot_validity_check"]["status"] == "exact-byte-transfer"
      and ledger_by_name["boot_validity_check"]["target_entry"] == "0x00001182")
for name in ("secoc_rx_verify_worker", "dq_current_pi_axis_a", "steering_torque_command_clamp_gain"):
    check(f"{name} is a structural candidate rather than byte-identical",
          ledger_by_name[name]["status"] == "unique-instruction-shape-candidate")

print("\n== boot memory-safety primitive transfer ==")
check("boot access-policy table transfers exactly at -0x20",
      codeflash[0x8D80:0x8DB0] == SIENNA[0x8DA0:0x8DD0])
check("RoutineControl 10F0/10F1/10F2/10F3/FF00 table transfers exactly at -0x20",
      codeflash[0x8F24:0x8F60] == SIENNA[0x8F44:0x8F80])
for index in range(3):
    s_row = struct.unpack_from("<7I", SIENNA, 0x8E00 + index * 28)
    h_row = struct.unpack_from("<7I", codeflash, 0x8DE0 + index * 28)
    check(f"boot region {index} policy geometry transfers",
          h_row[:6] == s_row[:6]
          and h_row[6] == s_row[6] - 0x20,
          f"S={tuple(hex(x) for x in s_row)} H={tuple(hex(x) for x in h_row)}")
for reference_entry, target_entry, label in (
    (0x4B7C, 0x4B60, "TransferData partial-block gate"),
    (0x567E, 0x5662, "RoutineControl dispatcher"),
    (0x5936, 0x591A, "10F0 CRC/CMAC authorization worker"),
    (0x6BDE, 0x6BC2, "payload decrypt/transfer worker"),
    (0x7122, 0x7106, "CMAC endpoint setup"),
    (0x7170, 0x7154, "CMAC stepping worker"),
    (0x6C8E, 0x6C72, "10F3 memory compare worker"),
):
    row = transfer_by_reference_entry[reference_entry]
    check(f"{label} transfers byte-for-byte",
          row["classification"] == "exact-unique-relocated"
          and row["target_entry"] == f"0x{target_entry:08X}"
          and row["delta"] == "-0x1C")
check("MEM-SAFE-004 command-8 copy-result body does not transfer exactly",
      transfer_by_reference_entry[0x86EE8]["classification"] == "changed-or-absent")

print("\n== XCP-shaped command-family transfer boundary ==")
selectors = []
targets = []
for index in range(7):
    selector, padding, target = struct.unpack_from("<B3sI", codeflash, 0x2AE38 + index * 8)
    check(f"foreign custom command record {index} has zero padding", padding == b"\0\0\0")
    selectors.append(selector)
    targets.append(target)
check("foreign custom command selectors remain FB/FA/F5/F3/EB/EA/E4",
      selectors == [0xFB, 0xFA, 0xF5, 0xF3, 0xEB, 0xEA, 0xE4], repr(selectors))
check("foreign custom command callbacks relocate to the recovered H handler family",
      targets == [0x922CA, 0x9232A, 0x92462, 0x92576, 0x9261E, 0x92698, 0x92724],
      repr([hex(x) for x in targets]))
check("three foreign custom handlers are exact complete-body transfers",
      all(transfer_by_name[name]["classification"] == "exact-unique-relocated"
          for name in ("xcp_command_fb_handler", "xcp_command_f3_handler", "xcp_command_e4_handler")))
check("Sienna plain-u32 0x7F7/0x7F8 route representation is absent from H CodeFlash",
      struct.pack("<I", 0x7F7) not in codeflash and struct.pack("<I", 0x7F8) not in codeflash)
packed_xcp_request = 0x80000000 | (0x7F7 << 18) | 0x2
packed_xcp_response = 0x80000000 | (0x7F8 << 18) | 0x2
check("H special response descriptor packs standard CAN 0x7F8",
      struct.unpack_from("<I", codeflash, 0x21EF4)[0] == packed_xcp_response
      and struct.unpack_from("<I", codeflash, 0x21954)[0] == 0x21EF4)
check("H special request descriptor packs standard CAN 0x7F7 with DLC 8",
      struct.unpack_from("<I", codeflash, 0x21EFC)[0] == packed_xcp_request
      and struct.unpack_from("<I", codeflash, 0x21F00)[0] == 8
      and struct.unpack_from("<I", codeflash, 0x21A50)[0] == 0x21EFC)
check("H special request class points at relocated receive callback 0x7C43E",
      struct.unpack_from("<I", codeflash, 0x21A54)[0] == 0x7C43E)
check("H special receive callback is 41/42 bytes identical to Sienna callback",
      len(codeflash[0x7C43E:0x7C468]) == 42
      and sum(a == b for a, b in zip(
          SIENNA[0x82042:0x8206C], codeflash[0x7C43E:0x7C468]
      )) == 41)

structure = analyze_codeflash_structure(codeflash)
xcp_structure = structure["xcp_command_surface"]
check("structure scanner distinguishes H packed XCP route from absent plain representation",
      xcp_structure["request_can_id_immediates"]["count"] == 0
      and xcp_structure["response_can_id_immediates"]["count"] == 0
      and xcp_structure["request_can_id_packed_standard_descriptors"]["count"] == 2
      and xcp_structure["response_can_id_packed_standard_descriptors"]["count"] == 1)

h_command_map = codeflash[0x22A48:0x22A48 + codeflash[0x22A15]]
s_command_map = SIENNA[0x22C04:0x22C04 + SIENNA[0x22BD1]]
check("generic XCP-shaped opcode map transfers byte-for-byte", h_command_map == s_command_map)
check("generic XCP-shaped map still has no GET_SEED or UNLOCK callback",
      h_command_map[0xFF - 0xF8] == 0 and h_command_map[0xFF - 0xF7] == 0)
s_callbacks = [struct.unpack_from("<I", SIENNA, 0x22C30 + i * 4)[0] for i in range(18)]
h_callbacks = [struct.unpack_from("<I", codeflash, 0x22A74 + i * 4)[0] for i in range(18)]
check("all 18 generic XCP-shaped callbacks preserve one -0x5C04 relocation",
      h_callbacks == [target - 0x5C04 for target in s_callbacks])
check("generic XCP-shaped LocalRAM bounds transfer exactly",
      codeflash[0x229C4:0x229D4] == SIENNA[0x22B80:0x22B90])
check("XCP-shaped exclusion count and 32-KiB shadow bounds transfer exactly",
      codeflash[0x2AE00:0x2AE0C] == SIENNA[0x2B3B8:0x2B3C4])
h_exclusions = [struct.unpack_from("<II", codeflash, 0x28F0C + i * 8) for i in range(5)]
check("H XCP-shaped LocalRAM exclusion table is recovered",
      h_exclusions == [
          (0xFEBE0000, 0xFEBE37FF),
          (0xFEBE4F28, 0xFEBE5193),
          (0xFEBF0150, 0xFEBF128F),
          (0xFEBF4958, 0xFEBF4B33),
          (0xFEBF6000, 0xFEBF6CDF),
      ], repr([(hex(a), hex(b)) for a, b in h_exclusions]))
check("H still carries the ordinary 0x7A1/0x777/0x7A0 application diagnostic literals",
      all(struct.pack("<I", can_id) in codeflash for can_id in (0x7A1, 0x777, 0x7A0)))

print("\n== steering/motor exact-transfer negative ==")
steering_motor = [
    row for row in tracked_transfer["functions"]
    if row.get("name") and re.search(
        r"(steer|torque|lta|motor|dq_|phase_|pwm|current_|actuation|control_partition)",
        row["name"], re.IGNORECASE,
    )
]
steering_motor_exact = [
    row for row in steering_motor
    if row["classification"] in {"exact-same-va", "exact-unique-relocated"}
]
check("39 named Sienna steering/motor bodies are in the comparison cohort", len(steering_motor) == 39)
check("none of those 39 complete bodies transfers byte-for-byte", len(steering_motor_exact) == 0)
for name in (
    "dq_current_pi_axis_a",
    "dq_current_pi_axis_b",
    "steering_torque_command_clamp_gain",
    "steering_torque_command_rate_limit",
    "steering_request_source_arbitration",
):
    row = transfer_by_name[name]
    check(f"{name} has no exact complete-body transfer", row["classification"] == "changed-or-absent")

print(f"\nResults: {passed} passed, {failed} failed")
if failed:
    raise SystemExit(1)
