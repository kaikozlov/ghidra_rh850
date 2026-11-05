#!/usr/bin/env python3
"""Verify Techstream's DB -> plugin -> frame -> transport execution spine."""
from __future__ import annotations

import hashlib
import json
import struct
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from dataclasses import dataclass

from tools import REPO_ROOT
from tools.techstream.ddb_semantics import (
    NativeQueryResult, NativeSelectionContext, NativeSelectionError, UnresolvedNativeContext,
    exception_event_metadata, merge_native_results, native_variable,
    resolve_frame_program, select_for_consumer, select_native_status,
)
from tools.techstream.gts.master import _master_category_rows
from tools.techstream.parse_ddb import DDBParser, ECUDataBase, Section, StringDataBase, TableDataHead
REPO = REPO_ROOT
ART = REPO / "data/generated/techstream_v18/diagnostic_execution_model.json"
TOOL = REPO / "tools/techstream/extract_diagnostic_execution_model.py"


def resolve_v18() -> Path:
    base = Path(os.environ.get(
        "TECHSTREAM_UNPACKED_ROOT",
        REPO / "software/Techstream/v18/unpacked/toyota/Toyota Diagnostics",
    ))
    for candidate in (base, base / "Techstream"):
        if (candidate / "bin/CommandCommon.dll").is_file():
            return candidate
    return base


def resolve_gts() -> Path:
    base = Path(os.environ.get("GTSPLUS_ROOT", REPO / "software/Techstream/gtsplus"))
    for candidate in (
        base,
        base / "unpacked/gtsplus/Toyota Diagnostics/GTSPlus",
        base / "Toyota Diagnostics/GTSPlus",
    ):
        if (candidate / "bin/CommandCommon.dll").is_file():
            return candidate
    return base


V18 = resolve_v18()
GTS = resolve_gts()
if not (V18 / "NA/DB/Toyota.ddb").is_file() or not (GTS / "NA/DB/Gen/Toyota.ddb").is_file():
    print("[SKIP] pinned Techstream V18 + GTS+ trees are unavailable")
    raise SystemExit(77)

passed = failed = 0
oracle = "instruction_semantics"


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}][{oracle}] {name}{suffix}")


def native_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()


