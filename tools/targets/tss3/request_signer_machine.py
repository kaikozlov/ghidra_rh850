"""Generate and run target-neutral P1M-E request-signer scenarios."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from exploit.ephemeral_runtime.build_tss3_request_signer import CONFIG_BASE, CONFIG_FIELDS
from exploit.ephemeral_runtime.tss3_request_signer import SAFE_APPLICATION, build_request
from exploit.ram_runtime.tss3_request_signer_contract import HELPER_TRANSIT_BASE
from tools import REPO_ROOT
from tools.emulation.p1me_machine import run_many
from tools.project.analysis_target import target as resolve_target

SCHEMA = "rh850-p1me-machine-scenario-v2"
REPORT_SCHEMA = "tss3-request-signer-machine-verification-v1"
RETURN_ADDRESS = 0x00010000
STACK = 0xFEBE2000
LOCAL_RAM = 0xFEBE0000
LOCAL_RAM_SIZE = 0x20000
INPUT = 0xFEBE0100
INPUT_BLOCK = 0xFEBE0200
OUTPUT_BLOCK = 0xFEBE0300
DESCRIPTOR = 0xFEF01080
PAYLOAD = 0xFEF01100

RSCFD_TX_ENTRY = {
    "role": "exact-rscfd-classic-tx",
    "scope": "function",
    "shape_sha256": "25ee217918d820e07dd1c8775ed08d2c124aa6c0eb36bf2d23435fa4bfea7848",
    "instruction_count": 69,
    "body_size": 172,
    "offset": 0,
    "requirements": [],
}
ICUS_SUBMIT_ENTRY = {
    "role": "exact-icus-command-five-submit",
    "scope": "function",
    "shape_sha256": "1cc1f56fa2265e15d26f98fdf0315534f94478862c1cd3c5e9c427a015147a6f",
    "instruction_count": 95,
    "body_size": 274,
    "offset": 0,
    "requirements": [],
}
ICUS_INPUT_ENTRY = {
    "role": "exact-icus-command-five-callback",
    "scope": "instructions",
    "shape_sha256": "7a660c536ae6cd2deccfb515979f687bed74195f37383efdcf8d7c7ef087fd7f",
    "instruction_count": 26,
    "body_size": 82,
    "offset": 0,
    "requirements": [{"index": 2, "mnemonic": "mov", "operand": 0, "scalar": "1"}],
}
ICUS_OUTPUT_ENTRY = {
    "role": "exact-icus-command-five-output-callback",
    "scope": "instructions",
    "shape_sha256": "7a660c536ae6cd2deccfb515979f687bed74195f37383efdcf8d7c7ef087fd7f",
    "instruction_count": 26,
    "body_size": 82,
    "offset": 0,
    "requirements": [{"index": 2, "mnemonic": "mov", "operand": 0, "scalar": "2"}],
}


def _hx(value: int) -> str:
    return f"0x{value:08X}"


def _le(value: int, size: int) -> str:
    return value.to_bytes(size, "little").hex()


def _resolved(role: str, address: int) -> dict[str, Any]:
    return {"role": role, "scope": "resolved-address", "address": _hx(address)}


def _registers(contract: dict[str, Any], **extra: int) -> dict[str, str]:
    execution = contract["execution"]
    values = {
        "sp": STACK,
        "gp": execution["gp"],
        "tp": execution["tp"],
        "lp": RETURN_ADDRESS,
        "PSW": 0,
        "PMR": 0,
        **extra,
    }
    return {name: _hx(value) for name, value in values.items()}


def _scenario(
    *,
    name: str,
    entry: dict[str, Any],
    contract: dict[str, Any],
    max_instructions: int,
    memory: list[dict[str, Any]],
    checks: list[dict[str, Any]],
    registers: dict[str, int] | None = None,
    stop: int = RETURN_ADDRESS,
    events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "name": name,
        "entry": entry,
        "max_instructions": max_instructions,
        "stop_addresses": [_hx(stop)],
        "gpr_fill": "0",
        "registers": _registers(contract, **(registers or {})),
        "memory": memory,
        "artifacts": [],
        "checks": checks,
        "events": events or [],
    }


def _return_check(name: str = "firmware returns through caller link") -> dict[str, Any]:
    return {
        "name": name,
        "kind": "register",
        "register": "PC",
        "equals": _hx(RETURN_ADDRESS),
    }

def _shadow_copy_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    shadow = contract["execution"]["startup_shadow_copy"]
    destination = shadow["destination"]
    end = destination + shadow["size"]
    resident_marker = bytes(range(1, 65))
    return _scenario(
        name="tss3-dynamic-startup-shadow-copy-boundary",
        entry=_resolved("dump-resolved-startup-shadow-copy", shadow["function"]),
        contract=contract,
        max_instructions=100000,
        memory=[
            {
                "address": _hx(LOCAL_RAM),
                "size": LOCAL_RAM_SIZE,
                "fill": 0xA5,
                "evidence": "scenario-owned nonzero LocalRAM baseline",
            },
            {
                "address": _hx(end),
                "hex": resident_marker.hex(),
                "evidence": "resident-boundary overwrite sentinel",
            },
        ],
        checks=[
            _return_check("startup shadow copy returns through caller link"),
            {
                "name": "startup shadow copy writes its first CodeFlash word",
                "kind": "memory",
                "address": _hx(destination),
                "size": 4,
                "equals_hex": shadow["source_first_word_hex"],
            },
            {
                "name": "startup shadow copy writes its final CodeFlash word",
                "kind": "memory",
                "address": _hx(end - 4),
                "size": 4,
                "equals_hex": shadow["source_last_word_hex"],
            },
            {
                "name": "startup shadow copy stops before the resident",
                "kind": "memory",
                "address": _hx(end),
                "size": len(resident_marker),
                "equals_hex": resident_marker.hex(),
            },
        ],
    )



def _tauj_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    entry = contract["execution"]["idle_fast"]["mode_initializer"]
    return _scenario(
        name="tss3-dynamic-tauj0-mode-initialization",
        entry=_resolved("tss3-tauj0-mode-initializer", entry),
        contract=contract,
        max_instructions=500,
        memory=[],
        checks=[
            _return_check(),
            {
                "name": "firmware selects undivided TAUJ0 prescalers",
                "kind": "memory",
                "address": "0xFFE50090",
                "size": 2,
                "equals_hex": "0000",
            },
            {
                "name": "firmware clears TAUJ0 channel-3 mode",
                "kind": "memory",
                "address": "0xFFE5008C",
                "size": 2,
                "equals_hex": "0000",
            },
        ],
    )


def _freshness_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    signer = contract["signer_abi"]
    descriptor = bytes.fromhex("1122334455667788") + bytes.fromhex("01000204")
    return _scenario(
        name="tss3-dynamic-freshness-encoder",
        entry=_resolved("tss3-freshness-encoder", signer["freshness_encode"]),
        contract=contract,
        max_instructions=200,
        registers={"r6": INPUT, "r7": INPUT_BLOCK, "r8": OUTPUT_BLOCK},
        memory=[
            {
                "address": _hx(INPUT),
                "hex": descriptor.hex(),
                "evidence": "scenario: four-bit freshness descriptor",
            },
            {
                "address": _hx(INPUT_BLOCK),
                "hex": "00",
                "evidence": "scenario: encoded freshness output",
            },
            {
                "address": _hx(OUTPUT_BLOCK),
                "hex": "08000000",
                "evidence": "scenario: available output length",
            },
        ],
        checks=[
            _return_check(),
            {
                "name": "firmware encodes the four-bit freshness value",
                "kind": "memory",
                "address": _hx(INPUT_BLOCK),
                "size": 1,
                "equals_hex": "60",
            },
            {
                "name": "firmware reports the encoded freshness length",
                "kind": "memory",
                "address": _hx(OUTPUT_BLOCK),
                "size": 4,
                "equals_hex": "04000000",
            },
        ],
    )


def _ring_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    request = contract["request"]
    payload = bytes.fromhex("1122334455667788")
    descriptor = (
        request["request_id"].to_bytes(4, "little")
        + bytes.fromhex("08000008")
        + PAYLOAD.to_bytes(4, "little")
    )
    producer_header = 0x00080008
    record = (
        producer_header.to_bytes(4, "little")
        + ((~producer_header) & 0xFFFFFFFF).to_bytes(4, "little")
        + request["request_id"].to_bytes(4, "little")
        + payload
    )
    return _scenario(
        name="tss3-dynamic-request-ring-producer",
        entry=_resolved("tss3-request-ring-producer", request["producer_function"]),
        contract=contract,
        max_instructions=2000,
        registers={"r6": 0, "r7": DESCRIPTOR},
        memory=[
            {
                "address": _hx(LOCAL_RAM),
                "size": LOCAL_RAM_SIZE,
                "fill": 0,
                "evidence": "scenario-owned zero LocalRAM baseline",
            },
            {
                "address": _hx(DESCRIPTOR),
                "hex": descriptor.hex(),
                "evidence": "scenario: dynamically resolved request record",
            },
            {
                "address": _hx(PAYLOAD),
                "hex": payload.hex(),
                "evidence": "scenario: eight-byte request payload",
            },
        ],
        checks=[
            _return_check(),
            {
                "name": "software ring consumer advances one five-word record",
                "kind": "memory",
                "address": _hx(request["ring_producer"]),
                "size": 4,
                "equals_hex": "05000000",
            },
            {
                "name": "software ring producer advances one five-word record",
                "kind": "memory",
                "address": _hx(request["ring_producer"] + 4),
                "size": 4,
                "equals_hex": "05000000",
            },
            {
                "name": "firmware publishes the exact request record",
                "kind": "memory",
                "address": _hx(request["ring_base"]),
                "size": len(record),
                "equals_hex": record.hex(),
            },
            {
                "name": "ring publication executes SYNCP",
                "kind": "sync-count",
                "operation": "SYNCP",
                "equals": "2",
            },
        ],
    )


def _receive_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    execution = contract["execution"]
    request = contract["request"]
    receive = contract["receive"]
    payload = bytes.fromhex("0001020304050607")
    header = request["request_record_header"]
    record = (
        header.to_bytes(4, "little")
        + ((~header) & 0xFFFFFFFF).to_bytes(4, "little")
        + request["request_id"].to_bytes(4, "little")
        + payload
    )
    gate_rows = [
        {
            "address": _hx(row["address"]),
            "hex": _le(row["value"], row["size"]),
            "evidence": f"dump-resolved request {name} gate",
        }
        for name, row in receive["state_gates"].items()
    ]
    stop = receive["stop_before"]
    memory = [
        {
            "address": _hx(LOCAL_RAM),
            "size": LOCAL_RAM_SIZE,
            "fill": 0,
            "evidence": "scenario-owned zero LocalRAM baseline",
        },
        *gate_rows,
        {
            "address": _hx(receive["service_gate"]),
            "hex": "01fe",
            "evidence": "dump-resolved foreground communication-service gate",
        },
        {
            "address": "0xFFFFB176",
            "hex": "4880",
            "evidence": "modeled level IRQ187 table-vector configuration",
        },
        {
            "address": "0xFFFFB110",
            "hex": "cf00",
            "evidence": "foreground TAUJ0 channel-3 interrupt starts masked and pending",
        },
        {"address": "0xFFE50090", "hex": "0000", "evidence": "TAUJ0 undivided CK0"},
        {
            "address": "0xFFE5008C",
            "hex": "0000",
            "evidence": "TAUJ0 channel-3 software-triggered interval mode",
        },
        {
            "address": "0xFFE5000C",
            "hex": "7f1a0600",
            "evidence": "steady 400000-PCLK interval",
        },
        {
            "address": "0xFFE5001C",
            "hex": "7f1a0600",
            "evidence": "scenario-owned initial timer countdown",
        },
        {"address": "0xFFE50050", "hex": "08", "evidence": "running TAUJ0 channel 3"},
        {
            "address": "0xFFD20088",
            "hex": "00000000",
            "evidence": "RSCFD global operating mode",
        },
        {
            "address": "0xFFD2008C",
            "hex": "00000000",
            "evidence": "RSCFD global operating status",
        },
        {
            "address": "0xFFD20014",
            "hex": "00000000",
            "evidence": "CAN1 communication mode",
        },
        {
            "address": "0xFFD20018",
            "hex": "00000000",
            "evidence": "CAN1 communication status",
        },
        {
            "address": "0xFFD2012C",
            "hex": "03110000",
            "evidence": "common FIFO 5 receive configuration",
        },
    ]
    return _scenario(
        name="tss3-dynamic-request-receive-to-foreground",
        entry=_resolved("tss3-foreground-timer-poll", execution["foreground"]),
        contract=contract,
        max_instructions=50000,
        stop=stop,
        registers={"RBASE": 0, "INTBP": receive["intbp"], "CTPC": 0, "CTPSW": 0},
        memory=memory,
        events=[
            {
                "kind": "clock",
                "after_instructions": 3,
                "p_bus_cycles": 400000,
                "evidence": "one explicit steady TAUJ0 channel-3 period",
            },
            {
                "kind": "can-rx",
                "after_instructions": 3,
                "fifo": receive["fifo"],
                "boundary": "post-filter",
                "can_id": _hx(request["request_id"]),
                "data_hex": payload.hex(),
                "label": request["request_rule_label"],
                "evidence": "dump-resolved functional request after acceptance filtering",
            },
        ],
        checks=[
            {
                "name": "foreground reaches its native post-ring-drain boundary",
                "kind": "register",
                "register": "PC",
                "equals": _hx(stop),
            },
            {
                "name": "one hardware request frame is accepted",
                "kind": "event-count",
                "operation": "can-rx",
                "equals": "1",
            },
            {
                "name": "native ISR pops the hardware FIFO",
                "kind": "event-count",
                "operation": "can-rx-pop",
                "equals": "1",
            },
            {
                "name": "request receive interrupt enters exactly once",
                "kind": "event-count",
                "operation": "interrupt-enter",
                "equals": "1",
            },
            {
                "name": "native EIRET returns to interrupted foreground",
                "kind": "event-count",
                "operation": "interrupt-return",
                "equals": "1",
            },
            {
                "name": "automatic in-service priority clears on EIRET",
                "kind": "register",
                "register": "ISPR",
                "equals": "0",
            },
            {
                "name": "interrupt preserves the timer-poll return PC",
                "kind": "register",
                "register": "EIPC",
                "equals": _hx(execution["foreground"] + 4),
            },
            {
                "name": "foreground acknowledges the timer request",
                "kind": "memory",
                "address": "0xFFFFB110",
                "size": 2,
                "equals_hex": "cf00",
            },
            {
                "name": "native FIFO drain clears its level source",
                "kind": "memory",
                "address": "0xFFD2018C",
                "size": 4,
                "equals_hex": "01000000",
            },
            {
                "name": "software ring cursors advance one complete record",
                "kind": "memory",
                "address": _hx(request["ring_producer"]),
                "size": 6,
                "equals_hex": "050005000000",
            },
            {
                "name": "native ring preserves request identity and bytes",
                "kind": "memory",
                "address": _hx(request["ring_base"]),
                "size": len(record),
                "equals_hex": record.hex(),
            },
        ],
    )


def _rscfd_tx_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    response_id = contract["request"]["response_id"]
    signer_abi = contract["signer_abi"]
    controller = signer_abi["response_controller"]
    resource = signer_abi["response_resource"]
    payload = bytes.fromhex("1122334455667788")
    descriptor = (
        PAYLOAD.to_bytes(4, "little")
        + response_id.to_bytes(4, "little")
        + bytes.fromhex("0000000008000000")
    )
    status_address = 0xFFD202D0 + controller * 0x10 + resource
    message_address = 0xFFD24000 + controller * 0x200 + resource * 0x20
    return _scenario(
        name="tss3-dynamic-response-rscfd-transmit",
        entry=RSCFD_TX_ENTRY,
        contract=contract,
        max_instructions=1000,
        registers={
            "r6": controller,
            "r7": resource,
            "r8": 2,
            "r9": DESCRIPTOR,
        },
        memory=[
            {
                "address": _hx(DESCRIPTOR),
                "hex": descriptor.hex(),
                "evidence": "scenario: dynamically resolved response descriptor",
            },
            {
                "address": _hx(PAYLOAD),
                "hex": payload.hex(),
                "evidence": "scenario: eight-byte response payload",
            },
        ],
        checks=[
            _return_check(),
            {
                "name": "firmware writes the response CAN identifier",
                "kind": "memory",
                "address": _hx(message_address),
                "size": 4,
                "equals_hex": _le(response_id, 4),
            },
            {
                "name": "firmware writes the response payload",
                "kind": "memory",
                "address": _hx(message_address + 0xC),
                "size": 8,
                "equals_hex": payload.hex(),
            },
            {
                "name": "RSCFD model records one transmit",
                "kind": "event-count",
                "operation": "can-tx",
                "equals": "1",
            },
            {
                "name": "RSCFD records successful transmit result",
                "kind": "memory",
                "address": _hx(status_address),
                "size": 1,
                "equals_hex": "04",
            },
        ],
    )


def _lower_can_response_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    """Execute the helper-facing lower CanIf-style response wrapper end to end.

    This closes the target-specific hop that sits above the generic RSCFD Tx
    primitive: lower handle -> controller/resource route map, controller-online
    gate, classic-PDU parsing, and the selected hardware transmit resource.
    """
    response_id = contract["request"]["response_id"]
    signer_abi = contract["signer_abi"]
    controller = signer_abi["response_controller"]
    resource = signer_abi["response_resource"]
    handle = signer_abi["response_handle"]
    online = signer_abi["lower_online_state_base"] + controller * 2
    payload = bytes.fromhex("1122334455667788")
    # Exact PduInfo shape emitted by tss3_request_signer_helper.S:
    # software confirmation handle, length/reserved, CAN ID, payload pointer.
    pdu = (
        (0x00F0).to_bytes(2, "little")
        + bytes((8, 0))
        + response_id.to_bytes(4, "little")
        + PAYLOAD.to_bytes(4, "little")
    )
    message_address = 0xFFD24000 + controller * 0x200 + resource * 0x20
    return _scenario(
        name="tss3-dynamic-response-lower-can-wrapper",
        entry=_resolved("dump-resolved-lower-can-writer", signer_abi["lower_can_write"]),
        contract=contract,
        max_instructions=5000,
        registers={"r6": handle, "r7": DESCRIPTOR},
        memory=[
            {
                "address": _hx(LOCAL_RAM),
                "size": LOCAL_RAM_SIZE,
                "fill": 0,
                "evidence": "scenario: zeroed application LocalRAM baseline",
            },
            {
                "address": _hx(online),
                "hex": "a857",
                "evidence": "exact lower-wrapper controller-online gate value 0x57A8",
            },
            {
                "address": _hx(DESCRIPTOR),
                "hex": pdu.hex(),
                "evidence": "helper-shaped lower CAN response PDU",
            },
            {
                "address": _hx(PAYLOAD),
                "hex": payload.hex(),
                "evidence": "scenario: eight-byte request-signer response payload",
            },
        ],
        checks=[
            _return_check("lower CAN wrapper returns through caller link"),
            {
                "name": "lower CAN wrapper reports success",
                "kind": "register",
                "register": "r10",
                "equals": "0",
            },
            {
                "name": "lower CAN wrapper routes the response CAN identifier",
                "kind": "memory",
                "address": _hx(message_address),
                "size": 4,
                "equals_hex": _le(response_id, 4),
            },
            {
                "name": "lower CAN wrapper routes the response payload",
                "kind": "memory",
                "address": _hx(message_address + 0xC),
                "size": 8,
                "equals_hex": payload.hex(),
            },
            {
                "name": "lower CAN wrapper reaches one RSCFD transmit",
                "kind": "event-count",
                "operation": "can-tx",
                "equals": "1",
            },
        ],
    )



def _lower_can_completion_scenario(contract: dict[str, Any]) -> dict[str, Any]:
    """Dispatch the helper's private software handle through native Tx completion."""
    signer_abi = contract["signer_abi"]
    slot = signer_abi["response_confirmation_slot"]
    return _scenario(
        name="tss3-dynamic-response-lower-can-completion",
        entry=_resolved(
            "dump-resolved-lower-can-tx-completion",
            signer_abi["lower_tx_completion"],
        ),
        contract=contract,
        max_instructions=1000,
        registers={
            "r6": signer_abi["response_controller"],
            "r7": signer_abi["response_resource"],
        },
        memory=[
            {
                "address": _hx(LOCAL_RAM),
                "size": LOCAL_RAM_SIZE,
                "fill": 0,
                "evidence": "scenario: zeroed application LocalRAM baseline",
            },
            {
                "address": _hx(slot),
                "hex": _le(signer_abi["software_confirmation_handle"], 2),
                "evidence": "helper private software-confirmation handle pending",
            },
        ],
        checks=[
            _return_check("lower CAN completion returns through caller link"),
            {
                "name": "lower CAN completion consumes the private software handle",
                "kind": "memory",
                "address": _hx(slot),
                "size": 2,
                "equals_hex": "ffff",
            },
        ],
    )


