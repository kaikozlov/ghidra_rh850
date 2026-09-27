#!/usr/bin/env python3
"""Verify the 2023 Corolla FRC/Brake calibration-acquisition correlation."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import struct
import sys
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ARTIFACT = REPO / "data/generated/techstream_v18/corolla_2023_calibration_acquisition.json"
CAMPAIGNS = REPO / "data/external/toyota_corolla_2023_calibration_campaigns.json"
BUILDER = REPO / "tools/techstream/build_corolla_2023_calibration_acquisition.py"
CUW_CORPUS = REPO / "software/Techstream/cuw"
sys.path.insert(0, str(REPO / "tools/techstream"))

from cuw_attach import parse_attach_bytes

passed = failed = 0
oracle = "generated_self_check+independent_external_artifact"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}" + (f" ({detail})" if detail else ""))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def descriptor(path: Path) -> dict[str, dict[str, str]]:
    # Independent descriptor-only raw parser: no generated corpus trust and no
    # need to materialize a 250-MiB image just to inspect attach.att.
    with path.open("rb") as f:
        header = f.read(24)
        if len(header) != 24:
            raise ValueError(f"truncated CUW header: {path.name}")
        name_len = struct.unpack_from(">H", header, 22)[0]
        name = f.read(name_len)
        meta = f.read(8)
        payload_len, payload_crc = struct.unpack(">II", meta)
        payload = f.read(payload_len)
    if name != b"attach.att" or len(payload) != payload_len:
        raise ValueError(f"invalid first member: {path.name}")
    if zlib.crc32(payload) & 0xFFFFFFFF != payload_crc:
        raise ValueError(f"attach payload CRC drift: {path.name}")
    return parse_attach_bytes(payload)


spec = importlib.util.spec_from_file_location("corolla_2023_calibration_acquisition_builder", BUILDER)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
art = json.loads(ARTIFACT.read_text(encoding="utf-8"))
ext = json.loads(CAMPAIGNS.read_text(encoding="utf-8"))

check("artifact regenerates exactly", art == mod.build())
check(
    "curated public campaign source identity pinned",
    art["sources"]["data/external/toyota_corolla_2023_calibration_campaigns.json"]["sha256"] == sha256(CAMPAIGNS),
)
frc_ext = ext["campaigns"]["23TC01_front_recognition_camera"]
check("23TC01 official source ID/URL/hash pinned", frc_ext["official_source"] == {
    "provider": "NHTSA mirror of Toyota technical instructions",
    "document_id": "MC-10242522-9999",
    "url": "https://static.nhtsa.gov/odi/tsbs/2023/MC-10242522-9999.pdf",
    "sha256": "3c275694a83825a98304068dce8c4c42666aba7ef3e528be7666b32426492bea",
})
check("23TC01 published Corolla FRC transitions exact", {
    (x["current_calibration_id"], x["new_calibration_id"])
    for x in frc_ext["published_transitions"]
} == {
    ("8646F1204300", "8646F1204500"),
    ("8646F1204400", "8646F1204500"),
})

raw_expected = {
    "T-0058-23.cuw": (256400446, "ac5015118d3c5541c62ac3b0626a2d676681b3c4dee2ce6cb84ad547d116fdd9", "8646F1204300"),
    "T-0060-23.cuw": (256399534, "b3e4a7a951c74ef9985cf05f5151a36538e57bd84392da988d5f8102c652837f", "8646F1204400"),
}
for fn, (size, digest, source_cid) in raw_expected.items():
    p = CUW_CORPUS / fn
    check(f"{fn}: raw package identity", p.stat().st_size == size and sha256(p) == digest)
    d = descriptor(p)
    check(
        f"{fn}: raw descriptor is 2023 Corolla P5 FRC",
        d["Vehicle"]["VehicleName"] == "COROLLA Series"
        and d["VehicleForNA"]["ModelYear"] == "23"
        and d["Vehicle"]["ContactType"] == "P5-Unified"
        and d["Node01"]["DiagID"] == "0792"
        and d["Node01"]["RequiredSpecReproVer"] == "04"
        and d["LogicalBlock101"]["ReproMethod"] == "07",
    )
    check(
        f"{fn}: raw descriptor exactly matches published transition",
        d["LogicalBlock101"]["01_TargetCalibration"] == source_cid
        and d["LogicalBlock101"]["NewCID"] == "8646F1204500",
    )

frc = art["front_recognition_camera"]
check("exactly two local 23TC01 transition matches", frc["local_match_count"] == 2)
check("both source CUWs converge on same target image", frc["target_image_shared"] is True and frc["target_image_sha256"] == "04b07fb4a817eaa340a7e34bb9e3d2a367989403671cf4f9968ee7c3b25c8dd3")

brake_ext = ext["campaigns"]["24TC01_brake_epb"]
check("24TC01 official source ID/URL/hash pinned", brake_ext["official_source"] == {
    "provider": "NHTSA mirror of Toyota technical instructions",
    "document_id": "MC-11005140-0001",
    "url": "https://static.nhtsa.gov/odi/tsbs/2024/MC-11005140-0001.pdf",
    "sha256": "b178aebd991ce065aea43172680cf735c66d370a0bbc4889b0beb31418ad2151",
})
check("24TC01 exact applicability/system", brake_ext["applicability"] == ["Certain 2023 Model Corolla"] and brake_ext["system"] == "Brake/EPB")
check("24TC01 published Brake CID transitions exact", {
    (x["current_calibration_id"], x["new_calibration_id"])
    for x in brake_ext["published_transitions"]
} == {
    ("F152612A5100", "F152612A5400"),
    ("F152612A5200", "F152612A5400"),
    ("F152612A5300", "F152612A5400"),
})

# Independent raw-descriptor negative. Acquisition identity lives in attach.att;
# binary member bodies need not be scanned for accidental ciphertext/text hits.
brake_cids = {"F152612A5100", "F152612A5200", "F152612A5300", "F152612A5400"}
raw_paths = sorted(CUW_CORPUS.glob("*.cuw"), key=lambda p: p.name)
diag_07b0: list[str] = []
cid_hits: list[str] = []
for path in raw_paths:
    d = descriptor(path)
    if d.get("Node01", {}).get("DiagID") == "07B0":
        diag_07b0.append(path.name)
    values = {value for section in d.values() for value in section.values()}
    if brake_cids & values:
        cid_hits.append(path.name)
check("no raw local CUW descriptor has DiagID 07B0", diag_07b0 == [], repr(diag_07b0))
check("no raw local CUW descriptor contains published 24TC01 Brake CID", cid_hits == [], repr(cid_hits))

brake = art["brake_epb"]
check("artifact preserves Brake acquisition absence", brake["local_target_diag_id_count"] == 0 and brake["local_target_diag_id_matches"] == [] and brake["local_published_cid_matches"] == [] and brake["package_bytes_available"] is False)

print(f"\nRESULT: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
