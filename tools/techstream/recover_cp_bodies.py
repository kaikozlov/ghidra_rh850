#!/usr/bin/env python3
"""Recover clean PE bodies from a current GTS+ CP stub/sidecar corpus."""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pefile

from techstream_paths import REPO, resolve_gts_root

DEFAULT_OUTPUT = REPO / "build/out/cuwplus-unprotected"
DEFAULT_AUX_OUTPUT = REPO / "build/out/gts-aux-unprotected"
DECODER = Path(__file__).with_name("cp_body_decode.py")


def _u16(data: bytes | bytearray, off: int) -> int:
    return struct.unpack_from("<H", data, off)[0]


def _u32(data: bytes | bytearray, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]


def _p16(data: bytearray, off: int, value: int) -> None:
    struct.pack_into("<H", data, off, value & 0xFFFF)


def _p32(data: bytearray, off: int, value: int) -> None:
    struct.pack_into("<I", data, off, value & 0xFFFFFFFF)


def _align(value: int, alignment: int) -> int:
    return (value + alignment - 1) & ~(alignment - 1)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _stem(path: Path) -> str:
    return path.name.replace(".", "_")


def _protected_source(gts_root: Path, explicit: Path | None) -> Path:
    if explicit:
        root = explicit.expanduser().resolve()
    else:
        root = (gts_root.parent / "CUWPlus").resolve()
    if not root.is_dir():
        raise SystemExit(f"protected CP source not found: {root}")
    return root


def _is_managed(stub: Path) -> bool:
    data = stub.read_bytes()
    pe = _u32(data, 0x3C)
    opt = pe + 24
    return bool(_u32(data, opt + 96 + 14 * 8))


