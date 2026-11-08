#!/usr/bin/env python3
"""Lossless DDB records and current native active-index/consumer semantics."""
from __future__ import annotations

import hashlib
import struct
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, overload

from tools import REPO_ROOT
from tools.techstream.parse_ddb import DDBParser, ECUDataBase, Section



def records(section: Section) -> Iterable[bytes]:
    """Read physical rows through the parser's fixed/variable record grammar."""
    for record in section.iter_records():
        yield record.raw


# Current KgpDataCtrl main/DS4 vtable+40/+44/+4C contracts. The selector's
# tertiary comparator key is deliberately NOT an additional query argument.
_INDEX_LAYOUTS = {
    16: (76, (68,), (68,), 70, 73),
    17: (8, (0,), (0,), None, None),
    18: (16, (0, 2), (0, 2, 10), 8, 14),
    25: (12, (4, 6), (4, 6), 8, 10),
    29: (16, (10,), (10,), 8, 15),
}
_STATUS_RANK = {
    0: 255, 0xA0030100: 255, 0xA0030101: 255, 0xA0030102: 3,
    0xA0030103: 255, 0xA0030104: 255, 0xA0030105: 255,
    0xA0030106: 2, 0xA0030107: 1, 0xA0030108: 5,
    0xA0030109: 255, 0xA0030110: 4,
}
_TOLERATED_MISSING = (0xA0030106, 0xA0030107)

# Exact current factory/vtable proofs for the actual terminal master tables.
# These prove mutation RETURN STATUS only, not their unmodeled query indices:
# base MakeIndex/SubstituteRecord return zero for nonnull, in-bounds materialized
# rows and valid index/count arguments, independently of the comparator result.
# Do not extend this to another class merely because its name looks similar.
_NATIVE_INDEX_PROGRAMS = {
    "gtsplus": "19e709e12e53f485a84ccfbf6b226922b88502206c34b767db543c7f3df101f8",
    "ds4": "a7e420f1cdca11594b2390c05b146c868a79c82d892449c98c5ffc4f12e12a4c",
}
_REFLECTION_STATUS_PROOFS = {
    # (row size, slots14/16/17/18: MakeIndex/H getter/flag getter/Substitute).
    ("gtsplus", 80): (16, 0x10064540, 0x100D0A20, 0x100D09E0, 0x10064740),
    ("gtsplus", 93): (16, 0x10064540, 0x100CC030, 0x100CBFF0, 0x10064740),
    ("ds4", 80): (16, 0x1005ED80, 0x100C2270, 0x100C2230, 0x1005EF80),
    ("ds4", 89): (8, 0x1005ED80, 0x1005EF60, 0x1005EF70, 0x1005EF80),
    ("ds4", 91): (4, 0x1005ED80, 0x1005EF60, 0x1005EF70, 0x1005EF80),
}


class NativeSelectionError(ValueError):
    def __init__(self, status: int, result: NativeQueryResult | None = None):
        self.status = status
        self.result = result
        super().__init__(f"native database selection failed: 0x{status:08X}")


class UnresolvedNativeContext(ValueError):
    def __init__(self, message: str, result: NativeQueryResult | None = None):
        self.result = result
        super().__init__(message)


@dataclass(frozen=True)
class NativeSource:
    path: str
    sha256: str
    product: str
    region: str
    family: str
    schema_family: str
    format_version: int

    @property
    def repo_path(self) -> str:
        """Path relative to the repository root, for identities and artifacts.

        ``path`` stays the absolute filesystem handle for IO; identities and
        serialized bundles must not embed workstation paths.
        """
        try:
            return str(Path(self.path).resolve().relative_to(REPO_ROOT))
        except ValueError:
            return self.path

    @property
    def identity(self) -> str:
        return (
            f"{self.product}/{self.region}/{self.family}:{self.repo_path}:"
            f"sha256:{self.sha256}:format:{self.format_version}:{self.schema_family}"
        )

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["path"] = self.repo_path
        return {**data, "identity": self.identity}


@dataclass(frozen=True)
class NativeOccurrence:
    source: NativeSource
    table_type: int
    ordinal: int
    raw: bytes
    source_payload_offset: int
    decoded_offset: int | None

    def u16(self, offset: int) -> int:
        return struct.unpack_from("<H", self.raw, offset)[0]

    @property
    def identity(self) -> str:
        return f"{self.source.identity}:table:{self.table_type}:ordinal:{self.ordinal}"

    @property
    def layout(self) -> tuple[int, tuple[int, ...], tuple[int, ...], int | None, int | None] | None:
        if self.source.format_version != 1 or self.source.schema_family not in ("gtsplus", "ds4"):
            return None
        if self.table_type == 19:
            role = 84 if self.source.schema_family == "gtsplus" else 86
            flag = 86 if self.source.schema_family == "gtsplus" else 87
            return (88, (role, 80), (role, 80), 82, flag)
        return _INDEX_LAYOUTS.get(self.table_type)

    @property
    def query_key(self) -> tuple[int, ...]:
        layout = self.layout
        if layout is None:
            raise UnresolvedNativeContext(f"unproved index layout: {self.identity}")
        return tuple(
            self.raw[offset] if self.table_type == 19 and offset == 86 else self.u16(offset)
            for offset in layout[1]
        )

    @property
    def native_key(self) -> tuple[int, ...]:
        layout = self.layout
        if layout is None:
            raise UnresolvedNativeContext(f"unproved comparator: {self.identity}")
        return tuple(
            self.raw[offset] if self.table_type == 19 and offset == 86 else self.u16(offset)
            for offset in layout[2]
        )

    @property
    def handling_id(self) -> int | None:
        layout = self.layout
        return None if layout is None else 0 if layout[3] is None else self.u16(layout[3])

    @property
    def handling_flag(self) -> int | None:
        layout = self.layout
        return None if layout is None else 0 if layout[4] is None else self.raw[layout[4]]

    def _require_table(self, table_type: int) -> None:
        if self.table_type != table_type or self.layout is None:
            raise UnresolvedNativeContext(f"unproved field layout: {self.identity}")

    @property
    def category_id(self) -> int:
        if self.layout is None or self.table_type not in (16, 19, 18, 25):
            raise UnresolvedNativeContext(f"unproved category field: {self.identity}")
        return self.u16({16: 68, 19: 80, 18: 0, 25: 4}[self.table_type])

    @property
    def dll_role_id(self) -> int:
        self._require_table(19)
        return self.query_key[0]

    @property
    def dll_name(self) -> str:
        self._require_table(19)
        return self.raw[:80].decode("utf-16le").split("\0", 1)[0]

    @property
    def database_name(self) -> str:
        self._require_table(16)
        return self.raw[:40].decode("utf-16le").split("\0", 1)[0]

    @property
    def ecu_short_name(self) -> str:
        self._require_table(16)
        return self.raw[40:60].decode("utf-16le").split("\0", 1)[0]

    @property
    def ecu_name_string_index(self) -> int:
        self._require_table(16)
        return struct.unpack_from("<I", self.raw, 60)[0]

    @property
    def generation(self) -> int:
        self._require_table(16)
        return self.raw[72]

    def as_dict(self) -> dict[str, Any]:
        result = {
            "identity": self.identity, "source": self.source.as_dict(),
            "table_type": self.table_type, "ordinal": self.ordinal,
            "raw": self.raw.hex(), "source_payload_offset": self.source_payload_offset,
            "decoded_offset": self.decoded_offset,
            "handling_id": self.handling_id, "handling_flag": self.handling_flag,
        }
        if self.layout is not None:
            result.update(query_key=list(self.query_key), native_key=list(self.native_key))
        return result


