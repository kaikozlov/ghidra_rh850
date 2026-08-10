# Panda/Toyota diagnostic bus routing — static boundary

> **Scope:** pinned Calvin Park openpilot/Panda checkout at
> `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822` plus pinned Bk2ol DataFlash
> tooling at `db453752beeb7cdd024a1a9c38c6711c981e75ad`
>
> **Status:** active
>
> **Evidence source:** external-source and local generated tooling
>
> **Verification:** optional `tests/verify_external_corroboration.py` and
> `tests/verify_toyota_eps_bus_probe.py`

Recent field discussion found a puzzling split: an EPS answered ordinary UDS
when addressed on Panda bus 1, but the programming transition timed out until
the physical CAN0/CAN1 harness pairs were swapped and the same workflow was run
on bus 0. This report defines the static software boundary before attributing
that behavior to the ECU.

## 1. What ELM327 safety mode actually changes

The pinned opendbc safety source states explicitly:

```text
If safety_param == 0, bus 1 is multiplexed to the OBD-II port.
```

Pinned Panda firmware implements that statement in `set_safety_mode`:

```text
SAFETY_ELM327, param == 0  -> CAN_MODE_OBD_CAN2
SAFETY_ELM327, param != 0  -> CAN_MODE_NORMAL
```

The pinned `query_fw_versions.py` exposes the same distinction through its
`--no-obd` option:

```text
elm327 param 0 -> OBD CAN2 mux
elm327 param 1 -> normal CAN routing
```

This is a physical routing decision for the CAN2 controller/pin set, not a
change to the UDS protocol.

## 2. Logical Panda bus numbering and harness orientation

Pinned `panda/board/drivers/can_common.h` initializes:

```text
logical bus 0 <-> MCU CAN1
logical bus 1 <-> MCU CAN2
logical bus 2 <-> MCU CAN3
```

Harness orientation swaps the logical assignment of **buses 0 and 2 only**.
Bus 1 remains attached to MCU CAN2.

For Tres/Red Panda hardware, `CAN_MODE_NORMAL` versus `CAN_MODE_OBD_CAN2`
changes which physical GPIO pair is configured as FDCAN2 and which CAN
transceiver is enabled. The exact selected pair also depends on detected harness
orientation. Therefore a script that changes only its `UdsClient(..., bus=...)`
argument is not necessarily testing the same physical wires as another script
or safety-parameter setting.

## 3. Current community extractor configuration

The pinned Bk2ol workflow combines two fixed choices:

```text
panda.set_safety_mode(3)   # ELM327, implicit param 0 -> OBD CAN2 mux
UdsClient(..., BUS=0)      # probe/dump target fixed to logical bus 0
```

The capture layer separately ignores logical bus 1.

This means the current workflow does **not** perform diagnostic-bus discovery,
and changing only `BUS = 1` while retaining ELM327 parameter 0 changes both the
logical UDS target and the physical CAN2 mux context relative to a normal-routing
probe.

## 4. What static analysis does and does not establish

Static source proves:

1. ELM327 parameter 0 and nonzero parameters select different Panda CAN routing.
2. The Bk2ol dumper does not explicitly request normal routing and does not
   discover the responding bus.
3. Panda logical bus 1 is the controller affected by the OBD CAN2 mux.
4. Physical harness orientation separately swaps logical buses 0 and 2.

Static source does **not** prove why a particular Toyota EPS stops answering when
entering programming mode. Remaining possibilities include physical topology,
ACK behavior across ECU reset, gateway behavior, transceiver/routing state, or
variant-specific ECU behavior.

Accordingly, the current evidence supports the hypothesis that the physical
CAN-pair repin can be replaced by correct software routing, but does not yet
prove it.

## 5. Non-destructive discovery helper

`tools/toyota_eps_bus_probe.py` is designed to settle the first routing question
without entering a programming session.

By default it only prints a plan. With `--execute` it:

- selects ELM327 **parameter 1** (normal CAN routing);
- probes logical buses 0, 1, and 2 independently;
- sends only `22 F1 81` to EPS physical address `0x7A1`;
- expects `0x7A9`;
- records the returned Application Software Identification;
- performs no session transition, SecurityAccess, DID write, download, routine,
  or reset.

Dry-run:

```bash
uv run --locked python tools/toyota_eps_bus_probe.py
```

On a comma/openpilot environment after boardd has been intentionally released:

```bash
uv run --locked python tools/toyota_eps_bus_probe.py --execute
```

A controlled second pass can explicitly select the OBD mux:

```bash
uv run --locked python tools/toyota_eps_bus_probe.py \
  --bus 1 --elm327-param 0 --execute
```

The useful result is a matrix of `(ELM327 routing mode, logical bus) -> F181
response`, obtained without the programming-session reset confounder.
