#!/usr/bin/env python3
"""Compile the canonical P1M-E SystemRDL source into repository projections."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any

from systemrdl import RDLCompiler
from systemrdl.node import MemNode, RegNode

from tools import REPO_ROOT

ROOT = REPO_ROOT
SOURCE = ROOT / "data" / "devices" / "p1me.rdl"
MACHINE_OUTPUT = ROOT / "data" / "generated" / "p1me_machine.json"
SFR_OUTPUT = ROOT / "data" / "p1m_sfr_labels.csv"
MEMORY_OUTPUT = ROOT / "data" / "p1me_product_memory.json"

SOURCE_METADATA = {
    "datasheet": {
        "path": "REFERENCE/r01ds0505ed0100-rh850p1m-e.pdf",
        "sha256": "71b80cf05abf256f4047c7c2d6fa706438f70440e5e2959f1ce83d18c7822aad",
        "revision": "R01DS0505ED0100 Rev.1.00",
        "date": "2025-09-30",
        "references": [
            "Table 1.1, page 2: R7F701381 and R7F701383 are DPS 1-MB products; Local RAM 128 KB; Global RAM 64 KB; DATA Flash 64 KB*1 / 32 KB*2, where note 2 applies to 1-MB devices",
            "Figure 1.3, page 6: TAUJ is on Peripheral IP Group 1 / P-Bus domain 80 MHz",
        ],
    },
    "hardware_manual": {
        "path": "REFERENCE/r01uh0585ej0120_manual.pdf",
        "sha256": "aaea89a7f5d9b029776945868d21728465d372223c41db05cbd728a0499a6e34",
        "revision": "R01UH0585EJ0120 Rev.1.20",
        "date": "2018-03-23",
        "references": [
            "Table 4.1, page 257: 1-MB device user CodeFlash 00000000-000FFFFF; 32-KB extended user area 01000000-01007FFF; DataFlash FF200000-FF207FFF; PE1 and self local-RAM views are each 128 KB",
            "Section 3.3.3: Global RAM uses write-through access and maintains PE/DMA data coherency",
            "Section 3.4.1.2: publishing instructions written to RAM requires a dummy read from the written memory followed by SYNCP and SYNCI before branching",
            "Section 3.4.5: initialize 48 bytes beyond RAM-resident code for speculative fetch and do not cross an access-prohibited/IPG boundary",
            "Section 24.3: TAUJ CDR/CNT/CMOR/TPS/BRS register semantics; PRS0=2 gives CK0=PCLK/4",
        ],
    },
    "flash_hardware_manual": {
        "path": "REFERENCE/r01uh0615ej0120-p1me-flash.pdf",
        "sha256": "67137458a8bd1046030f1db533cf12a2a948df27bb8d97ae1ec2614934a63b72",
        "revision": "R01UH0615EJ0120 Rev.1.20",
        "date": "2018-03-23",
        "references": [
            "Section 3.3: FACI register area FFA10000 and command-issuing area FFA20000",
            "Section 4: exact FACI register offsets and access widths",
            "Section 4.26-4.28: BFASELR and SELFID register locations",
        ],
    },
    "cpu_software_manual": {
        "path": "REFERENCE/r01us0123ej0140-rh850g3m.pdf",
        "sha256": "a5202645d03cbb8191444c97d7fe27d1852f2c69d6b3196c4b5a171d2bab241b",
        "revision": "R01US0123EJ0140 Rev.1.40",
        "date": "2018-12-22",
        "references": [
            "Chapter 3: exact G3M system-register numbers and selection IDs including MCFG0 HTCFG0 PMR MCC and CDBCR",
            "Table 3-55: MPAT E/G/SX/SW/SR/UX/UW/UR bit layout",
            "Section 5.1.1: MCTL.MA misalignment behavior",
        ],
    },
}


def _access(value: Any) -> str:
    return str(value).rsplit(".", 1)[-1]
def _reset_rules(value: Any) -> list[dict[str, str]]:
    if value is None:
        return []
    rules: list[dict[str, str]] = []
    for item in str(value).split(";"):
        reset_class, separator, mode = item.partition(":")
        if not separator or mode not in {"force", "controlled"}:
            raise RuntimeError(f"invalid reset rule: {item!r}")
        rules.append({"reset_class": reset_class, "mode": mode})
    return rules




def _compile() -> tuple[Any, str]:
    compiler = RDLCompiler()
    compiler.compile_file(str(SOURCE))
    root = compiler.elaborate(top_def_name="p1me")
    return root.top, hashlib.sha256(SOURCE.read_bytes()).hexdigest()


def _model() -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    top, source_sha = _compile()
    regions: list[dict[str, Any]] = []
    registers: list[dict[str, Any]] = []
    for node in top.children():
        if isinstance(node, MemNode):
            regions.append({
                "name": node.inst_name,
                "start": node.absolute_address,
                "end_exclusive": node.absolute_address + node.size,
                "size": node.size,
                "access": _access(node.get_property("sw")),
                "executable": bool(node.get_property("executable")),
                "alias_group": node.get_property("alias_group"),
                "reset_policy": node.get_property("reset_policy"),
                "reset_control": node.get_property("reset_control"),
                "reset_rules": _reset_rules(node.get_property("reset_rules")),
                "evidence": node.get_property("evidence"),
                "source_ref": node.get_property("source_ref"),
            })
        elif isinstance(node, RegNode):
            fields = node.fields()
            if len(fields) != 1 or fields[0].inst_name != "value":
                raise RuntimeError(f"{node.inst_name}: machine registers require one value field")
            field = fields[0]
            configured_widths = node.get_property("access_widths")
            if configured_widths:
                access_widths = [
                    int(value.strip()) for value in str(configured_widths).split(",")
                ]
            else:
                access_widths = [int(node.get_property("accesswidth")) // 8]
            row = {
                "name": node.inst_name,
                "address": node.absolute_address,
                "size": node.size,
                "access_widths": access_widths,
                "access": _access(field.get_property("sw")),
                "reset": field.get_property("reset"),
                "behavior": node.get_property("behavior"),
                "evidence": node.get_property("evidence"),
                "source_ref": node.get_property("source_ref"),
                "description": node.get_property("desc") or "",
            }
            for property_name in (
                "trigger",
                "status_register",
                "secondary_status_register",
                "access_register",
                "history_register",
                "reload_prefix",
                "counter_prefix",
                "payload_address",
                "completion_value",
                "channel_count",
                "interrupt_channel",
                "interrupt_register",
                "interrupt_register_prefix",
                "interrupt_channel_base",
                "mode_prefix",
                "prescaler_register",
                "control_register",
                "pointer_register",
                "window_register",
                "channel_control_register",
                "global_control_register",
                "fifo_index",
                "fifo_channel",
            ):
                value = node.get_property(property_name)
                if value is not None:
                    row[property_name] = value
            registers.append(row)
    regions.sort(key=lambda row: row["start"])
    registers.sort(key=lambda row: row["address"])
    product_ids = str(top.get_property("product_ids")).split(",")
    by_region = {row["name"]: row for row in regions}
    product_bytes = {
        "codeflash_bytes": by_region["codeflash_user"]["size"],
        "extended_user_codeflash_bytes": by_region["codeflash_extended"]["size"],
        "dataflash_bytes": by_region["dataflash"]["size"],
        "local_ram_bytes": by_region["local_ram_pe1"]["size"],
        "global_ram_bytes": by_region["global_ram"]["size"],
    }
    machine = {
        "schema": "rh850-p1me-machine-v2",
        "source": {
            "path": str(SOURCE.relative_to(ROOT)),
            "sha256": source_sha,
            "systemrdl_compiler": "1.33.0",
        },
        "products": [
            {"product_id": product_id, "regulator": "DPS", **product_bytes}
            for product_id in product_ids
        ],
        "p_bus_hz": int(top.get_property("p_bus_hz")),
        "manual": {
            "regions": regions,
            "registers": [row for row in registers if row["evidence"] == "manual"],
        },
        "target_derived": {
            "registers": [row for row in registers if row["evidence"] != "manual"],
        },
        "execution": {
            "engine": "Ghidra PcodeEmulator",
            "profile": "functional",
            "timing_claims": False,
            "unknown_read_policy": "fault",
            "codeflash_overlays": False,
        },
        "evidence_boundary": {
            "manual": "public specification-backed behavior",
            "recovered": "exact-firmware-derived behavior; not a public silicon specification",
            "observed": "identity-bound hardware capture input",
        },
    }
    by_register = {row["name"]: row for row in registers}
    memory = {
        "schema_version": 1,
        "scope": "Renesas RH850/P1M-E product and address-space facts used to interpret the retained Toyota EPS dumps",
        "sources": SOURCE_METADATA,
        "products": {
            product["product_id"]: {
                key: value for key, value in product.items() if key != "product_id"
            }
            for product in machine["products"]
        },
        "address_space": {
            "codeflash_user_1mb": {"start": by_region["codeflash_user"]["start"], "end_exclusive": by_region["codeflash_user"]["end_exclusive"]},
            "codeflash_extended_user": {"start": by_region["codeflash_extended"]["start"], "end_exclusive": by_region["codeflash_extended"]["end_exclusive"]},
            "dataflash_1mb": {"start": by_region["dataflash"]["start"], "end_exclusive": by_region["dataflash"]["end_exclusive"]},
            "dataflash_2mb": {"start": by_region["dataflash"]["start"], "end_exclusive": by_region["dataflash"]["start"] + 0x10000},
            "local_ram_pe1": {"start": by_region["local_ram_pe1"]["start"], "end_exclusive": by_region["local_ram_pe1"]["end_exclusive"]},
            "local_ram_self": {"start": by_region["local_ram_self"]["start"], "end_exclusive": by_region["local_ram_self"]["end_exclusive"]},
            "global_ram": {"start": by_region["global_ram"]["start"], "end_exclusive": by_region["global_ram"]["end_exclusive"]},
        },
        "ram_execution": {
            "architectural_fetch_views": ["local_ram_pe1", "local_ram_self", "global_ram"],
            "prefetch_initialized_bytes": 48,
            "global_ram_data_coherency": "write-through and hardware-maintained across PE and DMA",
        },
        "alignment": {
            "mctl_ma_reset": 0,
            "default_behavior": "misaligned data access exception",
            "mctl_ma_1_behavior": "split non-atomic access; doubleword still requires word alignment",
        },
        "reset_ram_initialization": {
            "baseline_behavior": "the reset table initializes local and global RAM to zero unless the applicable STAC disable control is active",
            "local_ram_disable_control": "STAC_LM0 for System Reset 1 except CVM reset, System Reset 2, and Application Reset 1",
            "global_ram_disable_control": "STAC_GRAM for Application Reset 1",
        },
        "mpat": {
            "bit_layout": {"E": 7, "G": 6, "SX": 5, "SW": 4, "SR": 3, "UX": 2, "UW": 1, "UR": 0},
            "0xB8": "enabled supervisor read/write/execute",
            "0xA8": "enabled supervisor read/execute",
        },
        "timer": {
            "p_bus_hz": machine["p_bus_hz"],
            "prs0": 2,
            "ck0_hz": machine["p_bus_hz"] // 4,
        },
    }
    if by_register["STAC_GRAM"]["reset"] != 3 or by_register["STAC_LM0"]["reset"] != 3:
        raise RuntimeError("STAC reset values drifted from the hardware manual")
    return machine, registers, memory


def _csv_text(registers: list[dict[str, Any]]) -> str:
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["address", "name", "size", "access", "comment"])
    for row in registers:
        writer.writerow([
            f"0x{row['address']:08X}", row["name"], row["size"], row["access"], row["description"],
        ])
    return out.getvalue()


def _json_text(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=True) + "\n"


def _update(path: Path, content: str, *, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.is_file() else None
    if current == content:
        return False
    if check:
        raise RuntimeError(f"generated artifact is stale: {path.relative_to(ROOT)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def generate(*, check: bool) -> list[Path]:
    machine, registers, memory = _model()
    outputs = {
        MACHINE_OUTPUT: _json_text(machine),
        SFR_OUTPUT: _csv_text(registers),
        MEMORY_OUTPUT: _json_text(memory),
    }
    changed = [path for path, content in outputs.items() if _update(path, content, check=check)]
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if any generated projection is stale")
    args = parser.parse_args()
    changed = generate(check=args.check)
    action = "would update" if args.check else "updated"
    for path in changed:
        print(f"{action}: {path.relative_to(ROOT)}")
    if not changed:
        print("P1M-E model projections are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
