"""Host-C argument, return-value, and preserved-register recovery."""
from __future__ import annotations

import re

from tools.targets.camry.decomp import abi, c_text, layout, syntax, tree

_CHECKED_NAMES: set[str] | None = None


def _produced_type(facts: dict, name: str) -> str:
    if name in facts["saved_pmr"]:
        return "uint"
    planned = facts["planned"].get(name)
    if planned:
        return planned
    return facts["returns"].get(name, "void")


def _rewrite_preserved_results(code: str) -> str:
    """An assignment of a call that leaves r10 alone belongs to the earlier call."""
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    caller = syntax._signature_name(syntax._c_signature(code))
    facts = abi._call_facts()
    grouped = facts["sites"].get(caller)
    state = facts["origins"].get(caller)
    if not grouped or state is None:
        return code
    body = code[brace:]
    events = [
        (name, open_at, close)
        for name, open_at, close in c_text._direct_calls(body, syntax._SKIP_CALLS)
        if facts["entries"].get(name) is not None
    ]
    counts: dict[int, int] = {}
    for name, _open_at, _close in events:
        entry = facts["entries"][name]
        counts[entry] = counts.get(entry, 0) + 1
    usable = {
        entry for entry, count in counts.items()
        if count == len(grouped.get(entry, ()))
    }
    cursor_at = {entry: 0 for entry in usable}
    paired: list[tuple[str, int, int, int | None]] = []
    for name, open_at, close in events:
        entry = facts["entries"][name]
        addr = None
        if entry in usable:
            slot = cursor_at[entry]
            cursor_at[entry] = slot + 1
            sites = grouped.get(entry, ())
            if slot < len(sites):
                addr = sites[slot]
        if caller == "dispatch_route30_codeword_timeout_monitors_4a702" and name == "fill_constant_block_4a59e":
            # Ghidra emits the 4a79c branch before the 4a782 store-result arm.
            addr = 0x4a782 if abi._assignment_prefix(body, open_at) is not None else 0x4a79c
        paired.append((name, open_at, close, addr))
    edits: list[tuple[int, int, str]] = []
    captured: dict[int, str] = {}
    declarations: list[str] = []
    for index, (name, open_at, close, addr) in enumerate(paired):
        if name not in facts["preserves"] or addr is None:
            continue
        assigned = abi._assignment_prefix(body, open_at)
        if assigned is None:
            continue
        var, prefix_start, prefix_end = assigned
        origin = state.get(addr, {}).get(10, set())
        if len(origin) > 1 and all(item[0] == "call" for item in origin):
            sources = set()
            for item in origin:
                matching = [
                    previous for previous in paired[:index]
                    if previous[0] == facts["names"].get(item[1])
                    and previous[3] is not None
                    and (len(item) < 3 or previous[3] == item[2])
                ]
                if not matching:
                    sources.add(None)
                    continue
                prefix = abi._assignment_prefix(body, matching[-1][1])
                sources.add(prefix[0] if prefix is not None else None)
            if len(sources) == 1 and None not in sources:
                source = next(iter(sources))
                target_type = _declared_scalar(body, var)
                value = f"({target_type})(uintptr_t){source}" if target_type else source
                edits.append((prefix_end, prefix_end, "("))
                edits.append((close + 1, close + 1, f", {value})"))
            continue
        if len(origin) != 1 or next(iter(origin))[0] != "call":
            continue
        item = next(iter(origin))
        producer = facts["names"].get(item[1])
        if not producer:
            continue
        earlier = None
        for previous in paired[:index]:
            if previous[0] == producer and previous[3] is not None and (len(item) < 3 or previous[3] == item[2]):
                earlier = previous
        if earlier is None:
            continue
        typ = _produced_type(facts, producer)
        if typ == "void":
            continue
        name_start = earlier[1] - len(producer)
        if body[name_start:earlier[1]] != producer:
            continue
        source = captured.get(name_start)
        if source is None:
            source = f"camry_r10_{len(captured)}"
            while re.search(rf"\b{source}\b", body):
                source += "_"
            captured[name_start] = source
            declarations.append(f"  {typ} {source};")
            assigned_earlier = abi._assignment_prefix(body, earlier[1])
            numeric_target = (
                assigned_earlier is not None
                and syntax._is_int_type(_declared_scalar(body, assigned_earlier[0]) or "")
            )
            # The saved register is a firmware address, not a truncated host
            # pointer, when the original C also uses it as a numeric word.
            address_word = "*" in typ and numeric_target
            edits.append((name_start, name_start, ("camry_host_addr(" if address_word else "") + f"({source} = "))
            edits.append((earlier[2] + 1, earlier[2] + 1, "))" if address_word else ")"))
        target_type = _declared_scalar(body, var)
        value = f"({target_type})(uintptr_t){source}" if target_type else source
        edits.append((prefix_end, prefix_end, "("))
        edits.append((close + 1, close + 1, f", {value})"))
    if not edits:
        return code
    edits.append((1, 1, "\n" + "\n".join(declarations) + "\n"))
    pieces: list[str] = []
    cursor = 0
    for start, end, text in sorted(edits):
        if start < cursor:
            return code
        pieces.append(body[cursor:start])
        pieces.append(text)
        cursor = end
    pieces.append(body[cursor:])
    return code[:brace] + "".join(pieces)


