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
`0x7F8` special transport channel**. Its XCP-shaped command semantics and
security impact are analyzed in
[xcp-command-dispatch.md](xcp-command-dispatch.md).

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
reference/call graph, while `verify_application_tx.py` derives
the decisive predicates, scaling instructions, thresholds, and zero stores
independently from raw CodeFlash.

### 4.2 CAN `0x262` / COM PDU 1

Public Toyota DBCs call CAN `0x262` `EPS_STATUS`. Here the public field geometry
is unusually useful because it aligns exactly with the finer generated signal
split recovered from this image:

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

The pinned public DBC defines `IPAS_STATE` as B0[3:0], `LTA_STATE` as B1[7:3],
`TYPE` as B3[0], and `LKA_STATE` as B3[7:1]. The firmware producer graph now
supports those aggregate boundaries independently; the public enum strings are
still treated as corroborating vocabulary rather than primary proof.

**B0 / `IPAS_STATE`.** Runtime producer `0x4B90A` explicitly clears signals
10–12 and 14–16 on every staging update. Signal 13 is an immediate zero in the
packer and B0[3] is unassigned/reserved, so the public four-bit `IPAS_STATE`
field is **0 in this calibration's recovered runtime producer**, and the whole
packed B0 becomes zero after the first normal staging/pack cycle. This is
stronger than the power-on image (`0x10`), whose B0[4] default is overwritten by
the generated packer.

**B1 / `LTA_STATE`.** Signals 17–21 are exactly the public five-bit field,
ordered bit4..bit0. They are not opaque packet bits: the normal command/state
export path supplies internal states `FEBEC12E`, `FEBEC0E2`, `FEBEC0E3`,
`FEBEC12F`, and `FEBEC130`, which are snapshotted and copied into B1[7:3]. The
producers show distinct roles: bit4 ORs two internal status flags; bit3 is a
recovery/timeout latch; bit2 is the steering-control active-state latch; bit1
ORs three condition flags; and bit0 is a base-eligibility predicate requiring
one source state plus the low nine status bits to be clear. The bit0 value also
passes through `0x4B92C`, which suppresses it when `0xFEBE7426 == 0x5A`.
Signal 22 is an immediate-zero 11-bit field covering B1[2:0] and all of B2, so
B2 is always zero in the recovered normal producer.

**B3 / `LKA_STATE` + `TYPE`.** Signals 23–29 line up exactly with public
`LKA_STATE` bit6..bit0. The high two bits (signals 23/24) are zeroed every cycle;
the five dynamic low bits are exported from `FEBEBF7B`, `FEBEBFA7`,
`FEBEBFA6`, `FEBEBFA5`, and `FEBEBFA9`. Their firmware structure is state-like:
bit4 is an OR aggregate, bit3 is a timed recovery latch, bit2 is an active-state
latch, bit1 is a timeout/availability status, and bit0 uses the same
base-eligibility predicate as the `LTA_STATE` low bit before the same `0x4B92C`
gate. This bit structure is consistent with the public odd-valued LKA state
enums (`1/3/5/9/11/17/25`) without using those strings as proof of individual
internal conditions. Signal 30 is B3[0], exactly the public one-bit `TYPE`
location, and `0x4B754` writes it **zero** every cycle in this calibration.

**B4–B6.** These bytes are absent from the public generic EPS_STATUS definition,
but they are also no longer opaque. Signals 31/32 are copied from
`FEBEC0D8/0D9`, two threshold/limiter flags produced by `0xC96D2`; signals
33/34 come from `FEBEC0FE/0FF`, a transition latch plus two-bit transition code
maintained by `0xC9CA8`. B4[2:0] is reserved zero. Finally, `0x4B920` explicitly
writes `0xFF` to the signal-35 and signal-36 staging bytes every cycle, so B5
and B6 are constant `FF` in the recovered normal producer.

