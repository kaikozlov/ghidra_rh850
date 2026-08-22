#!/usr/bin/env python3
"""Join semantic runtime resolution, raw SecOC records, and verified RAM geometry.

This tool is deliberately fail-closed.  Application/SecOC structure may resolve
on a foreign image while RAM execution/retention geometry remains unresolved;
in that case the manifest is useful for comparison but is not runtime-build
ready.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_GEOMETRY_DB = REPO / "data" / "variant_ram_exec_requirements.json"
DEFAULT_BOOTSTRAP_DB = REPO / "data" / "variant_bootstrap_profiles.json"
STEERING_IDS = (0x2E4, 0x131)
RECORD_STRIDE = 0x50
CAN_ID_OFFSET = 0x0A
RAW_OFFSET_OFFSET = 0x28
PDU_ID_OFFSET = 0x34
SECURED_LENGTH_OFFSET = 0x3C


class ManifestError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

CODEFLASH_SIZE = 0x100000
RANGE_DUMP_SIZE = 0x200000


def load_codeflash(path: Path) -> tuple[bytes, dict]:
    raw = path.read_bytes()
    source = {
        "path": str(path),
        "size": len(raw),
        "sha256": sha256(raw),
    }
    if len(raw) == CODEFLASH_SIZE:
        source["normalization"] = "bare-codeflash"
        return raw, source
    if len(raw) == RANGE_DUMP_SIZE and raw[CODEFLASH_SIZE:] == b"\xff" * CODEFLASH_SIZE:
        source["normalization"] = "trim-all-ff-upper-1mib-from-2mib-range-dump"
        return raw[:CODEFLASH_SIZE], source
    raise ManifestError(
        f"CodeFlash input must be 1 MiB, or a 2 MiB range dump whose upper 1 MiB is all 0xFF; got {len(raw):#x} bytes"
    )


def as_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    return value if isinstance(value, int) else int(value, 0)


def hx(value: int | None) -> str | None:
    return None if value is None else f"0x{value:X}"


def s16(value: int) -> int:
    return value - 0x10000 if value & 0x8000 else value


def is_jarl22(image: bytes, off: int) -> bool:
    if off < 0 or off + 4 > len(image):
        return False
    hw = struct.unpack_from("<H", image, off)[0]
    # v850_func.sinc: op6_10=0x1e, reg2=lp(31).  addr22 high bits
    # occupy the low six bits; reg2 is the high five bits of this halfword.
    return ((hw >> 6) & 0x1F) == 0x1E and ((hw >> 11) & 0x1F) == 0x1F


def jarl22_target(image: bytes, off: int) -> int:
    if not is_jarl22(image, off):
        raise ManifestError(f"not a direct JARL disp22 at {off:#x}")
    ins = struct.unpack_from("<I", image, off)[0]
    high6 = ins & 0x3F
    if high6 & 0x20:
        high6 -= 0x40
    return (off + (high6 << 16) + (ins >> 16)) & 0xFFFFFFFF


def unique_hit(name: str, hits: list[int]) -> int:
    if len(hits) != 1:
        raise ManifestError(f"expected one raw {name} candidate, found {len(hits)}")
    return hits[0]


def recover_boot_handoff(image: bytes) -> dict:
    hits: list[int] = []
    for base in range(0, len(image) - 0x40, 2):
        if image[base:base + 4] != bytes.fromhex("82076100"):
            continue
        if not all(is_jarl22(image, base + 4 + 4 * i) for i in range(5)):
            continue
        if image[base + 24:base + 26] != bytes.fromhex("e051"):  # cmp r0,r10
            continue
        hits.append(base)
    base = unique_hit("boot-handoff", hits)
    return {
        "boot_application_handoff": hx(base),
        "boot_transition_call_targets": [hx(jarl22_target(image, base + 4 + 4 * i)) for i in range(5)],
        "boot_validity_call_index": 4,
    }


def recover_application_register_immediate(image: bytes, context: int, opcode: bytes, name: str) -> int:
    end = min(context + 0x80, len(image) - 6)
    for off in range(context, end, 2):
        if image[off:off + 2] == bytes.fromhex("7f00"):  # first jmp lp ends context init
            end = off
            break
    hits = [off for off in range(context, end, 2) if image[off:off + 2] == opcode]
    off = unique_hit(f"application-{name}-immediate", hits)
    return struct.unpack_from("<I", image, off + 2)[0]


def recover_application_gp(image: bytes, context: int) -> int:
    return recover_application_register_immediate(image, context, bytes.fromhex("2406"), "gp")


def recover_application_tp(image: bytes, context: int) -> int:
    return recover_application_register_immediate(image, context, bytes.fromhex("2506"), "tp")


def recover_tick_counter(image: bytes, foreground: int, gp: int) -> int:
    hits: list[int] = []
    for off in range(foreground, min(foreground + 0x100, len(image) - 10), 2):
        if image[off:off + 2] != bytes.fromhex("24f6"):
            continue
        if image[off + 4:off + 10] == bytes.fromhex("6008410a800b"):
            hits.append(off)
    off = unique_hit("foreground-tick-counter", hits)
    disp = s16(struct.unpack_from("<H", image, off + 2)[0])
    return (gp + disp) & 0xFFFFFFFF


def recover_com_rx(image: bytes) -> int:
    # Register/prologue-only prefix: no calibration addresses are embedded.
    prefix = bytes.fromhex("8207e1f006e8dd0007d81de0c3e2c5e1")
    hits: list[int] = []
    start = 0
    while True:
        off = image.find(prefix, start)
        if off < 0:
            break
        if off % 2 == 0:
            hits.append(off)
        start = off + 1
    return unique_hit("Com_RxIndication", hits)


def timeout_shape(image: bytes, off: int) -> bool:
    if off < 0 or off + 30 > len(image):
        return False
    checks = {
        0: "c600",      # zxh r6
        2: "0606",      # addi imm16,r6,r0
        8: "06f0",      # mov r6,ep
        10: "c4f1",     # add gp,ep
        12: "5e07",     # st.b r0,disp,ep
        16: "24f6",     # movea disp,gp,ep
        20: "c6f1",     # add r6,ep
        22: "6008",     # sld.bu
        24: "410a",     # add 1
        26: "800b",     # sst.b
        28: "7f00",     # jmp lp
    }
    return all(image[off + pos:off + pos + len(bytes.fromhex(hxv))] == bytes.fromhex(hxv)
               for pos, hxv in checks.items())


def recover_timeout_helper(image: bytes, com_rx: int, gp: int) -> dict:
    hits = [off for off in range(0, len(image) - 30, 2) if timeout_shape(image, off)]
    helper = unique_hit("COM-timeout-helper", hits)
    call_targets = [jarl22_target(image, off) for off in range(com_rx, min(com_rx + 0x120, len(image) - 4), 2)
                    if is_jarl22(image, off)]
    if helper not in call_targets:
        raise ManifestError("raw COM-timeout helper is not a direct callee of Com_RxIndication")
    validity_disp = s16(struct.unpack_from("<H", image, helper + 14)[0])
    counter_disp = s16(struct.unpack_from("<H", image, helper + 18)[0])
    return {
        "com_timeout_helper": hx(helper),
        "com_validity_base": hx((gp + validity_disp) & 0xFFFFFFFF),
        "com_update_counter_base": hx((gp + counter_disp) & 0xFFFFFFFF),
    }


def _previous_function_start(image: bytes, body: int) -> int:
    # These small generated helpers are emitted immediately after the preceding
    # function's ``dispose ... lp``.  Recover the start without inheriting a
    # calibration address.
    marker = bytes.fromhex("40063f00")
    lo = max(0, body - 0x60)
    prev = image.rfind(marker, lo, body)
    if prev < 0:
        raise ManifestError(f"could not recover queue-helper function boundary before {body:#x}")
    return prev + len(marker)


def queue_case_shape(image: bytes, cmp_off: int) -> tuple[list[int], int] | None:
    # Queue 1 is selected by ``cmp 1,r6`` in both known compiler layouts.  The
    # body writes descriptor/head/raw pointers to output +0/+4/+8 and the record
    # count to +0xC.  Success-value scheduling may place ``mov 0,r10`` on either
    # side of the first store, so tolerate that harmless instruction motion.
    if image[cmp_off:cmp_off + 2] != bytes.fromhex("6132"):
        return None
    pos = cmp_off + 4  # skip the short conditional branch
    limit = min(len(image), pos + 0x30)
    while pos + 4 <= limit and image[pos:pos + 2] != bytes.fromhex("240e"):
        pos += 2
    if pos + 4 > limit:
        return None
    disps: list[int] = []
    for store in (bytes.fromhex("010d"), bytes.fromhex("030d"), bytes.fromhex("050d")):
        if image[pos:pos + 2] != bytes.fromhex("240e"):
            return None
        disps.append(s16(struct.unpack_from("<H", image, pos + 2)[0]))
        pos += 4
        if image[pos:pos + 2] == bytes.fromhex("0052"):
            pos += 2
        if image[pos:pos + 2] != store:
            return None
        pos += 2
        if image[pos:pos + 2] == bytes.fromhex("0052"):
            pos += 2
    if pos + 4 > len(image) or image[pos + 1] != 0x0A or image[pos + 2:pos + 4] != bytes.fromhex("860c"):
        return None
    count = image[pos]
    if not (1 <= count <= 0x20):
        return None
    return disps, count


def recover_queue_helper(image: bytes, gp: int) -> dict:
    candidates: list[tuple[int, int, list[int], int]] = []
    for cmp_off in range(0, len(image) - 0x40, 2):
        parsed = queue_case_shape(image, cmp_off)
        if parsed is None:
            continue
        disps, count = parsed
        helper = _previous_function_start(image, cmp_off)
        candidates.append((helper, cmp_off, disps, count))
    if len(candidates) != 1:
        raise ManifestError(f"expected one raw SecOC queue-1 storage case, found {len(candidates)}")
    helper, case, disps, count = candidates[0]
    return {
        "secoc_queue_storage_helper": hx(helper),
        "secoc_queue1_case": hx(case),
        "secoc_descriptor_base": hx((gp + disps[0]) & 0xFFFFFFFF),
        "secoc_queue_head_base": hx((gp + disps[1]) & 0xFFFFFFFF),
        "secoc_raw_buffer_base": hx((gp + disps[2]) & 0xFFFFFFFF),
        "secoc_record_count": count,
    }


def recover_secoc_table(image: bytes, gate_entry: int, tp: int) -> int:
    # Gate-2 indexes records as ``index * 0x50`` then adds one TP-relative table
    # base.  Recover the table displacement from that machine shape rather than
    # scanning for a Sienna CAN-ID sequence.
    hits: list[int] = []
    end = min(gate_entry + 0x40, len(image) - 4)
    for off in range(gate_entry, end, 2):
        if image[off:off + 4] != bytes.fromhex("fdde5000"):  # mulhi 0x50,r29,r27
            continue
        for movea in range(off + 4, min(off + 12, end), 2):
            if image[movea:movea + 2] == bytes.fromhex("250e"):  # movea disp,tp,r1
                disp = s16(struct.unpack_from("<H", image, movea + 2)[0])
                hits.append((tp + disp) & 0xFFFFFFFF)
    return unique_hit("Gate-2 SecOC-record-table", hits)


def secoc_record_shape(image: bytes, base: int) -> bool:
    if base < 0 or base + RECORD_STRIDE > len(image):
        return False
    if image[base:base + 6] != bytes.fromhex("80001c000000") or image[base + 8] != 0x80:
        return False
    can_id = struct.unpack_from("<H", image, base + CAN_ID_OFFSET)[0]
    raw_offset = struct.unpack_from("<I", image, base + RAW_OFFSET_OFFSET)[0]
    pdu_id = struct.unpack_from("<H", image, base + PDU_ID_OFFSET)[0]
    pdu_id_copy = struct.unpack_from("<H", image, base + PDU_ID_OFFSET + 2)[0]
    secured_length = struct.unpack_from("<I", image, base + SECURED_LENGTH_OFFSET)[0]
    secured_length_copy = struct.unpack_from("<I", image, base + SECURED_LENGTH_OFFSET + 8)[0]
    return (
        0 < can_id <= 0x7FF
        and pdu_id < 0x100
        and pdu_id == pdu_id_copy
        and 0 < secured_length <= 64
        and secured_length == secured_length_copy
        and raw_offset < 0x1000
        and raw_offset + secured_length <= 0x1000
    )

def merge_anchor(anchors: dict, key: str, raw_value: object) -> None:
    existing = anchors.get(key)
    if existing not in (None, "", "null", []):
        if existing != raw_value:
            raise ManifestError(f"semantic/raw disagreement for {key}: {existing!r} != {raw_value!r}")
    anchors[key] = raw_value


def complete_raw_anchors(image: bytes, semantic: dict) -> dict:
    anchors = dict(semantic["anchors"])
    context = int(anchors["application_context_init"], 0)
    foreground = int(anchors["foreground_loop"], 0)
    gp = recover_application_gp(image, context)
    tp = recover_application_tp(image, context)
    merge_anchor(anchors, "application_gp", hx(gp))
    merge_anchor(anchors, "application_tp", hx(tp))
    for key, value in recover_boot_handoff(image).items():
        merge_anchor(anchors, key, value)
    merge_anchor(anchors, "foreground_tick_counter", hx(recover_tick_counter(image, foreground, gp)))
    com_rx = recover_com_rx(image)
    merge_anchor(anchors, "com_rx_indication", hx(com_rx))
    for key, value in recover_timeout_helper(image, com_rx, gp).items():
        merge_anchor(anchors, key, value)
    for key, value in recover_queue_helper(image, gp).items():
        merge_anchor(anchors, key, value)
    gate_entry = int(semantic["gate_entry"], 0)
    merge_anchor(anchors, "secoc_record_table", hx(recover_secoc_table(image, gate_entry, tp)))
    completed = dict(semantic)
    completed["anchors"] = anchors
    completed["raw_completion"] = {
        "status": "complete",
        "method": "raw-rh850-level1-signatures-plus-gp-relative-displacements",
    }
    completed["status"] = "resolved"
    return completed


def parse_record(image: bytes, table: int, index: int) -> dict:
    base = table + index * RECORD_STRIDE
    return {
        "index": index,
        "record_address": hx(base),
        "can_id": hx(struct.unpack_from("<H", image, base + CAN_ID_OFFSET)[0]),
        "raw_offset": hx(struct.unpack_from("<I", image, base + RAW_OFFSET_OFFSET)[0]),
        "pdu_id": struct.unpack_from("<H", image, base + PDU_ID_OFFSET)[0],
        "secured_length": struct.unpack_from("<I", image, base + SECURED_LENGTH_OFFSET)[0],
    }


def choose_geometry(db: dict, image_sha: str, variant_id: str | None) -> tuple[dict | None, str]:
    variants = db.get("variants", [])
    matches = [v for v in variants if v.get("codeflash_sha256") == image_sha]
    if variant_id is not None:
        selected = [v for v in variants if v.get("id") == variant_id]
        if len(selected) != 1:
            raise ManifestError(f"unknown/ambiguous variant id: {variant_id}")
        item = selected[0]
        pinned_sha = item.get("codeflash_sha256")
        if pinned_sha is not None and pinned_sha != image_sha:
            raise ManifestError(
                f"variant {variant_id} geometry is bound to CodeFlash {pinned_sha}, not {image_sha}"
            )
        if pinned_sha is None:
            return item, "variant-evidence-not-image-bound"
        return item, "image-sha-bound"
    if len(matches) == 1:
        return matches[0], "image-sha-bound"
    if len(matches) > 1:
        raise ManifestError(f"multiple geometry entries match image SHA {image_sha}")
    return None, "no-image-bound-geometry"


def extract_software_ids(image: bytes) -> list[str]:
    import re
    return sorted({m.decode("ascii") for m in re.findall(rb"(?<![A-Z0-9])8965[A-Z0-9]{8}(?![A-Z0-9])", image)})


def choose_bootstrap_profile(db: dict, software_ids: list[str]) -> dict | None:
    matches: list[dict] = []
    for profile in db.get("profiles", []):
        evidence = [row for row in profile.get("evidence", []) if row.get("software_id") in software_ids]
        if evidence:
            matches.append({
                "id": profile["id"],
                "security_access_secret": profile["security_access_secret"],
                "security_access_data_record": profile["security_access_data_record"],
                "did_order": profile["did_order"],
                "did_0201_default": profile["did_0201_default"],
                "did_0202_default": profile["did_0202_default"],
                "authenticated_download_base": profile["authenticated_download_base"],
                "authenticated_download_size": profile["authenticated_download_size"],
                "verify_routine": profile["verify_routine"],
                "execute_routine": profile["execute_routine"],
                "matched_evidence": evidence,
                "boundary": profile["boundary"],
            })
    if len(matches) > 1:
        raise ManifestError(f"multiple bootstrap profiles match software IDs {software_ids}")
    return matches[0] if matches else None


def geometry_contract(item: dict | None, source: str) -> dict:
    required = (
        "authenticated_download_base",
        "authenticated_download_size",
        "payload_callback_base",
        "payload_callback_cell",
        "shellcode_link_vma",
        "retained_application_rwx_base",
        "retained_application_rwx_end_exclusive",
        "retained_application_rwx_size",
    )
    values = {name: (item.get(name) if item else None) for name in required}
    verified = bool(
        item
        and item.get("evidence") == "firmware-static-verified"
        and item.get("codeflash_sha256")
        and all(values[name] is not None for name in required)
    )
    return {
        "status": "verified" if verified else "unresolved",
        "selection_source": source,
        "variant_id": item.get("id") if item else None,
        "evidence": item.get("evidence") if item else None,
        "codeflash_sha256": item.get("codeflash_sha256") if item else None,
        **values,
        "canary_observation_address": item.get("canary_observation_address") if item else None,
        "canary_observation_method": item.get("canary_observation_method") if item else None,
        "command5_dispatch_address": item.get("command5_dispatch_address") if item else None,
        "command5_driver_record": item.get("command5_driver_record") if item else None,
        "command5_key_selector": item.get("command5_key_selector") if item else None,
        "command5_done_flag": item.get("command5_done_flag") if item else None,
        "command5_status_flag": item.get("command5_status_flag") if item else None,
        "command5_mailbox_address": item.get("command5_mailbox_address") if item else None,
        "command5_mailbox_size": item.get("command5_mailbox_size") if item else None,
        "command5_mailbox_transport": item.get("command5_mailbox_transport") if item else None,
        "notes": item.get("notes") if item else "No image-bound RAM execution/retention geometry is available.",
    }


def build_manifest(image_path: Path, gate_path: Path, semantic_path: Path,
                   geometry_db_path: Path, bootstrap_db_path: Path, variant_id: str | None) -> dict:
    image, image_source = load_codeflash(image_path)
    image_sha = sha256(image)
    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    semantic = json.loads(semantic_path.read_text(encoding="utf-8"))
    geometry_db = json.loads(geometry_db_path.read_text(encoding="utf-8"))
    bootstrap_db = json.loads(bootstrap_db_path.read_text(encoding="utf-8"))

    if gate.get("resolution") != "unique" or gate.get("candidate_count") != 1:
        raise ManifestError("Gate-2 semantic resolution is not unique")
    if gate.get("program_sha256") != image_sha:
        raise ManifestError("Gate-2 semantic resolution does not match input image SHA-256")
    if semantic.get("status") not in ("resolved", "control-resolved") or semantic.get("candidate_count") != 1:
        raise ManifestError("ephemeral runtime control skeleton is unresolved/ambiguous")
    gate_entry = gate.get("function", {}).get("entry")
    if int(semantic.get("gate_entry", "-1"), 0) != int(gate_entry, 0):
        raise ManifestError("runtime semantic resolver and Gate-2 resolver disagree on gate function")
    semantic = complete_raw_anchors(image, semantic)

    anchors = semantic["anchors"]
    table = int(anchors["secoc_record_table"], 0)
    record_count = int(anchors["secoc_record_count"])
    records = [parse_record(image, table, i) for i in range(record_count)]
    bad_records = [r for r in records if not secoc_record_shape(image, int(r["record_address"], 0))]
    if bad_records:
        raise ManifestError(
            "Gate-2 table contains records outside the recovered Level-1 SecOC shape: "
            + ", ".join(r["record_address"] for r in bad_records)
        )
    can_ids = [int(r["can_id"], 0) for r in records]
    if len(set(can_ids)) != len(can_ids):
        raise ManifestError("Gate-2 SecOC table contains duplicate CAN IDs")

    desc_base = int(anchors["secoc_descriptor_base"], 0)
    raw_base = int(anchors["secoc_raw_buffer_base"], 0)
    counter_base = int(anchors["com_update_counter_base"], 0)
    steering: list[dict] = []
    missing_steering: list[str] = []
    incompatible_steering: list[str] = []
    for can_id in STEERING_IDS:
        record = next((r for r in records if int(r["can_id"], 0) == can_id), None)
        if record is None:
            missing_steering.append(hx(can_id))
            continue
        if record["secured_length"] != 8:
            incompatible_steering.append(hx(can_id))
            continue
        pdu_id = record["pdu_id"]
        raw_offset = int(record["raw_offset"], 0)
        steering.append({
            **record,
            "descriptor_address": hx(desc_base + record["index"] * 8),
            "raw_buffer_address": hx(raw_base + raw_offset),
            "update_counter_address": hx(counter_base + pdu_id),
        })
    steering_applicable = not missing_steering and not incompatible_steering and len(steering) == len(STEERING_IDS)

    software_ids = extract_software_ids(image)
    bootstrap_profile = choose_bootstrap_profile(bootstrap_db, software_ids)

    geom_item, geom_source = choose_geometry(geometry_db, image_sha, variant_id)
    geometry = geometry_contract(geom_item, geom_source)
    build_ready = geometry["status"] == "verified" and steering_applicable
    if build_ready:
        status = "runtime-build-ready"
    elif not steering_applicable:
        status = "semantic-resolved-steering-unsupported"
    else:
        status = "semantic-resolved-geometry-unresolved"

    invariants = [
        "Gate-2 semantic resolver unique and SHA-bound to input CodeFlash",
        "startup/context/foreground/aggregate skeleton unique on analyzed program",
        "boot transition prefix structurally resolved instead of inherited",
        "SecOC queue-1 storage bases and record count structurally resolved",
        "Gate-2 SecOC table base derived from TP-relative index*0x50 machine shape",
        "Com_RxIndication and update-counter base structurally resolved",
        "every queue-1 record satisfies the generated Level-1 SecOC record shape",
        "runtime build readiness requires classic 0x2E4/0x131 bridge records",
        "runtime build readiness additionally requires image-bound firmware-static RAM retention geometry",
    ]
    return {
        "schema": "p1me-ephemeral-runtime-target-manifest-v1",
        "status": status,
        "runtime_build_ready": build_ready,
        "image": {
            "path": str(image_path),
            "size": len(image),
            "sha256": image_sha,
            "software_ids": software_ids,
            "source_size": image_source["size"],
            "source_sha256": image_source["sha256"],
            "normalization": image_source["normalization"],
        },
        "authenticated_bootstrap_profile": bootstrap_profile,
        "gate2": gate,
        "runtime_semantics": semantic,
        "secoc_records": {
            "table_address": hx(table),
            "record_count": record_count,
            "stride": hx(RECORD_STRIDE),
            "records": records,
            "steering_bridge_applicable": steering_applicable,
            "steering_bridge_required_ids": [hx(x) for x in STEERING_IDS],
            "steering_bridge_missing_ids": missing_steering,
            "steering_bridge_incompatible_ids": incompatible_steering,
            "steering_bridge_profiles": steering,
        },
        "ram_execution_geometry": geometry,
        "invariants": invariants,
        "transfer_boundary": (
            "Static Level-1 runtime construction is permitted for this exact image; hardware canary remains mandatory."
            if build_ready else
            "Application/SecOC shape resolved, but the configured Gate-2 queue does not expose both classic steering bridge records; the steering bridge is not applicable to this image."
            if not steering_applicable else
            "Application/SecOC shape resolved, but no image-bound verified RAM execution/retention geometry exists; do not build/deploy a runtime."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", required=True, type=Path)
    p.add_argument("--gate", required=True, type=Path)
    p.add_argument("--semantic", required=True, type=Path)
    p.add_argument("--geometry-db", type=Path, default=DEFAULT_GEOMETRY_DB)
    p.add_argument("--bootstrap-db", type=Path, default=DEFAULT_BOOTSTRAP_DB)
    p.add_argument("--variant-id")
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    try:
        manifest = build_manifest(args.image, args.gate, args.semantic, args.geometry_db, args.bootstrap_db, args.variant_id)
    except (ManifestError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        p.error(str(exc))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": manifest["status"],
        "runtime_build_ready": manifest["runtime_build_ready"],
        "out": str(args.out),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
