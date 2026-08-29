#!/usr/bin/env python3
"""Verify recovered PCS Data Viewer TSS3 Operation-FFD semantics artifact."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ART = REPO / "data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json"
DIAG = REPO / "software/Techstream/gtsplus/unpacked/gtsplus/Toyota Diagnostics"


def check(label: str, condition: bool) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"[OK] {label}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    data = json.loads(ART.read_text())
    check("schema", data["schema"] == "gtsplus-pcs-data-viewer-tss3-managed-semantics-v1")
    proof = data["recovery_proof"]
    check("PCS MethodDef census", proof["method_def_count"] == 22564)
    check("PCS executable MethodDef census", proof["method_body_rva_count"] == 22447)
    check("all PCS managed method bodies materialized", proof["method_body_materialized_count"] == 22447)
    operation = data["operation_ffd"]
    check("Operation-FFD bit-assignment row census", operation["detail_row_count"] == 1130)
    check("Operation-FFD DID census", operation["did_count"] == 623)
    check("RoB/trigger row census", data["rob_codes"]["row_count"] == 47)
    check("TSS3 RoB system enum", data["rob_codes"]["system_type_enum"] == {"0": "None", "1": "AHBAHS", "2": "LDA", "3": "PCS", "4": "IDA", "5": "URSM", "6": "SDG"})
    usage = data["rob_codes"]["system_type_usage"]
    check("RoB SYSTEM_TYPE classifies triggers rather than DIDs", usage["did_decode_scans_full_definition_table"] and not usage["analyze_rob_parameter_reads_system_type"] and usage["multi_trigger_matching_compares_system_type_and_group"])
    check("physical conversion formula", operation["physical_value_contract"]["formula"] == "physical = raw * Lsb + Offset")

    rows = {(row["DataID"], row["DataName"]): row for row in operation["detail_rows"]}
    expected = {
        ("5282", "TSS request - lateral ID"): (1, 7, 8, "u", "1", "0", 0),
        ("5282", "TSS request - pinion angle"): (2, 7, 16, "s", "0.001", "0", 3),
        ("5282", "Steering assist gain"): (4, 7, 8, "u", "0.01", "0", 2),
        ("5282", "Damping control gain"): (5, 7, 8, "u", "0.01", "0", 2),
        ("5285", "Arbitration result_lateral ID"): (1, 7, 8, "u", "1", "0", 0),
        ("5531", "LDA Control Request Pinion Angle"): (2, 7, 16, "s", "0.001", "0", 3),
        ("560D", "EPS Pinion Angle"): (4, 7, 16, "s", "0.001", "0", 3),
        ("5631", "LTA Control Request Pinion Angle"): (2, 7, 16, "s", "0.001", "0", 3),
        ("57DE", "Arbitration result Pinion angle"): (1, 7, 16, "s", "0.001", "0", 3),
    }
    for key, values in expected.items():
        row = rows[key]
        actual = (row["BytePosition"], row["BitPosition"], row["BitLength"], row["Type"], row["Lsb"], row["Offset"], row["Point"])
        check(f"{key[0]} {key[1]} byte/bit/scaling contract", actual == values)

    arbitration = operation["lateral_arbitration_schema"]
    check("generic/LDA/LTA request tuple shape equivalence", arbitration["shape_equivalence"]["generic_5282_equals_lda_5531_equals_lta_5631"])
    check("generic lateral request DID", arbitration["generic_request"]["data_id"] == "5282")
    check("LDA lateral request DID", arbitration["feature_requests"]["LDA"]["data_id"] == "5531")
    check("LTA lateral request DID", arbitration["feature_requests"]["LTA"]["data_id"] == "5631")
    check("PDA(OAA) lateral request split DIDs", arbitration["feature_requests"]["PDA_OAA"]["data_ids"] == ["5A09", "5A0A", "5A0D"])
    check("LCA is present but has no dedicated recorder request tuple", arbitration["feature_requests"]["LCA"]["presence_field"]["DataName"] == "LCA presence information" and arbitration["feature_requests"]["LCA"]["dedicated_request_tuple_rows"] == [])
    check("generic arbitration result ID", arbitration["arbitration_result"]["lateral_id"]["DataID"] == "5285")
    check("generic arbitration result pinion angle", arbitration["arbitration_result"]["pinion_angle"]["DataID"] == "57DE")

    rob = {row["rob_code"]: row for row in data["rob_codes"]["rows"]}
    for code, name, sampling, pre, post in (
        ("209D", "LCS Steer Override", "0.2", 36, 8),
        ("2818", "Steering Angle Speed Threshold Exceeded", "0.4", 10, 11),
        ("2845", "LTA Hands Free Cancel", "1", 3, 7),
        ("240F", "LCA Cancel", "0.2", 20, 5),
    ):
        row = rob[code]
        check(f"RoB {code} definition", (row["DataName"], row["Sampling"], row["PreTriggerNumber"], row["PostTriggerNumber"]) == (name, sampling, pre, post))
        check(f"RoB {code} Toyota system family", row["SystemType"] == 2 and row["SystemName"] == "LDA")

    image = data["image_ffd"]["fcm_tss3"]
    check("FCM TSS3 image specs", image["accepted_specs"] == [5, 7])
    check("FCM TSS3 image geometry", (image["width"], image["height"], image["filename_format"]) == (360, 180, "{0:D3}.jpg"))
    check("FCM TSS3 image XOR key", image["encryption_key"] == 0xAA)
    status = image["encryption_status"]
    check("FCM TSS3 encryption DID contract", (status["diagnostic_did"], status["positive_response_prefix"], status["value_hex_offset"], status["value_hex_length"]) == ("2081", "622081", 6, 2))
    check("FCM TSS3 encryption predicate", status["unencrypted_value"] == "01" and status["decrypt_when"] == "value != 01")
    check("FCM TSS3 image decryption formula", image["decryption"]["per_byte"] == "reverse_bits8(cipher_byte) XOR 0xAA")

    def decrypt_byte(value: int) -> int:
        reversed_bits = int(f"{value:08b}"[::-1], 2)
        return reversed_bits ^ image["encryption_key"]

    check("FCM TSS3 image decryption vectors", [decrypt_byte(v) for v in (0x00, 0x01, 0x55, 0xAA, 0xFF)] == [0xAA, 0x2A, 0x00, 0xFF, 0x55])

    split = image["split_transport"]
    check("FCM TSS3 split/unsplit markers", split["detected_markers"] == {"split": "EB31", "unsplit": "EB21"})
    check("FCM TSS3 current split path", split["supported_path"] == "split EB31/EB33; Extract rejects the EB21 discriminator")
    check("FCM TSS3 split info markers", split["split_info_markers"] == ["621103", "622081", "EB33"])
    check("FCM TSS3 split image DID range", split["split_image_dids"] == [f"{v:04X}" for v in range(0x6002, 0x6018)])
    check("FCM TSS3 assembled image DID", split["assembled_raw_image_did"] == "6001")
    eb33 = split["eb33"]
    check("FCM TSS3 EB33 header geometry", (eb33["rob_code_hex_offset"], eb33["rob_code_hex_length"], eb33["frame_number_hex_offset"], eb33["frame_number_hex_length"], eb33["did_stream_hex_offset"]) == (4, 4, 8, 8, 18))
    check("FCM TSS3 EB33 variable length widths", eb33["length_hex_length"] == {"did_starts_with_6": 8, "other": 2} and eb33["length_number_style"] == "0x203 (hex)")
    frame = split["frame_number"]
    check("FCM TSS3 split frame constants", frame["split_divisor"] == 0x200 and frame["trigger_point_max"] == 10 and frame["format_width_hex"] == 8)
    check("FCM TSS3 occurrence discriminator", frame["occurrence_selector"] == "first four frame-number hex characters are 0000")
    check("FCM TSS3 occurrence decode formulas", frame["occurrence_decode"] == {"split": "value // 0x200", "trigger": "((value % 0x200 - 1) % 10) + 1", "data_set": "ceil((value % 0x200) / 10)", "trigger_type": "1 when trigger == 1, otherwise 2"})
    check("FCM TSS3 time-series decode formulas", frame["time_series_decode"] == {"high16": "frame_number[0:4] as hex", "low16": "frame_number[4:8] as hex", "split": "high16 // 0x200", "trigger": "low16 + 1", "data_set": "((high16 - split*0x200 - 1) // 10) + 1", "trigger_type": 3})

    def decode_frame_number(text: str) -> tuple[int, int, int, int]:
        if text[:4] == "0000":
            value = int(text, 16)
            split_no = value // 0x200
            remainder = value % 0x200
            trigger = ((remainder - 1) % 10) + 1
            data_set = (remainder + 9) // 10
            return split_no, data_set, trigger, 1 if trigger == 1 else 2
        high = int(text[:4], 16)
        low = int(text[4:], 16)
        split_no = high // 0x200
        trigger = low + 1
        data_set = ((high - split_no * 0x200 - 1) // 10) + 1
        return split_no, data_set, trigger, 3

    check("FCM TSS3 occurrence frame inverse vectors", decode_frame_number("00000201") == (1, 1, 1, 1) and decode_frame_number("00002C1B") == (22, 3, 7, 2))
    check("FCM TSS3 time-series frame inverse vectors", decode_frame_number("02010000") == (1, 1, 1, 3) and decode_frame_number("2C150006") == (22, 3, 7, 3))

    def parse_managed_did_stream(text: str) -> dict[str, str]:
        pos = 0
        out: dict[str, str] = {}
        while pos < len(text):
            did = text[pos:pos + 4]
            pos += 4
            width = 8 if did.startswith("6") else 2
            length = int(text[pos:pos + width], 16)
            pos += width
            out[did] = text[pos:pos + length * 2]
            pos += length * 2
        if pos != len(text):
            raise AssertionError("managed EB33 DID parser vector did not consume input")
        return out

    synthetic = "6002" + "00000003" + "A1B2C3" + "0501" + "02" + "1234"
    check("FCM TSS3 EB33 parser vector", parse_managed_did_stream(synthetic) == {"6002": "A1B2C3", "0501": "1234"})
    check("FCM TSS3 split reassembly contract", split["first_split_group_required"] == 1 and split["first_group_metadata_split_id_removed"] == "6002" and split["reassembly"].endswith("publish the concatenation as DID 6001"))

    for key in ("protected_exe", "protected_sidecar", "english_resources"):
        src = data["sources"][key]
        path = DIAG / src["path"]
        check(f"{key} source identity", path.stat().st_size == src["size"] and sha256(path) == src["sha256"])

    print("GTS+ PCS Data Viewer recovered TSS3 semantics verification passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
