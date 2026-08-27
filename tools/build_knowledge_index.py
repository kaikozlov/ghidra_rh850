#!/usr/bin/env python3
"""Generate and validate the repository knowledge cross-reference layer.

The status ledgers remain the single source of truth for knowledge identities:
``FINDINGS.md`` owns finding IDs/canonical homes, ``CORRECTIONS.md`` owns
correction IDs/canonical homes, and ``OPEN_QUESTIONS.md`` owns active lead IDs.
This tool derives three navigation artifacts from them:

* ``docs/reference/index.md`` — global finding/correction/OQ/document registry;
* visible ``## Knowledge cross-references`` footers in every canonical Markdown
  home named by FINDINGS/CORRECTIONS;
* a complete generated ``data/generated/**`` registry inside
  ``docs/reference/generated-artifacts.md``.

Generated blocks are deterministic and replaceable.  ``--check`` verifies all
managed outputs without writing.  ``tests/verify_knowledge_index.py`` requires
all graph-health metrics to be exactly zero; there is intentionally no debt
baseline or ratchet.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from verification_deps import repository_paths, suite_dependency_map

REPO = Path(__file__).resolve().parent.parent
INDEX = REPO / "docs/reference/index.md"
ARTIFACTS = REPO / "docs/reference/generated-artifacts.md"

FINDINGS = "docs/status/FINDINGS.md"
CORRECTIONS = "docs/status/CORRECTIONS.md"
OPEN_QUESTIONS = "docs/status/OPEN_QUESTIONS.md"
INDEX_KEY = "docs/reference/index.md"
ARTIFACTS_KEY = "docs/reference/generated-artifacts.md"

FINDING_ROW = re.compile(r"^\|\s*`?([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)`?\s*\|")
CORRECTION_HEAD = re.compile(r"^###\s+(CORR-\d+)\b")
OQ_HEAD = re.compile(r"^- \*\*(OQ-\d{3}) — (.+?)(?:\.\*\*|\*\*)(.*)$", re.M)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
ID_MENTION = re.compile(r"\b([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d+)\b")

# FINDINGS rows must point to a narrative/report home, not back to status/root
# navigation.  Corrections are allowed to use FINDINGS as a navigation home
# when the corrected truth is represented by finding rows.
FINDING_NON_HOME = (CORRECTIONS, FINDINGS, "README.md")

XREF_BEGIN = "<!-- knowledge-cross-references:begin -->"
XREF_END = "<!-- knowledge-cross-references:end -->"
REGISTRY_BEGIN = "<!-- generated-artifact-registry:begin -->"
REGISTRY_END = "<!-- generated-artifact-registry:end -->"


@dataclass
class Entry:
    fid: str
    homes: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)


def repo_path(p: str, base: Path) -> str:
    return os.path.relpath((base / p).resolve(), REPO)


def unique(seq: list[str]) -> list[str]:
    return list(dict.fromkeys(seq))


def natural_id_key(value: str) -> tuple[str, int, str]:
    m = re.match(r"^(.*?)-(\d+)$", value)
    return (m.group(1), int(m.group(2)), value) if m else (value, -1, value)


def tracked_paths(pathspec: str) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "--", pathspec],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=True,
    )
    return sorted(p for p in proc.stdout.splitlines() if p)


def parse_finding_rows(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        m = FINDING_ROW.match(line)
        if m:
            out.append(m.group(1))
    return out


def scan_mentions(docs: dict[str, str]) -> dict[str, set[str]]:
    mentions: dict[str, set[str]] = collections.defaultdict(set)
    for path, text in docs.items():
        for m in ID_MENTION.finditer(text):
            mentions[m.group(1)].add(path)
    return mentions


def build_link_graph(docs: dict[str, str]) -> tuple[set[tuple[str, str]], set[str]]:
    """Collect relative Markdown-link edges and missing targets."""
    edges: set[tuple[str, str]] = set()
    broken: set[str] = set()
    known = set(docs)
    for src, text in docs.items():
        base = REPO / src
        for m in LINK.finditer(text):
            target = m.group(1).split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            # Pseudocode occasionally contains link-shaped fragments such as
            # ``[x](a, b)``.  They are not Markdown navigation targets.
            if any(ch.isspace() for ch in target):
                continue
            tp = repo_path(target, base.parent)
            edges.add((src, tp))
            if tp not in known and not (REPO / tp).exists():
                broken.add(f"{src} -> {target}")
    return edges, broken


def strip_block(text: str, begin: str, end: str) -> str:
    pattern = re.compile(
        r"\n*" + re.escape(begin) + r".*?" + re.escape(end) + r"\n*",
        re.S,
    )
    return pattern.sub("\n", text).rstrip() + "\n"


def replace_or_append_block(text: str, begin: str, end: str, body: str) -> str:
    base = strip_block(text, begin, end).rstrip()
    return base + "\n\n" + begin + "\n" + body.rstrip() + "\n" + end + "\n"


def canonical_fragment(block: str) -> str:
    """Return the canonical-home portion of one correction block.

    Most entries use ``- **Canonical:**``.  Five older entries use prose such
    as ``canonical report:``/``canonical tooling report:``; support those
    explicitly rather than treating every incidental link in a correction as a
    canonical home.
    """
    lines = block.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"- \*\*Canonical:\*\*", line):
            out = [line]
            for follow in lines[i + 1 :]:
                if not follow.strip() or follow.startswith("- **"):
                    break
                out.append(follow)
            return "\n".join(out)
    for i, line in enumerate(lines):
        if re.search(r"canonical(?: tooling)? reports?:", line, re.I):
            out = [line]
            for follow in lines[i + 1 :]:
                if not follow.strip() or follow.startswith("- **"):
                    break
                out.append(follow)
            return "\n".join(out)
    return ""


def extract_markdown_homes(fragment: str, *, relative_to: Path,
                           exclude: set[str]) -> list[str]:
    homes: list[str] = []
    for link in re.findall(r"\]\(([^)]+)\)", fragment):
        lp = link.split("#", 1)[0]
        if not lp.endswith(".md"):
            continue
        rp = repo_path(lp, relative_to)
        if rp not in exclude:
            homes.append(rp)
    # Backticked canonical paths (not Markdown links) are repo-root-relative.
    for tok in re.findall(r"`([^`]*\.md)`", fragment):
        if (REPO / tok).exists():
            rp = repo_path(tok, REPO)
            if rp not in exclude:
                homes.append(rp)
    return unique(homes)


def footer_for(path: str, findings: list[str], corrections: list[str]) -> str:
    rel_index = os.path.relpath(INDEX, (REPO / path).parent)

    def render(ids: list[str], prefix: str) -> str:
        if not ids:
            return "—"
        return ", ".join(
            f"[{item}]({rel_index}#{prefix}-{item.lower()})"
            for item in sorted(ids, key=natural_id_key)
        )

    return "\n".join([
        "## Knowledge cross-references",
        "",
        "Generated by `tools/build_knowledge_index.py` from the status ledgers;",
        "do not edit this block by hand.",
        "",
        f"- Findings with this document as canonical home: {render(findings, 'finding')}",
        f"- Corrections with this document as canonical home: {render(corrections, 'correction')}",
    ])


def expand_manifest_paths(paths: list[str]) -> list[str]:
    """Expand manifest file/directory paths for knowledge indexing only."""
    expanded: list[str] = []
    for path in paths:
        pp = REPO / path
        if pp.is_dir():
            expanded.extend(
                repo_path(str(f), REPO)
                for f in sorted(pp.rglob("*"))
                if f.is_file() and f.suffix in (
                    ".md", ".py", ".csv", ".json", ".jsonl", ".toml",
                    ".txt", ".sh",
                )
            )
        else:
            expanded.append(repo_path(path, REPO))
    return expanded


def artifact_registry(
    data_generated: list[str],
    owners: dict[str, list[str]],
    suites: dict[str, dict[str, object]],
    catalog_owners: dict[str, list[str]],
    catalogs: dict[str, dict[str, object]],
) -> str:
    lines = [
        "## Complete `data/generated/` registry",
        "",
        "Generated by `tools/build_knowledge_index.py` from tracked files and",
        "`verification.toml`; do not edit this block by hand.",
        "",
        "| Artifact | Verifying suite(s) | Gate test(s) | Catalog gate(s) |",
        "|---|---|---|---|",
    ]
    for path in data_generated:
        sset = unique(owners.get(path, []))
        tests = unique([
            test
            for sname in sset
            for test in suites[sname].get("tests", [])  # type: ignore[union-attr]
        ])
        gates = unique([
            str(catalogs[name].get("gate", ""))
            for name in unique(catalog_owners.get(path, []))
            if catalogs[name].get("gate")
        ])
        lines.append(
            f"| `{path}` | {', '.join(sset) or '—'} | "
            f"{', '.join(f'`{t}`' for t in tests) or '—'} | "
            f"{', '.join(f'`{g}`' for g in gates) or '—'} |"
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report generated-output drift without writing")
    ap.add_argument("--json", action="store_true",
                    help="emit machine-readable post-generation status")
    args = ap.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, int] = {}

    # ---- source documents --------------------------------------------------
    docs: dict[str, str] = {}
    for p in sorted(REPO.glob("docs/**/*.md")):
        docs[repo_path(str(p), REPO)] = p.read_text(encoding="utf-8")
    for extra in ("README.md", "AGENTS.md"):
        ep = REPO / extra
        if ep.exists():
            docs[extra] = ep.read_text(encoding="utf-8")

    # ---- verification ownership ------------------------------------------
    manifest = tomllib.loads((REPO / "verification.toml").read_text(encoding="utf-8"))
    suites: dict[str, dict[str, object]] = manifest["suite"]
    catalogs: dict[str, dict[str, object]] = manifest.get("catalog", {})
    suite_of_test: dict[str, list[str]] = collections.defaultdict(list)
    owners: dict[str, list[str]] = collections.defaultdict(list)
    catalog_owners: dict[str, list[str]] = collections.defaultdict(list)
    repo_paths = repository_paths(REPO)
    mechanical = suite_dependency_map(REPO, manifest, repo_paths)
    for sname, suite in suites.items():
        for test in suite.get("tests", []):  # type: ignore[union-attr]
            suite_of_test[test].append(sname)
        owned_patterns = [
            *list(suite.get("paths", [])),  # type: ignore[arg-type]
            *sorted(mechanical.get(sname, set())),
        ]
        for path in expand_manifest_paths(owned_patterns):
            owners[path].append(sname)
    for cname, catalog in catalogs.items():
        for path in expand_manifest_paths(list(catalog.get("paths", []))):  # type: ignore[arg-type]
            catalog_owners[path].append(cname)

    tests_on_disk = {repo_path(str(p), REPO) for p in REPO.glob("tests/verify_*.py")}
    suite_tests = set(suite_of_test)
    if tests_on_disk != suite_tests:
        if tests_on_disk - suite_tests:
            errors.append(
                "tests not owned by any verification.toml suite: "
                + repr(sorted(tests_on_disk - suite_tests))
            )
        if suite_tests - tests_on_disk:
            errors.append(
                "suites reference missing tests: "
                + repr(sorted(suite_tests - tests_on_disk))
            )

    # ---- findings ---------------------------------------------------------
    find_text = docs[FINDINGS]
    finding_ids_raw = parse_finding_rows(find_text)
    dupes = [fid for fid, n in collections.Counter(finding_ids_raw).items() if n > 1]
    if dupes:
        errors.append(f"duplicate finding IDs in FINDINGS.md: {dupes}")

    findings: dict[str, Entry] = {}
    for line in find_text.splitlines():
        m = FINDING_ROW.match(line)
        if not m:
            continue
        fid = m.group(1)
        # Right-split because claim prose may contain literal pipes while the
        # trailing scope/grade/checked/canonical columns do not.
        cells = line.rstrip("\n").rstrip("|").rsplit("|", 4)
        if len(cells) != 5:
            errors.append(f"{fid}: malformed FINDINGS row")
            continue
        canonical_cell, checked_cell = cells[4], cells[3]
        homes = extract_markdown_homes(
            canonical_cell,
            relative_to=(REPO / FINDINGS).parent,
            exclude=set(FINDING_NON_HOME),
        )
        tests: list[str] = []
        for token in re.findall(r"`([^`]+)`", checked_cell):
            if re.fullmatch(r"verify_[a-z0-9_]+\.py", token):
                tests.append(f"tests/{token}")
            elif token.startswith("tests/"):
                tests.append(token)
        findings[fid] = Entry(fid, unique(homes), unique(tests))

    for fid, entry in findings.items():
        if not entry.homes:
            errors.append(f"{fid}: no canonical Markdown home in FINDINGS row")
        for home in entry.homes:
            if not (REPO / home).exists():
                errors.append(f"{fid}: canonical report does not exist: {home}")

    # ---- corrections ------------------------------------------------------
    corr_text = docs[CORRECTIONS]
    correction_blocks: list[tuple[str, str]] = []
    correction_ids_raw: list[str] = []
    for block in re.split(r"^### ", corr_text, flags=re.M)[1:]:
        head = block.splitlines()[0]
        cm = CORRECTION_HEAD.match("### " + head)
        if not cm:
            continue
        cid = cm.group(1)
        correction_ids_raw.append(cid)
        correction_blocks.append((cid, block))
    dupes = [cid for cid, n in collections.Counter(correction_ids_raw).items() if n > 1]
    if dupes:
        errors.append(f"duplicate correction IDs in CORRECTIONS.md: {dupes}")

    corrections: dict[str, dict[str, list[str]]] = {}
    for cid, block in correction_blocks:
        fragment = canonical_fragment(block)
        if not fragment:
            errors.append(f"{cid}: missing canonical-home declaration")
            homes: list[str] = []
        else:
            homes = extract_markdown_homes(
                fragment,
                relative_to=(REPO / CORRECTIONS).parent,
                exclude={CORRECTIONS},
            )
        if not homes:
            errors.append(f"{cid}: canonical declaration has no Markdown home")
        corrections[cid] = {"homes": homes, "tests": []}
        for home in homes:
            if not (REPO / home).exists():
                errors.append(f"{cid}: canonical report does not exist: {home}")

    # Include canonical homes outside docs/ (exploit/community/root READMEs) in
    # the managed-text overlay so backlinks and --check cover them too.
    all_home_paths = sorted({
        home
        for entry in findings.values()
        for home in entry.homes
    } | {
        home
        for data in corrections.values()
        for home in data["homes"]
    })
    for path in all_home_paths:
        if path not in docs and (REPO / path).exists():
            docs[path] = (REPO / path).read_text(encoding="utf-8")

    # ---- generated artifact registry -------------------------------------
    data_generated = tracked_paths("data/generated")
    registry_body = artifact_registry(
        data_generated, owners, suites, catalog_owners, catalogs
    )
    raw_inventory = docs.get(ARTIFACTS_KEY, ARTIFACTS.read_text(encoding="utf-8"))
    expected_inventory = replace_or_append_block(
        raw_inventory, REGISTRY_BEGIN, REGISTRY_END, registry_body
    )
    docs[ARTIFACTS_KEY] = expected_inventory

    # ---- canonical-home footer overlay -----------------------------------
    home_findings: dict[str, list[str]] = collections.defaultdict(list)
    home_corrections: dict[str, list[str]] = collections.defaultdict(list)
    for fid, entry in findings.items():
        for home in entry.homes:
            home_findings[home].append(fid)
    for cid, data in corrections.items():
        for home in data["homes"]:
            home_corrections[home].append(cid)

    managed_texts: dict[str, str] = {ARTIFACTS_KEY: expected_inventory}
    home_paths = sorted(set(home_findings) | set(home_corrections))
    for path in home_paths:
        current = docs[path]
        expected = replace_or_append_block(
            current,
            XREF_BEGIN,
            XREF_END,
            footer_for(path, home_findings.get(path, []), home_corrections.get(path, [])),
        )
        docs[path] = expected
        managed_texts[path] = expected

    # Remove stale generated xref blocks from tracked Markdown files that are
    # no longer canonical homes.
    for path in tracked_paths("*.md"):
        if path in home_paths or path == INDEX_KEY or not (REPO / path).exists():
            continue
        current = (REPO / path).read_text(encoding="utf-8", errors="replace")
        if XREF_BEGIN in current:
            expected = strip_block(current, XREF_BEGIN, XREF_END)
            managed_texts[path] = expected
            if path in docs:
                docs[path] = expected

    # ---- open questions ---------------------------------------------------
    oq_text = docs[OPEN_QUESTIONS]
    oq: dict[str, str] = {}
    oq_ids_raw: list[str] = []
    for m in OQ_HEAD.finditer(oq_text):
        oq_ids_raw.append(m.group(1))
        oq[m.group(1)] = re.sub(r"\s+", " ", m.group(2).strip().rstrip("."))[:120]
    bullets = len(re.findall(r"(?m)^- \*\*", oq_text))
    if bullets != len(oq_ids_raw):
        errors.append(
            f"OPEN_QUESTIONS.md has {bullets - len(oq_ids_raw)} bullet(s) without OQ IDs"
        )
    dupes = [qid for qid, n in collections.Counter(oq_ids_raw).items() if n > 1]
    if dupes:
        errors.append(f"duplicate OQ IDs: {dupes}")

    oq_section: dict[str, str] = {}
    section = ""
    for line in oq_text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        m = re.match(r"^- \*\*(OQ-\d{3}) —", line)
        if m:
            oq_section[m.group(1)] = section

    oq_blocks: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for line in oq_text.splitlines():
        m = re.match(r"^- \*\*(OQ-\d{3}) —", line)
        if m:
            if cur:
                oq_blocks[cur] = "\n".join(buf)
            cur, buf = m.group(1), [line]
        elif cur:
            buf.append(line)
    if cur:
        oq_blocks[cur] = "\n".join(buf)

    oq_related: dict[str, list[str]] = collections.defaultdict(list)
    for qid, block in oq_blocks.items():
        for item in ID_MENTION.findall(block):
            if item in findings or item in corrections:
                oq_related[qid].append(item)
        oq_related[qid] = unique(oq_related[qid])

    # ---- post-generation health ------------------------------------------
    post_docs = {p: t for p, t in docs.items() if p != INDEX_KEY}
    mentions = scan_mentions(post_docs)

    metrics["finding_home_backlink_failures"] = sum(
        1
        for fid, entry in findings.items()
        for home in entry.homes
        if fid not in docs.get(home, "")
    )
    metrics["correction_backlink_failures"] = sum(
        1
        for cid, data in corrections.items()
        for home in data["homes"]
        if cid not in docs.get(home, "")
    )
    metrics["findings_unmentioned"] = sum(
        1
        for fid in findings
        if not [p for p in mentions.get(fid, set()) if p != FINDINGS]
    )

    graph_docs = {
        p: t for p, t in post_docs.items()
        if p.startswith("docs/") or p in {"README.md", "AGENTS.md"}
    }
    edges, broken = build_link_graph(graph_docs)
    inbound: dict[str, set[str]] = collections.defaultdict(set)
    for src, dst in edges:
        if dst in docs:
            inbound[dst].add(src)
    orphans = sorted(
        p for p in docs
        if p.startswith("docs/")
        and p not in {"docs/README.md", INDEX_KEY}
        and not inbound.get(p)
    )
    metrics["orphans"] = len(orphans)
    metrics["broken_links"] = len(broken)

    unmapped_docs = sorted(
        p for p in docs
        if p.startswith("docs/") and p != INDEX_KEY and p not in owners
    )
    data_files = {repo_path(str(p), REPO) for p in REPO.glob("data/*.*")}
    data_files.update(repo_path(str(p), REPO) for p in REPO.glob("data/generated/**/*.*"))
    unmapped_data = sorted(
        p for p in data_files if p not in owners and p not in catalog_owners
    )
    metrics["unmapped_docs"] = len(unmapped_docs)
    metrics["unmapped_data"] = len(unmapped_data)

    metrics["generated_artifact_inventory_gaps"] = sum(
        1 for path in data_generated if f"`{path}`" not in expected_inventory
    )

    for key in (
        "finding_home_backlink_failures",
        "correction_backlink_failures",
        "findings_unmentioned",
        "generated_artifact_inventory_gaps",
        "orphans",
        "broken_links",
        "unmapped_docs",
        "unmapped_data",
    ):
        if metrics.get(key, 0) != 0:
            errors.append(f"{key} must be zero, found {metrics[key]}")
    for path in orphans:
        warnings.append(f"orphan document: {path}")
    for item in sorted(broken):
        warnings.append(f"broken link: {item}")
    for path in unmapped_docs:
        warnings.append(f"doc not owned by verification.toml: {path}")
    for path in unmapped_data:
        warnings.append(f"data artifact lacks suite/catalog ownership: {path}")

    # ---- global index -----------------------------------------------------
    def fmt_link(path: str, label: str | None = None) -> str:
        label = label or path
        return f"[{label}]({os.path.relpath((REPO / path).resolve(), INDEX.parent)})"

    lines: list[str] = [
        "# Knowledge index",
        "",
        "GENERATED by `tools/build_knowledge_index.py` from `verification.toml` and",
        "the three status ledgers. Do not hand-edit generated blocks; rerun the",
        "generator. Canonical reports carry visible generated cross-reference footers",
        "back to the IDs below.",
        "",
        f"Findings: {len(findings)} · Corrections: {len(corrections)} · "
        f"Open questions: {len(oq)} · Docs: {len(docs)} · Suites: {len(suites)}",
        "",
        "## Reading this index",
        "",
        "- [Finding index](#finding-index): canonical reports, references, tests, and leads.",
        "- [Open-questions index](#open-questions-index): stable active-lead IDs.",
        "- [Correction index](#correction-index): canonical homes for corrected claims.",
        "- [Document registry](#document-registry): verification ownership.",
        "- [Graph health](#graph-health): all organization invariants; every value must be zero.",
        "",
        "## Finding index",
        "",
        "| Finding | Canonical report(s) | Also referenced by | Tests | Related OQ |",
        "|---|---|---|---|---|",
    ]
    for fid in sorted(findings, key=natural_id_key):
        entry = findings[fid]
        homes = ", ".join(fmt_link(h) for h in entry.homes) or "—"
        refby = sorted({
            p for p in mentions.get(fid, set())
            if p not in {FINDINGS, *entry.homes}
        })
        refby_s = ", ".join(fmt_link(p, Path(p).stem) for p in refby[:4])
        if len(refby) > 4:
            refby_s += f" (+{len(refby) - 4})"
        tests = ", ".join(f"`{t}`" for t in entry.tests) or "—"
        related = [qid for qid, vals in oq_related.items() if fid in vals]
        lines.append(
            f"| <a id=\"finding-{fid.lower()}\"></a>**{fid}** | {homes} | "
            f"{refby_s or '—'} | {tests} | {', '.join(related) or '—'} |"
        )

    lines += [
        "",
        "## Open-questions index",
        "",
        "| OQ | Title | Section | Related IDs |",
        "|---|---|---|---|",
    ]
    for qid in sorted(oq, key=natural_id_key):
        lines.append(
            f"| <a id=\"open-question-{qid.lower()}\"></a>**{qid}** | "
            f"{oq[qid]} | {oq_section.get(qid, '')} | "
            f"{', '.join(oq_related.get(qid, [])) or '—'} |"
        )

    lines += [
        "",
        "## Correction index",
        "",
        "| Correction | Canonical report(s) | Backlinked? |",
        "|---|---|---|",
    ]
    for cid in sorted(corrections, key=natural_id_key):
        homes = corrections[cid]["homes"]
        lines.append(
            f"| <a id=\"correction-{cid.lower()}\"></a>**{cid}** | "
            f"{', '.join(fmt_link(h) for h in homes) or '—'} | "
            f"{'yes' if homes and all(cid in docs.get(h, '') for h in homes) else 'no'} |"
        )

    lines += [
        "",
        "## Document registry",
        "",
        "Every tracked document under `docs/` with its owning suite(s) and gate tests.",
        "",
        "| Document | Suites | Gate tests |",
        "|---|---|---|",
    ]
    for path in sorted(p for p in docs if p.startswith("docs/")):
        sset = unique(owners.get(path, []))
        tests = unique([
            test
            for sname in sset
            for test in suites[sname].get("tests", [])  # type: ignore[union-attr]
        ])
        lines.append(
            f"| {fmt_link(path)} | {', '.join(sset) or '—'} | "
            f"{', '.join(f'`{t}`' for t in tests) or '—'} |"
        )

    lines += [
        "",
        "## Data artifact registry",
        "",
        "Suite ownership drives `tools/test` invalidation. Catalog gates document",
        "coverage performed outside that runner without creating false routing edges.",
        "",
        "| Artifact | Verification suites | Catalog gate(s) |",
        "|---|---|---|",
    ]
    for path in sorted(data_files):
        gates = unique([
            str(catalogs[name].get("gate", ""))
            for name in unique(catalog_owners.get(path, []))
            if catalogs[name].get("gate")
        ])
        lines.append(
            f"| `{path}` | {', '.join(unique(owners.get(path, []))) or '—'} | "
            f"{', '.join(f'`{gate}`' for gate in gates) or '—'} |"
        )

    lines += [
        "",
        "## Graph health",
        "",
        "All values below are hard zero invariants; there is no accepted debt baseline.",
        "",
    ]
    labels = {
        "finding_home_backlink_failures": "Finding canonical-home backlink failures",
        "correction_backlink_failures": "Correction canonical-home backlink failures",
        "findings_unmentioned": "Findings mentioned nowhere outside FINDINGS.md",
        "generated_artifact_inventory_gaps": "Tracked data/generated files absent from the inventory",
        "orphans": "Orphan docs",
        "broken_links": "Broken relative links",
        "unmapped_docs": "docs/ files without verification ownership",
        "unmapped_data": "data/ files without verification-suite or catalog ownership",
    }
    for key in labels:
        lines.append(f"- {labels[key]}: {metrics.get(key, 0)}")
    lines.append("")

    index_text = "\n".join(lines) + "\n"
    managed_texts[INDEX_KEY] = index_text

    if args.json:
        drift = sorted(
            path for path, expected in managed_texts.items()
            if not (REPO / path).exists()
            or (REPO / path).read_text(encoding="utf-8", errors="replace") != expected
        )
        print(json.dumps({
            "findings": len(findings),
            "corrections": len(corrections),
            "open_questions": len(oq),
            "docs": len(docs),
            "suites": len(suites),
            "managed_files": len(managed_texts),
            "drift": drift,
            "metrics": metrics,
            "errors": errors,
            "warnings": warnings,
        }, indent=2))
        return 0

    if args.check:
        drift = []
        for path, expected in managed_texts.items():
            actual = (
                (REPO / path).read_text(encoding="utf-8", errors="replace")
                if (REPO / path).exists() else ""
            )
            if actual != expected:
                drift.append(path)
        if drift:
            for path in sorted(drift):
                print(f"drift: {path}")
            return 1
        if errors:
            for error in errors:
                print(f"error: {error}")
            return 1
        print("clean")
        return 0

    for path, expected in managed_texts.items():
        target = REPO / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected, encoding="utf-8")
    print(
        f"wrote {len(managed_texts)} managed files: {len(findings)} findings, "
        f"{len(corrections)} corrections, {len(oq)} open questions; "
        f"errors={len(errors)} warnings={len(warnings)}"
    )
    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
