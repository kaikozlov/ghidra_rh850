"""Run identity-checked firmware in an installed CS+ RH850 simulator via CrossOver."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import uuid
from pathlib import Path

from tools import REPO_ROOT
from tools.project.analysis_target import target, verified_file

CROSSOVER = Path("/Applications/CrossOver.app/Contents/SharedSupport/CrossOver/bin/wine")
DEFAULT_BOTTLE = REPO_ROOT / "build/cache/renesas-csplus-81600"
INSTALLATION = Path("drive_c/Program Files (x86)/Renesas Electronics/CS+/CC")
BOOTSTRAP = Path("SampleProjects/RH850/RH850_F1L_Tutorial_Basic_Operation/RH850_F1L_Tutorial_Basic_Operation.mtpj")

# Per-pin mirrors of the effective group-register bits (Table 2.32).
PORT_PIN_FIELDS = (
    ("PFC", 0), ("PFCE", 1), ("PFCAE", 2), ("PM", 4), ("PIPC", 5), ("PMC", 6),
    ("PPR", 8), ("P", 12), ("PIBC", 16), ("PBDC", 17), ("PD", 18), ("PU", 19),
    ("PISA", 22), ("PDSC", 24), ("PUCC", 25), ("PODCE", 27), ("PODC", 28), ("PINV", 30),
)
SUPPORTED_TRIGGERS = frozenset((
    "ecc-protected-control", "banked-ecc-clear", "ecc-notification",
    "dcra-control", "dcra-seed", "dcra-input", "clock-divider", "clock-selector",
    "port-masked-alias", "port-pin-alias", "noise-filter-enable", "noise-clock-selector",
    "peripheral-ecc-control", "peripheral-ecc-test",
))


def peripheral_registers(registers: list[dict]) -> list[dict]:
    """Select implemented protocols and their transitive generated dependencies."""
    by_name = {register["name"]: register for register in registers}
    selected = set()
    pin_aliases = {}
    pending = [
        register["name"] for register in registers
        if register.get("trigger") in SUPPORTED_TRIGGERS
        or (register.get("trigger") is None and (
            register["behavior"] in ("port-config", "noise-filter")
            or register.get("read_value") is not None
        ))
    ]
    while pending:
        name = pending.pop()
        if name in selected:
            continue
        if name not in by_name:
            raise CSPlusError(f"missing shared peripheral dependency: {name}")
        register = by_name[name]
        trigger = register.get("trigger")
        if trigger is not None and trigger not in SUPPORTED_TRIGGERS:
            raise CSPlusError(f"unsupported peripheral dependency: {name} ({trigger})")
        if trigger is None and register.get("read_value") is None and register["behavior"] not in (
            "storage", "port-config", "port-input", "noise-filter", "noise-clock-status", "clock", "dcra",
        ):
            raise CSPlusError(f"unsupported peripheral behavior: {name} ({register['behavior']})")
        selected.add(name)
        pending.extend(register[field] for field in (
            "mode_register", "status_register", "control_register",
            "secondary_status_register", "enable_register",
        ) if field in register)
        pending.extend(register.get("capture_registers", []))
        if trigger == "port-pin-alias":
            group, pin = name.rsplit("_", 1)
            pin_mask = 1 << int(pin)
            prefix = "J" if name.startswith("J") else ""
            fields = []
            for base, bit in PORT_PIN_FIELDS:
                source_name = f"{prefix}{base}{group[-1]}"
                source = by_name.get(source_name)
                if source is None:
                    continue  # JP omits several group functions (Table 2.42).
                effective = source.get(
                    "active_mask" if source["behavior"] == "port-input" else "writable_mask", 0,
                )
                if effective & pin_mask:
                    fields.append({"source": source_name, "bit": bit, "pin_mask": pin_mask})
                    pending.append(source_name)
            pin_aliases[name] = fields
    return [
        dict(register, **({"pin_fields": pin_aliases[register["name"]]}
                          if register["name"] in pin_aliases else {}))
        for register in registers if register["name"] in selected
    ]


class CSPlusError(RuntimeError):
    pass


def windows_path(path: Path) -> str:
    """CrossOver exposes the host filesystem through its Z: drive."""
    return "Z:" + str(path.resolve()).replace("/", "\\")


# Executed by CS+'s embedded IronPython, which supplies project/debugger/enum globals.
DRIVER = r'''
import hashlib
import json
import re
import time
import traceback
import System

STORE_WIDTHS = {"st.b": 1, "sst.b": 1, "st.h": 2, "sst.h": 2,
                "st.w": 4, "sst.w": 4, "st.dw": 8}
REGISTER_ALIASES = {"r3": "sp", "r4": "gp", "r5": "tp", "r30": "ep", "r31": "lp"}
LOAD_WIDTHS = {"ld.b": 1, "ld.bu": 1, "sld.b": 1, "sld.bu": 1,
               "ld.h": 2, "ld.hu": 2, "sld.h": 2, "sld.hu": 2, "ld.w": 4, "sld.w": 4}

with open(CONTRACT_PATH) as source:
    contract = json.load(source)
report = {
    "schema": "rh850-csplus-run-v1",
    "run_id": contract["run_id"],
    "target": contract["target"],
    "mcu": contract["mcu"],
    "project": contract["project"],
    "process_id": int(System.Diagnostics.Process.GetCurrentProcess().Id),
    "status": "starting",
}
def save():
    with open(contract["report"], "w") as destination:
        json.dump(report, destination, indent=2, sort_keys=True)
        destination.write("\n")
save()

def set_state(register, value):
    if not debugger.Register.SetValue(register["ior"], value):
        raise RuntimeError("Cannot apply modeled IOR transaction: " + register["ior"])
    register["state"] = value

def refresh_port_aliases(changed=None):
    for alias in controls:
        trigger = alias.get("trigger")
        if trigger == "port-masked-alias":
            if changed is not None and alias["control_register"] not in changed:
                continue
            value = by_name[alias["control_register"]]["state"]
        elif trigger == "port-pin-alias":
            if changed is not None and alias["name"] not in changed and not any(
                    field["source"] in changed for field in alias["pin_fields"]):
                continue
            value = alias["reset"]
            for field in alias["pin_fields"]:
                mask = 1 << field["bit"]
                value = (value & ~mask) | (mask if by_name[field["source"]]["state"] & field["pin_mask"] else 0)
        else:
            continue
        if value != alias["state"]:
            set_state(alias, value)

def read_device(control, address, native_value, instruction, trace_complete=True):
    if control.get("requires_input", False):
        raise RuntimeError("DNF clock activity requires a new external input: " + control["ior"])
    if control.get("read_input", False):
        report["native_input_reads"].append({
            "ior": control["ior"], "address": address,
            "width": LOAD_WIDTHS.get(str(instruction.Mnemonic).split()[0]),
            "instruction_pc": int(instruction.FetchAddress),
            "native_bus_value": native_value, "native_trace_complete": trace_complete,
            "evidence": "native simulator bus response; not a documented silicon read value",
        })
    elif control.get("trigger") == "dcra-seed":
        complete_crc_read(control, address, native_value, instruction, trace_complete)

def write_device(control, address, written, instruction):
    opcode = str(instruction.Mnemonic).split()[0]
    width = STORE_WIDTHS.get(opcode)
    if width not in control["access_widths"] or address % width:
        raise RuntimeError("Unsupported peripheral store: %s at %#x" % (instruction.Mnemonic, address))
    if address + width > control["address"] + control["size"]:
        raise RuntimeError("Peripheral store crosses a register boundary")
    if "w" not in control["access"]:
        raise RuntimeError("CPU wrote a read-only modeled IOR: " + control["ior"])
    shift = 8 * (address - control["address"])
    lane_mask = ((1 << (8 * width)) - 1) << shift
    incoming = (written & ((1 << (8 * width)) - 1)) << shift
    merged = (control["state"] & ~lane_mask) | incoming
    trigger = control.get("trigger")
    native_latch = int(debugger.Register.GetValue(control["ior"]))
    if trigger == "peripheral-ecc-control":
        if incoming & ~(control["writable_mask"] | 0x30807):
            raise RuntimeError("Reserved peripheral ECC control bits must be zero")
        previous = control["state"]
        next_value = (previous & ~0x38) | (incoming & 0x38)
        if incoming & 0xC000 == 0x4000:
            next_value = (next_value & ~0x80) | (incoming & 0x80)
        if incoming & 0x200:
            next_value &= ~2
        if incoming & 0x400:
            next_value &= ~4
        if incoming & 0x600 or (next_value & 0x80 and not previous & 0x80):
            next_value &= ~0x30800
        # ECEMF is a live native input, not a zero-valued reset latch.
        next_value = (next_value & ~1) | (native_latch & 1)
        set_state(control, next_value & ~0xC600)
    elif trigger == "peripheral-ecc-test":
        if incoming & ~control["writable_mask"]:
            raise RuntimeError("Reserved peripheral ECC test bits must be zero")
        enabled = control["state"] & 0x80
        if incoming & 0xC000 == 0x8000:
            enabled = incoming & 0x80
        if enabled:
            set_state(control, control["state"])
            raise RuntimeError("Active peripheral ECC test mode requires unmodeled encoder/data substitution")
        set_state(control, 0)
    elif trigger == "ecc-protected-control":
        protection_mask = control.get("protection_mask", 0xC000)
        protection_value = control.get("protection_value", 0x4000)
        if address == control["address"] and written & protection_mask == protection_value:
            control["state"] = written & control["writable_mask"]
        set_state(control, control["state"] & control["writable_mask"])
    elif trigger == "banked-ecc-clear":
        if incoming & ~control["writable_mask"]:
            raise RuntimeError("Reserved ECC clear bits must be zero: " + control["ior"])
        status = by_name[control["status_register"]]
        secondary = by_name.get(control.get("secondary_status_register"))
        captures = control.get("capture_registers")
        secondary_masks = control.get("secondary_status_masks")
        for bank, status_mask in enumerate(control["status_masks"]):
            if incoming & (1 << bank):
                set_state(status, status["state"] & ~status_mask)
                if secondary is not None:
                    secondary_mask = secondary_masks[bank] if secondary_masks is not None else 1 << bank
                    set_state(secondary, secondary["state"] & ~secondary_mask)
                if captures is not None:
                    set_state(by_name[captures[bank]], 0)
        if control.get("read_input", False):
            # Preserve the native command latch; the manual specifies no read value.
            control["state"] = native_latch
        else:
            set_state(control, control["read_value"])
    elif trigger == "ecc-notification":
        if incoming & ~control["writable_mask"]:
            raise RuntimeError("Reserved ECC enable bits must be zero: " + control["ior"])
        set_state(control, merged)
    elif control["behavior"] == "port-config":
        changed = set([control["name"]])
        if trigger == "port-masked-alias":
            target = by_name[control["control_register"]]
            enabled = (incoming >> 16) & target["writable_mask"]
            set_state(target, (target["state"] & ~enabled) | (incoming & enabled))
            changed.add(target["name"])
        elif trigger == "port-pin-alias":
            for field in control["pin_fields"]:
                if control["writable_mask"] & (1 << field["bit"]):
                    target = by_name[field["source"]]
                    pin = field["pin_mask"]
                    set_state(target, (target["state"] & ~pin) | (pin if incoming & (1 << field["bit"]) else 0))
                    changed.add(target["name"])
        elif trigger is None:
            mask = control["writable_mask"]
            set_state(control, (control["reset"] & ~mask) | (merged & mask))
        else:
            raise RuntimeError("Unsupported port alias: " + str(trigger))
        refresh_port_aliases(changed)
    elif control["behavior"] == "noise-filter":
        if incoming & ~control["writable_mask"]:
            raise RuntimeError("Reserved noise-filter bits must be zero: " + control["ior"])
        if trigger == "noise-filter-enable" and incoming:
            raise RuntimeError("Enabled filtering requires external signal and sampling-clock behavior")
        if control.get("enable_register") and by_name[control["enable_register"]]["state"]:
            raise RuntimeError("Noise-filter configuration requires disabled filtering")
        if trigger == "noise-clock-selector":
            if incoming not in control["allowed_values"]:
                raise RuntimeError("Prohibited DNF sampling source")
            if any(by_name[name]["state"] for name in control["capture_registers"]):
                raise RuntimeError("DNF source selection requires all related filters disabled")
            if incoming != control["state"]:
                status = by_name[control["status_register"]]
                set_state(status, incoming)
                status["requires_input"] = True
                report["unresolved_clock_activity"].append(status["ior"])
        elif trigger not in (None, "noise-filter-enable"):
            raise RuntimeError("Unsupported noise-filter protocol: " + str(trigger))
        set_state(control, merged)
    elif trigger in ("clock-divider", "clock-selector"):
        if written & ~control["writable_mask"]:
            raise RuntimeError("Clock write sets reserved bits: " + control["ior"])
        status = by_name[control["status_register"]]
        if trigger == "clock-divider":
            if status["state"] & control["sync_mask"] != control["sync_mask"]:
                raise RuntimeError("Clock divider write before synchronization")
            completed = control["completion_value"]
            if written:
                completed |= control["active_mask"]
            set_state(status, completed)
        else:
            if written not in control["allowed_values"]:
                raise RuntimeError("Prohibited clock source ID: %d" % written)
            if written != control["state"]:
                divider = by_name[control["control_register"]]
                divider_status = by_name[control["secondary_status_register"]]
                if divider["state"] != 0 or divider_status["state"] != control["completion_value"]:
                    raise RuntimeError("Clock source change requires a stopped synchronized divider")
                set_state(status, written)
        control["state"] = written
    elif trigger in ("dcra-control", "dcra-seed", "dcra-input"):
        mode_control = control if trigger == "dcra-control" else by_name[control["mode_register"]]
        mode = written if trigger == "dcra-control" else mode_control["state"]
        if mode != 0 and not (mode_control["name"] == "DCRA0CTL" and mode == 0x22):
            raise RuntimeError("Unsupported DCRA mode: Ethernet/32-bit or DCRA0 SAE J1850/8-bit required")
        if trigger == "dcra-control":
            if written != control["state"]:
                for output in controls:
                    if output.get("trigger") == "dcra-seed" and output["mode_register"] == control["name"]:
                        output["seeded"] = False
            set_state(control, written)
        elif trigger == "dcra-seed":
            set_state(control, written ^ (0xFF if mode == 0x22 else 0xFFFFFFFF))
            control["seeded"] = True
            control["input_words"] = 0
            control["dirty"] = False
        else:
            output = by_name[control["status_register"]]
            if not output.get("seeded", False):
                raise RuntimeError("DCRA input before firmware initialized COUT")
            if mode == 0x22:
                # Table33.9: SAE J1850 polynomial 1D, low byte MSB first.
                crc = (output["state"] ^ 0xFF ^ written) & 0xFF
                for bit in xrange(8):
                    crc = ((crc << 1) ^ (0x1D if crc & 0x80 else 0)) & 0xFF
                output["state"] = (output["state"] & 0xFFFFFF00) | (crc ^ 0xFF)
            else:
                crc = (output["state"] ^ 0xFFFFFFFF) ^ written
                for bit in xrange(32):
                    crc = (crc >> 1) ^ (0xEDB88320 if crc & 1 else 0)
                output["state"] = crc ^ 0xFFFFFFFF
            output["input_words"] += 1
            output["dirty"] = True
            control["state"] = written
    elif trigger is None and control.get("read_value") is not None:
        set_state(control, control["read_value"])
    else:
        raise RuntimeError("Unsupported device trigger: " + str(trigger))
    control["writes"] += 1
    report["peripheral_writes"] += 1
    report["last_transaction"] = {
        "address": address, "ior": control["ior"], "width": width,
        "instruction_pc": int(instruction.FetchAddress), "written": written,
        "native_latch": native_latch, "readback": control["state"],
    }

def complete_crc_read(control, address, native_value, instruction, trace_complete=True):
    # CS+ read events retire the load. Complete only its documented bus-result
    # transfer; LD.W/SLD.W change no flags (G3M software manual pp251,304).
    mnemonic = str(instruction.Mnemonic)
    if mnemonic.split()[0] not in ("ld.w", "sld.w") or address != control["address"]:
        raise RuntimeError("Unsupported CRC result load: " + mnemonic)
    destination = mnemonic.rsplit(",", 1)[-1].strip()
    if destination not in ["r%d" % n for n in range(32)] + ["sp", "gp", "tp", "ep", "lp"]:
        raise RuntimeError("CRC result load has no general-register destination")
    decoded = debugger.Assemble.Disassemble(int(instruction.FetchAddress), 1)[0]
    next_pc = int(decoded.Address) + len(decoded.Code)
    if int(debugger.Register.GetValue("pc")) != next_pc:
        raise RuntimeError("CRC read event did not stop immediately after its load")
    if destination != "r0" and int(debugger.Register.GetValue(destination)) != native_value:
        raise RuntimeError("Native CRC load destination disagrees with its bus trace")
    psw = int(debugger.Register.GetValue("psw"))
    set_state(control, control["state"])
    control["dirty"] = False
    if destination != "r0" and not debugger.Register.SetValue(destination, control["state"]):
        raise RuntimeError("Cannot complete the modeled CRC bus read")
    if int(debugger.Register.GetValue("psw")) != psw or int(debugger.Register.GetValue("pc")) != next_pc:
        raise RuntimeError("CRC read completion changed non-load architectural state")
    report["crc_reads"].append({
        "ior": control["ior"], "mode": by_name[control["mode_register"]]["state"],
        "instruction_pc": int(instruction.FetchAddress), "destination": destination,
        "native_bus_value": native_value, "modeled_bus_value": control["state"],
        "input_words": control.get("input_words", 0), "native_trace_complete": trace_complete,
    })

def terminal_address(operand, overwritten=None):
    match = re.match(r"^([+-]?(?:0x[0-9a-fA-F]+|[0-9]+))?\[([a-z0-9]+)\]$", operand)
    if match is None:
        return int(debugger.Address(operand))
    displacement, base = match.groups()
    base = REGISTER_ALIASES.get(base, base)
    overwritten = REGISTER_ALIASES.get(overwritten, overwritten)
    if overwritten != "r0" and base == overwritten:
        raise RuntimeError("Truncated load trace lost its overwritten address register")
    return (int(debugger.Register.GetValue(base)) + int(displacement or "0", 0)) & 0xFFFFFFFF

def complete_trace_tail(instruction, saw_read, saw_write):
    if instruction is None or instruction.Mnemonic is None:
        return
    mnemonic = str(instruction.Mnemonic)
    opcode = mnemonic.split()[0]
    is_store = opcode in STORE_WIDTHS
    is_load = opcode in LOAD_WIDTHS
    if not ((is_store and not saw_write) or (is_load and not saw_read)):
        return
    decoded = debugger.Assemble.Disassemble(int(instruction.FetchAddress), 1)[0]
    pc = int(debugger.Register.GetValue("pc"))
    if pc == int(decoded.Address):
        return
    if pc != int(decoded.Address) + len(decoded.Code):
        raise RuntimeError("Trace-full boundary lost more than its terminal memory transaction")
    operands = mnemonic.split(None, 1)[1]
    left, right = [part.strip() for part in operands.split(",", 1)]
    address = terminal_address(right if is_store else left, None if is_store else right)
    control = by_address.get(address)
    if control is None:
        return
    if is_store:
        width = STORE_WIDTHS[opcode]
        mask = (1 << (width * 8)) - 1
        written = int(debugger.Register.GetValue(left)) & mask
        write_device(control, address, written, instruction)
        report["trace_completed_writes"] = report.get("trace_completed_writes", 0) + 1
    elif (control.get("trigger") == "dcra-seed" or control.get("read_input", False)
            or control.get("requires_input", False)):
        width = LOAD_WIDTHS[opcode]
        if control.get("read_input", False):
            if right == "r0":
                raise RuntimeError("Truncated undefined read lost its discarded native bus response")
            native_value = int(debugger.Register.GetValue(right)) & ((1 << (8 * width)) - 1)
        else:
            native_value = (int(debugger.Register.GetValue(control["ior"])) >> (8 * (address - control["address"]))) & ((1 << (8 * width)) - 1)
        read_device(control, address, native_value, instruction, False)

def native_event_ranges(selected, excluded):
    # One enclosing range per 64-KiB peripheral window, not one event per IOR.
    # Extra native stops in gaps do not add modeled behavior. Never enclose CIN:
    # its writes remain batched by the complete native trace and COUT read event.
    windows = {}
    for control in selected:
        start = control["address"]
        end = start + control["size"] - 1
        for page in range(start >> 16, (end >> 16) + 1):
            first, last = max(start, page << 16), min(end, (page << 16) + 0xFFFF)
            previous = windows.get(page, (first, last))
            windows[page] = (min(first, previous[0]), max(last, previous[1]))
    ranges = sorted(windows.values())
    for control in excluded:
        first = control["address"]
        last = first + control["size"] - 1
        split = []
        for start, end in ranges:
            if end < first or start > last:
                split.append((start, end))
            else:
                if start < first:
                    split.append((start, first - 1))
                if end > last:
                    split.append((last + 1, end))
        ranges = split
    return ranges

class NativeRangeEvents:
    """V8.16 simulator's own access-event detail/commit path, absent from DIP."""
    def __init__(self):
        from System.Reflection import BindingFlags
        self.flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic

    def invoke(self, instance, name, arguments):
        method = instance.GetType().GetMethod(name, self.flags)
        if method is None:
            raise RuntimeError("CS+ V8.16 native event API is unavailable: " + name)
        return method.Invoke(instance, arguments)

    def install(self, start, end, access):
        condition = BreakCondition()
        condition.Address = start
        condition.BreakType = BreakType.Write if access == "Write" else BreakType.Read
        number = debugger.Breakpoint.Set(condition)
        if number is None or int(number) <= 0:
            raise RuntimeError("Cannot create native %s event at %#x" % (access, start))
        # These are protected CLR entry points, not the restricted Python DIP.
        items = self.invoke(debugger.Breakpoint, "CreateBreakInformation", None)
        item = items[System.UInt32(number)]
        details = item.GetAllEventConditionItems()
        if details.Count != 1:
            raise RuntimeError("Native access event is not a single condition")
        detail = details[0]
        manager_field = item.GetType().GetField("m_eventManager", self.flags)
        if manager_field is None:
            raise RuntimeError("CS+ V8.16 native event manager is unavailable")
        manager = manager_field.GetValue(item)
        if str(manager.GetType().Name) != "EventRh850Simulator":
            raise RuntimeError("Native range adapter requires the RH850 simulator")
        arguments = System.Array[System.Object]([detail.EventInformation, None])
        if str(self.invoke(manager, "GetEventDetailData", arguments)) != "OK":
            raise RuntimeError("Cannot obtain native access-event details")
        properties = arguments[1]
        properties.AddressCompareCondition = System.Enum.Parse(
            properties.AddressCompareCondition.GetType(), "AddressRangeIn")
        properties.StartAddress = str(start)
        properties.EndAddress = str(end)
        # Same commit used by the access-event dialog: ModifyEvent in the engine,
        # then update its event dictionary. Mutating the CLR condition alone does
        # not install a range in the simulator.
        arguments = System.Array[System.Object]([detail.EventInformation, properties])
        if str(self.invoke(manager, "SetEventDetailData", arguments)) != "OK":
            raise RuntimeError("Cannot commit native access-event range")
        native = detail.EventInformation.Condition
        arguments = System.Array[System.Object]([detail.EventInformation, None])
        if str(self.invoke(manager, "GetEventDetailData", arguments)) != "OK":
            raise RuntimeError("Cannot read back native access-event range")
        properties = arguments[1]
        if (int(native.AccessAddress) != start or int(native.EndAddress) != end
                or str(properties.AddressCompareCondition) != "AddressRangeIn"
                or str(native.AccessType) != access or str(native.AccessSize) != "NotSpecify"
                or native.CompareData is not None or int(native.PassCount) != 1
                or int(native.InverseAddressMask) != 0
                or str(detail.EventInformation.Action.Kind) != "BreakAfter"):
            raise RuntimeError("Native access-event readback differs from requested range")
        return {
            "event": int(number), "native_id": int(detail.EventInformation.ID),
            "start": int(native.AccessAddress), "end": int(native.EndAddress),
            "access": str(native.AccessType), "access_size": str(native.AccessSize),
            "address_condition": str(properties.AddressCompareCondition),
            "range": int(native.Range), "action": str(detail.EventInformation.Action.Kind),
            "adapter": "V8.16 access-event detail/SetEventDetailData",
        }

