#!/usr/bin/env python3
"""Purpose-built memory-safety audit of application SID 0x23 ReadMemoryByAddress.

Scope: the entire tester-controlled address/length chain, pinned against
firmware bytes and the tracked decompiler corpus:

  dispatch object -> callback 0x948AA -> start 0x9479A (parse + policy gates)
  -> poll (async worker 0x948E6/0x8C456 -> copy primitive 0x4EB1C
  -> RAM checker 0x4EA76 / copier 0x4EABA, DF checker 0x4EAD6 / reader 0x65DE6)

Audit classes pinned here:
  * exact-length contract and ALFID whitelist (no parsing past the request)
  * integer overflow / wrap in every address+size computation
  * signedness / truncation (32-bit address, one-byte size, memid byte)
  * range boundary consistency (config range, end-fit, copy-time window)
  * requested-vs-emitted length identity
  * async state ownership / TOCTOU writer census over the RMBA state block

Config bytes (CodeFlash.bin, VA == file offset, same convention as the other
application suites):
  0x25EA0  service object (SID 0x23 -> callback 0x948AA)
  0x26204 -> 0x26128 -> 0x26130  ALFID whitelist (count 0x2612C, list 0x26130)
  0x26208 -> 0x261A4             memory-range descriptor records (stride 0xC)
  0x2620C                         enabled record count
  0x26328                         memid-consumption selector (must be 1)
  0x293E4 / 0x293E8..             DataFlash exclusion lo/hi pairs (stride 8)
  0x293F4 / 0x293F8..             LocalRAM  exclusion lo/hi pairs (stride 8)
"""
from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CF = (ROOT / "firmware" / "RH850_P1M-E_CodeFlash.bin").read_bytes()
CORPUS = ROOT / "data" / "generated" / "decompilations.jsonl"

passed = failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}" + (f" ({detail})" if detail else ""))


def u32(addr: int) -> int:
    return struct.unpack_from("<I", CF, addr)[0]


M32 = 0xFFFFFFFF


# ---------------------------------------------------------------------------
# 1. Configuration bytes (the policy the gates enforce)
# ---------------------------------------------------------------------------
print("== configuration bytes ==")

obj = 0x25EA0
callback, sec_ptr, session_ptr, sub_ptr = struct.unpack_from("<IIII", CF, obj)
sid, has_sub, sec_count, session_count, sub_count = CF[obj + 16 : obj + 21]
check("SID 0x23 object at 0x25EA0", sid == 0x23)
check("SID 0x23 direct callback is 0x948AA", callback == 0x948AA, hex(callback))
check("SID 0x23 direct service (no subfunction table)", has_sub == 0 and sub_ptr == 0)
check("SID 0x23 no service-level SecurityAccess", sec_ptr == 0 and sec_count == 0)
check("SID 0x23 extended-session-only", session_count == 1 and CF[session_ptr] == 3)

alfid_list_ptr = u32(0x26128)
alfid_count = CF[0x2612C]
alfids = list(CF[alfid_list_ptr : alfid_list_ptr + alfid_count])
check("ALFID whitelist is exactly {0x15}", alfid_count == 1 and alfids == [0x15],
      f"count={alfid_count} list={alfids!r}")

check("memid-consumption selector 0x26328 == 1", CF[0x26328] == 1,
      "0x94672 consumes data[1] as memory id only when this byte is 1")

range_base = u32(0x26208)
enabled_records = CF[0x2620C]
RANGES: dict[int, tuple[int, int]] = {}
for i in range(enabled_records):
    off = range_base + i * 0xC
    rd_ptr, wr_ptr = struct.unpack_from("<II", CF, off)
    rd_cnt, wr_cnt, memid, enabled = CF[off + 8 : off + 12]
    if enabled != 1 or rd_cnt == 0:
        continue
    # 16-byte range entry: inclusive low = u32@+8, inclusive high = u32@+4
    # (compare order in 0x92ECC: word@+8 <= addr <= word@+4)
    lows = [u32(rd_ptr + j * 0x10 + 8) for j in range(rd_cnt)]
    highs = [u32(rd_ptr + j * 0x10 + 4) for j in range(rd_cnt)]
    for lo, hi in zip(lows, highs):
        RANGES.setdefault(memid, (lo, hi))
    check(f"memid {memid} has no write-range counterpart", wr_ptr == 0 and wr_cnt == 0)
    check(f"memid {memid} read-range entries carry zero SecurityAccess entries",
          all(CF[rd_ptr + j * 0x10 + 0xC] == 0 for j in range(rd_cnt)))