@dataclass(frozen=True)
class NativeQueryResult:
    status: int | None
    records: tuple[NativeOccurrence, ...] = ()
    mode: str = "exact"
    provenance: tuple[dict[str, Any], ...] = ()
    raw_variants: tuple[NativeOccurrence, ...] = ()

    def require_success(self) -> NativeQueryResult:
        if self.status is None:
            raise UnresolvedNativeContext(self.mode, self)
        if self.status:
            raise NativeSelectionError(self.status, self)
        return self

    def as_dict(self) -> dict[str, Any]:
        return {
            "status": self.status, "mode": self.mode,
            "records": [row.as_dict() for row in self.records],
            "provenance": list(self.provenance),
            "raw_variants": [row.as_dict() for row in self.raw_variants],
        }


def select_native_status(gen_status: int, spe_status: int) -> int:
    return gen_status if _STATUS_RANK.get(gen_status, 0) <= _STATUS_RANK.get(spe_status, 0) else spe_status


def merge_native_results(table_type: int, gen: NativeQueryResult, spe: NativeQueryResult) -> NativeQueryResult:
    gs, ss = gen.status, spe.status
    if table_type == 16 or gs is None or gs not in (0, *_TOLERATED_MISSING):
        return gen
    if ss is None or ss not in (0, *_TOLERATED_MISSING):
        return NativeQueryResult(ss, mode=spe.mode, provenance=gen.provenance + spe.provenance,
                                 raw_variants=spe.raw_variants)
    status = 0 if gs == 0 or ss == 0 else select_native_status(gs, ss)
    rows = (gen.records if gs == 0 else ()) + (spe.records if ss == 0 else ())
    mode = gen.mode if gen.records else spe.mode if spe.records else gen.mode if gs == 0 else spe.mode
    return NativeQueryResult(status, rows, mode, gen.provenance + spe.provenance)


def _first_native_run(rows: Iterable[NativeOccurrence], position: int, value: int) -> tuple[NativeOccurrence, ...]:
    found: list[NativeOccurrence] = []
    for row in rows:
        if row.query_key[position] == value:
            found.append(row)
        elif found:
            break
    return tuple(found)


@dataclass
class NativeFile:
    database: ECUDataBase
    source: NativeSource
    ecu_id: int
    load_id: str
    catalog: dict[int, tuple[NativeOccurrence, ...]]
    _active: dict[int, list[NativeOccurrence]] = field(default_factory=dict)
    _first_runs: dict[tuple[int, int], tuple[NativeOccurrence, ...]] = field(default_factory=dict)

    def first_run(self, table_type: int, key: int) -> tuple[NativeOccurrence, ...]:
        """Memoize a native contiguous run only within this mutable load instance."""
        identity = (table_type, key)
        found = self._first_runs.get(identity)
        if found is None:
            found = _first_native_run(self._active[table_type], 0, key)
            self._first_runs[identity] = found
        return found

    def apply_handling(self, handling_id: int) -> list[str]:
        """Literal MakeIndex(H)/SubstituteRecord; never sort the physical rows."""
        self._first_runs.clear()
        applied = []
        for table_type in sorted(self._active):
            active = self._active[table_type]
            rows = self.catalog[table_type]
            start = next((i for i, row in enumerate(rows) if row.handling_id == handling_id), len(rows))
            for row in rows[start:]:
                current_id = row.handling_id
                if current_id is None or current_id > handling_id:
                    break
                if current_id != handling_id:
                    continue
                flag, key = row.handling_flag, row.native_key
                if flag == 1:
                    for index, old in enumerate(active):
                        if old.native_key == key:
                            del active[index]
                            applied.append(row.identity)
                            break
                elif flag == 2:
                    if not active:
                        active.append(row)
                        applied.append(row.identity)
                        continue
                    for index, old in enumerate(active):
                        if key < old.native_key:
                            active.insert(index, row)
                        elif key == old.native_key:
                            active[index] = row
                        elif index + 1 == len(active):
                            active.append(row)
                        else:
                            continue
                        applied.append(row.identity)
                        break
        return applied


    def proved_mutation_status(self, table_type: int) -> dict[str, Any] | None:
        """Discharge only exact source-qualified base-method input guards."""
        proof = _REFLECTION_STATUS_PROOFS.get((self.source.schema_family, table_type))
        rows = self.catalog.get(table_type, ())
        if self.source.format_version != 1 or proof is None or not rows:
            return None
        size, make_index, handling_getter, flag_getter, substitute = proof
        if any(len(row.raw) != size for row in rows):
            return None
        return {
            "table_type": table_type, "status": 0, "record_size": size,
            "record_count": len(rows),
            "native_program_sha256": _NATIVE_INDEX_PROGRAMS[self.source.schema_family],
            "vtable_slots": {"14": f"0x{make_index:08X}", "16": f"0x{handling_getter:08X}",
                             "17": f"0x{flag_getter:08X}", "18": f"0x{substitute:08X}"},
            "scope": "base-mutation return status; query/index layout remains unmodeled",
        }


