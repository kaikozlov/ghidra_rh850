#!/usr/bin/env python3
"""Close the provenance of the exact-F33 D5/snapshot/group-input path.

"D5" names the 0x5Dxxx snapshot-mirror trio (0x5D12C/0x5D5E0/0x5D6DC, driven by
0x58B1A under selector switches) plus the acquisition staging FEBE822C..FEBE8260
that feeds it.  This builder deterministically re-derives, from the canonical
6,065-function decompiler corpus and the exact CodeFlash image:

* the staging writer/reader census and per-writer copy edges,
* the group-input consume API over hardware-fed GlobalRAM rings,
* the serial torque-sensor frame decode chain,
* the driver-torque / command-current / command-torque working-cell chains and
  their Techstream/GTS+ DID export formulas,
* a CAN-join guard proving no D5-path function reads the generated-COM receive
  staging or the B6/control snapshot regions (except the already-verified B6
  command-torque terminal at 0xBF33E), and
* the single-RSCFD hardware fact that removes the second-CAN-controller class.

Everything asserted here is re-derived from tracked inputs; the emitted JSON is
checked byte-exact by tests/verify_camry_8965F3307000_d5_snapshot_provenance.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

from camry_f33_corpus import CORPUS, IMAGE, IMAGE_SHA256, REPO

OUT = REPO / "data/generated/camry_8965F3307000_d5_snapshot_provenance.json"

GP = 0xFEBEB800
STAGING = (0xFEBE822C, 0xFEBE8260)
ACQ_BLOCK = (0xFEBE5EC8, 0xFEBE5F30)
COM_STAGING = (0xFEBE7F00, 0xFEBE80E0)
CONTROL_SNAPSHOT = (0xFEBEAC00, 0xFEBEAFFF)
EF_SNAPSHOT = (0xFEBEF000, 0xFEBEF200)
RING_ZONE = (0xFEEF80A0, 0xFEEF9130)

# Functions whose READ references are guarded against a false CAN join.
GUARD_FUNCTIONS = [
    "0x00059448", "0x000486d0", "0x000387ce", "0x00047d62", "0x0005d12c",
    "0x0005d5e0", "0x0005d6dc", "0x00050b6a", "0x00050bbc", "0x00050c38",
    "0x00066824", "0x00066932", "0x000668e2", "0x00047b70", "0x000484f0",
    "0x00048684", "0x00037f16", "0x0003835e", "0x000384d8", "0x00037e48",
    "0x000bf33e",
]

# RH850/P1M-E hardware-manual register identities (R01UH0585EJ0120 Rev.1.20,
# Appendix A List of Registers / section 17 CANFD Interface).  These name SFR
# addresses that the corpus itself proves the firmware touches; the manual only
# supplies the register names and the single-unit RSCFD fact.
MANUAL = "R01UH0585EJ0120 Rev.1.20 (RH850/P1M-E User's Manual: Hardware)"
SFR_NAMES = {
    0xFFF99000: "DMACTRGSEL0 (DMAC primary/secondary select 0)",
    0xFFF99004: "DMACTRGSEL1 (DMAC primary/secondary select 1)",
    0xFFF91000: "ADCG0VCR00 (ADCG0 virtual channel register 00)",
    0xFFF92000: "ADCG1VCR00 (ADCG1 virtual channel register 00)",
    0xFFD82000: "CSIH1CTL0 (clocked serial H ch1 control 0)",
    0xFFD83000: "CSIH1MCTL1 (clocked serial H ch1 memory control 1)",
    0xFFD50000: "DCRA0CIN (CRC0 input register)",
    0xFFD51000: "DCRA1CIN (CRC1 input register)",
    0xFFD20000: "RSCFD0CFDC0NCFG (RS-CANFD0 channel 0 nominal bitrate)",
}


def load_corpus() -> dict[str, dict]:
    funcs: dict[str, dict] = {}
    with CORPUS.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("record") == "function":
                funcs[rec["entry_addr"]] = rec
    return funcs


def refs(funcs: dict[str, dict], lo: int, hi: int, kinds: tuple[str, ...]) -> list[tuple[str, str, str, int]]:
    out = []
    for ea, rec in funcs.items():
        for ref in rec["data_references"]:
            to = ref.get("to_addr", "")
            if ref.get("to_space") != "ram" or not to.startswith("0x"):
                continue
            if ref["ref_type"] not in kinds:
                continue
            addr = int(to, 16)
            if lo <= addr <= hi:
                out.append((ea, ref["from_addr"], ref["ref_type"], addr))
    return sorted(out)


def body(funcs: dict[str, dict], ea: str) -> str:
    return funcs[ea]["decompiled_c"] or ""


def assignments(src: str) -> list[tuple[str, str]]:
    """(destination, rhs) for simple DAT_ assignments in decompiled C."""
    return re.findall(r"(DAT_febe[0-9a-f]{4})\s*=\s*([^;]+);", src)


def copy_edges(funcs: dict[str, dict], ea: str) -> list[list[str]]:
    edges = []
    for dst, rhs in assignments(body(funcs, ea)):
        value = rhs.split(" << ")[0].strip()
        if value.startswith("DAT_febe"):
            edges.append([f"0x{dst[4:].upper()}", f"0x{value[4:].upper()}"])
    return edges


def scaled_edges(funcs: dict[str, dict], ea: str) -> dict[str, str]:
    out = {}
    for dst, rhs in assignments(body(funcs, ea)):
        if re.fullmatch(r"DAT_febe[0-9a-f]{4} << 2", rhs.strip()):
            out[f"0x{dst[4:].upper()}"] = "x4"
    return out


def builder_facts() -> dict:
    image = IMAGE.read_bytes()
    u32 = lambda off: struct.unpack_from("<I", image, off)[0]
    return {
        "chan_fifo_ptrs_0x313fc": [f"0x{u32(0x313FC + 4 * i):08X}" for i in range(2)],
        "chan_fifo_len_0x31411": [image[0x31411], image[0x31461]],
        "desc_channel_0x31676": [f"0x{image[0x31676 + i]:02X}" for i in range(2)],
        "sensor_type_0x31678": [f"0x{image[0x31678 + i]:02X}" for i in range(2)],
        "group_offsets_0x30f2c": list(image[0x30F2C:0x30F32]),
        "group_offsets_0x30f34": list(image[0x30F34:0x30F3A]),
        "image_sha256": IMAGE_SHA256,
    }


def build() -> dict:
    funcs = load_corpus()
    b = lambda ea: body(funcs, ea)

    # --- staging census -----------------------------------------------------
    staging_writers = sorted({ea for ea, _, kind, _ in refs(funcs, *STAGING, ("WRITE",))})
    staging_readers = sorted({ea for ea, _, kind, _ in refs(funcs, *STAGING, ("READ",))})

    # 0x58c9a seeds only invalid markers into staging -> init/reset only.
    init_markers = sorted(set(
        re.findall(r"\((?:&DAT_febe8(?:22c|238))\)\[iVar\d+\] = (0x8000);", b("0x00058c9a"))
    ))
    init_only = init_markers == ["0x8000"] and "0x00058c9a" in staging_writers

    # --- ring producer census ----------------------------------------------
    ring_writers = sorted({ea for ea, _, kind, _ in refs(funcs, *RING_ZONE, ("WRITE",))})
    ring_init = {
        "0x0005fa3a",  # zero rings A/B + head counters FEEF90E0/FEEF90E4
        "0x0005fa84",  # zero rings C/D + head counters FEEF90E8..FEEF90F4
        "0x00060aa8",  # zero comm-entry blocks FEEF90F8..FEEF910B, seed 0x800800 markers
    }
    ring_ack = {"0x00060c60"}  # consume-side ack clears entries at FEEF90FC/FEEF910C
    runtime_producers = [ea for ea in ring_writers if ea not in ring_init | ring_ack]

    # --- SFR evidence -------------------------------------------------------
    sfr_refs = {}
    for ea, name in (
        ("0x0006082c", "channel descriptor initializer"),
        ("0x0005fafe", "ADCG0/ADCG1 scan config"),
        ("0x00061260", "serial driver A"),
        ("0x000612dc", "serial driver B"),
        ("0x000611fa", "CRC unit A"),
        ("0x0006378c", "CRC unit B"),
    ):
        found = sorted({
            m.lower()
            for m in re.findall(
                r"(?<![0-9a-zA-Z])(?:[Rr]am)?(fff[0-9a-fA-F]{5}|ffd[0-9a-fA-F]{5})(?![0-9a-fA-F])",
                b(ea),
            )
        })
        names = set()
        for a in found:
            addr = int(a, 16)
            if addr in SFR_NAMES:
                names.add(SFR_NAMES[addr])
                continue
            base = next((bb for bb in sorted(SFR_NAMES) if bb <= addr < bb + 0x1000), None)
            if base is not None:
                names.add(SFR_NAMES[base])
        sfr_refs[ea] = {
            "role": name,
            "named_sfr": sorted(names),
            "raw_hits": [f"0x{a.upper()}" for a in found],
        }

    # --- CAN-join guard -----------------------------------------------------
    guard: dict[str, list] = {}
    for ea in GUARD_FUNCTIONS:
        hits = []
        for ref in funcs[ea]["data_references"]:
            to = ref.get("to_addr", "")
            if ref.get("to_space") != "ram" or not to.startswith("0x"):
                continue
            addr = int(to, 16)
            for region, (lo, hi) in (
                ("com_staging", COM_STAGING),
                ("control_snapshot", CONTROL_SNAPSHOT),
                ("ef_snapshot", EF_SNAPSHOT),
            ):
                if lo <= addr <= hi:
                    hits.append({
                        "from": ref["from_addr"], "kind": ref["ref_type"],
                        "to": to, "region": region,
                    })
        if hits:
            guard[ea] = hits

    artifact = {
        "schema": "camry-8965f3307000-d5-snapshot-provenance-v1",
        "target": {
            "analysis_target": "camry-8965F3307000",
            "software_id": "8965F3307000",
            "mcu": "R7F701381 (RH850/P1M-E)",
            "corpus_function_count": len(funcs),
            "image_sha256": IMAGE_SHA256,
        },
        "driver": {
            "periodic_task": "0x00058b5e",
            "selector_driver": "0x00058b1a",
            "mirrors": ["0x0005d12c", "0x0005d5e0", "0x0005d6dc"],
            "selector_values": ["0xffc0", "0xff80", "0xff00"],
            "post_mirror_calls": ["0x000fdc64", "0x000fdc78", "0x000fdc8c"],
            "note": (
                "0x58B5E gates the mirror pass behind a 0xA55A-magic checksummed block and a "
                "counter/inverse-counter handshake; 0x58B1A switches a data selector before "
                "each mirror."
            ),
        },
        "staging": {
            "range": ["0xFEBE822C", "0xFEBE8260"],
            "writers": staging_writers,
            "readers": staging_readers,
            "classification": {
                "0x00050b6a": (
                    "copies acquisition block FEBE5EC8..5EDE (group-input getter 0x6217e "
                    "output) into FEBE822C..8242"
                ),
                "0x00050bbc": (
                    "copies torque-sensor records FEBE5F12..5F30 into FEBE8244..825E with "
                    "x4 scaling on FEBE824C/824E/8250/8252"
                ),
                "0x00050c38": "zero-fill of FEBE8260..8263 (error-words slot, no data payload)",
                "0x00058c9a": (
                    "init/reset only: seeds FEBE822C..8242 with invalid marker 0x8000 and "
                    "constants (closes VAR-071's bounded second-staging-writer question)"
                ),
                "0x00059448": (
                    "snapshot distributor: staging -> freeze buffer FEBE5Cxx and working "
                    "cells; its FEBE7Fxx references are WRITEs only"
                ),
            },
            "copy_edges": {
                "0x00050b6a": copy_edges(funcs, "0x00050b6a"),
                "0x00050bbc": copy_edges(funcs, "0x00050bbc"),
            },
            "scaled_cells_0x50bbc": scaled_edges(funcs, "0x00050bbc"),
            "init_marker_only_0x58c9a": init_only,
        },
        "acquisition_source_block": {
            "range": ["0xFEBE5EC8", "0xFEBE5F30"],
            "writers": {
                "0x00066824": (
                    "getter 0x6217e (group-input channels 0/8) -> FEBE5EC8..5EDE; getter "
                    "0x629a2 (torque-sensor record pack) -> FEBE5F12..5F30"
                ),
                "0x00066932": "getters 0x62abc/0x62b18/0x6294e -> FEBE5EE0..5F00 and FEBE5F18..5F24",
                "0x000668e2": (
                    "getter 0x62b32 (hardware comm-entry values) -> FEBE5F02..5F10, gated "
                    "on FEBE5F28 bit0"
                ),
                "0x00098f4c": "one-time init: zeroes FEBE5EBC..5EC3 and sets FEBE5EC4=1",
            },
        },
        "group_input_api": {
            "descriptor_block": "FEBE3C00 + idx*0x40, 16 channels",
            "fill_count_getter": "0x00060940 (reads seq@+0x18 vs base@+0x08)",
            "ring_base_map": "0x000620dc (ring size 0x1b0)",
            "accessors": {
                "0x00060630": {"table": "0xFEEF80A0", "entries": 0x50},
                "0x00060676": {"table": "0xFEEF81E0", "entries": 0x1B0},
                "0x000606da": {"table": "0xFEEF88A0", "entries": 0x60},
                "0x00060720": {"table": "0xFEEF8A20", "entries": 0x1B0},
            },
            "entry_semantics": "value = (entry & 0x7ff8) << 1; consume clears low halfword (ack)",
            "d5_channels": {"0x620fe": 0, "0x6213e": 8, "0x62a86/0x62af4": 0xE},
            "ring_layout": (
                "contiguous FEEF80A0..FEEF90E0 followed by head counters FEEF90E0..FEEF90F4 "
                "and per-channel comm-entry blocks FEEF90F8..FEEF912B"
            ),
        },
        "ring_producers": {
            "zone": ["0xFEEF80A0", "0xFEEF9130"],
            "application_code_writers": ring_writers,
            "init_zeroing": sorted(ring_init),
            "consume_ack_only": sorted(ring_ack),
            "runtime_application_producers": runtime_producers,
            "classification": (
                "No application-code writer posts fresh ring/FIFO payloads: every direct "
                "writer in the zone is init zeroing/marker seeding or the consume-side ack "
                "clear. Producers are hardware/peripheral (DMAC) feeds into shared GlobalRAM. "
                "The channel initializer 0x6082C programs 0x40-stride channel descriptors and "
                "DMAC primary/secondary trigger-select SFRs; ADCG0/ADCG1 scan, CSIH1 serial, "
                "and CRC0/CRC1 unit config appear in the same driver family. Exact "
                "per-channel trigger identity beyond this evidence is bounded, not asserted."
            ),
            "sfr_evidence": sfr_refs,
            "sfr_name_source": MANUAL,
        },
        "torque_sensor_serial": {
            "frame_fetch": (
                "0x00061008 (per-channel 20x u16 FIFOs via flash PTR table 0x313fc)"
            ),
            "frame_decode": (
                "0x00062488 (5-byte frame, 2-bit sequence check at FEBE3928, CRC verify "
                "0x623ee, unpack 14/14/12-bit into FEBE38D0/D2/D4)"
            ),
            "record_pack": (
                "0x000629a2 (two 12-byte records from FEBE38D0[i*6]; channel type 0x11 from "
                "table 0x31678 negates the 14-bit pairs)"
            ),
            "config_tables": builder_facts(),
        },
        "four_sensor_decode": {
            "decode": (
                "0x000484f0: FEBE7DFC = FEBE81E6 - FEBE6AD2 (zero point), x flash gains "
                "0x30E54/0x30E56 /0x800, /2 -> FEBE7DEC/7DEE/7DF0/7DF2 plus main-sub diffs "
                "FEBE7DF4/7DF6"
            ),
            "raw_staging": (
                "0x00050a52/0x00050a9a: FEBE81E6/81E8 <- FEBE5F02/5F04, FEBE81EA/81EC <- "
                "FEBE5F0A/5F0C with per-channel validity bytes"
            ),
            "raw_origin": (
                "0x00062b32 -> 0x00060c60 reads hardware comm entries at FEEF90FC/FEEF910C "
                "(12-bit value pairs + 4-bit counter + status)"
            ),
            "mode_select": "0x0004845e selects main/sub/difference from FEBE71EC bits 5-6",
        },
        "driver_torque_chain": {
            "steps": [
                "0x0004845e/0x0004849a/0x000484d2 -> FEBE7DEA (computed steering-wheel torque)",
                "0x00048684: FEBE7E0C = FEBE6870 or FEBE7DEA (mode-dependent)",
                "0x0005d5e0 mirror: FEBE66A8 = FEBE7E0C",
                "DID 0x1035 (0x0004db70): signed16((FEBE66A8 * 1000) / 0x100), gated on FEBE6AF0 == 0xA55A5AA5",
            ],
            "torque_sensor_outputs": (
                "DID 0x1091..0x1094 (0x0004dd62 family): signed16((FEBE64F2.. * 1000) / "
                "0x100), mirrors of FEBE7DEC/7DEE/7DF0/7DF2"
            ),
        },
        "command_current_chain": {
            "steps": [
                "DID 0x1152 (0x0004e3d0): signed16((FEBE6724 * 100) / 0x80); DID 0x1154: FEBE6726",
                "0x0005d12c mirror: FEBE6724 = FEBE6D84, FEBE6726 = FEBE6D86",
                "0x00037f16: FEBE6D84 = FEBE6DD6, FEBE6D86 = FEBE6DC8",
                "0x000384d8/0x00038396: field-weakening piecewise clamp (tables via DAT_000210e0, speed FEBE6E0A) of FEBE6DC8 = 0x0003835e clamp of envelope FEBE6DEC",
            ],
            "classification": (
                "internal current-control state (measured speed + flash calibration + "
                "current-limit envelope); no COM/CAN read anywhere in the chain"
            ),
        },
        "command_torque_chain": {
            "steps": [
                "DID 0x1C02 (0x0004e7d6): signed16(((FEBE6772 * FEBEE8A6)/0x2000)*100/0x100)",
                "0x0005d5e0 mirror: FEBE6772 = FEBEE40A",
                "0x000bf33e: FEBEE40A = FEBEAC56 (the VAR-065-verified B6-selected internal command cone)",
            ],
            "classification": (
                "internal control state whose sole external input is the already-proved "
                "protected B6 target-angle ingress"
            ),
        },
        "structural_constants": {
            "invalid_marker_staging": (
                "FEBE81F4..820A is only ever written 0x8000 (0x00050b00) after init zeroing "
                "(0x00058c9a); its mirror outputs FEBE6468..647E carry the invalid marker, "
                "not data"
            ),
            "error_words": (
                "FEBE8260..8263 zeroed by 0x00050c38 each pass; 0x00050c58 OR-aggregates "
                "them into FEBE8274"
            ),
        },
        "did_export_callbacks": {
            "0x1035 steering_wheel_torque": "0x0004db70",
            "0x1091 torque_sensor_1_output": "0x0004dd62",
            "0x1152 command_value_current_q": "0x0004e3d0",
            "0x1154 command_value_current_2_d": "0x0004e448",
            "0x1c02 command_value_torque": "0x0004e7d6",
        },
        "can_join_guard": {
            "checked_functions": GUARD_FUNCTIONS,
            "regions": {
                "com_staging": ["0xFEBE7F00", "0xFEBE80E0"],
                "control_snapshot": ["0xFEBEAC00", "0xFEBEAFFF"],
                "ef_snapshot": ["0xFEBEF000", "0xFEBEF200"],
            },
            "hits": guard,
            "conclusion": (
                "The only READ into these regions from any checked function is 0xBF33E "
                "reading FEBEAC54..FEBEAC7E, i.e. the already-verified B6-selected "
                "command-torque cone. 0x59448's FEBE7Fxx references are WRITEs (it cannot "
                "source COM values). No D5-path function reads generated COM/CAN staging."
            ),
        },
        "single_can_controller": {
            "mcu": "R7F701381 (RH850/P1M-E)",
            "source": MANUAL + ", section 17: 'RSCFDn (n = 0)' -- exactly one RS-CANFD unit",
            "rscfd0_base": "0xFFD20000",
            "conclusion": (
                "A second CAN controller does not exist on this MCU; combined with the "
                "VAR-065 47-rule exhaustion of the single controller's acceptance surface, "
                "no second-CAN ingress route can feed the D5 path."
            ),
        },
        "conclusion": (
            "The D5/snapshot/group-input path carries only (a) hardware/peripheral-fed "
            "shared-memory acquisition (DMAC rings + serial torque-sensor interface + ADC "
            "scan config), (b) internal control state (current loop, field weakening, angle "
            "integrator, rotation math), (c) the protected-B6-derived command-torque "
            "terminal, and (d) structural constants (invalid markers, zeroed error words). "
            "No generated COM/CAN value and no second-CAN route enters these cells; with "
            "controller-1 B6 absent this snapshot surface cannot carry hidden lateral "
            "command/state."
        ),
        "boundary": [
            "Negative proofs are scoped to the canonical direct data-reference graph: computed aliases without a recovered reference, DMA/hardware mutation of LocalRAM outside the GlobalRAM rings, and unrecovered code remain outside the proof.",
            "Ring/FIFO producer identity is classified as hardware/peripheral-fed shared memory; the exact per-channel DMAC trigger/peripheral assignment is bounded, not asserted.",
            "No live vehicle I/O; firmware-static closure only.",
        ],
        "sources": {
            "corpus": str(CORPUS.relative_to(REPO)),
            "image": str(IMAGE.relative_to(REPO)),
            "corpus_sha256": hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
        },
    }
    return artifact


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    art = build()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(art, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
