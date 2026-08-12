# Application transmit-PDU and COM signal map

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS COM-003
>
> **Canonical artifacts:** `data/application_tx_map.csv`, `data/application_tx_producer_evidence.csv`
>
> **Verification:** `tests/verify_application_transmit.py`, `tests/verify_application_tx_producer_evidence.py`
>
> **Related:** [application-rx](application-rx.md), [firmware-architecture](../architecture/firmware-architecture.md)

This report completes the statically recoverable application transmit map for
China-market Sienna EPS firmware `8965B4512000`. It covers every active
application CanIf transmit route, all six COM transmit I-PDUs, and all 58 COM
signals assigned to those I-PDUs.

Addresses are CodeFlash virtual addresses unless they begin with `0xFEBE`. The
machine-readable 58-row map is `data/application_tx_map.csv`; independent
raw-image checks are in `tests/verify_application_transmit.py`.

## 1. Executive summary

The application has **11 active CanIf transmit configurations** divided among
three generated routing classes:

- six COM I-PDUs on CAN IDs `0x260`, `0x262`, `0x351`, `0x394`, `0x4A3`, and
  `0x4C8`;
- four transport/diagnostic routes on `0x7A9`, `0x7A9`, `0x7A8`, and `0x7A8`;
- one special route on `0x7F8`.

The six COM I-PDUs contain **58 configured signal IDs, 0 through 57**. The
static producer boundary is now closed for all 58. Generated packers directly
produce 55 fields; signals **9** (`0x260 B7`) and **37** (`0x262 B7`) are filled
after COM packing by the CanIf checksum callback at `0x7FEAC`; signal **57**
(`0x4C8 B4..B7`) is initial/default zero only in this calibration, with no
enabled packer, COM pre-transmit transform, CanIf post-packer transform, or
lower-stack writer.

The new producer census in `data/application_tx_producer_evidence.csv` closes a
more useful structural boundary for semantic work: the **50 RAM-backed Tx
signals use 50 distinct staging cells**, and each cell has exactly one
non-default WRITE, one generated-packer READ, and one write from
`application_ram_default_init @ 0x57BFE`. Those 50 non-default writes collapse
to only **11 producer functions** (`0x4B66C`, `0x4B754`, `0x4B7BA`, `0x4B882`,
`0x4B8B6`, `0x4B900`, `0x4B90A`, `0x4B920`, `0x4B93C`, `0x4B976`, `0x4B9CC`).
Only eight additional direct READ references exist, across signals 1, 6, 8,
10, and 38. The exporter derives the staging-address set from the six packer
bodies rather than from documentation, while the verifier independently pins
every owning-function body hash to raw CodeFlash. This is a producer-census
claim, not yet a semantic naming claim for the anonymous status fields.

The application transmit chain is:

```text
application output staging at 0xFEBE8094..0xFEBE8110
  -> six generated packers at 0x4BB1E..0x4C25C
  -> application_com_pack_big_endian_signal @ 0x7C232
     / application_com_send_signal          @ 0x7C0F0
  -> application_com_tx_main                @ 0x7D04E
  -> application_com_transmit_pending_pdu   @ 0x7CE28
  -> application_pdur_com_transmit          @ 0x80992
  -> application_pdu_transmit_router        @ 0x809C6
  -> application_canif_transmit             @ 0x7EE0C
  -> application_can_tx_enqueue             @ 0x7EC5A
       -> controller-0 pre-enqueue hook      @ 0x800D2
          -> additive checksum callback      @ 0x7FEAC  (PDU 0/1 only)
  -> software transmit queue
  -> application_rscfd_write_dispatch       @ 0x84022
  -> application_rscfd_write_classic        @ 0x842BA
  -> RSCFD channel-1 transmit resources
  -> EIINT 188 / 0x65028 / 0x8474E confirmation path
```

No COM transmit I-PDU in this image is CAN FD: the lengths are 8, 8, 4, 3, 8,
and 8 bytes and all six IDs are standard 11-bit identifiers.