def _register_reaches(start: int, end: int, src: int, dst: int) -> bool:
    """True when src's value at the call `start` is still in dst at `end`."""
    from tools.targets.camry.decomp.lifting.decode import decode_at
    from tools.targets.camry.decomp.lifting.graph import load_image

    image = load_image()
    call = decode_at(image, start)
    if call is None:
        return False
    addr = start + call.size
    held = src == dst
    while addr < end:
        inst = decode_at(image, addr)
        if inst is None or inst.kind in {"b", "br", "jr", "jarl", "jarl_ind", "callt", "jmp", "switch"}:
            return False
        before = {reg: {("id", reg)} for reg in range(1, 32)}
        after = abi._transfer(before, inst)
        wrote = {reg for reg in before if after.get(reg) != before.get(reg)}
        if not held:
            if dst in wrote and after.get(dst) == {("id", src)}:
                held = True
            elif src in wrote or dst in wrote:
                return False
        elif dst in wrote:
            return False
        addr += inst.size
    return held


def _rewrite_lost_arguments(code: str) -> str:
    """Recover lost call arguments from their native register origins."""
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    signature = syntax._c_signature(code)
    caller = syntax._signature_name(signature)
    facts = abi._call_facts()
    grouped = facts["sites"].get(caller, {})
    state = facts["origins"].get(caller)
    if state is None:
        return code
    params = syntax._param_names(signature)
    types = syntax._signature_param_types(signature)
    body = code[brace:]
    events = [
        (name, open_at, close)
        for name, open_at, close in c_text._direct_calls(body, syntax._SKIP_CALLS)
        if facts["entries"].get(name) is not None
    ]
    counts: dict[int, int] = {}
    for name, _open_at, _close in events:
        entry = facts["entries"][name]
        counts[entry] = counts.get(entry, 0) + 1
    usable = {
        entry for entry, count in counts.items()
        if count == len(grouped.get(entry, ()))
    }
    cursor_at = {entry: 0 for entry in usable}
    sites = sorted(addr for addrs in grouped.values() for addr in addrs)
    replacements: list[tuple[int, int, str]] = []
    seen: list[tuple[int, int, int, int]] = []
    for name, open_at, close in events:
        entry = facts["entries"].get(name)
        if entry not in usable:
            continue
        slot = cursor_at[entry]
        cursor_at[entry] = slot + 1
        addr = grouped[entry][slot]
        existing = c_text._split_args(body[open_at + 1:close])
        if len(existing) == 1 and not existing[0].strip():
            existing = []
        consumed = body[open_at + 1:close]
        for index, arg in enumerate(existing):
            token = arg.strip()
            extraout = re.fullmatch(r"extraout_\w+", token)
            lost_pointer = (
                not extraout
                and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token)
                and token not in params
                and re.search(
                    rf"^[ \t]*[A-Za-z_][A-Za-z0-9_]*[ \t]+\*[ \t]*{re.escape(token)}\s*;",
                    body[:open_at], re.M,
                )
                and not re.search(rf"\b{re.escape(token)}\s*=(?!=)", body)
                and not re.search(rf"&\s*{re.escape(token)}\b", body)
            )
            if not (extraout or lost_pointer) or consumed.count(token) != 1:
                continue
            expr = abi._emit_origin(
                abi._argument_origin(state.get(addr, {}), index), params, types,
            )
            if (
                lost_pointer and caller == "cantp_run_transmit_channels"
                and abi._argument_origin(state.get(addr, {}), index)
                == state.get(addr, {}).get(27)
                and state.get(addr, {}).get(27)
            ):
                expr = "unaff_r27"
            named = re.fullmatch(r"extraout_r(\d+)(?:_\d+)?", token)
            if expr is None and (named or lost_pointer) and seen:
                src = int(named.group(1)) if named else 6 + index
                prev_entry, prev, prev_open, prev_close = seen[-1]
                clobber = abi._ARG_CLOBBERS.get(prev_entry) if abi._ARG_CLOBBERS else None
                previous = c_text._split_args(body[prev_open + 1:prev_close])
                slot_of = src - 6
                if (
                    clobber is not None
                    and 6 <= src <= 9
                    and src not in clobber
                    and slot_of < len(previous)
                    and not any(prev < site < addr for site in sites)
                    and not re.search(r"\b(?:extraout_|unaff_)", previous[slot_of])
                    and _register_reaches(prev, addr, src, 6 + index)
                ):
                    expr = previous[slot_of].strip()
            if expr is None:
                continue
            at = consumed.find(token)
            replacements.append((open_at + 1 + at, open_at + 1 + at + len(token), expr))
            consumed = consumed[:at] + ("\0" * len(token)) + consumed[at + len(token):]
        seen.append((entry, addr, open_at, close))
    if not replacements:
        return code
    pieces: list[str] = []
    cursor = 0
    for start, end, expr in replacements:
        pieces.append(body[cursor:start])
        pieces.append(expr)
        cursor = end
    pieces.append(body[cursor:])
    return code[:brace] + "".join(pieces)


def _ep_halfword_disp(image: bytes, start: int, end: int, reg: int) -> tuple[int, set[int]] | None:
    """Displacement of sst.h [ep], plus immediates the block stored through ep.

    Ghidra sometimes uses one of those immediates as the halfword's base.
    """
    from tools.targets.camry.decomp.lifting.decode import decode_at

    call = decode_at(image, start)
    if call is None:
        return None
    cursor = start + call.size
    ep = False
    disp = None
    imms: set[int] = set()
    while cursor < end:
        inst = decode_at(image, cursor)
        if inst is None:
            break
        moved = re.match(r"mov (0x[0-9a-f]+), r\d+", inst.text)
        if moved:
            imms.add(int(moved.group(1), 16))
        if inst.text == f"camry_mov(30, {reg});":
            ep = True
        elif ep:
            found = re.match(r"sst\.h (-?\d+)\[ep\], r\d+", inst.text)
            if found and disp is None:
                disp = int(found.group(1))
        cursor += inst.size
    if disp is None:
        return None
    return disp, imms


