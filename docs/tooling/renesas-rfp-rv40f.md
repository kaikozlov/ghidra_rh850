# Renesas Flash Programmer RV40F host protocol

> **Scope:** Renesas Flash Programmer V3.24.00 `macos-arm64`
>
> **Document type:** external-source reverse engineering
>
> **Status:** recovered host protocol; target applicability bounded
>
> **Evidence source:** pinned `libRFP.dylib` and package resources
>
> **Canonical artifacts:** `renesas-rfp.lock.json`,
> `data/renesas_rfp_rv40f_commands.csv`,
> `data/renesas_rfp_rv40f_capabilities.csv`
>
> **Verification:** `tests/verify_renesas_rfp.py` (`make verify-rfp`)
>
> **Related:** [workflow](../WORKFLOW.md),
> [SecOC key lifecycle](../security/secoc/key-storage-and-lifecycle.md)

## Executive conclusion

The pinned Renesas Flash Programmer (RFP) package is now a substantially
complete primary source for the **host side** of the retained `BootRV40F`
serial-programming protocol. The Mach-O contains 61 `BootRV40F` symbols and a
complete static census recovers **52 distinct command IDs** covering connection,
clock/baud negotiation, memory operations, protection/authentication, option
configuration, area discovery, OCD state, and ICU lifecycle handling.

The ordinary request envelope is:

```text
01 || length_be16 || command || payload || checksum || 03
```

where `length = 1 + payload_length` and the checksum is the two's-complement
byte sum of `length_be16 || command || payload`. `SendRecvFrame` requires the
response to start with `0x81`, bounds the response length below `0x402`, obtains
the remaining bytes, and validates the packet against the request command.
`ProcessCommand` additionally performs an exact response-payload-length check
before copying returned data.

The ICU-specific result is now stronger than the earlier six-command survey.
Across the **complete retained command-constructor surface**, there is no
dedicated RV40F security/configuration request shaped as a SHE M1/M2/M3 package
(`16 + 32 + 16 = 64` bytes), and no named or structurally recovered command that
loads an arbitrary 16-byte key into an ICU slot. The nearby large security
requests have different meanings and shapes: `CheckPassword` is
`selector || 32 || 32` (65 bytes), short/long ID operations are 16/32/96-byte
authentication or identity fields, and `WriteConfig` is `be32 || 16` (20
bytes). The legacy `SetICUM` path is a fixed 20-byte option record split into
4-byte and 15-byte commands.

That negative is deliberately scoped. Generic write/data-transfer commands can
transport arbitrary program bytes to an allowed target address range; this is
not evidence of a dedicated ICU key-provisioning primitive. Nothing here proves
which commands an R7F701381/P1M-E mask ROM advertises, nor that standard RFP is
the manufacturing path used for Toyota/Denso SecOC provisioning.

The Sienna application has a separate, directly recovered key-update service:
RoutineControl RID `0x1010` drives MainPE ICU command 8 with a SHE-compatible
M1/M2/M3 → M4/M5 envelope. That application service is **not** any of the RFP
serial commands below.

## 1. Pinned source and family boundary

The analyzed distribution identifies itself as:

```text
Renesas Flash Programmer CLI V1.17
module V3.24.00.000
package V3.24.00
release 1 July 2026
platform macos-arm64
```

Exact package hashes, function virtual addresses/body hashes, embedded-data
prefixes, and the completed analysis scope are pinned by
`renesas-rfp.lock.json`. Verify the local licensed package with:

```bash
make verify-rfp
```

`Devices.xml` exposes generic `RH850`, `RH850/E2x`, and `RH850/U2x` entries but
contains no P1M-E/R7F701381-specific device record. The library also retains a
separate `BootRH850Gen2` implementation. Therefore `BootRV40F` is strong host
protocol evidence for the generic/older RH850 route, **not** proof that the
analyzed Toyota P1M-E selects it.

The package's executable-resource inventory does not supply a hidden P1M-E
agent. All 68 `Firmwares/*.bin` images identify as SEGGER probe firmware;
explicit target-resident resources are DA/RA-family files; and the only shipped
secure-provisioning payload is the RA6B1 image used by `BootRATZ_B`. There is no
RH850/RV40F/P1M/ICU-named target resource or `BootRV40F::DownloadImage` path.