def demand(condition: object, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def ordinals(result: NativeQueryResult) -> list[int]:
    result.require_success()
    return [row.ordinal for row in result.records]


@dataclass
class CategoryCase:
    ordinal: int
    category: int
    initial: list[int]
    history: list[int]
    reflected: list[int] | None = None

    def as_list(self) -> list[object]:
        return [self.ordinal, self.category, self.initial, self.history, self.reflected]


def verify_native_vectors() -> None:
    """Run every supplied current native vector, independently of V18 examples."""
    fixture = json.loads(Path(__file__).with_name("native_selection_vectors.json").read_text())
    parser = DDBParser()
    raw_categories = duplicate_roles = defaults = selector_groups = fallback_queries = 0
    paired_sources = {}
    terminal_sources = {
        "GTSPlus/EU/Gen": (93, 512), "GTSPlus/EU/Spe": (80, 80),
        "GTSPlus/JP/Gen": (93, 512), "GTSPlus/JP/Spe": (80, 80),
        "GTSPlus/NA/Gen": (93, 516), "GTSPlus/NA/Spe": (80, 80),
        "DS-4/DM/Gen": (91, 24), "DS-4/DM/Spe": (80, 20),
        "DS-4/OS/Gen": (89, 41523), "DS-4/OS/Spe": (80, 20),
    }
    for source in fixture["datasets"]:
        path = REPO / source["path"]
        database = parser.parse_master_db(path)

        def fresh() -> NativeSelectionContext:
            context = NativeSelectionContext()
            context.load(database, product=source["product"], region=source["region"], family=source["family"])
            return context

        initial = fresh()
        loaded = initial.file(family=source["family"])
        demand(loaded is not None, source["id"])
        if loaded is None:
            raise AssertionError("source must be loaded")
        demand(loaded.source.sha256 == source["sha256"], f'{source["id"]} exact source bytes')
        paired_sources.setdefault((source["product"], source["region"]), []).append(database)
        terminal_table, terminal_count = terminal_sources[source["id"]]
        proof = loaded.proved_mutation_status(terminal_table)
        demand(max(loaded.catalog) == terminal_table and proof is not None
               and proof["record_count"] == terminal_count and proof["status"] == 0,
               f'{source["id"]} exact current terminal vtable/framing proof')
        for table, expected in source["tables"].items():
            table_type = int(table)
            rows = initial.raw_records(table_type)
            actual = [
                [row.ordinal, row.raw.hex(), row.handling_id, row.handling_flag,
                 list(row.query_key), list(row.native_key)]
                for row in rows
            ]
            demand(len(rows) == expected["count"], f'{source["id"]} table{table} raw count')
            demand(native_digest(actual) == expected["raw_fields_sha256"], f'{source["id"]} table{table} every raw field/ordinal')
            active = initial.active_records(table_type, family=source["family"])
            demand(len(active) == expected["initial_count"], f'{source["id"]} table{table} leading prefix count')
            demand(native_digest([row.ordinal for row in active]) == expected["initial_ordinals_sha256"],
                   f'{source["id"]} table{table} initial physical order')
            demand(len({row.identity for row in rows}) == len(rows), "byte-identical occurrences retain distinct identities")
            demand(all(row.source.product == source["product"] and row.source.region == source["region"]
                       and row.source.family == source["family"] for row in rows), "complete source qualification")

        categories = initial.raw_records(16)
        category_cases = []
        for row in categories:
            handling = row.handling_id
            category_cases.append(CategoryCase(
                row.ordinal, row.category_id,
                ordinals(initial.query(16, row.category_id, family=source["family"])),
                [handling] if handling is not None and handling != 0 else [],
            ))
        raw_categories += len(categories)
        snapshots = [row for row in fixture["snapshots"] if row["dataset"] == source["id"]]
        roles = [row for row in fixture["duplicate_roles"] if row["dataset"] == source["id"]]
        role_defaults = [row for row in fixture["defaults"] if row["dataset"] == source["id"]]
        selectors = [row for row in fixture["duplicate_selectors"] if row["dataset"] == source["id"]]
        payloads = [row for row in fixture["selector136_payloads"] if row["dataset"] == source["id"]]
        histories = {(), *(tuple(row.history) for row in category_cases)}
        histories.update(tuple(row["history"]) for row in snapshots)
        for group in (*roles, *selectors, *payloads):
            histories.update(tuple(row["handling_history"]) for row in group["vectors"])
        for group in role_defaults:
            histories.update(tuple(row["handling_history"]) for row in group["context_changes"])

        for history in sorted(histories):
            context = initial if not history else fresh()
            for handling in history:
                context.correspondence_reflection(0, handling).require_success()
            for case in category_cases:
                if tuple(case.history) == history:
                    case.reflected = ordinals(context.query(16, case.category, family=source["family"]))
            for snapshot in snapshots:
                if tuple(snapshot["history"]) != history:
                    continue
                active = context.active_records(snapshot["table"], family=source["family"])
                demand(len(active) == snapshot["count"]
                       and native_digest([row.ordinal for row in active]) == snapshot["ordinals_sha256"],
                       f'{source["id"]} table{snapshot["table"]} ordered history {history}')
            for group in roles:
                for vector in group["vectors"]:
                    if tuple(vector["handling_history"]) != history:
                        continue
                    for category, expected in (
                        (group["category_id"], vector["exact_query"]),
                        (0xFFFF, vector["category_miss_query"]),
                    ):
                        result = context.query(19, group["role"], category, family=source["family"])
                        demand(ordinals(result) == expected["ordinals"] and result.mode == expected["mode"],
                               f'{source["id"]} role{group["role"]} category{category} history{history}')
            for group in role_defaults:
                vectors = ([{"handling_history": [], "expected": group["expected"]}] if not history else [])
                vectors += group["context_changes"]
                for vector in vectors:
                    if tuple(vector["handling_history"]) != history:
                        continue
                    result = context.query(19, group["role"], group["query_category_id"], family=source["family"])
                    expected = vector["expected"]
                    demand(ordinals(result) == expected["ordinals"] and result.mode == expected["mode"],
                           f'{source["id"]} role{group["role"]} actual role-head source history{history}')
                if not history:
                    result = context.query(19, group["role"], group["query_category_id"], family=source["family"])
                    selected = select_for_consumer(result, "plugin")
                    demand(selected.category_id == group["default_source_category_id"] and selected.dll_name == group["dll"],
                           "registered filename casing and nonzero-category defaults")
                    for start, end in fixture["fallback_category_sets"][group["fallback_category_set"]]:
                        for category in range(start, end + 1):
                            result = context.query(19, group["role"], category, family=source["family"])
                            demand(result.mode == "first-role" and ordinals(result) == group["expected"]["ordinals"],
                                   f'{source["id"]} every supplied role{group["role"]} category{category} fallback')
                            fallback_queries += 1
            for group in selectors:
                for vector in group["vectors"]:
                    if tuple(vector["handling_history"]) != history:
                        continue
                    result = context.query(18, *group["query_key"], family=source["family"])
                    demand(ordinals(result) == vector["expected_ordinals"],
                           f'{source["id"]} selector{group["query_key"]} history{history}')
                    actual_steps = [
                        [row.ordinal, row.u16(6), row.u16(4), result.records[0].u16(4),
                         [frame.ordinal for frame in context.query(17, row.u16(6), family=source["family"]).records],
                         [commset.ordinal for commset in context.query(29, result.records[0].u16(4), family=source["family"]).records]]
                        for row in result.records
                    ]
                    demand(actual_steps == vector["steps"], "every selector step keeps its frame and first-row CommSet")
            for group in payloads:
                for vector in group["vectors"]:
                    if tuple(vector["handling_history"]) != history:
                        continue
                    frames = resolve_frame_program(context, *group["query_key"], variable_namespace_base=0x2710)
                    demand([frame["selection"]["selector_occurrence"]["ordinal"] for frame in frames] == vector["expected_ordinals"],
                           "all21 selector136 source ordinals")
                    for frame, step in zip(frames, vector["steps"]):
                        demand(frame["comm_frame_raw"] == step["frame_raw"], "selector136 exact frame bytes")
                        for output, expected_key in (("send", "send"), ("receive_mask", "mask"), ("receive_check", "check")):
                            expected = step["variables"][expected_key]
                            demand(frame[output]["id"] == f'0x{expected["source_id"]:X}'
                                   and frame[output]["bytes"] == expected["bytes"], "selector136 initial0100/event2100 payload")

        demand(native_digest([case.as_list() for case in category_cases]) == source["category_queries_sha256"],
               f'{source["id"]} every raw category initial and own-handler query')
        duplicate_roles += len(roles)
        defaults += len(role_defaults)
        selector_groups += len(selectors)
    check("native all13772 raw category occurrences and conditional variants", raw_categories == 13772)
    check("native all66 duplicate role groups", duplicate_roles == 66)
    check("native all575 main plus359 DS4 role defaults", defaults == 934)
    check("native every supplied fallback category", fallback_queries == 1318787, str(fallback_queries))
    check("native all2549 duplicate selector query groups", selector_groups == 2549)
    check("native all269 single/cumulative/reversed history snapshots", len(fixture["snapshots"]) == 269)
    for identity, databases in paired_sources.items():
        context = NativeSelectionContext()
        for database in databases:
            context.load(database)
        for handling in (136, 1, 136):
            reflected = context.correspondence_reflection(0, handling).require_success()
            demand(all(file["terminal_status"] == 0 for file in reflected.provenance[0]["files"]),
                   f"{identity} actual Gen/Spe terminal statuses in repeated event history")
    check("native all5 current paired Gen/Spe terminal status contracts", len(paired_sources) == 5)


def verify_native_boundaries() -> None:
    """Synthetic raw rows isolate comparator, load, merge and consumer boundaries."""
    with tempfile.TemporaryDirectory(prefix="native-index-boundaries-") as tmp:
        root = Path(tmp)
        database_serial = 0

        def section(table: int, rows: list[bytes], *, variable: bool = False) -> Section:
            data = b"".join(rows)
            return Section(TableDataHead(table, 0, len(rows), len(data)), 0, data,
                           schema_family="gtsplus", variable_layout=variable)

        def database(family: str, sections: dict[int, Section], name: str = "Toyota.ddb", format_version: int = 1) -> ECUDataBase:
            nonlocal database_serial
            suffix = Path(name).suffix
            path = root / family / f"{Path(name).stem}-{database_serial}{suffix}"
            database_serial += 1
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(b"native index fixture:" + family.encode() + name.encode()
                             + b"".join(struct.pack("<I", table) + item.raw_data for table, item in sections.items()))
            return ECUDataBase(path, format_version, sections, schema_family="gtsplus")

        def dll(name: str, role: int, category: int, handling: int = 0, flag: int = 0) -> bytes:
            row = bytearray(88)
            encoded = name.encode("utf-16le")
            row[:len(encoded)] = encoded
            struct.pack_into("<3H", row, 80, category, handling, role)
            row[86] = flag
            return bytes(row)

        rows = [
            dll("a.dll", 9, 10), dll("b.dll", 9, 10),
            dll("delete.dll", 9, 10, 7, 1), dll("late-default.dll", 9, 0),
            dll("replace.dll", 9, 10, 8, 2),
            dll("before.dll", 9, 5, 9, 2), dll("after.dll", 9, 15, 9, 2),
        ]
        gen = database("Gen", {19: section(19, rows)})
        context = NativeSelectionContext()
        context.load(gen)
        demand(ordinals(context.query(19, 9, 10)) == [0, 1], "leading handling0 prefix only, duplicate equal rows retained")
        context.correspondence_reflection(0, 7).require_success()
        demand(ordinals(context.query(19, 9, 10)) == [1], "flag1 removes only the first equal active row")
        context.correspondence_reflection(0, 8).require_success()
        demand(ordinals(context.query(19, 9, 10)) == [4], "flag2 replaces the first equal row")
        context.correspondence_reflection(0, 9).require_success()
        demand([row.ordinal for row in context.active_records(19)] == [5, 4, 6], "comparator insertion before/after")
        demand(select_for_consumer(context.query(19, 9, 99), "plugin").ordinal == 5, "nonzero-category first-role fallback")
        context.correspondence_reflection(0, 8).require_success()
        demand([row.ordinal for row in context.active_records(19)] == [5, 4, 6], "repeated replacement identity")
        demand(context.correspondence_reflection(0, 0).status == 0xA0030102, "reflection rejects handling0")
        before = [row.identity for row in context.active_records(19)]
        context.correspondence_reflection(123, 8)
        demand([row.identity for row in context.active_records(19)] == before, "ECU-target events do not mutate master")
        cached = context.load(database("Gen", {19: section(19, rows)}, "ECU.ddb", 2), ecu_id=123, load_id="cached-ecu")
        context.correspondence_reflection(0, 8)
        current_cached = context.file(ecu_id=123)
        demand(current_cached is not None and current_cached.load_id == cached.load_id, "master mutation does not reload cached ECU")
        demand(context.query(19, 9, 10, ecu_id=123).status is None, "ECU table19 is not assigned a master comparator")
        context.load(gen, load_id="fresh")
        demand(ordinals(context.query(19, 9, 10)) == [0, 1], "reload restores initial index and clears query memo")
        empty = NativeSelectionContext()
        empty.load(database("Gen", {19: section(19, [dll("insert.dll", 9, 5, 1, 2)])}))
        demand(not empty.active_records(19), "first nonzero handling gives an empty default index")
        empty.correspondence_reflection(0, 1).require_success()
        demand(ordinals(empty.query(19, 9, 5)) == [0], "flag2 insertion into empty index")
        between = NativeSelectionContext()
        between.load(database("Gen", {19: section(19, [
            dll("low.dll", 9, 10), dll("high.dll", 9, 20),
            dll("middle.dll", 9, 15, 1, 2), dll("ignored.dll", 9, 13, 2, 3),
        ])}))
        between.correspondence_reflection(0, 1).require_success()
        demand([row.ordinal for row in between.active_records(19)] == [0, 2, 1], "comparator insertion between two active keys")
        between.correspondence_reflection(0, 2).require_success()
        demand([row.ordinal for row in between.active_records(19)] == [0, 2, 1], "flags other than1/2 do not mutate")

        selector_rows = [
            struct.pack("<7H2B", 1, 10, 1, 101, 0, 0, 0, 0, 0),
            struct.pack("<7H2B", 1, 10, 2, 102, 0, 1, 0, 0, 0),
            struct.pack("<7H2B", 1, 10, 1, 103, 9, 0, 0, 2, 0),
        ]
        variables = struct.pack("<IHIHIH", 0, 1, 1, 1, 2, 1) + b"\x01\x02\x03"
        variable_section = Section(TableDataHead(0, 0, 3, len(variables)), 0, variables,
                                   schema_family="gtsplus", variable_layout=True)
        commset = struct.pack("<IIHHHBB", 1, 100, 0, 1, 0, 1, 0)
        timer = struct.pack("<IHHHBB", 10, 1, 1, 0, 0, 0)
        master_sections = {
            0: variable_section, 18: section(18, selector_rows),
            17: section(17, [struct.pack("<4H", frame, index, 0, 0) for frame, index in ((101, 1), (102, 2), (103, 3))]),
            29: section(29, [commset]), 25: section(25, [timer, timer]),
        }
        frames_context = NativeSelectionContext()
        frames_context.load(database("Gen", master_sections))
        program = resolve_frame_program(frames_context, 1, 10)
        demand([row["send"]["bytes"] for row in program] == ["01", "02"], "true multiframe program retains every frame")
        demand([row["comm_set"] for row in program] == [1, 1], "every step consumes the first selector CommSet")
        frames_context.correspondence_reflection(0, 9).require_success()
        demand([row["send"]["bytes"] for row in resolve_frame_program(frames_context, 1, 10)] == ["03", "02"],
               "selector+A replacement key preserves the other query-equal step")
        spe_variables = struct.pack("<IHIH", 0, 1, 1, 1) + b"\xaa\xbb"
        frames_context.load(database("Spe", {
            0: Section(TableDataHead(0, 0, 2, len(spe_variables)), 0, spe_variables,
                       schema_family="gtsplus", variable_layout=True),
            17: section(17, [struct.pack("<4H", 101, 2, 0, 0)]),
        }))
        query = frames_context.query(17, 101)
        demand(len(query.records) == 2 and [row.source.family for row in query.records] == ["Gen", "Spe"],
               "Gen/Spe concatenation retains source-qualified equal-key records")
        demand(select_for_consumer(query, "frame").source.family == "Gen", "frame consumes record0, not exact1")
        demand(native_variable(frames_context, query.records[1], 2, namespace_base=0)["bytes"] == "bb",
               "equal-key Spe frame retains its own source variable table")
        spe_only_frames = {**master_sections, 17: section(17, [
            struct.pack("<4H", frame, index, 0, 0) for frame, index in ((102, 2), (103, 3))
        ])}
        frames_context.load(database("Gen", spe_only_frames))
        demand([row["send"]["bytes"] for row in resolve_frame_program(frames_context, 1, 10)] == ["bb", "02"],
               "selected Spe frame materializes Spe bytes while subsequent Gen step retains Gen bytes")
        frames_context.load(database("Gen", master_sections))
        frames_context.load(database("Spe", {29: section(29, [commset])}))
        try:
            select_for_consumer(frames_context.query(29, 1), "commset")
        except NativeSelectionError as error:
            demand(error.status == 0xC0040102, "merged CommSet exact1 cardinality")
        else:
            raise AssertionError("two merged CommSets were admitted")
        timer_query = frames_context.query(25, 1, 1)
        try:
            select_for_consumer(timer_query, "timer")
        except NativeSelectionError as error:
            demand(error.status == 0xC0040102, "strict timer excess count")
        else:
            raise AssertionError("strict timer accepted excess rows")
        demand(select_for_consumer(timer_query, "timer", timer_policy="report-and-continue").ordinal == 0,
               "module-specific row0 timer policy")
        empty_send = NativeSelectionContext()
        empty_send.load(database("Gen", {**master_sections, 17: section(17, [
            struct.pack("<4H", 101, 0, 0, 0), struct.pack("<4H", 102, 2, 0, 0),
        ])}))
        try:
            resolve_frame_program(empty_send, 1, 10)
        except NativeSelectionError as error:
            demand(error.status == 0xC0040102, "empty send-variable consumer failure")
        else:
            raise AssertionError("frame admitted an empty send variable")

        category = bytearray(76)
        category[:10] = "S.ddb".encode("utf-16le")
        struct.pack_into("<I", category, 60, 1)
        struct.pack_into("<H", category, 68, 2)
        family_context = NativeSelectionContext()
        family_context.load(database("Gen", {16: section(16, [])}))
        family_context.load(database("Spe", {16: section(16, [bytes(category)])}))
        demand(not family_context.query(16, 2).records, "public category query excludes Spe")
        demand(family_context.ecu_file_category(2, "Spe").records[0].database_name == "S.ddb",
               "ReadDbEcuFile uses its requested family's category")
        gen_categories = database("Gen", {16: section(16, [bytes(category)])})
        family_context.load(gen_categories)
        name_bytes = "GEN-only".encode("utf-16le")
        gen_strings = StringDataBase(
            gen_categories.path.with_name("M_English.ddb"), 1,
            struct.pack("<IH", 0, len(name_bytes)) + name_bytes, 6,
        )
        category_rows = _master_category_rows(DDBParser(), family_context, gen_strings)
        demand(len(category_rows) == 2 and category_rows[0]["name"] == "GEN-only"
               and category_rows[1]["name"] is None and category_rows[1]["name_string_index"] == 1
               and category_rows[1]["string_resolution"]["status"] == "unresolved-source",
               "all raw category occurrences survive without borrowing Gen strings for Spe")
        demand(family_context.query(16, 0x10000).status == 0xA0030102, "category key width")
        demand(context.query(19, 0x10000, 10).status == 0 and not context.query(19, 0x10000, 10).records,
               "DLL role aboveFFFF is a successful miss")
        unknown = NativeSelectionContext(history_known=False)
        unknown.load(gen)
        unresolved = unknown.query(19, 9, 10)
        demand(unresolved.status is None and not unresolved.records
               and [row.ordinal for row in unresolved.raw_variants] == list(range(7)), "unknown history retains all relevant raw role variants")
        try:
            unresolved.require_success()
        except UnresolvedNativeContext:
            pass
        else:
            raise AssertionError("unknown live history became initial selection")

        missing = NativeSelectionContext()
        demand(missing.query(17, 1).status == 0xA0030106, "missing loaded file")
        missing.load(database("Gen", {}))
        demand(missing.query(17, 1).status == 0xA0030107, "missing table wins its configured rank")
        demand(missing.ecu_file_category(1, "Gen").status == 0xA0030106, "ReadDbEcuFile absent category table")
        demand(select_native_status(0xA0030106, 0xA0030107) == 0xA0030107, "native failure rank")
        demand(select_native_status(0xDEADBEEF, 0xA0030107) == 0xDEADBEEF, "unlisted status rank0")
        demand(merge_native_results(17, NativeQueryResult(0), NativeQueryResult(0xA0030107)).status == 0,
               "successful zero-row Gen query tolerates absent Spe table")
        demand(merge_native_results(17, NativeQueryResult(0xA0030102), NativeQueryResult(0)).status == 0xA0030102,
               "hard Gen error aborts before Spe success")
        demand(merge_native_results(17, NativeQueryResult(0), NativeQueryResult(0xA0030108)).status == 0xA0030108,
               "hard Spe error propagates after successful Gen")
        for consumer, expected in (("plugin", 0xC0040101), ("selector", 0xC0040101),
                                   ("frame", 0xC0040101), ("commset", 0xC0040102),
                                   ("timer", 0xC0040101), ("read_ecu_file", 0xA0030104)):
            try:
                select_for_consumer(NativeQueryResult(0), consumer)
            except NativeSelectionError as error:
                demand(error.status == expected, f"{consumer} zero-count status")
            else:
                raise AssertionError(f"{consumer} accepted zero rows")
        overflow = NativeSelectionContext()
        overflow.load(database("Gen", {17: section(17, [b"\x01\0" + b"\0" * 6] * 0x8000)}))
        demand(overflow.query(17, 1).status == 0xA0030110, "SetData count8000 status")

        event = struct.pack("<II5H2B", 0, 0x00020001, 101, 7, 1, 136, 0, 1, 4)
        event_context = NativeSelectionContext()
        event_context.load(database("Gen", {4: section(4, [event])}))
        metadata = exception_event_metadata(event_context.raw_records(4)[0])
        demand(metadata["query_keys"] == [1, 2] and metadata["emitted_handling_id"] == 136
               and metadata["condition_mode"] == 1 and metadata["required_response_length"] == 4,
               "event fields remain data, without a synthesized probe result")
        default_event = struct.pack("<II4H3B", 0, 0x00020001, 101, 7, 1, 136, 3, 2, 8)
        event_context.load(database("Gen", {58: section(58, [default_event])}))
        metadata = exception_event_metadata(event_context.raw_records(58)[0])
        demand(metadata["query_keys"] == [1, 3, 2] and metadata["target_ecu"] == 1
               and metadata["emitted_handling_id"] == 136 and metadata["condition_mode"] == 2
               and metadata["required_response_length"] == 8, "default-event query width and byte gates")
        terminal_context = NativeSelectionContext()
        observed = {}
        for family, table in (("Gen", 93), ("Spe", 80)):
            loaded = terminal_context.load(database(family, {
                19: section(19, rows), 70: section(70, [b"\0"]), table: section(table, [bytes(16)]),
            }))
            observed[loaded.source.identity] = {70: 0xA0030108}
        reflected = terminal_context.correspondence_reflection(0, 8, table_statuses=observed)
        demand(reflected.status == 0 and all(file["derived_table_statuses"] for file in reflected.provenance[0]["files"]),
               "actual main terminal vtables overwrite earlier failure statuses without inventing query layouts")
        demand(terminal_context.query(93, 1).status is None, "terminal status proof does not invent a comparator/query")
        invalid_terminals = NativeSelectionContext()
        for family, table in (("Gen", 93), ("Spe", 80)):
            invalid_terminals.load(database(family, {table: section(table, [bytes(8)])}))
        demand(invalid_terminals.correspondence_reflection(0, 8).status is None,
               "terminal proof rejects incompatible physical record framing")
        failure_context = NativeSelectionContext()
        failures = {}
        for family in ("Gen", "Spe"):
            loaded = failure_context.load(database(family, {19: section(19, rows), 99: section(99, [b"\0"])}))
            failures[loaded.source.identity] = {99: 0xA0030108}
        result = failure_context.correspondence_reflection(0, 8, table_statuses=failures)
        demand(result.status == 0xA0030108 and failure_context.query(19, 9, 10).records[0].ordinal == 4,
               "later table failures do not roll back prior known mutations")
        demand(failure_context.query(99, 1).status is None, "unknown comparator layout remains unproved")
    check("native deterministic mutation/load/merge/cardinality/event boundaries", True)


verify_native_vectors()
verify_native_boundaries()


with tempfile.TemporaryDirectory() as td:
    out = Path(td) / "model.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(TOOL),
            "--techstream-root",
            str(V18),
            "--gts-root",
            str(GTS),
            "--out",
            str(out),
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    check("execution-model extractor succeeds", proc.returncode == 0, proc.stderr[-400:])
    check("execution-model artifact regenerates exactly", proc.returncode == 0 and out.read_bytes() == ART.read_bytes())

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
raise SystemExit(1 if failed else 0)