class NativeSelectionContext:
    """Loaded current-source objects and explicit ordered reflection history.

    Immutable physical occurrences survive index mutation and reload. Unknown
    table getters/comparators remain unproved; their observed terminal statuses
    can be supplied independently of the known tables' mutations.
    """

    def __init__(self, history_known: bool = True):
        self.history_known = history_known
        self._files: dict[tuple[int, str], NativeFile] = {}
        self.loads: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    def load(
        self, database: ECUDataBase, *, ecu_id: int = 0, load_id: str | None = None,
        product: str | None = None, region: str | None = None, family: str | None = None,
    ) -> NativeFile:
        if database.schema_family not in ("gtsplus", "ds4"):
            raise ValueError("current native proof does not apply to legacy V18")
        path = database.path
        family = family or path.parent.name
        if family not in ("Gen", "Spe"):
            raise ValueError(f"explicit Gen/Spe family required for {path}")
        if not 0 <= ecu_id <= 0xFFFF:
            raise NativeSelectionError(0xA0030102)
        source = NativeSource(
            str(path), hashlib.sha256(path.read_bytes()).hexdigest(),
            product or ("DS-4" if database.schema_family == "ds4" else "GTSPlus"),
            region or path.parent.parent.parent.name, family, database.schema_family, database.format_version,
        )
        catalog = {
            table: tuple(
                NativeOccurrence(source, table, row.index, row.raw, row.source_payload_offset, row.decoded_offset)
                for row in section.iter_records()
            ) for table, section in database.sections.items()
        }
        loaded = NativeFile(database, source, ecu_id, load_id or f"load-{len(self.loads)}", catalog)
        if source.format_version == 1:
            for table, rows in catalog.items():
                if table not in (*_INDEX_LAYOUTS, 19):
                    continue
                active: list[NativeOccurrence] = []
                for row in rows:
                    layout = row.layout
                    if layout is None or len(row.raw) != layout[0]:
                        raise ValueError(f"invalid proved record layout: {row.identity}")
                    if row.handling_id:
                        break
                    active.append(row)
                # Check conditional rows too, without admitting them to the index.
                for row in rows:
                    layout = row.layout
                    if layout is None or len(row.raw) != layout[0]:
                        raise ValueError(f"invalid proved table layout: {source.identity}:{table}")
                loaded._active[table] = active
        self._files[(ecu_id, family)] = loaded
        self.loads.append({"source": source.as_dict(), "ecu_id": ecu_id, "load_id": loaded.load_id,
                           "after_event_count": len(self.events)})
        return loaded

    def file(self, *, ecu_id: int = 0, family: str = "Gen") -> NativeFile | None:
        return self._files.get((ecu_id, family))

    def database_for(self, occurrence: NativeOccurrence) -> ECUDataBase:
        for loaded in self._files.values():
            if loaded.source == occurrence.source:
                return loaded.database
        raise UnresolvedNativeContext(f"occurrence source is no longer loaded: {occurrence.identity}")

    def raw_records(self, table_type: int, *, ecu_id: int = 0, family: str | None = None) -> tuple[NativeOccurrence, ...]:
        return tuple(
            row for selected in ((family,) if family is not None else ("Gen", "Spe"))
            if (loaded := self.file(ecu_id=ecu_id, family=selected)) is not None
            for row in loaded.catalog.get(table_type, ())
        )

    def active_records(self, table_type: int, *, ecu_id: int = 0, family: str | None = None) -> tuple[NativeOccurrence, ...]:
        if not self.history_known:
            raise UnresolvedNativeContext("unknown live reflection history")
        families = (family,) if family is not None else ("Gen",) if table_type == 16 else ("Gen", "Spe")
        rows = []
        for selected in families:
            loaded = self.file(ecu_id=ecu_id, family=selected)
            if loaded is None:
                continue
            if table_type in loaded.catalog and table_type not in loaded._active:
                raise UnresolvedNativeContext(f"unproved active index: {loaded.source.identity}:{table_type}")
            rows.extend(loaded._active.get(table_type, ()))
        return tuple(rows)

    def _query_family(self, table_type: int, keys: tuple[int, ...], ecu_id: int, family: str) -> NativeQueryResult:
        loaded = self.file(ecu_id=ecu_id, family=family)
        origin = {"family": family, "ecu_id": ecu_id, "table_type": table_type, "keys": list(keys),
                  "context": self.as_dict()}
        if loaded is None:
            return NativeQueryResult(0xA0030106, provenance=(origin,))
        origin.update(source=loaded.source.as_dict(), load_id=loaded.load_id)
        if table_type not in loaded.catalog:
            return NativeQueryResult(0xA0030107, provenance=(origin,))
        if not self.history_known or table_type not in loaded._active:
            return NativeQueryResult(None, mode="unresolved-history" if not self.history_known else "unproved-layout",
                                     provenance=(origin,), raw_variants=loaded.catalog[table_type])
        first = loaded.first_run(table_type, keys[0])
        if table_type == 19:
            role_rows = first
            exact = _first_native_run(role_rows, 1, keys[1])
            mode = "exact" if exact else "first-role" if role_rows else "no-role"
            selected = exact if exact else role_rows[:1]
        else:
            selected = first
            for position, key in enumerate(keys[1:], 1):
                selected = _first_native_run(selected, position, key)
            mode = "exact" if selected else "empty"
        # DLL GetQuery deliberately ignores its SetData return status.
        if len(selected) >= 0x8000:
            return NativeQueryResult(0 if table_type == 19 else 0xA0030110, mode="setdata-count-overflow", provenance=(origin,))
        origin.update(mode=mode, selected_ids=[row.identity for row in selected])
        return NativeQueryResult(0, selected, mode, (origin,))

    def _raw_candidates(self, table_type: int, keys: tuple[int, ...], ecu_id: int, family: str | None) -> tuple[NativeOccurrence, ...]:
        candidates = self.raw_records(table_type, ecu_id=ecu_id, family=family)
        return tuple(
            row for row in candidates
            if row.layout is None or (
                row.query_key[:1] == keys[:1] if table_type == 19 else row.query_key == keys
            )
        )

    def query(self, table_type: int, *keys: int, ecu_id: int = 0, family: str | None = None) -> NativeQueryResult:
        expected = 2 if table_type in (18, 19, 25) else 1
        if table_type not in (*_INDEX_LAYOUTS, 19):
            return NativeQueryResult(None, mode="unproved-layout", raw_variants=self.raw_records(table_type, ecu_id=ecu_id, family=family))
        if len(keys) != expected or any(not isinstance(key, int) or not 0 <= key <= 0xFFFFFFFF for key in keys):
            return NativeQueryResult(0xA0030102)
        if table_type == 16 and keys[0] > 0xFFFF:
            return NativeQueryResult(0xA0030102)
        if family is not None and family not in ("Gen", "Spe"):
            return NativeQueryResult(0xA0030102)
        if not self.history_known:
            selected_family = family or ("Gen" if table_type == 16 else None)
            return NativeQueryResult(
                None, mode="unresolved-history",
                provenance=({"table_type": table_type, "keys": list(keys), "context": self.as_dict()},),
                raw_variants=self._raw_candidates(table_type, keys, ecu_id, selected_family),
            )
        if family is not None:
            return self._query_family(table_type, keys, ecu_id, family)
        gen = self._query_family(table_type, keys, ecu_id, "Gen")
        if table_type == 16 or gen.status not in (0, *_TOLERATED_MISSING):
            return gen
        return merge_native_results(table_type, gen, self._query_family(table_type, keys, ecu_id, "Spe"))

    def ecu_file_category(self, ecu_id: int, family: str) -> NativeQueryResult:
        loaded = self.file(family=family)
        if loaded is None:
            return NativeQueryResult(0xA0030103)
        result = self.query(16, ecu_id, family=family)
        if result.status == 0xA0030107:
            return NativeQueryResult(0xA0030106, provenance=result.provenance)
        if result.status == 0 and not result.records:
            return NativeQueryResult(0xA0030104, provenance=result.provenance)
        return NativeQueryResult(result.status, result.records[:1], result.mode, result.provenance, result.raw_variants)

    def correspondence_reflection(
        self, ecu_id: int, handling_id: int, *,
        table_statuses: dict[str, dict[int | str, int]] | None = None,
    ) -> NativeQueryResult:
        if not 0 <= ecu_id <= 0xFFFF or not 0 < handling_id <= 0xFFFF:
            return NativeQueryResult(0xA0030102)
        family_statuses: list[int | None] = []
        details = []
        any_loaded = False
        for family in ("Gen", "Spe"):
            loaded = self.file(ecu_id=ecu_id, family=family)
            if loaded is None:
                family_statuses.append(0)  # Native locals start at zero for absent objects.
                continue
            any_loaded = True
            applied = loaded.apply_handling(handling_id)
            statuses = (table_statuses or {}).get(loaded.source.identity, (table_statuses or {}).get(loaded.source.path, {}))
            terminal: int | None = 0
            unproved = []
            derived = []
            for table in sorted(loaded.catalog):
                if table in loaded._active:
                    terminal = 0
                else:
                    terminal = statuses.get(table, statuses.get(str(table)))
                    if terminal is None:
                        proof = loaded.proved_mutation_status(table)
                        if proof is not None:
                            terminal = proof["status"]
                            derived.append(proof)
                        else:
                            unproved.append(table)
            family_statuses.append(terminal)
            details.append({"source": loaded.source.as_dict(), "load_id": loaded.load_id,
                            "applied_occurrence_ids": applied, "unproved_table_statuses": unproved,
                            "derived_table_statuses": derived,
                            "terminal_status": terminal})
        if not any_loaded:
            status = 0xA0030106
        elif 0 in family_statuses:
            status = 0
        elif family_statuses[0] is None or family_statuses[1] is None:
            status = None
        else:
            gen_status, spe_status = family_statuses
            if gen_status is None or spe_status is None:
                raise ValueError("unresolved reflection status")
            status = select_native_status(gen_status, spe_status)
        event = {"ecu_id": ecu_id, "handling_id": handling_id, "event_index": len(self.events),
                 "status": status, "files": details}
        self.events.append(event)
        return NativeQueryResult(status, mode="reflection", provenance=(event,))

    def as_dict(self) -> dict[str, Any]:
        return {
            "history_known": self.history_known,
            "resolution": "unknown" if not self.history_known else "event-history" if self.events else "initial",
            "files": [{"source": loaded.source.as_dict(), "ecu_id": loaded.ecu_id, "load_id": loaded.load_id}
                      for loaded in self._files.values()],
            "loads": list(self.loads), "events": list(self.events),
        }


