#!/usr/bin/env python3
"""Build the exact-F33 command-cone ingress census from the canonical corpus.

Closes the denominator of scalar generated-COM inputs into the cooperative/
lateral cluster (0xBCD66..0xCEFFC) and the command/actuation cone
(FEBECC62 -> FEBEAC56 -> FEBE6772 / command-current cells) beyond the pinned
19-signal copy-edge model of VAR-065.  The prior census stopped at one
snapshot copier (0xBCD66) and a fixed consumer list; this builder enumerates:

  * every literal and table-driven scalar extract (FUN_0007D12A/FUN_0007E72A),
  * the stage copy 0x58074 including init-constant cells,
  * all six snapshot copiers 0xBC96A/0xBCA08/0xBCAA6/0xBCBD8/0xBCD62/0xBCD66,
  * the qualification layer that turns stages into FEBEBxxx values/flags,
  * statement-level composition provenance for every FEBEE400..418 byte,
  * the gain/selector machinery (0xCB516/0xCB548/0xCB82C/0xCB9E2/0xCB73A),

and classifies each non-B6 COM input as magnitude / gate / observer /
telemetry.  Everything is re-derived from data/generated/camry-8965F3307000/
decompilations.jsonl plus firmware bytes; nothing is copied from narrative
docs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from collections import Counter, defaultdict
from pathlib import Path

from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256, REPO

OUT = REPO / "data/generated/camry_8965F3307000_command_cone_ingress.json"

GP = 0xFEBEB800
FRAME_BASE = GP - 0x6DB8      # 0xFEBE4A48 COM frame block
STATUS_BASE = GP - 0x6EC2     # 0xFEBE493E per-PDU status bytes
RX_TABLE, RX_COUNT = 0x21FE8, 43
SIGNAL_TO_PDU, SIGNAL_COUNT, PDU_OFFSETS = 0x22488, 284, 0x22840
CLUSTER_LO, CLUSTER_HI = 0xBCD66, 0xCEFFC

# table-driven extract configuration (indirect call sites)
INDIRECT_TABLES = {
    "signal_ids": 0x257DA,      # u8 step 2, 14 entries
    "wire_offsets": 0x257F6,    # u16 step 2, 14 entries
    "d12a_bits": (0x25812, 0x25815),
    "qual_threshold": 0x30E2F,
    "drivers": [(0x69780, 0x693FE, 8, "familyA"), (0x69C58, 0x697F4, 5, "familyB")],
}

# runtime stage cells that no raw extract feeds: init-only in this image
INIT_ONLY_STAGE_CELLS = {
    0xFEBEF098: 0, 0xFEBEF099: 0, 0xFEBEF09C: 1, 0xFEBEF0AA: 0, 0xFEBEF1C0: 0,
}


def need(cond: object, msg: str) -> None:
    if not cond:
        raise ValueError(msg)


def corpus_map() -> dict[int, dict]:
    out = {}
    with CORPUS.open() as f:
        for line in f:
            row = json.loads(line)
            if row.get("record") == "function":
                out[int(row["entry_addr"], 16)] = row
    return out


# ---------------------------------------------------------------- parsing ---

PTR_ASSIGN = re.compile(r"\b(puVar\d+|pbVar\d+)\s*=\s*&?(?:LAB_|DAT_)([0-9a-f]{8})")
DAT_TOK = re.compile(r"\bDAT_(fe[0-9a-f]{6})\b")
DEREF = re.compile(
    r"\*\s*\(\s*(?:undefined\d*|ushort|uint|int|short|char|uchar|ulong|long|bool)\s*\*?\s*\)"
    r"\s*\(\s*(puVar\d+)\s*\+\s*(-?0x[0-9a-f]+)\s*\)")
PARR = re.compile(r"\b(puVar\d+)\s*\[\s*(-?0x[0-9a-f]+)\s*\]")
PTRADD = re.compile(r"\(\s*(puVar\d+)\s*\+\s*(-?0x[0-9a-f]+)\s*\)")


def bases_of(text: str) -> dict[str, int]:
    return {m.group(1): int(m.group(2), 16) for m in PTR_ASSIGN.finditer(text)}


def cell_tokens(stmt: str, bases: dict[str, int]) -> set[int]:
    out = set()
    for m in DAT_TOK.finditer(stmt):
        out.add(int(m.group(1), 16))
    for m in DEREF.finditer(stmt):
        var, off = m.group(1), int(m.group(2), 16)
        if var in bases:
            out.add(bases[var] + off)
    for m in PARR.finditer(stmt):
        var, off = m.group(1), int(m.group(2), 16)
        if var in bases:
            out.add(bases[var] + off)
    for m in PTRADD.finditer(stmt):
        var, off = m.group(1), int(m.group(2), 16)
        if var in bases:
            out.add(bases[var] + off)
    return out


def exact_pairs(entry: int, funcs: dict[int, dict]) -> list[tuple[int, int]]:
    """Single-cell <- single-cell copy statements resolved through GP bases."""
    text = funcs[entry]["decompiled_c"]
    bases = bases_of(text)
    out = []
    for chunk in text.split(";"):
        m = re.match(r"^\s*(.+?)\s*=\s*(.+)$", chunk.strip(), re.S)
        if not m:
            continue
        lt = cell_tokens(m.group(1), bases)
        rt = cell_tokens(m.group(2), bases)
        if len(lt) == 1 and len(rt) == 1 and next(iter(lt)) != next(iter(rt)):
            out.append((next(iter(rt)), next(iter(lt))))
    return out


def accessors(cell: int, funcs: dict[int, dict]) -> dict[str, set[str]]:
    h = f"{cell:08x}"
    out: dict[str, set[str]] = defaultdict(set)
    for e, row in funcs.items():
        for r in row.get("data_references", []):
            if int(r["to_addr"], 0) == cell:
                out[f"0x{e:05X}"].add(r["ref_type"])
        if f"DAT_{h}" in row["decompiled_c"]:
            out[f"0x{e:05X}"].add("txt")
    return dict(out)


def token(entry: int, funcs: dict[int, dict], *tokens: str) -> str:
    text = funcs[entry]["decompiled_c"]
    for t in tokens:
        need(t in text, f"0x{entry:08X} missing {t!r}")
    return text


# ------------------------------------------------------------------ build ---

def build() -> dict:
    image = IMAGE.read_bytes()
    need(len(image) == 0x100000 and hashlib.sha256(image).hexdigest() == IMAGE_SHA256,
         "F33 image drift")
    funcs = corpus_map()
    need(len(funcs) == 6065, "F33 corpus function count drift")

    rx: dict[int, dict] = {}
    for i in range(RX_COUNT):
        raw, length = struct.unpack_from("<II", image, RX_TABLE + i * 8)
        pdu = 5 + i
        rx[pdu] = {"pdu": pdu, "can_id": raw & 0x1FFFFFFF,
                   "can_fd": bool(raw & 0x40000000), "length": length}
    s2p = [struct.unpack_from("<H", image, SIGNAL_TO_PDU + 2 * i)[0] for i in range(SIGNAL_COUNT)]
    pdu_off = [struct.unpack_from("<H", image, PDU_OFFSETS + 2 * i)[0] for i in range(48)]

    # ---- L1: scalar extracts (literal + indirect) ------------------------
    call_re = re.compile(
        r"FUN_0007d12a\((0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),"
        r"(0x[0-9a-f]+|\d+),(0x[0-9a-f]+|\d+),([^;]+)\);", re.I)
    scalar = []
    for entry, row in funcs.items():
        for m in call_re.finditer(row["decompiled_c"]):
            sid, off, bits, bitoff, signed = [int(m.group(i), 0) for i in range(1, 6)]
            pdu = s2p[sid]
            if pdu not in rx:
                continue
            dest = m.group(6).strip()
            cell = None
            dm = re.fullmatch(r"&DAT_(fe[0-9a-f]{6})", dest)
            if dm:
                cell = int(dm.group(1), 16)
            else:
                hm = re.fullmatch(r"0x(fe[0-9a-f]{6})", dest, re.I)
                if hm:
                    cell = int(hm.group(1), 16)
                else:
                    bm = re.fullmatch(r"(puVar\d+)\s*\+\s*(-?0x[0-9a-f]+)", dest)
                    if bm:
                        b = bases_of(row["decompiled_c"]).get(bm.group(1))
                        if b is not None:
                            cell = b + int(bm.group(2), 16)
            scalar.append({
                "signal": sid, "pdu": pdu, "can_id": rx[pdu]["can_id"],
                "length": rx[pdu]["length"], "can_fd": rx[pdu]["can_fd"],
                "wire_offset": off, "byte_offset": off - pdu_off[pdu],
                "bits": bits, "bit_offset": bitoff, "signed": bool(signed),
                "unpacker": f"0x{entry:05X}", "dest": dest,
                "raw_cell": f"0x{cell:08X}" if cell else None,
            })

    sig243_text = token(0x4BB62, funcs,
                        "auStack_9[0] = DAT_febe80a0;",
                        "FUN_0007d12a(0xf3,0x187,1,7,0,auStack_9);",
                        "puVar2[-0x3760] = auStack_9[0];")

    # indirect/table-driven extracts
    sid_tab = {a: image[a] for a in range(0x257DA, 0x257F6, 2)}
    off_tab = {a: struct.unpack_from("<H", image, a)[0] for a in range(0x257F6, 0x25812, 2)}
    indirect = []
    for a, sid in sid_tab.items():
        pdu = s2p[sid]
        off_a = 0x257F6 + (a - 0x257DA)
        caller = "0x000697F4" if sid >= 98 else "0x000693FE"
        indirect.append({
            "signal": sid, "pdu": pdu, "can_id": rx[pdu]["can_id"],
            "wire_offset": off_tab[off_a], "byte_offset": off_tab[off_a] - pdu_off[pdu],
            "source": f"DAT_{a:06X}", "caller": caller,
        })
    need({x["signal"] for x in indirect} == set(range(90, 104)),
         "indirect signal-id table drift")
    need({x["can_id"] for x in indirect} == set(range(0x013, 0x020)),
         "indirect PDU family drift")
    token(0x693FE, funcs, "FUN_0007e72a(DAT_000257da,DAT_000257f6,8,local_54);",
          "local_54[0x40] = 0x5a;", "DAT_00030e2f <= bVar4")
    token(0x697F4, funcs, "FUN_0007e72a(DAT_000257ee,DAT_0002580a,8,acStack_34 + 3);",
          "DAT_00030e2f <= bVar2")
    token(0x7E72A, funcs, "(&DAT_febe4a48)[uVar3 + (param_2 & 0xffff)]",
          "puVar4[uVar2 - 0x6ec2]")
    token(0x7D12A, funcs, "puVar8[uVar7 - 0x6ec2]", "puVar8 + ((param_2 & 0xffff) - 0x6db8)")

    # transforms applied inside unpackers (FUN_0004AFCC offset helper)
    token(0x4AFCC, funcs, "iVar1 = (param_3 & 0xffff) - (int)param_2;", "*param_4 = (short)iVar1;")
    token(0x4B9F4, funcs,
          "FUN_0007d12a(0xe5,0x167,10,0,0,puVar2 + -0x377c);",
          "FUN_0004afcc(0,0x200,*(undefined2 *)(puVar2 + -0x377c),puVar2 + -0x3776);")
    transforms = [
        {"helper": "0x0004AFCC", "form": "s16(raw10 - 0x200)",
         "signals": {229: "0xFEBE808A", 232: "0xFEBE808C", 235: "0xFEBE808E"},
         "can_id": "0x090"},
    ]

    # ---- L2: stage copy ---------------------------------------------------
    t74 = funcs[0x58074]["decompiled_c"]
    need("DAT_febef098 = 0" in t74 and "DAT_febef09c = 1" in t74
         and "DAT_febef1c0 = 0" in t74, "0x58074 init-constant drift")
    # FEBEF093/094 are staged copies, not constants: FEBE80A5 has no extractor
    # anywhere in the corpus (structurally 0), FEBE80A0 is B6 signal 243.
    need("DAT_febef093 = DAT_febe80a5" in t74 and "DAT_febef094 = DAT_febe80a0" in t74,
         "FEBEF093/094 staging drift")
    raw_cells = {int(x["raw_cell"], 16) for x in scalar if x["raw_cell"]} | {0xFEBE80A0}
    stage_edges = exact_pairs(0x58074, funcs)
    raw_stage = sorted((r, w) for r, w in stage_edges if r in raw_cells)
    staged_raws = {r for r, _ in raw_stage}
    need(len(staged_raws) == 98 and len(raw_stage) == 105,
         f"stage census drift: {len(staged_raws)}/{len(raw_stage)}")
    need(any(r == 0xFEBE80A0 and w == 0xFEBEF094 for r, w in raw_stage),
         "sig243 -> FEBEF094 stage edge drift")
    need(not any("FUN_0007d12a(" in funcs[e]["decompiled_c"] and "febe80a5" in funcs[e]["decompiled_c"]
                 for e in funcs), "unexpected extractor for FEBE80A5")
    for c, v in INIT_ONLY_STAGE_CELLS.items():
        h = f"{c:08x}"
        need(f"DAT_{h} = {v}" in t74, f"init-constant {h} drift")
        wr = [e for e, row in funcs.items()
              if any(int(r["to_addr"], 0) == c and r["ref_type"] == "WRITE"
                     for r in row.get("data_references", []))]
        need(set(wr) <= {0x58074, 0x59448}, f"runtime writer appeared for {h}: {wr}")

    # own unpacker, the stage copier (constants/flags), and the write-only
    # initializer 0x58C9A -- no consumer exists for them.
    unstaged = sorted(raw_cells - staged_raws)
    need(len(unstaged) == 18, f"unstaged raw census drift: {len(unstaged)}")
    for c in unstaged:
        acc = accessors(c, funcs)
        allowed = {x["unpacker"] for x in scalar
                   if x["raw_cell"] == f"0x{c:08X}"} | {"0x58074", "0x58C9A"}
        need(set(acc) <= allowed, f"unstaged raw 0x{c:08X} gained accessor {set(acc) - allowed}")
    need(not any(r["ref_type"] == "READ" for r in funcs[0x58C9A]["data_references"]),
         "0x58C9A initializer is no longer write-only")
    token(0x58C9A, funcs, "DAT_febe81f4 = 0;", "DAT_febe820c = 0;")
    # denominator close 2: complete stage-reader census (READ refs or RHS tokens)
    com_raw_space = raw_cells | {0xFEBE808A, 0xFEBE808C, 0xFEBE808E, 0xFEBE80A5}
    all_stages = ({w for r, w in stage_edges if r in com_raw_space}
                  | set(INIT_ONLY_STAGE_CELLS) | {0xFEBEF093, 0xFEBEF094})
    need(len(all_stages) == 114, f"COM stage-space drift: {len(all_stages)}")
    stage_readers = set()
    for e, row in funcs.items():
        if e == 0x58074:
            continue
        rd = {int(r["to_addr"], 0) for r in row.get("data_references", [])
              if r["ref_type"] == "READ"}
        if rd & all_stages:
            stage_readers.add(e)
            continue
        for m in re.finditer(r"=\s*([^;]+)", row["decompiled_c"]):
            if cell_tokens(m.group(1), bases_of(row["decompiled_c"])) & all_stages:
                stage_readers.add(e)
                break
    need(len(stage_readers) == 52, f"stage-reader census drift: {len(stage_readers)}")
    in_cluster = sorted(e for e in stage_readers if CLUSTER_LO <= e <= CLUSTER_HI)
    need(len(in_cluster) == 15, f"cluster stage-reader drift: {len(in_cluster)}")
    need(max(stage_readers) == 0xBF0EC,
         "a C/D-family compute function now reads stages directly")
    stage_reader_census = {
        "total": len(stage_readers),
        "in_cluster": len(in_cluster),
        "max_reader": f"0x{max(stage_readers):05X}",
        "readers": [f"0x{e:05X}" for e in sorted(stage_readers)],
        "structural_claim": "no function above 0xBF0EC (no C/D-family cluster compute or "
                            "composition function) reads stage cells directly; the C/D families "
                            "consume the L4 snapshot bank instead",
    }
    # denominator close 3: group receive callers are exactly the two qualifiers
    gcallers = sorted(e for e, row in funcs.items()
                      if e != 0x7E72A and "FUN_0007e72a(" in row["decompiled_c"])
    need(gcallers == [0x693FE, 0x697F4], f"group caller drift: {gcallers}")

    # ---- L4: snapshot copiers ---------------------------------------------
    COPIERS = [0xBC96A, 0xBCA08, 0xBCAA6, 0xBCBD8, 0xBCD62, 0xBCD66]
    copiers = {}
    pair_map: dict[int, int] = {}
    for e in COPIERS:
        prs = exact_pairs(e, funcs)
        copiers[f"0x{e:05X}"] = len(prs)
        for r, w in prs:
            pair_map[w] = r
    need(copiers == {"0xBC96A": 1, "0xBCA08": 13, "0xBCAA6": 1,
                     "0xBCBD8": 46, "0xBCD62": 245, "0xBCD66": 245},
         f"copier pair census drift: {copiers}")
    need(len(pair_map) == 306, f"unique snapshot dest drift: {len(pair_map)}")

    # ---- L5: composition + actuation byte map -----------------------------
    t33 = funcs[0xBF33E]["decompiled_c"]
    block_map = {}
    for chunk in t33.split(";"):
        m = re.match(r"^\s*(.+?)\s*=\s*(.+)$", chunk.strip(), re.S)
        if not m:
            continue
        lt = cell_tokens(m.group(1), bases_of(t33))
        rt = cell_tokens(m.group(2), bases_of(t33))
        lw = [a for a in lt if 0xFEBEE400 <= a <= 0xFEBEE418]
        if lw:
            block_map[f"FEBEE4{lw[0] - 0xFEBEE400:02X}"] = [
                f"0x{c:08X}" for c in sorted(rt)]
    need(len(block_map) == 17, f"command-block statement map drift: {len(block_map)}")
    need([k for k, v in block_map.items() if not v] == ["FEBEE401", "FEBEE402", "FEBEE404"],
         "constant-zero block bytes drift")
    token(0xD0AAE, funcs, "DAT_febeac56 = DAT_febecc62;", "DAT_febeac54 = DAT_febecc64;",
          "DAT_febeac68 = DAT_febecc60;", "DAT_febeac2d = 0x5a;")
    token(0xD039E, funcs, "sVar4 = (short)((iVar6 * *(short *)(puVar3 + 0x101a)) / 0x100);",
          "*(int *)(puVar3 + 0x1440) = iVar5;", "*(short *)(puVar3 + 0x1450) = sVar7;")
    token(0xD042C, funcs, "DAT_febecc62")
    token(0xD04AC, funcs, "DAT_febecc5a = DAT_febeac10;", "DAT_febecc56 = DAT_febeac10;")
    token(0xD0382, funcs, "DAT_febecc60 = DAT_febeac52;", "DAT_febecc60 = DAT_febecc4e,")

    # The CC60 branch is not sourced by FEBE71F2.  D0382 uses AC52 as a symmetric
    # LIMIT on the dynamic CC4E value.  Close the actual non-B6 value path before
    # recording composition provenance.
    token(0xD0218, funcs, "DAT_febecc48 = iVar1 + iVar3;", "DAT_febecb38 + (int)DAT_febec5ee",
          "DAT_febec43c + DAT_febec4c0 + (int)DAT_febec3ba + DAT_febecc2c + DAT_febebf3c")
    token(0xD0284, funcs, "DAT_febecc44", "DAT_febecc4c = DAT_000b1334;")
    token(0xD02DA, funcs, "DAT_febecc4e = DAT_febecc4c;", "DAT_febecc38 + DAT_febecc3c")

    # D0284's multiplier is internal calibration state too, not another external
    # value ingress.  BCBD8 snapshots FEBEB140 -> FEBEAC64.  The three normal
    # writers derive B140 from the exact u16 calibration at 0xAEF4C; BF97A's
    # reset/default writer uses the adjacent rounded constant 0x7637.
    need(pair_map.get(0xFEBEAC64) == 0xFEBEB140, "AC64 scale snapshot drift")
    token(0xB3866, funcs, "uVar1 = (uint)(ushort)PTR_DAT_000aef4c;",
          "DAT_febeb140 = DAT_febeb13c;", "0x2774564e / uVar1")
    token(0xB389C, funcs, "uVar1 = (uint)(ushort)PTR_DAT_000aef4c;",
          "DAT_febeb140 = DAT_febeb13c;", "0x2774564e / uVar1")
    token(0xB38D2, funcs, "uVar5 = (uint)(ushort)PTR_DAT_000aef4c;",
          "0x2774564e / uVar5", "*(undefined2 *)(puVar2 + -0x6c0) = uVar4;")
    token(0xBF97A, funcs, "*(undefined2 *)(puVar4 + -0x6c0) = 0x7637;")
    scale_cal = struct.unpack_from("<H", image, 0xAEF4C)[0]
    scale_runtime = 0x2774564E // scale_cal
    need(scale_cal == 0x5571 and scale_runtime == 0x7636,
         f"D0284 scale calibration drift: cal={scale_cal:#x} runtime={scale_runtime:#x}")
    scale_acc = accessors(0xFEBEB140, funcs)
    scale_writers = sorted(k for k, refs in scale_acc.items() if "WRITE" in refs)
    need(scale_writers == ["0xB3866", "0xB389C", "0xB38D2", "0xBF97A"],
         f"FEBEB140 writer census drift: {scale_writers}")
    token(0x3BDC6, funcs, "puVar4 = &LAB_0000569a;", "(&DAT_000317e0)[uVar1]",
          "*(short *)(&UNK_ffffb9f2 + (int)puVar2) = (short)puVar4;")
    token(0xB338C, funcs, "DAT_febeb112 = 0x5a;")
    token(0xB330A, funcs, "DAT_febeb112 = 0;")
    need(pair_map.get(0xFEBEAC2B) == 0xFEBEB112, "AC2B diagnostic snapshot drift")
    limit_table = [struct.unpack_from("<H", image, 0x317E0 + i * 2)[0] for i in range(16)]
    need(limit_table == [0x3A75, 0x3A75] + [0x2B4D] * 7 + [0x569A] * 7,
         f"FEBE71F2 limit table drift: {limit_table}")
    f71 = accessors(0xFEBE71F2, funcs)
    need("0x3BDC6" in f71 and "WRITE" in f71["0x3BDC6"], "FEBE71F2 runtime writer drift")

    baseline_writers = {
        "FEBECB38": "0xCF2B2", "FEBEC5EE": "0xC9A84", "FEBEC43C": "0xC7E36",
        "FEBEC4C0": "0xC8678", "FEBEC3BA": "0xC74AC", "FEBECC2C": "0xD0162",
        "FEBEBF3C": "0xC2B64", "FEBECBE8": "0xCFCD4",
    }
    for cell_name, writer in baseline_writers.items():
        acc = accessors(int(cell_name, 16), funcs)
        need(writer in acc and "WRITE" in acc[writer], f"{cell_name} runtime writer drift: {acc}")

    baseline_internal_path = {
        "D0218_sum": (
            "FEBECC48 baseline sum. Default diagnostic flag AC2B!=0x5A and B6 assist-active C7BF!=1: "
            "C43C + C4C0 + C3BA + CC2C + BF3C + clamp(CB38 + C5EE, +/-B132C/2) + CBE8. "
            "If AC2B==0x5A the diagnostic branch reduces to C4C0+C3BA+BF3C; if C7BF==1 "
            "the B6-active branch reduces to C4C0+BF3C."
        ),
        "D0284_scale_clamp": "FEBECC48 -> scaled by FEBEAC64/0x8000 -> clamp +/-ROM B1334 -> FEBECC4C",
        "D0284_scale_provenance": {
            "snapshot": "FEBEAC64 <- FEBEB140 via BCBD8",
            "calibration_u16_at_0x000AEF4C": f"0x{scale_cal:04X}",
            "runtime_derivation": f"FEBEB140 = floor(0x2774564E / 0x{scale_cal:04X}) = 0x{scale_runtime:04X} in B3866/B389C/B38D2",
            "reset_default": "BF97A writes FEBEB140=0x7637",
            "writer_census": scale_writers,
            "classification": "internal ROM/calibration-derived scale; no generated-COM/CAN value source",
        },
        "D02DA_filter": "FEBECC4C -> optional slew/filter state CC30/34/38/3C -> FEBECC4E",
        "D0382_limit": "FEBECC60 = clamp(FEBECC4E, +/-FEBEAC52); AC52 is a limit, not the source magnitude",
        "FEBEAC52_limit_provenance": (
            "BCBD8 <- FEBEEF8E <- FCC00 <- FEBE71F2. Runtime 0x3BDC6 selects the minimum "
            "active entry from ROM table 0x317E0 (0x2B4D/0x3A75/0x569A; default 0x569A) "
            "from an internal protected status mask and stores FEBE71F2."
        ),
        "AC2B_gate": "FEBEAC2B <- FEBEB112; B338C sets 0x5A through an internal API and B330A clears it",
        "C7BF_gate": "FEBEC7BF can activate only through CB73A when B6 sig261 snapshot FEBEADB0=='1'",
        "classification": (
            "B6-independent EPS-internal baseline-assist magnitude path. It explains how CC60/command torque "
            "can be nonzero with B6 absent; FEBE71F2 is only its saturation limit. This does not create a "
            "second generated-COM target ingress: the complete COM denominator remains separately closed."
        ),
        "direct_D0218_value_cells": ["FEBECB38", "FEBEC5EE", "FEBEC43C", "FEBEC4C0",
                                     "FEBEC3BA", "FEBECC2C", "FEBEBF3C", "FEBECBE8"],
        "direct_value_runtime_writers": baseline_writers,
        "limit_table": [f"0x{x:04X}" for x in limit_table],
    }

    # composition input provenance (statement-verified chains)
    comp_inputs = {
        "FEBECC50/FEBECC62 (command torque composition)": {
            "D039E": "FEBECC50 = clamp(sVar7*G1/0x100 + sVar4); sVar7 = FEBECC5A|FEBECC60 by FEBEAC28==1; "
                     "G1 = FEBEC7A0 (guard FEBEC7AA complement) via FUN_000CB9C8; "
                     "sVar4 = G2*FEBEC81A/0x100; G2 = FEBEC7BC via FUN_000CB9AE",
            "FEBEC81A": "CBA80 <- FEBEAE90 (B6 sig262 snapshot)",
            "FEBEAC5A": "BCBD8 <- FEBEB1F8 <- B4B6C/B4EF4 (internal mode state, no stage reads)",
            "FEBECC60": "D0382 <- dynamic FEBECC4E from D0218/D0284/D02DA, saturated to +/-FEBEAC52; AC52 <- FEBE71F2 is only the limit",
            "FEBECC5A": "D04AC mode-latch from FEBEAC10 <- FEBEAFA8 <- FUN_000C1BE4 <- FEBEAC68 (previous cycle echo)",
            "classification": "the only COM-derived VALUE inputs are B6 sig261 (mode via FEBEADB0) and B6 sig262 (magnitude via FEBEAE90); "
                              "gains are ROM-installed and internally adapted; a separate B6-independent EPS-internal baseline-assist path feeds FEBECC60",
        },
    }
    token(0xCBA80, funcs, "DAT_febeae90", "DAT_febec7dc")
    token(0xBCD66, funcs, "*(undefined2 *)(puVar15 + -0x9f4) = *(undefined2 *)(puVar15 + 0x696);")
    token(0xC1BE4, funcs, "DAT_febeafa8 = DAT_febeac68;")
    token(0xFCC00, funcs, "DAT_febeef8e = DAT_febe71f2;")
    token(0x57F00, funcs, "DAT_febeee02 = DAT_febe686c;", "DAT_febeee12 = DAT_febe8a24;")

    # ---- gain/selector machinery -----------------------------------------
    token(0xCB516, funcs, "*(short *)(puVar1 + 4000) = param_2;",
          "*(short *)(puVar1 + 0xfbc) = param_1;", "*(short *)(puVar1 + 0xfac) = -1 - param_1;",
          "*(short *)(puVar1 + 0xfaa) = -1 - param_2;")
    need(GP + 4000 == 0xFEBEC7A0 and GP + 0xFBC == 0xFEBEC7BC
         and GP + 0xFAC == 0xFEBEC7AC and GP + 0xFAA == 0xFEBEC7AA, "gain cell layout drift")
    token(0xCB82C, funcs, "DAT_febec7a2 = DAT_febec7a0 * (ushort)DAT_febec7b6;",
          "DAT_febec7a4 = DAT_febec7bc * (ushort)bVar3;")
    token(0xCB73A, funcs, "DAT_febec7bf == '\\0'", "(DAT_febeadb0 == '1')",
          "DAT_febeae02 < *(ushort *)((&PTR_DAT_000b1464)[DAT_febeac3c & 1] + 0x24)",
          "DAT_febec7b5 = 1;")
    # FEBEADB0 <- stage FEBEF130 (sig261) via 0xBCD66 pair
    need(pair_map.get(0xFEBEADB0) == 0xFEBEF130, "FEBEADB0 snapshot pair drift")
    need(dict(raw_stage).get(0xFEBE80BC) == 0xFEBEF130 or
         any(r == 0xFEBE80BC and w == 0xFEBEF130 for r, w in raw_stage),
         "sig261 raw->stage drift")
    sig261 = next(x for x in scalar if x["signal"] == 261)
    need(sig261["raw_cell"] == "0xFEBE80BC" and sig261["can_id"] == 0x0B6
         and sig261["bits"] == 6, "sig261 geometry drift")

    # ---- positive non-B6 cluster inputs -----------------------------------
    positive = [
        {
            "can_id": "0x090", "pdu": 40, "length": rx[40]["length"],
            "geometry": [
                {"signal": 227, "byte": 0, "bits": 1, "bit": 7},
                {"signal": 228, "byte": 0, "bits": 1, "bit": 6},
                {"signal": 229, "byte": 0, "bits": 10, "bit": 0, "transform": "s16(x-0x200) -> FEBE808A"},
                {"signal": 230, "byte": 2, "bits": 1, "bit": 7},
                {"signal": 231, "byte": 2, "bits": 1, "bit": 6},
                {"signal": 232, "byte": 2, "bits": 10, "bit": 0, "transform": "s16(x-0x200) -> FEBE808C"},
                {"signal": 233, "byte": 4, "bits": 1, "bit": 7},
                {"signal": 234, "byte": 4, "bits": 1, "bit": 6},
                {"signal": 235, "byte": 4, "bits": 10, "bit": 0, "transform": "s16(x-0x200) -> FEBE808E"},
                {"signal": 241, "byte": 28, "bits": 4, "bit": 4},
            ],
            "chains": [
                "sig232t*0x931/0x10 (FEBEF1C8) + sig229t branch -> 0xBE846 -> FEBEBE96 -> snapshot FEBEAE0C (0xBCD66)",
                "0xC310E integrator: FEBEBF58 += FEBEAE0C - FEBEBFA0; FEBEBFA0 = FEBEBF58*0x400/ROM_0AF564, gated by FEBEBFB1",
                "sig235t*0x3E77/0x100 (FEBEF1CA) -> 0xBEFD6 -> FEBEBF00 -> snapshot FEBEAF00 -> 0xC310E integrator FEBEBF54/FEBEBF80",
                "sig233|sig228|sig231 -> 0xBE80E -> FEBEBE8C/FEBEBE8D; 0xBEF9C -> FEBEBF4C/FEBEBF4D",
                "validity snapshots FEBEACE7/E8/DF/E0/E1 -> 0xC2F26 -> integrator-enable gate FEBEBFB1 (requires FEBEACC0==1, FEBEBF4B==0)",
                "0xC3C12/0xC3E44 plausibility aggregation -> FEBEC02C/FEBEC043/FEBEC045 flags",
            ],
            "consumers": ["0xBCD66", "0xBE80E", "0xBE846", "0xBEF9C", "0xBEFD6", "0xB93AA",
                          "0xC2F26", "0xC310E", "0xC3C12", "0xC3E44"],
            "classification": "observer/plausibility: 0x090-derived values are integrated and "
                              "cross-checked but never reach FEBECC50/FEBECC62/FEBEE400..418 as magnitudes",
        },
        {
            "can_id": "0x0D7", "pdu": 41, "length": rx[41]["length"],
            "geometry": [
                {"signal": 244, "byte": 0, "bits": 8, "bit": 0},
                {"signal": 246, "byte": 1, "bits": 16, "bit": 0, "signed": False},
                {"signal": 247, "byte": 3, "bits": 16, "bit": 0},
            ],
            "chains": [
                "sig246 u16 B1:B2 -> clamp(30000)*0x147B>>12 -> 0xBECF4 -> FEBEBEDE -> snapshot FEBEAE02 (0xBCD66)",
                "FEBEAE02 consumers: CB664 (B6 sig263 command-gate consumer), CB73A assist-activation speed threshold, "
                "CBD64, CD2A0, CD426, CD45C, CD590, CDE26, CDFF8 (sig270 percentage-contribution consumer), CE0AE, CE144, CE51C",
                "sig244 -> stage FEBEF095 -> qualification 0xB7728/0xBECD0 -> FEBEB37C 'Z' flag -> 0xBB7FA handler-branch select -> FEBEAF40",
                "FEBEAF40 -> snapshot FEBEAC4C (0xBCBD8) -> D042C -> FEBECC66/FEBECC68 -> FEBEAC76/FEBEAC7E -> FEBEE410/FEBEE414",
            ],
            "consumers": ["0xBECF4", "0xB7728", "0xBECD0", "0xBB7FA", "0xCB664", "0xCB73A",
                          "0xCDFF8", "0xD042C"],
            "classification": "speed-class gating and handler selection: sig246 bounds/qualifies command paths; "
                              "sig244 selects a handler pointer branch (FEBEAF40 stores a pointer, not a magnitude); "
                              "no FEBECC50/FEBECC62 magnitude contribution",
        },
        {
            "can_id": "0x675", "pdu": 33, "length": rx[33]["length"],
            "geometry": [{"signal": s, "byte": s - 177, "bits": 8, "bit": 0} for s in range(177, 183)],
            "chains": [
                "sigs177..182 -> decode FUN_000BE4A4 + range checks -> 0xBE4C2 -> FEBEBE66..FEBEBE6C (invalid = -1)",
                "FEBEBE66..6C readers: BA0C4, BDFAC, BE070 (diagnostic status builder), BE134, BE216, BE28E, BF3AA (telemetry)",
            ],
            "consumers": ["0xBE4C2", "0xBE070", "0xBF3AA", "0xBE134", "0xBE216", "0xBE28E"],
            "classification": "CAN-configured parameter/selector cells consumed by diagnostics, telemetry, "
                              "and plausibility family; no composition magnitude path recovered",
        },
        {
            "can_id": "0x13B", "pdu": 39, "length": rx[39]["length"],
            "geometry": [
                {"signal": 215, "byte": 0, "bits": 1, "bit": 7},
                {"signal": 219, "byte": 1, "bits": 6, "bit": 2},
                {"signal": 223, "byte": 3, "bits": 1, "bit": 7},
                {"signal": 224, "byte": 5, "bits": 1, "bit": 7},
            ],
            "chains": [
                "sig219 stages FEBEF04A/FEBEF04B/FEBEF0A2 -> 0xBCD66 snapshots; sig223 -> FEBEF091 -> snapshot (gate family)",
                "0xB7728 reads FEBEF094 = B6 signal 243 (staged at 0x58074) and FEBEF093 = FEBE80A5 "
                "(raw cell with no extractor anywhere in the corpus, structurally 0): the 0x0D7 "
                "sig244 qualifier FEBEB37C is invalidated by B6 sig243 != 0",
            ],
            "consumers": ["0xBCD66", "0xB93AA", "0xB7728"],
            "classification": "gate family whose 0x0D7-qualifier branch is B6-sig243-gated; no magnitude path",
        },
    ]
    # geometry pins
    for row in scalar:
        if row["signal"] == 246:
            need(row["byte_offset"] == 1 and row["bits"] == 16 and not row["signed"],
                 "sig246 geometry drift")
        if row["signal"] == 229:
            need(row["byte_offset"] == 0 and row["bits"] == 10, "sig229 geometry drift")

    # 0x090 transform stage pins (transform outputs are raw-region cells, not scalar dests)
    for raw, stage in ((0xFEBE808A, 0xFEBEF1C6), (0xFEBE808C, 0xFEBEF1C8), (0xFEBE808E, 0xFEBEF1CA)):
        need(any(r == raw and w == stage for r, w in stage_edges), f"transform stage pin drift {stage:08X}")
    token(0xBE846, funcs, "iVar8 = (DAT_febef1c6 * 0x931) / 0x10;",
          "local_2c[0] = (DAT_febef1c8 * 0x931) / 0x10;",
          "*(undefined2 *)(puVar10 + 0x696) = (undefined2)local_2c[0];")
    token(0xBEFD6, funcs, "puVar8 = (undefined *)((DAT_febef1c0 * 1999) / 0x100);",
          "puVar6 = (undefined *)((DAT_febef1ca * 0x3e77) / 0x100);",
          "*(undefined4 *)(puVar7 + 0x700) = local_18[0];")
    token(0xC310E, funcs, "DAT_febebf58 = (DAT_febebf58 + DAT_febeae0c) - (int)DAT_febebfa0;",
          "DAT_febebfa0 = (short)((DAT_febebf58 * 0x400) / (int)PTR_LAB_000af564);")
    token(0xC2F26, funcs, "DAT_febeace7 == '\\0'", "DAT_febeacc0 == '\\x01'",
          "DAT_febebfb1 = 0x5a;")
    token(0xBECF4, funcs, "FUN_000d1d5c(DAT_febef1b6,30000,auStack_6);",
          "*(short *)(puVar1 + 0x6de) = (short)((uint)auStack_6[0] * 0x147b >> 0xc);")
    need(GP + 0x6DE == 0xFEBEBEDE, "FEBEBEDE layout drift")
    need(pair_map.get(0xFEBEAE02) == 0xFEBEBEDE, "FEBEAE02 pair drift")
    need(any(r == 0xFEBE809A and w == 0xFEBEF1B6 for r, w in raw_stage), "sig246 stage drift")
    token(0xBB7FA, funcs, "((DAT_febeb11a & 0xff00) == 0x500)", "DAT_febeb37c == 'Z'",
          "*(short *)(puVar5 + -0x8c0) = (short)puVar6;")
    need(GP - 0x8C0 == 0xFEBEAF40, "FEBEAF40 layout drift")
    token(0xB7728, funcs, "DAT_febef093 != '\\0'", "DAT_febef094 != '\\0'")
    token(0xBE4C2, funcs, "uVar13 = FUN_000be4a4(DAT_febef0f1);", "puVar7[0x666] = (char)uVar13;")
    need(GP + 0x666 == 0xFEBEBE66, "FEBEBE66 layout drift")
    token(0xB49E4, funcs, "DAT_febeb1fa")  # qualification record family anchor

    # remaining stage readers -> qualification/telemetry only (bounded sweep)
    qual_readers = {
        "0xB34xx-B4Dxx": "per-signal qualification records into FEBEB1xx/FEBEB2xx/FEBEB4xx..B9xx "
                         "(values+flags consumed by 0xBCD66/0xBCD62/0xBCBD8 snapshots, 0xBF3AA telemetry, "
                         "0xBE070 diagnostic status)",
        "0xB93AA": "reads 14 stage cells (0x0AA wheel family 194-201, 0x13B, 0x116, 0x090, 0x0D7) "
                   "and writes only status cell FEBEB49E",
        "0xB95xx-B9Dxx/0xBA0xx": "sig246 (0x0D7) statistics/records into FEBEB4A3/7xx/Bxx family; "
                                  "0xD8 sigs 251-254 and 0x64F sig257 qualification records",
    }

    # ---- live-context intersection (from retained drives, no new I/O) -----
    live = json.loads((REPO / "data/generated/camry_8965F3307000_external_lateral_ingress.json").read_text())
    need(live["conclusion"]["b6"].startswith("Protected 0x0B6"), "prior ingress artifact drift")
    b6_absent = live["live_intersection"]["selected_counts"]["0x0B6/32"]
    need(sum(b6_absent.values()) == 0, "B6 unexpectedly present in retained drives")

    return {
        "schema": "camry-8965f3307000-command-cone-ingress-v2",
        "target": {"software_id": "8965F3307000", "codeflash_sha256": IMAGE_SHA256,
                   "corpus_function_count": len(funcs)},
        "cluster": {"range": [f"0x{CLUSTER_LO:05X}", f"0x{CLUSTER_HI:05X}"],
                    "command_cone": ["FEBECC50", "FEBECC62", "FEBEAC56", "FEBEAC5A",
                                     "FEBEE400..FEBEE418", "FEBE6768..FEBE6794", "FEBE6772",
                                     "FEBE7C58"]},
        "ingress_denominator": {
            "literal_scalar_extracts": len(scalar),
            "table_driven_extracts": len(indirect),
            "table_driven": indirect,
            "transform_helpers": transforms,
            "extract_api_geometry": {
                "frame_block_base": f"0x{FRAME_BASE:08X}",
                "pdu_status_base": f"0x{STATUS_BASE:08X}",
                "new_data_bit": "0x80 of status byte; extractor returns 0x20 when set",
            },
        },
        "pipeline": {
            "L1_raw_cells": {"count": 116, "span": "0xFEBE7FF0..0xFEBE80D6 (+0xFEBE80A0 stack-RMW via 0x4BB62)",
                              "signal243_path": "0x4BB62 auStack_9 -> FEBE80A0"},
            "L2_stage": {"copier": "0x00058074", "raw_cells_staged": 98, "edges": 105,
                          "init_only_stage_cells": {f"0x{c:08X}": v for c, v in sorted(INIT_ONLY_STAGE_CELLS.items())},
                          "init_only_evidence": "no writer besides 0x58074 constants and 0x59448 zero-init exists in the corpus"},
            "L3_qualification": qual_readers,
            "L3_stage_reader_census": stage_reader_census,
            "L2_unstaged_raw_closure": {
                "unstaged_count": 18,
                "evidence": "each unstaged raw cell is accessed only by its own unpacker, "
                            "the stage copier, and write-only initializer 0x58C9A; no consumer exists",
            },
            "group_api_callers": ["0x693FE", "0x697F4"],
            "L4_snapshot_copiers": {k: {"exact_pairs": v} for k, v in copiers.items()},
            "L4_unique_snapshot_destinations": len(pair_map),
        },
        "command_block_map": {
            "writer": "0x000BF33E",
            "bytes": block_map,
            "via_D0AAE": {"FEBEAC54": "FEBECC64", "FEBEAC56": "FEBECC62 (command torque)",
                          "FEBEAC58": "FEBEC128", "FEBEAC68": "FEBECC60", "FEBEAC70": "FEBEC172",
                          "FEBEAC76": "FEBECC66", "FEBEAC7E": "FEBECC68",
                          "FEBEAC2D": "0x5A iff FEBECC98 != 0", "FEBEAC39": "0", "FEBEAC3E": "0"},
        },
        "composition_provenance": comp_inputs,
        "gain_selector_machinery": {
            "install": "0x000CB516(param1,param2): FEBEC7BC/FEBEC7A0 = params; FEBEC7AC/FEBEC7AA = complements",
            "init": "0x000CB548: FEBEC7A2/A4 = ROM 0xB04C4*0xB04CD / 0xB04D4*0xB04D0 products",
            "adapt": "0x000CB82C: mode FEBEC7BA/FEBEC7B5 (1/2/3 -> ROM 0xB04CC..0xB04D1 bases) migrate "
                     "FEBEC7A0/FEBEC7BC toward FEBEC7A2/A4 within ROM 0xB04C2..0xB04D4 bounds; "
                     "0x000CB9E2 re-clamps deviations",
            "activation": "0x000CB73A: assist-active FEBEC7BF=1 requires FEBEC7B4==1, FEBEC7BE==0, "
                          "FEBEC795==1, FEBEC7B3==0, FEBEADB0=='1' (B6 sig261 snapshot), and "
                          "FEBEAE02 (sig246-derived speed class) < ROM threshold row [FEBEAC3C & 1]",
            "deactivation": "FEBEC7B5 = 3 on condition loss, 2 otherwise",
            "effect_on_command": "FEBECC50 = clamp(sVar7*G1 + sVar4) with G1/G2 the guarded gains; "
                                 "gain adaptation cannot activate while B6 sig261 is absent",
        },
        "positive_non_b6_cluster_inputs": positive,
        "baseline_internal_assist_path": baseline_internal_path,
        "non_com_internal_mirrors": {
            "0x000FCC00": {"FEBEEF8E": "FEBE71F2", "FEBEEF80": "FEBE7BBC", "FEBEEF81": "FEBE686C",
                            "FEBEEF88": "FEBE71EC", "FEBEEF8A": "FEBE7DA6", "FEBEEF8C": "FEBE7DA8",
                            "FEBEEF90": "FEBE8B28", "FEBEEF82": "FEBE7567", "FEBEEF83": "FEBE7568"},
            "0x00057F00": {"FEBEEE00": "FEBE7BBC", "FEBEEE02": "FEBE686C", "FEBEEE12": "FEBE8A24",
                            "FEBEEE1C": "FEBE7DB0", "FEBEEE26": "FEBE71F2"},
            "into_cone": "FEBE71F2 -> FCC00/FEBEEF8E -> BCBD8/FEBEAC52 -> D0382 saturation limit on dynamic FEBECC4E; "
                         "FEBEAC04/FEBEAC06 gates (D04AC mode-latch) <- FEBEEE02/FEBEEE12",
            "classification": "internal mirror/configuration class outside generated-COM; FEBE71F2 is a ROM-selected limit, not command magnitude",
        },
        "class_l_relevance": {
            "0x090": "the previously unresolved live 0x090 correlation now has a firmware path: "
                     "0x090-derived values are integrated observers (FEBEBFA0/FEBEBF80) whose plausibility "
                     "flags (FEBEC02C/FEBEC043/FEBEC045) and validity gates (FEBEBFB0..FB2) qualify other "
                     "paths; no 0x090 value is a command magnitude",
            "mode_without_b6": "no non-B6 COM signal can raise assist-active FEBEC7BF "
                               "(activation is B6-sig261-gated at 0xCB73A); Class-L mode change with B6=0 "
                               "must therefore arise from the B6-independent internal baseline-assist path, "
                               "other internal state machinery, or driver/feedback dynamics rather than another COM target",
        },
        "live_context": {
            "b6_frames_in_retained_drives": sum(b6_absent.values()),
            "note": "retained-drive intersection re-read from camry_8965F3307000_external_lateral_ingress.json; no new vehicle I/O",
        },
        "census_supersession": {
            "prior": "VAR-065 pinned copy-edge census: 19/116 nonempty, 97 empty",
            "finding": "the 19-signal set was an artifact of requiring a fixed raw->stage->snapshot "
                       "triple with pre-listed consumers; the complete pipeline stages 98/116 raw cells "
                       "and 6 copiers fill 306 unique snapshot destinations",
            "preserved": "the VAR-065 headline survives and is strengthened: at composition level the only "
                         "COM-derived VALUE inputs to FEBECC50/FEBECC62 are still B6 sig261 (mode) and "
                         "B6 sig262 (magnitude); every other non-B6 member is a gate, qualifier, observer, "
                         "or telemetry input",
            "correction": "docs/status/CORRECTIONS.md CORR entry: the '97 empty' framing is superseded",
        },
        "boundary": [
            "statement-level closure: 0xBF97A holds WRITE refs into FEBEE400..418 whose stores the "
            "decompiler elides; 0xBF33E is the statement-verified block writer and BF97A's block refs "
            "are treated as a second (runtime/reset) writer with unchanged sourcing",
            "FEBEACC0 (0xC2F26 integrator-enable input) is computed inside 0xBCD66 rather than copied; "
            "its exact inputs remain bounded",
            "FEBEB3FC/FEBEB3FE/FEBEB400/FEBEB354 (command block bytes 406/407/416/418) come from "
            "0xB7xxx/0xB8xxx internal qualification not traced byte-exhaustively here",
            "no live vehicle I/O was performed; live context is re-read from retained artifacts",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    obj = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")
    print(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