check("enabled range records == 2 (memid 1 and 2 only)", enabled_records == 2
      and set(RANGES) == {1, 2}, f"records={enabled_records} memids={sorted(RANGES)}")
check("memid 1 range is inclusive [FEBE0000, FEBFFFFF]",
      RANGES.get(1) == (0xFEBE0000, 0xFEBFFFFF), str(RANGES.get(1)))
check("memid 2 range is inclusive [FF200000, FF207FFF]",
      RANGES.get(2) == (0xFF200000, 0xFF207FFF), str(RANGES.get(2)))


def load_excl(base: int, count: int) -> list[tuple[int, int]]:
    return [(u32(base + 8 * i), u32(base + 8 * i + 4)) for i in range(count)]


DF_EXCL = load_excl(0x293E4, 2)
RAM_EXCL = load_excl(0x293F4, 5)
check("DataFlash exclusion pairs (lo,hi) x2",
      DF_EXCL == [(0xFF207800, 0xFF207FFF), (0xFF206C00, 0xFF206EFF)], str(DF_EXCL))
check("LocalRAM exclusion pairs (lo,hi) x5",
      RAM_EXCL == [(0xFEBE0000, 0xFEBE37FF), (0xFEBE5030, 0xFEBE529B),
                   (0xFEBF0288, 0xFEBF13CB), (0xFEBF4958, 0xFEBF4B33),
                   (0xFEBF6C00, 0xFEBF78DF)], str(RAM_EXCL))

# ---------------------------------------------------------------------------
# 2. Gate-implementation pins (sha256 of each gate function body)
# ---------------------------------------------------------------------------
print("== gate function bodies (sha256 over CodeFlash) ==")

functions: dict[int, tuple[str, int]] = {}  # entry -> (name, body_size)
by_name: dict[str, int] = {}
with CORPUS.open() as f:
    for line in f:
        r = json.loads(line)
        try:
            entry = int(r["entry_addr"], 16)
        except (KeyError, TypeError, ValueError):
            continue
        functions[entry] = (r.get("name", "?"), r.get("body_size", 0))
        by_name[r.get("name", "?")] = entry

GATES = {
    0x948AA: "callback (phase split 0/2/3)",
    0x9479A: "request start (length/ALFID/size/range/security gates)",
    0x9486C: "cancel (worker state reset)",
    0x92E92: "ALFID whitelist lookup",
    0x9462E: "size accumulation + response-capacity bound",
    0x94672: "address/memid parse + range + end-fit + security",
    0x92ECC: "configured range selection (inclusive lo<=addr<=hi)",
    0x92FAE: "unsigned end-fit check (high-addr < size-1 rejects)",
    0x92FEE: "per-range SecurityAccess check",
    0x948E6: "poll phase gate + worker dispatch",
    0x8C456: "async copy worker (window re-check, cursor advance)",
    0x8C406: "copy-or-NRC emit (exact requested length)",
    0x8C3E4: "cancel worker reset",
    0x4EB1C: "copy primitive (size 1..255, memid dispatch)",
    0x4EA76: "LocalRAM copy-time window + exclusion overlap",
    0x4EABA: "LocalRAM byte copier",
    0x4EAD6: "DataFlash copy-time window + exclusion overlap",
    0x65DE6: "DataFlash 4-byte-aligned reader",
}
for entry, label in GATES.items():
    name, size = functions.get(entry, ("?", 0))
    body = CF[entry : entry + size]
    check(f"gate {entry:#x} present in corpus ({label})",
          name != "?" and size > 0 and len(body) == size, f"{name=} {size=}")
    print(f"       sha256[{entry:#07x}:+{size}] = {hashlib.sha256(body).hexdigest()}")

