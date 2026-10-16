#!/usr/bin/env python3
"""Classify DEFAULT-named F33 functions into byte-verified structural idiom families.

Whole-image shape census over the canonical corpus: exact normalized-pseudocode
duplicate clusters plus machine-verified micro-idioms (return-only stubs,
far-call trampolines, constant publishers, constant sources). The census is
derived evidence for family-propagated recovered-function rows; it records the
byte gates so each class is reproducible from the exact image and corpus alone.
"""
from __future__ import annotations

from tools.targets.camry.support import camry_f33_corpus as f33
from tools import REPO_ROOT
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = REPO_ROOT
IMAGE = f33.IMAGE
CORPUS = f33.CORPUS
INVENTORY = f33.INVENTORY
DEFAULT_OUT = ROOT / "data/generated/camry_8965F3307000_function_family_census.json"
SHA = f33.IMAGE_SHA256

RETURN_ONLY_BYTES = "7f00"
TRAMPOLINE_HEAD = "80072100"
TRAMPOLINE_TAIL = "40063f00"
ASSIGN_RE = r"DAT_[0-9a-f]+ = (?:0x[0-9a-f]+|\d+);"


def hx(addr: int) -> str:
    return f"0x{addr:X}"


def load_functions() -> dict[int, dict]:
    functions: dict[int, dict] = {}
    with INVENTORY.open() as fh:
        for line in fh:
            row = json.loads(line)
            if row.get("record") == "function":
                functions[int(row["entry"]["offset"], 16)] = row
    return functions


def normalize(text: str) -> str:
    text = re.sub(r"0x[0-9a-fA-F]+", "N", text)
    text = re.sub(r"\b\d+\b", "N", text)
    text = re.sub(r"\b(FUN_|DAT_|UNK_|LAB_)[0-9a-f]+", "S", text)
    text = re.sub(r"\bparam_\d+", "P", text)
    text = re.sub(r"\b[uaculs]?Var\d+|\blocal_\d+|\bs_\d+|\bunaff_[a-z]+\d*", "V", text)
    return re.sub(r"\s+", " ", text).strip()


def body_lines(text: str) -> list[str]:
    skip_decl = re.compile(r"^(void|undefined\d?|u?int\d?_t|char|long|short)\b.*\(void\)$")
    out = []
    for raw in text.strip().splitlines():
        line = raw.strip()
        if not line or line in ("{", "}") or skip_decl.match(line):
            continue
        if line != "return;":
            out.append(line)
    return out


def classify(image: bytes, functions: dict[int, dict], corpus_rows: list[dict]) -> dict:
    ret_only: list[dict] = []
    trampolines: list[dict] = []
    publisher1: list[dict] = []
    publisher2: list[dict] = []
    const_source: list[dict] = []
    clusters: dict[str, list[int]] = defaultdict(list)

    for row in corpus_rows:
        if row.get("record") != "function":
            continue
        entry = int(row["entry_addr"], 16)
        meta = functions.get(entry)
        if meta is None or meta.get("name_source") != "DEFAULT":
            continue
        size = meta.get("body_address_count", 0)
        body = image[entry : entry + size]
        text = row["decompiled_c"]
        clusters[hashlib.sha1(normalize(text).encode()).hexdigest()[:12]].append(entry)

        if size == 2 and body.hex() == RETURN_ONLY_BYTES:
            ret_only.append({"entry": hx(entry)})
            continue
        if (
            size == 12
            and body.hex().startswith(TRAMPOLINE_HEAD)
            and body.hex().endswith(TRAMPOLINE_TAIL)
        ):
            callees = re.findall(r"FUN_([0-9a-f]{8})\(\);", text)
            if len(callees) == 1:
                trampolines.append({"entry": hx(entry), "target": hx(int(callees[0], 16))})
                continue
        lines = body_lines(text)
        if len(lines) == 1 and re.fullmatch(ASSIGN_RE, lines[0]):
            publisher1.append({"entry": hx(entry), "store": lines[0]})
            continue
        if len(lines) == 2 and all(re.fullmatch(ASSIGN_RE, x) for x in lines):
            publisher2.append({"entry": hx(entry), "stores": list(lines)})
            continue
        if len(lines) == 1 and re.fullmatch(r"return (?:0x[0-9a-f]+|\d+);", lines[0]):
            const_source.append({"entry": hx(entry), "value": lines[0].rstrip(";")})
            continue

    duplicate_clusters = {h: sorted(v) for h, v in clusters.items() if len(v) >= 2}
    return {
        "ret_only": ret_only,
        "trampolines": trampolines,
        "publisher1": publisher1,
        "publisher2": publisher2,
        "const_source": const_source,
        "shape_count": len(clusters),
        "duplicate_clusters": duplicate_clusters,
    }