def native_context(master: ECUDataBase | NativeSelectionContext, spe_master: ECUDataBase | None = None) -> NativeSelectionContext:
    if isinstance(master, NativeSelectionContext):
        if spe_master is not None:
            raise ValueError("load additional files explicitly into the existing context")
        return master
    context = NativeSelectionContext()
    context.load(master)
    if spe_master is not None:
        context.load(spe_master)
    return context


def query_native_records(context: NativeSelectionContext, class_id: int, *keys: int, ecu_id: int = 0) -> NativeQueryResult:
    if class_id not in (0x110, 0x111, 0x112, 0x113, 0x119, 0x11D):
        return NativeQueryResult(0xA0030102)
    return context.query(class_id - 0x100, *keys, ecu_id=ecu_id)


@overload
def select_for_consumer(result: NativeQueryResult, consumer: Literal["selector"], *, timer_policy: str = "exactly-one") -> tuple[NativeOccurrence, ...]: ...


@overload
def select_for_consumer(
    result: NativeQueryResult,
    consumer: Literal["commset", "plugin", "frame", "timer", "category", "read_ecu_file"],
    *, timer_policy: str = "exactly-one",
) -> NativeOccurrence: ...


@overload
def select_for_consumer(result: NativeQueryResult, consumer: str, *, timer_policy: str = "exactly-one") -> NativeOccurrence | tuple[NativeOccurrence, ...]: ...


