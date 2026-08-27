#!/usr/bin/env python3
"""Generate a complete static census of CUW writer DLLs selected by V18 factory rows.

This artifact intentionally separates exact wire grammar already recovered for the
standard/unified/VFOREST paths from broader import-level fingerprints for the
remaining legacy/specialized writer families.  Import fingerprints are structural
evidence; they are not promoted to request semantics without an independently
recovered builder.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

from techstream_paths import V18_DIAGNOSTICS_ROOT
from typing import Any

import pefile
from pe_utils import exports as pe_exports, imports as pe_imports

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from tools.techstream.generate_cuw_writer_inventory import COMMANDS, factory_routes  # noqa: E402
from tools.techstream.generate_cuw_writer_protocol_grammar import route_verdict  # noqa: E402

DEFAULT_ROOT = V18_DIAGNOSTICS_ROOT
DEFAULT_OUT = REPO / "data/generated/techstream_v18/cuw_writer_family_matrix.json"
CUW_SUBDIR = Path("Calibration Update Wizard")

COMMON_DLLS = {
    "TCUWCanCommonPrepareWriter.dll": "common_prepare",
    "TCUWCanCommonFlashWriter.dll": "common_flash",
    "TCUWCanDiagCommUtils.dll": "diag_comm",
    "TCUWJ2534DeviceIF.dll": "j2534",
    "TCUWFlashWriterUtils.dll": "flash_utils",
    "TCUWParameterForVC.dll": "parameter",
}

EXACT_ROUTE_BY_DLL = {
    "TCUWCanReproStdPrepareWriter.dll": "standard-prepare",
    "TCUWCanReproStdFlashWriter.dll": "standard-flash",
    "TCUWCanUnifiedPrepareWriter.dll": "unified-prepare",
    "TCUWCanUnifiedFlashWriter.dll": "unified-flash",
    "TCUWCanUnifiedFlashWriterEachArea.dll": "unified-flash-each-area",
    "TCUWCanSecurityVFORESTFlashWriter.dll": "security-vforest-flash",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def undecorated_tail(name: str) -> str:
    """Return the human-meaningful C++ method token when one is present."""
    m = re.search(r"\?([A-Za-z0-9_]+)@", name)
    return m.group(1) if m else name


def classify_tags(name: str, imports: list[dict[str, str]]) -> list[str]:
    joined = "\n".join(x["name"] for x in imports)
    tags: set[str] = set()
    if "PrepareWriter" in name:
        tags.add("prepare")
    if "FlashWriter" in name:
        tags.add("flash")
    if "Ethernet" in name:
        tags.add("ethernet")
    if "Unified" in name:
        tags.add("unified")
    if "ReproStd" in name or "Reprostd" in name:
        tags.add("repro-standard")
    if "VFOREST" in name:
        tags.add("vforest")
    if "Security" in name:
        tags.add("security-named")
    if "CalcSeedKeyForSecurityUp" in joined:
        tags.add("security-up-aes-wrapper")
    if "CalcSeedKey@" in joined:
        tags.add("seed-key")
    if any(token in joined for token in ("SendNonce@", "SendSeedKey@", "SendNonceAndSeedKey@")):
        tags.add("nonce-seed-material-transfer")
    if "SendRequMsgAndReceiveRespMsgForP5Can" in joined:
        tags.add("p5-can-diagnostic-transport")
    if "CCanCommonFlashWriter" in joined:
        tags.add("common-flash-protocol")
    if "CCanCommonPrepareWriter" in joined:
        tags.add("common-prepare-protocol")
    if "GetECUAuthKey@CalibrationFile" in joined and "GetServiceAuthKey@CalibrationFile" in joined:
        tags.add("calibration-auth-pair")
    if "GetNonce@CalibrationFile" in joined:
        tags.add("calibration-nonce")
    if "GetSeedKey@CalibrationFile" in joined:
        tags.add("calibration-seed-key")
    if "GetOffsetAddress@CalibrationFile" in joined:
        tags.add("calibration-offset")
    return sorted(tags)


def exact_commands(name: str) -> list[dict[str, Any]]:
    route = EXACT_ROUTE_BY_DLL.get(name)
    if route is None:
        return []
    out: list[dict[str, Any]] = []
    for command in COMMANDS:
        r = command["route"]
        if r == route or (r == "both-flash" and "flash" in route):
            out.append(command)
    # Unified EachArea's exact request builders are pinned by the second-stage
    # route-grammar artifact rather than COMMANDS; do not duplicate them here.
    if route == "unified-flash-each-area":
        return []
    return out


def target_disposition(name: str, tags: list[str]) -> dict[str, str]:
    """Writer-level structural summary.

    Exact target compatibility is a property of the prepare+flash route, not an
    isolated DLL.  `target_route_dispositions` below is authoritative and is
    computed with the same exact route classifier as the protocol-grammar
    artifact.  Keep this field only for backward-compatible structural hints.
    """
    if name in {"TCUWCanReproStdPrepareWriter.dll", "TCUWCanReproStdFlashWriter.dll"}:
        status = "structural-standard-family"
    elif name in {"TCUWCanUnifiedPrepareWriter.dll", "TCUWCanUnifiedFlashWriter.dll", "TCUWCanUnifiedFlashWriterEachArea.dll"}:
        status = "structural-unified-family"
    elif "nonce-seed-material-transfer" in tags or "vforest" in tags:
        status = "structural-vforest-family"
    else:
        status = "structural-specialized-family"
    return {
        "sienna_8965B4512000": status,
        "corolla_8965H1202000": status,
        "reason": "writer-level import/tag summary only; exact target disposition is route-pair-specific in target_route_dispositions",
    }


def inspect_writer(path: Path, roles: set[str], route_rows: list[dict[str, Any]]) -> dict[str, Any]:
    data = path.read_bytes()
    pe = pefile.PE(data=data)
    imports = pe_imports(pe)
    exports = pe_exports(pe, unnamed_none=True)

    calibration = []
    categorized: dict[str, list[str]] = {value: [] for value in COMMON_DLLS.values()}
    for item in imports:
        dll, name = item["dll"], item["name"]
        if dll == "TCUWCalibrationFile.dll" and ("@CalibrationFile@@" in name or "@CalibArchivedFile@@" in name):
            calibration.append(undecorated_tail(name))
        if dll in COMMON_DLLS:
            categorized[COMMON_DLLS[dll]].append(undecorated_tail(name))

    tags = classify_tags(path.name, imports)
    factories = sorted({row["factory_identifier"] for row in route_rows if row["factory_identifier"]})
    params = sorted({row["parameter_file"] for row in route_rows})
    pair_counts = collections.Counter((row["prepare_writer"], row["flash_writer"]) for row in route_rows)
    route_dispositions = []
    for (prepare, flash), count in sorted(pair_counts.items()):
        verdict, reason = route_verdict(prepare, flash)
        route_dispositions.append({
            "prepare_writer": prepare,
            "flash_writer": flash,
            "factory_rows": count,
            "sienna_8965B4512000": verdict,
            "corolla_8965H1202000": verdict,
            "reason": reason,
        })
    result = {
        "name": path.name,
        "roles": sorted(roles),
        "route_row_count": len(route_rows),
        "factory_identifiers": factories,
        "parameter_files": params,
        "size": len(data),
        "sha256": sha256(data),
        "image_base": pe.OPTIONAL_HEADER.ImageBase,
        "exports": sorted(exports, key=lambda x: (x["rva"], x["name"] or "")),
        "calibration_getters": sorted(set(calibration)),
        "common_operations": {k: sorted(set(v)) for k, v in categorized.items() if v},
        "protocol_tags": tags,
        "exact_recovered_commands": exact_commands(path.name),
        "target_disposition": target_disposition(path.name, tags),
        "target_route_dispositions": route_dispositions,
    }
    return result


def generate(root: Path) -> dict[str, Any]:
    routes, stats = factory_routes(root)
    by_name: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    roles: dict[str, set[str]] = collections.defaultdict(set)
    for row in routes:
        for key, role in (("prepare_writer", "prepare"), ("flash_writer", "flash")):
            name = row[key]
            if name:
                by_name[name].append(row)
                roles[name].add(role)

    writers = []
    missing = []
    for name in sorted(by_name, key=str.lower):
        path = root / CUW_SUBDIR / name
        if not path.is_file():
            missing.append(name)
            continue
        writers.append(inspect_writer(path, roles[name], by_name[name]))

    prep = [w for w in writers if "prepare" in w["roles"]]
    flash = [w for w in writers if "flash" in w["roles"]]
    tag_counts = collections.Counter(tag for w in writers for tag in w["protocol_tags"])
    return {
        "schema_version": 2,
        "source": "external-source",
        "distribution": "Toyota Techstream V18.00.003",
        "route_stats": stats,
        "writer_stats": {
            "distinct_referenced_writers": len(by_name),
            "present_referenced_writers": len(writers),
            "prepare_writers": len(prep),
            "flash_writers": len(flash),
            "missing_referenced_writers": missing,
            "protocol_tag_counts": dict(sorted(tag_counts.items())),
        },
        "evidence_boundary": {
            "imports": "structural: imported helper/getter names prove dependencies, not exact on-wire requests",
            "exact_recovered_commands": "recovered subset: this inventory retains legacy COMMANDS pins; the second-stage route-grammar artifact owns the additional exact formerly-specialized builders",
            "target_disposition": "writer-level structural compatibility hint retained for backward compatibility; do not use for route decisions",
            "target_route_dispositions": "exact route-pair classifier shared with cuw_writer_protocol_grammar.json; all 196 rows are either byte-compatible or rejected",
        },
        "writers": writers,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    result = generate(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
