#!/usr/bin/env python3
"""Verify the FRC CUW corpus (format 0x67 / ReproMethod 07) evidence.

Part A recomputes every corpus claim from the raw `.cuw` bytes in
REFERENCE/cuw: container grammar, descriptor fields, S-record framing,
cross-package invariants, and the whole-repro/delta boundary.

Part B byte-checks the modern GTS+ CUWPlus host anchors against the pinned
binaries in REFERENCE/gtsplus_cuwplus (unpacked images + shipped INIs):
descriptor parser (IsControlledBySCC semantics), CLogicalBlockInfo area
layout, ReproMethod enum, the ReproStd writer's RequestDownload grammar and
compact DFI 0x21 selector, JudgeReproGWNodeForP4AndP5, and the RKS 27 21/22
sink.

Evidence boundaries asserted here (do not weaken):
- `.xx` members are Motorola S-record framing only; decoded data is
  high-entropy with unknown encoding (no plaintext claim).
- `.datx` is the DeltaReproData payload downloaded with DFI 0x21 (compact
  delta representation) and consumed ECU-side as its delta input; the exact
  transform/semantics are unknown and "decrypted" is not claimed.
- IsControlledBySCC does NOT select RKS; RKS selection is the runtime
  JudgeReproGWNode result.
"""
from __future__ import annotations

import binascii
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "REFERENCE/cuw"
GTS = REPO / "REFERENCE/gtsplus_cuwplus/CUWPlus"
V18_CUW = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics/Calibration Update Wizard"
ARTIFACT = REPO / "data/generated/techstream_v18/cuw_frc_corpus.json"
sys.path.insert(0, str(REPO / "tools/techstream"))

from parse_cuw_container import parse as parse_container

p = f = 0
oracle = "independent_external_artifact+raw_bytes"

FRC_PACKAGES = {
    "T-0058-23.cuw": (256400446, "ac5015118d3c5541c62ac3b0626a2d676681b3c4dee2ce6cb84ad547d116fdd9"),
    "T-0060-23.cuw": (256399534, "b3e4a7a951c74ef9985cf05f5151a36538e57bd84392da988d5f8102c652837f"),
    "T-0061-23.cuw": (256401572, "007a351fa0ac096af6c9c7c8085c6690c79abefea058e1fc438033ef3512bf94"),
    "T-0062-23.cuw": (257142135, "9971e3052d63dfe1fb262509ec59bcc8924db0082210117c63e9b01b73070e5b"),
    "T-0149-24.cuw": (257894251, "70bea932f3ae641e0d9fab99419aeb59ac76b08adcfeca97b9278d59d15ad6a8"),
    "T-0150-24.cuw": (257646163, "c28455c5b4ee6b48b4bf7b0fc51c6110969c6de9294bf488583e50727f91b5f1"),
}
CONTRAST_PACKAGES = {
    "T-0003-25.cuw": (7872007, "ec52b1b673d9bf1c1497fc6f0ac2c5f7bfd8bf330907a2e9162c0c84eb9824b4"),
    "T-0005-25.cuw": (7872031, "3f72d67aa4da84aa02d4a9a3661ae458e1d2015c9fcba2f1e4a9961cb39f419e"),
    "T-0008-22.cuw": (35551267, "df77121f29aa45a8ebc203f9bec22147ed2e62362c8d267380ef21637ff90630"),
    "T-0009-22.cuw": (5481006, "a2cdb0667ae07822e5622569b8fbc9e552e51a94c616aff18d5fa66b29574018"),
    "T-0051-26.cuw": (13045570, "536bf4c05e7c135445547574c4bb321d4521e413765be0c6c2ec42d13a1c0117"),
}
SERVICE_AUTH_KEY = "3A8A90AE0ED81B6C37E21C1C5179A93E"
NONCE = "5587BF845F3FF525E610A8A5EC9BD6E5"
ROUTINE_RAW_SHA = "5baa1feba14586b13b131095b44213481292bd3e87a62efceba7a55aed0c430f"
ROUTINE_DECODED_SHA = "161fd56df2bc3454184e63d92aaad43fc5baedd63c112da830bc99304d96cedb"
IMAGE_PREFIX32 = "8b273e8284a5baca96e562b7be41591f25a12998b328c64741b28e63e6d23dfc"
DATX_LEADING_BLOCK = "0a4aba7f300a8745e2acb15b5b59a046"
FLASH_RANGE = (0x08E80000, 0x0E000000)
ROUTINE_RANGE = (0x008F6C00, 0x008F7170)


def check(name: str, cond: object, detail: str = "") -> None:
    global p, f
    ok = bool(cond)
    p += int(ok)
    f += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def decode_index_obfuscated_hex(value: str) -> bytes:
    raw = bytes.fromhex(value)
    return bytes((b - i) & 0xFF for i, b in enumerate(raw))


def parse_attach(raw: bytes) -> dict[str, dict[str, str]]:
    """Independent minimal attach parser (INI-shaped, preserves raw)."""
    sections: dict[str, dict[str, str]] = {}
    current = ""
    for line in raw.decode("latin1").splitlines():
        line = line.strip()
        if not line or line.startswith(";"):
            continue
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            sections.setdefault(current, {})
            continue
        if "=" in line and current:
            key, _, value = line.partition("=")
            sections[current][key.strip()] = value.strip()
    return sections


def scan_srec(payload: bytes) -> tuple[dict, dict[tuple[int, int], bytes]]:
    """Independent S-record framing scan with count/checksum validation."""
    kinds: Counter[str] = Counter()
    bad = 0
    total = 0
    chunks: dict[tuple[int, int], bytes] = {}
    cur: tuple[int, int] | None = None
    buf = bytearray()
    addr_len = {"1": 2, "2": 3, "3": 4}
    for line in payload.split(b"\r\n"):
        if not line:
            continue
        total += 1
        if line[:1] != b"S" or line[1:2] not in b"0123456789":
            bad += 1
            continue
        k = line[1:2].decode()
        try:
            count = int(line[2:4], 16)
            body = binascii.unhexlify(line[4:])
        except ValueError:
            bad += 1
            continue
        if len(body) != count or (sum(body) + count) & 0xFF != 0xFF:
            bad += 1
            continue
        kinds[k] += 1
        if k in addr_len:
            al = addr_len[k]
            addr = int.from_bytes(body[:al], "big")
            chunk = body[al:-1]
            end = addr + len(chunk)
            if cur is None:
                cur = (addr, end)
                buf = bytearray()
            elif addr == cur[1]:
                cur = (cur[0], end)
            elif addr > cur[1]:
                chunks[cur] = bytes(buf)
                cur = (addr, end)
                buf = bytearray()
            else:
                bad += 1
                continue
            buf += chunk
    if cur is not None:
        chunks[cur] = bytes(buf)
    return {"total": total, "bad": bad, "kinds": dict(kinds)}, chunks


