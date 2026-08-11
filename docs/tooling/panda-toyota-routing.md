# Panda/Toyota diagnostic bus routing — end-to-end software model

> **Scope:** pinned Calvin Park openpilot/Panda checkout at
> `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822`, pinned Bk2ol DataFlash tooling
> at `db453752beeb7cdd024a1a9c38c6711c981e75ad`, and Toyota EPS
> `8965B4512000` firmware.
>
> **Status:** active; software-equivalence candidate recovered, vehicle transition
> confirmation still required.
>
> **Evidence source:** firmware-static, pinned external-source, and local tooling.
>
> **Verification:** `tests/verify_toyota_eps_bus_probe.py` plus optional
> `tests/verify_external_corroboration.py`.

## 1. Question and result

The field observation is unusually specific:

- with an unmodified Toyota-B harness, the EPS answers ordinary UDS on Panda
  logical bus 1 but times out when programming mode is requested;
- physically swapping the Toyota-B CAN0/CAN1 pairs makes the firmware-dump path
  work on bus 0;
- changing only the software UDS bus does not reproduce the physical swap.

The software trace now explains **why those two experiments are not equivalent**.
There are two independent routing controls:

1. `UdsClient.bus` selects a **Panda logical CAN queue/controller**;
2. the Panda ELM327 routing state selects which **physical FDCAN2 pin bank and
   transceiver** logical bus 1 is connected to.

The current community dump flow changes or hard-codes only the first dimension
while leaving the second in the OBD-mux state.

For the reported Toyota-B CAN0/CAN1 repin case, the strongest software-equivalent
candidate is therefore:

```python
panda.set_safety_mode(3, 1)  # ELM327 + CAN_MODE_NORMAL
BUS = 1                      # Panda logical bus 1 -> MCU FDCAN2
```

This is a **high-confidence static-equivalence candidate**, not yet a vehicle-
verified programming fix. The decisive test is entering programming mode on the
unmodified harness with this exact pair of settings.

## 2. Keep four naming layers separate

Most of the confusion comes from collapsing several meanings of “CAN1” or “bus
1.” This report uses four layers explicitly:

1. **UDS client bus** — the integer passed to `UdsClient` and ultimately
   `Panda.can_send`.
2. **Panda logical bus** — queue/bus numbering visible over USB: 0, 1, 2.
3. **MCU controller** — STM32 FDCAN1, FDCAN2, FDCAN3.
4. **Physical route** — the enabled transceiver/pin bank and therefore the
   electrical vehicle network reached by that MCU controller.

Pinned Panda initializes the normal logical/controller relationship as:

```text
Panda logical bus 0 -> MCU FDCAN1
Panda logical bus 1 -> MCU FDCAN2
Panda logical bus 2 -> MCU FDCAN3
```

Harness orientation can swap logical buses 0 and 2. It does **not** swap logical
bus 1 away from FDCAN2.

A further terminology trap exists in Panda utility scripts: the OBD-muxed
FDCAN2 path is sometimes presented as pseudo “bus 3.” For example,
`panda/scripts/can_printer.py` handles requested bus 3 by calling
`set_obd(True)` and then filtering **logical bus 1**. There is no fourth Panda
CAN controller in this path. For this investigation, `(logical bus, mux state)`
is the meaningful identity.

## 3. End-to-end UDS transmit path

The software path from a UDS request to a physical MCU CAN controller is:

```text
UdsClient(..., bus=N)
  -> CanClient.send()
     -> panda.can_send(tx_addr, payload, N)
        -> USB CAN packet with packet.bus = N
           -> board/can_comms.h
              -> can_send(&packet, packet.bus, false)
                 -> can_queues[N]
                 -> process_can(CAN_NUM_FROM_BUS_NUM(N))
                    -> MCU FDCAN controller
```

The receive side is equally narrow: `CanClient._recv_filter()` accepts a reply
only when both the CAN address and returned logical bus equal the configured
values.

Therefore `UdsClient.bus` controls **which logical queue/controller is used**.
It does not call `set_obd`, `set_can_mode`, change GPIO alternate functions, or
select a transceiver.

For logical bus 1, the queue resolves to MCU FDCAN2. Which physical wires
FDCAN2 reaches is a second state machine described below.

## 4. ELM327 parameter 0 versus 1

Pinned opendbc documents the key behavior directly in `elm327.h`:

```text
If safety_param == 0, bus 1 is multiplexed to the OBD-II port.
```

Pinned Panda implements that in `set_safety_mode`:

```text
SAFETY_ELM327 + param == 0 -> CAN_MODE_OBD_CAN2
SAFETY_ELM327 + param != 0 -> CAN_MODE_NORMAL
```

