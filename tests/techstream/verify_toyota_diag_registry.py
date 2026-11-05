"""Verify the clean derived Toyota diagnostics registry for the maintainer Camry."""
from __future__ import annotations

import gzip
import os

import struct
import tempfile
from pathlib import Path
from tools import REPO_ROOT
REPO = REPO_ROOT

from tools.techstream import techstream_paths
from tools.techstream.ddb_semantics import (
    NativeSelectionContext,
    native_context,
    convert_p5_physical,
    decode_p5_signal,
    extract_msb0,
    format_p5_decimal,
)
from tools.techstream.gts.registry import (
    _registry_request_row,
    _registry_role_bindings,
    _registry_selected_role_bindings,
    _registry_session_control,
    build_toyota_diag_registry,
    load_toyota_diag_registry,
    write_toyota_diag_registry,
)
from tools.techstream.parse_ddb import DDBParser, ECUDataBase, Section, TableDataHead

ART = REPO / "data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json.gz"

passed = failed = 0


def check(name: str, condition: object) -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")


def verify_synthetic_native_programs(parser: DDBParser) -> None:
    """Exercise consumer projection with deliberately different selector CommSets."""
    def selector(frame: int, commset: int, order: int) -> bytes:
        return struct.pack("<HHHHHHHBB", 397, 0xD2, commset, frame, 0, order, 0, 0, 0)

    def commset(identifier: int) -> bytes:
        return struct.pack("<IIHHHBB", 1000, 1020, 0, identifier, 0, 1, 0)

    def database(root: Path, family: str, tables: dict[int, list[bytes]]) -> ECUDataBase:
        path = root / "NA" / "DB" / family / "Toyota.ddb"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"synthetic native consumer fixture\0" + b"".join(
            raw for rows in tables.values() for raw in rows
        ))
        sections = {}
        for table, rows in tables.items():
            payload = b"".join(rows)
            if table == 0:
                offsets = []
                offset = 0
                for raw in rows:
                    offsets.append(struct.pack("<IH", offset, len(raw)))
                    offset += len(raw)
                payload = b"".join(offsets) + payload
            sections[table] = Section(
                TableDataHead(table, 0, len(rows), len(payload)), 0, payload,
                schema_family="gtsplus", variable_layout=table == 0, source_path=path,
            )
        return ECUDataBase(path, 1, sections, schema_family="gtsplus")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        dll = "MissingFixture.dll".encode("utf-16le").ljust(80, b"\0") + struct.pack("<HHHBB", 77, 0, 0x52, 0, 0)
        gen = database(root, "Gen", {
            0: [bytes.fromhex("1001"), bytes.fromhex("1003")],
            17: [struct.pack("<HHHH", 100, 1, 0, 0), struct.pack("<HHHH", 101, 2, 0, 0)],
            18: [selector(100, 1, 0), selector(101, 2, 1)],
            19: [dll],
            29: [commset(1), commset(2)],
        })
        spe = database(root, "Spe", {
            0: [bytes.fromhex("1002")],
            17: [struct.pack("<HHHH", 102, 1, 0, 0)],
            18: [selector(102, 2, 0)],
        })
        context = native_context(gen, spe)
        session = _registry_session_control(parser, context, [{"category_id": 397, "generation": 20}])
        program = session["per_category"]["397"]["extended_session"]
        check("multiframe session retains Gen then Spe order and first-row CommSet across every step",
              program["resolved"]
              and [frame["send"] for frame in program["frames"]] == ["1001", "1003", "1002"]
              and [frame["comm_set"] for frame in program["frames"]] == [1, 1, 1]
              and [frame["native"]["frame_occurrence"]["source"]["family"] for frame in program["frames"]]
                  == ["Gen", "Gen", "Spe"])
        bindings = _registry_selected_role_bindings(parser, context, {"category_id": 999}, root / "bin")
        check("first-role fallback may originate from a nonzero source category",
              bindings[0]["binding_category_id"] == 77
              and bindings[0]["exact_category_binding"] is False
              and bindings[0]["semantic_status"] == "plugin_file_missing"
              and _registry_role_bindings(parser, context, {"category_id": 999}, root / "bin") == [])
        context.load(database(root, "Spe", {29: [commset(1)]}), family="Spe")
        duplicate = _registry_request_row(parser, context, 397, 0xD2, "ambiguous_commset")
        check("merged duplicate CommSet is a native consumer failure, not dict last-wins",
              not duplicate["resolved"] and duplicate["native"]["status"] == 0xC0040102
              and len(duplicate["native"]["failure_query"]["records"]) == 2)


