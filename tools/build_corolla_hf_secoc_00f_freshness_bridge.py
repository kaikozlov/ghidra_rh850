#!/usr/bin/env python3
"""Correlate exact H/F 0x00F SecOC freshness state with live Corolla 0x0D7 traffic.

This builder intentionally joins distinct evidence classes without merging specimen identity:
- exact-H/F EPS receiver semantics from verified generated firmware artifacts;
- the Albino TSKM sync-only oracle from the same 2023 Corolla investigation as exact H;
- wire evolution from the pinned 2023 public Corolla route and Span's tracked 2025 rlog.

The raw route files are parsed through an explicitly supplied openpilot checkout so the
tracked JSON remains reproducible without vendoring cereal/logreader into this repo.
"""
from __future__ import annotations

import argparse
import bisect
import collections
import json
import statistics
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
H_VERIFY = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification.json"
H_DECOMP = REPO / "data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json"
STRUCTURAL = REPO / "data/generated/corolla_h_sienna_secoc_structural_comparison.json"
PUBLIC_EVIDENCE = REPO / "data/generated/corolla_2023_public_route_opendbc_evidence.json"
SPAN_EVIDENCE = REPO / "data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json"
EXTERNAL_LOCK = REPO / "external-references.lock.json"
DEFAULT_PUBLIC = REPO / "REFERENCE/public_route_corolla_2023_segment0_rlog.zst"
DEFAULT_SPAN = REPO / "community/spanconstant/span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst"
DEFAULT_ALBINO = REPO / "community/albinoelephant/can_oracle.ndjson"
DEFAULT_OUTPUT = REPO / "data/generated/corolla_hf_secoc_00f_freshness_bridge.json"