def select_for_consumer(result: NativeQueryResult, consumer: str, *, timer_policy: str = "exactly-one") -> NativeOccurrence | tuple[NativeOccurrence, ...]:
    result.require_success()
    rows = result.records
    if consumer == "commset":
        if len(rows) != 1:
            raise NativeSelectionError(0xC0040102, result)
    elif consumer in ("selector", "plugin", "frame", "timer", "category", "read_ecu_file"):
        if not rows:
            raise NativeSelectionError(0xA0030104 if consumer == "read_ecu_file" else 0xC0040101, result)
        if consumer == "timer":
            if timer_policy not in ("exactly-one", "report-and-continue"):
                raise ValueError(f"unknown timer consumer policy: {timer_policy}")
            if timer_policy == "exactly-one" and len(rows) != 1:
                raise NativeSelectionError(0xC0040102, result)
    else:
        raise ValueError(f"unknown native consumer: {consumer}")
    return rows if consumer == "selector" else rows[0]


def native_variable(context: NativeSelectionContext, occurrence: NativeOccurrence, variable_id: int, *, namespace_base: int = 0x2710) -> dict[str, Any]:
    normalized = variable_id - namespace_base if namespace_base and variable_id > namespace_base else variable_id
    if variable_id == 0:
        payload = b""
    else:
        database = context.database_for(occurrence)
        section = database.sections.get(0)
        if section is None or not 1 <= normalized <= section.header.record_count:
            raise NativeSelectionError(0xC0040102)
        payload = next(row.raw for row in section.iter_records() if row.index == normalized - 1)
    return {"id": f"0x{variable_id:X}", "normalized_id": f"0x{normalized:X}", "bytes": payload.hex()}


def exception_event_metadata(row: NativeOccurrence) -> dict[str, Any]:
    """Decode proved event inputs, without synthesizing probe results/events."""
    if row.source.format_version != 1 or row.source.schema_family not in ("gtsplus", "ds4"):
        raise UnresolvedNativeContext("event layout is established only for current master sources")
    if row.table_type == 4 and len(row.raw) == 20:
        return {
            "query_keys": [row.u16(4), row.u16(6)], "frame": row.u16(8),
            "support_selector": row.u16(10), "commset": row.u16(12),
            "emitted_handling_id": row.u16(14), "condition_mode": row.raw[18],
            "required_response_length": row.raw[19], "occurrence": row.as_dict(),
        }
    if row.table_type == 58 and len(row.raw) >= 19:
        return {
            "query_keys": [row.u16(4), row.raw[16], row.u16(6)],
            "target_ecu": row.u16(4), "frame": row.u16(8), "support_selector": row.u16(10),
            "commset": row.u16(12), "emitted_handling_id": row.u16(14),
            "condition_mode": row.raw[17], "required_response_length": row.raw[18],
            "occurrence": row.as_dict(),
        }
    raise UnresolvedNativeContext(f"unproved event layout: {row.identity}")


def native_commset(row: NativeOccurrence) -> dict[str, Any]:
    return {
        "comm_set_id": row.u16(10), "send_parameter": struct.unpack_from("<I", row.raw, 0)[0],
        "receive_timeout": struct.unpack_from("<I", row.raw, 4)[0],
        "exception_handler_id": row.u16(8), "unknown_word_0c": row.u16(12),
        "retry_count": row.raw[14], "exception_handler_flag": row.raw[15],
        "raw": row.raw.hex(), "occurrence": row.as_dict(),
    }


def resolve_frame_program(context: NativeSelectionContext, category_id: int, selector: int, *, variable_namespace_base: int = 0) -> list[dict[str, Any]]:
    selectors = context.query(18, category_id, selector)
    selected = select_for_consumer(selectors, "selector")
    if not isinstance(selected, tuple):
        raise ValueError("selector consumer must retain its complete program")
    commset_id = selected[0].u16(4)
    frames = []
    for row in selected:
        commsets = context.query(29, commset_id)
        commset = select_for_consumer(commsets, "commset")
        frame_id = row.u16(6)
        frame_query = context.query(17, frame_id)
        frame = select_for_consumer(frame_query, "frame")
        if isinstance(commset, tuple) or isinstance(frame, tuple):
            raise ValueError("record0 consumers must return one occurrence")
        send, mask, check = (
            native_variable(context, frame, frame.u16(offset), namespace_base=variable_namespace_base)
            for offset in (2, 4, 6)
        )
        if not send["bytes"]:
            raise NativeSelectionError(0xC0040102, frame_query)
        frames.append({
            "kind": "frame", "category_id": category_id, "selector": f"0x{selector:X}",
            "comm_set": commset_id, "comm_set_metadata": native_commset(commset),
            "comm_frame_id": f"0x{frame_id:X}", "send": send, "receive_mask": mask, "receive_check": check,
            "func_comm_frame_raw": row.raw.hex(), "comm_frame_raw": frame.raw.hex(),
            "selection": {"selector_query": selectors.as_dict(), "frame_query": frame_query.as_dict(),
                          "commset_query": commsets.as_dict(), "selector_occurrence": row.as_dict(),
                          "frame_occurrence": frame.as_dict(), "commset_occurrence": commset.as_dict(),
                          "context": context.as_dict()},
        })
    return frames


@dataclass(frozen=True)
class MonitorRecord:
    table: int
    index: int
    name_string_index: int
    flags: int
    monitor_key: int
    ffd_support_condition_key: int
    physical_data_key: int
    bit_start: int
    bit_end: int
    pattern_display_key: int
    primary_did: int
    alternate_did: int
    sort_key: int
    raw: bytes


@dataclass(frozen=True)
class BehaviorRecord:
    table: int
    index: int
    signature: str
    name_string_index: int
    comment_string_index: int
    behavior_code: int
    raw: bytes


@dataclass(frozen=True)
class RobSignalRecord:
    table: int
    index: int
    name_string_index: int
    record_key: int
    support_condition_key: int
    physical_data_key: int
    bit_start: int
    bit_end: int
    sort_key: int
    pattern_display_key: int
    exception_handler_id: int
    did: int
    extraction_mode: int
    presentation_mode: int
    exception_handler_flag: int
    raw: bytes