None of the 11 active transmit routes is a configured SecOC transmit path. The
separate ICU-S command-5 MAC-generation dispatcher has exactly one recovered
caller, a dormant receive-fed crypto-test harness, and its 16-byte result is
compared locally rather than passed to the PDU router. Using the EPS as a
signing proxy would therefore require new application-resident code, an output
or in-EPS transmit route, and sender-side freshness handling; no production
SecOC Tx stack in this firmware is available to repurpose. This stock-EPS
boundary does not imply that no external sender exists: pinned opendbc code and
the independent local stateless signer implement the accepted classic frame
format. See the [SecOC application chain](../security/secoc/application-chain.md)
and [sender implementation](../security/secoc/sender-implementation.md).

## 2. Generated configuration tables

Application `tp` is `0x23EE4`. The relevant generated tables are:

| Address | Contents |
|---:|---|
| `0x21A68` | six routing-class counts: `6, 0, 4, 0, 0, 1` |
| `0x21F78` | six COM CanIf Tx records |
| `0x21FA8` | four transport/diagnostic CanIf Tx records |
| `0x21F68` | active special CanIf Tx record (`0x7F8`) |
| `0x21F70` | class-5 special Rx match record (`0x7F7`) |
| `0x21A2C` | receive-class descriptor pointer table; class 5 -> `0x21AC4` |
| `0x21FE0` | COM-to-CanIf post-packer route flags; first six = `1,1,0,0,0,0` |
| `0x21900` / `0x2194C` | controller-0 pre-enqueue hook `0x800D2` / checksum callback `0x7FEAC` |
| `0x221DC` | initial COM I-PDU data image |
| `0x223B8` | 300-byte COM signal type/property array |
| `0x224E4` | 300-entry `signal_id -> COM I-PDU` map |
| `0x2273C` | 53 eight-byte COM I-PDU descriptors |
| `0x228E4` | COM I-PDU data-buffer offsets |

The 53 COM I-PDU descriptors split exactly into six transmit I-PDUs followed by
47 normal receive I-PDUs. This independently agrees with the 47 normal receive
CAN IDs documented in `../architecture/firmware-architecture.md`.

Each active CanIf record is eight bytes:

```text
CAN_ID:u32, controller:u8, reserved:u8, confirmation_route:u16
```

The COM records use controller 0. Their source PDU IDs are the ordinary class-0
indexes `0..5`. Generated PDU IDs use the high five bits as a routing class, so
the transport class is `0x0800..0x0803` and the special class is `0xF800`.

### 2.1 All active application transmit routes

| Generated source PDU | CAN ID | Class | Static upper role |
|---:|---:|---|---|
| `0x0000` | `0x260` | 0 | COM Tx I-PDU 0 |
| `0x0001` | `0x262` | 0 | COM Tx I-PDU 1 |
| `0x0002` | `0x351` | 0 | COM Tx I-PDU 2 |
| `0x0003` | `0x394` | 0 | COM Tx I-PDU 3 |
| `0x0004` | `0x4A3` | 0 | COM Tx I-PDU 4 |
| `0x0005` | `0x4C8` | 0 | COM Tx I-PDU 5 |
| `0x0800` | `0x7A9` | 2 | transport/diagnostic route 0; used by application negative-response path `0x55C44` |
| `0x0801` | `0x7A9` | 2 | transport/diagnostic route 1 |
| `0x0802` | `0x7A8` | 2 | transport/diagnostic route 2 |
| `0x0803` | `0x7A8` | 2 | transport/diagnostic route 3 |
| `0xF800` | `0x7F8` | 5 | special bidirectional channel Tx route |

The adjacent record at `0x21F70` is **not** a second active Tx record. It is the
match table selected by receive-class descriptor `0x21AC4`, whose upper callback
is `0x82042`; acceptance rule 50 supplies CAN `0x7F7`. That callback reaches the
special protocol receive path through `0x81FE4 -> 0x81F00`. On the transmit
side, the same protocol state machinery calls `0x8206C`, which explicitly ORs
source PDU class `0xF800` and calls `application_canif_transmit`; class 5 has one
active Tx record, `0x21F68 -> CAN 0x7F8`. This proves a paired **Rx `0x7F7` / Tx
`0x7F8` special transport channel**. The application-level service semantics of
that channel remain unnamed.

## 3. Six COM transmit I-PDUs

The first six records at `0x2273C` provide the cyclic count and length. Buffer
offsets at `0x228E4` are contiguous: `0, 8, 16, 20, 23, 31`.

