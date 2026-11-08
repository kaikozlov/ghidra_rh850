"""J1979-2/3 monitor readiness, result metadata and scaling.

Current KgpDataCtrl lookup/exception consumers: table160 100B9940/100B9A40/
100B9B80/100B9BC0;161 100B79F0/100B7AF0/100B7C30/100B7C70;
162 100A6840/100A6940/100A6A80/100A6AC0;170 100C7D70/100C7EB0/100C7EF0.
GetMonitorStatusInfo_DT 10002210/10002490 defines readiness bits and detail
joins. GetMonitorResultInfo_DT 10003190 joins DTC/scaling identifier to
table161, then table170 and unit15. Values and limits arrive from SID19.
Older result27/scaling29 and aliases143/144 retain distinct source identities.
GetMonitorResultInfo_DT 100016A0/100021A0 consumes CAN/ISO results; KgpDataCtrl
100B8630/100B8830 defines ISO's four-component selection predicate.
GetO2SData_DT 10001870/10001F00/100014E0 consumes oxygen sensor21 and monitor23;
CommandCommon 10069AA0/10069C10 consumes test22 lengths/support fields.
GetDatMonList_MultiPid_DT 100013B0/10001E00 requires all table26 dependencies.
Table24/25/34 currently expose native indexes/exceptions, not an invented
request decoder: no current consumer of their remaining fields was located.
Their unconsumed byte spans are explicit and remain a semantic coverage gap.
Alternative-source audit: V18 GetMonitorResultInfo Execute10001010 dispatches
to table28 (10001D40),27 (100028D0),143/144 (10003440), not24/25.
V18 KgpDataMonitorCtrl references25 only through record copy/destruction;
current GetMonitoringTestCARB 10001060 uses response analyzers, not24/25.
Across NA/EU/JP and PowerTrain_CARB/CAN_CARB all six copies are byte-identical:
table24 has six unique rows and table25 fourteen. This does NOT establish
that the fields are unused in every historical release. An older consuming
implementation or a format specification is needed to prove the other roles.
"""
from __future__ import annotations
import struct
from typing import Any
from tools.techstream.gts.legacy_freeze import extract_legacy_scalar, decode_legacy_scalar


def _rows(db: Any, table: int, size: int):
    if table not in db.sections:
        return
    for record in db.sections[table].iter_records():
        if len(record.raw) != size:
            raise ValueError(f"OBD table {table} row {record.index}: expected {size} bytes")
        yield record.index, record.raw


