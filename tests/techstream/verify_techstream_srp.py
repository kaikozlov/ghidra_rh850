#!/usr/bin/env python3
"""Verify strict UtilityNeo script/registry decoding and current source joins."""
from __future__ import annotations

import hashlib
import re
from collections import Counter
from collections.abc import Callable
from xml.etree import ElementTree

import pefile
from Crypto.Cipher import AES

from tools import REPO_ROOT
from tools.techstream.decode_srp import (
    SRP_AES_KEY,
    SRP_REGISTRY_SENTINEL,
    SRP_WRAPPER,
    SRPRegistration,
    decrypt_srp,
    decrypt_srp_bytes,
    decrypt_srp_registry,
    decrypt_srp_registry_bytes,
)

ROOT = REPO_ROOT / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/GTSPlus"
V18 = REPO_ROOT / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics/Techstream"
REGISTRATIONS = (
    (2382, "UE0302382", "EFI-39"),
    (2385, "UT0302385", "TVD-01"),
    (2387, "UE0102387", "ECD-43"),
    (2389, "UE0102389", "ECD-45"),
    (2390, "UE0102390", "ECD-46"),
    (2393, "UD0102393", "DCM-13"),
    (2395, "UC0202395", "CSP-03"),
    (2397, "UC0202397", "CSP-05"),
    (2399, "UF0202399", "FHV-03"),
    (2449, "UR0302449", "RCM-01"),
    (2450, "UD0502450", "DSC-03"),
    (2451, "UA0702451", "ALM-01"),
    (2460, "UM0402460", "MG-01"),
    (2492, "US0602492", "SAS-01"),
    (2614, "UD0102614", "DCM-33"),
    (2645, "UL0302645", "LAMP-02"),
    (2646, "UL0302646", "LAMP-03"),
    (2765, "UM0202765", "MM-37"),
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][raw_bytes] {name}" + (f" ({detail})" if detail else ""))


def rejects(name: str, decoder: Callable[[bytes], object], ciphertext: bytes) -> None:
    try:
        decoder(ciphertext)
    except ValueError:
        check(name, True)
    else:
        check(name, False)


def encrypt(plaintext: bytes, *, pad: bool = True) -> bytes:
    if pad:
        padding = AES.block_size - len(plaintext) % AES.block_size
        plaintext += bytes([padding]) * padding
    return AES.new(SRP_AES_KEY, AES.MODE_ECB).encrypt(plaintext)


sample = '<?xml version="1.0"?><UTILITY a="b">\r\n  <DATA> x &amp; y </DATA>tail</UTILITY>'
script = encrypt(SRP_WRAPPER + sample.encode("utf-16"))
check("script text, attributes and whitespace are returned without XML rewriting",
      decrypt_srp_bytes(script) == sample)
check("big-endian BOM remains supported",
      decrypt_srp_bytes(encrypt(SRP_WRAPPER + b"\xfe\xff" + sample.encode("utf-16-be"))) == sample)
registry_text = "2382,UE0302382,1,0\r\n" + SRP_REGISTRY_SENTINEL
registry_cipher = encrypt(registry_text.encode("ascii"))
registry = decrypt_srp_registry_bytes(registry_cipher)
check("typed registry retains all fields, sentinel and original ASCII text",
      registry.registrations == (SRPRegistration(2382, "UE0302382", 1, 0),)
      and registry.sentinel == SRPRegistration(0, "0", 0, 0) and registry.text == registry_text)
check("empty registry is represented by the sentinel rather than a registration",
      decrypt_srp_registry_bytes(encrypt(SRP_REGISTRY_SENTINEL.encode("ascii"))).registrations == ())
check("column3 decimal values and column4 one are retained, not inferred booleans",
      decrypt_srp_registry_bytes(encrypt(b"1,A,12,1\r\n0,0,0,0\r\n")).registrations
      == (SRPRegistration(1, "A", 12, 1),))
rejects("script decoder rejects the separate registry format", decrypt_srp_bytes, registry_cipher)
rejects("registry decoder rejects the separate wrapped UTF16 format", decrypt_srp_registry_bytes, script)
for decoder in (decrypt_srp_bytes, decrypt_srp_registry_bytes):
    prefix = decoder.__name__
    for name, ciphertext in (
        ("empty ciphertext", b""),
        ("partial block", script[:-1]),
        ("truncated aligned ciphertext", encrypt(b"x" * 16 + b"\x10" * 16, pad=False)[:-16]),
        ("zero padding", encrypt(b"\x00" * 16, pad=False)),
        ("padding count above one block", encrypt(b"\x11" * 16, pad=False)),
        ("mismatched tail bytes accepted by native clearing but not offline PKCS7",
         encrypt(b"x" * 14 + b"\x03\x02", pad=False)),
    ):
        rejects(f"{prefix}: rejects {name}", decoder, ciphertext)