| COM Tx PDU | CAN ID | Length | Cycle count | RAM buffer | Generated packer | Signal IDs |
|---:|---:|---:|---:|---:|---:|---|
| 0 | `0x260` | 8 | 4 | `0xFEBE4A49` | `0x4BCEE` | 0–9 |
| 1 | `0x262` | 8 | 8 | `0xFEBE4A51` | `0x4BE24` | 10–37 |
| 2 | `0x351` | 4 | 200 | `0xFEBE4A59` | `0x4C25C` | 38–39 |
| 3 | `0x394` | 3 | 60 | `0xFEBE4A5D` | `0x4C158` | 40–45 |
| 4 | `0x4A3` | 8 | 100 | `0xFEBE4A60` | `0x4BB1E` | 46–53 |
| 5 | `0x4C8` | 8 | 196 | `0xFEBE4A68` | `0x4BC54` | 54–57 |

“Cycle count” is the raw COM main-function count. The scheduler tick period has
not been calibrated, so these values must not be silently relabeled as
milliseconds.

The initial 39 transmit-buffer bytes at `0x221DC` are:

```text
260: 0E 00 00 00 00 00 00 00
262: 10 00 00 00 00 FF FF 00
351: 00 00 00 00
394: 00 00 00
4A3: 00 00 00 00 00 00 00 00
4C8: 09 00 00 00 00 00 00 00
```

## 4. COM signal-to-wire map

`application_com_pack_big_endian_signal @ 0x7C232` writes a big-endian bit
field into the COM buffer. `B0` means the first transmitted byte and `B0[7]`
means its most-significant bit. Multi-byte integer fields below are serialized
big-endian.

The firmware contains no AUTOSAR symbolic names. Signal numbers are therefore
the generated IDs present in this exact image. The complete CSV also carries
every RAM source address.

### 4.1 CAN `0x260` / COM PDU 0

Public Toyota DBCs call this message `STEER_TORQUE_SENSOR`. The wire positions
of the three 16-bit fields and the two legacy named status bits align with this
firmware, but the producer audit now distinguishes **wire-position
corroboration** from what this exact calibration actually computes. In
particular, the public `STEER_OVERRIDE` position is not backed by an active
threshold producer here: its recovered producer graph is constant-clear.

| Signal | Wire field | Source | Firmware-first static interpretation |
|---:|---|---:|---|
| 0 | `B0[7]` | `0xFEBE8094` | constant-clear in the recovered producer graph; public DBC location is `STEER_OVERRIDE` |
| 1 | `B0[4]` | `0xFEBE8096` | composite initialization/validity flag; public DBC calls this `STEER_ANGLE_INITIALIZING` |
| 2 | `B0[3]` | `0xFEBE8098` | debounced steering-control consistency status |
| 3 | `B0[2]` | `0xFEBE8099` | operational-mode/status inhibit A |
| 4 | `B0[1]` | `0xFEBE809A` | operational-mode/status inhibit B |
| 5 | `B0[0]` | `0xFEBE809B` | thresholded motor-feedback magnitude status |
| 6 | `B1..B2` | `0xFEBE810A` | scaled/clamped sensor torque; public DBC `STEER_TORQUE_DRIVER` |
| 7 | `B3..B4` | `0xFEBE810E` | saturated signed steering-control estimate; public DBC `STEER_ANGLE` |
| 8 | `B5..B6` | `0xFEBE8110` | scaled motor-feedback torque estimate; public DBC `STEER_TORQUE_EPS` |
| 9 | `B7` | `0x7FEAC` post-packer callback | additive Toyota checksum |

The status-bit producer graph is compact and explicit. Signal 0 follows
`FEBEAD33 -> FEBEE830 -> FEBE8094`; `eps_subsystem_init_orchestrator @ 0xBD10E`
and normal `steering_command_export_scale @ 0xCB700` both write the upstream
byte as zero, and the live-project reference census finds no other direct
producer. This is why the legacy `STEER_OVERRIDE` name is retained only as a
DBC wire-position label, not as a claim that this Sienna emits the historical
driver-threshold behavior on that bit.

Signal 1 is synthesized in `0x4B66C`: three local validity fields must be zero
and three snapshotted status bytes are compared against marker `0x22`. That
firmware behavior independently supports the DBC's initialization/validity
category without importing an OEM name for the underlying status bytes.
Signal 2 is sourced from `FEBEC100`, a steering-control consistency state
initialized asserted and maintained by `0xC9D7C` with an absolute-difference
threshold of **524** and a **40-count** persistence threshold before export via
`FEBEAD4B -> FEBEE83A`.

