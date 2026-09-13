#!/usr/bin/env python3
"""Verify the exact-F33 finite network-only EPS triage state machine."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.targets.camry.live import camry_f33_eps_network_triage as triage


passed = failed = 0


def check(name: str, condition: object, detail: str = "") -> None:
    global passed, failed
    ok = bool(condition)
    passed += int(ok)
    failed += int(not ok)
    suffix = f" ({detail})" if detail else ""
    print(f"[{'PASS' if ok else 'FAIL'}] {name}{suffix}")


BRAKE_VALUE = bytes.fromhex("f700fd007c00a9000000")
BRAKE_POSITIVE = bytes.fromhex("62102f") + BRAKE_VALUE
BRAKE_OPEN_POSITIVE = bytes.fromhex("62102f") + BRAKE_VALUE[:-1] + b"\x20"
BRAKE_DTCS = bytes.fromhex("5902ffc13187ac")
TP_POSITIVE = bytes.fromhex("7e00")
F186_APPLICATION = bytes.fromhex("62f18601")
F181_APPLICATION = bytes.fromhex("62f181") + triage.EXPECTED_APPLICATION_F181
F181_BOOT = bytes.fromhex("62f181") + triage.BOOT_PLACEHOLDER_F181


class FakePanda:
    def __init__(self, *, initial_failures: int = 0, restore_failures: int = 0,
                 mismatch_restore_health: int = 0, obd_entry_failure: bool = False):
        self.safety_calls: list[tuple[int, int]] = []
        self.heartbeat_calls = 0
        self.mode = triage.ELM327_SAFETY_MODE
        self.param = triage.NORMAL_ROUTE_PARAM
        self.initial_failures = initial_failures
        self.restore_failures = restore_failures
        self.mismatch_restore_health = mismatch_restore_health
        self.obd_entry_failure = obd_entry_failure
        self.obd_seen = False
        self.can_sent = []
        self.recv_batches = []
        self.data_speed_calls = []
        self.non_iso_calls = []
        self.clear_calls = []
        self.can_rx_overflow_buffer = b""
        self.tx_counts = [0, 0, 0]

    def send_heartbeat(self, engaged=False):
        check_value = engaged
        if check_value is not False:
            raise AssertionError("triage heartbeat must never report engaged")
        self.heartbeat_calls += 1

    def set_safety_mode(self, mode, param):
        self.safety_calls.append((int(mode), int(param)))
        if param == triage.NORMAL_ROUTE_PARAM and not self.obd_seen and self.initial_failures:
            self.initial_failures -= 1
            raise RuntimeError("normal route entry failed")
        if param == triage.OBD_ROUTE_PARAM:
            self.obd_seen = True
            if self.obd_entry_failure:
                raise RuntimeError("ambiguous OBD USB control failure")
        if param == triage.NORMAL_ROUTE_PARAM and self.obd_seen and self.restore_failures:
            self.restore_failures -= 1
            raise RuntimeError("normal restore failed")
        self.mode = int(mode)
        self.param = int(param)

    def health(self):
        param = self.param
        if self.param == triage.NORMAL_ROUTE_PARAM and self.obd_seen and self.mismatch_restore_health:
            self.mismatch_restore_health -= 1
            param = triage.OBD_ROUTE_PARAM
        return {
            "safety_mode": self.mode,
            "safety_param": param,
            "controls_allowed": False,
            "heartbeat_lost": False,
            "voltage": 13000,
            "safety_tx_blocked": 0,
            "tx_buffer_overflow": 0,
            "rx_buffer_overflow": 0,
        }

    def set_can_data_speed_kbps(self, bus, speed):
        self.data_speed_calls.append((int(bus), int(speed)))

    def set_canfd_non_iso(self, bus, non_iso):
        self.non_iso_calls.append((int(bus), bool(non_iso)))

    def can_health(self, _bus):
        return {
            "bus_off": 0,
            "bus_off_cnt": 0,
            "error_warning": 0,
            "error_passive": 0,
            "total_error_cnt": 0,
            "total_tx_lost_cnt": 0,
            "total_rx_lost_cnt": 0,
            "total_tx_checksum_error_cnt": 0,
            "total_tx_cnt": self.tx_counts[int(_bus)],
            "total_rx_cnt": 0,
            "can_speed": triage.EXPECTED_CAN_SPEED_KBPS,
            "can_data_speed": triage.EXPECTED_CAN_DATA_SPEED_KBPS,
            "canfd_non_iso": 0,
            "can_core_reset_count": 0,
        }

    def can_clear(self, selector):
        self.clear_calls.append(int(selector))
        self.recv_batches.clear()

    def can_send(self, address, data, bus, timeout=None):
        self.can_sent.append((address, bytes(data), bus, timeout))
        self.note_tx(bus)

    def note_tx(self, bus):
        self.tx_counts[int(bus)] += 1

    def can_recv(self):
        return self.recv_batches.pop(0) if self.recv_batches else []


class FakeExchange:
    def __init__(self, script: dict[str, bytes | BaseException]):
        self.script = dict(script)
        self.calls: list[tuple[str, triage.Route, bytes]] = []

    def __call__(self, stage: str, route: triage.Route, request: bytes) -> bytes:
        self.calls.append((stage, route, bytes(request)))
        if stage not in self.script:
            raise AssertionError(f"unexpected exchange {stage}")
        result = self.script[stage]
        if isinstance(result, BaseException):
            raise result
        return result


def base_script(primary: bytes | BaseException = TP_POSITIVE) -> dict[str, bytes | BaseException]:
    return {
        "initial-brake-did": BRAKE_POSITIVE,
        "brake-dtc-status": BRAKE_DTCS,
        "primary-eps-tester-present": primary,
    }


def call_names(exchange: FakeExchange) -> list[str]:
    return [row[0] for row in exchange.calls]


print("== immutable plan and protocol allowlist ==")
plain_plan = triage.build_plan(False)
gateway_plan = triage.build_plan(True)
check("schema is exact-F33 network triage v1", triage.SCHEMA == "camry-f33-eps-network-triage-v1")
check("normal route is fixed to post-repin bus0 ELM327 param1",
      plain_plan["normal_route"] == {"panda_bus": 0, "elm327_safety_mode": 3, "elm327_param": 1})
check("live preflight pins 500/2000 kbps ISO CAN-FD and exits SILENT",
      plain_plan["controller_format"]
      == {"nominal_kbps": 500, "data_kbps": 2000, "can_fd_non_iso": False}
      and plain_plan["exit_safety_mode"] == {"name": "SILENT", "numeric": 0})
check("plan exposes stale-correlation and clean-timeout transport gates",
      plain_plan["exchange_evidence_gate"]["global_rx_clear_immediately_before_send"] is True
      and plain_plan["exchange_evidence_gate"]["physical_can_controllers"] == [0, 1, 2]
      and plain_plan["exchange_evidence_gate"]["clean_timeout_aggregate_total_tx_delta"] == 1
      and "total_tx_checksum_error_cnt"
      in plain_plan["exchange_evidence_gate"]["can_counter_deltas_must_be_zero"])
check("gateway route is fixed to bus1 temporary param0 and param1 restore",
      gateway_plan["gateway_route"]["panda_bus"] == 1
      and gateway_plan["gateway_route"]["temporary_elm327_param"] == 0
      and gateway_plan["gateway_route"]["mandatory_restore_param"] == 1)
check("ordinary plan has an exact five-request maximum", plain_plan["maximum_uds_requests"] == 5)
check("gateway plan has an exact seven-request maximum", gateway_plan["maximum_uds_requests"] == 7)
check("plan declares no mutating UDS request", plain_plan["mutating_uds_requests"] == gateway_plan["mutating_uds_requests"] == [])
allowed_tuples = {(stage, route.bus, route.tx_address, route.rx_address, route.tx_sub_address,
                   route.rx_sub_address, request.hex()) for stage, route, request in triage.ALLOWED_REQUESTS}
check("allowlist has exactly nine conditional stage/route/request tuples", len(allowed_tuples) == 9)
check("Brake requests are only DID102F and DTC status",
      {(row[0], row[-1]) for row in allowed_tuples if row[2] == 0x7B0}
      == {("initial-brake-did", "22102f"), ("brake-dtc-status", "1902ff"), ("final-brake-did", "22102f")})
check("primary EPS allowlist is TP then F186/F181 only",
      {(row[0], row[-1]) for row in allowed_tuples if row[2] == 0x7A1}
      == {("primary-eps-tester-present", "3e00"), ("primary-eps-f186", "22f186"), ("primary-eps-f181", "22f181")})
check("secondary EPS allowlist is one TP only",
      {(row[0], row[-1]) for row in allowed_tuples if row[2] == 0x7A0}
      == {("secondary-eps-tester-present", "3e00")})
check("gateway allowlist pins both address extensions to 5F",
      {(row[0], row[4], row[5], row[-1]) for row in allowed_tuples if row[2] == 0x750}
      == {("gateway-tester-present", 0x5F, 0x5F, "3e00"), ("gateway-f186", 0x5F, 0x5F, "22f186")})
try:
    triage.assert_allowed_request("secondary-eps-tester-present", triage.PRIMARY_EPS_ROUTE, triage.TESTER_PRESENT_REQUEST)
except triage.TriageError:
    wrong_route_refused = True
else:
    wrong_route_refused = False
check("same safe payload at wrong route/stage is refused", wrong_route_refused)

setup_panda = FakePanda()
silent_setup = triage._configure_silent(setup_panda, sleep_fn=lambda _seconds: None)
format_setup = triage._configure_can_format(setup_panda)
check("direct-Panda setup re-enables a disengaged heartbeat and verifies SILENT",
      silent_setup["verified"] and setup_panda.safety_calls == [(0, 0)]
      and setup_panda.heartbeat_calls == 2)
check("direct-Panda setup replaces persistent data-rate/non-ISO state",
      format_setup["verified"]
      and setup_panda.data_speed_calls == [(0, 2000), (1, 2000), (2, 2000)]
      and setup_panda.non_iso_calls == [(0, False), (1, False), (2, False)])


print("\n== gateway address-extension transport filter ==")
noise_panda = FakePanda()
noise_panda.recv_batches = [
    [(0x758, bytes([0x0F, 0x02, 0x7E, 0x00]), 1)] * 253
    + [(0x758, bytes([0x6D, 0x02, 0x7E, 0x00]), 1)],
    [
        (0x758, bytes([0x5F, 0x02, 0x7E, 0x00]), 1),
        (0x123, b"", 0),
        (0x124, bytes([0x0F, 0x00]), 0),
    ],
]
extension_adapter = triage._AddressExtensionAdapter(noise_panda, 0x5F)
filtered = extension_adapter.can_recv()
check("address-extension filter discards shared-ID nodes 0F and 6D",
      filtered == [(0x758, bytes([0x5F, 0x02, 0x7E, 0x00]), 1), (0x123, b"", 0)])
check("full 254-frame batch keeps draining to the next non-full batch", noise_panda.recv_batches == [])
extension_adapter.can_send(0x750, b"\x5F\x02\x3E\x00", 1)
check("address-extension adapter borrows the original CAN sender",
      noise_panda.can_sent[-1][:3] == (0x750, b"\x5F\x02\x3E\x00", 1))


class ConstructorWitnessClient:
    calls = []

    def __init__(self, panda, tx_addr, rx_addr=None, bus=0, sub_addr=None, rx_sub_addr=None,
                 timeout=1, tx_timeout=1, response_pending_timeout=10):
        self.__class__.calls.append({
            "panda": panda, "tx_addr": tx_addr, "rx_addr": rx_addr, "bus": bus,
            "sub_addr": sub_addr, "rx_sub_addr": rx_sub_addr, "timeout": timeout,
            "response_pending_timeout": response_pending_timeout,
        })
        base_panda = getattr(getattr(panda, "can_send", None), "__self__", panda)
        self._can_client = SimpleNamespace(panda=base_panda, bus=bus)


class ConstructorWitnessIsoTp:
    def __init__(self, can_client, timeout=1):
        self.can_client = can_client
        self.timeout = timeout

    def send(self, request):
        self.request = bytes(request)
        self.can_client.panda.note_tx(self.can_client.bus)

    def recv(self, timeout=None):
        return bytes.fromhex("7e00"), False


class StaleDuringHealthPanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.health_reads = 0

    def can_health(self, bus):
        health = super().can_health(bus)
        self.health_reads += 1
        if self.health_reads == 3:
            self.recv_batches = [[(0x7A9, bytes.fromhex("027e000000000000"), 0)]]
        return health


class QueueBoundaryIsoTp(ConstructorWitnessIsoTp):
    stale_present_at_send = None

    def send(self, request):
        self.__class__.stale_present_at_send = bool(self.can_client.panda.recv_batches)
        super().send(request)


constructor_panda = FakePanda()
constructor_panda.param = triage.OBD_ROUTE_PARAM
constructor_uds = SimpleNamespace(UdsClient=ConstructorWitnessClient, IsoTpMessage=ConstructorWitnessIsoTp)
constructor_exchange = triage._raw_exchange_factory(constructor_panda, constructor_uds)
constructor_reply = constructor_exchange(
    "gateway-tester-present", triage.GATEWAY_ROUTE, triage.TESTER_PRESENT_REQUEST,
)
constructor_call = ConstructorWitnessClient.calls[-1]
check("raw exchange uses current UdsClient positional tx/rx/bus signature",
      constructor_call["tx_addr"] == 0x750 and constructor_call["rx_addr"] == 0x758 and constructor_call["bus"] == 1)
check("raw exchange supplies supported sub_addr and rx_sub_addr keywords",
      constructor_call["sub_addr"] == constructor_call["rx_sub_addr"] == 0x5F)
check("gateway UdsClient receives the local extension-prefilter adapter",
      isinstance(constructor_call["panda"], triage._AddressExtensionAdapter)
      and constructor_reply == TP_POSITIVE and constructor_panda.clear_calls == [0xFFFF])
stale_boundary_panda = FakePanda()
stale_boundary_panda.recv_batches = [[(0x7A9, bytes.fromhex("027e000000000000"), 0)]]
stale_boundary_panda.can_rx_overflow_buffer = b"partial"
triage._clear_stale_receive_boundary(stale_boundary_panda)
check("fresh-response boundary clears board backlog and host partial packet state",
      stale_boundary_panda.clear_calls == [0xFFFF]
      and stale_boundary_panda.recv_batches == []
      and stale_boundary_panda.can_rx_overflow_buffer == b"")
stale_window_panda = StaleDuringHealthPanda()
stale_window_uds = SimpleNamespace(UdsClient=ConstructorWitnessClient, IsoTpMessage=QueueBoundaryIsoTp)
stale_window_reply = triage._raw_exchange_factory(stale_window_panda, stale_window_uds)(
    "primary-eps-tester-present", triage.PRIMARY_EPS_ROUTE, triage.TESTER_PRESENT_REQUEST,
)
check("a matching frame arriving during baseline health reads is cleared before send",
      stale_window_reply == TP_POSITIVE
      and QueueBoundaryIsoTp.stale_present_at_send is False
      and stale_window_panda.clear_calls == [0xFFFF])


print("\n== timeout classification and heartbeat polling ==")


class MessageTimeoutError(Exception):
    pass


class TimeoutIsoTpBase:
    instances = []

    def __init__(self, can_client, timeout=1):
        self.can_client = can_client
        self.timeout = timeout
        self.rx_dat = b""
        self.calls = 0
        self.__class__.instances.append(self)

    def send(self, request):
        self.request = bytes(request)
        self.can_client.panda.note_tx(self.can_client.bus)


class PendingThenTimeoutIsoTp(TimeoutIsoTpBase):
    def recv(self, timeout=None):
        self.calls += 1
        if self.calls == 1:
            self.rx_dat = bytes.fromhex("7f3e78")
            return self.rx_dat, False
        raise MessageTimeoutError("pending response never completed")


class PartialThenTimeoutIsoTp(TimeoutIsoTpBase):
    def recv(self, timeout=None):
        self.calls += 1
        if self.calls == 1:
            self.rx_dat = bytes.fromhex("62f1")
        raise MessageTimeoutError("partial ISO-TP response never completed")


class SilentTimeoutIsoTp(TimeoutIsoTpBase):
    def recv(self, timeout=None):
        self.calls += 1
        raise MessageTimeoutError("no response")


class LostFramePanda(FakePanda):
    def __init__(self):
        super().__init__()
        self.can_health_calls = 0

    def can_health(self, bus):
        health = super().can_health(bus)
        snapshot = self.can_health_calls // 3
        self.can_health_calls += 1
        if snapshot and int(bus) == 0:
            health["total_rx_lost_cnt"] = 1
        return health


class NoTxPanda(FakePanda):
    def note_tx(self, bus):
        pass


original_timings = (
    triage.REQUEST_TIMEOUT_SECONDS,
    triage.RESPONSE_PENDING_TIMEOUT_SECONDS,
    triage.MAX_EXCHANGE_SECONDS,
    triage.HEARTBEAT_POLL_SECONDS,
)
triage.REQUEST_TIMEOUT_SECONDS = 0.002
triage.RESPONSE_PENDING_TIMEOUT_SECONDS = 0.004
triage.MAX_EXCHANGE_SECONDS = 0.006
triage.HEARTBEAT_POLL_SECONDS = 0.0005
try:
    pending_panda = FakePanda()
    pending_uds = SimpleNamespace(UdsClient=ConstructorWitnessClient, IsoTpMessage=PendingThenTimeoutIsoTp)
    try:
        triage._raw_exchange_factory(pending_panda, pending_uds)(
            "primary-eps-tester-present", triage.PRIMARY_EPS_ROUTE, triage.TESTER_PRESENT_REQUEST,
        )
    except triage.IncompleteResponse as error:
        pending_incomplete = error.observed_response == bytes.fromhex("7f3e78")
    else:
        pending_incomplete = False
    check("NRC78 followed by timeout is preserved as incomplete activity", pending_incomplete)
    check("response-pending wait services Panda heartbeat in short slices", pending_panda.heartbeat_calls > 2)

    partial_panda = FakePanda()
    partial_uds = SimpleNamespace(UdsClient=ConstructorWitnessClient, IsoTpMessage=PartialThenTimeoutIsoTp)
    try:
        triage._raw_exchange_factory(partial_panda, partial_uds)(
            "primary-eps-f181", triage.PRIMARY_EPS_ROUTE, triage.F181_REQUEST,
        )
    except triage.IncompleteResponse as error:
        partial_incomplete = error.observed_response == bytes.fromhex("62f1")
    else:
        partial_incomplete = False
    check("partial ISO-TP followed by timeout is not collapsed to silence", partial_incomplete)

    silent_panda = FakePanda()
    silent_uds = SimpleNamespace(UdsClient=ConstructorWitnessClient, IsoTpMessage=SilentTimeoutIsoTp)
    silent_exchange = triage._raw_exchange_factory(silent_panda, silent_uds)
    try:
        silent_exchange(
            "primary-eps-tester-present", triage.PRIMARY_EPS_ROUTE, triage.TESTER_PRESENT_REQUEST,
        )
    except triage.NoResponse:
        clean_silence = True
    else:
        clean_silence = False
    check("no received ISO-TP bytes remains a clean timeout only with clean transport health",
          clean_silence and silent_exchange.health_ledger[-1]["clean"])

    loss_panda = LostFramePanda()
    loss_uds = SimpleNamespace(UdsClient=ConstructorWitnessClient, IsoTpMessage=SilentTimeoutIsoTp)
    loss_exchange = triage._raw_exchange_factory(loss_panda, loss_uds)
    try:
        loss_exchange(
            "primary-eps-tester-present", triage.PRIMARY_EPS_ROUTE, triage.TESTER_PRESENT_REQUEST,
        )
    except triage.NoResponse:
        lost_frame_timeout_rejected = False
    except triage.TriageError as error:
        lost_frame_timeout_rejected = "timeout transport health invalid" in str(error)
    else:
        lost_frame_timeout_rejected = False
    check("RX loss during a silent exchange cannot be classified as ECU silence",
          lost_frame_timeout_rejected
          and not loss_exchange.health_ledger[-1]["clean"]
          and loss_exchange.health_ledger[-1]["can_deltas"]["0"]["total_rx_lost_cnt"] == 1)

    no_tx_panda = NoTxPanda()
    no_tx_uds = SimpleNamespace(UdsClient=ConstructorWitnessClient, IsoTpMessage=SilentTimeoutIsoTp)
    no_tx_exchange = triage._raw_exchange_factory(no_tx_panda, no_tx_uds)
    try:
        no_tx_exchange(
            "primary-eps-tester-present", triage.PRIMARY_EPS_ROUTE, triage.TESTER_PRESENT_REQUEST,
        )
    except triage.NoResponse:
        missing_tx_rejected = False
    except triage.TriageError as error:
        missing_tx_rejected = "aggregate physical-controller total_tx_cnt delta" in str(error)
    else:
        missing_tx_rejected = False
    check("a request not admitted to a physical CAN TX FIFO cannot prove ECU silence",
          missing_tx_rejected
          and no_tx_exchange.health_ledger[-1]["aggregate_total_tx_delta"] == 0
          and no_tx_exchange.health_ledger[-1]["expected_total_tx_delta"] == 1)
finally:
    (
        triage.REQUEST_TIMEOUT_SECONDS,
        triage.RESPONSE_PENDING_TIMEOUT_SECONDS,
        triage.MAX_EXCHANGE_SECONDS,
        triage.HEARTBEAT_POLL_SECONDS,
    ) = original_timings


print("\n== exact Brake decoding ==")
normal = triage.decode_brake_did(BRAKE_POSITIVE)
opened = triage.decode_brake_did(BRAKE_OPEN_POSITIVE)
check("Brake 102F exact retained bytes decode Normal", normal["value_hex"] == BRAKE_VALUE.hex() and normal["eps_communication_state"] == "Normal")
check("Brake MSB0 bit74 set decodes Under intermittent", opened["eps_communication_open_bit"] and opened["eps_communication_state"] == "Under intermittent")
try:
    triage.decode_brake_did(bytes.fromhex("62102f00"))
except triage.TriageError:
    short_brake_refused = True
else:
    short_brake_refused = False
check("short Brake DID value is refused", short_brake_refused)
dtcs = triage.parse_brake_dtcs(BRAKE_DTCS)
check("Brake DTC parser preserves U0131-87 raw status AC",
      dtcs["u0131_87"]["code"] == "U013187" and dtcs["u0131_87"]["status"] == 0xAC)
check("DTC status bits are decoded without inventing current liveness",
      dtcs["u0131_87"]["status_bits"] == ["pendingDTC", "confirmedDTC", "testFailedSinceLastClear", "warningIndicatorRequested"])

entry_exchange = FakeExchange({})
entry_panda = FakePanda(initial_failures=3)
entry_result = triage.run_on_panda(
    entry_panda, include_gateway=True, exchange_fn=entry_exchange, sleep_fn=lambda _seconds: None,
)
check("unverified normal-route entry makes all three bounded attempts",
      entry_panda.safety_calls == [(3, 1), (3, 1), (3, 1)])
check("unverified normal-route entry is an unsafe stop before vehicle traffic",
      entry_result["status"] == "unsafe-stop" and not entry_exchange.calls)


print("\n== primary response closes later branches ==")
application_script = base_script()
application_script.update({"primary-eps-f186": F186_APPLICATION, "primary-eps-f181": F181_APPLICATION})
application_exchange = FakeExchange(application_script)
application_panda = FakePanda()
application_result = triage.run_on_panda(
    application_panda, include_gateway=True, exchange_fn=application_exchange, sleep_fn=lambda _seconds: None,
)
check("primary application sequence completes", application_result["status"] == "triage-complete")
check("primary positive response permits exactly F186 then F181",
      call_names(application_exchange) == ["initial-brake-did", "brake-dtc-status", "primary-eps-tester-present", "primary-eps-f186", "primary-eps-f181"])
check("exact saved identity is classified as application", application_result["stages"]["primary_eps"]["identity_classification"] == "exact-application")
check("primary response suppresses secondary and gateway", application_result["stages"]["secondary_eps"]["state"] == "skipped" and application_result["stages"]["gateway"]["state"] == "skipped")
check("identity classification never authorizes restore", application_result["stages"]["primary_eps"]["restore_authorized"] is False)
check("no OBD mux transition occurs after primary response", application_panda.safety_calls == [(3, 1)])

boot_script = base_script(bytes.fromhex("7f3e22"))
boot_script.update({"primary-eps-f186": bytes.fromhex("7f2231"), "primary-eps-f181": F181_BOOT})
boot_result = triage.run_on_panda(FakePanda(), include_gateway=False, exchange_fn=FakeExchange(boot_script), sleep_fn=lambda _seconds: None)
check("valid negative TP is still a native reply and permits identity", boot_result["status"] == "triage-complete")
check("F186 NRC31 plus bang F181 is only boot-compatible", boot_result["stages"]["primary_eps"]["identity_classification"] == "exact-boot-compatible")


print("\n== primary-silent secondary discriminator ==")
silent_script = base_script(triage.NoResponse("primary silent"))
silent_script["secondary-eps-tester-present"] = triage.NoResponse("secondary silent")
silent_exchange = FakeExchange(silent_script)
silent_result = triage.run_on_panda(FakePanda(), include_gateway=False, exchange_fn=silent_exchange, sleep_fn=lambda _seconds: None)
check("clean primary timeout permits exactly one secondary TP",
      call_names(silent_exchange) == ["initial-brake-did", "brake-dtc-status", "primary-eps-tester-present", "secondary-eps-tester-present"])
check("both silent listeners are a complete bounded observation", silent_result["status"] == "triage-complete")

incomplete_script = base_script(triage.IncompleteResponse("pending primary", bytes.fromhex("7f3e78")))
incomplete_exchange = FakeExchange(incomplete_script)
incomplete_panda = FakePanda()
incomplete_result = triage.run_on_panda(
    incomplete_panda, include_gateway=True, exchange_fn=incomplete_exchange, sleep_fn=lambda _seconds: None,
)
check("primary correlated activity timeout stops secondary and gateway",
      call_names(incomplete_exchange) == ["initial-brake-did", "brake-dtc-status", "primary-eps-tester-present"]
      and incomplete_result["status"] == "stopped"
      and incomplete_result["stages"]["gateway"]["state"] == "skipped")
check("incomplete activity bytes are retained in the transmit ledger",
      incomplete_result["stages"]["primary_eps"]["tester_present"]["observed_response_hex"] == "7f3e78")

malformed_script = base_script(bytes.fromhex("7e01"))
malformed_exchange = FakeExchange(malformed_script)
malformed_result = triage.run_on_panda(FakePanda(), include_gateway=True, exchange_fn=malformed_exchange, sleep_fn=lambda _seconds: None)
check("malformed primary reply stops without secondary", call_names(malformed_exchange) == ["initial-brake-did", "brake-dtc-status", "primary-eps-tester-present"])
check("malformed primary reply stops without OBD gateway", malformed_result["status"] == "stopped" and malformed_result["stages"]["gateway"]["state"] == "skipped")

secondary_bad_script = base_script(triage.NoResponse("primary silent"))
secondary_bad_script["secondary-eps-tester-present"] = bytes.fromhex("7e01")
secondary_bad_exchange = FakeExchange(secondary_bad_script)
secondary_bad_panda = FakePanda()
secondary_bad_result = triage.run_on_panda(secondary_bad_panda, include_gateway=True, exchange_fn=secondary_bad_exchange, sleep_fn=lambda _seconds: None)
check("invalid secondary response fails closed before gateway", secondary_bad_result["terminal_reason"] == "secondary-exchange-invalid")
check("invalid secondary response never selects OBD mux", secondary_bad_panda.safety_calls == [(3, 1)])

dtc_timeout_script = base_script(triage.NoResponse("primary silent"))
dtc_timeout_script["brake-dtc-status"] = triage.NoResponse("DTC read unsupported")
dtc_timeout_script["secondary-eps-tester-present"] = TP_POSITIVE
dtc_timeout_exchange = FakeExchange(dtc_timeout_script)
dtc_timeout_result = triage.run_on_panda(FakePanda(), include_gateway=False, exchange_fn=dtc_timeout_exchange, sleep_fn=lambda _seconds: None)
check("Brake DID remains the route gate when DTC status times out", dtc_timeout_result["status"] == "triage-complete" and "primary-eps-tester-present" in call_names(dtc_timeout_exchange))


print("\n== optional gateway and mandatory restoration ==")
gateway_timeout_script = base_script(triage.NoResponse("primary silent"))
gateway_timeout_script.update({
    "secondary-eps-tester-present": triage.NoResponse("secondary silent"),
    "gateway-tester-present": triage.NoResponse("gateway silent"),
    "final-brake-did": BRAKE_POSITIVE,
})
gateway_timeout_exchange = FakeExchange(gateway_timeout_script)
gateway_timeout_panda = FakePanda()
gateway_timeout_result = triage.run_on_panda(
    gateway_timeout_panda, include_gateway=True, exchange_fn=gateway_timeout_exchange, sleep_fn=lambda _seconds: None,
)
check("gateway timeout is one bounded observation", call_names(gateway_timeout_exchange).count("gateway-tester-present") == 1)
check("gateway timeout does not permit gateway F186", "gateway-f186" not in call_names(gateway_timeout_exchange))
check("gateway timeout restores param1 before final Brake",
      gateway_timeout_panda.safety_calls == [(3, 1), (3, 0), (3, 1)]
      and call_names(gateway_timeout_exchange)[-1] == "final-brake-did")
check("verified restore and final Brake complete gateway triage", gateway_timeout_result["status"] == "triage-complete")
check("restoration records health readback", gateway_timeout_result["stages"]["normal_route_restoration"]["verified"] is True)

gateway_positive_script = base_script(triage.NoResponse("primary silent"))
gateway_positive_script.update({
    "secondary-eps-tester-present": TP_POSITIVE,
    "gateway-tester-present": TP_POSITIVE,
    "gateway-f186": bytes.fromhex("62f18601"),
    "final-brake-did": BRAKE_POSITIVE,
})
gateway_positive_exchange = FakeExchange(gateway_positive_script)
gateway_positive_result = triage.run_on_panda(
    FakePanda(), include_gateway=True, exchange_fn=gateway_positive_exchange, sleep_fn=lambda _seconds: None,
)
check("native gateway TP permits exactly one gateway F186", call_names(gateway_positive_exchange).count("gateway-f186") == 1)
check("gateway AE5F route is retained in ledger",
      next(row for row in gateway_positive_result["transmit_ledger"] if row["stage"] == "gateway-tester-present")["route"]["tx_sub_address"] == 0x5F)

retry_script = dict(gateway_timeout_script)
retry_exchange = FakeExchange(retry_script)
retry_panda = FakePanda(restore_failures=2)
retry_result = triage.run_on_panda(retry_panda, include_gateway=True, exchange_fn=retry_exchange, sleep_fn=lambda _seconds: None)
check("normal restore is bounded to and succeeds on the third attempt",
      len(retry_result["stages"]["normal_route_restoration"]["attempts"]) == 3
      and retry_result["stages"]["normal_route_restoration"]["verified"] is True)
check("final Brake is sent only after verified third restore", call_names(retry_exchange)[-1] == "final-brake-did")

restore_sleep_calls = 0


def interrupt_first_restore(_seconds):
    global restore_sleep_calls
    restore_sleep_calls += 1
    if restore_sleep_calls == 3:
        raise triage.TriageInterrupted("SIGTERM")


restore_interrupt_exchange = FakeExchange(dict(gateway_timeout_script))
restore_interrupt_result = triage.run_on_panda(
    FakePanda(),
    include_gateway=True,
    exchange_fn=restore_interrupt_exchange,
    sleep_fn=interrupt_first_restore,
)
check("cleanup retries after an interrupt but cannot report ordinary success",
      restore_interrupt_result["status"] == "interrupted"
      and restore_interrupt_result["stages"]["normal_route_restoration"]["verified"]
      and restore_interrupt_result["stages"]["normal_route_restoration"]["interruptions"]
      and call_names(restore_interrupt_exchange)[-1] == "final-brake-did")

mismatch_exchange = FakeExchange(dict(gateway_timeout_script))
mismatch_panda = FakePanda(mismatch_restore_health=1)
mismatch_result = triage.run_on_panda(mismatch_panda, include_gateway=True, exchange_fn=mismatch_exchange, sleep_fn=lambda _seconds: None)
check("param1 health mismatch forces another fixed restoration attempt",
      len(mismatch_result["stages"]["normal_route_restoration"]["attempts"]) == 2)

failed_restore_script = dict(gateway_timeout_script)
failed_restore_script.pop("final-brake-did")
failed_restore_exchange = FakeExchange(failed_restore_script)
failed_restore_panda = FakePanda(restore_failures=3)
failed_restore_result = triage.run_on_panda(
    failed_restore_panda, include_gateway=True, exchange_fn=failed_restore_exchange, sleep_fn=lambda _seconds: None,
)
check("three failed restores produce unsafe-stop", failed_restore_result["status"] == "unsafe-stop" and failed_restore_result["terminal_reason"] == "normal-route-restoration-not-verified")
check("no vehicle request follows an unverified restore", "final-brake-did" not in call_names(failed_restore_exchange))
check("all fixed restore attempts were made", failed_restore_panda.safety_calls[-3:] == [(3, 1), (3, 1), (3, 1)])

obd_fail_exchange = FakeExchange(dict(gateway_timeout_script))
obd_fail_panda = FakePanda(obd_entry_failure=True)
obd_fail_result = triage.run_on_panda(obd_fail_panda, include_gateway=True, exchange_fn=obd_fail_exchange, sleep_fn=lambda _seconds: None)
check("ambiguous OBD control failure still restores and final-checks Brake",
      obd_fail_panda.safety_calls == [(3, 1), (3, 0), (3, 1)] and call_names(obd_fail_exchange)[-1] == "final-brake-did")
check("failed OBD entry is not mislabeled a completed gateway observation", obd_fail_result["status"] == "stopped" and obd_fail_result["terminal_reason"] == "obd-route-entry-not-verified")

final_fail_script = dict(gateway_timeout_script)
final_fail_script["final-brake-did"] = triage.NoResponse("final Brake missing")
final_fail_result = triage.run_on_panda(FakePanda(), include_gateway=True, exchange_fn=FakeExchange(final_fail_script), sleep_fn=lambda _seconds: None)
check("missing final Brake control is unsafe-stop", final_fail_result["status"] == "unsafe-stop" and final_fail_result["terminal_reason"] == "final-brake-positive-control-failed")

interrupt_script = dict(gateway_timeout_script)
interrupt_script["gateway-tester-present"] = triage.TriageInterrupted("SIGTERM")
interrupt_exchange = FakeExchange(interrupt_script)
interrupt_panda = FakePanda()
interrupt_result = triage.run_on_panda(interrupt_panda, include_gateway=True, exchange_fn=interrupt_exchange, sleep_fn=lambda _seconds: None)
check("gateway interruption cannot skip normal restoration", interrupt_panda.safety_calls[-1] == (3, 1) and interrupt_result["stages"]["normal_route_restoration"]["verified"] is True)
check("gateway interruption still performs final Brake control", call_names(interrupt_exchange)[-1] == "final-brake-did")
check("post-cleanup result preserves interrupted status", interrupt_result["status"] == "interrupted")


print("\n== source-level and CLI fail-closed boundary ==")
source_path = ROOT / "tools/targets/camry/live/camry_f33_eps_network_triage.py"
source = source_path.read_text(encoding="utf-8")
check("implementation has one diagnostic-PDU send call", source.count("message.send(request)") == 1)
guard_index = source.index("assert_allowed_request(stage, route, request)")
health_index = source.index("health_start = _transport_health_snapshot(panda)", guard_index)
clear_index = source.index("_clear_stale_receive_boundary(panda)", health_index)
send_index = source.index("message.send(request)", clear_index)
check("baseline health precedes the final stale-RX clear immediately before sole send",
      guard_index < health_index < clear_index < send_index
      and source[clear_index:send_index]
      == "_clear_stale_receive_boundary(panda)\n            ")
check("implementation never calls Panda set_obd", ".set_obd(" not in source)
check("implementation never disables heartbeat checks", "set_heartbeat_disabled" not in source and "disable_checks=False" in source)
check("implementation clears only the global receive queue before correlation",
      source.count("panda.can_clear(0xFFFF)") == 1 and "panda.can_clear(0xFFFF)\n" in source)
check("implementation contains no high-level mutation call sites",
      all(token not in source for token in (
          ".diagnostic_session_control(", ".ecu_reset(", ".security_access(",
          ".clear_diagnostic_information(", ".write_data_by_identifier(",
          ".request_download(", ".routine_control(",
      )))
check("process-owner matcher catches modern Python pandad title",
      triage.PANDA_OWNER_COMMAND_PATTERN.search("python openpilot.selfdrive.pandad.pandad") is not None)
check("process-owner matcher catches boardd paths but ignores its own pgrep expression",
      triage.PANDA_OWNER_COMMAND_PATTERN.search("/data/openpilot/selfdrive/boardd/boardd") is not None
      and triage.PANDA_OWNER_COMMAND_PATTERN.search("pgrep -af pandad|boardd") is None)

listed = subprocess.run(
    [str(ROOT / "tools/toyota"), "target", "list", "camry", "network-triage"],
    cwd=ROOT, capture_output=True, text=True, check=False,
)
check("tools/toyota auto-discovers target-specific workflow", listed.returncode == 0 and "live/f33-eps-network-triage" in listed.stdout)
dry = subprocess.run(
    [str(ROOT / "tools/toyota"), "target", "run", "camry", "live/f33-eps-network-triage", "--", "--include-gateway"],
    cwd=ROOT, capture_output=True, text=True, check=False,
)
dry_document = json.loads(dry.stdout)
check("default target command is hardware-free dry-run", dry.returncode == 0 and dry_document["mode"] == "dry-run" and dry_document["status"] == "planned")
check("dry-run exposes exact gateway cleanup plan", dry_document["plan"]["gateway_route"]["requested"] is True and dry_document["plan"]["maximum_uds_requests"] == 7)

missing = subprocess.run(
    [sys.executable, str(source_path), "--execute"],
    cwd=ROOT, capture_output=True, text=True, check=False,
)
missing_document = json.loads(missing.stdout)
check("missing attestations refuse before Panda import",
      missing.returncode == 2 and missing_document["status"] == "refused"
      and "live execution preflight failed" in str(missing_document["terminal_reason"])
      and "cannot import Panda" not in str(missing_document["terminal_reason"]))

print(f"\n== RESULT: {passed} passed, {failed} failed ==")
if failed:
    raise SystemExit(1)