## 2. Wire protocol and complete command census

### 2.1 Common request/response behavior

`ProcessCommand @ 0x19C94` builds the normal request:

```text
01 || length_be16 || command || payload || checksum || 03
```

with:

```text
length   = 1 + payload_length
checksum = -sum(length_be16 || command || payload) mod 256
```

After the normal request succeeds, `ProcessCommand` uses a command-matched
control/receive frame and requires the returned payload length to equal the
caller's expected length before copying it.

`SendRecvFrame @ 0x1B37C` is the lower-level packet primitive. It requires a
request of at least six bytes, receives the first six response bytes, checks
`response[0] == 0x81`, parses a big-endian length below `0x402`, receives any
remaining response bytes, and calls the common packet validator using the
request command.

Several older/high-throughput methods construct the same framing manually
rather than calling `ProcessCommand`; the complete census therefore covers both
paths. `WriteData`, `VerifyData`, `Read`/`ReadEX`, and the RX-style configuration
methods also use command-specific **data-phase** frames after their setup
request. `AbortSendData` is a separate `0x81` control frame and is not counted as
one of the 52 ordinary request command IDs.

### 2.2 Command families

The exact per-command request length/layout, response length/layout, host method,
calling task, preconditions, result handling, and confidence are in
`data/renesas_rfp_rv40f_commands.csv`. The recovered command-ID set is:

| Family | Commands |
|---|---|
| inquiry / memory | `00 10 12 13 14 15 16 18 1C` |
| protection / auth / option | `20 21 22 23 26 27 28 29 2A 2B 2C 2D 2E 30` |
| clock / identity | `32 34 36 38 3A 3C` |
| configuration | `48 49 4A 4B 4D 4E 4F 50 51 52 53 54 56 57` |
| ICU lifecycle/options | `6E 6F 70 71 74 75` |
| password / CCC config | `78 79 7A` |

High-signal layouts include:

| Command | Host method | Recovered shape |
|---:|---|---|
| `0x38` | `GetDeviceType` | response 24 = `TypeCode[8]` + four BE32 frequency-range fields |
| `0x3A` | `GetSignature` | response 58 or 72 bytes, parsed into device/memory geometry |
| `0x30` | `CheckIDAuth` | request 16 or 32 authentication bytes |
| `0x78` | `CheckPassword` | request 65 = selector + 32 + 32 |
| `0x79/0x7A` | `WriteConfig` / `VerifyConfig` | request 20 = BE32 selector/address + 16 bytes |
| `0x22/0x2D` | `SetLockBit` / `SetOTP` | request 98-byte option structures |
| `0x26/0x27` | set/get option byte | 16/17/32-byte layout variants |
| `0x53/0x54` | area discovery | count + 17-byte per-area descriptor |
| `0x6E/0x6F` | ICU-S option | four-byte set/get value |
| `0x70` | `ValidateICU_S` | no request payload |
| `0x71` | `CheckICUMode` | one-byte probe |
| `0x74/0x75` | legacy `SetICUM` | 15-byte main + 4-byte auxiliary |

Program/write data are intentionally distinguished from configuration
primitives. Command `0x13` starts with an 8-byte start/end range and then
accepts raw data chunks under command `0x13`; `GetWriteDataSize` selects `0x400`
or `0x4000` depending on driver mode. Command `0x16` similarly carries verify
data. Those generic memory streams can naturally contain arbitrary byte
patterns, including 16 or 64 bytes, but they are not slot/key commands.

## 3. Connection and setup state machine

The retained host path separates **generic mode entry**, **RV40F connection**,
**baud/auth/signature setup**, and **clock negotiation**.

### 3.1 Generic serial entry → RV40F selection

`Task_Connect_Generic::_RunInternal @ 0xAAEF4` obtains the configured serial
entry selector from the driver/session, then calls
`_RunModeEntry_SerialBoot @ 0xAB578` before any RV40F command is issued.
`_GetModeEntryPattern @ 0xABD70` chooses a fixed `uint16` mode-entry pattern from
the configured device/mode/interface tuple and the task delegates that pattern
to the driver's virtual `RunModeEntry` implementation (`Driver_COM`,
`Driver_E1E2`, `Driver_JLink`, `Driver_USB`, or wrapper implementations retain
that named method).

