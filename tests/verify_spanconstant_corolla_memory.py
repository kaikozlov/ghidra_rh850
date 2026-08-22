#!/usr/bin/env python3
"""Verify Span Corolla mutable-memory and extended-CodeFlash conclusions."""
from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.analyze_toyota_dataflash import analyze  # noqa: E402

SPAN = REPO / "community/spanconstant/raw-20260821/span-corolla-2025.20260821-1511"
ALBINO = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023"
DF = sorted(SPAN.glob("dump_dataflash_ff200000_ff210000_*.bin"))
EXT = SPAN / "dump_extended_codeflash_01000000_0100c000_20260821-151952.bin"
ALBINO_EXT = sorted(ALBINO.glob("dump_extended_codeflash_01000000_0100c000_*.bin"))
GRAM = SPAN / "dump_global_ram_feef8000_fef08000_20260821-151923.bin"
ALBINO_GRAM = sorted(ALBINO.glob("dump_global_ram_feef8000_fef08000_*.bin"))
LRAM = SPAN / "dump_local_ram_pe1_febe0000_fec00000_20260821-151834.bin"
LRAM_SELF = SPAN / "dump_local_ram_self_fede0000_fee00000_20260821-152418.bin"
ALBINO_LRAM = sorted(ALBINO.glob("dump_local_ram_pe1_febe0000_fec00000_*.bin"))
CODEFLASH = SPAN / "dump_codeflash_00000000_00200000_20260821-152033.bin"
TRACKED_DF = REPO / "data/generated/corolla_2025_span_dataflash_analysis.json"
ALBINO_DF = REPO / "data/generated/corolla_2023_albino_dataflash_analysis.json"


def check(label: str, condition: object) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[ok] {label}")


def diff(left: bytes, right: bytes) -> int:
    return sum(a != b for a, b in zip(left, right))


def pairwise(paths: list[Path], limit: int | None = None, start: int = 0) -> list[int]:
    blobs = [p.read_bytes() for p in paths]
    if limit is None:
        chunks = [blob[start:] for blob in blobs]
    else:
        chunks = [blob[start:start + limit] for blob in blobs]
    return [diff(a, b) for a, b in itertools.combinations(chunks, 2)]


print("== physical DataFlash boundary and repeatability ==")
check("three 64-KiB host-range DataFlash captures are retained", len(DF) == 3 and all(p.stat().st_size == 0x10000 for p in DF))
check("only the first 32 KiB are interpreted as R7F701383 physical DataFlash", json.loads((REPO / "data/p1me_product_memory.json").read_text())["products"]["R7F701383"]["dataflash_bytes"] == 0x8000)
check("physical-DataFlash pairwise differences are pinned", pairwise(DF, 0x8000) == [2860, 3017, 2934])
blobs32 = [p.read_bytes()[:0x8000] for p in DF]
check("28,430/32,768 physical byte positions are stable across all three reads", sum(len({blob[i] for blob in blobs32}) == 1 for i in range(0x8000)) == 28430)
check("upper nonphysical 32-KiB host-range half also varies and is not promoted to DataFlash semantics", pairwise(DF, 0x8000, 0x8000) == [3066, 2988, 3134])

tracked = json.loads(TRACKED_DF.read_text(encoding="utf-8"))
fresh = analyze(DF[0], physical_prefix_size=0x8000)
check("tracked Span DataFlash analysis regenerates from the first physical 32-KiB prefix", tracked == fresh)
check("analysis preserves the original 64-KiB source provenance", tracked["size"] == 0x8000 and tracked["source_size"] == 0x10000 and tracked["normalization"] == "physical-prefix-0x8000")

results = [analyze(path, physical_prefix_size=0x8000, rank_limit=1) for path in DF]
for index, result in enumerate(results):
    geom = result["reference_nvm_geometry"]
    objects = {row["object"]: row for row in result["triplicate_objects"]}
    check(f"read {index + 1}: 122-record geometry / 61 committed / 52 checkpoints repeats", geom["configured_physical_records"] == 122 and geom["committed_records"] == 61 and geom["checkpoint_committed_records"] == 52)
    check(f"read {index + 1}: exactly 50 reference-enabled checkpoint envelopes repeat", geom["reference_enabled_checkpoint_envelopes"] == 50)
    check(f"read {index + 1}: objects 0/2/5 each retain three valid consensus copies", all(objects[obj]["valid_copy_count"] == 3 and objects[obj]["valid_consensus"] for obj in (0, 2, 5)))
    check(f"read {index + 1}: object 15 remains invalid in all three copies", objects[15]["valid_copy_count"] == 0 and not objects[15]["valid_consensus"])
    check(f"read {index + 1}: owner-28 disabled envelopes remain slots 117/118", [row["storage_index"] for row in geom["reference_disabled_checkpoint_envelopes"]] == [117, 118])

