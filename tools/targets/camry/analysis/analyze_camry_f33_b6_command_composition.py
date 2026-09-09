#!/usr/bin/env python3
"""Close exact-F33 B6 ID11 command composition and exclusivity.

This firmware-static reducer exhausts every canonical CodeFlash function that
references the B6 Target Lateral ID selector (FEBECB00) and the decoded B6 ID
snapshot (FEBEADB0), and every direct writer of the shared steering command
funnel.  It pins the exact target-angle path into the B6 supervisor, the
supervisor contribution into FEBECB38, the ordinary D0218 sum, and the unique
runtime writers through the physical-current mirror.  The question answered is
structural: does accepted ID11 B6 select an exclusive replacement command path?
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
DEFAULT_OUT = ROOT / "data/generated/camry_f33_b6_command_composition.json"
EXPECTED_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

# Exact LocalRAM cells that define the relevant control cone.
ADB0 = 0xFEBEADB0  # B6 sig261 / Target Lateral ID snapshot
AE90 = 0xFEBEAE90  # B6 sig262 / target steering angle snapshot
CB00 = 0xFEBECB00  # decoded target-lateral mode bank
CB38 = 0xFEBECB38  # B6 supervisor contribution into ordinary assist sum

# Exhaustive, non-overlapping semantic partition of every function that reads or
# writes the target-lateral controller-bank selector.  The sets are checked
# against the complete corpus at runtime so a new CB00 consumer cannot silently
# fall outside the analysis.
CB00_PARTITION = {
  "mode_mirror_status": {
    0x0C5164, 0x0C666C, 0x0C6C82, 0x0C7A18, 0x0C7D14, 0x0C7DD4, 0x0C890E, 0x0C9058, 0x0CF4A8,
  },
  "controller_calibration_supervision": {
    0x0CCCC6, 0x0CCDC4, 0x0CCECC, 0x0CCFB2, 0x0CD094, 0x0CD128, 0x0CD2A0, 0x0CD426,
    0x0CD538, 0x0CD590, 0x0CD5EA, 0x0CD662, 0x0CD724, 0x0CD84E, 0x0CD932, 0x0CDA20,
    0x0CDAE0, 0x0CDB5C, 0x0CDC48, 0x0CDEBC, 0x0CDFF8, 0x0CE144, 0x0CE384, 0x0CE454,
    0x0CE4B8, 0x0CE4DA, 0x0CE51C, 0x0CE6CC,
  },
  "readiness_fault_supervision": {
    0x0CE836, 0x0CECD6, 0x0CED28, 0x0CEDA4, 0x0CEE46, 0x0CEE7C, 0x0CEF26,
  },
  "bank_selection": {0x0CEFF4, 0x0CEFFC},
  "gain_output_shaping": {0x0CF0EA, 0x0CF22C, 0x0CF276},
}

FINAL_CELLS = {
  "CC48": 0xFEBECC48,
  "CC4C": 0xFEBECC4C,
  "CC4E": 0xFEBECC4E,
  "CC60": 0xFEBECC60,
  "CC50": 0xFEBECC50,
  "CC62": 0xFEBECC62,
  "CC64": 0xFEBECC64,
  "AC54": 0xFEBEAC54,
  "EE40C": 0xFEBEE40C,
}

# Functions whose bodies establish the semantic path.  The exhaustive selector
# and writer censuses below are independent of this curated evidence set.
FUNCTIONS = {
  0x0CBB66: "B6 target-angle input conditioning",
  0x0CCF0E: "B6 target-angle scale/continuity stage",
  0x0CCFB2: "B6 target-angle supervisor staging",
  0x0CEFFC: "Target Lateral ID to controller bank",
  0x0CE384: "default-bank versus B6-bank controller dispatch",
  0x0CDFD4: "B6-bank controller aggregate",
  0x0CD128: "target-minus-measured B6 controller",
  0x0CDFF8: "mode-selected B6 supervisor",
  0x0CE144: "mode-selected B6 supervisor",
  0x0CE6F4: "B6 supervisor consolidation",
  0x0CCDF8: "B6 supervisor output conditioning",
  0x0CF22C: "B6 supervisor source selection to CB08",
  0x0CF148: "B6 supervisor gain state",
  0x0CF276: "mode-bank limits",
  0x0CF2B2: "B6 supervisor ramp to CB38",
  0x0CB73A: "special 0x31 transient gate",
  0x0CBF9E: "local C81A damping/assist addend",
  0x0CBC80: "local measured-angle-rate state",
  0x0D0218: "ordinary assist sum including CB38",
  0x0D0284: "shared command scale/clamp",
  0x0D02DA: "shared command slew/filter",
  0x0D0382: "shared command saturation",
  0x0D039E: "shared base plus local addend composition",
  0x0D042C: "shared pre-slew command output",
  0x0D06D6: "internal override aggregate",
  0x0D0674: "internal CC94/CC98 override writer",
  0x0D047C: "shared post-slew/override output",
  0x0D0AAE: "shared command snapshot",
  0x0BF33E: "command-model/current mirror",
  0x0D0EEC: "B6 supervisor cyclic coordinator",
  0x0D1130: "B6 supervisor coordinator wrapper",
  0x0BCD62: "input snapshot plus B6 supervisor invocation",
  0x0D0AF6: "shared command-composition coordinator",
  0x0D1100: "shared command-composition wrapper",
  0x0BCD02: "shared snapshot plus command-composition invocation",
  0x0C1F7A: "state transition command-composition caller",
  0x0C2000: "steady-state command-composition caller",
  0x05899E: "state-transition/steady-state scheduler",
  0x035C4C: "motor-driving EE40C consumer",
}


def sha256(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def load_corpus() -> dict[int, dict[str, Any]]:
  out: dict[int, dict[str, Any]] = {}
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") == "function":
        out[int(rec["entry_addr"], 16)] = rec
  return out


def body_bytes(image: bytes, rec: dict[str, Any]) -> bytes:
  chunks: list[bytes] = []
  for rr in rec["body_ranges"]:
    if rr["space"] != "ram":
      raise RuntimeError(f"non-CodeFlash body range in {rec['entry_addr']}")
    lo = int(rr["min"], 16)
    hi = int(rr["max"], 16)
    chunks.append(image[lo:hi + 1])
  return b"".join(chunks)


def refs_to(corpus: dict[int, dict[str, Any]], target: int) -> list[dict[str, str]]:
  refs: list[dict[str, str]] = []
  for entry, rec in sorted(corpus.items()):
    for ref in rec.get("data_references", []):
      try:
        to_addr = int(ref["to_addr"], 16)
      except (KeyError, ValueError):
        continue
      if to_addr == target:
        refs.append({
          "function": f"0x{entry:06X}",
          "from": ref["from_addr"],
          "type": ref["ref_type"],
        })
  return refs


def funcs_referencing(corpus: dict[int, dict[str, Any]], token: str) -> list[int]:
  return sorted(entry for entry, rec in corpus.items() if token in rec.get("decompiled_c", ""))


def analyze() -> dict[str, Any]:
  image = IMAGE.read_bytes()
  image_sha = sha256(image)
  if image_sha != EXPECTED_SHA256:
    raise RuntimeError(f"exact F33 CodeFlash SHA mismatch: {image_sha}")
  corpus = load_corpus()
  if len(corpus) != 6065:
    raise RuntimeError(f"canonical corpus function count drift: {len(corpus)}")
  missing = set(FUNCTIONS) - set(corpus)
  if missing:
    raise RuntimeError(f"missing semantic functions: {[hex(x) for x in sorted(missing)]}")

  f = {entry: corpus[entry]["decompiled_c"] for entry in FUNCTIONS}

  # Exhaustive selector census: every function in the complete 6065-function
  # corpus containing CB00/ADB0, plus exact direct references.
  cb00_funcs = funcs_referencing(corpus, "DAT_febecb00")
  adb0_funcs = funcs_referencing(corpus, "DAT_febeadb0")
  cb00_refs = refs_to(corpus, CB00)
  adb0_refs = refs_to(corpus, ADB0)
  ae90_refs = refs_to(corpus, AE90)

  # Exhaust every writer/read of the shared command cone.  This is stronger
  # than enumerating expected functions by hand: new aliases/writers drift the
  # generated artifact and fail the verifier.
  funnel_refs = {name: refs_to(corpus, addr) for name, addr in FINAL_CELLS.items()}
  funnel_writers = {
    name: sorted({r["function"] for r in refs if r["type"] == "WRITE"})
    for name, refs in funnel_refs.items()
  }

  # Exhaustively classify all CB00-aware functions, then check whether any directly touches the
  # shared final command cells.  None should: CB00 terminates in the B6
  # supervisor, which contributes via CB38 before D0218.
  partition_flat = set().union(*CB00_PARTITION.values())
  partition_overlap = sum(len(v) for v in CB00_PARTITION.values()) - len(partition_flat)
  if partition_overlap or partition_flat != set(cb00_funcs):
    raise RuntimeError(
      f"CB00 semantic partition drift: overlap={partition_overlap} "
      f"missing={[hex(x) for x in sorted(set(cb00_funcs) - partition_flat)]} "
      f"extra={[hex(x) for x in sorted(partition_flat - set(cb00_funcs))]}"
    )
  cb00_partition = {
    name: [f"0x{x:06X}" for x in sorted(entries)]
    for name, entries in CB00_PARTITION.items()
  }

  cb00_final_refs: dict[str, list[str]] = {}
  for entry in cb00_funcs:
    rec = corpus[entry]
    touched: list[str] = []
    for ref in rec.get("data_references", []):
      try:
        target = int(ref["to_addr"], 16)
      except (KeyError, ValueError):
        continue
      for name, addr in FINAL_CELLS.items():
        if target == addr:
          touched.append(f"{name}:{ref['ref_type']}")
    if touched:
      cb00_final_refs[f"0x{entry:06X}"] = sorted(set(touched))

  function_evidence: dict[str, Any] = {}
  for entry, role in FUNCTIONS.items():
    rec = corpus[entry]
    body = body_bytes(image, rec)
    function_evidence[f"0x{entry:06X}"] = {
      "role": role,
      "body_size": len(body),
      "body_sha256": sha256(body),
      "decompiled_c_sha256": rec["decompiled_c_sha256"],
    }

  # Semantic predicates are all mechanically checked against the canonical
  # decompilation, while body hashes bind those statements to exact CodeFlash.
  semantic_checks = {
    "id11_maps_to_bank2": (
      "DAT_febeadb0 == '\\v'" in f[0xCEFFC]
      and "DAT_febecb00 = 2;" in f[0xCEFFC]
      and "DAT_febecb00 = 7;" in f[0xCEFFC]
    ),
    "only_adb0_runtime_readers_are_bank_decode_and_special_transient": (
      sorted({r["function"] for r in adb0_refs if r["type"] == "READ"})
      == ["0x0CB73A", "0x0CEFFC"]
    ),
    "id11_does_not_arm_special_transient": (
      "DAT_febeadb0 == '1'" in f[0xCB73A]
      and "DAT_febeadb0 == '1'" not in f[0xCEFFC]
    ),
    "b6_angle_enters_supervisor": (
      "DAT_febeae90" in f[0xCBB66]
      and "DAT_febeae90 * 2" in f[0xCCF0E]
      and all(x in f[0xCCF0E] for x in ("DAT_febec8b4", "DAT_febec99c", "DAT_febec9c8"))
      and all(x in f[0xCCFB2] for x in ("DAT_febec8b4", "DAT_febec8b8", "DAT_febec9a0", "DAT_febec9cc"))
      and all(x in f[0xCD128] for x in ("DAT_febec8b8", "DAT_febec9a0", "DAT_febec9cc", "DAT_febecb00"))
    ),
    "bank2_uses_b6_controller_not_default_branch": (
      "(DAT_febecb00 & 7) == 7" in f[0xCE384]
      and "FUN_000cdfd4();" in f[0xCE384]
      and "FUN_000cdff8();" in f[0xCE384]
      and "FUN_000ce144();" in f[0xCE384]
    ),
    "b6_supervisor_reaches_cb38": (
      all(x in f[0xCCDF8] for x in ("DAT_febecaa6", "DAT_febecaa8", "DAT_febecaaa"))
      and "DAT_febecb08" in f[0xCF22C]
      and all(x in f[0xCF2B2] for x in ("DAT_febecb08", "DAT_febecb20", "DAT_febecb38"))
    ),
    "d0218_adds_cb38_to_ordinary_terms": (
      all(x in f[0xD0218] for x in (
        "DAT_febec43c", "DAT_febec4c0", "DAT_febec3ba", "DAT_febecc2c",
        "DAT_febebf3c", "DAT_febecb38", "DAT_febec5ee", "DAT_febecbe8", "DAT_febecc48"
      ))
    ),
    "shared_command_coordinator_always_calls_same_funnel": (
      all(f"FUN_{entry:08x}();" in f[0xD0AF6] for entry in (0xD0218, 0xD0284, 0xD02DA, 0xD0382, 0xD039E, 0xD042C, 0xD06D6, 0xD047C, 0xD0AAE))
      and "DAT_febecb00" not in f[0xD0AF6]
      and "DAT_febeadb0" not in f[0xD0AF6]
    ),
    "d039e_retains_shared_base_and_local_addend": (
      "FUN_000cb9c8()" in f[0xD039E]
      and "FUN_000cb9ae()" in f[0xD039E]
      and "puVar3 + 0x101a" in f[0xD039E]  # C81A
      and "puVar3 + 0x1460" in f[0xD039E]  # CC60
      and "puVar3 + 0x1450" in f[0xD039E]  # CC50
    ),
    "c81a_is_local_not_raw_b6_target": (
      "DAT_febec172" in f[0xCBF9E]
      and "DAT_febec81a" in f[0xCBF9E]
      and "DAT_febeadb0" not in f[0xCBF9E]
      and "DAT_febeae90" not in f[0xCBF9E]
    ),
    "no_cb00_function_directly_writes_or_reads_final_funnel": not cb00_final_refs,
    "post_slew_override_is_internal_not_b6_selected": (
      all(x in f[0xD047C] for x in ("DAT_febecc66", "DAT_febecc94", "DAT_febecc98", "DAT_febecc64"))
      and "DAT_febecb00" not in f[0xD047C] and "DAT_febeadb0" not in f[0xD047C]
      and "DAT_febecb00" not in f[0xD0674] and "DAT_febeadb0" not in f[0xD0674]
    ),
    "motor_snapshot_uses_same_cc64": (
      "DAT_febeac54 = DAT_febecc64;" in f[0xD0AAE]
      and "DAT_febee40c = DAT_febeac54;" in f[0xBF33E]
      and "DAT_febe6af4 = -sVar1;" in f[0x35C4C]
      and "DAT_febee40c" in f[0x35C4C]
    ),
    "b6_supervisor_and_shared_composition_have_distinct_wrappers": (
      "FUN_000d0eec();" in f[0xD1130]
      and "FUN_000d1130();" in f[0xBCD62]
      and "FUN_000d0af6();" in f[0xD1100]
      and "FUN_000d1100();" in f[0xBCD02]
    ),
  }
  if not all(semantic_checks.values()):
    bad = [k for k, v in semantic_checks.items() if not v]
    raise RuntimeError(f"semantic composition checks failed: {bad}")

  expected_writers = {
    "CC48": ["0x0D01B4", "0x0D0218"],
    "CC4C": ["0x0D01B4", "0x0D0284"],
    "CC4E": ["0x0D01B4", "0x0D02DA"],
    "CC60": ["0x0D01B4", "0x0D0382"],
    "CC50": ["0x0D01B4", "0x0D039E"],
    "CC62": ["0x0D01B4", "0x0D042C"],
    "CC64": ["0x0D01B4", "0x0D047C"],
    "AC54": ["0x0BF97A", "0x0D0AAE"],
    "EE40C": ["0x0BF33E", "0x0BF97A"],
  }
  if funnel_writers != expected_writers:
    raise RuntimeError(f"shared funnel writer census drift: {funnel_writers}")

  return {
    "schema": "camry-f33-b6-command-composition-v1",
    "target": {
      "software_id": "8965F3307000",
      "codeflash_sha256": image_sha,
      "corpus_function_count": len(corpus),
    },
    "function_evidence": function_evidence,
    "selector_census": {
      "CB00_address": f"0x{CB00:08X}",
      "CB00_decompiled_function_count": len(cb00_funcs),
      "CB00_decompiled_functions": [f"0x{x:06X}" for x in cb00_funcs],
      "CB00_semantic_partition": cb00_partition,
      "CB00_semantic_partition_counts": {name: len(entries) for name, entries in cb00_partition.items()},
      "CB00_direct_references": cb00_refs,
      "ADB0_address": f"0x{ADB0:08X}",
      "ADB0_decompiled_functions": [f"0x{x:06X}" for x in adb0_funcs],
      "ADB0_direct_references": adb0_refs,
      "AE90_direct_references": ae90_refs,
      "CB00_final_funnel_direct_references": cb00_final_refs,
    },
    "shared_funnel_writer_census": funnel_writers,
    "shared_funnel_direct_references": funnel_refs,
    "semantic_checks": semantic_checks,
    "exact_path": [
      "B6 sig261 ADB0=0x0B -> CEFFC -> CB00=2",
      "B6 sig262 AE90 -> CBB66/CCF0E/CCFB2 -> CD128 target-minus-measured controller",
      "CDFD4/CDFF8/CE144 -> CE6F4 -> CCDF8 -> CF22C -> CF2B2 -> CB38",
      "D0218: ordinary terms + clamp(CB38 + C5EE) -> CC48",
      "D0284 -> CC4C -> D02DA -> CC4E -> D0382 -> CC60",
      "D039E: shared CC60/history base + local C81A addend -> CC50",
      "D042C -> CC62/CC66 -> D047C -> CC64 -> D0AAE -> AC54 -> BF33E -> EE40C",
      "35C4C consumes EE40C into the physical current-control side",
    ],
    "special_transient": {
      "gate_function": "0x0CB73A",
      "required_ADB0_literal": "0x31",
      "id11_literal": "0x0B",
      "same": False,
      "consequence": "the C7BF special transient that can change the ordinary sum is not the ID11 B6 path",
    },
    "proof": {
      "accepted_id11_selects_exclusive_b6_motor_path": False,
      "accepted_id11_replaces_shared_command_funnel": False,
      "accepted_id11_contributes_via_cb38_inside_ordinary_d0218_sum": True,
      "ordinary_eps_terms_remain_in_id11_composition": True,
      "later_id11_specific_final_command_override_recovered": False,
      "all_cb00_aware_functions_exhausted": True,
      "all_cb00_aware_functions_partitioned_nonoverlapping": True,
      "all_shared_funnel_direct_writers_exhausted": True,
      "conclusion": (
        "Accepted B6 Target Lateral ID11 is a co-modulating input to the ordinary EPS command composition, not an exclusive replacement path. "
        "ID11 selects bank2, its target-angle controller reaches CB38, and D0218 adds CB38 inside the ordinary assist sum before the single shared CC48->CC64/current funnel. "
        "The only special transient that can alter that sum requires ADB0==0x31, not ID11 0x0B. No CB00/ADB0-selected writer exists later in the final command funnel."
      ),
      "stock_request_plane_boundary": (
        "This proves EPS-side composition. It does not mean F33 literally adds the upstream 0x08A angle: exact F33 receives neither 0x08A nor 0x081. "
        "The Toyota/FRC request-to-chassis authority handoff is a separate upstream/local provenance question."
      ),
    },
  }


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()
  result = analyze()
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
  print(f"camry F33 B6 command composition: {result['proof']['conclusion']}")


if __name__ == "__main__":
  main()
