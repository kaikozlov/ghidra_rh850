#!/usr/bin/env python3
"""Compare the exact Camry F33 DCM policy matrix with a Gallia UDS server."""
from __future__ import annotations

import argparse
import asyncio
import importlib.metadata
import re
import json
import sys
from collections import Counter, defaultdict
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from tools import REPO_ROOT

TARGET = "camry-8965F3307000"
DEFAULT_OUT = (
    REPO_ROOT
    / "build/out/targets/camry-8965F3307000/gallia-reference/report.json"
)
GALLIA_VERSION = "2.2.0"
GALLIA_LICENSE = "Apache-2.0"
FINAL_NEGATIVE = 0xFEBE5967

SERVICE_CLAUSES = {
    0x10: "ISO 14229-1:2020 DiagnosticSessionControl request/response clause",
    0x14: "ISO 14229-1:2020 ClearDiagnosticInformation request/response clause",
    0x19: "ISO 14229-1:2020 ReadDTCInformation request/response clause",
    0x22: "ISO 14229-1:2020 ReadDataByIdentifier request/response clause",
    0x23: "ISO 14229-1:2020 ReadMemoryByAddress request/response clause",
    0x27: "ISO 14229-1:2020 SecurityAccess requestSeed positive-response clause; NRC 0x13 incorrect length/format",
    0x28: "ISO 14229-1:2020 CommunicationControl request/response clause",
    0x2E: "ISO 14229-1:2020 WriteDataByIdentifier request/response clause",
    0x31: "ISO 14229-1:2020 RoutineControl request/response clause",
    0x3E: "ISO 14229-1:2020 TesterPresent request/response clause",
    0x85: "ISO 14229-1:2020 ControlDTCSetting request/response clause",
}
SUBFUNCTION_SERVICES = frozenset((0x10, 0x19, 0x27, 0x28, 0x31, 0x3E, 0x85))
IDENTIFIER_SERVICES = frozenset((0x22, 0x2E))
INVALID_SUBFUNCTION_SERVICES = frozenset((0x10, 0x19, 0x27, 0x28, 0x3E, 0x85))


@dataclass(frozen=True)
class MatrixCase:
    service: int
    session: int
    security: int
    variant: str
    request: bytes

    @property
    def name(self) -> str:
        return (
            f"sid_{self.service:02x}_s{self.session}_sec{self.security}_"
            f"{self.variant}"
        )

    @property
    def clause(self) -> str:
        if self.variant == "truncated":
            return SERVICE_CLAUSES[self.service] + "; Annex A.1 NRC 0x13"
        if self.variant == "invalid":
            nrc = (
                0x13
                if self.service == 0x14
                else 0x12
                if self.service in INVALID_SUBFUNCTION_SERVICES
                else 0x31
            )
            return SERVICE_CLAUSES[self.service] + f"; Annex A.1 NRC 0x{nrc:02X}"
        return SERVICE_CLAUSES[self.service]

    @property
    def expected_nrc(self) -> int | None:
        if self.variant == "truncated":
            return 0x13
        if self.variant == "invalid":
            if self.service == 0x14:
                return 0x13
            return 0x12 if self.service in INVALID_SUBFUNCTION_SERVICES else 0x31
        return None


@dataclass(frozen=True)
class Comparison:
    service: int
    request: str
    session: int
    security: int
    variant: str
    firmware_response: str
    reference_response: str
    classification: str
    clause: str
    clause_favors: str