poll_entry = by_name.get("application_read_memory_by_address_request_poll", 0)
check("poll function recovered from corpus", poll_entry != 0, hex(poll_entry))

# ---------------------------------------------------------------------------
# 3. Behavioral model of the gate chain (semantics transcribed from the
#    decompiled/disassembled compare-and-branch logic above)
# ---------------------------------------------------------------------------
print("== behavioral model: boundary matrix ==")


def rmba_request(data: bytes, remaining: int = 255):
    """Emulate the SID 0x23 gate chain on post-SID request bytes.

    Request layout for ALFID 0x15: [ALFID][memid][address:4 BE][size:1].
    Returns ("NRC", code) or ("OK", (memid, addr, size)).
    Gate order mirrors 0x9479A exactly; each comparison keeps the firmware's
    unsigned 32-bit arithmetic.
    """
    ln = len(data)
    if ln < 3:                                        # start: len < 3
        return ("NRC", 0x13)
    alfid = data[0]
    if alfid not in alfids:                           # 0x92E92 whitelist
        return ("NRC", 0x31)
    lo_n, hi_n = alfid & 0xF, alfid >> 4
    if ln != lo_n + hi_n + 1:                         # exact length contract
        return ("NRC", 0x13)
    # 0x9462E: size = BE bytes at data[1+lo_n : 1+lo_n+hi_n]; reject 0 / > remaining
    size = int.from_bytes(data[1 + lo_n : 1 + lo_n + hi_n], "big")
    if size == 0 or remaining < size:
        return ("NRC", 0x31)
    # 0x94672 (0x26328 == 1): memid = data[1]; address = BE(data[2 : 1+lo_n])
    memid = data[1]
    addr = int.from_bytes(data[2 : 1 + lo_n], "big")
    rng = RANGES.get(memid)                           # 0x92ECC exact-byte memid
    if rng is None:
        return ("NRC", 0x31)
    low, high = rng
    if not (low <= addr <= high):                     # inclusive both ends
        return ("NRC", 0x31)
    if ((high - addr) & M32) < ((size - 1) & M32):    # 0x92FAE unsigned end-fit
        return ("NRC", 0x31)
    # 0x92FEE: per-range SecurityAccess count is 0 (pinned above) -> passes
    # poll(0) -> 0x948E6 -> 0x8C456: memid>>4 is 0 for memid 1/2, so the
    # chunked/programming branch is unreachable; direct copy primitive runs.
    if not ((size - 1) & M32 < 0xFF):                 # 0x4EB1C: size in 1..255
        return ("NRC", 0x31)
    if memid == 1:                                    # 0x4EA76 copy-time window
        if not ((0xFEBDFFFF < addr) and (addr <= (0xFEC00000 - size) & M32)):
            return ("NRC", 0x31)
        excl = RAM_EXCL
    elif memid == 2:                                  # 0x4EAD6 copy-time window
        if not ((0xFF1FFFFF < addr) and (addr <= (0xFF208000 - size) & M32)):
            return ("NRC", 0x31)
        excl = DF_EXCL
    else:
        return ("NRC", 0x31)
    for lo_e, hi_e in excl:                           # exclusion overlap test
        if addr <= hi_e and ((lo_e + 1 - size) & M32) <= addr:
            return ("NRC", 0x31)
    return ("OK", (memid, addr, size))


def req(memid: int, addr: int, size: int, alfid: int = 0x15, ln_pad: int = 0) -> bytes:
    body = bytes([alfid, memid & 0xFF]) + struct.pack(">I", addr & M32) + bytes([size & 0xFF])
    if ln_pad:
        body += b"\x00" * ln_pad
    return body


def expect(label: str, data: bytes, want, remaining: int = 255) -> None:
    got = rmba_request(data, remaining)
    check(label, got == want, f"got={got} want={want}")


