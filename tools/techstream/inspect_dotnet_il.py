#!/usr/bin/env python3
"""List and disassemble selected managed methods in Techstream assemblies."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
from typing import Any

import dnfile
import dnfile.mdtable
from dnfile.stream import HeapItemBinary, MetaDataTables
from dnfile.enums import MetadataTables
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBase
from dncil.cil.error import MethodBodyFormatError
from dncil.cil.enums import OpCodeType, OperandType
from dncil.clr.token import InvalidToken, StringToken, Token

TABLES_BY_INDEX = {table.value: table.name for table in MetadataTables}


class MethodBodyReader(CilMethodBodyReaderBase):
    def __init__(self, pe: dnfile.dnPE, row: dnfile.mdtable.MethodDefRow):
        self.pe = pe
        self.offset = pe.get_offset_from_rva(row.Rva)

    def read(self, n: int) -> bytes:
        data = self.pe.get_data(self.pe.get_rva_from_offset(self.offset), n)
        self.offset += n
        return bytes(data)

    def tell(self) -> int:
        return self.offset

    def seek(self, rva: int) -> int:
        self.offset = rva
        return rva


def _metadata_tables(pe: dnfile.dnPE) -> MetaDataTables:
    net = pe.net
    if net is None or net.mdtables is None:
        raise ValueError("PE has no CLR metadata")
    return net.mdtables


def resolve_token(pe: dnfile.dnPE, token: Token) -> Any:
    tables = _metadata_tables(pe)
    if isinstance(token, StringToken):
        try:
            net = pe.net
            if net is None or net.user_strings is None:
                return InvalidToken(token.value)
            value = net.user_strings.get(token.rid)
        except UnicodeDecodeError:
            return InvalidToken(token.value)
        return value.value if value is not None else InvalidToken(token.value)

    table_name = TABLES_BY_INDEX.get(token.table)
    table = getattr(tables, table_name, None) if table_name else None
    if table is None or token.rid < 1 or token.rid > len(table.rows):
        return InvalidToken(token.value)
    return table.rows[token.rid - 1]


def type_name(row: Any) -> str:
    namespace = str(getattr(row, "TypeNamespace", ""))
    name = str(getattr(row, "TypeName", row))
    return f"{namespace}.{name}" if namespace else name


def format_operand(pe: dnfile.dnPE, operand: Any) -> str:
    if isinstance(operand, Token):
        operand = resolve_token(pe, operand)
    if isinstance(operand, str):
        return repr(operand)
    if isinstance(operand, int):
        return hex(operand)
    if isinstance(operand, list):
        return "[" + ", ".join(f"IL_{value:04X}" for value in operand) + "]"
    if isinstance(operand, dnfile.mdtable.MemberRefRow):
        owner = getattr(operand.Class, "row", None)
        return f"{type_name(owner)}::{operand.Name}" if owner else str(operand.Name)
    if isinstance(operand, dnfile.mdtable.MethodDefRow):
        return str(operand.Name)
    if isinstance(operand, dnfile.mdtable.FieldRow):
        return str(operand.Name)
    if isinstance(operand, (dnfile.mdtable.TypeDefRow, dnfile.mdtable.TypeRefRow)):
        return type_name(operand)
    if operand is None:
        return ""
    return str(operand)


class _BoundedMethodBodyReader(MethodBodyReader):
    """Keep dncil reads inside the method's file-backed PE section."""

    def __init__(self, pe: dnfile.dnPE, row: dnfile.mdtable.MethodDefRow):
        super().__init__(pe, row)
        section = pe.get_section_by_rva(row.Rva)
        if section is None:
            raise MethodBodyFormatError("method RVA is outside PE sections")
        self.start = self.offset
        raw_start = section.get_PointerToRawData_adj()
        self.end = min(raw_start + section.SizeOfRawData, len(pe.__data__))
        if not raw_start <= self.start < self.end:
            raise MethodBodyFormatError("method RVA has no file-backed bytes")
        self.limit = self.end

    def read(self, n: int) -> bytes:
        if n < 0 or not self.start <= self.offset <= self.limit - n:
            raise MethodBodyFormatError("method read exceeds file-backed bounds")
        data = self.pe.__data__[self.offset : self.offset + n]
        if len(data) != n:
            raise MethodBodyFormatError("truncated method bytes")
        self.offset += n
        return bytes(data)

    def seek(self, rva: int) -> int:
        if not self.start <= rva <= self.limit:
            raise MethodBodyFormatError("method seek exceeds file-backed bounds")
        self.offset = rva
        return rva