def matrix_cases() -> tuple[MatrixCase, ...]:
    rows: list[MatrixCase] = []
    specs = (
        (0x10, (1, 2, 3), bytes.fromhex("1001"), bytes.fromhex("107f")),
        (0x14, (1, 3), bytes.fromhex("14ffffff"), bytes.fromhex("14ffffff00")),
        (0x19, (1, 3), bytes.fromhex("1901ff"), bytes.fromhex("197f")),
        (0x22, (1, 2, 3), bytes.fromhex("222030"), bytes.fromhex("22ffff")),
        (
            0x23,
            (3,),
            bytes.fromhex("231501febe700001"),
            bytes.fromhex("2315fffebe700001"),
        ),
        (0x27, (2, 3), None, None),
        (0x28, (3,), bytes.fromhex("280101"), bytes.fromhex("287f01")),
        (0x2E, (2, 3), bytes.fromhex("2e201201"), bytes.fromhex("2effff00")),
        (0x31, (1, 2, 3), bytes.fromhex("31011000"), bytes.fromhex("3101ffff")),
        (0x3E, (1, 2, 3), bytes.fromhex("3e00"), bytes.fromhex("3e7f")),
        (0x85, (3,), bytes.fromhex("8501"), bytes.fromhex("857f")),
    )
    for sid, sessions, common_valid, common_invalid in specs:
        for session in sessions:
            if sid == 0x27:
                valid = bytes((0x27, 0x01 if session == 2 else 0x03))
                invalid = bytes.fromhex("277f")
            else:
                assert common_valid is not None and common_invalid is not None
                valid, invalid = common_valid, common_invalid
            rows.extend((
                MatrixCase(sid, session, 0, "valid", valid),
                MatrixCase(sid, session, 0, "truncated", valid[:-1]),
                MatrixCase(sid, session, 0, "invalid", invalid),
            ))
    return tuple(rows)


def _is_negative(response: bytes) -> bool:
    return len(response) == 3 and response[0] == 0x7F


def response_shape(request: bytes, response: bytes) -> tuple[Any, ...]:
    if _is_negative(response):
        return ("negative", response[1], response[2], len(response))
    sid = request[0] if request else -1
    subfunction = (
        response[1] & 0x7F
        if sid in SUBFUNCTION_SERVICES and len(response) >= 2
        else None
    )
    identifier = (
        response[1:3]
        if sid in IDENTIFIER_SERVICES and len(response) >= 3
        else response[2:4]
        if sid == 0x31 and len(response) >= 4
        else None
    )
    return (
        "positive",
        response[0] if response else None,
        subfunction,
        identifier,
        len(response),
    )


def classify_response(
    firmware: bytes | None,
    reference: bytes | None,
    request: bytes = b"",
) -> str:
    """Return comparison class a-e from the E6 campaign contract."""
    if firmware is None or reference is None:
        return "e"
    firmware_negative = _is_negative(firmware)
    reference_negative = _is_negative(reference)
    if firmware_negative and reference_negative:
        if firmware[2] != reference[2]:
            return "b"
        return (
            "a"
            if response_shape(request, firmware) == response_shape(request, reference)
            else "d"
        )
    if firmware_negative != reference_negative:
        return "c"
    return (
        "a"
        if response_shape(request, firmware) == response_shape(request, reference)
        else "d"
    )


def clause_favors(
    case: MatrixCase,
    firmware: bytes | None,
    reference: bytes | None,
) -> str:
    expected_nrc = case.expected_nrc

    def conforms(response: bytes | None) -> bool:
        if response is None:
            return False
        if expected_nrc is not None:
            return _is_negative(response) and response[2] == expected_nrc
        return not _is_negative(response)

    firmware_conforms = conforms(firmware)
    reference_conforms = conforms(reference)
    if firmware_conforms and reference_conforms:
        return "both"
    if firmware_conforms:
        return "firmware"
    if reference_conforms:
        return "reference"
    return "neither"


def _load_gallia() -> dict[str, Any]:
    # Gallia 2.2.0 omits a Darwin TransportScheme declaration. Its UDS server
    # is platform-neutral, so use the complete registry only while importing.
    native_platform = sys.platform
    if native_platform == "darwin":
        import sysconfig  # noqa: F401
        import zoneinfo  # noqa: F401

        import pydantic  # noqa: F401

        sys.platform = "linux"
    try:
        from gallia.services.uds.core import service
        from gallia.services.uds.core.constants import UDSErrorCodes, UDSIsoServices
        from gallia.services.uds.server import (
            TCPUDSServerTransport,
            UDSServer,
            UDSServerTransport,
        )
        from gallia.transports import TargetURI
    except ImportError as exc:
        raise SystemExit(
            f"Gallia {GALLIA_VERSION} is required; run with "
            f"`uv run --locked --with gallia=={GALLIA_VERSION} python -m "
            f"{__spec__.name} ...`"
        ) from exc
    finally:
        sys.platform = native_platform
    return {
        "service": service,
        "UDSErrorCodes": UDSErrorCodes,
        "UDSIsoServices": UDSIsoServices,
        "TCPUDSServerTransport": TCPUDSServerTransport,
        "UDSServer": UDSServer,
        "UDSServerTransport": UDSServerTransport,
        "TargetURI": TargetURI,
    }