Signal 37 remains the CanIf additive checksum at B7. The raw verifier
`verify_application_tx.py` pins the producer instructions and the
public field geometry, while `AssertApplicationTransmitSemantics.java` now
locks all 25 RAM-backed `0x262` staging-reference sets plus the decisive
state-source relationships against the live Ghidra project.

### 4.3 CAN `0x351` / COM PDU 2

Only two configured signals are packed, but their producer is now joined to the
already-recovered plausibility/debounce monitor family:

| Signal | Wire field | Source | Firmware-first role |
|---:|---|---:|---|
| 38 | `B2[7:5]` | `0xFEBE80B8` | filtered plausibility-monitor status code; system-gated override value `7` |
| 39 | `B2[4]` | `0xFEBE80B9` | system-gated override flag |

`plausibility_fault_debounce_monitor` writes its final boolean status at
`0xFEBEB5F8`; `application_input_snapshot_update` copies that byte to
`0xFEBEE82B`; and `0x4B82C` applies a seven-count hold/filter before passing the
result to `0x4B882`. Under the normal gate this yields the filtered monitor
state. If `(0xFEBE673C & 3) != 0` and `0xFEBE80FB != 0`, `0x4B882` instead forces
signal 38 to `7` and signal 39 to `1`; otherwise signal 39 is zero.
`0xFEBE80FB` is itself set to the marker `0x5A` when bit `0x8000` is present in
the system input consumed by `0x3BE82`. The exact OEM meaning of that gate is
not recovered, so the packet is described structurally rather than named from
speculation. Bytes 0, 1, and 3 remain zero.

### 4.4 CAN `0x394` / COM PDU 3

All six fields are generated from a table-driven internal status state:

| Signal | Wire field | Source | Firmware-first role |
|---:|---|---:|---|
| 40 | `B0[6:4]` | `0xFEBE80BA` | state-table tuple byte 0 |
| 41 | `B0[1:0]` | `0xFEBE80C2` | coarse internal-state class code |
| 42 | `B1[7:6]` | `0xFEBE80BD` | state-table tuple byte 4 |
| 43 | `B1[2:0]` | `0xFEBE80BE` | state-table tuple byte 1 |
| 44 | `B2[3:1]` | `0xFEBE80BF` | state-table tuple byte 2 |
| 45 | `B2[0]` | `0xFEBE80C1` | state-table tuple byte 3 |

`FUN_00050268` evaluates a fault/status decision tree into an internal state
stored at `0xFEBE8258`, normally in the range **1..16**. It indexes the exact
17×5-byte table at `0x2A33C` with `state * 5` and writes the selected tuple to
`0xFEBE8266/8262/8263/8264/8265`. `0x4B8B6` then maps those five tuple bytes to
signals 40 and 42–45 and compresses the state itself into signal 41:

```text
state 5       -> class 1
state 15      -> class 2
other 1..16   -> class 3
0 / >16       -> class 0
```

The table values and state-class arithmetic are pinned directly from CodeFlash.
The legacy Toyota reference DBC also contains decimal CAN 916 (`0x394`) as the
one-byte CGW message `EPS1S90`; that is not structurally the same three-byte EPS
packet and is therefore **not** used to name these fields. Unassigned wire bits
remain zero.

### 4.5 CAN `0x4A3` / COM PDU 4

This packet is a compact mixed steering-telemetry export rather than eight
opaque bytes:

| Signal | Wire field | Firmware-first role |
|---:|---|---|
| 46 | `B0` | CAN `0x260` initialization/validity staging flag OR `0x20` |
| 47 | `B1` | incoming CAN `0x025` signal 221, signed 12-bit mirror bits 11:8 |
| 48 | `B2` | incoming CAN `0x025` signal 221 mirror bits 7:0 |
| 49 | `B3` | clamped signed-12 delta `(0x025 s221 - 0x64F s289)` bits 11:8 |
| 50 | `B4` | same delta bits 7:0 |
| 51 | `B5` | signed-byte conversion of CAN `0x260` driver-torque staging / 10 |
| 52 | `B6` | CAN `0x260` EPS-torque staging mirror, high byte |
| 53 | `B7` | CAN `0x260` EPS-torque staging mirror, low byte |

