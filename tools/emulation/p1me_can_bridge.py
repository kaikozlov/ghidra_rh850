"""Optional python-can BusABC backed by the exact Camry P1M-E machine.

The bridge boots the synthetic-board fixture from reset and opens its loopback
event socket after the configured foreground-complete arrivals. The target
daemon's script executor remains occupied until the bus closes. python-can is optional.
"""

from __future__ import annotations

import json
import queue
import socket
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import suppress
from functools import lru_cache
from pathlib import Path
from typing import Any

from tools import REPO_ROOT
from tools.emulation.p1me_machine import capture_many
from tools.targets.camry.analysis import convert_camry_capture_machine_events as capture_rules
from tools.targets.camry.research import replay_camry_f33_capture_machine as replay

try:
    import can
except ImportError:  # pragma: no cover - exercised in an ephemeral optional environment
    can = None  # type: ignore[assignment]


TARGET = replay.TARGET


@lru_cache(maxsize=1)
def _acceptance_rules() -> dict[int, dict[str, Any]]:
    """Receive rules decoded from the registered image, keyed by identifier."""
    receive, _transmit = capture_rules.decode_firmware_rules()
    return receive


DIAGNOSTIC_READY_CYCLES = replay.DIAGNOSTIC_READY_EMPTY_CYCLES + 1


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def _unbounded_board_scenario() -> dict[str, Any]:
    scenario = json.loads(replay.BOARD_FIXTURE.read_text(encoding="utf-8"))
    repeated_inputs: dict[tuple[int, int, int], dict[str, Any]] = {}
    for event in scenario.get("events", []):
        if event.get("kind") != "csih-word" or "repeat" not in event:
            continue
        stride = int(event.get("stride_words", 1))
        first = int(event["after_transmit_words"])
        key = (int(event["unit"]), stride, first % stride)
        prior = repeated_inputs.get(key)
        if prior is None or first > int(prior["after_transmit_words"]):
            repeated_inputs[key] = event
    for event in repeated_inputs.values():
        event.pop("repeat")
        event["repeat_forever"] = True
    return scenario


def write_bridge_scenario(
    path: Path,
    port: int,
    name: str = "camry-f33-python-can-bridge",
    *,
    hold_when_ready: bool = False,
) -> dict[str, Any]:
    """Write a board boot and matching unbounded RESET-pin replay fragment."""
    path = path.resolve()
    reset_path = path.with_name(f"{path.stem}.reset-replay.json")
    reset = _unbounded_board_scenario()
    reset["name"] = f"{name}-reset-replay"
    reset["source"] = {
        **reset.get("source", {}),
        "kind": "python-can-reset-replay",
        "board_fixture": str(replay.BOARD_FIXTURE.relative_to(REPO_ROOT)),
    }
    reset_path.write_text(json.dumps(reset, indent=2) + "\n", encoding="utf-8")

    scenario = _unbounded_board_scenario()
    scenario["name"] = name
    scenario["source"] = {
        **scenario.get("source", {}),
        "kind": "python-can-loopback-bridge",
        "board_fixture": str(replay.BOARD_FIXTURE.relative_to(REPO_ROOT)),
        "ready_condition": f"{DIAGNOSTIC_READY_CYCLES} arrivals at the foreground completion PC",
    }
    scenario["max_instructions"] = 5_000_000_000
    scenario["stop_addresses"] = []
    scenario["expected_termination"] = "halt"
    scenario["event_socket"] = {
        "host": "127.0.0.1",
        "port": port,
        "ready_after_arrivals": {
            "address": hex(replay.FOREGROUND_COMPLETE),
            "count": DIAGNOSTIC_READY_CYCLES,
        },
    }
    if hold_when_ready:
        scenario["event_socket"]["hold_when_ready"] = True
    scenario["reset_replay"] = {"scenario": reset_path.name}
    scenario["checks"] = []
    path.write_text(json.dumps(scenario, indent=2) + "\n", encoding="utf-8")
    return scenario


class MachineGone(RuntimeError):
    """The machine closed its event socket or published a row the bridge cannot read."""


_DOWN = object()