def make_reference_server() -> Any:
    api = _load_gallia()
    service = api["service"]
    errors = api["UDSErrorCodes"]
    iso_services = api["UDSIsoServices"]
    base = api["UDSServer"]

    from tools.targets.camry.research.fuzz_camry_f33_dcm_handlers import (
        ROUTINE_RIDS,
        WDBI_DIDS,
        publication_rows,
    )

    readable_dids = {did: length for did, length, _reader in publication_rows()}
    writable_dids = frozenset(WDBI_DIDS)
    routine_rids = frozenset(ROUTINE_RIDS)
    writable_widths = {
        did: 2 if did in (0x0204, 0x2013) else 1 for did in writable_dids
    }
    routine_response_widths = {
        0x1000: 32,
        0x1001: 32,
        0x1010: 49,
        0x1100: 32,
    }
    subfunctions = {
        0x10: {1: (1, 2, 3), 2: (2, 3), 3: (1, 3)},
        0x19: {1: (1, 3), 2: (1, 3), 3: (1, 3), 4: (1, 3)},
        0x27: {1: (2,), 2: (2,), 3: (3,), 4: (3,)},
        0x28: {0: (3,), 1: (3,), 3: (3,)},
        0x3E: {0: (1, 2, 3)},
        0x85: {1: (3,), 2: (3,)},
    }
    sessions = {
        0x10: (1, 2, 3),
        0x14: (1, 3),
        0x19: (1, 3),
        0x22: (1, 2, 3),
        0x23: (3,),
        0x27: (2, 3),
        0x28: (3,),
        0x2E: (2, 3),
        0x31: (1, 2, 3),
        0x3E: (1, 2, 3),
        0x85: (3,),
    }

    class CamryReferenceServer(base):
        class Behavior(base.Behavior):
            default_response_if_missing_sub_function: bool = False
            default_response_if_sub_function_not_supported: bool = False
            default_response_if_incorrect_format: bool = False
            default_response_if_session_change: bool = False
            default_response_if_session_read: bool = False
            default_response_if_tester_present: bool = False
            default_response_if_none: bool = False

        def __init__(self) -> None:
            super().__init__()
            self.conditions_ok: dict[int, bool] = defaultdict(lambda: True)
            self.security_delay_active = False
            self.failed_keys = 0
            self.seed_pending: dict[int, bytes] = {}

        @property
        def supported_services(self) -> dict[int, dict[Any, list[int] | None]]:
            result: dict[int, dict[Any, list[int] | None]] = {1: {}, 2: {}, 3: {}}
            for sid, allowed_sessions in sessions.items():
                for session_id in allowed_sessions:
                    values = subfunctions.get(sid)
                    result[session_id][iso_services(sid)] = (
                        None
                        if values is None
                        else [
                            sub
                            for sub, sub_sessions in values.items()
                            if session_id in sub_sessions
                        ]
                    )
            return result

        @staticmethod
        def raw(pdu: bytes) -> Any:
            return service.RawPositiveResponse(pdu)

        @staticmethod
        def negative(sid: int, code: Any) -> Any:
            return service.NegativeResponse(sid, code)

        def validate_subfunction(self, pdu: bytes) -> Any | None:
            sid = pdu[0]
            if sid not in subfunctions:
                return None
            if len(pdu) < 2:
                return self.negative(
                    sid, errors.incorrectMessageLengthOrInvalidFormat
                )
            sub = pdu[1] & 0x7F
            if sub not in subfunctions[sid]:
                return self.negative(sid, errors.subFunctionNotSupported)
            if self.state.session not in subfunctions[sid][sub]:
                return self.negative(
                    sid, errors.subFunctionNotSupportedInActiveSession
                )
            return None

        def conditions(self, sid: int) -> Any | None:
            if self.conditions_ok[sid]:
                return None
            return self.negative(sid, errors.conditionsNotCorrect)

        async def respond_after_default(self, request: Any) -> Any | None:
            pdu = request.pdu
            sid = pdu[0]
            if (rejected := self.validate_subfunction(pdu)) is not None:
                return rejected

            if sid == 0x10:
                if len(pdu) != 2:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                session_id = pdu[1] & 0x7F
                self.state.session = session_id
                return self.raw(bytes((0x50, session_id, 0x00, 0x32, 0x01, 0xF4)))
            if sid == 0x14:
                if len(pdu) != 4:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                return self.raw(b"\x54")
            if sid == 0x19:
                sub = pdu[1] & 0x7F
                expected = {1: 3, 2: 3, 3: 2, 4: 6}[sub]
                if len(pdu) != expected:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                if sub == 1:
                    return self.raw(b"\x59\x01\x00\x01\x00\x00")
                if sub == 2:
                    return self.raw(b"\x59\x02\x00")
                if sub == 3:
                    return self.raw(b"\x59\x03")
                return self.raw(b"\x59\x04" + pdu[2:5] + b"\x00" + pdu[5:6])
            if sid == 0x22:
                if len(pdu) < 3 or len(pdu) % 2 == 0:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                dids = [
                    int.from_bytes(pdu[offset:offset + 2], "big")
                    for offset in range(1, len(pdu), 2)
                ]
                if any(did not in readable_dids for did in dids):
                    return self.negative(sid, errors.requestOutOfRange)
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                records = b"".join(
                    did.to_bytes(2, "big") + bytes(readable_dids[did])
                    for did in dids
                )
                return self.raw(b"\x62" + records)
            if sid == 0x23:
                if len(pdu) < 2:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                address_width, size_width = pdu[1] & 0x0F, pdu[1] >> 4
                if len(pdu) != 2 + address_width + size_width:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if pdu[1] != 0x15 or pdu[2] != 1 or pdu[-1] == 0:
                    return self.negative(sid, errors.requestOutOfRange)
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                return self.raw(b"\x63" + bytes(pdu[-1]))
            if sid == 0x27:
                sub = pdu[1] & 0x7F
                if not sub & 1 and len(pdu) != 18:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                level = sub if sub & 1 else sub - 1
                if self.security_delay_active:
                    return self.negative(sid, errors.requiredTimeDelayNotExpired)
                if sub & 1:
                    seed = bytes(16)
                    self.seed_pending[level] = seed
                    return self.raw(bytes((0x67, sub)) + seed)
                if level not in self.seed_pending:
                    return self.negative(sid, errors.requestSequenceError)
                expected_key = self.seed_pending.pop(level)
                if pdu[2:] != expected_key:
                    self.failed_keys += 1
                    if self.failed_keys >= 2:
                        self.failed_keys = 0
                        self.security_delay_active = True
                        return self.negative(sid, errors.exceededNumberOfAttempts)
                    return self.negative(sid, errors.invalidKey)
                self.state.security_access_level = level
                return self.raw(bytes((0x67, sub)))
            if sid == 0x28:
                if len(pdu) != 3:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if pdu[2] != 1:
                    return self.negative(sid, errors.requestOutOfRange)
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                return self.raw(bytes((0x68, pdu[1] & 0x7F)))
            if sid == 0x2E:
                if len(pdu) < 3:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                did = int.from_bytes(pdu[1:3], "big")
                if did not in writable_dids:
                    return self.negative(sid, errors.requestOutOfRange)
                if len(pdu) != 3 + writable_widths[did]:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                return self.raw(b"\x6e" + pdu[1:3])
            if sid == 0x31:
                if len(pdu) < 4:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                control = pdu[1] & 0x7F
                if control not in (1, 2, 3):
                    return self.negative(sid, errors.subFunctionNotSupported)
                rid = int.from_bytes(pdu[2:4], "big")
                if rid not in routine_rids:
                    return self.negative(sid, errors.requestOutOfRange)
                option_width = (
                    {0x1004: 2, 0x1010: 64}.get(rid, 0) if control == 1 else 0
                )
                if len(pdu) != 4 + option_width:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                record_width = routine_response_widths.get(rid, 0)
                return self.raw(
                    bytes((0x71, control)) + pdu[2:4] + bytes(record_width)
                )
            if sid == 0x3E:
                if len(pdu) != 2:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                return self.raw(b"\x7e\x00")
            if sid == 0x85:
                if len(pdu) != 2:
                    return self.negative(
                        sid, errors.incorrectMessageLengthOrInvalidFormat
                    )
                if (rejected := self.conditions(sid)) is not None:
                    return rejected
                return self.raw(bytes((0xC5, pdu[1] & 0x7F)))
            return None

    return CamryReferenceServer()


