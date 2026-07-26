# Application diagnostic stack and bootloader-entry analysis

This note separates the **application-mode** diagnostic stack from the bootloader
stack documented in `DID_MODEL.md`, `CAN_TRANSPORT_ANALYSIS.md`,
`PAYLOAD_GATE_ANALYSIS.md`, and `BOOTLOADER_DIAGNOSTICS.md`. The latter completes
bootloader SIDs `0x10/0x11/0x28/0x3E/0x85` and routines `0x10F1–0x10F3`.
Both stacks are present in the committed
`8965B4512000` CodeFlash image, but they use different tables, handlers, and
identification responses.

This distinction matters when comparing field probes from a related EPS. A request
sent while `F181` still returns a real part number is handled by the application;
the bootloader handlers at `0x4948`, `0x5FB8`, and `0x614A` do not yet control that
request.

All addresses below are CodeFlash virtual addresses. The independent checks in
`../tests/verify_application_diagnostics.py` validate the static tables and key
instruction sequences directly from the committed image.

## Executive result

The image contains a Denso application diagnostic configuration that is structurally
separate from the 20-entry bootloader UDS table at `0x8E54`:

- primary application service table at **`0x25E30`**;
- application identification-DID records at **`0x2A30C`**;
- application session-subfunction records at **`0x25BC0`**;
- application callbacks for sessions 1/2/3 at
  **`0x93FF6` / `0x94006` / `0x94016`**;
- a shared application session-control state machine at **`0x93F3C`**.

The primary application service table contains exactly these 17 SIDs:

```text
10 11 14 19 22 23 27 28 2E 31 34 36 37 3E 85 AB BA
```

The nearby application DID records expose `F181`, `F186`, and `F18C`, matching the
identity/session/serial shape observed by field tooling before bootloader entry.
By contrast, the bootloader DID table at `0x8F14` exposes only generated `F181` plus
write-only `0201/0202/0203`.

This is strong evidence that related EPS variants returning real `F181` and `F18C`
values are still in a closely related Denso **application** stack. It is not proof
that a related variant uses the same MCU, contains byte-identical bootloader code,
or retains the same payload-build secrets and routines.

## 1. Application identification DIDs

Three 16-byte records begin at `0x2A30C`. Their proven fields are the DID, flags,
and first callback pointer; the remaining two words are zero for these records:

```c
struct application_did_record {
    uint16_t did;
    uint16_t flags;
    uint32_t read_callback;
    uint32_t auxiliary_1;
    uint32_t auxiliary_2;
};
```

| Record | DID | Flags | Callback | Result |
|---:|---:|---:|---:|---|
| `0x2A30C` | `F181` | `0x0011` | `0x4E8E4` | application software identification |
| `0x2A31C` | `F186` | `0x0001` | `0x4E90A` | active diagnostic session |
| `0x2A32C` | `F18C` | `0x0014` | `0x4E918` | ECU serial record |

### `F181` application response

`application_read_f181 @ 0x4E8E4` writes prefix byte `0x01`, then copies 16 bytes
from CodeFlash `0x20860`:

```text
8965B4512000 00 00 00 00
```

A second 16-byte software-ID slot begins at `0x20870` and starts with `8A311`, but
this exact callback emits only the first 16-byte slot and reports count `0x01`.
Related application variants can use the same schema with a different count and
additional 16-byte records.

This callback is distinct from bootloader
`uds_read_data_by_identifier @ 0x5FB8`, which synthesizes `02 || 32*0x21` and
does not reference either stored software-ID slot.

### `F186` and `F18C`

- `application_read_f186 @ 0x4E90A` delegates to the application Dcm session API
  at `0x8FDDE`.
- `application_read_f18c @ 0x4E918` requests NvM record `0x207`; on a valid
  record it copies the serial bytes to the response, otherwise it fills the
  requested field with literal `0x3F` (`'?'`).

The presence of these callbacks explains why field tools can read a real part
number, current session, and ECU serial before entering the bootloader even though
those DIDs are absent from the four-entry bootloader table.

## 2. Primary application UDS service table

Seventeen 24-byte records begin at `0x25E30`. The SID is byte 8 of each record.
Several pointer and policy fields remain unnamed, so the report deliberately does
not assign AUTOSAR types to every byte. The complete SID sequence is definitive:

