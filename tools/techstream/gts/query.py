"""Fast query surface over GTS+ evidence: status census, ECU table inventories, DID/DTC rows, cross-corpus search, writer routes, PE inspection."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pefile

from tools import REPO_ROOT
from tools.techstream.gts.cuw import _search_cuw_corpus
from tools.techstream.cuw_parameter import factory_routes_from_ini_root
from tools.techstream.gts.ddb import (
    _behavior_rows,
    _dtc_rows,
    _english_string_dbs,
    _english_strings,
    _fold_match,
    _monitor_rows,
    _normalize_did,
    _resolve_ecu,
)
from tools.techstream.parse_ddb import DDBParser, ECU_TABLE_CLASS_NAMES
from tools.techstream.pe_utils import binary_strings
from tools.techstream.pe_utils import exports as pe_exports
from tools.techstream.pe_utils import imports as pe_imports


def _route_rows(cuwplus_root: Path) -> list[dict[str, Any]]:
    ini_root = cuwplus_root / "Ini"
    if not ini_root.is_dir():
        return []
    shared, _ = factory_routes_from_ini_root(ini_root)
    return [
        {
            **row,
            "kind": "route",
            "row": row["row_index"],
            "contact_type": row["factory_identifier"],
        }
        for row in shared
    ]


def _search_ddbs(
    query: str,
    db_root: Path,
    *,
    ecu_filter: str | None,
    kinds: set[str],
    all_string_dbs: bool = False,
) -> list[dict[str, Any]]:
    parser = DDBParser()
    semantic_kinds = kinds.intersection({"did", "dtc", "behavior", "string"})
    strings = _english_strings(parser, db_root) if semantic_kinds else None
    results: list[dict[str, Any]] = []
    files = sorted(db_root.glob("*.ddb"), key=lambda p: p.name.casefold())
    if ecu_filter:
        files = [p for p in files if ecu_filter.casefold() in p.name.casefold()]
    for path in files:
        if path.name in {"M_English.ddb", "V_English.ddb", "U_English.ddb", "Toyota.ddb"} or re.match(r"^[MVU]_[A-Za-z]+\.ddb$", path.name):
            continue
        if "file" in kinds and _fold_match(query, path.name):
            results.append({"kind": "file", "source": str(path.relative_to(db_root))})
        if not kinds.intersection({"did", "dtc", "behavior"}):
            continue
        assert strings is not None
        try:
            db = parser.parse_ecu_db(path)
        except (ValueError, OSError):
            continue
        if "did" in kinds:
            for row in _monitor_rows(db, strings, path.name):
                if _fold_match(query, row.get("name"), f"0x{row['primary_did']:04X}", f"0x{row['alternate_did']:04X}"):
                    results.append(row)
        if "dtc" in kinds:
            for row in _dtc_rows(parser, db, strings, path.name):
                if _fold_match(query, row.get("code"), row.get("packed_dtc"), row.get("description"), row.get("failure")):
                    results.append(row)
        if "behavior" in kinds:
            for row in _behavior_rows(db, strings, path.name):
                if _fold_match(query, row.get("signature"), row.get("name"), row.get("comment")):
                    results.append(row)
    if "string" in kinds and not ecu_filter:
        assert strings is not None
        string_dbs = _english_string_dbs(parser, db_root, strings) if all_string_dbs else {"M_English.ddb": strings}
        for source, string_db in string_dbs.items():
            for offset, text in string_db.search(query, limit=500):
                results.append({"kind": "string", "source": source, "offset": offset, "text": text})
    return results


def _iter_pe_candidates(gts_root: Path, cuwplus_root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in (gts_root / "bin", cuwplus_root, cuwplus_root / "unpack"):
        if not root.is_dir():
            continue
        for pattern in ("*.dll", "*.exe", "*.dll._", "*.exe._"):
            for path in root.glob(pattern):
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield resolved


def _route_match(query: str, row: dict[str, Any]) -> bool:
    return _fold_match(
        query,
        row.get("contact_type"),
        row.get("parameter_file"),
        row.get("cid_getter"),
        row.get("prepare_writer"),
        row.get("flash_writer"),
        row.get("get_can_id_cid"),
        row.get("get_can_id_prepare"),
        row.get("get_can_id_flash"),
        row.get("version_contract"),
        row.get("prepare_retry"),
    )


def _resolve_pe(gts_root: Path, cuwplus_root: Path, query: str) -> Path:
    direct = Path(query)
    if direct.is_file():
        return direct.resolve()
    candidates = list(_iter_pe_candidates(gts_root, cuwplus_root))
    exact = [p for p in candidates if p.name.casefold() == query.casefold()]
    if len(exact) == 1:
        return exact[0]
    matches = [p for p in candidates if query.casefold() in p.name.casefold()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"no GTS+/CUWPlus PE matches {query!r}")
    raise SystemExit("ambiguous PE; matches:\n" + "\n".join(f"  {p}" for p in matches[:60]))


def status_payload(gts: Path, cuwplus: Path, corpus: Path, db: Path) -> dict[str, Any]:
    payload = {
        "gtsplus_root": str(gts),
        "ddb_root": str(db),
        "ddb_files": len(list(db.glob("*.ddb"))) if db.is_dir() else 0,
        "gtsplus_bin": str(gts / "bin"),
        "pe_files": len(list((gts / "bin").glob("*.dll"))) + len(list((gts / "bin").glob("*.exe"))) if (gts / "bin").is_dir() else 0,
        "cuwplus_root": str(cuwplus),
        "route_ini_files": len(list((cuwplus / "Ini").glob("*.ini"))) if (cuwplus / "Ini").is_dir() else 0,
        "cuw_corpus": str(corpus),
        "cuw_files": len(list(corpus.glob("*.cuw"))) if corpus.is_dir() else 0,
    }
    return payload


def ecu_payload(db_root: Path, ecu_query: str) -> dict[str, Any]:
    path = _resolve_ecu(db_root, ecu_query)
    parser = DDBParser()
    db = parser.parse_ecu_db(path)
    rows = [
        {
            "table": table_id,
            "class": ECU_TABLE_CLASS_NAMES.get(table_id, "unknown"),
            "records": section.header.record_count,
            "record_size": section.decoded_record_size,
        }
        for table_id, section in sorted(db.sections.items())
    ]
    payload = {"path": str(path), "sections": rows}
    return payload


def did_rows(db_root: Path, ecu_query: str, query: str | None = None) -> list[dict[str, Any]]:
    path = _resolve_ecu(db_root, ecu_query)
    parser = DDBParser()
    db = parser.parse_ecu_db(path)
    strings = _english_strings(parser, db_root)
    rows = _monitor_rows(db, strings, path.name)
    if query:
        did = _normalize_did(query)
        if did is not None:
            rows = [r for r in rows if did in {r["primary_did"], r["alternate_did"]}]
        else:
            rows = [r for r in rows if _fold_match(query, r.get("name"), r.get("monitor_key"), r.get("physical_data_key"))]
    return rows


def recorder_payload(schema: str, query: str | None = None) -> dict[str, Any]:
    """Inspect recovered PCS field definitions, independently of ECU Data List DIDs."""
    filenames = {
        "tss3": "pcs_data_viewer_tss3_managed_semantics.json",
        "adu": "pcs_data_viewer_adu_semantics.json",
    }
    source = Path("data/generated/gtsplus_2026") / filenames[schema]
    artifact = json.loads((REPO_ROOT / source).read_text())
    definitions = artifact["operation_ffd"]["detail_rows"] if schema == "tss3" else artifact["adu"]["rows"]
    did = _normalize_did(query) if query else None
    fields = []
    for row in definitions:
        record_id = _normalize_did(row["DataID"])
        if record_id is None:
            continue  # Viewer metadata entries are not recorder field definitions.
        if query:
            if did is not None:
                if record_id != did:
                    continue
            elif not _fold_match(query, row["DataName"]):
                continue
        fields.append(row)
    return {
        "namespace": "pcs-recorder",
        "schema": schema,
        "artifact_schema": artifact["schema"],
        "source": source.as_posix(),
        "sources": artifact["sources"],
        "fields": fields,
    }


def dtc_rows(db_root: Path, ecu_query: str, query: str | None = None) -> list[dict[str, Any]]:
    path = _resolve_ecu(db_root, ecu_query)
    parser = DDBParser()
    db = parser.parse_ecu_db(path)
    strings = _english_strings(parser, db_root)
    rows = _dtc_rows(parser, db, strings, path.name)
    if query:
        rows = [r for r in rows if _fold_match(query, r.get("code"), r.get("packed_dtc"), r.get("description"), r.get("failure"))]
    return rows


def pe_payload(path: Path, query: str | None, min_string: int, limit: int) -> dict[str, Any]:
    data = path.read_bytes()
    try:
        pe = pefile.PE(data=data, fast_load=False)
    except pefile.PEFormatError as exc:
        raise SystemExit(f"not a parseable PE: {path}: {exc}") from exc
    exports = pe_exports(pe)
    imports = pe_imports(pe)
    strings = binary_strings(data, min_string)
    if query:
        exports = [e for e in exports if _fold_match(query, e["name"])]
        imports = [i for i in imports if _fold_match(query, i["dll"], i["name"])]
        strings = [s for s in strings if _fold_match(query, s)]
    exports = exports[: limit]
    imports = imports[: limit]
    strings = strings[: limit]
    payload = {
        "path": str(path),
        "image_base": pe.OPTIONAL_HEADER.ImageBase,
        "machine": f"0x{pe.FILE_HEADER.Machine:04X}",
        "exports": exports,
        "imports": imports,
        "strings": strings,
    }
    return payload


def search_rows(query: str, gts: Path, cuwplus: Path, db_root: Path, corpus: Path, *, kinds: set[str], ecu_filter: str | None, all_string_dbs: bool) -> list[dict[str, Any]]:
    results = _search_ddbs(
        query,
        db_root,
        ecu_filter=ecu_filter,
        kinds=kinds,
        all_string_dbs=all_string_dbs,
    )
    if "file" in kinds:
        for path in _iter_pe_candidates(gts, cuwplus):
            if _fold_match(query, path.name):
                try:
                    rel = path.relative_to(REPO_ROOT)
                except ValueError:
                    rel = path
                results.append({"kind": "file", "source": str(rel)})
    if "route" in kinds:
        results.extend(row for row in _route_rows(cuwplus) if _route_match(query, row))
    if "cuw" in kinds:
        results.extend(_search_cuw_corpus(query, corpus))
    return results