try:
    common.ThrowExcept = True
    common.ViewOutput = False
    project.Close()
    if not project.Create(contract["project"], MicomType.RH850, contract["mcu"], ProjectKind.DebugOnly, Compiler.CC_RH):
        raise RuntimeError("CS+ could not create the exact-device debug-only project")
    if not debugger.DebugTool.Change(DebugTool.Simulator):
        raise RuntimeError("CS+ could not select the simulator")
    if not debugger.Connect():
        raise RuntimeError("CS+ simulator connection failed")
    debugger.Breakpoint.Delete()
    for index, image in enumerate(contract["images"]):
        if not debugger.Download.Binary(image["path"], image["base"], index != 0):
            raise RuntimeError("CS+ could not load " + image["kind"])
        if not debugger.Upload.Binary(image["readback"], image["base"], image["base"] + image["size"] - 1, True):
            raise RuntimeError("CS+ could not read back " + image["kind"])
        with open(image["readback"], "rb") as loaded:
            content = loaded.read()
        if len(content) != image["size"] or hashlib.sha256(content).hexdigest() != image["sha256"]:
            raise RuntimeError("Simulator image identity mismatch: " + image["kind"])
    report["readback_verified_before_execution"] = True
    debugger.Reset()
    report["reset_pc"] = int(debugger.Register.GetValue("pc"))
    report["ior_inputs"] = contract["ior_inputs"]
    debugger.Option.Coverage = True
    debugger.Option.ReuseCoverageData = True
    if not debugger.XCoverage.Clear():
        raise RuntimeError("CS+ could not clear coverage from previous execution")
    controls = contract["peripheral_registers"]
    report["peripheral_registers"] = controls
    iors = debugger.GetIORList() if contract["ior_inputs"] or controls else []
    ior_addresses = {}
    iors_by_address = {}
    for row in iors:
        address = int(str(row.Address), 0)
        ior_addresses[row.IORName] = address
        iors_by_address.setdefault(address, []).append(row.IORName)
    by_address = {}
    by_name = {}
    for control in controls:
        matches = iors_by_address.get(control["address"], [])
        canonical = [name for name in matches
                     if name == control["name"] or name.endswith("." + control["name"])
                     or name.replace(".", "") == control["name"]]
        matches = canonical or matches
        if len(matches) != 1:
            raise RuntimeError("Cannot resolve modeled IOR %s at %#x: %s" %
                               (control["name"], control["address"], str(matches)))
        control["ior"] = matches[0]
        control["binding_evidence"] = "canonical-name-and-address" if canonical else "unique-exact-device-address"
        native_reset = int(debugger.Register.GetValue(control["ior"]))
        control["native_reset_value"] = native_reset
        full_mask = (1 << (8 * control["size"])) - 1
        reset_mask = control.get("reset_mask", full_mask)
        if control["reset"] is None or control.get("read_input", False):
            reset_mask = 0
        if reset_mask != full_mask:
            control["native_supplied_initial_bits"] = {
                "mask": full_mask & ~reset_mask, "value": native_reset & ~reset_mask,
                "evidence": "native simulator initial response; not a documented reset constant",
            }
        if reset_mask:
            set_state(control, (native_reset & ~reset_mask) | (control["reset"] & reset_mask))
        else:
            control["state"] = native_reset
        control["writes"] = 0
        by_name[control["name"]] = control
        control["events"] = []
        for offset in range(control["size"]):
            by_address[control["address"] + offset] = control
    if controls:
        excluded = [control for control in controls if control.get("trigger") == "dcra-input"]
        writes = [control for control in controls if control.get("trigger") != "dcra-input"]
        reads = [control for control in controls
                 if control.get("trigger") == "dcra-seed" or control.get("read_input", False)
                 or control["behavior"] == "noise-clock-status"]
        plans = [(access, start, end)
                 for access, selected in (("Write", writes), ("Read", reads))
                 for start, end in native_event_ranges(selected, excluded)]
        report["native_access_event_limit"] = 64
        if len(plans) > report["native_access_event_limit"]:
            raise RuntimeError("Modeled access ranges exceed the native 64-event limit")
        report["native_access_events"] = []
        adapter = NativeRangeEvents()
        for access, start, end in plans:
            event = adapter.install(start, end, access)
            report["native_access_events"].append(event)
            for control in writes if access == "Write" else reads:
                if start <= control["address"] and control["address"] + control["size"] - 1 <= end:
                    control["events"].append(event["event"])
        for access, selected in (("Write", writes), ("Read", reads)):
            for control in selected:
                if not any(event["access"] == access and event["start"] <= control["address"]
                           and control["address"] + control["size"] - 1 <= event["end"]
                           for event in report["native_access_events"]):
                    raise RuntimeError("Native event ranges do not cover " + control["ior"])
    if controls:
        debugger.Option.Trace = True
        debugger.Option.TraceDataAccess = True
        debugger.Option.AfterTraceMemoryFull = AfterTraceMemoryFull.Stop
        if not Save():
            raise RuntimeError("Cannot save native trace configuration")
        import clr
        clr.AddReference("System.Xml")
        from System.Xml import XmlDocument
        configuration = XmlDocument()
        configuration.Load(contract["project"])
        capacities = configuration.GetElementsByTagName("DebuggerProperty-OptionalProperty-Trace-TraceMemorySize")
        if capacities.Count != 1:
            raise RuntimeError("Cannot determine exact native trace capacity")
        report["trace_capacity"] = int(capacities[0].InnerText)
        if report["trace_capacity"] <= 0:
            raise RuntimeError("Invalid native trace capacity")
        debugger.Trace.Clear()
    if contract["ior_inputs"]:
        for name, value in contract["ior_inputs"].items():
            if name not in ior_addresses:
                raise RuntimeError("Not an IOR in the exact device: " + name)
            modeled = by_address.get(ior_addresses[name])
            if modeled is not None and (
                    modeled["behavior"] in ("dcra", "clock", "port-config", "noise-filter")
                    or modeled.get("read_value") is not None):
                raise RuntimeError("IOR input cannot override derived peripheral state: " + name)
            if not debugger.Register.SetValue(name, value):
                raise RuntimeError("CS+ rejected IOR input: " + name)
            if int(debugger.Register.GetValue(name)) != value:
                raise RuntimeError("IOR input readback mismatch: " + name)
    for control in controls:
        control["state"] = int(debugger.Register.GetValue(control["ior"]))
        if control.get("trigger") == "ecc-protected-control" and control["state"] & ~control["writable_mask"]:
            raise RuntimeError("Invalid modeled IOR initial state: " + control["ior"])
    refresh_port_aliases()
    report["device_model_sha256"] = contract["device_model_sha256"]
    report["peripheral_writes"] = 0
    report["crc_reads"] = []
    report["native_input_reads"] = []
    report["unresolved_clock_activity"] = []
    report["unsupported_triggers"] = contract.get("unsupported_triggers", [])
    report["model_scope"] = [
        "digital startup register transactions only; no ECC fault generation or ECM delivery",
        "port latches/aliases only; no external pin electrical behavior or ECM loopback",
        "noise-filter configuration only while disabled; changed source activity requires new external input",
        "undefined initial/read bits are native simulator samples, unlike strict model explicit-input requirements",
        "native MPU configuration and CPU core are unchanged",
    ]
    report["status"] = "running"
    save()
    started = time.time()
    report["observation_pause"] = False
    debugger.Go(GoOption.Normal)
    deadline = started + contract["seconds"]
    while True:
        running = bool(debugger.IsRunning())
        if time.time() >= deadline and running:
            debugger.Stop()
            report["observation_pause"] = True
            running = False
        if running:
            time.sleep(min(0.001, max(0.0, deadline - time.time())))
            continue
        reason = str(debugger.GetBreakStatus())
        if not controls:
            break
        frames = debugger.Trace.Get(report["trace_capacity"])
        if frames and (int(frames[0].FrameNumber) != 0 or int(frames[-1].FrameNumber) != len(frames) - 1):
            raise RuntimeError("Native trace is not a complete prefix of this execution interval")
        instruction = None
        saw_read = saw_write = False
        for frame in frames:
            if frame.FetchAddress is not None:
                instruction = frame
                saw_read = saw_write = False
            if frame.WriteAddress is not None:
                saw_write = True
                address = int(frame.WriteAddress)
                control = by_address.get(address)
                if control is not None:
                    if instruction is None or instruction.Mnemonic is None:
                        raise RuntimeError("Peripheral write lost its instruction provenance")
                    write_device(control, address, int(frame.WriteData), instruction)
            if frame.ReadAddress is not None:
                saw_read = True
                control = by_address.get(int(frame.ReadAddress))
                if control is not None:
                    if instruction is None or instruction.Mnemonic is None:
                        raise RuntimeError("Peripheral read lost its instruction provenance")
                    read_device(control, int(frame.ReadAddress), int(frame.ReadData), instruction)
        if reason == "TraceFull":
            complete_trace_tail(instruction, saw_read, saw_write)
        for control in controls:
            if control.get("dirty", False):
                set_state(control, control["state"])
                control["dirty"] = False
        debugger.Trace.Clear()
        if reason not in ("Event", "TraceFull"):
            break
        if time.time() >= deadline:
            break
        debugger.Go(GoOption.Normal)
    report["observation_timeout"] = time.time() >= deadline
    report["host_elapsed_seconds"] = time.time() - started
    report["break_status"] = str(debugger.GetBreakStatus())
    for control in controls:
        control["native_final_readback"] = int(debugger.Register.GetValue(control["ior"]))
    names = ["r0", "r1", "r2", "sp", "gp", "tp"] + ["r%d" % index for index in range(6, 30)] + ["ep", "lp", "pc", "psw"]
    report["registers"] = dict((name, int(debugger.Register.GetValue(name))) for name in names)
    system_names = ["fepc", "fepsw", "feic", "eipc", "eipsw", "eiic", "ebase", "rbase"]
    if controls:
        system_names += ["mea", "mei", "mpm", "mprc", "asid"]
        system_names += ["%s%d" % (kind, index) for kind in ("mpla", "mpua", "mpat") for index in range(16)]
    report["system_registers"] = dict((name, int(debugger.Register.GetValue(name))) for name in system_names)
    if not debugger.Upload.Coverage(contract["coverage"], True):
        raise RuntimeError("CS+ could not export native execution coverage")
    common.ViewOutput = True
    debugger.Assemble.Disassemble(report["registers"]["pc"], 12)
    report["status"] = "observed"
