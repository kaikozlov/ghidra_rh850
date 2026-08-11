# Panda/Toyota diagnostic bus routing — static boundary

> **Scope:** pinned Calvin Park openpilot/Panda checkout at
> `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822` plus pinned Bk2ol DataFlash
> tooling at `db453752beeb7cdd024a1a9c38c6711c981e75ad`
>
> **Status:** active
>
> **Evidence source:** firmware-static, pinned external-source, and local tooling
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
orientation. Comma 4 uses the Cuatro board definition, and pinned `cuatro.h`
assigns `.set_can_mode = tres_set_can_mode`, so the same FDCAN2 physical mux
logic applies there as well.

The pinned `UdsClient` implementation does something much narrower with its
`bus` argument: transmit calls pass `self.bus` to `panda.can_send`, and receive
filtering requires the returned bus to equal `self.bus`. It does not reconfigure
the board CAN mode. Therefore changing only `UdsClient(..., bus=...)` is **not**
the electrical equivalent of changing the ELM327 routing parameter or physically
repinning harness CAN pairs.

There is a second hardware distinction in the same direction. Panda's generic
harness topology treats buses 0 and 2 as the two relay/forwarding sides; bus 1 is
not part of that 0<->2 pair, and harness orientation swaps only 0 and 2. The
pinned optskug history records an earlier Toyota-B/TSS3 field observation that an
incorrect CAN assignment put "the relay ... on bus 1 instead of bus 0/2" and
that physically flipping the buses restored EPS interaction. That observation is
not proof of yc's exact transition failure, but it demonstrates why a physical
CAN0/CAN1 repin can alter network topology in a way a client-bus number cannot.

## 3. Current community extractor configuration

The pinned Bk2ol workflow combines two fixed choices:

```text
panda.set_safety_mode(3)   # ELM327, implicit param 0 -> OBD CAN2 mux
UdsClient(..., BUS=0)      # probe/dump target fixed to logical bus 0
```

The capture layer separately ignores logical bus 1.

This means the current workflow does **not** perform diagnostic-bus discovery.
More importantly for the yc experiment, changing only `BUS = 1` while retaining
ELM327 parameter 0 changes the logical UDS queue but leaves the Panda in the
OBD-CAN2 physical mux state. That "software swap" is therefore not equivalent
to physically swapping the harness CAN pairs.

## 4. EPS-side controller continuity across programming mode

The `8965B4512000` firmware rules out a second tempting explanation: the EPS does
**not** move its `0x7A1/0x7A9` diagnostic endpoint to another RSCFD controller
when it enters the boot/programming environment.

### Application

The application EIINT table at `0x20200` installs only the CAN1 pair:

```text
EIINT 184 CAN0 RX -> 0x61D88 default handler
EIINT 185 CAN0 TX -> 0x61D88 default handler
EIINT 187 CAN1 RX -> application_can1_rx_isr @ 0x6506A
EIINT 188 CAN1 TX -> application_can1_tx_isr @ 0x65028
EIINT 192 CAN2 RX -> 0x61D88 default handler
EIINT 193 CAN2 TX -> 0x61D88 default handler
```

The application RX/TX interrupt bodies at `0x82E40` and `0x8474E` both
hard-code RSCFD channel `1` into their generic handlers.

### Boot/programming environment

The boot CanIf configuration is independently channel-1-specific for the EPS
endpoint:

- receive filter 0 at `0x8920` matches request CAN ID `0x7A1`;
- the HRH route table at `0x898C` exposes that filter only through HRHs `0x10`
  and `0x13`; both encode RSCFD channel 1;
- channel-0 HRHs `0x00..0x0F` and channel-2 HRHs `0x20..0x2F` have no active
  receive filter;
- the sole diagnostic Tx PDU config at `0x8948` uses response CAN ID `0x7A9`
  and HTH `0x13`, which also encodes RSCFD channel 1.

`tests/verify_toyota_eps_bus_probe.py` pins these bytes and vector/config-table
relationships directly from CodeFlash.

Therefore the observed transition-time timeout cannot be explained by an
application-to-boot switch from EPS CAN1 to CAN0/CAN2. The routing discontinuity,
if any, is outside that ECU-controller selection.

## 5. What static analysis does and does not establish

Static analysis now proves two distinct points:

1. **Why the reported bus-only software swap was not equivalent to the physical
   repin:** `UdsClient.bus` selects a logical Panda bus, while ELM327 parameter 0
   separately keeps FDCAN2 physically multiplexed to the OBD path. Comma 4 uses
   the same mux implementation. Separately, Panda's harness relay/forwarding
   topology is the 0<->2 pair, not bus 1; a Toyota-B CAN0/CAN1 repin can therefore
   move a vehicle network onto or off the relay-backed harness path, which a
   `UdsClient` bus change cannot reproduce.
2. **The EPS does not itself change diagnostic CAN controller at programming
   transition:** both the application and boot `0x7A1/0x7A9` paths are RSCFD
   channel 1 on `8965B4512000`.

Static evidence still does **not** prove why yc's OBD-muxed/logical-bus path
specifically stops working at the programming transition. With an EPS
controller switch ruled out, the strongest remaining explanation is that the
stock path reaches the EPS through a different physical network segment (for
example an OBD/gateway path), while the repin places Panda on the direct
relay-backed harness segment that remains reachable after the EPS enters boot.
That mechanism fits both the Panda topology and the observed app-success /
programming-timeout boundary, but a transition capture is still required to
separate gateway reachability from ACK availability or another physical-network
effect. Calvin's opposite field result is consistent with setup-dependent
topology and is a reason not to promote the gateway mechanism itself to fact.

A correct software replacement for the physical repin must reproduce the same
**physical Panda pin/transceiver route**, not merely change the `UdsClient` bus
number.

## 6. Non-destructive discovery helper

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
