# Application receive I-PDU and COM signal map

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS COM-001, COM-002
>
> **Canonical artifacts:** `data/application_rx_map.csv` (final map), `data/application_rx_signal_evidence.csv` (extraction evidence)
>
> **Verification:** `tests/verify_application_receive.py`
>
> **Related:** [application-tx](application-tx.md), [firmware-architecture](../architecture/firmware-architecture.md)

This report completes the statically recoverable application receive map for
China-market Sienna EPS firmware `8965B4512000`. It covers all **47 normal
application Rx I-PDUs** and all **242 configured COM receive signals**.

Addresses are CodeFlash virtual addresses unless they begin with `0xFEBE`. The
machine-readable map is `data/application_rx_map.csv` (one row per signal with
repeated parent-PDU columns). Recovered extraction parameters come from
`data/application_rx_signal_evidence.csv` (Ghidra exporter
`ExportApplicationRxSignalEvidence.java`). Independent raw checks are in
`tests/verify_application_receive.py`; `AssertApplicationReceiveMap.java`
audits destination WRITE / consumer READ ownership under `make verify-processor`.

## 1. Executive summary

| Class | Count | Inclusion |
|---|---:|---|
| Normal application Rx I-PDUs | 47 | **In scope** — acceptance rules 0..46 and COM PDUs 6..52 |
| Configured COM receive signals | 242 | **In scope** — generated signal IDs 58..299 |
| SecOC envelopes | 6 | **Also in the 47** — flagged `secoc_envelope=yes`; SecOC verify is additional to COM |
| Diagnostic/special acceptance | 4 | **Excluded** — `0x7A1`/`0x777`/`0x7A0`/`0x7F7` use separate demux classes |
| CAN `0x344` | 0 | **Absent** from acceptance, descriptors, and the CSV |

Static extraction/classification closure (this calibration):

| Evidence class | Signals |
|---|---:|
| extracted bitfield | 131 |
| extracted group/opaque bytes | 14 |
| configured ID omitted by an otherwise-active PDU handler | 93 |
| configured ID on no-COM-unpacker SecOC PDU (`0x00F`) | 3 |
| configured ID on ordinary no-COM-unpacker PDU (`0x2E8`) | 1 |

Thus all **242/242** configured Rx signal IDs are classified. The final 97 are
negative COM-extraction results, not guessed bit layouts: the stock firmware has
no signal-level extraction call for those IDs. This does **not** claim that every
wire bit in the containing PDU is globally unused by direct-buffer or security
logic.

No OEM message names, physical scaling, or DBC field names are assigned. Signal
numbers are the generated COM IDs present in this image.

## 2. Receive chain

```text
EIINT 187 / CAN1 RX
  -> application_can1_rx_interrupt_body     @ 0x82E40
  -> application_can_normal_rx_demux        @ 0x80006
       maps acceptance index n -> application PDU ID 6+n
  -> application_pdu_rx_router              @ 0x80C44
  -> (optional SecOC ingress for six envelopes) @ 0x8DC64
  -> application_com_rx_indication          @ 0x7C640
       copies frame into COM buffer FEBE4A49+offset
       clears validity byte FEBE52CC[pdu]
       increments update counter FEBE532C[pdu]
  -> generated COM unpackers (e.g. 0x4A244 for PDU 6)
       call application_com_receive_signal  @ 0x7C03E
       or opaque byte-copy helper           @ 0x7D63E
```

Diagnostic IDs use `application_can_diagnostic_rx_demux @ 0x80114` and special
`0x7F7` uses `application_can_special_rx_demux @ 0x7FF86`. Those paths are not
COM I-PDUs and are not rows in this map.

## 3. Generated configuration tables

Application `tp` is `0x23EE4`.