Signals 3 and 4 are separate inhibit predicates generated directly by
`0x4B66C`. Both mask the current system mode to `0xFF00`, explicitly recognize
modes `0x400` and `0x500`, special-case transition phase `0x11`, and test the
low nine bits of `0xFEBE673C`; signal 4 additionally requires
`0xFEBE6738 == 0` for its non-inhibit state. The exact OEM meanings of those two
input status objects remain unresolved, so the two output bits are deliberately
left with bounded structural names.

Signal 5 is not an arbitrary spare bit. Its chain is
`FEBE6DA8 -> FEBEEC0C -> FEBEAFE0 -> FEBEB725 -> FEBEB724 -> FEBEE848 ->
FEBE809B`. `0x37F86` derives `FEBE6DA8` from the already recovered d/q-feedback
state (`FEBE6D20`, `FEBE6D18`) through calibrated lookup/interpolation;
`0xBC9DC` takes its signed magnitude and compares it against calibration
thresholds **5120 / 2560**, and `0xBCA28` publishes the resulting threshold
state. The OEM label for the final bit remains unknown.

The three 16-bit fields now also have firmware-side support independent of the
DBC. Signal 6 selects between two signed sensor paths before `0x4B66C` scales by
`100/256` and clamps to **-700..700**. Signal 7 comes from saturated signed
steering-control difference state `FEBEC0FC`, exported through
`FEBEAE5C -> FEBEE8BC`. Signal 8 originates in the high-rate motor-feedback
path above, reaches `FEBE66F0`, and is negated/scaled by `100/128` before
packing. Those structures support the public driver-torque, steering-angle,
and EPS-torque roles respectively, while the public names remain corroborating
vocabulary rather than the primary proof.

Signal 9 is intentionally absent from `application_pack_can_260`: after the
packed eight-byte buffer reaches CanIf, PDU-0 route flag `1` selects
`0x800D2 -> 0x7FEAC`, which overwrites the final byte with the additive checksum
described in §4.7. `AssertApplicationTransmitSemantics.java` pins the live
reference/call graph, while `verify_application_tx_260_semantics.py` derives
the decisive predicates, scaling instructions, thresholds, and zero stores
independently from raw CodeFlash.

### 4.2 CAN `0x262` / COM PDU 1

Public Toyota DBCs call CAN `0x262` `EPS_STATUS`, but this calibration has a
richer 28-signal decomposition than the public generic definitions. Only the
message name and last-byte checksum convention are used as corroboration; OEM
names are not invented for the remaining fields.

```text
B0: s10[7] s11[6] s12[5] s13[4]=0 reserved[3] s14[2] s15[1] s16[0]
B1: s17[7] s18[6] s19[5] s20[4] s21[3] s22[10:8]
B2: s22[7:0]
B3: s23[7] s24[6] s25[5] s26[4] s27[3] s28[2] s29[1] s30[0]
B4: s31[7] s32[6] s33[5] s34[1:0] at bits [4:3], bits [2:0] reserved
B5: s35
B6: s36
B7: s37 (post-packer additive checksum from 0x7FEAC)
```

Signals 10–12, 14–21, and 23–36 use the exact RAM sources listed in the CSV.
Signals 13 and 22 are explicitly packed from zero-valued staging fields.

### 4.3 CAN `0x351` / COM PDU 2

Only two configured signals are packed:

| Signal | Wire field | Source |
|---:|---|---:|
| 38 | `B2[7:5]` | `0xFEBE80B8` |
| 39 | `B2[4]` | `0xFEBE80B9` |

Bytes 0, 1, and 3 initialize to zero. Their runtime semantics remain unresolved.

### 4.4 CAN `0x394` / COM PDU 3

| Signal | Wire field | Source |
|---:|---|---:|
| 40 | `B0[6:4]` | `0xFEBE80BA` |
| 41 | `B0[1:0]` | `0xFEBE80C2` |
| 42 | `B1[7:6]` | `0xFEBE80BD` |
| 43 | `B1[2:0]` | `0xFEBE80BE` |
| 44 | `B2[3:1]` | `0xFEBE80BF` |
| 45 | `B2[0]` | `0xFEBE80C1` |

