"""Native-used DTC source metadata, without dropping disabled definitions.

GTS+ KgpDataCtrl: FindDbItem1 100A8A30/100A7FF0; exception accessors
100A8B80/100A8BC0 and 100A8140/100A8180; string joins100A8360/100A7730.
GetDiagCodeInfo_DT100013C0 selects table5 enabled byte+26 and detail47
by DTC identifier;10001800 selects table65 enabled byte+64 and copies
byte+65/word+62 to CCmdDiagCodeInfo+34/+36. CommandDataLib10010100
serializes these with widths1/2. Their business labels are not guessed.
"""
from __future__ import annotations
import struct
from typing import Any
from tools.techstream.ddb_semantics import records


def dtc_source_catalog(db: Any, strings: Any, source: str) -> list[dict[str, Any]]:
    """Return all table5/65 rows, retaining native filters as metadata."""
    rows=[]
    for table,size in ((5,28),(65,68)):
        section=db.sections.get(table)
        if section is None:
            continue
        if section.header.record_count and section.decoded_record_size != size:
            raise ValueError(f"DTC table {table}: expected {size}-byte records, got {section.decoded_record_size}")
        for index,raw in enumerate(records(section)):
            def u16(offset): return struct.unpack_from("<H",raw,offset)[0]
            def u32(offset): return struct.unpack_from("<I",raw,offset)[0]
            name_offset,comment_offset=(12,16) if table==5 else (48,56)
            name_index,comment_index=u32(name_offset),u32(comment_offset)
            enabled=raw[26 if table==5 else 64]
            row={"source":source,"table":table,"record":index,"raw":raw.hex(),
                 "code":raw[:12 if table==5 else 44].decode("utf-16le").split("\0",1)[0],
                 "description_string_index":name_index,"description":strings.get_string(name_index),
                 "comment_string_index":comment_index,"comment":strings.get_string(comment_index),
                 "enabled_value":enabled,"enabled":enabled!=0,
                 "exception_handler_id":u16(22 if table==5 else 60),
                 "exception_handler_flag":raw[27 if table==5 else 66]}
            if table==5:
                row.update(dtc_identifier=u16(20),detail_table=47,detail_lookup_key=u16(20),
                           unconsumed_descriptor_offsets=[24,25])
            else:
                packed=u32(44)
                row.update(packed_dtc=packed,base_dtc=(packed>>8)&0xffff,failure_type=packed&0xff,
                           failure_string_index=u32(52),failure_description=strings.get_string(u32(52)),
                           diag_code_info_fields=[
                               {"source_offset":65,"output_offset":52,"width":1,"value":raw[65]},
                               {"source_offset":62,"output_offset":54,"width":2,"value":u16(62)}])
            rows.append(row)
    return rows