if not CORPUS.is_dir():
    print("[SKIP] FRC CUW corpus unavailable")
    raise SystemExit(77)

ev = json.loads(ARTIFACT.read_text()) if ARTIFACT.is_file() else {}

# ---------------------------------------------------------------- Part A
print("== FRC corpus identity and container grammar ==")
frc_payloads: dict[str, dict[str, bytes]] = {}
frc_descriptors: dict[str, dict] = {}
for name, (size, digest) in FRC_PACKAGES.items():
    data = (CORPUS / name).read_bytes()
    check(f"{name}: pinned identity", len(data) == size and sha256(data) == digest)
    parsed = parse_container(data)
    check(f"{name}: container clean", not parsed["errors"] and parsed["format_type"] == 0x67)
    check(f"{name}: declared total equals file size", parsed["declared_total_size"] == len(data))
    check(f"{name}: format-0x67 tail member count is 3", parsed["format67_member_count"] == 3)
    members = parsed["format67_members"]
    check(f"{name}: all member CRCs verify", all(m["computed_payload_crc32"] == m["payload_crc32"] for m in members))
    check(f"{name}: member records consume the declared total",
          members[-1]["record_end"] == parsed["declared_total_size"])
    end = parsed["first_member_end"]
    attach = data[end - parsed["payload_length"]:end]
    desc = parse_attach(attach)
    frc_descriptors[name] = desc
    frc_payloads[name] = {m["name"]: data[m["payload_offset"]:m["payload_offset"] + m["payload_length"]] for m in members}
    check(f"{name}: descriptor shape", desc["Format"]["Version"] == "105"
          and desc["Format"].get("VersionForCFM2") == "1"
          and desc["Vehicle"]["ContactType"] == "P5-Unified"
          and desc["Node01"]["DiagID"] == "0792"
          and desc["Node01"]["RequiredSpecReproVer"] == "04"
          and desc["Node01"]["01_GatewayDiagID"] == "07505F"
          and desc["KindOfCal"]["IsControlledBySCC"] == "1"
          and desc["KindOfCal"]["IsBlankECU"] == "0"
          and desc["LogicalBlock101"]["ReproMethod"] == "07"
          and desc["LogicalBlock101"]["SecurityProperty2"] == "9C")
    check(f"{name}: ServiceAuthKey/Nonce decode (index subtraction)",
          decode_index_obfuscated_hex(desc["Node01"]["ServiceAuthKey"]).decode() == SERVICE_AUTH_KEY
          and decode_index_obfuscated_hex(desc["LogicalBlock101"]["Nonce"]).decode() == NONCE)
    whole = desc["LogicalBlock101"]["WholeReproFileName"]
    datx = desc["LogicalBlock101"]["DeltaReproDataFileName"]
    routine = desc["LogicalBlock101"]["DeltaEraseAndReproRoutineFileName"]
    check(f"{name}: members match descriptor filenames",
          [m["name"] for m in members] == [whole, datx, routine])
    # area descriptors: whole/delta pairs share one DigitalSignature; CRC/CMAC empty
    for whole_sec, delta_sec in (("ReproData101", "DeltaReproData101"),
                                 ("EraseAndReproRoutine101", "DeltaEraseAndReproRoutine101")):
        w, dl = desc[whole_sec], desc[delta_sec]
        sig_w = decode_index_obfuscated_hex(w["DigitalSignature"]) if w["DigitalSignature"] else b""
        sig_d = decode_index_obfuscated_hex(dl["DigitalSignature"]) if dl["DigitalSignature"] else b""
        check(f"{name}: {whole_sec}/{delta_sec} share one 512-byte area signature",
              len(sig_w) == 512 and sig_w == sig_d)
        check(f"{name}: {whole_sec} area is CRC/CMAC empty",
              w["CRC"] == "" and w["CMAC"] == "")
    check(f"{name}: routine area pinned at 0x8F6C00/0x570",
          desc["EraseAndReproRoutine101"]["StartAddress"] == "008F6C00"
          and desc["EraseAndReproRoutine101"]["Length"] == "00000570")

print("\n== S-record framing and payload boundary ==")
images: dict[str, bytes] = {}
for name, payload_map in frc_payloads.items():
    desc = frc_descriptors[name]
    whole_member = desc["LogicalBlock101"]["WholeReproFileName"]
    routine_member = desc["LogicalBlock101"]["DeltaEraseAndReproRoutineFileName"]
    census, chunks = scan_srec(payload_map[whole_member])
    check(f"{name}: whole-repro S-records all validate", census["bad"] == 0, f"{census['total']} records")
    ranges = sorted(chunks)
    check(f"{name}: exactly two data ranges (routine slot + flash)",
          ranges == [ROUTINE_RANGE, FLASH_RANGE],
          str([hex(a) for a, _ in ranges]))
    image = chunks[FLASH_RANGE]
    images[name] = image
    check(f"{name}: decoded image length is 0x5180000", len(image) == 0x5180000)
    counts = Counter(image)
    ent = -sum((c / len(image)) * (c / len(image) and __import__("math").log2(c / len(image)) or 0) for c in counts.values())
    check(f"{name}: decoded body global entropy >= 7.9999 bits/byte (no plaintext claim)",
          ent >= 7.9999, f"{ent:.7f}")
    if name == "T-0058-23.cuw":
        # Complete non-overlapping 4-KiB window scan: no low-entropy/plaintext
        # island.  Supports opacity only, not any specific crypto transform.
        import math
        def went(w):
            n = len(w)
            return -sum((c / n) * math.log2(c / n) for c in Counter(w).values())
        wins = [image[i:i + 4096] for i in range(0, len(image) - 4095, 4096)]
        wmin = min(went(w) for w in wins)
        check("T-0058: minimum 4-KiB window entropy 7.93098 (no plaintext island)",
              7.9295 <= wmin <= 7.9325, f"{wmin:.5f} over {len(wins)} windows")
        printable = sum(1 for b in image[::97] if 0x20 <= b <= 0x7E) / len(image[::97])
        check("T-0058: printable/zero/FF fractions are random-like",
              abs(printable - 95 / 256) < 0.01
              and abs(image.count(0) / len(image) - 1 / 256) < 0.002
              and abs(image.count(0xFF) / len(image) - 1 / 256) < 0.002,
              f"printable {printable:.5f} vs {95/256:.5f}")
    rc, rchunks = scan_srec(payload_map[routine_member])
    check(f"{name}: routine member S-records all validate", rc["bad"] == 0)
    check(f"{name}: routine member decodes to exactly the routine slot",
          rchunks.get(ROUTINE_RANGE, b"") == chunks[ROUTINE_RANGE])
    check(f"{name}: routine member raw bytes pinned",
          sha256(payload_map[routine_member]) == ROUTINE_RAW_SHA)
    check(f"{name}: routine slot decoded sha pinned",
          sha256(chunks[ROUTINE_RANGE]) == ROUTINE_DECODED_SHA)
    if name == "T-0058-23.cuw":
        import math as _m
        rr = chunks[ROUTINE_RANGE]
        rent = -sum((c / len(rr)) * _m.log2(c / len(rr)) for c in Counter(rr).values())
        check("T-0058: routine range entropy 7.8798 over 1392 B",
              7.8785 <= rent <= 7.8810, f"{rent:.6f}")