After a successful driver mode-entry operation, the host performs a
selector-dependent serial transition:

| Entry selector | Host action after mode-entry pattern |
|---:|---|
| `1` | set 9600 baud → wait 1 ms → `BootGeneric::ZeroTransmission(..., true)` |
| `2` | set 9600 baud → wait 1 ms → `BootGeneric::ZeroTransmission(..., false)` |
| `3` | set 10000 baud |
| `4` | no additional baud/zero-transmission operation in this routine |
| `5` | set 250000 baud |
| other | return the generic mode-entry error path |

For driver-kind values `0x0A..0x0D`, the routine also obtains a driver status
structure after `RunModeEntry` and rejects a zero status byte before continuing.
The host then calls `BootGeneric::GetBootCode`; `_RunInternal` stores that code
and dispatches through its family jump table, reaching `_ConnectRV40F @
0xAB91C` for the retained RV40F family.

This is the exact **host orchestration** around mode entry. The selected
`uint16` pattern is configuration/interface dependent, and the concrete reset
pin/boot-pin electrical behavior lives behind each driver's `RunModeEntry`
implementation. Without a P1M-E session we therefore do not assign one of
these generic patterns/selectors to R7F701381.

`_ConnectRV40F` immediately executes:

```text
GetDeviceType (0x38)
```

The 24-byte response is important for later capability decisions:

- bytes `0..7` are copied as an 8-byte `TypeCode`/capability vector into
  `DeviceInfo+0x30`;
- bytes `8..23` are four big-endian 32-bit fields copied into the frequency
  range information structure.

If device information is not already loaded, `_ConnectRV40F` materializes the
8-byte vector in `DeviceInfo`; if a cached device record exists it compares the
new value against it. This is the origin of the capability word decoded in §4.
It is **not** sourced from `GetSignature`.

### 3.2 `Task_SetupBaudrate_RV40F`

The classic setup task performs, subject to driver/config branches:

```text
optional SetBaudrate (0x34)
→ host baud reconfiguration / delay
→ Inquiry (0x00)
→ GetIDAuth (0x2C)
→ temporary long timeout
```

If authentication is required, it obtains the configured ID and calls
`CheckIDAuth (0x30)`. The task retries the specific target result `0xE1000007`
up to **10** times and emits warning `0x83000001` while retrying; other errors
fail normally.

If the target does not require that ID challenge, the task calls
`GetSignature (0x3A)` and `_SetSignatureToDeviceInfo`. That parser consumes the
58/72-byte signature to recover device/memory geometry while consulting the
already-populated 8-byte capability vector for layout decisions.

Additional capability-dependent setup then includes:

- `0x1107` → `GetVersion (0x3C)` / `GetTMemory (0x4F)` paths;
- `0x1106` → `CheckICUMode (0x71)`, whose successful result is cached in
  `DeviceInfo` for later option-writing decisions.

### 3.3 RV40F2 area-discovery variant

`Task_SetupBaudrate_RV40F2::Run @ 0xC2E6C` has the same broad baud → inquiry →
ID-auth structure, but its non-authenticated discovery path uses:

```text
GetAreaNum (0x53)
→ GetAreaInfo (0x54) for each area
```

instead of the classic signature-based memory-geometry path. Its ID-auth retry
rule is the same bounded ten-attempt treatment of `0xE1000007`.

### 3.4 Clock/password setup

`Task_SetupClock_RV40F::Run @ 0xBFC9C` consults capability `0x1002`. On that
format family it obtains derived widths `0x1211` and `0x1212` (32 bytes each in
the recovered normal case), obtains the corresponding values, and performs
`CheckPassword (0x78)` with selector 1 and then the second configured selector.
One selector-2 failure path is downgraded to warning `0x83000003` rather than
being treated as a generic fatal error.

The task then calls `SetFrequency (0x32)`, delays briefly, stores the returned
negotiation values, and updates host driver timing/baud state.

This is a **host state machine** only. It does not establish the exact physical
reset pin timing or mask-ROM behavior of the P1M-E without a target capture.

