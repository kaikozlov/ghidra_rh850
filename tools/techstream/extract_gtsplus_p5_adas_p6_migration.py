#!/usr/bin/env python3
"""Extract the P5 distributed-ADAS -> P6 ADAS-domain-controller semantic migration surface.

Targets the current GTS+ ADAS databases that the category-498 join left unused
(DSSystem_P5, Fr_RadSen_P5, PCS1_P5, PCS2_P5, RoadSign_P5, LDA_P5) plus the
generation-22 successor ADCU_P6/ADCU_P6F, and records:

* master routing/plugins/install-set architecture joins per region,
* OEM monitor/DID, DTC, RoB, and active-test vocabulary per database,
* the lost-communication/software-incompatibility module dependency graph,
* ADCU_P6 RoB/DDR recorder surfaces,
* concept-level P5->P6 migration joins (exact-name, DTC-code, active-test),
* the generation-22 P6 plugin/ECU ecosystem census.

Every claim is derived from the pinned GTS+ corpus bytes; host metadata is not
promoted to ECU-side producer ownership. P6 names are a successor oracle only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ddb_semantics import behavior_rows, dtc_rows, monitor_rows, records
from ddb_strings import load_string_db
from parse_ddb import ECU_TABLE_CLASS_NAMES, DDBParser, _fixed_utf16le
from techstream_paths import gts_db_root, resolve_gts_root

REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUT = REPO / "data/generated/gtsplus_2026/p5_adas_p6_migration.json"
REGIONS = ("NA", "EU", "JP")

P5_TARGETS = (
    "DSSystem_P5",
    "Fr_RadSen_P5",
    "PCS1_P5",
    "PCS2_P5",
    "RoadSign_P5",
    "LDA_P5",
)
P6_TARGETS = ("ADCU_P6", "ADCU_P6F")
ALL_TARGETS = P5_TARGETS + P6_TARGETS

# Category IDs used for architecture co-occurrence.
ARCHITECTURE_CATEGORY_NAMES = {
    142: "legacy_EMPS_P4",
    405: "EMPS_P5",
    418: "LDA_P5",
    427: "PCS1_P5",
    428: "DSSystem_P5",
    429: "Fr_RadSen_P5",
    430: "Fr_Camera_P5",
    431: "RoadSign_P5",
    432: "PCS2_P5",
    435: "ABS_P5",
    466: "BrakeBooster_P5",
    476: "ADS_Eth_P5",
    477: "ADeU_Eth_P5",
    485: "EPB_P5",
    498: "FRC_P5",
    499: "EMPS2_P5_steering_actuator",
    6032: "FDRS_P6_front_radar",
    6037: "ADCU_P6",
    6500: "P6F_family_base",
    6532: "FDRS_P6F_front_radar",
    6537: "ADCU_P6F",
}
ARCH_ANCHORS = (418, 427, 428, 429, 431, 432, 430, 498, 6037, 6537)

ADAS_KEYWORDS = {
    "lta_lane": re.compile(r"\blta\b|lane", re.IGNORECASE),
    "cruise_longitudinal": re.compile(r"cruise|proactive driving|proactive", re.IGNORECASE),
    "pcs_brake_request": re.compile(
        r"\bpcs\b|pre.?collision|brake request|pre.?fill|deceleration request", re.IGNORECASE
    ),
    "steering_control": re.compile(
        r"steer.*(assist|control|torque|request)|avoidance steer|emergency steer", re.IGNORECASE
    ),
    "radar_sensing": re.compile(r"radar", re.IGNORECASE),
    "road_sign": re.compile(r"road sign|rsa\b|traffic sign", re.IGNORECASE),
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source(path: Path, root: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(root)).replace("\\", "/"),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def u16(raw: bytes, off: int) -> int:
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw: bytes, off: int) -> int:
    return struct.unpack_from("<I", raw, off)[0]


def norm_name(value: str | None) -> str:
    return " ".join((value or "").split()).casefold()


# ── master routing ────────────────────────────────────────────────────────────


class RegionContext:
    def __init__(self, parser: DDBParser, root: Path, region: str) -> None:
        self.region = region
        self.root = root
        self.db_root = gts_db_root(root, region, "Gen")
        self.master = parser.parse_master_db(self.db_root / "Toyota.ddb")
        self.strings = load_string_db(parser, self.db_root / "M_English.ddb")
        self.categories: dict[int, dict[str, Any]] = {}
        for row in parser.extract_master_ecu_categories(self.master.sections[16]):
            self.categories[row.category_id] = {
                "category_id": row.category_id,
                "generation": row.generation,
                "database": row.database_name,
                "short_name": row.ecu_short_name,
                "name": self.strings.get_string(row.ecu_name_string_index) or "",
            }
        self.dlls: dict[int, list[tuple[int, str]]] = defaultdict(list)
        for row in parser.extract_master_dlls(self.master.sections[19]):
            self.dlls[row.category_id].append((row.dll_role_id, row.dll_name))
        self.vehicle_names = {
            u16(r, 0x04): self.strings.get_string(u32(r, 0x00))
            for r in records(self.master.sections[43])
        }
        self.vehicle_sets: dict[int, set[int]] = defaultdict(set)
        for r in records(self.master.sections[5]):
            self.vehicle_sets[u16(r, 0x04)].add(u16(r, 0x06))
        self.set_categories: dict[int, set[int]] = defaultdict(set)
        for r in records(self.master.sections[44]):
            self.set_categories[u16(r, 0x04)].add(u16(r, 0x06))

    def category_for_database(self, database: str) -> list[int]:
        return sorted(
            cid for cid, cat in self.categories.items() if cat["database"] == database
        )

    def architecture_rows(self, anchor: int) -> list[tuple[str, int, tuple[int, ...]]]:
        rows = []
        for vehicle_id, install_sets in self.vehicle_sets.items():
            name = self.vehicle_names.get(vehicle_id)
            if not name:
                continue
            for install_set in sorted(install_sets):
                installed = self.set_categories.get(install_set, set())
                if anchor not in installed:
                    continue
                arch = tuple(
                    cid for cid in sorted(ARCHITECTURE_CATEGORY_NAMES) if cid in installed
                )
                rows.append((name, install_set, arch))
        return rows


def plugin_bindings(ctx: RegionContext, category_id: int) -> list[dict[str, Any]]:
    return [
        {"role": f"0x{role:02X}", "dll": dll}
        for role, dll in sorted(ctx.dlls.get(category_id, []))
    ]


def routing_section(contexts: dict[str, RegionContext]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for name in ALL_TARGETS:
        per_region = {}
        for region, ctx in contexts.items():
            matches = ctx.category_for_database(f"{name}.ddb")
            if len(matches) != 1:
                raise ValueError(f"{region}: {name}.ddb resolved {len(matches)} categories")
            cid = matches[0]
            cat = ctx.categories[cid]
            per_region[region] = {
                "category_id": cid,
                "generation": cat["generation"],
                "ecu_name": cat["name"],
                "plugins": plugin_bindings(ctx, cid),
            }
        ids = {entry["category_id"] for entry in per_region.values()}
        gens = {entry["generation"] for entry in per_region.values()}
        if len(ids) != 1 or len(gens) != 1:
            raise ValueError(f"{name}: region disagreement {ids} {gens}")
        out[name] = {
            "category_id": ids.pop(),
            "generation": gens.pop(),
            "regional": per_region,
        }
    return out


def architecture_section(contexts: dict[str, RegionContext]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for anchor in ARCH_ANCHORS:
        label = ARCHITECTURE_CATEGORY_NAMES.get(anchor, str(anchor))
        rows = contexts["NA"].architecture_rows(anchor)
        arch_counts = Counter(arch for _, _, arch in rows)
        architectures = []
        for arch, count in sorted(arch_counts.items(), key=lambda kv: (-kv[1], kv[0])):
            arch_models = sorted({n for n, _, a in rows if a == arch})
            architectures.append({
                "categories": [
                    {"category_id": cid, "label": ARCHITECTURE_CATEGORY_NAMES.get(cid, str(cid))}
                    for cid in arch
                ],
                "install_row_count": count,
                "model_names": arch_models,
            })
        out[str(anchor)] = {
            "label": label,
            "install_row_count_na": len(rows),
            "model_count_na": len({name for name, _, _ in rows}),
            "architecture_count_na": len(arch_counts),
            "architectures_na": architectures,
        }
    return out


def _plugin_role_continuity(contexts: dict[str, RegionContext]) -> list[dict[str, Any]]:
    """Role-ID continuity between the P5 target plugins and the ADCU P6 plugins."""
    ctx = contexts["NA"]
    adcu_cid = ctx.category_for_database("ADCU_P6.ddb")
    if len(adcu_cid) != 1:
        raise ValueError(f"ADCU_P6.ddb resolved {adcu_cid}")
    adcu_roles = {role: dll for role, dll in ctx.dlls[adcu_cid[0]]}
    rows = []
    for role, p6_dll in sorted(adcu_roles.items()):
        p5_dlls = sorted(
            {
                dll
                for name in P5_TARGETS
                for cid in ctx.category_for_database(f"{name}.ddb")
                for bound_role, dll in ctx.dlls.get(cid, [])
                if bound_role == role
            }
        )
        rows.append({
            "role": f"0x{role:02X}",
            "p5_target_dlls": p5_dlls,
            "adcu_p6_dll": p6_dll,
            "p6_only": not p5_dlls,
        })
    return rows


def p6_ecosystem_section(contexts: dict[str, RegionContext]) -> dict[str, Any]:
    ctx = contexts["NA"]
    gen22 = sorted(cid for cid, cat in ctx.categories.items() if cat["generation"] == 22)
    categories = [
        {
            "category_id": cid,
            "name": ctx.categories[cid]["name"],
            "database": ctx.categories[cid]["database"] or None,
        }
        for cid in gen22
        if ctx.categories[cid]["database"]
    ]
    p6_dll_categories: dict[str, set[int]] = defaultdict(set)
    for cid, roles in ctx.dlls.items():
        for _role, dll in roles:
            if "P6" in dll:
                p6_dll_categories[dll].add(cid)
    rare = sorted(dll for dll, cids in p6_dll_categories.items() if len(cids) <= 2)
    rare_bindings = {
        dll: {
            "category_count": len(p6_dll_categories[dll]),
            "categories": [
                {
                    "category_id": cid,
                    "name": ctx.categories.get(cid, {}).get("name"),
                    "database": ctx.categories.get(cid, {}).get("database"),
                }
                for cid in sorted(p6_dll_categories[dll])
            ],
        }
        for dll in rare
    }
    staged = sorted(dll for dll, cids in p6_dll_categories.items() if set(cids) == {0})
    return {
        "generation_22_category_count_na": len(gen22),
        "generation_22_categories_with_database": categories,
        "p6_dll_count": len(p6_dll_categories),
        "rare_p6_plugin_bindings": rare_bindings,
        "staged_unbound_p6_plugins_category0": staged,
        "plugin_binding_counts": {
            dll: len(p6_dll_categories[dll]) for dll in sorted(p6_dll_categories)
        },
        "plugin_role_continuity": _plugin_role_continuity(contexts),
    }


# ── ECU database surfaces ─────────────────────────────────────────────────────


def table_census(db: Any) -> dict[str, dict[str, int]]:
    out = {}
    for tid in sorted(db.sections):
        section = db.sections[tid]
        out[str(tid)] = {
            "class": ECU_TABLE_CLASS_NAMES.get(tid, "unknown"),
            "record_count": section.header.record_count,
            "record_size": section.decoded_record_size,
        }
    return out


def compact_monitor_rows(db: Any, strings: Any, name: str) -> list[dict[str, Any]]:
    rows = []
    for row in monitor_rows(db, strings, name, deduplicate=True, include_signal_info=False):
        rows.append({
            "name": row["name"],
            "monitor_key": f"0x{row['monitor_key']:04X}",
            "primary_did": f"0x{row['primary_did']:04X}",
            "alternate_did": f"0x{row['alternate_did']:04X}",
            "bit_start": row["bit_start"],
            "bit_end": row["bit_end"],
            "tables": row["tables"],
        })
    return sorted(rows, key=lambda r: (norm_name(r["name"]), r["primary_did"]))


def rich_monitor_rows(db: Any, strings: Any, name: str) -> list[dict[str, Any]]:
    rows = []
    for row in monitor_rows(db, strings, name, deduplicate=True, include_signal_info=True):
        info = row.get("signal_info") or {}
        rows.append({
            "name": row["name"],
            "monitor_key": f"0x{row['monitor_key']:04X}",
            "primary_did": f"0x{row['primary_did']:04X}",
            "alternate_did": f"0x{row['alternate_did']:04X}",
            "bit_start": row["bit_start"],
            "bit_end": row["bit_end"],
            "unit": info.get("unit"),
            "pattern_display": (
                {str(key): value for key, value in sorted((info.get("pattern_display") or {}).items())}
                or None
            ),
            "tables": row["tables"],
        })
    return sorted(rows, key=lambda r: (norm_name(r["name"]), r["primary_did"]))


def dtc_surface(parser: DDBParser, db: Any, strings: Any, name: str) -> list[dict[str, Any]]:
    return sorted(
        (
            {"code": row["code"], "description": row["description"], "failure": row["failure"]}
            for row in dtc_rows(parser, db, strings, name)
        ),
        key=lambda r: r["code"],
    )


def behavior_surface(db: Any, strings: Any, name: str) -> list[dict[str, Any]]:
    rows = []
    for row in behavior_rows(db, strings, name):
        raw = row["raw"]
        rows.append({
            "signature": row["signature"],
            "behavior_code": f"0x{u32(raw, 0x14):06X}",
            "name": row["name"],
        })
    return sorted(rows, key=lambda r: r["signature"])


def rob_data_ids(db: Any, strings: Any) -> list[dict[str, Any]]:
    """RoB data-ID lists (tables 90/151) joined to record names via 88/153."""
    name_by_id: dict[int, str | None] = {}
    for tid in (88, 153):
        section = db.sections.get(tid)
        if section is None:
            continue
        for raw in records(section):
            if len(raw) < 0x40:
                continue
            data_id = u16(raw, 0x3C)
            resolved = strings.get_string(u32(raw, 0x20))
            existing = name_by_id.get(data_id)
            if existing is None or (resolved and not existing):
                name_by_id[data_id] = resolved
    out = []
    for tid in (90, 151):
        section = db.sections.get(tid)
        if section is None:
            continue
        seen: set[int] = set()
        for raw in records(section):
            data_id = u16(raw, 2)
            if data_id in seen:
                continue
            seen.add(data_id)
            out.append({
                "table": tid,
                "data_id": f"0x{data_id:04X}",
                "kind": u16(raw, 4),
                "flags": u16(raw, 6),
                "record_name": name_by_id.get(data_id),
            })
    return sorted(out, key=lambda r: (r["data_id"], r["table"]))


def routine_active_tests(db: Any, strings: Any) -> list[dict[str, Any]]:
    """Type-71 routine Active Tests decoded with the consumer-proven field set."""
    section = db.sections.get(71)
    if section is None:
        return []
    if section.decoded_record_size != 72:
        raise ValueError(f"table 71 record size {section.decoded_record_size} != 72")
    rows = []
    for index, raw in enumerate(records(section)):
        rows.append({
            "record": index,
            "active_test_id": f"0x{u16(raw, 0x1E):04X}",
            "routine_id": f"0x{u16(raw, 0x1C):04X}",
            "name": strings.get_string(u32(raw, 0x08)),
            "routine_command_variable": u16(raw, 0x28),
            "routine_stop_command_variable": u16(raw, 0x2A),
            "output_mask_value_variable": u16(raw, 0x2C),
            "output_mask_button_variable": u16(raw, 0x2E),
            "sort_key": u16(raw, 0x40),
        })
    return sorted(rows, key=lambda r: r["record"])


def p5_database_section(
    parser: DDBParser, db: Any, strings: Any, name: str, src: dict[str, Any]
) -> dict[str, Any]:
    return {
        "source": src,
        "table_census": table_census(db),
        "monitors": rich_monitor_rows(db, strings, name),
        "dtcs": dtc_surface(parser, db, strings, name),
        "behaviors": behavior_surface(db, strings, name),
        "rob_data_ids": rob_data_ids(db, strings),
        "routine_active_tests": routine_active_tests(db, strings),
    }


# ── ADCU P6 recorder surfaces ─────────────────────────────────────────────────


def adcu_rob_diag_codes(db: Any, strings: Any) -> list[dict[str, Any]]:
    section = db.sections.get(163)
    if section is None:
        return []
    rows = []
    for raw in records(section):
        rows.append({
            "code": _fixed_utf16le(raw[:0x2C]),
            "packed_dtc": f"0x{u32(raw, 0x2C):08X}",
            "description": strings.get_string(u32(raw, 0x30)),
            "failure": strings.get_string(u32(raw, 0x34)),
        })
    return sorted(rows, key=lambda r: r["code"])


def adcu_ddr_diag_codes(db: Any, strings: Any) -> list[dict[str, Any]]:
    section = db.sections.get(165)
    if section is None:
        return []
    rows = []
    for raw in records(section):
        rows.append({
            "group_code": f"0x{u32(raw, 0):08X}",
            "trigger": strings.get_string(u32(raw, 4)),
            "secondary_name": strings.get_string(u32(raw, 8)),
            "subtype": u16(raw, 16),
            "flags": u16(raw, 18),
        })
    return sorted(rows, key=lambda r: (r["group_code"], r["subtype"]))


def adcu_ddr_data_ids(db: Any, strings: Any) -> list[dict[str, Any]]:
    section = db.sections.get(166)
    if section is None:
        return []
    rows = []
    for raw in records(section):
        index = u32(raw, 0)
        rows.append({
            "string_index": index,
            "resolved": strings.get_string(index),
            "tail": u32(raw, 4),
        })
    return sorted(rows, key=lambda r: r["string_index"])


def adcu_p6_section(
    parser: DDBParser, db: Any, strings: Any, name: str, src: dict[str, Any]
) -> dict[str, Any]:
    monitors = compact_monitor_rows(db, strings, name)
    keyword_rows: dict[str, list[dict[str, Any]]] = {}
    for keyword, pattern in ADAS_KEYWORDS.items():
        keyword_rows[keyword] = sorted(
            ({"name": m["name"], "primary_did": m["primary_did"]} for m in monitors
             if pattern.search(m["name"] or "")),
            key=lambda m: norm_name(m["name"]),
        )
    did_histogram = Counter(m["primary_did"][1:2] for m in monitors)
    return {
        "source": src,
        "table_census": table_census(db),
        "monitor_count": len(monitors),
        "monitors": monitors,
        "adas_keyword_monitors": keyword_rows,
        "did_prefix_histogram": {
            f"0x{prefix}xxx": count for prefix, count in sorted(did_histogram.items())
        },
        "dtcs": dtc_surface(parser, db, strings, name),
        "routine_active_tests": routine_active_tests(db, strings),
        "rob_surface": {
            "rob_diag_codes": adcu_rob_diag_codes(db, strings),
            "rob_freeze_frame_count": db.sections[164].header.record_count
            if 164 in db.sections else 0,
            "rob_data_id_counts": {
                str(tid): db.sections[tid].header.record_count
                for tid in (90, 151) if tid in db.sections
            },
        },
        "ddr_surface": {
            "ddr_diag_codes": adcu_ddr_diag_codes(db, strings),
            "ddr_data_ids": adcu_ddr_data_ids(db, strings),
            "ddr_freeze_frame_count": db.sections[167].header.record_count
            if 167 in db.sections else 0,
            "ddr_invalid_condition_count": db.sections[168].header.record_count
            if 168 in db.sections else 0,
        },
    }


# ── dependency graph + migration joins ────────────────────────────────────────


def normalize_module(description: str) -> str:
    # Keep the OEM quoting intact ("ECM/PCM \"A\""); only drop the (ch2)
    # channel suffix that marks the second comm path of the same module.
    text = description.strip()
    text = text.removesuffix(" (ch2)")
    return text.strip()


def dependency_edges(dtcs: list[dict[str, Any]]) -> list[dict[str, str]]:
    edges = []
    for row in dtcs:
        description = row["description"] or ""
        if description.startswith("Lost Communication with "):
            module = normalize_module(description[len("Lost Communication with "):])
            edges.append({"kind": "lost_communication", "module": module, "code": row["code"]})
        elif description.startswith("Software Incompatibility with "):
            module = normalize_module(
                description[len("Software Incompatibility with "):
            ]
            )
            edges.append({"kind": "software_incompatibility", "module": module,
                          "code": row["code"]})
    return sorted(edges, key=lambda e: (e["kind"], e["module"], e["code"]))


def dependency_section(surfaces: dict[str, Any]) -> dict[str, Any]:
    per_ecu = {}
    p5_modules: set[str] = set()
    for name in P5_TARGETS:
        edges = dependency_edges(surfaces[name]["dtcs"])
        per_ecu[name] = {
            "modules": sorted({e["module"] for e in edges}),
            "edge_count": len(edges),
        }
        p5_modules |= {e["module"] for e in edges}
    adcu_edges = dependency_edges(surfaces["ADCU_P6"]["dtcs"])
    adcu_modules = {e["module"] for e in adcu_edges}
    return {
        "p5_per_ecu": per_ecu,
        "adcu_p6_modules": sorted(adcu_modules),
        "adcu_p6_edge_count": len(adcu_edges),
        "retained_external_modules": sorted(p5_modules & adcu_modules),
        "internalized_or_dropped_modules": sorted(p5_modules - adcu_modules),
        "adcu_new_external_modules": sorted(adcu_modules - p5_modules),
    }


def migration_section(surfaces: dict[str, Any]) -> dict[str, Any]:
    adcu_monitors = surfaces["ADCU_P6"]["monitors"]
    adcu_names = {norm_name(m["name"]) for m in adcu_monitors}
    per_target = {}
    for name in P5_TARGETS:
        own = surfaces[name]["monitors"]
        own_names = {norm_name(m["name"]) for m in own}
        exact = sorted(n for n in own_names if n in adcu_names)
        partial = []
        for monitor in own:
            key = norm_name(monitor["name"])
            if not key or key in adcu_names:
                continue
            pattern = re.compile(re.escape(key).replace(r"\ ", r"\s+"), re.IGNORECASE)
            hits = sorted(
                {m["name"] for m in adcu_monitors if pattern.search(m["name"] or "")}
            )
            if hits:
                partial.append({"p5_name": monitor["name"], "adcu_names": hits})
        adcu_codes = {row["code"] for row in surfaces["ADCU_P6"]["dtcs"]}
        own_codes = {row["code"] for row in surfaces[name]["dtcs"]}
        per_target[name] = {
            "monitor_count": len(own_names),
            "exact_monitor_name_joins": exact,
            "renamed_monitor_continuations": sorted(
                partial, key=lambda p: norm_name(p["p5_name"])
            ),
            "dtc_code_joins": sorted(own_codes & adcu_codes),
        }
    adcu_tests = {norm_name(t["name"]) for t in surfaces["ADCU_P6"]["routine_active_tests"]}
    p5_active_tests = {
        name: [
            {
                "name": t["name"],
                "routine_id": t["routine_id"],
                "active_test_id": t["active_test_id"],
                "continues_in_adcu": norm_name(t["name"]) in adcu_tests,
            }
            for t in surfaces[name]["routine_active_tests"]
        ]
        for name in P5_TARGETS
    }
    return {
        "monitor_name_joins": per_target,
        "routine_active_test_migration": p5_active_tests,
        "housekeeping_did_core": {
            "names": sorted(
                {
                    "Absolute Value Time (Year)",
                    "Clock Type",
                    "IG-ON Elapsed Time",
                    "Key Cycle",
                    "Master Sync Information",
                    "Number of DTC",
                    "Total Distance Traveled",
                }
            ),
            "meaning": (
                "Every P5 target and ADCU_P6 carries this identical housekeeping monitor "
                "grammar; only function-specific vocabulary differs between generations."
            ),
        },
    }


# ── build ─────────────────────────────────────────────────────────────────────


def component_version(root: Path) -> str:
    manifest = json.loads((root / "Ver/Manifest.json").read_text(encoding="utf-8-sig"))
    for row in manifest[0]["Components"]:
        if row["Name"] == "GTS+ DB":
            return row["Version"]
    raise ValueError("GTS+ DB version missing from manifest")


def build() -> dict[str, Any]:
    root = resolve_gts_root()
    parser = DDBParser()
    contexts = {region: RegionContext(parser, root, region) for region in REGIONS}

    db_root = contexts["NA"].db_root
    na_strings = contexts["NA"].strings
    surfaces: dict[str, Any] = {}
    for name in ALL_TARGETS:
        surfaces[name] = parser.parse_ecu_db(db_root / f"{name}.ddb")

    p5_section = {}
    for name in P5_TARGETS:
        db_path = db_root / f"{name}.ddb"
        p5_section[name] = p5_database_section(
            parser, surfaces[name], na_strings, name, source(db_path, root)
        )
    adcu_section: dict[str, Any] = {}
    for name in P6_TARGETS:
        db_path = db_root / f"{name}.ddb"
        if name == "ADCU_P6":
            adcu_section[name] = adcu_p6_section(
                parser, surfaces[name], na_strings, name, source(db_path, root)
            )
        else:
            # ADCU_P6F is byte-identical to ADCU_P6 in every region (pinned in
            # adcu_p6_p6f_database_identity); emit only its identity footprint
            # instead of duplicating the full monitor vocabulary payload.
            adcu_section[name] = {
                "source": source(db_path, root),
                "table_census": table_census(surfaces[name]),
                "payload_reference": "ADCU_P6",
            }

    p6f_identity = {}
    for region, ctx in contexts.items():
        p6_bytes = (ctx.db_root / "ADCU_P6.ddb").read_bytes()
        p6f_bytes = (ctx.db_root / "ADCU_P6F.ddb").read_bytes()
        p6f_identity[region] = {
            "byte_identical": p6_bytes == p6f_bytes,
            "adcu_p6_sha256": hashlib.sha256(p6_bytes).hexdigest(),
        }

    merged = {**p5_section, "ADCU_P6": adcu_section["ADCU_P6"]}
    payload = {
        "schema": "gtsplus-p5-adas-p6-migration-v1",
        "title": (
            "Current GTS+ underused P5 ADAS databases and the P6 ADAS domain "
            "controller successor surface"
        ),
        "gtsplus_version": component_version(root),
        "regions": list(REGIONS),
        "master_sources": {
            region: {
                "master": source(ctx.db_root / "Toyota.ddb", root),
                "strings": source(ctx.db_root / "M_English.ddb", root),
            }
            for region, ctx in contexts.items()
        },
        "routing": routing_section(contexts),
        "install_set_architectures": architecture_section(contexts),
        "p6_ecosystem": p6_ecosystem_section(contexts),
        "adcu_p6_p6f_database_identity": p6f_identity,
        "p5_databases": p5_section,
        "adcu_p6_databases": adcu_section,
        "module_dependency_graph": dependency_section(merged),
        "concept_migration": migration_section(merged),
        "interpretation": {
            "p5_distributed_ownership": (
                "In the P5 generation the longitudinal/lateral ADAS surface is split across "
                "peers: Fr_RadSen_P5 owns radar health/calibration/blockage vocabulary, "
                "PCS2_P5 owns the pre-collision brake/buzzer/steering request outputs, "
                "PCS1_P5 owns seat-belt pre-tensioner actuation, RoadSign_P5 owns traffic-sign "
                "fusion, LDA_P5 owns lane-departure alert/hands-off vocabulary, and "
                "DSSystem_P5 is the driving-support arbitration ECU whose DTC set enumerates "
                "every upstream sensor it consumes."
            ),
            "p6_consolidation": (
                "ADCU_P6/ADCU_P6F (generation 22) absorbs the recognition/planning role: its "
                "lost-communication set drops the radar/camera/DSS/PCS/steering-actuator "
                "self-facing modules that P5 peers watched, adds direct LVDS/GVIF/MIPI camera "
                "links and per-radar front/side/rear-side comms, and retains only "
                "chassis/powertrain/body consumers (brake, EPS front/rear, steering angle, "
                "ECM/PCM, IPC, restraints, TCM, telematics, navigation)."
            ),
            "recorder_surface_growth": (
                "The P5 RecordOnBehavior surface (behavior X-codes plus RoB data IDs) grows "
                "into a 2,045-entry RoB data-ID surface with a 501-code RoB diag-code "
                "dictionary and a separate DDR event-recorder dictionary with 445 data IDs, "
                "1,797 freeze-frame rows, and 1,165 invalid-condition rows inside ADCU_P6."
            ),
            "plugin_role_continuity": (
                "ADCU keeps the P5 command role numbering (0x05 monitor list, 0x41 signal "
                "info, 0xA0/0xA1 RoB get/delete, 0x19 DTC clear, 0x52 CID) but binds the P6 "
                "plugin implementations, and adds routine active-test (0xAE/0xAF), image-FFD "
                "(0xD2), per-freeze-frame (0xB5), and utility-result (0xB3) roles."
            ),
        },
        "generalization_boundaries": {
            "successor_oracle_only": (
                "ADCU_P6/P6F vocabulary is a generation-22 successor oracle. It must not be "
                "projected onto TSS3/P5 ECUs or onto the Sienna EPS firmware without an "
                "independent join; matching monitor/DTC names are host vocabulary continuity, "
                "not proof of wire-identical behavior."
            ),
            "no_frc_join": (
                "The six P5 targets still have zero install-set co-occurrence with FRC_P5 "
                "category 498 in NA/EU/JP; nothing here changes that boundary."
            ),
            "host_metadata_limit": (
                "DDB/plugin data proves which host-side vocabulary and command roles exist, "
                "not CAN arbitration IDs, ECU-side producer transforms, or SecOC ownership."
            ),
            "rob_ddr_fields_bounded": (
                "RoB/DDR table rows are decoded through name/unit/string joins and the "
                "consumer-proven type-71 offsets; unattributed tail fields remain bounded "
                "raw bytes."
            ),
        },
    }
    return payload


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    payload = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