def extract_msb0(payload: bytes, bit_start: int, bit_end: int) -> int:
    """Extract a Toyota Data Monitor bit range (inclusive, MSB-first per byte)."""
    if bit_start < 0 or bit_end < bit_start:
        raise ValueError(f"invalid bit range {bit_start}..{bit_end}")
    if bit_end >= len(payload) * 8:
        raise ValueError(f"bit range {bit_start}..{bit_end} exceeds {len(payload)}-byte payload")
    start_byte = bit_start >> 3
    end_byte = bit_end >> 3
    assembled = int.from_bytes(payload[start_byte:end_byte + 1], "big")
    shift = 7 - (bit_end & 7)
    width = bit_end - bit_start + 1
    return (assembled >> shift) & ((1 << width) - 1)


def _trunc_div_toward_zero(numerator: int, denominator: int) -> int:
    if denominator == 0:
        raise ZeroDivisionError("Toyota physical conversion divisor is zero")
    quotient = abs(numerator) // abs(denominator)
    return -quotient if (numerator < 0) != (denominator < 0) else quotient


def convert_p5_physical(raw: int, *, bit_width: int, signed: bool, mul: int, div: int, offset: int) -> int:
    """Apply ordinary P5 CCmdConversionTbl/CComDataConvert integer semantics."""
    if bit_width <= 0:
        raise ValueError(f"invalid bit width {bit_width}")
    mask = (1 << bit_width) - 1
    value = raw & mask
    if signed and value & (1 << (bit_width - 1)):
        value -= 1 << bit_width
    numerator = value * mul
    converted = numerator if div <= 1 else _trunc_div_toward_zero(numerator, div)
    return converted + offset


def format_p5_decimal(converted_integer: int, decimal_point_count: int) -> str:
    """Render Techstream's integer graph value with its DDB decimal precision."""
    if decimal_point_count < 0:
        raise ValueError(f"invalid decimal point count {decimal_point_count}")
    if decimal_point_count == 0:
        return str(converted_integer)
    scale = 10 ** decimal_point_count
    magnitude = abs(converted_integer)
    whole, fraction = divmod(magnitude, scale)
    sign = "-" if converted_integer < 0 else ""
    return f"{sign}{whole}.{fraction:0{decimal_point_count}d}"


def decode_p5_signal(
    payload: bytes,
    *,
    bit_start: int,
    bit_end: int,
    mul: int,
    div: int,
    offset: int,
    signed: bool,
    decimal_point_count: int,
    patterns: dict[int, str | None] | None = None,
) -> dict[str, Any]:
    """Decode one ordinary current-P5 Data Monitor signal from its DID value payload."""
    raw = extract_msb0(payload, bit_start, bit_end)
    converted = convert_p5_physical(
        raw,
        bit_width=bit_end - bit_start + 1,
        signed=signed,
        mul=mul,
        div=div,
        offset=offset,
    )
    pattern = (patterns or {}).get(converted)
    return {
        "raw": raw,
        "converted_integer": converted,
        "value": format_p5_decimal(converted, decimal_point_count),
        "pattern": pattern,
    }


def extract_monitor_records(section: Any) -> list[MonitorRecord]:
    table = int(section.header.table_type)
    if table not in {62, 157}:
        raise ValueError(f"expected monitor table 62/157, got {table}")
    size = int(section.decoded_record_size)
    shift = 0x10 if size >= 0x50 else 0
    if size < 0x3A + shift:
        raise ValueError(f"monitor table {table} record size too small: 0x{size:X}")
    out = []
    for index, raw in enumerate(records(section)):
        u16 = lambda off: struct.unpack_from("<H", raw, off)[0]
        u32 = lambda off: struct.unpack_from("<I", raw, off)[0]
        out.append(MonitorRecord(
            table=table,
            index=index,
            name_string_index=u32(0x18 + shift),
            flags=raw[0x20 + shift],
            monitor_key=u16(0x24 + shift),
            ffd_support_condition_key=u16(0x28 + shift),
            physical_data_key=u16(0x2A + shift),
            bit_start=u16(0x2C + shift),
            bit_end=u16(0x2E + shift),
            pattern_display_key=u16(0x32 + shift),
            primary_did=u16(0x36 + shift),
            alternate_did=u16(0x38 + shift),
            sort_key=u16(0x30 + shift),
            raw=raw,
        ))
    return out


def extract_behavior_records(section: Any) -> list[BehaviorRecord]:
    table = int(section.header.table_type)
    if table != 87 or section.decoded_record_size < 20:
        raise ValueError(f"expected behavior table 87 with >=20-byte rows, got {table}/{section.decoded_record_size}")
    out = []
    for index, raw in enumerate(records(section)):
        out.append(BehaviorRecord(
            table=87,
            index=index,
            signature=raw[:12].decode("utf-16-le", errors="replace").split("\x00", 1)[0],
            name_string_index=struct.unpack_from("<I", raw, 0x0C)[0],
            comment_string_index=struct.unpack_from("<I", raw, 0x10)[0],
            behavior_code=struct.unpack_from("<H", raw, 0x14)[0],
            raw=raw,
        ))
    return out


def extract_rob_signal_records(section: Any) -> list[RobSignalRecord]:
    table = int(section.header.table_type)
    size = int(section.decoded_record_size)
    if table != 88 or size < 0x43:
        raise ValueError(f"expected current behavior-data table 88 with >=0x43-byte rows, got {table}/0x{size:X}")
    out = []
    for index, raw in enumerate(records(section)):
        u16 = lambda off: struct.unpack_from("<H", raw, off)[0]
        u32 = lambda off: struct.unpack_from("<I", raw, off)[0]
        out.append(RobSignalRecord(
            table=88,
            index=index,
            name_string_index=u32(0x20),
            record_key=u16(0x2C),
            support_condition_key=u16(0x2E),
            physical_data_key=u16(0x30),
            bit_start=u16(0x32),
            bit_end=u16(0x34),
            sort_key=u16(0x36),
            pattern_display_key=u16(0x38),
            exception_handler_id=u16(0x3A),
            did=u16(0x3C),
            extraction_mode=raw[0x3E],
            presentation_mode=raw[0x3F],
            exception_handler_flag=raw[0x42],
            raw=raw,
        ))
    return out


