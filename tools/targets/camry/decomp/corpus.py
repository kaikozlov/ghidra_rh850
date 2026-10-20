"""Corpus generation, native compilation, and candidate-tree maintenance."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from tools import REPO_ROOT
from concurrent.futures import ThreadPoolExecutor
import json
import re
from tools.project.analysis_target import target as resolve_target
import subprocess
import tempfile

from tools.targets.camry.decomp import layout, syntax, tree
from tools.targets.camry.decomp.conversion import rewrite, rewrite_pointer
from .declarations import _common_header





def _function_at_line(selected: dict[int, dict], rendered: str, line_number: int) -> str | None:
    lines = rendered.splitlines()
    owners: list[tuple[int, str]] = []
    for row in selected.values():
        needle = row["name"] + "("
        for index, line in enumerate(lines, 1):
            if needle in line and not line.endswith(";"):
                owners.append((index, row["name"]))
                break
    owners.sort()
    found = None
    for start, name in owners:
        if start <= line_number:
            found = name
        else:
            break
    return found


_CC_FLAGS = [
    "-std=c11", "-c", "-O2", "-Wall", "-Wextra", "-Werror", "-fwrapv",
    "-Wno-unused-variable", "-Wno-unused-parameter",
    "-Wno-unused-function", "-Wno-unused-label",
    "-Wno-pointer-to-int-cast", "-Wno-int-to-pointer-cast",
    "-Wno-bitwise-op-parentheses", "-Wno-sign-compare", "-Wno-parentheses",
    "-Wno-pointer-sign", "-Wno-incompatible-pointer-types",
    "-Wno-unused-but-set-variable",
    "-Wno-uninitialized",
    "-Wno-deprecated-non-prototype",
    "-ferror-limit=0",
    "-DCAMRY_HOST",
]


def _prefer_bodies(functions: list[dict]) -> dict[str, dict]:
    chosen: dict[str, dict] = {}
    for row in functions:
        current = chosen.get(row["name"])
        if current is not None and layout._self_call_count(row) > layout._self_call_count(current):
            continue
        chosen[row["name"]] = row
    return chosen


def _failure_class(message: str) -> str:
    match = re.search(r"use of undeclared identifier '([^']+)'", message)
    if match:
        ident = match.group(1)
        if re.fullmatch(r"unaff_\w+", ident):
            shape = "unaff_*"
        elif re.fullmatch(r"extraout_\w+", ident):
            shape = "extraout_*"
        elif re.fullmatch(r"in_r\d+", ident):
            shape = "in_r*"
        elif ident.startswith("Ram"):
            shape = "Ram*"
        elif ident.startswith(("CONCAT", "SUB", "SBORROW", "OVERFLOW")):
            shape = ident.split("_", 1)[0] + "*"
        elif ident.startswith("in_"):
            shape = ident
        else:
            shape = ident
        return f"undeclared identifier {shape}"
    text = re.sub(r"\(aka '[^']*'\)", "", message)
    text = re.sub(r"'[^']*'", "'…'", text)
    text = re.sub(r"\b0x[0-9A-Fa-f]+\b", "N", text)
    text = re.sub(r"\b\d+\b", "N", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:200]




def _compile_file(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["cc", *_CC_FLAGS, "-I", str(tree.ROOT / "include"), "-o", "/dev/null", str(path)],
        text=True,
        capture_output=True,
    )


def _isolate_errors(name: str, body: str, directory: Path) -> list[str]:
    path = directory / f"one-{name}.c"
    path.write_text('#include "common.h"\n\n' + body, encoding="utf-8")
    result = _compile_file(path)
    path.unlink(missing_ok=True)
    if result.returncode == 0:
        return []
    messages = [
        line.split("error:", 1)[1].strip()
        for line in (result.stderr or "").splitlines()
        if "error:" in line
    ]
    return messages or [(result.stderr or "compile failed")[:300]]


def _shard_errors(
    path: Path, selected: dict[int, dict], rendered: str,
) -> dict[str, list[str]]:
    result = _compile_file(path)
    found: dict[str, list[str]] = {}
    if result.returncode == 0:
        return found
    for line in (result.stderr or "").splitlines():
        if "error:" not in line:
            continue
        match = re.search(rf"{re.escape(path.name)}:(\d+):", line)
        if match is None:
            found.setdefault("", []).append(line.split("error:", 1)[1].strip())
            continue
        name = _function_at_line(selected, rendered, int(match.group(1)))
        message = line.split("error:", 1)[1].strip()
        found.setdefault(name or "", []).append(message)
    if result.returncode != 0 and not found:
        found[""] = [(result.stderr or "compile failed")[:500]]
    return found


def _write_statuses(compiled_names: set[str]) -> tuple[int, int, int]:
    path = tree.ROOT / "matched.jsonl"
    kept: list[str] = []
    kept_addrs: set[int] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") in tree._CHECKED_STATUS:
            kept.append(line)
            kept_addrs.add(tree._address(row["addr"]))
    hand = layout._prototype_names()
    extra: list[dict] = []
    converted = 0
    unconvertible = 0
    for symbol in tree.load_symbols():
        addr = tree._address(symbol["addr"])
        if addr in kept_addrs:
            continue
        status = "converted" if symbol["name"] in compiled_names or symbol["name"] in hand else "unconvertible"
        if status == "converted":
            converted += 1
        else:
            unconvertible += 1
        extra.append({
            "addr": hex(addr),
            "name": symbol["name"],
            "status": status,
        })
    extra.sort(key=lambda row: int(row["addr"], 16))
    payload = kept + [
        json.dumps(row, separators=(", ", ": "))
        for row in extra
    ]
    path.write_text("\n".join(payload) + "\n", encoding="utf-8")
    return len(kept), converted, unconvertible


def _compile_tree(functions: list[dict]) -> tuple[set[str], Counter[str], list[str]]:
    from .sources import load_c_bodies, retained_paths

    retained, _duplicates = load_c_bodies(retained_paths())
    verified = {
        row["name"] for row in tree.load_matched() if row.get("status") in tree._CHECKED_STATUS
    }
    retained = {name: body for name, body in retained.items() if name in verified}
    hand = layout._prototype_names()
    chosen = _prefer_bodies(functions)
    rewritten: dict[str, str] = {}
    signatures: dict[str, str] = {}
    rows_by_name: dict[str, dict] = {}
    failed_rewrite: list[str] = []
    for name, row in chosen.items():
        if name in hand:
            continue
        try:
            body = retained[name] if name in retained else rewrite._rewrite_body(row["decompiled_c"])
            signatures[name] = syntax._c_signature(body)
        except (ValueError, IndexError, KeyError) as exc:
            failed_rewrite.append(f"{name} {type(exc).__name__}")
            continue
        rewritten[name] = body
        rows_by_name[name] = row
    if not rewritten:
        return set(), Counter({"rewrite failed": len(failed_rewrite)}), failed_rewrite
    param_types = {
        name: syntax._signature_param_types(signature) for name, signature in signatures.items()
    }
    param_types.update(layout._hand_param_types())
    for name in list(rewritten):
        if name in retained and rewritten[name] == retained[name]:
            continue
        try:
            rewritten[name] = rewrite_pointer._rewrite_pointer_arguments(rewritten[name], param_types)
        except (ValueError, IndexError, KeyError) as exc:
            failed_rewrite.append(f"{name} {type(exc).__name__}")
            del rewritten[name]
            signatures.pop(name, None)
            rows_by_name.pop(name, None)

    def shards_of(names: set[str]) -> dict[str, dict[int, dict]]:
        grouped: dict[str, dict[int, dict]] = {}
        for name in names:
            row = rows_by_name[name]
            addr = int(row["entry_addr"], 16)
            grouped.setdefault(f"{addr >> 14:03x}", {})[addr] = row
        return grouped

    def prototype_at(header: str, line_number: int) -> str | None:
        rows = header.splitlines()
        if line_number < 1 or line_number > len(rows):
            return None
        match = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", rows[line_number - 1])
        if match is None or match.group(1) not in active:
            return None
        return match.group(1)

    with tempfile.TemporaryDirectory(prefix="camry-tree-") as tmp:
        root = Path(tmp)
        active = set(rewritten)
        hidden: set[str] = set()
        blame: dict[str, list[str]] = {}
        header_errors: list[str] = []
        text = "\n".join(rewritten[name] for name in sorted(rewritten))
        for _round in range(8):
            header_errors = []
            print(f"compile {_round + 1} {len(active)}")
            header = _common_header(
                text, {name: signatures[name] for name in signatures if name not in hidden},
            )
            (root / "common.h").write_text(header, encoding="utf-8")
            probe = root / "probe.c"
            probe.write_text('#include "common.h"\n', encoding="utf-8")
            probe_result = _compile_file(probe)
            dropped: set[str] = set()
            if probe_result.returncode != 0:
                header_errors = []
                for line in (probe_result.stderr or "").splitlines():
                    if "error:" not in line:
                        continue
                    message = line.split("error:", 1)[1].strip()
                    match = re.search(r"common\.h:(\d+):", line)
                    name = prototype_at(header, int(match.group(1))) if match else None
                    if name:
                        dropped.add(name)
                        hidden.add(name)
                        blame[name] = [message]
                    else:
                        header_errors.append(message)
                if dropped:
                    active -= dropped
                    print(f"dropped {len(dropped)}")
                    continue
                break
            grouped = shards_of(active - dropped)
            rendered_shards: dict[str, tuple[Path, dict[int, dict], str]] = {}
            for shard, selected in grouped.items():
                parts = ['#include "common.h"', ""]
                for addr in sorted(selected):
                    parts.append(rewritten[selected[addr]["name"]])
                    if not rewritten[selected[addr]["name"]].endswith("\n"):
                        parts.append("")
                rendered = "\n".join(parts) + "\n"
                path = root / f"{shard}.c"
                path.write_text(rendered, encoding="utf-8")
                rendered_shards[shard] = (path, selected, rendered)
            suspects: list[tuple[str, str]] = []
            shard_blame: dict[str, list[str]] = {}
            with ThreadPoolExecutor(max_workers=8) as pool:
                compiled = pool.map(
                    lambda item: (item[0], _shard_errors(*item[1])),
                    rendered_shards.items(),
                )
                for shard, errors in compiled:
                    selected = rendered_shards[shard][1]
                    if not errors:
                        continue
                    if set(errors) == {""}:
                        header_errors.extend(errors[""])
                        continue
                    for name, messages in errors.items():
                        if name:
                            shard_blame.setdefault(name, []).extend(messages)
                    for row in selected.values():
                        suspects.append((row["name"], rewritten[row["name"]]))
            if header_errors and not suspects and not dropped:
                break
            print(f"isolate {len(suspects)}")
            with ThreadPoolExecutor(max_workers=8) as pool:
                isolated = pool.map(
                    lambda item: (item[0], _isolate_errors(item[0], item[1], root)),
                    suspects,
                )
                for name, messages in isolated:
                    if messages:
                        dropped.add(name)
                        blame[name] = messages
            if not dropped:
                for name, messages in shard_blame.items():
                    if name in active:
                        dropped.add(name)
                        blame[name] = messages
            header_errors = []
            if not dropped:
                break
            active -= dropped
            print(f"dropped {len(dropped)}")
        else:
            header_errors.append("compile did not converge")
        classes: Counter[str] = Counter()
        if failed_rewrite:
            classes["rewrite failed"] = len(failed_rewrite)
        for name, messages in blame.items():
            if name in active or not messages:
                continue
            for kind in {_failure_class(message) for message in messages}:
                classes[kind] += 1
        if header_errors:
            for message in header_errors[:12]:
                print(f"header {message}")
            return set(), classes, failed_rewrite + [f"header {message}" for message in header_errors[:12]]
        tree.CANDIDATES.mkdir(parents=True, exist_ok=True)
        for stale in tree.CANDIDATES.glob("*.c"):
            stale.unlink()
        (tree.CANDIDATES / "common.h").write_text(
            _common_header(
                text, {name: signatures[name] for name in signatures if name not in hidden},
            ),
            encoding="utf-8",
        )
        for shard, selected in shards_of(active).items():
            parts = ['#include "common.h"', ""]
            for addr in sorted(selected):
                parts.append(rewritten[selected[addr]["name"]])
            (tree.CANDIDATES / f"{shard}.c").write_text("\n".join(parts) + "\n", encoding="utf-8")
        return active, classes, failed_rewrite


def cmd_corpus(_args: argparse.Namespace) -> int:
    from tools.project.pseudo import load_corpus

    metadata = resolve_target(tree.TARGET)[1]
    _meta, functions = load_corpus(REPO_ROOT / metadata["decompiler_corpus"])
    print(f"functions {len(functions)}")
    compiled, classes, failures = _compile_tree(functions)
    header_failed = any(item.startswith("header ") for item in failures)
    if header_failed:
        verified = converted = unconvertible = 0
    else:
        verified, converted, unconvertible = _write_statuses(compiled)
    print(f"compiled {len(compiled)}")
    print(f"oracle-verified {verified}")
    print(f"converted-unverified {converted}")
    print(f"unconvertible {unconvertible}")
    if failures:
        print(f"rewrite-failed {len(failures)}")
    print("failure classes:")
    for kind, count in classes.most_common(30):
        print(f"  {count:5d}  {kind}")
    return 0 if not failures or compiled else 1