def build() -> dict:
    image = IMAGE.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != SHA:
        raise SystemExit(f"exact F33 image drift: {digest}")
    functions = load_functions()
    corpus_rows = [json.loads(line) for line in CORPUS.open()]
    classes = classify(image, functions, corpus_rows)

    default_named = [
        m for m in functions.values() if m.get("name_source") == "DEFAULT"
    ]
    idiom_members = (
        {int(r["entry"], 16) for r in classes["ret_only"]}
        | {int(r["entry"], 16) for r in classes["trampolines"]}
        | {int(r["entry"], 16) for r in classes["publisher1"]}
        | {int(r["entry"], 16) for r in classes["publisher2"]}
        | {int(r["entry"], 16) for r in classes["const_source"]}
    )
    return {
        "schema": "camry-8965f3307000-function-family-census-v1",
        "target": {"software_id": "8965F3307000", "codeflash_sha256": SHA},
        "canonical_corpus": {
            "path": str(CORPUS.relative_to(ROOT)),
            "sha256": hashlib.sha256(CORPUS.read_bytes()).hexdigest(),
        },
        "summary": {
            "default_named_functions": len(default_named),
            "distinct_normalized_shapes": classes["shape_count"],
            "duplicate_cluster_count": len(classes["duplicate_clusters"]),
            "duplicate_cluster_members": sum(len(v) for v in classes["duplicate_clusters"].values()),
            "idiom_class_counts": {
                "return_only_stub": len(classes["ret_only"]),
                "far_call_trampoline": len(classes["trampolines"]),
                "single_constant_publisher": len(classes["publisher1"]),
                "paired_constant_publisher": len(classes["publisher2"]),
                "constant_source": len(classes["const_source"]),
            },
            "idiom_class_members": len(idiom_members),
        },
        "byte_gates": {
            "return_only_stub": f"body==2 && bytes=={RETURN_ONLY_BYTES}",
            "far_call_trampoline": f"body==12 && prefix=={TRAMPOLINE_HEAD} && suffix=={TRAMPOLINE_TAIL} && single callee",
            "single_constant_publisher": "exactly one `DAT_x = literal;` statement",
            "paired_constant_publisher": "exactly two `DAT_x = literal;` statements",
            "constant_source": "exactly one `return literal;` statement",
        },
        "classes": {
            "return_only_stub": classes["ret_only"],
            "far_call_trampoline": classes["trampolines"],
            "single_constant_publisher": classes["publisher1"],
            "paired_constant_publisher": classes["publisher2"],
            "constant_source": classes["const_source"],
        },
        "evidence_note": (
            "Idiom membership is byte/shape-verified against the exact image and "
            "canonical corpus; family-propagated names derived from this census are "
            "structural hypotheses, not executed or OEM-verified semantics."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ns = ap.parse_args()
    data = build()
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if ns.output.exists() and ns.output.read_text() == text:
        print(f"unchanged: {ns.output}")
        return 0
    ns.output.write_text(text)
    print(f"wrote {ns.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
