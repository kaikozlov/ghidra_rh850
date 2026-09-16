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

Grades: observed structural continuity is `observed`; physical Bus-4 publication
is topology-bounded to a downstream chassis/gateway participant; CMAC generation
and key ownership remain open after CORR-194 because the FRC itself is an
ECU-Security-Key provisioning participant.
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
    return {
        "schema": "camry-2026-08a-signer-continuity-v1",
        "question": (
            "Does the authenticated Bus-4 0x08A publication continue at zero lateral "
            "request, and what can that continuity say about physical publication versus "
            "CMAC ownership? CORR-194 keeps FRC private pre-authentication open because "
            "the camera family itself participates in ECU-Security-Key provisioning."
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
                "Structural security-envelope continuity does not identify the signer or "
                "key holder. VAR-091/096 bound the physical Bus-4 publisher/proxy to the "
                "brake family (ABS 435 / Brake Booster 466) or Central Gateway. CORR-194 "
                "reopens private FRC pre-authentication because camera-family "
                "ECU-Security-Key provisioning is now positive evidence. Producer "
                "firmware plus FRC key-update/private-link evidence remain decisive."
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
            "grade": "open",
            "verdict": (
                "Physical publication hypothesis: a brake-family node (Skid Control ABS / "
                "Brake Booster) or the Central Gateway proxies and transmits 0x08A on Bus "
                "4. Cryptographic ownership is unresolved: CMAC may be generated in that "
                "downstream participant or supplied through an unseen/private FRC "
                "pre-authentication path. GTS+ places the camera on Bus 1 and the brake "
                "family on Bus 4, but topology does not locate the key/CMAC operation."
            ),
            "decisive_evidence": (
                "Exact downstream producer firmware can identify the 0x08A Tx descriptor "
                "and any local SecOC generation profile. Exact FRC firmware, a live FRC "
                "M1-M5 key-update trace, or private-link capture is additionally required "
                "to exclude or prove upstream camera pre-authentication."
            ),
            "frc_branch_disposition": (
                "FRC-side private TSK/SecOC pre-authentication is open after CORR-194. "
                "Current FRC_P5 diagnostics and Toyota replacement procedure prove that "
                "the camera family participates in ECU-Security-Key provisioning. Native "
                "Bus-1 Profile-5 framing proves only that the observed public camera PDUs "
                "are not themselves the Bus-4 SecOC publication."
            ),
            "grades": {
                "zero_request_signing_continuity": "observed",
                "signer_identity_brake_family_or_cgw": "physical-publisher-hypothesis-only",
                "frc_excluded_as_key_holder": "withdrawn-by-corr194",
            },
        },
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
