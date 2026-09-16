#!/usr/bin/env python3
"""Deterministic 0x08A signer-continuity artifact for the 2026 Camry.

Answers one bounded question from OQ-054: does the authenticated Bus-4 `0x08A`
publication/security envelope continue when the lateral request itself is zero?

Primary evidence is the retained 2026-08-26 stationary NRTD->READY capture
(`camry_ready_gear_20260826.json.gz`, bus 1), which aggregates the secured
chassis family on the pre-repin development plane. With the vehicle
stationary and `B21` (Target Lateral ID) equal to zero in every frame, the
artifact records whether the FV4 freshness still tracks the live `0x00F`
epoch, whether B26 still advances +1 mod 64, and whether the MAC28 stays
frame-unique — the structural signature of an always-on authenticated
publication. This does not locate the CMAC engine.

The two relay-correct drives supply the active-request contrast: their ID11
intervals carry `B21 == 11` (LTA/LCA) while the stationary capture carries
`B21 == 0`. The secured publication's cadence/freshness statistics are compared
between the zero-request and active-request regimes.

Grades: observed structural continuity is `observed`. The later repin/source result
places the protected publisher inside the FRC ECU/assembly boundary; the exact
FRC-internal CMAC engine, key slot and freshness owner remain open.
"""
from __future__ import annotations

import bisect
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
READY = REPO / "targets/camry-2026/raw-20260826/camry_ready_gear_20260826.json.gz"
DRIVES = {
    "drive_a": REPO / "targets/camry-2026/raw-20260827/camry_relay_route_can_20260827.ndjson.gz",
    "drive_b": REPO / "targets/camry-2026/raw-20260827/camry_relay_lta_confirm_route_can_20260827.ndjson.gz",
}
DEFAULT_OUT = REPO / "data/generated/camry_2026_08a_signer_continuity.json"
REQUEST_PLANE = REPO / "data/generated/camry_2026_longitudinal_request_plane.json"


def _sync_epoch(dat: bytes) -> tuple[int, int]:
    return ((dat[0] << 8) | dat[1], (dat[2] << 12) | (dat[3] << 4) | (dat[4] >> 4))


def analyze_ready() -> dict:
    with gzip.open(READY, "rt") as f:
        doc = json.load(f)
    frames = [fr for fr in doc["frames"] if fr["bus"] == 1]
    a8 = [fr for fr in frames if fr["addr"] == 0x8A and fr["len"] == 32]
    f00f = [fr for fr in frames if fr["addr"] == 0x00F and fr["len"] == 8]
    for fr in a8 + f00f:
        fr["data"] = bytes.fromhex(fr["data"])

    b21 = Counter(fr["data"][21] for fr in a8)
    sync = [(*_sync_epoch(fr["data"]), fr["t"]) for fr in f00f]
    sync_times = [s[2] for s in sync]
    sync_resets = [s[1] for s in sync]

    agree = total = 0
    for fr in a8:
        i = bisect.bisect_right(sync_times, fr["t"]) - 1
        if i < 0:
            continue
        total += 1
        if (fr["data"][28] >> 4) & 0x3 == sync_resets[i] & 0x3:
            agree += 1

    b26 = [fr["data"][26] & 0x3F for fr in a8]
    plus1 = sum(1 for i in range(1, len(b26)) if (b26[i] - b26[i - 1]) & 0x3F == 1)
    last4 = Counter(fr["data"][-4:] for fr in a8)
    fv4 = Counter(fr["data"][28] >> 4 for fr in a8)

    return {
        "source": str(READY.relative_to(REPO)),
        "sha256": hashlib.sha256(READY.read_bytes()).hexdigest(),
        "capture_name": doc.get("capture", ""),
        "duration_s": doc.get("duration_s"),
        "stationary": True,
        "b21_census": {str(k): v for k, v in sorted(b21.items())},
        "a8_frames": len(a8),
        "f00f_frames": len(f00f),
        "f00f_trip_values": sorted({s[0] for s in sync}),
        "f00f_reset_span": [min(s[1] for s in sync), max(s[1] for s in sync)],
        "fv4_census": {str(k): v for k, v in sorted(fv4.items())},
        "fv4_reset_low2_agreement": {
            "agree": agree,
            "total": total,
            "fraction": agree / total if total else 0.0,
        },
        "b26_plus1_mod64_fraction": plus1 / (len(b26) - 1) if len(b26) > 1 else 0.0,
        "mac28_last4_unique_fraction": len(last4) / len(a8) if a8 else 0.0,
    }


