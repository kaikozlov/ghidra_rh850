"""CUW saved-session corpus: container validation, fast first-member descriptors, calibration/CID summaries, corpus search."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

from tools.techstream.cuw_attach import parse_attach_bytes
from tools.techstream.parse_cuw_container import first_member_payload
from tools.techstream.parse_cuw_container import parse as parse_cuw_container
from tools.techstream.parse_cuw_container import read_first_member


def _cuw_files(corpus: Path) -> list[Path]:
    return sorted(corpus.glob("*.cuw"), key=lambda p: p.name.casefold()) if corpus.is_dir() else []


def _resolve_cuw(corpus: Path, query: str) -> Path | None:
    direct = Path(query)
    if direct.is_file():
        return direct.resolve()
    exact = [p for p in _cuw_files(corpus) if p.name.casefold() == query.casefold() or p.stem.casefold() == query.casefold()]
    return exact[0] if len(exact) == 1 else None


def _cuw_descriptor(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    """Fully validate a CUW before returning its first attach descriptor."""
    raw = path.read_bytes()
    outer = parse_cuw_container(raw)
    if outer["errors"]:
        raise ValueError("; ".join(outer["errors"]))
    outer["validation"] = "full-container"
    payload = first_member_payload(raw, outer)
    descriptor = parse_attach_bytes(payload)
    return outer, descriptor


def _cuw_first_member_fast(path: Path) -> tuple[dict[str, Any], bytes]:
    return read_first_member(path)


def _cuw_descriptor_fast(path: Path) -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    """Read only the CUW header + first attach member for interactive lookup.

    Large format-0x67 CUWs can be hundreds of MiB while attach.att is only a
    few KiB. Discovery should not stream/hash the flash payload merely to learn
    vehicle, contact type, DiagID, or calibration IDs. Use ``--validate`` when
    the full container integrity gate is desired.
    """
    outer, payload = _cuw_first_member_fast(path)
    return outer, parse_attach_bytes(payload)


def _new_cids(descriptor: dict[str, dict[str, str]]) -> list[str]:
    values = []
    for section, fields in descriptor.items():
        if section.startswith(("Node", "CPU", "LogicalBlock")) and fields.get("NewCID"):
            values.append(fields["NewCID"])
    return sorted(set(values))


def _target_calibrations(descriptor: dict[str, dict[str, str]]) -> list[str]:
    values = []
    for section, fields in descriptor.items():
        if not section.startswith("LogicalBlock"):
            continue
        values.extend(value for key, value in fields.items() if key.endswith("_TargetCalibration") and value)
    return sorted(set(values))


def _node_summary(descriptor: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    rows = []
    for section, fields in descriptor.items():
        if not section.startswith("Node"):
            continue
        rows.append({
            "section": section,
            "diag_id": fields.get("DiagID", ""),
            "required_spec_repro_ver": fields.get("RequiredSpecReproVer", ""),
            "logical_blocks": fields.get("NumberOfLogicalBlock", ""),
        })
    return rows


def _search_cuw_corpus(query: str, corpus: Path) -> list[dict[str, Any]]:
    out = []
    needle = query.casefold()
    for path in _cuw_files(corpus):
        try:
            _, payload = _cuw_first_member_fast(path)
        except (ValueError, KeyError, struct.error):
            continue
        # Prefilter on the raw ANSI attach text. Parsing every descriptor is
        # disproportionately expensive compared with reading their few KiB.
        if needle not in path.name.casefold() and needle not in payload.decode("latin1").casefold():
            continue
        descriptor = parse_attach_bytes(payload)
        vehicle = descriptor.get("Vehicle", {})
        out.append({
            "kind": "cuw",
            "source": path.name,
            "vehicle": vehicle.get("VehicleName", ""),
            "contact_type": vehicle.get("ContactType", ""),
            "new_cids": ",".join(_new_cids(descriptor)),
        })
    return out
