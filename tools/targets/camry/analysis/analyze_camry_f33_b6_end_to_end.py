#!/usr/bin/env python3
"""Build the exact 8965F3307000 protected-B6 end-to-end execution map.

The reducer deliberately spans transport, SecOC, PduR/COM, application staging,
cooperative-controller supervision, shared steering-command composition, and the
proved motor-current boundary. It also emits an ordered live witness ladder so a
single capture can identify the first stage at which an injected B6 disappears.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
DEFAULT_OUT = ROOT / "data/generated/camry_f33_b6_end_to_end.json"
EXPECTED_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

# Stock functions that establish every software stage after CanIf/PduR mapping.
FUNCTIONS = {
  0x04BD46: "generated-COM PDU44 application unpacker",
  0x058074: "generated-COM stage copier",
  0x05899E: "shared command task coordinator",
  0x058B5E: "generated-COM/application task coordinator",
  0x0572E6: "internal steering actuator-state aggregate producer",
  0x05DF5C: "motor-model scheduler aggregate",
  0x07D800: "route44 configured guard",
  0x081CA6: "PduR upper-route dispatcher",
  0x088FC0: "ICU-S operation descriptor builder",
  0x089646: "ICU-S command dispatcher",
  0x089C98: "ICU-S synchronous operation wrapper",
  0x08E772: "COM route generation/age update",
  0x08E9C6: "SecOC level-1 queue insert/copy",
  0x08ECB2: "SecOC authentication-input builder",
  0x08EE7C: "SecOC secured-PDU ingress",
  0x08F19A: "authenticated sync snapshot",
  0x08F34A: "SecOC receive-state/queue wrapper",
  0x08F434: "FV4/MAC28 extractor",
  0x08F546: "verified upper-PDU delivery",
  0x08F676: "ICU-S verify wrapper",
  0x08F746: "SecOC verification coordinator",
  0x08F8D2: "post-crypto profile callback dispatcher",
  0x08F906: "root result / Gate-2 coordinator",
  0x090204: "upper PduR indication shim",
  0x090248: "freshness slot resolver",
  0x0909CA: "reset-counter candidate search",
  0x090A48: "message-counter/freshness reconstruction",
  0x090B1C: "same-epoch freshness comparison",
  0x090B8A: "freshness candidate selector",
  0x090D6A: "pending-to-committed freshness commit",
  0x0B330A: "diagnostic/service branch clear API",
  0x0B338C: "diagnostic/service branch set API",
  0x0B4B6C: "common command output-scale ramp",
  0x0B4EF4: "common command output-scale coordinator",
  0x0BCAA6: "common steering actuator-enable/inhibit decoder",
  0x0BCBD8: "common command-state snapshot",
  0x0BCD02: "shared command snapshot/coordinator wrapper",
  0x0BCD62: "application snapshot + cooperative-controller wrapper",
  0x0BF33E: "command/current mirror",
  0x0C1F7A: "transition-mode command task",
  0x0C2000: "steady-mode command task",
  0x0CB2A2: "B6 route-health readiness flags",
  0x0CB664: "special-0x31 transient companion qualification",
  0x0CB73A: "special-0x31 transient activation state",
  0x0CBB66: "B6 target-angle conditioning",
  0x0CCDF8: "cooperative supervisor output conditioning",
  0x0CCF0E: "B6 target-angle scale/continuity",
  0x0CCFB2: "B6 target-angle per-step limiter",
  0x0CD128: "target-minus-measured controller",
  0x0CDA20: "B6 sig265-controlled supervisor term",
  0x0CDFF8: "B6 sig270-weighted supervisor",
  0x0CE144: "bank-selected cooperative supervisor",
  0x0CE3AA: "B6 sig269-weighted supervisor",
  0x0CE51C: "cooperative supervisor limit selection",
  0x0CE594: "cooperative supervisor shaping",
  0x0CE6F4: "cooperative supervisor consolidation",
  0x0CE772: "cooperative readiness permissive helper",
  0x0CE7A6: "cooperative readiness inhibit helper",
  0x0CE7FE: "cooperative readiness state",
  0x0CE836: "cooperative activation/ramp state",
  0x0CEC8A: "B6 application sequence delta",
  0x0CECD6: "sequence-dependent persistence state",
  0x0CEE20: "cooperative threshold dwell aggregate",
  0x0CEE7C: "cooperative target-angle inhibit synthesis",
  0x0CEF26: "cooperative persistence/fault supervisor",
  0x0CEFA4: "B6 profile health synthesis",
  0x0CEFFC: "Target Lateral ID to cooperative bank",
  0x0CF0B6: "cooperative gain-state selector",
  0x0CF0EA: "cooperative gain-rate calibration load",
  0x0CF148: "cooperative gain ramp CB20",
  0x0CF22C: "cooperative controller output select CB08",
  0x0CF276: "cooperative output slew/magnitude limits",
  0x0CF2B2: "final cooperative contribution CB38",
  0x0CFDA0: "B6 sig273 health-qualified publication",
  0x0FCC00: "internal system-state snapshot to EEF90",
  0x0D0218: "ordinary EPS command sum",
  0x0D0284: "shared command scale/clamp",
  0x0D02DA: "shared command filter/slew",
  0x0D0382: "shared command saturation",
  0x0D039E: "shared command + local damping composition",
  0x0D042C: "shared output scaling + common actuator gate",
  0x0D047C: "internal post-gate override",
  0x0D04F0: "internal override state initialization",
  0x0D0528: "internal override trigger",
  0x0D05B4: "internal override monitor",
  0x0D064C: "internal override debounce",
  0x0D0674: "internal override output construction",
  0x0D06D6: "internal override aggregate",
  0x0D0AAE: "shared command snapshot",
  0x0D0AF6: "shared command aggregate",
  0x0D0EEC: "cooperative-controller aggregate",
  0x0D1100: "shared command wrapper",
  0x0D1130: "cooperative-controller wrapper",
  0x035C4C: "EE40C motor-side selection",
  0x0387BA: "selected command to motor current model",
  0x038502: "motor-current command magnitude map",
  0x03835E: "motor-current bound stage",
  0x0384D8: "signed motor-current command stage",
  0x038162: "downstream motor-current processing",
  0x065FEA: "shared command cyclic task root",
  0x066062: "communications/application cyclic task root",
  0x06679E: "shared command task wrapper",
  0x0667E6: "communications/application aggregate",
}

# Exact recovered bodies that are not canonical function entries in the older corpus.
RAW_RANGES = {
  "rscfd_common_fifo_rx_callback": (0x400A, 0x4060),
  "CanIf_RxIndication": (0x4678, 0x48FC),
  "freshness_callback_0x903A0": (0x903A0, 0x903F6),
  "post_crypto_callback_0x90448": (0x90448, 0x90482),
  "route44_callback_0x7D72C": (0x7D72C, 0x7D800),
  "icu_command0_start_0x891CC": (0x891CC, 0x892CC),
  "icu_command0_completion_0x892CC": (0x892CC, 0x89386),
}

FIELD_MAP = [
  {"signal": 261, "wire": "B3[5:0]", "raw": "FEBE80BC", "stage": "FEBEF130", "snapshot": "FEBEADB0", "role": "Target Lateral ID"},
  {"signal": 262, "wire": "B4:B5 s16BE", "raw": "FEBE80B8", "stage": "FEBEF1FA", "snapshot": "FEBEAE90", "role": "target steering angle"},
  {"signal": 263, "wire": "B6[7]", "raw": "FEBE80CB", "stage": "FEBEF155", "snapshot": "FEBEADDD", "role": "special-0x31 transient companion; not a normal ID11 bank-admission requirement"},
  {"signal": 264, "wire": "B6[6:4]", "raw": "FEBE80BE", "stage": "FEBEF132", "snapshot": "FEBEADB1", "role": "snapshotted companion; no runtime reader recovered"},
  {"signal": 265, "wire": "B6[2]", "raw": "FEBE80C0", "stage": "FEBEF134", "snapshot": "FEBEADBB", "role": "additive-term suppression companion"},
  {"signal": 266, "wire": "B6[1:0]", "raw": "FEBE80C1", "stage": "FEBEF135", "snapshot": None, "role": "companion state"},
  {"signal": 267, "wire": "B7[7:6]", "raw": "FEBE80C2", "stage": "FEBEF136", "snapshot": "FEBEADC2", "role": "snapshotted companion; no runtime reader recovered"},
  {"signal": 268, "wire": "B7[5:0]", "raw": "FEBE80C3", "stage": "FEBEF137", "snapshot": "FEBEADBC", "role": "application modulo-64 sequence"},
  {"signal": 269, "wire": "B8", "raw": "FEBE80C4", "stage": "FEBEF138", "snapshot": "FEBEADBD", "role": "cooperative supervisor percentage"},
  {"signal": 270, "wire": "B9", "raw": "FEBE80C5", "stage": "FEBEF139", "snapshot": "FEBEADBE", "role": "cooperative supervisor percentage"},
  {"signal": 271, "wire": "B10[7]", "raw": "FEBE80C6", "stage": "FEBEF13A", "snapshot": "FEBEADC1", "role": "snapshotted companion; no runtime reader recovered"},
  {"signal": 272, "wire": "B10[5]", "raw": "FEBE80C7", "stage": "FEBEF13C", "snapshot": "FEBEADE5", "role": "snapshotted companion; no runtime reader recovered"},
  {"signal": 273, "wire": "B10[2:0]", "raw": "FEBE80CA", "stage": "FEBEF14D", "snapshot": "FEBEADD9", "role": "health-qualified publication companion"},
]


def h(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def u16(image: bytes, off: int) -> int:
  return struct.unpack_from("<H", image, off)[0]


def u32(image: bytes, off: int) -> int:
  return struct.unpack_from("<I", image, off)[0]


def load_corpus() -> dict[int, dict[str, Any]]:
  out: dict[int, dict[str, Any]] = {}
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") == "function":
        out[int(rec["entry_addr"], 16)] = rec
  return out


def body_bytes(image: bytes, rec: dict[str, Any]) -> bytes:
  data = bytearray()
  for r in rec["body_ranges"]:
    assert r["space"] == "ram"
    lo, hi = int(r["min"], 16), int(r["max"], 16)
    data.extend(image[lo:hi + 1])
  return bytes(data)


def refs_to(corpus: dict[int, dict[str, Any]], target: int, ref_type: str | None = None) -> list[dict[str, str]]:
  out: list[dict[str, str]] = []
  for entry, rec in sorted(corpus.items()):
    for ref in rec.get("data_references", []):
      try:
        to_addr = int(ref["to_addr"], 16)
      except (KeyError, ValueError):
        continue
      if to_addr != target or (ref_type is not None and ref.get("ref_type") != ref_type):
        continue
      out.append({"function": f"0x{entry:06X}", "from": ref["from_addr"], "type": ref["ref_type"]})
  return out


def writer_functions(corpus: dict[int, dict[str, Any]], target: int) -> list[str]:
  return sorted({r["function"] for r in refs_to(corpus, target, "WRITE")})


def reader_functions(corpus: dict[int, dict[str, Any]], target: int) -> list[str]:
  return sorted({r["function"] for r in refs_to(corpus, target, "READ")})


def addr(text: str | None) -> int | None:
  return None if text is None else int(text, 16)


def analyze() -> dict[str, Any]:
  image = IMAGE.read_bytes()
  if h(image) != EXPECTED_SHA256:
    raise RuntimeError("exact F33 CodeFlash identity drift")
  corpus = load_corpus()
  if len(corpus) != 6065:
    raise RuntimeError(f"canonical corpus function count drift: {len(corpus)}")
  missing = sorted(set(FUNCTIONS) - set(corpus))
  if missing:
    raise RuntimeError(f"missing functions: {[hex(x) for x in missing]}")
  c = {a: corpus[a]["decompiled_c"] for a in FUNCTIONS}

  # Raw configuration joins from exact CodeFlash.
  canif_desc = image[0x21FE8 + 39 * 8:0x21FE8 + 40 * 8]
  route44 = image[0x226C0 + 44 * 8:0x226C0 + 45 * 8]
  exact_config = {
    "rscfd_controller1_rule": 39,
    "canif_descriptor_index": 39,
    "canif_descriptor_hex": canif_desc.hex(),
    "canif_id": f"0x{u32(image, 0x21FE8 + 39 * 8):08X}",
    "canif_length": u16(image, 0x21FE8 + 39 * 8 + 4),
    "pdur_route_base": image[0x21A48],
    "pdur_route": 44,
    "pdur_route_selector": image[0x21FB8 + 44],
    "route44_record_hex": route44.hex(),
    "route44_length": route44[4],
    "route44_flags": route44[7],
    "route44_raw_window_offset": f"0x{u16(image, 0x22840 + 44 * 2):03X}",
    "route44_guard_ptr": f"0x{u32(image, 0x21E08):06X}",
    "secoc_profile": 2,
    "secoc_queue_record": "0xFEBE547A",
    "secoc_secured_buffer": "0xFEBE54D4",
    "secoc_min_trailer_bytes": u16(image, 0x258EE),
    "secoc_selector": u16(image, 0x258FE),
  }
  if exact_config["canif_id"] != "0x400000B6" or exact_config["canif_length"] != 32:
    raise RuntimeError(f"B6 CanIf descriptor drift: {exact_config}")
  if route44.hex() != "060000002000000c" or exact_config["route44_raw_window_offset"] != "0x1B7":
    raise RuntimeError("route44 configuration drift")
  if exact_config["secoc_min_trailer_bytes"] != 4 or exact_config["secoc_selector"] != 0:
    raise RuntimeError("B6 SecOC ingress config drift")

  # Freshness-profile table: record0 is the special synchronized source; ordinary
  # records 1/2 compact to freshness slots 0/1. B6 is record2/FreshnessId2 -> slot1.
  profile_base = 0x23DFC + 0x1A40
  profile_records = []
  ordinary_slot = 0
  b6_freshness_slot = None
  for index in range(3):
    rec = profile_base + index * 0x50
    special = image[rec + 0x15]
    freshness_id = u16(image, rec + 0x1E)
    slot = None if special == 1 else ordinary_slot
    if special != 1:
      if freshness_id == 2:
        b6_freshness_slot = ordinary_slot
      ordinary_slot += 1
    profile_records.append({
      "index": index,
      "address": f"0x{rec:06X}",
      "special": special,
      "freshness_id": freshness_id,
      "ordinary_slot": slot,
      "sha256": h(image[rec:rec + 0x50]),
    })
  if [(r["special"], r["freshness_id"], r["ordinary_slot"]) for r in profile_records] != [(1, 0, None), (0, 1, 0), (0, 2, 1)]:
    raise RuntimeError(f"freshness profile table drift: {profile_records}")

  # Exhaustive raw -> staging -> snapshot direct-reference census. The application
  # code does not have a hidden whole-PDU consumer after generated COM: every known
  # B6 scalar can be followed independently, including the secondary fields that die.
  raw_stage_snapshot_census: list[dict[str, Any]] = []
  for field in FIELD_MAP:
    row: dict[str, Any] = {"signal": field["signal"], "role": field["role"]}
    for layer in ("raw", "stage", "snapshot"):
      text = field[layer]
      if text is None:
        row[layer] = None
        continue
      target = int(text, 16)
      row[layer] = {
        "address": f"0x{target:08X}",
        "readers": reader_functions(corpus, target),
        "writers": writer_functions(corpus, target),
        "references": refs_to(corpus, target),
      }
    raw_stage_snapshot_census.append(row)

  snapshot_reader_expectations = {
    261: ["0x0CB73A", "0x0CEFFC"],
    262: ["0x0CBA80", "0x0CBB66", "0x0CCF0E", "0x0CEE7C"],
    263: ["0x0CB664"],
    264: [],
    265: ["0x0CDA20"],
    267: [],
    268: ["0x0CEC8A"],
    269: ["0x0CE3AA"],
    270: ["0x0CDFF8"],
    271: [],
    272: [],
    273: ["0x0CFDA0"],
  }
  for row in raw_stage_snapshot_census:
    sig = row["signal"]
    if sig == 266:
      if row["snapshot"] is not None:
        raise RuntimeError("signal266 unexpectedly gained a snapshot")
      continue
    if row["snapshot"]["readers"] != snapshot_reader_expectations[sig]:
      raise RuntimeError(f"signal{sig} snapshot reader drift: {row['snapshot']['readers']}")

  key_cells = {
    "CB00_bank": 0xFEBECB00,
    "CB20_gain": 0xFEBECB20,
    "CB38_b6_contribution": 0xFEBECB38,
    "CC48_sum": 0xFEBECC48,
    "CC4C_scaled": 0xFEBECC4C,
    "CC4E_filtered": 0xFEBECC4E,
    "CC60_limited": 0xFEBECC60,
    "CC50_pre_scale": 0xFEBECC50,
    "CC62_scaled": 0xFEBECC62,
    "CC66_gated": 0xFEBECC66,
    "CC64_selected": 0xFEBECC64,
    "AC54_motor_snapshot": 0xFEBEAC54,
    "EE40C_motor_mirror": 0xFEBEE40C,
    "6AF4_motor_selected": 0xFEBE6AF4,
    "6E0A_motor_model_input": 0xFEBE6E0A,
    "6DEC_current_bound": 0xFEBE6DEC,
    "6DC8_current_component": 0xFEBE6DC8,
    "6DD6_signed_current_component": 0xFEBE6DD6,
  }
  writer_census = {name: writer_functions(corpus, target) for name, target in key_cells.items()}
  expected_writers = {
    "CB00_bank": ["0x0CEFF4", "0x0CEFFC"],
    "CB20_gain": ["0x0CF056", "0x0CF148"],
    "CB38_b6_contribution": ["0x0CF056", "0x0CF2B2"],
    "CC48_sum": ["0x0D01B4", "0x0D0218"],
    "CC4C_scaled": ["0x0D01B4", "0x0D0284"],
    "CC4E_filtered": ["0x0D01B4", "0x0D02DA"],
    "CC60_limited": ["0x0D01B4", "0x0D0382"],
    "CC50_pre_scale": ["0x0D01B4", "0x0D039E"],
    "CC62_scaled": ["0x0D01B4", "0x0D042C"],
    "CC66_gated": ["0x0D01B4", "0x0D042C"],
    "CC64_selected": ["0x0D01B4", "0x0D047C"],
    "AC54_motor_snapshot": ["0x0BF97A", "0x0D0AAE"],
    "EE40C_motor_mirror": ["0x0BF33E", "0x0BF97A"],
    "6AF4_motor_selected": ["0x035C4C", "0x059448"],
    "6E0A_motor_model_input": ["0x0387BA", "0x059448"],
    "6DEC_current_bound": ["0x038502", "0x059448"],
    "6DC8_current_component": ["0x03835E", "0x059448"],
    "6DD6_signed_current_component": ["0x0384D8", "0x059448"],
  }
  if writer_census != expected_writers:
    raise RuntimeError(f"end-to-end writer census drift: {writer_census}")

  gate_source_census = {
    "AC2B_diag_gate": {"address": "0xFEBEAC2B", "writers": writer_functions(corpus, 0xFEBEAC2B), "readers": reader_functions(corpus, 0xFEBEAC2B)},
    "B112_diag_source": {"address": "0xFEBEB112", "writers": writer_functions(corpus, 0xFEBEB112), "readers": reader_functions(corpus, 0xFEBEB112)},
    "AC5A_output_scale": {"address": "0xFEBEAC5A", "writers": writer_functions(corpus, 0xFEBEAC5A), "readers": reader_functions(corpus, 0xFEBEAC5A)},
    "B1F8_output_scale_source": {"address": "0xFEBEB1F8", "writers": writer_functions(corpus, 0xFEBEB1F8), "readers": reader_functions(corpus, 0xFEBEB1F8)},
    "AC29_enable": {"address": "0xFEBEAC29", "writers": writer_functions(corpus, 0xFEBEAC29), "readers": reader_functions(corpus, 0xFEBEAC29)},
    "AC2A_inhibit": {"address": "0xFEBEAC2A", "writers": writer_functions(corpus, 0xFEBEAC2A), "readers": reader_functions(corpus, 0xFEBEAC2A)},
    "8B28_internal_status": {"address": "0xFEBE8B28", "writers": writer_functions(corpus, 0xFEBE8B28), "readers": reader_functions(corpus, 0xFEBE8B28)},
    "EEF90_internal_status_snapshot": {"address": "0xFEBEEF90", "writers": writer_functions(corpus, 0xFEBEEF90), "readers": reader_functions(corpus, 0xFEBEEF90)},
    "CC98_override_mode": {"address": "0xFEBECC98", "writers": writer_functions(corpus, 0xFEBECC98), "readers": reader_functions(corpus, 0xFEBECC98)},
    "CC94_override_value": {"address": "0xFEBECC94", "writers": writer_functions(corpus, 0xFEBECC94), "readers": reader_functions(corpus, 0xFEBECC94)},
  }
  expected_gate_writers = {
    "AC2B_diag_gate": ["0x0BCBD8", "0x0BF97A"],
    "B112_diag_source": ["0x0B3314", "0x0B338C", "0x0BF97A"],
    "AC5A_output_scale": ["0x0BCBD8", "0x0BF97A"],
    "B1F8_output_scale_source": ["0x0B4B6C", "0x0B4EF4", "0x0BF97A"],
    "AC29_enable": ["0x0BCAA6", "0x0BF97A"],
    "AC2A_inhibit": ["0x0BCAA6", "0x0BF97A"],
    "8B28_internal_status": ["0x0572E6", "0x059448"],
    "EEF90_internal_status_snapshot": ["0x0FCC00"],
    "CC98_override_mode": ["0x0D04F0", "0x0D0528", "0x0D0674"],
    "CC94_override_value": ["0x0D0674"],
  }
  for name, expected in expected_gate_writers.items():
    if gate_source_census[name]["writers"] != expected:
      raise RuntimeError(f"{name} writer drift: {gate_source_census[name]['writers']}")

  checks = {
    "secoc_ingress_state_and_pointer_checks": all(x in c[0x8EE7C] for x in ("DAT_febe54f4 == -0x1ff", "param_2 != (int *)0x0", "FUN_0008f34a")),
    "queue_wrapper_calls_insert": "FUN_0008e9c6(1" in c[0x8F34A],
    "queue_insert_copies_secured_payload": "FUN_00089f2e(local_34 + iStack_20,*param_3);" in c[0x8E9C6] and "*puVar1 = *(undefined2 *)(param_3 + 1);" in c[0x8E9C6],
    "worker_extracts_auth_then_freshness_then_crypto": all(x in c[0x8F746] for x in ("FUN_0008f434", "FUN_0008ecb2", "FUN_0008f676")),
    "freshness_profile2_slot1": b6_freshness_slot == 1 and all(x in c[0x90248] for x in ("param_1 == *(short *)(iVar2 + 0x1a5e)", "*(char *)(iVar2 + 0x1a55) != '\\x01'", "sVar8 = sVar8 + 1")),
    "freshness_candidate_search_has_plus_minus_two": all(x in c[0x909CA] for x in ("+ 1", "- 1", "+ 2", "- 2")),
    "upper_delivery_reaches_pdur": "FUN_00090204" in c[0x8F546] and "FUN_00081ca6" in c[0x90204],
    "route44_guard_unconditional": "return 1;" in c[0x7D800],
    "route_generation_update": "DAT_febe5338" in c[0x8E772] and "DAT_febe52d8" in c[0x8E772],
    "app_unpack_requires_new_generation_and_global_state": "DAT_febe7f68 < 2" in c[0x4BD46] and "DAT_febe80c8 != DAT_febe5364" in c[0x4BD46],
    "stage_maps_b6_core_fields": all(x in c[0x58074] for x in ("DAT_febef130 = DAT_febe80bc", "DAT_febef1fa = DAT_febe80b8", "DAT_febef138 = DAT_febe80c4", "DAT_febef139 = DAT_febe80c5", "DAT_febef000 = DAT_febe7f68")),
    "snapshot_maps_b6_fields": all(x in c[0xBCD62] for x in ("puVar38[-0xa50] = puVar38[0x3930]", "*(undefined2 *)(puVar38 + -0x970) = *(undefined2 *)(puVar38 + 0x39fa)", "puVar38[-0xa23] = puVar38[0x3955]", "puVar38[-0xa45] = puVar38[0x3934]", "puVar38[-0xa44] = puVar38[0x3937]", "puVar38[-0xa43] = puVar38[0x3938]", "puVar38[-0xa42] = puVar38[0x3939]", "puVar38[-0xa47] = puVar38[0x393e]")),
    "global_com_state_normalizes_to_acbd": all(x in c[0xBCD62] for x in ("cVar1 = puVar38[0x3800]", "cVar21 = cVar1", "cVar21 = '\\x04'", "cVar21 = '\\x01'", "puVar38[-0xb43] = cVar21")) or all(x in c[0xBCD62] for x in ("cVar1 = puVar38[0x3800]", "cVar44 = cVar1", "cVar44 = '\\x04'", "cVar44 = '\\x01'", "puVar38[-0xb43] = cVar44")),
    "b6_health_requires_status_zero": all(x in c[0xCEFA4] for x in ("FUN_000bdb76(0x11)", "FUN_000bdb76(0x1a)", "puVar2[0x12ff] = bVar1 && puVar2[-0xa47] == '\\0'")),
    "id11_maps_bank2_only_when_health_and_acbd_allow": all(x in c[0xCEFFC] for x in ("DAT_febecb00 = 7", "DAT_febeacbd == '\\0'", "DAT_febecaff == '\\x01'", "DAT_febeadb0 == '\\v'", "DAT_febecb00 = 2")),
    "sig263_is_special_0x31_transient_condition_not_id11_gate": all(x in c[0xCB664] for x in ("DAT_febeaddd == '\\0'", "DAT_febeaddd != '\\0'", "DAT_febec7b4")) and all(x in c[0xCB73A] for x in ("DAT_febec7b4", "DAT_febeadb0 == '1'", "DAT_febec7bf = '\\x01'")),
    "sig265_one_suppresses_controller_term": "DAT_febeadbb != '\\x01'" in c[0xCDA20] and "FUN_000d0a06" in c[0xCDA20],
    "route_status_participates_readiness": "puVar4[-0xa47] == '\\0'" in c[0xCB2A2],
    "app_sequence_is_independent_modulo_counter": all(x in c[0xCEC8A] for x in ("DAT_febeadbc", "DAT_febecada", "DAT_000b0620", "DAT_000b0622")),
    "sig270_scales_supervisor": "DAT_febeadbe" in c[0xCDFF8] and "/ 100" in c[0xCDFF8],
    "sig269_scales_supervisor": "DAT_febeadbd" in c[0xCE3AA] and "/ 100" in c[0xCE3AA],
    "sig273_is_health_qualified_publication": "puVar1[0x13f2] = puVar1[-0xa27]" in c[0xCFDA0] and "puVar1[-0xa47] != '\\0'" in c[0xCFDA0],
    "target_controller_is_target_minus_measured": all(x in c[0xCD128] for x in ("DAT_febec8b8", "DAT_febecb00", "DAT_febec8e0")),
    "gain_ramp_exists": all(x in c[0xCF148] for x in ("DAT_febecb20", "DAT_febecb22", "DAT_febecb24", "DAT_febecb26", "DAT_febecb28")),
    "final_b6_term_is_gain_slew_magnitude_limited": all(x in c[0xCF2B2] for x in ("DAT_febecb08", "DAT_febecb20", "DAT_febecb2c", "DAT_febecb2e", "DAT_febecb38")),
    "ordinary_sum_adds_b6_term_only_in_normal_branch": all(x in c[0xD0218] for x in ("DAT_febeac2b == 'Z'", "DAT_febec7bf != '\\x01'", "DAT_febecb38", "DAT_febec5ee", "DAT_febecc48")),
    "ac2b_is_internal_diagnostic_service_gate": "DAT_febeb112 = 0x5a" in c[0xB338C] and "DAT_febeb112 = 0" in c[0xB330A] and "DAT_febeac2b = DAT_febeb112" in c[0xBCBD8],
    "ac5a_is_internal_ramped_scale": "DAT_febeac5a = DAT_febeb1f8" in c[0xBCBD8] and "DAT_febeb1f8" in c[0xB4B6C] and "0x400" in c[0xB4EF4],
    "d042c_multiplies_by_ac5a": "DAT_febecc62 = (short)((int)((int)DAT_febecc50 * (uint)DAT_febeac5a) / 0x400);" in c[0xD042C],
    "common_actuator_gate_can_zero_command": all(x in c[0xD042C] for x in ("DAT_febeac29", "DAT_febeac2a", "DAT_febecc66 = 0")),
    "ac29_ac2a_derive_internal_system_state": "0x70017001" in c[0xBCAA6] and "0x40004" in c[0xBCAA6] and "DAT_febeef90 = DAT_febe8b28" in c[0xFCC00],
    "8b28_is_computed_internal_status_aggregate": "*(uint *)(puVar4 + -0x2cd8) = uVar5" in c[0x572E6] and "FUN_000571b4" in c[0x572E6] and "FUN_0005721c" in c[0x572E6],
    "internal_override_trigger_and_replacement_are_exact": "DAT_febecc98 = uVar7" in c[0xD0528] and "DAT_febecc94 = -DAT_febecc80" in c[0xD0674] and all(x in c[0xD047C] for x in ("DAT_febecc98", "DAT_febecc94", "DAT_febecc64")),
    "motor_side_can_substitute_internal_bounded_source": all(x in c[0x35C4C] for x in ("DAT_febee40c", "DAT_febee780 == 'Z'", "DAT_febee406 == 'Z'", "DAT_febe6af4 = -sVar1")),
    "motor_mirror_path": "DAT_febee40c = DAT_febeac54" in c[0xBF33E] and "DAT_febe6af4 = -sVar1" in c[0x35C4C] and "DAT_febe6e0a = DAT_febe6af4" in c[0x387BA],
    "motor_scheduler_runs_current_chain_in_order": all(f"FUN_{a:08x}();" in c[0x5DF5C] for a in (0x387BA, 0x38502, 0x3835E, 0x384D8, 0x38162)),
    "separate_cyclic_roots": "FUN_0006679e" in c[0x65FEA] and "FUN_000667e6" in c[0x66062],
    "application_task_contains_unpack_stage_snapshot_controller": all(x in c[0x58B5E] for x in ("FUN_0005ec24", "FUN_0005f610")) and "FUN_000d1130" in c[0xBCD62],
    "command_task_contains_common_gate_and_motor_mirror": "FUN_000bcaa6" in c[0xBCD02] and "FUN_000d1100" in c[0xBCD02] and "FUN_000bf33e" in c[0xC2000],
  }
  if not all(checks.values()):
    raise RuntimeError(f"semantic checks failed: {[k for k,v in checks.items() if not v]}")

  gates = [
    {"order": 1, "layer": "physical CAN / CanIf", "site": "RSCFD controller1 rule39 / CanIf descriptor39", "condition": "0x0B6 is physically decoded as the configured 32-byte FD PDU and descriptor/rule match", "failure_effect": "no PduR44/SecOC ingress", "stage5_bypasses": False, "live_witness": "ECU-side SecOC queue; Panda TX echo alone is insufficient"},
    {"order": 2, "layer": "SecOC ingress/queue", "site": "8EE7C -> 8F34A -> 8E9C6", "condition": "SecOC initialized; PduInfo/data/length valid; queue/link geometry accepts and copies the frame", "failure_effect": "profile2 queue/secured bytes do not change", "stage5_bypasses": False, "live_witness": "FEBE547A + FEBE54D4"},
    {"order": 3, "layer": "freshness transaction", "site": "8F746/903A0/90248/909CA/90A48", "condition": "stock: FV4 reconstructs an acceptable profile2 slot1 candidate", "failure_effect": "stock hard-fail/retry; cumulative stage4/5 neutralizes the recovered callback/result failure", "stage5_bypasses": True, "live_witness": "FEBE55E8 committed / FEBE5600 pending + result/budget"},
    {"order": 4, "layer": "ICU-S authentication result", "site": "8F676/89C98/89646/891CC/88FC0 -> ICU-S -> 8F906", "condition": "stock: command submission/completion and CMAC result succeed", "failure_effect": "stock rejects; cumulative stage1/2/3/5 neutralizes every recovered software-visible auth-result consequence", "stage5_bypasses": True, "live_witness": "FEBE5564 + ICU command completion state"},
    {"order": 5, "layer": "upper PduR/COM publication", "site": "8F546 -> 90204 -> 81CA6 -> 7D72C/7D800 -> 8E772", "condition": "delivery callback executes; route44 copy/guard/new-data bookkeeping succeeds", "failure_effect": "raw route44 application window/generation remains stale", "stage5_bypasses": False, "live_witness": "FEBE4BFF..FEBE4C1E + FEBE5364"},
    {"order": 6, "layer": "generated COM unpack", "site": "4BD46", "condition": "FEBE7F68 < 2 and route generation FEBE5364 != local FEBE80C8", "failure_effect": "all B6 generated scalars remain stale even if raw COM changed", "stage5_bypasses": False, "live_witness": "FEBE7F68/FEBE5364/FEBE80C8 + FEBE80BC/80B8/..."},
    {"order": 7, "layer": "generated stage / task snapshot", "site": "58074 -> BCD62", "condition": "normal cyclic task staging/snapshot runs", "failure_effect": "controller sees stale ADB0/AE90/companions despite updated generated COM", "stage5_bypasses": False, "live_witness": "F130/F1FA/F155/F134/F137/F138/F139/F13E -> ADB0/AE90/ADDD/ADBB/ADBC/ADBD/ADBE/ADB9"},
    {"order": 8, "layer": "B6 route health + bank admission", "site": "CEFA4 -> CEFFC", "condition": "ACBD=0, route-family health good, ADB9=0 => CAFF=1, and Target Lateral ID ADB0=11", "failure_effect": "CB00 remains default7 instead of B6 LTA/LCA bank2", "stage5_bypasses": False, "live_witness": "ACBD/ADB9/CAFF/ADB0/CB00"},
    {"order": 9, "layer": "B6 application companions/readiness", "site": "CB2A2/CB664/CDA20/CEC8A/CE3AA/CDFF8/CE7FE/CE836/...", "condition": "sig265=0 permits its term; application sequence is sane; sig269/270 percentages and local readiness/inhibits permit contribution. sig263/CB664 belongs to the separate ADB0==0x31 transient and is not an ID11 admission gate", "failure_effect": "controller can remain unready, suppress a term, attenuate contribution, or ramp down without any SecOC failure", "stage5_bypasses": False, "live_witness": "ADBB/ADBC/ADBD/ADBE + readiness state CAB*/CA*; ADDD only if separately studying the 0x31 transient"},
    {"order": 10, "layer": "target-angle controller", "site": "CBB66/CCF0E/CCFB2/CD128/CDFF8/CE144/CE594", "condition": "target passes profile target/rate/magnitude and supervisor bounds", "failure_effect": "internal cooperative controller result is clipped/held/attenuated", "stage5_bypasses": False, "live_witness": "AE90 + C8B8/C8E0/controller intermediates"},
    {"order": 11, "layer": "cooperative gain/output", "site": "CF0B6/CF0EA/CF148/CF22C/CF276/CF2B2", "condition": "activation state produces nonzero CB20 and bank-specific output limits admit a command", "failure_effect": "CB38 remains zero, ramps, or is bounded despite admitted ID11", "stage5_bypasses": False, "live_witness": "CB20/CB08/CB2C/CB2E/CB38"},
    {"order": 12, "layer": "D0218 diagnostic/service branch", "site": "B330A/B338C -> B112 -> BCBD8/AC2B -> D0218", "condition": "AC2B != 0x5A for the normal branch containing CB38", "failure_effect": "AC2B==0x5A selects reduced C4C0+C3BA+BF3C branch and omits CB38 entirely", "stage5_bypasses": False, "live_witness": "B112/AC2B/CB38/CC48"},
    {"order": 13, "layer": "ordinary EPS composition/limits", "site": "D0218 -> D0284 -> D02DA -> D0382 -> D039E", "condition": "ordinary internal terms, AC64 scale, AC52 limit, slew/filter, and local damping produce a shared CC50", "failure_effect": "B6 is mixed with/limited by ordinary EPS state; it is never exclusive authority", "stage5_bypasses": False, "live_witness": "CC48/CC4C/CC4E/AC52/CC60/CC50"},
    {"order": 14, "layer": "common output scale", "site": "B4B6C/B4EF4 -> B1F8 -> BCBD8/AC5A -> D042C", "condition": "internal AC5A scale is nonzero (0x400 is unity)", "failure_effect": "CC62 = CC50*AC5A/0x400 can be attenuated all the way to zero before the hard actuator gate", "stage5_bypasses": False, "live_witness": "B1F8/AC5A/CC50/CC62"},
    {"order": 15, "layer": "common actuator hard inhibit", "site": "572E6 -> 8B28 -> FCC00/EEF90 -> BCAA6/AC29,AC2A -> D042C", "condition": "AC29 != 0 and AC2A == 0", "failure_effect": "D042C forces CC66=0 after computing/slew-limiting CC62", "stage5_bypasses": False, "live_witness": "8B28/EEF90/AC29/AC2A/CC62/CC66"},
    {"order": 16, "layer": "common internal override", "site": "D05B4/D0528/D064C/D0674 -> CC98/CC94 -> D047C", "condition": "CC98==0 for ordinary CC66 pass-through", "failure_effect": "CC94 replaces/bounds CC64 independently of B6", "stage5_bypasses": False, "live_witness": "CC98/CC94/CC66/CC64"},
    {"order": 17, "layer": "motor-side service/limit selection", "site": "D0AAE -> BF33E -> 35C4C", "condition": "normal motor-side branch uses EE40C; service/status branches can substitute bounded internal EE416/EE418/EEB10-derived value", "failure_effect": "B6-containing command can be replaced before 6AF4 while staying in the same downstream motor model", "stage5_bypasses": False, "live_witness": "AC54/EE40C + EEB1E/EE780/EE406 + 6AF4"},
    {"order": 18, "layer": "motor-current model", "site": "387BA -> 38502 -> 3835E/384D8 -> 38162", "condition": "current-command magnitude/sign/bounds and downstream motor-control state permit response", "failure_effect": "command is transformed/limited before physical motor response", "stage5_bypasses": False, "live_witness": "6E0A/6DEC/6DC8/6DD6 + 0x030 motor feedback"},
  ]

  live_ladder = [
    {"n": 1, "name": "host_send", "cells": ["sendcan B6", "Panda src=128 TX echo"], "proves": "host/Panda emitted candidate; does not prove F33 reception"},
    {"n": 2, "name": "secoc_queue", "cells": ["FEBE547A", "FEBE54D4"], "proves": "F33 CanIf/PduR/SecOC ingress copied B6"},
    {"n": 3, "name": "freshness_auth", "cells": ["FEBE55E8", "FEBE5600", "FEBE5564"], "proves": "profile2 freshness/auth transaction state"},
    {"n": 4, "name": "raw_com", "cells": ["FEBE4BFF..FEBE4C1E", "FEBE5364"], "proves": "upper route44 publication"},
    {"n": 5, "name": "generated_com", "cells": ["FEBE7F68", "FEBE80C8", "FEBE80BC", "FEBE80B8", "FEBE80CB", "FEBE80C0", "FEBE80C3", "FEBE80C4", "FEBE80C5", "FEBE80C9"], "proves": "4BD46 unpacked the new PDU under the global state gate"},
    {"n": 6, "name": "stage_snapshot", "cells": ["FEBEF130", "FEBEF1FA", "FEBEF155", "FEBEF134", "FEBEF137", "FEBEF138", "FEBEF139", "FEBEF13E", "FEBEADB0", "FEBEAE90", "FEBEADDD", "FEBEADBB", "FEBEADBC", "FEBEADBD", "FEBEADBE", "FEBEADB9"], "proves": "application task staged/snapshotted all command-relevant B6 fields"},
    {"n": 7, "name": "bank_health", "cells": ["FEBEACBD", "FEBECAFF", "FEBEADB0", "FEBECB00"], "proves": "ID11 reached cooperative bank2"},
    {"n": 8, "name": "application_supervision", "cells": ["FEBEADDD", "FEBEADBB", "FEBEADBC", "FEBEADBD", "FEBEADBE", "FEBECAB5", "FEBECAB6", "FEBECAB7", "FEBECAFC", "FEBECAFD"], "proves": "B6 companion/sequence/readiness state"},
    {"n": 9, "name": "cooperative_contribution", "cells": ["FEBECB20", "FEBECB08", "FEBECB38"], "proves": "supervised B6 contribution became nonzero"},
    {"n": 10, "name": "d0218_branch", "cells": ["FEBEB112", "FEBEAC2B", "FEBECB38", "FEBECC48"], "proves": "normal D0218 branch actually included B6 rather than diagnostic/service reduction"},
    {"n": 11, "name": "ordinary_funnel", "cells": ["FEBECC48", "FEBECC4C", "FEBECC4E", "FEBEAC52", "FEBECC60", "FEBECC50"], "proves": "B6-containing ordinary command survived common scaling/limits to CC50"},
    {"n": 12, "name": "output_scale", "cells": ["FEBEB1F8", "FEBEAC5A", "FEBECC50", "FEBECC62"], "proves": "common AC5A output scaling retained command"},
    {"n": 13, "name": "hard_actuator_gate", "cells": ["FEBE8B28", "FEBEEF90", "FEBEAC29", "FEBEAC2A", "FEBECC62", "FEBECC66"], "proves": "common actuator gate did/did not force command to zero"},
    {"n": 14, "name": "internal_override", "cells": ["FEBECC98", "FEBECC94", "FEBECC66", "FEBECC64"], "proves": "ordinary pass-through versus internal replacement"},
    {"n": 15, "name": "motor_side_selection", "cells": ["FEBEAC54", "FEBEE40C", "FEBEEB1E", "FEBEE780", "FEBEE406", "FEBE6AF4"], "proves": "motor-side branch selected the shared command or substituted another bounded internal source"},
    {"n": 16, "name": "motor_current_model", "cells": ["FEBE6E0A", "FEBE6DEC", "FEBE6DC8", "FEBE6DD6", "0x030 B22:B23 motor proxy"], "proves": "command reached downstream current model and exposes physical-response proxy"},
    {"n": 17, "name": "plant_response", "cells": ["measured steering angle/rate", "driver torque"], "proves": "physical rack response"},
  ]


  monitor_phases = [
    {
      "phase": "A",
      "purpose": "SecOC queue through raw route44 publication",
      "watch_windows": [
        {"address": "0xFEBE5478", "covers": ["FEBE547A queue metadata"]},
        {"address": "0xFEBE54D4", "covers": ["secured B0..B3 / ID byte"]},
        {"address": "0xFEBE54D8", "covers": ["secured B4..B7 / target bytes"]},
        {"address": "0xFEBE55E8", "covers": ["profile2 committed freshness"]},
        {"address": "0xFEBE5564", "covers": ["authentication result state"]},
        {"address": "0xFEBE4C00", "covers": ["route44 raw B1..B4"]},
        {"address": "0xFEBE4C04", "covers": ["route44 raw B5..B8"]},
        {"address": "0xFEBE5364", "covers": ["route44 generation"]},
      ],
      "first_divergence": "TX echo with no queue change => before/at F33 ingress; queue changes with no route44 generation/raw change => SecOC/upper-publication transaction",
    },
    {
      "phase": "B",
      "purpose": "raw route44 publication through generated COM",
      "watch_windows": [
        {"address": "0xFEBE5364", "covers": ["route44 generation"]},
        {"address": "0xFEBE7F68", "covers": ["global COM state gate"]},
        {"address": "0xFEBE80C8", "covers": ["local route generation latch", "generated sig272/273 neighborhood"]},
        {"address": "0xFEBE80B8", "covers": ["generated target angle sig262"]},
        {"address": "0xFEBE80BC", "covers": ["generated Target Lateral ID sig261"]},
        {"address": "0xFEBE80C0", "covers": ["generated sig265..268 neighborhood"]},
        {"address": "0xFEBE80C4", "covers": ["generated sig269..272 neighborhood"]},
        {"address": "0xFEBEF1F8", "covers": ["staged target angle at F1FA"]},
      ],
      "first_divergence": "route44 generation/raw changes with stale generated scalars => 4BD46/global-state gate; generated target changes with stale F1FA => 58074 staging",
    },
    {
      "phase": "C",
      "purpose": "generated staging through application snapshot and bank prerequisites",
      "watch_windows": [
        {"address": "0xFEBEF130", "covers": ["staged sig261", "staged sig264"]},
        {"address": "0xFEBEF134", "covers": ["staged sig265..268"]},
        {"address": "0xFEBEF138", "covers": ["staged sig269/270 neighborhood"]},
        {"address": "0xFEBEF1F8", "covers": ["staged sig262 at F1FA"]},
        {"address": "0xFEBEADB0", "covers": ["Target Lateral ID snapshot", "companion snapshot neighborhood"]},
        {"address": "0xFEBEAE90", "covers": ["target angle snapshot"]},
        {"address": "0xFEBEACBC", "covers": ["ACBD normalized global COM state"]},
        {"address": "0xFEBECAFC", "covers": ["CAFC/CAFD readiness", "CAFF route health"]},
      ],
      "first_divergence": "stages change but ADB0/AE90 stay stale => BCD62 snapshot task; snapshots change with bad ACBD/CAFF => bank prerequisite failure",
    },
    {
      "phase": "D",
      "purpose": "bank selection, normal-ID11 readiness, and cooperative contribution",
      "watch_windows": [
        {"address": "0xFEBECAFC", "covers": ["CAFC/CAFD readiness", "CAFF route health"]},
        {"address": "0xFEBECB00", "covers": ["CB00 selected bank"]},
        {"address": "0xFEBEADBC", "covers": ["sig268 sequence", "sig269/270 percentages"]},
        {"address": "0xFEBEACCC", "covers": ["ACCC/ACCD cooperative readiness inputs"]},
        {"address": "0xFEBECAB4", "covers": ["CAB5/CAB6/CAB7 readiness"]},
        {"address": "0xFEBECB20", "covers": ["cooperative gain CB20"]},
        {"address": "0xFEBECB08", "covers": ["cooperative controller source CB08"]},
        {"address": "0xFEBECB38", "covers": ["final cooperative contribution CB38"]},
      ],
      "first_divergence": "ADB0=11/CAFF=1 with CB00!=2 => bank admission; CB00=2 with CB20/CB38 zero => readiness/gain/controller state",
    },
    {
      "phase": "E",
      "purpose": "D0218 branch through shared command and common output scale",
      "watch_windows": [
        {"address": "0xFEBECB38", "covers": ["cooperative contribution CB38"]},
        {"address": "0xFEBEB110", "covers": ["B112 diagnostic/service branch source"]},
        {"address": "0xFEBEAC28", "covers": ["AC29 actuator enable", "AC2A actuator inhibit", "AC2B D0218 branch selector"]},
        {"address": "0xFEBECC48", "covers": ["D0218 output CC48"]},
        {"address": "0xFEBECC4C", "covers": ["CC4C", "CC4E"]},
        {"address": "0xFEBECC50", "covers": ["CC50 shared command"]},
        {"address": "0xFEBECC60", "covers": ["CC60", "CC62 scaled output"]},
        {"address": "0xFEBEAC58", "covers": ["AC5A common output scale"]},
      ],
      "first_divergence": "CB38 nonzero but CC48 lacks it => AC2B branch; CC50 nonzero but CC62 zero => AC5A scaling; AC29/AC2A are captured in the same phase",
    },
    {
      "phase": "F",
      "purpose": "hard actuator gate, internal override, and motor mirror",
      "watch_windows": [
        {"address": "0xFEBECC60", "covers": ["CC62 before hard gate"]},
        {"address": "0xFEBECC64", "covers": ["CC64 post-override", "CC66 hard-gated command"]},
        {"address": "0xFEBEAC28", "covers": ["AC29 actuator enable", "AC2A actuator inhibit"]},
        {"address": "0xFEBEEF90", "covers": ["internal status snapshot feeding AC29/AC2A"]},
        {"address": "0xFEBECC94", "covers": ["CC94 override value"]},
        {"address": "0xFEBECC98", "covers": ["CC98 override mode"]},
        {"address": "0xFEBEAC54", "covers": ["motor snapshot AC54"]},
        {"address": "0xFEBEE40C", "covers": ["motor mirror EE40C"]},
      ],
      "first_divergence": "CC62 nonzero with CC66 zero => AC29/AC2A gate; CC66 nonzero with CC64 different => CC98/CC94 override; CC64 differs from AC54/EE40C => snapshot/mirror path",
    },
    {
      "phase": "G",
      "purpose": "motor-side selection through current model",
      "watch_windows": [
        {"address": "0xFEBEE40C", "covers": ["shared-command motor mirror"]},
        {"address": "0xFEBE6AF4", "covers": ["selected motor-side command"]},
        {"address": "0xFEBE6E08", "covers": ["motor-model input 6E0A"]},
        {"address": "0xFEBE6DEC", "covers": ["current bound stage"]},
        {"address": "0xFEBE6DC8", "covers": ["current component stage"]},
        {"address": "0xFEBE6DD4", "covers": ["signed current component at 6DD6"]},
        {"address": "0xFEBEE780", "covers": ["35C4C service/status selector state"]},
        {"address": "0xFEBEE404", "covers": ["35C4C EE406 selector neighborhood"]},
      ],
      "first_divergence": "EE40C differs from selected 6AF4 => motor-side substitution; nonzero 6AF4 with stale/zero 6E0A/current stages => current-model boundary; current-model output without CAN/plant response moves beyond this RAM ladder",
    },
  ]
  for phase in monitor_phases:
    windows = phase["watch_windows"]
    if len(windows) > 8:
      raise RuntimeError(f"monitor phase {phase['phase']} exceeds eight watch slots")
    for window in windows:
      address = int(window["address"], 16)
      if not (0xFEBE0000 <= address <= 0xFEBFFFFC and address % 4 == 0):
        raise RuntimeError(f"invalid monitor watch window {window['address']} in phase {phase['phase']}")

  function_evidence = {}
  for addr, role in FUNCTIONS.items():
    rec = corpus[addr]
    body = body_bytes(image, rec)
    function_evidence[f"0x{addr:06X}"] = {"role": role, "body_sha256": h(body), "decompiled_c_sha256": rec["decompiled_c_sha256"], "body_size": len(body)}
  raw_evidence = {name: {"start": f"0x{lo:06X}", "end_exclusive": f"0x{hi:06X}", "sha256": h(image[lo:hi]), "size": hi-lo} for name,(lo,hi) in RAW_RANGES.items()}

  return {
    "schema": "camry-f33-b6-end-to-end-v1",
    "target": {"software_id": "8965F3307000", "codeflash_sha256": h(image), "canonical_function_count": len(corpus)},
    "exact_config": exact_config,
    "freshness_profile_records": profile_records,
    "b6_freshness_slot": b6_freshness_slot,
    "semantic_checks": checks,
    "raw_stage_snapshot_census": raw_stage_snapshot_census,
    "key_writer_census": writer_census,
    "gate_source_census": gate_source_census,
    "function_evidence": function_evidence,
    "raw_boundary_evidence": raw_evidence,
    "application_field_map": FIELD_MAP,
    "execution_path": [
      "RSCFD controller1 rule39 -> CanIf descriptor39 (0x400000B6/32 FD) -> PduR44",
      "8EE7C -> 8F34A -> 8E9C6 -> profile2 queue FEBE547A / secured bytes FEBE54D4",
      "8F746 -> 8F434 -> 903A0 freshness -> 8ECB2 -> 8F676 -> ICU-S command7/slot4 -> 8F906",
      "stage5 forces all recovered freshness/ICU/result consequences to software success",
      "8F546 -> 90204 -> 81CA6 -> 7D72C -> raw COM FEBE4BFF..4C1E + generation FEBE5364",
      "4BD46 -> generated B6 scalars -> 58074 stage -> BCD62 snapshots",
      "CEFA4 health + ACBD global state + CEFFC: ADB0=11 -> CB00=2",
      "CBB66/CCF0E/CCFB2/CD128 + companion/sequence/readiness supervisors -> CF2B2 -> CB38",
      "B330A/B338C -> B112 -> AC2B chooses whether D0218 includes CB38 at all",
      "D0218 normal branch adds CB38 inside ordinary EPS sum -> shared CC48/CC60/CC50",
      "B4B6C/B4EF4 -> B1F8 -> AC5A scales CC50 -> CC62",
      "572E6 -> 8B28 -> FCC00/EEF90 -> BCAA6 -> AC29/AC2A hard-gates CC66",
      "D05B4/D0528/D064C/D0674 -> CC98/CC94; D047C can replace CC66 -> CC64",
      "D0AAE -> AC54 -> BF33E -> EE40C -> 35C4C motor-side selection -> 6AF4 -> 387BA -> 6E0A -> motor-current stages",
    ],
    "gate_matrix": gates,
    "live_witness_ladder": live_ladder,
    "stationary_monitor_phases": monitor_phases,
    "scheduler": {
      "communications_application_root": "66062 -> 667E6 -> 58B5E -> 5EC24/5F610 -> 4BD46 -> 58074 -> BCD62 -> D1130 -> D0EEC",
      "shared_command_root": "65FEA -> 6679E -> 5899E -> C1F7A/C2000 -> BCD02 -> BCAA6/BCBD8 -> D1100 -> D0AF6 -> BF33E",
      "boundary": "The two cyclic roots share snapshot RAM; exact within-task ordering is recovered. Absolute inter-task phase is scheduler/runtime state, not one direct call chain.",
    },
    "stage5_boundary": {
      "bypassed": ["freshness callback result", "ICU command return", "ICU root verification result", "post-crypto callback result", "final Gate-2 delivery predicate"],
      "not_bypassed": ["physical CAN/CanIf reception", "SecOC queue integrity/geometry", "upper PduR/COM copy", "generated-COM new-data/global-state gate", "application staging/snapshot", "application bank/health/readiness", "B6 companion/sequence supervision", "target/supervisor gain and limits", "D0218 diagnostic/service branch", "ordinary EPS composition", "common AC5A output scale", "common AC29/AC2A hard inhibit", "common CC98/CC94 internal override", "motor-side service/limit selection", "motor/current limits"],
      "icu_black_box": "Only ICU-S cryptographic silicon internals are unavailable. Every software-visible consequence used by the recovered B6 verification path is mapped and neutralized by cumulative stage5.",
    },
    "objective_conclusions": {
      "all_recovered_software_gates_on_b6_to_motor_current_path_are_mapped": True,
      "proof_boundary": "Complete canonical direct-reference/writer closure for the recovered B6 scalar and shared-command path. Computed aliases, DMA/peripheral mutation, ICU-S silicon internals, and final hardware PWM commit remain outside this exact-F33 proof where separately noted.",
      "stage5_removes_recovered_freshness_and_auth_result_rejection_after_valid_secoc_ingress": True,
      "stage5_forces_noncrypto_queue_pdur_com_or_controller_gates": False,
      "successful_panda_tx_echo_proves_eps_application_delivery": False,
      "accepted_id11_guarantees_nonzero_cb38": False,
      "nonzero_cb38_guarantees_nonzero_motor_command": False,
      "accepted_id11_is_exclusive_eps_authority": False,
      "accepted_id11_is_a_co_modulated_input": True,
      "remaining_live_nonresponse_can_be_localized_with_adjacent_internal_witnesses": True,
      "final_hardware_pwm_commit_recovered_exact_f33_here": False,
      "next_runtime_question": "At which adjacent rung of the 17-step witness ladder does the injected B6 first diverge?",
    },
  }


def main() -> None:
  ap = argparse.ArgumentParser()
  ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
  args = ap.parse_args()
  out = analyze()
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
  print("camry exact-F33 B6 end-to-end map: PASS")


if __name__ == "__main__":
  main()
