#!/usr/bin/env python3
"""Verify the acquisition -> structure-scanner -> resolver-readiness artifact."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from tools.build_secoc_patch_manifest import P1M_E_CODEFLASH_SIZE, validate_codeflash_geometry  # noqa: E402
from tools.check_variant_acquisition import (  # noqa: E402
    MANIFEST_SCHEMA,
    RUN_SCHEMA,
    SCHEMA,
    AcquisitionReadinessError,
    build_report,
    check_acquisition,
    check_resolver_readiness,
    check_structure,
)

FIRMWARE = REPO / "firmware" / "RH850_P1M-E_CodeFlash.bin"
BLOB = FIRMWARE.read_bytes()
import hashlib  # noqa: E402

SHA = hashlib.sha256(BLOB).hexdigest()
passed = failed = 0


def check(label: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {label}{suffix}")


print("== acquisition stage ==")
check("schema pinned as v1", SCHEMA == "variant-acquisition-readiness-v1")
acq = check_acquisition(FIRMWARE, BLOB, None)
check("canonical firmware passes the geometry gate", acq["geometry_valid"] is True and acq["problems"] == [])
check("acquisition recomputes the canonical SHA-256", acq["sha256"] == SHA and acq["size_bytes"] == P1M_E_CODEFLASH_SIZE)
short = check_acquisition(Path("truncated.bin"), BLOB[:0x80000], None)
check("truncated image fails the geometry gate with no problems list suppression", short["geometry_valid"] is False and short["problems"] == ["image geometry is not resolver-ready"])
concat = check_acquisition(Path("concat.bin"), b"\x00" * 0x8000 + BLOB, None)
check("DataFlash+CodeFlash concatenation is diagnosed as DataFlash-relative", concat["geometry_valid"] is False and "strip the leading 0x8000" in concat["geometry_note"])

run_record = {
    "schema": RUN_SCHEMA,
    "image": {"sha256": SHA, "complete": True, "missing_word_count": 0},
    "capture": {"sha256": "0" * 64, "accepted_frames": 262145},
    "resolver": {"status": "resolved"},
    "interrupted": False,
}
bound = check_acquisition(FIRMWARE, BLOB, run_record)
check("run record SHA binding passes for matching bytes", bound["run_record"]["run_sha_matches_bytes"] is True and bound["run_record"]["run_reports_complete"] is True and bound["problems"] == [])
bad_run = dict(run_record)
bad_run["image"] = {"sha256": "f" * 64, "complete": False, "missing_word_count": 4}
mismatch = check_acquisition(FIRMWARE, BLOB, bad_run)
check(
    "run record SHA/completeness disagreement is reported as problems",
    mismatch["run_record"]["run_sha_matches_bytes"] is False
    and mismatch["run_record"]["run_reports_complete"] is False
    and mismatch["problems"] == [
        "run sha256 does not match image bytes",
        "run record does not report a complete acquisition",
    ],
    repr(mismatch["problems"]),
)

print("\n== structure triage stage ==")
structure = check_structure(BLOB)
check("triage stage summarizes the scanner output", structure["schema"] == "rh850-codeflash-structure-triage-v1" and structure["image_sha256"] == SHA)
check("canonical image classifies as bare 1 MiB CodeFlash", structure["geometry"] == "bare-codeflash-1m")
check("Sienna image shows the XCP route/map anchors", structure["xcp_surface"]["command_map_window_count"] >= 1 and structure["xcp_surface"]["request_can_id_immediate_count"] >= 1)
check("Sienna image shows boot-CRC descriptors and RAM-exec anchors", structure["boot_trust"]["crc_descriptor_count"] >= 1 and structure["ram_exec_gate"]["download_window_immediate_count"] >= 1)
check("Sienna image shows resolver prefilter sites", structure["semantic_resolver_prefilter"]["byte_load_then_cmov_site_count"] >= 1)
check("triage stage keeps the no-transfer disclaimer", "does not prove" in structure["disclaimer"] or "triage candidates" in structure["disclaimer"])

print("\n== resolver readiness stage ==")
resolver = check_resolver_readiness(acq, None)
check("geometry-valid acquisition is resolver-ready without a manifest", resolver["ready"] is True and resolver["manifest_bound"] is None)
check("ready result names the exact next command", "tools/resolve_secoc_patch_image.sh" in resolver["next_step"])
blocked = check_resolver_readiness(short, None)
check("geometry-invalid acquisition is not resolver-ready", blocked["ready"] is False and "fix acquisition problems" in blocked["next_step"])

good_manifest = {"schema": MANIFEST_SCHEMA, "image": {"sha256": SHA}, "semantic_resolution": {"gate_va": "0x8E6C8"}}
manifest_bound = check_resolver_readiness(acq, good_manifest)
check("manifest SHA binding passes for matching bytes", manifest_bound["manifest_bound"] is True and manifest_bound["ready"] is True and manifest_bound["manifest"]["semantic_resolution_present"] is True)
wrong_manifest = {"schema": MANIFEST_SCHEMA, "image": {"sha256": "e" * 64}, "semantic_resolution": {}}
manifest_refused = check_resolver_readiness(acq, wrong_manifest)
check("manifest SHA mismatch blocks readiness", manifest_refused["manifest_bound"] is False and manifest_refused["ready"] is False)

print("\n== full report and CLI ==")
report = build_report(FIRMWARE, BLOB, run_record, good_manifest, "unit-test provenance note")
check("report is JSON-serializable and pins the boundary text", json.dumps(report) is not None and report["schema"] == SCHEMA and "hypothesis" in report["readiness_boundary"])
check("report records the verbatim provenance note", report["notes"] == "unit-test provenance note")
check("report ready flag agrees with stages", report["ready"] is True and report["acquisition"]["geometry_valid"] and report["resolver_readiness"]["ready"])

with tempfile.TemporaryDirectory() as td:
    temp = Path(td)
    image = temp / "target.bin"
    image.write_bytes(BLOB)
    out = temp / "readiness.json"
    cli = subprocess.run(
        [sys.executable, str(REPO / "tools/check_variant_acquisition.py"), str(image), "-o", str(out), "--notes", "cli"],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("CLI exits 0 on a ready artifact", cli.returncode == 0)
    written = json.loads(out.read_text())
    check("CLI artifact matches the report schema and SHA", written["schema"] == SCHEMA and written["acquisition"]["sha256"] == SHA)

    partial = temp / "partial.bin"
    partial.write_bytes(BLOB[:0x1000])
    bad = subprocess.run(
        [sys.executable, str(REPO / "tools/check_variant_acquisition.py"), str(partial)],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("CLI exits nonzero on a non-ready artifact", bad.returncode != 0 and "reject truncated or oversized" in bad.stdout)

    bad_run_path = temp / "run.json"
    bad_run_path.write_text(json.dumps(bad_run))
    schema_refusal = subprocess.run(
        [sys.executable, str(REPO / "tools/check_variant_acquisition.py"), str(image), "--run-json", str(bad_run_path)],
        cwd=REPO, capture_output=True, text=True, check=False,
    )
    check("CLI still reports run-record problems through the exit code", schema_refusal.returncode == 1)
    foreign = temp / "foreign.json"
    foreign.write_text(json.dumps({"schema": "something-else"}))
    try:
        from tools.check_variant_acquisition import _load_json
        _load_json(foreign, RUN_SCHEMA, "dumper run record")
    except AcquisitionReadinessError:
        check("foreign run-record schema is rejected", True)
    else:
        check("foreign run-record schema is rejected", False)

print(f"\nResults: {passed} passed, {failed} failed")
raise SystemExit(1 if failed else 0)
