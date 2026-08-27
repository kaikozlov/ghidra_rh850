#!/usr/bin/env python3
"""Verify the generated knowledge cross-reference layer.

The repository accepts no organization-debt baseline.  This test requires:

* every generated index/footer/artifact-registry block to match fresh generation;
* every knowledge-index health metric to be exactly zero;
* no structural generator errors or warnings; and
* the primary navigation documents to link to the knowledge index.

Run via ``tools/test knowledge_index``.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from verification_deps import path_matches_pattern, repository_paths, suite_dependency_map  # noqa: E402

GENERATOR = REPO / "tools/build_knowledge_index.py"
INDEX = REPO / "docs/reference/index.md"
ARTIFACTS = REPO / "docs/reference/generated-artifacts.md"

ZERO_METRICS = (
    "finding_home_backlink_failures",
    "correction_backlink_failures",
    "findings_unmentioned",
    "generated_artifact_inventory_gaps",
    "orphans",
    "broken_links",
    "unmapped_docs",
    "unmapped_data",
)

passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> bool:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" ({detail})" if detail else ""))
    return ok


def main() -> int:
    check("generator exists", GENERATOR.exists())
    check("knowledge index exists", INDEX.exists())
    check("generated-artifacts inventory exists", ARTIFACTS.exists())
    check("no organization-debt baseline file",
          not (REPO / "tools/knowledge_index_baseline.json").exists())

    report_proc = subprocess.run(
        [sys.executable, str(GENERATOR), "--json"],
        capture_output=True, text=True, cwd=REPO,
    )
    check("generator --json succeeded", report_proc.returncode == 0,
          report_proc.stderr.strip()[:300])
    report = json.loads(report_proc.stdout)

    check("zero generator errors", not report["errors"],
          "; ".join(report["errors"][:5]))
    check("zero generator warnings", not report["warnings"],
          "; ".join(report["warnings"][:5]))

    metrics = report["metrics"]
    for key in ZERO_METRICS:
        check(f"{key} == 0", metrics.get(key) == 0,
              f"actual {metrics.get(key)!r}")

    check_proc = subprocess.run(
        [sys.executable, str(GENERATOR), "--check"],
        capture_output=True, text=True, cwd=REPO,
    )
    check("all generated knowledge outputs are drift-free",
          check_proc.returncode == 0 and check_proc.stdout.strip() == "clean",
          (check_proc.stdout + check_proc.stderr).strip()[:500])
    check("generator reports no managed-file drift", not report["drift"],
          ", ".join(report["drift"][:10]))

    # Independent shape checks: the generated layer must be visible where a
    # reader actually lands, not only in the global index.
    findings = (REPO / "docs/status/FINDINGS.md").read_text(encoding="utf-8")
    canonical_footer_docs = 0
    for path in REPO.glob("docs/**/*.md"):
        text = path.read_text(encoding="utf-8")
        if "<!-- knowledge-cross-references:begin -->" in text:
            canonical_footer_docs += 1
            check(f"balanced xref markers: {path.relative_to(REPO)}",
                  text.count("<!-- knowledge-cross-references:begin -->") == 1
                  and text.count("<!-- knowledge-cross-references:end -->") == 1
                  and "## Knowledge cross-references" in text)
    check("visible cross-reference footers were generated",
          canonical_footer_docs > 0, f"count {canonical_footer_docs}")

    artifact_text = ARTIFACTS.read_text(encoding="utf-8")
    tracked_generated = subprocess.run(
        ["git", "ls-files", "--", "data/generated"],
        cwd=REPO, text=True, capture_output=True, check=True,
    ).stdout.splitlines()
    missing = [p for p in tracked_generated if f"`{p}`" not in artifact_text]
    check("complete tracked data/generated registry", not missing,
          ", ".join(missing[:10]))

    check("FINDINGS retains restored SECOC-042 row",
          "| SECOC-042 |" in findings and "[truncated]" not in next(
              line for line in findings.splitlines() if line.startswith("| SECOC-042 |")))

    docs_readme = (REPO / "docs/README.md").read_text(encoding="utf-8")
    ref_readme = (REPO / "docs/reference/README.md").read_text(encoding="utf-8")
    root_readme = (REPO / "README.md").read_text(encoding="utf-8")
    check("docs/README.md links knowledge index", "reference/index.md" in docs_readme)
    check("docs/reference/README.md links knowledge index", "index.md" in ref_readme)
    check("root README.md links knowledge index", "docs/reference/index.md" in root_readme)
    manifest = tomllib.loads((REPO / "verification.toml").read_text(encoding="utf-8"))
    mechanical = suite_dependency_map(REPO, manifest, repository_paths(REPO))
    ownership = [
        *manifest["suite"]["knowledge_index"].get("paths", []),
        *mechanical.get("knowledge_index", set()),
    ]
    check(
        "knowledge index suite-owned",
        any(path_matches_pattern("docs/reference/index.md", pattern) for pattern in ownership),
    )

    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