def main() -> int:
    actual = load_toyota_diag_registry(ART)
    gts = techstream_paths.resolve_gts_root(os.environ.get("GTSPLUS_ROOT"))
    regenerated = build_toyota_diag_registry(gts)
    check("registry regenerates exactly from current GTS+ and pinned live evidence", actual == regenerated)
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        # Exercise order, duplicate occurrences, Unicode, and provenance without
        # rebuilding the large fixture for each serialization variant.
        sample = {
            "schema": actual["schema"],
            "history": [{"source": "Spe", "raw": "00ff"}, {"source": "Gen", "raw": "00ff"}],
            "name": "診断",
        }
        for compact in (False, True):
            first = root / "first.json.gz"
            second = root / "second.json.gz"
            plain = root / "export.json"
            write_toyota_diag_registry(sample, first, compact=compact)
            write_toyota_diag_registry(sample, second, compact=compact)
            write_toyota_diag_registry(sample, plain, compact=compact)
            check(f"gzip registry roundtrip preserves content (compact={compact})",
                  load_toyota_diag_registry(first) == sample)
            check(f"gzip registry bytes ignore output filename and time (compact={compact})",
                  first.read_bytes() == second.read_bytes()
                  and first.read_bytes()[4:8] == b"\0" * 4)
            check(f"gzip registry expands to the plain export (compact={compact})",
                  gzip.decompress(first.read_bytes()) == plain.read_bytes())
    check("registry separates raw occurrences from the initial native snapshot",
          actual["schema"] == "toyota-diagnostics-registry-v8"
          and actual["native_context"]["resolution"] == "initial"
          and len(actual["category_rows"]) >= len(actual["initial_categories"]))

    parser = DDBParser()
    verify_synthetic_native_programs(parser)
    gen_path = techstream_paths.gts_db_root(gts, "NA", "Gen") / "Toyota.ddb"
    spe_path = techstream_paths.gts_db_root(gts, "NA", "Spe") / "Toyota.ddb"
    master = parser.parse_master_db(gen_path)
    spe = parser.parse_master_db(spe_path) if spe_path.is_file() else None
    context = native_context(master, spe)
    multi = _registry_request_row(parser, context, 1, 0xA, "multistep")
    selector_query = context.query(18, 1, 0xA)
    first_commset = struct.unpack_from("<H", selector_query.records[0].raw, 4)[0]
    check("selector duplicate steps remain ordered and all consume the first selector CommSet",
          multi["resolved"] and len(multi["frames"]) == len(selector_query.records) >= 2
          and all(frame["comm_set"] == first_commset for frame in multi["frames"])
          and [frame["native"]["selector_occurrence"] for frame in multi["frames"]]
              == [row.as_dict() for row in selector_query.records])
    absent = _registry_request_row(parser, context, 0xFFFF, 0xFFFF, "missing")
    check("missing native selector retains consumer failure instead of an empty success",
          absent["resolved"] is False and absent["frames"] == []
          and absent["native"]["status"] == 0xC0040101)
    unknown = NativeSelectionContext(history_known=False)
    unknown.load(master, family="Gen")
    unknown_program = _registry_request_row(parser, unknown, 1, 0x66, "unknown")
    check("unknown live history retains unresolved context and raw variants",
          unknown_program["resolved"] is False
          and unknown_program["native"]["status"] is None
          and unknown_program["native"]["context"]["resolution"] == "unknown"
          and unknown_program["native"]["query"]["raw_variants"])
    initial = _registry_request_row(parser, context, 1, 0x66, "initial")
    context.correspondence_reflection(0, 136)
    reflected = _registry_request_row(parser, context, 1, 0x66, "reflected")
    check("explicit handling136 changes selector66 without rewriting the initial snapshot",
          [frame["send"] for frame in initial["frames"]] == ["0100"]
          and [frame["send"] for frame in reflected["frames"]] == ["2100"]
          and initial["native"]["context"]["resolution"] == "initial"
          and reflected["native"]["context"]["resolution"] == "event-history")
    context = native_context(master, spe)
    raw_bindings = _registry_role_bindings(parser, context, {"category_id": 405}, gts / "bin")
    selected_bindings = _registry_selected_role_bindings(parser, context, {"category_id": 405}, gts / "bin")
    fallback = next(row for row in selected_bindings if row["role"] == 0xDA)
    check("raw bindings and native first-role fallback are distinct source-qualified surfaces",
          all(row["role"] != 0xDA for row in raw_bindings)
          and fallback["dll"] == "GetCurAbsTimeInfo_DT.Dll"
          and fallback["binding_category_id"] == 0
          and fallback["exact_category_binding"] is False
          and fallback["native"]["query"]["records"][0] == fallback["occurrence"])

    profile = actual["profile"]
    check("exact F33 EPS identity guard is pinned",
          profile["identity_guard"] == {
              "ecu": "eps", "did": 0xF181, "contains_ascii": "8965F3307000",
          })
    check("post-repin DTC sweep retains the exact 17 validated addresses",
          [row["address"] for row in profile["ecus"]] == [
              0x700, 0x701, 0x724, 0x7D2, 0x747, 0x745, 0x707, 0x703, 0x7A1,
              0x7B0, 0x750, 0x7B3, 0x7C4, 0x7D1, 0x7D0, 0x792, 0x7A2,
          ])
    functional = profile["dtc_clear"]["functional_obd"]
    check("functional OBD Mode 04 route matches the live-validated Camry clear",
          functional == {
              "request_id": 0x7DF,
              "mode04_request": "0104000000000000",
              "positive_prefix": "0144",
              "expected_responders": [0x7E8, 0x7EA, 0x7EB, 0x7ED, 0x7EE],
          })
    check("core current P5 catalogs are present",
          profile["catalog_category_ids"] == [372, 395, 397, 398, 405, 435, 450, 498])

    resolver = profile["vehicle_resolution"]
    check("Toyota vehicle resolver selects current Camry-HV vehicle type",
          resolver["generation"] == "current-gtsplus-vehicle-resolver-v3"
          and resolver["vehicle_type"] == 12704
          and resolver["vehicle_name"] == "Camry HV"
          and resolver["install_set_ids"] == [8119, 8120, 8121, 27706])
    check("Toyota VIN decision matcher is vendored as structured data",
          resolver["vin_decision"]["source_category_id"] == 372
          and len(resolver["vin_decision"]["rows"]) == 2
          and {row["route_selector"] for row in resolver["vin_decision"]["rows"]} == {0x12}
          and {row["vehicle_type"] for row in resolver["vin_decision"]["rows"]} == {12704})
    mount = resolver["mount"]
    check("Toyota mount resolver carries all 34 logical Camry categories",
          mount["candidate_count"] == 34
          and len(mount["candidates"]) == 34
          and len({row["category_id"] for row in mount["candidates"]}) == 34
          and {row["connection_frame_id"] for row in mount["candidates"]} == {0}
          and {row["connection_comm_set_id"] for row in mount["candidates"]} == {9}
          and {row["connection_route_selector"] for row in mount["candidates"]} == {0x12, 0x22})
    check("Toyota current Camry connection frame has empty send/mask/check geometry",
          {key: mount["frame_0"]["selected"][key] for key in (
              "frame_id", "send_variable_id", "receive_mask_variable_id", "receive_check_variable_id", "empty"
          )} == {
              "frame_id": 0, "send_variable_id": 0, "receive_mask_variable_id": 0,
              "receive_check_variable_id": 0, "empty": True,
          }
          and mount["frame_0"]["status"] == 0
          and mount["comm_set_9"]["selected"]["send_parameter"] == 1000
          and mount["comm_set_9"]["selected"]["receive_timeout"] == 1020)
    routes = {row["category_id"]: row["transport_route"] for row in mount["candidates"]}
    check("Toyota route contains direct endpoints absent from the old 17-address sweep",
          routes[409]["request_address"] == 0x7C0 and routes[444]["request_address"] == 0x780)
    check("Toyota shared 0x750 routes preserve logical address extensions",
          (routes[452]["request_address"], routes[452]["address_extension"]) == (0x750, 0x2A)
          and (routes[466]["request_address"], routes[466]["address_extension"]) == (0x750, 0x29)
          and (routes[470]["request_address"], routes[470]["address_extension"]) == (0x750, 0x7B)
          and (routes[492]["request_address"], routes[492]["address_extension"]) == (0x750, 0x96))
    check("Toyota P5 live support resolver is carried independently of DDB presence",
          resolver["p5_support"]["options"] == {"1": "PID", "2": "DID", "3": "RID"}
          and resolver["p5_support"]["did_root"]["request"] == "220101"
          and resolver["p5_support"]["did_root"]["selector"] == "0xC8"
          and resolver["p5_support"]["routine_root"]["request"] == "31011001")

    topology = profile["gts_can_topology"]
    placements = topology["placement_variants"][0]["placements"]
    placement_by_domain = {row["ecu_domain"]: row for row in placements}
    check("current GTS Camry-HV CAN topology is a single invariant 18-option placement",
          topology["vehicle_type"] == 12704
          and topology["vehicle_name"] == "Camry HV"
          and topology["can_bus_car_id"] == "0x00A7D910"
          and topology["option_count"] == 18
          and topology["placement_variant_count"] == 1
          and len(topology["placement_variants"][0]["component_groups"]) == 18)
    check("GTS Bus 1 is the Front Camera domain behind Central Gateway",
          placement_by_domain["Front Camera Module"]["bus_name"] == "Bus 1"
          and placement_by_domain["Front Camera Module"]["gateway_names"] == ["Central Gateway"])
    check("GTS Bus 4 carries both EPS and Skid Control behind Central Gateway",
          placement_by_domain["Power Steering (EPS)"]["bus_name"] == "Bus 4"
          and placement_by_domain["Power Steering (EPS)"]["gateway_names"] == ["Central Gateway"]
          and placement_by_domain["Skid Control (ABS/VSC/TRAC)"]["bus_name"] == "Bus 4"
          and placement_by_domain["Skid Control (ABS/VSC/TRAC)"]["gateway_names"] == ["Central Gateway"])

    ecu_by_key = {row["key"]: row for row in profile["ecus"]}
    eps_identity = ecu_by_key["eps"]["observed_identity"]
    frc_identity = ecu_by_key["frc"]["observed_identity"]
    brake_identity = ecu_by_key["brake"]["observed_identity"]
    check("historical EPS identity is exact without rewriting its pre-repin Panda route",
          eps_identity["f181_software_ids"] == ["8965F3307000", "8A3113303100"]
          and eps_identity["f18c_serial"] == "8965033K9011J2740743"
          and eps_identity["panda_bus_at_observation"] == 1
          and eps_identity["elm327_param"] == 1)
    check("historical FRC identity is exact without rewriting its pre-repin Panda route",
          frc_identity["f181_software_ids"] == ["8646F3315000"]
          and frc_identity["ecu_part_0105"] == "8646C06091"
          and frc_identity["f18c_serial"] == "TN69400026030404235J"
          and frc_identity["panda_bus_at_observation"] == 1)
    check("historical Brake identity is exact without rewriting its pre-repin Panda route",
          brake_identity["f181_software_ids"] == ["F152633K0000"]
          and brake_identity["ecu_part_0105"] == "8954147040"
          and brake_identity["f18c_serial"] == "8954147040CFC1800985"
          and brake_identity["panda_bus_at_observation"] == 1)

    eps_angle = actual["catalogs"]["405"]["dids"]["0x1037"]
    check("EPS steering-angle DID retains exact current scaling",
          len(eps_angle) == 1
          and eps_angle[0]["decoder"] == "p5-linear-msb0-v1"
          and eps_angle[0]["name"] == "Steering Angle"
          and (eps_angle[0]["bit_start"], eps_angle[0]["bit_end"]) == (0, 15)
          and eps_angle[0]["mul"] == 15
          and eps_angle[0]["signed"] is True
          and eps_angle[0]["unit"] == "deg")
    signal_rows = [
        signal
        for catalog in actual["catalogs"].values()
        for signals in catalog["dids"].values()
        for signal in signals
    ]
    check("every shipped current-P5 DID signal explicitly selects the closed decoder",
          signal_rows and all(row["decoder"] == "p5-linear-msb0-v1" for row in signal_rows))
    check("MSB0 extraction crosses bytes exactly",
          extract_msb0(bytes.fromhex("a53c"), 4, 11) == 0x53)
    check("signed conversion truncates division toward zero rather than Python floor",
          convert_p5_physical(0xFF, bit_width=8, signed=True, mul=5, div=2, offset=0) == -2)
    check("decimal presentation retains exact DDB precision",
          format_p5_decimal(-15, 1) == "-1.5" and format_p5_decimal(15, 3) == "0.015")
    eps_decoded = decode_p5_signal(
        bytes.fromhex("0001"),
        bit_start=eps_angle[0]["bit_start"], bit_end=eps_angle[0]["bit_end"],
        mul=eps_angle[0]["mul"], div=eps_angle[0]["div"], offset=eps_angle[0]["offset"],
        signed=eps_angle[0]["signed"], decimal_point_count=eps_angle[0]["decimal_point_count"],
    )
    check("Steering Angle raw 1 deterministically renders as 1.5 deg",
          eps_decoded == {"raw": 1, "converted_integer": 15, "value": "1.5", "pattern": None})

    frc_lta = actual["catalogs"]["498"]["dids"]["0x1601"]
    check("FRC 0x1601 carries the current LTA and Hands-Off state vocabulary",
          [row["name"] for row in frc_lta] == [
              "LTA Switch Condition Flag", "LTA Control Condition",
              "Hands-Off Customize Condition Flag", "Hands-Off Control Condition",
          ]
          and frc_lta[1]["patterns"] == {"0": "LTA Enabled", "1": "LTA Disabled"})
    frc_condition = frc_lta[1]
    frc_decoded = decode_p5_signal(
        bytes.fromhex("00010000"),
        bit_start=frc_condition["bit_start"], bit_end=frc_condition["bit_end"],
        mul=frc_condition["mul"], div=frc_condition["div"], offset=frc_condition["offset"],
        signed=frc_condition["signed"], decimal_point_count=frc_condition["decimal_point_count"],
        patterns={int(key): value for key, value in frc_condition["patterns"].items()},
    )
    check("FRC 0x1601 pattern display matches the converted integer",
          frc_decoded["raw"] == 1 and frc_decoded["converted_integer"] == 1
          and frc_decoded["pattern"] == "LTA Disabled")

    for category in (397, 435, 450, 498):
        dtc = actual["catalogs"][str(category)]["dtcs"].get("C13187", [])
        check(f"category {category} resolves live U0131-87 as missing EPS message",
              len(dtc) == 1 and dtc[0]["code"] == "U013187" and dtc[0]["failure"] == "Missing Message")

    hv_test = next(row for row in actual["catalogs"]["397"]["active_tests"] if row["id"] == 1)
    check("Hybrid Active Test 1 is a closed plan-only 0x2F executor",
          hv_test["name"] == "Activate the Inverter Water Pump"
          and hv_test["service"] == 0x2F
          and hv_test["did"] == 0x2801
          and [frame["materialized_prefix"] for frame in hv_test["start_frames"]] == ["2f280103"]
          and [frame["materialized_prefix"] for frame in hv_test["stop_frames"]] == ["2f280100"]
          and hv_test["runtime_length_probe"]["kind"] == "read_data_by_identifier_value_length"
          and [frame["materialized_request"] for frame in hv_test["runtime_length_probe"]["frames"]] == ["222801"]
          and [frame["positive_check"] for frame in hv_test["runtime_length_probe"]["frames"]] == ["62"]
          and hv_test["runtime_length_probe"]["response_prefix_length"] == 3
          and hv_test["execution"] == "plan_only")

    hybrid_water_pump = next(row for row in actual["catalogs"]["397"]["active_tests"] if row["id"] == 1)
    check("direct Active Test exports exact role-0x70 physical conversion and OEM choice text",
          hybrid_water_pump["signal_info"]["physical"]["mul"] == 1
          and hybrid_water_pump["signal_info"]["physical"]["div"] == 1
          and hybrid_water_pump["signal_info"]["physical"]["offset"] == 0
          and hybrid_water_pump["signal_info"]["choices"] == [{"value": 1, "text": "ON"}])
    engine_vvt = next(row for row in actual["catalogs"]["372"]["active_tests"] if row["id"] == 4)
    check("Engine direct Active Test retains engineering offset/unit for inverse conversion",
          engine_vvt["signal_info"]["physical"]["offset"] == -128
          and engine_vvt["signal_info"]["physical"]["unit"] == "%")

    engine_shared_direct = next(row for row in actual["catalogs"]["372"]["active_tests"] if row["id"] == 77)
    check("shared-DID direct Active Test preserves the full one-to-many type-67 control geometry",
          engine_shared_direct["name"] == "Pilot Injection Volume Select Cylinder"
          and engine_shared_direct["did"] == 0x284A
          and engine_shared_direct["encoding_mode"] == 0
          and [(row["control_enable_bit_1based"], row["data_byte_offset"], row["data_byte_length"])
               for row in engine_shared_direct["data_id_for_act_records"]] == [(1, 0, 1), (2, 1, 1)]
          and engine_shared_direct["control_enable_mask"]["start"] == "type67_rows_for_selected_byte_span"
          and engine_shared_direct["control_enable_mask"]["stop"] == "type67_rows_for_selected_byte_span"
          and engine_shared_direct["execution"] == "plan_only")
    brake_shared_direct = next(row for row in actual["catalogs"]["435"]["active_tests"] if row["id"] == 42)
    check("Brake shared-DID direct control is no longer rejected merely because type-67 is one-to-many",
          brake_shared_direct["did"] == 0x2805
          and brake_shared_direct["encoding_mode"] == 0
          and len(brake_shared_direct["data_id_for_act_records"]) == 2
          and brake_shared_direct["execution"] == "plan_only")

    engine_static_routine = next(row for row in actual["catalogs"]["372"]["active_tests"] if row["id"] == 40402)
    check("static routine-command variable bytes do not falsely make a routine runtime-parameterized",
          engine_static_routine["name"] == "AIR PUMP: OFF / ASV B1: CLOSE / ASV B2: CLOSE"
          and [frame["materialized_static_request"] for frame in engine_static_routine["start_frames"]] == ["3101113600"]
          and [row["bytes"] for row in engine_static_routine["routine_commands"]] == ["00"]
          and engine_static_routine["output_mask_value"]["bytes"] == ""
          and engine_static_routine["output_mask_button"]["bytes"] == ""
          and engine_static_routine["fixed_request"] is True
          and engine_static_routine["execution"] == "executable")
    engine_masked_routine = next(row for row in actual["catalogs"]["372"]["active_tests"] if row["id"] == 40000)
    check("runtime button mask remains plan-only while its exact mask bytes are exported",
          engine_masked_routine["fixed_request"] is False
          and engine_masked_routine["output_mask_button"]["bytes"] == "ff"
          and engine_masked_routine["execution"] == "plan_only")

    frc_test = next(row for row in actual["catalogs"]["498"]["active_tests"] if row["id"] == 0xA429)
    check("FRC LTA Steering Vibration is exact fixed RID 0x1588 executable RoutineControl geometry",
          frc_test["name"] == "LTA Steering Vibration"
          and frc_test["routine_id"] == 0x1588
          and frc_test["fixed_request"] is True
          and [frame["materialized_static_request"] for frame in frc_test["start_frames"]] == ["31011588"]
          and [frame["materialized_static_request"] for frame in frc_test["stop_frames"]] == ["31021588"]
          and [frame["materialized_static_request"] for frame in frc_test["result_frames"]] == ["31031588"]
          and frc_test["session_requirement"] == "extended"
          and frc_test["execution"] == "executable")

    active = [row for catalog in actual["catalogs"].values() for row in catalog["active_tests"]]
    check("Active Tests are graded by fixed-geometry sufficiency without guessing",
          sum(row["execution"] == "executable" for row in active) == 69
          and sum(row["execution"] == "plan_only" for row in active) == 349
          and sum(row["execution"] == "unresolved_static_plan" for row in active) == 10
          and all(row["execution"] != "executable" for row in active if row["kind"] == "direct"))

    # Source-qualified native programs alongside raw metadata.
    hv = actual["catalogs"]["397"]
    check("catalog metadata remains available alongside native programs",
          all(key in hv for key in ("category", "dids", "dtcs", "active_tests"))
          and hv_test["execution"] == "plan_only"
          and [frame["materialized_prefix"] for frame in hv_test["start_frames"]] == ["2f280103"])
    check("initial-read request is materialized per direct Active Test",
          hv_test["initial_read"]["mode"] == 0
          and hv_test["initial_read"]["resolved"]
          and [(frame["send"], frame["check"]) for frame in hv_test["initial_read"]["frames"]] == [("222801", "62")]
          and hv_test["session_requirement"] == "extended")
    eps_ffd_meta = actual["catalogs"]["405"]["generic_ffd"]
    eps_ffd_steering = next(row for row in eps_ffd_meta["signals"] if row["name"] == "Steering Angle")
    check("EPS generic P5 FFD signal selection and scaling are exported from current host semantics",
          eps_ffd_steering["snapshot_did"] == 0x3037
          and eps_ffd_steering["primary_did"] == 0x1037
          and eps_ffd_steering["flags"] & 0x02
          and eps_ffd_steering["local_support_mode"] == 0
          and eps_ffd_steering["support_condition"] is None
          and eps_ffd_steering["signal_info"]["mul"] == 15
          and eps_ffd_steering["signal_info"]["unit"] == "deg")
    eps_ffd_odo = next(row for row in eps_ffd_meta["signals"] if row["monitor_key"] == 9905)
    check("EPS generic P5 FFD cross-DID condition resolves through the master variable table",
          eps_ffd_odo["snapshot_did"] == 0x0403
          and eps_ffd_odo["support_condition"] == {
              "key": 10001, "variable_id": 11290, "referenced_did": 0x0403,
              "bit_start": 7, "bit_end": 7, "condition_type": 7,
          }
          and eps_ffd_meta["dynamic_lsb_table_present"] is False)

    hv_ffd = next(row for row in hv["commands"] if row["kind"] == "p5_dtc_snapshot")
    check("ordinary P5 generic DTC snapshot request is exported from role-0xB5 fallback",
          hv_ffd["role"] == 0xB5
          and hv_ffd["plugin_binding"]["binding_category_id"] == 0
          and hv_ffd["plugin_binding"]["dll"] == "GetEachFrzFrmDatP5_DT.dll"
          and [frame["send"] for frame in hv_ffd["requests"][0]["frames"]] == ["1904000000ff"]
          and [frame["check"] for frame in hv_ffd["requests"][0]["frames"]] == ["5904"]
          and hv_ffd["execution"] == "read_only")

    hv_rob_meta = hv["rob"]
    hv_behavior = next(row for row in hv_rob_meta["behavior_codes"] if row["behavior_code"] == 0x0450)
    check("Hybrid RoB behavior metadata carries current OEM code/name identity",
          hv_behavior["signature"] == "X0450"
          and hv_behavior["name"] == "Hybrid/EV Battery Pack Sensor Module Mismatch"
          and hv_rob_meta["dynamic_lsb_table_present"] is False)

    eps_rob_meta = actual["catalogs"]["405"]["rob"]
    eps_steering = next(row for row in eps_rob_meta["signals"] if row["name"] == "Steering Angle")
    eps_info = eps_steering["signal_info"]
    check("EPS RoB Steering Angle current type-88 geometry and physical metadata are exact",
          eps_steering["did"] == 0x5037
          and (eps_steering["bit_start"], eps_steering["bit_end"]) == (0, 15)
          and eps_steering["local_support_mode"] == 0
          and eps_steering["support_condition_key"] == 0
          and eps_steering["dynamic_lsb_possible"] is False
          and (eps_info["mul"], eps_info["div"], eps_info["offset"]) == (15, 1, 0)
          and eps_info["signed"] is True
          and eps_info["decimal_point_count"] == 1
          and eps_info["unit"] == "deg")
    eps_pos = decode_p5_signal(bytes.fromhex("0001"), bit_start=0, bit_end=15,
                               mul=15, div=1, offset=0, signed=True, decimal_point_count=1)
    eps_neg = decode_p5_signal(bytes.fromhex("ffff"), bit_start=0, bit_end=15,
                               mul=15, div=1, offset=0, signed=True, decimal_point_count=1)
    check("EPS RoB Steering Angle uses canonical signed P5 conversion",
          eps_pos["value"] == "1.5" and eps_neg["value"] == "-1.5")

    hv_rob = next(row for row in hv["commands"] if row["kind"] == "p5_rob")
    check("ordinary P5 RoB transport preserves native order and exact role-0xA0 binding",
          hv_rob["role"] == 0xA0
          and hv_rob["plugin_binding"]["binding_category_id"] == 397
          and hv_rob["plugin_binding"]["exact_category_binding"] is True
          and hv_rob["plugin_binding"]["dll"] == "GetRoBP5_DT.dll"
          and [[(frame["send"], frame["check"]) for frame in hv_rob["requests"][phase]["frames"]]
               for phase in ("inventory", "frames", "record")] == [
                  [("ab11", "eb11"), ("ab01", "eb01")],
                  [("ab120000", "eb12"), ("ab020000", "eb02")],
                  [("ab1300000000", "eb13"), ("ab0300000000", "eb03")],
               ]
          and hv_rob["execution"] == "read_only")

    session = profile["session_control"]
    check("session_control carries the runtime current-P5 contract",
          session["generation"] == "current-p5"
          and session["default_session"] == 1
          and session["extended_session"] == 3
          and session["enter_sequence"] == ["1001", "1003"]
          and session["return_default"] == "1001"
          and session["keepalive"] == {
              "kind": "session_did_poll", "did": "0xF186", "request": "22f186",
              "positive_prefix": "62f186", "interval_s": 2.0,
          } | {key: session["keepalive"][key] for key in ("selector", "mask", "check", "meaning", "session_state")})
    check("every catalog category resolves identical D1/D2/0xDD session frames",
          set(session["per_category"]) == {str(cid) for cid in profile["catalog_category_ids"]}
          and all(row["generation_low5"] == "0x14"
                  and [frame["send"] for frame in row["default_session"]["frames"]] == ["1001"]
                  and [frame["send"] for frame in row["extended_session"]["frames"]] == ["1003"]
                  and [frame["send"] for frame in row["keepalive"]["frames"]] == ["22f186"]
                  and [frame["check"] for frame in row["keepalive"]["frames"]] == ["62"]
                  for row in session["per_category"].values()))

    check("referenced CommSet timeout/retry rows are carried exactly",
          {key: {field: row[field] for field in (
              "send_parameter", "receive_timeout", "retry_count", "exception_handler_id", "exception_handler_flag"
          )} for key, row in actual["commsets"]["rows"].items()} == {
              "1": {
                  "send_parameter": 1000, "receive_timeout": 1020, "retry_count": 1,
                  "exception_handler_id": 0, "exception_handler_flag": 0,
              },
              "9": {
                  "send_parameter": 1000, "receive_timeout": 1020, "retry_count": 0,
                  "exception_handler_id": 0, "exception_handler_flag": 0,
              },
          })

    hv_selectors = {row["selector"]: row for row in hv["selectors"]}
    check("resolved selector frames include the recovered executor templates",
          [(frame["frame"], frame["comm_set"], frame["send"], frame["mask"], frame["check"])
           for frame in hv_selectors["0xDD"]["frames"]] == [("0x2B55", 1, "22f186", "ff", "62")]
          and hv_selectors["0x9D"]["frames"][0]["send"] == "2fffff03"
          and hv_selectors["0x9D"]["frames"][0]["check"] == "6f"
          and hv_selectors["0x64"]["frames"][0]["send"] == "2fffff00"
          and hv_selectors["0xD5"]["frames"][0]["send"] == "3101ffff"
          and hv_selectors["0xD7"]["frames"][0]["check"] == "7103")

    hv_plugins = {row["role"]: row for row in hv["selected_plugins"]}
    check("role bindings carry recovered kinds and fail closed elsewhere",
          hv_plugins[0x19]["dll"] == "DelDiagCodeP4.dll"
          and hv_plugins[0x19]["semantic_kind"] == "dtc_clear"
          and hv_plugins[0x41]["semantic_kind"] == "p5_signal_info"
          and hv_plugins[0x29]["semantic_kind"] is None
          and hv_plugins[0x29]["semantic_status"] == "plugin_semantics_unrecovered_for_identity")
    emps_plugins = {row["role"]: row for row in actual["catalogs"]["405"]["selected_plugins"]}
    check("EMPS binds the exactly-recovered 0x52 CID plugin",
          emps_plugins[0x52]["dll"] == "GetCID_SID22_DT.dll"
          and emps_plugins[0x52]["semantic_kind"] == "generic_cid")

    hv_commands = {row["role"]: row for row in hv["commands"]}
    check("DTC-clear command carries both selector paths with per-request session class",
          hv_commands[0x19]["kind"] == "dtc_clear"
          and [{key: frame[key] for key in (
              "name", "selector", "send", "mask", "check", "comm_set",
              "receive_timeout", "retry_count", "session_requirement",
          )} for frame in hv_commands[0x19]["requests"][0]["frames"]] == [{
              "name": "primary", "selector": "0x1", "send": "04", "mask": "", "check": "44",
              "comm_set": 1, "receive_timeout": 1020, "retry_count": 1,
              "session_requirement": "default",
          }]
          and hv_commands[0x19]["requests"][1]["frames"][0]["send"] == "14ffffff"
          and hv_commands[0x19]["requests"][1]["frames"][0]["session_requirement"] == "extended"
          and hv_commands[0x19]["timer"]["resolved"]
          and hv_commands[0x19]["timer"]["delay_ms"] == 0
          and hv_commands[0x19]["timer"]["consumer_policy"] == "first-record-if-nonempty"
          and len(hv_commands[0x19]["flow"]["fallback_error_codes_when_function_gate_set"]) == 10)
    emps_cid = {row["role"]: row for row in actual["catalogs"]["405"]["commands"]}[0x52]
    check("CID response model is carried where the exact plugin identity is recovered",
          emps_cid["requests"][0]["selector"] == "0xDC"
          and emps_cid["requests"][0]["frames"][0]["check"] == "62f181"
          and emps_cid["response_model"]["payload_offset"] == 4
          and emps_cid["response_model"]["record_size"] == 16)

    hv_functions = {row["function_id"]: row for row in hv["functions"]}
    check("supported-function hierarchy joins type-26 functions to type-27 details",
          len(hv["functions"]) == 9
          and sum(len(row["detail_ids"]) for row in hv["functions"]) == 18
          and sorted(hv_functions) == [2, 3, 4, 10, 28, 29, 30, 32, 37]
          and all(row["name"] is None and row["description"] is None for row in hv["functions"]))

    hv_data_list = hv["data_list"]
    check("Data List display order is the consumer-pinned monitor sort key",
          hv_data_list["record_counts"] == {"157": 1448, "62": 1464}
          and hv_data_list["row_count"] == 1457
          and hv_data_list["rows"][0] == {"monitor_key": 662, "sort_key": 0, "did": "0x0103",
                                          "bit_start": 8, "bit_end": 31,
                                          "name": "Total Distance Traveled"}
          and [row["sort_key"] for row in hv_data_list["rows"]]
          == sorted(row["sort_key"] for row in hv_data_list["rows"]))

    engine_groups = actual["catalogs"]["372"]["active_test_groups"]
    group76 = next(row for row in engine_groups["groups"] if row["group_id"] == 76)
    group102 = next(row for row in engine_groups["groups"] if row["group_id"] == 102)
    check("multi-control Active-Test group geometry carries runtime input slots and composer boundary",
          engine_groups["group_count"] == 5 and engine_groups["membership_count"] == 10
          and engine_groups["materializable_group_count"] == 4
          and engine_groups["blocked_group_count"] == 1
          and group76["members"] == [77, 78]
          and [(row["active_test_id"], row["input_slot"], row["did"]) for row in group76["member_inputs"]]
              == [(77, 1, 0x284A), (78, 2, 0x284A)]
          and group76["execution"] == "materializable" and group76["did"] == 0x284A
          and group102["members"] == [103, 104]
          and group102["execution"] == "blocked" and group102["did"] is None
          and actual["catalogs"]["397"]["active_test_groups"]["group_count"] == 0)

    utilities = actual["utilities"]
    check("utility surface is the recovered generic families only, others absent",
          len(utilities["bindings"]) == 10
          and {row["semantic_kind"] for row in utilities["bindings"]} == {
              "test_present_start", "test_present_stop", "check_mode_frame_get",
              "check_mode_frame_confirm", "active_test_start", "routine_active_test_init",
              "routine_active_test_signal_info", "set_default_session", "move_session_cgwd",
              "single_routine_active_test",
          }
          and {row["role"] for row in utilities["bindings"]}
          == {0x3A, 0x3B, 0x61, 0x62, 0xB0, 0xAE, 0xAF, 0xBF, 0xCA, 0xD4}
          and utilities["routine_control"]["session_requirement"] == "extended"
          and utilities["io_control"]["session_requirement"] == "extended")

    print(f"\n== RESULT: {passed} passed, {failed} failed ==")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