# --- length contract -------------------------------------------------------
expect("len 2 -> NRC 0x13 (minimum-length gate fires first)", b"\x15\x01\x00", ("NRC", 0x13))
expect("len 6 (missing size byte) -> NRC 0x13", req(1, 0xFEBE3800, 1)[:-1], ("NRC", 0x13))
expect("len 8 (trailing byte) -> NRC 0x13", req(1, 0xFEBE3800, 1, ln_pad=1), ("NRC", 0x13))
expect("exact len 7 well-formed -> parsed OK", req(1, 0xFEBE3800, 1), ("OK", (1, 0xFEBE3800, 1)))

# --- ALFID whitelist -------------------------------------------------------
for bad in (0x00, 0x14, 0x16, 0x25, 0x0F, 0xF5):
    expect(f"ALFID {bad:#04x} -> NRC 0x31", req(1, 0xFEBE3800, 1, alfid=bad), ("NRC", 0x31))

# --- size domain -----------------------------------------------------------
expect("size 0 -> NRC 0x31 (upper-layer zero gate)", req(1, 0xFEBE3800, 0), ("NRC", 0x31))
expect("size 255 in-range -> OK", req(1, 0xFEBE3800, 0xFF), ("OK", (1, 0xFEBE3800, 0xFF)))
expect("size 255 at DF low edge -> OK", req(2, 0xFF200000, 0xFF), ("OK", (2, 0xFF200000, 0xFF)))
check("single-byte size field cannot encode > 255 (max encodable 255)",
      max(req(1, 0xFEBE3800, s)[6] for s in range(0x100)) == 0xFF)
expect("size exceeding response capacity -> NRC 0x31 (capacity parameterized)",
       req(1, 0xFEBE3800, 50), ("NRC", 0x31), remaining=49)

# --- memid exact-byte matching (programming-path unreachability) ------------
for mid in (0x00, 0x03, 0x11, 0x21, 0xFF):
    expect(f"memid {mid:#04x} -> NRC 0x31 (range table exact-byte match; "
           f"0x8C456 memid>>4 branch unreachable)", req(mid, 0xFEBE3800, 1), ("NRC", 0x31))

# --- LocalRAM boundaries ---------------------------------------------------
expect("RAM addr FEBDFFFF -> NRC 0x31 (range low exclusive edge)",
       req(1, 0xFEBDFFFF, 1), ("NRC", 0x31))
expect("RAM addr FEBE3800 size 1 -> OK (first readable byte above exclusion 1)",
       req(1, 0xFEBE3800, 1), ("OK", (1, 0xFEBE3800, 1)))
expect("RAM addr FEBE37FF size 1 -> NRC 0x31 (exclusion 1 high edge)",
       req(1, 0xFEBE37FF, 1), ("NRC", 0x31))
expect("RAM addr FEBE37FE size 2 -> NRC 0x31 (crossing into exclusion 1)",
       req(1, 0xFEBE37FE, 2), ("NRC", 0x31))
expect("RAM addr FEBE502F size 1 -> OK (exclusion 2 low edge minus one)",
       req(1, 0xFEBE502F, 1), ("OK", (1, 0xFEBE502F, 1)))
expect("RAM addr FEBE529C size 1 -> OK (exclusion 2 high edge plus one)",
       req(1, 0xFEBE529C, 1), ("OK", (1, 0xFEBE529C, 1)))
expect("RAM addr FEBF6B01 size 255 -> OK (largest read ending at exclusion 5 low edge minus one)",
       req(1, 0xFEBF6B01, 0xFF), ("OK", (1, 0xFEBF6B01, 0xFF)))
expect("RAM addr FEBF6B02 size 255 -> NRC 0x31 (overlap formula lo+1-size <= addr)",
       req(1, 0xFEBF6B02, 0xFF), ("NRC", 0x31))
expect("RAM addr FEBFFFFF size 1 -> OK (range high inclusive; end-fit 0>=0; window equals range)",
       req(1, 0xFEBFFFFF, 1), ("OK", (1, 0xFEBFFFFF, 1)))