This parameter does **not** select a different ELM diagnostic whitelist.
`elm327_hooks.init` is `nooutput_init`, whose parameter is explicitly unused,
and `elm327_tx_hook` has no parameter-dependent branch. The `0x700..0x7FF`
11-bit ISO-TP range remains permitted under either routing parameter, so EPS
request `0x7A1` is allowed with both parameter 0 and parameter 1.

Thus, in this context, ELM parameter 0/1 is a **physical-routing choice**, not a
UDS-permission choice.

### Intended openpilot usage is revealing

The pinned `PandaRunner` starts standalone fingerprinting with:

```python
set_safety_mode(SafetyModel.elm327, 1)
```

and passes `Panda.set_obd` separately to the fingerprint/query layer. The
fingerprinting code then toggles OBD multiplexing only for queries that require
it and disables it again for normal harness traffic.

That establishes the intended software abstraction:

```text
ELM param 1 = persistent baseline: normal harness routing
set_obd(True) = temporary FDCAN2 -> OBD physical mux
set_obd(False) = temporary FDCAN2 -> normal physical mux
```

By contrast, the community DataFlash workflow starts ELM with implicit parameter
0, making the OBD mux the remembered baseline for the whole script.

## 5. Why `set_obd(False)` is not as robust as ELM param 1

The Python controls are distinct USB requests:

```text
Panda.set_obd(...)            -> request 0xDB
Panda.set_safety_mode(..., p) -> request 0xDC
```

The Panda firmware handlers are materially different:

- `0xDB` calls `current_board->set_can_mode(...)` directly;
- `0xDC` calls `set_safety_mode(mode, param)`.

`set_safety_hooks()` records the latter as `current_safety_mode` and
`current_safety_param`. The `0xDB` handler does not update that remembered
parameter.

This matters because Panda continuously detects harness orientation. When the
detected status changes, the 8 Hz tick path does all of the following:

```text
can_set_orientation(...)
can_init_all()
set_safety_mode(current_safety_mode, current_safety_param)
set_power_save_state(...)
```

So this sequence is fragile:

```python
panda.set_safety_mode(3)  # remembers param 0 = OBD
panda.set_obd(False)      # temporarily selects normal path
```

A later harness-status reinitialization can reapply remembered ELM parameter 0
and silently return FDCAN2 to the OBD path.

The robust baseline for a normal-harness programming attempt is instead:

```python
panda.set_safety_mode(3, 1)
```

That makes the state Panda itself reapplies the desired state.

## 6. Comma 4/Cuatro FDCAN2 physical truth table

Comma 4 uses the Cuatro Panda board definition. Pinned `cuatro.h` assigns:

```text
.set_can_mode = tres_set_can_mode
```

so Cuatro inherits the Tres FDCAN2 mux implementation.

`tres_set_can_mode` first disables transceivers 2 and 4 and then connects
FDCAN2 to one of two GPIO/transceiver paths. The exact GPIO bank changes with
USB-C harness orientation so that the **semantic route** remains stable.

The recovered truth table is:

| Harness orientation | ELM param | Board mode | FDCAN2 pins | CAN transceiver | Semantic path |
|---|---:|---|---|---:|---|
| normal | 1/nonzero | `CAN_MODE_NORMAL` | PB5/PB6 | 2 | normal harness |
| normal | 0 | `CAN_MODE_OBD_CAN2` | PB12/PB13 | 4 | OBD |
| flipped | 1/nonzero | `CAN_MODE_NORMAL` | PB12/PB13 | 4 | normal harness |
| flipped | 0 | `CAN_MODE_OBD_CAN2` | PB5/PB6 | 2 | OBD |

Two invariants are important:

- logical bus 1 remains MCU FDCAN2 in all four rows;
- ELM parameter 1 means the **normal harness semantic path** in either cable
  orientation, while parameter 0 means the **OBD semantic path**.

`tools/toyota_eps_bus_probe.py` now emits this truth table for the selected
ELM parameter, and `tests/verify_toyota_eps_bus_probe.py` pins the model.

## 7. Relay and forwarding: an important correction

Panda's generic software forwarding relation is:

```text
logical bus 0 -> logical bus 2
logical bus 2 -> logical bus 0
logical bus 1 -> no generic forwarding destination
```

This correctly reflects the two-sided camera/car harness topology and explains
why field reports describe a bad Toyota-B assignment as putting the relay on
“bus 1 instead of bus 0/2.” Harness orientation also swaps 0 and 2 only.

