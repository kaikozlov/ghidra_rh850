"""Derived module-local physical lookups; no persisted monitor associations."""

from functools import lru_cache
import struct


def load_library(db, module_id, source_id):
    physical = {}
    units = {}
    patterns = {}
    seen = set()
    for identity, table, ordinal, raw in db.execute(
        """
      SELECT v.id,r.table_type,r.ordinal,r.raw FROM ecu_records r
      JOIN physical_record_views v ON v.record_id=r.id
       AND v.source_name_id=? AND v.projection=0
      WHERE r.module_id=? AND r.table_type IN(13,14,15)
      ORDER BY r.table_type,r.ordinal""",
        (source_id, module_id),
    ):
        if (table, ordinal) in seen:
            raise ValueError("ambiguous physical source view")
        seen.add((table, ordinal))
        size = {13: 24, 14: 24, 15: 12}[table]
        if len(raw) != size:
            raise ValueError("invalid physical source layout")
        u16 = lambda off: struct.unpack_from("<H", raw, off)[0]
        if table == 13:
            physical.setdefault(u16(12), []).append((ordinal, identity, u16(14)))
        elif table == 14:
            patterns.setdefault(u16(12), []).append((ordinal, identity))
        else:
            units.setdefault(u16(4), []).append((ordinal, identity))
    return physical, units, patterns


@lru_cache(maxsize=8)
def _cached_library(db, module_id, source_id, change_counter):
    # Bound both context count and records per retained context. Large future
    # source modules remain supported but are not retained in this cache.
    library = load_library(db, module_id, source_id)
    count = sum(len(rows) for group in library for rows in group.values())
    return library if count <= 8192 else None


def cached_library(db, module_id, source_id, change_counter):
    # Reader connections are immutable. Counter isolates deliberate test writes.
    found = _cached_library(db, module_id, source_id, change_counter)
    return found if found is not None else load_library(db, module_id, source_id)


cached_library.cache_info = _cached_library.cache_info
cached_library.cache_clear = _cached_library.cache_clear


def children_for(table, raw, library):
    if table not in (62, 157, 88, 153):
        return ((), (), ())
    if len(raw) != (80 if table in (62, 157) else 72):
        raise ValueError("invalid monitor source layout")
    physical, units, patterns = library
    key = struct.unpack_from("<H", raw, 58 if table in (62, 157) else 48)[0]
    pattern = struct.unpack_from("<H", raw, 66 if table in (62, 157) else 56)[0]
    candidates = physical.get(key, ())
    # A unit source row appears once even if multiple physical candidates use it.
    unit_keys = {unit_key for _, _, unit_key in candidates}
    matches = sorted(row for k in unit_keys for row in units.get(k, ()))
    return (
        tuple(identity for _, identity, _ in candidates),
        tuple(identity for _, identity in matches),
        tuple(identity for _, identity in patterns.get(pattern, ())),
    )