def _native_build(stub: Path, meta_path: Path, memory_path: Path, out_path: Path) -> dict[str, Any]:
    stub_data = stub.read_bytes()
    meta = json.loads(meta_path.read_text())
    mem = bytearray(memory_path.read_bytes())
    if not meta.get("protector_success") or not meta.get("entrypoint_rva"):
        raise RuntimeError(f"incomplete native decode metadata for {stub.name}")

    peoff = _u32(stub_data, 0x3C)
    nsec = _u16(stub_data, peoff + 6)
    optsz = _u16(stub_data, peoff + 20)
    opt = peoff + 24
    sec0 = opt + optsz
    image_base = _u32(stub_data, opt + 28)
    sec_align = _u32(stub_data, opt + 32)
    clr_dir = (_u32(mem, opt + 96 + 14 * 8), _u32(mem, opt + 100 + 14 * 8))

    protected_sections: dict[str, dict[str, int]] = {}
    for index in range(nsec):
        off = sec0 + 40 * index
        name = stub_data[off : off + 8].split(b"\0", 1)[0].decode("ascii", "replace")
        vs, va, rs, rp = struct.unpack_from("<IIII", stub_data, off + 8)
        protected_sections[name] = {"vs": vs, "va": va, "rs": rs, "rp": rp, "ch": _u32(stub_data, off + 36)}

    calls = [(int(rva), int(size), int(prot)) for rva, size, prot in meta["protect_calls"] if int(rva)]
    if len(calls) == 5:
        names = [".text", ".rdata", ".data", ".rsrc", ".reloc"]
    elif len(calls) == 7:
        names = [".text", ".rdata", ".data", ".idata", ".00cfg", ".rsrc", ".reloc"]
    else:
        raise RuntimeError(f"unexpected native restored-range count for {stub.name}: {calls}")

    default_chars = {
        ".text": 0x60000020,
        ".rdata": 0x40000040,
        ".data": 0xC0000040,
        ".rsrc": 0x40000040,
        ".reloc": 0x42000040,
    }
    sections: list[dict[str, int | str]] = []
    for name, (va, vs, prot) in zip(names, calls):
        old = protected_sections.get(name, {})
        sections.append({
            "name": name,
            "va": va,
            "vs": vs,
            "prot": prot,
            "ch": int(old["ch"] if "ch" in old else default_chars.get(name, 0x40000040)),
        })
    if int(sections[0]["va"]) != 0x1000:
        raise RuntimeError(f"unexpected restored .text RVA for {stub.name}: {sections[0]}")

    groups: list[dict[str, Any]] = []
    for record0 in meta["imports"]:
        record = dict(record0)
        if not groups or groups[-1]["dll"].lower() != record["dll"].lower():
            groups.append({"dll": record["dll"], "dll_ptr_rva": record["dll_ptr_rva"], "imports": []})
        groups[-1]["imports"].append(record)

    rdata = next((item for item in sections if item["name"] == ".rdata"), None)
    if groups and rdata is None:
        raise RuntimeError(f"imports recovered without .rdata for {stub.name}")

    for group in groups:
        dll_ptr = int(group["dll_ptr_rva"])
        dll_bytes = group["dll"].encode("ascii")
        mem[dll_ptr : dll_ptr + len(dll_bytes) + 1] = dll_bytes + b"\0"
        values: list[int] = []
        iats: list[int] = []
        for record in group["imports"]:
            name = record["name"]
            name_ptr = int(record["name_ptr"])
            iat_rva = int(record["iat_rva"])
            iats.append(iat_rva)
            if name.startswith("#") and name_ptr < 0x10000:
                value = 0x80000000 | int(name[1:])
            else:
                name_rva = name_ptr - image_base
                encoded = name.encode("ascii")
                mem[name_rva : name_rva + len(encoded) + 1] = encoded + b"\0"
                mem[name_rva - 2 : name_rva] = b"\0\0"
                value = name_rva - 2
            values.append(value)
        if any(right - left != 4 for left, right in zip(iats, iats[1:])):
            raise RuntimeError(f"non-contiguous IAT for {stub.name}:{group['dll']}")
        group["ft"] = iats[0]
        for iat_rva, value in zip(iats, values):
            _p32(mem, iat_rva, value)
        _p32(mem, iats[-1] + 4, 0)

        seq = b"".join(struct.pack("<I", value) for value in values) + b"\0\0\0\0"
        hits: list[int] = []
        pos = int(rdata["va"])
        end = pos + int(rdata["vs"])
        while True:
            found = mem.find(seq, pos, end)
            if found < 0:
                break
            if not (int(group["ft"]) <= found <= int(group["ft"]) + 4 * len(values)):
                hits.append(found)
            pos = found + 1
        group["oft"] = hits[0] if len(hits) == 1 else 0

    export_rva = _u32(stub_data, opt + 96)
    export_size = _u32(stub_data, opt + 100)
    imp_rva = _align(export_rva + export_size, 4) if groups else 0
    imp_size = (len(groups) + 1) * 20 if groups else 0
    if groups:
        rdata_start = int(rdata["va"])
        rdata_end = rdata_start + int(rdata["vs"])
        if not (rdata_start <= imp_rva and imp_rva + imp_size <= rdata_end):
            # TCUWControlCommPhase has a genuine separate .idata section and its
            # restored .rdata ends exactly at the export directory. Only the
            # import descriptors need fresh storage; IAT/name RVAs stay original.
            imp_rva = _align(max(int(sec["va"]) + int(sec["vs"]) for sec in sections), sec_align)
            needed = _align(imp_size, 0x200)
            if imp_rva + needed > len(mem):
                mem.extend(b"\0" * (imp_rva + needed - len(mem)))
            sections.append({"name": ".impfix", "va": imp_rva, "vs": imp_size, "prot": 2, "ch": 0x40000040})
        mem[imp_rva : imp_rva + imp_size] = b"\0" * imp_size
        for index, group in enumerate(groups):
            struct.pack_into(
                "<IIIII",
                mem,
                imp_rva + 20 * index,
                int(group["oft"]),
                0,
                0,
                int(group["dll_ptr_rva"]),
                int(group["ft"]),
            )

    file_align = 0x200
    headers = _align(sec0 + 40 * len(sections), file_align)
    raw_ptr = headers
    packed: list[dict[str, int | str]] = []
    for sec in sections:
        raw_size = _align(int(sec["vs"]), file_align)
        packed.append({**sec, "rs": raw_size, "rp": raw_ptr})
        raw_ptr += raw_size
    out = bytearray(raw_ptr)
    out[: min(headers, len(stub_data))] = stub_data[: min(headers, len(stub_data))]
    for sec in packed:
        va = int(sec["va"])
        vs = int(sec["vs"])
        rp = int(sec["rp"])
        out[rp : rp + vs] = mem[va : va + vs]

    _p16(out, peoff + 6, len(packed))
    _p32(out, opt + 4, sum(int(sec["rs"]) for sec in packed if int(sec["ch"]) & 0x20))
    _p32(out, opt + 8, sum(int(sec["rs"]) for sec in packed if not (int(sec["ch"]) & 0x20)))
    _p32(out, opt + 12, 0)
    _p32(out, opt + 16, int(meta["entrypoint_rva"]))
    code = next(sec for sec in packed if sec["name"] == ".text")
    data = next((sec for sec in packed if sec["name"] in (".rdata", ".data")), packed[1])
    _p32(out, opt + 20, int(code["va"]))
    _p32(out, opt + 24, int(data["va"]))
    _p32(out, opt + 32, sec_align)
    _p32(out, opt + 36, file_align)
    _p32(out, opt + 56, _align(max(int(sec["va"]) + int(sec["vs"]) for sec in packed), sec_align))
    _p32(out, opt + 60, headers)
    _p32(out, opt + 64, 0)

    def set_dir(index: int, rva: int, size: int) -> None:
        _p32(out, opt + 96 + 8 * index, rva)
        _p32(out, opt + 100 + 8 * index, size)

    by_name = {str(sec["name"]): sec for sec in packed}
    set_dir(0, export_rva, export_size)
    set_dir(1, imp_rva, imp_size)
    rsrc = by_name.get(".rsrc")
    reloc = by_name.get(".reloc")
    set_dir(2, int(rsrc["va"]), int(rsrc["vs"])) if rsrc else set_dir(2, 0, 0)
    set_dir(4, 0, 0)
    set_dir(5, int(reloc["va"]), int(reloc["vs"])) if reloc else set_dir(5, 0, 0)
    for index in (6, 9, 10, 11, 12, 13, 15):
        set_dir(index, 0, 0)
    set_dir(14, *clr_dir) if clr_dir[0] else set_dir(14, 0, 0)

    for index in range(nsec):
        out[sec0 + 40 * index : sec0 + 40 * (index + 1)] = b"\0" * 40
    for index, sec in enumerate(packed):
        off = sec0 + 40 * index
        name = str(sec["name"]).encode("ascii")[:8]
        out[off : off + 8] = name.ljust(8, b"\0")
        struct.pack_into(
            "<IIIIIIHHI",
            out,
            off + 8,
            int(sec["vs"]),
            int(sec["va"]),
            int(sec["rs"]),
            int(sec["rp"]),
            0,
            0,
            0,
            0,
            int(sec["ch"]),
        )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(out)
    return {
        "entrypoint_rva": int(meta["entrypoint_rva"]),
        "import_count": sum(len(group["imports"]) for group in groups),
        "import_dll_count": len(groups),
        "section_count": len(packed),
        "classification": "mixed-managed" if clr_dir[0] else "native",
    }


