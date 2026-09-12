# F33 network-only recovery: gateway route and transport qualification

2026-09-12. This work uses the existing vehicle network only. No connector work,
vehicle transmission, session change, reset, RAM upload or ECU flash write was
performed. A working EPS repair has **not** been demonstrated.

## Candidate: complete the OEM gateway preparation before judging EPS silence

The meaningful untested condition is not another unmodified EPS request. It is:

```text
Existing diagnostic/OBD connection
  -> positively identify the actual central-gateway endpoint
  -> perform that gateway family's supported, authorized reprogramming preparation
  -> establish its successful acknowledgement/result
  -> query the EPS through the prepared route
  -> identify any surviving application/boot executor before considering restoration
```

This candidate tests whether a surviving EPS listener is hidden by network
routing/state. It does not assert that a gateway can execute flash commands
inside a CPU trapped by the malformed instruction. Successful gateway preparation
without a native EPS response is **not** a successful recovery.

The existing detailed evidence is in
[the exception follow-up, sections 18–21](camry-f33-recovery-exception-followup.md).
The optional pre-transition read was independently checked in this pass against
the current recovered `TCUWCanUnifiedPrepareWriter.dll`:

- `10002211` calls the optional F181 wrapper at `100026E0`.
- The `ReadSoftwareID` call is at `10002778`; the catch-all continuation at
  `100027AE` targets ordinary cleanup `1000277E`, followed by the wrapper return.
- Back at `10002216..10002230`, the caller stops/restarts its periodic machinery
  and enters the configured gateway loop, without testing an F181-success flag.
- The mandatory target programming-session call is **later**, at `10002363`.

Thus failure of the early EPS identity request does not, by itself, stop the
host from attempting gateway preparation. The later target-service dependency
must not be projected backward onto this optional initial read. Conversely,
getting past the host's optional read does not prove a bootloader is listening.

The retained 39 post-incident log segments do not establish that node-5F gateway
preparation was completed: the selected shared-ID records are for other logical
nodes. Their time coverage is partial. This is an untested-condition finding,
not a claim that no such operation was attempted at any time.

## Exact Camry endpoint, rather than a shared CAN ID alone

Current Toyota master data and the runtime's unmodified offline mount resolver
agree for **both** Camry HV vehicle types 12704 and 12984:

| Logical ECU | Category | Request | Address extension |
|---|---:|---|---|
| EPS / EMPS | 405 | `7A1` | None |
| Brake/EPB | 435 | `7B0` | None |
| Central Gateway | 443 | `750` | `5F` |
| Brake Booster | 466 | `750` | `29` |

The central-gateway reply route is `758`, extension `5F`, as independently
constructed by the current CUW helpers. A `750/758` exchange using extension
`0F` or `6D` is not an exchange with this gateway. The physical `7B0` identity
must not silently identify the separate logical brake-booster endpoint.

Primary inputs are current `Toyota.ddb` type 13, the vehicle's install-set
membership, and the recovered helper's `000007505F/000007585F` literals.
The vehicle tables describe candidates, not proof of installed/live responders.

## Two reproduced client defects that would invalidate the gateway experiment

These were found in the separate `toyota-diagnostics` runtime and fixed there,
not in the ECU or the openpilot driving path.

### 1. An explicit OBD-route request was silently discarded

Before `41e1931`, `transport.connect(..., obd_multiplexing=True)` returned
`ManagedPandaAdapter(profile)` whenever pandad owned Panda. The requested
physical mux setting was neither propagated nor applied. Transport status also
reported the inherited managed route as ready.

The fix requires direct Panda ownership for this **explicit route change** and
reports that limitation before constructing a managed adapter or sending data.
Ordinary managed diagnostics remain unchanged. Direct mode applies normal Panda
ELM327 parameter 0 for OBD routing; parameter 1 selects the normal harness route.
These settings are independently supported by Panda `board/main.c` and the
`tres_set_can_mode` implementation in `board/boards/tres.h`.

A logical bus-1 label is not proof of the physical mux state. `safetyParam` alone
is not a mux readback either, because Panda also has a separate `set_obd()` path.
This fix is not evidence that the withdrawn incident catcher used the new CLI
or suffered this particular defect; it prevents a future test from silently
using the wrong requested route.

### 2. Another node's shared-ID reply aborted the selected transaction

Before `cd0aa90`, a valid `758` response from extension `0F` or `6D` caused the
installed upstream ISO-TP client to raise `InvalidSubAddressError` while waiting
for `5F`, even if the matching gateway reply immediately followed in the same
batch. The failure was reproduced with actual `UdsClient`/`IsoTpMessage` code and
FakePanda, rather than by mocking the ISO-TP result.