async def reference_response(case: MatrixCase) -> bytes | None:
    api = _load_gallia()
    server = make_reference_server()
    server.state.session = case.session
    server.state.security_access_level = case.security or None
    transport = api["UDSServerTransport"](
        server, api["TargetURI"]("tcp-lines://127.0.0.1:0")
    )
    await server.setup()
    try:
        response, _elapsed = await transport.handle_request(case.request)
        return response
    finally:
        await server.teardown()


def firmware_responses(
    cases: Sequence[MatrixCase],
    work: Path,
    timeout: float,
    batch_size: int,
) -> tuple[dict[tuple[bytes, int, int], bytes | None], list[dict[str, Any]]]:
    from tools.targets.camry.research import (
        fuzz_camry_f33_dcm_handlers as dcm,
        fuzz_camry_f33_stateful_coverage as stateful,
    )

    work.mkdir(parents=True, exist_ok=True)
    elf, _model = stateful.prepare_elf(work, timeout)
    trials: list[tuple[int, MatrixCase, Any]] = []
    for index, case in enumerate(cases):
        step = stateful.request(case.request)
        primes = (
            dcm.dispatcher_primes(0, case.request, case.session)
            + dcm.session_primes(case.session, case.security)
            + ((stateful.TRANSPORT_CONTEXT, stateful.transport_context(step)),)
        )
        trials.append((
            index,
            case,
            dcm.Trial(case.name, dcm.DISPATCH_TASK, (), primes),
        ))

    publication_number = len(dcm.SINKS) + 3
    publication_probe = (
        "break *0x933f8",
        f"commands {publication_number}",
        "silent",
        'printf "E6PUB %x %x %x\\n", *(unsigned int*)$r6, '
        "*(unsigned short*)($r6+4), $r7",
        "continue",
        "end",
    )
    responses: dict[tuple[bytes, int, int], bytes | None] = {}
    publication_re = re.compile(
        r"^E6PUB ([0-9a-fA-F]+) ([0-9a-fA-F]+) ([0-9a-fA-F]+)$"
    )
    fill_groups = (
        (0, [row for row in trials if row[1].service not in (0x22, 0x2E)]),
        (None, [row for row in trials if row[1].service in (0x22, 0x2E)]),
    )
    run_index = 0
    for salt, selected in fill_groups:
        for offset in range(0, len(selected), batch_size):
            group = selected[offset:offset + batch_size]
            output, _images = dcm.run_batch(
                elf,
                [(index, trial) for index, _case, trial in group],
                work,
                timeout,
                f"uds-reference-{run_index:04d}",
                salt=salt,
                extra_prelude=publication_probe,
            )
            run_index += 1
            publications: dict[int, tuple[int, int, int]] = {}
            pending: list[tuple[int, int, int]] = []
            for line in output.splitlines():
                if match := publication_re.fullmatch(line):
                    pending.append(
                        tuple(int(value, 16) for value in match.groups())
                    )
                    continue
                if match := dcm.RX_LINE.fullmatch(line):
                    index = int(match.group(1))
                    if pending:
                        publications[index] = pending[-1]
                    pending.clear()

            for index, case, _trial in group:
                dump_path = elf.parent / f"tp-{index:06d}.bin"
                image_path = elf.parent / f"img-{index:06d}.bin"
                if not dump_path.is_file():
                    raise RuntimeError(
                        f"matrix case {case.name} has no completed dump"
                    )
                dump = dump_path.read_bytes()
                context = dcm.ACTIVE_DCM_CONTEXT - dcm.RAM_BASE
                response = dcm.RESP_BUF - dcm.RAM_BASE
                active_length = int.from_bytes(
                    dump[context + 12:context + 16], "little"
                )
                use_active = (
                    case.variant == "valid"
                    and active_length > 0
                    and not (case.service == 0x27 and case.session == 2)
                )
                if use_active:
                    value: bytes | None = dump[
                        response:response + active_length
                    ]
                    if case.service == 0x27 and len(value) == 2:
                        value += bytes(16)
                elif index not in publications:
                    raise RuntimeError(
                        f"matrix case {case.name} has no published response"
                    )
                else:
                    data, length, disposition = publications[index]
                    if disposition == 0:
                        start = data - dcm.RAM_BASE
                        if start < 0 or start + length > len(dump):
                            raise RuntimeError(
                                f"matrix case {case.name} published outside modeled RAM"
                            )
                        value = dump[start:start + length]
                    elif disposition == 1:
                        start = FINAL_NEGATIVE - dcm.RAM_BASE
                        value = dump[start:start + 3]
                    elif disposition == 2:
                        value = None
                    else:
                        raise RuntimeError(
                            f"matrix case {case.name} remained pending "
                            f"(disposition {disposition})"
                        )
                responses[(case.request, case.session, case.security)] = value
                dump_path.unlink(missing_ok=True)
                image_path.unlink(missing_ok=True)
    return responses, []