def _managed_build(stub: Path, meta_path: Path, memory_path: Path, out_path: Path) -> dict[str, Any]:
    stub_data = stub.read_bytes()
    meta = json.loads(meta_path.read_text())
    mem = bytearray(memory_path.read_bytes())
    if not meta.get("protector_success"):
        raise RuntimeError(f"incomplete managed decode metadata for {stub.name}")
    peoff = _u32(stub_data, 0x3C)
    optsz = _u16(stub_data, peoff + 20)
    opt = peoff + 24
    image_base = _u32(stub_data, opt + 28)
    calls = [tuple(map(int, item)) for item in meta["protect_calls"] if int(item[0])]
    if len(calls) == 3:
        (text_va, text_vs, _), (rsrc_va, rsrc_vs, _), (reloc_va, reloc_vs, _) = calls
        data_range = None
    elif len(calls) == 4:
        (text_va, text_vs, _), (data_va, data_vs, _), (rsrc_va, rsrc_vs, _), (reloc_va, reloc_vs, _) = calls
        data_range = (data_va, data_vs)
    else:
        raise RuntimeError(f"unexpected managed restored-range count for {stub.name}: {calls}")
    if _u32(mem, opt + 96 + 14 * 8) == 0:
        raise RuntimeError(f"restored CLR header missing for {stub.name}")

    pattern = b"\xff\x25" + struct.pack("<I", image_base + text_va)
    hits: list[int] = []
    pos = text_va
    while True:
        found = mem.find(pattern, pos, text_va + text_vs)
        if found < 0:
            break
        hits.append(found)
        pos = found + 1
    if len(hits) == 1:
        entry = hits[0]
    elif not hits and stub.suffix.lower() == ".exe":
        chunk = mem[text_va : text_va + text_vs]
        last = max((index for index, value in enumerate(chunk) if value), default=0)
        entry = text_va + _align(last + 1, 0x10)
        if entry + 6 > text_va + text_vs or any(mem[entry : entry + 6]):
            raise RuntimeError(f"no safe CLR EXE bootstrap padding for {stub.name}")
        mem[entry : entry + 6] = b"\xff\x25" + struct.pack("<I", image_base + text_va)
    else:
        raise RuntimeError(f"expected one CLR bootstrap jump for {stub.name}, got {hits}")

    recovered = [
        rec
        for rec in meta.get("imports", [])
        if rec["dll"].lower() == "mscoree.dll" and rec["name"] in ("_CorDllMain", "_CorExeMain")
    ]
    if len(recovered) == 1:
        function = recovered[0]["name"].encode("ascii")
    elif not recovered:
        function = b"_CorExeMain" if stub.suffix.lower() == ".exe" else b"_CorDllMain"
    else:
        raise RuntimeError(f"ambiguous CLR handoff for {stub.name}: {recovered}")

    dll = b"mscoree.dll"
    section_align = 0x2000
    file_align = 0x200
    idata_va = _align(reloc_va + reloc_vs, section_align)
    int_off = 40
    ibn_off = _align(int_off + 8, 2)
    dll_off = ibn_off + 2 + len(function) + 1
    idata = bytearray(dll_off + len(dll) + 1)
    ibn_rva = idata_va + ibn_off
    dll_rva = idata_va + dll_off
    int_rva = idata_va + int_off
    struct.pack_into("<IIIII", idata, 0, int_rva, 0, 0, dll_rva, text_va)
    struct.pack_into("<II", idata, int_off, ibn_rva, 0)
    struct.pack_into("<H", idata, ibn_off, 0)
    idata[ibn_off + 2 : ibn_off + 2 + len(function) + 1] = function + b"\0"
    idata[dll_off : dll_off + len(dll) + 1] = dll + b"\0"
    _p32(mem, text_va, ibn_rva)
    _p32(mem, text_va + 4, 0)

    sections: list[tuple[str, int, int, int]] = [(".text", text_va, text_vs, 0x60000020)]
    if data_range:
        sections.append((".data", data_range[0], data_range[1], 0xC0000040))
    sections += [
        (".rsrc", rsrc_va, rsrc_vs, 0x40000040),
        (".reloc", reloc_va, reloc_vs, 0x42000040),
        (".idata", idata_va, len(idata), 0x40000040),
    ]
    sec0 = opt + optsz
    headers = _align(sec0 + 40 * len(sections), file_align)
    raw_ptr = headers
    packed: list[tuple[str, int, int, int, int, int]] = []
    for name, va, vs, chars in sections:
        raw_size = _align(vs, file_align)
        packed.append((name, va, vs, raw_size, raw_ptr, chars))
        raw_ptr += raw_size
    out = bytearray(raw_ptr)
    out[: min(headers, len(stub_data))] = stub_data[: min(headers, len(stub_data))]
    for name, va, vs, raw_size, rp, chars in packed:
        if name == ".idata":
            out[rp : rp + len(idata)] = idata
        else:
            out[rp : rp + vs] = mem[va : va + vs]

    _p16(out, peoff + 6, len(sections))
    _p32(out, opt + 4, packed[0][3])
    _p32(out, opt + 8, sum(item[3] for item in packed[1:]))
    _p32(out, opt + 12, 0)
    _p32(out, opt + 16, entry)
    _p32(out, opt + 20, text_va)
    _p32(out, opt + 24, data_range[0] if data_range else rsrc_va)
    _p32(out, opt + 32, section_align)
    _p32(out, opt + 36, file_align)
    _p32(out, opt + 56, _align(idata_va + len(idata), section_align))
    _p32(out, opt + 60, headers)
    _p32(out, opt + 64, 0)

    def set_dir(index: int, rva: int, size: int) -> None:
        _p32(out, opt + 96 + 8 * index, rva)
        _p32(out, opt + 100 + 8 * index, size)

    set_dir(0, 0, 0)
    set_dir(1, idata_va, 40)
    set_dir(2, rsrc_va, rsrc_vs)
    set_dir(4, 0, 0)
    set_dir(5, reloc_va, reloc_vs)
    set_dir(6, 0, 0)
    set_dir(9, 0, 0)
    set_dir(10, 0, 0)
    set_dir(11, 0, 0)
    set_dir(12, text_va, 8)
    set_dir(13, 0, 0)
    # Data directory 14 is the restored CLR header and must be preserved.
    set_dir(15, 0, 0)

    old_sections = _u16(stub_data, peoff + 6)
    for index in range(old_sections):
        out[sec0 + 40 * index : sec0 + 40 * (index + 1)] = b"\0" * 40
    for index, (name, va, vs, raw_size, rp, chars) in enumerate(packed):
        off = sec0 + 40 * index
        out[off : off + 8] = name.encode("ascii").ljust(8, b"\0")
        struct.pack_into("<IIIIIIHHI", out, off + 8, vs, va, raw_size, rp, 0, 0, 0, 0, chars)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(out)
    return {
        "entrypoint_rva": entry,
        "import_count": 1,
        "import_dll_count": 1,
        "section_count": len(packed),
        "classification": "managed",
    }