class _CompleteCilMethodBody(CilMethodBody):
    """Apply strict framing around dncil's header, instruction and EH readers."""
    extra_sections: list[dict[str, int | bool]]

    def parse_header(self, reader: CilMethodBodyReaderBase) -> None:
        if not isinstance(reader, _BoundedMethodBodyReader):
            raise MethodBodyFormatError("complete IL parsing requires a bounded PE reader")
        first = reader.read(1)[0]
        reader.seek(self.offset)
        if first & 3 == 3:
            flags = int.from_bytes(reader.read(2), "little")
            reader.seek(self.offset)
            if flags >> 12 < 3 or flags & 0x0FE4:
                raise MethodBodyFormatError("invalid fat method header size/flags")
            if reader.pe.get_rva_from_offset(self.offset) & 3:
                raise MethodBodyFormatError("unaligned fat method header")
        elif first & 3 != 2:
            raise MethodBodyFormatError("invalid IL method header")
        super().parse_header(reader)
        if not self.code_size:
            raise MethodBodyFormatError("empty IL instruction stream")
        if self.offset + self.header_size + self.code_size > reader.end:
            raise MethodBodyFormatError("truncated IL instruction stream")
        if self.local_var_sig_tok is not None:
            token = self.local_var_sig_tok
            net = reader.pe.net
            tables = net.mdtables if net is not None else None
            table = tables.StandAloneSig if tables is not None else None
            if token.table != 0x11 or table is None or not 1 <= token.rid <= len(table.rows):
                raise MethodBodyFormatError("invalid local-variable signature token")

    def parse_instructions(self, reader: CilMethodBodyReaderBase) -> None:
        if not isinstance(reader, _BoundedMethodBodyReader):
            raise MethodBodyFormatError("complete IL parsing requires a bounded PE reader")
        reader.limit = self.offset + self.header_size + self.code_size
        try:
            super().parse_instructions(reader)
        finally:
            reader.limit = reader.end
        starts = {instruction.offset for instruction in self.instructions}
        for instruction in self.instructions:
            if instruction.opcode.op_code_type == OpCodeType.Nternal:
                raise MethodBodyFormatError("reserved or unknown IL opcode")
            if instruction.opcode.operand_type in (
                OperandType.InlineBrTarget, OperandType.ShortInlineBrTarget,
            ):
                targets = [instruction.operand]
            elif instruction.opcode.operand_type == OperandType.InlineSwitch:
                operand = instruction.operand
                if not isinstance(operand, list):
                    raise MethodBodyFormatError("invalid switch target list")
                targets = operand
            else:
                continue
            for target in targets:
                if not isinstance(target, int) or target not in starts:
                    raise MethodBodyFormatError("branch target is not an instruction boundary")

    def parse_exception_handlers(self, reader: CilMethodBodyReaderBase) -> None:
        if not isinstance(reader, _BoundedMethodBodyReader):
            raise MethodBodyFormatError("complete IL parsing requires a bounded PE reader")
        self.extra_sections = []
        more = self.flags.MoreSects
        while more:
            reader.seek((reader.tell() + 3) & ~3)
            start = reader.tell()
            header = reader.read(4)
            kind = header[0]
            fat = bool(kind & 0x40)
            size = int.from_bytes(header[1:4], "little") if fat else header[1]
            clause_size = 24 if fat else 12
            if kind & 0x3F != 1 or size < 4 or (size - 4) % clause_size:
                raise MethodBodyFormatError("invalid exception section kind/size")
            if not fat and header[2:4] != b"\0\0":
                raise MethodBodyFormatError("invalid small exception section reserved bytes")
            end = start + size
            if end > reader.end:
                raise MethodBodyFormatError("truncated exception section")
            reader.seek(start + 1)
            reader.limit = end
            try:
                if fat:
                    self.parse_fat_exception_handlers(reader)
                else:
                    self.parse_tiny_exception_handlers(reader)
                if reader.tell() != end:
                    raise MethodBodyFormatError("exception section length mismatch")
            finally:
                reader.limit = reader.end
            self.extra_sections.append({"file_offset": start, "size": size, "fat": fat})
            more = bool(kind & 0x80)
        self.size = reader.tell() - self.offset
        code_start = self.offset + self.header_size
        starts = {instruction.offset - code_start for instruction in self.instructions}
        ends = starts | {self.code_size}
        for handler in self.exception_handlers:
            if handler.exception_type not in (0, 1, 2, 4):
                raise MethodBodyFormatError("invalid exception clause flags")
            for start, end in (
                (handler.try_start, handler.try_end),
                (handler.handler_start, handler.handler_end),
            ):
                if start not in starts or end not in ends or end <= start:
                    raise MethodBodyFormatError("invalid exception clause instruction range")
            if handler.is_filter() and handler.filter_start not in starts:
                raise MethodBodyFormatError("invalid exception filter offset")