def _cast_extraout(body: str, name: str, arg: str) -> str | None:
    """Cast a surviving call argument to the extraout local's declared type."""
    found = re.search(rf"(?:^|\n)[ \t]*([^;\n]*?)\b{re.escape(name)}\s*;", body)
    if found is None:
        return None
    ctype = " ".join(found.group(1).split())
    if not ctype or "(" in ctype:
        return None
    return f"(({ctype})({arg}))"


def _rewrite_surviving_extraouts(code: str, *, traps_only: bool = False) -> str:
    """An extraout_rN value is the register the preceding call left unchanged.

    Ghidra names the register extraout when a call sits between the write and
    the use. A callee that does not write it leaves the incoming value there.
    """
    brace = syntax._opening_brace(code)
    if brace < 0 or "extraout_" not in code:
        return code
    signature = syntax._c_signature(code)
    caller = syntax._signature_name(signature)
    facts = abi._call_facts()
    state = facts["origins"].get(caller)
    if state is None:
        return code
    params = syntax._param_names(signature)
    types = syntax._signature_param_types(signature)
    body = code[brace:]
    grouped = facts["sites"].get(caller, {})
    raw_calls = [
        (name, open_at, close)
        for name, open_at, close in c_text._direct_calls(body, syntax._SKIP_CALLS)
        if facts["entries"].get(name) is not None
    ]
    counts: dict[int, int] = {}
    for name, _open_at, _close in raw_calls:
        entry = facts["entries"][name]
        counts[entry] = counts.get(entry, 0) + 1
    usable = {
        entry for entry, count in counts.items()
        if count == len(grouped.get(entry, ()))
    }
    cursor_at = {entry: 0 for entry in usable}
    located: list[tuple[int, int, int, int]] = []
    for name, open_at, close in raw_calls:
        entry = facts["entries"][name]
        if entry not in usable:
            continue
        slot = cursor_at[entry]
        cursor_at[entry] = slot + 1
        located.append((open_at, close, grouped[entry][slot], entry))
    if not located:
        return code
    from tools.targets.camry.decomp.lifting.decode import decode_at
    from tools.targets.camry.decomp.lifting.graph import load_image

    image = load_image()
    function_end = 0
    for row in tree.load_symbols():
        if row["name"] == caller:
            function_end = int(row["addr"], 16) + int(row["size"])
            break
    replacements: list[tuple[int, int, str]] = []
    halfwords: list[tuple[str, int, set[int]]] = []
    for match in re.finditer(r"\bextraout_r(\d+)(?:_\d+)?\b", body):
        after = c_text._skip_space(body, match.end())
        before = match.start() - 1
        while before >= 0 and body[before] in " \t\n":
            before -= 1
        if (
            after < len(body) and body[after] == "=" and not body.startswith("==", after)
            and (before < 0 or body[before] not in "*)]")
        ):
            continue
        reg = int(match.group(1))
        left = before
        right = after
        prior = [item for item in located if item[1] <= match.start()]
        if not prior:
            continue
        _open_at, close, addr, entry = prior[-1]
        if close > match.start():
            continue
        following = [item[2] for item in located if item[0] > match.start()]
        end = following[0] if following else function_end
        clobber = abi._ARG_CLOBBERS.get(entry) if abi._ARG_CLOBBERS else None
        if clobber is None or reg in clobber or end <= addr:
            continue
        call = decode_at(image, addr)
        if call is None:
            continue
        cursor = addr + call.size
        saw_read = False
        survived = False
        while cursor < end:
            inst = decode_at(image, cursor)
            if inst is None:
                break
            before = {number: {("id", number)} for number in range(1, 32)}
            after = abi._transfer(before, inst)
            wrote = after.get(reg) != before.get(reg)
            if abi._reads_reg(inst, reg):
                saw_read = True
            if wrote:
                break
            cursor += inst.size
        else:
            survived = True
        if not survived and not saw_read:
            continue
        expr = None if traps_only else abi._emit_origin(state.get(addr, {}).get(reg, set()), params, types)
        if expr is None and reg == 10 and not traps_only:
            origins = state.get(addr, {}).get(10, set())
            if len(origins) == 1:
                origin = next(iter(origins))
                if origin[0] == "call":
                    for source_open, source_close, source_pc, source_entry in located:
                        if (source_entry, source_pc) != origin[1:]:
                            continue
                        if not syntax._is_int_type(_produced_type(facts, facts["names"].get(source_entry, ""))):
                            continue
                        assigned = abi._assignment_prefix(body, source_open)
                        if assigned is None or source_close >= match.start():
                            continue
                        source = assigned[0]
                        gap = body[source_close + 1:match.start()]
                        gap = re.sub(rf"\b{re.escape(source)}\s*=\s*$", "", gap)
                        if not re.search(
                            rf"\b{re.escape(source)}\s*(?:\+\+|--|(?:<<|>>|[+\-*/%&|^])?=(?!=))|(?:\+\+|--|&)\s*\b{re.escape(source)}\b",
                            gap,
                        ):
                            expr = source
                            break
        dereferenced = (left >= 0 and body[left] == "*") or (
            right < len(body) and body[right] == "["
        )
        if expr is not None:
            expr = _cast_extraout(body, match.group(0), expr) or expr
        if expr is None and dereferenced and 6 <= reg <= 9:
            # Origin tracking lost the value, but the callee left the argument
            # register alone. The call's own argument is that pointer. A store
            # through the uninitialized local is a trap under -O2.
            args = c_text._split_args(body[_open_at + 1:close])
            slot = reg - 6
            if slot < len(args):
                arg = args[slot].strip()
                if arg and not re.search(r"\b(?:extraout_|unaff_)", arg):
                    expr = _cast_extraout(body, match.group(0), arg)
                    found = _ep_halfword_disp(image, addr, end, reg)
                    if expr is not None and found is not None and not halfwords:
                        halfwords.append((expr, found[0], found[1]))
        if expr is None:
            continue
        replacements.append((match.start(), match.end(), expr))
    if not replacements:
        return code
    pieces: list[str] = []
    cursor = 0
    for start, end, expr in replacements:
        pieces.append(body[cursor:start])
        pieces.append(expr)
        cursor = end
    pieces.append(body[cursor:])
    text = code[:brace] + "".join(pieces)
    for expr, disp, imms in halfwords:
        for imm in imms:
            token = f"0x{imm:x}u"
            if token not in text:
                continue
            text, count = re.subn(
                rf"\(\*\(\(volatile undefined2 \*\)camry_host_ptr\(\(uint32_t\)\({re.escape(token)}.*?\)\)\)\) = 0xffff;",
                f"(*((volatile undefined2 *)((uint8_t *){expr} + {disp}u))) = 0xffff;",
                text,
                count=1,
            )
            if count:
                break
    return text