| Index | Record | SID | Selected configured pointer |
|---:|---:|---:|---:|
| 0 | `0x25E30` | `10` | subfunction table `0x25BC0` |
| 1 | `0x25E48` | `11` | callback `0x8B1F0` |
| 2 | `0x25E60` | `14` | — |
| 3 | `0x25E78` | `19` | callback `0x945DC` |
| 4 | `0x25E90` | `22` | callback `0x948AA` |
| 5 | `0x25EA8` | `23` | — |
| 6 | `0x25EC0` | `27` | subfunction table `0x25C30` |
| 7 | `0x25ED8` | `28` | callback `0x93C62` |
| 8 | `0x25EF0` | `2E` | callback `0x95DCE` |
| 9 | `0x25F08` | `31` | — |
| 10 | `0x25F20` | `34` | — |
| 11 | `0x25F38` | `36` | — |
| 12 | `0x25F50` | `37` | — |
| 13 | `0x25F68` | `3E` | subfunction table `0x25CA0` |
| 14 | `0x25F80` | `85` | subfunction table `0x25CB0` |
| 15 | `0x25F98` | `AB` | callback `0x8D344` |
| 16 | `0x25FB0` | `BA` | — |

The service-group directory at `0x25DE0` resolves the records after the primary table. It contains three generated service contexts:

| Group key | Index list | Receive connection | Response CAN IDs | Effective SID set |
|---:|---:|---|---|---|
| 2 | `0x25DF8`, 17 entries `0..16` | physical `0x7A1` | `0x7A9` | primary 17-SID table above |
| 3 | `0x25DC0`, six entries `17,2,7,9,13,14` | functional `0x777` | `0x7A9` | `10,14,28,31,3E,85` |
| 4 | `0x25E1C`, five entries `18..22` | secondary physical `0x7A0` | `0x7A8` | `10,19,22,3E,AB` |

The six extra 24-byte records at `0x25FC8..0x26057` supply the unique records needed by groups 3 and 4. They are not a fourth free-standing service table: the functional group reuses five primary records, while the secondary physical group uses five extra records. The application CAN demultiplexer maps `0x7A1/0x777/0x7A0` in that order to upper PDU IDs `0x0800..0x0802`; the generated Dcm group keys are correspondingly `2/3/4`. The transmit configuration supplies paired transport routes on `0x7A9` and `0x7A8`.

This limited `0x7A0 -> 0x7A8` diagnostic endpoint is therefore real, but its intended external tester or manufacturing role and the OEM meaning of SID `0xAB` remain unresolved. The primary application table must not be confused with the bootloader table at `0x8E54`.
For example, bootloader SIDs `14`, `19`, `23`, `AB`, and `BA` all point to
`uds_unsupported_service_handler @ 0x69B0`, while the application configures them
as independent services.

Consequently:

- an application response for `0x23`, `0xAB`, or `0xBA` does not establish that
  the bootloader implements that service;
- an application NRC `0x31` for DIDs `0201/0202/0203` does not establish that the
  bootloader payload-DID table is absent;
- bootloader session/security policies cannot be projected onto an application
  SecurityAccess level such as `0x03/0x04`.

## 3. Application DiagnosticSessionControl

The `SID 0x10` record points to the subfunction table at `0x25BC0`. The first
three 16-byte records select callbacks for the three configured sessions:

| Record | Subfunction | Callback | Wrapper behavior |
|---:|---:|---:|---|
| `0x25BC0` | `0x01` default | `0x93FF6` | call shared dispatcher with session 1 |
| `0x25BD0` | `0x02` programming | `0x94006` | call shared dispatcher with session 2 |
| `0x25BE0` | `0x03` extended | `0x94016` | call shared dispatcher with session 3 |

The wrappers all reach `application_session_callback_dispatch @ 0x93F3C`. The
first argument acts as an operation phase:

```text
phase 0 -> application_session_request_start  @ 0x93D28
phase 2 -> application_session_request_cancel @ 0x93E32
phase 3 -> application_session_request_poll   @ 0x93E72
```

### Current-session and request-shape prerequisites

The subfunction records contain current-session allow-lists. They are enforced by
the generic Dcm layer before the wrapper callback runs:

| Requested session | Allow-list pointer | Allowed current sessions |
|---|---:|---|
| default `0x01` | `0x25BAB` | default `01`, programming `02`, extended `03` |
| programming `0x02` | `0x25B64` | programming `02`, extended `03` |
| extended `0x03` | `0x25B66` | default `01`, extended `03` |

Thus the first Sienna application request must be **EXTENDED -> PROGRAMMING**.
A direct DEFAULT -> PROGRAMMING request does not reach `0x94006`; already being
in PROGRAMMING is also accepted. This table restriction is independent of the
application-specific policy hook below.

