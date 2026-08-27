#!/usr/bin/env python3
"""Verify the Tacoma VFOREST CUW corpus census and comparative invariants."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "data/generated/techstream_v18/cuw_tacoma_vforest_corpus.json"
CORPUS = REPO / "software/Techstream/cuw"
ROOT = REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"
sys.path.insert(0, str(REPO / "tools/techstream"))

from cuw_attach import parse_attach_bytes
from parse_cuw_container import first_member_payload
from inspect_cuw_vforest import decode_ascii_hex_payload, parse_zv_lzf_stream
from parse_cuw_container import parse as parse_container

p = f = 0
oracle = "independent_external_artifact+generated_self_check"


def check(name: str, cond: object, detail: str = "") -> None:
    global p, f
    ok = bool(cond)
    p += int(ok); f += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


if not ROOT.is_dir():
    print("[SKIP] V18 unavailable")
    raise SystemExit(77)
ev = json.loads(EVIDENCE.read_text())

EXPECTED_PACKAGES = {
    "T-0002-21 - 04A72.cuw": (2521231, "8329b19f4e02d6902bb1702b156a6890f578f87f83888c3a641e46ee1bc4847b"),
    "T-0003-21 - 04B42.cuw": (2547117, "1424b70028e3eb4ec35e8f52e5d6dc6d2f76766ac287fada7f112e83da63cdd9"),
    "T-0004-21 - 04B91.cuw": (2573420, "626153b7ea6092c482d7588866f8970cb23bf531b86e10958766f8f8d96cebba"),
    "T-0011-21 - 04C21.cuw": (2825257, "e0525b4fe0224772a3dde68d16bf2fb7a808d6d937fa32a337db34d95f5ba61d"),
    "T-0012-21 - 04B82.cuw": (3939174, "6f88600c05ff90e05d55482caf41901b6a27e30c62d7fdf997c81ecc82f576be"),
    "T-0014-20 - 04B14.cuw": (2413081, "1615d3f4e463f7088ada0149e9c42d7238a831ab693c4b7b6d93cb6c9c14196b"),
    "T-0022-20 - 04B33.cuw": (3891207, "579c898a34e27b4b25ac5d233a4102a12f6eadb3f18e4e3bd1c95cf50c46b908"),
    "T-0023-20 - 04B81.cuw": (3939040, "4a6d6616b0307b8f4b92d8a5b3eede1e5db43a884c781d6ff12777e991d57337"),
    "T-0034-18 - 04B04.cuw": (3720924, "34480b3d167f0834d622992973408958ace89cd2b1ceb2bfb78b1f9ef868f246"),
    "T-0036-18 - 04A61.cuw": (3856075, "24aa61d71891d433b986e7e8819ffd7d763bcfc670201966a0d3e395846c5828"),
    "T-0037-18 - 04A71.cuw": (2521449, "a2462044980eb02c5f5b1073fe5fb2610c432d77889e85cf8eaaa2b86f56f770"),
}
EXPECTED_TRAILING_FILL_STARTS = {
    "8966304A7200": 0x160350, "8966304B4200": 0x164640, "8966304B9100": 0x1677EC,
    "8966304C2100": 0x18BAF0, "8966304B8200": 0x18BE18, "8966304B1400": 0x151698,
    "896650407200": 0x920BC, "8966304B3300": 0x184A64, "8966304B8100": 0x18BE08,
    "896650401400": 0x902B8, "8966304B0400": 0x16FB08, "896650404100": 0x919FC,
    "8966304A6100": 0x180708, "8966304A7100": 0x16032C,
}
EXPECTED_TRAILING_FILL_START_04101 = 0x92898

EXPECTED_IMAGES = {
    ("T-0002-21 - 04A72.cuw", "8966304A7200"): (0x200000, "205883b2da3b3f113d338b5388223f2b14487322cc81adacbe64e9948a21b5bb", [[353, 510]]),
    ("T-0003-21 - 04B42.cuw", "8966304B4200"): (0x200000, "4def0c57afdb332c58be43d7c4396ca86447aadd8d62f7c39b10e30578aaa1cb", [[357, 510]]),
    ("T-0004-21 - 04B91.cuw", "8966304B9100"): (0x200000, "7b18097eed046d1e37771ca533f0963ed71f663ad274183d4a2fd242f906e35e", [[360, 510]]),
    ("T-0011-21 - 04C21.cuw", "8966304C2100"): (0x200000, "feb1e7ff00f7268ece3f043a56ac39a33bd22dffbe4f7f23fad1286b53db8e04", [[396, 510]]),
    ("T-0012-21 - 04B82.cuw", "896650410100"): (0x140000, "11278da8f4ded5bf6a15a53eac28be98d2f1919720eeaf8e0365e170fe0f8b8b", [[147, 318]]),
    ("T-0012-21 - 04B82.cuw", "8966304B8200"): (0x200000, "1fa5ddfc2bb8381daf40a57ff1c8dbd88ca68a8ae02162d8f214df72d91d55be", [[396, 510]]),
    ("T-0014-20 - 04B14.cuw", "8966304B1400"): (0x180000, "9b67316a8bcee2c5082d5ad2ae93bf6f58ce66b5148892085975a18427a9b131", [[338, 382]]),
    ("T-0022-20 - 04B33.cuw", "896650407200"): (0x140000, "21eaef015991f0dd422a45521188ee2cc4eb48d6e8c0caf4fdd08c751d61897e", [[147, 318]]),
    ("T-0022-20 - 04B33.cuw", "8966304B3300"): (0x200000, "9c4a8f225272aca768a6288e6293df71ea3bc25fa5167e799b3702d4780a6034", [[389, 510]]),
    ("T-0023-20 - 04B81.cuw", "896650410100"): (0x140000, "11278da8f4ded5bf6a15a53eac28be98d2f1919720eeaf8e0365e170fe0f8b8b", [[147, 318]]),
    ("T-0023-20 - 04B81.cuw", "8966304B8100"): (0x200000, "7ea4c187baa867f7ceb34bee8ce05053d14c125982fdaeb5b05b445a75918d1e", [[396, 510]]),
    ("T-0034-18 - 04B04.cuw", "896650401400"): (0x140000, "d13943bb5fd57efaef0fda887d6be390ff2f674d93d5551aa4199ac55bd61ae3", [[145, 318]]),
    ("T-0034-18 - 04B04.cuw", "8966304B0400"): (0x180000, "62d65181f566ebf0959696863c998a977553c5846ae1f6c1d4bc2c38b53c6c2c", [[368, 382]]),
    ("T-0036-18 - 04A61.cuw", "896650404100"): (0x140000, "17ed52838c79477a86e9425fd1fdf40beb955cbd2e5d6450b7268ec9ba376440", [[146, 318]]),
    ("T-0036-18 - 04A61.cuw", "8966304A6100"): (0x200000, "7ef2e7a0030d4452c9ae7d1bef811f4e93938ebb9861f597207c34952ac15694", [[385, 510]]),
    ("T-0037-18 - 04A71.cuw", "8966304A7100"): (0x200000, "edd1c733d26541c2ec97dccb431993553cb30f651ba76e2a59e099f80e4ccfa0", [[353, 510]]),
}

print("== pinned corpus census ==")
check("schema version", ev["schema_version"] == 1)
check("11 Tacoma packages", ev["corpus"]["package_count"] == 11 and len(ev["packages"]) == 11)
check("16 logical CPU images", ev["corpus"]["logical_image_count"] == 16 and len(ev["images"]) == 16)
check("package identities pinned", {
    row["filename"]: (row["size"], row["sha256"]) for row in ev["packages"]
} == EXPECTED_PACKAGES)

print("\n== size-class and route join ==")
types = ev["corpus"]["cpu_types"]
check("CPU86 is VFOREST_2_0M / 2 MiB", types["86"] == {
    "cpu_type_export": "?glptrCPUType_VFOREST_2_0M@@3PBDB", "image_count": 9,
    "logical_image_lengths": [0x200000], "route_keys": ["0P5-CAN86"],
})
check("CPU87 is VFOREST_1_5M / 1.5 MiB", types["87"] == {
    "cpu_type_export": "?glptrCPUType_VFOREST_1_5M@@3PBDB", "image_count": 2,
    "logical_image_lengths": [0x180000], "route_keys": ["0P5-CAN87"],
})
check("CPU89 is VFOREST_1_25M / 1.25 MiB", types["89"] == {
    "cpu_type_export": "?glptrCPUType_VFOREST_1_25M@@3PBDB", "image_count": 5,
    "logical_image_lengths": [0x140000], "route_keys": ["0P5-CAN89"],
})
for row in ev["images"]:
    route = row["route"]
    check(f"{row['package']} {row['cpu_section']} integrated route exact",
          route["PasswordAddress"] == "0000100E" and route["ByteOrder"] == "0" and
          route["CalibrationType"] == "2" and route["EngineTypeFlag"] == "1" and
          route["FORESTTypeFlag"] == "1" and route["M16CTypeFlag"] == "0" and
          route["FlagToUseCIDGetterAndFlashWriterDLL"] == "0" and
          route["FlagToUseGetFlashSizeFunc"] == "1" and
          route["WaitTimeAfterIGOn"] == "10000" and route["WaitTimeForIGOFFON"] == "10" and
          route["FlagToChangeToReprogGWModeForCentralGW"] == "1" and
          route["FlagToCancelAutomaticIGOFF"] == "1" and
          route["FlagToDoIGOFFONAtCPUTypeChange"] == "0" and
          route["CPUTypeWithModeChangeAtCPUTypeChangeFlag"] == "0")

print("\n== exact image identities and structural invariants ==")
actual_images = {
    (row["package"], row["new_cid"]): (
        row["logical_image"]["length"], row["logical_image"]["sha256"],
        row["logical_image"]["full_fill_block_runs"],
    ) for row in ev["images"]
}
check("all logical image hashes/sizes/fill runs pinned", actual_images == EXPECTED_IMAGES)
for row in ev["images"]:
    check(f"{row['package']} {row['cpu_section']} archive member maps to descriptor CPU",
          row["logical_image"]["part_identity_offset"] == 0x100C and
          row["logical_image"]["part_identity_ascii"] == f"{row['new_cid'][:5]}-{row['new_cid'][5:10]}-")
    check(f"{row['package']} {row['cpu_section']} password/address/footer invariant",
          row["metadata"]["password_field_logical_offset"] == 0x1004 and
          row["metadata"]["password_address_in_decoded_zv"] == 0x100E and
          row["metadata"]["logical_password_equals_zv_password"] and
          row["metadata"]["marker_hex"] == "9E5D123A" and
          row["metadata"]["footer_magic_hex"] == "B270AD78E88F32B558FEEB58D03B3B1D" and
          row["metadata"]["footer_repeats_metadata_window"])
    expected_fill_start = (EXPECTED_TRAILING_FILL_START_04101 if row["new_cid"] == "896650410100"
                           else EXPECTED_TRAILING_FILL_STARTS[row["new_cid"]])
    trailing = row["logical_image"]["trailing_fill_before_footer"]
    check(f"{row['package']} {row['cpu_section']} exact trailing fill boundary",
          trailing["start_offset"] == expected_fill_start and
          trailing["end_exclusive"] == row["logical_image"]["length"] - 52 and
          trailing["length"] == trailing["end_exclusive"] - trailing["start_offset"])

inv = ev["cross_image_invariants"]
check("all 16 images share exact 0x1004-byte prefix",
      inv["exact_common_prefix_length"] == 0x1004 and
      inv["exact_common_prefix_sha256"] == "515a0f447cdf25ce3bab0978087a00162aad66c089c0c2454fd831a19f3a00cd" and
      inv["common_first_4k_block_sha256"] == "9973b8547c168795f279ae402a0777a08f4791f0a37395a3f74351f48b021eed" and
      inv["first_divergent_offset"] == 0x1004)
check("common footer layout exact", inv["footer_layout"] == "magic[16] || zero[4] || image[0x1004:0x1024]" and inv["all_images_have_footer_layout"])
check("all new password bytes appear at logical 0x1004", inv["all_password_fields_match_decoded_zv_at_password_address"])
check("fill representation pinned", inv["all_images_use_fill_word_hex"] == "E203F133")
check("representation conclusion remains bounded", "not behaving as whole-image cryptographic ciphertext" in inv["representation_boundary"] and "remains bounded" in inv["representation_boundary"])

cpu86 = ev["cpu86_comparative_structure"]
check("CPU86 common blocks are block0 plus 396..510", cpu86["common_4k_block_ranges"] == [[0, 0], [396, 510]])
EXPECTED_MATRIX = {
    "8966304A6100": [0,385,385,387,385,395,395,385,395],
    "8966304A7100": [385,0,284,389,355,396,396,359,396],
    "8966304A7200": [385,284,0,389,355,396,396,359,396],
    "8966304B3300": [387,389,389,0,389,395,395,389,395],
    "8966304B4200": [385,355,355,389,0,396,396,359,396],
    "8966304B8100": [395,396,396,395,396,0,73,396,392],
    "8966304B8200": [395,396,396,395,396,73,0,396,392],
    "8966304B9100": [385,359,359,389,359,396,396,0,396],
    "8966304C2100": [395,396,396,395,396,392,392,396,0],
}
rows = cpu86["pairwise_changed_4k_block_counts"]
ordered_cids = [row["new_cid"] for row in rows]
check("CPU86 pairwise changed-block matrix pinned",
      ordered_cids == sorted(EXPECTED_MATRIX) and
      all([row["changed_4k_blocks"][cid] for cid in ordered_cids] == EXPECTED_MATRIX[row["new_cid"]] for row in rows))

print("\n== controlled direct-update comparisons ==")
comparisons = {row["name"]: row for row in ev["direct_update_comparisons"]}
a = comparisons["04A71_to_04A72"]
check("04A71 is explicit source target of 04A72", a["target_edge_present"])
check("04A71->04A72 diff pinned", a["logical_image_diff"]["changed_bytes"] == 144280 and a["logical_image_diff"]["changed_block_count"] == 284 and a["logical_image_diff"]["changed_block_ranges"] == [[1,4],[7,7],[13,16],[19,21],[25,26],[45,45],[68,69],[74,76],[78,83],[91,96],[100,102],[104,108],[110,352],[511,511]])
bc = comparisons["04B81_to_04B82_companion_CPUType89"]
check("B81/B82 companion CPU89 decoded archive is byte-identical", bc["decoded_zv_identical"] and bc["logical_image_diff"]["identical"] and bc["logical_image_diff"]["changed_bytes"] == 0)
bm = comparisons["04B81_to_04B82_main_CPUType86"]
check("04B81 is explicit source target of 04B82", bm["target_edge_present"])
check("04B81->04B82 main diff pinned", bm["logical_image_diff"]["changed_bytes"] == 135465 and bm["logical_image_diff"]["changed_block_count"] == 73 and bm["logical_image_diff"]["changed_block_ranges"] == [[1,4],[15,15],[80,80],[82,82],[87,87],[101,101],[110,111],[113,113],[120,120],[124,126],[128,128],[130,133],[139,139],[141,141],[145,145],[147,147],[186,186],[237,237],[243,243],[306,306],[308,308],[318,319],[355,356],[358,395],[511,511]])
check("B81->B82 has sparse patches plus dense rewritten tail region", bm["logical_image_diff"]["dense_changed_blocks_gt_2048_bytes"] == list(range(362,396)))

print("\n== multi-CPU ordering and predecessor password closure ==")
multi = {row["package"]: row for row in ev["multi_cpu_packages"]}
check("five packages carry two CPU images", set(multi) == {
    "T-0012-21 - 04B82.cuw", "T-0022-20 - 04B33.cuw", "T-0023-20 - 04B81.cuw",
    "T-0034-18 - 04B04.cuw", "T-0036-18 - 04A61.cuw",
})
for package, row in multi.items():
    order = row["cpu_member_order"]
    check(f"{package} archive member order follows CPU01/CPU02",
          len(order) == 2 and order[0]["cpu_section"] == "CPU01" and order[0]["member_index"] == 1 and
          order[1]["cpu_section"] == "CPU02" and order[1]["member_index"] == 2 and
          order[0]["cpu_type"] == "89" and order[1]["cpu_type"] in {"86", "87"})
closures = ev["predecessor_password_closures"]
check("two in-corpus predecessor password joins close exactly",
      len(closures) == 2 and all(row["password_matches"] for row in closures) and
      {(row["predecessor_cid"], row["successor_cid"]) for row in closures} == {
          ("8966304A7100", "8966304A7200"), ("8966304B8100", "8966304B8200")
      })

print("\n== security boundary ==")
sec = ev["security_boundary"]
check("all size classes share legacy SA grammar", "PasswordAddress=0x100E" in sec["cpu_types_86_87_89_route_equivalence"] and "seed XOR 00 60 60 00" in sec["diagnostic_security_access"])
check("software password remains independent CheckID", "independent CheckID" in sec["software_password"])
check("modern EPS transfer explicitly rejected", "comparative only" in sec["modern_eps_transfer"] and "ECUAuthKey" in sec["modern_eps_transfer"])

if CORPUS.is_dir():
    print("\n== local raw-corpus cross-check ==")
    # The corpus directory also carries non-Tacoma specimens pinned by other
    # suites (FRC format-0x67 packages, contrast set, T-0087-17); this suite
    # verifies the 11 pinned Tacoma packages and ignores the rest.
    local = sorted(path for path in CORPUS.glob("T-*.cuw") if path.name in EXPECTED_PACKAGES)
    check("all 11 pinned Tacoma CUWs present", len(local) == 11 and {path.name for path in local} == set(EXPECTED_PACKAGES))
    local_image_hashes = {}
    for path in local:
        data = path.read_bytes()
        check(f"{path.name} raw package hash", (len(data), hashlib.sha256(data).hexdigest()) == EXPECTED_PACKAGES[path.name])
        obj = parse_container(data)
        attach = parse_attach_bytes(first_member_payload(data, obj))
        cpus = [attach[key] for key in sorted(key for key in attach if key.startswith("CPU"))]
        check(f"{path.name} member count maps to CPU count", len(cpus) == len(obj["format4_archives"]))
        for cpu, member in zip(cpus, obj["format4_archives"]):
            start = int(member["payload_offset"])
            payload = data[start:start + int(member["payload_length"])]
            raw = decode_ascii_hex_payload(payload)
            records, image = parse_zv_lzf_stream(raw)
            key = (path.name, cpu["NewCID"])
            local_image_hashes[key] = (len(image), hashlib.sha256(image).hexdigest())
            check(f"{path.name} {cpu['NewCID']} consumes ZV stream exactly",
                  sum(r["header_length"] + r["stored_length"] for r in records) == len(raw))
    check("local reconstructed image identities match generated evidence",
          local_image_hashes == {key: (value[0], value[1]) for key, value in EXPECTED_IMAGES.items()})

print(f"\nResults: {p} passed, {f} failed")
raise SystemExit(1 if f else 0)
