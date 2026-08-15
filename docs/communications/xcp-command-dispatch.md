# Application calibration-command dispatch

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence source:** firmware-static
>
> **Confidence:** verified disclosure + direct RAM-write primitives; bounded
> downstream write impact
>
> **Canonical artifact:** `data/recovered_callback_tables.csv`
>
> **Verification:** `tests/verify_function_discovery.py`,
> `tests/verify_xcp_security.py`, `tests/verify_xcp_shadow_write_live.py`,
> `tests/verify_xcp_window_mpu_permissions.py`,
> `tests/verify_exploit_followups.py`, `AssertXcpShadowWriteBoundary.java`,
> `AssertRecoveredCallbackTables.java`, `AssertFunctionDiscoveryFloor.java`

## Result

The application contains a seven-entry command table at CodeFlash `0x2B3F0`.
`FUN_00097160` walks exactly seven eight-byte records, compares the request
selector with byte zero, loads the little-endian callback from record offset
four, and invokes it through the computed `jarl r29,lp` at `0x971A2`. The
handler bodies and their shared response builder match an XCP-shaped
calibration command family. That protocol identification is recovered from the
firmware behavior; no OEM symbol or external specification is used as naming
evidence.

The same firmware path exposes an unauthenticated memory disclosure on the
paired CAN `0x7F7` request / `0x7F8` response route. The configured generic
command map has no GET_SEED (`0xF8`) or UNLOCK (`0xF7`) callback. After CONNECT
(`0xFF`), SET_MTA (`0xF6`) accepts a tester-supplied 32-bit address without an
authorization check and the custom UPLOAD command (`0xF5`) returns one to seven
bytes from permitted LocalRAM. Independently, configured standard SHORT_UPLOAD
(`0xF4`, callback `0x81A2E`) accepts a one-to-seven-byte length plus a tester
32-bit address in the same request and directly returns the bytes after the
same LocalRAM/exclusion checks; it does not require a prior SET_MTA. The `0xE4`
page-copy command first makes
CodeFlash `0x10000..0x17DEF` readable by copying it to permitted LocalRAM
`0xFEBF7C00..0xFEBFF9EF`. Repeated uploads therefore recover 32,240 CodeFlash
bytes exactly.

| Selector | Pointer field | Handler | Body bytes | Structural role |
|---:|---:|---:|---:|---|
| `0xFB` | `0x2B3F4` | `0x9729A` | 74 | response builder |
| `0xFA` | `0x2B3FC` | `0x972FA` | 96 | indexed-identifier response |
| `0xF5` | `0x2B404` | `0x97432` | 100 | bounded upload response |
| `0xF3` | `0x2B40C` | `0x97546` | 168 | bounded checksum response |
| `0xEB` | `0x2B414` | `0x975EE` | 122 | page-state writer |
| `0xEA` | `0x2B41C` | `0x97668` | 104 | page-state reader |
| `0xE4` | `0x2B424` | `0x976F4` | 106 | guarded page-copy operation |

Every target begins at an independently decoded function boundary, has a
bounded return, is not an alternate entry into another function, and is pinned
by exact body size and SHA-256 in the canonical CSV. The handlers converge on
the response helper at `0x9724E`, which builds an eight-byte response in RAM at
`0xFEBE5E94`.

## Security path

All request frames are eight bytes. This is the minimal firmware-static proof
sequence; the final request is repeated, using a shorter length for the last
fragment.

| Operation | Request bytes | Effect |
|---|---|---|
| CONNECT | `FF 00 00 00 00 00 00 00` | sets the protocol connected state |
| copy page | `E4 00 00 00 01 00 00 00` | copies CodeFlash `0x10000..0x17DEF` to RAM |
| SET_MTA | `F6 00 00 00 00 7C BF FE` | selects RAM `0xFEBF7C00` (little-endian) |
| UPLOAD | `F5 07 00 00 00 00 00 00` | returns seven bytes and advances the MTA |