The callback receives the subfunction after generic Dcm parsing. At `0x93D28`,
the remaining request-data length must be zero. For the ordinary wire request,
that means the exact two-byte UDS payload `10 02`; trailing bytes produce NRC
`0x13`. Generic suppress-positive-response parsing can route `10 82` to the same
subfunction, but negative responses such as `0x78` are not suppressed.

### Runtime session record and timing

Application `tp` is `0x23EE4`, so the five 10-byte records scanned as
`tp+0x2412+n*10` start at `0x262F6`. The PROGRAMMING record is at `0x26300`:

```text
02 02 32 00 88 13 D0 07 F4 01
```

The first byte is transition kind `2`, selecting the asynchronous handoff. The
second is session `2`. The response timing words include P2 `0x0032` = 50 ms and
encoded P2* `0x01F4` = 500 units = 5,000 ms. The two intermediate configuration
words are `0x1388` and `0x07D0`; their exact generated-Dcm field names have not
been recovered. The same timing values occur in the default and extended
records, so no one-second pre-request delay is encoded as a PROGRAMMING
prerequisite.

### Immediate vehicle-speed policy

`0x93D28` calls:

```text
0x93FE8 -> application_session_transition_check_adapter @ 0x8A27E
         -> application_session_transition_policy @ 0x4C942
```

Disassembly resolves the calling-convention ambiguity: the adapter places the
current session in `r6` and requested session in `r7`. The policy ignores `r6`.
It rejects only requested session `2` when:

```text
uint16(FEBFC892) > uint16(CodeFlash[0x181DC])
                         0x0180
```

Internal result `0x0B` is mapped by `0x8D5FC` to standard UDS NRC `0x88`,
`vehicleSpeedTooHigh` (not a vendor-specific NRC). Elsewhere at `0x5379C`, the
same RAM value is converted as `raw * 100 / 128`; threshold `0x0180` therefore
becomes 300 scaled units, strongly indicating a **3.00 km/h** ceiling. The raw
comparison and NRC meaning are definitive; the physical-unit reconstruction is
a strong inference.

There is no security-unlock, DTC-setting, communication-control, tester-present,
or prior failed-attempt check in this policy.

### Asynchronous handoff prerequisites

After the speed check passes, `0x93D28` selects transition kind 2, stores pending
state, and emits NRC `0x78`. Polling reaches:

```text
0x93E72 -> 0x93FDC -> application_session_transition_async_worker @ 0x8A244
```

The worker has two generated lower stages:

1. `application_programming_prepare_handoff @ 0x8A0C2` calls `0x8A01C` with
   operation `0x08000200`, status `10`, and no payload.
2. `application_programming_commit_handoff @ 0x8A172` calls `0x8A01C` with
   operation `0x08000201`, status `10`, and four zero bytes.

Crucially, `0x8A01C`, its poll helper `0x8A020`, and token validator `0x8D534`
are compiled stubs in this image: they return immediate success/valid without
using the operation ID or payload. These constants therefore do **not** prove an
NvM boot-selection write. The observed handoff state at `0xFEBF3B14` is explicitly
zeroed before the second call.

Between those stages, `0x4C960` requires all three of the following:

| Check | Exact condition | Failure |
|---|---|---|
| status input | byte `FEBFC81F != 0x11` | internal `1` -> NRC `0x22` |
| scaled supply input | `uint16(FEBF4692) >= 0x0A00` (`CodeFlash 0x181DE`) | internal `1` -> NRC `0x22` |
| alternate-handoff flag | byte `FEBF6152 == 0` | internal `1` -> NRC `0x22` |

The supply value is converted elsewhere as `raw * 10 / 256`; `0x0A00` becomes
100 scaled units, strongly indicating a **10.0 V** minimum.

The first byte is now bounded structurally. `application_input_snapshot_update @
0xBCB3A` copies it from the live GP-relative byte at `0xFEBEB1A4` (`gp-0x65C`)
to snapshot byte `0xFEBFC81F` (`gp+0x301F`). The live source is owned by the
generated transition state machine at `0xB28AC/0xB2912`, not by Dcm. Initialization
sets phase `0`; the recovered transitions assign phase markers `0x11` and `0x22`
while coordinating system modes `0x300/0x400/0x500` and event `0x23`. Adjacent
state-machine flags use `0x5A`, but the copied phase byte itself is not that
marker. The handoff gate rejects phase `0x11` specifically.

Accordingly the defensible name is **system-transition phase snapshot**, not
"programming status", ignition state, READY state, or communication status. Its
exact Toyota/Denso phase labels and physical condition remain unavailable.
`FEBF6152` is set from an application initialization callback (`0x8F1E8 ->
0x8A00C -> 0x4C506`); normal diagnostic operation requires its clear branch.