def _whole_helper_scenario(
    contract: dict[str, Any], *, helper_path: Path, trampoline: int,
    command_completed: bool,
) -> dict[str, Any]:
    """Execute the assembled universal helper across one complete request.

    The timeout case leaves the native ICU-S command in flight. The success case
    supplies only the recovered asynchronous completion state after submission;
    exact submit/input/output callback scenarios remain separate, and neither
    case pretends to model provisioned key material.
    """
    request = contract["request"]
    signer_abi = contract["signer_abi"]
    state_base = contract["memory"]["state_base"]
    runtime_config = contract["runtime_config"]
    command5_globals = signer_abi["command5_globals"]
    scratch_base = contract["memory"]["scratch_base"]

    helper_path = helper_path.resolve()
    helper = helper_path.read_bytes()
    helper_sha = hashlib.sha256(helper).hexdigest()
    config = b"".join(int(runtime_config[name]).to_bytes(4, "little") for name in CONFIG_FIELDS)

    state = bytearray(0x24)
    state[0:4] = (0x4C433841).to_bytes(4, "little")
    state[4] = 3
    state[5] = 1
    state[32:34] = (0).to_bytes(2, "little")

    request_frames = build_request(SAFE_APPLICATION, 1)
    header = request["request_record_header"]
    ring = b"".join(
        header.to_bytes(4, "little")
        + ((~header) & 0xFFFFFFFF).to_bytes(4, "little")
        + request["request_id"].to_bytes(4, "little")
        + frame
        for frame in request_frames
    )
    # Every classic eight-byte 0x777 record occupies five ring words.
    producer_index = 5 * len(request_frames)
    online_state = signer_abi["lower_online_state_base"] + signer_abi["response_controller"] * 2
    message_address = (
        0xFFD24000
        + signer_abi["response_controller"] * 0x200
        + signer_abi["response_resource"] * 0x20
    )


    scenario = _scenario(
        name=(
            "tss3-dynamic-whole-request-signer-helper-success"
            if command_completed
            else "tss3-dynamic-whole-request-signer-helper-timeout"
        ),
        entry=_resolved("exact-codeflash-indirect-call-trampoline", trampoline),
        contract=contract,
        max_instructions=200000,
        stop=trampoline + 4,
        registers={"r12": HELPER_TRANSIT_BASE},
        memory=[
            {
                "address": _hx(LOCAL_RAM),
                "size": LOCAL_RAM_SIZE,
                "fill": 0,
                "evidence": "scenario: zeroed application LocalRAM baseline",
            },
            {
                "address": _hx(CONFIG_BASE),
                "hex": config.hex(),
                "evidence": "exact dump-resolved universal runtime config",
            },
            {
                "address": _hx(state_base),
                "hex": bytes(state).hex(),
                "evidence": "resident-initialized request-signer state",
            },
            {
                "address": _hx(request["ring_producer"]),
                "hex": producer_index.to_bytes(2, "little").hex() + "000000000000",
                "evidence": "four complete request records pending at the producer",
            },
            {
                "address": _hx(request["ring_base"]),
                "hex": ring.hex(),
                "evidence": "four exact classic 0x777 request records",
            },
            {
                "address": _hx(signer_abi["auth_trip"]),
                "hex": "01000000",
                "evidence": "scenario authenticated trip epoch",
            },
            {
                "address": _hx(signer_abi["auth_reset"]),
                "hex": "01000000",
                "evidence": "scenario authenticated reset epoch",
            },
            {
                "address": _hx(command5_globals - 0x34),
                "hex": "e1",
                "evidence": "dump-relative ICU-S idle state",
            },
            {
                "address": _hx(command5_globals - 0x28),
                "hex": "e100d2",
                "evidence": "dump-relative command-router idle and available-lock state",
            },
            {
                "address": _hx(command5_globals - 0x210),
                "hex": "e1",
                "evidence": "dump-relative cryptographic manager initialized-idle state",
            },
            {
                "address": _hx(command5_globals - 0x234),
                "hex": "d2",
                "evidence": "dump-relative cryptographic manager available-lock state",
            },
            {
                "address": "0xFFC5D00C",
                "hex": "00000000",
                "evidence": "ICU-S not-busy status",
            },
            {
                "address": "0xFFC5D014",
                "hex": "00000000",
                "evidence": "ICU-S companion ready status",
            },
            {
                "address": _hx(online_state),
                "hex": "a857",
                "evidence": "target lower CAN controller online state",
            },
        ],
        checks=[
            {
                "name": "whole helper returns through exact indirect-call trampoline",
                "kind": "register",
                "register": "PC",
                "equals": _hx(trampoline + 4),
            },
            {
                "name": "whole helper assembles one four-frame request",
                "kind": "memory",
                "address": _hx(state_base + 8),
                "size": 4,
                "equals_hex": "01000000",
            },
            {
                "name": "whole helper counts one lower response transmit",
                "kind": "memory",
                "address": _hx(state_base + 16),
                "size": 4,
                "equals_hex": "01000000",
            },
            {
                "name": "whole helper emits one modeled CAN response",
                "kind": "event-count",
                "operation": "can-tx",
                "equals": "1",
            },
            {
                "name": "whole helper routes the response CAN identifier",
                "kind": "memory",
                "address": _hx(message_address),
                "size": 4,
                "equals_hex": _le(request["response_id"], 4),
            },
            {
                "name": "whole helper packs private response magic",
                "kind": "memory",
                "address": _hx(message_address + 0xC),
                "size": 1,
                "equals_hex": "c9",
            },
        ],
    )
    expected_response = "c90100fe51122334" if command_completed else "c90102fe00000000"
    scenario["checks"].extend([
        {
            "name": "whole helper exposes the command result",
            "kind": "memory",
            "address": _hx(state_base + 20),
            "size": 4,
            "equals_hex": "00010010" if command_completed else "02000110",
        },
        {
            "name": "whole helper packs the complete response status",
            "kind": "memory",
            "address": _hx(message_address + 0xC),
            "size": 8,
            "equals_hex": expected_response,
        },
    ])
    if command_completed:
        scenario["checks"].append({
            "name": "whole helper counts one successful signature",
            "kind": "memory",
            "address": _hx(state_base + 12),
            "size": 4,
            "equals_hex": "01000000",
        })
        scenario["events"] = [
            {
                "kind": "memory-write",
                "after_instructions": 2000,
                "evidence": (
                    "modeled asynchronous ICU-S output after exact command-five submission; "
                    "output bytes are scenario data, not a cryptographic claim"
                ),
                "address": _hx(scratch_base + 52),
                "data_hex": "112233445566778899aabbccddeeff00",
            },
            {
                "kind": "memory-write",
                "after_instructions": 2000,
                "evidence": (
                    "modeled asynchronous ICU-S completion after exact command-five submission"
                ),
                "address": _hx(command5_globals + 0xC),
                "data_hex": "10000000" + "00" * 12 + "0100",
            },
        ]
    scenario["artifacts"] = [
        {
            "address": _hx(HELPER_TRANSIT_BASE),
            "path": str(helper_path),
            "sha256": helper_sha,
            "executable": True,
            "evidence": "current built universal request-signer helper",
        }
    ]
    return scenario


