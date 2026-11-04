#!/usr/bin/env python3
"""Recover every CP-protected PE body in the pinned GTS+ diagnostics suite."""
from __future__ import annotations

import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from tools.techstream.recover_cp_bodies import (
    _producer_provenance,
    _sha256,
    recover as recover_cp_bodies,
    recover_auxiliary,
)
from tools.techstream.recover_gtsplus_bodies import recover as recover_gtsplus_bodies

from tools import REPO_ROOT
from tools.techstream.techstream_paths import resolve_gts_root


DEFAULT_OUTPUT = REPO_ROOT / "build/out/gts-all-unprotected"
ProgressCallback = Callable[[str, int, int, Path], None]


def qualify_recovered_source(
    recovered: Path, protected: Path, *, component_root: Path
) -> dict[str, Any]:
    """Verify an output and protected pair against one exact manifest entry.

    This establishes reconstruction provenance. Managed IL admission belongs to
    inspect_dotnet_il.validate_managed_bodies; consumers retain native byte pins.
    """
    recovered = recovered.expanduser().resolve()
    protected = protected.expanduser().resolve()
    component_root = component_root.expanduser().resolve()
    relative = recovered.relative_to(component_root).as_posix()
    manifest_path = component_root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if "binaries" in manifest:
        matches = [row for row in manifest["binaries"] if row["path"] == relative]
        if len(matches) != 1:
            raise ValueError(f"recovery manifest requires one exact entry: {relative}")
        entry = matches[0]
        output_size = entry["plaintext"]["size"]
        output_sha256 = entry["plaintext"]["sha256"]
        pair = entry["protected"]
    else:
        matches = [row for row in manifest["entries"] if row["relative_path"] == relative]
        if len(matches) != 1:
            raise ValueError(f"recovery manifest requires one exact entry: {relative}")
        entry = matches[0]
        output_size = entry["output_size"]
        output_sha256 = entry["output_sha256"]
        pair = entry
    sidecar = Path(str(protected) + "._")
    for path, expected_size, expected_sha256 in (
        (recovered, output_size, output_sha256),
        (protected, pair["stub_size"], pair["stub_sha256"]),
        (sidecar, pair["sidecar_size"], pair["sidecar_sha256"]),
    ):
        if path.stat().st_size != expected_size or _sha256(path) != expected_sha256:
            raise ValueError(f"recovery manifest identity drift: {relative}: {path}")
    return {
        "manifest": str(manifest_path),
        "manifest_sha256": _sha256(manifest_path),
        "relative_path": relative,
        "protected_stub_sha256": pair["stub_sha256"],
        "protected_sidecar_sha256": pair["sidecar_sha256"],
        "recovered_sha256": output_sha256,
        "method": manifest.get("method", manifest.get("format", manifest.get("schema"))),
    }


def _rewrite_component_manifest(manifest: dict[str, Any], staged: Path, final: Path) -> None:
    """Make a staged component manifest point at its post-commit location."""
    if "output_root" in manifest:
        manifest["output_root"] = str(final)
    (staged / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def recover(
    *,
    gtsplus_root: Path | None = None,
    output: Path = DEFAULT_OUTPUT,
    workers: int | None = None,
    keep_workspace: bool = False,
    progress: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Recover the 54 main GTSPlus, 143 CUWPlus, and 52 auxiliary bodies."""
    gts = resolve_gts_root(gtsplus_root)
    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    staging: Path | None = Path(tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=output.parent))

    try:
        assert staging is not None
        main = recover_gtsplus_bodies(
            output=staging / "GTSPlus",
            installed_root=gts,
            keep_workspace=keep_workspace,
        )
        if progress is not None:
            progress("GTSPlus", 54, 54, Path("GTSPlus"))

        cuw = recover_cp_bodies(
            gtsplus_root=gts,
            source=gts.parent / "CUWPlus",
            output=staging / "CUWPlus",
            workers=workers,
            keep_workspace=keep_workspace,
            workspace_name="cuwplus-body-recovery",
            progress=(
                (lambda done, total, path: progress("CUWPlus", done, total, path))
                if progress is not None
                else None
            ),
        )
        auxiliary = recover_auxiliary(
            gtsplus_root=gts,
            output=staging / "Auxiliary",
            workers=workers,
            keep_workspace=keep_workspace,
            progress=(
                (lambda done, total, path: progress("Auxiliary", done, total, path))
                if progress is not None
                else None
            ),
        )

        counts = {
            "gtsplus": int(main["recovered_plaintext_body_count"]),
            "cuwplus": int(cuw["recovered_body_count"]),
            "auxiliary": int(auxiliary["recovered_body_count"]),
        }
        total = sum(counts.values())
        if counts != {"gtsplus": 54, "cuwplus": 143, "auxiliary": 52} or total != 249:
            raise RuntimeError(f"unexpected protected-body census after recovery: {counts}, total={total}")

        final_components = {
            "GTSPlus": output / "GTSPlus",
            "CUWPlus": output / "CUWPlus",
            "Auxiliary": output / "Auxiliary",
        }
        _rewrite_component_manifest(main, staging / "GTSPlus", final_components["GTSPlus"])
        _rewrite_component_manifest(cuw, staging / "CUWPlus", final_components["CUWPlus"])
        _rewrite_component_manifest(auxiliary, staging / "Auxiliary", final_components["Auxiliary"])

        manifest = {
            "format": "gtsplus-all-protected-body-recovery-v1",
            "gtsplus_version": main["gtsplus_version"],
            "source_root": str(gts.parent),
            "gtsplus_root": str(gts),
            "producer": _producer_provenance(
                Path(__file__), Path(__file__).with_name("recover_gtsplus_bodies.py"),
            ),
            "output_root": str(output),
            "protected_body_count": 249,
            "recovered_body_count": total,
            "components": {
                "GTSPlus": {
                    "method": "same-release-installer-plaintext-twin",
                    "count": counts["gtsplus"],
                    "manifest": str(final_components["GTSPlus"] / "manifest.json"),
                    "manifest_sha256": _sha256(staging / "GTSPlus" / "manifest.json"),
                },
                "CUWPlus": {
                    "method": "cp-emulation-clean-pe-rebuild",
                    "count": counts["cuwplus"],
                    "manifest": str(final_components["CUWPlus"] / "manifest.json"),
                    "manifest_sha256": _sha256(staging / "CUWPlus" / "manifest.json"),
                },
                "Auxiliary": {
                    "method": "cp-emulation-clean-pe-rebuild",
                    "count": counts["auxiliary"],
                    "manifest": str(final_components["Auxiliary"] / "manifest.json"),
                    "manifest_sha256": _sha256(staging / "Auxiliary" / "manifest.json"),
                },
            },
        }
        (staging / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

        backup = output.parent / f".{output.name}.previous"
        shutil.rmtree(backup, ignore_errors=True)
        if output.exists():
            output.rename(backup)
        try:
            staging.rename(output)
            staging = None
        except Exception:
            if backup.exists() and not output.exists():
                backup.rename(output)
            raise
        else:
            shutil.rmtree(backup, ignore_errors=True)
        return manifest
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
