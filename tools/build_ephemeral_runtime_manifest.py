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
SECOC_IDS = (0x00F, 0x2E4, 0x131, 0x132, 0x090, 0x0D7)
RECORD_STRIDE = 0x50
CAN_ID_OFFSET = 0x0A
RAW_OFFSET_OFFSET = 0x28
PDU_ID_OFFSET = 0x34
SECURED_LENGTH_OFFSET = 0x3C


class ManifestError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def recover_application_gp(image: bytes, context: int) -> int:
    end = min(context + 0x80, len(image) - 6)
    for off in range(context, end, 2):
        if image[off:off + 2] == bytes.fromhex("7f00"):  # first jmp lp ends context init
            end = off
            break
    hits = [off for off in range(context, end, 2)
            if image[off:off + 2] == bytes.fromhex("2406")]
    off = unique_hit("application-gp-immediate", hits)
    return struct.unpack_from("<I", image, off + 2)[0]


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


def queue_shape(image: bytes, off: int) -> bool:
    if off < 0 or off + 34 > len(image):
        return False
    checks = {
        0: "c600", 2: "6132", 6: "07f0", 8: "240e", 12: "010d",
        14: "0052", 16: "240e", 20: "030d", 22: "240e", 26: "050d",
        28: "060a", 30: "860c", 32: "7f00",
    }
    return all(image[off + pos:off + pos + len(bytes.fromhex(hxv))] == bytes.fromhex(hxv)
               for pos, hxv in checks.items())


def recover_queue_helper(image: bytes, gp: int) -> dict:
    hits = [off for off in range(0, len(image) - 34, 2) if queue_shape(image, off)]
    helper = unique_hit("SecOC-queue-storage-helper", hits)
    disps = [s16(struct.unpack_from("<H", image, helper + pos)[0]) for pos in (10, 18, 24)]
    return {
        "secoc_queue_storage_helper": hx(helper),
        "secoc_descriptor_base": hx((gp + disps[0]) & 0xFFFFFFFF),
        "secoc_queue_head_base": hx((gp + disps[1]) & 0xFFFFFFFF),
        "secoc_raw_buffer_base": hx((gp + disps[2]) & 0xFFFFFFFF),
    }


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
    merge_anchor(anchors, "application_gp", hx(gp))
    for key, value in recover_boot_handoff(image).items():
        merge_anchor(anchors, key, value)
    merge_anchor(anchors, "foreground_tick_counter", hx(recover_tick_counter(image, foreground, gp)))
    com_rx = recover_com_rx(image)
    merge_anchor(anchors, "com_rx_indication", hx(com_rx))
    for key, value in recover_timeout_helper(image, com_rx, gp).items():
        merge_anchor(anchors, key, value)
    for key, value in recover_queue_helper(image, gp).items():
        merge_anchor(anchors, key, value)
    completed = dict(semantic)
    completed["anchors"] = anchors
    completed["raw_completion"] = {
        "status": "complete",
        "method": "raw-rh850-level1-signatures-plus-gp-relative-displacements",
    }
    completed["status"] = "resolved"
    return completed


def find_secoc_tables(image: bytes) -> list[int]:
    hits: list[int] = []
    span = RECORD_STRIDE * len(SECOC_IDS)
    # The generated table is naturally at least halfword aligned.  Requiring
    # exact six-record order is intentionally conservative Level-1 behavior.
    for base in range(0, len(image) - span + 1, 2):
        if all(struct.unpack_from("<H", image, base + i * RECORD_STRIDE + CAN_ID_OFFSET)[0] == can_id
               for i, can_id in enumerate(SECOC_IDS)):
            hits.append(base)
    return hits


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
    return sorted({m.decode("ascii") for m in re.findall(rb"8965[A-Z0-9]{8}", image)})


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
        "notes": item.get("notes") if item else "No image-bound RAM execution/retention geometry is available.",
    }


def build_manifest(image_path: Path, gate_path: Path, semantic_path: Path,
                   geometry_db_path: Path, bootstrap_db_path: Path, variant_id: str | None) -> dict:
    image = image_path.read_bytes()
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

    tables = find_secoc_tables(image)
    if len(tables) != 1:
        raise ManifestError(f"expected one six-record SecOC table, found {len(tables)}")
    table = tables[0]
    records = [parse_record(image, table, i) for i in range(len(SECOC_IDS))]
    if [int(r["can_id"], 0) for r in records] != list(SECOC_IDS):
        raise ManifestError("SecOC table CAN-ID order mismatch")

    anchors = semantic["anchors"]
    desc_base = int(anchors["secoc_descriptor_base"], 0)
    raw_base = int(anchors["secoc_raw_buffer_base"], 0)
    counter_base = int(anchors["com_update_counter_base"], 0)
    steering: list[dict] = []
    for can_id in (0x2E4, 0x131):
        record = next(r for r in records if int(r["can_id"], 0) == can_id)
        if record["secured_length"] != 8:
            raise ManifestError(f"CAN {can_id:#x} secured length is not classic 8-byte shape")
        pdu_id = record["pdu_id"]
        raw_offset = int(record["raw_offset"], 0)
        if pdu_id >= 0x100 or raw_offset >= 0x1000:
            raise ManifestError(f"CAN {can_id:#x} record geometry is outside Level-1 bounds")
        steering.append({
            **record,
            "descriptor_address": hx(desc_base + record["index"] * 8),
            "raw_buffer_address": hx(raw_base + raw_offset),
            "update_counter_address": hx(counter_base + pdu_id),
        })

    software_ids = extract_software_ids(image)
    bootstrap_profile = choose_bootstrap_profile(bootstrap_db, software_ids)

    geom_item, geom_source = choose_geometry(geometry_db, image_sha, variant_id)
    geometry = geometry_contract(geom_item, geom_source)
    build_ready = geometry["status"] == "verified"

    invariants = [
        "Gate-2 semantic resolver unique and SHA-bound to input CodeFlash",
        "startup/context/foreground/aggregate skeleton unique on analyzed program",
        "boot transition prefix structurally resolved instead of inherited",
        "SecOC queue-storage bases structurally resolved",
        "Com_RxIndication and update-counter base structurally resolved",
        "exact six-record SecOC Level-1 table order unique in raw CodeFlash",
        "protected steering records 0x2E4/0x131 are classic 8-byte records",
        "runtime build readiness additionally requires image-bound firmware-static RAM retention geometry",
    ]
    return {
        "schema": "p1me-ephemeral-runtime-target-manifest-v1",
        "status": "runtime-build-ready" if build_ready else "semantic-resolved-geometry-unresolved",
        "runtime_build_ready": build_ready,
        "image": {
            "path": str(image_path),
            "size": len(image),
            "sha256": image_sha,
            "software_ids": software_ids,
        },
        "authenticated_bootstrap_profile": bootstrap_profile,
        "gate2": gate,
        "runtime_semantics": semantic,
        "secoc_records": {
            "table_address": hx(table),
            "stride": hx(RECORD_STRIDE),
            "records": records,
            "steering_bridge_profiles": steering,
        },
        "ram_execution_geometry": geometry,
        "invariants": invariants,
        "transfer_boundary": (
            "Static Level-1 runtime construction is permitted for this exact image; hardware canary remains mandatory."
            if build_ready else
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
