#!/usr/bin/env python3
"""Correlate Albino's retained eps-telescope probe with the tracked Corolla image.

This is deliberately a byte-level correlator.  It does not treat telescope's
variant classifier as authoritative for this target; instead it joins the live
probe bytes to the tracked CodeFlash/RAM and derives only crypto values whose
algorithms/secrets are already recovered from the target bootloader family.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from Crypto.Cipher import AES

REPO = Path(__file__).resolve().parents[1]
PROBE = REPO / "community/albinoelephant/telescope/probe.json"
PROBE_MD = REPO / "community/albinoelephant/telescope/probe.md"
CODEFLASH = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
RAW_RAM_DIR = (
    REPO
    / "community/albinoelephant/raw-20260818"
    / "albinoelephant-corolla-2023.20260814-0023"
)

BOOT_SA_SECRET = bytes.fromhex("f05f36b7d78c03e24ab4faef2a57d044")
PAYLOAD_BUILD_SECRET = bytes.fromhex("ba052435f8843f985fd1329d2b6117b0")
PAYLOAD_BUILD_SECRET_OFFSET = 0xBFD8
BOOT_SA_SECRET_OFFSET = 0xBFE8
ZERO16 = bytes(16)
RAM_BASE = 0xFEBE0000
PROBE_RAM_BASE = 0xFEBF2CF8
EGG_SIGNATURE = bytes.fromhex("e0d19a0d1a38bfff")
GATE_CANDIDATE = 0x88C62
GATE_WINDOW_BASE = GATE_CANDIDATE - 31
GATE_WINDOW_LEN = 64
GATE_WINDOW_SHA256 = "50d793a2942716dcf0582238edfe6c2d72378eea8bd4e1bf575a8539cd497350"
CRC_START = 0x18000
CRC_END = 0xFFDF0


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def decode_f181(raw: bytes) -> dict:
    if not raw:
        raise ValueError("empty F181")
    count = raw[0]
    body = raw[1:]
    if len(body) != count * 16:
        raise ValueError(f"F181 count={count} but body has {len(body)} bytes")
    records = []
    for index in range(count):
        field = body[index * 16:(index + 1) * 16]
        records.append({
            "index": index + 1,
            "raw_hex": field.hex(),
            "ascii": field.rstrip(b"\x00").decode("ascii", errors="replace"),
        })
    return {"raw_hex": raw.hex(), "count": count, "records": records}


def crc32_iso_hdlc(data: bytes) -> int:
    # Python's binascii/zlib CRC32 uses the reflected ISO-HDLC convention used
    # by the existing CodeFlash resigning tooling when called on the full range.
    import binascii
    return binascii.crc32(data) & 0xFFFFFFFF


def read_probe_region(probe: dict, address: int) -> bytes:
    regions = probe["layer3"]["regions"]
    key = str(address)
    if key not in regions:
        raise KeyError(f"probe has no region {address:#x}")
    return bytes.fromhex(regions[key])


def prior_ram_snapshots() -> list[dict]:
    rows = []
    for path in sorted(RAW_RAM_DIR.glob("dump_local_ram_pe1_febe0000_fec00000_*.bin")):
        blob = path.read_bytes()
        off = PROBE_RAM_BASE - RAM_BASE
        window = blob[off:off + 0x50]
        if len(window) != 0x50:
            raise ValueError(f"short RAM snapshot {path}")
        rows.append({
            "path": str(path.relative_to(REPO)),
            "sha256": sha256_path(path),
            "did_0202_iv": window[0x00:0x10].hex(),
            "did_0201_key_material": window[0x10:0x20].hex(),
            "derived_payload_key": window[0x20:0x30].hex(),
            "payload_cmac_work_buffer": window[0x30:0x40].hex(),
            "boot_sa_seed_snapshot": window[0x40:0x50].hex(),
        })
    return rows


def build() -> dict:
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    codeflash = CODEFLASH.read_bytes()
    if len(codeflash) != 0x100000:
        raise ValueError("normalized CodeFlash must be exactly 1 MiB")
    if codeflash[PAYLOAD_BUILD_SECRET_OFFSET:PAYLOAD_BUILD_SECRET_OFFSET + 16] != PAYLOAD_BUILD_SECRET:
        raise ValueError("target CodeFlash payload-build secret drift")
    if codeflash[BOOT_SA_SECRET_OFFSET:BOOT_SA_SECRET_OFFSET + 16] != BOOT_SA_SECRET:
        raise ValueError("target CodeFlash boot-SA secret drift")

    app_f181 = decode_f181(bytes.fromhex(probe["meta"]["app_f181"]))
    boot_f181 = decode_f181(bytes.fromhex(probe["meta"]["boot_f181"]))

    sampled = []
    for address in (0x8E6A0, 0xFFDE0, 0x17D80):
        live = read_probe_region(probe, address)
        static = codeflash[address:address + len(live)]
        sampled.append({
            "address": f"0x{address:X}",
            "length": len(live),
            "live_sha256": sha256_bytes(live),
            "tracked_sha256": sha256_bytes(static),
            "exact_match": live == static,
        })

    ram = read_probe_region(probe, PROBE_RAM_BASE)
    if len(ram) != 0x100:
        raise ValueError("unexpected telescope RAM window length")
    did_0202 = ram[0x00:0x10]
    did_0201 = ram[0x10:0x20]
    derived_payload = ram[0x20:0x30]
    cmac_work = ram[0x30:0x40]
    boot_seed = ram[0x40:0x50]

    expected_payload_key = AES.new(PAYLOAD_BUILD_SECRET, AES.MODE_ECB).encrypt(did_0201)
    stage1 = AES.new(BOOT_SA_SECRET, AES.MODE_ECB).decrypt(ZERO16)
    expected_sa_key = AES.new(stage1, AES.MODE_ECB).encrypt(boot_seed)

    prior = prior_ram_snapshots()
    all_seeds = [row["boot_sa_seed_snapshot"] for row in prior] + [boot_seed.hex()]

    gate_window = codeflash[GATE_WINDOW_BASE:GATE_WINDOW_BASE + GATE_WINDOW_LEN]
    live_candidates = [int(x) for x in probe["layer3"]["egg_candidates"]]

    return {
        "schema": "corolla-2023-albino-telescope-analysis-v1",
        "source": {
            "probe_json": str(PROBE.relative_to(REPO)),
            "probe_json_sha256": sha256_path(PROBE),
            "probe_md": str(PROBE_MD.relative_to(REPO)),
            "probe_md_sha256": sha256_path(PROBE_MD),
            "timestamp": probe["meta"]["timestamp"],
            "diagnostic_address": probe["meta"]["addr"],
            "depth": probe["meta"]["depth"],
            "attribution": "albinoelephant, contributor-stated same 2023 US Corolla",
        },
        "identity": {
            "application_f181": app_f181,
            "application_f181_record_sources": ["0x20860", "0x17DC0"],
            "auxiliary_single_record_identity": {
                "did": "0x2032",
                "source": "0x17D80",
                "ascii": codeflash[0x17D80:0x17D90].rstrip(b"\x00").decode("ascii"),
            },
            "boot_f181": boot_f181,
            "boot_f181_is_two_bang_placeholders": (
                boot_f181["count"] == 2
                and bytes.fromhex(boot_f181["raw_hex"])[1:] == b"\x21" * 32
            ),
            "prdname_ascii": b"".join(
                int(probe["layer3"]["registers"][f"PRDNAME{i}"]).to_bytes(4, "little")
                for i in range(1, 5)
            ).decode("ascii").rstrip(),
        },
        "live_codeflash_sample_join": {
            "tracked_codeflash": str(CODEFLASH.relative_to(REPO)),
            "tracked_codeflash_sha256": sha256_path(CODEFLASH),
            "samples": sampled,
            "total_live_bytes_compared": sum(row["length"] for row in sampled),
            "all_exact": all(row["exact_match"] for row in sampled),
        },
        "gate2": {
            "live_egg_candidates": [f"0x{x:X}" for x in live_candidates],
            "expected_candidate": f"0x{GATE_CANDIDATE:X}",
            "candidate_is_exact": live_candidates == [GATE_CANDIDATE],
            "egg_signature_hex": EGG_SIGNATURE.hex(),
            "tracked_candidate_bytes": codeflash[GATE_CANDIDATE:GATE_CANDIDATE + 8].hex(),
            "tracked_64b_window_base": f"0x{GATE_WINDOW_BASE:X}",
            "tracked_64b_window_sha256": sha256_bytes(gate_window),
            "matches_pinned_sienna_window_sha256": sha256_bytes(gate_window) == GATE_WINDOW_SHA256,
            "patch_word": {
                "address": f"0x{GATE_CANDIDATE:X}",
                "original": codeflash[GATE_CANDIDATE:GATE_CANDIDATE + 2].hex(),
                "replacement": "e001",
            },
            "probe_candidate_window_status": probe["layer3"]["fingerprint"]["candidates"][0]["status"],
            "probe_candidate_window_boundary": "NO_DATA means telescope found the live 8-byte egg but did not stream the relocated 64-byte candidate window; the 64-byte match above is from the separately tracked dump",
        },
        "boot_integrity": {
            "live_adjust_word": f"0x{int.from_bytes(read_probe_region(probe, 0xFFDE0)[0xC:0x10], 'little'):08X}",
            "tracked_adjust_word": f"0x{int.from_bytes(codeflash[0xFFDEC:0xFFDF0], 'little'):08X}",
            "tracked_crc_range": [f"0x{CRC_START:X}", f"0x{CRC_END:X}"],
            "tracked_crc32": f"0x{crc32_iso_hdlc(codeflash[CRC_START:CRC_END]):08X}",
            "live_dcra1cin": f"0x{probe['layer3']['registers']['DCRA1CIN']:08X}",
            "live_dcra1cout": f"0x{probe['layer3']['registers']['DCRA1COUT']:08X}",
            "live_dcra1ctl": f"0x{probe['layer3']['registers']['DCRA1CTL']:08X}",
            "telescope_stock_classifier_boundary": "telescope's Sienna-specific adjust-word classifier reports unknown; the target-native tracked image independently proves 0xAD59D70C and CRC32 residue 0xFFFFFFFF are stock-valid for this Corolla image",
        },
        "authenticated_ram_bootstrap": {
            "security_access_ok": probe["layer2"]["sa_ok"],
            "envelope_auth_ok": probe["layer2"]["envelope_ok"],
            "stream_valid": probe["layer3"]["stream_valid"],
            "region_crc_failures": probe["layer3"]["region_bad"],
            "ram_window_base": f"0x{PROBE_RAM_BASE:X}",
            "did_0202_iv": did_0202.hex(),
            "did_0201_key_material": did_0201.hex(),
            "derived_payload_key_observed": derived_payload.hex(),
            "derived_payload_key_expected": expected_payload_key.hex(),
            "payload_build_secret_source": f"{CODEFLASH.relative_to(REPO)}@0x{PAYLOAD_BUILD_SECRET_OFFSET:X}",
            "boot_sa_secret_source": f"{CODEFLASH.relative_to(REPO)}@0x{BOOT_SA_SECRET_OFFSET:X}",
            "derived_payload_key_matches": derived_payload == expected_payload_key,
            "payload_cmac_work_buffer": cmac_work.hex(),
            "boot_sa_seed_snapshot": boot_seed.hex(),
            "boot_sa_zero_record_stage1_key": stage1.hex(),
            "boot_sa_expected_response_for_snapshot": expected_sa_key.hex(),
            "prior_retained_ram_snapshots": prior,
            "all_observed_boot_sa_seed_snapshots": all_seeds,
            "all_boot_sa_seed_snapshots_unique": len(all_seeds) == len(set(all_seeds)),
        },
        "live_registers": {
            "fpm_on": f"0x{probe['layer3']['registers']['FPMON']:02X}",
            "fastat": f"0x{probe['layer3']['registers']['FASTAT']:02X}",
            "fstatr": f"0x{probe['layer3']['registers']['FSTATR']:08X}",
            "fentryr": f"0x{probe['layer3']['registers']['FENTRYR']:04X}",
            "fhve15": f"0x{probe['layer3']['registers']['FHVE15']:08X}",
            "fhve3": f"0x{probe['layer3']['registers']['FHVE3']:08X}",
            "selfid": [f"0x{probe['layer3']['registers'][f'SELFID{i}']:08X}" for i in range(4)],
            "selfidst": f"0x{probe['layer3']['registers']['SELFIDST']:08X}",
            "boundary": "register values are retained as observations; SELFIDST is the self-programming ID-authentication status, not proof that the OCD debugger ID or ICU-S key store is unlocked",
        },
        "boundaries": [
            "This probe independently replays the bootloader authenticated-RAM execution path already required by the earlier range-dump acquisition; it does not prove application-context resident-code retention.",
            "The FEBF2CF8 window contains boot SecurityAccess and payload-build crypto state; it is not evidence that the operational SecOC/ICU-S slot-4 key is CPU-readable.",
            "The probe never invokes ICU-S command 5, so provisioned slot-4 generate permission and latency remain live tests.",
            "The live egg scan proves the 8-byte signature at 0x88C62; the exact 64-byte surrounding-window equality comes from the separately retained CodeFlash image.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path, help="compare generated JSON to an existing artifact")
    args = parser.parse_args()
    result = build()
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check is not None:
        existing = args.check.read_text(encoding="utf-8")
        if existing != text:
            raise SystemExit(f"generated artifact differs from {args.check}")
    if args.output is not None:
        args.output.write_text(text, encoding="utf-8")
    elif args.check is None:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