check("routine member is byte-identical across all six packages",
      len({sha256(pm[fd["LogicalBlock101"]["DeltaEraseAndReproRoutineFileName"]])
           for fd, pm in ((frc_descriptors[n], frc_payloads[n]) for n in FRC_PACKAGES)}) == 1
      and sha256(next(iter(frc_payloads.values()))[next(iter(frc_descriptors.values()))["LogicalBlock101"]["DeltaEraseAndReproRoutineFileName"]]) == ROUTINE_RAW_SHA)
check("all decoded images share the same first 32 bytes",
      len({img[:32] for img in images.values()}) == 1
      and next(iter(images.values()))[:32].hex() == IMAGE_PREFIX32)
distinct = {sha256(img) for img in images.values()}
check("five distinct target images; T-0058/T-0060 share one target",
      len(distinct) == 5 and sha256(images["T-0058-23.cuw"]) == sha256(images["T-0060-23.cuw"]))

_t58_datx = frc_payloads["T-0058-23.cuw"][frc_descriptors["T-0058-23.cuw"]["LogicalBlock101"]["DeltaReproDataFileName"]]
check("T-0058: datx member raw identity (offset/length/sha)",
      next(m for m in parse_container((CORPUS / "T-0058-23.cuw").read_bytes())["format67_members"]
           if m["name"].endswith("-write.datx"))["payload_offset"] == 256387015
      and len(_t58_datx) == 9184
      and sha256(_t58_datx) == "f9bf53cd6157f9f426beae2c5037ff27a5bf7d73e8c64ccbe148f96e82818465")

print("\n== datx compact-delta representation invariants ==")
datx = {n: pm[frc_descriptors[n]["LogicalBlock101"]["DeltaReproDataFileName"]]
        for n, pm in frc_payloads.items()}
check("all datx lengths are 16-byte multiples", all(len(d) % 16 == 0 for d in datx.values()))
check("all six datx share exactly one leading 16-byte block",
      len({d[:16] for d in datx.values()}) == 1
      and next(iter(datx.values()))[:16].hex() == DATX_LEADING_BLOCK)


def blake8(b: bytes) -> bytes:
    return hashlib.blake2b(b, digest_size=8).digest()


interior_shared = 0
items = [data for _, data in sorted(datx.items())]
for i in range(len(items)):
    a = items[i]
    set_a = {blake8(a[o:o + 16]) for o in range(16, len(a) - 15, 16)}
    for j in range(i + 1, len(items)):
        b = items[j]
        interior_shared += sum(1 for o in range(16, len(b) - 15, 16) if blake8(b[o:o + 16]) in set_a)
check("excluding the shared leading block, cross-package datx block collisions are zero", interior_shared == 0,
      f"{interior_shared}")

print("\n== direct-update whole-image comparisons (corpus-internal chains) ==")
by_newcid = {frc_descriptors[n]["LogicalBlock101"]["NewCID"]: n for n in FRC_PACKAGES}
chains = []
for n in FRC_PACKAGES:
    src = frc_descriptors[n]["LogicalBlock101"]["01_TargetCalibration"]
    if src in by_newcid:
        chains.append((by_newcid[src], n))
check("two corpus-internal chains close (62->149, 61->150)",
      set(chains) == {("T-0062-23.cuw", "T-0149-24.cuw"), ("T-0061-23.cuw", "T-0150-24.cuw")})
for old, new in sorted(chains):
    a, b = images[old], images[new]
    same = sum(1 for x, y in zip(a, b) if x == y)
    frac = same / len(a)
    set_a = {blake8(a[o:o + 16]) for o in range(0, len(a) - 15, 16)}
    shared_blocks = sum(1 for o in range(0, len(b) - 15, 16) if blake8(b[o:o + 16]) in set_a)
    run = longest = 0
    for x, y in zip(a[32:], b[32:]):
        run = run + 1 if x == y else 0
        longest = max(longest, run)
    check(f"{old} -> {new}: byte identity is chance-level (per-version independence)",
          0.0035 < frac < 0.0043 and frac < 1.5 / 256, f"{frac:.6f} vs 1/256")
    check(f"{old} -> {new}: zero shared 16-byte blocks beyond the 32-byte prefix",
          shared_blocks == 2, f"{shared_blocks} (the prefix is 2 blocks)")
    check(f"{old} -> {new}: no identical run >= 8 beyond the prefix", longest < 8, f"longest {longest}")

print("\n== whole-repro contrast set (ReproMethod 01) ==")
contrast_descriptors: dict[str, dict] = {}
for name, (size, digest) in CONTRAST_PACKAGES.items():
    data = (CORPUS / name).read_bytes()
    check(f"{name}: pinned identity", len(data) == size and sha256(data) == digest)
    parsed = parse_container(data)
    check(f"{name}: container clean format 0x67", not parsed["errors"] and parsed["format_type"] == 0x67)
    end = parsed["first_member_end"]
    attach = data[end - parsed["payload_length"]:end]
    desc = parse_attach(attach)
    contrast_descriptors[name] = desc
    check(f"{name}: ReproMethod 01 / SecurityProperty2 98 / IsControlledBySCC 0",
          desc["LogicalBlock101"]["ReproMethod"] == "01"
          and desc["LogicalBlock101"]["SecurityProperty2"] == "98"
          and desc["KindOfCal"]["IsControlledBySCC"] == "0")
    check(f"{name}: no Delta sections (whole-repro only)",
          "DeltaReproData101" not in desc and "DeltaEraseAndReproRoutine101" not in desc)