objects0 = [{row["object"]: row for row in result["triplicate_objects"]} for result in results]
check("Span object-2 consensus content is stable across all three captures", len({row[2]["consensus_payload_sha256"] for row in objects0}) == 1)
check("objects 0 and 5 retain the same consensus payload hashes as albino", all(objects0[0][obj]["consensus_payload_sha256"] == json.loads(ALBINO_DF.read_text())["triplicate_objects"][obj]["consensus_payload_sha256"] for obj in (0, 5)))
check("Span object-2 payload differs from albino's mutable state", objects0[0][2]["consensus_payload_sha256"] != json.loads(ALBINO_DF.read_text())["triplicate_objects"][2]["consensus_payload_sha256"])
span_checkpoint = {row["storage_index"] for row in results[0]["reference_nvm_geometry"]["checkpoint_records"]}
albino_checkpoint = {row["storage_index"] for row in json.loads(ALBINO_DF.read_text())["reference_nvm_geometry"]["checkpoint_records"]}
check("Span adds exactly committed checkpoint slot 104 relative to the tracked albino read", span_checkpoint - albino_checkpoint == {104} and not (albino_checkpoint - span_checkpoint))

print("\n== extended CodeFlash ==")
ext_blob = EXT.read_bytes()
check("Span extended-CodeFlash capture is the expected 48 KiB", len(ext_blob) == 0xC000)
check("Span extended CodeFlash is byte-identical to all three albino reads", len(ALBINO_EXT) == 3 and all(ext_blob == path.read_bytes() for path in ALBINO_EXT))
check("extended-CodeFlash shared image has pinned SHA-256", __import__("hashlib").sha256(ext_blob).hexdigest() == "90cc7b3d88e0c8b7ef330160ecb792134f5fbf9b9d8219c80d038a5451a15cc7")

print("\n== GlobalRAM / LocalRAM runtime state ==")
gram = GRAM.read_bytes()
check("Span GlobalRAM capture is complete 64 KiB", len(gram) == 0x10000)
check("Span-vs-albino GlobalRAM differences are bounded near albino's own runtime churn", [diff(gram, p.read_bytes()) for p in ALBINO_GRAM] == [867, 854, 907])
lram = LRAM.read_bytes(); self_lram = LRAM_SELF.read_bytes()
check("Span PE1/self LocalRAM captures are complete 128-KiB aliases", len(lram) == len(self_lram) == 0x20000)
check("different-time Span PE1/self alias snapshots differ by 3678 bytes", diff(lram, self_lram) == 3678)
check("Span-vs-albino PE1 LocalRAM differences remain bounded runtime-state deltas", [diff(lram, p.read_bytes()) for p in ALBINO_LRAM] == [6205, 6793, 7010])

probes = {
    "secoc_key_slot_metadata": (0xFEBE6EC0, bytes.fromhex("00220000030000000000000000000000")),
    "master_key_slot": (0xFEBE6E60, bytes(16)),
    "factory_key_slot": (0xFEBF42E0, bytes(16)),
    "object15_ram_field": (0xFEBF02F8, bytes(16)),
    "object15_workbuf_1": (0xFEBF0C28, bytes(16)),
    "object15_workbuf_2": (0xFEBF0C48, bytes(16)),
    "object15_workbuf_3": (0xFEBF0C68, bytes(16)),
    "identity_mirror_1": (0xFEBFF980, b"8965H1213000\0\0\0\0"),
    "identity_mirror_2": (0xFEBFF9C0, b"8A3111213000\0\0\0\0"),
}
for name, (address, expected) in probes.items():
    offset = address - 0xFEBE0000
    check(f"{name} is stable across PE1/self aliases", lram[offset:offset + 16] == self_lram[offset:offset + 16] == expected)

codeflash = CODEFLASH.read_bytes()[:0x100000]
app_sa = codeflash[0x20840:0x20850]
check("application-SA root is mirrored once at LocalRAM +0x17B80 in both Span snapshots", lram.find(app_sa) == self_lram.find(app_sa) == 0x17B80 and lram.find(app_sa, 0x17B81) == -1 and self_lram.find(app_sa, 0x17B81) == -1)
check("same application-SA mirror position recurs in every albino PE1 snapshot", all(path.read_bytes().find(app_sa) == 0x17B80 for path in ALBINO_LRAM))
check("payload-build and boot-SA CodeFlash roots are not copied verbatim into retained Span non-CodeFlash captures", all(blob.find(root) == -1 for root in (codeflash[0xBFD8:0xBFE8], codeflash[0xBFE8:0xBFF8]) for blob in [ext_blob, gram, lram, self_lram, *[p.read_bytes() for p in DF]]))

print("\nSpan Corolla mutable-memory verification passed.")
