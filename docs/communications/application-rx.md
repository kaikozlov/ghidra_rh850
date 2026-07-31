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

Recovered vs bounded (this calibration):

| Evidence status | Signals |
|---|---:|
| recovered (unpacker + wire/dest) | 145 |
| configured-unresolved | 97 |

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
Opaque property-class-4 signals copy whole PDU payloads through helpers at
`0x68368` / `0x6875E` using the tables at `0x25902` / `0x2591E`.

For each recovered signal the CSV records:

- parent PDU / CAN ID / lengths / timeout ticks
- unpacker address
- wire field, bit length, start argument, signedness
- destination RAM (or COM opaque shadow expression) and width
- first non-unpacker READ consumer when Ghidra xrefs prove one, else a bounded
  `configured-unresolved` string

### 5.1 Known vs configured-unresolved

**Known (145):** machine-exported call-site evidence in
`data/application_rx_signal_evidence.csv` (131 bitfield calls to `0x7C03E` plus
14 opaque table rows). Tests re-hash every distinct unpacker body and re-check
signal-ID / buffer / length / signedness immediates and GP-relative destinations
against CodeFlash; they do not reimport a generator overlay.

**Configured-unresolved (97):** signal exists in `0x224E4` / property table, but
no exportable unpack call or opaque-table row proves extraction parameters.
Bound language is stored in `first_consumer` / `notes`.

Example: COM PDU 11 / CAN `0x00F` has three configured signals and no COM
unpacker in this image; SecOC still processes the frame.

### 5.2 Processor audit coverage

`AssertApplicationReceiveMap.java` (via `make verify-processor`) audits the 145
recovered CSV rows against Ghidra refs:

| Check | Count |
|---|---:|
| Recovered rows audited | 145 |
| Concrete dest DATA/WRITE ownership (unpacker targets dest) | 131 |
| Concrete first-consumer READ ownership | 106 |
| Bounded exceptions (14 opaque dest + 25 unresolved consumer) | 39 |

Indirect stores through `receive_signal` are proved by unpacker DATA refs to the
destination. Explicit WRITE co-owners `0x1404` (boot BSS clear) and `0x57bfe`
(app default-init) are allowlisted; unexpected WRITE/READ owners fail.

### 5.3 Signals 95..100 form a dormant crypto-test input bank

The consumer at `0x6875E` bounds six previously anonymous generated signals:

| CAN ID | Signal IDs | Recovered structural use |
|---:|---:|---|
| `0x01B` | 95, 96 | ICU-S runtime key selector and test mode |
| `0x01C`, `0x01D` | 97, 98 | 16-byte chosen crypto input |
| `0x01E`, `0x01F` | 99, 100 | 16-byte expected result |

The collector watches PDU update-counter indices `20..24` and requires three
identical updates before committing the values. These CAN frames do not expose
a normally reachable signing service: the periodic consumer runs only after
the dormant activator at `0x69018` sets the bank active, and no caller or
CodeFlash function-pointer entry to that activator has been recovered. The
command-5 result is compared locally with the expected input and is not sent
back on CAN. The complete ICU interpretation and evidence bounds live in
[SecOC application chain](../security/secoc/application-chain.md).

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

Three hand-written OEM motor-control functions sit beneath calibration ingress,
but the complete caller graph corrects an earlier overgeneralization: only
`0x32B80` and `0xB98BC` remain calibration-transition-only. `0x47C3C` also has a
steady TAUJ0 CH0 caller and is part of the per-tick phase-current pipeline.

| Function | Size | Runtime role | Calibration block |
|---|---:|---|---|
| `dual_motor_phase_current_conditioning` (`0x47C3C`) | 1632 B | Steady and transition CH0 phase-current conditioning with offset/gain multiplication, saturation, and missing-phase reconstruction | CodeFlash `0x1875x` |
| `motor_coord_transform_calib_handler` (`0x32B80`) | 1560 B | Calibration-transition handler; exact runtime consumer semantics remain bounded | CodeFlash `0x3103x` |
| `motor_rotor_observer_calib_handler` (`0xB98BC`) | 1040 B | Calibration-transition handler with atan2/sqrt, interpolation, and DTC state | CodeFlash `0x1A12x-0x1A15x` |

The runtime current-control and TSG3 PWM chain is canonical in
[../architecture/control-partition.md](../architecture/control-partition.md)
§"Independent phase-current control to physical PWM boundary". CORR-016 records
the superseded calibration-only classification.

## 10. Hardware register access helper

`hardware_register_access_helper` (`0x48312`, 2044 bytes) provides
register-level I/O for peripheral configuration during signal processing.
12 SFR references. Called by the CAN signal processing chain
(`0x5D3CE`/`0x5D94E`).

## 11. Evidence boundaries

Core conclusions—47/242 counts, table addresses, CAN IDs, lengths, PDU
ownership, `0x344` absence, SecOC inclusion (cross-checked to records at
`0x25970`), diagnostic exclusion, COM roots from GP immediates
(`GP=0xFEBEB800` → `0xFEBE4A49`/`0xFEBE52CC`/`0xFEBE532C`), recovered unpack
parameters from the evidence CSV, and consumer xrefs—come from committed
CodeFlash plus read-only Ghidra export/audit. No claim assigns OEM signal names,
engineering units, or physical scaling.