async def compare(
    out: Path,
    timeout: float,
    batch_size: int,
) -> dict[str, Any]:
    cases = matrix_cases()
    firmware, hangs = firmware_responses(
        cases, out.parent / "gnu-matrix", timeout, batch_size
    )
    rows: list[Comparison] = []
    for case in cases:
        firmware_response = firmware.get(
            (case.request, case.session, case.security)
        )
        reference = await reference_response(case)
        rows.append(Comparison(
            service=case.service,
            request=case.request.hex(),
            session=case.session,
            security=case.security,
            variant=case.variant,
            firmware_response=(
                "" if firmware_response is None else firmware_response.hex()
            ),
            reference_response="" if reference is None else reference.hex(),
            classification=classify_response(
                firmware_response, reference, case.request
            ),
            clause=case.clause,
            clause_favors=clause_favors(case, firmware_response, reference),
        ))

    class_counts = Counter(row.classification for row in rows)
    service_counts: dict[str, dict[str, int]] = {}
    for sid in sorted({row.service for row in rows}):
        service_rows = [row for row in rows if row.service == sid]
        counts = Counter(row.classification for row in service_rows)
        service_counts[f"0x{sid:02X}"] = {
            "cells": len({(row.session, row.security) for row in service_rows}),
            "compared": len(service_rows),
            "equal": counts.get("a", 0),
            "b": counts.get("b", 0),
            "c": counts.get("c", 0),
            "d": counts.get("d", 0),
            "e": counts.get("e", 0),
        }
    return {
        "schema": "camry-f33-gallia-uds-reference-matrix-v2",
        "target": TARGET,
        "library": {
            "name": "Gallia",
            "version": importlib.metadata.version("gallia"),
            "license": GALLIA_LICENSE,
        },
        "services": len(service_counts),
        "cells": sum(row["cells"] for row in service_counts.values()),
        "requests": len(rows),
        "payload_comparison": (
            "Record payload bytes unknown to the reference are excluded; "
            "response class, echoes, NRC, and total length are compared."
        ),
        "class_counts": {key: class_counts.get(key, 0) for key in "abcde"},
        "service_counts": service_counts,
        "gnu_hangs": hangs,
        "comparisons": [asdict(row) for row in rows],
    }


async def serve(host: str, port: int) -> None:
    api = _load_gallia()
    server = make_reference_server()
    transport = api["TCPUDSServerTransport"](
        server, api["TargetURI"](f"tcp-lines://{host}:{port}")
    )
    await server.setup()
    try:
        await transport.run()
    finally:
        await server.teardown()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    compare_parser = subparsers.add_parser(
        "compare", help="run the GNU-sim policy matrix and compare it in process"
    )
    compare_parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    compare_parser.add_argument("--timeout", type=float, default=120.0)
    compare_parser.add_argument("--batch-size", type=int, default=96)
    serve_parser = subparsers.add_parser(
        "serve", help="serve line-delimited hexadecimal UDS over TCP"
    )
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=13400)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "serve":
        asyncio.run(serve(args.host, args.port))
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    report = asyncio.run(compare(args.out, args.timeout, args.batch_size))
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "report": str(args.out),
        "library": report["library"],
        "cells": report["cells"],
        "requests": report["requests"],
        "class_counts": report["class_counts"],
        "gnu_hangs": len(report["gnu_hangs"]),
    }, indent=2))
    return 0 if not report["gnu_hangs"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