def _physical_info(
    db: Any, strings: Any, *, physical_data_key: int, bit_start: int, bit_end: int,
    pattern_display_key: int,
) -> dict[str, Any] | None:
    physical_section = db.sections.get(13)
    unit_section = db.sections.get(15)
    if physical_section is None or unit_section is None:
        return None
    physical = next((raw for raw in records(physical_section)
                     if len(raw) >= 0x16 and struct.unpack_from("<H", raw, 0x0C)[0] == physical_data_key), None)
    if physical is None:
        return None
    unit_key = struct.unpack_from("<H", physical, 0x0E)[0]
    unit = next((raw for raw in records(unit_section)
                 if len(raw) >= 8 and struct.unpack_from("<H", raw, 0x04)[0] == unit_key), None)
    unit_text = None if unit is None else strings.get_string(struct.unpack_from("<I", unit, 0x00)[0])
    patterns: dict[int, str | None] = {}
    pattern_section = db.sections.get(14)
    if pattern_section is not None and pattern_display_key:
        for raw in records(pattern_section):
            if len(raw) >= 0x0E and struct.unpack_from("<H", raw, 0x0C)[0] == pattern_display_key:
                patterns[struct.unpack_from("<I", raw, 0x04)[0]] = strings.get_string(struct.unpack_from("<I", raw, 0x00)[0])
    return {
        "physical_data_key": physical_data_key,
        "mul": struct.unpack_from("<i", physical, 0x00)[0],
        "div": struct.unpack_from("<i", physical, 0x04)[0],
        "offset": struct.unpack_from("<i", physical, 0x08)[0],
        "unit_key": unit_key,
        "unit": unit_text,
        "signed": bool(physical[0x14]),
        "decimal_point_count": physical[0x15],
        "bit_width": bit_end - bit_start + 1,
        "pattern_display": dict(sorted(patterns.items())),
    }


def _signal_info(db: Any, strings: Any, record: MonitorRecord) -> dict[str, Any] | None:
    info = _physical_info(
        db, strings,
        physical_data_key=record.physical_data_key,
        bit_start=record.bit_start,
        bit_end=record.bit_end,
        pattern_display_key=record.pattern_display_key,
    )
    if info is None:
        return None
    shift = 0x10 if len(record.raw) >= 0x50 else 0
    info.update({
        "data_range": [
            struct.unpack_from("<i", record.raw, 0x10 + shift)[0],
            struct.unpack_from("<i", record.raw, 0x0C + shift)[0],
        ],
        "graph_range": [
            struct.unpack_from("<i", record.raw, 0x08 + shift)[0],
            struct.unpack_from("<i", record.raw, 0x04 + shift)[0],
        ],
    })
    return info