print("\n== complete local CUW acquisition inventory ==")
EXPECTED_REFERENCE_IDENTITIES = {
    'T-0002-21 - 04A72.cuw': (2521231, '8329b19f4e02d6902bb1702b156a6890f578f87f83888c3a641e46ee1bc4847b'),
    'T-0003-21 - 04B42.cuw': (2547117, '1424b70028e3eb4ec35e8f52e5d6dc6d2f76766ac287fada7f112e83da63cdd9'),
    'T-0003-25.cuw': (7872007, 'ec52b1b673d9bf1c1497fc6f0ac2c5f7bfd8bf330907a2e9162c0c84eb9824b4'),
    'T-0004-21 - 04B91.cuw': (2573420, '626153b7ea6092c482d7588866f8970cb23bf531b86e10958766f8f8d96cebba'),
    'T-0005-25.cuw': (7872031, '3f72d67aa4da84aa02d4a9a3661ae458e1d2015c9fcba2f1e4a9961cb39f419e'),
    'T-0008-22.cuw': (35551267, 'df77121f29aa45a8ebc203f9bec22147ed2e62362c8d267380ef21637ff90630'),
    'T-0009-22.cuw': (5481006, 'a2cdb0667ae07822e5622569b8fbc9e552e51a94c616aff18d5fa66b29574018'),
    'T-0011-21 - 04C21.cuw': (2825257, 'e0525b4fe0224772a3dde68d16bf2fb7a808d6d937fa32a337db34d95f5ba61d'),
    'T-0012-21 - 04B82.cuw': (3939174, '6f88600c05ff90e05d55482caf41901b6a27e30c62d7fdf997c81ecc82f576be'),
    'T-0014-20 - 04B14.cuw': (2413081, '1615d3f4e463f7088ada0149e9c42d7238a831ab693c4b7b6d93cb6c9c14196b'),
    'T-0015-20.cuw': (9887355, 'a533dd59a4b73ab972d3cf4b6755c4dd7cb1811610df90c2ef9fff6d8edcfc3b'),
    'T-0022-20 - 04B33.cuw': (3891207, '579c898a34e27b4b25ac5d233a4102a12f6eadb3f18e4e3bd1c95cf50c46b908'),
    'T-0023-20 - 04B81.cuw': (3939040, '4a6d6616b0307b8f4b92d8a5b3eede1e5db43a884c781d6ff12777e991d57337'),
    'T-0034-18 - 04B04.cuw': (3720924, '34480b3d167f0834d622992973408958ace89cd2b1ceb2bfb78b1f9ef868f246'),
    'T-0035-22.cuw': (5725237, '9882b1b6dd6acda2d142a2825eda396b0a425e41c13f822b9a18e022d4c43e81'),
    'T-0036-18 - 04A61.cuw': (3856075, '24aa61d71891d433b986e7e8819ffd7d763bcfc670201966a0d3e395846c5828'),
    'T-0036-22.cuw': (5725230, '14521a416fccffe720d37afea8f07218ea031c27a5530fbcdd5415262d810b36'),
    'T-0037-18 - 04A71.cuw': (2521449, 'a2462044980eb02c5f5b1073fe5fb2610c432d77889e85cf8eaaa2b86f56f770'),
    'T-0051-26.cuw': (13045570, '536bf4c05e7c135445547574c4bb321d4521e413765be0c6c2ec42d13a1c0117'),
    'T-0058-23.cuw': (256400446, 'ac5015118d3c5541c62ac3b0626a2d676681b3c4dee2ce6cb84ad547d116fdd9'),
    'T-0060-23.cuw': (256399534, 'b3e4a7a951c74ef9985cf05f5151a36538e57bd84392da988d5f8102c652837f'),
    'T-0061-23.cuw': (256401572, '007a351fa0ac096af6c9c7c8085c6690c79abefea058e1fc438033ef3512bf94'),
    'T-0062-23.cuw': (257142135, '9971e3052d63dfe1fb262509ec59bcc8924db0082210117c63e9b01b73070e5b'),
    'T-0087-17.cuw': (5112447, 'd40cc0988f7310ce0417fba17e512ae915719b40fed9a98f829ca1c5639c3cbd'),
    'T-0149-24.cuw': (257894251, '70bea932f3ae641e0d9fab99419aeb59ac76b08adcfeca97b9278d59d15ad6a8'),
    'T-0150-24.cuw': (257646163, 'c28455c5b4ee6b48b4bf7b0fc51c6110969c6de9294bf488583e50727f91b5f1'),
}
EXPECTED_REFERENCE_NAMES = set(EXPECTED_REFERENCE_IDENTITIES)
reference_paths = sorted(CORPUS.glob("*.cuw"), key=lambda p: p.name)
check("local CUW inventory is exact 26-file pinned set",
      {p.name for p in reference_paths} == EXPECTED_REFERENCE_NAMES)
check("all 26 local CUW package identities are pinned",
      all((len(path.read_bytes()), sha256(path.read_bytes())) == EXPECTED_REFERENCE_IDENTITIES[path.name]
          for path in reference_paths))
reference_diag_ids: dict[str, str] = {
    name: desc.get("Node01", {}).get("DiagID", "")
    for name, desc in frc_descriptors.items()
}
reference_diag_ids.update({
    name: desc.get("Node01", {}).get("DiagID", "")
    for name, desc in contrast_descriptors.items()
})
for path in reference_paths:
    if path.name in reference_diag_ids:
        continue
    data = path.read_bytes()
    parsed = parse_container(data)
    end = parsed["first_member_end"]
    attach = data[end - parsed["payload_length"]:end]
    desc = parse_attach(attach)
    reference_diag_ids[path.name] = desc.get("Node01", {}).get("DiagID", "")
reference_diag_counts = Counter(reference_diag_ids.values())
EXPECTED_REFERENCE_DIAG_COUNTS = {
    "": 12, "0724": 1, "07500F": 1, "07506D": 1, "0792": 6, "07A1": 3, "07D2": 2
}
check("local CUW DiagID census exact", dict(sorted(reference_diag_counts.items())) == EXPECTED_REFERENCE_DIAG_COUNTS)
check("local CUW corpus has positive FRC/EPS controls but no category-435 07B0 package",
      reference_diag_counts["0792"] == 6
      and reference_diag_counts["07A1"] == 3
      and reference_diag_counts["07B0"] == 0)