except:
    common.ViewOutput = True
    report["status"] = "error"
    report["error"] = traceback.format_exc()
    print(report["error"])
finally:
    try:
        if "debugger" in globals() and debugger.IsConnected():
            if debugger.IsRunning():
                debugger.Stop()
            debugger.Breakpoint.Delete()
            debugger.Disconnect()
    except:
        report["status"] = "error"
        report["cleanup_error"] = traceback.format_exc()
    save()
'''


def run(
    name: str, *, seconds: float, bottle: Path, output_dir: Path | None = None,
    ior_inputs: list[str] | None = None, p1me_peripherals: bool = False,
) -> dict:
    """Observe a free run; 'observed' is not a firmware lifecycle pass verdict."""
    if not math.isfinite(seconds) or seconds <= 0:
        raise CSPlusError("--seconds must be finite and positive")
    inputs = {}
    for assignment in ior_inputs or []:
        register, separator, value = assignment.partition("=")
        if not separator or not register:
            raise CSPlusError(f"expected --ior NAME=VALUE, got {assignment!r}")
        try:
            inputs[register] = int(value, 0)
        except ValueError as exc:
            raise CSPlusError(f"invalid IOR input value: {assignment!r}") from exc
    name, row = target(name)
    mcu = row.get("mcu")
    if not isinstance(mcu, str) or not mcu:
        raise CSPlusError(f"target {name} has no exact MCU identity")
    controls = []
    model_sha = None
    if p1me_peripherals:
        from tools.emulation.p1me_machine import P1MEMachineError, _load_model

        try:
            model, model_sha = _load_model()
        except P1MEMachineError as exc:
            raise CSPlusError(str(exc)) from exc
        if mcu not in {product["product_id"] for product in model["products"]}:
            raise CSPlusError(f"shared P1M-E device model does not describe {mcu}")
        controls = peripheral_registers(model["manual"]["registers"])
        if not controls:
            raise CSPlusError("generated device model lacks peripheral definitions; run tools/rh850 model update")
    images = []
    for kind in ("codeflash", "dataflash"):
        if kind not in row:
            continue
        try:
            source = verified_file(name, kind)
        except (ValueError, KeyError, OSError) as exc:
            raise CSPlusError(str(exc)) from exc
        images.append({
            "kind": kind,
            "path": windows_path(source),
            "base": int(str(row[f"{kind}_base"]), 0),
            "size": source.stat().st_size,
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        })
    if not images or images[0]["kind"] != "codeflash":
        raise CSPlusError(f"target {name} has no CodeFlash image")
    bottle = bottle.resolve()
    installation = bottle / INSTALLATION
    executable = installation / "64CS.exe"
    bootstrap = installation / BOOTSTRAP
    for required in (CROSSOVER, executable, bootstrap):
        if not required.is_file():
            raise CSPlusError(f"missing CS+ execution prerequisite: {required}")
    run_id = uuid.uuid4().hex
    work = (output_dir or REPO_ROOT / "build/out/rh850-csplus" / name / run_id).resolve()
    work.mkdir(parents=True, exist_ok=True)
    report_path = work / "report.json"
    for image in images:
        image["readback"] = windows_path(work / f"{image['kind']}-readback.bin")
    contract = {
        "run_id": run_id,
        "target": name,
        "mcu": mcu,
        "seconds": seconds,
        "images": images,
        "ior_inputs": inputs,
        "peripheral_registers": controls,
        "unsupported_triggers": sorted({
            register["trigger"] for register in model["manual"]["registers"]
            if register.get("trigger") and register["trigger"] not in SUPPORTED_TRIGGERS
        }) if p1me_peripherals else [],
        "device_model_sha256": model_sha,
        "project": windows_path(work / f"firmware-{run_id}.mtpj"),
        "report": windows_path(report_path),
        "coverage": windows_path(work / "coverage.csrcv"),
    }
    contract_path = work / "contract.json"
    contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")
    driver_path = work / "driver.py"
    driver_path.write_text("CONTRACT_PATH = u" + json.dumps(windows_path(contract_path)) + "\n" + DRIVER, encoding="utf-8")
    command = [
        str(CROSSOVER), "--bottle", str(bottle), "--no-gui", "--dll", "mscoree=n",
        str(executable), "/lang", "en-US", "/lp", "PythonConsole",
        "/ps", windows_path(driver_path), windows_path(bootstrap),
    ]
    log_path = work / "console.log"
    with log_path.open("w", encoding="utf-8") as log:
        try:
            process = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=seconds + 90, check=False)
        except subprocess.TimeoutExpired as exc:
            # Wine children can survive their Unix launcher. Kill only this run's recorded PID.
            if report_path.is_file():
                partial = json.loads(report_path.read_text(encoding="utf-8"))
                if partial.get("run_id") == run_id and isinstance(partial.get("process_id"), int):
                    subprocess.run([
                        str(CROSSOVER), "--bottle", str(bottle), "--no-gui", "--cx-app", "taskkill.exe",
                        "/pid", str(partial["process_id"]), "/f",
                    ], stdout=log, stderr=subprocess.STDOUT, timeout=15, check=False)
            raise CSPlusError(f"CS+ host timed out; execution evidence: {work}") from exc
    if not report_path.is_file():
        raise CSPlusError(f"CS+ did not execute the driver (exit {process.returncode}); see {log_path}")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("run_id") != run_id or report.get("status") != "observed" or process.returncode:
        raise CSPlusError(f"CS+ execution failed; see {report_path} and {log_path}")
    report["images"] = []
    for image in images:
        readback = work / f"{image['kind']}-readback.bin"
        actual = hashlib.sha256(readback.read_bytes()).hexdigest()
        if actual != image["sha256"] or readback.stat().st_size != image["size"]:
            raise CSPlusError(f"CS+ {image['kind']} readback differs from registered firmware: {readback}")
        report["images"].append({key: image[key] for key in ("kind", "base", "size", "sha256")})
    report["report_path"] = str(report_path)
    report["console_log"] = str(log_path)
    coverage = work / "coverage.csrcv"
    if not coverage.is_file():
        raise CSPlusError(f"CS+ did not produce its native execution coverage: {coverage}")
    report["coverage"] = str(coverage)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
