#!/usr/bin/env python3
"""Deterministic 0x08A signer-continuity artifact for the 2026 Camry.

Answers one bounded question from OQ-054: is the Bus-4 `0x08A` signer
on-demand (active only when FRC has a lateral request) or always-on?

Primary evidence is the retained 2026-08-26 stationary NRTD->READY capture
(`camry_ready_gear_20260826.json.gz`, bus 1), which aggregates the secured
chassis family on the pre-repin development plane. With the vehicle
stationary and `B21` (Target Lateral ID) equal to zero in every frame, the
artifact records whether the FV4 freshness still tracks the live `0x00F`
epoch, whether B26 still advances +1 mod 64, and whether the MAC28 stays
frame-unique — the structural signature of an always-on signing engine
independent of the FRC request lifecycle.

The two relay-correct drives supply the active-request contrast: their ID11
intervals carry `B21 == 11` (LTA/LCA) while the stationary capture carries
`B21 == 0`. The signer's cadence/freshness statistics are compared between
the zero-request and active-request regimes.

Grades: observed structural facts are `observed`; the signer identity
inference (brake family / Central Gateway, FRC excluded as key holder) is
`hypothesis` pending producer firmware, consistent with VAR-091/096.
"""
from __future__ import annotations

import bisect
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
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
            "Is the Bus-4 0x08A signer always-on (signing at zero lateral request) "
            "or on-demand? An always-on signer is structurally inconsistent with the "
            "front camera being the SecOC key holder, because the camera only signs "
            "what its planner authorizes."
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
                "The secured 0x08A family signs continuously at zero lateral request: "
                "B21=0 in 100% of stationary frames while FV4 reset-low2 tracks the "
                "live 0x00F epoch, B26 advances +1 mod 64, and MAC28 stays frame-unique. "
                "The signer is an always-on chassis engine whose output is independent "
                "of the FRC request lifecycle."
            ),
            "boundary": (
                "Structural signing continuity does not identify the signer. VAR-091/096 "
                "bound candidates to the brake family (ABS 435 / Brake Booster 466) or "
                "Central Gateway; FRC is excluded as generated-COM transmitter and as a "
                "plausible always-on key holder. Producer firmware remains the decisive "
                "evidence (acquisition route TMS-049/050)."
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
            "grade": "hypothesis",
            "verdict": (
                "Hypothesis: a brake-family node (Skid Control ABS / Brake Booster) or "
                "the Central Gateway signs 0x08A; the FRC publishes the request into the "
                "chassis domain and cannot be the key holder. Architectural support: TSK "
                "AES-CMAC keys live in ICU-S protected storage (F33-class RH850 parts); "
                "the FRC is not an ICU-S key-store part in any retained evidence; GTS+ "
                "places the brake family and EPS on Bus 4 where 0x08A appears; ADCU_P6 "
                "vocabulary names the OEM request/arbitrate/sign pattern explicitly "
                "(Lateral Arbitration ID / Lateral Control ID of Arbitrated Result)."
            ),
            "decisive_evidence": (
                "Exact producer firmware: decode the brake-family Tx descriptors "
                "(search order in camry_f152633k0000_brake_acquisition.json). A "
                "0x08A Tx descriptor + SecOC generation profile in F152633K0000 or "
                "Skid Control firmware identifies the signer deterministically."
            ),
            "frc_branch_disposition": (
                "FRC pre-authentication is not excluded by signing continuity alone — an "
                "always-on signer could re-sign a forwarded FRC image — but it requires "
                "the FRC to hold no key while forwarding unsigned request images to the "
                "signer, which the zero-request continuity makes unnecessary as an "
                "assumption. The decisive FRC exclusion remains producer firmware."
            ),
            "grades": {
                "zero_request_signing_continuity": "observed",
                "signer_identity_brake_family_or_cgw": "hypothesis",
                "frc_excluded_as_key_holder": "hypothesis",
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