def _rewrite_recovered_arguments(code: str) -> str:
    """Recover omitted native arguments for direct and function-pointer calls."""
    if syntax._signature_name(syntax._c_signature(code)) == "complete_nvm_queued_operation_unless_status16_72fde":
        # 73002 loads the popped operation into r7, which 72FC8 preserves
        # for 7300E's completion callback. Repair raw and retained C.
        for record in ("local_28", "(*((uint32_t *)(stack_record_28 + 0)))"):
            code = code.replace(
                f"normalize_nvm_completion_status_72fc8(param_3,{record})",
                f"normalize_nvm_completion_status_72fc8(param_3,operation = {record})",
            )
            code = code.replace(f"(void)({record})", f"(void)(operation = {record})")
    if syntax._signature_name(syntax._c_signature(code)) == "boot_diagnostic_initialize_from_handoff":
        # 6a8a reloads sp into r6 after the preceding calls.
        code = code.replace(
            "boot_diagnostic_replay_handoff_session();",
            "boot_diagnostic_replay_handoff_session(camry_host_addr(local_2c));",
        )
    if syntax._signature_name(syntax._c_signature(code)) == "dcm_submit_transport_response":
        # Retained C discarded 929EE's result under the old one-argument
        # veneer ABI. 929F2 compares that new r10, not 9185C's earlier result.
        code = re.sub(
            r"\(\(void\)\(response\),\s*invoke_prefixed_id_callback_21ccc_92a52\(transmit_id\)\);",
            "iVar3 = invoke_prefixed_id_callback_21ccc_92a52(transmit_id,response);", code,
        )
    if syntax._signature_name(syntax._c_signature(code)) == "cantp_poll_receive_capacity_and_flow":
        # 7A9F2 saves the r6 left intact by 7A862 in r27, and 7AA02
        # reads the same connection after 7A8B0. Retained typed C lost
        # that alias and kept a host-pointer-to-int cast for the upper ID.
        code = re.sub(
            r"^[ \t]*F33CanTpRxConnection\s*\*\s*connection_00\s*;\s*\n",
            "", code, flags=re.M,
        )
        code = re.sub(r"\bconnection_00\b", "connection", code)
        code = code.replace(
            "(*((ushort *)camry_host_ptr((uint32_t)(((int)(connection)) + 8))))",
            "connection->upper_receive_id",
        )
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    signature = syntax._c_signature(code)
    caller = syntax._signature_name(signature)
    facts = abi._call_facts()
    grouped = facts["sites"].get(caller, {})
    state = facts["origins"].get(caller)
    if state is None:
        return code
    params = syntax._param_names(signature)
    types = syntax._signature_param_types(signature)
    body = code[brace:]
    events = [
        (name, open_at, close)
        for name, open_at, close in c_text._direct_calls(body, syntax._SKIP_CALLS)
        if facts["entries"].get(name) is not None
    ]
    counts: dict[int, int] = {}
    for name, _open_at, _close in events:
        entry = facts["entries"][name]
        counts[entry] = counts.get(entry, 0) + 1
    usable = {
        entry for entry, count in counts.items()
        if count == len(grouped.get(entry, ()))
    }
    cursor_at = {entry: 0 for entry in usable}
    indirect = c_text._indirect_calls(body)
    native_indirect = facts["indirect_sites"].get(caller, ())
    indirect_at = {}
    if len(indirect) == len(native_indirect):
        indirect_at = {
            opening: address
            for (opening, _close), address in zip(indirect, native_indirect)
        }
        events.extend((None, opening, close) for opening, close in indirect)
        events.sort(key=lambda event: event[2])
    edits: list[tuple[int, str]] = []
    captured: dict[tuple, str] = {}
    declarations: list[str] = []
    for name, open_at, close in events:
        entry = facts["entries"].get(name)
        unknown_indirect = False
        if name is None:
            addr = indirect_at[open_at]
            target = facts["names"].get(abi._STATIC_CALL_TARGETS.get(addr))
            unknown_indirect = target is None
            # The native call passes the live argument registers even when
            # Ghidra inferred a zero-argument callback type. Unknown callbacks
            # use the existing unprototyped ABI, so preserve the available
            # register prefix without inventing a target-specific interface.
            need = 4 if unknown_indirect else facts["need"].get(target, 0)
        else:
            if entry not in usable:
                continue
            slot = cursor_at[entry]
            cursor_at[entry] = slot + 1
            addr = grouped[entry][slot]
            need = facts["need"].get(name, 0)
        existing = c_text._split_args(body[open_at + 1:close])
        if len(existing) == 1 and not existing[0].strip():
            existing = []
        if existing and entry is not None and 6 not in abi._ARG_CLOBBERS.get(entry, {6}):
            after = min((opening for _target, opening, _end in events if opening > close), default=len(body))
            alias = re.search(r"\bextraout_r6(?:_[0-9]+)?\b", body[close + 1:after])
            if alias and not re.search(rf"\b{alias.group(0)}\s*=", existing[0]):
                # Preserve the native incoming word, not the C compiler's caller-saved r6.
                start = c_text._skip_space(body, open_at + 1)
                edits.append((start, f"({alias.group(0)} = "))
                edits.append((start + len(existing[0]), ")"))
        if len(existing) >= need:
            continue
        if caller == "reconcile_requested_normal_network_policy" and entry == 0x83204:
            # Ghidra prints 7c2a8 before 7c240. The former already names
            # r7=3; the latter constructs r7 from the two request bits.
            addr = 0x7c2a8 if len(existing) == 2 else 0x7c240
        recovered: list[str] = []
        for index in range(len(existing), need):
            origin = abi._argument_origin(state.get(addr, {}), index)
            if unknown_indirect and any(item[0] not in {"entry", "imm", "sp", "call"} for item in origin):
                # Extra arguments must not introduce a volatile memory read.
                break
            expr = abi._emit_origin(origin, params, types)
            if expr is None and len(origin) == 1 and next(iter(origin))[0] == "sp":
                expr = abi._stack_local(code, next(iter(origin))[1])
            if expr is None and len(origin) == 1 and next(iter(origin))[0] == "stackload":
                item = next(iter(origin))
                pointer = abi._stack_local(code, item[1])
                if pointer is not None:
                    ctype = {1: "uint8_t", 2: "uint16_t", 4: "uint32_t"}[item[2]]
                    expr = f"(*(({ctype} *)({pointer})))"
                    local = re.fullmatch(r"&?([A-Za-z_][A-Za-z0-9_]*)", pointer)
                    if local is not None:
                        local_name = local.group(1)
                        declaration = re.search(
                            rf"^\s*(\w+)\s+{re.escape(local_name)}\s*(\[[^\]]*\])?\s*;",
                            body, re.M,
                        )
                        if declaration is not None and layout._STACK_WIDTH.get(declaration.group(1)) == item[2]:
                            expr = local_name + ("[0]" if declaration.group(2) else "")
                    if item[3]:
                        signed_type = {1: "int8_t", 2: "int16_t", 4: "int32_t"}[item[2]]
                        expr = f"(int)({signed_type}){expr}"
            if expr is None and len(origin) == 1 and next(iter(origin))[0] == "call":
                callee = facts["names"].get(next(iter(origin))[1])
                if callee:
                    expr = abi._value_of_call(body, open_at, callee)
                    if expr is None and callee == "dcm_get_response_queue":
                        # The inlined getter is movea -0x5e90,gp,r10.
                        expr = "&dcm_response_queue"
                    if expr is None and len(next(iter(origin))) >= 3:
                        item = next(iter(origin))
                        produced = _produced_type(facts, callee)
                        prior = [
                            (op, cl) for target, op, cl in events
                            if target == callee and cl < open_at
                        ]
                        native = grouped.get(item[1], [])
                        if produced != "void" and len(prior) == len(native) == 1 and native[0] == item[2]:
                            expr = captured.get(item)
                            if expr is None:
                                expr = f"camry_arg_result_{len(captured)}"
                                while re.search(rf"\b{expr}\b", body):
                                    expr += "_"
                                captured[item] = expr
                                declarations.append(f"  {produced} {expr};")
                                op, cl = prior[0]
                                edits.extend(((op - len(callee), f"({expr} = "), (cl + 1, ")")))
            if expr is None and origin and all(item[0] == "call" for item in origin):
                # Several native call results can share one C phi destination.
                callees = {facts["names"].get(item[1]) for item in origin}
                if len(callees) == 1 and None not in callees:
                    callee = next(iter(callees))
                    prior = [
                        abi._assignment_prefix(body, opening)
                        for target, opening, closing in events
                        if target == callee and closing < open_at
                    ]
                    destinations = {item[0] if item is not None else None for item in prior}
                    if len(prior) == len(origin) and len(destinations) == 1 and None not in destinations:
                        expr = abi._value_of_call(body, open_at, callee)
            if expr is None:
                # These phi/loop values have C names but no single origin in
                # the register lattice. Keys are the exact native call sites.
                expr = {
                    (0x2b66, 0): "uVar6",
                    (0x2ec4, 1): "DAT_febf2932",
                    (0x3108, 0): "((param_2 & 0xffff) >> 8)",
                    (0x311c, 0): "((param_2 & 0xffff) >> 8)",
                    (0x52958, 0): "(byte)(&DAT_0002fc52)[uVar1 * 8]",
                    (0x55b84, 1): "uVar7 + param_3",
                    (0x55cbc, 4): "(cVar2 == 'D' ? 3u : cVar2 == 'U' ? 2u : 0u)",
                    (0x56f6a, 0): "uVar6 & 7",
                    (0x61b7e, 2): "compare",
                    (0x774d6, 1): "nvm_checksum_accumulator",
                    (0x782aa, 4): "*(byte *)((uint)param_2[1] + (uint)param_1[1] * *param_2 + *(uint *)(param_1 + 4))",
                    (0x79948, 0): "(iVar1 == 2 ? 2u : iVar1 == 10 ? 0u : 1u)",
                    (0x7c6aa, 0): "(param_1 - (ushort)DAT_0002183d) & 0xff",
                    (0x7c954, 0): "bVar3",
                    (0x7cffa, 0): "(&selected_network_recovery)[param_1 & 0xff].aggregated_cause",
                    (0x7de24, 2): "(ushort)sVar4",
                    (0x7e274, 2): "(ushort)sVar5",
                    (0x80058, 1): "*(byte *)(psVar1 + 2)",
                    (0x80d6e, 0): "driver_to_logical_controller_map[param_1 & 0xff]",
                    (0x82de0, 2): "*(ushort *)(puVar1 + uVar6 * 2 - 0x6940)",
                    (0x831ae, 2): "bVar2",
                    (0x8aeaa, 0): "(undefined4 *)(uintptr_t)puVar6[1]",
                    (0x8cace, 0): "*dcm_dtc_list_message.request",
                    (0xb9314, 1): "uVar2 & 0xf0",
                    (0xc4b26, 0): "DAT_febec0c0",
                    (0xc4b26, 1): "DAT_febec0bc",
                    (0xc4b38, 0): "DAT_febec0c0",
                    (0xc4b38, 1): "DAT_febec0bc",
                    (0x7ab8c, 0): "unaff_r25",
                    (0x7ab8c, 1): "state",
                    (0x80458, 1): "(controller_route >> 8)",
                    (0xb92a0, 0): "iVar4",
                    (0x96176, 0): "operation",
                    (0x7c240, 1): "(uVar3 & 3)",
                    (0x57504, 0): "DAT_febe8b60",
                    (0x57504, 1): "DAT_febe8b62",
                    (0x57504, 2): "DAT_febe8b64",
                    (0x5758a, 0): "uVar7",
                    (0x5758a, 1): "uVar9",
                    (0x5758a, 2): "uVar11",
                    (0x3e42a, 0): "(undefined4 *)&DAT_febe757c",
                    (0x3e4fc, 0): "(undefined4 *)&DAT_febe758c",
                }.get((addr, index))
            if expr is None:
                if not unknown_indirect:
                    recovered = []
                break
            recovered.append(expr)
        if not recovered:
            continue
        joiner = "" if not existing else ", "
        edits.append((close, joiner + ", ".join(recovered)))
    if not edits:
        return code
    if declarations:
        edits.append((1, "\n" + "\n".join(declarations) + "\n"))
    pieces: list[str] = []
    cursor = 0
    for close, text in sorted(edits):
        pieces.append(body[cursor:close])
        pieces.append(text)
        cursor = close
    pieces.append(body[cursor:])
    return code[:brace] + "".join(pieces)


