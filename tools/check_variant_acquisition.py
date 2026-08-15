#!/usr/bin/env python3
"""Check acquisition/variant readiness of a CodeFlash artifact (offline, read-only).

Given an acquired CodeFlash image (and optionally the `.run.json` produced by
``exploit/dumper/dump_codeflash.py``), this tool verifies the evidence chain that
the next analysis stages depend on and emits one machine-readable artifact:

1. **acquisition** — exact bare-1MiB geometry, recomputed SHA-256/size, and (when
   a run record is supplied) agreement of the run record's image SHA/completeness
   with the bytes on disk;
2. **structure triage** — the calibration-independent structural scanner runs on
   the image and its anchor classes are summarized (XCP surface, RAM-exec gate,
   boot-CRC descriptors, SecOC resolver prefilter);
3. **resolver readiness** — whether the image is in the exact state
   ``tools/resolve_secoc_patch_image.sh`` accepts (geometry + optional
   patch-manifest SHA binding), plus the exact next command to run.

The tool never mutates the image, never opens Ghidra, and never requires
hardware. A foreign calibration that passes here is *ready for triage*, not
validated: every Sienna-recovered mechanism remains a hypothesis until checked
against the target's own bytes (see docs/variants/README.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.analyze_rh850_codeflash_structure import analyze as scan_structure  # noqa: E402
from tools.build_secoc_patch_manifest import (  # noqa: E402
    P1M_E_CODEFLASH_SIZE,
    validate_codeflash_geometry,
)

SCHEMA = "variant-acquisition-readiness-v1"
RUN_SCHEMA = "p1me-codeflash-live-acquisition-v1"
MANIFEST_SCHEMA = "toyota-secoc-patch-manifest-v1"


class AcquisitionReadinessError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_json(path: Path, expected_schema: str, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionReadinessError(f"cannot load {label} {path}: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != expected_schema:
        raise AcquisitionReadinessError(
            f"{label} {path} has unsupported schema (expected {expected_schema})"
        )
    return data


def check_acquisition(image: Path, blob: bytes, run: dict[str, Any] | None) -> dict[str, Any]:
    """Geometry + SHA/size provenance, with optional dumper run-record binding."""
    try:
        validate_codeflash_geometry(len(blob))
        geometry_ok = True
        geometry_note = "exact bare 1 MiB RH850/P1M-E CodeFlash geometry"
    except ValueError as exc:
        geometry_ok = False
        geometry_note = str(exc)

    result: dict[str, Any] = {
        "geometry_valid": geometry_ok,
        "geometry_note": geometry_note,
        "size_bytes": len(blob),
        "expected_size_bytes": P1M_E_CODEFLASH_SIZE,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "path": str(image),
        "run_record": None,
    }

    if run is not None:
        image_record = run.get("image") or {}
        run_sha = image_record.get("sha256")
        complete = image_record.get("complete")
        missing = image_record.get("missing_word_count")
        capture = run.get("capture") or {}
        resolver = run.get("resolver") or {}
        checks = {
            "run_schema": RUN_SCHEMA,
            "run_image_sha256": run_sha,
            "run_sha_matches_bytes": run_sha == result["sha256"],
            "run_reports_complete": complete is True,
            "run_missing_word_count": missing,
            "run_interrupted": run.get("interrupted") is True,
            "run_capture_sha256": capture.get("sha256"),
            "run_capture_accepted_frames": capture.get("accepted_frames"),
            "run_resolver_status": resolver.get("status"),
        }
        result["run_record"] = checks
        result["problems"] = [
            name
            for name, ok in (
                ("run sha256 does not match image bytes", checks["run_sha_matches_bytes"]),
                ("run record does not report a complete acquisition", checks["run_reports_complete"]),
            )
            if not ok
        ]
    else:
        result["problems"] = [] if geometry_ok else ["image geometry is not resolver-ready"]
    return result


def check_structure(blob: bytes) -> dict[str, Any]:
    """Summarize the structural triage scan without claiming any transfer."""
    report = scan_structure(blob)
    xcp = report["xcp_command_surface"]
    boot = report["boot_trust"]
    ram_exec = report["ram_exec_gate"]
    prefilter = report["semantic_resolver_prefilter"]
    return {
        "schema": report["schema"],
        "image_sha256": report["image"]["sha256"],
        "geometry": report["image"]["geometry"]["classification"],
        "boot_trust": {
            "crc_descriptor_count": boot["crc_descriptor_count"],
            "terminal_valid_descriptor_count": boot["terminal_valid_descriptor_count"],
            "validity_marker_count": boot["validity_marker_word"]["count"],
        },
        "ram_exec_gate": {
            "download_window_immediate_count": ram_exec["download_window_base_immediates"]["count"],
            "package_descriptor_pair_count": ram_exec["package_descriptor_pair_count"],
        },
        "xcp_surface": {
            "request_can_id_immediate_count": xcp["request_can_id_immediates"]["count"],
            "response_can_id_immediate_count": xcp["response_can_id_immediates"]["count"],
            "command_map_window_count": xcp["command_map_window_count"],
        },
        "semantic_resolver_prefilter": {
            "byte_load_then_cmov_site_count": prefilter["byte_load_then_cmov_site_count"],
        },
        "disclaimer": report["disclaimer"],
    }


def check_resolver_readiness(
    acquisition: dict[str, Any], manifest: dict[str, Any] | None
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "resolver": "tools/resolve_secoc_patch_image.sh",
        "geometry_gate": acquisition["geometry_valid"],
        "manifest": None,
    }
    if manifest is not None:
        manifest_image = manifest.get("image") or {}
        result["manifest"] = {
            "schema": manifest.get("schema"),
            "image_sha256": manifest_image.get("sha256"),
            "sha_matches_bytes": manifest_image.get("sha256") == acquisition["sha256"],
            "semantic_resolution_present": isinstance(manifest.get("semantic_resolution"), dict),
        }
        result["manifest_bound"] = result["manifest"]["sha_matches_bytes"]
    else:
        result["manifest_bound"] = None
    result["ready"] = (
        acquisition["geometry_valid"]
        and not acquisition.get("problems")
        and result["manifest_bound"] is not False
    )
    result["next_step"] = (
        "run: tools/resolve_secoc_patch_image.sh <image> - (disposable Ghidra import; "
        "zero/multiple semantic candidates fail closed)"
        if result["ready"]
        else "fix acquisition problems above before invoking the semantic resolver"
    )
    return result


def build_report(
    image: Path,
    blob: bytes,
    run: dict[str, Any] | None,
    manifest: dict[str, Any] | None,
    notes: str | None,
) -> dict[str, Any]:
    acquisition = check_acquisition(image, blob, run)
    structure = check_structure(blob)
    resolver = check_resolver_readiness(acquisition, manifest)
    return {
        "schema": SCHEMA,
        "created_at": _utc_now(),
        "image_path": str(image),
        "notes": notes,
        "acquisition": acquisition,
        "structure_triage": structure,
        "resolver_readiness": resolver,
        "ready": acquisition["geometry_valid"] and not acquisition["problems"],
        "readiness_boundary": (
            "ready-for-triage means the artifact is bound (geometry, SHA, optional run/manifest "
            "provenance) and structurally scanned; it does not validate any Sienna-recovered "
            "mechanism on this target — all transfer claims stay hypothesis until verified "
            "against the target's own firmware"
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="acquired CodeFlash image (bare 1 MiB)")
    parser.add_argument(
        "--run-json",
        type=Path,
        help="optional .run.json written by exploit/dumper/dump_codeflash.py",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="optional patch manifest (toyota-secoc-patch-manifest-v1) to bind to the image",
    )
    parser.add_argument("--notes", help="free-form provenance note recorded verbatim")
    parser.add_argument("-o", "--output", type=Path, help="write the readiness artifact as JSON")
    args = parser.parse_args(argv)

    try:
        blob = args.image.read_bytes()
    except OSError as exc:
        parser.error(f"cannot read image: {exc}")

    run = None
    manifest = None
    try:
        if args.run_json is not None:
            run = _load_json(args.run_json, RUN_SCHEMA, "dumper run record")
        if args.manifest is not None:
            manifest = _load_json(args.manifest, MANIFEST_SCHEMA, "patch manifest")
    except AcquisitionReadinessError as exc:
        parser.error(str(exc))

    report = build_report(args.image, blob, run, manifest, args.notes)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
