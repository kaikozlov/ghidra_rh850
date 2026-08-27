#!/usr/bin/env python3
"""Promote exact-H decompiler evidence for the complete protected-0x0B6 SecOC verify state machine."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from sienna_target import CODEFLASH as SIENNA_CODEFLASH
from corolla_h_constants import CODEFLASH as H_CODEFLASH

REPO = Path(__file__).resolve().parents[1]
GENERATOR = Path(__file__).resolve()
IMAGE = H_CODEFLASH
SIENNA = SIENNA_CODEFLASH
OUT = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json"

# These are target-native H functions needed beyond the earlier byte-complete
# receiver-envelope proof. CryptoIf/ICU-S helper bodies that were already
# promoted by the key-provenance artifact are intentionally not duplicated.
ENTRIES = {
    0x00062430: "disabled_slot4_command7_kat",
    0x000822D0: "icus_command7_descriptor_prepare",
    0x00082F6A: "cryptoif_begin",
    0x00082F9C: "cryptoif_update",
    0x00082FA8: "cryptoif_finish",
    0x00082956: "crypto_driver_dispatch",
    0x00083BF4: "icus_command7_driver",
    0x00088288: "failure_delivery_grace_tick_wrapper",
    0x00088308: "secoc_receive_main_cycle",
    0x000884AA: "secoc_crypto_config_get",
    0x000884E0: "failure_delivery_global_mode_setter",
    0x00088512: "failure_delivery_global_mode_test",
    0x0008857C: "secoc_verify_engine_init",
    0x000886DA: "failure_delivery_grace_counter_increment",
    0x000886FC: "failure_delivery_grace_counter_reset",
    0x00088702: "secoc_new_or_retry_transition",
    0x00088744: "secoc_trailer_extract",
    0x00087FC2: "secoc_authenticated_input_build",
    0x00088856: "queued_pdu_upper_delivery",
    0x000888A6: "verification_failure_handler",
    0x00088908: "freshness_boundary_callback_dispatch",
    0x0008891E: "authentication_candidate_retry",
    0x00088986: "secoc_cmac_submit",
    0x000889C2: "crypto_submit_retry",
    0x00088A56: "secoc_verify_worker",
    0x00088BE2: "freshness_commit_callback_dispatch",
    0x00088C16: "post_cmac_acceptance_gate",
    0x00088C9C: "secoc_queue_dispatch",
    0x00089558: "freshness_profile_lookup",
    0x000896B0: "freshness_get_dispatch",
    0x00089758: "freshness_commit_dispatch",
    0x00089812: "freshness_state_init",
    0x00089876: "full_freshness_pack",
    0x000899B4: "sync_freshness_pack",
    0x00089A46: "transmitted_freshness_parse",
    0x00089B46: "sync_freshness_parse",
    0x00089CDA: "reset_candidate_search",
    0x00089D58: "normal_freshness_window_check",
    0x00089E2C: "normal_freshness_candidate_build",
    0x00089E9A: "normal_freshness_reconstruct",
    0x00089F6E: "sync_freshness_reconstruct",
    0x0008A07A: "normal_freshness_commit",
    0x0008A0AE: "trip_wrap_normal_state_clear",
    0x0008A130: "sync_freshness_commit",
}

# Sienna's generic SecOC acceptance engine is useful prior art.  The comparison
# is deliberately raw-byte descriptive only: H freshness storage/profile counts
# are recovered independently below and are not transferred from Sienna.
SIENNA_UPPER = {
    0x00088702: 0x0008E166,
    0x0008891E: 0x0008E382,
    0x000889C2: 0x0008E426,
    0x00088A56: 0x0008E4BA,
    0x00088BE2: 0x0008E646,
    0x00088C16: 0x0008E67A,
    0x00088C9C: 0x0008E700,
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    resolved = path.resolve()
    return str(resolved.relative_to(REPO.resolve())) if resolved.is_relative_to(REPO.resolve()) else str(resolved)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--sienna", type=Path, default=SIENNA)
    ap.add_argument("--corpus", type=Path, required=True,
                    help="disposable exact-H corpus with the SecOC/freshness boundaries forced")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = args.image.read_bytes()
    sienna = args.sienna.read_bytes()
    if len(image) != 0x100000 or len(sienna) < 0x100000:
        raise SystemExit("expected 1 MiB CodeFlash application images")

    rows: dict[int, dict] = {}
    for line in args.corpus.open():
        row = json.loads(line)
        if row.get("record") == "function" and row.get("entry_addr"):
            rows[int(row["entry_addr"], 16)] = row

    functions = []
    for entry, role in ENTRIES.items():
        row = rows.get(entry)
        if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
            raise SystemExit(f"missing complete H decompile 0x{entry:X} ({role})")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"function body outside H image 0x{entry:X}")
        text = row["decompiled_c"]
        functions.append({
            "entry": f"0x{entry:08X}",
            "role": role,
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })

    sienna_comparison = []
    for h_entry, s_entry in SIENNA_UPPER.items():
        row = rows[h_entry]
        size = int(row["body_size"])
        h_body = image[h_entry:h_entry + size]
        s_body = sienna[s_entry:s_entry + size]
        diff_offsets = [i for i, (a, b) in enumerate(zip(h_body, s_body)) if a != b]
        sienna_comparison.append({
            "role": ENTRIES[h_entry],
            "h_entry": f"0x{h_entry:08X}",
            "sienna_entry": f"0x{s_entry:08X}",
            "body_size": size,
            "h_sha256": sha(h_body),
            "sienna_sha256": sha(s_body),
            "different_byte_count": len(diff_offsets),
            "different_offsets": diff_offsets,
            "entry_delta": f"0x{s_entry - h_entry:X}",
        })

    out = {
        "schema": "corolla-h-b6-secoc-verification-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "generator": {"path": rel(GENERATOR), "sha256": sha(GENERATOR.read_bytes())},
        "image": {"path": rel(args.image), "size": len(image), "sha256": sha(image)},
        "sienna_reference": {"path": rel(args.sienna), "size": len(sienna), "sha256": sha(sienna)},
        "source_corpus": {"path": rel(args.corpus), "sha256": sha(args.corpus.read_bytes())},
        "function_count": len(functions),
        "functions": functions,
        "sienna_upper_engine_comparison": {
            "rows": sienna_comparison,
            "boundary": (
                "Sienna supplies role anchors for the generic acceptance engine. The H functions occupy the same control roles "
                "near a +0x5A64 Sienna relocation but are not claimed byte-identical: raw differences include relocated calls, "
                "GP/table displacements, and generated-profile geometry. H freshness/window conclusions below must be recovered "
                "from the target-native H bodies rather than transferred from Sienna."
            ),
        },
        "boundary": (
            "Exact-H disposable-project decompilations for the protected 0x0B6 freshness/verification state machine, raw-byte-bound "
            "to 8965H1202000. This evidence is intended to complement, not replace, the separately verified byte-complete receiver "
            "envelope and ICU-S key-selector provenance artifacts."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(functions)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
