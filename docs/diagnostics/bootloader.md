# Remaining bootloader diagnostic services and routines

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS DIAG-BOOT-002
>
> **Canonical artifacts:** —
>
> **Verification:** `tests/verify_bootloader_diagnostics.py`
>
> **Related:** [bootloader-dids](bootloader-dids.md), [payload-gate](../security/bootloader-payload-gate.md)

This note completes the implemented bootloader diagnostics that were not covered
in `../diagnostics/bootloader-dids.md`, `../security/bootloader-payload-gate.md`, or the SecurityAccess analysis in
the top-level README. Its scope is the bootloader UDS table at CodeFlash
`0x8E54`, not the separate application Dcm configuration documented in
`../diagnostics/application.md`.

All addresses are CodeFlash virtual addresses. The independent checks in
`../tests/verify_bootloader_diagnostics.py` validate the service/routine tables,
policy bytes, state-machine instructions, response builders, and memory-transfer
mode directly from the committed CodeFlash image.

## Executive result

The five remaining implemented services are deliberately narrow:

| SID | Handler | Addressing | Required session | Accepted request | Effect |
|---:|---:|---|---:|---|---|
| `10` | `0x614A` | physical or functional | transition-dependent | `10 01/02/03`, suppress bit allowed | queue default/programming/extended transition |
| `11` | `0x60C2` | physical only | programming `02` | `11 01`, suppress bit allowed | hard-reset after response handling |
| `28` | `0x688A` | functional only | extended `03` | `28 01 01`, suppress bit allowed | positive acknowledgment only |
| `3E` | `0x4FF8` | functional only | default/programming/extended | `3E 00`, or suppressed `3E 80` | positive acknowledgment only |
| `85` | `0x693A` | functional only | extended `03` | `85 02`, suppress bit allowed | positive acknowledgment only |

`0x28` and `0x85` do not change a communication or DTC manager in this
bootloader. Their accepted subfunction bytes are stored only long enough to
construct the positive response. TesterPresent likewise has no service-local
session timer or keepalive state.

The RoutineControl table at `0x8F44` contains five StartRoutine-only records:

| RID | Option length | Function |
|---:|---:|---|
| `10F0` | 10 | verify/authenticate the 4 KiB RAM payload region |
| `10F1` | 10 | exact compiled alias of `10F0` |
| `10F2` | 10 | verify a CodeFlash region, then program its four-byte validity marker |
| `10F3` | 0 | arm the alternate RequestDownload/TransferData compare mode |
| `FF00` | 10 | start the authorized erase path used for payload execution |

All five routines require programming session, unlocked SecurityAccess state 2,
and StartRoutine subfunction 1. `10F3` is not a checksum or erase operation: it
sets transfer state 8, after which a class-0 RequestDownload selects operation
bit 5 and TransferData compares tester bytes against existing CodeFlash in
16-byte asynchronous steps.

## 1. Policy bytes and request addressing

The bootloader service-table records are `SID:u8, addressing_mask:u8,
reserved:u16, handler:u32` — 20 entries at `0x8E54`, walked by
`uds_service_dispatch @ 0x5222`. The complete table:

```text
0x8E54  SID 10  mask 03  handler 614A  DiagnosticSessionControl
0x8E5C  SID 11  mask 02  handler 60C2  ECUReset
0x8E64  SID 27  mask 02  handler 5516  SecurityAccess
0x8E6C  SID 28  mask 01  handler 688A  CommunicationControl
0x8E74  SID 3E  mask 01  handler 4FF8  TesterPresent
0x8E7C  SID 85  mask 01  handler 693A  ControlDTCSetting
0x8E84  SID 22  mask 02  handler 5FB8  ReadDataByIdentifier
0x8E8C  SID 23  mask 03  handler 69B0  ReadMemoryByAddress         (unsupported)
0x8E94  SID 2C  mask 03  handler 69B0  DynamicallyDefineDataIdentifier (unsupported)
0x8E9C  SID 2E  mask 02  handler 4948  WriteDataByIdentifier
0x8EA4  SID 14  mask 02  handler 69B0  ClearDiagnosticInformation (unsupported)
0x8EAC  SID 19  mask 03  handler 69B0  ReadDTCInformation         (unsupported)
0x8EB4  SID 2F  mask 03  handler 69B0  InputOutputControlByIdentifier (unsupported)
0x8EBC  SID 31  mask 02  handler 567E  RoutineControl
0x8EC4  SID 34  mask 02  handler 5D68  RequestDownload
0x8ECC  SID 36  mask 02  handler 4DBA  TransferData
0x8ED4  SID 37  mask 02  handler 5C92  RequestTransferExit
0x8EDC  SID AB  mask 03  handler 69B0  (proprietary — unsupported)
0x8EE4  SID BA  mask 03  handler 69B0  (proprietary — unsupported)
0x8EEC  SID BB  mask 03  handler 69B0  (proprietary — unsupported)
```

