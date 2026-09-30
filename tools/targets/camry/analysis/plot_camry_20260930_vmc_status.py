#!/usr/bin/env python3
"""Render the retained VMC incident and cross-state evidence (offline only).

Uses the extraction/join cache and matplotlib (available in the openpilot/
opendbc runtime). Plot thinning is deterministic and does not affect numerical
summaries. Titles retain byte offsets rather than asserting OEM field names.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from tools import REPO_ROOT

DEFAULT_CORPUS = REPO_ROOT / "build/cache/camry_20260930_vmc_corpus"
DEFAULT_OUTPUT = REPO_ROOT / "data/generated/camry_20260930_vmc_status"
ROUTES = ("00000086--575a5fd6a5", "00000087--7e7f16f8af", "00000088--462e38e23b", "0000008a--0c0e51b672")


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--corpus-dir", type=Path, default=DEFAULT_CORPUS)
  parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
  args = parser.parse_args()
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt
  plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": .2})
  args.output_dir.mkdir(parents=True, exist_ok=True)
  info = json.loads((args.corpus_dir / (ROUTES[0] + ".joined.json")).read_text())
  with np.load(args.corpus_dir / (ROUTES[0] + ".joined.npz")) as j, np.load(args.corpus_dir / (ROUTES[0] + ".npz")) as raw:
    pedal = raw["pedal"]
    onset = float(pedal[(pedal[:, 2] == info["brake_source"]) & (pedal[:, 4] == 1)
                        & (pedal[:, 0] > 250) & (pedal[:, 0] < 255), 0].min())
    select = (j["t"] >= onset - 15) & (j["t"] <= onset + 10)
    x, w, cc = j["t"][select] - onset, j["words"][select] * .001, j["cc"][select]
    fig, axes = plt.subplots(4, 1, figsize=(14, 12), sharex=True)
    axes[0].plot(x, np.where(cc[:, 3] == 1, cc[:, 2], np.nan), label="comma CarControl.accel while longActive", lw=2)
    axes[0].plot(x, j["applied"][select, 0], label="vehicle-side Tx-confirmed 0x08A upper", lw=1.5)
    axes[0].plot(x, j["native"][select, 0], "--", label="native FRC 0x08A upper (may be blocked)", alpha=.8)
    axes[0].set_ylabel("request (m/s²)")
    axes[0].legend(loc="lower left", fontsize=9)
    axes[0].set_title(f"Route86, segment4: 0 = driver brake onset at route {onset:.3f}s (logger time)")
    for offset, label, color in ((4, "B4:B5", "black"), (18, "B18:B19", "tab:orange"),
                                 (20, "B20:B21", "tab:purple"), (24, "B24:B25", "tab:green")):
      axes[1].plot(x, w[:, offset // 2], label=label, color=color, lw=1.5)
    axes[1].plot(x, j["cs"][select, 4], ":", color="tab:red", label="wheel-derived aEgo", lw=2)
    axes[1].set_ylabel("status s16BE ×0.001")
    axes[1].legend(loc="lower left", fontsize=9, ncol=2)
    axes[2].step(x, j["result_id"][select], where="post", label="0x081 result ID")
    axes[2].step(x, j["origin"][select] * 10, where="post",
                 label="Tx origin: 10=host, 20=native, 30=both, 0=unknown", alpha=.65)
    axes[2].set_ylabel("ID / origin code")
    axes[2].legend(loc="upper left", fontsize=9)
    axes[3].plot(x, j["gas"][select, 3], label="raw accelerator fraction")
    axes[3].step(x, j["brake_on"][select].astype(float), where="post", label="driver brake switch")
    axes[3].step(x, cc[:, 3], where="post", label="comma longActive", alpha=.7)
    axes[3].set(ylabel="pedal / active", xlabel="seconds relative to raw driver brake onset")
    axes[3].legend(loc="upper left", fontsize=9)
    for axis in axes:
      axis.axvline(0, color="tab:red", ls="--", alpha=.55)
    fig.tight_layout()
    fig.savefig(args.output_dir / "incident_and_restart.png", dpi=180)
    plt.close(fig)

  all_rows = []
  for route in ROUTES:
    with np.load(args.corpus_dir / (route + ".joined.npz")) as j:
      valid = np.isfinite(j["v"]) & (j["v"] > .5) & np.isfinite(j["cs"][:, 4]) & (j["request_loss"] == 0)
      words, native = j["words"][valid] * .001, j["native"][valid]
      all_rows.append(np.column_stack((words[:, 2], words[:, 9], words[:, 10], words[:, 11], words[:, 12],
                                      j["cs"][valid, 4], j["gas"][valid, 3], native[:, 0], native[:, 2], native[:, 3])))
  a = np.concatenate(all_rows)
  fig, axes = plt.subplots(2, 2, figsize=(13, 11))
  s = a[::max(1, len(a) // 18000)]
  axes[0, 0].scatter(np.maximum(s[:, 0], s[:, 4]), s[:, 1], s=2, alpha=.2)
  axes[0, 0].plot([-5, 4], [-5, 4], "k--", lw=1)
  axes[0, 0].set(xlabel="max(B4, B24)", ylabel="B18", title="Dominant numerical relation, moving vehicle")
  idle = (a[:, 8] == 0) & (a[:, 9] == 4) & np.isfinite(a[:, 7])
  axes[0, 1].scatter(a[idle, 7], a[idle, 2], s=2, alpha=.15)
  axes[0, 1].plot([-2, 2], [-2, 2], "k--", lw=1)
  axes[0, 1].set(xlabel="inactive native FRC upper word (IDs0/4)", ylabel="B20", title="Inactive request words versus B20")
  axes[1, 0].scatter(s[:, 5], s[:, 0], s=2, alpha=.2)
  axes[1, 0].plot([-5, 4], [-5, 4], "k--", lw=1)
  axes[1, 0].set(xlabel="wheel-derived aEgo (m/s²)", ylabel="B4", title="B4 comparison (not a proved sensor reading)")
  ratio = (a[:, 4] - a[:, 2]) / np.maximum(a[:, 3] - a[:, 2], .01)
  valid = np.isfinite(a[:, 6]) & (a[:, 6] > 0) & (a[:, 3] - a[:, 2] > .2) & (ratio > -.2) & (ratio < 1.2)
  axes[1, 1].scatter(a[valid, 6], ratio[valid], s=2, alpha=.15)
  axes[1, 1].set(xlabel="raw GAS_PEDAL_USER fraction", ylabel="(B24-B20)/(B22-B20)", title="Driver-demand/reference hypothesis")
  fig.suptitle("Four current drives — raw status offsets; semantic names remain provisional", fontsize=13)
  fig.tight_layout()
  fig.savefig(args.output_dir / "cross_state_relationships.png", dpi=180)
  plt.close(fig)
  print(json.dumps({"moving_rows": len(a), "output_dir": str(args.output_dir)}))


if __name__ == "__main__":
  main()