def _icus_scenarios(contract: dict[str, Any]) -> list[dict[str, Any]]:
    base = contract["signer_abi"]["command5_globals"]
    submit = _scenario(
        name="tss3-dynamic-icus-command-five-submit",
        entry=ICUS_SUBMIT_ENTRY,
        contract=contract,
        max_instructions=500,
        registers={"r6": INPUT},
        memory=[
            {
                "address": _hx(INPUT),
                "hex": "2001befe4001befe",
                "evidence": "scenario: command descriptor and key pointers",
            },
            {
                "address": _hx(INPUT + 0x20),
                "hex": "443322118000000003000000",
                "evidence": "scenario: message, length, and selector",
            },
            {
                "address": _hx(INPUT + 0x40),
                "hex": "88776655",
                "evidence": "scenario: nonzero key input",
            },
            {
                "address": _hx(base - 0x34),
                "hex": "e1",
                "evidence": "dump-relative ICU-S idle state",
            },
            {
                "address": "0xFFC5D00C",
                "hex": "00000000",
                "evidence": "ICU-S not-busy status",
            },
            {
                "address": "0xFFC5D014",
                "hex": "00000000",
                "evidence": "ICU-S companion ready status",
            },
        ],
        checks=[
            {
                "name": "command-five engine returns success",
                "kind": "register",
                "register": "r10",
                "equals": "0",
            },
            _return_check("command-five engine returns through caller link"),
            {
                "name": "firmware submits one ICU-S command",
                "kind": "event-count",
                "operation": "icus-command",
                "equals": "1",
            },
            {
                "name": "command engine retains message input",
                "kind": "memory",
                "address": _hx(base - 0x60),
                "size": 4,
                "equals_hex": "44332211",
            },
            {
                "name": "command engine retains key input",
                "kind": "memory",
                "address": _hx(base - 0x5C),
                "size": 4,
                "equals_hex": "88776655",
            },
            {
                "name": "command engine enters command-five in-flight state",
                "kind": "memory",
                "address": _hx(base - 0x34),
                "size": 1,
                "equals_hex": "d2",
            },
        ],
    )
    input_callback = _scenario(
        name="tss3-dynamic-icus-command-five-input-callback",
        entry=ICUS_INPUT_ENTRY,
        contract=contract,
        max_instructions=200,
        memory=[
            {
                "address": _hx(base - 0x74),
                "hex": "0100000000000000",
                "evidence": "dump-relative input block count and cursor",
            },
            {
                "address": _hx(base - 0x60),
                "hex": "0002befe",
                "evidence": "dump-relative input pointer",
            },
            {
                "address": _hx(base - 0x50),
                "hex": "fffd4101",
                "evidence": "dump-relative inverted input pointer",
            },
            {
                "address": _hx(INPUT_BLOCK),
                "hex": "112233445566778899aabbccddeeff00",
                "evidence": "scenario: authenticated input block",
            },
        ],
        checks=[
            {
                "name": "command-five input callback returns success",
                "kind": "register",
                "register": "r10",
                "equals": "0",
            },
            _return_check("command-five input callback returns through caller link"),
            {
                "name": "native callback feeds the fourth input word",
                "kind": "memory",
                "address": "0xFFC5D004",
                "size": 4,
                "equals_hex": "ddeeff00",
            },
            {
                "name": "native callback advances input pointer",
                "kind": "memory",
                "address": _hx(base - 0x60),
                "size": 4,
                "equals_hex": "1002befe",
            },
            {
                "name": "native callback advances input cursor",
                "kind": "memory",
                "address": _hx(base - 0x70),
                "size": 4,
                "equals_hex": "01000000",
            },
            {
                "name": "native input callback acknowledges ICU-S",
                "kind": "memory",
                "address": "0xFFC5D024",
                "size": 4,
                "equals_hex": "01000000",
            },
        ],
    )
    output_callback = _scenario(
        name="tss3-dynamic-icus-command-five-output-callback",
        entry=ICUS_OUTPUT_ENTRY,
        contract=contract,
        max_instructions=200,
        memory=[
            {
                "address": _hx(base - 0x6C),
                "hex": "0100000000000000",
                "evidence": "dump-relative output block count and cursor",
            },
            {
                "address": _hx(base - 0x5C),
                "hex": "0003befe",
                "evidence": "dump-relative output pointer",
            },
            {
                "address": _hx(base - 0x4C),
                "hex": "fffc4101",
                "evidence": "dump-relative inverted output pointer",
            },
            {
                "address": _hx(OUTPUT_BLOCK),
                "hex": "00" * 16,
                "evidence": "scenario: command-five output block",
            },
            {
                "address": "0xFFC5D008",
                "hex": "11223344",
                "evidence": "scenario: supplied ICU-S output word",
            },
        ],
        checks=[
            {
                "name": "command-five output callback returns success",
                "kind": "register",
                "register": "r10",
                "equals": "0",
            },
            _return_check("command-five output callback returns through caller link"),
            {
                "name": "native callback copies four ICU-S output words",
                "kind": "memory",
                "address": _hx(OUTPUT_BLOCK),
                "size": 16,
                "equals_hex": "11223344" * 4,
            },
            {
                "name": "native callback advances output pointer",
                "kind": "memory",
                "address": _hx(base - 0x5C),
                "size": 4,
                "equals_hex": "1003befe",
            },
            {
                "name": "native callback advances output cursor",
                "kind": "memory",
                "address": _hx(base - 0x68),
                "size": 4,
                "equals_hex": "01000000",
            },
            {
                "name": "native output callback acknowledges ICU-S",
                "kind": "memory",
                "address": "0xFFC5D024",
                "size": 4,
                "equals_hex": "02000000",
            },
        ],
    )
    return [submit, input_callback, output_callback]