def sha256(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def median_int(values: list[int]) -> int | float | None:
    if not values:
        return None
    return statistics.median(values)


def counter_json(counter: collections.Counter[Any]) -> dict[str, int]:
    return {str(k): v for k, v in sorted(counter.items(), key=lambda kv: str(kv[0]))}


def decode_sync(dat: bytes) -> tuple[int, int, int]:
    if len(dat) != 8:
        raise ValueError(f"0x00F must be 8 bytes, got {len(dat)}")
    trip = (dat[0] << 8) | dat[1]
    reset = (dat[2] << 12) | (dat[3] << 4) | (dat[4] >> 4)
    mac28 = ((dat[4] & 0xF) << 24) | (dat[5] << 16) | (dat[6] << 8) | dat[7]
    return trip, reset, mac28


def decode_fd_ordinary_fv4(dat: bytes) -> tuple[int, int, int]:
    if len(dat) != 32:
        raise ValueError(f"ordinary H/F FD SecOC PDU must be 32 bytes, got {len(dat)}")
    fv4 = dat[28] >> 4
    return fv4, (fv4 >> 2) & 3, fv4 & 3


def reset_candidates(current: int, reset_low2: int) -> list[tuple[int, int]]:
    """Exact H 0x89CDA trial order, excluding out-of-range reset20 values."""
    out: list[tuple[int, int]] = []
    for delta in (0, -1, 1, -2, 2):
        candidate = current + delta
        if 0 <= candidate <= 0xFFFFF and (candidate & 3) == reset_low2:
            out.append((delta, candidate))
    return out


def expected_locked_sha(path: Path) -> str:
    lock = json.loads(EXTERNAL_LOCK.read_text())
    rel = str(path.resolve().relative_to(REPO))
    for group in lock.values():
        if not isinstance(group, list):
            continue
        for row in group:
            if isinstance(row, dict) and row.get("path") == rel:
                return str(row["sha256"])
    raise SystemExit(f"no external lock entry for {rel}")


def analyze_albino_sync_oracle(path: Path) -> dict[str, Any]:
    expected_sha = expected_locked_sha(path)
    actual_sha = sha256(path)
    if actual_sha != expected_sha:
        raise SystemExit(f"Albino 0x00F oracle SHA mismatch: expected {expected_sha}, got {actual_sha}")

    by_bus: dict[int, list[tuple[int, int, int, int, bytes]]] = collections.defaultdict(list)
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if int(row["addr"]) != 0x00F:
            raise SystemExit(f"Albino oracle contains non-0x00F row: {row}")
        dat = bytes.fromhex(row["data"])
        trip, reset, mac = decode_sync(dat)
        by_bus[int(row["bus"])].append((round(float(row["ts_ms"]) * 1_000_000), trip, reset, mac, dat))

    if sorted(by_bus) != [0, 2]:
        raise SystemExit(f"unexpected Albino oracle buses: {sorted(by_bus)}")
    payloads0 = [r[4] for r in by_bus[0]]
    payloads2 = [r[4] for r in by_bus[2]]
    if payloads0 != payloads2:
        raise SystemExit("Albino bus0/bus2 sync payload sequences differ")

    sync = by_bus[0]
    states: list[tuple[int, int, int, int, bytes]] = []
    for row in sync:
        if not states or (row[1], row[2]) != (states[-1][1], states[-1][2]):
            states.append(row)
    intervals = [states[i][0] - states[i - 1][0] for i in range(1, len(states))]
    reset_deltas = collections.Counter((states[i][2] - states[i - 1][2]) & 0xFFFFF for i in range(1, len(states)))
    state_counts = collections.Counter((r[1], r[2]) for r in sync)
    state_payloads: dict[tuple[int, int], set[bytes]] = collections.defaultdict(set)
    for row in sync:
        state_payloads[(row[1], row[2])].add(row[4])

    return {
        "source": {
            "path": str(path.resolve().relative_to(REPO)),
            "sha256": actual_sha,
            "identity_boundary": (
                "Contributor-supplied TSKM 0x00F oracle from the same 2023 Corolla investigation as the exact-H dump corpus, but CAN collection and "
                "memory dumping were separate jobs; this is not a same-runtime-epoch CodeFlash-to-CAN proof."
            ),
        },
        "rows": len(sync) + len(by_bus[2]),
        "rows_per_bus": {"0": len(sync), "2": len(by_bus[2])},
        "bus0_bus2_payload_sequences_identical": True,
        "trip_values": sorted({r[1] for r in sync}),
        "trip_values_hex": [f"0x{x:04X}" for x in sorted({r[1] for r in sync})],
        "reset_first": sync[0][2],
        "reset_last": sync[-1][2],
        "unique_states": len(state_counts),
        "all_repeated_state_payloads_byte_identical": all(len(v) == 1 for v in state_payloads.values()),
        "state_copy_counts": counter_json(collections.Counter(state_counts.values())),
        "reset_transition_deltas": counter_json(reset_deltas),
        "state_transition_period_ns_median": median_int(intervals),
        "state_transition_interval_count": len(intervals),
        "state_transition_intervals_280_to_320ms": sum(280_000_000 <= dt <= 320_000_000 for dt in intervals),
        "initial_collection_gap": {
            "observed_reset_delta": 115,
            "interpretation": "The early 1873->1988 discontinuity occurs inside the TSKM collection artifact; later consecutive reset states resume at nominal ~300 ms cadence."
        },
        "first_frames": [
            {"trip": trip, "reset": reset, "mac28": f"0x{mac:07X}", "payload": dat.hex()}
            for _, trip, reset, mac, dat in states[:8]
        ],
    }


def analyze_capture(name: str, path: Path, LogReader: Any, expected_sha: str) -> dict[str, Any]:
    actual_sha = sha256(path)
    if actual_sha != expected_sha:
        raise SystemExit(f"{name} rlog SHA mismatch: expected {expected_sha}, got {actual_sha}")

    # Preserve pandad's CAN-array order as well as Event.logMonoTime. pandad serializes
    # raw_can_data in the order produced by Panda::unpack_can_buffer, so this sequence
    # distinguishes 0x00F-before-D7 from D7-before-0x00F inside one batched CAN event.
    sync: list[tuple[int, int, int, int, int, bytes]] = []
    d7: list[tuple[int, int, int, int, int, bytes]] = []
    frame_seq = 0
    for ev in LogReader(str(path), sort_by_time=True):
        if ev.which() != "can":
            continue
        t = int(ev.logMonoTime)
        for c in ev.can:
            seq = frame_seq
            frame_seq += 1
            if int(c.src) != 1:
                continue
            addr = int(c.address)
            dat = bytes(c.dat)
            if addr == 0x00F:
                trip, reset, mac = decode_sync(dat)
                sync.append((t, seq, trip, reset, mac, dat))
            elif addr == 0x0D7:
                fv4, msg2, reset2 = decode_fd_ordinary_fv4(dat)
                d7.append((t, seq, fv4, msg2, reset2, dat))

    if not sync or not d7:
        raise SystemExit(f"{name}: missing 0x00F or 0x0D7 on incoming logical bus 1")

    sync_periods = [sync[i][0] - sync[i - 1][0] for i in range(1, len(sync))]
    transition_rows: list[tuple[int, int, int, int, int, int]] = []
    # t, seq, old_trip, old_reset, new_trip, new_reset
    prev = sync[0]
    for row in sync[1:]:
        if (row[2], row[3]) != (prev[2], prev[3]):
            transition_rows.append((row[0], row[1], prev[2], prev[3], row[2], row[3]))
        prev = row
    transition_periods = [transition_rows[i][0] - transition_rows[i - 1][0] for i in range(1, len(transition_rows))]

    state_payloads: dict[tuple[int, int], set[bytes]] = collections.defaultdict(set)
    state_counts: collections.Counter[tuple[int, int]] = collections.Counter()
    state_macs: dict[tuple[int, int], set[int]] = collections.defaultdict(set)
    for _, _, trip, reset, mac, dat in sync:
        key = (trip, reset)
        state_payloads[key].add(dat)
        state_counts[key] += 1
        state_macs[key].add(mac)

    runs: list[int] = []
    current: tuple[int, int] | None = None
    n = 0
    for _, _, trip, reset, _, _ in sync:
        key = (trip, reset)
        if key != current:
            if n:
                runs.append(n)
            current = key
            n = 1
        else:
            n += 1
    if n:
        runs.append(n)

    reset_transition_deltas = collections.Counter()
    trip_transition_deltas = collections.Counter()
    for _, _, old_trip, old_reset, new_trip, new_reset in transition_rows:
        if new_trip != old_trip:
            trip_transition_deltas[(new_trip - old_trip) & 0xFFFF] += 1
        else:
            reset_transition_deltas[(new_reset - old_reset) & 0xFFFFF] += 1
    near_300ms_transition_intervals = sum(280_000_000 <= dt <= 320_000_000 for dt in transition_periods)

    sync_keys = [(row[0], row[1]) for row in sync]
    mapped: list[dict[str, Any]] = []
    unmapped = 0
    multi_match = 0
    for t, seq, fv4, msg2, reset2, dat in d7:
        j = bisect.bisect_right(sync_keys, (t, seq)) - 1
        if j < 0:
            continue
        current_trip, current_reset = sync[j][2], sync[j][3]
        matches = reset_candidates(current_reset, reset2)
        if not matches:
            unmapped += 1
            continue
        if len(matches) > 1:
            multi_match += 1
        delta, candidate_reset = matches[0]
        mapped.append({
            "t": t,
            "seq": seq,
            "fv4": fv4,
            "message_low2": msg2,
            "reset_low2": reset2,
            "sync_trip": current_trip,
            "sync_reset": current_reset,
            "candidate_reset": candidate_reset,
            "candidate_delta": delta,
            "trailer": dat[28:32].hex(),
        })

    # Reconstruct message8 independently inside each mapped trip/reset epoch.  This is
    # exactly H 0x89D58's same-epoch rule; the first observed value is only an anchor.
    epoch_rows: dict[tuple[int, int], list[dict[str, Any]]] = collections.defaultdict(list)
    last_msg: dict[tuple[int, int], int] = {}
    same_epoch_deltas: collections.Counter[int] = collections.Counter()
    for row in mapped:
        key = (row["sync_trip"], row["candidate_reset"])
        low2 = row["message_low2"]
        if key not in last_msg:
            msg = low2
        else:
            prev_msg = last_msg[key]
            msg = (prev_msg & ~3) | low2
            if low2 <= (prev_msg & 3):
                msg += 4
            same_epoch_deltas[msg - prev_msg] += 1
        row["reconstructed_message8"] = msg
        last_msg[key] = msg
        epoch_rows[key].append(row)

    epoch_frame_counts = collections.Counter(len(rows) for rows in epoch_rows.values())
    exact_1_to_15 = 0
    complete_15 = 0
    non_initial_first_msg = collections.Counter()
    ordered_epochs = sorted(epoch_rows.items(), key=lambda kv: kv[1][0]["t"])
    for idx, (_, rows) in enumerate(ordered_epochs):
        seq = [r["reconstructed_message8"] for r in rows]
        if len(rows) == 15:
            complete_15 += 1
            exact_1_to_15 += int(seq == list(range(1, 16)))
        if idx > 0:
            non_initial_first_msg[rows[0]["message_low2"]] += 1

    # At each new sync state, characterize the immediately preceding/current-epoch D7
    # and the first D7 that actually uses the new reset fragment.
    d7_keys = [(row[0], row[1]) for row in d7]
    transition_old_reset_after_sync = 0
    transition_old_reset_before_sync = 0
    transition_old_after_sync_message3 = 0
    first_new_reset_delays_ns: list[int] = []
    first_new_reset_msg_low2 = collections.Counter()
    exact_plus1_transitions = 0
    for t, sync_seq, old_trip, old_reset, new_trip, new_reset in transition_rows:
        if new_trip == old_trip and new_reset == old_reset + 1:
            exact_plus1_transitions += 1
        j = bisect.bisect_left(d7_keys, (t, -1))
        while j < len(d7) and d7[j][0] == t:
            _, d7_seq, _, msg2, reset2, _ = d7[j]
            if reset2 == (old_reset & 3):
                if d7_seq > sync_seq:
                    transition_old_reset_after_sync += 1
                    transition_old_after_sync_message3 += int(msg2 == 3)
                else:
                    transition_old_reset_before_sync += 1
            j += 1
        j = bisect.bisect_right(d7_keys, (t, sync_seq))
        while j < len(d7) and d7[j][4] != (new_reset & 3):
            j += 1
        if j < len(d7):
            first_new_reset_delays_ns.append(d7[j][0] - t)
            first_new_reset_msg_low2[d7[j][3]] += 1

    trip_values = sorted({row[2] for row in sync})
    candidate_deltas = collections.Counter(row["candidate_delta"] for row in mapped)

    return {
        "source": {
            "path": str(path.relative_to(REPO)) if path.is_relative_to(REPO) else str(path),
            "sha256": actual_sha,
        },
        "wire_counts": {"0x00F": len(sync), "0x0D7": len(d7), "mapped_0x0D7_after_first_00F": len(mapped)},
        "sync_00f": {
            "trip_values": trip_values,
            "trip_values_hex": [f"0x{x:04X}" for x in trip_values],
            "reset_first": sync[0][3],
            "reset_last": sync[-1][3],
            "unique_states": len(state_payloads),
            "frame_period_ns_median": median_int(sync_periods),
            "state_transition_period_ns_median": median_int(transition_periods),
            "state_transition_interval_count": len(transition_periods),
            "state_transition_intervals_280_to_320ms": near_300ms_transition_intervals,
            "state_run_lengths": counter_json(collections.Counter(runs)),
            "reset_transition_deltas_same_trip": counter_json(reset_transition_deltas),
            "trip_transition_deltas": counter_json(trip_transition_deltas),
            "all_repeated_state_payloads_byte_identical": all(len(v) == 1 for v in state_payloads.values()),
            "all_repeated_state_mac28_identical": all(len(v) == 1 for v in state_macs.values()),
            "unique_mac28_count": len({next(iter(v)) for v in state_macs.values()}),
            "first_frames": [
                {"trip": trip, "reset": reset, "mac28": f"0x{mac:07X}", "payload": dat.hex()}
                for _, _, trip, reset, mac, dat in sync[:5]
            ],
        },
        "d7_receiver_model_replay": {
            "unmapped_after_first_sync": unmapped,
            "multiple_reset_candidates_before_auth_retry": multi_match,
            "candidate_delta_counts": counter_json(candidate_deltas),
            "same_epoch_message8_delta_counts": counter_json(same_epoch_deltas),
            "epochs_observed": len(epoch_rows),
            "epoch_frame_counts": counter_json(epoch_frame_counts),
            "complete_15_frame_epochs": complete_15,
            "complete_epochs_exact_message8_1_through_15": exact_1_to_15,
            "non_initial_epoch_first_message_low2": counter_json(non_initial_first_msg),
        },
        "transition_ordering": {
            "sync_state_transitions": len(transition_rows),
            "exact_same_trip_reset_plus1_transitions": exact_plus1_transitions,
            "d7_same_timestamp_after_sync_using_previous_reset_low2": transition_old_reset_after_sync,
            "d7_same_timestamp_before_sync_using_previous_reset_low2": transition_old_reset_before_sync,
            "those_after_sync_previous_reset_frames_with_message_low2_3": transition_old_after_sync_message3,
            "first_d7_new_reset_delay_ns_median": median_int(first_new_reset_delays_ns),
            "first_d7_new_reset_delay_ns_min": min(first_new_reset_delays_ns) if first_new_reset_delays_ns else None,
            "first_d7_new_reset_delay_ns_max": max(first_new_reset_delays_ns) if first_new_reset_delays_ns else None,
            "first_d7_new_reset_message_low2": counter_json(first_new_reset_msg_low2),
        },
    }


def static_model() -> dict[str, Any]:
    h = json.loads(H_VERIFY.read_text())
    decomp = json.loads(H_DECOMP.read_text())
    comp = json.loads(STRUCTURAL.read_text())
    funcs = {f["entry"]: f for f in decomp["functions"]}
    prof = comp["profile_tables"]["corolla_h_f"]["records"][0]
    if prof["data_id"] != "0x00F" or prof["full_freshness_bits"] != 36 or prof["transmitted_freshness_bits"] != 36:
        raise SystemExit(f"unexpected H sync profile: {prof}")
    return {
        "applies_to": comp["applies_to"],
        "profile_record": {
            "address": prof["address"],
            "data_id": prof["data_id"],
            "freshness_id": prof["freshness_id"],
            "secured_pdu_length": prof["secured_pdu_length"],
            "full_freshness_bits": prof["full_freshness_bits"],
            "transmitted_freshness_bits": prof["transmitted_freshness_bits"],
            "transmitted_cmac_bits": prof["transmitted_cmac_bits"],
            "full_cmac_bits": prof["full_cmac_bits"],
            "authentication_retry_limit": prof["authentication_retry_limit"],
            "cryptoif_busy_retry_limit": prof["cryptoif_busy_retry_limit"],
            "record_sha256": prof["record_sha256"],
        },
        "wire_layout": {
            "B0_B1": "trip16, big-endian",
            "B2_B3_B4_7_4": "reset20, big-endian",
            "B4_3_0_B5_B6_B7": "CMAC_MSB28",
            "freshness36": "trip16 || reset20",
            "authenticated_input": "00 0F || trip16 || reset20 || 0000b",
            "authenticated_input_bytes": 7,
            "application_payload_bytes": 0,
        },
        "ram_state": h["freshness_acceptance"]["global_epoch_source"],
        "sync_acceptance": {
            "reconstruct_function": "0x00089F6E",
            "commit_function": "0x0008A130",
            "strict_forward": "new_trip > current_trip OR (new_trip == current_trip AND new_reset > current_reset)",
            "equal_state_result": 1,
            "trip_wrap_threshold": h["freshness_acceptance"]["trip_wrap"]["sync_threshold"],
            "trip_wrap_rule": h["freshness_acceptance"]["trip_wrap"]["wrap_acceptance"],
            "trip_wrap_clears_b6_and_d7": h["freshness_acceptance"]["trip_wrap"]["b6_state_cleared_on_authenticated_trip_wrap"],
            "stage_then_commit_after_cmac": True,
        },
        "ordinary_freshness": {
            "wire_fv4": h["transmitted_freshness"],
            "full_freshness": h["transmitted_freshness"]["full_freshness"],
            "reset_candidate_search": h["freshness_acceptance"]["reset_candidate_search"],
            "same_epoch_message_rule": h["freshness_acceptance"]["message_reconstruction_same_epoch"],
            "new_epoch_message_rule": h["freshness_acceptance"]["epoch_transition"]["new_epoch_message"],
            "d7_freshness_id": 1,
            "b6_freshness_id": 2,
            "independent_ordinary_slots": True,
        },
        "decompiler_bindings": {
            "authenticated_input_build": {"entry": "0x00087FC2", "body_sha256": funcs["0x00087FC2"]["body_sha256"]},
            "sync_parse": {"entry": "0x00089B46", "body_sha256": funcs["0x00089B46"]["body_sha256"]},
            "sync_pack": {"entry": "0x000899B4", "body_sha256": funcs["0x000899B4"]["body_sha256"]},
            "sync_reconstruct": {"entry": "0x00089F6E", "body_sha256": funcs["0x00089F6E"]["body_sha256"]},
            "sync_commit": {"entry": "0x0008A130", "body_sha256": funcs["0x0008A130"]["body_sha256"]},
            "normal_reset_search": {"entry": "0x00089CDA", "body_sha256": funcs["0x00089CDA"]["body_sha256"]},
            "normal_window": {"entry": "0x00089D58", "body_sha256": funcs["0x00089D58"]["body_sha256"]},
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--span-rlog", type=Path, default=DEFAULT_SPAN)
    ap.add_argument("--public-rlog", type=Path, default=DEFAULT_PUBLIC)
    ap.add_argument("--albino-oracle", type=Path, default=DEFAULT_ALBINO)
    ap.add_argument("--openpilot-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = ap.parse_args()

    public_expected = json.loads(PUBLIC_EVIDENCE.read_text())["source"]
    span_expected = json.loads(SPAN_EVIDENCE.read_text())["source"]
    if not args.span_rlog.is_file() or not args.public_rlog.is_file() or not args.albino_oracle.is_file():
        raise SystemExit(
            f"missing raw capture(s): span={args.span_rlog.is_file()} public={args.public_rlog.is_file()} albino={args.albino_oracle.is_file()}"
        )

    sys.path.insert(0, str(args.openpilot_root.resolve()))
    from openpilot.tools.lib.logreader import (
        LogReader,  # type: ignore[import-not-found]
    )

    captures = {
        "albino_2023_tskm_sync_oracle": analyze_albino_sync_oracle(args.albino_oracle),
        "span_2025_discord": analyze_capture("span", args.span_rlog, LogReader, span_expected["sha256"]),
        "public_2023": analyze_capture("public", args.public_rlog, LogReader, public_expected["sha256"]),
    }
    span = captures["span_2025_discord"]
    public = captures["public_2023"]

    artifact = {
        "schema": 1,
        "title": "Corolla H/F 0x00F SecOC synchronization -> ordinary freshness bridge",
        "evidence_boundary": (
            "Exact H/F firmware proves receiver-side 0x00F and D7/B6 freshness semantics. The two captures prove wire evolution but are not exact "
            "H/F firmware-identity joins and the slot-4 key is unavailable, so their MAC28 values are not independently cryptographically verified here. "
            "D7 is used as the live ordinary-PDU oracle because exact H/F puts D7 and B6 under the same authenticated 0x00F trip/reset state while retaining "
            "independent per-PDU message8 slots. No D7 message counter is transferred to B6."
        ),
        "static_h_f_receiver": static_model(),
        "captures": captures,
        "cross_capture_conclusions": {
            "sync_wire_is_direct_epoch_oracle": True,
            "observed_trip_counter_constant_inside_each_60s_capture": True,
            "observed_reset_state_period_nominal_ms": 300,
            "span_reset_transition_intervals_280_to_320ms": [
                span["sync_00f"]["state_transition_intervals_280_to_320ms"],
                span["sync_00f"]["state_transition_interval_count"],
            ],
            "public_reset_transition_intervals_280_to_320ms": [
                public["sync_00f"]["state_transition_intervals_280_to_320ms"],
                public["sync_00f"]["state_transition_interval_count"],
            ],
            "receiver_reset_candidate_search_replays_all_post_sync_d7": (
                span["d7_receiver_model_replay"]["unmapped_after_first_sync"] == 0
                and public["d7_receiver_model_replay"]["unmapped_after_first_sync"] == 0
            ),
            "span_logged_order_exercises_current_minus_1_overlap": (
                span["transition_ordering"]["d7_same_timestamp_after_sync_using_previous_reset_low2"]
                == span["transition_ordering"]["sync_state_transitions"]
                and span["transition_ordering"]["d7_same_timestamp_before_sync_using_previous_reset_low2"] == 0
            ),
            "observed_candidate_deltas": {
                "span": span["d7_receiver_model_replay"]["candidate_delta_counts"],
                "public": public["d7_receiver_model_replay"]["candidate_delta_counts"],
            },
            "all_complete_d7_epochs_are_message8_1_through_15": (
                span["d7_receiver_model_replay"]["complete_15_frame_epochs"]
                == span["d7_receiver_model_replay"]["complete_epochs_exact_message8_1_through_15"]
                and public["d7_receiver_model_replay"]["complete_15_frame_epochs"]
                == public["d7_receiver_model_replay"]["complete_epochs_exact_message8_1_through_15"]
            ),
            "interpretation": (
                "The live D7 sequence exercises the exact H reset search/window model under logged receive order: in Span, every new 0x00F is stored before "
                "one same-logMonoTime old-reset D7, which therefore maps to current-1; the next new-reset D7 seeds a new ordinary epoch, and within an epoch "
                "message8 advances by one. Physical sub-event timing inside one batched CAN publication is not independently reconstructed."
            ),
        },
        "b6_sender_implication": {
            "what_00f_reveals": "36/46 meaningful B6 freshness bits directly: trip16 and reset20.",
            "what_remains_per_b6": "message8 is B6-local state; FV4 additionally repeats reset_low2. D7's message8 must not be copied into B6.",
            "new_epoch_reanchor": (
                "If the stock B6 producer is suppressed before the EPS commits a strictly newer authenticated 0x00F trip/reset, the first B6 under that new epoch "
                "does not require knowledge of the previous B6 message8: H 0x89D58 seeds full message8 from transmitted message_low2 (0..3). Thereafter the "
                "replacement sender can maintain the B6-local message8 and FV4 itself."
            ),
            "same_epoch_boundary": (
                "Without a new epoch, the receiver reconstructs the next message8 congruent with transmitted message_low2 (+1..+4 from committed B6), so the "
                "sender still needs the reconstructed full message8 to compute a correct CMAC."
            ),
            "transition_race": (
                "H's current-1 reset candidate and the live D7 transition show that one old-reset ordinary frame can remain valid immediately after 0x00F advances. "
                "A replacement sender should therefore treat a visible new 0x00F plus subsequent ordinary new-reset traffic as the clean epoch boundary rather than "
                "assuming simultaneous bus timestamps imply atomic sender rollover."
            ),
            "still_blocking": [
                "slot-4 secret value or approved slot-4 CMAC operation",
                "stock B6 producer suppression / relay-side ownership",
                "B6 sender cadence and complete application-payload policy",
                "live B6 capture to validate the sender's own message8 initialization/cadence; D7 proves receiver arithmetic, not B6 sender policy",
            ],
        },
        "prior_art_note": (
            "Current comma/opendbc Toyota SecOC code independently treats 0x00F RESET_CNT changes as the event that resets per-PDU sender message counters. "
            "That is useful sender-side prior art, but the live H/F-family conclusion above is based on D7 wire evolution and exact H receiver code, not transferred "
            "from the older Toyota implementation."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