def read_managed_body(pe: dnfile.dnPE, row: dnfile.mdtable.MethodDefRow) -> _CompleteCilMethodBody:
    """Read one complete, bounded IL body; callers must first classify its flags."""
    return _CompleteCilMethodBody(_BoundedMethodBodyReader(pe, row))


def managed_method_identities(pe: dnfile.dnPE, source_sha256: str) -> dict[str, Any]:
    """Return lossless source/module/token identities, including nested ownership."""
    tables = _metadata_tables(pe)
    for name, table in (
        ("Module", tables.Module), ("TypeDef", tables.TypeDef),
        ("MethodDef", tables.MethodDef), ("NestedClass", tables.NestedClass),
    ):
        if table is not None and (
            len(table.rows) != table.num_rows
            or any(len(row._data) != table.row_size for row in table.rows)
        ):
            raise ValueError(f"truncated {name} metadata table")
    modules = tables.Module
    if modules is None or len(modules.rows) != 1 or modules.rows[0].Mvid is None:
        raise ValueError("managed module must have exactly one Module row with MVID")
    mvid = str(modules.rows[0].Mvid)
    scope = f"sha256:{source_sha256}:module:{mvid}"
    type_defs, method_defs = tables.TypeDef, tables.MethodDef
    types = list(type_defs.rows) if type_defs is not None else []
    methods = list(method_defs.rows) if method_defs is not None else []
    parents: dict[int, int] = {}
    nested_records = []
    nested = tables.NestedClass
    for row in nested.rows if nested else ():
        child, parent = row.NestedClass.row_index, row.EnclosingClass.row_index
        if child in parents or not 1 <= child <= len(types) or not 1 <= parent <= len(types):
            raise ValueError("invalid or duplicate NestedClass ownership")
        parents[child] = parent
        nested_records.append({
            "nested_typedef_token": f"0x{0x02000000 | child:08X}",
            "enclosing_typedef_token": f"0x{0x02000000 | parent:08X}",
        })
    chains: dict[int, list[int]] = {}
    for rid in range(1, len(types) + 1):
        chain = []
        current = rid
        while current not in chains:
            if current in chain:
                raise ValueError("cyclic NestedClass ownership")
            chain.append(current)
            if current not in parents:
                break
            current = parents[current]
        prefix = chains.get(current, [])
        for child in reversed(chain):
            prefix = [*prefix, child]
            chains[child] = prefix
    method_rids = {id(row): rid for rid, row in enumerate(methods, 1)}
    owners: dict[int, dict[str, Any]] = {}
    type_records = []
    for rid, row in enumerate(types, 1):
        chain = chains[rid]
        full_name = type_name(types[chain[0] - 1])
        full_name += "".join(f"+{types[parent - 1].TypeName}" for parent in chain[1:])
        token = f"0x{0x02000000 | rid:08X}"
        record = {
            "identity": f"{scope}:{token}", "typedef_token": token,
            "namespace": str(row.TypeNamespace), "name": str(row.TypeName),
            "full_nested_name": full_name,
            "owner_chain": [f"0x{0x02000000 | parent:08X}" for parent in chain],
            "method_tokens": [],
        }
        for index in row.MethodList:
            method_rid = method_rids.get(id(index.row))
            if method_rid is None or method_rid in owners:
                raise ValueError("invalid or multiply owned MethodDef")
            owners[method_rid] = record
            record["method_tokens"].append(f"0x{0x06000000 | method_rid:08X}")
        type_records.append(record)
    method_records = []
    for rid, row in enumerate(methods, 1):
        owner = owners.get(rid)
        if owner is None:
            raise ValueError(f"unowned MethodDef 0x{0x06000000 | rid:08X}")
        # dnfile's MethodDefRow annotation says bytes, but _parse_struct_blobs
        # materializes HeapItemBinary (or None on a missing/invalid heap).
        signature: object = getattr(row, "Signature", None)
        if not isinstance(signature, HeapItemBinary):
            raise ValueError("MethodDef signature is missing")
        signature_value: object = signature.value
        if not isinstance(signature_value, (bytes, bytearray)) or not signature_value:
            raise ValueError("MethodDef signature is missing")
        if len(signature_value) != signature.item_size:
            raise ValueError("MethodDef signature is truncated")
        structure = row.struct
        if not isinstance(structure, dnfile.mdtable.MethodDefRowStruct):
            raise ValueError("invalid MethodDef row structure")
        token = f"0x{0x06000000 | rid:08X}"
        method_records.append({
            "identity": f"{scope}:{token}", "methoddef_token": token,
            "owner_identity": owner["identity"], "typedef_token": owner["typedef_token"],
            "full_nested_name": owner["full_nested_name"], "name": str(row.Name),
            "signature_hex": signature_value.hex(), "rva": int(row.Rva),
            "impl_flags": structure.ImplFlags, "flags": structure.Flags,
        })
    return {
        "source_sha256": source_sha256, "module_mvid": mvid,
        "type_definitions": type_records, "nested_classes": nested_records,
        "methods": method_records,
    }


