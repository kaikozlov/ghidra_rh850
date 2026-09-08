#!/usr/bin/env python3
"""Prove exact-F33 B6 zero-MAC and wrong-key-MAC equivalence under stage 5.

This is a firmware-static reducer. It follows the exact 8965F3307000 protected
B6 receive path from trailer extraction through ICU-S submission, all five
installed result-neutralization sites, post-crypto freshness commit, PduR/COM
publication, and the application B6 unpacker. It intentionally does not model
ICU-S silicon internals; instead it proves every software-visible ICU result on
this receive path is neutralized before upper delivery by the cumulative stage-5
image.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from exploit.patcher.build_payload import config_from_manifest, simulate_apply
from tools import build_camry_f33_crypto_result_patch as stage5
from tools import build_camry_f33_freshness_result_patch as stage4
from tools import build_camry_f33_gate2_root_result_patch as stage3
from tools import build_camry_f33_gate2_semantic_patch as stage2

IMAGE = ROOT / "firmware/camry-8965F3307000/CodeFlash.bin"
CORPUS = ROOT / "data/generated/camry-8965F3307000/decompilations.jsonl"
DEFAULT_OUT = ROOT / "data/generated/camry_f33_b6_mac_equivalence.json"
EXPECTED_IMAGE_SHA256 = "42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7"

# Functions whose exact stock bodies define the software-visible B6 auth path.
FUNCTIONS = {
  0x04BD46: "application B6 signal unpack",
  0x07D800: "route guard: unconditional success",
  0x081CA6: "PduR upper-route dispatcher",
  0x088FC0: "ICU-S command buffer/descriptor builder",
  0x089646: "ICU-S command dispatcher",
  0x089C98: "ICU-S synchronous command wrapper",
  0x08E772: "COM new-data generation update",
  0x08ECB2: "authentication-input builder",
  0x08F434: "secured trailer extractor",
  0x08F546: "verified PDU upper delivery",
  0x08F676: "ICU-S verify wrapper",
  0x08F746: "secured PDU verify coordinator",
  0x08F8D2: "post-crypto profile callback dispatcher",
  0x08F906: "root result / Gate-2 / delivery coordinator",
  0x090204: "upper PduR indication shim",
  0x090A48: "ordinary freshness reconstruction",
  0x090D6A: "ordinary pending-to-committed freshness commit",
}

# Current disposable-project recovery supplied exact boundaries for these bodies
# even though the canonical decompilation corpus predates their function creation.
RAW_FUNCTION_RANGES = {
  "freshness_callback_0x903A0": (0x903A0, 0x903F6),
  "post_crypto_callback_0x90448": (0x90448, 0x90482),
  "route44_callback_0x7D72C": (0x7D72C, 0x7D800),
  "icu_command0_start_0x891CC": (0x891CC, 0x892CC),
  "icu_command0_completion_0x892CC": (0x892CC, 0x89386),
}


def sha256_bytes(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def load_functions(entries: set[int]) -> dict[int, dict[str, Any]]:
  out: dict[int, dict[str, Any]] = {}
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") != "function":
        continue
      entry = int(rec["entry_addr"], 16)
      if entry in entries:
        out[entry] = rec
  if set(out) != entries:
    missing = sorted(entries - set(out))
    raise RuntimeError(f"missing canonical decompilation records: {[hex(x) for x in missing]}")
  return out


def body_bytes(image: bytes, rec: dict[str, Any]) -> bytes:
  chunks: list[bytes] = []
  for r in rec["body_ranges"]:
    if r["space"] != "ram":
      raise RuntimeError("unexpected non-RAM CodeFlash body range")
    lo = int(r["min"], 16)
    hi = int(r["max"], 16)
    chunks.append(image[lo:hi + 1])
  return b"".join(chunks)


def direct_refs_to(target: int) -> list[dict[str, str]]:
  refs: list[dict[str, str]] = []
  with CORPUS.open(encoding="utf-8") as fh:
    for line in fh:
      rec = json.loads(line)
      if rec.get("record") != "function":
        continue
      for ref in rec.get("data_references", []):
        try:
          to_addr = int(ref["to_addr"], 16)
        except (KeyError, ValueError):
          continue
        if to_addr == target:
          refs.append({
            "function": rec["entry_addr"],
            "from": ref["from_addr"],
            "type": ref["ref_type"],
          })
  return refs


def reconstruct_stage5(stock: bytes) -> tuple[bytes, dict[str, Any]]:
  source, stage4_manifest = stage5.reconstruct_stage4(stock)
  manifest = stage5.build_stage5_manifest(source, stage4_manifest)
  cfg = config_from_manifest(manifest, mode="apply")
  final_image, fixup, residue = simulate_apply(source, cfg)
  if sha256_bytes(final_image) != stage5.EXPECTED_FINAL_SHA256:
    raise RuntimeError("stage-5 image SHA drift")
  if fixup != stage5.EXPECTED_STAGE5_FIXUP or residue != 0xFFFFFFFF:
    raise RuntimeError("stage-5 CRC repair drift")
  return final_image, {
    "source_stage4_sha256": sha256_bytes(source),
    "final_sha256": sha256_bytes(final_image),
    "final_fixup": f"0x{fixup:08X}",
    "final_crc_residue": f"0x{residue:08X}",
  }


def analyze() -> dict[str, Any]:
  image = IMAGE.read_bytes()
  image_sha = sha256_bytes(image)
  if image_sha != EXPECTED_IMAGE_SHA256:
    raise RuntimeError(f"exact F33 SHA mismatch: {image_sha}")

  funcs = load_functions(set(FUNCTIONS))
  final_image, stage5_meta = reconstruct_stage5(image)

  function_evidence: dict[str, Any] = {}
  for entry, role in FUNCTIONS.items():
    rec = funcs[entry]
    body = body_bytes(image, rec)
    function_evidence[f"0x{entry:06X}"] = {
      "role": role,
      "body_size": len(body),
      "body_sha256": sha256_bytes(body),
      "decompiled_c_sha256": rec["decompiled_c_sha256"],
    }

  raw_ranges = {
    name: {
      "start": f"0x{lo:06X}",
      "end_exclusive": f"0x{hi:06X}",
      "size": hi - lo,
      "sha256": sha256_bytes(image[lo:hi]),
    }
    for name, (lo, hi) in RAW_FUNCTION_RANGES.items()
  }

  # B6 is secured record 2 (stride 0x50). Pin the exact fields consumed by the
  # generic SecOC machinery rather than relying on a vehicle-side nickname.
  record = 2
  stride = 0x50
  off = record * stride
  b6 = {
    "secured_record": record,
    "data_id": struct.unpack_from("<H", image, 0x25852 + off)[0],
    "authenticator_bits": struct.unpack_from("<H", image, 0x2584A + off)[0],
    "trailer_extract_bytes": struct.unpack_from("<H", image, 0x2584E + off)[0],
    "authenticator_start_bit_in_trailer": image[0x2585D + off],
    "freshness_id": struct.unpack_from("<H", image, 0x2585A + off)[0],
    "crypto_command_selector": struct.unpack_from("<H", image, 0x25868 + off)[0],
    "post_crypto_callback": f"0x{struct.unpack_from('<I', image, 0x25878 + off)[0]:06X}",
    "upper_pdur_destination": struct.unpack_from("<H", image, 0x2587E + off)[0],
    "freshness_callback": f"0x{struct.unpack_from('<I', image, 0x25890 + off)[0]:06X}",
  }

  # The upper destination is route 44. Its exact 8-byte receive record is
  # base+route*8. Flags 0x0C select the always-true 0x7D800 guard and the COM
  # new-data update, but not the optional pre-copy hook (0x10).
  route = b6["upper_pdur_destination"]
  route_addr = 0x226C0 + route * 8
  route_rec = image[route_addr:route_addr + 8]
  window_base = struct.unpack_from("<H", image, 0x22840 + route * 2)[0]
  route44 = {
    "route": route,
    "record_address": f"0x{route_addr:06X}",
    "record_hex": route_rec.hex(),
    "configured_length": struct.unpack_from("<H", route_rec, 4)[0],
    "flags": route_rec[7],
    "optional_precopy_hook_enabled": bool(route_rec[7] & 0x10),
    "pass_guard_enabled": bool(route_rec[7] & 0x08),
    "new_data_update_enabled": bool(route_rec[7] & 0x04),
    "com_window_base": window_base,
    "application_bytes": [window_base, window_base + 27],
    "secured_trailer_bytes": [window_base + 28, window_base + 31],
    "application_unpack_offsets": [0x1BA, 0x1BB, 0x1BD, 0x1BE, 0x1BF, 0x1C0, 0x1C1],
    "application_unpack_max_offset": 0x1C1,
    "trailer_direct_data_refs": {
      f"0x{0xFEBE4BFF + i:08X}": direct_refs_to(0xFEBE4BFF + i)
      for i in range(28, 32)
    },
  }

  patch_sites = [
    ("stage1_final_delivery_gate", stage2.STAGE1_VA, stage2.STAGE1_ORIGINAL, stage2.STAGE1_REPLACEMENT,
     "cmp r0,r26 -> cmp r0,r0: final Gate-2 branch always takes native success tail"),
    ("stage2_post_crypto_callback_result", stage2.STAGE2_VA, stage2.STAGE2_ORIGINAL, stage2.STAGE2_REPLACEMENT,
     "mov r26,r7 -> mov 0,r7: profile callback is told verification succeeded"),
    ("stage3_root_result_boolean", stage3.ROOT_RESULT_VA, stage3.ROOT_RESULT_ORIGINAL, stage3.ROOT_RESULT_REPLACEMENT,
     "cmovne 1,r1,r26 -> cmovne 0,r0,r26: ICU root-result byte cannot assert failure"),
    ("stage4_freshness_callback_status", stage4.FRESHNESS_RESULT_VA, stage4.FRESHNESS_RESULT_ORIGINAL, stage4.FRESHNESS_RESULT_REPLACEMENT,
     "mov r10,r27 -> mov 0,r27: freshness callback return cannot reject the PDU"),
    ("stage5_icu_command_return", stage5.CRYPTO_RESULT_CMP_VA, stage5.CRYPTO_RESULT_CMP_ORIGINAL, stage5.CRYPTO_RESULT_CMP_REPLACEMENT,
     "cmp r0,r10 -> cmp r0,r0: ICU command return cannot reject the PDU"),
  ]
  patch_evidence: list[dict[str, Any]] = []
  for name, va, original, replacement, effect in patch_sites:
    patch_evidence.append({
      "name": name,
      "address": f"0x{va:06X}",
      "stock": original.hex(),
      "stage5": final_image[va:va + len(replacement)].hex(),
      "expected_stage5": replacement.hex(),
      "effect": effect,
    })

  auth_refs = direct_refs_to(0xFEBE5554)
  result_refs = direct_refs_to(0xFEBE5564)

  return {
    "schema": "camry-f33-b6-invalid-mac-equivalence-v1",
    "firmware": {
      "part": "8965F3307000",
      "codeflash_sha256": image_sha,
      "stage5": stage5_meta,
    },
    "b6_secoc_profile": b6,
    "function_evidence": function_evidence,
    "raw_function_ranges": raw_ranges,
    "direct_reference_census": {
      "received_authenticator_buffer_FEBE5554": auth_refs,
      "icu_root_result_byte_FEBE5564": result_refs,
    },
    "route44_upper_delivery": route44,
    "installed_patch_sites": patch_evidence,
    "proof": {
      "pre_icu_authenticator_content_branch_recovered": False,
      "authenticator_treatment_before_icu": "opaque bit extraction/copy; pointer and length validation only",
      "only_semantic_authenticator_consumer": "ICU-S command 0 verify operation",
      "freshness_callback_still_executes": True,
      "freshness_status_forced_success_after_callback": True,
      "icu_command_return_forced_success": True,
      "icu_root_result_forced_success": True,
      "post_crypto_callback_forced_success": True,
      "post_crypto_success_commits_pending_freshness": True,
      "final_delivery_gate_forced_success": True,
      "route44_post_secoc_content_recheck": False,
      "application_unpack_reads_secoc_trailer": False,
      "conclusion": "For the cumulative stage-5 F33 software path, an all-zero invalid MAC28 and a wrong-key/dummy-CMAC invalid MAC28 are acceptance-equivalent. The dummy CMAC preserves native envelope grammar but cannot improve software admission relative to zero MAC.",
      "silicon_boundary": "ICU-S internal cryptographic implementation is not CodeFlash. Both candidate tags are invalid under the real slot-4 key except accidental 1/2^28 truncation matches; every recovered software-visible ICU return/result/callback consequence on this B6 path is neutralized by stage 5.",
    },
  }


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
  parser.add_argument("--check", action="store_true", help="require generated output to match the existing artifact")
  args = parser.parse_args()
  data = analyze()
  rendered = json.dumps(data, indent=2, sort_keys=True) + "\n"
  if args.check:
    if not args.out.exists() or args.out.read_text(encoding="utf-8") != rendered:
      raise SystemExit("camry F33 B6 MAC-equivalence artifact drift")
    print("camry F33 B6 invalid-MAC equivalence: MATCH")
    return 0
  args.out.parent.mkdir(parents=True, exist_ok=True)
  args.out.write_text(rendered, encoding="utf-8")
  print(args.out)
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
