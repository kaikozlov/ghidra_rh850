# Panda/Toyota diagnostic bus routing — end-to-end software model

> **Scope:** pinned Calvin Park openpilot/Panda checkout at
> `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822`, pinned Bk2ol DataFlash tooling
> at `db453752beeb7cdd024a1a9c38c6711c981e75ad`, official comma hardware at
> `530b7da136b6a6d4b0d37b95bdb3472c59f672f4`, Sienna `8965B4512000`, and
> tracked Corolla `8965H1202000` CodeFlash.
>
> **Status:** active; physical pin-swap function statically resolved, direct
> diagnostic software route recovered, exact OBD-transition failure mechanism bounded.
>
> **Evidence source:** firmware-static, official hardware schematics, pinned
> external-source, contributor raw CodeFlash, and local tooling.
>
> **Verification:** `tests/verify_toyota_eps_bus_probe.py`,
> `tests/verify_toyota_b_programming_topology.py`, plus optional
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

Official harness schematics add a third dimension: the harness box is designed
around a **CAN0/CAN2 intercept-relay pair**, while CAN1 is a separate unsplit
network. The field report that the Toyota-B pinout puts the desired network on
CAN1 instead of the expected CAN0/CAN2 pair is therefore literal hardware
topology, not just Panda naming.

For diagnostics, Panda can still attach directly to that stock CAN1 pair without
repinning:

```python
panda.set_safety_mode(3, 1)  # ELM327 + CAN_MODE_NORMAL
BUS = 1                      # Panda logical bus 1 -> FDCAN2 -> harness CAN1
```

This is a **high-confidence direct-diagnostic-route candidate**. It is not a full
electrical equivalent of repinning the vehicle network onto the CAN0/CAN2
intercept-relay pair, and therefore it must not be described as a software
replacement for the relay topology used by normal openpilot forwarding.

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

## 7. Official Toyota-B / harness-box topology

The official comma hardware repository closes a gap that Panda source alone
cannot: which named harness networks are physically attached to the relay.
Three pinned schematics are relevant:

- `harness/v3/Harness_Box.pdf` states the intended mapping explicitly:
  `CAN0 = CAR`, `CAN1 = RADAR`, `CAN2 = CAMERA`, `CAN3 = COMMA POWER`;
- the same harness-box schematic places the solid-state intercept relay between
  **CAN0 and CAN2**, with the associated termination network on that pair;
- `harness/v3/Toyota_B_Harness.pdf` carries CAN2 and CAN1 on the camera-side
  connector and CAN0 and CAN1 on the car-side connector;
- `harness/OBD-C.sch.pdf` maps the USB-C lanes and states that SBU1 drives the
  relay between CAN0 and CAN2.

That yields the intended physical model:

```text
camera-side main CAN -------- CAN2 ----+
                                      | harness-box intercept relay
car-side main CAN ----------- CAN0 ----+

secondary/shared CAN -------- CAN1 ----- no CAN0/CAN2 intercept relay
OBD / Comma Power path ------ CAN3 ----- separate harness-box path
```

This makes the pinned optskug field statement precise: on the affected Toyota-B
vehicles, the relevant network assignment was reported as "flipped" such that
**the relay ends up on bus 1 instead of bus 0/2**. Physically exchanging the
Toyota-B CAN0/CAN1 pairs moves that vehicle network onto the harness-box topology
for which comma's interception design was built.

That is the first part of the pin-swap root cause. It is source-backed by the
official schematics plus the independent field report; it is not inferred from
EPS firmware.

### Diagnostic equivalence is not relay-topology equivalence

This distinction corrects the earlier wording in this report.

`ELM param 1 + logical bus 1` can put Panda FDCAN2 directly on the **existing
harness CAN1 wires**. For a point-to-point diagnostic exchange, that can remove
the need to repin merely to reach the EPS directly.

It does **not** move those wires onto CAN0/CAN2, does not insert the CAN0/CAN2
solid-state relay around that network, and does not make generic 0↔2 forwarding
represent its camera/car sides. Therefore:

```text
param=1 + bus=1      == candidate direct diagnostic route to stock CAN1
physical CAN0/CAN1   == correction of harness network assignment / relay topology
```

Those are different operations with different goals.

## 8. Relay and forwarding

Panda's generic software forwarding relation is:

```text
logical bus 0 -> logical bus 2
logical bus 2 -> logical bus 0
logical bus 1 -> no generic forwarding destination
```