However, **ELM diagnostics do not depend on that software forwarder**.
`SAFETY_ELM327` calls `set_intercept_relay(false, false)`, and `nooutput_init`
sets `disable_forwarding=true`. `harness_init()` likewise says to “keep buses
connected by default” and leaves the intercept relay undriven.

So the precise model is:

- bus 0/2 describe the normal relay-separated camera/car sides when interception
  is active;
- in ELM mode the relay remains physically pass-through and software 0<->2
  forwarding is disabled;
- bus 1/FDCAN2 is a separate controller whose physical endpoint can be normal
  harness or OBD depending on the mux state.

This distinction removes an earlier overstatement that the successful dump
necessarily depended on active Panda software forwarding. The material point is
**physical topology/path selection**, not an ELM forwarding rule.

## 8. Current Bk2ol DataFlash workflow

The pinned community workflow contains three coupled assumptions.

### EPS probe

```python
BUS = 0
panda.set_safety_mode(3)  # implicit param 0
```

### DataFlash dump

```python
BUS = 0
panda.set_safety_mode(3)  # implicit param 0
```

### CAN oracle collection

```python
ORACLE_BUSES = {0, 2}
panda.set_safety_mode(3)  # implicit param 0
```

Consequences:

1. logical bus 1/FDCAN2 is permanently muxed to OBD for the script;
2. the probe and dump never discover which normal-harness logical bus actually
   reaches the EPS;
3. simply changing `BUS = 1` still leaves bus 1 on the OBD physical route;
4. the oracle collector ignores bus 1 entirely.

This exactly explains why a “software swap” implemented as only `BUS=0 -> 1`
is not an equivalent test of a physical Toyota-B CAN0/CAN1 repin.

### Heartbeat is not the hidden failure here

Standalone `Panda()` defaults to `disable_checks=True`. Its connect path disables
Panda heartbeat checks and exits power save before the script selects ELM mode.
Therefore the Bk2ol script is not expected to fall back to SILENT merely because
its programming sequence takes more than the normal heartbeat timeout.

This was checked because an unnoticed SILENT transition would have mimicked a
routing failure; it does not fit this standalone path.

### CAN-FD automatic switching is also not silently changing the path

The same `Panda()` connect path disables automatic CAN-FD switching on every
logical bus and initializes the configured CAN speed. That is relevant for
future CAN-FD variants, but it does not provide an alternate explanation for the
reported classic-CAN routing asymmetry.

## 9. Why the physical repin can succeed when bus-only software fails

For the reported experiment, the two configurations are best represented as
follows.

### Reported bus-only “software swap”

```text
stock Toyota-B wiring
+ ELM param 0
+ UDS bus 1

UDS bus 1
 -> Panda logical bus 1
 -> MCU FDCAN2
 -> CAN_MODE_OBD_CAN2
 -> OBD physical path
```

This can plausibly produce ordinary UDS responses through the vehicle's OBD/
gateway-visible network while still being the wrong path for a reset/programming
transition.

### Successful physical repin

```text
Toyota-B CAN0/CAN1 vehicle pairs physically exchanged
+ ELM param 0
+ dump on logical bus 0

UDS bus 0
 -> Panda logical bus 0 / corresponding normal harness controller path
 -> repinned vehicle network now lands on that physical interface
```

The electrical network itself has moved. No Panda logical-bus setting alone can
move the vehicle wires.

### Candidate true software equivalent on stock pins

```text
stock Toyota-B wiring
+ ELM param 1
+ UDS bus 1

UDS bus 1
 -> Panda logical bus 1
 -> MCU FDCAN2
 -> CAN_MODE_NORMAL
 -> normal-harness FDCAN2 physical path
```

This is the software state that addresses the physical path omitted by the
reported bus-only test. It is therefore the next experiment to run before
attributing the timeout to an unavoidable harness defect.

## 10. Why this is not an EPS app-to-boot controller switch

The `8965B4512000` firmware independently rules out a tempting ECU-side
explanation: its application and boot/programming environment both use RSCFD
channel 1 for the `0x7A1/0x7A9` diagnostic endpoint.

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

The application RX/TX bodies at `0x82E40` and `0x8474E` hard-code RSCFD channel
1.

### Boot/programming environment

The boot CanIf configuration is also channel-1-specific:

- receive filter 0 at `0x8920` matches `0x7A1`;
- only HRHs `0x10` and `0x13` expose that filter, both channel 1;
- channel-0 and channel-2 HRHs have no active receive filter;
- the sole diagnostic Tx route uses response `0x7A9` and HTH `0x13`, also
  channel 1.

