#!/usr/bin/env python3
"""List and disassemble selected managed methods in Techstream assemblies."""

from __future__ import annotations

import argparse
import re
from typing import Any

import dnfile
from dnfile.enums import MetadataTables
from dncil.cil.body import CilMethodBody
from dncil.cil.body.reader import CilMethodBodyReaderBase
from dncil.cil.error import MethodBodyFormatError
from dncil.clr.token import InvalidToken, StringToken, Token

TABLES_BY_INDEX = {table.value: table.name for table in MetadataTables}


class MethodBodyReader(CilMethodBodyReaderBase):
    def __init__(self, pe: dnfile.dnPE, row: dnfile.mdtable.MethodDefRow):
        self.pe = pe
        self.offset = pe.get_offset_from_rva(row.Rva)

    def read(self, count: int) -> bytes:
        data = self.pe.get_data(self.pe.get_rva_from_offset(self.offset), count)
        self.offset += count
        return data

    def tell(self) -> int:
        return self.offset

    def seek(self, offset: int) -> int:
        self.offset = offset
        return offset


def resolve_token(pe: dnfile.dnPE, token: Token) -> Any:
    if isinstance(token, StringToken):
        try:
            value = pe.net.user_strings.get(token.rid)
        except UnicodeDecodeError:
            return InvalidToken(token.value)
        return value.value if value is not None else InvalidToken(token.value)

    table_name = TABLES_BY_INDEX.get(token.table)
    table = getattr(pe.net.mdtables, table_name, None) if table_name else None
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

    for type_row in pe.net.mdtables.TypeDef:
        qualified_name = type_name(type_row)
        if not type_pattern.search(qualified_name):
            continue
        methods = [
            index.row
            for index in type_row.MethodList
            if method_pattern.search(str(index.row.Name))
        ]
        if not methods:
            continue
        if args.list:
            print(qualified_name)
            for row in methods:
                print(f"  {row.Name} RVA=0x{row.Rva:X}")
            continue

        for row in methods:
            print(f"\n{qualified_name}::{row.Name} RVA=0x{row.Rva:X}")
            if not row.ImplFlags.miIL or row.Flags.mdAbstract or row.Flags.mdPinvokeImpl:
                print("  <no managed body>")
                continue
            try:
                body = CilMethodBody(MethodBodyReader(pe, row))
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