| Address | Contents |
|---:|---|
| `0x231A0` | 51 sixteen-byte RSCAN acceptance rules + `0xFFFFFFFF` terminator |
| `0x22018` | 47 eight-byte normal Rx descriptors (`software_id:u32`, `length:u32`) |
| `0x2273C` | 53 eight-byte COM PDU descriptors; entries 6..52 are Rx |
| `0x228E4` | COM data-buffer offsets into the image at `0xFEBE4A49` |
| `0x224E4` | 300-entry `signal_id -> COM PDU` map |
| `0x223B8` | 300-byte signal property/type array |
| `0x25902` | 14 opaque Rx signal IDs `87..100` (property class 4) |
| `0x2591E` | matching COM buffer offsets for those opaque signals |

Each COM PDU descriptor is:

```text
timeout_or_cycle:u16, b1:u8, b2:u8, length:u16, b4:u8, flags:u8
```

All 47 Rx descriptors use `flags=0x0C`. The first `u16` is recorded as
`timeout_ticks` (raw COM counts; not claimed as milliseconds).

Acceptance rule layout matches `../architecture/firmware-architecture.md`: normal rules use
hardware labels 9..55 and route word `2`. Software CAN-FD markers
(`0x40000000`) appear on descriptors for `0x025`, `0x090`, and `0x0D7` with
length 32; hardware-rule ID fields keep the underlying 11-bit IDs.

## 4. The 47 normal Rx I-PDUs

Application PDU ID = `6 + acceptance_index`. CAN IDs:

```text
2E4 3B0 63B 624 63D 00F 013 014 015 016 017 018 019 01A 01B 01C
01D 01E 01F 191 131 2FD 0D0 3BF 127 115 1C5 294 51E 132 611 2D1
675 2E8 025 423 0AA 101 0D5 13B 090 0D7 64F 020 403 490 1DA
```

Lengths are eight bytes except FD entries `0x025`/`0x090`/`0x0D7` (32) and
classic `0x423`/`0x490` (1). Every PDU has at least one configured COM signal.

### 4.1 SecOC envelopes (included in the 47)

These six normal Rx I-PDUs also have SecOC receive records at `0x25970` (see
`../security/secoc/application-chain.md`):

| CAN ID | Acceptance | COM PDU | Format |
|---:|---:|---:|---|
| `0x2E4` | 0 | 6 | classic |
| `0x00F` | 5 | 11 | classic sync |
| `0x131` | 20 | 26 | classic |
| `0x132` | 29 | 35 | classic |
| `0x090` | 40 | 46 | CAN FD |
| `0x0D7` | 41 | 47 | CAN FD |

CSV column `secoc_envelope=yes` marks them. SecOC authentication is upstream of
or alongside COM indication; it does not remove them from the normal 47.

### 4.2 Diagnostic/special contexts (excluded)

| CAN ID | Acceptance index | Demux |
|---:|---:|---|
| `0x7A1` | 47 | diagnostic |
| `0x777` | 48 | diagnostic |
| `0x7A0` | 49 | diagnostic |
| `0x7F7` | 50 | special |

These are not COM PDUs 6..52 and have no rows in `application_rx_map.csv`.

## 5. Signals and extraction

Signals **0..57** are transmit (see `../communications/application-tx.md`). Signals
**58..299** are receive.

`application_com_receive_signal @ 0x7C03E` extracts a big-endian bit field from
the COM buffer. Wire fields use the same `B0[7]` notation as the transmit map.
Its destination store width is determined by the extracted bit length, not by a
nominal C destination type: **1 byte for 1..8 bits, 2 bytes for 9..16 bits, and
4 bytes for 17..32 bits**. The raw helper branches at `0x7C0D8..0x7C0EA` are
pinned by `verify_application_receive.py`; this matters for the 10/12/15-bit
signals, whose evidence rows are halfword destinations rather than overlapping
four-byte objects. Opaque property-class-4 signals copy whole PDU payloads
through helpers at `0x68368` / `0x6875E` using the tables at `0x25902` /
`0x2591E`.

For each recovered signal the CSV records:

- parent PDU / CAN ID / lengths / timeout ticks
- unpacker address
- wire field, bit length, start argument, signedness
- destination RAM (or COM opaque shadow expression) and width
- first non-unpacker READ consumer when Ghidra xrefs prove one; lack of a
  downstream semantic consumer remains a separate bound from extraction
- for configured IDs with no stock COM extraction, an explicit negative
  classification and structural basis instead of fabricated wire fields

### 5.1 Complete extraction census and the 97 negative rows

**Positive extraction evidence (145):** the exporter records 131 bitfield
extractions through `application_com_receive_signal @ 0x7C03E` plus 14
property-class-4 group/opaque signals from the tables at `0x25902/0x2591E` and
`application_com_receive_signal_group_bytes @ 0x7D63E`. Tests re-hash every
distinct unpacker body and re-check signal-ID / buffer / length / signedness
immediates and GP-relative destinations against CodeFlash.

The negative side is now deterministic rather than residual. The
`signal_id -> PDU` table at `0x224E4` has only four code readers in the image:
`application_com_receive_signal`, `application_com_send_signal`,
`application_com_pack_big_endian_signal`, and
`application_com_receive_signal_group_bytes`. On the Rx side, the complete
`application_com_receive_signal` xref census contains 133 call references: 131
ordinary generated bitfield calls plus two table-driven calls inside the known
crypto-test collector. The byte-group helper has exactly 12 call references,
all in the two already-modeled opaque/test-bank collectors. There is no third
generic COM signal-extraction API.

The remaining **97 configured IDs therefore have no stock COM extraction**:

- **93** are omitted by generated PDU handlers that do extract other configured
  IDs from the same PDU;
- signals **84, 85, 86** belong to COM PDU 11 / CAN `0x00F`, which has no COM
  unpacker but is consumed as the SecOC synchronization envelope;
- signal **217** belongs to COM PDU 39 / CAN `0x2E8`, the sole ordinary PDU with
  a configured signal but no recovered COM unpacker.

These rows are emitted as `classified-no-com-extraction` with `wire_field=n/a`
and no invented destination. The claim is deliberately signal-API scoped: it
excludes a configured COM extraction of that signal ID, not every possible
direct read of the containing PDU buffer.

### 5.2 Processor audit coverage

`AssertApplicationReceiveMap.java` (via `make verify-processor`) audits the 145
recovered CSV rows against Ghidra refs:

| Check | Count |
|---|---:|
| Recovered rows audited | 145 |
| Concrete dest DATA/WRITE ownership (unpacker targets dest) | 131 |
| Concrete non-unpacker first-consumer READ ownership | 106 |
| Unpacker-local post-process inputs | 7 |
| Stored scalar destinations with no direct READ consumer | 18 |
| Opaque/group destinations | 14 |

Indirect stores through `receive_signal` are proved by unpacker DATA refs to the
destination. Explicit WRITE co-owners `0x1404` (boot BSS clear) and `0x57bfe`
(app default-init) are allowlisted; unexpected WRITE/READ owners fail. The old
25-row `configured-unresolved` consumer bucket is no longer treated as one
undifferentiated exception. `data/application_rx_consumer_audit.csv` regenerates
that exact denominator from the live project and splits it into **7 local
post-process inputs** and **18 store-only direct-reference shapes**.

The seven local inputs are deterministic generated conversions rather than dead
fields. CAN `0x0AA` signals **231/233/235/237** are unsigned 15-bit halfwords;
each raw value is immediately re-read by the same unpacker and passed through
`FUN_0004A49C` with offset `0x1A6F`, producing the derived halfwords at
`0xFEBE8032/8034/8036/8038`. SecOC CAN-FD `0x090` signals
**270/273/276** are unsigned 10-bit halfwords normalized the same way with
offset `0x0200`, producing `0xFEBE8060/8062/8064`. All seven derived outputs
have downstream reads in `application_rx_signal_consumer_56fc2`; several of the
`0x0AA` results also feed additional state consumers.