`tests/verify_toyota_eps_bus_probe.py` reads these relationships directly from
CodeFlash.

Therefore an EPS-side “application uses one controller, bootloader uses another”
model is false for this firmware.

## 11. Remaining transition-time uncertainty

Static analysis can now establish the software-routing mismatch and identify the
missing normal-route configuration, but it cannot yet prove what makes the OBD
route fail exactly at programming transition.

Possible residual mechanisms include:

- a gateway path that stops forwarding/reaching the EPS while it resets into
  boot;
- loss of a CAN acknowledger or other network participant on the indirect path;
- a topology-dependent reset/wakeup condition;
- FDCAN2 ACK/bus-off behavior on the wrong physical segment.

The last item is worth instrumenting: pinned Panda FDCAN code explicitly contains
recovery for ACK errors encountered while multiplexing FDCAN2 between its normal
and OBD physical paths. That is evidence that physical mux state can materially
affect link-level behavior, but it is **not** proof that ACK failure caused yc's
specific timeout.

Calvin's opposite field result further argues against promoting any one gateway
mechanism to fact until the exact Panda routing state in both tests is recorded.

## 12. Decisive vehicle test

The minimum high-value test is deliberately narrow.

### A. Stock harness, normal FDCAN2 route

On an unmodified Toyota-B harness:

```python
panda = Panda()
panda.set_safety_mode(3, 1)
uds = UdsClient(panda, 0x7A1, 0x7A9, bus=1, ...)
```

First confirm read-only `F181`. Then, only in the existing controlled programming
workflow, try the same default -> extended -> programming transition used by the
known dump method.

Record immediately before and after the transition:

```text
panda.health():
  safety_mode
  safety_param
  car_harness_status
  heartbeat_lost
  power_save_enabled

panda.can_health(1):
  last_error / last_stored_error
  transmit_error_cnt / receive_error_cnt
  bus_off / bus_off_cnt
  total_tx_cnt / total_rx_cnt
  can_core_reset_count
```

The important invariant is `safety_param == 1` throughout the attempt.

### B. Compare the OBD route explicitly

Repeat the read-only probe with:

```python
panda.set_safety_mode(3, 0)
UdsClient(..., bus=1)
```

This distinguishes “logical bus 1 responds” from “normal-harness bus 1
responds.” Those are different electrical experiments.

### Interpretation

If stock pins + `param=1,bus=1` enter programming successfully, the physical
repin has a software replacement and the immediate tooling bug is solved.

If `F181` works on `param=1,bus=1` but programming still fails, then the repin is
changing something beyond the FDCAN2 normal/OBD mux and the next step is a
simultaneous transition capture on the relevant physical segments.

If `F181` does not answer on `param=1,bus=1`, the assumed correspondence between
the stock Toyota-B CAN1 pair and FDCAN2 normal-harness path is wrong for that
setup, and the response matrix itself tells us which branch to investigate.

## 13. Tooling recommendation

The community extractor should eventually stop encoding routing as a single
hard-coded `BUS` constant. The robust workflow is:

1. create Panda and explicitly select `SAFETY_ELM327, param=1`;
2. perform read-only `0x7A1 -> 0x7A9 / F181` discovery on logical buses 0, 1, 2
   in **normal routing**;
3. require exactly one expected EPS identity, or fail closed on ambiguity;
4. persist the discovered `(logical bus, elm327_param)` pair as the diagnostic
   route;
5. use that exact pair throughout programming and dump;
6. only use OBD muxing as an explicit alternate route, never as an implicit
   default;
7. include bus 1 in CAN-oracle capture/discovery instead of assuming `{0,2}`;
8. log `health()` and `can_health()` state around programming transition so a
   routing or ACK failure is distinguishable from an ECU negative response.

`tools/toyota_eps_bus_probe.py` implements the read-only discovery half and now
emits the recovered FDCAN2 route model plus the Toyota-B static-equivalence
candidate. It intentionally does **not** enter programming mode.

## 14. Bottom line

The important result is no longer merely “hardware and software swaps are
different.” The exact missing software state is identified:

```text
logical bus 1 alone          = insufficient
logical bus 1 + ELM param 0  = FDCAN2 on OBD path
logical bus 1 + ELM param 1  = FDCAN2 on normal harness path
```

The reported “software swap” exercised the second row. The physical repin
changed the network attachment itself. For the unmodified harness, the third row
is the software configuration that must be tested.

That makes `ELM327 param 1 + logical bus 1` the current best software replacement
candidate for yc's physical Toyota-B CAN0/CAN1 swap, with dynamic programming-
transition confirmation as the only remaining step before calling it a verified
fix.
