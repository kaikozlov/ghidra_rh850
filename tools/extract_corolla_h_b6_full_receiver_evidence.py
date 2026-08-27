#!/usr/bin/env python3
"""Promote exact-H decompiler evidence needed to exhaust the protected 0x0B6 receiver envelope."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from corolla_h_constants import CODEFLASH as H_CODEFLASH

REPO = Path(__file__).resolve().parents[1]
GENERATOR = Path(__file__).resolve()
IMAGE = H_CODEFLASH
OUT = REPO / "data/generated/corolla_8965H1202000_b6_full_receiver_decompiler_evidence.json"

# These functions close the paths deliberately outside the earlier request/loss
# receiver artifact: queue storage/retrieval, trailer extraction, authenticated-
# input construction, freshness reconstruction, verification, and upper delivery.
ENTRIES = [
    0x0007AFB6,  # PduR upper routing helper
    0x00087E2C,  # queued PDU pointer/length getter
    0x00087FC2,  # DataID || authentic payload || full freshness builder
    0x0008865A,  # SecOC queue ingress
    0x00088744,  # FV/authenticator extraction from secured PDU tail
    0x00088856,  # verified-PDU upper delivery
    0x00088986,  # authenticator comparison/CryptoIf wrapper
    0x00088A56,  # SecOC verification worker
    0x00089514,  # upper routing wrapper
    0x000896B0,  # freshness get callback dispatcher
    0x00089758,  # freshness commit callback dispatcher
    0x00089876,  # full-freshness packer
    0x00089A46,  # truncated/full freshness parser
    0x00089E2C,  # normal freshness candidate/window policy
    0x00089E9A,  # normal freshness reconstruction wrapper
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_direct_region_hits(text: str, gp: int, region_lo: int, region_hi: int) -> list[dict[str, str]]:
    """Find named/absolute or simple GP-alias constant references into a RAM region."""
    hits: list[dict[str, str]] = []
    abs_pat = re.compile(r"(?:DAT_|uRam|cRam|bRam)?(febe[0-9a-f]{4})", re.IGNORECASE)
    gp_assign_pat = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*unaff_gp\s*;")
    constant_assign_pat = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*(-?0x[0-9a-f]+|-?\d+)\s*;", re.IGNORECASE)
    alias_assign_pat = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*;")

    aliases = {"unaff_gp"}
    aliases.update(match.group(1) for match in gp_assign_pat.finditer(text))
    for match in constant_assign_pat.finditer(text):
        try:
            value = int(match.group(2), 0) & 0xFFFFFFFF
        except ValueError:
            continue
        if value == gp:
            aliases.add(match.group(1))
    while True:
        before = len(aliases)
        for match in alias_assign_pat.finditer(text):
            if match.group(2) in aliases:
                aliases.add(match.group(1))
        if len(aliases) == before:
            break

    for alias in aliases:
        displacement_pat = re.compile(
            rf"\b{re.escape(alias)}\s*([+-])\s*(-?0x[0-9a-f]+|-?\d+)", re.IGNORECASE
        )
        for match in displacement_pat.finditer(text):
            delta = int(match.group(2), 0)
            if match.group(1) == "-":
                delta = -delta
            address = (gp + delta) & 0xFFFFFFFF
            if region_lo <= address <= region_hi:
                hits.append({"kind": "gp_relative_or_simple_alias", "base": alias,
                             "expression": match.group(0), "address": f"0x{address:08X}"})
    for match in abs_pat.finditer(text):
        address = int(match.group(1), 16)
        if region_lo <= address <= region_hi:
            hits.append({"kind": "absolute_symbol", "expression": match.group(0),
                         "address": f"0x{address:08X}"})
    return hits


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", type=Path, default=IMAGE)
    ap.add_argument("--corpus", type=Path, required=True,
                    help="disposable exact-H corpus with the SecOC helper boundaries forced")
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    image = args.image.read_bytes()
    if len(image) != 0x100000:
        raise SystemExit(f"expected 1 MiB H CodeFlash, got {len(image):#x}")

    rows: dict[int, dict] = {}
    for line in args.corpus.open():
        row = json.loads(line)
        if row.get("record") == "function":
            rows[int(row["entry_addr"], 16)] = row

    # Application-corpus direct-reference sweep for the exact PDU42 COM-RAM
    # window.  In addition to named absolute references, follow the simple GP
    # aliases Ghidra emits (`iVar = unaff_gp`, the signed-32 GP constant, and
    # alias-to-alias copies) before checking constant displacements.  This is
    # intentionally not a general value-set/dataflow analysis.
    gp = 0xFEBEB800
    b6_lo, b6_hi = 0xFEBE4AF4, 0xFEBE4B13
    app_lo, app_hi = 0x20000, 0x100000
    # Fail closed if the small parser stops recognizing the Ghidra forms this
    # negative depends on. In particular, Ghidra commonly spells a negative
    # displacement as `base + -0xNNNN` and sometimes materializes GP as its
    # signed-32 constant instead of retaining the `unaff_gp` name.
    parser_probes = [
        "return unaff_gp - 0x6d0c;",
        "iVar1 = unaff_gp; return iVar1 + -0x6d0c;",
        "iVar2 = -0x1414800; return iVar2 - 0x6d0c;",
        "return DAT_febe4af4;",
    ]
    for probe in parser_probes:
        probe_hits = find_direct_region_hits(probe, gp, b6_lo, b6_hi)
        if not any(hit["address"] == "0xFEBE4AF4" for hit in probe_hits):
            raise ValueError(f"direct-region parser self-test failed: {probe}")

    direct_region_hits = []
    scanned_application_functions = 0
    for entry, row in rows.items():
        if not app_lo <= entry < app_hi:
            continue
        scanned_application_functions += 1
        text = row.get("decompiled_c", "") or ""
        hits = find_direct_region_hits(text, gp, b6_lo, b6_hi)
        if hits:
            direct_region_hits.append({"entry": f"0x{entry:08X}", "hits": hits})

    functions = []
    for entry in ENTRIES:
        row = rows.get(entry)
        if not row or not row.get("decompile_completed") or not row.get("decompiled_c"):
            raise SystemExit(f"missing complete decompile 0x{entry:X}")
        size = int(row["body_size"])
        body = image[entry:entry + size]
        if len(body) != size:
            raise SystemExit(f"function body outside image 0x{entry:X}")
        text = row["decompiled_c"]
        functions.append({
            "entry": f"0x{entry:08X}",
            "body_size": size,
            "body_sha256": sha(body),
            "decompiled_c_sha256": sha(text.encode()),
            "decompiled_c": text,
        })

    def rel(path: Path) -> str:
        resolved = path.resolve()
        return str(resolved.relative_to(REPO.resolve())) if resolved.is_relative_to(REPO.resolve()) else str(resolved)

    out = {
        "schema": "corolla-h-b6-full-receiver-decompiler-evidence-v1",
        "software_id": "8965H1202000",
        "generator": {"path": rel(GENERATOR), "sha256": sha(GENERATOR.read_bytes())},
        "image": {"path": rel(args.image), "size": len(image), "sha256": sha(image)},
        "source_corpus": {"path": rel(args.corpus), "sha256": sha(args.corpus.read_bytes())},
        "function_count": len(functions),
        "functions": functions,
        "direct_b6_com_region_reference_census": {
            "gp": f"0x{gp:08X}",
            "application_first": f"0x{app_lo:08X}",
            "application_end_exclusive": f"0x{app_hi:08X}",
            "scanned_application_function_count": scanned_application_functions,
            "first_byte": f"0x{b6_lo:08X}",
            "last_byte": f"0x{b6_hi:08X}",
            "direct_hits": direct_region_hits,
            "hit_count": len(direct_region_hits),
            "boundary": "Complete source-corpus application-function sweep for named absolute references and simple GP aliases/constants/copies with constant displacements. Bootloader reuse is outside the post-SecOC application question; arbitrary computed-base/value-set aliases remain outside this bounded census."
        },
        "boundary": (
            "Exact-H disposable-project decompilations for the protected 0x0B6 SecOC envelope and verified upper-delivery path. "
            "Every promoted body is raw-byte-bound to 8965H1202000. The evidence closes receiver-side extraction, freshness, "
            "authentication-input construction, and generic upper routing; it does not identify sender-side producer logic, "
            "the secret value selected by ICU-S slot 4, or arbitrary peripheral/DMA aliases outside recovered CPU code."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}: {len(functions)} functions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