def obd_monitor_catalog(db: Any, strings: Any, source: str = "") -> dict[str, Any]:
    def u16(raw, offset):
        return struct.unpack_from("<H", raw, offset)[0]
    def u32(raw, offset):
        return struct.unpack_from("<I", raw, offset)[0]
    def base(table, index, raw):
        return {"source": source, "table": table, "record": index, "raw": raw.hex()}
    units = {}
    for index, raw in _rows(db, 15, 12):
        units.setdefault(u16(raw, 4), []).append({"record": index,
            "name_string_index": u32(raw, 0), "name": strings.get_string(u32(raw, 0))})
    links = [{
        **base(162, index, raw), "dtc": u32(raw, 0), "group_id": u16(raw, 4),
        "exception_id": u16(raw, 6), "exception_flag": raw[8],
        "unconsumed": raw[9:].hex(),
    } for index, raw in _rows(db, 162, 12)]
    status = []
    for index, raw in _rows(db, 160, 28):
        group = u16(raw, 16)
        status.append({
            **base(160, index, raw), "name_string_index": u32(raw, 0),
            "name": strings.get_string(u32(raw, 0)), "system_id": u16(raw, 4),
            "status_bit_start": u16(raw, 6), "status_bit_end": u16(raw, 8),
            "condition_bit_start": u16(raw, 10), "condition_bit_end": u16(raw, 12),
            "detail_group_id": group, "detail_links": [r for r in links if r["group_id"] == group] if group else [],
            "exception_id": u16(raw, 18), "did": u16(raw, 22),
            "status_enabled": raw[24], "condition_enabled": raw[25],
            "visibility_policy": raw[26], "exception_flag": raw[27],
            "response_offset": 3, "request_frame": 0x132,
            "unconsumed": {"offset14": raw[14:16].hex(), "offset20": raw[20:22].hex()},
        })
    scalings = []
    for index, raw in _rows(db, 170, 24):
        mul, div, offset = struct.unpack_from("<iii", raw)
        unit = u16(raw, 12)
        scalings.append({
            **base(170, index, raw), "scaling_id": u16(raw, 16),
            "mul": mul, "div": div, "offset": offset, "unit_key": unit,
            "units": units.get(unit, []), "sign_mode": raw[18], "decimal_point_count": raw[19],
            "bit_width": 16, "exception_id": u16(raw, 14), "exception_flag": raw[20],
            "unconsumed": raw[21:].hex(),
        })
    results = []
    for index, raw in _rows(db, 161, 24):
        scaling_id = u16(raw, 18)
        results.append({
            **base(161, index, raw), "name_string_index": u32(raw, 0),
            "name": strings.get_string(u32(raw, 0)), "help_id": u32(raw, 4),
            "dtc": u32(raw, 8), "result_id": u16(raw, 12),
            "scaling_id": scaling_id, "scalings": [s for s in scalings if s["scaling_id"] == scaling_id],
            "exception_id": u16(raw, 16), "exception_flag": raw[22],
            "visibility_policy": raw[20], "data_type": raw[21],
            "unconsumed": {"offset14": raw[14:16].hex(), "offset23": raw[23]},
        })
    old_links = [{
        **base(31, index, raw), "group_id": u16(raw, 0), "monitor_or_test_id": raw[4],
        "exception_id": u16(raw, 2), "exception_flag": raw[5], "unconsumed": raw[6:].hex(),
    } for index, raw in _rows(db, 31, 8)]
    old_status = []
    for index, raw in _rows(db, 30, 28):
        iso_group, can_group = u16(raw, 16), u16(raw, 18)
        old_status.append({
            **base(30, index, raw), "name_string_index": u32(raw, 0),
            "name": strings.get_string(u32(raw, 0)), "system_id": u16(raw, 4),
            "status_bit_start": u16(raw, 6), "status_bit_end": u16(raw, 8),
            "condition_bit_start": u16(raw, 10), "condition_bit_end": u16(raw, 12),
            "iso_detail_group_id": iso_group, "can_detail_group_id": can_group,
            "iso_detail_links": [r for r in old_links if r["group_id"] == iso_group] if iso_group else [],
            "can_detail_links": [r for r in old_links if r["group_id"] == can_group] if can_group else [],
            "exception_id": u16(raw, 20), "exception_flag": raw[26],
            "status_enabled": raw[22], "pid_kind": raw[23], "condition_enabled": raw[24],
            "visibility_policy": raw[25], "response_offset": 2,
            "unconsumed": {"offset14": raw[14:16].hex(), "offset27": raw[27]},
        })
    old_scalings = []
    for table, index, raw in ((table, index, raw) for table in (29, 144)
                              for index, raw in _rows(db, table, 20)):
        mul, div, offset = struct.unpack_from("<iii", raw)
        unit = u16(raw, 12)
        old_scalings.append({
            **base(table, index, raw), "scaling_id": raw[16],
            "mul": mul, "div": div, "offset": offset, "unit_key": unit,
            "units": units.get(unit, []), "sign_mode": raw[17], "decimal_point_count": raw[18],
            "bit_width": 16, "exception_id": u16(raw, 14), "exception_flag": raw[19],
        })
    patterns = {}
    for index, raw in _rows(db, 14, 24):
        patterns.setdefault(u16(raw, 12), []).append({**base(14, index, raw),
            "value": u32(raw, 4), "name_string_index": u32(raw, 0),
            "name": strings.get_string(u32(raw, 0))})
    old_results = []
    for table, index, raw in ((table, index, raw) for table in (27, 143)
                              for index, raw in _rows(db, table, 20)):
        scaling_id = raw[16]
        old_results.append({
            **base(table, index, raw), "name_string_index": u32(raw, 0),
            "name": strings.get_string(u32(raw, 0)), "help_id": u32(raw, 4),
            "result_id": u16(raw, 8), "pattern_key": u16(raw, 10),
            "patterns": patterns.get(u16(raw, 10), []) if u16(raw, 10) else [],
            "monitor_id": raw[14], "test_id": raw[15], "scaling_id": scaling_id,
            "scalings": [s for s in old_scalings if s["scaling_id"] == scaling_id
                         and s["table"] == (144 if table == 143 else 29)],
            "exception_id": u16(raw, 12), "exception_flag": raw[19],
            "visibility_policy": raw[17], "data_type": raw[18],
        })
    physical = {}
    for index, raw in _rows(db, 13, 24):
        key, unit = u16(raw, 12), u16(raw, 14)
        mul, div, offset = struct.unpack_from("<iii", raw)
        physical.setdefault(key, []).append({
            **base(13, index, raw), "physical_key": key, "mul": mul, "div": div, "offset": offset,
            "unit_key": unit, "units": units.get(unit, []), "sign_mode": raw[20],
            "decimal_point_count": raw[21], "bit_width": 16,
        })
    iso_results = []
    for index, raw in _rows(db, 28, 36):
        key, pattern_key = u16(raw, 14), u16(raw, 16)
        iso_results.append({
            **base(28, index, raw), "name_string_index": u32(raw, 4),
            "name": strings.get_string(u32(raw, 4)), "help_id": u32(raw, 8),
            "result_id": u16(raw, 12), "physical_key": key,
            "physical_records": physical.get(key, []), "pattern_key": pattern_key,
            "patterns": patterns.get(pattern_key, []) if pattern_key else [],
            "test_id": raw[22], "component_id": raw[23], "visibility_policy": raw[24],
            "data_type": raw[25], "exception_id": u16(raw, 18), "exception_flag": raw[26],
            "condition_ignore_mask": u32(raw, 0),
            "conditions": [{"value": raw[27 + i*2], "operator": raw[28 + i*2]}
                           for i in range(4)],
            "unconsumed": {"offset20": raw[20:22].hex(), "offset35": raw[35]},
        })
    oxygen_sensors = [{
        **base(21, index, raw), "name_string_index": u32(raw, 0),
        "name": strings.get_string(u32(raw, 0)), "sensor_id": u16(raw, 4),
        "request_selector": raw[8], "exception_id": u16(raw, 6),
        "exception_flag": raw[9], "request_frame": 0x8D, "request_byte_offset": 2,
        "unconsumed": raw[10:].hex(),
    } for index, raw in _rows(db, 21, 12)]
    multi_pid = [{
        **base(26, index, raw), "monitor_id": u16(raw, 0),
        "secondary_key": u16(raw, 2), "dependency_monitor_id": u16(raw, 4),
        "exception_id": u16(raw, 6), "exception_flag": raw[8], "unconsumed": raw[9:].hex(),
    } for index, raw in _rows(db, 26, 12)]
    mode05_tests = [{
        **base(22, index, raw), "test_id": raw[4], "data_length": raw[5],
        "support_value": raw[6], "exception_id": u16(raw, 0), "exception_flag": raw[7],
        "unconsumed": raw[2:4].hex(),
    } for index, raw in _rows(db, 22, 8)]
    mode06_tests = [{
        **base(24, index, raw), "semantic_status": "indexes_only", "primary_key": raw[5], "secondary_key": raw[4],
        "exception_id": u16(raw, 0), "exception_flag": raw[7],
        "unconsumed": {"offset2": raw[2:4].hex(), "offset6": raw[6]},
    } for index, raw in _rows(db, 24, 8)]
    mode06_mids = [{
        **base(34, index, raw), "semantic_status": "indexes_only", "monitor_id": raw[0],
        "exception_id": u16(raw, 2), "exception_flag": raw[4],
        "unconsumed": {"offset1": raw[1], "offset5": raw[5:].hex()},
    } for index, raw in _rows(db, 34, 10)]
    test_monitors = []
    for table in (23, 25):
        for index, raw in _rows(db, table, 84):
            row = {**base(table, index, raw), "name_string_index": u32(raw, 48),
                   "name": strings.get_string(u32(raw, 48)),
                   "exception_id": u16(raw, 72), "exception_flag": raw[80 if table == 23 else 81]}
            if table == 23:
                phy, pattern = u16(raw, 60), u16(raw, 70)
                start, end = u16(raw, 62), u16(raw, 64)
                row.update({
                    "test_id": raw[76], "monitor_id": u16(raw, 56),
                    "short_name": raw[:24].decode("utf-16-le").split("\0", 1)[0],
                    "help_id": u32(raw, 52), "support_condition_key": u16(raw, 58),
                    "support_policy": raw[77], "value_role": raw[78],
                    "value_role_name": {1: "value", 2: "maximum", 4: "minimum"}.get(raw[78]),
                    "data_type": raw[79], "bit_start": start, "bit_end": end,
                    "physical_key": phy, "pattern_key": pattern,
                    "physical_records": [{**p, "bit_width": end-start+1,
                        "patterns": [{"value": x["value"], "text": x["name"]} for x in patterns.get(pattern, [])]}
                        for p in physical.get(phy, [])],
                    "patterns": patterns.get(pattern, []) if pattern else [],
                    "request_frame": 0x8D, "test_id_request_offset": 1,
                    "unconsumed": {"offset24": raw[24:48].hex(), "offset66": raw[66:70].hex(),
                                   "offset74": raw[74:76].hex(), "offset81": raw[81:].hex()},
                })
            else:
                row.update(semantic_status="indexes_only", primary_key=raw[77], secondary_key=raw[76],
                           short_name=raw[:48].decode("utf-16-le").split("\0", 1)[0],
                           short_name_evidence="GetDataMonitorShortName1006ACF0 returns row base; buffer capacity unresolved",
                           unconsumed={"offset0": raw[:48].hex(), "offset52": raw[52:72].hex(),
                                       "offset74": raw[74:76].hex(), "offset78": raw[78:81].hex(),
                                       "offset82": raw[82:].hex()})
            test_monitors.append(row)
    return {"statuses": status, "detail_links": links, "results": results, "scalings": scalings,
            "legacy_statuses": old_status, "legacy_detail_links": old_links,
            "legacy_results": old_results, "legacy_scalings": old_scalings,
            "iso_results": iso_results, "oxygen_sensors": oxygen_sensors,
            "multi_pid_dependencies": multi_pid, "mode05_tests": mode05_tests,
            "mode06_tests": mode06_tests, "mode06_mids": mode06_mids, "test_monitors": test_monitors,
            "result_request_frame": 0x135, "support_dtc_request_frame": 0x134}