The other **18** destinations have an exact two-reference scalar shape in the
current graph: one DATA target from their generated unpacker and one default
initializer WRITE, with **no direct READ**. The read-only consumer audit also
finds no outside `PARAM` pointer into the exact destination range owned by the
same unpacker. As a separate whole-bank check, **no `PARAM` or plain `DATA`
address-taking reference into `0xFEBE7F94..0xFEBE8084` originates outside the
generated unpacker cluster**; this excludes the Ghidra-visible pointer forms a
generic memcpy/RTE-style whole-bank consumer would normally require. Sixteen of
those 18 are selective omissions inside unpackers whose sibling fields do have
downstream consumers; only CAN `0x020` signals **291/292** form an entire
two-signal unpacker with no scalar consumer. This remains a bounded static
result, not a proof against a representation that creates neither a direct
READ nor a Ghidra `PARAM`/plain-`DATA` address reference.

For SecOC specifically, the nine formerly direct-read-unresolved fields split
as follows:

- **local post-process:** CAN `0x090` signals **270/273/276**;
- **stored-no-direct-consumer:** CAN `0x2E4` signal **62**, CAN `0x131` signal
  **115**, CAN `0x132` signals **194/197**, CAN `0x090` signal **278**, and CAN
  `0x0D7` signal **286**.

The latter six are still inside the SecOC-protected envelope. Signals 62,
194, and 197 occupy authentic-payload bits; signals 115, 278, and 286 occupy the
transmitted-freshness nibble at the start of the trailer, which affects full
freshness reconstruction and therefore verification. Thus
"stored-no-direct-consumer" means the recovered post-unpack scalar has no
direct software consumer; it does **not** mean those wire bits bypass SecOC or
can be changed without satisfying freshness/MAC verification.

### 5.3 Protected steering PDU downstream roles

The whole-image decompiler corpus plus canonical-address xrefs closes the three
classic protected steering-adjacent PDUs more deeply than extraction alone.

