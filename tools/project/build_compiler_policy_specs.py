#!/usr/bin/env python3
"""Derive native compiler specs for exact EP/GP/TP/r2 preservation policies.

Runs only against the installer's disposable extension copy. Native default
prototypes apply to direct *and* unresolved indirect calls; named prototype
extensions alone cannot change Ghidra's EVAL_CALLED model.
"""
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import xml.etree.ElementTree as ET


REGISTERS = ("ep", "gp", "tp", "r2")


def generate(language_dir: Path) -> None:
    definitions = ET.parse(language_dir / "v850.ldefs")
    produced: set[str] = set()
    for language in definitions.getroot().findall("language"):
        for compiler in list(language.findall("compiler")):
            if compiler.get("id") not in ("default", "gcc", "ccrh"):
                continue
            source_name = compiler.attrib["spec"]
            insert_at = list(language).index(compiler) + 1
            for mask in range(16):
                selected = [name for bit, name in enumerate(REGISTERS) if mask & (1 << bit)]
                policy = "_".join(selected) or "none"
                output_name = f"{Path(source_name).stem}_callee_{policy}.cspec"
                if output_name not in produced:
                    spec = ET.parse(language_dir / source_name)
                    prototype = spec.getroot().find("default_proto/prototype")
                    if prototype is None:
                        raise ValueError(f"{source_name}: missing default prototype")
                    for tag, names in (
                        ("unaffected", selected),
                        ("killedbycall", [name for name in REGISTERS if name not in selected]),
                    ):
                        effects = prototype.find(tag)
                        if effects is None:
                            effects = ET.SubElement(prototype, tag)
                        for register in list(effects.findall("register")):
                            if register.get("name") in REGISTERS:
                                effects.remove(register)
                        for name in names:
                            ET.SubElement(effects, "register", {"name": name})
                    ET.indent(spec, space="  ")
                    spec.write(language_dir / output_name, encoding="utf-8", xml_declaration=True)
                    produced.add(output_name)
                variant = copy.deepcopy(compiler)
                variant.set("id", f"{compiler.attrib['id']}-callee-{policy}")
                variant.set("spec", output_name)
                variant.set("name", f"{compiler.attrib['name']} — callee-save: {', '.join(selected) or 'none'}")
                language.insert(insert_at, variant)
                insert_at += 1
    ET.indent(definitions, space="  ")
    definitions.write(language_dir / "v850.ldefs", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("language_dir", type=Path)
    generate(parser.parse_args().language_dir)
