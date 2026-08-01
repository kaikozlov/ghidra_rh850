#!/usr/bin/env python3
"""SecOC flash patcher — disables MAC verification via egg-hunter shellcode."""

import argparse
import struct
import time
from subprocess import check_output, CalledProcessError

from Crypto.Cipher import AES

from panda import Panda
from opendbc.car.uds import UdsClient, ACCESS_TYPE, SESSION_TYPE, DATA_IDENTIFIER_TYPE, SERVICE_TYPE, ROUTINE_CONTROL_TYPE, NegativeResponseError
from opendbc.car.structs import CarParams
from opendbc.car.isotp import isotp_send

ADDR = 0x7a1
BUS = 0

SEED_KEY_SECRET = b'\xf0\x5f\x36\xb7\xd7\x8c\x03\xe2\x4a\xb4\xfa\xef\x2a\x57\xd0\x44'
DID_201_KEY = b'\x00' * 16
DID_202_IV = b'\x00' * 16

PATCH_VERSIONS = {
    b'\x048965F3401200\x00\x00\x00\x008A3113402000\x00\x00\x00\x008965F3402200\x00\x00\x00\x008A3213402000\x00\x00\x00\x00': {
        'name': '8965F3401200 dual-CPU',
        'num_cpus': 2,
        'new_uds': True,
    },
    b'\x028965F4207000\x00\x00\x00\x008A3114212000\x00\x00\x00\x00': {
        'name': '8965F4207000 single-CPU',
        'num_cpus': 1,
        'new_uds': None,
    },
    b'\x028965F4201000\x00\x00\x00\x008A3114201000\x00\x00\x00\x00': {
        'name': '8965F4201000 single-CPU',
        'num_cpus': 1,
        'new_uds': None,
    },
}

KEY_EXTRACT_VERSIONS = {
    b'\x018965B4209000\x00\x00\x00\x00': '8965B4209000',
    b'\x018965B4233100\x00\x00\x00\x00': '8965B4233100',
    b'\x018965B4509100\x00\x00\x00\x00': '8965B4509100',
}

STAGE_NAMES = {
    0x01: "Egg hunt",
    0x02: "Read-modify block",
    0x03: "Erase + reprogram",
    0x04: "CRC fixup",
    0x05: "Complete",
    0xFF: "Done",
}


def decode_frame(data):
    if len(data) < 8:
        return None

    w0 = struct.unpack("<I", data[:4])[0]
    w1 = struct.unpack("<I", data[4:])[0]

    if (w0 & 0xFFFF0000) == 0xDEAD0000 and w1 == 0xCAFEBABE:
        stage = w0 & 0xFF
        name = STAGE_NAMES.get(stage, f"stage 0x{stage:02x}")
        print(f"\n{'='*50}")
        print(f"  {name}")
        print(f"{'='*50}")
        return stage

    tag = w0 & 0xFF
    addr = (w0 >> 8) & 0xFFFFFF

    if tag == 0xB0:
        what = "BL stubs valid" if addr == 0 else "BL stub probe"
        print(f"  [{what}] = 0x{w1:08x}")
    elif tag == 0xC1:
        if addr == 0x00FF:
            print(f"  [EGG] total matches: {w1}")
        else:
            print(f"  [EGG] match #{addr} at 0x{w1:08x}")
    elif tag == 0xC2:
        labels = {0: "block_base", 4: "patch_offset", 0x10: "orig", 0x20: "patched"}
        print(f"  [BLOCK] {labels.get(addr, f'0x{addr:x}')} = 0x{w1:08x}")
    elif tag == 0xC3:
        if addr == 0xF0:
            print(f"  [VERIFY] {'PASS' if w1 == 0x600D else 'FAIL'}")
        else:
            labels = {0x10: "flash_err", 0x20: "readback"}
            print(f"  [FLASH] {labels.get(addr, f'0x{addr:x}')} = 0x{w1:08x}")
    elif tag == 0xC4:
        if addr == 0xF0:
            print(f"  [CRC] {'PASS' if w1 == 0x600D else 'FAIL'}")
        else:
            labels = {0: "crc_pre", 4: "adj_new", 8: "adj_orig", 0x10: "flash_err", 0x20: "crc_verify"}
            print(f"  [CRC] {labels.get(addr, f'0x{addr:x}')} = 0x{w1:08x}")
    elif tag == 0xC5:
        labels = {0: "egg_addr", 4: "match_count"}
        print(f"  [DONE] {labels.get(addr, f'0x{addr:x}')} = 0x{w1:08x}")
    elif tag == 0xEE:
        print(f"  [ERROR] stage=0x{addr:04x} code=0x{w1:08x}")
    else:
        print(f"  [0x{tag:02x}] 0x{addr:04x} = 0x{w1:08x}")

    return None