The `0xF5` range checker permits LocalRAM `0xFEBE0000..0xFEBFFFFF` except five
inclusive intervals encoded at `0x293F4`:

- `0xFEBE0000..0xFEBE37FF`
- `0xFEBE5030..0xFEBE529B`
- `0xFEBF0288..0xFEBF13CB`
- `0xFEBF4958..0xFEBF4B33`
- `0xFEBF6C00..0xFEBF78DF`

That leaves 107,924 readable RAM bytes. The checker rejects requests crossing
an exclusion and rejects address wraparound. The page-copy destination lies
outside every exclusion.

Standard SHORT_UPLOAD (`0xF4`) independently exposes the same LocalRAM allow-set.
Its configured request length is eight bytes; byte 1 selects a read length of
1..7, byte 3 must be address-extension zero, and bytes 4..7 are the
little-endian source address. `application_command_05_callback @ 0x81A2E`
explicitly rejects 32-bit address wrap, calls `0x81FBA -> 0x971D2` to reject
intersection with the same five exclusion intervals, then enforces
`0xFEBE0000..0xFEBFFFFF` before copying source bytes into response bytes 1..7.
Thus `F4` is a second unauthenticated direct RAM-read primitive that does not
need a prior SET_MTA to select its source address; it does **not** expand the
readable address set beyond the 107,924 bytes already exposed by F5/DAQ. The
outer protocol dispatcher still requires a successful CONNECT on the same
logical channel before either standard or custom memory commands execute;
CONNECT itself has no GET_SEED/UNLOCK prerequisite in this image.

For example, an eight-byte `F4 01 00 00 28 6D BE FE` request selects one byte at
`0xFEBE6D28`. Firmware-static evidence establishes the parser and read path, not
external gateway reachability.

The copied interval does not contain the bootloader secrets at `0xBFD8` and
`0xBFE8` or the application SecurityAccess secret at `0x20840`; this finding
does not claim direct key disclosure.

### DAQ commands provide event-driven RAM telemetry, not a reverse write path

The lower command map also implements a complete XCP-shaped DAQ subset:

| Opcode | Callback | Recovered role |
|---:|---:|---|
| `E3` | `0x81794` | clear DAQ list |
| `E2` | `0x813CC` | set DAQ pointer |
| `E1` | `0x81424` | write one DAQ entry |
| `E0` | `0x8152A` | set DAQ-list mode/event/prescaler |
| `DE` | `0x815EA` | start/stop one DAQ list |
| `DD` | `0x816C8` | synchronized DAQ start/stop |
| `DA/D9/D8/D7` | `0x81870/0x818AE/0x81824/0x818E2` | DAQ capability/list/event queries |

The configured geometry is four DAQ lists, four ODTs per list, and seven
one-byte entries per ODT: **112 source pointers** total. `WRITE_DAQ` requires an
eight-byte CTO with bit-offset `FF`, element size `01`, address extension `00`,
and a tester-controlled 32-bit address. The address must lie in
`0xFEBE0000..0xFEBFFFFF` and pass the same five exclusion intervals used by the
UPLOAD path. `SET_DAQ_LIST_MODE` rejects any mode byte with mask bits `0x33`
set, requires a valid event ID, a nonzero prescaler, and zero priority. Four
event slots are configured as IDs `0/1/2/3`; the periodic event worker reloads
each after two eligible communication-manager invocations. The absolute
foreground-tick duration remains unsupported, so no wall-clock DAQ rate is
claimed.

The runtime data direction is pinned at the instruction level. `WRITE_DAQ`
stores the accepted tester address into the pointer table at `FEBE4CF0`. The
periodic sampler then executes:

```text
0x812C2  sld.w  0[ep], ep          # load configured source pointer
0x812CE  sld.bu 0[ep], r18         # read one byte from that address
0x812D0  st.b   r18, ...           # store only into local DTO staging
```

