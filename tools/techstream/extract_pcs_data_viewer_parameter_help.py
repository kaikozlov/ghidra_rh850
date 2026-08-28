#!/usr/bin/env python3
"""Extract PCS Data Viewer FFD parameter descriptions from the shipped CHM help."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PCS_DIR = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics/PCS Data Viewer"
DICT_ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_dictionary.json"
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_parameter_help.json"


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).replace("\xa0", " ").split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_member(chm: Path, member: str, seven_zip: str) -> bytes:
    return subprocess.check_output([seven_zip, "x", "-so", str(chm), member])


def parse_ffd_help(chm: Path, seven_zip: str) -> list[dict[str, Any]]:
    raw = extract_member(chm, "FFD.htm", seven_zip)
    parser = TableParser()
    parser.feed(raw.decode("utf-8", errors="replace"))
    rows = parser.rows
    if not rows or rows[0][:3] != ["No.", "Parameter Name", "Description"]:
        raise ValueError(f"unexpected FFD help table header in {chm.name}: {rows[:1]}")
    out = []
    for row in rows[1:]:
        if len(row) < 3:
            continue
        out.append({"index": int(row[0]), "name": row[1], "description": row[2]})
    return out


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", text.lower())


def dictionary_name_index(payload: dict[str, Any]) -> dict[str, list[dict[str, str]]]:
    index: dict[str, list[dict[str, str]]] = {}
    for family, block in payload["dictionaries"]["families"].items():
        for entry in block["entries"]:
            name = entry.get("name_en")
            if not name:
                continue
            index.setdefault(norm(name), []).append(
                {"family": family, "key": entry["key"], "name": name}
            )
    return index


def build(seven_zip: str | None = None) -> dict[str, Any]:
    exe = seven_zip or shutil.which("7z") or shutil.which("7zz")
    if not exe:
        raise RuntimeError("7z/7zz is required to extract the shipped CHM help")

    en = PCS_DIR / "Help/ParameterHelp.chm"
    ja = PCS_DIR / "Help/ParameterHelp_JA.chm"
    en_rows = parse_ffd_help(en, exe)
    ja_rows = parse_ffd_help(ja, exe)
    if len(en_rows) != 28 or len(ja_rows) != 28:
        raise ValueError(f"FFD help row-count drift: EN={len(en_rows)} JA={len(ja_rows)}")

    dictionary = json.loads(DICT_ART.read_text(encoding="utf-8"))
    name_index = dictionary_name_index(dictionary)
    joins = []
    for row in en_rows:
        matches = name_index.get(norm(row["name"]), [])
        if matches:
            joins.append({"help_index": row["index"], "help_name": row["name"], "matches": matches})

    by_index = {row["index"]: row for row in en_rows}
    oracles = {
        "pcs_control_status": by_index[9],
        "deceleration_request": by_index[10],
        "target_object_number": by_index[11],
        "target_lateral_position": by_index[19],
        "steering_angle": by_index[28],
    }

    return {
        "schema": "gtsplus-pcs-data-viewer-parameter-help-v1",
        "title": "PCS Data Viewer FFD parameter help and TSS3 dictionary joins",
        "sources": {
            "english_chm": {"path": str(en.relative_to(REPO)), "size": en.stat().st_size, "sha256": sha256(en)},
            "japanese_chm": {"path": str(ja.relative_to(REPO)), "size": ja.stat().st_size, "sha256": sha256(ja)},
            "tss3_dictionary_artifact": {"path": str(DICT_ART.relative_to(REPO)), "sha256": sha256(DICT_ART)},
        },
        "english_ffd_parameters": en_rows,
        "japanese_help_ffd_parameters": ja_rows,
        "exact_normalized_dictionary_joins": joins,
        "exact_join_count": len(joins),
        "oracles": oracles,
        "interpretation": [
            "The CHM is an OEM-authored parameter-help surface shipped with PCS Data Viewer, independent of the resource-key display dictionary.",
            "The FFD help page contains 28 parameter names with plain-language descriptions and some enumerated control-state semantics.",
            "Exact normalized name joins tie a subset of help descriptions directly to recovered TSS3/resource keys; non-joined help rows are retained without guessed IDs.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--7z", dest="seven_zip", default=None)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    payload = build(args.seven_zip)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: params={len(payload['english_ffd_parameters'])} joins={payload['exact_join_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