def _method_classification(row: dnfile.mdtable.MethodDefRow) -> str:
    impl, flags = row.ImplFlags, row.Flags
    if not row.Rva:
        for condition, classification in (
            (flags.mdAbstract, "abstract"), (flags.mdPinvokeImpl, "pinvoke"),
            (impl.miRuntime, "runtime"), (impl.miInternalCall, "internal_call"),
            (impl.miForwardRef, "forward_ref"),
        ):
            if condition:
                return classification
    if impl.miNative:
        return "native"
    if impl.miRuntime:
        return "runtime"
    if impl.miOPTIL:
        return "optil"
    if impl.miUnmanaged:
        return "unmanaged"
    return "il" if row.Rva else "missing_il"


def inspect_managed_bodies(path: str | Path) -> dict[str, Any]:
    """Validate IL and expose exact identities, framing and hashes for every row.

    Raises ValueError for invalid metadata, missing required IL, or malformed IL.
    Native/OPTIL/unmanaged bytes are classified, not certified as instructions.
    """
    path = Path(path)
    pe = None
    try:
        pe = dnfile.dnPE(str(path))
        tables = _metadata_tables(pe)
        result = managed_method_identities(pe, hashlib.sha256(pe.__data__).hexdigest())
        result["source_path"] = str(path)
        assembly = tables.Assembly
        result["assembly_name"] = str(assembly.rows[0].Name) if assembly and assembly.rows else None
        method_defs = tables.MethodDef
        rows = list(method_defs.rows) if method_defs is not None else []
        counts: dict[str, int] = {}
        for row, record in zip(rows, result["methods"]):
            classification = _method_classification(row)
            record["implementation"] = classification
            counts[classification] = counts.get(classification, 0) + 1
            if classification == "missing_il":
                raise ValueError(f'{record["methoddef_token"]}: required IL body has RVA 0')
            if classification != "il":
                continue
            try:
                body = read_managed_body(pe, row)
            except Exception as error:
                raise ValueError(f'{record["methoddef_token"]}: invalid IL body: {error}') from error
            record["body"] = {
                "file_offset": body.offset, "header_size": body.header_size,
                "code_size": body.code_size, "size": body.size,
                "sha256": hashlib.sha256(body.raw_bytes).hexdigest(),
                "extra_sections": body.extra_sections,
            }
        result.update({
            "method_def_count": len(rows),
            "method_body_rva_count": sum(bool(row.Rva) for row in rows),
            "method_body_materialized_count": counts.get("il", 0),
            "classification_counts": counts,
        })
        return result
    except ValueError:
        raise
    except Exception as error:
        raise ValueError(f"{path}: invalid managed metadata: {error}") from error
    finally:
        if pe is not None:
            pe.close()