def detect_cpu_count(app_version):
    if len(app_version) > 0 and app_version[0] >= 4:
        return 2
    return 1


def security_access(uds_client):
    seed_payload = b"\x00" * 16
    seed = uds_client.security_access(ACCESS_TYPE.REQUEST_SEED, data_record=seed_payload)
    key = AES.new(SEED_KEY_SECRET, AES.MODE_ECB).decrypt(seed_payload)
    key = AES.new(key, AES.MODE_ECB).encrypt(seed)
    uds_client.security_access(ACCESS_TYPE.SEND_KEY, key)
    return seed


def enter_programming(uds_client):
    uds_client.diagnostic_session_control(SESSION_TYPE.DEFAULT)
    uds_client.diagnostic_session_control(SESSION_TYPE.EXTENDED_DIAGNOSTIC)
    uds_client.diagnostic_session_control(SESSION_TYPE.PROGRAMMING)


def probe_uds_variant(uds_client):
    """Returns True for new UDS, False for old."""
    try:
        enter_programming(uds_client)
        security_access(uds_client)
        uds_client.write_data_by_identifier(0x203, b"\x00" * 5)
        return False
    except NegativeResponseError:
        return True
    except Exception:
        return True
    finally:
        try:
            uds_client.diagnostic_session_control(SESSION_TYPE.DEFAULT)
        except Exception:
            pass