def decode_mode06_tid_responses(responses: list[bytes]) -> list[dict[str, Any]]:
    """CommandCommon10004210: header + six-byte ISO Mode06 records.

    Native framing validates (length-1)%6, not the service byte. Inputs are
    already framed responses from CCommFrameDataMultiReceive, not bus packets.
    Duplicate (TID,CID) records retain the first value and first of each limit.
    No table24/25 interpretation is implied by this response decoder.
    """
    output = {}
    for response in responses:
        if not response or (len(response) - 1) % 6:
            raise ValueError("Mode06 TID response must contain header + six-byte records")
        for start in range(1, len(response), 6):
            tid, flags = response[start:start+2]
            cid = flags & 0x7F
            value = int.from_bytes(response[start+2:start+4], "big")
            limit = int.from_bytes(response[start+4:start+6], "big")
            row = output.setdefault((tid, cid), {
                "test_id": tid, "component_id": cid, "value": value,
                "minimum": None, "maximum": None,
            })
            role = "minimum" if flags & 0x80 else "maximum"
            if row[role] is None:
                row[role] = limit
    return list(output.values())


def multi_pid_supported(monitor_id: int, rows: list[dict[str, Any]], supported: set[int]) -> bool:
    """GetDatMonList_MultiPid_DT 100013B0: all selected dependency rows must exist."""
    dependencies = [row for row in rows if row["monitor_id"] == monitor_id]
    return bool(dependencies) and all(row["dependency_monitor_id"] in supported for row in dependencies)


