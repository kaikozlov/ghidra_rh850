"""Exploit-interest scoring, stratification, and deterministic output."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import graph as G
from .model import (
    AUTH_BARRIERS,
    CURATED_ROOTS,
    DATAFLASH_HI,
    DATAFLASH_LO,
    FAMILIES,
    HAZARD_PATTERNS,
    LOCAL_RAM_HI,
    LOCAL_RAM_LO,
    SFR_LO,
    SA_GATED_INGRESS,
    SINK_ADDRESSES,
    XCP_WRITE_WINDOW,
)

# Address ranges whose reference is itself a control-relevant sink (beyond the
# exact SINK_ADDRESSES bytes).
SINK_RANGES: dict[str, tuple[int, int]] = {
    "xcp_daq_pointer_table": (0xFEBE4CF0, 0xFEBE4EAF),  # 112 pointers, 4B each
    "xcp_write_window": XCP_WRITE_WINDOW,
}
# Sinks that represent persistent/privilege transitions (family input).
PERSISTENT_SINKS = {
    "boot_sa_unlock_byte",
    "ba_persistent_marker",
    "handoff_phase_snapshot",
}

SYSTEM_HARD_RESET = 0x608AA  # named in canonical corpus
_NVM_NAME = re.compile(r"nvm|persistent|checkpoint|lifecycle", re.IGNORECASE)
_PROXIMITY_CAP = 10

WEIGHTS = {
    "ingress_prox": 0.20,
    "pre_sa": 0.10,
    "selector": 0.12,
    "indirect": 0.10,
    "computed_store": 0.14,
    "dynamic_copy": 0.08,
    "narrow_cast": 0.04,
    "mmio_flash": 0.10,
    "sink_ref": 0.06,
    "persistent": 0.06,
}


@dataclass
class Row:
    entry: int
    name: str
    body_size: int
    ingress_distance: int | None
    pre_sa_distance: int | None
    nearest_root: int | None
    root_label: str
    hazards: dict[str, int] = field(default_factory=dict)
    ram_write_refs: int = 0
    mmio_read_refs: int = 0
    mmio_write_refs: int = 0
    dataflash_refs: int = 0
    xcp_window_write_refs: int = 0
    xcp_window_read_refs: int = 0
    sink_names: set[str] = field(default_factory=set)
    persistent_transition: int = 0
    families: set[str] = field(default_factory=set)
    final_score: float = 0.0
    rank: int = 0


def _hexes(text: str) -> list[int]:
    return [int(m, 16) for m in re.findall(r"0x[0-9a-fA-F]+", text)]


def roots_from_tables(repo: Path) -> dict[int, str]:
    """Extract external-ingress roots from tracked evidence CSVs."""
    roots: dict[int, str] = {}

    def add(addr: int, label: str) -> None:
        if addr:
            roots.setdefault(addr, label)

    diag = repo / "data" / "application_diagnostic_map.csv"
    if diag.exists():
        with diag.open(newline="") as handle:
            for row in csv.DictReader(handle):
                sid = row.get("sid", "")
                for column in ("service_callback", "async_worker", "subfunctions"):
                    for addr in _hexes(row.get(column, "")):
                        add(addr, f"application UDS SID {sid} {column}")
    rx = repo / "data" / "application_rx_map.csv"
    if rx.exists():
        with rx.open(newline="") as handle:
            for row in csv.DictReader(handle):
                can_id = row.get("can_id", "?")
                for column in ("rx_callback", "unpacker", "first_consumer"):
                    for addr in _hexes(row.get(column, "")):
                        add(addr, f"CAN {can_id} Rx {column}")
    tables = repo / "data" / "recovered_callback_tables.csv"
    if tables.exists():
        with tables.open(newline="") as handle:
            for row in csv.DictReader(handle):
                role = row.get("structural_role", "")
                add(int(row["dispatcher_addr"], 16), f"callback-table dispatcher ({role})")
                add(int(row["target_addr"], 16), f"callback-table target ({role})")
    return roots


def collect_rows(repo: Path, functions: dict[int, G.Function]) -> list[Row]:
    curated = dict(CURATED_ROOTS)
    table_roots = roots_from_tables(repo)
    all_roots = {**table_roots, **curated}  # curated labels win
    distance, root_of = G.bfs_distance(functions, all_roots)
    # Pre-SA reachability: gated bootloader handlers leave the root set and
    # send-key implementations stop the traversal (frontier only).
    pre_sa_roots = {a: label for a, label in all_roots.items() if a not in SA_GATED_INGRESS}
    pre_sa_distance, _ = G.bfs_distance(functions, pre_sa_roots, barriers=AUTH_BARRIERS)

    hazard_re = {name: re.compile(pattern) for name, pattern in HAZARD_PATTERNS.items()}
    rows: list[Row] = []
    for entry in sorted(functions):
        fn = functions[entry]
        persistent_sink_refs = 0
        row = Row(
            entry=entry,
            name=fn.name,
            body_size=fn.body_size,
            ingress_distance=distance.get(entry),
            pre_sa_distance=pre_sa_distance.get(entry),
            nearest_root=root_of.get(entry),
            root_label=all_roots.get(root_of.get(entry, -1), ""),
            hazards={name: len(rx.findall(fn.decompiled_c)) for name, rx in hazard_re.items()},
        )
        for ref in fn.data_references:
            to = int(ref["to_addr"], 16)
            kind = ref["ref_type"]
            if to >= SFR_LO and not (DATAFLASH_LO <= to <= DATAFLASH_HI):
                if kind in ("WRITE", "READ_WRITE"):
                    row.mmio_write_refs += 1
                elif kind == "READ":
                    row.mmio_read_refs += 1
            elif DATAFLASH_LO <= to <= DATAFLASH_HI:
                row.dataflash_refs += 1
            if LOCAL_RAM_LO <= to <= LOCAL_RAM_HI and kind in ("WRITE", "READ_WRITE"):
                row.ram_write_refs += 1
            if XCP_WRITE_WINDOW[0] <= to <= XCP_WRITE_WINDOW[1]:
                if kind in ("WRITE", "READ_WRITE"):
                    row.xcp_window_write_refs += 1
                elif kind == "READ":
                    row.xcp_window_read_refs += 1
            for name, sink in SINK_ADDRESSES.items():
                if to == sink:
                    row.sink_names.add(name)
                    if name in PERSISTENT_SINKS and kind in ("WRITE", "READ_WRITE"):
                        persistent_sink_refs += 1
            for name, (lo, hi) in SINK_RANGES.items():
                if lo <= to <= hi:
                    row.sink_names.add(name)
        # Persistent/privilege transitions: sink writes, reset handoff, NvM callees.
        persistent = persistent_sink_refs
        if SYSTEM_HARD_RESET in fn.calls:
            persistent += 1
        if any(_NVM_NAME.search(functions.get(t, G.Function(t, "", 0, False, None, "", "", [])).name) for t in fn.calls):
            persistent += 1
        row.persistent_transition = persistent

        d = row.ingress_distance
        p = row.pre_sa_distance
        if d is not None and d <= 1:
            row.families.add("ingress_direct")
        if d is not None and d <= 8 and (row.hazards["selector_switch"] or row.hazards["selector_mask"]):
            row.families.add("selector_dispatch")
        if row.hazards["computed_store"] or row.hazards["address_of_store"]:
            row.families.add("computed_store")
        if fn.indirect_call_count:
            row.families.add("indirect_call")
        if row.hazards["loop"] and row.hazards["copy_call"]:
            row.families.add("dynamic_copy")
        if row.mmio_write_refs or row.dataflash_refs:
            row.families.add("mmio_flash_write")
        if row.persistent_transition:
            row.families.add("persistent_transition")
        if p is not None and (row.ram_write_refs or row.mmio_write_refs or row.hazards["computed_store"]):
            row.families.add("pre_sa_write")
        rows.append(row)
    return rows, all_roots, distance, pre_sa_distance  # type: ignore[return-value]


def score(rows: list[Row], functions: dict[int, G.Function]) -> None:
    def proximity(distances: list[float]) -> list[float]:
        prox = [1.0 / (1.0 + d) if d <= _PROXIMITY_CAP else 0.0 for d in distances]
        return prox

    ingress_present = [r.ingress_distance if r.ingress_distance is not None else math.inf for r in rows]
    pre_sa_present = [r.pre_sa_distance if r.pre_sa_distance is not None else math.inf for r in rows]
    raw = {
        "ingress_prox": proximity(ingress_present),
        "pre_sa": proximity(pre_sa_present),
        "selector": [
            float(r.hazards["selector_switch"] + r.hazards["selector_mask"] + r.hazards["param_index"])
            for r in rows
        ],
        "indirect": [float(functions[r.entry].indirect_call_count) for r in rows],
        "computed_store": [
            float(r.hazards["computed_store"] + r.hazards["address_of_store"]) for r in rows
        ],
        "dynamic_copy": [
            float(r.hazards["loop"] * r.hazards["copy_call"] + r.hazards["copy_call"]) for r in rows
        ],
        "narrow_cast": [float(r.hazards["narrow_cast"]) for r in rows],
        "mmio_flash": [float(r.mmio_write_refs + r.dataflash_refs) for r in rows],
        "sink_ref": [float(len(r.sink_names)) for r in rows],
        "persistent": [float(r.persistent_transition) for r in rows],
    }
    normalized: dict[str, list[float]] = {}
    for key, values in raw.items():
        transformed = [math.log1p(v) for v in values]
        peak = max(transformed, default=0.0)
        normalized[key] = [v / peak if peak > 0 else 0.0 for v in transformed]
    for index, row in enumerate(rows):
        row.final_score = round(
            sum(WEIGHTS[key] * normalized[key][index] for key in WEIGHTS), 6
        )
    rows.sort(key=lambda r: (-r.final_score, r.entry))
    for index, row in enumerate(rows, start=1):
        row.rank = index


CSV_HEADER = [
    "rank", "entry_addr", "name", "body_size", "ingress_distance",
    "pre_sa_distance", "nearest_root", "root_label",
    "selector_switch", "selector_mask", "param_index", "narrow_cast",
    "indirect_call", "computed_store", "address_of_store", "loop", "copy_call",
    "ram_write_refs", "mmio_read_refs", "mmio_write_refs", "dataflash_refs",
    "xcp_window_write_refs", "xcp_window_read_refs", "sink_names",
    "persistent_transition", "families", "final_score",
]


def write_csv(rows: list[Row], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(CSV_HEADER)
        for row in rows:
            writer.writerow([
                row.rank, f"0x{row.entry:08x}", row.name, row.body_size,
                "" if row.ingress_distance is None else row.ingress_distance,
                "" if row.pre_sa_distance is None else row.pre_sa_distance,
                "" if row.nearest_root is None else f"0x{row.nearest_root:08x}",
                row.root_label,
                row.hazards["selector_switch"], row.hazards["selector_mask"],
                row.hazards["param_index"], row.hazards["narrow_cast"],
                functions_indirect(row), row.hazards["computed_store"],
                row.hazards["address_of_store"], row.hazards["loop"],
                row.hazards["copy_call"],
                row.ram_write_refs, row.mmio_read_refs, row.mmio_write_refs,
                row.dataflash_refs, row.xcp_window_write_refs,
                row.xcp_window_read_refs,
                ";".join(sorted(row.sink_names)), row.persistent_transition,
                ";".join(f for f in FAMILIES if f in row.families),
                f"{row.final_score:.6f}",
            ])


def functions_indirect(row: Row) -> int:
    return row.hazards.get("indirect_call", 0)


def write_cohorts(
    rows: list[Row],
    functions: dict[int, G.Function],
    all_roots: dict[int, str],
    inputs: dict[str, str],
    path: Path,
    per_family: int = 15,
) -> None:
    payload: dict = {
        "schema": "exploit-interest-cohorts/1",
        "inputs": inputs,
        "weights": WEIGHTS,
        "proximity_cap": _PROXIMITY_CAP,
        "auth_barriers": {f"0x{k:08x}": v for k, v in sorted(AUTH_BARRIERS.items())},
        "root_count": len(all_roots),
        "families": {},
    }
    for family in FAMILIES:
        members = [r for r in rows if family in r.families]
        members.sort(key=lambda r: (-r.final_score, r.entry))
        payload["families"][family] = [
            {
                "entry": f"0x{r.entry:08x}",
                "name": r.name,
                "score": r.final_score,
                "rank": r.rank,
                "ingress_distance": r.ingress_distance,
                "pre_sa_distance": r.pre_sa_distance,
                "nearest_root": "" if r.nearest_root is None else f"0x{r.nearest_root:08x}",
                "root_label": r.root_label,
                "body_size": r.body_size,
            }
            for r in members[:per_family]
        ]
        payload["families"][family + "_total"] = len(members)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