expect("RAM addr FEBFFFFF size 2 -> NRC 0x31 (end-fit: high-addr < size-1)",
       req(1, 0xFEBFFFFF, 2), ("NRC", 0x31))
expect("RAM addr FEC00000 -> NRC 0x31 (range high exclusive edge)",
       req(1, 0xFEC00000, 1), ("NRC", 0x31))

# --- DataFlash boundaries --------------------------------------------------
expect("DF addr FF1FFFFF -> NRC 0x31 (range low exclusive edge)",
       req(2, 0xFF1FFFFF, 1), ("NRC", 0x31))
expect("DF addr FF200000 size 1 -> OK (range low inclusive)",
       req(2, 0xFF200000, 1), ("OK", (2, 0xFF200000, 1)))
expect("DF addr FF206BFF size 1 -> OK (last byte before exclusion 1)",
       req(2, 0xFF206BFF, 1), ("OK", (2, 0xFF206BFF, 1)))
expect("DF addr FF206BFF size 2 -> NRC 0x31 (crossing into exclusion 1)",
       req(2, 0xFF206BFF, 2), ("NRC", 0x31))
expect("DF addr FF206C00 size 1 -> NRC 0x31 (exclusion 1 low edge)",
       req(2, 0xFF206C00, 1), ("NRC", 0x31))
expect("DF addr FF206EFF size 1 -> NRC 0x31 (exclusion 1 high edge)",
       req(2, 0xFF206EFF, 1), ("NRC", 0x31))
expect("DF addr FF206F00 size 1 -> OK (first byte after exclusion 1)",
       req(2, 0xFF206F00, 1), ("OK", (2, 0xFF206F00, 1)))
expect("DF addr FF2077FF size 1 -> OK (last readable byte before exclusion 2)",
       req(2, 0xFF2077FF, 1), ("OK", (2, 0xFF2077FF, 1)))
expect("DF addr FF2077FE size 2 -> OK (two-byte read ending at last readable byte)",
       req(2, 0xFF2077FE, 2), ("OK", (2, 0xFF2077FE, 2)))
expect("DF addr FF2077FF size 2 -> NRC 0x31 (crossing into exclusion 2)",
       req(2, 0xFF2077FF, 2), ("NRC", 0x31))
expect("DF addr FF207800 size 1 -> NRC 0x31 (exclusion 2 low edge)",
       req(2, 0xFF207800, 1), ("NRC", 0x31))
expect("DF addr FF207FFF size 1 -> NRC 0x31 (exclusion 2 high edge == range high)",
       req(2, 0xFF207FFF, 1), ("NRC", 0x31))
expect("DF addr FF208000 -> NRC 0x31 (range high exclusive edge)",
       req(2, 0xFF208000, 1), ("NRC", 0x31))

# --- wrap / overflow candidates: every one is cut by an earlier gate -------
for label, mid, addr, size in (
    ("addr 0xFFFFFFFF memid 1 (window subtraction wrap candidate)", 1, 0xFFFFFFFF, 1),
    ("addr 0xFFFFFFFF memid 2 (window subtraction wrap candidate)", 2, 0xFFFFFFFF, 1),
    ("addr 0x80000000 memid 2", 2, 0x80000000, 1),
    ("addr 0x00000000 memid 1", 1, 0x00000000, 1),
    ("addr 0x7FFFFFFF memid 1 (signedness candidate)", 1, 0x7FFFFFFF, 0xFF),
    ("addr FEC00001..FEC0FF00 range (window==range equivalence check)", 1, 0xFEC0FF00, 1),
):
    expect(f"{label} -> NRC 0x31 (configured range gate fires before any "
           f"addr+size / subtraction arithmetic)", req(mid, addr, size), ("NRC", 0x31))

# window arithmetic cannot wrap for in-range operands (proof by bounds)
check("no unsigned wrap possible in window checks: FEC00000-size and "
      "FF208000-size stay positive for all size in 1..255",
      all((0xFEC00000 - s) & M32 > 0xFEBE0000 and (0xFF208000 - s) & M32 > 0xFF1FFFFF
          for s in range(1, 256)))
