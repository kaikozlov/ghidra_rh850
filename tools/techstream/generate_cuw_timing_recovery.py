#!/usr/bin/env python3
"""Generate Techstream V18 CUW timing/retry/recovery evidence.

The artifact intentionally combines only static facts that are useful for a
future short GTS+/J2534 capture: decoded timing tables, byte-pinned controller
and writer bodies, Flash Recovery persistence geometry, targeted EMPS_P5
power-cycle observables, and bounded legacy iQ-EMPS vocabulary.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pefile

from generate_cuw_writer_inventory import decode_parameter_ini

REPO = Path(__file__).resolve().parents[2]
TECH = REPO / "Techstream/unpacked/toyota/Toyota Diagnostics"
CUW = TECH / "Calibration Update Wizard"
INI = CUW / "Ini"
DDB_ART = REPO / "data/generated/techstream_v18/priority_steering_ddb_semantics.json"
OUT = REPO / "data/generated/techstream_v18/cuw_timing_recovery.json"

FACTORY_KEYS = [
    "WaitTimeAfterSeedData",
    "WaitTimeAfterSeedKey",
    "WaitTimeAfterReprogrammingMode",
    "WaitTimeAfterFlashWrite",
    "WaitTimeAfterEndOfFlashing",
    "WaitTimeBeforeStatusCheckForBlankCheck",
    "WaitTimeBeforeStatusCheckForEraseBlock",
    "WaitTimeBeforeStatusCheckForInVerify",
    "WaitTimeBeforeStatusCheckForVerify",
    "WaitTimeBeforeStatusCheckForWriteBlock",
    "ReceiveTimeoutBeforeGetCID",
    "ReceiveTimeoutBeforeFlashWrite",
    "ReceiveTimeoutBeforeInitialCommand",
    "SendTimeoutBeforePrepareWrite",
    "ReceiveTimeoutBeforePrepareRetry",
    "WaitTimeAfterIGOnAtRetry",
    "WaitTimeBetweenSF",
    "PrepareRetryFlag",
    "IGOffRetriableFlag",
    "FlagToSendAllOnPrepareRetry",
    "FlagToWaitAfterFuncReq",
    "ReceveTimeoutSumCheck",
    "RequestCANIDAllowingTimeout",
    "RequestCANIDBreakingResponse",
    "CANCommunicationSpeedAddress",
]

SYSTEM_KEYS = [
    "WaitTimeForIGOFFON",
    "WaitTimeAfterIGOn",
    "WaitTimeAfterBatteryDisconnected",
    "WaitTimeAfterBatteryConnected",
    "FlagToCancelAutomaticIGOFF",
    "FlagToChangeToReprogGWModeForCentralGW",
    "FlagToDoIGOFFONAtCPUTypeChange",
    "CPUTypeWithModeChangeAtCPUTypeChangeFlag",
    "FlagToUseCIDGetterAndFlashWriterDLL",
]

# Function extents are from the isolated PE Ghidra analysis.  The generator
# hashes raw PE bytes only; the verifier re-derives the same hashes without
# requiring a live Ghidra project.
FUNCTIONS: dict[str, list[tuple[int, int, str]]] = {
    "Cuw.exe": [
        (0x004296C4, 717, "flash_recovery_static_keys_init"),
        (0x00429FF4, 200, "flash_recovery_create_or_activate"),
        (0x0042A0BC, 10799, "flash_recovery_load"),
        (0x0042DE54, 32, "flash_recovery_finalize_delete"),
        (0x0042EDF0, 234, "flash_recovery_restore_backup"),
        (0x0042ECBC, 27, "set_write_cpu_index"),
        (0x0042ECE4, 25, "set_writing"),
        (0x0042ED0C, 27, "set_use_new_software_password"),
        (0x0042ED34, 27, "set_writing_end_block"),
        (0x0042EDC8, 27, "set_passthru_error_code"),
        (0x0042EEDC, 3142, "flash_recovery_save"),
        (0x0044F568, 563, "flash_recovery_startup_check"),
        (0x0044FC80, 458, "flash_recovery_delete_dialog"),
        (0x0045E880, 19128, "legacy_reprogram_controller"),
        (0x00584254, 1659, "modern_reprogram_flow_a"),
        (0x00587AD4, 694, "modern_reprogram_flow_b"),
    ],
    "TCUWControlCommPhase.dll": [
        (0x10007750, 2060, "retry_driver"),
        (0x10002090, 378, "reconnect_transport"),
        (0x1000A8B0, 582, "phase_dispatcher"),
    ],
    "TCUWP4P5CanPowerTrainPrepareWriter.dll": [
        (0x100016A0, 1150, "legacy_seed_key_sequence"),
        (0x10001F0B, 78, "legacy_post_seed_key_wait"),
    ],
    "TCUWCanSecurityVFORESTFlashWriter.dll": [
        (0x10001200, 1519, "vforest_mode_transition_and_status_poll"),
    ],
    "TCUWCanCommonPrepareWriter.dll": [
        (0x10001630, 204, "get_bus_type_from_cpu_image"),
    ],
}

RECOVERY_STRINGS = [
    (0x005D8D10, "RecoveryInfo"),
    (0x005D8D1D, "SavedCalibrationFilePath"),
    (0x005D8D36, "SelectedJ2534Device"),
    (0x005D8D4A, "CIDNum"),
    (0x005D8D51, "CID%d"),
    (0x005D8D57, "VIN"),
    (0x005D8D5B, "CIDNodeNum"),
    (0x005D8D66, "CIDNode%d"),
    (0x005D8D70, "ReproCheckResult"),
    (0x005D8D81, "IsCentralGWExist"),
    (0x005D8D92, "WriteCpuIndex"),
    (0x005D8DA0, "Writing"),
    (0x005D8DA8, "UseNewSoftwarePassword"),
    (0x005D8DBF, "WritingEndBlock"),
    (0x005D8DCF, "RecoveryInfo.ini"),
    (0x005D8DE0, "PassThruErrorCode"),
    (0x005D8DF2, "AssyNoNum"),
    (0x005D8DFC, "AssyNo%d"),
    (0x005D8E05, "VehicleInfoForUpdateAvailableFlagNum"),
    (0x005D8E2A, "VehicleInfoForUpdateAvailableFlag%d"),
]

RECOVERY_FIELDS = [
    {"offset": 0x00, "name": "SavedCalibrationFilePath", "type": "string"},
    {"offset": 0x04, "name": "SelectedJ2534Device", "type": "string"},
    {"offset": 0x18, "name": "CID", "type": "vector<string>"},
    {"offset": 0x28, "name": "VIN", "type": "string"},
    {"offset": 0x40, "name": "CIDNode", "type": "vector<string>"},
    {"offset": 0x50, "name": "ReproCheckResult", "type": "bool"},
    {"offset": 0x51, "name": "IsCentralGWExist", "type": "bool"},
    {"offset": 0x54, "name": "WriteCpuIndex", "type": "int32"},
    {"offset": 0x58, "name": "Writing", "type": "bool"},
    {"offset": 0x59, "name": "UseNewSoftwarePassword", "type": "bool"},
    {"offset": 0x5A, "name": "WritingEndBlock", "type": "bool"},
    {"offset": 0x74, "name": "PassThruErrorCode", "type": "int32"},
    {"offset": 0x88, "name": "AssyNo", "type": "vector<string>"},
    {"offset": 0xB8, "name": "VehicleInfoForUpdateAvailableFlag", "type": "vector<bool>"},
]

INTERNAL_RECOVERY_FIELDS = [
    {"offset": 0x5B, "name": "resume_armed", "type": "bool"},
    {"offset": 0x5C, "name": "recovery_disabled", "type": "bool"},
    {"offset": 0x60, "name": "backup_path", "type": "string"},
    {"offset": 0x6C, "name": "persistence_active", "type": "bool"},
    {"offset": 0x70, "name": "recovery_ini_path", "type": "string"},
]

TARGET_DDB_IDS = [
    0x0016, 0x0017, 0x0018, 0x0019,
    0x0033, 0x0034, 0x0036,
    0x0167,
    0x0421, 0x0422,
    0x07D1, 0x07D2,
    0x26AC, 0x26AD, 0x26C0, 0x26C1, 0x26C3,
]

IQ_STRINGS = [
    "Flash Calibration Update in Process - 1st retry",
    "Flash Calibration Update in Process - 2nd retry",
    "Flash Calibration Update in Process - 3rd retry",
    "CUW made three unsuccessful attempts to reprogram the ECU.",
    "CFlashWriter::SelectRetryPassword",
    "CSilVinReader::FiveBaudInit",
    "CSilFlashWriter::SetBaudRateOfECU",
    "CSilFlashWriter::TweakBaudRate",
    "CCanFlashWriter::ChangeReprogrammingMode",
    "TabSheet_PrepareWrite1_iQ_EMPS",
    "TabSheet_PrepareWrite2_iQ_EMPS",
    "TabSheet_PrepareWrite3_iQ_EMPS",
    "CTechVim_iQ_EPS_FlashWriter",
    "CTester2IF",
    "Verify Calibration ID",
    "The previous reprogramming attempt was interrupted or did not finish.",
    "A recovery file for the previous vehicle has been created.",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def decoded_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    decoded = decode_parameter_ini(path.read_bytes())
    rows = list(csv.reader(io.StringIO(decoded.decode("latin1"))))
    if not rows:
        return [], []
    header = rows[0]
    out = []
    for row in rows[1:]:
        row = row + [""] * (len(header) - len(row))
        out.append(dict(zip(header, row)))
    return header, out


def factory_rows() -> tuple[list[str], list[dict[str, str]]]:
    columns: set[str] = set()
    out: list[dict[str, str]] = []
    for path in sorted(INI.glob("*.ini"), key=lambda p: p.name.lower()):
        try:
            h, rows = decoded_rows(path)
        except (ValueError, UnicodeError, csv.Error):
            continue
        if "DLLFileNameForPrepareWrite" not in h:
            continue
        columns.update(h)
        out.extend(rows)
    return sorted(columns), out


def distributions(rows: list[dict[str, str]], keys: list[str]) -> dict[str, dict[str, int]]:
    return {
        key: dict(sorted(Counter(row.get(key, "") for row in rows).items()))
        for key in keys
    }


def function_identities() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for name, funcs in FUNCTIONS.items():
        path = CUW / name
        data = path.read_bytes()
        pe = pefile.PE(data=data)
        base = pe.OPTIONAL_HEADER.ImageBase
        for va, size, role in funcs:
            body = pe.get_data(va - base, size)
            out.append({
                "binary": name,
                "binary_sha256": digest(data),
                "va": va,
                "size": size,
                "role": role,
                "sha256": digest(body),
            })
    return out


def recovery_string_records() -> list[dict[str, Any]]:
    path = CUW / "Cuw.exe"
    data = path.read_bytes()
    pe = pefile.PE(data=data)
    base = pe.OPTIONAL_HEADER.ImageBase
    out = []
    for va, text in RECOVERY_STRINGS:
        raw = pe.get_data(va - base, len(text) + 1)
        out.append({"va": va, "text": text, "raw_hex": raw.hex()})
    return out


def ddb_observables() -> list[dict[str, Any]]:
    src = json.loads(DDB_ART.read_text())
    wanted_sources = {"NA/DB/EMPS_P5.ddb", "NA/DB/EMPS2_P5.ddb"}
    by_id: dict[int, dict[str, Any]] = {}
    for source in src["sources"]:
        if source["relative_path"] not in wanted_sources:
            continue
        records = source.get("sections", {}).get("62", {}).get("records", [])
        for record in records:
            fields = record.get("fields", {})
            data_id = fields.get("monitor_key_u16")
            if data_id not in TARGET_DDB_IDS:
                continue
            item = by_id.setdefault(data_id, {
                "data_id": f"0x{data_id:04X}",
                "name": fields.get("resolved_name"),
                "sources": [],
            })
            item["sources"].append({
                "relative_path": source["relative_path"],
                "record_index": record["record_index"],
                "record_sha256": digest(bytes.fromhex(record["raw_hex"])),
            })
    return [by_id[k] for k in sorted(by_id)]


def iq_comparative() -> dict[str, Any]:
    path = CUW / "Cuw_iQ_EMPS.exe"
    data = path.read_bytes()
    strings = []
    for text in IQ_STRINGS:
        off = data.find(text.encode("ascii"))
        strings.append({"text": text, "file_offset": off})
    return {
        "binary": path.name,
        "sha256": digest(data),
        "strings": strings,
        "boundary": "legacy/V850-M16C-era naming is comparative evidence only; it does not establish RH850 target behavior",
        "inferences": [
            "SelectRetryPassword is historical vocabulary consistent with the modern UseNewSoftwarePassword recovery field",
            "FiveBaudInit/SetBaudRateOfECU/TweakBaudRate are legacy transport ancestry, not evidence that the modern CAN target performs those operations",
            "PrepareWrite1/2/3 iQ-EMPS pages expose operator-driven IG-OFF -> start -> IG-ON sequencing ancestry",
            "three retry captions and terminal three-attempt error show a longstanding CUW retry model; exact modern counter implementation remains independently bounded",
            "Verify Calibration ID and prior-reprogramming recovery strings show EPS-specific recovery/CID verification ancestry",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, default=OUT)
    args = ap.parse_args()

    factory_header, factories = factory_rows()
    system_header, systems = decoded_rows(INI / "Parameter.ini")
    eps_rows = [
        {
            "factory_identifier": row.get("ParamFileKeySystemProtocolMicon", ""),
            "kind_of_ecu": row.get("KindOfECUNames", ""),
            "calibration_type": row.get("CalibrationType", ""),
            "wait_igoffon": row.get("WaitTimeForIGOFFON", ""),
            "wait_after_ig_on": row.get("WaitTimeAfterIGOn", ""),
            "use_cid_getter_flash_writer": row.get("FlagToUseCIDGetterAndFlashWriterDLL", ""),
            "password_address": row.get("PasswordAddress", ""),
        }
        for row in systems
        if "EMPS" in row.get("KindOfECUNames", "") or "PPS" in row.get("KindOfECUNames", "")
    ]

    obj = {
        "schema_version": 1,
        "distribution": "Toyota Techstream V18.00.003",
        "source": "external-source + generated-artifact",
        "factory_parameter_table": {
            "rows": len(factories),
            "columns": len(factory_header),
            "timing_retry_distributions": distributions(factories, FACTORY_KEYS),
        },
        "system_parameter_table": {
            "rows": len(systems),
            "columns": len(system_header),
            "host_ig_recovery_distributions": distributions(systems, SYSTEM_KEYS),
            "eps_rows": eps_rows,
        },
        "function_identities": function_identities(),
        "timing_semantics": {
            "legacy_seed_data": "P4/P5 prepare uses WaitTimeAfterSeedData between seed receipt/CalcSeedKey and the key-send phase; V18 table value is 100 ms for 162/196 factory rows",
            "legacy_seed_key": "P4/P5 prepare uses WaitTimeAfterSeedKey after the 27 02 exchange; V18 table value is 100 ms for the same 162 rows",
            "modern_seed_pacing": "ReproStd/Unified prepare do not consume the WaitTimeAfterSeed* keys; their pacing is code-immediate/route-specific",
            "retry_driver": "TCUWControlCommPhase retry driver consumes IGOffRetriableFlag, PrepareRetryFlag and ReceiveTimeoutBeforePrepareRetry, can reconnect after teardown, and contains a hardcoded 5000 ms post-flash-confirm wait",
            "transport_reconnect": "controller reconnect selects CAN Connect(6) versus Ethernet Connect0500(0x800f) by contact type",
            "vforest_mode_wait": "Security-VFOREST flash consumes WaitTimeAfterReprogrammingMode and WaitTimeBetweenSF around mode transition/status polling",
            "bus_type": "CANCommunicationSpeedAddress is interpreted by GetBusTypeFromCPUImage as a CPU-image byte location used to select one of the bus/speed modes; it is not a hardware register address",
            "host_ig": "Parameter.ini supplies WaitTimeForIGOFFON and WaitTimeAfterIGOn plus automatic-IG/gateway/CPU-type-change flags used by the host-side reprogramming flow",
        },
        "flash_recovery": {
            "file": "Save/RecoveryInfo.ini",
            "section": "RecoveryInfo",
            "string_records": recovery_string_records(),
            "persisted_fields": RECOVERY_FIELDS,
            "internal_fields": INTERNAL_RECOVERY_FIELDS,
            "lifecycle": {
                "create_or_activate": "0x00429FF4 creates/activates recovery state; modern and legacy reprogram flows call it when a job starts",
                "load": "0x0042A0BC reconstructs strings/vectors/bools/integers from RecoveryInfo.ini",
                "save": "0x0042EEDC writes the whole state; setters persist changes when persistence is active",
                "restore_backup": "0x0042EDF0 copies the backup recovery file into place when needed",
                "finalize": "0x0042DE54 deletes the saved calibration payload and RecoveryInfo.ini on final success/delete",
                "startup_check": "0x0044F568 loads remaining recovery state and drives the Retry/Cancel/Delete eligibility UI",
                "delete_dialog": "0x0044FC80 confirms permanent recovery deletion then finalizes it",
                "resume": "WriteCpuIndex selects the CPU-image restart point; Writing/WritingEndBlock/UseNewSoftwarePassword constrain the resumed phase",
            },
            "identity_binding": "VIN plus AssyNo/CID lists are persisted and checked/displayed for recovery eligibility; no cryptographic vehicle binding is recovered in this client path",
        },
        "capture_observables": {
            "emsp5_power_cycle_data_ids": ddb_observables(),
            "later_session_requirements": [
                "preserve raw calibration package/extracted attach.att and the Save/RecoveryInfo.ini directory before and after any deliberate interruption",
                "retain J2534 API timing plus raw message timestamps across 10 02, 27 01/02, reset, disconnect/reconnect, and any IG OFF/ON transition",
                "capture Data IDs 0x0016..0x0019, 0x0033/0x0034/0x0036, 0x0421/0x0422, 0x07D1/0x07D2, and 0x26AC/0x26AD/0x26C1/0x26C3 during recovery/retry experiments",
                "compare on-wire SecurityAccess spacing with the static route fingerprints rather than assuming the 100 ms legacy table applies to Unified",
                "record the selected factory/contact/CPU metadata so timing evidence can be attributed to one CUW route",
            ],
        },
        "legacy_iq_emps": iq_comparative(),
        "boundary": "static V18 can recover timing/recovery mechanics and capture targets, but the exact Sienna/Corolla factory row still requires the matching calibration package or a retained live CUW/GTS+ session",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
