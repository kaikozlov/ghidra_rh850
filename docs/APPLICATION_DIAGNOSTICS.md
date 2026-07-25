# Application diagnostic stack and bootloader-entry analysis

This note separates the **application-mode** diagnostic stack from the bootloader
stack already documented in `DID_MODEL.md`, `CAN_TRANSPORT_ANALYSIS.md`, and
`PAYLOAD_GATE_ANALYSIS.md`. Both stacks are present in the committed
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

A shorter secondary configuration block begins at `0x25FC8`; its protocol/connection role is not yet resolved and is outside this report's 17-record table model. The primary application table must not be confused with the bootloader table at `0x8E54`.
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

### Initial request path

`0x93D28`:

1. validates the request object/length;
2. calls the application transition-policy hook through
   `0x93FE8 -> 0x8A27E -> 0x4C942`;
3. finds the requested session in a five-entry session configuration;
4. either updates the Dcm session and prepares the positive timing response, or
   starts an asynchronous transition and emits NRC `0x78` (response pending).

### Asynchronous programming transition

The poll path at `0x93E72` eventually invokes
`0x93FDC -> application_session_transition_async_worker @ 0x8A244`. That worker
uses the application's lower service path around `0x8A0C2/0x8A172` and can return
success, failure, or pending. `application_internal_result_to_nrc @ 0x8D5FC`
maps internal result codes to UDS NRCs including `0x22`, `0x31`, `0x72`, `0x78`,
and vendor NRC `0x88`.

This is the code relevant to the **first** `10 02` in the public extraction flow.
The tooling reads an application `F181`, sends DEFAULT -> EXTENDED -> PROGRAMMING,
then reads the bootloader's placeholder `F181`. The bootloader handler at `0x614A`
is therefore not sufficient to explain whether that first request was accepted,
filtered, or stalled.

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
functional path at `0x777`. The application transport configuration has not yet
been traced end-to-end, so `0x777` should be treated as a high-value,
firmware-grounded test—not as proof that every related application must listen on
that ID.

## 6. Related-variant interpretation and limits

A related EPS that returns:

- a counted list of one or more 16-byte software IDs from `F181`;
- current session from `F186`;
- an ASCII serial from `F18C`;
- the same application service set;

is showing strong structural continuity with this Denso application stack. This
supports investigating the known bootloader-entry and payload path before assuming
that a different part-number prefix implies a completely different implementation.

It still does **not** prove:

- the MCU part number;
- byte-identical application transition policy;
- the identity of an intervening gateway or diagnostic master;
- that silence on `10 02` is external rather than an application policy/stall;
- that `SEED_KEY_SECRET`, `PAYLOAD_BUILD_SECRET`, DIDs `0201/0202/0203`, or
  routines `10F0/FF00` are retained in the related bootloader.

Those require either successful bootloader entry, a firmware image from the
related EPS, or additional transport/gateway evidence.

## 7. Evidence grades

| Finding | Grade |
|---|---|
| primary application service table location and 17-SID sequence | **Definitive** |
| application `F181/F186/F18C` records and callback addresses | **Definitive** |
| `F181` copies one stored 16-byte software ID in this image | **Definitive** |
| session 1/2/3 wrapper callbacks and shared state machine | **Definitive** |
| application session state machine supports asynchronous transition and NRC `0x78` | **Definitive** |
| PROGRAMMING uses that asynchronous lower transition to enter the bootloader | **Strong inference** |
| bootloader `0x614A` queues valid transitions instead of responding directly | **Definitive** |
| `0x4776` state is cleared by the main-loop task and is not per-boot one-shot | **Definitive** |
| a related real-identifier response indicates application mode | **Strong inference** |
| a related EPS probably retains the same bootloader payload path | **Variant inference** |
| an observed PROGRAMMING timeout proves gateway filtering | **Unsupported without more evidence** |