def request_signer_machine_scenarios(
    contract: dict[str, Any], *, helper_path: Path, trampoline: int,
) -> list[dict[str, Any]]:
    return [
        _shadow_copy_scenario(contract),
        _tauj_scenario(contract),
        _freshness_scenario(contract),
        _ring_scenario(contract),
        _receive_scenario(contract),
        _rscfd_tx_scenario(contract),
        _lower_can_response_scenario(contract),
        _lower_can_completion_scenario(contract),
        _whole_helper_scenario(
            contract, helper_path=helper_path, trampoline=trampoline, command_completed=False,
        ),
        _whole_helper_scenario(
            contract, helper_path=helper_path, trampoline=trampoline, command_completed=True,
        ),
        *_icus_scenarios(contract),
    ]


def _helper_trampoline(target_name: str, expected_sha256: str) -> int:
    resolved_name, target = resolve_target(target_name)
    codeflash = REPO_ROOT / target["codeflash"]
    image = codeflash.read_bytes()
    if hashlib.sha256(image).hexdigest() != expected_sha256:
        raise RuntimeError(f"{resolved_name}: request-signer machine CodeFlash identity drift")
    # Any exact-CodeFlash `jarl [r12], lp` is sufficient as a model-only
    # trampoline into the executable RAM artifact. Choose the first aligned
    # instance deterministically and stop at its return address.
    pattern = bytes.fromhex("ecc760f9")
    hits = [
        offset for offset in range(0, len(image) - len(pattern) + 1, 2)
        if image[offset:offset + len(pattern)] == pattern
    ]
    if not hits:
        raise RuntimeError(f"{resolved_name}: no exact indirect-call trampoline")
    return hits[0]


