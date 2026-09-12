#!/usr/bin/env python3
"""Exercise saved-log recovery counting without openpilot, capnp, or a vehicle."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/targets/camry/analysis/analyze_camry_eps_recovery_liveness.py"
spec = importlib.util.spec_from_file_location("recovery_liveness", SOURCE)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def event(kind: str, seconds: int, payload) -> NS:
    return NS(logMonoTime=seconds * 10**9, which=lambda: kind, **{kind: payload})


def frame(address: int, src: int, size: int = 8) -> NS:
    return NS(address=address, src=src, dat=bytes(size))


def scan(events: list) -> dict:
    def reader(path: str, *, only_union_types: bool):
        assert path == "local-test.zst" and only_union_types
        return iter(events)
    return module.scan(Path("local-test.zst"), reader)


def main() -> int:
    empty = scan([])
    assert empty["duration_s"] == 0 and empty["wall_start_utc"] is None
    assert empty["logger_build"] is None and not empty["watched_frames"]

    # A TX echo, a rejected return, and a neighboring ECU are not an EPS reply.
    absent = scan([
        event("sendcan", 10, [frame(0x7A1, 1), frame(0x030, 0, 32)]),
        event("can", 11, [frame(0x7A9, 129), frame(0x7A9, 193),
                          frame(0x7AA, 1), frame(0x030, 128, 32)]),
    ])
    assert absent["eps_generated_tx_native_rx"] == 0
    assert absent["eps_diagnostic_response_native_rx"] == 0
    assert absent["frame_counts_by_source"]["can/src129"] == 1

    # Repeated metadata can precede a segment's CAN; it is not its start time.
    present = scan([
        event("initData", 1, NS(wallTimeNanos=1000 * 10**9,
                                gitCommit="producer", gitBranch="branch",
                                dirty=False, version="test")),
        event("can", 11, [frame(0x030, 0, 32), frame(0x030, 2, 32)]),
        event("can", 13, [frame(0x7A9, 1), frame(0x7A9, 1, 12)]),
        event("can", 15, [frame(0x7A9, 1, 12)]),
    ])
    assert present["duration_s"] == 4
    assert present["wall_start_utc"] == "1970-01-01T00:16:50+00:00"
    assert present["eps_generated_tx_native_rx"] == 2
    assert present["eps_diagnostic_response_native_rx"] == 3
    assert present["logger_build"] == {
        "git_commit": "producer", "git_branch": "branch",
        "dirty": False, "version": "test",
    }
    short = next(r for r in present["watched_frames"]
                 if r["address"] == "0x7A9" and r["length"] == 8)
    assert short["first_relative_s"] == short["last_relative_s"] == 2
    assert "fd" not in short  # Length alone does not establish the frame format.

    # A sendcan-only file is valid input, not evidence of CAN receive coverage.
    tx_only = scan([event("sendcan", 6, [frame(0x7A1, 1)]),
                    event("sendcan", 7, [frame(0x7A1, 1)])])
    assert tx_only["duration_s"] == 0 and tx_only["wall_start_utc"] is None
    assert tx_only["watched_frames"][0]["last_relative_s"] == 1
    assert tx_only["eps_diagnostic_response_native_rx"] == 0
    # A recorded mode is useful only across agreeing, nearby state samples.
    probe = (150_000_000, "can", 129, 0x7A1, "023e000000000000")
    mode = ("elm327", 1)

    def assigned(states):
        return module.diagnostic_modes([probe], states)["observations"][0]["mode"]

    assert assigned([(100_000_000, mode), (200_000_000, mode)]) == ["elm327", 1]
    assert assigned([(100_000_000, mode), (200_000_000, ("elm327", 0))]) is None
    assert assigned([(0, mode), (400_000_000, mode)]) is None
    assert assigned([]) is None
    assert assigned([(100_000_000, None), (200_000_000, None)]) is None
    assert assigned([(100_000_000, None), (100_000_000, mode),
                     (200_000_000, mode)]) == ["elm327", 1]
    print("camry EPS recovery saved-log counting: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
