#!/usr/bin/env python3
"""Build an evidence-graded static-analysis coverage matrix for 8965H1202000.

This is a navigation/denominator artifact. It never upgrades a raw transfer
candidate merely because the canonical Sienna function has a useful name.
Coverage is promoted only by one of:
  * exact complete-body transfer;
  * a unique complete-instruction-shape target that is present in a tracked
    target-native evidence artifact;
  * an explicitly complete generated-surface recensus (currently application
    RDBI/RoutineControl and the complete steering-supervisor direct-stage set).
A tracked target-native role-recovery report may also promote a canonical role when
the foreign function was independently recovered even though generated restructuring
prevents exact/unique-shape matching. Everything else remains structural-only or unresolved.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DID = struct.Struct("<HHIII")
RID_CB = struct.Struct("<HHII")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_codeflash(path: Path) -> bytes:
    data = path.read_bytes()
    if len(data) != 0x100000:
        raise ValueError(f"expected 1 MiB CodeFlash: {path} got {len(data):#x}")
    return data


def canonical_supervisor_calls() -> set[int]:
    records = []
    for line in (REPO / "data/generated/decompilations.jsonl").read_text().splitlines():
        r = json.loads(line)
        if "entry_addr" in r:
            records.append(r)
    by_name = {r["name"]: int(r["entry_addr"], 16) for r in records}
    root = next(r for r in records if int(r["entry_addr"], 16) == 0xCB86E)
    out = set()
    for line in root["decompiled_c"].splitlines():
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\(\);", line)
        if not match:
            continue
        name = match.group(1)
        if name.startswith("FUN_"):
            out.add(int(name[4:], 16))
        elif name in by_name:
            out.add(by_name[name])
    if len(out) != 94:
        raise ValueError(f"canonical supervisor direct-stage denominator drifted: {len(out)}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--ledger",
        type=Path,
        default=REPO / "data/generated/corolla_8965H1202000_named_function_transfer_ledger.json",
    )
    ap.add_argument(
        "--structural",
        type=Path,
        default=REPO / "data/generated/corolla_8965H1202000_structural_function_transfer.json",
    )
    ap.add_argument(
        "--sienna-image",
        type=Path,
        default=REPO / "firmware/RH850_P1M-E_CodeFlash.bin",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=REPO / "data/generated/corolla_8965H1202000_static_coverage_matrix.json",
    )
    args = ap.parse_args()

    ledger = load_json(args.ledger)
    rows = ledger["functions"]
    structural = load_json(args.structural)
    sienna = load_codeflash(args.sienna_image)

    # Unique target->reference map from the independent structural artifact.
    target_to_reference = {
        int(r["target_entry"], 16): int(r["reference_entry"], 16)
        for r in structural["matches"]
    }

    # Every H function explicitly carried in a compact target-native evidence set.
    evidence_files = sorted((REPO / "data/generated").glob("corolla_8965H1202000_*decompiler_evidence.json"))
    evidence_target_entries: dict[int, set[str]] = defaultdict(set)
    evidence_file_hashes = {}
    for path in evidence_files:
        doc = load_json(path)
        if doc.get("software_id") != "8965H1202000":
            continue
        evidence_file_hashes[str(path.relative_to(REPO))] = sha256(path.read_bytes())
        for record in doc.get("functions", []):
            raw = record.get("entry") or record.get("entry_addr")
            if raw is None:
                continue
            evidence_target_entries[int(raw, 16)].add(str(path.relative_to(REPO)))

    evidence_reference_entries: dict[int, set[str]] = defaultdict(set)
    h_native_unpaired_count = 0
    for target, owners in evidence_target_entries.items():
        reference = target_to_reference.get(target)
        if reference is None:
            h_native_unpaired_count += 1
            continue
        evidence_reference_entries[reference].update(owners)

    # Explicit target-native high-level role recovery. This is intentionally
    # separate from unique-shape transfer and from generated-surface recensus.
    role_recovery: dict[int, dict] = {}
    orchestration_path = REPO / "data/generated/corolla_8965H1202000_system_orchestration.json"
    if orchestration_path.is_file():
        orchestration = load_json(orchestration_path)
        orchestration_rel = str(orchestration_path.relative_to(REPO))
        evidence_file_hashes[orchestration_rel] = sha256(orchestration_path.read_bytes())
        system_ev_path = REPO / orchestration["evidence"]["decompiler_evidence"]
        system_ev = load_json(system_ev_path)
        system_targets = {int(r["entry"], 16) for r in system_ev.get("functions", [])}
        reset_target = int(system_ev["reset_0x1f2"]["entry"], 16)
        for item in orchestration.get("scheduler_system_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in system_targets and target != reset_target:
                raise ValueError(f"orchestration role target lacks tracked target-native evidence: {target:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": orchestration_rel,
                "evidence": orchestration["evidence"]["decompiler_evidence"],
                "role": item["role"],
            }

    can_com_path = REPO / "data/generated/corolla_8965H1202000_can_com.json"
    if can_com_path.is_file():
        can_com = load_json(can_com_path)
        can_com_rel = str(can_com_path.relative_to(REPO))
        evidence_file_hashes[can_com_rel] = sha256(can_com_path.read_bytes())
        can_ev_path = REPO / can_com["evidence"]["decompiler_evidence"]
        can_ev = load_json(can_ev_path)
        can_targets = {int(r["entry"], 16) for r in can_ev.get("functions", [])}
        for item in can_com.get("can_com_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in can_targets:
                raise ValueError(f"CAN/COM role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": can_com_rel,
                "evidence": can_com["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }
        route_names = {
            "special_rx_demux": "application_can_special_rx_demux",
            "normal_rx_demux": "application_can_normal_rx_demux",
            "pdu_transmit_router": "application_pdu_transmit_router",
            "pdu_rx_router": "application_pdu_rx_router",
        }
        for key, role_name in route_names.items():
            item = can_com.get("supporting_route_chain", {}).get(key)
            if not item:
                continue
            ref = int(item["sienna"], 16); target = int(item["h"], 16)
            if target not in can_targets:
                raise ValueError(f"CAN/COM supporting-route target lacks tracked H evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["h"],
                "report": can_com_rel,
                "evidence": can_com["evidence"]["decompiler_evidence"],
                "role": role_name,
            }

    storage_path = REPO / "data/generated/corolla_8965H1202000_storage_nvm.json"
    if storage_path.is_file():
        storage = load_json(storage_path)
        storage_rel = str(storage_path.relative_to(REPO))
        evidence_file_hashes[storage_rel] = sha256(storage_path.read_bytes())
        storage_ev_path = REPO / storage["evidence"]["decompiler_evidence"]
        storage_ev = load_json(storage_ev_path)
        storage_targets = {int(r["entry"], 16) for r in storage_ev.get("functions", [])}
        for item in storage.get("storage_nvm_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in storage_targets:
                raise ValueError(f"storage/NvM role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": storage_rel,
                "evidence": storage["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }

    xcp_path = REPO / "data/generated/corolla_8965H1202000_xcp.json"
    if xcp_path.is_file():
        xcp = load_json(xcp_path)
        xcp_rel = str(xcp_path.relative_to(REPO))
        evidence_file_hashes[xcp_rel] = sha256(xcp_path.read_bytes())
        xcp_ev_path = REPO / xcp["evidence"]["decompiler_evidence"]
        xcp_ev = load_json(xcp_ev_path)
        xcp_targets = {int(r["entry"], 16) for r in xcp_ev.get("functions", [])}
        for item in xcp.get("xcp_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in xcp_targets:
                raise ValueError(f"XCP role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": xcp_rel,
                "evidence": xcp["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }

    motor_path = REPO / "data/generated/corolla_8965H1202000_motor_control.json"
    if motor_path.is_file():
        motor = load_json(motor_path)
        motor_rel = str(motor_path.relative_to(REPO))
        evidence_file_hashes[motor_rel] = sha256(motor_path.read_bytes())
        motor_ev_path = REPO / motor["evidence"]["decompiler_evidence"]
        motor_ev = load_json(motor_ev_path)
        motor_targets = {int(r["entry"], 16) for r in motor_ev.get("functions", [])}
        for item in motor.get("motor_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in motor_targets:
                raise ValueError(f"motor-control role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": motor_rel,
                "evidence": motor["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }

    secoc_path = REPO / "data/generated/corolla_8965H1202000_secoc_surface.json"
    if secoc_path.is_file():
        secoc = load_json(secoc_path)
        secoc_rel = str(secoc_path.relative_to(REPO))
        evidence_file_hashes[secoc_rel] = sha256(secoc_path.read_bytes())
        secoc_ev_path = REPO / secoc["evidence"]["decompiler_evidence"]
        secoc_ev = load_json(secoc_ev_path)
        secoc_targets = {int(r["target_entry"], 16) for r in secoc_ev.get("functions", [])}
        for item in secoc.get("secoc_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in secoc_targets:
                raise ValueError(f"SecOC/ICU-S role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": secoc_rel,
                "evidence": secoc["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }

    crypto_path = REPO / "data/generated/corolla_8965H1202000_crypto_residue.json"
    if crypto_path.is_file():
        crypto = load_json(crypto_path)
        crypto_rel = str(crypto_path.relative_to(REPO))
        evidence_file_hashes[crypto_rel] = sha256(crypto_path.read_bytes())
        crypto_ev_path = REPO / crypto["evidence"]["decompiler_evidence"]
        crypto_ev = load_json(crypto_ev_path)
        crypto_targets = {int(r["target_entry"], 16) for r in crypto_ev.get("functions", [])}
        for item in crypto.get("crypto_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in crypto_targets:
                raise ValueError(f"crypto role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": crypto_rel,
                "evidence": crypto["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }

    steering_nested_path = REPO / "data/generated/corolla_8965H1202000_steering_nested.json"
    steering_nested = None
    if steering_nested_path.is_file():
        steering_nested = load_json(steering_nested_path)
        steering_nested_rel = str(steering_nested_path.relative_to(REPO))
        evidence_file_hashes[steering_nested_rel] = sha256(steering_nested_path.read_bytes())
        steering_ev_path = REPO / steering_nested["evidence"]["decompiler_evidence"]
        steering_ev = load_json(steering_ev_path)
        steering_targets = {int(r["entry"], 16) for r in steering_ev.get("functions", [])}
        for item in steering_nested.get("steering_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in steering_targets:
                raise ValueError(f"steering role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": steering_nested_rel,
                "evidence": steering_nested["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }

    diagnostic_residue_path = REPO / "data/generated/corolla_8965H1202000_diagnostic_residue.json"
    diagnostic_residue = None
    if diagnostic_residue_path.is_file():
        diagnostic_residue = load_json(diagnostic_residue_path)
        diagnostic_residue_rel = str(diagnostic_residue_path.relative_to(REPO))
        evidence_file_hashes[diagnostic_residue_rel] = sha256(diagnostic_residue_path.read_bytes())
        diagnostic_ev_path = REPO / diagnostic_residue["evidence"]["decompiler_evidence"]
        diagnostic_ev = load_json(diagnostic_ev_path)
        diagnostic_targets = {int(r["entry"], 16) for r in diagnostic_ev.get("functions", [])}
        for item in diagnostic_residue.get("diagnostic_role_closure", []):
            ref = int(item["reference_entry"], 16)
            target = int(item["target_entry"], 16)
            if target not in diagnostic_targets:
                raise ValueError(f"diagnostic role target lacks tracked target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {
                "target_entry": item["target_entry"],
                "report": diagnostic_residue_rel,
                "evidence": diagnostic_residue["evidence"]["decompiler_evidence"],
                "role": item["reference_name"],
            }

    # Explicit generated-surface recensuses. These are not function homology:
    # they prove the foreign generated surface was exhaustively re-enumerated.
    recensus: dict[int, set[str]] = defaultdict(set)

    # Sienna application RDBI producers: complete foreign RDBI producer recensus exists.
    for i in range(242):
        _did, _length, callback, _aux, _tail = DID.unpack_from(sienna, 0x2941C + i * DID.size)
        if callback:
            recensus[callback].add("application-rdbi-complete-producer-recensus")

    # Sienna RoutineControl precondition/action callbacks: complete 19-RID H recensus exists.
    for i in range(19):
        _rid, _pad, precondition, action = RID_CB.unpack_from(sienna, 0x25804 + i * RID_CB.size)
        if precondition:
            recensus[precondition].add("application-routinecontrol-complete-callback-recensus")
        if action:
            recensus[action].add("application-routinecontrol-complete-callback-recensus")

    # Every canonical direct steering-supervisor stage has an explicit row in the 94->123 ledger.
    for entry in canonical_supervisor_calls():
        recensus[entry].add("steering-supervisor-complete-direct-stage-ledger")

    # The classic 0x131/0x2E4 arbitration+latch trio is removed/replaced as one H surface.
    if steering_nested is not None:
        for item in steering_nested.get("classic_command_surface_recensus", []):
            recensus[int(item["reference_entry"], 16)].add("steering-classic-command-mode-complete-replacement-recensus")

    if diagnostic_residue is not None:
        for item in diagnostic_residue.get("diagnostic_surface_recensus", []):
            recensus[int(item["reference_entry"], 16)].add("diagnostic-complete-target-surface-recensus")

    deadline_surface_path = REPO / "data/generated/corolla_8965H1202000_deadline_monitor_surface.json"
    if deadline_surface_path.is_file():
        deadline_surface = load_json(deadline_surface_path)
        deadline_surface_rel = str(deadline_surface_path.relative_to(REPO))
        evidence_file_hashes[deadline_surface_rel] = sha256(deadline_surface_path.read_bytes())
        for item in deadline_surface.get("surface_recensus", []):
            recensus[int(item["reference_entry"], 16)].add("deadline-monitor-complete-three-table-recensus")

    plausibility_path = REPO / "data/generated/corolla_8965H1202000_plausibility_monitor.json"
    if plausibility_path.is_file():
        plausibility = load_json(plausibility_path)
        plausibility_rel = str(plausibility_path.relative_to(REPO))
        evidence_file_hashes[plausibility_rel] = sha256(plausibility_path.read_bytes())
        plausibility_ev_path = REPO / plausibility["evidence"]["decompiler_evidence"]
        plausibility_ev = load_json(plausibility_ev_path)
        plausibility_targets = {int(r["entry"], 16) for r in plausibility_ev.get("functions", [])}
        for item in plausibility.get("role_closure", []):
            ref = int(item["reference_entry"], 16); target = int(item["target_entry"], 16)
            if target not in plausibility_targets:
                raise ValueError(f"plausibility role target lacks evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {"target_entry":item["target_entry"],"report":plausibility_rel,"evidence":plausibility["evidence"]["decompiler_evidence"],"role":item["reference_name"]}

    small_adapters_path = REPO / "data/generated/corolla_8965H1202000_small_adapters.json"
    if small_adapters_path.is_file():
        small_adapters = load_json(small_adapters_path)
        small_adapters_rel = str(small_adapters_path.relative_to(REPO))
        evidence_file_hashes[small_adapters_rel] = sha256(small_adapters_path.read_bytes())
        small_ev_path = REPO / small_adapters["evidence"]["decompiler_evidence"]
        small_ev = load_json(small_ev_path)
        small_targets = {int(r["entry"], 16) for r in small_ev.get("functions", [])}
        for item in small_adapters.get("role_closure", []):
            ref = int(item["reference_entry"], 16); target = int(item["target_entry"], 16)
            if target not in small_targets:
                raise ValueError(f"small-adapter role target lacks evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {"target_entry":item["target_entry"],"report":small_adapters_rel,"evidence":small_adapters["evidence"]["decompiler_evidence"],"role":item["reference_name"]}

    veneer_bank_path = REPO / "data/generated/corolla_8965H1202000_veneer_bank.json"
    if veneer_bank_path.is_file():
        veneer_bank = load_json(veneer_bank_path)
        veneer_bank_rel = str(veneer_bank_path.relative_to(REPO))
        evidence_file_hashes[veneer_bank_rel] = sha256(veneer_bank_path.read_bytes())
        veneer_targets = {int(x, 16) for x in veneer_bank.get("target_evidence_entries", [])}
        for item in veneer_bank.get("role_closure", []):
            ref = int(item["reference_entry"], 16); target = int(item["target_entry"], 16)
            if target not in veneer_targets:
                raise ValueError(f"veneer-bank role target lacks raw slot evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {"target_entry":item["target_entry"],"report":veneer_bank_rel,"evidence":veneer_bank_rel,"role":item["role"]}
        for item in veneer_bank.get("surface_recensus", []):
            recensus[int(item["reference_entry"], 16)].add("high-page-veneer-bank-complete-recensus")

    final_residue_path = REPO / "data/generated/corolla_8965H1202000_final_named_residue.json"
    if final_residue_path.is_file():
        final_residue = load_json(final_residue_path)
        final_residue_rel = str(final_residue_path.relative_to(REPO))
        evidence_file_hashes[final_residue_rel] = sha256(final_residue_path.read_bytes())
        final_evidence_path = REPO / final_residue["evidence"]["final_compact_evidence"]
        final_evidence_rel = str(final_evidence_path.relative_to(REPO))
        evidence_file_hashes[final_evidence_rel] = sha256(final_evidence_path.read_bytes())
        final_targets = {int(x,16) for x in final_residue.get("target_evidence_entries", [])}
        if not final_residue.get("static_conclusion", {}).get("all_34_prior_unresolved_names_closed"):
            raise ValueError("final named-residue closure is incomplete")
        for item in final_residue.get("role_closure", []):
            ref=int(item["reference_entry"],16);target=int(item["target_entry"],16)
            if target not in final_targets:
                raise ValueError(f"final role target lacks target-native evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate final named-residue role recovery: {ref:#x}")
            role_recovery[ref]={"target_entry":item["target_entry"],"report":final_residue_rel,"evidence":final_evidence_rel,"role":item["role"]}
        for item in final_residue.get("surface_recensus", []):
            recensus[int(item["reference_entry"],16)].add("boot-eiint-complete-table-recensus")

    keyless_event_path = REPO / "data/generated/corolla_8965H1202000_keyless_event_formatter.json"
    if keyless_event_path.is_file():
        keyless_event = load_json(keyless_event_path)
        keyless_event_rel = str(keyless_event_path.relative_to(REPO))
        evidence_file_hashes[keyless_event_rel] = sha256(keyless_event_path.read_bytes())
        keyless_event_ev_path = REPO / keyless_event["evidence"]["decompiler_evidence"]
        keyless_event_ev_rel = str(keyless_event_ev_path.relative_to(REPO))
        evidence_file_hashes[keyless_event_ev_rel] = sha256(keyless_event_ev_path.read_bytes())
        keyless_event_targets = {int(x,16) for x in keyless_event.get("target_evidence_entries", [])}
        for item in keyless_event.get("role_closure", []):
            ref=int(item["reference_entry"],16); target=int(item["target_entry"],16)
            if target not in keyless_event_targets:
                raise ValueError(f"keyless event formatter target lacks evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate keyless event formatter role recovery: {ref:#x}")
            role_recovery[ref]={"target_entry":item["target_entry"],"report":keyless_event_rel,"evidence":keyless_event_ev_rel,"role":item["role"]}

    direct_call_surface_path = REPO / "data/generated/corolla_8965H1202000_direct_call_surface.json"
    if direct_call_surface_path.is_file():
        direct_call_surface = load_json(direct_call_surface_path)
        direct_call_surface_rel = str(direct_call_surface_path.relative_to(REPO))
        evidence_file_hashes[direct_call_surface_rel] = sha256(direct_call_surface_path.read_bytes())
        direct_call_evidence_path = REPO / direct_call_surface["evidence"]["call_surface"]
        evidence_file_hashes[str(direct_call_evidence_path.relative_to(REPO))] = sha256(direct_call_evidence_path.read_bytes())
        if not direct_call_surface.get("static_conclusion", {}).get("target_literal_call_graph_closed"):
            raise ValueError("H direct-call graph recensus is not closed")
        for item in direct_call_surface.get("surface_recensus", []):
            recensus[int(item["reference_entry"],16)].add("clean-h-direct-call-graph-complete-recensus")

    app_interrupt_bodies_path = REPO / "data/generated/corolla_8965H1202000_application_interrupt_bodies.json"
    if app_interrupt_bodies_path.is_file():
        app_interrupt_bodies = load_json(app_interrupt_bodies_path)
        app_interrupt_bodies_rel = str(app_interrupt_bodies_path.relative_to(REPO))
        evidence_file_hashes[app_interrupt_bodies_rel] = sha256(app_interrupt_bodies_path.read_bytes())
        app_interrupt_targets = {int(x,16) for x in app_interrupt_bodies.get("target_evidence_entries", [])}
        for item in app_interrupt_bodies.get("role_closure", []):
            ref=int(item["reference_entry"],16);target=int(item["target_entry"],16)
            if target not in app_interrupt_targets: raise ValueError(f"interrupt body target lacks evidence: {target:#x}")
            if ref in role_recovery: raise ValueError(f"duplicate interrupt body recovery: {ref:#x}")
            role_recovery[ref]={"target_entry":item["target_entry"],"report":app_interrupt_bodies_rel,"evidence":app_interrupt_bodies["evidence"]["decompiler_evidence"],"role":item["role"]}

    app_vectors_path = REPO / "data/generated/corolla_8965H1202000_application_interrupt_vectors.json"
    if app_vectors_path.is_file():
        app_vectors = load_json(app_vectors_path)
        app_vectors_rel = str(app_vectors_path.relative_to(REPO))
        evidence_file_hashes[app_vectors_rel] = sha256(app_vectors_path.read_bytes())
        vector_targets = {int(x,16) for x in app_vectors.get("target_evidence_entries", [])}
        for item in app_vectors.get("role_closure", []):
            ref=int(item["reference_entry"],16);target=int(item["target_entry"],16)
            if target not in vector_targets: raise ValueError(f"vector role target lacks raw evidence: {target:#x}")
            if ref in role_recovery: raise ValueError(f"duplicate vector role recovery: {ref:#x}")
            role_recovery[ref]={"target_entry":item["target_entry"],"report":app_vectors_rel,"evidence":app_vectors_rel,"role":item["role"]}

    app_transport_path = REPO / "data/generated/corolla_8965H1202000_application_transport_residue.json"
    if app_transport_path.is_file():
        app_transport = load_json(app_transport_path)
        app_transport_rel = str(app_transport_path.relative_to(REPO))
        evidence_file_hashes[app_transport_rel] = sha256(app_transport_path.read_bytes())
        app_transport_targets = {int(x,16) for x in app_transport.get("target_evidence_entries", [])}
        for item in app_transport.get("role_closure", []):
            ref = int(item["reference_entry"],16); target = int(item["target_entry"],16)
            # supporting CAN routes may already be credited from the parent CAN report.
            if ref in role_recovery:
                existing = int(role_recovery[ref]["target_entry"],16)
                if existing != target:
                    raise ValueError(f"transport role conflicts at {ref:#x}: {existing:#x}!={target:#x}")
                continue
            if target not in app_transport_targets:
                raise ValueError(f"application transport target lacks evidence: {target:#x}")
            role_recovery[ref] = {"target_entry":item["target_entry"],"report":app_transport_rel,"evidence":app_transport["evidence"]["decompiler_evidence"],"role":item["role"]}
        for item in app_transport.get("surface_recensus", []):
            recensus[int(item["reference_entry"],16)].add("application-transport-complete-pdu-recensus")

    app_callbacks_path = REPO / "data/generated/corolla_8965H1202000_application_callback_tables.json"
    if app_callbacks_path.is_file():
        app_callbacks = load_json(app_callbacks_path)
        app_callbacks_rel = str(app_callbacks_path.relative_to(REPO))
        evidence_file_hashes[app_callbacks_rel] = sha256(app_callbacks_path.read_bytes())
        app_callback_targets = {int(x, 16) for x in app_callbacks.get("target_evidence_entries", [])}
        for item in app_callbacks.get("role_closure", []):
            ref = int(item["reference_entry"], 16); target = int(item["target_entry"], 16)
            if target not in app_callback_targets:
                raise ValueError(f"application callback role target lacks raw table evidence: {target:#x}")
            if ref in role_recovery:
                raise ValueError(f"duplicate target-native role recovery for {ref:#x}")
            role_recovery[ref] = {"target_entry":item["target_entry"],"report":app_callbacks_rel,"evidence":app_callbacks_rel,"role":item["role"]}
        for item in app_callbacks.get("surface_recensus", []):
            recensus[int(item["reference_entry"], 16)].add("application-async-operation-complete-table-recensus")

    # Classify each canonical named function conservatively.
    classified = []
    for row in rows:
        ref = int(row["reference_entry"], 16)
        status = row["status"]
        target = row.get("target_entry")
        target_int = int(target, 16) if target else None
        owners = sorted(evidence_reference_entries.get(ref, set()))
        census = sorted(recensus.get(ref, set()))

        if status == "exact-byte-transfer":
            coverage = "verified-exact-body-transfer"
            basis = ["complete canonical body is byte-identical at resolved H target"]
        elif ref in role_recovery:
            recovered = role_recovery[ref]
            coverage = "target-native-role-recovered"
            basis = [
                f"target-native role recovery: {recovered['role']}",
                f"report:{recovered['report']}",
                f"target-native:{recovered['evidence']}",
            ]
            target = recovered["target_entry"]
            target_int = int(target, 16)
        elif status == "unique-instruction-shape-candidate" and owners:
            coverage = "target-native-inspected-unique-shape"
            basis = ["unique complete instruction-shape target"] + [f"target-native:{x}" for x in owners]
        elif census:
            coverage = "target-surface-recensused"
            basis = census
        elif status == "unique-instruction-shape-candidate":
            coverage = "structural-candidate-only"
            basis = ["unique complete instruction-shape match exists; target-native operand/dataflow not yet recorded"]
        else:
            coverage = "genuinely-unresolved"
            basis = ["no exact transfer, no inspected unique structural target, and no complete generated-surface recensus"]

        classified.append(
            {
                "reference_entry": row["reference_entry"],
                "reference_name": row["reference_name"],
                "body_size": row["body_size"],
                "semantic_tags": row["semantic_tags"],
                "transfer_status": status,
                "target_entry": target,
                "coverage": coverage,
                "coverage_basis": basis,
                "target_native_evidence_files": (owners if ref not in role_recovery else [role_recovery[ref]["evidence"]]),
                "role_recovery": role_recovery.get(ref),
                "surface_recensus": census,
            }
        )

    counts = Counter(row["coverage"] for row in classified)
    tag_counts: dict[str, Counter] = defaultdict(Counter)
    for row in classified:
        tags = row["semantic_tags"] or ["untagged"]
        for tag in tags:
            tag_counts[tag][row["coverage"]] += 1

    unresolved = [row for row in classified if row["coverage"] == "genuinely-unresolved"]
    structural_only = [row for row in classified if row["coverage"] == "structural-candidate-only"]

    payload = {
        "schema": "corolla-8965H1202000-static-coverage-matrix-v1",
        "evidence_boundary": (
            "Navigation/denominator artifact. Surface recensus means the foreign generated surface was exhaustively re-enumerated; it is not function homology. Target-native role recovery means a foreign role was independently reconstructed and pinned; it is not byte/shape identity. Structural-candidate-only is not semantic transfer. Genuinely-unresolved means only that none of the tracked promotion conditions apply."
        ),
        "source": {
            "named_transfer_ledger": str(args.ledger.relative_to(REPO)),
            "named_transfer_ledger_sha256": sha256(args.ledger.read_bytes()),
            "structural_transfer": str(args.structural.relative_to(REPO)),
            "structural_transfer_sha256": sha256(args.structural.read_bytes()),
            "sienna_codeflash_sha256": sha256(sienna),
            "target_native_evidence_files": evidence_file_hashes,
        },
        "summary": {
            "named_function_count": len(classified),
            "coverage_counts": dict(sorted(counts.items())),
            "genuinely_unresolved_count": len(unresolved),
            "structural_candidate_only_count": len(structural_only),
            "h_native_evidence_functions_without_unique_sienna_pair": h_native_unpaired_count,
            "surface_recensus_reference_function_count": sum(bool(v) for v in recensus.values()),
            "target_native_inspected_reference_function_count": len(evidence_reference_entries),
            "tag_coverage_counts": {tag: dict(sorted(counter.items())) for tag, counter in sorted(tag_counts.items())},
        },
        "functions": classified,
        "genuinely_unresolved": unresolved,
        "structural_candidate_only": structural_only,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