The sampled DTO is queued through `0x81E58`, drained through `0x81CAC`, and
transmitted by configured callback `0x8206C`, which ORs class `0xF800` before
`application_canif_transmit`; the special route resolves to CAN `0x7F8`. A
read-only live-project assertion finds exactly four direct references to the
DAQ pointer-table base: initialization, list clearing, `WRITE_DAQ`, and the
sampler. No reverse store through the configured source pointer is recovered.
Thus this DAQ surface is a **firmware-static unauthenticated event-driven
LocalRAM disclosure primitive**, not a STIM-style memory-write primitive in this
calibration.

This is directly useful to the remaining dynamic steering discriminator if the
physical `0x7F7/0x7F8` route is reachable. The already-recovered d/q reference
bytes at `FEBE6D28/6D2A` and staged TSG3 compare bytes at
`FEBE38A2/38A4/38A6` all pass the DAQ address validator. Configuring adjacent
byte entries can therefore observe those multi-byte states without patching the
motor-control loop. `exploit/followups/xcp_daq_probe.py` now reproduces the
exact volatile list-0 configuration and has named observation profiles for this
actuation discriminator plus recent WDBI/BA/async state. It never implements
`DOWNLOAD` or `MODIFY_BITS`, and live mode remains isolated-bench/F181 gated.
Physical gateway/connector reachability remains unobserved; this does not turn
the bounded 32 KiB shadow writer below into an actuation or execution primitive.

### Generic write commands are real direct RAM writes

The same unauthenticated generic command map contains standard XCP-shaped
`DOWNLOAD` (`0xF0`, callback `0x80F12`) and `MODIFY_BITS` (`0xEC`, callback
`0x80FD8`). These are not merely configuration records for a hypothetical
calibration writer.

`DOWNLOAD` obtains the current MTA from `FEBE4FF4`, accepts 1–6 tester bytes in
an eight-byte CTO, validates the complete interval against both LocalRAM
`0xFEBE0000..0xFEBFFFFF` and the narrower write window
`0xFEBF7C00..0xFEBFFBFF`, then directly stores each tester byte to `MTA+i`.
After success it advances MTA to `end+1`. Repeated six-byte-or-smaller requests
therefore cover any contiguous portion of the entire 32 KiB window, including
the complete window from start through `0xFEBFFBFF`.

`MODIFY_BITS` uses the same MTA and write-window validation, requires word
alignment, and performs an in-place 32-bit masked read-modify-write. Neither
command has a GET_SEED/UNLOCK prerequisite because those command slots are not
configured in this image.

That is a firmware-static **unauthenticated arbitrary 32 KiB LocalRAM write
primitive**, with important impact bounds. First, the hardware MPU itself
marks this window **supervisor-executable**: MPU region-1 bounds at CodeFlash
`0x3181C/0x31820` are exactly `FEBF7C00..FEBFFBFC`, and the context attribute
bytes `0x31898 = 0xB8` (context 0: supervisor R/W/X) and `0x318D8 = 0xA8`
(context 1: supervisor R/X) prove execution is not hardware-denied. Both
attributes use ASID 0/G=0; reset startup explicitly clears ASID to 0, MPU init
enables protection in supervisor mode with `MPM=3` (MPE+SVP), and the
application MPU loader selects context 0 initially (`0x3180F=0`), context 1 for
foreground/flash-end entry (`0x31810=1`), and context 0 for CAN1 Tx/Rx ISR
wrappers (`0x31811=0`). MPAT bit semantics are those in the Renesas P1M-E
manual (`REFERENCE/r01uh0585ej0120_manual.pdf`, Table 3.49). The
Ghidra LocalRAM memory block's `execute=false` is **analysis metadata about
the imported program database, not a hardware security bound** (see
CORRECTIONS). Second, an exhaustive live-project
census over all defined function instructions finds exactly three direct
references into `0xFEBF7C00..0xFEBFFBFF`, all `WRITE` references to the base
`FEBF7C00` (`0x142E`, `0x62652`, `0x976E4`). It finds zero function-owned direct
`READ`, `PARAM`, call/jump, or other references and zero function entries inside
the window. The four recovered executable-code materializations of the actual
window base are also pinned: startup clear `0x1426`, application page copy
`0x6263E`, XCP range/translation helper `0x974D0`, and XCP E4 copy `0x976D0`.
A nearby apparent alias at `0x6266E` is a separate 64-byte application-info
initializer rooted at `FEBF7BB0`; its exact loop stops at `FEBF7BEF`, 16 bytes
below the XCP window. The current static graph therefore does **not** establish a
callback pointer, executable alias, persistent-flash consumer, or motor-control
consumer for attacker-written bytes. Runtime-only aliasing or computed consumers
remain a bounded unknown; the absence of direct xrefs/materialized consumers is
not a universal non-use proof.