**CAN `0x2E4`** is the LKA torque-command mode. Signal 60 B0[0]
(`STEER_REQUEST` in the pinned Toyota SecOC DBC) follows
`FEBE7F98 -> FEBEF02A -> FEBEACFF` and enters source arbitration at `0xCA354`;
signal 61 B1..B2 (`STEER_TORQUE_CMD`) follows
`FEBE7F94 -> FEBEF184 -> FEBEAE20` and the clamp/rate-limit chain documented in
[control partition §9.3](../architecture/control-partition.md#93-protected-steering-command-arbitration-and-the-dq-join).
The request and value meet through torque-mode state `FEBEC13D` at the common
selector `0xCA6B8`.

**CAN `0x131`** is the second protected steering command mode. The pinned Toyota
SecOC DBC names it `STEERING_LTA_2`; the firmware mapping is:

| Signal | Wire field | Snapshot state | Downstream role |
|---:|---|---:|---|
| 109 | B0[3] / public `STEER_REQUEST` | `FEBEAD54` | LTA request/submode latch |
| 110 | B0[2] | `FEBEAD53` | snapshot only; no runtime reader |
| 111 | B0[1] | `FEBEAD52` | additional firmware submode selector; OEM name unresolved |
| 112 | B0[0] / public `STEER_REQUEST_2` | `FEBEAD50` | source arbitration at `0xCA354` |
| 113 | B1[5:0] / public `COUNTER` | `FEBEAD4F` | wrapped counter/deadline logic at `0xC9EF4` |
| 114 | B2..B3 signed16 / public `STEER_ANGLE_CMD` | `FEBEAE60` | LTA controller input |
| 115 | B4[7:4] | — | stored-no-direct-consumer freshness-envelope field |

The signed angle is not telemetry-only: `0xC8DE0` conditions it into
`FEBEBFF0`, then `0xC96D2 -> 0xC97B2 -> 0xC8D62` produces alternate command
`FEBEC0D6`. LTA-mode state `FEBEC13A` makes `0xCA6B8` select `FEBEC0D6` into
common command state `FEBEC144`. A separate `0xCA0B4` branch reuses
`FEBEAE60` for command plausibility/range supervision. Thus the protected
`0x131` stream is both a steering-control and supervision input in this image.

**CAN `0x132`** was checked specifically as a possible parallel actuator path.
Signals 191/192/193/196/195/198 are copied by `0x56FC2` into
`FEBEF064/061/062/063/F19C/F19A` respectively and then by `0xBA43A` into
`FEBEAD06/AD04/AD05/AD07/AE28/AE2A`. All six post-snapshot locations have
exactly two direct references in the corrected project: the snapshot WRITE and
an initialization WRITE. They have no runtime READ. Signals 194/197 are already
in the stored-no-direct-consumer bucket above. Therefore no recovered scalar
field of protected `0x132` reaches steering actuation in this calibration.

One corpus representation caveat is now pinned explicitly: instruction
`0x572B0` reads byte `FEBE8001` (signal 196) and `0x572B4` writes `FEBEF063`,
but the decompiler currently prints that source as `DAT_febe8000._1_1_` because
Ghidra typed the adjacent bytes as one object. Canonical instruction/data xrefs,
not the textual composite spelling, are authoritative for this join.

### 5.4 Complete six-profile SecOC downstream surface

The receive-table fact that a PDU is SecOC-protected does **not** imply that it
is a steering command. Tracing every configured protected profile through its
COM/staging consumers gives the calibration-specific partition recorded in
`data/secoc_rx_control_surface.csv`:

| CAN | Protected role | Recovered downstream semantics |
|---:|---|---|
| `0x00F` | synchronization | SecOC trip/reset freshness source; no scalar COM unpacker and no steering command selection |
| `0x2E4` | steering command | authenticated LKA torque request/value; selects `FEBEC13D` mode 1 and enters `FEBEC144` from `FEBEBFA2` |
| `0x131` | steering command | authenticated `STEERING_LTA_2` request/angle; selects `FEBEC13A` mode 2 and enters `FEBEC144` from controller output `FEBEC0D6` |
| `0x132` | protected snapshot | six recovered post-snapshot scalars have zero runtime readers; bounded non-actuation result |
| `0x090` | rear-wheel speed + steering-angle-speed validity prerequisite | signals 270/273 form the protected RR/RL rear-wheel-speed pair; signal 276 is protected `CAN Steering Angle Speed (SSAV)`; status bits feed steering validity gates; none selects `C13A/C13D` command mode |
| `0x0D7` | SP1 vehicle speed / validity | signal 283 is protected `CAN Vehicle Speed (SP1)` and becomes `FEBEB6F2` then `application_vehicle_speed_raw`; protected status can force a fault/event path; remaining fields terminate in snapshot state |

#### `0x090`: protected rear-wheel speed, steering-angle speed, and validity

PDU 46 is a 32-byte SecOC CAN-FD profile with 28 authentic payload bytes. Its
generated unpacker recovers three unsigned 10-bit channels (signals
270/273/276) at `FEBE805A/805C/805E`. The unpacker immediately recenters each
around `0x0200`, producing `FEBE8060/8062/8064`; the common staging routine then
copies those values to `FEBEF1C6/F1C8/F1CA`.

A cross-source Techstream correlation now resolves the physical quantities.
`EMPS2_P5.ddb` exposes four consecutive CAN monitors, byte-identically in
NA/EU/JP: key 303 `CAN Vehicle Speed (Speed Sensor RR)` (`km/h`), key 304
`CAN Vehicle Speed (Speed Sensor RL)` (`km/h`), key 305 `CAN Vehicle Speed
(SP1)` (`km/h`), and key 306 `CAN Steering Angle Speed (SSAV)` (`deg/s`). The
firmware independently supplies the same shape: the first two `0x090` channels
have identical width/scaling and are processed as a redundant pair, while the
third has a distinct signed-dynamic transform and steering-validity/filter use.
Accordingly signals 270/273 are promoted as the **unordered RR/RL rear-wheel-
speed pair**, and signal 276 as **SSAV steering-angle speed**. Static evidence
does not bind signal 270 versus 273 individually to RR versus RL, so that
ordering remains explicitly unresolved.

The first two channels are consumed by
`fd090_rear_wheel_speed_plausibility @ 0xBBF0E`; the third is consumed by
`fd090_steering_angle_speed_plausibility @ 0xBC766`. These routines apply
calibration scaling/bounds and publish `FEBEB6AA/FEBEB714` plus 0/`0x5A`
plausibility flags. `BA43A` then promotes the numeric states into the
steering-cycle snapshot:

```text
0x090 signals 270/273
  -> 8060/8062 -> F1C6/F1C8 -> BBF0E -> B6AA
  -> BA43A -> FEBEAE02
  -> C8F04 / C8F2A / C9106 / C94D0 / C955A / C9632

0x090 signal 276
  -> 8064 -> F1CA -> BC766 -> B714
  -> BA43A -> FEBEAF00
  -> BFBA8 (only while aggregate validity B7C4 == 0x5A)
```

`FEBEAE02` is therefore the selected/conditioned rear-wheel-speed input used by
the recovered LTA/steering subsystem, not telemetry-only state. The normal
calibration publishes the second member of the RR/RL pair while retaining the
first for cross-channel plausibility; an alternate configuration enables a
combined two-channel calculation. `FEBEAF00` is the conditioned SSAV input.
Only the individual RR-versus-RL wire ordering remains unresolved.

Protected `0x090` status fields are also steering prerequisites. `BA43A` copies
two staged status bytes to `FEBEAD71/AD72`, which `BF750` folds into validity
state feeding `FEBEB75F`; two more reach `FEBEACE3/ACE4`, which participate in
the larger all-healthy conjunction at `BF96A -> FEBEB7C4`. `B7C4` in turn gates
`BFBA8` and is read by additional steering-cycle monitor/filter functions. Thus
`0x090` can inhibit or qualify steering-control state without being a command
source.

#### `0x0D7`: protected vehicle speed and invalidity/status

PDU 47 is the second 32-byte SecOC CAN-FD profile. Its unsigned 16-bit signal
283 is recovered at `FEBE8070`, staged to `FEBEF1B6`, and normalized by
`fd0d7_sp1_vehicle_speed_normalize @ 0xBC484`:

```text
0x0D7 signal 283
  -> FEBE8070 -> FEBEF1B6
  -> BC484 (bound to 30000, scale by 0x147B >> 12)
  -> FEBEB6F2
  -> application_input_snapshot_update
  -> application_vehicle_speed_raw @ FEBEE892
```

`FEBEB6F2` is consumed throughout low/high-speed thresholds and state machines;
the named application snapshot is also used by diagnostic-session and routine
speed guards. Techstream independently identifies the corresponding family CAN
quantity as `CAN Vehicle Speed (SP1)`, and its section-62 monitor record carries
an exact raw upper bound of **30000** in all three regions—the same value
`0xBC484` uses to clamp signal 283 before conversion. This upgrades signal 283
to a very-high-confidence protected **SP1 vehicle-speed** source.

Signal 280 is a separate protected B0[7] status/invalidity input. It exposed a
receiver-evidence bug because this generated unpacker does not pass a
GP-relative destination directly: it initializes stack byte `SP+0x0B` from
`FEBE8076`, passes that stack pointer to `application_com_receive_signal`, then
reloads the byte and persists it at instruction `0x4B45C` to `FEBE8076`.
`0x56FC2` stages it into `FEBEF094`. `fd0d7_status_fault_monitor @ 0xB6396`
reads `FEBEF094`; while its local state is healthy, an asserted status joins
other invalidity predicates, forces the fault state, invokes the fault helper,
and raises system-mode event `0x2D`. Additional direct reads of `FEBE8076` are
bounded to diagnostic/routine status gating and the generated preserve-on-no-
update read in its own unpacker.

This also corrects the former map entry that assigned both signals 280 and 284
to `FEBE8072`: signal **284** independently owns `FEBE8072`; signal **280**
persists to `FEBE8076`. The evidence exporter now reconstructs this generated
stack-temporary pattern rather than inheriting the previous call's GP pointer.

The other staged `0x0D7` scalar fields close negatively after publication:
`FEBEAED6`, `FEBEAED8`, `FEBEADE1`, and `FEBEADE2` each have exactly two direct
references—one `BA43A` snapshot WRITE and one subsystem-initialization WRITE—
and no runtime READ.

The resulting distinction is operationally important for target bring-up: the
only recovered SecOC **command** PDUs in this Sienna calibration are `0x2E4`
and `0x131`. A target can still require other authenticated streams such as
`0x090` or `0x0D7` as prerequisite sensor/validity state, so key recovery and
message-profile discovery must not be reduced to checking command IDs alone.

### 5.5 Signals 95..100 form a dormant crypto-test input bank

The consumer at `0x6875E` bounds six previously anonymous generated signals.
The property-4 descriptor table is separate from the main property-3 table, but
the decompiler plus raw metadata make the byte layout exact:

| CAN ID | Signal IDs | Exact recovered use |
|---:|---:|---|
| `0x01B` | 95, 96 | byte 0 / COM `0x97` = ICU-S key selector; byte 1 / COM `0x98` = test mode; both are 8-bit |
| `0x01C`, `0x01D` | 97, 98 | COM `0x9F/0xA7`: exact 16-byte chosen crypto input |
| `0x01E`, `0x01F` | 99, 100 | COM `0xAF/0xB7`: exact 16-byte expected result |

For the selector-4 command-5 probe, `0x01B` therefore begins `04 01`
(selector 4, mode 1), while `0x01C/0x01D` carry the 16-byte message. The
collector watches PDU update-counter indices `20..24` and the flash threshold at
`0x30FBB` is `0x03`: after a changed value updates the shadow, the same value
must be observed unchanged three times before commit. A dynamic probe should
therefore send at least four, preferably five, **spaced** identical rounds rather
than a burst whose updates may collapse into one cyclic observation.

These CAN frames still do not activate the bank by themselves: no stock caller
or CodeFlash function-pointer entry to `crypto_test_bank1_activate @ 0x69018`
has been recovered. The minimal application-context experiment now tail-calls
that stock activator once after the normal crypto-test initializer and otherwise
leaves the stock command-5 state machine intact. The generated result is not
stock CAN output, but a three-site diagnostic-only redirection lets existing DID
`0x1010` selector 3 expose the dormant result buffer without modifying the
production SecOC path. See [SecOC application chain](../security/secoc/application-chain.md),
[software-path assessment](../security/secoc/software-path-assessment.md), and
`exploit/command5/stimulus.py`.

## 6. Timeout / validity RAM

| Root | Role |
|---|---|
| `0xFEBE52CC + pdu` | validity / freshness byte; init `0x5A`; cleared on RxIndication |
| `0xFEBE532C + pdu` | update generation counter; incremented on RxIndication; watched by unpackers |

Helpers `0x48CC8` / `0x48D14` consume validity through a secondary slot table at
`0x29178`. Those slot semantics stay structural.

## 7. COM signal deadline monitors

Four large functions form the AUTOSAR COM signal deadline/timeout monitoring
layer. They manage signal lifecycle states through function-pointer tables,
which is why Ghidra's type propagation does not settle on them.

| Function | Size | Indirect calls | Role |
|---|---:|---:|---|
| `com_signal_deadline_monitor_a` (`0x69824`) | 1352 B | 15-slot FP table | Called by 8 functions in `0x3Cxxx-0x45xxx` |
| `com_signal_deadline_monitor_b` (`0x6AD24`) | 1444 B | 31 indirect calls | Called by 8 functions in `0x45xxx-0x46xxx` |
| `com_signal_deadline_monitor_c` (`0x69DEC`) | 1182 B | 33 indirect calls | Called by 8 functions |
| `com_signal_deadline_monitor_d` (`0x6A28A`) | 1208 B | 28 indirect calls | Called by 8 functions |

Signal lifecycle states managed by these monitors:

| State | Meaning |
|---|---|
| `0x00` | init |
| `0x11` | signal received / alive |
| `0x22` | timeout / deadline expired |
| `0x33`/`0x44` | marked / replaced |

Each dispatches lifecycle callbacks (timeout notification, reception
notification, etc.) through a 15-slot function-pointer table
(`param_3[0]`..`param_3[0xe]`). The four variants differ in signal class
and timeout behavior.

## 8. RTE input staging copies

Three functions are pure AUTOSAR RTE-generated input staging — field-by-field
struct copies with zero logic, zero `if` statements, and zero calls. They
gather runnable inputs from scattered Rte buffers into contiguous
runnable-local input structs inside critical sections.

| Function | Size | Field copies | Source | Destination |
|---|---:|---:|---|---|
| `rte_input_staging_copy_a` (`0x5C666`) | 1442 B | 220 | `0xFEBE6800-0xFEBEE600` | `0xFEBE6400-0xFEBE676F` |
| `rte_input_staging_copy_b` (`0x5C0B6`) | 1204 B | 189 | scattered Rte buffers | `0xFEBE6400-0xFEBE6600` |
| `rte_input_staging_copy_c` (`0x5B9C4`) | 1250 B | 192 | scattered Rte buffers | `0xFEBE6200-0xFEBE6400` |

Copy A and B run under the E2E config-management cyclic (`0x57AC2`) inside
critical sections (interrupt masks `0xFF00`/`0xFFC0`). Copy C runs from both
the TAUJ0 CH2 ISR and the foreground cyclic.

## 9. Motor-control calibration ingress

Three hand-written OEM motor-control/calibration functions sit beneath this
application ingress. Stage 6 now bounds all three by their execution domains:

| Function | Size | Runtime role | Calibration block |
|---|---:|---|---|
| `dual_motor_phase_current_conditioning` (`0x47C3C`) | 1632 B | Steady and transition TAUJ0 CH0 phase-current conditioning with offset/gain multiplication, saturation, and missing-phase reconstruction | CodeFlash `0x1875x` |
| `motor_coord_transform_calib_handler` (`0x32B80`) | 1560 B | State `0x33` of `0x33198`; reached by CH0 transition and steady dispatch when version domain is `0x512` or `0x600` | CodeFlash `0x3103x` |
| `motor_rotor_observer_calib_handler` (`0xB98BC`) | 1040 B | Observer/state recalculation in TAUJ0 CH2 version domain `0x200..0x522`, reached through transition `0xBEB44` and steady `0xBEBF6` wrappers | CodeFlash `0x1A12x-0x1A15x` |

The runtime acquisition/current-control/TSG3 PWM chain and the version-domain
proof are canonical in [../architecture/control-partition.md](../architecture/control-partition.md)
§9 and `data/motor_calibration_handlers.csv`. CORR-016 records the earlier
`0x47C3C` correction; Stage-6 corrections record the remaining stale handler
and phase-acquisition interpretations.

## 10. Hardware register access helper

`hardware_register_access_helper` (`0x48312`, 2044 bytes) provides
register-level I/O for peripheral configuration during signal processing.
12 SFR references. Called by the CAN signal processing chain
(`0x5D3CE`/`0x5D94E`).

## 11. Evidence boundaries

Core conclusions—47/242 counts, table addresses, CAN IDs, lengths, PDU
ownership, `0x344` absence, SecOC inclusion (cross-checked to records at
`0x25970`), diagnostic exclusion, COM roots from GP immediates
(`GP=0xFEBEB800` → `0xFEBE4A49`/`0xFEBE52CC`/`0xFEBE532C`), all 145 positive
extractions, the complete signal-API xref boundary behind the 97 negative
classifications, and consumer xrefs—come from committed CodeFlash plus read-only
Ghidra export/audit. No claim assigns OEM signal names, engineering units, or
physical scaling.