The bootloader speaks **standard UDS only**. Twelve SIDs are implemented
(`0x10/0x11/0x22/0x27/0x28/0x2E/0x31/0x34/0x36/0x37/0x3E/0x85`); eight are
explicitly routed to `uds_unsupported_service_handler @ 0x69B0` (five standard
UDS SIDs the firmware declines — `0x14/0x19/0x23/0x2C/0x2F` — plus three
non-standard `0xAB/0xBA/0xBB`, presumably Toyota/DENSO proprietary opcodes
this calibration rejects). Any SID not in the table falls through to
`FUN_000051fa(sid, 0x11)` → NRC `0x11` (serviceNotSupported). **There is no
proprietary/VFOREST protocol handler** — the reflash path is entirely standard
UDS (`0x2E` DID writes → `0x34/0x36/0x37` → `0x31`), which is why the CUW
VFOREST `SendNonceAndSeedKey` frames (`0x37`–`0x3c` block-seq) cannot apply to
this calibration (see [../tooling/techstream.md](../tooling/techstream.md) §4.6,
CORR-021).

Mask `0x02` is physical-only (`0x7A1`), mask `0x01` is functional-only
(`0x777`), and mask `0x03` permits both. These masks are independent of the
session checks inside each handler.

The contiguous session-policy bytes at `0x8EF4..0x8EFF` resolve as:

```text
0x8EF4  02   ECUReset
0x8EF6  03   CommunicationControl
0x8EF7  03   ControlDTCSetting
0x8EF9  02   RoutineControl
0x8EFD  01 02 03   TesterPresent allow-list
```

Unsupported active sessions return NRC `0x7F`. Exact-length failures return NRC
`0x13`; unsupported subfunctions return NRC `0x12` unless noted otherwise.

## 2. DiagnosticSessionControl (`SID 0x10`)

`uds_diagnostic_session_control @ 0x614A` accepts only the two-byte request and
subfunctions 1, 2, or 3. Bit 7 is the standard suppress-positive-response bit.
There is no SecurityAccess prerequisite.

The supported transitions are:

| Requested session | Allowed current session(s) | Rejected transition |
|---:|---|---|
| default `01` | `01`, `02`, `03` | — |
| programming `02` | `02`, `03` | default `01` -> NRC `0x7E` |
| extended `03` | `01`, `03` | programming `02` -> NRC `0x7E` |

Valid requests store the requested session/subfunction around
`0xFEBF2BA0..0xFEBF2BA3`. `bootloader_session_control_task @ 0x6244` advances
the queued transition; `0x614A` does not directly build the normal positive
response.

Programming uses the asynchronous main-operation path. The task waits for the
reserved operation at `0x4776/0x478E/0x4794`, returns NRC `0x22` if it cannot
complete, and otherwise updates the current session through
`bootloader_set_diagnostic_session @ 0x51D8`. Default and extended transitions
use the same final update helper.

`bootloader_session_positive_response @ 0x6204` emits:

```text
50 requested_session 00 32 01 F4
```

The timing fields are P2 = 50 ms and encoded P2* = 500 units = 5,000 ms. With
bit 7 set, the session transition still occurs and only the final positive
response is suppressed.

### 2.1 Bootloader SecurityAccess failure counter and delay

The physical-only `SecurityAccess` handler at `0x5516` implements a small
RAM-only anti-bruteforce state machine for the bootloader `27 01/27 02` flow.
The relevant state is:

```text
FEBF2B57  failed-key attempt counter
FEBF2B56  delay/lockout flag
FEBF2B20  delay start tick
FEBF2B1C  delay duration ticks
```

A mismatching `27 02` key first checks `attempt_counter - 1`. From the initialized
value zero, the first bad key increments `FEBF2B57` to 1 and returns NRC `0x35`
(`invalidKey`). The second consecutive bad key takes the exceeded-attempts path:
it records the current free-running timer value, stores duration `200000000`,
sets `FEBF2B56 = 1`, clears `FEBF2B57` to zero, and returns NRC `0x36`
(`exceededNumberOfAttempts`). While the flag is set, `27 01` returns NRC `0x37`
(`requiredTimeDelayNotExpired`). `direct_call_target_00005584 @ 0x5584` clears
the flag once the elapsed timer delta exceeds the stored duration.