That matches the official hardware design: logical 0/2 represent the two sides
of the normal interceptable camera/car pair, while bus 1 is a separate controller.
Harness orientation swaps logical 0 and 2 only.

ELM diagnostics do **not** depend on the software forwarder. `SAFETY_ELM327`
calls `set_intercept_relay(false, false)`, `nooutput_init` sets
`disable_forwarding=true`, and harness initialization leaves the physical relay
pass-through by default. Thus the dump/programming question is about which
physical transceiver/network the diagnostic controller is attached to, not about
Panda synthesizing 0↔2 forwarding while in ELM mode.

This also means a successful ELM diagnostic test on bus 1 does not prove that the
same wiring is suitable for normal openpilot interception. The latter needs the
network on the relay-backed 0/2 topology or an equivalent hardware redesign.

## 9. Why the old community "software swap" was not direct CAN1

The pinned Bk2ol workflow couples:

```python
BUS = 0
panda.set_safety_mode(3)  # implicit parameter 0
```

and the later public Calvin range-dumper family preserves the same implicit
ELM-parameter-zero assumption. Merely changing `BUS` to 1 changes only the Panda
logical queue. With ELM parameter 0, logical bus 1/FDCAN2 is still selected as
`CAN_MODE_OBD_CAN2`.

Therefore the reported bus-only experiment was:

```text
UDS bus 1
 -> Panda logical bus 1
 -> MCU FDCAN2
 -> CAN_MODE_OBD_CAN2
 -> OBD / CAN3-side physical route
 -> vehicle-side gateway/topology
 -> EPS
```

It was **not**:

```text
Panda FDCAN2 -> stock Toyota-B CAN1 wires -> EPS segment
```

This explains how ordinary UDS can work while the experiment still fails to
exercise the same network attachment as the physical repin.

Other Panda-side false leads are statically excluded:

- ELM parameter 0 and 1 use the same diagnostic transmit whitelist; `0x7A1` is
  permitted under both;
- standalone `Panda()` disables heartbeat checks, so a normal programming delay
  should not silently force SILENT safety mode;
- the connect path disables automatic CAN-FD switching, so an automatic protocol
  mode change is not silently remapping the route;
- `set_obd(False)` after remembering ELM parameter 0 is fragile because a harness
  orientation reinitialization reapplies the remembered safety parameter;
- the stable normal-harness choice is `set_safety_mode(3, 1)`.

## 10. The three configurations, precisely

### A. Unmodified harness + old bus-only attempt

```text
stock Toyota-B pinout
ELM param 0
logical bus 1
    -> FDCAN2
    -> OBD physical mux
    -> indirect vehicle path
```

This can observe an EPS that is gateway-reachable without placing Panda on the
EPS's stock harness CAN1 segment.

### B. Physical CAN0/CAN1 repin + old bus-0 tooling

```text
vehicle CAN pairs physically exchanged at Toyota-B adapter
ELM param 0
logical bus 0
    -> network of interest now lands on harness CAN0
    -> matching camera side lands on CAN2
    -> harness-box CAN0/CAN2 relay topology is now correct
```

The electrical network itself has moved. This is why the field report says the
relay moved from the wrong bus 1 assignment to the expected 0/2 pair.

### C. Stock pins + direct diagnostic software route

```text
stock Toyota-B pinout
ELM param 1
logical bus 1
    -> FDCAN2
    -> CAN_MODE_NORMAL
    -> harness CAN1 physical wires
    -> target vehicle network directly
```

C is the correct static software replacement **for direct diagnostics**. It is
not a replacement for B when the objective is ordinary openpilot interception
through the CAN0/CAN2 relay.

`tools/toyota_eps_bus_probe.py` now reports this distinction explicitly and marks
its `param=1,bus=1` candidate as `relay_topology_equivalent=false`.

## 11. The real Corolla firmware eliminates an EPS-side bus switch

The tracked `8965H1202000` CodeFlash gives a foreign-image check independent of
the Sienna firmware.

### Application

Its EIINT table installs only the RSCFD CAN1 receive/transmit pair:

```text
EIINT 184 CAN0 RX -> default handler 0x5C0F2
EIINT 185 CAN0 TX -> default handler 0x5C0F2
EIINT 187 CAN1 RX -> 0x5F3AA
EIINT 188 CAN1 TX -> 0x5F368
EIINT 192 CAN2 RX -> default handler 0x5C0F2
EIINT 193 CAN2 TX -> default handler 0x5C0F2
```

The application RX and TX bodies at `0x7D240` and `0x7EB4E` both carry the same
channel-1 specialization. More strongly, the complete three-channel RSCFD
register-address map is byte-identical to the Sienna map, and the complete
three-channel `3 × 0x34` application driver-configuration table is also
byte-identical.

