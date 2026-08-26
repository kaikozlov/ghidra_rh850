#!/usr/bin/env python3
"""Falsify obvious/static SecOC-key hypotheses against retained 2023-Corolla evidence.

This is intentionally a negative/offline experiment. It reuses the repository's
verified Toyota classic-SecOC oracle and never transmits vehicle traffic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.toyota_secoc_oracle import load_capture, verify_key, verify_sync_sample  # noqa: E402

PUBLIC_ORACLE = REPO / "community/albinoelephant/public_route_secoc_oracle.ndjson"
LOCAL_ORACLE = REPO / "community/albinoelephant/can_oracle.ndjson"
CODEFLASH = REPO / "community/albinoelephant/normalized/8965H1202000_CodeFlash.bin"
RAW = REPO / "community/albinoelephant/raw-20260818/albinoelephant-corolla-2023.20260814-0023"
DEFAULT_OUTPUT = REPO / "data/generated/corolla_2023_albino_secoc_default_key_probe.json"

# Public example printed by pinned I-CAN-hack/secoc README at commit 4ce19cc3... .
# It is an example KEY_4 from the older RAV4-Prime/Sienna extraction family, not
# a secret recovered from the Albino Corolla.
LEGACY_PUBLIC_KEY4 = bytes.fromhex("c5fc900668d068ec39695d9a8885be2d")
LEGACY_SOURCE_COMMIT = "4ce19cc31ff560b697bcd59cc3db55711f50b7b3"
LEGACY_README_SHA256 = "3f40cddb47ff954cb4f2c30b2c2ea6764ae62f32d111a63ba1c4f05b3c08cb60"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def corpus_paths() -> list[Path]:
    return [CODEFLASH, *sorted(RAW.glob("dump_dataflash_*.bin")),
            *sorted(RAW.glob("dump_extended_codeflash_*.bin")),
            *sorted(RAW.glob("dump_global_ram_*.bin")),
            *sorted(RAW.glob("dump_local_ram_pe1_*.bin"))]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    public_sync, public_protected, public_summary = load_capture(PUBLIC_ORACLE)
    local_sync, local_protected, local_summary = load_capture(LOCAL_ORACLE)
    if not public_sync or not local_sync:
        raise SystemExit("both synchronization oracles must contain 0x00F")

    legacy_public = verify_key(LEGACY_PUBLIC_KEY4, public_sync, public_protected)
    legacy_local = verify_key(LEGACY_PUBLIC_KEY4, local_sync, local_protected)

    # Exhaust every 16-byte key with a period of <=2 bytes. Period-1 keys are a
    # subset, including all-zero and all-FF.
    periodic_hits_public: list[int] = []
    periodic_hits_local: list[int] = []
    for word in range(0x10000):
        key = word.to_bytes(2, "big") * 8
        if verify_sync_sample(key, public_sync[0]):
            periodic_hits_public.append(word)
        if verify_sync_sample(key, local_sync[0]):
            periodic_hits_local.append(word)

    # Search each unique raw 16-byte value once across all retained CPU-visible
    # H memory classes. For 64-KiB host DataFlash reads, only first 0x8000 is the
    # specified R7F701383 DataFlash array; the over-read half is excluded.
    seen: set[bytes] = set()
    file_rows = []
    hits_public = []
    hits_local = []
    for path in corpus_paths():
        raw = path.read_bytes()
        considered = raw[:0x8000] if path.name.startswith("dump_dataflash_") else raw
        new_unique = 0
        for off in range(max(0, len(considered) - 15)):
            key = considered[off:off + 16]
            if key in seen:
                continue
            seen.add(key)
            new_unique += 1
            if verify_sync_sample(key, public_sync[0]):
                hits_public.append({"path": rel(path), "offset": off, "key_sha256": sha256_bytes(key)})
            if verify_sync_sample(key, local_sync[0]):
                hits_local.append({"path": rel(path), "offset": off, "key_sha256": sha256_bytes(key)})
        file_rows.append({
            "path": rel(path),
            "source_size": len(raw),
            "considered_size": len(considered),
            "sha256": sha256_bytes(raw),
            "new_unique_16byte_windows": new_unique,
        })

    out = {
        "schema": "corolla-2023-albino-secoc-default-key-probe-v1",
        "title": "2023 Corolla SecOC obvious/default/static-key falsification",
        "oracles": {
            "public_route": {
                "path": rel(PUBLIC_ORACLE), "sha256": sha256_file(PUBLIC_ORACLE),
                "sync_samples": len(public_sync), "trip_values": sorted({x.trip for x in public_sync}),
                "first_sync_decoded": {"trip": public_sync[0].trip, "reset": public_sync[0].reset, "authenticator28": public_sync[0].authenticator},
                "protected_samples": len(public_protected), "summary": public_summary,
                "identity_boundary": "Contributor-supplied public route; no carFw/F181 join to exact H firmware.",
            },
            "local_tskm": {
                "path": rel(LOCAL_ORACLE), "sha256": sha256_file(LOCAL_ORACLE),
                "sync_samples": len(local_sync), "trip_values": sorted({x.trip for x in local_sync}),
                "first_sync_decoded": {"trip": local_sync[0].trip, "reset": local_sync[0].reset, "authenticator28": local_sync[0].authenticator},
                "protected_samples": len(local_protected), "summary": local_summary,
                "identity_boundary": "Same contributor TSKM investigation as the H dump corpus, but CAN capture and memory dump are separate jobs/runtime epochs.",
            },
        },
        "legacy_public_example_key4": {
            "source_repository": "I-CAN-hack/secoc",
            "source_commit": LEGACY_SOURCE_COMMIT,
            "source_readme_sha256": LEGACY_README_SHA256,
            "key_sha256": sha256_bytes(LEGACY_PUBLIC_KEY4),
            "public_route_verification": legacy_public,
            "local_tskm_verification": legacy_local,
            "conclusion": "The pinned public older-family KEY_4 example authenticates none of the retained Albino synchronization/protected samples.",
        },
        "low_complexity_key_family": {
            "construction": "every 16-byte key formed by repeating one big-endian u16 eight times",
            "candidate_count": 65536,
            "includes_all_repeated_single_byte_keys": True,
            "includes_all_zero": True,
            "includes_all_ff": True,
            "public_route_first_sync_hits": periodic_hits_public,
            "local_tskm_first_sync_hits": periodic_hits_local,
        },
        "retained_cpu_visible_raw_key_scan": {
            "files": file_rows,
            "unique_16byte_windows_tested": len(seen),
            "public_route_first_sync_hits": hits_public,
            "local_tskm_first_sync_hits": hits_local,
            "dataflash_boundary": "Only FF200000..FF207FFF (first 0x8000 bytes) of each 64-KiB host range is treated as R7F701383 physical DataFlash.",
        },
        "conclusions": {
            "classic_secoc_is_observed": True,
            "legacy_public_example_key4_disproved_for_retained_albino_oracles": not any((legacy_public["sync"]["matches"], legacy_local["sync"]["matches"])),
            "two_byte_periodic_default_key_family_disproved": not periodic_hits_public and not periodic_hits_local,
            "raw_static_key_absent_from_retained_cpu_visible_corpus_under_oracle_epoch_assumptions": not hits_public and not hits_local,
            "still_plausible": [
                "a Corolla/platform-specific pre-provisioned key not present as a raw CPU-visible 16-byte value in the retained corpus",
                "a vehicle-specific pre-provisioned key",
                "automatic provisioning or key update not exposed as a technician-visible replacement step",
                "an ICU-S slot-4 key or derivation that remains opaque to CPU-visible memory",
                "key changes between the retained CAN and memory-acquisition epochs",
            ],
            "service_boundary": "Absence of a technician-visible re-key step during ECU replacement does not establish absence of SecOC or establish a universal/default key.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