The timer scheduler at `0x1D2C` converts its 16-bit millisecond delay argument to
this same free-running tick domain as `delay * 20000`; the adjacent CanTp timing
configuration contains ordinary `1000/150/10` ms values consumed through that
scheduler. Therefore the SecurityAccess duration is:

```text
200000000 ticks / 20000 ticks-per-ms = 10000 ms = 10 s
```

Initialization at `0x55AA` deliberately starts with the same `200000000`-tick
delay active and the attempt counter zero. A reset therefore does not bypass the
wait; it restarts the nominal 10-second delay. The counter, delay flag, start
value, and duration all live in LocalRAM. No DataFlash/NvM persistence is involved.
A successful `27 02` clears the attempt counter as it sets the bootloader SA
unlock state to 2.

This policy applies only to failed bootloader **send-key** attempts. A
`DiagnosticSessionControl` request such as `10 02`, including an asynchronous
programming transition whose final response is lost during reset, does not
increment `FEBF2B57`.

## 3. ECUReset (`SID 0x11`)

`uds_ecu_reset @ 0x60C2` accepts only hardReset subfunction 1:

```text
11 01     normal positive response
11 81     perform the same reset with positive-response suppression
```

It requires:

- current session `02` (programming);
- SecurityAccess state `02` (unlocked);
- exact request length 2.

The locked path returns NRC `0x33`. Other subfunctions return NRC `0x12` and
malformed length returns NRC `0x13`.

`bootloader_reset_after_response @ 0x67DA` coordinates reset with transport
completion. If no diagnostic transmission is active it immediately enters the
non-returning reset path. Otherwise it sets pending-reset byte `0xFEBF2BBD`.

- A non-suppressed response is `51 01`; successful
  `Dcm_TpTxConfirmation @ 0x66BE` then enters the reset path.
- A failed Tx confirmation clears the pending request instead of resetting.
- A suppressed positive response reaches the no-transmit branch in
  `Dcm_TransmitResponse @ 0x674A`, which enters the reset path immediately.

`bootloader_hard_reset_wait @ 0x159E` disables interrupts, records low-level
boot state 3, and enters the non-returning hardware wait/halt sequence at
`0x1560`. This path is separate from the application event-9 shutdown/reset
coordinator described in `../diagnostics/application.md`.

## 4. CommunicationControl (`SID 0x28`)

`uds_communication_control @ 0x688A` is functional-only and requires extended
session. It accepts exactly:

```text
28 01 01
```

Control type `01` is the standard `enableRxAndDisableTx` value; communication
type `01` selects normal communication messages. Suppression (`28 81 01`) is
accepted. Other control types return NRC `0x12`; another communication type
returns NRC `0x31`.

The handler stores the subfunction at RAM `0xFEBF2BC3`, and
`communication_control_positive_response @ 0x6860` reads that byte only to emit
`68 01`. Those are the only two instruction references to this RAM byte. No
communication-mode state, CanIf mode API, or network-control callback consumes
the request. In this bootloader, the service is therefore a syntactic positive
acknowledgment rather than an implemented communication-state change.

## 5. ControlDTCSetting (`SID 0x85`)

`uds_control_dtc_setting @ 0x693A` is also functional-only and extended-session
only. It accepts exactly DTCSettingOff:

```text
85 02
```

Suppression (`85 82`) is accepted. Other subfunctions return NRC `0x12`.

The handler stores the request byte at RAM `0xFEBF2BC4`, and
`control_dtc_setting_positive_response @ 0x6910` uses it only to emit `C5 02`.
Those are the only two instruction references to the byte. There is no DTC
manager call or persistent setting change. Like `0x28`, this service acknowledges
the expected programming preamble without changing a local subsystem.

## 6. TesterPresent (`SID 0x3E`)

`uds_tester_present @ 0x4FF8` is functional-only. It accepts all three bootloader
sessions through the explicit allow-list `01 02 03` at `0x8EFD`.

Only exact subfunction bytes `00` and `80` are accepted:

```text
3E 00   -> 7E 00
3E 80   -> no positive response
```

Any other value returns NRC `0x12`; malformed length returns NRC `0x13`.

The handler stores the byte at `0xFEBF2ACC` solely for the response builder.
The current-session byte at `0xFEBF2B0E` is written only by diagnostic
initialization and explicit SessionControl completion; no bootloader inactivity
writer reverts it to default. Thus this implementation does not maintain an S3
session timer through TesterPresent. Generic transport activity still proceeds
normally, but `0x3E` has no additional keepalive side effect in the recovered
bootloader state.