for name, body in (
    ("wrong wrapper", b"nope" + sample.encode("utf-16")),
    ("missing BOM", SRP_WRAPPER + sample.encode("utf-16-le")),
    ("truncated UTF16 code unit", SRP_WRAPPER + b"\xff\xfeA"),
    ("unpaired UTF16 surrogate", SRP_WRAPPER + b"\xff\xfe\x00\xd8"),
):
    rejects(f"script rejects {name}", decrypt_srp_bytes, encrypt(body))
for name, body in (
    ("missing sentinel", b"1,A,1,0\r\n"),
    ("missing final CRLF", b"1,A,1,0\r\n0,0,0,0"),
    ("LF instead of CRLF", b"1,A,1,0\n0,0,0,0\r\n"),
    ("missing field", b"1,A,1\r\n0,0,0,0\r\n"),
    ("extra field", b"1,A,1,0,0\r\n0,0,0,0\r\n"),
    ("empty stem", b"1,,1,0\r\n0,0,0,0\r\n"),
    ("nondecimal column3", b"1,A,x,0\r\n0,0,0,0\r\n"),
    ("nonbit column4", b"1,A,1,2\r\n0,0,0,0\r\n"),
    ("non-ASCII", b"1,\xff,1,0\r\n0,0,0,0\r\n"),
    ("embedded NUL", b"1,A\x00B,1,0\r\n0,0,0,0\r\n"),
    ("data following sentinel", b"0,0,0,0\r\n1,A,1,0\r\n0,0,0,0\r\n"),
    ("nonexact sentinel", b"0,A,1,0\r\n0,0,0,0\r\n"),
):
    rejects(f"registry rejects {name}", decrypt_srp_registry_bytes, encrypt(body))

if not ROOT.is_dir():
    print("[SKIP] pinned GTS+ current tree is unavailable")
    raise SystemExit(1 if failed else 77)

files = sorted((ROOT / "CONF").glob("*.srp"))
check("pinned current tree contains exactly 18 SRP utility scripts", len(files) == 18, str(len(files)))
check("SRP AES key is the recovered current 32-byte value", len(SRP_AES_KEY) == 32)
check("SRP wrapper is the recovered four-byte marker", SRP_WRAPPER == b"H\x02H\x02")
list_path = ROOT / "bin/UtilityNeo.srplst"
check("current registry ciphertext identity is pinned",
      hashlib.sha256(list_path.read_bytes()).hexdigest()
      == "291cecc527fb9b8e7e60214920faeb7bb1eed57aa82d5cb1dd1638c9426125c4")
registry = decrypt_srp_registry(list_path)
check("all 18 registrations and both consumer columns are pinned in native order",
      registry.registrations == tuple(SRPRegistration(fid, stem, 1, 0) for fid, stem, _ in REGISTRATIONS))
check("current sentinel and source text are exact",
      registry.sentinel == SRPRegistration(0, "0", 0, 0)
      and registry.text == "".join(f"{fid},{stem},1,0\r\n" for fid, stem, _ in REGISTRATIONS)
      + SRP_REGISTRY_SENTINEL)
check("every registration joins exactly one current script; no scripts are dropped",
      {path.stem for path in files} == {row.script_stem for row in registry.registrations})

service_counts: Counter[int] = Counter()
node_counts: Counter[str] = Counter()
all_text = []
for fid, stem, funcid in REGISTRATIONS:
    path = ROOT / "CONF" / f"{stem}.srp"
    text = decrypt_srp(path)
    all_text.append(text)
    root = ElementTree.fromstring(text)
    check(f"{path.name}: numeric registration {fid} joins textual FUNCID {funcid}",
          root.tag == "UTILITY" and root.findtext("FUNCTION/FUNCID") == funcid)
    node_counts.update(node.tag for node in root.iter())
    for match in re.finditer(r"<FRAME>\$([0-9A-Fa-f]{2})", text):
        service_counts[int(match.group(1), 16)] += 1
    old = V18 / "CONF" / path.name
    if old.is_file():
        check(f"{path.name}: exact V18 payload compatibility", old.read_bytes() == path.read_bytes()
              and decrypt_srp(old) == text)
check("all 3900 nodes and 57 tag names survive script decoding",
      sum(node_counts.values()) == 3900 and len(node_counts) == 57, repr(node_counts))