def match_iso_result(row: dict[str, Any], test_id: int, component_id: int, context: bytes) -> bool:
    """KgpDataCtrl CompResultKey 100B8630 and DecideByCondition 100B8830."""
    if len(context) != 4:
        raise ValueError("ISO monitor lookup requires four context bytes")
    if row["test_id"] != test_id or row["component_id"] != component_id:
        return False
    for index, (condition, actual) in enumerate(zip(row["conditions"], context)):
        if row["condition_ignore_mask"] & (1 << index):
            continue
        expected = condition["value"]
        matches = {1: actual == expected, 2: actual != expected,
                   3: actual >= expected, 4: actual <= expected}
        if not matches.get(condition["operator"], False):
            return False
    return True


def resolve_monitor_result(
    catalog: dict[str, Any], dtc: int, scaling_id: int, *,
    regulatory_catalog: dict[str, Any] | None = None, subaru: bool = False,
) -> dict[str, Any]:
    """Native lookup after exception selection, including Subaru's zero selector.

    Result metadata can come from category799, but runtime scaling/unit metadata
    always comes from category155. Callers supply those selected catalogs.
    """
    selector = 0 if subaru else scaling_id
    matches = [row for row in catalog["results"]
               if row["dtc"] == dtc and row["scaling_id"] == selector]
    if len(matches) != 1:
        raise ValueError(f"expected one selected result for DTC {dtc:X}/scaling {selector:X}")
    regulatory = regulatory_catalog if regulatory_catalog is not None else catalog
    scalings = [row for row in regulatory["scalings"] if row["scaling_id"] == scaling_id]
    if len(scalings) != 1:
        raise ValueError(f"expected one selected regulatory scaling {scaling_id:X}")
    return {**matches[0], "runtime_scaling_id": scaling_id, "scalings": scalings}