## 7. RoutineControl common policy

`uds_routine_control @ 0x567E` scans five 12-byte records at `0x8F44`. All records
allow only StartRoutine (`01`). The service is physical-only, requires current
session `02`, and requires SecurityAccess state `02`.

The common ten-byte option record used by `10F0`, `10F1`, `10F2`, and `FF00` is:

```text
45 00 || address_be32 || length_be32
```

The complete ordinary wire request is therefore 14 bytes:

```text
31 01 RID_hi RID_lo 45 00 address_be32 length_be32
```

`10F3` has no option bytes and uses the four-byte request `31 01 10 F3`.
Unknown RIDs, incorrect format markers, or an address range in the wrong memory
class return NRC `0x31`. A busy asynchronous verifier returns NRC `0x22`.
Integrity/programming failures complete with NRC `0x72`.

## 8. Routines `0x10F0` and `0x10F1`

The compiled branches for `10F0` and `10F1` are identical. Both:

1. require option marker `45 00`;
2. validate operation bit 4 against the memory-access table;
3. require memory class 1, which selects only
   `0xFEBF0000..0xFEBF0FFF` in this image;
4. resolve authorization bit 0;
5. queue asynchronous embedded-address/length and CRC verification;
6. when payload authentication is configured, verify the AES-CMAC described in
   `../security/bootloader-payload-gate.md`;
7. set authorization bit 0 only after successful completion;
8. emit `71 01 RID_hi RID_lo`.

No instruction branches on `10F0` versus `10F1` after table lookup. They are
functionally aliases in this build, even if the two identifiers had distinct
names in the generator or update protocol that produced it.

## 9. Routine `0x10F2`: CodeFlash validation and marker programming

`10F2` uses the same option record and operation bit 4, but requires memory class
0. The permitted CodeFlash regions are:

| Data region | CRC/tag area | Marker programmed after success |
|---|---|---:|
| `0x10000..0x17DFF` | descriptor/tag ending at `0x17DFF` | `0x17E00` |
| `0x18000..0xFFDFF` | descriptor/tag ending at `0xFFDFF` | `0xFFE00` |

`routine_program_verify_task @ 0x5A04` waits for CRC and, where configured, CMAC
verification. It then resolves the selected region's marker address and calls
the flash programming path with four bytes:

```text
5A A5 A5 5A
```

The worker waits for asynchronous flash completion before returning
`71 01 10 F2`. A verification or programming failure returns NRC `0x72`.

This routine does not authorize the RAM callback used by `FF00`; it validates a
CodeFlash region and commits that region's four-byte validity marker.

## 10. Routine `0x10F3`: arm read-back comparison mode

`10F3` has no option record. On a valid request it:

1. sets the shared transfer state to `8`;
2. immediately emits `71 01 10 F3` (unless suppressed semantics prevent it);
3. leaves no asynchronous RoutineControl worker pending.

A subsequent class-0 RequestDownload sees state 8 instead of the ordinary idle
state. It validates memory-access operation bit 5, accepts a CodeFlash range,
and changes transfer state to 9. The next TransferData call changes state 9 to
10 and uses the alternate worker at `0x4CA2/0x4E92`.

That worker does not program the supplied bytes. `memory_compare_enqueue @
0x6C6C` records tester source, target CodeFlash address, and length;
`memory_compare_task @ 0x6C8E` compares up to 16 bytes per invocation. Only a
successful comparison advances the destination and remaining length. Mismatch or
worker failure eventually returns NRC `0x72`; normal blocks receive `76
blockSequenceCounter`.

Thus `10F3` arms a post-program read-back/compare transfer mode. It does not
itself erase memory, calculate a checksum, or expose CodeFlash contents.

## 11. Evidence grades

| Finding | Grade |
|---|---|
| service addressing masks, session bytes, accepted request shapes, and NRC branches | **Definitive** |
| SessionControl transition restrictions and queued positive response | **Definitive** |
| ECUReset waits for successful Tx confirmation unless response is suppressed | **Definitive** |
| `0x28` and `0x85` request bytes have no consumer beyond their response builders | **Definitive** |
| TesterPresent has no service-local timer and no inactivity writer changes current session | **Definitive** |
| `10F0` and `10F1` compile to identical RAM verification/authentication behavior | **Definitive** |
| `10F2` verifies CodeFlash and programs marker `5A A5 A5 5A` at `0x17E00/0xFFE00` | **Definitive** |
| `10F3` arms operation-bit-5 TransferData comparison against CodeFlash | **Definitive** |
| original generator/OEM names for `10F0..10F3` | **Unknown** |
