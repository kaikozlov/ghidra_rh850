"""GTS+ ECU DDB helpers: DID/name matching, OEM string databases, ECU resolution, semantic row shaping."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from tools.techstream.ddb_semantics import behavior_rows as semantic_behavior_rows
from tools.techstream.ddb_semantics import dtc_rows as semantic_dtc_rows
from tools.techstream.ddb_semantics import ffd_rows as semantic_ffd_rows
from tools.techstream.ddb_semantics import monitor_rows as semantic_monitor_rows
from tools.techstream.ddb_semantics import rob_rows as semantic_rob_rows
from tools.techstream.ddb_strings import load_string_db
from tools.techstream.parse_ddb import DDBParser, StringDataBase


def _normalize_did(value: str) -> int | None:
    text = value.strip().lower()
    try:
        if text.startswith("0x"):
            return int(text, 16)
        if re.fullmatch(r"[0-9a-f]{4}", text):
            return int(text, 16)
    except ValueError:
        return None
    return None


def _fold_match(query: str, *values: Any) -> bool:
    needle = query.casefold()
    return any(value is not None and needle in str(value).casefold() for value in values)


def _english_strings(parser: DDBParser, db_root: Path):
    path = db_root / "M_English.ddb"
    if not path.is_file():
        raise SystemExit(f"missing GTS+ OEM string database: {path}")
    return load_string_db(parser, path)


def _english_string_dbs(parser: DDBParser, db_root: Path, m_strings: StringDataBase | None = None) -> dict[str, Any]:
    out = {}
    for name in ("M_English.ddb", "V_English.ddb", "U_English.ddb"):
        path = db_root / name
        if path.is_file():
            out[name] = m_strings if name == "M_English.ddb" and m_strings is not None else load_string_db(parser, path)
    if "M_English.ddb" not in out:
        raise SystemExit(f"missing GTS+ OEM string database: {db_root / 'M_English.ddb'}")
    return out


def _resolve_ecu(db_root: Path, query: str) -> Path:
    direct = Path(query)
    if direct.is_file():
        return direct.resolve()
    files = sorted(
        (p for p in db_root.glob("*.ddb") if p.name not in {"M_English.ddb", "V_English.ddb", "U_English.ddb", "Toyota.ddb"}),
        key=lambda p: p.name.casefold(),
    )
    exact = [p for p in files if p.name.casefold() == query.casefold() or p.stem.casefold() == query.casefold()]
    if len(exact) == 1:
        return exact[0]
    matches = [p for p in files if query.casefold() in p.name.casefold()]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise SystemExit(f"no GTS+ ECU database matches {query!r} under {db_root}")
    raise SystemExit("ambiguous ECU database; matches:\n" + "\n".join(f"  {p.name}" for p in matches[:40]))


def _without_raw(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{key: value for key, value in row.items() if key != "raw"} for row in rows]


def _monitor_rows(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    return _without_raw(
        semantic_monitor_rows(db, strings, source, deduplicate=True, include_signal_info=True)
    )


def _dtc_rows(parser: DDBParser, db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    return _without_raw(semantic_dtc_rows(parser, db, strings, source))


def _behavior_rows(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    return _without_raw(semantic_behavior_rows(db, strings, source))


def _rob_rows(db: Any, strings: Any, source: str) -> dict[str, Any]:
    payload = semantic_rob_rows(db, strings, source, include_signal_info=True)
    signals = _without_raw(payload["signals"])
    for row in signals:
        info = row.get("signal_info")
        if isinstance(info, dict) and isinstance(info.get("pattern_display"), dict):
            info["pattern_display"] = {str(key): value for key, value in info["pattern_display"].items()}
    return {
        **{key: value for key, value in payload.items() if key not in {"behavior_codes", "signals"}},
        "behavior_codes": _without_raw(payload["behavior_codes"]),
        "signals": signals,
    }


def _generic_ffd_rows(db: Any, strings: Any, source: str, resolve_variable: Any) -> dict[str, Any]:
    payload = semantic_ffd_rows(
        db, strings, source,
        resolve_variable=resolve_variable,
        include_signal_info=True,
    )
    signals = _without_raw(payload["signals"])
    for row in signals:
        info = row.get("signal_info")
        if isinstance(info, dict) and isinstance(info.get("pattern_display"), dict):
            info["pattern_display"] = {str(key): value for key, value in info["pattern_display"].items()}
    return {**{key: value for key, value in payload.items() if key != "signals"}, "signals": signals}