def _run_decoder(stub: Path, decoded: Path, log_dir: Path) -> tuple[Path, Path]:
    decoded.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    log = log_dir / f"{_stem(stub)}.log"
    with log.open("w") as handle:
        subprocess.run(
            [sys.executable, str(DECODER), str(stub), "--output-dir", str(decoded)],
            stdout=handle,
            stderr=subprocess.STDOUT,
            check=True,
        )
    meta = decoded / f"{_stem(stub)}.json"
    memory = decoded / f"{_stem(stub)}.final.mem"
    if not meta.is_file() or not memory.is_file():
        raise RuntimeError(f"decoder did not emit expected artifacts for {stub.name}; see {log}")
    data = json.loads(meta.read_text())
    if not data.get("protector_success"):
        raise RuntimeError(f"CP protector did not reach success for {stub.name}; see {log}")
    return meta, memory


def _validate_output(path: Path, expect_managed: bool) -> dict[str, Any]:
    pe = pefile.PE(str(path), fast_load=False)
    imports = sum(len(desc.imports) for desc in getattr(pe, "DIRECTORY_ENTRY_IMPORT", []))
    result: dict[str, Any] = {
        "entrypoint_rva": pe.OPTIONAL_HEADER.AddressOfEntryPoint,
        "image_base": pe.OPTIONAL_HEADER.ImageBase,
        "section_count": len(pe.sections),
        "import_count": imports,
        "export_count": len(pe.DIRECTORY_ENTRY_EXPORT.symbols) if hasattr(pe, "DIRECTORY_ENTRY_EXPORT") else 0,
        "size": path.stat().st_size,
    }
    if expect_managed:
        import dnfile

        managed = dnfile.dnPE(str(path))
        if not (managed.net and managed.net.metadata and managed.net.mdtables):
            raise RuntimeError(f"rebuilt managed PE has no parseable CLR metadata: {path}")
        assembly = managed.net.mdtables.Assembly
        if assembly and assembly.rows:
            result["assembly_name"] = str(assembly.rows[0].Name)
    return result