### Boot/programming environment

The foreign boot CanIf/RSCFD configuration is equally specific:

```text
physical request:   0x7A1
functional request: 0x777
response:           0x7A9
Tx HTH:             0x13 (channel 1)
0x7A1 HRHs:         0x10 and 0x13 (channel 1)
channel 0 Rx:       none
channel 2 Rx:       none
```

Only the channel-1 boot channel record is enabled. The 442-byte boot peripheral
initialization implementation is byte-identical between `8965B4512000` and
`8965H1202000`. Across the core boot CAN/CanIf transport region
`0x3400..0x46FF`, the foreign image differs from Sienna at only three relocation
bytes caused by shifted variant-local tables; the driver logic itself transfers.

Therefore the physical repin is **not** compensating for an application→boot
controller migration, a different boot diagnostic arbitration ID, or an alternate
CAN0/CAN2 boot endpoint. The actual Corolla stays on RSCFD channel 1 across the
transition.

The public successful dump path also keeps the Panda CAN speed fixed across the
application→boot transition. Whatever the exact register-level timing fields
mean, a boot-only incompatible bitrate is incompatible with the observed
successful swapped-path dump and is not a viable explanation for the pin swap.

## 12. The real Corolla also reproduces the asynchronous `10 02` reset handoff

The foreign image independently transfers the Sienna programming-session
architecture:

- the five 10-byte session runtime records are byte-identical; the PROGRAMMING
  row is the same asynchronous kind-2 record;
- the programming policy uses the same `0x0180` speed threshold;
- readiness uses the same `0x0A00` supply threshold and the same phase/inhibit
  shape;
- the lower `0x08000200`/`0x08000201` handoff operation is backed by the same
  zero-return stub shape rather than a hidden network/security unlock;
- the same `0x5A` token/success convention is present;
- commit requests the same reset/system-mode path.

The session front end consequently has the same important observable property:
a successful PROGRAMMING request can remain in response-pending handling while
the application commits the reset. Endpoint disappearance can overtake a final
`50 02` response.

This matters because the pinned Bk2ol dumper constructs its UDS client with a
`0.1 s` timeout when that API accepts it, sends `10 02`, sleeps one second, then
sends `10 02` again; an exception exits the programming block as a failure. A
reported "PROGRAMMING timeout" from that tooling is therefore not evidence that
the ECU rejected programming. It can be a valid asynchronous reset whose final
positive response is overtaken, followed by failure to rediscover/reach the boot
endpoint on the selected physical route.

The pin swap does not bypass a hidden application SecurityAccess prerequisite,
change these speed/supply gates, or select a different lower handoff primitive.

## 13. Hypothesis matrix

| Hypothesis for why the swap helped | Static result | Evidence |
|---|---|---|
| EPS changes from CAN1 in application to CAN0/CAN2 in boot | **Eliminated** | `8965H1202000` app vectors/bodies and boot CanIf/RSCFD are channel 1 |
| bootloader changes `0x7A1/0x7A9` IDs | **Eliminated** | foreign boot tables retain `0x7A1/0x777 -> 0x7A9` |
| boot stack is a substantially different CAN implementation on Corolla | **Eliminated** | boot peripheral init exact; core CAN/CanIf driver transfers except three relocation bytes |
| pin swap satisfies a hidden programming SecurityAccess gate | **Eliminated for the first `10 02` handoff** | foreign session policy/handoff path has the same non-SA architecture; lower operation is stubbed |
| pin swap changes the application speed/supply programming prerequisites | **No direct mechanism recovered** | thresholds are local state predicates identical in shape/value; wiring operation has no firmware edge to them |
| Panda ELM param 0 vs 1 changes UDS permissions | **Eliminated** | same ELM whitelist; parameter selects board CAN mode |
| Panda heartbeat silently forces SILENT during programming | **Eliminated for standalone public tool pattern** | standalone Panda connect disables heartbeat checks |
| ELM software 0↔2 forwarding is required for the dump | **Eliminated** | ELM disables software forwarding and leaves relay pass-through |
| old `BUS=1` test directly exercised Toyota-B CAN1 | **Eliminated** | implicit ELM param 0 routes FDCAN2 to OBD path |
| physical swap corrects the network's placement relative to the CAN0/CAN2 intercept relay | **Supported directly** | official harness schematics + pinned field report that relay ended up on bus 1 instead of 0/2 |
| `param=1,bus=1` can directly attach diagnostics to stock CAN1 | **Supported statically; live programming confirmation pending** | Panda FDCAN2 mux truth table + Toyota-B wiring |
| `param=1,bus=1` is fully equivalent to repinning for normal openpilot interception | **Eliminated** | it leaves the vehicle network on unsplit CAN1 rather than the relay-backed CAN0/CAN2 pair |
| OBD/gateway path stops forwarding during/reset after `10 02` | **Survives; unproved** | consistent with topology, but no gateway firmware or dual-segment transition capture is pinned |
| indirect OBD path loses ACK / bus-off stability during transition | **Survives; unproved** | Panda explicitly handles FDCAN2 mux-related ACK errors; no field health trace binds this to the event |
| old client timeout semantics misclassified a successful async reset | **Strongly plausible contributor, not sufficient alone** | foreign firmware permits reset before final positive response; old tooling treated timeout as failure |