def run_exploit(panda, uds_client, cpu_index, num_cpus, new_uds):
    offset_addr = b"\x01\x00\x00\x00\x00" if cpu_index == 0 else b"\x00\x00\x00\x00\x00"
    mem_id = b"\x01" if cpu_index == 0 else b"\x00"
    routine_magic = b"\x45\x01" if new_uds else b"\x45\x00"
    cpu_name = f"CPU{cpu_index + 1}" if num_cpus > 1 else "CPU"

    print(f"\n{'#'*50}")
    print(f"  Patching {cpu_name}")
    print(f"{'#'*50}")

    enter_programming(uds_client)
    if not new_uds:
        enter_programming(uds_client)

    seed = security_access(uds_client)
    print(f"  SA seed: {seed.hex()}")

    uds_client.write_data_by_identifier(0x203, offset_addr)
    uds_client.write_data_by_identifier(0x201, DID_201_KEY)
    uds_client.write_data_by_identifier(0x202, DID_202_IV)

    data = b"\x01\x46" + mem_id + b"\x00"
    data += struct.pack('!I', 0xfebf0000)
    data += struct.pack('!I', 0x1000)
    uds_client._uds_request(SERVICE_TYPE.REQUEST_DOWNLOAD, data=data)

    payload = open("flash_payload.bin", "rb").read()
    assert len(payload) == 0x1000
    chunk_size = 0x400
    for i in range(len(payload) // chunk_size):
        uds_client.transfer_data(i + 1, payload[i * chunk_size:(i + 1) * chunk_size])
    uds_client.request_transfer_exit()
    print(f"  Payload uploaded ({len(payload)} bytes)")

    data = routine_magic + struct.pack('!I', 0xfebf0000) + struct.pack('!I', 0x1000)
    uds_client.routine_control(ROUTINE_CONTROL_TYPE.START, 0x10f0, data)
    print(f"  Payload verified")

    data = routine_magic + struct.pack('!I', 0xe0000) + struct.pack('!I', 0x8000)
    isotp_send(panda, b"\x31\x01\xff\x00" + data, ADDR, bus=BUS)
    print(f"  Triggered! Listening...")

    done = False
    success = False
    timeout = time.time() + 60

    while not done and time.time() < timeout:
        for can_addr, *_, can_data, bus in panda.can_recv():
            if bus != BUS or can_addr != ADDR + 8:
                continue
            if can_data == b"\x03\x7f\x31\x78\x00\x00\x00\x00":
                continue
            if len(can_data) < 8:
                continue
            stage = decode_frame(can_data)
            if stage == 0xFF:
                done = True
                success = True
                break
            elif stage == 0x05:
                success = True

    return success


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="SecOC flash patcher")
    ap.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompts")
    args = ap.parse_args()

    try:
        check_output(["pidof", "boardd"])
        print("boardd is running — kill openpilot first")
        exit(1)
    except CalledProcessError as e:
        if e.returncode != 1:
            raise e
    except FileNotFoundError:
        pass

    panda = Panda()
    panda.set_safety_mode(CarParams.SafetyModel.elm327)
    uds_client = UdsClient(panda, ADDR, ADDR + 8, BUS, timeout=0.1, response_pending_timeout=1.0)

    print("Reading version...")
    try:
        app_version = uds_client.read_data_by_identifier(DATA_IDENTIFIER_TYPE.APPLICATION_SOFTWARE_IDENTIFICATION)
        print(f"  {app_version.hex()}")
    except NegativeResponseError:
        print("Can't read version. Cycle ignition.")
        exit(1)

    if app_version in KEY_EXTRACT_VERSIONS:
        print(f"\nOlder ECU ({KEY_EXTRACT_VERSIONS[app_version]}) — use extract_keys.py instead.")
        exit(1)

    if app_version in PATCH_VERSIONS:
        config = PATCH_VERSIONS[app_version]
        print(f"  Matched: {config['name']}")
    else:
        print(f"\nUnknown version — egg-hunter may still work.")
        if not args.yes:
            resp = input("  Continue? [y/N] ")
            if resp.lower() != 'y':
                exit(1)
        config = {
            'name': 'Unknown',
            'num_cpus': detect_cpu_count(app_version),
            'new_uds': None,
        }

    num_cpus = config['num_cpus']
    new_uds = config['new_uds']

    if new_uds is None:
        print("  Probing UDS variant...")
        new_uds = probe_uds_variant(uds_client)
        uds_client = UdsClient(panda, ADDR, ADDR + 8, BUS, timeout=0.1, response_pending_timeout=1.0)
        print(f"  -> {'new' if new_uds else 'old'} UDS")

    print(f"  CPUs: {num_cpus}, UDS: {'new' if new_uds else 'old'}")

    print(f"\n{'='*50}")
    print(f"  Patching {num_cpus} CPU(s)")
    print(f"  SecOC verification will be permanently disabled.")
    print(f"  Reversible via dealer reflash.")
    print(f"{'='*50}")

    if not args.yes:
        resp = input("\nType 'PATCH' to confirm: ")
        if resp != 'PATCH':
            print("Aborted.")
            exit(1)

    all_success = True
    for cpu in range(num_cpus):
        ok = run_exploit(panda, uds_client, cpu, num_cpus, new_uds)
        if not ok:
            print(f"\nCPU{cpu + 1} FAILED")
            all_success = False
            break
        if cpu < num_cpus - 1:
            print(f"\nWaiting for ECU reset...")
            time.sleep(5)
            uds_client = UdsClient(panda, ADDR, ADDR + 8, BUS, timeout=0.1, response_pending_timeout=1.0)

    if all_success:
        print(f"\n  All {num_cpus} CPU(s) patched. ECU will reboot via watchdog.")
    else:
        print(f"\n  Patch incomplete. May need dealer reflash.")
