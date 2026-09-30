#!/usr/bin/env python3
"""Extract the 2026-09-30 Camry VMC status/request corpus from original rlogs.

Walks a caller-supplied rlog tree, groups ``rlog.zst`` segment files by route,
and samples each route into fixed-column float64 streams plus raw 32-byte
0x081 status and 0x08A request payloads. Per route this writes
``<output-dir>/<route>.npz`` (streams plus ``status_bytes``/``req_bytes``),
``<output-dir>/<route>.json`` (extraction metadata and input provenance), and
one shared ``manifest.json`` describing the inventory.

Invocation (repository root, environment providing numpy, capnp, zstandard):

  uv run --no-sync --project /path/to/opendbc python \
    -m tools.targets.camry.analysis.extract_camry_20260930_vmc_corpus \
    --logs-root /path/to/rlogs --openpilot-root /path/to/openpilot-checkout \
    --routes 00000089--0dd1afd752

Environment prerequisites:
- numpy (existing repository dependency).
- ``--openpilot-root`` is a caller-supplied openpilot checkout containing
  ``tools/lib/logreader.py`` (nested-package forks accepted). Its importable
  parent is added to ``sys.path`` lazily at runtime; this is caller input, not
  repository-owned importing, so the default checkout path must be passed
  explicitly.

Provenance: each route's ``.json`` records the selected source files with
their readable absolute ``path`` (matching the cached originals),
``relative_path`` against ``--logs-root``, ``size_bytes``, and ``sha256``;
``logs_root`` is retained at the top level so the corpus can be rebased when
consumed from another location. The route ``origin_ns`` and per-segment
sampled first/last ``logMonoTime`` come from decoded events only; the cached
``initData``/``carParams`` records are capture metadata and are not
per-segment playback anchors. Outputs stay in git-ignored caches; no raw
rlogs or derived caches are tracked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from tools import REPO_ROOT

ROOT = REPO_ROOT
DEFAULT_OUTPUT_DIR = ROOT / "build/cache/camry_20260930_vmc_corpus"
PRIMARY = {"00000086--575a5fd6a5", "00000087--7e7f16f8af", "00000088--462e38e23b", "00000089--0dd1afd752", "0000008a--0c0e51b672"}
COLUMNS = {
  "req": ["t", "segment", "kind_can0_send1", "src"],
  "status": ["t", "segment", "src"],
  "cs": ["t", "segment", "vRaw", "vEgo", "aEgo", "gasPressed", "brakePressed", "standstill", "cruiseEnabled", "cruiseStandstill", "canValid", "sensorsInvalid"],
  "cc": ["t", "segment", "accel", "longActive", "latActive", "enabled", "longState", "pitch"],
  "out": ["t", "segment", "accel"],
  "plan": ["t", "segment", "aTarget", "shouldStop", "source", "fcw"],
  "sd": ["t", "segment", "enabled", "experimentalMode", "personality"],
  "wheel": ["t", "segment", "src", "v_mps", "fault"],
  "pedal": ["t", "segment", "src", "gas_fraction", "brakePressed"],
}
LONG_STATES = {"off": 0, "pid": 1, "stopping": 2, "starting": 3}
PLAN_SOURCES = {"cruise": 0, "lead0": 1, "lead1": 2, "e2e": 3}
TIMING_NOTE = (
  "origin_ns and per-segment start_ns/end_ns are sampled from decoded "
  "logMonoTime events in each rlog; cached init/carParams timestamps are "
  "capture metadata, not actual segment playback anchors."
)


def load_logreader(openpilot_root: Path):
  """Import LogReader from the caller-supplied openpilot checkout."""
  root = openpilot_root.resolve()
  for candidate in (root, root / "openpilot"):
    if (candidate / "tools/lib/logreader.py").exists():
      # In a nested-package checkout `candidate` is itself the openpilot
      # package, so `from openpilot...` needs candidate's parent importable.
      base = candidate.parent if (candidate / "__init__.py").exists() else candidate
      if str(base) not in sys.path:
        sys.path.insert(0, str(base))
      break
  else:
    raise FileNotFoundError(f"no tools/lib/logreader.py under {openpilot_root}")
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def sha256_file(path: Path) -> str:
  digest = hashlib.sha256()
  with path.open("rb") as stream:
    for block in iter(lambda: stream.read(1 << 20), b""):
      digest.update(block)
  return digest.hexdigest()


def relative(path: Path, logs_root: Path) -> str:
  try:
    return str(path.resolve().relative_to(logs_root.resolve()))
  except ValueError:
    return str(path)


def inventory(logs_root: Path, output_dir: Path):
  groups = defaultdict(list)
  excluded = []
  for p in sorted(logs_root.rglob("rlog.zst")):
    m = re.fullmatch(r"([0-9a-f]{8}--[0-9a-f]{10})--(\d+)", p.parent.name)
    if m:
      route, seg = m.group(1), int(m.group(2))
    elif p.parent.name.isdigit() and re.fullmatch(r"[0-9a-f]{8}--[0-9a-f]{10}", p.parent.parent.name):
      route, seg = p.parent.parent.name, int(p.parent.name)
    else:
      excluded.append({"path": str(p), "reason": "not an unambiguous route/segment path"})
      continue
    groups[route].append({"path": str(p), "segment": seg})
  if not groups:
    raise FileNotFoundError(f"no rlog.zst segment files found under {logs_root}")
  rows = [{"route": r, "primary": r in PRIMARY, "files": sorted(v, key=lambda x: x["segment"])} for r, v in sorted(groups.items())]
  output_dir.mkdir(parents=True, exist_ok=True)
  (output_dir / "manifest.json").write_text(json.dumps({
    "logs_root": str(logs_root.resolve()),
    "routes": rows,
    "excluded_paths": excluded,
    "columns": COLUMNS,
    "long_states": LONG_STATES,
    "plan_sources": PLAN_SOURCES,
  }, indent=2))
  return rows


def extract(route: dict, logs_root: Path, output_dir: Path, openpilot_root: Path, LogReader) -> None:
  streams = {k: [] for k in COLUMNS}
  payloads = {"req": [], "status": []}
  meta = {"route": route["route"], "primary": route["primary"], "files": [], "init": None, "cp": None, "errors": [], "segments": [], "target_counts": {}}
  counts = Counter()
  for f in route["files"]:
    seg = f["segment"]
    path = logs_root / f["path"]
    first = None
    last = None
    for m in LogReader(str(path), only_union_types=True, sort_by_time=True):
      t = int(m.logMonoTime)
      first = t if first is None else min(first, t)
      last = t if last is None else max(last, t)
      k = m.which()
      try:
        if k == "initData" and meta["init"] is None:
          d = m.initData.to_dict()
          meta["init"] = {x: d[x] for x in ("version", "gitCommit", "gitBranch", "gitDirty", "wallTimeNanos", "deviceType") if x in d}
        elif k == "carParams" and meta["cp"] is None:
          d = m.carParams.to_dict()
          meta["cp"] = {x: d[x] for x in ("carFingerprint", "brand", "openpilotLongitudinalControl", "dashcamOnly", "flags", "safetyConfigs", "wheelSpeedFactor", "longitudinalActuatorDelay", "longitudinalTuning") if x in d}
        elif k == "carState":
          s = m.carState
          streams["cs"].append((t, seg, s.vEgoRaw, s.vEgo, s.aEgo, s.gasPressed, s.brakePressed, s.standstill, s.cruiseState.enabled, s.cruiseState.standstill, s.canValid, s.vehicleSensorsInvalid))
        elif k == "carControl":
          s = m.carControl
          streams["cc"].append((t, seg, s.actuators.accel, s.longActive, s.latActive, s.enabled, LONG_STATES.get(str(s.actuators.longControlState), -1), s.orientationNED[1] if len(s.orientationNED) == 3 else float("nan")))
        elif k == "carOutput":
          streams["out"].append((t, seg, m.carOutput.actuatorsOutput.accel))
        elif k == "longitudinalPlan":
          s = m.longitudinalPlan
          streams["plan"].append((t, seg, s.aTarget, s.shouldStop, PLAN_SOURCES.get(str(s.longitudinalPlanSource), -1), s.fcw))
        elif k == "selfdriveState":
          s = m.selfdriveState
          streams["sd"].append((t, seg, s.enabled, s.experimentalMode, int(s.personality.raw)))
        elif k in ("can", "sendcan"):
          kind = int(k == "sendcan")
          for q in getattr(m, k):
            addr, src = q.address, q.src
            if addr in (0x081, 0x08A) and len(q.dat) == 32:
              key = "status" if addr == 0x081 else "req"
              counts[(k, addr, src)] += 1
              if key == "status" and kind:
                continue
              streams[key].append((t, seg, src) if key == "status" else (t, seg, kind, src))
              payloads[key].append(bytes(q.dat))
            elif not kind and src < 4 and len(q.dat) == 8:
              if addr == 0x0AA:
                b = bytes(q.dat)
                raw = [int.from_bytes(b[i:i + 2], "big") for i in (0, 2, 4, 6)]
                v = sum((x & 0x7FFF) * .01 - 67.67 for x in raw) / 4 / 3.6
                streams["wheel"].append((t, seg, src, v, any(x & 0x8000 for x in raw)))
              elif addr == 0x116:
                streams["pedal"].append((t, seg, src, bytes(q.dat)[1] * .005, float("nan")))
              elif addr == 0x101:
                streams["pedal"].append((t, seg, src, float("nan"), bool(bytes(q.dat)[0] & 8)))
      except Exception as e:
        if len(meta["errors"]) < 20:
          meta["errors"].append({"segment": seg, "kind": k, "error": repr(e)})
        counts[("decode_error", k, -1)] += 1
    meta["segments"].append({"segment": seg, "start_ns": first, "end_ns": last})
  starts = [x["start_ns"] for x in meta["segments"] if x["start_ns"] is not None]
  origin = min(starts)
  meta["origin_ns"] = origin
  meta["duration_s"] = (max(x["end_ns"] for x in meta["segments"] if x["end_ns"] is not None) - origin) / 1e9
  meta["target_counts"] = {f"{k}:{a}:{s}": n for (k, a, s), n in counts.items()}
  files_provenance = []
  for f in route["files"]:
    path = Path(f["path"])
    files_provenance.append({"path": f["path"], "segment": f["segment"], "relative_path": relative(path, logs_root), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)})
  meta["files"] = files_provenance
  meta["logs_root"] = str(logs_root.resolve())
  meta["openpilot_root"] = str(openpilot_root)
  meta["timing_note"] = TIMING_NOTE
  arrays = {}
  meta["rows"] = {}
  meta["duplicates_removed"] = {}
  for key, rows in streams.items():
    indices = sorted(range(len(rows)), key=lambda i: rows[i][0])
    seen = set()
    keep = []
    for i in indices:
      row = rows[i]
      if key in payloads:
        signature = (row[0], *row[2:], payloads[key][i])
      else:
        # Ignore segment labels when the same sampled event straddles a segment boundary.
        signature = (row[0], *row[2:])
      if signature not in seen:
        seen.add(signature)
        keep.append(i)
    a = np.asarray([rows[i] for i in keep], dtype=np.float64).reshape((-1, len(COLUMNS[key])))
    if len(a):
      a[:, 0] = (a[:, 0] - origin) / 1e9
    arrays[key] = a
    if key in payloads:
      arrays[key + "_bytes"] = np.frombuffer(b"".join(payloads[key][i] for i in keep), dtype=np.uint8).reshape((-1, 32)).copy()
    meta["rows"][key] = len(keep)
    meta["duplicates_removed"][key] = len(rows) - len(keep)
  np.savez(output_dir / (route["route"] + ".npz"), **arrays)
  (output_dir / (route["route"] + ".json")).write_text(json.dumps(meta, indent=2, default=str))
  print(json.dumps({"route": route["route"], "primary": route["primary"], "duration_s": round(meta["duration_s"], 2), "cp": meta["cp"], "init": meta["init"], "rows": meta["rows"], "errors": meta["errors"]}), flush=True)


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--logs-root", type=Path, required=True, help="directory tree of <route>--<segment>/rlog.zst captures")
  parser.add_argument("--openpilot-root", type=Path, required=True, help="openpilot checkout providing tools/lib/logreader.py")
  parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help=f"corpus output directory (default {DEFAULT_OUTPUT_DIR}, ignored by git)")
  parser.add_argument("--routes", nargs="*", help="restrict to these route ids")
  parser.add_argument("--primary", action="store_true", help="restrict to the five primary routes")
  parser.add_argument("--inventory", action="store_true", help="print the route inventory without extracting")
  parser.add_argument("--missing", action="store_true", help="skip routes whose .npz and .json outputs already exist")
  args = parser.parse_args()
  LogReader = load_logreader(args.openpilot_root)
  manifest = inventory(args.logs_root, args.output_dir)
  if args.inventory:
    print(json.dumps([{"route": r["route"], "segments": len(r["files"]), "primary": r["primary"]} for r in manifest], indent=2))
    return
  for route in manifest:
    if args.primary and not route["primary"]:
      continue
    if args.routes and route["route"] not in args.routes:
      continue
    if args.missing and (args.output_dir / (route["route"] + ".npz")).exists() and (args.output_dir / (route["route"] + ".json")).exists():
      continue
    extract(route, args.logs_root, args.output_dir, args.openpilot_root, LogReader)


if __name__ == "__main__":
  main()