expected = {
    0x10: 4, 0x11: 1, 0x14: 1, 0x21: 4, 0x22: 5, 0x2E: 1, 0x2F: 1,
    0x31: 8, 0x3B: 13, 0x50: 1, 0x51: 1, 0x54: 1, 0x61: 4, 0x62: 13,
    0x6E: 2, 0x6F: 1, 0x71: 12, 0x7B: 13, 0x7F: 86, 0xA8: 7, 0xE8: 7,
}
check("literal SRP FRAME service-byte census is exact", dict(service_counts) == expected, repr(dict(service_counts)))
for sid in (0x27, 0x34, 0x36, 0x37):
    check(f"SRP scripts contain no literal service SID 0x{sid:02X}", service_counts[sid] == 0)
check("decoded SRPs contain no SecurityAccess/auth-key vocabulary",
      all(token not in "\n".join(all_text).lower()
          for token in ("securityaccess", "seedkey", "serviceauthkey", "ecuauthkey")))

# Exact current native gates: no transfer of V18 native addresses/semantics.
for name, digest, pins in (
    ("IT3UtilityNeoNK.dll", "0ca847b5b5fd1aa21fb73054c4c7006eb7e8615608f2710774863c7fbb626167", (
        (0x452BC, SRP_AES_KEY + b"\x00"),
        (0x2690B, bytes.fromhex("f6c30f")),  # AES-block alignment
        (0x2696C, bytes.fromhex("e8cf020000")),  # independent block decrypt
        (0x269F2, bytes.fromhex("0fb64c3bff")),  # native final-byte count
        (0x269F7, bytes.fromhex("3bcf771c")),  # count <= whole buffer, not <= 16
        (0x26A08, bytes.fromhex("e8224a0000")),  # memset tail, not PKCS7 comparison
        (0x1F42, bytes.fromhex("83bfbc00000074")),  # region == 0x74
        (0x1F4B, bytes.fromhex("3de8030000")),  # unsigned ID >= 1000
        (0x1F5B, bytes.fromhex("0518fcffff")),  # subtract 1000
    )),
    ("eVbBroker.dll", "d1c9914b84396dfb3024145ea09362741fd2122cbc8f14da4d338bd2d8ea51bd", (
        (0x1CF9, bytes.fromhex("81fecd0a0000")),  # 2765
        (0x1D01, bytes.fromhex("83fa16")),  # protocol 0x16 exclusion
        (0x1D0D, bytes.fromhex("81feb50e0000")),  # 3765
        (0x1D15, bytes.fromhex("83fa16")),
    )),
):
    path = ROOT / "bin" / name
    check(f"{name}: current native identity", hashlib.sha256(path.read_bytes()).hexdigest() == digest)
    pe = pefile.PE(str(path))
    for rva, expected_bytes in pins:
        check(f"{name}: source gate RVA 0x{rva:x}", pe.get_data(rva, len(expected_bytes)) == expected_bytes)
    if name == "eVbBroker.dll":
        check("broker function-body identity is distinct from its whole-file identity",
              hashlib.sha256(pe.get_data(0x1490, 2844)).hexdigest()
              == "cd6c433b8379da3e46350f5ef9a833e388018de63482db6d39dc58475a1bcd63")
        compare_rvas = {
            2382: 0x1BE1, 3382: 0x1BEF, 2385: 0x1BFD, 3385: 0x1C09,
            2387: 0x1C15, 3387: 0x1C21, 2389: 0x1C2D, 3389: 0x1C39,
            2390: 0x1C45, 3390: 0x1C51, 2395: 0x1C5D, 3395: 0x1C69,
            2397: 0x1C75, 3397: 0x1C81, 2399: 0x1C89, 3399: 0x1C91,
            2393: 0x1C99, 3393: 0x1CA1, 2614: 0x1CA9, 3614: 0x1CB1,
            2460: 0x1CB9, 3460: 0x1CC1, 2492: 0x1CC9, 3492: 0x1CD1,
            2645: 0x1CD9, 3645: 0x1CE1, 2646: 0x1CE9, 3646: 0x1CF1,
            2765: 0x1CF9, 3765: 0x1D0D, 2449: 0x1D21, 2451: 0x1D29,
            3449: 0x1D31, 3451: 0x1D39,
        }
        for fid, _, _ in REGISTRATIONS:
            for alias in (fid, fid + 1000):
                endpoints = (alias - 1, alias + 1) if fid == 2450 else (alias,)
                check(f"broker FunctionID {alias} has exact current selector compares",
                      all(pe.get_data(compare_rvas[value], 6) == b"\x81\xfe" + value.to_bytes(4, "little")
                          for value in endpoints))
        check("broker uses inclusive base/+1000 ranges for registrations 2449..2451",
              pe.get_data(0x1D27, 2) == bytes.fromhex("7208")
              and pe.get_data(0x1D2F, 2) == bytes.fromhex("76d5")
              and pe.get_data(0x1D37, 2) == bytes.fromhex("7208")
              and pe.get_data(0x1D3F, 2) == bytes.fromhex("76c5"))
    pe.close()

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