def _rewrite_returned_call(code: str, saved_context: set[int] | None = None) -> str:
    """Recover produced returns, not synthetic incoming saved-register pairs."""
    signature = syntax._c_signature(code)
    name = syntax._signature_name(signature)
    facts = abi._call_facts() if saved_context is None else None
    if saved_context is None:
        saved_context = facts["context_saved"].get(name, set())
    old_type = syntax._return_type_of(signature, name)
    brace = syntax._opening_brace(code)
    if {10, 11} <= saved_context and old_type in {"undefined8", "uint64_t", "ulonglong", "longlong"} and brace >= 0:
        head, body = code[:brace], code[brace:]
        incoming_return = re.compile(r"\breturn\s+CONCAT44\(\s*in_r11\s*,\s*in_r10\s*\)\s*;")
        declarations = {
            reg: re.compile(rf"^[ \t]*(?:undefined4|uint32_t|uint|int)\s+in_r{reg}\s*;[ \t]*\n", re.M)
            for reg in (10, 11)
        }
        stripped = syntax._strip_comments(body)
        if (
            incoming_return.search(body) is not None
            and len(re.findall(r"\breturn\b", stripped)) == 1
            and all(
                len(re.findall(rf"\bin_r{reg}\b", stripped)) == 2
                and declaration.search(body) is not None
                for reg, declaration in declarations.items()
            )
        ):
            body = incoming_return.sub("return;", body)
            for declaration in declarations.values():
                body = declaration.sub("", body)
            head = re.sub(rf"\b{old_type}(?=\s+{re.escape(name)}\s*\()", "void", head)
            return head + body
    if facts is None:
        return code
    new_type = facts["planned"].get(name)
    if name in {"dispatch_record_callback_slot_twelve_21b70_7f366", "dispatch_record_callback_slot_thirty_two_7f3a6"}:
        # Native table 21b70 has seven entries, pointing at 21b10/21b40.
        # Slot +0xc returns zero (7f3ee). Slot +0x20 is 7f3dc or
        # 7f23c; the latter reads incoming r6 and returns its status in r10.
        exits = facts["ret_r10"].get(name, [])
        if exits and all(
            len(origin) == 1 and next(iter(origin))[:2] == ("call", None)
            for origin in exits
        ):
            new_type = "uint32_t"
    span = syntax._trailing_call_span(code)
    if not new_type or span is None or syntax._return_type_of(signature, name) != "void":
        return code
    statement, start, ret_end = span
    if name == "dispatch_record_callback_slot_thirty_two_7f3a6":
        opening = statement.rfind("(")
        if opening >= 0 and not statement[opening + 1:-1].strip():
            statement = statement[:opening + 1] + syntax._param_names(signature)[0] + ")"
    brace = syntax._opening_brace(code)
    head, body = code[:brace], code[brace:]
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + new_type + found.group(1) + head[found.end():]
    body = body[:start] + "\n  return " + statement + ";" + body[ret_end:]
    return head + body