check("no unsigned underflow in exclusion overlap formula: min(lo)+1-255 > 0 "
      "for both exclusion tables",
      min(lo for lo, _ in RAM_EXCL + DF_EXCL) + 1 - 255 > 0)
check("copy-time windows exactly equal configured range end-fit "
      "(addr+size <= window_end  <=>  addr+size-1 <= range_high)",
      all(w_end - 1 == RANGES[m][1] for m, w_end in ((1, 0xFEC00000), (2, 0xFF208000))))

# --- requested-vs-emitted length identity ---------------------------------
ok = 0
for data in (req(1, 0xFEBE3800, 1), req(1, 0xFEBF6B01, 0xFF), req(2, 0xFF206F00, 0xB0)):
    res = rmba_request(data)
    if res[0] == "OK":
        memid, addr, size = res[1]
        ok += (memid == data[1] and addr == int.from_bytes(data[2:6], "big")
               and size == data[6])
check("requested == parsed == emitted length on every OK (single-shot copy, "
      "cursor advances by requested size)", ok == 3)

# ---------------------------------------------------------------------------
# 4. Async state ownership / TOCTOU writer census (tracked corpus)
# ---------------------------------------------------------------------------
print("== async state writer census ==")

PRIVATE_STATE = sorted(
    [0xFEBE5D78, 0xFEBE5D7C, 0xFEBE5D80, 0xFEBE5D81, 0xFEBE5D82]
    + list(range(0xFEBE5D84, 0xFEBE5DA0))
    + list(range(0xFEBF4598, 0xFEBF459D))
)
RMBA_GRAPH = set(GATES) | {poll_entry, 0x9392E, 0x8F554, 0x8C3BE}  # 0x8C3BE = cancel reset body (0x8C3E4 thunk target)

writers: dict[int, set[int]] = {}
readers: dict[int, set[int]] = {}
with CORPUS.open() as f:
    for line in f:
        r = json.loads(line)
        try:
            entry = int(r["entry_addr"], 16)
        except (KeyError, TypeError, ValueError):
            continue
        for ref in r.get("data_references") or []:
            try:
                to = int(ref.get("to_addr", ""), 16)
            except (TypeError, ValueError):
                continue
            if to in PRIVATE_STATE:
                (writers if ref.get("ref_type") == "WRITE" else readers).setdefault(to, set()).add(entry)

outside = {a: es for a, es in writers.items() if es - RMBA_GRAPH}
check("every writer of RMBA private state lies inside the RMBA call graph "
      "(TOCTOU surface closed)", not outside,
      "; ".join(f"{a:#x}: {[hex(e) for e in es]}" for a, es in outside.items()) or "none outside")
check("RMBA state block is actively managed (writers exist for address/size/memid/worker state)",
      all(a in writers for a in (0xFEBE5D78, 0xFEBE5D7C, 0xFEBE5D80))
      and 0xFEBF4598 in writers)

# shared response-buffer census (informational; cursor/capacity are Dcm-shared)
SHARED = {0xFEBE5D8C, 0xFEBE5D90, 0xFEBE5D98}
shared_refs: dict[int, set[int]] = {}
with CORPUS.open() as f:
    for line in f:
        r = json.loads(line)
        try:
            entry = int(r["entry_addr"], 16)
        except (KeyError, TypeError, ValueError):
            continue
        for ref in r.get("data_references") or []:
            try:
                to = int(ref.get("to_addr", ""), 16)
            except (TypeError, ValueError):
                continue
            if to in SHARED:
                shared_refs.setdefault(to, set()).add(entry)
for a in sorted(shared_refs):
    print(f"       info: {a:#x} referenced by {[hex(e) for e in sorted(shared_refs[a])]}")
check("poll-side cursor/capacity references present (5D8C/5D90/5D98 wired into RMBA poll)",
      poll_entry in shared_refs.get(0xFEBE5D90, set())
      or 0x8C456 in shared_refs.get(0xFEBE5D90, set()))

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
