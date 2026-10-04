#!/usr/bin/env python3
"""Verify ram_exec boot-transition identity and handoff behavior."""
from __future__ import annotations

import sys
from types import SimpleNamespace
from unittest import mock

from exploit.common import ram_exec
from tools import REPO_ROOT

ROOT = REPO_ROOT


def check(name: str, cond: object) -> None:
    if not cond:
        raise AssertionError(name)
    print(f"PASS {name}")


class _TransientF181Client:
    def __init__(self, payload: bytes | None):
        self.payload = payload

    def read_data_by_identifier(self, _did):
        if self.payload is None:
            raise TimeoutError("boot endpoint is still transitioning")
        return self.payload

    def diagnostic_session_control(self, session):
        self.session = session


boot_f181 = bytes.fromhex("02" + "21" * 32)
transient_clients = iter((_TransientF181Client(None), _TransientF181Client(boot_f181)))
with mock.patch.object(ram_exec, "_make_uds_client", side_effect=lambda *_args, **_kwargs: next(transient_clients)):
    identity_client, identity_hex, _, identity_attempts = ram_exec._wait_for_f181_response(
        object(), SimpleNamespace(DATA_IDENTIFIER_TYPE=SimpleNamespace(APPLICATION_SOFTWARE_IDENTIFICATION=0xF181)),
        ram_exec.explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0), timeout=0.5,
    )
check("caught boot identity retries with a fresh UDS transport after a transient miss",
      identity_client.payload == boot_f181 and identity_hex == boot_f181.hex() and identity_attempts == 2)

app_f181 = bytes.fromhex("023839363546333330373030300000000038413331313333303331303000000000")
transition_clients = iter((_TransientF181Client(app_f181), _TransientF181Client(boot_f181)))
with mock.patch.object(ram_exec, "_make_uds_client", side_effect=lambda *_args, **_kwargs: next(transition_clients)):
    transition_client, transition_hex, _, transition_attempts = ram_exec._wait_for_f181_response(
        object(), SimpleNamespace(DATA_IDENTIFIER_TYPE=SimpleNamespace(APPLICATION_SOFTWARE_IDENTIFICATION=0xF181)),
        ram_exec.explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0), timeout=0.5,
        expected_f181_hex=boot_f181.hex(),
    )
check("caught PROGRAMMING ignores transitional application F181 until exact boot identity",
      transition_client.payload == boot_f181 and transition_hex == boot_f181.hex() and transition_attempts == 2)


class _FakeExecPanda:
    def set_safety_mode(self, *_args):
        pass
    def can_recv(self):
        return []


fake_exec_panda = _FakeExecPanda()
fake_boot_client = object()
route = ram_exec.explicit_route(bus=0, elm327_param=1, uds_variant="old", cpu_index=0)
with (mock.patch.dict(sys.modules, {"panda": SimpleNamespace(Panda=lambda *_a, **_k: fake_exec_panda)}),
      mock.patch.object(ram_exec, "ensure_boardd_stopped"),
      mock.patch.object(ram_exec, "_import_uds", return_value=SimpleNamespace()),
      mock.patch.object(ram_exec, "_wait_for_f181_response",
                        return_value=(fake_boot_client, boot_f181.hex(), None, 3)) as wait_exact_boot,
      mock.patch.object(ram_exec, "_enter_programming_bootloader",
                        side_effect=AssertionError("caught startup path must not request PROGRAMMING twice")),
      mock.patch.object(ram_exec, "_prepare_direct_bootloader",
                        return_value=(fake_boot_client, boot_f181.hex(), None,
                                      {"direct_bootloader": True}, {"status": "test"})) as prepare_direct,
      mock.patch.object(ram_exec, "_security_access", return_value=b"\x00" * 16),
      mock.patch.object(ram_exec, "_upload_and_trigger")):
    caught_exec = ram_exec.execute_ram_payload(
        b"\x00" * 0x1000,
        route=route,
        security_secret=b"\x00" * 16,
        timeout=0.0,
        expected_f181_hex=app_f181.hex(),
        expected_boot_f181_hex=boot_f181.hex(),
        geometry=ram_exec.explicit_ram_exec_geometry(load_addr=0xFEBF0000, evidence="test:caught-programming"),
        allow_direct_boot=True,
        programming_already_requested=True,
        panda=fake_exec_panda,
    )
check("caught PROGRAMMING execution path never re-enters the application handoff",
      caught_exec["direct_bootloader"] is True and caught_exec["programming_already_requested"] is True and
      wait_exact_boot.call_args.kwargs["expected_f181_hex"] == boot_f181.hex() and prepare_direct.call_count == 1)

print("PASS ram_exec boot transitions")