No latch requires a power cycle between attempts. The worker state is reset by
`0x8A082 -> 0x8A044`, and the one-request marker at `FEBF6166` is explicitly
cleared before a new reset request.

### Reset/shutdown behavior

When both lower stages succeed, `application_programming_reset_request @ 0x4C98C`:

1. checks that `FEBF6152` is clear;
2. if marker `FEBF6166` is clear, invokes the system event API at `0xB02BC` with
   event `9`;
3. sets `FEBF6166 = 0x5A` so that the event is queued once.

`system_mode_coordinator @ 0xB0518` checks event 9 in every ordinary mode and
moves to mode `0x900`. Its entry callback at `0xB20EA` writes paired subsystem
shutdown requests `0x70017001` and `0x00020002`. The coordinator then advances
through mode `0x800`; its final reset branch reaches `0x608AA`, which disables
hardware, programs reset/watchdog registers, invokes the low-level reset helper,
and loops forever awaiting reset.

After event 9 is queued, `0x8A244` latches `FEBF3B19 = 0x5A` and deliberately
returns internal value `10` (pending), not success. The UDS path therefore keeps
NRC `0x78`/pending semantics while shutdown and reset overtake it; an application
`50 02` is not required before the CAN endpoint disappears. This behavior can
look exactly like a client timeout when the client consumes response-pending
frames and waits for a final positive response.

This is the code relevant to the **first** `10 02` in the public extraction flow.
The tooling reads an application `F181`, sends DEFAULT -> EXTENDED -> PROGRAMMING,
then expects the bootloader's placeholder `F181`. The bootloader handler at
`0x614A` cannot explain the first request, and a silent final response is
compatible with the confirmed application reset path.

## 4. Corrected bootloader session-control interpretation

`uds_diagnostic_session_control @ 0x614A` belongs to the bootloader table at
`0x8E54`. It does not directly transmit a response on every path:

- invalid session/length/policy branches call the negative-response helper at
  `0x6136`;
- valid transitions store request state around `0xFEBF2B9F..0xFEBF2BA3` and
  return;
- `bootloader_session_control_task @ 0x6244` advances the queued transition;
- the positive response is built later at `0x6204` after the current session is
  updated through `0x51D8`.

The helper at `0x4776` is also not a permanent one-attempt-per-boot latch. It
reserves a transient main-loop operation flag at `0xFEBF2AA3`; main-loop function
`0x137A` calls `0x479A`, which clears both `0xFEBF2AA3` and the associated byte at
`0xFEBF2AA2`. Treating this as a one-shot PROGRAMMING allowance is incorrect.

A healthy instance of this bootloader is expected to eventually produce either a
positive response or an NRC, but the static handler alone does not prove that a
related application's initial `10 02` timeout must be external to the EPS.

## 5. Addressing implications

The bootloader transport configuration proves:

```text
physical request    0x7A1
functional request  0x777
response            0x7A9
```

The bootloader `SID 0x10` addressing mask is `0x03` (physical or functional).
Its `0x28` and `0x85` masks are `0x01` (functional-only), while `0x11`, `0x27`,
`0x2E`, `0x31`, `0x34`, `0x36`, and `0x37` are physical-only.

Standard OBD functional ID `0x7DF` is **not** configured in this bootloader.
A related-variant probe that uses `0x7DF` has not exercised the firmware-derived
functional path at `0x777`. The application configuration also contains physical `0x7A1 -> 0x7A9`,
functional `0x777 -> 0x7A9`, and limited secondary physical `0x7A0 -> 0x7A8`
contexts. These are firmware facts for this image, not proof that every related
application retains all three endpoints.

## 6. Corolla comparison

The 2025 Corolla Hybrid observations for EPS `8965F1208000` show the same
application-facing identity shape (`F181`, `F186`, and `F18C`) and successful
DEFAULT/EXTENDED sessions. That is strong evidence of related Denso application
architecture, but the Sienna prerequisites must be compared individually:

| Sienna requirement/behavior | Corolla probe status | Interpretation |
|---|---|---|
| start in EXTENDED (`F186=03`) or PROGRAMMING | **tested** by extended -> programming sequences | matches the required Sienna starting session |
| direct DEFAULT -> PROGRAMMING | **tested but invalid for Sienna** | its failure/silence says nothing about the valid Sienna path |
| exact physical `10 02` to `0x7A1` | **tested** | correct physical request shape/ID |
| speed `<= 0x0180` raw (strongly 3.00 km/h) | **likely but not measured from EPS RAM** in stationary/Not-Ready tests | no observed motion suggests it was met, but this is not a firmware-level Corolla proof |
| scaled supply `>= 0x0A00` (strongly 10.0 V) | **not measured** | a low-voltage condition remains an untested Sienna-equivalent NRC `0x22` cause |
| system-transition phase snapshot not `0x11` | **not measured** | the producer is identified, but its Corolla value and OEM phase labels are unknown |
| security unlock before `10 02` | **not required by Sienna** | Corolla security-first attempts test a variant difference, not a Sienna prerequisite |
| `0x85`/`0x28` preamble | **not required by Sienna** | those experiments may reveal Corolla-specific behavior but cannot satisfy a missing Sienna gate |
| one-second settle/tester-present/double request | **not required by Sienna** | no such prerequisite exists in the session record or policy |
| initial and continuing NRC `0x78` followed by shutdown/reset | client reports final timeout/silence | compatible with the Sienna path because the client waits for a final `50 02` that the reset can overtake |
| bootloader functional request at `0x777` | **untested**; probes used `0x7DF` | the firmware-derived functional path remains open |
| post-reset bootloader response on `0x7A9` | not conclusively captured during the reset window | required to distinguish successful silent handoff from Corolla policy/filtering |

The key correction is that Sienna does **not** require a secret preamble. Its
valid path is EXTENDED -> PROGRAMMING while stationary, with adequate supply and
the system-transition phase not equal to `0x11`. It then queues reset while keeping UDS pending. A
Corolla timeout after a valid extended request is therefore not, by itself,
evidence of either refusal or gateway filtering.

A post-timeout `F186` read is also not decisive: if the ECU reset into the
bootloader and then returned to the application before the read, it will again
report default/application state. The discriminating probe is reset-window
capture on every panda bus for response ID `0x7A9`, followed by bootloader `F181`
and functional `10 02`/preamble traffic on `0x777` rather than `0x7DF`.

The similarity still does **not** prove:

- the Corolla MCU part number or byte-identical application policy;
- the Corolla value and OEM phase label corresponding to the Sienna system-transition snapshot;
- the identity of responder `0x7F1` or an intervening gateway/diagnostic master;
- that the Corolla bootloader retains `SEED_KEY_SECRET`, `PAYLOAD_BUILD_SECRET`,
  DIDs `0201/0202/0203`, or routines `10F0/FF00`.

Those require successful bootloader capture or a firmware image from part
`8965F-12080`.

## 7. Evidence grades

| Finding | Grade |
|---|---|
| primary application service table location and 17-SID sequence | **Definitive** |
| group keys 2/3/4 select primary, functional six-SID, and secondary five-SID contexts | **Definitive** |
| secondary `0x7A0 -> 0x7A8` endpoint's intended OEM tester role | **Unknown** |
| application `F181/F186/F18C` records and callback addresses | **Definitive** |
| `F181` copies one stored 16-byte software ID in this image | **Definitive** |
| session 1/2/3 wrapper callbacks and shared state machine | **Definitive** |
| PROGRAMMING is allowed only from current session 2 or 3 | **Definitive** |
| programming policy rejects raw speed above `0x0180` with NRC `0x88` | **Definitive** |
| `0x0180` represents 3.00 km/h | **Strong inference from conversion and NRC semantics** |
| lower handoff requires transition phase != `0x11`, supply >= `0x0A00`, and flag clear | **Definitive** |
| `FEBFC81F` is a snapshot of the `0xB28AC/0xB2912` system-transition phase | **Definitive** |
| OEM names for phase values `0/0x11/0x22` | **Unknown** |
| `0x0A00` represents 10.0 V | **Strong inference from conversion and use** |
| lower operation IDs `0x08000200/201` write an NvM boot flag | **Unsupported; compiled callee is a no-op stub** |
| application session state machine supports asynchronous transition and NRC `0x78` | **Definitive** |
| successful PROGRAMMING queues event 9, shutdown mode `0x900`, and reset sequencing | **Definitive** |
| reset reaches the bootloader rather than returning directly to application | **Strong inference** |
| bootloader `0x614A` queues valid transitions instead of responding directly | **Definitive** |
| `0x4776` state is cleared by the main-loop task and is not per-boot one-shot | **Definitive** |
| a related real-identifier response indicates application mode | **Strong inference** |
| a related EPS probably retains the same bootloader payload path | **Variant inference** |
| an observed PROGRAMMING timeout proves gateway filtering | **Unsupported without more evidence** |
