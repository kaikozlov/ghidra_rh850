#!/usr/bin/env python3
"""Verify the pinned Tacoma VFOREST CUW corpus identities by live decoding."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CORPUS = REPO / "software/Techstream/cuw"
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


if not CORPUS.is_dir():
    print("[SKIP] local CUW corpus unavailable")
    raise SystemExit(77)

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
check("local reconstructed image identities match pinned identities",
      local_image_hashes == {key: (value[0], value[1]) for key, value in EXPECTED_IMAGES.items()})

print(f"\nResults: {p} passed, {f} failed")
raise SystemExit(1 if f else 0)