def recover(
    *,
    gtsplus_root: Path | None = None,
    source: Path | None = None,
    output: Path = DEFAULT_OUTPUT,
    workers: int | None = None,
    only: list[str] | None = None,
    exclude: list[str] | None = None,
    keep_workspace: bool = False,
) -> dict[str, Any]:
    gts = resolve_gts_root(gtsplus_root)
    source_root = _protected_source(gts, source)
    output = output.expanduser().resolve()
    stubs = sorted({Path(str(sidecar)[:-2]) for sidecar in [*source_root.rglob("*.dll._"), *source_root.rglob("*.exe._")]})
    if only:
        wanted = {name.replace("\\", "/").casefold() for name in only}
        stubs = [
            stub for stub in stubs
            if any(
                (token in stub.relative_to(source_root).as_posix().casefold())
                if "/" in token else (token in stub.name.casefold())
                for token in wanted
            )
        ]
    if exclude:
        blocked = {name.replace("\\", "/").strip("/").casefold() for name in exclude}
        stubs = [
            stub for stub in stubs
            if not any(
                (rel := stub.relative_to(source_root).as_posix().casefold()) == token
                or rel.startswith(token + "/")
                for token in blocked
            )
        ]
    if not stubs:
        raise SystemExit(f"no protected CP stubs selected under {source_root}")

    if output.exists() and not only:
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)
    build_tmp = REPO / "build/tmp"
    build_tmp.mkdir(parents=True, exist_ok=True)
    temp: tempfile.TemporaryDirectory[str] | None = None
    if keep_workspace:
        workspace = build_tmp / "cp-body-recovery"
        if workspace.exists():
            shutil.rmtree(workspace)
        workspace.mkdir(parents=True)
    else:
        temp = tempfile.TemporaryDirectory(prefix="cp-body-recovery-", dir=build_tmp)
        workspace = Path(temp.name)
    decoded = workspace / "decoded"
    logs = workspace / "logs"

    max_workers = max(1, min(workers or min(8, os.cpu_count() or 1), len(stubs)))
    decoded_paths: dict[Path, tuple[Path, Path]] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_run_decoder, stub, decoded, logs): stub for stub in stubs}
        for future in concurrent.futures.as_completed(futures):
            stub = futures[future]
            decoded_paths[stub] = future.result()

    entries: list[dict[str, Any]] = []
    for stub in stubs:
        meta_path, memory_path = decoded_paths[stub]
        meta = json.loads(meta_path.read_text())
        calls = [item for item in meta["protect_calls"] if item[0]]
        managed_input = _is_managed(stub)
        rel = stub.relative_to(source_root)
        destination = output / rel
        if managed_input and len(calls) in (3, 4):
            build_info = _managed_build(stub, meta_path, memory_path, destination)
        else:
            build_info = _native_build(stub, meta_path, memory_path, destination)
        validation = _validate_output(destination, managed_input)
        sidecar = Path(str(stub) + "._")
        entries.append({
            "relative_path": rel.as_posix(),
            "classification": build_info["classification"],
            "managed_input": managed_input,
            "stub_size": stub.stat().st_size,
            "stub_sha256": _sha256(stub),
            "sidecar_size": sidecar.stat().st_size,
            "sidecar_sha256": _sha256(sidecar),
            "output_size": destination.stat().st_size,
            "output_sha256": _sha256(destination),
            "lfsr_rva": meta.get("lfsr_rva"),
            "phase5c_done": bool(meta.get("phase5c_done")),
            "protector_success": bool(meta.get("protector_success")),
            "protect_calls": meta["protect_calls"],
            "recovered_import_count": len(meta.get("imports", [])),
            **validation,
        })

    manifest = {
        "format": "gtsplus-cp-body-recovery-v1",
        "source_root": str(source_root),
        "output_root": str(output),
        "protected_body_count": len(stubs),
        "recovered_body_count": len(entries),
        "native_count": sum(not entry["managed_input"] for entry in entries),
        "managed_count": sum(entry["managed_input"] for entry in entries),
        "mixed_managed_count": sum(entry["classification"] == "mixed-managed" for entry in entries),
        "entries": entries,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    if temp is not None:
        temp.cleanup()
    return manifest


def recover_auxiliary(
    *,
    gtsplus_root: Path | None = None,
    output: Path = DEFAULT_AUX_OUTPUT,
    workers: int | None = None,
    keep_workspace: bool = False,
) -> dict[str, Any]:
    """Recover CP bodies outside the main GTSPlus and CUWPlus trees."""
    gts = resolve_gts_root(gtsplus_root)
    return recover(
        gtsplus_root=gts,
        source=gts.parent,
        output=output,
        workers=workers,
        exclude=["GTSPlus", "CUWPlus"],
        keep_workspace=keep_workspace,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gtsplus-root", type=Path)
    parser.add_argument("--source", type=Path, help="protected CP source directory (default: CUWPlus)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int)
    parser.add_argument("--only", action="append", help="recover only a filename or relative-path substring (repeatable)")
    parser.add_argument("--exclude", action="append", help="exclude a relative path/top-level subtree (repeatable)")
    parser.add_argument("--keep-workspace", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    manifest = recover(
        gtsplus_root=args.gtsplus_root,
        source=args.source,
        output=args.output,
        workers=args.workers,
        only=args.only,
        exclude=args.exclude,
        keep_workspace=args.keep_workspace,
    )
    if args.json:
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(f"CP: recovered {manifest['recovered_body_count']}/{manifest['protected_body_count']} protected PE bodies")
        print(f"native\t{manifest['native_count']}")
        print(f"managed\t{manifest['managed_count']} (mixed={manifest['mixed_managed_count']})")
        print(f"output\t{manifest['output_root']}")
        print(f"manifest\t{Path(manifest['output_root']) / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