def _saved_pmr_variable(body: str) -> str | None:
    """The variable holding the PMR read that the bytes return in r10."""
    found = None
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=\s*PMR\s*;", body):
        found = match
        break
    if found is None:
        return None
    name = found.group(1)
    if re.search(r"\breturn\b", body[:found.start()]):
        return None
    if re.search(rf"\b{re.escape(name)}\s*=(?!=)", body[found.end():]):
        return None
    if not re.search(r"\breturn\s*;", body[found.end():]):
        return None
    return name


def _rewrite_stored_result(code: str) -> str:
    """A void function that stores r10 and returns it yields that stored object."""
    signature = syntax._c_signature(code)
    name = syntax._signature_name(signature)
    facts = abi._call_facts()
    # The terminal native stores are r10 itself, including stores followed
    # by other register stores. Returning the stored narrow object is exact:
    # 49c24/49c5e store a byte; 4c6e2 stores a byte-valued phi; c915a
    # follows sxh r10, so its halfword must be sign-extended on return.
    stored = {
        "update_threshold_holdoff_pair_49bba": ("uint", "DAT_febe7f4e"),
        "update_true_flag_holdoff_49c2c": ("uint", "DAT_febe7f4f"),
        "consume_ten_status_flags_and_update_admission_latch_4c650": ("uint", "DAT_febe818a"),
        "apply_c544_and_c548_q10_gains_c9134": ("int", "(short)DAT_febec54a"),
    }.get(name)
    if (
        (name not in facts["stored_r10"] and stored is None)
        or name in facts["hand"]
        or name in facts["saved_pmr"]
        or facts["planned"].get(name)
        or syntax._return_type_of(signature, name) != "void"
    ):
        return code
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    head, body = code[:brace], code[brace:]
    if stored is not None:
        typ, expression = stored
        head = re.sub(rf"\bvoid(?=\s+{re.escape(name)}\s*\()", typ, head)
        body = re.sub(r"\breturn\s*;", f"return {expression};", body)
        return head + body
    lhss = list(dict.fromkeys(re.findall(
        r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)",
        body,
        flags=re.M,
    )))
    returns = list(re.finditer(r"\breturn\s*;", body))
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if len(lhss) != 1 or len(returns) != 1 or not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + "uint" + found.group(1) + head[found.end():]
    ret = returns[0]
    body = body[:ret.start()] + f"return {lhss[0]};" + body[ret.end():]
    return head + body


