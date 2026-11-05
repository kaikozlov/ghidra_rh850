"""Presentation layer for the GTS CLI: all human/JSON output formatting lives here."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def _format_row(row: dict[str, Any]) -> str:
    kind = row.get("kind", "?")
    if kind == "did":
        did = row.get("primary_did")
        alt = row.get("alternate_did")
        alt_text = f" alt=0x{alt:04X}" if isinstance(alt, int) and alt not in {0, did} else ""
        info = row.get("signal_info")
        info_text = ""
        if isinstance(info, dict):
            unit = info.get("unit") or "-"
            info_text = (
                f"\tconv={info['mul']}/{info['div']} offset={info['offset']} "
                f"dec={info['decimal_point_count']} signed={int(info['signed'])} "
                f"bits={info['bit_width']} unit={unit}"
            )
            if info.get("pattern_display"):
                info_text += f" patterns={len(info['pattern_display'])}"
        tables = "/".join(str(table) for table in row.get("tables", [row["table"]]))
        refs = (
            f"\ttable={tables} monitor={row['monitor_key']} "
            f"bits={row['bit_start']}..{row['bit_end']} "
            f"physical={row['physical_data_key']} pattern={row['pattern_display_key']}"
        )
        return f"did\t{row['source']}\t0x{did:04X}{alt_text}\t{row.get('name') or ''}{refs}{info_text}"
    if kind == "dtc":
        return f"dtc\t{row['source']}\t{row.get('code') or row.get('packed_dtc')}\t{row.get('description') or ''}\t{row.get('failure') or ''}"
    if kind == "behavior":
        return f"behavior\t{row['source']}\t{row.get('signature') or ''}\t{row.get('name') or ''}\t{row.get('comment') or ''}"
    if kind == "string":
        return f"string\t{row['source']}\t@0x{row['offset']:X}\t{row['text']}"
    if kind == "file":
        return f"file\t{row['source']}"
    if kind == "route":
        return (
            f"route\t{row.get('selector','')}\t{row.get('cid_getter','')}\t"
            f"{row.get('prepare_writer','')}\t{row.get('flash_writer','')}\t{row.get('parameter_file') or '(master only)'}"
            f"\topen_failure={row.get('engine_selection', {}).get('own_ini_open_failure', '')}"
        )
    if kind == "frame":
        return (
            f"frame\tcategory={row['category_id']}\tselector={row['selector']}\t"
            f"comm_set={row['comm_set']}\tframe={row['comm_frame_id']}\t"
            f"rcv_timeout={row['comm_set_metadata']['receive_timeout']}\t"
            f"retries={row['comm_set_metadata']['retry_count']}\t"
            f"send={row['send']['bytes']}\tmask={row['receive_mask']['bytes']}\tcheck={row['receive_check']['bytes']}"
        )
    if kind == "cuw":
        return f"cuw\t{row.get('source','')}\t{row.get('vehicle','')}\t{row.get('contact_type','')}\t{row.get('new_cids','')}"
    return json.dumps(row, sort_keys=True)


def _print_rows(rows: list[dict[str, Any]], *, as_json: bool, limit: int | None = None) -> None:
    shown = rows if limit is None else rows[:limit]
    if as_json:
        print(json.dumps(shown, indent=2, sort_keys=True))
    else:
        for row in shown:
            print(_format_row(row))
        if limit is not None and len(rows) > limit:
            print(f"... {len(rows) - limit} more result(s); use --limit to raise the cap", file=sys.stderr)


def did(rows, *, as_json, limit):
    _print_rows(rows, as_json=as_json, limit=limit)
    if not rows and not as_json:
        print("No Data List / alternate snapshot DID matches in this ECU database.")
        print("PCS recorder IDs are a separate namespace: tools/gts recorder --help")


def recorder(payload, *, as_json, limit):
    fields = payload["fields"]
    shown = fields[:limit]
    if as_json:
        print(json.dumps({**payload, "fields": shown, "matched_fields": len(fields)}, indent=2, sort_keys=True))
    else:
        print(f"pcs-recorder\tschema={payload['schema']}\tsource={payload['source']}")
        print("Record positions: byte is 1-based, bit 7 is MSB; these are not CAN-frame offsets.")
        if not fields:
            print("No recorder fields match in this schema.")
        for row in shown:
            point = f" point={row['Point']}" if "Point" in row else ""
            print(
                f"0x{row['DataID']}\t{row['DataName']}\t"
                f"size={row['DataSize']} byte={row['BytePosition']} bit={row['BitPosition']} "
                f"width={row['BitLength']} type={row['Type']} "
                f"lsb={row['Lsb']} offset={row['Offset']}{point} "
                f"support={row['SupportDID']} invalid={row['InvalidValueList']}"
            )
    if len(fields) > limit:
        print(f"... {len(fields) - limit} more field(s); use --limit to raise the cap", file=sys.stderr)


def _recovery_progress(label: str):
    def report(done: int, total: int, path: Path) -> None:
        if done == 1 or done == total or done % 10 == 0:
            print(f"{label}\t{done}/{total}\t{path.as_posix()}", file=sys.stderr, flush=True)

    return report


def _aggregate_recovery_progress(component: str, done: int, total: int, path: Path) -> None:
    if done == 1 or done == total or done % 10 == 0:
        print(f"{component}\t{done}/{total}\t{path.as_posix()}", file=sys.stderr, flush=True)


def status(payload, *, as_json):
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for key, value in payload.items():
            print(f"{key}\t{value}")


def ecu(payload, *, as_json):
    rows = payload["sections"]
    path = payload["path"]
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(path)
        for row in rows:
            print(f"{row['table']:>3}\t{row['class']}\tcount={row['records']}\tsize={row['record_size']}")


def _active_phase(phase, label):
    for index, row in enumerate(phase["frames"]):
        frame = row["base_frame"]
        request = row.get("materialized_prefix", row.get("materialized_static_request", row.get("materialized_request")))
        print(
            f"{label}\tframe={index}\tselector={phase['selector']}\tsend={request}\t"
            f"expect={frame['receive_check']['bytes']}\tcommset={frame['comm_set']}"
        )


def active_test(payload, kind, category, *, as_json):
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    selected = payload["selected_test"]
    executor = payload["executor"]
    print(
        f"active-test\tcategory={category['category_id']}\t{category['name']}\tkind={kind}\t"
        f"id={selected['active_test_id_hex']}\tname={selected['name'] or '-'}\t"
        f"native_context={payload['native_context']['resolution']}\tmetadata=raw-catalog"
    )
    _active_phase(executor["start"], "start")
    _active_phase(executor["stop"], "stop")
    if kind == "direct":
        length = executor["runtime_data_length"]
        print(
            f"wire\tservice={executor['service']}\tdid={executor['data_id_for_act']['did_hex']}\t"
            f"runtime_length=N\tminimum={length['minimum_from_bit_geometry']}"
        )
        _active_phase(length["probe"], "runtime-length-probe")
        examples = executor.get("minimum_length_examples")
        if examples is not None:
            print(f"minimum-examples\t{json.dumps(examples, sort_keys=True)}")
    else:
        _active_phase(executor["result"], "result")
        print(
            f"wire\tservice={executor['service']}\trid={executor['routine_id_hex']}\t"
            f"fixed={int(executor['fixed_request'])}"
        )
        print(
            f"routine-vars\tstart=0x{selected['routine_command_variable']:X}\t"
            f"stop=0x{selected['routine_stop_command_variable']:X}\t"
            f"value_mask=0x{selected['output_mask_value_variable']:X}\t"
            f"button_mask=0x{selected['output_mask_button_variable']:X}\t"
            f"status_key=0x{selected['routine_status_key']:X}"
        )


def command(payload, category, *, as_json):
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        f"command	category={category['category_id']}	{category['name']}	role={payload['role_hex']}	"
        f"plugin={payload['plugin']}	surface={payload['operation_surface']}	semantics={payload['semantic_status']}"
    )
    print(f"native-context\t{payload['native_context']['resolution']}")
    for name, frames in payload["frames"].items():
        for index, frame in enumerate(frames):
            print(
                f"{name}\tframe={index}\tselector={frame['selector']}\tsend={frame['send']['bytes']}\t"
                f"expect={frame['receive_check']['bytes']}\tcommset={frame['comm_set']}\t"
                f"timeout={frame['comm_set_metadata']['receive_timeout']}\tretries={frame['comm_set_metadata']['retry_count']}"
            )
    for timer in payload["timers"]:
        print(f"timer	id={timer['timer_id']}	delay_ms={timer['delay_ms']}")
    multi_active = payload["multi_active_test_init_model"]
    if multi_active is not None:
        category_plan = multi_active.get("category_plan")
        if category_plan is not None:
            print(
                f"multi-active-test-census\tgroups={category_plan['group_count']}\t"
                f"memberships={category_plan['membership_count']}\ttable={category_plan['group_table']}"
            )
        selected_plan = multi_active.get("selected_plan")
        if selected_plan is not None:
            group = selected_plan["group"]
            print(
                f"multi-active-test\tgroup={group['group_id_hex']}\tname={group['name'] or '-'}\t"
                f"members={group['member_count']}"
            )
            for member in selected_plan["members"]:
                selected = member["selected_test"]
                tx = member["initial_transaction"]
                print(
                    f"member\torder={member['sort_order']}\tid={selected['active_test_id_hex']}\t"
                    f"name={selected['name'] or '-'}\tdid=0x{selected['initial_read_did']:04X}\t"
                    f"bits={selected['bit_start']}..{selected['bit_end']}"
                )
                for index, frame in enumerate(tx.get("frames", [])):
                    print(f"member-initial-read\tframe={index}\tsend={frame['materialized_send']}\texpect={frame['receive_check']}")
    active_test_monitor = payload["active_test_monitor_model"]
    if active_test_monitor is not None:
        category_plan = active_test_monitor.get("category_plan")
        if category_plan is None:
            print("active-test-monitors\tcategory_partition=unresolved")
        else:
            part = category_plan["candidate_partition"]
            print(
                f"active-test-monitors\ttable={category_plan['candidate_table']}\t"
                f"total={category_plan['candidate_count']}\tactive={category_plan['active_test_candidate_count']}\t"
                f"nonmember={category_plan['nonmember_count']}\t"
                f"direct={part['active_direct_include']}\t"
                f"runtime_active={part['active_runtime_check_support_pid']}\t"
                f"runtime_nonmember={part['nonmember_runtime_probe_then_filter']}\t"
                f"builder={category_plan['support_list_builder']}"
            )
    active_test_signal_info = payload["active_test_signal_info_model"]
    if active_test_signal_info is not None:
        selected_plan = active_test_signal_info.get("selected_plan")
        if selected_plan is None:
            print("active-test-signal-info\tselected_item=required")
        else:
            selected = selected_plan["selected_test"]
            pattern = selected_plan["active_test_pattern"]
            physical = selected_plan["physical"]
            display = selected_plan["display_info"]
            display_text = ",".join(f"{row['value']}={row['text'] or '-'}" for row in display) or "-"
            print(
                f"active-test-signal-info\tid={selected['active_test_id_hex']}\tname={selected['name'] or '-'}\t"
                f"pattern_key={pattern['key']}\tphysical_key={physical['key']}\t"
                f"conv={physical['mul']}/{physical['div']} offset={physical['offset']}\t"
                f"dec={physical['decimal_point_count']}\tsigned={int(physical['signed'])}\t"
                f"unit={physical['unit'] or '-'}"
            )
            print(
                f"active-test-display\tpattern={selected['pattern']}\tbutton_size={pattern['button_size']}\t"
                f"key_op={pattern['key_operation_pattern']}\tkey_invalid={pattern['key_invalid_flag']}\t"
                f"values={display_text}"
            )
    active_test_init = payload["active_test_init_model"]
    if active_test_init is not None:
        selected_plan = active_test_init.get("selected_plan")
        if selected_plan is None:
            print("active-test-init\tselected_item=required")
        else:
            selected = selected_plan["selected_test"]
            tx = selected_plan["initial_transaction"]
            linked = selected_plan["linked_monitor"]
            print(
                f"active-test-init\tid={selected['active_test_id_hex']}\tname={selected['name'] or '-'}\t"
                f"did=0x{selected['initial_read_did']:04X}\tbits={selected['bit_start']}..{selected['bit_end']}\t"
                f"init_mode={selected['initial_read_mode']}\tmonitor_link_mode={selected['monitor_link_mode']}"
            )
            if tx["performed"]:
                for index, frame in enumerate(tx["frames"]):
                    print(
                        f"initial-read\tframe={index}\tselector={tx['selector']}\tsend={frame['materialized_send']}\t"
                        f"expect={frame['receive_check']}\tbits={tx['bit_start']}..{tx['bit_end']}"
                    )
            monitor = linked.get("monitor")
            print(
                f"linked-monitor\tkey={linked['monitor_key']}\tresolution={linked['resolution']}\t"
                f"name={(monitor or {}).get('name') or '-'}"
            )
            executor = selected_plan["executor"]
            length = executor["runtime_data_length"]
            print(
                f"active-test-executor\tservice={executor['service']}\tdid={executor['data_id_for_act']['did_hex']}\t"
                f"encoding_mode={executor['data_id_for_act']['encoding_mode']}\t"
                f"runtime_length=N\tminimum={length['minimum_from_bit_geometry']}"
            )
            _active_phase(executor["start"], "start")
            _active_phase(executor["stop"], "stop")
            _active_phase(length["probe"], "runtime-length-probe")
            examples = executor.get("minimum_length_examples")
            if examples is not None:
                print(f"active-test-wire-minimum\t{json.dumps(examples, sort_keys=True)}")
    active_test_model = payload["active_test_model"]
    if active_test_model is not None:
        category_plan = active_test_model.get("category_plan")
        if category_plan is None:
            print("active-tests\tcategory_partition=unresolved")
        else:
            print(
                f"active-tests\tdirect={category_plan['direct_candidate_count']}\t"
                f"routine={category_plan['routine_candidate_count']}\t"
                f"multi_did={category_plan['multi_did_count']}\t"
                f"did_helper={category_plan['direct_support_helper']}\t"
                f"rid_helper={category_plan['routine_support_helper']}"
            )
    list_model = payload["list_model"]
    if list_model is not None:
        category_plan = list_model.get("category_plan")
        if category_plan is None:
            print("list\tcategory_partition=unresolved")
        else:
            part = category_plan["candidate_partition"]
            print(
                f"list\ttable={category_plan['candidate_table']}\tcandidates={category_plan['candidate_count']}\t"
                f"direct_include={part['direct_include']}\tdirect_exclude={part['direct_exclude']}\t"
                f"runtime_probe={part['runtime_check_support_pid']}\t"
                f"builder={category_plan['support_list_builder']}"
            )
    metadata = payload["metadata_model"]
    if metadata is not None:
        fields = metadata["conversion_fields"]
        print(
            f"metadata\tphysical=table{metadata['physical_data_table']}\tunit=table{metadata['unit_table']}\t"
            f"patterns=table{metadata['pattern_display_table']}\tfields={len(fields)}"
        )
    response = payload["response_model"]
    if response is not None:
        print(
            f"response	payload_offset={response['payload_offset']}	record_size={response['record_size']}	"
            f"names={response['entry_name_prefix']}1...	conversion=CP_ACP"
        )
    flow = payload["control_flow"]
    if flow is not None:
        print(
            f"flow	primary={flow['primary_selector']}	fallback={flow['fallback_selector']}	"
            f"fallback_errors={len(flow['fallback_error_codes_when_function_gate_set'])}"
        )


def timers(category, shown, *, native_context, as_json):
    if as_json:
        print(json.dumps({"category": category, "timers": shown, "native_context": native_context}, indent=2, sort_keys=True))
        return
    print(f"native-context\t{native_context['resolution']}")
    for row in shown:
        print(
            f"timer	category={row['category_id']}	id={row['timer_id']}	"
            f"delay_ms={row['delay_ms']}	unknown_08={row['unknown_dword_08']}"
        )


def commsets(shown, *, native_context, query, as_json):
    if as_json:
        print(json.dumps({"rows": shown, "query": query, "native_context": native_context}, indent=2, sort_keys=True))
        return
    print(f"native-context\t{native_context['resolution']}")
    for row in shown:
        send_value = "FFFFFFFF" if row["send_parameter"] == 0xFFFFFFFF else str(row["send_parameter"])
        receive_value = "FFFFFFFF" if row["receive_timeout"] == 0xFFFFFFFF else str(row["receive_timeout"])
        print(
            f"commset\t{row['comm_set_id']}\tsend_parameter={send_value}\t"
            f"receive_timeout={receive_value}\tretries={row['retry_count']}\t"
            f"exception_id={row['exception_handler_id']}\texception_flag={row['exception_handler_flag']}\t"
            f"unknown_0c={row['unknown_word_0c']}"
        )


def roles(shown, plugin_limit, *, native_context, as_json):
    if as_json:
        print(json.dumps({
            "selection": "raw-role-census-with-native-defaults",
            "roles": shown, "native_context": native_context,
        }, indent=2, sort_keys=True))
        return
    print(f"native-context\t{native_context['resolution']}\tcensus=raw-catalog")
    for row in shown:
        plugins = "; ".join(
            f"{item['dll']}({item['binding_count']})"
            for item in row["plugins"][: plugin_limit]
        )
        surface_counts = row.get("binding_surface_counts", {})
        surfaces = ",".join(f"{name}:{count}" for name, count in surface_counts.items())
        surface_text = f"\tsurfaces={surfaces}" if surfaces else ""
        print(
            f"role\t{row['role_hex']}\tbindings={row['binding_count']}\t"
            f"categories={row['category_count']}{surface_text}\t{plugins}"
        )


def category(payload, limit, *, as_json):
    category = payload["category"]
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(f"native-context\t{payload['native_context']['resolution']}\tfunctions=raw-catalog")
    print(
        f"category\t{category['category_id']}\t{category['name']}\t"
        f"db={category['database']}\tshort={category['short_name']}\tgeneration={category['generation']}"
    )
    print("plugins")
    for row in payload["plugins"][: limit]:
        print(f"{row['role_hex']}\t{row['dll']}")
    print("functions")
    for row in payload["functions"][: limit]:
        print(f"{row['function_hex']}\t{row['name']}\t{row['description']}")


def canbus(rows, *, as_json):
    if as_json:
        print(json.dumps(rows, indent=2, sort_keys=True))
        return
    print("selection\traw-catalog")
    for index, row in enumerate(rows):
        if index:
            print()
        print(
            f"vehicle={row['vehicle_type']} name={row['vehicle_name']} "
            f"can_bus_car_id={row['can_bus_car_id']} options={row['option_count']} "
            f"placement_variants={row['placement_variant_count']}"
        )
        for variant_index, variant in enumerate(row["placement_variants"], 1):
            if row["placement_variant_count"] > 1:
                print(f"  variant {variant_index}: groups={','.join(variant['component_groups'])}")
            by_bus: dict[tuple[int, str, tuple[str, ...]], list[dict[str, Any]]] = {}
            for placement in variant["placements"]:
                key = (
                    placement["bus_index"],
                    placement["bus_name"],
                    tuple(placement["gateway_names"]),
                )
                by_bus.setdefault(key, []).append(placement)
            for (bus_index, bus_name, gateways), placements in sorted(by_bus.items()):
                gateway = ", ".join(gateways) if gateways else "-"
                print(f"  {bus_name} index={bus_index} gateway={gateway}")
                for placement in placements:
                    junction = placement["junction_name"]
                    suffix = f" via {junction}" if junction and junction != "-" else ""
                    print(f"    {placement['component_hex']} {placement['ecu_domain']}{suffix}")


def cuw(payload, outer, vehicle, routes, contact, descriptor, *, verbose, as_json):
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(payload["path"])
    print(f"format\t0x{outer['format_type']:02X}\tfirst_member={outer.get('name')}\tpayload={outer.get('payload_length')}\tvalidation={outer.get('validation')}")
    for key in ("VehicleName", "ModelYear", "ContactType", "KindOfECU", "RequiredSpecReproVer", "ReproMethod"):
        if vehicle.get(key):
            print(f"vehicle.{key}\t{vehicle[key]}")
    for node in payload["nodes"]:
        print(
            f"{node['section']}\tdiag_id={node['diag_id']}\t"
            f"required_spec={node['required_spec_repro_ver']}\tlogical_blocks={node['logical_blocks']}"
        )
    if payload["new_cids"]:
        print("new_cids\t" + ", ".join(payload["new_cids"]))
    if payload["target_calibrations"]:
        print("target_calibrations\t" + ", ".join(payload["target_calibrations"]))
    selection = payload["gtsplus_selection"]
    if "error" in selection["model"]:
        print("gtsplus_selection_error\t" + json.dumps(selection["model"]["error"], sort_keys=True))
    else:
        engine = selection["engine"]
        print(f"gtsplus_engine\t{engine['name']}\tselector={engine['selector']}\t{engine['reason']}")
        for binding in selection["roles"]:
            parameter = binding["parameter"]
            print(f"gtsplus_binding\t{binding['role']}\tcpu={binding['cpu_index']}\tnode={binding['node_index']}"
                  f"\t{parameter['parameter_file']}\t{binding.get('dll', '')}"
                  f"\t{json.dumps(parameter.get('error'), sort_keys=True)}")
        for precondition in selection.get("role_preconditions", []):
            print("gtsplus_binding_precondition\t" + json.dumps(precondition, sort_keys=True))
    if routes:
        print("gtsplus_route")
        for route in routes:
            print(_format_row(route))
    else:
        print(f"gtsplus_route\t(no exact selected factory row; runtime ContactType={contact!r})")
    if verbose:
        for section, fields in descriptor.items():
            print(f"[{section}]")
            for key, value in fields.items():
                print(f"{key}={value}")


def pe(payload, data, path, *, limit, as_json):
    exports = payload["exports"]
    imports = payload["imports"]
    strings = payload["strings"]
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(path)
    print(f"image_base\t0x{payload['image_base']:X}\tmachine={payload['machine']}\tsize={len(data)}")
    if exports:
        print("exports")
        for item in exports[: limit]:
            print(f"0x{item['rva']:08X}\t{item['name']}")
    if imports:
        print("imports")
        for item in imports[: limit]:
            print(f"{item['dll']}!{item['name']}")
    if strings:
        print("strings")
        for value in strings:
            print(value)


def recover_bodies(manifest, *, as_json):
    if as_json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        count = manifest["recovered_plaintext_body_count"]
        installed = manifest["installed_protected_body_count"]
        print(f"GTS+ {manifest['gtsplus_version']}: recovered {count}/{installed} protected PE bodies")
        print(f"output\t{manifest['output_root']}")
        print(f"manifest\t{Path(manifest['output_root']) / 'manifest.json'}")


def recover_cuw_bodies(manifest, *, as_json):
    if as_json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"CUWPlus: recovered {manifest['recovered_body_count']}/{manifest['protected_body_count']} protected PE bodies")
        print(f"native\t{manifest['native_count']}")
        print(f"managed\t{manifest['managed_count']} (mixed={manifest['mixed_managed_count']})")
        print(f"output\t{manifest['output_root']}")
        print(f"manifest\t{Path(manifest['output_root']) / 'manifest.json'}")


def recover_aux_bodies(manifest, *, as_json):
    if as_json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"GTS+ auxiliary: recovered {manifest['recovered_body_count']}/{manifest['protected_body_count']} protected PE bodies")
        print(f"native\t{manifest['native_count']}")
        print(f"managed\t{manifest['managed_count']} (mixed={manifest['mixed_managed_count']})")
        print(f"output\t{manifest['output_root']}")
        print(f"manifest\t{Path(manifest['output_root']) / 'manifest.json'}")


def recover_all_bodies(manifest, *, as_json):
    if as_json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"GTS+ protected bodies: recovered {manifest['recovered_body_count']}/{manifest['protected_body_count']}")
        for name, row in manifest["components"].items():
            print(f"{name}\t{row['count']}\t{row['method']}")
        print(f"output\t{manifest['output_root']}")
        print(f"manifest\t{Path(manifest['output_root']) / 'manifest.json'}")


def registry_bundle(out, payload, *, as_json):
    if as_json:
        print(json.dumps({
            "path": str(out),
            "schema": payload["schema"],
            "release": payload["release"],
            "regions": {key: value["counts"] for key, value in payload["regions"].items()},
        }, sort_keys=True))
        return
    print(out)
    for region, value in payload["regions"].items():
        counts = value["counts"]
        print(
            f"{region}\traw_categories={counts['raw_category_row_count']}\t"
            f"initial_categories={counts['initial_category_count']}\t"
            f"selected_categories={counts['selected_category_count']}"
        )


def registry_json_text(payload, *, compact):
    return json.dumps(payload, indent=None if compact else 2, sort_keys=True, separators=(",", ":") if compact else None) + "\n"


def vdas_value(selected, *, as_json):
        if isinstance(selected, (dict, list)) or as_json:
            print(json.dumps(selected, indent=2, ensure_ascii=False, sort_keys=True))
        elif selected is None:
            print("null")
        else:
            print(selected)


def vdas_document(payload, *, as_json):
    if as_json:
        print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
        return

    document = payload["document"]
    gts = document.get("Gts") if isinstance(document.get("Gts"), dict) else document.get("gts")
    print(f"vdas\t{payload['path']}\tentries={len(payload['archive_entries'])}\tjson_bytes={payload['json_bytes']}")
    print("entries\t" + ",".join(payload["archive_entries"]))
    if isinstance(gts, dict):
        version = gts.get("FormatVersion")
        if isinstance(version, dict):
            version = version.get("Version")
        print(f"format_version\t{version if version is not None else '-'}")
        for key in ("Ddr", "AduDdr", "PcsFfd", "LcsFfd", "Tss3Ffd", "AdsFfd", "AdsEng", "AduFfd", "PcsImg", "PvmImg", "AdsImg", "RcImg", "DmcImg", "AbsoluteTime"):
            section = gts.get(key)
            data = section.get("Data") if isinstance(section, dict) else None
            if data not in (None, ""):
                length = len(data) if isinstance(data, (str, list, dict)) else 1
                print(f"payload\t{key}\tpresent\tlength={length}")