The two incoming fields are already independently mapped by the Rx pipeline:
signal 221 is a signed 12-bit field from FD CAN `0x025` into `0xFEBE801C`, and
signal 289 is a signed 12-bit field from classic CAN `0x64F` into
`0xFEBE807C`. `FUN_0004703E` computes `s221 - s289`, saturates the intermediate,
and stores it at `0xFEBE7CE6`; the `0x4B7BA` Tx producer clamps that value again
to **-2048..2047** before packing B3/B4. B1/B2 re-encode signal 221 directly.
This is therefore an explicit verified **Rx→Tx state join**, not merely a shared
RAM-address coincidence.

The same producer also reuses states recovered for `0x260`: B5 derives from the
driver-torque staging word after division by 10 and signed-byte saturation,
while B6/B7 are the exact high/low bytes of the EPS-torque staging word. No
matching modern Toyota `0x4A3` definition was found in the pinned public DBC
corpus, so these fields keep firmware-derived structural descriptions rather
than invented OEM names.

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

### 4.8 Cross-interface Rx→Tx joins

`data/application_interface_state_joins.csv` records the currently proved
application-facing joins rather than treating the Rx and Tx maps as unrelated
AUTOSAR plumbing:

1. incoming CAN-FD `0x025` signal **221** (signed 12-bit,
   `0xFEBE801C`) is repacked directly into CAN `0x4A3` B1/B2;
2. the same signal minus incoming CAN `0x64F` signal **289** (signed 12-bit,
   `0xFEBE807C`) is computed/saturated by `0x4703E`, clamped to signed-12 by
   `0x4B7BA`, and exported in `0x4A3` B3/B4;
3. authenticated CAN `0x2E4` signal **61** (signed B1..B2) follows the already
   recovered command-conditioning chain through `0xFEBE7F94 -> 0xFEBEF184 ->
   0xFEBEAE20`. In parallel with the torque clamp/rate-limit path, `0xC8072`
   evaluates that scaled command with steering-control state and writes predicate
   `0xFEBEBF74`; `0xC8280` combines it with companion status into
   `0xFEBEBF7B`, which is exported through `0xFEBEACF6 -> 0xFEBEE844 ->
   0xFEBE80A3` to CAN `0x262` B3[5], **bit4 of public `LKA_STATE`**.

The third relation is deliberately phrased as *command contributes to visible
status*, not `status = command`: `0xC8072` has additional state inputs. It does,
however, establish a firmware-static authenticated-command→external-status edge.
The raw path is pinned by `verify_application_interface_state_joins.py`; the
exact live-project reference sets are pinned by
`AssertApplicationInterfaceStateJoins.java`.

Techstream supplies independent vocabulary/shape corroboration for the command
side, but not a new firmware edge. Master-routed `EMPS_P5.ddb` monitor 402 is
`Command Value Torque`, is 16 bits wide, and resolves to unit `Nm`; this is
accepted as corroboration for the recovered authenticated steering-command
domain. `Cooperation Control State` (monitor 60) remains ambiguous relative to
the `0x262` LTA/LKA bits, and generic 16-bit `Control State Information`
(monitor 403) is explicitly rejected as a direct name for any specific Tx
field. See [techstream.md](../tooling/techstream.md) §6.2.1 and the deterministic
`application_interface_correlations.json` artifact. The underlying command-
conditioning ownership remains canonical in
[control-partition.md](../architecture/control-partition.md) §8.

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
- the XCP-shaped `0x7F7/0x7F8` channel has a recovered Toyota OEM name.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [COM-003](../reference/index.md#finding-com-003)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