## 4. Device-type capability word

`UtilityRV40F::GetRV40FInfo @ 0xC2528` accepts a vector only when its length is
exactly **8 bytes**, loads it as one packed 64-bit word, and projects internal
keys from that word. The complete recovered projection is in
`data/renesas_rfp_rv40f_capabilities.csv`.

This corrects a tempting but wrong interpretation: feature key `0x1106` does
**not** originate in the `0x3A GetSignature` payload. The 8-byte word originates
in the first eight bytes of `0x38 GetDeviceType` and is copied into
`DeviceInfo+0x30`; the signature parser later consults it.

Important normal-format projections are:

| Key | Structural interpretation |
|---:|---|
| `0x1001` | `(low_byte & 0xF0) == 0x20` |
| `0x1002` | `low_byte == 0x11` |
| `0x1003` | derived layout value: 12, 11, or 10 |
| `0x1101` | bit 16 |
| `0x1102` | bit 17 |
| `0x1103` | bit 30 |
| `0x1104` | bit 24 |
| `0x1105` | bit 8 |
| `0x1106` | `bits[50:48] == 1 or 4` |
| `0x1107` | bit 54 |
| `0x1108` | bit 9 |
| `0x1109` | bit 51 |
| `0x110A` | bit 10 |

Selected derived-size keys are:

| Key | Structural interpretation |
|---:|---|
| `0x1201` | `1 << bits[43:40]` |
| `0x1202` | `1 << bits[46:44]` |
| `0x1203` | ID width: 32 if low byte is `0x11`, else 16 |
| `0x1204` | option width: 16 for `0x2x` family, else 32 |
| `0x1205` | 32 for `0x11`; else 8 if bit51; else **20** when bits48..50 == 2; else 0 |
| `0x1210` | 1024 when bits48..50 == 1; 2048 when == 4; else 0 |
| `0x1211/0x1212` | 32 when low byte == `0x11`, else 0 |

A separate phase-2 path is selected when the low byte is `0x30`. In that path
`0x1001=1`, `0x1002=0`, `0x1003=14`, `0x1108=1`, `0x1203=16`, and the other
recovered `0x110x`/derived fields default to zero.

These keys are internal RFP structural capabilities. Human-readable Renesas
enum names were not retained, so the repository uses bit/field definitions and
observed call-site roles rather than assigning speculative silicon feature
names.

## 5. ICU option/lifecycle behavior

### 5.1 Extended option dispatch

`SetOptionByteEx @ 0x1C164` receives two capability-derived booleans corresponding
to `0x1002` and `0x1109` and selects four layouts:

- `0x1002 && 0x1109`: send `0x6E` with four bytes from the extended option
  record, then command `0x26` selector 3 with 16 option bytes;
- `0x1002 && !0x1109`: use command `0x26` selectors 2 and 3 for two 16-byte
  halves;
- `!0x1002 && 0x1109`: send only `0x6E` with four ICU-S option bytes;
- `!0x1002 && !0x1109`: use the legacy `SetICUM` path.

Thus `SetICUM` is specifically a legacy fallback, not the universal ICU-S
configuration method.

### 5.2 Exact `SetICUM` structural record

On the legacy path the derived `0x1205` width is 20 bytes. `SetICUM @ 0x1C5AC`
uses that 20-byte source record as follows:

```text
source[0]      unused by SetICUM
source[1..3]   three flag-like bytes, normalized: > 0xEF -> 0xFF, else 0x00
source[4..7]   raw u32 field A
source[8..11]  raw u32 field B
source[12..15] raw u32 field C
source[16..19] raw u32 auxiliary field
```

Wire order:

```text
command 0x75 payload (4):
    source[16:20]

command 0x74 payload (15):
    normalized(source[3])
    source[8:12]
    source[12:16]
    source[4:8]
    normalized(source[2])
    normalized(source[1])
```

The package contains no device XML, retained enum, or nearby string that gives
those four integer fields or three flags trustworthy semantic names. They are
therefore kept **structural**. This pass does establish that the record is not
`slot || AES-128 key`, does not contain a recovered slot selector, and is not a
64-byte M1/M2/M3 envelope.