if can is not None:
    class P1MEMachineBus(can.BusABC):
        """A python-can bus backed by the shared P1M-E target daemon."""

        def __init__(
            self,
            channel: str = TARGET,
            *,
            output_dir: str | Path = REPO_ROOT / "build/out/p1me-can-bridge",
            startup_timeout: float = 600.0,
            start_held: bool = False,
            **kwargs: Any,
        ) -> None:
            super().__init__(channel=channel, **kwargs)
            if channel != TARGET:
                raise ValueError(f"only {TARGET} is supported")
            self._rx: queue.Queue[can.Message] = queue.Queue()
            self._transmit_rows: list[dict[str, Any]] = []
            self._receive_rows: list[dict[str, Any]] = []
            self._arrivals: queue.Queue[dict[str, Any]] = queue.Queue()
            self._control: queue.Queue[dict[str, Any]] = queue.Queue()
            self._failure: Exception = MachineGone("machine event socket closed")
            self._output_dir = Path(output_dir).resolve()
            self._output_dir.mkdir(parents=True, exist_ok=True)
            self._port = _free_loopback_port()
            self._scenario_path = self._output_dir / "bridge.scenario.json"
            write_bridge_scenario(
                self._scenario_path, self._port, hold_when_ready=start_held,
            )
            self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="p1me-can")
            self._future: Future[list[dict[str, Any]]] = self._executor.submit(
                capture_many,
                TARGET,
                [self._scenario_path],
                self._output_dir,
            )
            deadline = time.monotonic() + startup_timeout
            while True:
                if self._future.done():
                    self._future.result()
                    raise RuntimeError("machine stopped before opening its event socket")
                try:
                    self._socket = socket.create_connection(
                        ("127.0.0.1", self._port), timeout=0.25,
                    )
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("machine event socket did not open")
                    time.sleep(0.05)
            self._socket.settimeout(None)
            self._reader = self._socket.makefile("r", encoding="utf-8")
            self._writer = self._socket.makefile("w", encoding="utf-8")
            while True:
                line = self._reader.readline()
                if not line:
                    raise RuntimeError("machine event socket closed before ready")
                ready = json.loads(line)
                if ready.get("kind") == "machine-ready":
                    break
            self.ready_instruction = int(ready["instruction"])
            if bool(ready.get("held", False)) != start_held:
                raise RuntimeError("machine readiness hold state does not match the bridge request")
            self._closed = False
            self._held = start_held
            self._write_lock = threading.Lock()
            self._reader_thread = threading.Thread(
                target=self._read_machine, name="p1me-can-reader", daemon=True,
            )
            self._reader_thread.start()

        def _write_event(self, row: dict[str, Any]) -> None:
            with self._write_lock:
                self._writer.write(json.dumps(row, separators=(",", ":")) + "\n")
                self._writer.flush()

        def _read_machine(self) -> None:
            failure: Exception = self._failure
            try:
                for line in self._reader:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError as exc:
                        raise MachineGone(f"invalid machine event-socket JSON: {line!r}") from exc
                    kind = row.get("kind")
                    if kind == "instruction-arrival":
                        self._arrivals.put(row)
                        continue
                    if kind in {"machine-ready", "memory-read", "reset-asserted", "hold-armed", "machine-held", "resumed"}:
                        self._control.put(row)
                        continue
                    if kind in {"can-rx", "can-rx-discard", "can-rx-pop"}:
                        self._receive_rows.append(row)
                        continue
                    if kind != "can-tx":
                        continue
                    self._transmit_rows.append(row)
                    payload = bytes.fromhex(row["data_hex"])
                    self._rx.put(can.Message(
                        arbitration_id=int(row["can_id"], 0),
                        data=payload,
                        is_extended_id=False,
                        is_fd=len(payload) > 8,
                        channel=self.channel_info,
                        timestamp=time.time(),
                    ))
            except MachineGone as exc:
                failure = exc
            finally:
                self._failure = failure
                for pending in (self._rx, self._control, self._arrivals):
                    pending.put(_DOWN)

        def _waiter(self, pending: queue.Queue, timeout: float | None) -> Any:
            row = pending.get(timeout=timeout)
            if row is _DOWN:
                raise self._failure
            return row

        def _discard_arrivals(self) -> None:
            while True:
                try:
                    self._waiter(self._arrivals, 0)
                except queue.Empty:
                    return

        def send(self, msg: can.Message, timeout: float | None = None) -> None:
            del timeout
            rule = _acceptance_rules().get(msg.arbitration_id)
            if rule is None:
                return  # The controller's acceptance rules discard the frame.
            self._write_event({
                "kind": "can-rx",
                "fifo": rule["fifo"],
                "can_id": hex(msg.arbitration_id),
                "data_hex": bytes(msg.data).hex(),
                "extended": bool(msg.is_extended_id),
                "fd": bool(msg.is_fd),
                "boundary": "post-filter",
                "label": rule["label"],
                "timestamp": 0,
                "evidence": "python-can BusABC ingress",
            })

        @staticmethod
        def _remaining(deadline: float | None) -> float | None:
            return None if deadline is None else max(0.0, deadline - time.monotonic())

        def _control_response(
            self, kind: str, request_id: str | None, timeout: float | None,
        ) -> dict[str, Any]:
            deadline = None if timeout is None else time.monotonic() + timeout
            while True:
                try:
                    row = self._waiter(self._control, self._remaining(deadline))
                except queue.Empty as exc:
                    raise TimeoutError(f"machine {kind} response timeout") from exc
                if row.get("kind") == kind and (
                    request_id is None or row.get("request_id") == request_id
                ):
                    return row

        def read_memory(self, address: int, size: int, timeout: float = 5.0) -> bytes:
            """Read initialized machine memory at an instruction boundary."""
            if not 0 <= address <= 0xFFFFFFFF or not 1 <= size <= 0x10000:
                raise ValueError("address must be 32-bit and size must be 1..65536")
            request_id = f"memory-{time.monotonic_ns()}"
            self._write_event({
                "kind": "memory-read", "request_id": request_id,
                "address": hex(address), "size": size,
            })
            row = self._control_response("memory-read", request_id, timeout)
            return bytes.fromhex(row["data_hex"])

        def reset(self, timeout: float = 60.0) -> dict[str, Any]:
            """Assert the RESET pin and wait for the next readiness gate."""
            if self._held:
                raise RuntimeError("machine is held at a foreground arrival; call resume() first")
            request_id = f"reset-{time.monotonic_ns()}"
            self._discard_arrivals()
            self._write_event({
                "kind": "reset-assert", "request_id": request_id,
                "reset_class": "system-1-pin",
                "evidence": "python-can BusABC RESET-pin assertion",
            })
            asserted = self._control_response("reset-asserted", request_id, timeout)
            ready = self._control_response("machine-ready", None, timeout)
            self.ready_instruction = int(ready["instruction"])
            return {"asserted": asserted, "ready": ready}

        @property
        def machine_instruction(self) -> int:
            """Instruction count when the event socket signaled readiness."""
            return self.ready_instruction

        @property
        def transmit_rows(self) -> tuple[dict[str, Any], ...]:
            """Firmware transmit rows, including machine scheduler ticks."""
            return tuple(self._transmit_rows)

        @property
        def receive_rows(self) -> tuple[dict[str, Any], ...]:
            """Machine ingress rows, including explicit discard reasons."""
            return tuple(self._receive_rows)



        def wait_foreground_cycles(
            self, count: int = 1, timeout: float | None = None, hold: bool = False,
        ) -> tuple[dict[str, Any], ...]:
            """Wait for future completed foreground-cycle arrivals.

            With ``hold`` the machine then stays at the last arrival until
            ``resume``, so memory reads land on that instruction boundary.
            """
            if count < 1:
                raise ValueError("count must be positive")
            if self._held:
                raise RuntimeError("machine is held at a foreground arrival; call resume() first")
            deadline = None if timeout is None else time.monotonic() + timeout
            self._discard_arrivals()
            rows: list[dict[str, Any]] = []
            if not hold:
                for _ in range(count):
                    try:
                        rows.append(self._waiter(self._arrivals, self._remaining(deadline)))
                    except queue.Empty as exc:
                        raise TimeoutError("foreground-cycle arrival timeout") from exc
                return tuple(rows)
            request_id = f"hold-{time.monotonic_ns()}"
            self._write_event({
                "kind": "hold-at-arrival", "request_id": request_id, "arrivals": count,
            })
            armed = self._control_response("hold-armed", request_id, self._remaining(deadline))
            held = self._control_response("machine-held", None, self._remaining(deadline))
            self._held = True
            # The machine counts arrivals from its arm; keep the rows it counted.
            while True:
                try:
                    row = self._waiter(self._arrivals, 0)
                except queue.Empty:
                    break
                if int(armed["instruction"]) < int(row["instruction"]) <= int(held["instruction"]):
                    rows.append(row)
            if len(rows) != count:
                raise RuntimeError(f"machine held after {len(rows)} of {count} foreground arrivals")
            return tuple(rows)

        def resume(self, timeout: float = 60.0) -> None:
            """Release a machine held at a foreground arrival."""
            if not self._held:
                raise RuntimeError("machine is not held")
            request_id = f"resume-{time.monotonic_ns()}"
            self._write_event({"kind": "resume", "request_id": request_id})
            self._control_response("resumed", request_id, timeout)
            self._held = False

        def _recv_internal(self, timeout: float | None) -> tuple[can.Message | None, bool]:
            try:
                return self._waiter(self._rx, timeout), False
            except queue.Empty:
                return None, False

        def shutdown(self) -> None:
            if getattr(self, "_closed", True):
                return
            self._closed = True
            with suppress(Exception):
                self._write_event({"kind": "stop"})
            with suppress(Exception):
                self._writer.close()
            with suppress(Exception):
                self._reader.close()
            with suppress(Exception):
                self._socket.close()
            future = self._future
            del self._future
            with suppress(Exception):
                future.result(timeout=300)
            executor = self._executor
            del self._executor
            executor.shutdown(wait=True)
            super().shutdown()
else:
    class P1MEMachineBus:  # pragma: no cover - dependency-error surface
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError(
                "python-can is optional; run this bridge in an ephemeral environment "
                "such as `uv run --with python-can ...`"
            )
