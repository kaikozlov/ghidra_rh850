#!/usr/bin/env python3
"""Preserve openpilot carState steering evidence for a behavioral-proof phase."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def value(obj, name):
    try:
        return getattr(obj, name)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--duration", type=float, default=10.0)
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    if args.duration <= 0:
        parser.error("--duration must be positive")
    try:
        import cereal.messaging as messaging
    except ImportError as exc:
        parser.error(f"cannot import cereal.messaging; run inside openpilot: {exc}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sm = messaging.SubMaster(["carState"])
    deadline = time.monotonic() + args.duration
    count = 0
    with args.output.open("w", encoding="utf-8") as stream:
        while time.monotonic() < deadline:
            sm.update(100)
            if not sm.updated.get("carState", False):
                continue
            cs = sm["carState"]
            stream.write(
                json.dumps(
                    {
                        "timestamp_ns": time.time_ns(),
                        "vEgo": value(cs, "vEgo"),
                        "steeringAngleDeg": value(cs, "steeringAngleDeg"),
                        "steeringRateDeg": value(cs, "steeringRateDeg"),
                        "steeringTorque": value(cs, "steeringTorque"),
                        "steeringTorqueEps": value(cs, "steeringTorqueEps"),
                        "steeringPressed": value(cs, "steeringPressed"),
                        "steerFaultTemporary": value(cs, "steerFaultTemporary"),
                        "steerFaultPermanent": value(cs, "steerFaultPermanent"),
                    },
                    sort_keys=True,
                )
                + "\n"
            )
            count += 1

    metadata = {
        "schema": "openpilot-steering-state-evidence-v1",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duration_seconds": args.duration,
        "sample_count": count,
        "note": args.note,
        "path": str(args.output),
        "sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
    }
    args.output.with_suffix(args.output.suffix + ".json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0 if count else 2


if __name__ == "__main__":
    raise SystemExit(main())