_HELD_TYPES = {
    "int", "uint", "long", "ulong", "short", "ushort", "char", "uchar", "byte",
    "sbyte", "undefined", "undefined1", "undefined2", "undefined4", "bool",
}


def _held_assignments(body: str, var: str) -> list[str]:
    found: list[str] = []
    for match in re.finditer(rf"(?<![\w.]){re.escape(var)}\s*=(?!=)", body):
        if match.start() and body[match.start() - 1] in ".>":
            continue
        found.append(body[match.end():syntax._rhs_end(body, match.end())].strip())
    return found


def _declared_scalar(body: str, var: str) -> str | None:
    """The function-scope scalar type of `var`, when it has one declaration."""
    types: list[str] = []
    depth = 0
    index = 0
    while index < len(body):
        if body.startswith("/*", index):
            end = body.find("*/", index + 2)
            index = len(body) if end < 0 else end + 2
            continue
        char = body[index]
        if char == "{":
            depth += 1
            index += 1
            continue
        if char == "}":
            depth = max(0, depth - 1)
            index += 1
            continue
        if depth == 1:
            match = re.match(
                rf"([A-Za-z_][A-Za-z0-9_]*)\s+{re.escape(var)}\s*;",
                body[index:],
            )
            if match and (index == 0 or body[index - 1] in " \t\n\r{(;"):
                types.append(match.group(1))
                index += match.end()
                continue
        index += 1
    if len(types) != 1 or types[0] not in _HELD_TYPES:
        return None
    return types[0]


def _assignment_token(rhs: str, var: str) -> tuple:
    value = syntax._const_value(rhs)
    if value is not None:
        return ("imm", value)
    if re.match(rf"(?:\([^)]*\)\s*)*{re.escape(var)}\b", rhs):
        return ("self",)
    call = re.fullmatch(
        r"(?:\([^)]*\)\s*)?([A-Za-z_][A-Za-z0-9_]*)\s*\(.*\)",
        rhs,
        flags=re.S,
    )
    if call and call.group(1) not in {"if", "for", "while", "switch", "return", "sizeof"}:
        return ("call", call.group(1))
    return ("other",)