## 14. What static analysis still cannot choose

The remaining causal fork is now outside the EPS firmware.

The OBD-mux route can reach ordinary application diagnostics, but the repository
does not contain the relevant Toyota gateway firmware/configuration or a
simultaneous capture on both the OBD-facing and EPS-facing segments during
`10 02`. Consequently static evidence cannot distinguish among:

1. gateway forwarding/state changes while the EPS resets;
2. a gateway/indirect-route timing effect combined with the old client's short
   response-pending timeout;
3. ACK/bus-off behavior on the FDCAN2 OBD physical path during endpoint reset;
4. another vehicle-network wake/topology effect outside the EPS.

These are no longer equally broad hypotheses: all known EPS-side controller,
address, handoff, and privilege alternatives are closed on the real Corolla
image. A gateway policy must not be promoted from "plausible" to fact without a
gateway artifact or transition capture.

## 15. Correct tooling behavior

The robust diagnostic workflow is:

1. select `SAFETY_ELM327, param=1` so the remembered Panda state is normal-harness
   routing;
2. discover `0x7A1 -> 0x7A9 / F181` across logical buses, preferring bus 1;
3. persist `(elm327_param, tx_bus, rx_bus, request_id, response_id, F181)` as the
   route identity;
4. keep that physical route fixed across stateful operations;
5. treat a `10 02` response timeout as inconclusive unless an NRC was actually
   received;
6. rediscover the EPS/boot endpoint on the **same route** after the reset;
7. capture `health()`/`can_health()` around the transition so ACK/bus-off failures
   are distinguishable from ECU protocol behavior.

The current `kai-openpilot` TSK implementation already follows this model:
`tsk/lib/diagnostic_route.py` prefers normal routing and records the physical
route dimension, while `tsk/lib/programming.py` preserves it, tolerates the
expected asynchronous `10 02` timeout, and requires post-reset reappearance.

For normal openpilot interception, this diagnostic solution is insufficient by
itself. The vehicle network must still be presented to the harness box in the
expected CAN0/CAN2 split topology, whether by the physical repin or a corrected
Toyota-B adapter/harness mapping.

## 16. Bottom line

The static root cause is now substantially resolved:

```text
Why did the physical swap matter?
    Because the affected Toyota-B network was reported on harness CAN1,
    while comma's intercept relay is physically a CAN0 <-> CAN2 device.
    Swapping CAN0/CAN1 moves the vehicle network into the topology the
    harness box expects.

Why did ordinary UDS work before the swap?
    The attempted software bus-1 route still had ELM param 0, so FDCAN2
    was muxed to the OBD path. That indirect path could reach the EPS.

Does the EPS itself require the pin swap to enter boot/programming?
    No static evidence supports that. The actual 8965H1202000 Corolla uses
    RSCFD channel 1 and 0x7A1/0x7A9 in both application and boot, and its
    asynchronous programming-reset architecture transfers from Sienna.

Can diagnostics avoid the physical swap?
    Statically, the correct candidate is ELM param 1 + logical bus 1,
    which attaches FDCAN2 directly to stock harness CAN1. Live confirmation
    remains useful, but this is the correct electrical diagnostic experiment.

Can software alone make stock CAN1 equivalent to the 0/2 relay topology?
    No. Direct diagnostic access and harness interception are different
    problems. The relay topology still requires the network to be on CAN0/CAN2.
```

The only unresolved part is the exact vehicle-side reason the **indirect OBD
route** does not reliably survive/observe the programming reset. That is bounded
to gateway/timing/ACK/wakeup behavior outside the EPS; the pin-swap function
itself is no longer mysterious.