def verify_request_signer_target(
    *,
    target: str,
    contract: dict[str, Any],
    helper_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    scenario_dir = output_dir / "scenarios"
    report_dir = output_dir / "reports"
    scenario_dir.mkdir(parents=True, exist_ok=True)
    trampoline = _helper_trampoline(target, contract["codeflash_sha256"])
    scenarios = request_signer_machine_scenarios(
        contract, helper_path=helper_path, trampoline=trampoline,
    )
    paths: list[Path] = []
    for scenario in scenarios:
        path = scenario_dir / f"{scenario['name']}.json"
        path.write_text(
            json.dumps(scenario, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        paths.append(path)
    reports = run_many(target, paths, report_dir)
    result = {
        "schema": REPORT_SCHEMA,
        "status": "verified-local-execution",
        "target": target,
        "codeflash_sha256": contract["codeflash_sha256"],
        "scenario_count": len(reports),
        "scenarios": [
            {
                "name": report["scenario"],
                "status": report["status"],
                "instruction_count": report["instruction_count"],
                "entry_resolution": report["entry_resolution"],
                "report": report["report_path"],
            }
            for report in reports
        ],
        "evidence_boundary": (
            "exact registered firmware plus dump-resolved contract and P1M-E functional model; "
            "no silicon, timing, vehicle, or provisioned-key claim"
        ),
    }
    (output_dir / "report.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result