### 5.3 `CheckICUMode` and `ValidateICU_S`

`CheckICUMode @ 0x1D688` is gated by capability `0x1106` during classic setup.
Its exact host algorithm is:

```text
send 0x71 payload FF
if result == E1000010:
    send 0x71 payload 00
    if success: output_mode = 00
else if first request succeeds:
    output_mode = FF
otherwise:
    return the error
```

The successful mode is cached in `DeviceInfo`; later option-read/write tasks
consult that cached state.

`ValidateICU_S @ 0x1D5E8` is simpler: it sends payload-free command `0x70` once
and returns the packet result. It contains **no internal retry loop**, no key
payload, and no independently recovered persistent-state write in the host.
`Task_WriteOption_RV40F::_WriteOptionRH850` invokes it from the high-level ICU-S
security-option path when the cached state says validation is still required.
The CLI documents that high-level option as `-fo flags icus` / “Enable ICU-S.”

This proves the host precondition/sequence, not the target-side effect. Static
RFP code alone cannot establish whether validation burns an irreversible
lifecycle bit, what the mask ROM checks internally, or whether a specific
P1M-E permits the command.

`SetICUSOptionByte @ 0x1C4DC` and `GetICUSOptionByte @ 0x1CA90` remain valid
four-byte host primitives. The direct exported helpers have no recovered
ordinary internal code callers; `SetOptionByteEx` independently constructs the
same `0x6E` four-byte command in its extended-option branches. The documented
high-level ICU-S enable transition concretely reaches `ValidateICU_S`, not a
secret key-load operation.

## 6. Complete key-provisioning negative

The completed 52-command census allows a stronger scoped conclusion than the
old symbol-name search.

For the security/configuration commands (`0x20..0x30`, `0x48..0x4F`,
`0x56/0x57`, `0x6E..0x75`, `0x78..0x7A`):

- no fixed request payload is 64 bytes;
- no command has the SHE `M1[16] || M2[32] || M3[16]` shape;
- no ICU command accepts a standalone arbitrary 16-byte key plus slot selector;
- `0x78` is explicitly a password check with `1 + 32 + 32` bytes;
- `0x79/0x7A` are config write/verify with `4 + 16` bytes;
- `0x74/0x75` consume the structural 20-byte legacy option record above;
- the retained `BootRV40F` symbol surface has no `SetKey`, `LoadKey`,
  `KeyUpdate`, or provisioning-image download method.

This is a **complete negative for dedicated key provisioning in the retained
standard RV40F host command surface**, not a universal negative for the silicon.
It does not exclude:

- generic flash writes carrying arbitrary bytes to an address that a particular
  mask ROM exposes;
- an undocumented command omitted from this library build;
- a manufacturing-only or target-resident provisioning program distributed
  separately;
- Toyota/Denso-specific software or application diagnostics;
- a target-internal key derivation/provisioning action behind a structurally
  ordinary option command.

The Sienna's recovered DID-`0x1010` command-8 path remains the only static path
in the current project that actually has the SHE M1/M2/M3 shape.

## 7. Remaining dynamic boundary

The useful static RFP questions from the earlier roadmap are now closed. The
remaining RFP/P1M-E questions require a target or a legitimate capture:

- Does R7F701381/P1M-E select this `BootRV40F` family after mode entry?
- What exact 24-byte `GetDeviceType` response and 8-byte capability word does it
  return?
- Which of the 52 commands are accepted, rejected, or lifecycle-gated?
- What target-side state transition does `ValidateICU_S` cause, and is it
  reversible?
- Does a manufacturing-only provisioning path exist outside this standard RFP
  distribution?

The shipped RFP CLI documentation includes a generic all-`FF` ID-code example,
and retained generic configuration strings use `UserID=0xFFFFFFFF`. Those facts
support an all-`FF` `CheckIDAuth` value as a reasonable **probe hypothesis**,
not as a recovered R7F701381/P1M-E blank-ID state. The analyzed distribution has
no specific P1M-E device record that closes that transfer. Acceptance or
rejection must therefore be treated as target observation (CORR-092).

Until those are observed, host support must not be promoted into a claim about
P1M-E mask-ROM capabilities.
