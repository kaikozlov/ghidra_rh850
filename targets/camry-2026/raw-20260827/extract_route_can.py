#!/usr/bin/env python3
"""Privacy-minimize a comma route to deterministic incoming-CAN NDJSON gzip.

Run in an openpilot Python environment that provides LogReader. The output keeps
only [segment, logMonoTime, src, address, data_hex] for src<128 CAN frames.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

from openpilot.tools.lib.logreader import LogReader


def main() -> int:
  ap = argparse.ArgumentParser()
  ap.add_argument("route_dir", type=Path, help="directory containing <segment>-rlog.zst")
  ap.add_argument("out", type=Path)
  ap.add_argument("--start-segment", type=int, default=0)
  ap.add_argument("--segments", type=int, default=9, help="number of consecutive segments")
  args = ap.parse_args()

  with args.out.open("wb") as f, gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0, compresslevel=9) as gz:
    for seg in range(args.start_segment, args.start_segment + args.segments):
      path = args.route_dir / f"{seg}-rlog.zst"
      for event in LogReader(str(path), sort_by_time=True):
        if event.which() != "can":
          continue
        t = int(event.logMonoTime)
        for frame in event.can:
          src = int(frame.src)
          if src >= 128:
            continue
          row = [seg, t, src, int(frame.address), bytes(frame.dat).hex()]
          gz.write((json.dumps(row, separators=(",", ":")) + "\n").encode())
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