def decode_monitor_status(row: dict[str, Any], response: bytes) -> dict[str, Any]:
    """Native readiness tuple; 0xFFFF means the corresponding field is disabled."""
    output = {"visible": row["visibility_policy"] != 2, "condition": 0xFFFF, "status": 0xFFFF}
    if not output["visible"]:
        return output
    payload = response[row["response_offset"]:]
    for field in ("condition", "status"):
        if row[field + "_enabled"] != 1:
            continue
        start, end = row[field + "_bit_start"], row[field + "_bit_end"]
        if end >= len(payload) * 8:
            output["visible"] = False
            return output
        value = extract_legacy_scalar(payload, start, end)
        if value not in (0, 1):
            raise ValueError(f"native monitor {field} is not Boolean")
        output[field] = value
    return output


def decode_monitor_result(raw_value: int, scaling: dict[str, Any]) -> dict[str, Any]:
    """Apply the native 16-bit physical conversion to a SID19 value or limit."""
    if not 0 <= raw_value <= 0xFFFF:
        raise ValueError("monitor result must be a 16-bit value")
    row = {"data_type": 1, "bit_start": 0, "bit_end": 15,
           "physical_records": [{**scaling, "patterns": []}]}
    return decode_legacy_scalar(row, raw_value.to_bytes(2, "big"))


def parse_non_can_mode06_result(response: bytes) -> dict[str, Any]:
    """Parse one application payload, without transport headers or checksum.

    SAE J1979 APR2002 Table69 and 5.6.3.3 specify:
    46, TID, limit-type/CID, value MSB, value LSB, limit MSB, limit LSB.
    This is not the CAN MID/TID/UASID format. Manufacturer-specific scaling
    and signed interpretation are not inferred, so no pass/fail is fabricated.
    Supported-TID bitmaps and multiple messages require separate handling.
    """
    if len(response) != 7:
        raise ValueError("non-CAN Mode06 result requires one seven-byte application payload")
    if response[0] != 0x46:
        raise ValueError("non-CAN Mode06 result requires response service 0x46")
    if response[1] == 0:
        raise ValueError("TID00 is a supported-test query, not a monitor result")
    return {
        "test_id": response[1],
        "component_id": response[2] & 0x7F,
        "limit_type": "minimum" if response[2] & 0x80 else "maximum",
        "raw_value": int.from_bytes(response[3:5], "big"),
        "raw_limit": int.from_bytes(response[5:7], "big"),
        "raw_response": response.hex(),
    }


def match_non_can_mode06_metadata(
    catalog: dict[str, Any], response: bytes, context: bytes,
) -> list[dict[str, Any]]:
    """Match the wire IDs to native table28 metadata and its context predicates.

    The caller supplies the four native lookup-context bytes, not invented
    defaults. All matching source variants remain visible; exception selection
    and choosing a physical conversion are separate native-context operations.
    """
    result = parse_non_can_mode06_result(response)
    if len(context) != 4:
        raise ValueError("ISO monitor lookup requires four context bytes")
    return [
        row for row in catalog["iso_results"]
        if match_iso_result(row, result["test_id"], result["component_id"], context)
    ]