Unassigned bits remain at their initialized zero values unless another runtime
path changes the buffer; no such static producer was recovered.

### 4.5 CAN `0x4A3` / COM PDU 4

Signals 46–53 are eight direct bytes:

```text
B0..B7 <- 0xFEBE80C3..0xFEBE80CA
```

The packer at `0x4BB1E` copies each source byte and invokes the COM big-endian
packer with widths of eight bits. OEM field semantics remain unresolved.

### 4.6 CAN `0x4C8` / COM PDU 5

| Signal | Wire field | Static source |
|---:|---|---|
| 54 | `B0` | constant `0x09` |
| 55 | `B1[7]` | constant zero |
| 56 | `B2..B3` | constant zero 16-bit value |
| 57 | `B4..B7` | initial/default zero only |

Signal 57 is assigned to PDU 5 by the raw signal map, but the generated packer
`0x4BC54` writes only signals 54..56. The PDU descriptor flags are `0x03`, so
neither COM pre-transmit transform class (`0x10/0x20`) is enabled; the PDU-5
CanIf route flag at `0x21FE0+5` is zero, so the lower post-packer callback is also
skipped; the subsequent queue/driver path copies rather than synthesizes data.
The initial bytes `B4..B7` are all zero. Therefore signal 57 is **default-only
zero in this calibration**. This does not claim the generated configuration
could never be used by another calibration.

### 4.7 Post-packer checksum callback (`0x260` / `0x262`)

`application_can_tx_enqueue @ 0x7EC5A` invokes controller-0 hook `0x800D2`
before placing the frame on the software queue. The six COM route flags at
`0x21FE0` are exactly `1,1,0,0,0,0`; only PDU 0 (`0x260`) and PDU 1 (`0x262`)
therefore dispatch through controller callback `0x7FEAC`. Its 70-byte body is
pinned by SHA-256
`0e077cd8d1f3c22b7fe2c1478e98a44e2d05f0c7febfa45e9385a5181607c8f1`.

For a standard CAN frame, the callback computes:

```text
checksum = (DLC + sum(CAN_ID bytes) + sum(payload[0:DLC-1])) & 0xFF
payload[DLC-1] = checksum
```

That is independently the checksum function used by the pinned Toyota opendbc
source. In this firmware it resolves configured signals **9** and **37** as
lower-stack checksum fields rather than ordinary COM packer outputs.

## 5. Confirmation path

The application uses RSCAN CAN1 and EIINT 188, already established in
`../architecture/firmware-architecture.md`:

```text
EIINT 188
  -> application_can1_tx_isr                @ 0x65028
  -> adapter                                @ 0x65770
  -> application_can1_tx_interrupt_body     @ 0x8474E
  -> application_rscfd_tx_confirmation_dispatch @ 0x84710
  -> release hardware/software Tx state
  -> application_canif_tx_confirmation      @ 0x7F002
  -> generated upper-PDU confirmation callback
```

`application_canif_get_tx_can_id @ 0x7E5F2` resolves the same generated source
PDU to the first word of its eight-byte CanIf record. This independently ties
the route IDs to the CAN identifiers instead of treating the ID-looking words
as unreferenced constants.

## 6. Evidence boundaries and external naming

Core conclusions—counts, table addresses, IDs, lengths, cyclic counts, signal
membership, bit packing, RAM sources, initial bytes, and call chain—come from the
committed CodeFlash and do not require an external checkout.

The names `STEER_TORQUE_SENSOR`, `STEER_OVERRIDE`,
`STEER_ANGLE_INITIALIZING`, `STEER_TORQUE_DRIVER`, `STEER_ANGLE`,
`STEER_TORQUE_EPS`, `EPS_STATUS`, and `CHECKSUM`, plus the checksum arithmetic,
are optional corroboration from commaai/opendbc at pinned commit
`c9b31d21bc396e8958891e271936bdbdf1a6ca93`. They are used only where the public
bit layout agrees. All other generated signals remain explicitly anonymous.

No claim is made that:

- the raw cycle counts are milliseconds;
- CAN `0x351`, `0x394`, `0x4A3`, or `0x4C8` have recovered OEM message names;
- signal 57 has an OEM semantic beyond its recovered default-zero behavior;
- the `0x7F7/0x7F8` special channel has a recovered Toyota service/protocol name.