def analyze_drive(path: Path) -> dict:
    # rows are [src, ts, bus, addr, hexdata]
    a8 = []
    with gzip.open(path, "rt") as f:
        for line in f:
            row = json.loads(line)
            if len(row) >= 5 and row[3] == 138 and row[2] == 0:
                dat = bytes.fromhex(row[4])
                if len(dat) == 32:
                    a8.append((row[1], dat))
    b21 = Counter(dat[21] for _, dat in a8)
    b26 = [dat[26] & 0x3F for _, dat in a8]
    plus1 = sum(1 for i in range(1, len(b26)) if (b26[i] - b26[i - 1]) & 0x3F == 1)
    last4 = Counter(dat[-4:] for _, dat in a8)
    return {
        "source": str(path.relative_to(REPO)),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "a8_bus0_frames": len(a8),
        "b21_census": {str(k): v for k, v in sorted(b21.items())},
        "b26_plus1_mod64_fraction": plus1 / (len(b26) - 1) if len(b26) > 1 else 0.0,
        "mac28_last4_unique_fraction": len(last4) / len(a8) if a8 else 0.0,
    }


def build() -> dict:
    ready = analyze_ready()
    drives = {name: analyze_drive(path) for name, path in DRIVES.items()}
    request_plane = json.loads(REQUEST_PLANE.read_text())
    repin = request_plane["topology"]
    if repin["0x08A"] != "native upstream Panda bus2 -> chassis bus0 on Toyota Bus 4":
        raise RuntimeError("0x08A repin direction drift")
    if repin["0x081"] != "native Brake/chassis Panda bus0 -> upstream bus2 on Toyota Bus 4":
        raise RuntimeError("0x081 repin direction drift")
    return {
        "schema": "camry-2026-08a-signer-continuity-v2",
        "question": (
            "Does the authenticated Bus-4 0x08A publication continue at zero lateral "
            "request, and what remains open after the repin/source experiment places its "
            "protected publisher inside the FRC assembly?"
        ),
        "zero_request_result": {
            "regime": "stationary READY, B21=0 (No Request) in every retained frame",
            "signing_continues": (
                ready["a8_frames"] > 0
                and ready["fv4_reset_low2_agreement"]["fraction"] >= 0.98
                and ready["b26_plus1_mod64_fraction"] >= 0.99
                and ready["mac28_last4_unique_fraction"] >= 0.98
            ),
            "interpretation": (
                "The secured 0x08A publication continues at zero lateral request: "
                "B21=0 in 100% of stationary frames while FV4 reset-low2 tracks the "
                "live 0x00F epoch, B26 advances +1 mod 64, and MAC28 stays frame-unique. "
                "The authenticated publication/security pipeline is therefore always-on "
                "with respect to the request state; this does not locate the CMAC engine."
            ),
            "boundary": (
                "Structural security-envelope continuity alone does not identify a CMAC engine, "
                "but the repin direction result does identify the secured publisher boundary: "
                "0x08A is native on the FRC-side endpoint before the accessible relay split. "
                "The unresolved identity is therefore which chip/HSM inside the FRC assembly "
                "owns the key, freshness and MAC operation."
            ),
        },
        "active_request_contrast": {
            name: {
                "b21_census": d["b21_census"],
                "b26_plus1_mod64_fraction": d["b26_plus1_mod64_fraction"],
                "mac28_last4_unique_fraction": d["mac28_last4_unique_fraction"],
            }
            for name, d in drives.items()
        },
        "signer_identity": {
            "grade": "frc-assembly-boundary-observed/internal-engine-open",
            "verdict": (
                "The protected 0x08A publisher is inside the FRC ECU/assembly diagnostic "
                "boundary: it is native on the FRC/camera-side endpoint of the intercepted "
                "Toyota Bus-4 pair and FRC normal-Tx suppression removes it. The exact "
                "internal signer is still open: main TSS compute SoC/HSM or another "
                "network/security controller inside the FRC module."
            ),
            "decisive_evidence": (
                "Exact FRC firmware or a live FRC key-update/HSM-service trace is required "
                "to identify the internal SecOC key selector, freshness owner, CMAC call and "
                "Tx descriptor. Brake firmware remains decisive for 0x08A verification/"
                "arbitration and downstream B6 generation, not for locating the 0x08A publisher."
            ),
            "frc_branch_disposition": (
                "The old external Brake/Booster/CGW physical-publisher hypothesis is superseded "
                "by the repin direction result. Native public Bus-1 Profile-5 PDUs are simply a "
                "different FRC interface; they do not negate the protected Bus-4-side request "
                "emitted from the same FRC assembly."
            ),
            "grades": {
                "zero_request_signing_continuity": "observed",
                "physical_publisher_frc_assembly": "observed",
                "frc_internal_cmac_engine": "open",
            },
        },
        "repin_direction": repin,
        "stationary_ready_detail": ready,
        "production_output_authorized": False,
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
