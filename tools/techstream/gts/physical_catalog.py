"""Independent physical, unit and enum source definitions, including unused rows.

KgpDataCtrl: PhyData GetRecordAddress100bf580/exception100bf5a0/100bf5e0;
PatDisp GetRecordAddress100be1c0/exception100be200/100be240 and
ComparativeKey100be280 (key12/value4); Unit GetRecordAddress100d20a0,
exception100d20e0/100d2120. SetRecString100bdaf0/100d1ae0 pins string0.
Conversion operands are consumed by native GetDatMonSignalInfo and
CommandDataLib GetValue10022ac0, implemented in native_conversion.
"""
from __future__ import annotations

import struct
from typing import Any
from tools.techstream.ddb_semantics import records


def physical_catalog(db: Any, strings: Any, source: str) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {"physical": [], "patterns": [], "units": []}
    for table, size, collection in ((13, 24, "physical"), (14, 24, "patterns"), (15, 12, "units")):
        section = db.sections.get(table)
        if section is None:
            continue
        if section.decoded_record_size != size:
            raise ValueError(f"table{table}: expected{size}-byte rows, got{section.decoded_record_size}")
        for index, raw in enumerate(records(section)):
            u16 = lambda offset: struct.unpack_from("<H", raw, offset)[0]
            row: dict[str, Any] = {"source": source, "table": table, "record": index, "raw": raw.hex()}
            if table == 13:
                mul, div, offset = struct.unpack_from("<iii", raw)
                row.update(key=u16(12), unit_key=u16(14), mul=mul, div=div, offset=offset,
                           sign_mode=raw[20], decimal_point_count=raw[21],
                           exception_handler_id=u16(16), exception_handler_flag=raw[22],
                           unassigned_fields={"18_19": raw[18:20].hex(), "23": raw[23]})
            else:
                string_id = struct.unpack_from("<I", raw)[0]
                row.update(name_string_index=string_id, name=strings.get_string(string_id))
                if table == 14:
                    row.update(key=u16(12), value=struct.unpack_from("<i", raw, 4)[0],
                               exception_handler_id=u16(16), exception_handler_flag=raw[23],
                               unassigned_fields={"8_11": raw[8:12].hex(), "14_15": raw[14:16].hex(),
                                                  "18_22": raw[18:23].hex()})
                else:
                    row.update(key=u16(4), genre_id=u16(6),
                               exception_handler_id=u16(8), exception_handler_flag=raw[10],
                               unassigned_fields={"11": raw[11]})
            result[collection].append(row)
    return result