print("\n== generated artifact self-check ==")
if ev:
    check("artifact schema/counts", ev["schema_version"] == 2
          and ev["corpus"]["frc_package_count"] == 6
          and ev["corpus"]["contrast_format67_package_count"] == 5)
    ref_inv = ev["reference_inventory"]
    check("artifact: complete local CUW acquisition inventory",
          ref_inv["package_count"] == 26
          and ref_inv["diag_id_counts"] == EXPECTED_REFERENCE_DIAG_COUNTS
          and {row["filename"] for row in ref_inv["packages"]} == EXPECTED_REFERENCE_NAMES)
    ref_by_name = {row["filename"]: row for row in ref_inv["packages"]}
    identity_ok = True
    for path in reference_paths:
        row = ref_by_name.get(path.name, {})
        expected_size, expected_sha = EXPECTED_REFERENCE_IDENTITIES[path.name]
        identity_ok = identity_ok and row.get("size") == expected_size and row.get("sha256") == expected_sha
        identity_ok = identity_ok and row.get("diag_id") == reference_diag_ids[path.name]
    check("artifact: every reference package identity and DiagID matches raw corpus", identity_ok)
    acq = ref_inv["category_435_acquisition"]
    check("artifact: category-435 07B0 acquisition gap with positive controls",
          acq["target_diag_id"] == "07B0"
          and acq["matching_packages"] == []
          and acq["positive_controls"] == {
              "front_recognition_camera_0792": 6, "power_steering_07A1": 3
          }
          and "does not prove Toyota/TIS has no such calibration package" in acq["boundary"])
    inv = ev["cross_package_invariants"]
    check("artifact: routine identity + routine-slot embedding",
          inv["routine_member_raw_identical_across_all"]
          and inv["routine_member_raw_sha256"] == ROUTINE_RAW_SHA
          and inv["routine_slot_in_whole_image_equals_routine_member"])
    distinct_images = {sha256(image): image for image in images.values()}
    check("raw images: exactly 32-byte common prefix across distinct targets",
          len(distinct_images) == 5
          and len({image[:32] for image in distinct_images.values()}) == 1
          and len({image[32] for image in distinct_images.values()}) == 5)
    check("artifact: image prefix/distinct count", inv["decoded_images_share_first_32_bytes"]
          and inv["first_32_bytes_hex"] == IMAGE_PREFIX32
          and inv["first_32_bytes_is_exactly_the_shared_prefix"]
          and inv["distinct_decoded_image_count"] == 5)
    check("artifact: datx invariants", inv["datx_sizes_are_16_byte_multiples"]
          and inv["datx_shared_single_leading_block"]
          and inv["datx_shared_leading_block_hex"] == DATX_LEADING_BLOCK
          and inv["datx_interior_cross_package_shared_blocks"] == 0)
    probe = next(x["entropy_probe"] for x in ev["packages"] if "entropy_probe" in x)
    check("artifact: T-0058 entropy probe pinned",
          probe["global_entropy_bits"] == 7.9999977
          and probe["min_window_entropy_bits"] == 7.93098
          and probe["window_count"] == 20864
          and probe["routine_range_entropy_bits"] == 7.879802)
    check("artifact: entropy wording bounded (no crypto-transform claim)",
          "does not distinguish any specific cryptographic transform"
          in ev["transform_boundary"]["entropy_support"])
    check("artifact: boundary wording pinned", ev["transform_boundary"]["datx_members"].startswith(
          "DeltaReproData payload; downloaded by the ReproStd writer with RequestDownload DFI 0x21")
          and "unknown" in ev["transform_boundary"]["xx_members"])
    check("artifact: member read path recorded as orchestration-only",
          "CDeltaReproArchiveCtrlr" in ev["transform_boundary"]["member_read_path"]
          and "no crypto or compression imports" in ev["transform_boundary"]["member_read_path"])
    cmp_rows = {(c["old_package"], c["new_package"]): c for c in ev["direct_update_comparisons"]}
    check("artifact: direct comparisons recorded", set(cmp_rows) == set(chains))
else:
    check("generated artifact present", False)

# ---------------------------------------------------------------- Part B
print("\n== modern GTS+ CUWPlus host anchors ==")
if not GTS.is_dir():
    print("[SKIP] REFERENCE/gtsplus_cuwplus unavailable (modern host anchors not checked)")
