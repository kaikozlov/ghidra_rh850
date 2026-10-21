"""Promote differential agreements and restore the complete retained bank."""
from __future__ import annotations

from pathlib import Path
from tools import REPO_ROOT
from tools.targets.camry.decomp.tree import COMMON_HEADER, ROOT
from tools.targets.camry.decomp.syntax import _c_signature
import json
from tools.targets.camry.decomp.lifting.graph import load_image
from tools.targets.camry.decomp.tree import load_matched
from tools.targets.camry.decomp.tree import load_symbols
import re
import subprocess
import time
from tools.targets.camry.decomp.c_text import _c_calls, _split_args
from tools.targets.camry.decomp.execution.host_rewrite import _fill_local_arrays, _seed_incoming_locals
from tools.targets.camry.decomp.execution.link import _body_closure, _linkable, _prototypes, _undefined_symbols
from tools.targets.camry.decomp.execution.model import Planned
from tools.targets.camry.decomp.sources import _src_definitions, load_c_bodies, retained_paths, write_retained


def _reachable_stubs(
    planned: list[tuple[Planned, list[dict]]],
    support: list[str],
    bodies: dict[str, str],
    stubs: dict[str, str],
) -> list[str]:
    wanted: list[str] = []
    seen: set[str] = set()
    pending = list(support) + [item.name for item, _rows in planned]
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        referenced = set(re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", bodies.get(name, "")))
        referenced.update(_c_calls(bodies.get(name, "")))
        for callee in referenced:
            if callee in stubs and callee not in wanted:
                wanted.append(callee)
            elif callee in bodies:
                pending.append(callee)
    return wanted


def _signature_key(code: str) -> str:
    """Return and parameter types, with typedef aliases folded together.

    A uint body can replace a uint32_t body. A void body cannot replace an
    int body: the host compile rejects that as a conflicting type.
    """
    aliases = (
        ("unsigned int", "uint32_t"),
        ("unsigned short", "uint16_t"),
        ("unsigned char", "uint8_t"),
        ("undefined4", "uint32_t"),
        ("undefined2", "uint16_t"),
        ("undefined1", "uint8_t"),
        ("int32_t", "int"),
        ("int16_t", "short"),
        ("int8_t", "schar"),
        ("uint", "uint32_t"),
        ("ulong", "uint32_t"),
        ("ushort", "uint16_t"),
        ("uchar", "uint8_t"),
        ("byte", "uint8_t"),
    )

    def canon(text: str) -> str:
        text = " ".join(text.replace("*", " * ").split())
        for source, dest in aliases:
            text = re.sub(rf"\b{source}\b", dest, text)
        return text

    signature = _c_signature(code)
    opening = signature.find("(")
    closing = signature.rfind(")")
    if opening < 0 or closing < opening:
        return canon(signature)
    head = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\s*$", "", signature[:opening]).strip()
    body = signature[opening + 1:closing].strip()
    params: list[str] = []
    if body and body != "void":
        for part in _split_args(body):
            stripped = re.sub(r"\b[A-Za-z_][A-Za-z0-9_]*\s*$", "", part).strip()
            params.append(canon(stripped or part))
    return canon(head) + "(" + ",".join(params) + ")"


def _refresh_bodies(
    retained: dict[str, str], bodies: dict[str, str], refresh: set[str] | None = None,
    *, reverified: set[str] | None = None,
) -> dict[str, str]:
    """Refresh converted support and explicitly reverified retained bodies."""
    by_name: dict[str, set[str]] = {}
    for row in load_matched():
        by_name.setdefault(row["name"], set()).add(row["status"])
    refreshed = dict(retained)
    for name, chunk in retained.items():
        statuses = by_name.get(name, set())
        blocked = bool(statuses & {"equivalent", "byte-matched"})
        allowed = not blocked and "converted" in statuses
        fresh = bodies.get(name)
        if (
            (allowed or (blocked and refresh is not None and name in refresh))
            and fresh is not None
            and fresh.strip() != chunk.strip()
            and (
                allowed
                or name in (reverified or ())
                or _signature_key(chunk) == _signature_key(fresh)
            )
        ):
            refreshed[name] = fresh
    return refreshed


_PTR_MACRO = re.compile(
    r"#define\s+([A-Za-z_][A-Za-z0-9_]*)\s+"
    r"\(\*\(\(volatile uint32_t \*\)camry_host_ptr\((0x[0-9A-Fa-f]+)u?\)\)\)"
)


_INDIRECT_ARG = re.compile(
    r"camry_indirect\(\(uint32_t\)\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\)"
)


_UNRESOLVED_INDIRECT = re.compile(r"unresolved camry indirect 0x([0-9A-Fa-f]+)")


def _constant_indirect_targets() -> dict[str, str]:
    """A ROM function-pointer macro maps to the function whose address it holds."""
    cached = getattr(_constant_indirect_targets, "cached", None)
    if cached is not None:
        return cached
    header = COMMON_HEADER
    if not header.exists():
        _constant_indirect_targets.cached = {}
        return {}
    code = load_image()
    by_addr: dict[int, str] = {}
    for row in load_symbols():
        by_addr.setdefault(int(row["addr"], 16), row["name"])
    found: dict[str, str] = {}
    for name, slot in _PTR_MACRO.findall(header.read_text(encoding="utf-8")):
        addr = int(slot, 16)
        if addr < 0 or addr + 4 > len(code):
            continue
        target = int.from_bytes(code[addr:addr + 4], "little")
        function = by_addr.get(target)
        if function:
            found[name] = function
    _constant_indirect_targets.cached = found
    return found


def _indirect_targets(names: list[str], bodies: dict[str, str]) -> list[str]:
    """Functions a constant camry_indirect call reaches, which the table must link.

    Direct callees are scanned too. A promoted function often calls a helper
    that is already in the retained library, and that helper is the one that
    loads the ROM function pointer.
    """
    targets = _constant_indirect_targets()
    extra: list[str] = []
    scanned: set[str] = set()
    queued = set(names)
    pending = list(names)
    while pending:
        name = pending.pop()
        if name in scanned:
            continue
        scanned.add(name)
        body = bodies.get(name)
        if body is None:
            continue
        for macro in _INDIRECT_ARG.findall(body):
            function = targets.get(macro)
            if function is None or function in queued or function not in bodies:
                continue
            queued.add(function)
            extra.append(function)
            pending.append(function)
        for callee in _c_calls(body):
            if callee in queued or callee not in bodies:
                continue
            queued.add(callee)
            pending.append(callee)
    return extra


def _names_at_addresses(addresses: set[int]) -> list[str]:
    """Function names for code addresses a retained camry_indirect could not resolve."""
    by_addr = getattr(_names_at_addresses, "by_addr", None)
    if by_addr is None:
        by_addr = {}
        for row in load_symbols():
            by_addr.setdefault(int(row["addr"], 16), row["name"])
        _names_at_addresses.by_addr = by_addr
    found: list[str] = []
    for address in addresses:
        name = by_addr.get(address)
        if name and name not in found:
            found.append(name)
    return found


def _with_indirect_support(
    names: list[str], support: list[str], bodies: dict[str, str],
) -> list[str]:
    """Support plus the constant indirect callees the retained table must link."""
    merged = list(support)
    have = set(merged)
    targets = [
        name for name in _indirect_targets([*merged, *names], bodies)
        if name not in have
    ]
    for name in _body_closure(targets, bodies):
        if name in have:
            continue
        have.add(name)
        merged.append(name)
    return merged


def _promote(
    planned: list[tuple[Planned, list[dict]]],
    support: list[str],
    bodies: dict[str, str],
    stubs: dict[str, str] | None = None,
) -> None:
    from tools.targets.camry.decomp.conversion.rewrite_types import _rewrite_merged_call_results, _rewrite_packed_stack, _rewrite_scalar_host_indexes, _rewrite_inlined_mmio
    from tools.targets.camry.decomp.conversion.rewrite_context import _rewrite_paired_gpr_context
    from tools.targets.camry.decomp.runtime import _rewrite_system_inputs
    from tools.targets.camry.decomp.conversion.rewrite_abi import _rewrite_lost_arguments, _rewrite_surviving_extraouts, _rewrite_recovered_arguments
    from tools.targets.camry.decomp.layout import _hand_param_types
    from tools.targets.camry.decomp.conversion.rewrite_pointer import _rewrite_pointer_arguments, _rewrite_int_to_pointer
    from tools.targets.camry.decomp.syntax import _signature_param_types, _pointer_names
    from tools.targets.camry.decomp.abi import _widen_signature
    from tools.targets.camry.decomp.conversion.rewrite_memory import _rewrite_firmware_call_wrap
    from tools.targets.camry.decomp.declarations import _common_header

    retained, _duplicates = load_c_bodies(retained_paths())
    reverified = {item.name for item, _scenarios in planned}
    refresh = set(support) | reverified
    verified = {
        row["name"] for row in load_matched()
        if row.get("status") in {"equivalent", "byte-matched"}
    }
    prepared = {}
    for name, body in bodies.items():
        # Ordinary refresh supplies the actual retained body. Recover its
        # native ABI here so the existing repaired-body gate sees the change.
        body = _rewrite_recovered_arguments(_widen_signature(body))
        if "stack_record_" in body:
            body = _rewrite_packed_stack(body)
        if "camry_r10_result" in body:
            body = _rewrite_merged_call_results(body)
        if "camry_host_ptr" in body:
            body = _rewrite_scalar_host_indexes(body)
        body = _rewrite_surviving_extraouts(body)
        body = _rewrite_lost_arguments(body)
        body = _rewrite_inlined_mmio(body)
        body = _rewrite_system_inputs(body)
        body = _rewrite_paired_gpr_context(body)
        body = _rewrite_firmware_call_wrap(body)
        if "(code *)camry_host_ptr" in body:
            body = _rewrite_int_to_pointer(
                body, _pointer_names(_c_signature(body), body), known_only=True,
            )
        prepared[name] = body
    param_types = {
        name: _signature_param_types(_c_signature(body)) for name, body in prepared.items()
    }
    param_types.update(_hand_param_types())
    prepared = {
        name: _rewrite_pointer_arguments(body, param_types) for name, body in prepared.items()
    }
    repaired = {name for name in verified if name in prepared and prepared[name] != bodies[name]}
    refresh.update(repaired)
    reverified.update(repaired)
    for name in refresh:
        if name in prepared and name not in verified:
            prepared[name] = _fill_local_arrays(_seed_incoming_locals(prepared[name]))
    retained = _refresh_bodies(retained, prepared, refresh, reverified=reverified)
    # src/*.c is already linked by the verifier. Emitting those names again
    # fails the link with a duplicate symbol and drops the whole batch.
    have = set(retained) | _src_definitions()
    support = list(dict.fromkeys((
        *support, *_body_closure(sorted(_c_calls("\n".join(retained.values()))), prepared),
    )))
    # The host compare seeds incoming registers and fills stack arrays. Store
    # that form for names that are not already verified, so the verifier runs
    # the same locals. Verified bodies already match without those seeds.
    def host_locals(name: str, body: str) -> str:
        if name in verified:
            return body
        return _fill_local_arrays(_seed_incoming_locals(body))

    for name in support:
        if name in have:
            continue
        retained[name] = host_locals(name, prepared[name])
        have.add(name)
    for item, _scenarios in sorted(planned, key=lambda row: row[0].address):
        if item.name in have:
            continue
        retained[item.name] = host_locals(item.name, prepared[item.name])
        have.add(item.name)
    # A refreshed body can call a prototype that is outside this closure.
    # Emit every requested stub; reachability alone misses that reference.
    for name in dict.fromkeys((*_reachable_stubs(planned, support, bodies, stubs or {}), *(stubs or {}))):
        if name in have or name not in (stubs or {}):
            continue
        signature = stubs[name]
        retained[name] = signature.rstrip() + "\n{\n  __builtin_trap();\n}\n"
        have.add(name)
    # Declarations change with promoted bodies, never merely with candidate
    # generation. The trial verifier snapshots this header with the source bank.
    signatures = _prototypes(COMMON_HEADER)
    signatures.update({name: _c_signature(body) for name, body in retained.items()})
    COMMON_HEADER.write_text(
        _common_header("\n".join(retained.values()), signatures), encoding="utf-8",
    )
    write_retained(retained)
    if not planned:
        return

    matched_path = ROOT / "matched.jsonl"
    promoted = {item.address: item for item, _scenarios in planned}
    lines = []
    for line in matched_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        item = promoted.get(int(row["addr"], 16))
        if item is not None:
            row = {
                "addr": row["addr"],
                "name": row["name"],
                "status": "equivalent",
                "form": "corpus",
                "signature": item.signature,
            }
            line = json.dumps(row, separators=(", ", ": "))
        lines.append(line)
    matched_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    oracle_rows = ROOT / "oracles.jsonl"
    with oracle_rows.open("a", encoding="utf-8") as handle:
        for _item, scenarios in planned:
            for scenario in scenarios:
                handle.write(json.dumps(scenario, separators=(",", ":")) + "\n")


def _restore(snapshots: dict[Path, str | None]) -> None:
    # Restore the whole bank, including any windows created after the snapshot.
    for path in retained_paths():
        if path not in snapshots:
            path.unlink()
    for path, text in snapshots.items():
        if text is None:
            if path.exists():
                path.unlink()
            continue
        path.write_text(text, encoding="utf-8")


def _verify(only: list[str] | None = None) -> str | None:
    """Run the retained suite once.

    ``only`` rechecks those functions' own oracles. The object cache makes an
    unchanged shard free, so this second launch does not rebuild the library.
    """
    command = ["uv", "run", "--locked", "python", "tests/targets/camry/verify_camry_decomp.py"]
    if only:
        path = REPO_ROOT / "build" / "tmp" / "camry-verify-only.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(sorted(set(only))) + "\n", encoding="utf-8")
        command.append(f"--only-file={path}")
    started = time.perf_counter()
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed = time.perf_counter() - started
    scope = f"{len(set(only))} functions" if only else "full"
    print(f"verifier {scope} {elapsed:.0f}s", flush=True)
    log_path = REPO_ROOT / "build" / "tmp" / "camry-oracle-verify.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text((result.stderr or "") + "\n" + (result.stdout or ""), encoding="utf-8")
    if result.returncode == 0:
        return None
    blob = (result.stderr or "") + "\n" + (result.stdout or "")
    missing = _undefined_symbols(blob)
    err = [line for line in (result.stderr or "").splitlines() if line.strip()]
    fails = [line for line in (result.stdout or "").splitlines() if line.startswith("FAIL ")]
    shown = (err[-4:] + fails) or (result.stdout or "").strip().splitlines()[-6:]
    text = " | ".join(shown)
    if missing:
        text = "undefined:" + ",".join(missing) + "\n" + text
    print(text, flush=True)
    return text


# (function, scenario) pairs that already fail on HEAD. A later verify
# drops a candidate only when it adds a pair, or it calls or is called by
# a function that added one.
_BASELINE_FAILS: set[tuple[str, str]] | None = None


def _fail_pairs(error: str) -> set[tuple[str, str]]:
    pairs: set[tuple[str, str]] = set()
    for match in re.finditer(r"(?:^|\|\s*)FAIL (\S+) (\S+)", error):
        pairs.add((match.group(1), match.group(2)))
    missing = re.search(r"matched functions with no executed oracle: ([^\n|]+)", error)
    if missing:
        for part in missing.group(1).split(","):
            name = part.strip()
            if name:
                pairs.add((name, "no-executed-oracle"))
    return pairs


def _new_fail_names(error: str) -> list[str]:
    baseline = _BASELINE_FAILS or set()
    found: list[str] = []
    for name, scenario in _fail_pairs(error):
        if (name, scenario) in baseline:
            continue
        found.append(name)
    return list(dict.fromkeys(found))


def _implicated(
    error: str, batch: set[str], bodies: dict[str, str],
) -> tuple[set[str], set[str]]:
    """Candidates a new failure touches.

    A name already failing on HEAD does not take a new function with it.
    A candidate still drops when its own scenario fails, when it calls a
    function with a new failure, or when a newly failing function calls it.
    """
    new_names = set(_new_fail_names(error))
    bad: set[str] = set()
    callers: set[str] = set()
    for name in new_names:
        if name in batch:
            bad.add(name)
            continue
        callees = _c_calls(bodies.get(name, "")) & batch
        if callees:
            bad |= callees
            callers.add(name)
    for name in batch:
        if _c_calls(bodies.get(name, "")) & new_names:
            bad.add(name)
    return bad, callers


def _keep_verified(
    passed: list[tuple[Planned, list[dict]]],
    snapshots: dict[Path, str | None],
    bodies: dict[str, str],
    defined: set[str],
    symbols: set[str],
    macros: set[str],
    reject,
    examples: dict[str, str],
    stubs: dict[str, str] | None = None,
    forced: tuple[str, ...] = (),
    seen_indirect: frozenset[int] = frozenset(),
    linked: list[str] | None = None,
) -> list[tuple[Planned, list[dict]]]:
    global _BASELINE_FAILS
    if not passed:
        return []
    if _BASELINE_FAILS is None:
        base_error = _verify()
        _BASELINE_FAILS = _fail_pairs(base_error or "")
    kept, support = _linkable(
        [item.name for item, _rows in passed], bodies, defined, symbols, macros,
    )
    support = list(dict.fromkeys((*forced, *support)))
    runnable = [(item, rows) for item, rows in passed if item.name in kept]
    support = _with_indirect_support(
        [item.name for item, _rows in runnable], support, bodies,
    )
    for item, _rows in passed:
        if item.name not in kept:
            reject("host-link", item.name, address=item.address)
    if not runnable:
        return []
    _restore(snapshots)
    _promote(runnable, support, bodies, stubs)
    error = _verify()
    if error is None:
        return runnable
    # A missing indirect target or an undefined symbol changes the linked set.
    # Run the complete scenario set once more against the newly linked binary.
    unresolved = {int(item, 16) for item in _UNRESOLVED_INDIRECT.findall(error)} - seen_indirect
    wanted = [name for name in _names_at_addresses(unresolved) if name in bodies]
    closure = [
        name for name in _body_closure(wanted, bodies)
        if name not in support and name not in forced
    ]
    if closure:
        if linked is not None:
            linked.extend(name for name in closure if name not in linked)
        _restore(snapshots)
        return _keep_verified(
            runnable, snapshots, bodies, defined, symbols, macros, reject, examples,
            stubs, tuple(dict.fromkeys((*forced, *closure))),
            seen_indirect | unresolved, linked,
        )
    if error.startswith("undefined:"):
        header, _, detail = error.partition("\n")
        missing = [name for name in header.split(":", 1)[1].split(",") if name]
        prototypes = _prototypes(COMMON_HEADER)
        have = set(forced) | set(support) | defined
        extra = list(forced)
        stub_map = dict(stubs or {})
        grew = False
        for name in missing:
            if name in have or name in stub_map:
                continue
            if name in bodies:
                extra.append(name)
                have.add(name)
                grew = True
            elif name in prototypes:
                stub_map[name] = prototypes[name]
                grew = True
        if grew:
            _restore(snapshots)
            return _keep_verified(
                runnable, snapshots, bodies, defined, symbols, macros, reject, examples,
                stub_map, tuple(extra), seen_indirect, linked,
            )
        error = detail or error
    dupes = set(re.findall(
        r"(?:redefinition of '|duplicate symbol '_)([A-Za-z_][A-Za-z0-9_]*)",
        error,
    ))
    if dupes:
        def reaches(name: str, seen: set[str] | None = None) -> bool:
            if name in dupes:
                return True
            if name not in bodies:
                return False
            seen = set() if seen is None else seen
            if name in seen:
                return False
            seen.add(name)
            return any(reaches(callee, seen) for callee in _c_calls(bodies[name]))

        bad = [item for item, _rows in runnable if reaches(item.name)]
        if bad and len(bad) < len(runnable):
            for item in bad:
                reject("verifier", item.name, address=item.address)
            examples["verifier"] = error[:180]
            rest = [(item, rows) for item, rows in runnable if item not in bad]
            _restore(snapshots)
            return _keep_verified(
                rest, snapshots, bodies, defined, symbols, macros, reject, examples, stubs, forced,
                seen_indirect, linked,
            )
    if "FAIL " not in error and "matched functions with no executed oracle" not in error:
        for item, _rows in runnable:
            reject("verifier", item.name, address=item.address)
        examples["verifier"] = error[:180]
        return []
    # The full suite already ran. Recheck only the new functions that failed
    # and the callers whose retained oracle failed with them. An unrelated
    # retained failure does not start another full run.
    batch = {item.name for item, _rows in runnable}
    failed, callers = _implicated(error, batch, bodies)
    if not failed:
        return runnable
    scoped = _verify(sorted(failed | callers))
    if scoped is None:
        return runnable
    still, _still_callers = _implicated(scoped, batch, bodies)
    drop = still or failed
    for item, _rows in runnable:
        if item.name in drop:
            reject("verifier", item.name, address=item.address)
    examples["verifier"] = scoped[:180]
    return [(item, rows) for item, rows in runnable if item.name not in drop]

