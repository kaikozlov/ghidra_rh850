#!/usr/bin/env python3
"""Exact-target 2026 Camry EPS volatile-RAM acquisition using authenticated range payloads.

The memory result is read-only PE1 LocalRAM or GlobalRAM. The acquisition mechanism
enters the EPS bootloader, performs one boot SecurityAccess unlock, writes the
bootloader's temporary 0203/0201/0202 payload state, downloads one 4 KiB authenticated
range-reader payload, verifies it with 0x10F0, then invokes the 0xFF00 callback route.
It never programs flash and refuses any application identity/route other than the
retained 8965F3307000 Camry specimen.

The LocalRAM profile necessarily overwrites FEBF0000..FEBF0FFF with the 4 KiB payload
before reading the range. Those 4096 bytes are therefore acquisition-clobbered and
must not be interpreted as the original application/boot RAM contents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# When executed from /cache on AGNOS, make the active openpilot checkout importable.
if Path("/data/openpilot").is_dir():
    sys.path.insert(0, "/data/openpilot")

EXPECTED_APP_F181 = bytes.fromhex(
    "023839363546333330373030300000000038413331313333303331303000000000"
)
EXPECTED_BOOT_F181 = b"\x02" + b"!" * 32
PROFILES = {
    "local_ram_pe1": {
        "label": "PE1 LocalRAM",
        "payload_sha256": "fbb1f5bd352c3f0bf416d6b1ef6a7696f97cad2b9f49570ca859207f3269e44f",
        "start": 0xFEBE0000,
        "end": 0xFEC00000,
        "clobber_start": 0xFEBF0000,
        "clobber_end": 0xFEBF1000,
    },
    "global_ram": {
        "label": "GlobalRAM",
        "payload_sha256": "43d00fdaf790c6deb230d3a4e7b8f8bd17e077a100fa53ebb194532f55c510fd",
        "start": 0xFEEF8000,
        "end": 0xFEF08000,
        "clobber_start": None,
        "clobber_end": None,
    },
}
TX = 0x7A1
RX = 0x7A9
BUS = 1
ELM327_PARAM = 1
LOAD_ADDR = 0xFEBF0000
LOAD_SIZE = 0x1000
TRIGGER_ADDR = 0x000E0000
TRIGGER_SIZE = 0x00008000
IDLE_TIMEOUT = 10.0
MAX_SECONDS = 1200.0
RESPONSE_PENDING = bytes.fromhex("037f317800000000")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("profile", choices=tuple(PROFILES))
    ap.add_argument("payload", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("/cache/tsk/camry-ram"))
    args = ap.parse_args()

    profile = PROFILES[args.profile]
    range_start = int(profile["start"])
    range_end = int(profile["end"])
    payload = args.payload.read_bytes()
    if len(payload) != LOAD_SIZE or sha256(payload) != profile["payload_sha256"]:
        ap.error(f"{profile['label']} payload hash/size mismatch")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = args.out_dir / f"camry_8965F3307000_{args.profile}_{stamp}"
    run_path = base.with_suffix(".run.json")
    dump_path = base.with_suffix(".bin")
    coverage_path = base.with_suffix(".coverage.bin")

    report = {
        "schema": "camry-8965f3307000-ram-acquisition-v1",
        "started_at": utc_now(),
        "target": {
            "application_f181_hex": EXPECTED_APP_F181.hex(),
            "boot_f181_hex": EXPECTED_BOOT_F181.hex(),
            "tx": "0x7a1", "rx": "0x7a9", "bus": BUS,
            "elm327_param": ELM327_PARAM, "semantic_path": "normal-harness",
        },
        "payload": {
            "sha256": profile["payload_sha256"],
            "size": len(payload),
            "source": f"calvinpark-openpilot dump branch {args.payload.name}",
            "profile": args.profile,
            "label": profile["label"],
            "range": [f"0x{range_start:08x}", f"0x{range_end:08x}"],
            "clobber_range": (
                [f"0x{profile['clobber_start']:08x}", f"0x{profile['clobber_end']:08x}"]
                if profile["clobber_start"] is not None else None
            ),
        },
        "stages": [],
        "result": {},
    }

    def save() -> None:
        run_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")

    def stage(name: str, status: str, **detail) -> None:
        row = {"at": utc_now(), "name": name, "status": status, **detail}
        report["stages"].append(row)
        save()
        shown = " ".join(f"{k}={v}" for k, v in detail.items() if k not in {"seed_hex", "key_hex"})
        print(f"[{status.upper()}] {name}" + (f" {shown}" if shown else ""), flush=True)

    save()

    # Use the already-installed openpilot environment on comma. Do not construct a venv.
    from Crypto.Cipher import AES
    from panda import Panda
    from panda.python.spi import PandaSpiException
    from opendbc.car.structs import CarParams
    from opendbc.car.isotp import isotp_send
    from opendbc.car.uds import (
        ACCESS_TYPE, SESSION_TYPE, SERVICE_TYPE, ROUTINE_CONTROL_TYPE,
        InvalidServiceIdError, MessageTimeoutError, NegativeResponseError,
    )
    from tsk.lib.bootstrap_profile import BOOT_SA_SECRET
    from tsk.lib.programming import enter_programming_bootloader, uds_client

    subprocess.run(["pkill", "-9", "-f", "manager.py"], check=False)
    subprocess.run(["pkill", "-9", "-f", "pandad"], check=False)
    time.sleep(2.0)

    serials = Panda.list()
    if len(serials) != 1:
        stage("panda", "failed", detail=f"expected one Panda, found {len(serials)}")
        return 2
    panda = Panda(serials[0])
    route = {
        "tx": TX, "rx": RX, "tx_bus": BUS, "rx_bus": BUS,
        "elm327_param": ELM327_PARAM, "semantic_path": "normal-harness",
    }

    try:
        panda.set_safety_mode(CarParams.SafetyModel.elm327, ELM327_PARAM)
        time.sleep(0.05)
        app = uds_client(panda, route, timeout=0.5, response_pending_timeout=3.0)
        try:
            app.diagnostic_session_control(SESSION_TYPE.DEFAULT)
        except Exception:
            pass
        app_f181 = bytes(app.read_data_by_identifier(0xF181))
        if app_f181 != EXPECTED_APP_F181:
            stage("application identity", "failed", observed_hex=app_f181.hex())
            return 3
        stage("application identity", "accepted", observed_hex=app_f181.hex())

        # Independently require Not Ready to Drive from the already-validated Camry
        # 0x51E B0[7] Ready carrier before any programming/session handoff.
        ready_samples = []
        ready_deadline = time.monotonic() + 2.5
        while time.monotonic() < ready_deadline:
            for addr, *_rest, data, bus in panda.can_recv():
                data = bytes(data)
                if int(bus) == BUS and int(addr) == 0x51E and len(data) == 8:
                    ready_samples.append((data[0] >> 7) & 1)
            if ready_samples:
                break
            time.sleep(0.001)
        if not ready_samples:
            stage("NRTD Ready-status guard", "failed", detail="no bus1 0x51E sample")
            return 31
        if any(ready_samples):
            stage("NRTD Ready-status guard", "failed", ready_values=sorted(set(ready_samples)))
            return 32
        stage("NRTD Ready-status guard", "accepted", ready_values=[0])

        # Application -> bootloader. This helper treats the reset/handoff asynchronously and
        # requires the endpoint to reappear on the exact preserved physical route.
        boot_route, handoff = enter_programming_bootloader(
            panda, route, prepare_sessions=True, settle_extended=0.7, reappearance_timeout=8.0,
        )
        if not (
            int(boot_route["tx"]) == TX and int(boot_route["rx"]) == RX
            and int(boot_route["tx_bus"]) == BUS and int(boot_route["rx_bus"]) == BUS
            and int(boot_route.get("elm327_param", ELM327_PARAM)) == ELM327_PARAM
        ):
            stage("programming handoff", "failed", detail="route changed", handoff=handoff)
            return 4
        stage("programming handoff", "accepted", handoff=handoff)

        boot = uds_client(panda, boot_route, timeout=0.5, response_pending_timeout=3.0)
        boot_f181 = bytes(boot.read_data_by_identifier(0xF181))
        if boot_f181 != EXPECTED_BOOT_F181:
            stage("boot identity", "failed", observed_hex=boot_f181.hex())
            return 5
        stage("boot identity", "accepted", observed_hex=boot_f181.hex())

        # Cheap direct-read discriminator. The analyzed Sienna bootloader marks SID 0x23
        # unsupported, but a newer F33 bootloader might expose it. A success is retained as
        # evidence; the authenticated payload flow remains the fallback.
        try:
            boot.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
            direct = bytes(boot.read_memory_by_address(range_start, 0x10))
            stage("boot SID 0x23 RAM probe", "accepted", data_hex=direct.hex())
        except NegativeResponseError as e:
            stage("boot SID 0x23 RAM probe", "rejected", nrc=f"0x{int(e.error_code):02x}")
        except (InvalidServiceIdError, MessageTimeoutError) as e:
            stage("boot SID 0x23 RAM probe", "rejected", detail=type(e).__name__)

        # Re-establish the exact bootloader programming ladder before the one counted key.
        boot = uds_client(panda, boot_route, timeout=0.5, response_pending_timeout=3.0)
        boot.diagnostic_session_control(SESSION_TYPE.DEFAULT)
        boot.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
        boot.diagnostic_session_control(SESSION_TYPE.PROGRAMMING)
        stage("boot programming session", "accepted")

        seed_record = bytes(16)
        seed = bytes(boot.security_access(ACCESS_TYPE.REQUEST_SEED, data_record=seed_record))
        if len(seed) != 16:
            stage("boot SecurityAccess seed", "failed", detail=f"unexpected seed length {len(seed)}")
            return 6
        stage("boot SecurityAccess seed", "accepted", seed_hex=seed.hex())
        derived = AES.new(BOOT_SA_SECRET, AES.MODE_ECB).decrypt(seed_record)
        key = AES.new(derived, AES.MODE_ECB).encrypt(seed)
        try:
            boot.security_access(ACCESS_TYPE.SEND_KEY, key)
        except NegativeResponseError as e:
            stage("boot SecurityAccess key", "rejected", nrc=f"0x{int(e.error_code):02x}")
            return 7
        stage("boot SecurityAccess key", "accepted", key_hex=key.hex())

        # Calvin/blurbdust old-vs-new UDS discriminator. Old stack accepts 0203=zeros.
        # New stack uses CPU0 offset selector 01 00 00 00 00 and 45 01 routine grammar.
        uds_variant = None
        try:
            boot.write_data_by_identifier(0x203, bytes(5))
            uds_variant = "old"
            stage("UDS variant / DID 0x0203", "accepted", variant="old", value="0000000000")
        except NegativeResponseError as old_err:
            stage("UDS variant / DID 0x0203 old probe", "rejected", nrc=f"0x{int(old_err.error_code):02x}")
            try:
                boot.write_data_by_identifier(0x203, b"\x01" + bytes(4))
                uds_variant = "new"
                stage("UDS variant / DID 0x0203", "accepted", variant="new", value="0100000000")
            except NegativeResponseError as new_err:
                stage("UDS variant / DID 0x0203 new probe", "rejected", nrc=f"0x{int(new_err.error_code):02x}")
                return 8
        if uds_variant is None:
            stage("UDS variant", "failed")
            return 8
        routine_magic = b"\x45\x00" if uds_variant == "old" else b"\x45\x01"
        report["uds_variant"] = uds_variant
        save()

        boot.write_data_by_identifier(0x201, bytes(16))
        boot.write_data_by_identifier(0x202, bytes(16))
        stage("DID 0x0201/0x0202", "accepted", value="zero16")

        req = b"\x01\x46\x01\x00" + struct.pack("!I", LOAD_ADDR) + struct.pack("!I", LOAD_SIZE)
        boot._uds_request(SERVICE_TYPE.REQUEST_DOWNLOAD, data=req)
        stage("RequestDownload", "accepted", data_hex=req.hex())
        for i in range(4):
            boot.transfer_data(i + 1, payload[i * 0x400:(i + 1) * 0x400])
            stage("TransferData", "accepted", block=i + 1)
        boot.request_transfer_exit()
        stage("RequestTransferExit", "accepted")

        verify = routine_magic + struct.pack("!I", LOAD_ADDR) + struct.pack("!I", LOAD_SIZE)
        try:
            boot.routine_control(ROUTINE_CONTROL_TYPE.START, 0x10F0, verify)
        except NegativeResponseError as e:
            stage("RoutineControl 0x10F0", "rejected", nrc=f"0x{int(e.error_code):02x}", data_hex=verify.hex())
            return 9
        stage("RoutineControl 0x10F0", "accepted", data_hex=verify.hex())

        # At this point the target itself has authenticated the exact 4 KiB Calvin package.
        trigger = b"\x31\x01\xff\x00" + routine_magic + struct.pack("!I", TRIGGER_ADDR) + struct.pack("!I", TRIGGER_SIZE)
        # Drop ordinary-CAN/UDS backlog immediately before the one-shot payload stream.
        # This cannot affect ECU state; it only clears Panda's host-facing RX ring.
        panda.can_clear(0xFFFF)
        time.sleep(0.01)
        isotp_send(panda, trigger, TX, bus=BUS)
        stage("RoutineControl 0xFF00 callback trigger", "sent", data_hex=trigger.hex())

        total = range_end - range_start
        words = total // 4
        image = bytearray(total)
        seen = bytearray(words)
        unique_words = 0
        duplicate_words = 0
        conflicts = 0
        raw_frames = 0
        spi_errors = 0
        consecutive_spi_errors = 0
        started = time.monotonic()
        last_progress = started
        last_print = started

        while True:
            now_mono = time.monotonic()
            if now_mono - started > MAX_SECONDS:
                stage("RAM stream", "timeout", seconds=round(now_mono - started, 3))
                break
            made_progress = False
            try:
                batch = panda.can_recv()
                consecutive_spi_errors = 0
            except PandaSpiException as e:
                spi_errors += 1
                consecutive_spi_errors += 1
                if spi_errors == 1 or (spi_errors % 25) == 0:
                    print(f"[SPI] recoverable {type(e).__name__} count={spi_errors}", flush=True)
                if consecutive_spi_errors >= 100:
                    stage("RAM stream SPI", "failed", errors=spi_errors, detail="100 consecutive SPI errors")
                    break
                continue
            for addr, data, bus in batch:
                # Filter before constructing/copying payload bytes. Normal vehicle traffic
                # is much larger than the one response stream we need.
                if bus != BUS or addr != RX or len(data) < 8:
                    continue
                data = bytes(data)
                raw_frames += 1
                if data == RESPONSE_PENDING:
                    continue
                word0 = struct.unpack("<I", data[:4])[0]
                if (word0 & 0xFF) != 0x07:
                    continue
                address = (range_start & 0xFF000000) | ((word0 >> 8) & 0xFFFFFF)
                if address < range_start or address + 4 > range_end or (address & 3):
                    continue
                idx = (address - range_start) // 4
                word = data[4:8]
                off = idx * 4
                if seen[idx]:
                    duplicate_words += 1
                    if image[off:off + 4] != word:
                        conflicts += 1
                        stage("RAM stream", "failed", detail="conflicting duplicate", address=f"0x{address:08x}")
                        raise RuntimeError(f"conflicting duplicate at 0x{address:08x}")
                else:
                    image[off:off + 4] = word
                    seen[idx] = 1
                    unique_words += 1
                    made_progress = True

            if made_progress:
                last_progress = time.monotonic()
            elif time.monotonic() - last_progress > IDLE_TIMEOUT:
                break
            else:
                time.sleep(0.001)
            if unique_words >= words:
                break
            if time.monotonic() - last_print > 5.0:
                pct = unique_words * 100.0 / words
                print(f"[STREAM] {unique_words}/{words} words ({pct:.2f}%)", flush=True)
                last_print = time.monotonic()

        elapsed = time.monotonic() - started
        coverage = bytes(seen)
        dump_path.write_bytes(bytes(image))
        coverage_path.write_bytes(coverage)
        complete = unique_words == words and conflicts == 0
        report["result"] = {
            "status": "complete" if complete else ("partial" if unique_words else "empty"),
            "dump_path": str(dump_path),
            "coverage_path": str(coverage_path),
            "dump_size": len(image),
            "profile": args.profile,
            "range_start": f"0x{range_start:08x}",
            "range_end": f"0x{range_end:08x}",
            "clobber_range": report["payload"]["clobber_range"],
            "expected_words": words,
            "unique_words": unique_words,
            "duplicate_words": duplicate_words,
            "conflicts": conflicts,
            "raw_rx_frames": raw_frames,
            "spi_errors": spi_errors,
            "elapsed_s": round(elapsed, 3),
            "coverage_percent": round(unique_words * 100.0 / words, 6),
            "sha256": sha256(bytes(image)) if complete else None,
        }
        stage("RAM stream", "complete" if complete else "partial", unique_words=unique_words,
              expected_words=words, elapsed_s=round(elapsed, 3))

        # Best-effort post-payload liveness only; do not reset or send another key.
        try:
            panda.set_safety_mode(CarParams.SafetyModel.elm327, ELM327_PARAM)
            post = uds_client(panda, route, timeout=0.5, response_pending_timeout=1.0)
            post_f181 = bytes(post.read_data_by_identifier(0xF181))
            stage("post-RAM-dump application identity", "observed", observed_hex=post_f181.hex())
        except Exception as e:
            stage("post-RAM-dump application identity", "unavailable", detail=type(e).__name__)

        report["finished_at"] = utc_now()
        save()
        print(json.dumps(report["result"], indent=2, sort_keys=True), flush=True)
        return 0 if complete else 10

    except NegativeResponseError as e:
        stage("unhandled UDS negative response", "failed", nrc=f"0x{int(e.error_code):02x}")
        return 20
    except Exception as e:
        stage("exception", "failed", detail=f"{type(e).__name__}: {e}")
        return 21
    finally:
        try:
            panda.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
