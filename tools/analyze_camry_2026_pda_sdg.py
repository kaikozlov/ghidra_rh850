#!/usr/bin/env python3
"""Recover the Camry TSS3 PDA/SDG lateral-request relationship.

This reducer joins three independent surfaces:

* exact-F33 B6 Target-Lateral-ID handling;
* current Toyota TSS3 Operation-FFD feature/recorder semantics; and
* native 0x08A behavior in the 2026-09-04/06 maintainer highway corpus.

The dynamic ``pda_sa_regime_proxy`` is intentionally only an operating-regime
filter: cruise off, 10..140 km/h, and fresh CarState.  It is not used to claim
that every eligible frame is a PDA-SA opportunity.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_LOG_ROOT = Path("/Users/kai/dev/inspect/logs/camry-2026")
DEFAULT_OPENPILOT_ROOT = Path("/Users/kai/dev/inspect/repos/kai-openpilot")
DEFAULT_OUT = REPO / "data/generated/camry_2026_pda_sdg_attribution.json"

ROUTES = {
  "3b": ("2026-09-04", "0000003b--62262eb7a1"),
  "3c": ("2026-09-04", "0000003c--97b9e7a69a"),
  "3d": ("2026-09-04", "0000003d--0e812cecba"),
  "3e": ("2026-09-06", "0000003e--1a2f20417d"),
  "3f": ("2026-09-06", "0000003f--36e72f5fdc"),
}
MIN_PDA_SA_PROXY_SPEED_MS = 10 / 3.6
MAX_PDA_SA_PROXY_SPEED_MS = 140 / 3.6
MAX_CARSTATE_AGE_S = 0.2


def load_logreader(openpilot_root: Path):
  sys.path.insert(0, str(openpilot_root))
  from openpilot.tools.lib.logreader import LogReader  # type: ignore[import-not-found]
  return LogReader


def discover(route_dir: Path) -> list[Path]:
  flat = sorted(route_dir.glob("rlog-*.zst"), key=lambda p: int(p.stem.split("-")[1].split(".")[0]))
  if flat:
    return flat
  return sorted(route_dir.glob("*/rlog.zst"), key=lambda p: int(p.parent.name.rsplit("--", 1)[1]))


def scan_route(LogReader, route_dir: Path) -> dict:
  files = discover(route_dir)
  if not files:
    raise FileNotFoundError(route_dir)
  all_ids: Counter[int] = Counter()
  proxy_ids: Counter[int] = Counter()
  native_count = 0
  latest_cs: tuple[float, float, bool] | None = None

  for path in files:
    for evt in LogReader(str(path), sort_by_time=True):
      t = evt.logMonoTime / 1e9
      which = evt.which()
      if which == "carState":
        latest_cs = (t, float(evt.carState.vEgo), bool(evt.carState.cruiseState.enabled))
      elif which == "can":
        for frame in evt.can:
          if frame.src != 2 or frame.address != 0x08A or len(frame.dat) < 22:
            continue
          dat = bytes(frame.dat)
          lateral_id = dat[21] & 0x3F
          native_count += 1
          all_ids[lateral_id] += 1
          if latest_cs is None:
            continue
          cs_t, speed_ms, cruise_enabled = latest_cs
          if (t - cs_t <= MAX_CARSTATE_AGE_S and not cruise_enabled and
              MIN_PDA_SA_PROXY_SPEED_MS <= speed_ms <= MAX_PDA_SA_PROXY_SPEED_MS):
            proxy_ids[lateral_id] += 1

  return {
    "segment_count": len(files),
    "native_08a_frames": native_count,
    "target_lateral_id_counts": {str(k): v for k, v in sorted(all_ids.items())},
    "pda_sa_regime_proxy": {
      "definition": "fresh CarState <=0.2 s, cruise disabled, 10..140 km/h; operating-regime proxy only",
      "frames": sum(proxy_ids.values()),
      "target_lateral_id_counts": {str(k): v for k, v in sorted(proxy_ids.items())},
    },
  }


def exact_f33_join() -> dict:
  codeflash = json.loads((REPO / "data/generated/camry_8965F3307000_codeflash.json").read_text())
  selector = codeflash["b6_steering_command"]["selector_signal"]
  corpus = REPO / "data/generated/camry-8965F3307000/decompilations.jsonl"
  ceffc = None
  cb73a = None
  cb00_readers = []
  id19_direct_consumers = []
  for line in corpus.open():
    row = json.loads(line)
    c = row.get("decompiled_c", "")
    entry = row.get("entry_addr")
    if entry == "0x000ceffc":
      ceffc = c
    if entry == "0x000cb73a":
      cb73a = c
    if "DAT_febecb00" in c:
      cb00_readers.append(entry)
    if "DAT_febeadb0" in c and "\\x13" in c:
      id19_direct_consumers.append(entry)
  if ceffc is None or cb73a is None:
    raise RuntimeError("missing exact F33 CEFFC/CB73A decompilation")

  expected_snippets = {
    "1": ("\\x01", 0),
    "4": ("\\x04", 1),
    "10": ("\\n", 3),
    "11": ("\\v", 2),
    "18": ("\\x12", 5),
    "19": ("\\x13", 4),
  }
  bank_map = {}
  for lateral_id, (literal, bank) in expected_snippets.items():
    pattern = rf"DAT_febeadb0 == '{re.escape(literal)}'.*?DAT_febecb00 = {bank};"
    if not re.search(pattern, ceffc, flags=re.S):
      raise RuntimeError(f"CEFFC bank mapping missing for ID {lateral_id}")
    bank_map[lateral_id] = bank

  if "DAT_febeadb0 == '1'" not in cb73a:
    raise RuntimeError("CB73A raw 0x31 special consumer missing")

  return {
    "wire": selector["wire"],
    "oem_name": selector["oem_name"],
    "accepted_controller_values": selector["accepted_controller_values"],
    "controller_bank_map": bank_map,
    "common_cb00_reader_function_count": len(cb00_readers),
    "id19_direct_snapshot_consumers": id19_direct_consumers,
    "separate_special_snapshot_consumer": {
      "entry": "0x000CB73A",
      "raw_value": 49,
      "oem_label": selector["additional_target_native_value"]["49"],
      "boundary": "separate transient state machine; not PDA",
    },
  }


def gts_join() -> dict:
  pcs = json.loads((REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json").read_text())
  schema = pcs["operation_ffd"]["lateral_arbitration_schema"]
  pda_oaa = schema["feature_requests"]["PDA_OAA"]
  rob = next(row for row in pcs["rob_codes"]["rows"] if row["rob_code"] == "22B4")
  sa_rows = [row for row in pcs["operation_ffd"]["detail_rows"] if row["DataID"] in {"5D81", "5D85", "5D89", "5D8D", "5D8E"}]
  return {
    "pda_oaa_request": {
      "data_ids": pda_oaa["data_ids"],
      "field_names": [row["DataName"] for row in pda_oaa["fields"]],
      "layout": pda_oaa["layout"],
    },
    "pda_sa": {
      "rob_code": rob["rob_code"],
      "rob_name": rob["DataName"],
      "rob_system_type": rob["SystemType"],
      "rob_system_name": rob["SystemName"],
      "status_field_names": [row["DataName"] for row in sa_rows],
    },
    "arbitration_result_lateral_id_did": schema["arbitration_result"]["lateral_id"]["DataID"],
  }


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("--log-root", type=Path, default=DEFAULT_LOG_ROOT)
  ap.add_argument("--openpilot-root", type=Path, default=DEFAULT_OPENPILOT_ROOT)
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()
  LogReader = load_logreader(args.openpilot_root)

  routes = {}
  for short, (day, route) in ROUTES.items():
    routes[short] = scan_route(LogReader, args.log_root / day / route)
    routes[short]["route"] = route

  report = {
    "schema": "camry-2026-pda-sdg-attribution-v1",
    "conclusion": {
      "pda_sa_to_sdg": "Toyota's TSS3 recorder classifies PDA(SA) under SystemType 6 / SDG; same-car ID18 is therefore the strongest wire identity for PDA-SA/SDG steering.",
      "id19_boundary": "Target Lateral ID 19 is OEM-labeled PDA and exact F33 gives it a distinct bank in the same B6 controller. No native ID19 episode is present in the scanned 2026-09-04/06 corpus, so PDA-OAA->ID19 remains an architectural interpretation rather than a dynamic same-car join.",
      "other_path": "PDA does not create a second recovered F33 external steering ingress: ID18/ID19 are common B6-controller profiles; the separate target-native snapshot consumer is raw 49 / Self-Propelled Transport.",
    },
    "exact_f33": exact_f33_join(),
    "gts_tss3": gts_join(),
    "routes": routes,
    "supplemental_archive_scan": {
      "boundary": "Supplemental one-time scan of pre-Sep-1 full rlogs retained on the maintainer comma; not required for deterministic regeneration of this artifact.",
      "routes": {
        "00000027--885099a1d4": {"0": 32023, "11": 27348, "18": 15468},
        "00000029--bae47e927f": {"0": 27846, "11": 76, "18": 206},
        "0000002a--c5647fd694": {"0": 21773, "18": 964},
        "0000002c--c784367b7e": {"0": 57532, "11": 3460, "18": 238},
      },
      "native_08a_frames": 186934,
      "aggregate_target_lateral_id_counts": {"0": 139174, "11": 30884, "18": 16876},
      "id19_frames": 0,
    },
  }
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
  print(f"wrote {args.out}")
  for short, row in routes.items():
    print(short, row["target_lateral_id_counts"], row["pda_sa_regime_proxy"]["target_lateral_id_counts"])


if __name__ == "__main__":
  main()
