#!/usr/bin/env python3
"""Build the V850 arithmetic reference-template catalog for the Renesas_v850 module.

Derives normalized instruction templates for the GCC libgcc DImode arithmetic
helpers from the pinned, committed reference objects under
``data/reference/v850-gcc-libgcc/16.2.0`` and writes the runtime catalog
consumed by ``V850ArithmeticReferenceMatcher``:

    ghidra/ghidra_v850/data/arithmetic/v850_arithmetic_reference_templates.json

Provenance (fully reproducible)
-------------------------------
The reference objects are genuine GCC 16.2.0 build-tree libgcc objects for
``v850-elf`` (default multilib, binutils 2.46.1 in-tree).  They are reproduced
byte-identically (sha256 verified when this producer was introduced) with:

    docker run --rm -v /tmp/out:/out v850-gcc-scratch:latest \
        sh -c 'cd /build/gcc && make all-target-libgcc && \
               cp v850-elf/libgcc/{_muldi3,_udivdi3,_divdi3,_moddi3,_umoddi3, \
               _udivmoddi4,_udivsi3,_umodsi3,_mulsi3,_negdi2,_ashldi3,_ashrdi3, \
               _lshrdi3,_cmpdi2,_ucmpdi2,_addvdi3,_subvdi3,_mulvdi3,_negvdi2, \
               _save_20c,_save_24c,_save_26c,_save_31c,_clz}.o /out/'

``v850-gcc-scratch`` is the build-stage image of the tracked toolchain recipe
``tools/toolchains/v850-gcc/Dockerfile`` (GCC ``releases/gcc-16.2.0`` @
78d4ac73dd391005b895a6148cd9831e28e1208b, binutils 2.46.1 @
5e56594815854de5eca35c7c04b11705d0f19c02, GDB 18.1): its image history was
audited to be that same recipe and GCC configure command
(docs/tooling/processor-module-audit.md), with the ``/build/gcc`` tree kept so
``make all-target-libgcc`` can run in place.  The disassembly pass itself runs
through the pinned runner ``tools/rh850 toolchain run`` (image
ghidra-rh850-v850-gcc:16.2.0-binutils2.46.1-gdb18.1-simfix2, built from the
same tracked Dockerfile), so no host toolchain is required beyond Docker.
``helpers.o`` (adddi3/subdi3 carry idioms; GCC inlines DImode add/sub, so
libgcc ships no __adddi3 object) is rebuilt byte-identically with:

    tools/rh850 toolchain run --work-dir data/reference/v850-gcc-libgcc/16.2.0 \
        v850-elf-gcc -O2 -ffreestanding -c helpers.c -o helpers.o

The upstream sources are pinned by sha256 against the gcc-mirror
``releases/gcc-16.2.0`` tag (libgcc2.c, libgcc/libgcc2.h, include/longlong.h;
verification done at introduction time - the sources are not vendored, so the
producer records the pins instead of re-reading them).  ``___clz_tab`` bytes
are read from the committed ``_clz.o`` .rodata and verified against its
mathematical definition: t[0] == 0 and t[i] == i.bit_length() (floor(log2 i) + 1
for i >= 1), NOT floor(log2 i).

License: the committed objects and their embedded code are GPL-3.0-or-later
with the GCC Runtime Library Exception 3.1 (see COPYING3 / COPYING.RUNTIME in
the reference directory); the generated catalog is a functional interface
description, kept under the repo's own terms.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REF_DIR = REPO_ROOT / "data/reference/v850-gcc-libgcc/16.2.0"
OUTPUT = (
    REPO_ROOT / "ghidra" / "ghidra_v850" / "data" / "arithmetic"
    / "v850_arithmetic_reference_templates.json"
)
SCHEMA = "v850-arithmetic-reference-templates-v1"

# Pinned toolchain identity (see tools/toolchains/rh850.py IMAGE).
OBJDUMP = "/opt/gcc-v850-elf-master/bin/v850-elf-objdump"
TOOLCHAIN_IMAGE = "ghidra-rh850-v850-gcc:16.2.0-binutils2.46.1-gdb18.1-simfix2"
GCC_RELEASE = "releases/gcc-16.2.0"
GCC_VERSION = "16.2.0"
BINUTILS_VERSION = "2.46.1"
# sha256 of the upstream gcc-mirror sources at the pinned GCC commit; recorded
# for provenance (verification was done at introduction; the sources are not
# vendored into this repo, so nothing re-reads them at runtime).
UPSTREAM_SHA256 = {
    "libgcc2.c": "83e1247be3f78dd8c70d32c4df95f04161c0f47838cf62be8cdb5b9eb2f06c34",
    "libgcc2.h": "80c3fe2ae1062abf56456f52518bd670f9ec3917b7f85e152b347ac6b6faf880",
    "longlong.h": "9f768d7d7cbdf02f890e14e505a49375568ac80f3d47855e53b7835645e1e19e",
}

# Function symbol -> template stem (recursive dependency validation).
FUNCTION_DEPS = {
    "___udivsi3": "udivsi3",
    "___umodsi3": "umodsi3",
    "___mulsi3": "mulsi3",
    "___muldi3": "muldi3",
    "___udivmoddi4": "udivmoddi4",
    "__save_r20_r31": "save_r20_r31",
    "__return_r20_r31": "return_r20_r31",
    "__save_r24_r31": "save_r24_r31",
    "__return_r24_r31": "return_r24_r31",
    "__save_r26_r31": "save_r26_r31",
    "__return_r26_r31": "return_r26_r31",
    "__save_r31": "save_r31",
    "__return_r31": "return_r31",
}
DATA_DEPS = {"___clz_tab": "clztab"}
ABORT_DEPS = {"_abort": "abort"}

# stem -> (object file, symbol) pairs; order defines catalog order.
TEMPLATE_SOURCES = [
    ("adddi3", "helpers.o", "_t_add"),
    ("subdi3", "helpers.o", "_t_sub"),
    ("negdi2", "_negdi2.o", "___negdi2"),
    ("ashldi3", "_ashldi3.o", "___ashldi3"),
    ("ashrdi3", "_ashrdi3.o", "___ashrdi3"),
    ("lshrdi3", "_lshrdi3.o", "___lshrdi3"),
    ("cmpdi2", "_cmpdi2.o", "___cmpdi2"),
    ("ucmpdi2", "_ucmpdi2.o", "___ucmpdi2"),
    ("muldi3", "_muldi3.o", "___muldi3"),
    ("udivsi3", "_udivsi3.o", "___udivsi3"),
    ("umodsi3", "_umodsi3.o", "___umodsi3"),
    ("mulsi3", "_mulsi3.o", "___mulsi3"),
    ("udivmoddi4", "_udivmoddi4.o", "___udivmoddi4"),
    ("udivdi3", "_udivdi3.o", "___udivdi3"),
    ("divdi3", "_divdi3.o", "___divdi3"),
    ("moddi3", "_moddi3.o", "___moddi3"),
    ("umoddi3", "_umoddi3.o", "___umoddi3"),
    ("addvdi3", "_addvdi3.o", "___addvdi3"),
    ("subvdi3", "_subvdi3.o", "___subvdi3"),
    ("mulvdi3", "_mulvdi3.o", "___mulvdi3"),
    ("negvdi2", "_negvdi2.o", "___negvdi2"),
    ("save_r20_r31", "_save_20c.o", "__save_r20_r31"),
    ("return_r20_r31", "_save_20c.o", "__return_r20_r31"),
    ("save_r24_r31", "_save_24c.o", "__save_r24_r31"),
    ("return_r24_r31", "_save_24c.o", "__return_r24_r31"),
    ("save_r26_r31", "_save_26c.o", "__save_r26_r31"),
    ("return_r26_r31", "_save_26c.o", "__return_r26_r31"),
    ("save_r31", "_save_31c.o", "__save_r31"),
    ("return_r31", "_save_31c.o", "__return_r31"),
]

# objdump Bcond spellings (binutils uses bl/bnl as aliases of bc/bnc); the
# canonical catalog names are the module SLEIGH cc0003 spellings.
CC_ALIASES = {
    "v", "nv", "c", "nc", "e", "ne", "nh", "h", "n", "p", "r", "sa",
    "lt", "ge", "le", "gt", "l", "nl",
}


def is_bcond(mnem: str, words: list[int]) -> bool:
    return (mnem.startswith("b") and mnem != "br" and len(words) == 1
            and mnem[1:] in CC_ALIASES)


# Ghidra cc0003 names indexed by the 4-bit condition selector VALUE; the
# catalog normalizes objdump alias spellings (bl/bnl/...) to the SLEIGH names.
CC_NAMES = ["v", "c", "e", "nh", "n", "r", "lt", "le",
            "nv", "nc", "ne", "h", "p", "sa", "ge", "gt"]

REGS = {
    "r0": 0, "r1": 1, "r2": 2, "sp": 3, "r3": 3, "gp": 4, "r4": 4, "tp": 5,
    "r5": 5, "r6": 6, "r7": 7, "r8": 8, "r9": 9, "r10": 10, "r11": 11,
    "r12": 12, "r13": 13, "r14": 14, "r15": 15, "r16": 16, "r17": 17,
    "r18": 18, "r19": 19, "r20": 20, "r21": 21, "r22": 22, "r23": 23,
    "r24": 24, "r25": 25, "r26": 26, "r27": 27, "r28": 28, "r29": 29,
    "ep": 30, "r30": 30, "lp": 31, "r31": 31,
}

RE_FUNC = re.compile(r"^([0-9a-f]+) <(.+)>:$")
RE_INSN = re.compile(
    r"^\s+([0-9a-f]+):\s+((?:[0-9a-f]{2} )+)[ \t]*([a-z][a-z0-9.]*)\s*(.*)$")
RE_RELOC = re.compile(r"^\s+([0-9a-f]+): (R_\S+)\s+(\S+)")
RE_TARGET = re.compile(r"^([0-9a-f]+)(?:\s+<([^>+]+)(?:\+0x([0-9a-f]+))?>)?$")


def fail(msg: str) -> None:
    raise SystemExit(f"build_v850_arithmetic_reference_templates: {msg}")


def sha256_file(path: Path) -> str:
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_objdump(args: list[str]) -> str:
    """Run the pinned container objdump against the committed reference dir."""
    cmd = [
        str(REPO_ROOT / "tools/rh850"), "toolchain", "run",
        "--work-dir", str(REF_DIR), "sh", "-c",
        " ".join([OBJDUMP, *args]),
    ]
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(f"objdump failed ({' '.join(args)}):\n{proc.stderr}")
    return proc.stdout


def parse_functions(text: str):
    """objdump -dr text -> {symbol: {"insns": [(off, words, mnem, ops)], "relocs": {off: (type, sym)}}}."""
    funcs: dict[str, dict] = {}
    cur = None
    for line in text.splitlines():
        m = RE_FUNC.match(line)
        if m:
            cur = {"entry": int(m.group(1), 16), "name": m.group(2),
                   "insns": [], "relocs": {}}
            funcs[m.group(2)] = cur
            continue
        m = RE_RELOC.match(line)
        if m and cur is not None:
            off = int(m.group(1), 16)
            prev = cur["relocs"].get(off)
            if prev is not None:
                fail(f"multiple relocations at {off:#x} in {cur['name']}")
            cur["relocs"][off] = (m.group(2), m.group(3))
            continue
        m = RE_INSN.match(line)
        if m and cur is not None:
            off = int(m.group(1), 16)
            bs = m.group(2).split()
            words = [int(bs[i], 16) | (int(bs[i + 1], 16) << 8)
                     for i in range(0, len(bs), 2)]
            cur["insns"].append((off, words, m.group(3), m.group(4).strip()))
    return funcs


def words_hex(words: list[int]) -> str:
    return ",".join(f"{w & 0xffff:04x}" for w in words)


def reg_token(name: str) -> str:
    n = REGS.get(name)
    if n is None:
        fail(f"unknown register operand {name!r}")
    return f"r{n}"


def cc_of(words: list[int]) -> int:
    return words[0] & 0xF


def norm_mnemonic(mnem: str, words: list[int]) -> str:
    """Canonicalize objdump mnemonics to the module SLEIGH spellings."""
    if is_bcond(mnem, words):
        return "b" + CC_NAMES[cc_of(words)]
    if mnem.startswith("setf") and len(words) == 2:
        return "setf" + CC_NAMES[cc_of(words)]
    if mnem.startswith("sasf") and len(words) == 2:
        return "sasf" + CC_NAMES[cc_of(words)]
    return mnem


# Mnemonics whose final register operand is a destination (backward def scan).
WRITERS = {
    "mov", "movhi", "movea", "addi", "andi", "ori", "xori", "add", "sub",
    "subr", "or", "and", "xor", "not", "mulh", "shr", "shl", "sar",
    "setf", "ld.b", "ld.bu", "ld.h", "ld.hu", "ld.w",
}


def parse_target(text: str) -> int:
    m = RE_TARGET.match(text)
    if not m or m.group(1) is None:
        fail(f"unparsable branch target {text!r}")
    return int(m.group(1), 16)


def normalize(symbol: str, func: dict) -> dict:
    """Build one normalized template body from a parsed function."""
    entry = func["entry"]
    insns = func["insns"]
    out_insns = []
    lengths = []
    consumed_relocs = set()
    prev_end = 0
    for idx, (off, words, mnem, ops) in enumerate(insns):
        m = norm_mnemonic(mnem, words)
        # A relocation binds to the halfword it patches: PCR22 sits on the
        # first word of a (4-byte) jr/jarl; R_V810_WHI1/R_V810_WLO sit on the
        # imm16 SECOND word of a 4-byte movhi/movea (off + 2).  Never attach
        # an off+2 relocation to a 2-byte instruction: that halfword belongs
        # to the following instruction.
        reloc = func["relocs"].get(off)
        if reloc is not None:
            consumed_relocs.add(off)
        elif len(words) == 2 and (off + 2) in func["relocs"]:
            reloc = func["relocs"][off + 2]
            consumed_relocs.add(off + 2)
        if off - entry != prev_end:
            fail(f"{symbol}+{off:#x}: non-contiguous instruction stream "
                 f"(expected {entry + prev_end:#x})")
        prev_end = off - entry + 2 * len(words)
        lengths.append(2 * len(words))
        toks: list[str] = []
        raw_ops = [o for o in ops.split(",")] if ops else []
        if m == "br" or is_bcond(mnem, words):
            target = parse_target(raw_ops[0])
            toks.append(f"@{target - entry:#x}")
            raw_ops = raw_ops[1:]
        elif m in ("jr", "jarl"):
            if reloc is not None:
                if reloc[0] != "R_V850_PCR22":
                    fail(f"{symbol}+{off:#x}: unexpected reloc {reloc[0]}")
                toks.append(f"P:{reloc[1]}")
            else:
                target = parse_target(raw_ops[0])
                toks.append(f"@{target - entry:#x}")
            raw_ops = raw_ops[1:]
        elif m == "jmp":
            t = raw_ops[0]
            if not (t.startswith("[") and t.endswith("]")):
                fail(f"{symbol}+{off:#x}: bad jmp operand {ops!r}")
            toks.append(reg_token(t[1:-1]))
            raw_ops = raw_ops[1:]
        elif mnem.startswith("setf") or mnem.startswith("sasf"):
            raw_ops = raw_ops[1:]  # objdump renders the condition as operand 1
        for op in raw_ops:
            op = op.strip()
            mm = re.fullmatch(r"(-?\w+)\[(\w+)\]", op)
            if mm:
                if reloc is not None:
                    fail(f"{symbol}+{off:#x}: reloc on memory operand")
                toks.append(f"#{int(mm.group(1), 0)}")
                toks.append(reg_token(mm.group(2)))
            elif op in REGS:
                toks.append(reg_token(op))
            else:
                try:
                    val = int(op, 0)
                except ValueError:
                    fail(f"{symbol}+{off:#x}: unparsable operand {op!r}")
                if reloc is not None and reloc[0] == "R_V810_WHI1":
                    if val != 0:
                        fail(f"{symbol}+{off:#x}: nonzero WHI1 addend")
                    toks.append(f"H:{reloc[1]}")
                elif reloc is not None and reloc[0] == "R_V810_WLO":
                    if val != 0:
                        fail(f"{symbol}+{off:#x}: nonzero WLO addend")
                    toks.append(f"L:{reloc[1]}")
                else:
                    toks.append(f"#{val}")
        if reloc is not None and reloc[0] not in (
                "R_V850_PCR22", "R_V810_WHI1", "R_V810_WLO"):
            fail(f"{symbol}+{off:#x}: unhandled reloc type {reloc[0]}")
        out_insns.append([off - entry, m, *toks])
    # Every relocation under the function must have been attached to some
    # instruction halfword; a dropped relocation would silently weaken the
    # template, so fail loudly instead.
    stray = set(func["relocs"]) - consumed_relocs
    if stray:
        fail(f"{symbol}: relocations not attached to any instruction: "
             + ", ".join(f"{o:#x} {func['relocs'][o][0]}" for o in sorted(stray)))
    # symbol bindings and indirect-jump register provenance
    bindings: dict[str, dict] = {}
    jumps: list[dict] = []
    for idx, (off, words, mnem, ops) in enumerate(insns):
        toks = out_insns[idx][2:]
        for t in toks:
            if t.startswith(("P:", "H:", "L:")):
                sym = t[2:]
                slot = {"P": "p", "H": "h", "L": "l"}[t[0]]
                bindings.setdefault(sym, {"p": [], "h": [], "l": []})[slot].append(idx)
        if out_insns[idx][1] == "jmp" and toks and toks[0].startswith("r"):
            reg = toks[0]
            j = idx - 1
            while j >= 0:
                prev = out_insns[j]
                if prev[1] in WRITERS and prev[-1] == reg:
                    if prev[1] == "movea" and len(prev) >= 4 and prev[-3].startswith("L:"):
                        hi_idx = None
                        k = j - 1
                        while k >= 0:
                            cand = out_insns[k]
                            if cand[1] == "movhi" and cand[-1] == reg:
                                hi_idx = k
                                break
                            k -= 1
                        if hi_idx is None:
                            fail(f"{symbol}+{off:#x}: no movhi for jmp {reg}")
                        jumps.append({"i": idx, "reg": reg, "hi": hi_idx, "lo": j})
                    break
                j -= 1
    return {"insns": out_insns, "lengths": lengths, "bindings": bindings,
            "jumps": jumps,
            "encoding": [words_hex(w) for _, w, _, _ in insns]}


def clz_table() -> dict:
    text = run_objdump(["-s", "-j", ".rodata", "/out/_clz.o"])
    data = bytearray()
    for line in text.splitlines():
        m = re.match(r"^\s*[0-9a-f]+ ((?:[0-9a-f]{2,8} ){1,4})", line)
        if not m:
            continue
        row = m.group(1).replace(" ", "")
        data.extend(int(row[i:i + 2], 16) for i in range(0, len(row), 2))
    if len(data) != 256:
        fail(f"___clz_tab: expected 256 bytes, parsed {len(data)}")
    # GCC libgcc2.c defines __clz_tab[0] = 0 and __clz_tab[i] = floor(log2 i)+1
    # (i.e. i.bit_length()); verified against the committed object's .rodata.
    for i, b in enumerate(data):
        want = i.bit_length()
        if b != want:
            fail(f"___clz_tab[{i}] = {b}, expected {want}")
    return {"bytes": data.hex()}


def toolchain_identities() -> dict:
    proc = subprocess.run(
        [str(REPO_ROOT / "tools/rh850"), "toolchain", "run", "--work-dir", str(REF_DIR),
         "sh", "-c",
         "/opt/gcc-v850-elf-master/bin/v850-elf-gcc --version | head -n1; "
         "/opt/gcc-v850-elf-master/bin/v850-elf-objdump --version | head -n1"],
        cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(f"toolchain identity probe failed:\n{proc.stderr}")
    lines = [l for l in proc.stdout.splitlines() if l.strip()]
    if len(lines) < 2:
        fail(f"toolchain identity probe returned {lines!r}")
    return {"gcc": lines[0], "objdump": lines[1]}


def build() -> dict:
    objects = sorted({src for _, src, _ in TEMPLATE_SOURCES})
    for obj in objects:
        if not (REF_DIR / obj).is_file():
            fail(f"missing reference object {obj}")
    script = " ".join(
        [f"{OBJDUMP} -dr /out/{o};" for o in objects]
        + [f"{OBJDUMP} -s -j .rodata /out/_clz.o;"])
    proc = subprocess.run(
        [str(REPO_ROOT / "tools/rh850"), "toolchain", "run", "--work-dir", str(REF_DIR),
         "sh", "-c", script],
        cwd=REPO_ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        fail(f"objdump batch failed:\n{proc.stderr}")
    all_funcs = parse_functions(proc.stdout)

    helpers = []
    for stem, obj, symbol in TEMPLATE_SOURCES:
        if symbol not in all_funcs:
            fail(f"{obj}: symbol {symbol} not found")
        body = normalize(symbol, all_funcs[symbol])
        if not body["insns"]:
            fail(f"{obj}:{symbol}: empty body")
        helpers.append({
            "stem": stem,
            "symbol": symbol,
            "object": obj,
            "object_sha256": sha256_file(REF_DIR / obj),
            "size": len(body["insns"]),
            "instructions": body["insns"],
            "lengths": body["lengths"],
            "bindings": body["bindings"],
            "jumps": body["jumps"],
        })

    symbols = {}
    for stem, _, _ in TEMPLATE_SOURCES:
        symbols["___" + stem] = {"kind": "function", "stem": stem}
        symbols["__" + stem] = {"kind": "function", "stem": stem}
        symbols[stem] = {"kind": "function", "stem": stem}
    for sym, stem in FUNCTION_DEPS.items():
        symbols[sym] = {"kind": "function", "stem": stem}
    for sym, kind in DATA_DEPS.items():
        symbols[sym] = {"kind": kind}
    for sym, kind in ABORT_DEPS.items():
        symbols[sym] = {"kind": kind}

    doc = {
        "schema": SCHEMA,
        "provenance": {
            "gcc_release": GCC_RELEASE,
            "gcc_version": GCC_VERSION,
            "binutils_version": BINUTILS_VERSION,
            "toolchain_image": TOOLCHAIN_IMAGE,
            "toolchain_identities": toolchain_identities(),
            "upstream_sha256": UPSTREAM_SHA256,
            "reference_objects": {
                o: sha256_file(REF_DIR / o) for o in objects
            },
            "rebuild_recipe": (
                "docker run --rm -v /tmp/out:/out v850-gcc-scratch:latest "
                "sh -c 'cd /build/gcc && make all-target-libgcc && "
                "cp v850-elf/libgcc/<objects> /out/'; v850-gcc-scratch is "
                "the build-stage image of the tracked recipe "
                "tools/toolchains/v850-gcc/Dockerfile (GCC releases/gcc-16.2.0 "
                "@ 78d4ac73dd391005b895a6148cd9831e28e1208b, target v850-elf, "
                "default multilib; image history audited in "
                "docs/tooling/processor-module-audit.md; byte-identity of the "
                "copied objects verified against reference_objects sha256 at "
                "introduction); helpers.o: tools/rh850 toolchain run "
                "--work-dir data/reference/v850-gcc-libgcc/16.2.0 "
                "v850-elf-gcc -O2 -ffreestanding -c helpers.c -o helpers.o"
            ),
            "license": "GPL-3.0-or-later WITH GCC-exception-3.1 "
                       "(see data/reference/v850-gcc-libgcc/16.2.0/COPYING3 "
                       "and COPYING.RUNTIME)",
        },
        "clz_tab": clz_table(),
        "symbols": symbols,
        "helpers": helpers,
    }
    return doc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    doc = build()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(doc, indent=1, sort_keys=False) + "\n")
    total = sum(h["size"] for h in doc["helpers"])
    print(f"wrote {OUTPUT.relative_to(REPO_ROOT)}: {len(doc['helpers'])} templates, "
          f"{total} instructions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