The fix adds a small borrowed-transport address-extension demultiplexer before
ISO-TP. It leaves bus/CAN-ID filtering and all ISO-TP validation with the upstream
client, honors an explicit different RX extension including zero, and preserves
full-batch draining. Physical unextended EPS transactions remain unwrapped.
There is no target-specific CAN-ID list, vehicle permission state or change to
Panda safety in this demultiplexer.

The new tests fail on the old implementation and pass after the fixes. The full
runtime suite passes **182 tests**, including **14 transport tests**. These are
hardware-independent software tests, not successful vehicle transactions.

## Checked baseline command: existing CLI, no new probing framework

The existing raw endpoint command can make the initial ordinary gateway
TesterPresent read without an automatic VIN scan, EPS identity guard, session
ladder or programming attempt:

```sh
toyota --bus 1 --obd-multiplexing uds raw 0x750 0x3E 00 \
  --sub-address 0x5F --rx-address 0x758 --rx-sub-address 0x5F
```

This command was exercised end-to-end with all Panda I/O replaced by FakePanda.
It requested ELM327 parameter 0 and made exactly one host submission:

```text
bus 1, CAN 750: 5F 02 3E 00 00 00 00 00
```

After simulated unrelated `0F/6D` replies, the real ISO-TP implementation
accepted the simulated `5F` reply and returned payload `7E 00`. That proves the
host routing request, address-extension framing and receive isolation, **not**
the vehicle's response. Panda host submissions are not a count of wire retries.

This is only the baseline read. Manufacturer gateway-family qualification and
reprogramming preparation are separate stages. The current native classifier
uses request form and its validated response, not merely the model year or
an assumed gateway generation. P4-shaped preparation has an explicit default-
session cleanup in the host; the P5-specific cleanup must not be invented by
borrowing the SMC or P6 flow. Preserve the actual response and use the matching
supported OEM procedure, including normal authorization and exit handling.

Do not run this from the wrong environment: the car must remain parked, and
an explicit direct-Panda remap requires releasing pandad/manager ownership.
No command here changes EPS software or demonstrates restoration. A fresh
read-only gateway response is needed to select the actual next branch rather
than guess a mode-changing sequence.

## Separate SMC state/cleanup helper is not a Camry cancellation primitive

An apparent missing cleanup was investigated in current `TCUWUnifiedUtils.dll`,
not inferred from an export name. `ReadProgrammingModeControlState` at
`100043D0` builds RDBI `22 10 05`, checks `62 10 05`, and extracts bit 0 of the
first data byte. Its address literals at `100082BC/100082C8` are **751/761**,
not the Camry `750/758` plus `5F` route.

The actual UnifiedFlashWriter caller (`10001961..100019B8`) first matches the
package gateway string **0751**, reads this state, and invokes SMC routine type
4 when the state is nonzero. ReproStdFlashWriter has the same explicit 0751
selection at `100025C0..10002617`. `RoutineControlForSMCCentralGW` at
`10005250` has its own start/stop operations for that separate endpoint.
The SMC acronym is not expanded here without OEM provenance.

Toyota master categories 5038/8502 carry 751 routes in the overall corpus;
neither a 751 route nor those logical candidates is present in either inspected
Camry install set. This bounds applicability, not the contents of every real
vehicle. Sending the SMC stop operation to the Camry's normal gateway would be
an unsupported substitution, not completion of the P5 exit proof.

The protected stubs, sidecars and recovered copies of UnifiedUtils,
UnifiedPrepareWriter, UnifiedFlashWriter and CommonPrepareWriter were freshly
hash-matched against `build/out/cuwplus-unprotected/manifest.json`. Their current
installed PE inputs are the reproducible source. Disposable disassemblies under
`build/work/f33-gateway-control-state-20260912/` are convenient working outputs,
not required authority for these conclusions.

## Live boundary

The configured comma SSH endpoint did not answer. A read-only check of the
owner's router's cached, comma-named DHCP lease still resolves to that same
configured address; this is not an overlooked known replacement IP. The stored
comma-named overlay-network peer is offline and stale. Local J2534 provider
discovery returns no provider; no local serial-device candidate was present.
These availability observations are not facts about EPS execution.

There has been no live gateway response, completed gateway preparation, new EPS
identity or ECU repair in this pass. The concrete next experiment is the
properly routed and demultiplexed **OEM gateway-preparation condition**, not a
repeat of unchanged EPS polling and not any work under the car.
