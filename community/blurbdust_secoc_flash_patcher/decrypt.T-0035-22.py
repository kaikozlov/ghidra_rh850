#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import cmac


def deobfuscate(raw32):
    shifted = bytes((b - i) & 0xff for i, b in enumerate(raw32))
    hex_chars = shifted.decode("ascii")
    return bytes.fromhex(hex_chars), hex_chars


def explain_obfuscation(label, raw32):
    _, hex_chars = deobfuscate(raw32)
    print(f"  {label}:")
    print(f"    raw bytes   : {raw32.hex()}")
    print(f"    per-byte op : out[i] = raw[i] - i  (mod 256)")
    preview = " -> ".join(
        f"0x{raw32[i]:02x}-{i:02}=0x{(raw32[i]-i)&0xff:02x}='{hex_chars[i]}'" for i in range(4)
    )
    print(f"    first 4     : {preview}")
    print(f"    hex string  : {hex_chars}")


def load_cuw(path):
    data = Path(path).read_bytes()
    print(f"[read] {path}  size={len(data):,} bytes")
    return data


def parse_ini(data):
    text_end = data.find(b"\x02\x00")
    ini_text = data[:text_end].decode("latin-1", errors="replace")
    sections = {}
    current = None
    for line in ini_text.splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]"):
            current = line[1:-1]
            sections[current] = {}
        elif "=" in line and current is not None:
            key, value = line.split("=", 1)
            sections[current][key.strip()] = value.strip()
    print(f"[ini ] end=0x{text_end:x}  sections={len(sections)}: {', '.join(sections.keys())}")
    return sections


def parse_srec_streams(data):
    lines = [m.group(0) for m in re.finditer(rb"S[03789][0-9A-Fa-f]+(?=\r\n)", data)]
    streams = []
    current = []
    for line in lines:
        kind = line[1:2]
        if kind == b"0":
            if current:
                streams.append(current)
            current = [line]
        else:
            current.append(line)
            if kind == b"7":
                streams.append(current)
                current = []
    if current:
        streams.append(current)
    print(f"[srec] {len(lines):,} lines across {len(streams)} stream(s)")
    return streams


def stream_to_regions(stream):
    records = {}
    for line in stream:
        if line[1:2] != b"3":
            continue
        count = int(line[2:4], 16)
        addr = int(line[4:12], 16)
        payload = bytes.fromhex(line[12:12 + 2 * (count - 5)].decode())
        records[addr] = payload

    regions = []
    for addr in sorted(records):
        chunk = records[addr]
        if regions and addr == regions[-1][0] + len(regions[-1][1]):
            regions[-1] = (regions[-1][0], regions[-1][1] + chunk)
        else:
            regions.append((addr, chunk))
    return regions


def derive_key(bl_key, did_201):
    return Cipher(algorithms.AES(bl_key), modes.ECB()).encryptor().update(did_201)


def aes_cbc_decrypt(derived_key, iv, ciphertext):
    return Cipher(algorithms.AES(derived_key), modes.CBC(iv)).decryptor().update(ciphertext)


def cmac_verify(derived_key, iv, plaintext):
    mac = cmac.CMAC(algorithms.AES(derived_key))
    mac.update(iv + plaintext[:-16])
    return mac.finalize() == plaintext[-16:]


def process_section(ini, sec_name, stream, bl_key, out_dir):
    section = ini[sec_name]
    idx = sec_name[3:]
    cid = section.get("NewCID", sec_name)

    print(f"\n[sect] {sec_name}  CID={cid}")
    raw_seed = bytes.fromhex(section["SeedKey"])
    raw_nonce = bytes.fromhex(section["Nonce"])
    explain_obfuscation("SeedKey -> DID_201", raw_seed)
    explain_obfuscation("Nonce   -> DID_202", raw_nonce)

    did_201, _ = deobfuscate(raw_seed)
    did_202, _ = deobfuscate(raw_nonce)
    derived = derive_key(bl_key, did_201)

    print(f"  DID_201     = {did_201.hex()}")
    print(f"  DID_202     = {did_202.hex()}")
    print(f"  derived_key = AES_ECB(BL_KEY, DID_201)")
    print(f"              = {derived.hex()}")

    body_addr = int(ini[f"CPUImage{idx}"]["01_StartAddress"], 16)
    erase_addr = int(ini[f"EraseRoutine{idx}"]["01_StartAddress"], 16)

    failures = 0
    for addr, ciphertext in stream_to_regions(stream):
        if addr == body_addr:
            tag = "body"
        elif addr == erase_addr:
            tag = "erase"
        else:
            tag = f"unknown_{addr:08x}"

        if len(ciphertext) % 16:
            print(f"  [skip] {tag}@0x{addr:08x}: ct_len={len(ciphertext)} not multiple of 16")
            failures += 1
            continue

        plaintext = aes_cbc_decrypt(derived, did_202, ciphertext)
        ok = cmac_verify(derived, did_202, plaintext)
        out_path = out_dir / f"{cid}_{tag}.pt.bin"
        out_path.write_bytes(plaintext)

        status = "OK" if ok else "FAIL"
        print(f"  [write] {tag}@0x{addr:08x}  {len(ciphertext):>7} B  -> {out_path.name}  CMAC={status}")
        if not ok:
            failures += 1

    return failures


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bl-key", required=True)
    parser.add_argument("--cuw", required=True)
    parser.add_argument("--out")
    args = parser.parse_args()

    cuw_path = Path(args.cuw)
    out_path = Path(args.out) if args.out else cuw_path.with_suffix("").with_name(cuw_path.stem + "_pt")

    bl_key = bytes.fromhex(args.bl_key)
    if len(bl_key) != 16:
        sys.exit("--bl-key must be 32 hex chars (16 bytes)")
    print(f"[key ] BL_KEY = {bl_key.hex()}")

    data = load_cuw(cuw_path)
    ini = parse_ini(data)
    streams = parse_srec_streams(data)

    sections = sorted(
        (s for s in ini if re.fullmatch(r"CPU\d+", s)),
        key=lambda s: int(s[3:]),
    )
    if len(sections) != len(streams):
        sys.exit(f"section count {len(sections)} != stream count {len(streams)}")

    out_path.mkdir(exist_ok=True)
    print(f"[out ] writing plaintexts to {out_path}")

    failures = 0
    for sec_name, stream in zip(sections, streams):
        failures += process_section(ini, sec_name, stream, bl_key, out_path)

    print()
    print("Decrypted?" if failures == 0 else f"{failures} FAILURES")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    main()