def monitor_rows(
    db: Any,
    strings: Any,
    source: str,
    *,
    deduplicate: bool = True,
    include_signal_info: bool = False,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for table in (62, 157):
        section = db.sections.get(table)
        if section is None:
            continue
        for record in extract_monitor_records(section):
            row = {
                "kind": "did",
                "source": source,
                "table": table,
                "tables": [table],
                "record": record.index,
                "name": strings.get_string(record.name_string_index),
                "flags": record.flags,
                "monitor_key": record.monitor_key,
                "ffd_support_condition_key": record.ffd_support_condition_key,
                "physical_data_key": record.physical_data_key,
                "bit_start": record.bit_start,
                "bit_end": record.bit_end,
                "pattern_display_key": record.pattern_display_key,
                "primary_did": record.primary_did,
                "alternate_did": record.alternate_did,
                "sort_key": record.sort_key,
                "raw": record.raw,
            }
            if include_signal_info:
                row["signal_info"] = _signal_info(db, strings, record)
            rows.append(row)
    if not deduplicate:
        return rows
    by_identity: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        identity = (row["name"], row["primary_did"], row["alternate_did"])
        existing = by_identity.get(identity)
        if existing is None:
            by_identity[identity] = row
        elif row["table"] not in existing["tables"]:
            existing["tables"].append(row["table"])
    return list(by_identity.values())


def _data_id_modes(section: Any | None) -> dict[int, int]:
    out: dict[int, int] = {}
    if section is None:
        return out
    for raw in records(section):
        if len(raw) >= 7:
            out[struct.unpack_from("<H", raw, 0x02)[0]] = raw[0x06]
    return out


def _ffd_conditions(
    section: Any | None,
    resolve_variable: Callable[[int], bytes],
) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    if section is None:
        return out
    for raw in records(section):
        if len(raw) < 12:
            raise ValueError(f"FFD condition table 80 row too small: {len(raw)}")
        key = struct.unpack_from("<H", raw, 0x00)[0]
        variable_id = struct.unpack_from("<H", raw, 0x02)[0]
        variable = resolve_variable(variable_id)
        if len(variable) < 2:
            raise ValueError(f"FFD condition {key} variable {variable_id} has no referenced DID")
        if key in out:
            raise ValueError(f"duplicate FFD condition key {key}")
        out[key] = {
            "key": key,
            "variable_id": variable_id,
            "referenced_did": int.from_bytes(variable[:2], "big"),
            "bit_start": struct.unpack_from("<H", raw, 0x06)[0],
            "bit_end": struct.unpack_from("<H", raw, 0x08)[0],
            "condition_type": raw[0x0B],
        }
    return out


def ffd_rows(
    db: Any,
    strings: Any,
    source: str,
    *,
    resolve_variable: Callable[[int], bytes],
    include_signal_info: bool = False,
) -> dict[str, Any]:
    """Current ordinary-P5 generic FFD signal schema used by GetEachFrzFrmDatP5.

    The host selects monitor rows whose FFD-membership bit (+0x30 & 0x02 in the
    current 80-byte row) is set and whose alternate/SSR DID (+0x48) matches the
    returned snapshot DID. Type 61 supplies the local support mode. A nonzero
    +0x38 support key resolves through type 80 to another DID/bit condition from
    the same snapshot record.
    """
    did_modes = _data_id_modes(db.sections.get(61))
    conditions = _ffd_conditions(db.sections.get(80), resolve_variable)
    dynamic_lsb = 64 in db.sections
    rows: list[dict[str, Any]] = []
    for table in (62, 157):
        section = db.sections.get(table)
        if section is None:
            continue
        for record in extract_monitor_records(section):
            if not (record.flags & 0x02):
                continue
            condition = None
            if record.ffd_support_condition_key:
                condition = conditions.get(record.ffd_support_condition_key)
                if condition is None:
                    raise ValueError(
                        f"FFD monitor key {record.monitor_key} references missing condition "
                        f"{record.ffd_support_condition_key}"
                    )
            row: dict[str, Any] = {
                "source": source,
                "table": table,
                "record": record.index,
                "name": strings.get_string(record.name_string_index),
                "monitor_key": record.monitor_key,
                "flags": record.flags,
                "snapshot_did": record.alternate_did,
                "primary_did": record.primary_did,
                "physical_data_key": record.physical_data_key,
                "bit_start": record.bit_start,
                "bit_end": record.bit_end,
                "sort_key": record.sort_key,
                "pattern_display_key": record.pattern_display_key,
                "local_support_mode": did_modes.get(record.alternate_did),
                "support_condition": condition,
                "dynamic_lsb_possible": dynamic_lsb,
                "raw": record.raw,
            }
            if include_signal_info:
                row["signal_info"] = _physical_info(
                    db, strings,
                    physical_data_key=record.physical_data_key,
                    bit_start=record.bit_start,
                    bit_end=record.bit_end,
                    pattern_display_key=record.pattern_display_key,
                )
            rows.append(row)
    by_identity: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        identity = (row["name"], row["snapshot_did"], row["monitor_key"])
        existing = by_identity.get(identity)
        if existing is None:
            by_identity[identity] = row
        elif row["table"] != existing["table"]:
            existing.setdefault("tables", [existing["table"]]).append(row["table"])
    return {
        "signals": list(by_identity.values()),
        "condition_count": len(conditions),
        "dynamic_lsb_table_present": dynamic_lsb,
    }


def dtc_rows(parser: DDBParser, db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    legacy = db.sections.get(5)
    if legacy is not None:
        for index, raw in enumerate(records(legacy)):
            if len(raw) != 28:
                raise ValueError(f"table 5: expected 28-byte DTC record, got {len(raw)}")
            description_index, comment_index = struct.unpack_from("<II", raw, 12)
            rows.append({
                "kind": "dtc", "source": source, "table": 5, "record": index,
                "code": raw[:12].decode("utf-16-le").rstrip("\x00"),
                "dtc_identifier": struct.unpack_from("<H", raw, 20)[0],
                "description": strings.get_string(description_index),
                "comment": strings.get_string(comment_index),
                "raw": raw,
            })
    section = db.sections.get(65)
    if section is None:
        return rows
    rows.extend({
        "kind": "dtc",
        "source": source,
        "table": 65,
        "record": index,
        "code": entry.code,
        "packed_dtc": f"0x{entry.packed_dtc:06X}",
        "description": strings.get_string(entry.description_string_index),
        "failure": strings.get_string(entry.failure_string_index),
        "raw": entry.raw,
    } for index, entry in enumerate(parser.extract_dtc_failure_entries(section)))
    return rows


def behavior_rows(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    section = db.sections.get(87)
    if section is None:
        return []
    return [{
        "kind": "behavior",
        "source": source,
        "table": 87,
        "record": record.index,
        "signature": record.signature,
        "name": strings.get_string(record.name_string_index),
        "comment": strings.get_string(record.comment_string_index),
        "behavior_code": record.behavior_code,
        "raw": record.raw,
    } for record in extract_behavior_records(section)]



def rob_rows(db: Any, strings: Any, source: str, *, include_signal_info: bool = False) -> dict[str, Any]:
    """Decode current ordinary-P5 RoB behavior names and DID-scoped signal schemas.

    Type-88 rows are selected by returned DID at runtime. Type-90 supplies the local
    support mode; type-89 is represented as an explicit cross-DID key when present.
    Type-64 presence is exported explicitly. The same-release unprotected 2026
    CommandCommon body closes ChangeSignalLSB; ordinary current-P5 RoB catalogs in
    NA/EU/JP do not carry type 64, so their base physical coefficients are final.
    """
    behavior = behavior_rows(db, strings, source)
    signal_section = db.sections.get(88)
    if signal_section is None:
        return {"behavior_codes": behavior, "signals": [], "dynamic_lsb_table_present": 64 in db.sections}

    did_modes: dict[int, int] = {}
    section90 = db.sections.get(90)
    if section90 is not None:
        for raw in records(section90):
            if len(raw) >= 7:
                did_modes[struct.unpack_from("<H", raw, 0x02)[0]] = raw[0x06]

    dynamic_keys: set[int] = set()
    section64 = db.sections.get(64)
    if section64 is not None:
        # Same-release 2026 CommandCommon closes ChangeSignalLSB. Current ordinary
        # P5 RoB catalogs have no type-64 rows, but preserve this flag for categories
        # outside that presently observed surface.
        dynamic_keys = {-1}

    signals = []
    for record in extract_rob_signal_records(signal_section):
        row: dict[str, Any] = {
            "source": source,
            "table": 88,
            "record": record.index,
            "name": strings.get_string(record.name_string_index),
            "record_key": record.record_key,
            "support_condition_key": record.support_condition_key,
            "physical_data_key": record.physical_data_key,
            "bit_start": record.bit_start,
            "bit_end": record.bit_end,
            "sort_key": record.sort_key,
            "pattern_display_key": record.pattern_display_key,
            "exception_handler_id": record.exception_handler_id,
            "did": record.did,
            "extraction_mode": record.extraction_mode,
            "presentation_mode": record.presentation_mode,
            "exception_handler_flag": record.exception_handler_flag,
            "local_support_mode": did_modes.get(record.did),
            "dynamic_lsb_possible": bool(dynamic_keys),
            "raw": record.raw,
        }
        if include_signal_info:
            row["signal_info"] = _physical_info(
                db, strings,
                physical_data_key=record.physical_data_key,
                bit_start=record.bit_start,
                bit_end=record.bit_end,
                pattern_display_key=record.pattern_display_key,
            )
        signals.append(row)
    return {
        "behavior_codes": behavior,
        "signals": signals,
        "dynamic_lsb_table_present": 64 in db.sections,
        "cross_did_condition_rows": db.sections[89].header.record_count if 89 in db.sections else 0,
    }