def validate_managed_bodies(path: str | Path) -> dict[str, Any]:
    """Return compact admission proof; raise ValueError on invalid metadata/IL.

    method_def_count counts all rows. method_body_rva_count counts all nonzero
    RVAs, including native code. method_body_materialized_count counts complete
    valid IL bodies only. classification_counts distinguishes legitimate RVA0
    abstract/pinvoke/runtime/internal_call/forward_ref methods and non-IL code.
    Full token/ownership records are available through inspect_managed_bodies.
    """
    result = inspect_managed_bodies(path)
    return {key: result[key] for key in (
        "assembly_name", "source_sha256", "module_mvid", "classification_counts",
        "method_def_count", "method_body_rva_count", "method_body_materialized_count",
    )}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("assembly")
    parser.add_argument("--type", default=".*", help="type-name regex")
    parser.add_argument("--method", default=".*", help="method-name regex")
    parser.add_argument("--list", action="store_true", help="list matches only")
    args = parser.parse_args()

    type_pattern = re.compile(args.type, re.IGNORECASE)
    method_pattern = re.compile(args.method, re.IGNORECASE)
    pe = dnfile.dnPE(args.assembly)

    tables = _metadata_tables(pe)
    identities = managed_method_identities(pe, hashlib.sha256(pe.__data__).hexdigest())
    method_records = {record["methoddef_token"]: record for record in identities["methods"]}
    type_defs = tables.TypeDef
    for type_row, type_record in zip(
        type_defs.rows if type_defs is not None else (), identities["type_definitions"],
    ):
        qualified_name = type_record["full_nested_name"]
        if not type_pattern.search(qualified_name):
            continue
        methods = []
        for index, token in zip(type_row.MethodList, type_record["method_tokens"]):
            method_row = index.row
            if method_row is None:
                raise ValueError("invalid MethodDef index")
            if method_pattern.search(str(method_row.Name)):
                methods.append((method_row, method_records[token]))
        if not methods:
            continue
        if args.list:
            print(f'{qualified_name} [{type_record["typedef_token"]}]')
            for row, record in methods:
                token = record["methoddef_token"]
                print(
                    f'  {record["name"]} {token} sig={record["signature_hex"]} '
                    f'RVA=0x{record["rva"]:X} {_method_classification(row)}'
                )
            continue

        for row, record in methods:
            print(
                f'\n{qualified_name}::{row.Name} [{record["methoddef_token"]}] '
                f'sig={record["signature_hex"]} RVA=0x{row.Rva:X}'
            )
            classification = _method_classification(row)
            if classification != "il":
                print(f"  <{classification}>")
                continue
            try:
                body = read_managed_body(pe, row)
            except MethodBodyFormatError as error:
                print(f"  <invalid body: {error}>")
                continue
            for instruction in body.instructions:
                operand = format_operand(pe, instruction.operand)
                print(
                    f"  IL_{instruction.offset:04X}: "
                    f"{str(instruction.opcode):<14} {operand}"
                )


if __name__ == "__main__":
    main()