else:
    import pefile

    UNPACK = GTS / "unpack"

    def raw(fn: str, va: int, n: int) -> bytes:
        pe = pefile.PE(str(UNPACK / fn), fast_load=True)
        return pe.get_data(va - 0x10000000, n)

    MODERN_PINS = {
        "CUW.unpack.dll": "89f7e7d24f2ead1788b9713a030ba6fde90895ae0f584e104c71ec1dabbf9f70",
        "TCUWCalibrationFile.unpack.dll": "23832182d1fbcc5836c487e5a9c6ba98e497b0f778c2fc6d24f3b70847913366",
        "TCUWCanCommonPrepareWriter.unpack.dll": "9fd1f92196e096326787732145886465232334635271d25edca6b5ee88bc8629",
        "TCUWCanReproStdFlashWriter.unpack.dll": "207ee08c45a5bd377fba8fe8a468586c600d5c8d35d087ce73d2f96966f7bd6a",
        "TCUWCanReproStdPrepareWriter.unpack.dll": "585be216333f3e68c55eb25ce3171f91b1cf35d1922a275bfd3fa217240cfaa9",
        "TCUWP6CanReprostdFlashWriter.unpack.dll": "2d69d9aaf43f1518ec982db66ef10a01ba52e50e05b54c6fec3a7a7ad8c487ad",
    }
    for fn, digest in MODERN_PINS.items():
        check(f"{fn}: pinned unpacked-image identity", sha256((UNPACK / fn).read_bytes()) == digest)

    CUW_DLL = "CUW.unpack.dll"

    def cstr(fn: str, va: int) -> str:
        data = raw(fn, va, 96)
        return data.split(b"\0")[0].decode("ascii")

    # Descriptor parser: section-name -> area-object offset mapping (FUN_1000DD60
    # stores) and CLogicalBlockInfo ctor area offsets (parser - 0x1C).
    check("parser: ReproDatanxx/EraseAndReproRoutinenxx/Delta names at pinned VAs",
          cstr(CUW_DLL, 0x100793E0) == "ReproDatanxx"
          and cstr(CUW_DLL, 0x100793F0) == "EraseAndReproRoutinenxx"
          and cstr(CUW_DLL, 0x10079408) == "DeltaReproDatanxx"
          and cstr(CUW_DLL, 0x1007941C) == "DeltaEraseAndReproRoutinenxx"
          and cstr(CUW_DLL, 0x1007943C) == "CompressionReproDatanxx"
          and cstr(CUW_DLL, 0x10079454) == "CompressionEraseAndReproRoutinenxx"
          and cstr(CUW_DLL, 0x10079478) == "DeltaOrCompressionReproDatanxx")
    for va, off in ((0x1000F2E1, 0x24), (0x1000F32D, 0xCC), (0x1000F37B, 0x174),
                    (0x1000F3C9, 0x21C), (0x1000F417, 0x2C4), (0x1000F465, 0x36C)):
        expect = bytes([0x83, 0xC0, off]) if off < 0x80 else bytes([0x05]) + off.to_bytes(4, "little")
        check(f"parser: area +0x{off:X} store at 0x{va:X}", raw(CUW_DLL, va, len(expect)) == expect)
    check("parser: 0xA8-stride ReproDataSegment loop at 0x1000F56E",
          raw(CUW_DLL, 0x1000F56E, 5) == bytes.fromhex("0564050000"))
    ctor = raw("TCUWCalibrationFile.unpack.dll", 0x10001400, 0x80)
    for off in (0x8, 0xB0, 0x158, 0x200, 0x2A8, 0x350):
        lea = b"\x8d\x8e" + off.to_bytes(4, "little") if off > 0x80 else b"\x8d\x4e" + off.to_bytes(1, "little")
        check(f"CLogicalBlockInfo ctor: area object at +0x{off:X}", lea in ctor)

    # IsControlledBySCC semantics: stored at calibration+0x24 from [KindOfCal]
    # comparison; SCC set AND blank clear calls FUN_100115E0 (VehicleForNA/EUOT
    # parser).  IsControlledBySCC does NOT select RKS.
    check("parser: IsControlledBySCC stored at calibration+0x24 from KindOfCal",
          cstr(CUW_DLL, 0x1007934C) == "IsControlledBySCC"
          and cstr(CUW_DLL, 0x10079360) == "KindOfCal"
          and raw(CUW_DLL, 0x1000CF89, 1) == b"\x88"
          and raw(CUW_DLL, 0x1000CF89, 3) == bytes.fromhex("884724"))
    # cmp [edi+0x24],0 / je +0x0e / cmp [edi+0x25],0 / jne +0x0e... exact:
    # 80 7f 24 00 | 74 0e | 80 7f 25 00 | 75 08 | 56 | 8b cf | e8 c1 45 00 00
    scc_branch = raw(CUW_DLL, 0x1000D00B, 20)
    check("parser: SCC set AND IsBlankECU clear calls VehicleForNA/EUOT parser",
          scc_branch == bytes.fromhex("807f2400740e807f25007508568bcfe8c1450000"),
          scc_branch.hex())
    check("parser: FUN_100115E0 consumes VehicleForNA/VehicleForEUOT",
          cstr(CUW_DLL, 0x10079540) == "VehicleForNA" and cstr(CUW_DLL, 0x10079550) == "VehicleForEUOT")

    # ReproMethod enum: 07 = DeltaReproRoutinePackageDLType
    cal = "TCUWCalibrationFile.unpack.dll"
    check("CalibrationFile: DeltaReproRoutinePackageDLType string pinned",
          cstr(cal, 0x1000D5C4).startswith("DeltaReproRoutinePackageDLType"))
    check("CalibrationFile: Delta/Compression/Whole Phase6 strings pinned",
          cstr(cal, 0x1000D540).startswith("DeltaReproPhase6")
          and cstr(cal, 0x1000D460).startswith("CompressionReproPhase6"))
    # Method-code slot array at 0x10009100: nine embedded two-char ASCII
    # method codes, dword-aligned.  Classic six "01/05/07/08/09/0A", then
    # Phase6 Whole/Compression/Delta "00/02/03".
    slots = raw(cal, 0x10009100, 36)
    expected = (b"01\x00\x00" + b"05\x00\x00" + b"07\x00\x00"
                + b"08\x00\x00" + b"09\x00\x00" + b"0A\x00\x00"
                + b"00\x00\x00" + b"02\x00\x00" + b"03\x00\x00")
    check("CalibrationFile: ReproMethod slot array 01/05/07/08/09/0A + 00/02/03",
          slots == expected, slots.hex())

    # Modern ReproStd writer: RequestDownload grammar 34||DFI||44 and DFI switch
    FW_DLL = "TCUWCanReproStdFlashWriter.unpack.dll"
    check("writer: exports StartFlashWrite @0x100039D0",
          pefile.PE(str(UNPACK / FW_DLL)).get_data(0x39D0, 6).startswith(b"\x55\x8b\xec"))
    check("writer: RequestDownload stores SID 0x34 @0x1000288E",
          raw(FW_DLL, 0x1000288E, 8) == bytes.fromhex("c6840db0efffff34"))
    check("writer: RequestDownload stores 0x44 @0x10002898",
          raw(FW_DLL, 0x10002898, 8) == bytes.fromhex("c6840db2efffff44"))
    check("writer: expected response 0x74 @0x100028E7",
          raw(FW_DLL, 0x100028E7, 8) == bytes.fromhex("c6843d40cfffff74"))
    for va, dfi in ((0x100031E7, 0x01), (0x100031F0, 0x21), (0x100031F9, 0x11)):
        check(f"writer: DFI selector case -> 0x{dfi:02X} @0x{va:X}",
              raw(FW_DLL, va, 7) == bytes.fromhex("c685d8f7ffff") + bytes([dfi]))
    jt = b"".join(v.to_bytes(4, "little") for v in (0x100031E7, 0x100031E7, 0x100031F0, 0x100031F9))
    check("writer: DFI jump table maps 0/1->0x01, 2->0x21, 3->0x11",
          raw(FW_DLL, 0x10003410, 16) == jt)

    # P6 ReproStd names the DFI semantics by ReproMethod string comparison:
    # CompressionReproPhase6 -> 0x11, DeltaReproPhase6 -> 0x21, default/Whole
    # Phase6 -> 0x01.  This is Toyota host code naming 0x21 as the delta-data
    # DFI and 0x11 as the compression-data DFI; no ISO nibble semantics claimed.
    P6_DLL = "TCUWP6CanReprostdFlashWriter.unpack.dll"
    pe6 = pefile.PE(str(UNPACK / P6_DLL))
    imp6 = {}
    for entry in pe6.DIRECTORY_ENTRY_IMPORT:
        for imp in entry.imports:
            if imp.name and b"ReproMethod" in imp.name:
                imp6[imp.name.decode("ascii", "replace")] = imp.address
    comp_slot = next(v for k, v in imp6.items() if "CompressionReproPhase6" in k)
    delta_slot = next(v for k, v in imp6.items() if k.endswith("DeltaReproPhase6@CLogicalBlockInfo@@2PBDB"))
    check("P6 writer: imports mlptr Compression/DeltaReproPhase6 from CalibrationFile",
          hex(comp_slot).endswith("8108") and hex(delta_slot).endswith("8118"),
          f"comp@{comp_slot:#x} delta@{delta_slot:#x}")
    check("P6 writer: default DFI byte is 0x01 @0x10004043",
          raw(P6_DLL, 0x10004043, 7) == bytes.fromhex("c685a4f3ffff01"))
    check("P6 writer: CompressionReproPhase6 select -> DFI 0x11 @0x10004063",
          raw(P6_DLL, 0x10004063, 7) == bytes.fromhex("c685a4f3ffff11"))
    check("P6 writer: DeltaReproPhase6 select -> DFI 0x21 (cmovne) @0x10004086",
          raw(P6_DLL, 0x10004086, 10) == bytes.fromhex("84c0ba210000000f45ca"))

    # Recovered ReproMethod==2 (delta) worker sequence in the modern ReproStd
    # main worker 0x10001B40: packageDL routine area (+0x200) is downloaded
    # with tag 0 => DFI 0x01 and closed with StartRoutine RID 10 F5; the delta
    # data area (+0x158) is downloaded with tag 2 => DFI 0x21 and closed with
    # RID 10 F6.  Pre-data/post-data routine-control only - no erase/verify
    # semantics are claimed for the RIDs, and the host never executes the
    # 0x8F6C00 bytes itself.
    check("writer: delta routine area +0x200 selected @0x10002171",
          raw(FW_DLL, 0x10002171, 6) == bytes.fromhex("8db300020000"))
    check("writer: routine download tag 0 @0x10002186",
          raw(FW_DLL, 0x10002186, 2) == bytes.fromhex("6a00"))
    check("writer: delta data area +0x158 selected @0x100022A8",
          raw(FW_DLL, 0x100022A8, 6) == bytes.fromhex("8db358010000"))
    check("writer: delta data download tag 2 @0x100022B5",
          raw(FW_DLL, 0x100022B5, 2) == bytes.fromhex("6a02"))
    check("writer: StartRoutine SID word 31 01 @0x10002CA1",
          raw(FW_DLL, 0x10002CA1, 10) == bytes.fromhex("66c7843db0ebffff3101")
          and raw(FW_DLL, 0x10002CAD, 8) == bytes.fromhex("c6843db4ebffff44"))
    # RID selector block in builder 0x10002B60: little-endian dword writes
    # 0x4D => bytes F5 10 (10F5), 0x45 => F6 10 (10F6), 0x56 => 00 FF (FF00).
    check("writer: RID selector dwords encode 10F5/10F6/FF00",
          raw(FW_DLL, 0x10002BE9, 7) == bytes.fromhex("c78510c3ffff4d")
          and raw(FW_DLL, 0x10002C03, 7) == bytes.fromhex("c78510c3ffff45")
          and raw(FW_DLL, 0x10002C16, 7) == bytes.fromhex("c78510c3ffff56"))

    # CDeltaReproArchiveCtrlr is orchestration-only and the member read path is
    # raw + CRC-gated: the host never parses/transforms/decompresses/decrypts
    # the .datx payload (TMS-042 hard boundary).
    check("CUW: CDeltaReproArchiveCtrlr RTTI -> vtable 0x1007C918",
          struct.unpack_from("<I", raw(CUW_DLL, 0x1007C918, 4))[0] == 0x10066DC0
          and struct.unpack_from("<I", raw(CUW_DLL, 0x1007DDE4 + 12, 4))[0] == 0x1008A9A0
          and cstr(CUW_DLL, 0x1008A9A0 + 8) == ".?AVCDeltaReproArchiveCtrlr@@")
    check("CUW: global instance vtable store at 0x10030CA8",
          raw(CUW_DLL, 0x10030CA8, 10) == bytes.fromhex("c7050cca081018c90710"))
    check("CUW: deleting dtor 0x10066DC0 reinstalls the vtable",
          raw(CUW_DLL, 0x10066DC0, 12) == bytes.fromhex("558bec568bf1c70618c90710"))
    check("CUW: source-path + DeltaReproCalFile strings pinned",
          cstr(CUW_DLL, 0x1007C8F8).endswith("CDeltaReproArchiveCtrlr.cpp")
          and cstr(CUW_DLL, 0x1007B92C) == "DeltaReproCalFile")
    check("CUW: loader calls whole-file CRC32 gate",
          raw(CUW_DLL, 0x10031C0C, 5) == b"\xe8" + struct.pack("<i", 0x1002A3B0 - 0x10031C11))
    check("CUW: raw reader pushes fread chunk 0xFFF, 1 @0x1002BF83",
          raw(CUW_DLL, 0x1002BF83, 7) == bytes.fromhex("68ff0f00006a01"))
    check("CUW: Error FileCRC string pinned", cstr(CUW_DLL, 0x1007B86C) == "Error FileCRC")
    # CAES never touches the member path: its only callers are the INI
    # parameter decode and the SecurityUp seed-key helpers.
    for site, target in ((0x1001B9B2, 0x100155F0), (0x1005AC52, 0x100155F0), (0x1005AD02, 0x10015970)):
        check(f"CUW: CAES caller site {site:#x} -> {target:#x}",
              raw(CUW_DLL, site, 5) == b"\xe8" + struct.pack("<i", target - site - 5))
    # Writer-side negative: no crypto/compression imports on the payload path.
    crypto_pat = re.compile(r"(?i)crypt|bcrypt|zlib|liblz|deflat|inflate|sha\d|aes_|_aes|cipher")
    for fn in ("TCUWCalibrationFile.unpack.dll", FW_DLL):
        pe_w = pefile.PE(str(UNPACK / fn))
        names = [(i.name or b"").decode("ascii", "replace")
                 for e in pe_w.DIRECTORY_ENTRY_IMPORT for i in e.imports]
        hits = [n for n in names if crypto_pat.search(n)]
        check(f"{fn}: no crypto/compression imports on payload path", not hits, ",".join(hits[:3]))

    # JudgeReproGWNodeForP4AndP5: runtime gateway-node probe that selects the
    # RKS flow (returns 1 -> CollateSeedKeyForP5CentralGW family).
    CPW = "TCUWCanCommonPrepareWriter.unpack.dll"
    pe = pefile.PE(str(UNPACK / CPW))
    names = {(e.name or b"").decode("ascii", "replace"): e.address + 0x10000000
             for e in pe.DIRECTORY_ENTRY_EXPORT.symbols}
    judge = next((v for k, v in names.items() if "JudgeReproGWNodeForP4AndP5" in k), None)
    secu = next((v for k, v in names.items() if "CalcSeedKeyForSecurityUp" in k), None)
    check("common prepare: JudgeReproGWNodeForP4AndP5 exported @0x10001820", judge == 0x10001820)
    check("common prepare: CalcSeedKeyForSecurityUp exported @0x100014A0", secu == 0x100014A0)
    check("common prepare: gateway probe strings 000007505F/000007585F",
          cstr(CPW, 0x10003184) == "000007505F" and cstr(CPW, 0x10003190) == "000007585F")

    # RKS sink in CUW.dll: 27 21 (16-byte seed) -> 27 22 || token[256].
    check("CUW: RKS seed request 27 21 / expected 67 21 word stores",
          raw(CUW_DLL, 0x1001C102, 9) == bytes.fromhex("66c78555cfffff2721")
          and raw(CUW_DLL, 0x1001C12B, 9) == bytes.fromhex("66c785c5efffff6721"))
    check("CUW: RKS key request 27 22 / expected 67 22 word stores",
          raw(CUW_DLL, 0x1001C29B, 9) == bytes.fromhex("66c7858ddfffff2722")
          and raw(CUW_DLL, 0x1001C2D7, 9) == bytes.fromhex("66c7851dbfffff6722"))
    check("CUW: 27 22 request length is 0x107 (1+1+256+prefix)",
          raw(CUW_DLL, 0x1001C2C5, 10) == bytes.fromhex("c78580dfffff07010000"))
    check("CUW: token copy is rep movsd ecx=0x40 (256 bytes)",
          raw(CUW_DLL, 0x1001C5D4, 10) == bytes.fromhex("b9400000008b7d08f3a5"))

    # Route INIs (per-nibble 0x23+4n obfuscation).
    def decode_ini(path: Path) -> str:
        data = path.read_bytes()
        out = bytearray()
        for i in range(0, len(data) - 1, 2):
            hi = (data[i] - 0x23) // 4
            lo = (data[i + 1] - 0x23) // 4
            if not (0 <= hi <= 15 and 0 <= lo <= 15):
                raise ValueError("not a 0x23+4n nibble stream")
            out.append((hi << 4) | lo)
        return out.decode("ascii")

    ini = decode_ini(GTS / "Ini/P5-Unified04.ini")
    import csv as _csv
    import io as _io
    ini_rows = list(_csv.reader(_io.StringIO(ini)))
    cols = ini_rows[0]
    row = next(r for r in ini_rows[1:] if r and r[0] == "P5-Unified04")
    check("Ini: P5-Unified04 decodes with header + route row",
          "ParamFileKeySystemProtocolMicon" in cols and len(cols) == 87)
    rec = dict(zip(cols, row))
    check("Ini: P5-Unified04 selects Unified CID getter + ReproStd prepare/flash writers",
          rec["DLLFileNameForGetCID"] == "TCUWCanUnifiedCIDGetter.dll"
          and rec["DLLFileNameForPrepareWrite"] == "TCUWCanReproStdPrepareWriter.dll"
          and rec["DLLFileNameForFlashWrite"] == "TCUWCanReproStdFlashWriter.dll"
          and rec["PrepareRetryFlag"] == "0")
    check("Ini: P5-Unified04 gets CID/prepare/flash CAN IDs from package CAN-ID table",
          rec["GetCANIDFunctionNameForGetCID"] == "GetCanIDsFromCANIDTable"
          and rec["GetCANIDFunctionNameForPrepareWrite"] == "GetCanIDsFromCANIDTable"
          and rec["GetCANIDFunctionNameForFlashWrite"] == "GetCanIDsFromCANIDTable"
          and rec["CanIDForGetCID"] == ""
          and rec["CanIDForPrepareWrite"] == "")
    rks_ini = decode_ini(GTS / "Ini/RKS.ini")
    check("Ini: RKS.ini [ReproKeyRequest] fields",
          "[ReproKeyRequest]" in rks_ini and "SoftwareID=GTS" in rks_ini
          and "LicenseKey=" in rks_ini and "VehicleIdentificationNumber=" in rks_ini
          and "RequesterKind=" in rks_ini and "KeypairID=" in rks_ini)

    # V18 Unified CID acquisition has an explicit FRC/0x792 branch. Generic
    # ReadSoftwareID is DID F181, while the camera-special GetSWINForFCM
    # helper directly addresses 0x792->0x79A and reads DID 1FFF. F18C and
    # legacy 0105 are separate CID-reader paths. GetSWINForFCM is NOT F181.
    if V18_CUW.is_dir():
        cid = V18_CUW / "TCUWCanUnifiedCIDGetter.dll"
        uu = V18_CUW / "TCUWUnifiedUtils.dll"
        check("V18 CIDGetter identity", sha256(cid.read_bytes()) ==
              "af7110a183af9754cfc8163ebff9af5300ed7a3d28bcbff718480ac29c0ce056")
        check("V18 UnifiedUtils identity", sha256(uu.read_bytes()) ==
              "bc357c49d52911bd85e97b9c89b6dd29df1d967a0dfa43d657e3c851b2c1a130")

        def v18raw(path: Path, va: int, n: int) -> bytes:
            pe = pefile.PE(str(path), fast_load=True)
            return pe.get_data(va - pe.OPTIONAL_HEADER.ImageBase, n)

        def v18cstr(path: Path, va: int) -> str:
            return v18raw(path, va, 64).split(b"\0")[0].decode("ascii")

        check("V18 CIDGetter: legacy DID 0105 + 62 01 05",
              v18cstr(cid, 0x10004204) == "0105"
              and v18raw(cid, 0x1000124D, 5) == bytes.fromhex("6804420010")
              and bytes.fromhex("80bdc9edffff62") in v18raw(cid, 0x1000128E, 40)
              and bytes.fromhex("80bdcaedffff01") in v18raw(cid, 0x1000128E, 40)
              and bytes.fromhex("b8050000003885cbedffff") in v18raw(cid, 0x1000128E, 40))
        check("V18 CIDGetter: F18C + 62 F1 8C",
              v18cstr(cid, 0x1000420C) == "F18C"
              and v18raw(cid, 0x100013DD, 5) == bytes.fromhex("680c420010")
              and bytes.fromhex("80bdc9edffff62") in v18raw(cid, 0x1000141E, 40)
              and bytes.fromhex("80bdcaedfffff1") in v18raw(cid, 0x1000141E, 40)
              and bytes.fromhex("80bdcbedffff8c") in v18raw(cid, 0x1000141E, 40))
        check("V18 CIDGetter: global camera discriminator is 0792",
              v18cstr(cid, 0x10004294) == "0792"
              and v18raw(cid, 0x10003E90, 10) == bytes.fromhex("6894420010b9d8600010"))
        check("V18 CIDGetter: mode-2 0792 branch waits to 5000 ms then calls GetSWINForFCM",
              v18raw(cid, 0x10002E9B, 6) == bytes.fromhex("807e2402756a")
              and v18raw(cid, 0x10002EA1, 5) == bytes.fromhex("68d8600010")
              and v18raw(cid, 0x10002EBC, 5) == bytes.fromhex("3d88130000")
              and v18raw(cid, 0x10002EC3, 5) == bytes.fromhex("b988130000")
              and v18raw(cid, 0x10002EE9, 6) == bytes.fromhex("ff1578410010"))
        check("V18 UnifiedUtils: generic ReadSoftwareID is 22 F1 81 / 62 F1 81",
              bytes.fromhex("c68435dcefffff22") in v18raw(uu, 0x100010C8, 40)
              and bytes.fromhex("c68435ddeffffff1") in v18raw(uu, 0x100010C8, 40)
              and bytes.fromhex("c68435deefffff81") in v18raw(uu, 0x100010C8, 40)
              and bytes.fromhex("c68435a4dfffff62") in v18raw(uu, 0x100010F7, 40)
              and bytes.fromhex("c68435a5dffffff1") in v18raw(uu, 0x100010F7, 40)
              and bytes.fromhex("c68435a6dfffff81") in v18raw(uu, 0x100010F7, 40))
        check("V18 UnifiedUtils: GetSWINForFCM binds direct CAN 0x792 -> 0x79A",
              v18cstr(uu, 0x10005154) == "00000792"
              and v18cstr(uu, 0x10005148) == "0000079A"
              and v18raw(uu, 0x1000151F, 5) == bytes.fromhex("6854510010")
              and v18raw(uu, 0x1000152E, 5) == bytes.fromhex("6848510010"))
        check("V18 UnifiedUtils: GetSWINForFCM reads DID 1FFF, not F181",
              bytes.fromhex("c6843540caffff22") in v18raw(uu, 0x100015E3, 40)
              and bytes.fromhex("c6843541caffff1f") in v18raw(uu, 0x100015E3, 40)
              and bytes.fromhex("889c3542caffff") in v18raw(uu, 0x100015E3, 40)
              and bytes.fromhex("c68435b0eaffff62") in v18raw(uu, 0x10001613, 40)
              and bytes.fromhex("c68435b1eaffff1f") in v18raw(uu, 0x10001613, 40))
    else:
        print("[SKIP] V18 CUW binaries unavailable (FRC software-ID anchors not checked)")

print(f"\n{'='*40}\npassed={p} failed={f}")
raise SystemExit(1 if f else 0)