The security conclusion is therefore corrected and still bounded:
**write capability is verified, and the window is supervisor-executable by MPU
configuration, but no control-transfer consumer is recovered** — so this
remains a write primitive, not a claimed RCE.
`exploit/followups/xcp_shadow_write_plan.py` now represents the verified
SET_MTA/DOWNLOAD wire primitive as an offline-only planner/simulator. It has no
live transport path; that preserves the distinction between proving the write
primitive and claiming an as-yet-unrecovered consumer or actuation effect.

Firmware-static evidence proves CAN1 acceptance and response construction, not
that an external vehicle gateway or diagnostic connector forwards CAN
`0x7F7/0x7F8`. The transport also closes the obvious short-frame stale-tail
avenue: `0x81FE4` accepts only nonzero payload lengths up to eight bytes, clears
the eight-byte receive staging slot before copying the supplied bytes, and the
custom handlers require an exact eight-byte request before consuming their
fields. Standard commands retain their own configured request-length checks.
Any live confirmation belongs on an isolated bench and should exercise only the
read chain. The default-plan/simulation tool
[`../../exploit/followups/xcp_read_probe.py`](../../exploit/followups/xcp_read_probe.py)
operationalizes that bounded proof, requires an F181-bound isolated bench for
live mode, and implements no generic write command. Its default CodeFlash
acquisition path uses CONNECT + `E4` copy + address-explicit `F4 SHORT_UPLOAD`,
so each read selects its own source without relying on prior MTA state; the older
`SET_MTA + F5` sequence remains an explicit comparison mode. A separate bounded
`--ram-address/--ram-length` mode uses CONNECT + F4 only and mirrors the exact
five firmware exclusions, making the known `FEBE6D28/6D2A` and
`FEBE38A2/38A4/38A6` observation bytes directly probeable if the physical route
is confirmed.

## Reproducibility and remaining boundary

`SeedRecoveredCallbackTables.java` validates the table bytes, selector order,
dispatcher instructions, target hashes, and boundaries before creating the
seven functions and `USER_DEFINED` pointer references. A clean four-stage
rebuild therefore recovers them without interactive edits. The asserting floor
also covers the other firmware-proven indirect tables and rejects any literal
call whose destination lacks an exact function entry.

The nearby 60-pointer array at `0x27C88..0x27D77`, including the wrapper-shaped
targets referenced by `0x27D08..0x27D54`, is intentionally not seeded. Its
bytes are valid CodeFlash pointers to entry-shaped runs, but this image has no
referenced executable walker or computed-call consumer. The negative is now
stronger than "unreferenced": the descriptor array at `0x27E94` has exactly six
recovered accessors, and every one consumes `desc+0x04` (bounds-checked
`32x4` table at `0x27C08`) plus code slots `+0x10/+0x14/+0x18/+0x1C/+0x20` —
never `desc+0x0C`, which is where `0x27C88` sits. The sole live xref to
`0x27C88` is a single DATA word at `0x27D84`, the canonical data-reference
graph contains no function-owned reference, and all 60 target pointer
literals occur only inside the table itself. Prologue shape and pointer shape
alone do not prove dispatch; the cluster stays `unresolved-reviewed` in
`data/outside_function_candidates.csv` as a bounded structural negative, with
no consumed selector path in this calibration.