def _held_local(body: str, needed: set[tuple]) -> tuple[str, str] | None:
    """The one local whose assignments are exactly `needed`, and nothing else."""
    if not needed:
        return None
    names = {
        match.group(1)
        for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)", body)
    }
    found: list[tuple[str, str]] = []
    for var in names:
        tokens = {_assignment_token(rhs, var) for rhs in _held_assignments(body, var)}
        if tokens != needed:
            continue
        typ = _declared_scalar(body, var)
        if typ is None:
            continue
        found.append((var, typ))
    if len(found) != 1:
        return None
    var = found[0][0]
    for match in re.finditer(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(", body):
        callee = match.group(1)
        if ("call", callee) not in needed:
            continue
        prev = max(
            body.rfind(";", 0, match.start()),
            body.rfind("{", 0, match.start()),
            body.rfind("}", 0, match.start()),
        )
        if not re.search(r"(?<![=<>!])=(?!=)", body[prev + 1:match.start()]):
            return None
    return found[0]


def _rewrite_held_result(code: str) -> str:
    """A void function whose r10 is one local at every return returns that local."""
    signature = syntax._c_signature(code)
    name = syntax._signature_name(signature)
    facts = abi._call_facts()
    if (
        name in facts["hand"]
        or name in facts["saved_pmr"]
        or name in facts["stored_r10"]
        or facts["planned"].get(name)
        or syntax._return_type_of(signature, name) != "void"
    ):
        return code
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    head, body = code[:brace], code[brace:]
    if not re.search(r"\breturn\s*;", body) or re.search(r"\breturn\b(?!\s*;)", body):
        return code
    if name == "count_nonzero_dtcs_matching_status_mask_526cc":
        # 526dc initializes r10 separately from the r1 snapshot index.
        # 526e4..526fe increment it only for a masked status with nonzero
        # DTC number at 30850 + index*8. Ghidra dropped that whole slice.
        mask = (syntax._param_names(signature) or ["param_1"])[0]
        if not syntax._param_names(signature):
            head = re.sub(rf"\b{re.escape(name)}\s*\(\s*void\s*\)", f"{name}(byte {mask})", head)
        body = body.replace(
            "  do {",
            "  uint camry_r10_result = 0;\n  do {\n"
            f"    if ((local_a8[uVar1] & {mask}) != 0 &&\n"
            "        *(const uint32_t *)camry_host_ptr(0x30850u + uVar1 * 8u) != 0) {\n"
            "      camry_r10_result = (camry_r10_result + 1u) & 0xffffu;\n"
            "    }",
            1,
        )
        body = re.sub(r"\breturn\s*;", "return camry_r10_result;", body)
        head = re.sub(rf"\bvoid(?=\s+{re.escape(name)}\s*\()", "uint", head)
        return head + body
    if name == "convert_u16_units_to_ceiling_configured_ticks_7bde2":
        # 7bdf0 initializes r10; 7be00/7be06 shift and narrow it,
        # and 7be18 appends one on the nonnegative remainder branch.
        body = body.replace("  do {", "  uint camry_r10_result = 0;\n  do {\n    camry_r10_result = (camry_r10_result << 1) & 0xffffu;", 1)
        body = body.replace("      iVar4 = 0x1e;", "      camry_r10_result |= 1u;\n      iVar4 = 0x1e;")
        body = re.sub(r"\breturn\s*;", "return camry_r10_result;", body)
        head = re.sub(rf"\bvoid(?=\s+{re.escape(name)}\s*\()", "uint", head)
        return head + body
    origins = facts["ret_r10"].get(name) or []
    flat: set = set()
    for origin in origins:
        flat |= origin
    held = None
    if flat and all(item[0] in {"imm", "call"} for item in flat):
        needed = set()
        for item in flat:
            if item[0] == "imm":
                needed.add(("imm", item[1] & 0xFFFFFFFF))
                continue
            callee = facts["names"].get(item[1])
            if not callee:
                needed = set()
                break
            needed.add(("call", callee))
        held = _held_local(body, needed)
        if held is None and needed:
            seed = facts["initial_r10"].get(name)
            immediates = {item[1] for item in flat if item[0] == "imm"}
            calls = {facts["names"].get(item[1]) for item in flat if item[0] == "call"}
            if seed is not None and immediates == {seed} and calls and all(
                callee is not None and syntax._is_int_type(_produced_type(facts, callee)) for callee in calls
            ):
                edits = []
                found = set()
                for callee, opening, closing in c_text._direct_calls(body, syntax._SKIP_CALLS):
                    if callee not in calls:
                        continue
                    start = opening - len(callee)
                    edits.extend(((start, "(camry_r10_result = "), (closing + 1, ")")))
                    found.add(callee)
                if found == calls and not re.search(r"\bcamry_r10_result\b", body):
                    for at, text in sorted(edits, reverse=True):
                        body = body[:at] + text + body[at:]
                    body = body[:1] + f"\n  uint32_t camry_r10_result = 0x{seed:x}u;\n" + body[1:]
                    held = ("camry_r10_result", "uint32_t")
    elif name in facts["counters"]:
        imms = facts["counters"][name]
        if flat and all(
            item[0] == "fail" or (item[0] == "imm" and (item[1] & 0xFFFFFFFF) in imms)
            for item in flat
        ):
            held = _held_local(body, {("imm", value) for value in imms} | {("self",)})
    if held is None:
        return code
    var, typ = held
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + typ + found.group(1) + head[found.end():]
    body = re.sub(r"\breturn\s*;", f"return {var};", body)
    return head + body


def _checked_names() -> set[str]:
    global _CHECKED_NAMES
    if _CHECKED_NAMES is None:
        _CHECKED_NAMES = {
            row["name"]
            for row in tree.load_matched()
            if row.get("status") in {"equivalent", "byte-matched"}
        }
    return _CHECKED_NAMES


def _rewrite_saved_pmr(code: str) -> str:
    """A void function whose r10 is the PMR it read returns that saved value."""
    signature = syntax._c_signature(code)
    name = syntax._signature_name(signature)
    facts = abi._call_facts()
    if name in facts["hand"] or name not in facts["saved_pmr"]:
        return code
    if syntax._return_type_of(signature, name) != "void":
        return code
    brace = syntax._opening_brace(code)
    if brace < 0:
        return code
    head, body = code[:brace], code[brace:]
    saved = _saved_pmr_variable(body)
    declarator = list(re.finditer(rf"\bvoid(\s+{re.escape(name)}\s*\()", head))
    if saved is None or not declarator:
        return code
    for found in reversed(declarator):
        head = head[:found.start()] + "uint" + found.group(1) + head[found.end():]
    body = re.sub(r"\breturn\s*;", f"return {saved};", body, count=1)
    return head + body
