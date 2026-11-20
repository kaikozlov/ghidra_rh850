# yc R4P 2024 meter firmware

## Specimen

Registered target: **`r4p-838004AD91`**, reference role, software identifier
`838004AD9110` at CodeFlash `0x156898`.
The [canonical artifacts](../../firmware/r4p-838004AD91/README.md) record
the hashes, mapped bases, and original `community/yc/r4p/meter/` captures.

Toyota lists assembly **`83800-4AD91`** as component 55 in its
[12.3-inch combination-meter report](https://static.nhtsa.gov/odi/rcl/2025/RCLRPT-25V595-0339.pdf)
(RAV4 Prime on p. 3, DENSO on p. 8, part number on p. 15). The dumps cover
the RH850's CodeFlash, BootFlash and DataFlash.

## How the meter works in normal operation

The RH850 calculates the instrument readings, reads local sensors and
steering-wheel switches, and plays warning sounds. Over SPI it sends a
display-side device both processed values (including trip distance in
tenths) and copies of selected CAN frames. The route and callback counts
below come from this specimen's flash.

| What was counted | Coverage | What the rows tell us |
|---|---|---|
| [Main cyclic callbacks](../../data/targets/r4p-838004AD91/cyclic_callbacks.csv) | 66; 42 confirmed operations, 24 partial | Which work the timer releases: instruments, sound, display exchange, timekeeping, supervision and nested workers. [Reset and scheduling](#from-reset-to-recurring-work) and [shutdown/wake](#run-shutdown-and-wake) explain when that work runs. |
| [CAN receive routes](../../data/targets/r4p-838004AD91/can_receive_routes.csv) | 171; 97 copied into the raw SPI record | Which controller and buffer own a received frame, and whether the [display link](#the-display-link) also carries a raw copy. |
| [CAN transmit routes](../../data/targets/r4p-838004AD91/can_transmit_routes.csv) | 54; 51 application, 3 service/diagnostic | Which frames the meter can originate, on which internal controller, and under which [COM group masks](#configured-can-publications). |
| [Application diagnostic identifiers](../../data/targets/r4p-838004AD91/application_did_inventory.csv) | 74; 34 with an ordinary value callback | Which named diagnostic displays have a value reader, a feature/support reader, or only a catalog label. |

### What a passive openpilot port can use

At the [project's opendbc pin](../architecture/toyota-openpilot-porting-contract.md#upstream-prior-art),
[`values.py`](https://github.com/commaai/opendbc/blob/c9b31d21bc396e8958891e271936bdbdf1a6ca93/opendbc/car/toyota/values.py#L280-L291)
lists RAV4 Prime 2021–23 and RAV4 Hybrid 2023–25 separately. For this
2024 Prime, three comparisons matter:

| openpilot observation | Evidence from this meter | Passive check on the vehicle |
|---|---|---|
| Cluster speed | The pinned [Toyota `CarState`](https://github.com/commaai/opendbc/blob/c9b31d21bc396e8958891e271936bdbdf1a6ca93/opendbc/car/toyota/carstate.py#L83-L94) uses four wheel speeds and estimates `vEgoCluster` as `vEgo × 1.015`. Here `0x610` B2 republishes rounded, uncorrected km/h from `0x0D7`; [`0x376`](#speedometer-input-and-display-correction) carries the calibrated speed, unit and unavailable code. | Record wheel speeds and all three frames alongside the dashboard during acceleration and deceleration to capture the meter's filter and hold behavior. |
| Steering buttons and cruise | The meter [assembles `0x24D`](#0x24d-application-producer) from CXPI switch data and local status; the pinned DBC names the sender `PCM`. [`0x399`](#cruise-lane-and-collision-warning-presentation) supplies displayed set speed. | Correlate button presses, displayed set speed and cruise engagement as separate observations. |
| Body state and distance | The meter publishes [turn/hazard state](#body-inputs-turn-hazard-doors-and-buckle) and the [selected-unit odometer](#odometer-and-trip-distance). | While parked, compare left, right and hazard separately; change one door or buckle at a time; compare `0x611` before and after changing units. |

For these comparisons, record the physical bus tap and synchronize CAN
timestamps with a dashboard recording. The registered capture contains flash only.

### Cruise, lane and collision-warning presentation

Scheduled worker `0x4F386` (row `0x157F44`, mask `0x40`) builds the
processed indications. The raw SPI record also carries the original frames:

| Received on firmware channel 0 | Raw SPI payload start | What the meter computes for the processed record |
|---|---|---|
| `0x399`, B3 (`UI_SET_SPEED` in the pinned DBC) | `+0x2B0` | `0x4F49C` reads B3 and a companion flag on a valid receive. `0x4EA70` qualifies the value without unit conversion; `0x13C16..0x13C2E` packs it in `+0x4A0[31:16]`, with the companion in bits 15:8. With presentation mask `0x200` absent the value is `FFFF`. |
| `0x412`, B0 bits 5:4 and 3:2 (`LEFT_LINE`, `RIGHT_LINE`) | `+0x1D8` | `0x4F688` repacks the two lines and other fields. On initial reception state or timeout the consumer can retain earlier payload bits with updated status. Classifier `0x4E96C` uses the line fields **and** status; the processed record carries resulting flags at `+0x498/+0x49C` and group validity at `+0x4A8[15:8]`. |
| `0x411`, including B0 bits 7:6 (`PCS_INDICATOR`) | `+0x1D0` | `0x4F944` combines the PCS input and independently qualified `0x3B7` B1 bits 4:3. The selector table at `0x15E5A4` consumes its cached output for the processed SPI record. |

Signal names in parentheses come from the pinned DBC. Monitor group `0x154528`
combines `0x411`, `0x412` and `0x489` into event 15, DTC row `0x172DFC`,
**U023A87 — Lost Communication with Image Processing Module “A”**.

DID `0x15A1` reads cached feature-presence flags for LDA, PCS and radar
cruise (`0x28652`). The catalog labels DID `0x2951` **SET Indicator**;
its dispatch row at `0x156DE0` has a zero support mask and a null reader.

### Body inputs: turn, hazard, doors and buckle

**The meter publishes `0x614` on controller 0.** COM PDU 6 maps to lower
TX row `0x1B` (`0x170DDA → 0x170624`). COM PDU `0x1B` is a separate
CXPI-derived publication: lower row `0x14`, CAN `0x529`.

| Observation | Source → normal application → output |
|---|---|
| Directional turn | `0x5BB94` checks receive status and reads two bit pairs in channel-0 `0x2D8` B5[3:0]. `0x5BC36/0x5BD1C` qualify the events; `0x6ABDA` packs `0x614` **B3[5:4]**. Sustained directional events produce codes 1 and 2; the left/right labels come from the pinned DBC. |
| Hazard | `0x59D46` qualifies local switch `0x7C240(0x13)` and updates a latch. `0x5BA70` combines it with an auxiliary state; `0x6AC28` packs the result in `0x614` **B3[3]**. |
| Doors | Five getters at `0x6CDE8..0x6CE88` read channel-0 `0x620` B5[5:1]. After checking receive status, `0x5B060` sets one flag if any input is active. `0x1537A` copies B5 to raw SPI `+0xC6`. The older DBC assigns individual door corners to bits 5:2. |
| Driver buckle | Active-low `PPR17` bit 4 supplies local input `0x7C240(0x0E)`, read by `0x3D944`. It also supplies DID `0x1101` B1 mask `0x40`, **Driver Buckle Switch** (`1` = not fastened). |

`Meter_P5` names both local switches. The `0x1101` reader `0x2849C` uses
callback rows `0x1576D4` (buckle) and
`0x1576EC` (hazard, `PPR0` bit 4, DID B3 mask `0x02`). Only callback
result `1` sets the diagnostic bit; invalid local input also reads as
zero. In contrast, the catalog's **Parking Brake Switch** entry for
`0x1401` has a null callback at `0x15785C`. `0x620` B7 bit 4 has an
active consumer (`0x6CEB0 → 0x52FAA` in dataflow order), but the parking-brake
meaning comes from the comparison DBC alone.

### Configured CAN publications

`0x9DD00` indexes the six lower TX domains by the pointers at `0x16D0E0`
and row counts at `0x16D160`. Domain 0 contains all 51 application rows:
**34 on controller 0, 17 on controller 1**, 44 distinct IDs. Seven IDs are
used on both controllers (`0x520/521/522/524/525/526/527`), with separate
COM buffers. The other populated domains contain `0x442` (service) and
`0x7C8/0x7CA` (diagnostic transport).

The sender `0x9D122` uses `0x16FBF0` for buffer offsets and `0x16F3BC`
for lengths. `0x9CE26` requires the PDU's configured group mask to overlap
the active mask. Fifteen rows can match the initial `0x01` bit; the other
36 require an additional mode bit. This includes indicated speed `0x376`
and every controller-1 row. On controller 1, `0x500` takes words from the
alternate SPI peer record (`0x140B2 → 0x154CA`); `0x62FB4` conditionally
packs record-state fields for `0x520..0x526`.

### Where the text and sound are

The [RAV4 Prime owner's manual, p. 203](https://assets.sia.toyota.com/publications/en/om-s/OM42E79U/pdf/OM42E79U.pdf)
names distinct screens for information since hybrid-system start and since a
trip reset. We searched all three images for 15 actual English labels:
`Drive Info Items`, `TRIP A Items`, `TRIP B Items`, `Total Time`, `Eco Score`,
`Energy monitor`, `Language`, `Units`, `Brightness`, `Charging Schedule`,
`Fuel Economy`, `Power Consumption`, `Trip Average`, `Closing Display` and
`Refuel`. **Zero matches**, case-insensitive, at any byte offset in ASCII
or UTF-16/32, either byte order, without requiring a terminator.

CodeFlash nevertheless has **704** printable ASCII runs of eight or more
characters (`[ -~]{8,}`); BootFlash and DataFlash have none at that threshold.
Most long text is audio middleware: of 171 runs of at least 24 characters,
160 start in `0x166000..0x16CFFF` and five in the audio assets below.
All 14 case-insensitive `READY` hits occur inside `already`. `Unknown Warning`
at `0x16B6C6` goes to an audio error reporter. The 892-character apparent
UTF-16LE string at `0x16E76A` is part of a numeric CAN lookup table: `0x9C67C`
indexes it by signal ID. The real ASCII `838004AD9110` at `0x156898` is copied
into an identity record by `0x27174`.

Audio initializer `0x17172` passes three adjacent regions and their lengths to the playback library
(`0x1726E..0x172C0`; ends exclusive):

| CodeFlash range | Asset | How the firmware uses it |
|---|---|---|
| `0xE7824..0xE8C64` | CRI Atom Automotive configuration | `0x8832E` checks `@UTF`; the tables name DSP settings and controls. |
| `0xE8C64..0x14B288` | `AFS2` wave bank | `0x890AE` opens it. Its directory has eight slots, IDs 0–7, with 32-byte alignment. |
| `0x14B288..0x14F184` | `CACB` cue data | `0x88D9E` associates it with the bank. `0x17480` supplies the handle and numeric cue ID; `0x87C42` checks the ID and starts playback. |

The image search found no PNG signature, valid BMP header or JPEG
start-of-frame header. The location of display assets remains open.

### Who chooses the sound

There are two playback paths. For general reminders, `0x790A4` polls
the non-null callbacks in a 137-row request table at `0x164CC4`.
`0x7A050` finds the lowest eligible request bit; the current request,
age and playback state also enter the selection (`0x7A0A2/0x7A14E`).
`0x174AC` maps the selected request through `0xE73D0` to a cue and gain
on player 0. For example, a seatbelt-family reminder predicate at
`0x3069E` maps through row `0x164D9C` to request `0x1B`, then through
`0xE74A8` to cue `0x08`.

The flasher uses **player 1**. Worker `0x5A580` maintains its own
phase. `0x30966/0x30A3C` distinguish onset from finish; the calls at
`0x175EA/0x17600` start cues `0x38/0x39`. Saved **Flasher Sound Volume
Adjust** sets the gain. The driver writes audio samples
to `PCMP0AUSA` at `0xFFF10018` (`0x17160/0x17162`; D1L/D1M manual,
pp. 2585–2586). In parallel the flasher worker feeds local port handling
and a two-side state in processed SPI word `+0x3B0`, bits 5:4.

### From reset to recurring work

On the application path the reset jump at `0x0 → 0xEE8` eventually reaches
`0xBA0`, which reads the entry pointer `0x1FFFE0 = 0x10634`. `0xF9C` jumps
to that entry. Application reset installs its own stack and vector table,
then transfers through `0x10B28` to `0x83E88`. The stage walker `0x83E2A`
reads 54 action/selector pairs at `0x16607C`. Stage 10 initializes application
RAM as [described below](#normalization-and-analysis-model); stage `0x21`
enters the foreground loop via `0x84EDC → 0x842A8`.

OSTM0 releases one timer interrupt per 150,000 timer clocks
(descriptor `0x157D74`, compare store `0x7D6F4`).
IRQ `0x7D` advances a 20-slot schedule at `0x157D94`, ORs the slot's mask
into a pending word, and requests IRQ `0xA8`. Handler `0x8424A` switches
pending banks and calls matching rows of `0x157DE4` in order. That table
releases SPI service `0x15BA2` and packet builder `0x15BD2` every **two**
intervals, and speed processing `0x57D20` every **four**. Pending bits can
coalesce; converting these intervals to elapsed time requires the board clock.

The main callback table ends at the first null pointer (`0x157FF4`;
dispatcher `0x84278..0x8429C`, eight-byte stride). It includes an immediate
return (`0x56E34`) and a worker with an empty list (`0x83720`). Nested
workers have their own tables: `0x770DE` dispatches another 13 rows using
the same pending mask. Foreground, receive and DMA handlers run separately.

### Run, shutdown and wake

Bit `0x40` of the operating-state word represents the qualified local
supply voltage. `0x17C42` accepts ADC sample 0 at **357–1,023** counts;
`0x7C1B4` qualifies input 0, `0x167A2` sets the bit as part of the
`0x16874` update, and `0x168AA` tests the cached word. The same ADC sample
feeds DID `0x1021` **+B Voltage** (`0x27F9A`).

Stage `0x21` rotates three foreground callbacks independently of timer
releases. Its exit qualifier `0x83C98` combines eight predicates, pending
wake state and a 3,000-call threshold. Audio playback and pending storage
work participate; `0x83D06` checks for wake again before exiting. Subsequent
stages stop ADC and OSTM, configure wake sources and request hardware
**DEEPSTOP** (`0x7E6EC`, descriptor `0x165CEC`). Hardware wake restarts
at the reset vector. Ordinary RAM is reinitialized; wake scratch and
trip baselines have separate retention-RAM storage. The power-on-clear
test at `0x1077A` and the retained marker checks at `0x83C0A` distinguish
retention through standby from durability through complete power loss.

### Odometer and trip distance

CAN `0x0D7` bytes 1–2 carry the speed used by the
[speedometer](#speedometer-input-and-display-correction). Byte 0 bits 5:0
carry a rolling distance count (`0x734DC`, signal `0x542`). `0x55BBC`
synchronizes on the first fresh sample. Normal accumulation uses the
modulo-64 delta and checks receive status, operating state, uncorrected
speed ≥1.76 km/h and the sum over 50 samples. Below 1.76 km/h,
`0x55C48..0x55C58` updates the reference on a fresh receive and discards
the delta.

`0x55E18` adds five remainder units per accepted count. At 25,480
remainder units it advances the whole kilometre: **5,096 counts/km**.
`0x55904` converts at **8,200 counts/mile**. The processed SPI record
carries both unit systems.

`0x5616E` subtracts the trip baselines, including any borrow from the
remainder. For imperial trip tenths, `0x55986` subtracts the baseline
and `0x5593E` truncates the residual counts modulo 8,200 by dividing by
`0x334` (820). The metric and imperial getters (`0x56270/0x56298`,
`0x562DA/0x562F0`) each keep five BCD digits and roll independently from
9,999.9 to 0.0.
The packet builder converts packed BCD digits to ordinary 32-bit integers
(`0x79196`; six stores at `0x13586..0x135BA`):

| Quantity | Metric packet offset | Imperial packet offset | Resolution |
|---|---|---|---|
| Total distance | `0xF0` | `0x634` | Whole km / mile |
| Trip slot 1 | `0xF8` | `0x638` | 0.1 km / mile |
| Trip slot 2 | `0x100` | `0x63C` | 0.1 km / mile |

The incoming SPI `F0` handler (`0x12C16..0x12C7E`) reads the peer's
reset requests at `+0xA0` (slot 1) and `+0xA8` (slot 2). During normal
accumulation, a zero latches the corresponding request. `0x55E98` copies
both whole kilometres and the remainder to that slot's baseline. The
first nonzero word after the request finalizes the reset. Metric and
imperial values share this baseline. The total and the other trip continue
accumulating. The GTS `Meter_P5` catalog lists **ODO/TRIP Change Switch**
and **Trip Reset Switch** under DID `0x1001`.

GTS `Meter_P5` names DID `0x0103`
(`0x0403` snapshot) **Total Distance Traveled**: one unit byte (`1` km,
`2` mile) and a three-byte big-endian integer. `0x5521E` publishes the
selected total, bounded to 999,999; `0x22904` caches its unit and value for
these readers. DID `0x12A1` **Integrated value for Maintenance** subtracts a
different baseline (`0x548AE`). A screen observation can match the two
SPI trip slots to their A/B labels.

The normal CAN publication is **`0x611`**. COM PDU 3 starts at offset
`0x18`; `0x66B5C` packs the selected total at `0x1C`, so B4..B7 are the
32-bit big-endian value. `0x66B18` packs the **unit in B3[5:4]** at
`0x1B`, width 2, shift 4 (`1` km, `2` mile). COM 3 maps to lower row
`0x19` via `0x170DDA`, then to CAN ID `0x611` at `0x170614`. The pinned
[`UI_SETTING` DBC](https://github.com/commaai/opendbc/blob/c9b31d21bc396e8958891e271936bdbdf1a6ca93/opendbc/dbc/generator/toyota/_toyota_2017.dbc#L395-L397)
places `ODOMETER` in those same four bytes but `UNITS` in **B3[2:1]**.

The same producer `0x5521E` puts the two trip slots, in selected-unit
tenths, in `0x614` and `0x615` B4..B7. `0x30D` B4..B7 carries total
distance in tenths.

See the [Camry capture analysis](camry-2026-live-baseline.md#separating-distance-on-the-wire-from-distance-credited-by-the-meter)
for observed distance increments and low-speed counts on that vehicle.

### Engine speed and hybrid instrumentation

**Engine RPM and indicated tachometer value have different readers.** On
channel 0, `0x115` B0:B1 is a signed big-endian input. On fresh data,
`0x5891A` zeros inputs below `0x100`; `0x58862` otherwise computes
`q = floor((50 × raw + 64) / 128)`. After the sample/hold logic, GTS DID
`0x1042` **Engine RPM** reports in 50-r/min units (`0x28086`): healthy
raw `0x1000` yields `0x40` or 3,200 r/min; `FF` means unavailable.
The display path can also select seven-byte CAN `0x247` **B5:B6**, signed
big-endian: `0x6F348` reads two bytes at COM `0x2F5`, five bytes past the
PDU base `0x2F0`. The selector (`0x58870`) and the subsequent processing
feed SPI word `+0x94` (`0x58E8A → 0x133AA`).

**The HV/EV System Indicator is a signed gauge.**
`0x5472C` takes channel 0 `0x247` B0 bits 1:0 followed by B1 and
sign-extends bit 9. Raw `0x201` is unavailable; zero is a valid neutral
sample. DID `0x1641` (`0x286CA`) writes only the low ten bits in a
two-byte big-endian container. For example, `03 E7` decodes as **−25%**
when sign-extended from bit 9; GTS lists the field width as 16. Two 64-entry
filters (`0x5442C/0x545FA`) feed SPI words `+0xA0/+0x9C`; the latter
biases its signed value by 512, so neutral is `0x200`. The raw SPI slot
for `0x247` is 56, with its own receive-status bits.

GTS labels `0x10A8` bit 33 **EV Drive Indicator**; this DID is absent
from the normal read/support tables. The catalog lists **Ready Indicator**
and **EV Mode Indicator** under `0x2961`, whose value reader is null
(`0x156E08`).

### Coolant temperature: the diagnostic and the display update differently

On controller 0, `0x3C6` carries signal `0x3DD` (`0x1708B4`, extractor
`0x703E6`). For `n = ((B0 & 1) << 8) | B1`, the sample is `n / 2 − 80`
°C. The filter requires a qualified supply and fresh receive status.
Codes 0 and 3 leave an existing filter unchanged (`0x593CC`, bitmap
`0x16026C`).

Worker `0x59052` seeds a four-sample ring with the first accepted value.
It then replaces one sample every ten calls (`0x59428`).

| Reader | Value |
|---|---|
| GTS `Meter_P5` DID `0x1241` **Coolant Temperature** | `0x28574` reads the latest sample inserted in the ring. It reports 0.5 °C/count, clamps to 0–127 °C and returns `FF` on the invalid-status branch. |
| Processed SPI record `00`, word `+0xAC` | `0x591B8` moves toward the four-sample mean in steps. `0x5929E → 0x133E8` stores a little-endian 32-bit value in the input coding. The raw SPI mirror omits `0x3C6`. |

In an offline replay of the ROM tables for an 80 → 100 °C step, the
diagnostic reaches 100 °C on worker call 10. The SPI word is then
322 (81 °C) and reaches 360 (100 °C) on call 48.

The separate high-temperature logic at `0x3961E` trips on a qualified
mean at **120 °C** and rearms at **115 °C**. Toyota's
[2024 Prime instrument guide](https://assets.sia.toyota.com/publications/en/om-s/OM24V5QRG/pdf/OM24V5QRG.pdf)
lists a high coolant temperature warning.

### The display link

There are two outgoing records, each **2,048 bytes**. `0x15BD2 → 0x129E8`
selects the builder; `0x15734` drives the full-duplex CSIG2/DMA transfer.
Descriptor rows `0xE6290/0xE62B8` specify `0x200` 32-bit words each. CSIG2
exchanges 1,024 halfwords in each direction. Offsets below refer to the
little-endian RAM record.

| Direction | Selector at `+0x7F6` | Payload |
|---|---|---|
| RH850 → peer | `00` | Processed values (`0x12F08`) and mailboxes (`0x162DE`): speed, distance, temperature, dimmer and display control. |
| RH850 → peer | `0F` | Raw CAN mirror (`0x1537A`): receive status at `+0x08..+0x47`; 226 eight-byte slots from `+0x48`, of which 97 are mapped by `0xE66B0`. Each four CAN bytes are packed most-significant byte first into a word. |
| Peer → RH850 | `F0` | Settings and selections (`0x12AB2/0x16212`). Four selectors at `+0x240..+0x243` choose records for a subsequent processed reply (`0x6310A`); two identity fields are described below. |
| Peer → RH850 | `FF` | Alternate control record: `0x140B2` extracts bounded bitfields at `+0x18..+0x44` and forwards changed values. |

`0x15D70` writes header word `0x53ACB269` and an exchange counter at `+0x7F7`.
The last word at `+0x7FC` is the sum of the first 511 words modulo $2^{32}$,
XOR `0x53ACB269` (`0x1285A`). `0x159A6` checks the header, checkword and
peer status; `0x15B00..0x15B32` dispatches a valid reply by its selector.

**Outside temperature illustrates the encoding.** On channel 0, CAN `0x3B0`
B3 and B5 bit 4 feed `0x56CAE → 0x56C00`. The Celsius branch subtracts 48
from B3; the Fahrenheit branch also uses the half-degree bit. `0x56D6E`
supplies the processed builder, which writes `(signed temperature + 40) ×
100` in the low 16 bits at `+0xB4` and a remapped sample status in bits
31:30 (`0x13406..0x1345C`). For valid B3=`0x44`, half-degree bit clear,
the normal word is `0x1770` for 20 °C or `0x2A30` for 68 °F. GTS DID
`0x1141` names Celsius and Fahrenheit and reads the same cached sample.

**Driver's dimmer.** Captured
variant 1 selects the analog rheostat. `0x42BF2` reads ADCE0 slot 2, shifts
the 10-bit sample right by two, and feeds the filter at `0x42B3E/0x42B90`.
After four equal samples of `0x200` from cleared state, the filtered count
is `0x80`. The `st.w` at `0x134FE` puts that count at `+0xDC`, while DID
`0x1024` **Rheostat value** returns `floor(128 × 254 / 255) = 127`, or
50% on the GTS scale. Before readiness the DID returns `FF`. The catalog's
lux DIDs `0x1026/0x1142` and backlight DID `0x280B` are absent from this
image's dispatch, fallback and length tables (`0x1568B8/0x1565AC/0x1556FC`).

**Fuel level.** Cyclic worker `0x51DD8`
uses a local ADC snapshot. ROM selectors `0xE626E` and `0x15F472` route
the main sender to ADCE0I4; two readings of ADCE0I3 provide a reference.
`0x51F3C` checks both reference samples and normalizes the sender before
filtering. GTS DID `0x1022` **Fuel Input** reports the calibrated result
in 0.01 L (`0x53958 →` conversion in `0x52D00`). The second sender is
disabled in all nine variant tables; `0x1023` returns unavailable (`FFFF`).

The gauge uses a held, rate-limited quantity.
`0x51504` updates that state; one branch subtracts an adjustment accumulated
from CAN `0x3D3` B0:B1. `0x5182E` applies a separate gauge curve. On the
captured profile, one sender calibration knot corresponds to **27.50 L**;
the same internal quantity (18,022) maps to **50** on the 0–100 gauge curve
at `0x15F0CE`. `0x133C2..0x133DA` writes the gauge result and a status
bit at processed packet offset `+0xA4`.

### What would identify the renderer?

In an `F0` reply,
`0x16126` accepts 12-byte fields at `+0x60C` and `+0x618` when the low two
bits of their respective status words (`+0x604`, `+0x608`) are clear.
Identity builder `0x27174` reads those fields via `0x1643E` for entries
1 and 2; entry 0 is the local `838004AD9110`. Board package markings and
the two remote identifiers would narrow the search for the peer firmware
and its fonts and translations. A synchronized SPI trace and screen recording
while switching trips, units and language would tie record fields to screens.

## Normalization and analysis model

CodeFlash is **2 MiB, already based at zero**. Its reset vector branches
to `0xEE8`. Application tables extend through `0x177A4F`; additional
flash-control code occupies `0x1FAFE0–0x1FCA87`, followed by data through
`0x1FCAD7`. Metadata at `0x1FFFE0` points to application reset `0x10634`.
All original bytes are retained. Erased gaps and identified data are
mapped non-executable.

The profile maps BootFlash at `0x01000000` and 64 KiB DataFlash at
`0xFF200000`, then loads the ten startup relocation rows at their RAM
destinations. The D1L/D1M manual, **R01UH0451EJ0220**, figures 5.1 and
52.3, supplies the flash address map. New imports of `r4p-838004AD91` use the
[D1L/D1M-compatible G3M profile](../tooling/processor-module-audit.md#device-profile-and-interrupt-recovery),
`v850e3:LE:32:D1LD1M`. The exact MCU part remains unidentified.

Application and reprogramming startup establish different register contexts:

| Phase | GP | TP | Evidence |
|---|---|---|---|
| Boot/RPRG | `FEDD9AD4` | `FEDDBA98` | Startup `0xF24/0xF2A`; EP=`FEDD5FD8` at `0xF30` |
| Application | `FEDC04C0` | `000D9FE0` | Loads at `0x106F6/0x106F8`, constants `0x10B48/0x10B4C` |

Application initializer `0x84EB0` clears `[FEDC04C0,FEDFFBB8)` and copies
CodeFlash `[D9B38,D9FE0)` to `FEDC0018`. This reuses RPRG RAM. The project
retains the RPRG relocation snapshot and disables constant propagation
from writable memory; application initialization is not overlaid onto it.

```sh
tools/gtarget show r4p-838004AD91
tools/pseudo --target r4p-838004AD91 0x58406          # digital speed calculation
tools/gtarget r4p-838004AD91 disasm 0x13386 -n 8      # four speed fields in SPI packet
```

Two independent rebuilds produced byte-identical inventories. The promoted
snapshot and canonical corpus contain **15,990 functions**, all successfully
decompiled. `tools/gtarget show` and `tools/pseudo --target` resolve this target.

Registered-project smoke checks verified all three mapped images byte-for-byte,
both GP/TP contexts, the returning `0x7982C` helper and its cipher continuation,
and the four-byte AES load at `0xFEDD0688`. Firmware execution passed the
FIPS-197 encryption vector and the application response vector below.
`tools/test analysis_targets` passed.

## Recovered keys

| Material | CodeFlash offset | Runtime address | Value |
|---|---:|---:|---|
| Boot/RPRG SecurityAccess root | `0xD360` | `0xFEDD4D4C` | `f579ca07326b246812a31464b123cbc6` |
| Payload encryption/authentication root | `0xD350` | `0xFEDD4D3C` | `22620f1d268f9aa5275e0307c6b18f51` |
| Application SecurityAccess round keys | `0x165760–0x16580F` | Same | Eleven 16-byte keys, below |

The startup copy row at `0x11F8` maps CodeFlash
`[0xCD00,0xD370)` to RAM `0xFEDD46EC`, including both reprogramming roots.
Each root occurs once in CodeFlash; neither occurs in the supplied BootFlash
or DataFlash.

### Boot SecurityAccess

BootFlash offset `0x774C` registers SID `0x27`; configuration at `0x78DA`
selects subfunctions `01/02`, with 16-byte seeds and responses.
The request-seed auxiliary record is also 16 bytes.

```text
working_key = AES128-ECB-DEC(boot_root, auxiliary_record)
response    = AES128-ECB-ENC(working_key, seed)
```

`0xFEDC6D56` loads the root through pointer cell `0xFEDD4D30`
(CodeFlash `0xD344`); `0xFEDC6D8E` performs the second stage.
`0xFEDC6E02–0xFEDC6E20` compares all 16 response bytes.
The separate seed generator uses a dynamically generated AES key with
zero-block input/IV at CodeFlash `0xD370/0xD380`.

### Payload decryption and authentication

`0xFEDC5FF0` and `0xFEDC4BC2` independently derive the same key for
decryption and authentication:

```text
K         = AES128-ECB-ENC(payload_root, DID0201[16])
plaintext = AES128-CBC-DEC(K, IV=DID0202[16], ciphertext)
tag       = AES128-CMAC(K, DID0202[16] || authenticated_plaintext)
```

Both root lookups resolve pointer cell `0xFEDD4C98` (CodeFlash `0xD2AC`)
to `0xFEDD4D3C`. DID storage is `0xFEDD3506` / `0xFEDD3516`.
The CBC worker `0xFEDD0ECC` performs inverse AES, XORs the chaining block,
and retains the original ciphertext for the next block.
`0xFEDC4948` feeds the IV into CMAC before plaintext; `0xFEDC4A68`
compares the complete tag.

The RAM descriptor at CodeFlash `0xD11C` specifies start `0xFEDD7800`,
size **`0x800`**, and tag address `0xFEDD7FF0`. Its authenticated plaintext
is `[0:0x7F0]`, followed by the 16-byte tag. The
[Sienna EPS payload](../security/bootloader-payload-gate.md#7-exact-4-kib-plaintext-format)
uses a `0x1000`-byte image.

### Calvin/Willem range-dumper adaptation

The EPS dumper's addressed-word protocol and reassembler are reused for the
meter's **2 MiB** CodeFlash. The meter source is
`tsk/dumper/rav4_meter_main.c`; its authenticated-package builder is
`tsk/dumper/build_rav4_meter_payload.py`. The retained EPS client is
`targets/camry-2026/raw-20260826/camry_codeflash_dump.py`, and the maintained
EPS payload is `tsk/dumper/main.c`.

The meter package is exactly `0x800` bytes. The builder places code and zero
padding in `[0,0x7EC)`, writes little-endian
`CRC32(plaintext[0:0x7EC])` at `0x7EC`, writes the CMAC at `0x7F0`, then
encrypts the complete plaintext with the CBC construction above. The `10F0`
handler reads the CRC field separately and compares it with the CRC32 computed
over `[0,0x7EC)`. The builder emits upload ciphertext as `payload.bin` and the
decrypted inspection image as `payload.plaintext.bin`. DID `0201` and `0202`
use the retained all-zero package values.

The accepted RoutineControl start request is:

```text
31 01 FF 00 45 00 00 01 00 00 00 1F 00 00
|  |  RID   |  |---- address ----| |---- length -----|
SID SF      tag selector
```

`0xFEDC67BE` requires session mask `0x02`, SecurityAccess bit 0, start
subfunction, exactly ten option bytes, tag `0x45`, and selector `0`.
The selector-0 table at runtime `0xFEDD4DD4` contains the exact tuple
`0x10000/0x1F0000/0/0`, covering the application CodeFlash window. The path is
`FF00 → FEDC66D2 → FEDCEEC8 → FEDC6F08 → FEDC77BE → FEDC71D8`.
At `0xFEDC7218` it calls `0xFEDD7800` with mode 1. A zero return would continue
to uploaded offset `0x7E` and the stock erase driver. The payload accepts only
mode 1 and never returns from that mode; other modes return failure.

These values are target-specific, not corrections to the EPS package or
client. The Sienna `8965B4512000`, Camry `8965F3307000`, and Crown
`8965F3012000` bootloaders are byte-identical across the CRC validator,
RoutineControl handler, policy tables, erase path, and callback path. The
Corolla `8965F1208000` and `8965H1202000` copies have the same implementation
and table contents shifted earlier in CodeFlash.

The EPS RAM CRC descriptor is
`{0xFEBF0000, 0xFF0, 0xFEBF0FE0, 0xFEBF0FE4}`. Its validator (`0x481A`, or
Corolla `0x47FE`) verifies the embedded address and length, feeds the complete
`0xFF0` bytes to the hardware CRC engine with seed `0xFFFFFFFF`, and requires
the result to pass its zero-result check. The pinned EPS RAM-dump plaintext has
prefix CRC `0xF675E81A`, stored fixup `0x098A17E5`, and Python CRC32 residue
`0xFFFFFFFF` over all `0xFF0` bytes. The meter instead reads its four-byte CRC
field separately and compares it directly with CRC32 over the preceding
`0x7EC` bytes. The verified meter plaintext stores `0xD4681225`; the EPS
residue-style value would be `0x2B97EDDA` and is rejected.

The EPS `FF00` handler (`0x567E`, or Corolla `0x5662`) does not match an exact
address/length tuple. It checks that the requested range is contained in its
CodeFlash policy and validity-region rows, then maps both endpoints through
the physical erase-block table. `0xE0000/0x8000` is exactly block 34,
`0xE0000..0xE7FFF`, inside the permitted `0x18000..0xFFDFF` region. The meter
adds the exact four-field matcher at `0xFEDCAF38`; selector 0 uses the
BootFlash record at source offset `0x762C`, relocated to `0xFEDD4DD4`, whose
tuple is `{0x10000, 0x1F0000, 0, 0}`. Thus the CRC construction and `FF00`
arguments are real bootloader-contract differences. The EPS values remain
correct for the EPS callback setup; the meter values are required by the
meter's package and operation tables.

The compiled payload uses classic RSCAN channel 2 transmit buffer 2 and emits
response ID `0x7C8`. BootFlash records `0x7ADC/0x7AEC` route physical `0x7C0`
and functional `0x777` to ISO-TP receive callback `0xFEDC9814`; `0x7AFC`
routes `0x7C8` to the send-completion callback. The EPS RSCFD registers,
`0x7A1/0x7A9` route, and Panda bus assumptions do not apply.

After disabling interrupts, the payload calls the meter's WDTA0/1 service at
`0xFEDC1D7E`. That service reads the option-byte enable and variable-activation
bits, programs mode `0x5F` from the meter's retained configuration, and feeds
either `0xAC` or `0xAC-reference`. Mode `0x5F` selects the 100% watchdog
window. Completion and transport failures call the meter's own `0xAD4`
protected `SWRESA` sequence. The normal mode-1 path therefore cannot return
success into the erase continuation.

Offline verification:

```sh
uv run python tests/firmware/verify_rav4_meter_dumper.py --full
```

One continuous GNU RH850 simulation now consumes the retained programming
handoff, enters programming session `10 02`, completes SecurityAccess `27
01/02` with the firmware's seed and key routines, writes DIDs `0203/0201/0202`,
downloads the encrypted package with `34/36/37`, accepts `31 01 10F0`, verifies
the package CRC32 and CMAC, accepts the exact `FF00` request above, executes the
uploaded payload, and reassembles its nine-frame 16-byte dump byte-for-byte.
The simulator enters the receive path at the firmware's PduR/DCM
StartOfReception/CopyRxData/RxIndication APIs. GDB invokes the exact foreground
task entries in scheduler order and supplies successful lower-layer transmit
confirmation, one RTOS resource/timer read, inherited RSCAN configuration, and
RSCAN transmit completion.

The same test executes fixed and variable watchdog-feed paths, mode rejection,
first/last-word and progress-boundary reads, and busy, missing-completion,
abort, and uninitialized-controller failures. Its full payload run emits
524,421 frames; the retained reassembler produces 2,097,152 bytes with
SHA-256
`cc75cac2aaa4a648dadcad3d3d59d0c1bb293c53f1dbfcf9bc0fc88b4b6a4322`,
identical to the registered specimen. The simulator does not model D1L RSCAN,
the RTOS scheduler, physical CAN, or reset side effects. No vehicle traffic was
sent. A Camry combination meter still requires its own firmware and boot
contract. `tools/targets/camry/live/camry_meter_boot_sa_probe.py` is the narrow
live compatibility probe. The Camry meter was observed on Panda bus 1 through
ELM327 parameter 0 (OBD mux), `0x7C0 -> 0x7C8`. While the vehicle was READY
(`0x51E B0[7]=1`), `10 01` and `10 03` returned positive responses, `10 02`
timed out, and a following boot-shaped `27 01 || zero16` returned NRC `0x12`.
On 2026-11-20 the probe repeated `27 01 || zero16` for 15 seconds after the
`10 02` timeout; no seed arrived, and its final response remained NRC `0x12`.
The application was therefore still serving the meter endpoint rather than
handing it to the bootloader. The probe uses the recovered meter boot root and
stops after SecurityAccess. It performs no upload, DID write, RoutineControl,
or ECU reset.

Current GTS+ narrows the expected reprogramming family. The live Camry meter's
`F181` payload is `03` followed by three 16-byte slots: `8381GAQ02100`, an empty
slot, and `8381FAQ01200`. That is the exact record shape consumed by
`TCUWCanUnifiedCIDGetter.dll`. Conversely, the DH/SU-regulation getter's
`1A 88 00` request returns `7F 1A 11` on the Camry meter. The P5-Unified prepare
writer performs network-wide session/communication preparation and then sends
the target **directly** `10 02 -> 50 02`; it does not first put the target into
`10 03`. It then sends `27 01 || ECUAuthKey[16]`, receives a 16-byte seed, and
sends a 16-byte derived key. Its base/spec-02 flash writer subsequently uses
`2E 0203/0201/0202`, `34/36/37`, `10F0`, and `FF00`, matching the recovered RAV4
meter boot/package grammar. No retained CUW in the local corpus targets this
Camry meter, so its exact package metadata and RequiredSpecReproVer are not yet
available.

### Application SecurityAccess

The application's SID `0x27` table at `0x172414` selects **`03/04`**,
with a zero-length seed-request record and 16-byte seed/key.
Verifier `0x19784` calls `0x7AA30` and compares all 16 result bytes.

`0x7AA30` uses a ten-round substitution/permutation network. Each round
XORs a 16-byte round key, substitutes both nibbles of each byte through
the S-box at `0x165750`, then permutes all 128 bits using `0x165810`.
Permutation byte `P[i]` encodes destination byte `P[i] >> 4` and bit
`P[i] & 15`. The eleventh key is the final XOR. The firmware reads this
176-byte key schedule directly:

```text
b92cc430bd999c11971c8d55f66c6647
8f0f75b769ee955b3c901fdf2072ef14
540705cbc5ad03bb6c044afcd9f8967b
3de3d52c27c7592400ca957443241467
45e52261fc4762d1bab02838c9404718
d20a4d75fc548237797249fff997d663
ab39e0bed252958e572b4a69e3892d00
42b6ecd2f2f16b82519731112c0cd3f1
e51d1b67e7457d287980499d10fbed45
5f8645c5aadca3845b256cf58ce2afd8
63cfd9245dea7881b2eed867f35d7131
```

Its S-box is `030105060a0b0f0c0002070409080e0d`.
Application seed generation uses xorshift128; the constants at
`0x165730` initialize that generator.

### Original-byte verification

Detached Ghidra p-code execution used the startup relocation rows and
`v850e3:LE:32:default`. The broader `v850e3x` profile misdecodes the
four-byte `ld.bu` at `0xFEDD0688` as six-byte `ldv.w`, breaking AES
SubBytes analysis.

Observed checks:

- AES encryption/decryption passed the FIPS-197
  `000102…0f` / `001122…ff` known-answer vector.
- Boot auxiliary `000102030405060708090a0b0c0d0e0f` and seed
  `00112233445566778899aabbccddeeff` produced intermediate
  `6d094663ec71701814133d79bf58cbca` and response
  `2773a705f9258d378e1dbe6c7839ac07`, matching independent AES.
- Both payload KDF functions produced
  `99b110bcf5976c25e5ff41ee6d303314` for DID0201 `000102…0f`.
- CBC two-block chaining and CMAC over IV plus plaintext matched
  independent PyCryptodome results.
- The application cipher matched a separate byte-level implementation for
  three seeds. Seed `000102030405060708090a0b0c0d0e0f` produced
  `dcc1ffca5df5f09c996e91f51f962797`.

These checks execute firmware offline; no vehicle diagnostics were sent.

## Application SecOC

**The meter verifies synchronization on CAN `0x00F` and signs outgoing
CAN `0x24D`, using hardware key selector `4` for both.** This is the
classic Toyota SecOC format: a 28-bit truncated AES-CMAC and packed
trip/reset/message freshness.

Evidence: registered target `r4p-838004AD91`, application decompilation,
CodeFlash configuration bytes, and disassembly of the routing, command
issue, freshness comparison, and commit gates below.

### Configured messages and routing

| Direction | CAN ID / DataID | Frame bytes | Application bytes | Full / transmitted freshness bits | MAC bits | Profile |
|---|---|---:|---:|---:|---:|---|
| Receive synchronization | `0x00F` | 8 | 0 | 36 / 36 | 28 | `0x1732C4` |
| Transmit authenticated data | `0x24D` | 8 | 4 | 46 / 4 | 28 | `0x173314` |

The module has one RX and one TX profile: `0xBFBE6` and `0xC04C8`
map only RX PDU `0x47` and TX PDU `0`, respectively; `0xC0E66`
gives a queue count of one in each direction.

- **RX:** channel-0 CAN table `0x1706E4`, row 20, maps `0x00F` to
  PDU `0x47`. Router `0xA8A88` uses row `0x1710B2` and descriptor
  `0x17040C` to call SecOC ingress `0xBF6C6`.
- **TX:** router descriptor `0x1704C4` selects SecOC submission
  `0xBF5D2`. After signing, `0xC0BA2 → 0xC0DA2 → 0xA8178`
  reaches CAN submission `0x9DD00`. Its domain-0 table pointer at
  `0x16D0E0` resolves to `0x17054C`; entry 0 contains CAN ID
  `0x24D`, channel 0. Hook `0xA7DB6` sees a zero flag byte at
  `0x170C3C`, so it does not add a Toyota byte checksum.
- CAN `0x090` and `0x0D7` are ordinary receives here: their router
  rows `0x1711D2/0x1711D6` select COM copier `0xA4502`, without
  entering this SecOC verifier.

### Authenticated bytes

`0xC12C4` prepends the big-endian DataID. Packers `0xC174A` and
`0xC166E` produce the freshness bytes; `0xBFD52` extracts the RX
tag and `0xC09B8` assembles the TX trailer.

```text
T = trip counter (16 bits), R = reset counter (20 bits)
M = message counter (8 bits), P = four application bytes
|| = bit concatenation; fields are most-significant-bit first

0x00F CMAC input:  00 0F || T16 || R20 || zero4       (7 bytes)
0x00F CAN data:    T16 || R20 || CMAC_msb28           (8 bytes)

0x24D CMAC input:  02 4D || P32 || T16 || R20 ||
                  M8 || R_low2 || zero2             (12 bytes)
0x24D CAN data:    P32 || M_low2 || R_low2 ||
                  CMAC_msb28                        (8 bytes)
```

### Freshness and commit gates

`0xC1A3C` compares synchronization candidates with committed trip/reset
at `0xFEDDC448/0xFEDDC44C`. It stages a newer trip, or a larger reset
within the same trip. The configured rollover window (`0x1732C0 = 15`)
also permits stored trip `65520..65535` to advance to trip `1..16`.
An identical pair returns `1`; other stale candidates return `0x22`.

Candidates live at `0xFEDDC450/0xFEDDC454` until verification completes.
`0xC0196` treats verification result `0` at `0xFEDDC3C4` as success;
`0xC0160 → 0xC1550 → 0xC1B9A` then commits the pair and its bitwise
complements at `0xFEDDC458/0xFEDDC45C`. Failed authentication does not
commit the candidate.

For TX, `0xC1924` starts each new trip/reset epoch at message counter
`1` and increments within that epoch. Counter `255` or reset `0xFFFFF`
returns `0x24`, preventing another MAC request. The usable message
counters are `1..254`. Complement-check failure also prevents freshness
generation.

TX state is staged at `0xFEDDC470..0xFEDDC47B`.
Only a zero return from lower CAN submission makes `0xC0BA2` call
`0xC1532 → 0xC1B2A`, copying it to committed TX state
`0xFEDDC464..0xFEDDC46F`. This is queue acceptance, not a physical
bus-delivery acknowledgement.

### Hardware key and provisioning

Initializer `0xBF52E` installs key configuration `0x1732A4`:
mode word `1`, selector byte `4`. `0xBFA8C` copies it to
`0xFEDDC368/0xFEDDC36C`; both SecOC profiles select key reference `0`.
The provider reads the selector byte, rather than a plaintext AES key.

- RX worker `0xBFF14` submits verification through `0xBC43A`.
  Provider `0xBEF84` writes `(4 << 16) | 7` to `0xFFF60000`.
- TX worker `0xC07FA` submits MAC generation through `0xBCAA4`.
  Provider `0xBEDD8` writes `(4 << 16) | 5` to the same register.
- The hardware interface streams input through `0xFFF60004` and
  reads output through `0xFFF60008`.

Application RID `0x1010` exposes the hardware key-update path:
`0x1D4E8` stages 64 request bytes; `0x1D51A` calls `0xBC882`;
`0xBF094` issues command `8` with four input blocks and three output
blocks. Result handler `0x1D5DE` returns a status byte plus 48 result
bytes. This matches the family's SHE `M1/M2/M3 → M4/M5` exchange
documented in the [hardware command census](../security/icu-hsm-command-surface.md).

The operational SecOC key value has not been recovered. The configured
selector is established; the software boot/payload AES roots above
belong to a separate crypto path.

### `0x24D` application producer

**The meter assembles `0x24D` from CXPI frame `0x10` in its
Steering Switch Control Module communication group, adding local
presence/receive-status fields.** The recovered layout matches the existing
cruise-switch DBC. The byte-source map and OEM peer-role join follow.

ROM table `0x170DDA`, COM PDU **28**, selects lower PDU `0`. Its route
row at `0x170F96` is `{0x001C, 0x0000}`; router `0xA875A` selects
`0x170284 → 0x1704C4 → 0xBF5D2`. Sender `0x9D122` passes the buffer
selected by `0x16FBF0[28] = 0x00E0`: **`0xFEDDB498`**, eight bytes.
The SecOC queue retains the four application bytes and constructs the trailer.

Producer `0x3F482` runs when its input bit 3 is set. It checks configuration
item `0x4A` through `0x5FD42`, then receive record `0x8B` through
`0x863F4(0x8B, 0x101, 300)`. With configuration value `1`, low two status
bits zero, and combined timeout flag `0xFEDD2380` clear, it copies:

| CAN application field | Source at `0xFEDD69A8` | Signal IDs |
|---|---|---|
| B0 bits 7..2 | Record B0 bits 7..2 | `0x10C..0x111` |
| B1 bits 7..3 | Record B1 bits 7..3 | `0x112..0x116` |
| B3 bits 3..0 | Record B3 bits 3..0 | `0x11B` |
| B3 bits 7..6 | `1` when configuration is `1`, otherwise `2` | `0x119` |
| B3 bit 5 | Combined timeout flag | `0x11A` |

Packers `0x9C728/0x9C870` write these fields at COM-buffer offsets
`0xE0/0xE1/0xE3`. `0x3EF6E` builds the combined timeout flag from
status bit 1 of records `0x89..0x8C`, using the same threshold `300`,
when configuration is `1`; otherwise it clears the flag.

The invalid-reception branch clears B0 bits 7..2, sets B1 bits 7..3,
and retains the previous B3 low nibble. The unconfigured branch uses the
same B0/B1 defaults, clears the low nibble, and selects status `2`.
ROM initialization bytes at `0x16D7CC` are `00 F8 00 00 00 00 00 00`.
B2 has generated setters for bits 7/6 (`0x641C6/0x641E8` and their
pointer-argument wrappers); the recovered producer does not update them.
Their live application writers remain open.

Configuration getter `0x5FD42` reads cached byte
`0xFEDD324B + 0x4A`. Loader `0x5FBFC` obtains this item through internal
key **`0x055B`**, read from ROM `0x1619DE`, via `0x83938`.
Item `0x4A` is managed as a received-device presence state: callback
`0x11664 → 0x112F8` marks it present when logical record **2**
(`0x89`) is received and its status is available. The callback selects
`0x5FC96(0x4A) → 0x5FDEE → 0x5FD5A(..., 1)`; the generic manager
`0x5F06C/0x5EFCC` promotes the cached value after three qualifying samples.
Policy row `0x161834` uses callback `0x5FA68`, which reads calibration
word `0x17` bits 1:0; all nine variant tables select policy `1`.
The default is zero, and the NVM-slot entry at `0x161930` is `0xFFFF`.
This is a receive-driven gate, rather than a direct read of a static
installed-option bit.

### Upstream serial record

Receive-copy table `0x177474`, slot **4**, points to descriptor
`0x17754C`; descriptor `+0x24` is `0xFEDD69A8`.
Callback `0xCBCAC → 0xCA4F8` copies exactly **12 bytes** from its supplied
record pointer to that destination. The descriptor's completion callback
`0xCA01C → 0xCBCA4` is empty.

The associated low-level configuration chain is
`0x177720 + 0x10 → 0x177824`, with I/O configuration at `0x177844`
and serial configuration at `0x177968`. The serial peripheral base is
**`0xFFCE2000`**. Initializer `0xCDACC` writes `0x21` at base `+0x08`;
the D1L/D1M manual **R01UH0451EJ0220**, table 20.5 and section 20.3.3.3
(p. 1186), identifies **RLIN32 in UART mode**, with receive noise filtering
disabled. This establishes the hardware transport used by the serial stack.
The framing identifies **CXPI normal frames**: validator `0xCC8A6`
checks seven-bit IDs with odd parity using `0x1779D0..0x177A4F`
(all 128 entries verified); parser `0xCC9B6` reads FI bits 7:4 as DLC
and bits 1:0 as the two-bit counter; `0xCBAD4` constructs the network-state
bits 3:2; CRC routine `0xCDCDC` right-shifts and XORs `0xC8` over
PID, FI, and data. This combined fingerprint matches the normal-frame
layout in [Infineon's CXPI training, slide 8](https://www.infineon.com/assets/row/public/documents/10/56/infineon-traveo-ii-clock-extension-peripheral-interface-cxpi-training-en.pdf).
Protocol identification is inferred from those independently checked fields.

ID lookup `0x17769E` maps **CXPI ID `0x10` to slot 4**.
Its configuration row `0x17766E` is `10 08 02 02 00 00 00 00`:
eight-byte configured payload, receive mode `2` (`0xCA800` uses mode `1`
for transmission). The twelve-byte application record is storage capacity.
The sibling slot 2 maps **CXPI ID `0x50`**, also eight-byte receive,
through row `0x17765E` and descriptor `0x1774EC` to `0xFEDD6990`.
These frame IDs select messages; physical node ownership needs separate
evidence.

The sibling logical record **2**, at `0xFEDD6990`, has an exact OEM
switch-field join. DID `0x1002` dispatch row `0x156908` selects reader
`0x27F76 → 0x2AB42(0, 1)`. Callback rows `0x1575F4..0x15761C`
select `0x116F2`, which extracts record B0. GTS `Meter_P5` Data List
DID `0x1002` names the resulting fields:

| Record-2 B0 bit | DID payload byte 1 bit | OEM name |
|---:|---:|---|
| 3 | 7 | Multi Switch (Up) |
| 2 | 6 | Multi Switch (Down) |
| 5 | 5 | Multi Switch (Left) |
| 4 | 4 | Multi Switch (Right) |
| 7 | 3 | Multi Switch (Enter) |
| 6 | 2 | Multi Switch (Back) |

These names identify the multiplex-switch input carried by the same
serial interface and the record that enables item `0x4A`.

The exact firmware also supplies the peer's **OEM diagnostic role**.
Communication monitor rows `0x154458/0x154462/0x15446C/0x154476`
cover records `0x89..0x8C`, including `0x8B` for CAN `0x24D`.
Group row `0x154564` selects all four (start index 24, count 4) and
reports event **20** through `0x1A32C → 0x1A11E → 0xB1982`.
Event resolver `0xB5AE2` subtracts one, yielding internal event index
**19**. Its descriptor at `0x172FC8` selects DTC row `0x172E38`,
containing **`0x951287`**. GTS `Meter_P5` names **B151287**
**Lost Communication with Steering Switch Control Module**, failure
**Missing Message**. This joins the four-record CXPI group to a named
steering-switch peer role. A frame ID remains a message identifier;
installation and physical node ownership need wiring or capture evidence.

The pinned Toyota SecOC DBC calls B0 bits 7/6/5/4/2
`INCREASE/ENABLE/DECREASE/CANCEL/DISTANCE` and B3's low nibble `COUNTER`.
Those are external-source labels consistent with the recovered layout and
Steering Switch Control Module diagnostic role; the meter dataflow above
supplies the source bytes and gates. B0 bit 3 and the B1 fields remain
unnamed. The named cruise inputs are DBC-derived interpretations, pending
an exact physical-switch/capture or peer-firmware join for this specimen. The
[Camry steering-touch investigation](camry-2026-tss3-opendbc-port.md)
separately identifies a meter/CXPI architecture on newer vehicles.
The recovered RAV4 sibling record has named multi-switch inputs; assigning
ID `0x10` to a capacitive touch sensor would require additional evidence.

### Camry capture comparison and verification

The two retained relay-correct August 27 Camry CAN captures contain
`0x24D/8` on Panda buses **0 and 2**, with zero bus-1 observations:

| Capture under `targets/camry-2026/raw-20260827/` | Frames per bus 0/2 | Median interval, bus 0 |
|---|---:|---:|
| `camry_relay_route_can_20260827.ndjson.gz` | 517 / 517 | 1.003356 s |
| `camry_relay_lta_confirm_route_can_20260827.ndjson.gz` | 600 / 600 | 1.003403 s |

Every application prefix in these captures is **`00 00 00 80`**.
Bus 2 is the retained relay mirror. The second capture spans 598.992039 s
between first/last `0x24D` frames, giving 1.000013 Hz. These are observed
Camry bytes; RAV4's unconfigured path includes B1=`F8`, so a shared
arbitration ID does not establish identical configuration semantics.

Verification used the registered corpus, original CodeFlash table bytes,
and offline GNU V850 disassembly of `0x3F482`, `0x3EF6E`, `0xCA4F8`,
`0xCDACC`, `0x112F8`, `0x116F2`, `0x27F76`, and `0x2AB42`, plus
the CXPI PID/FI/CRC routines and communication-event selection at
`0x1A32C/0x1A11E/0xB5AE2`. OEM field/DTC names come from
`tools/gts did Meter_P5 0x1002` and `tools/gts dtc Meter_P5 B151287`
(`Meter_P5.ddb` SHA-256
`79b2bf8b8edeb40321b82d3b170143179cddac124b94588c670fbc176eaf0576`).
The repository's installed toolchain image ran with
network disabled and firmware mounted read-only; the existing Ghidra
working session was left untouched. Capture counts were recomputed directly
from retained incoming-CAN NDJSON. No vehicle traffic was transmitted.

## Speedometer input and display correction

**This meter applies an upward, table-driven calibration after receiving speed.**
The normal input is **CAN `0x0D7` B1:B2**, unsigned big-endian in
hundredths of km/h: receive row `0x1709CC`, PDU `0x90`, COM buffer
start `0x471`, signal `0x543` at offset `0x472`. Getter
`0x73504 → 0x11850 → 0x57B5C` supplies `0x57D20`; values through
`175` become zero. The valid-input state machine `0x57C42` stores the
input in `0xFEDD2C80`, read by `0x57D74(0, 180)`.
IOControl `0x2A01` can substitute test speeds inside `0x11850`;
its metric table `0xDA4A6` contains `0, 4000, …, 40000`, independently
establishing the input scale.

DID **`0x1041 Vehicle Speed Meter`** reads the input before display
correction: dispatch row `0x15696C → 0x2804C → 0x57A52 → 0x57D74`,
with normal result `floor((raw + 50) / 100)` km/h. The reader returns
`0xFF` when the status gate fails; otherwise it caps the computed byte at `0xFE`.
`0x57C16 → 0x6A814` separately publishes the same rounded input as
**CAN `0x610` B2**: signal `0x19`, PDU 2, COM offset `0x12`, lower
TX index `0x18`, transmit row `0x17060C`.
The adjacent DID `0x1042` is Engine RPM and belongs to another subsystem.

The digital-speed path is `0x58406`:

1. `0x58026` takes the integer mean of a fourteen-sample ring of input
   hundredths of km/h.
2. For imperial output, it computes
   `floor((mean * 5096 + 4100) / 8200)`; the metric path retains `mean`.
3. `0x58608(value, unit, 1)` selects a ROM curve from `0x15FD9C`.
   `0x796D2` clamps at the endpoints and linearly interpolates between
   knots using integer division.
4. The calibrated hundredths are divided by `50` into half-unit steps.
   `0x5819C` updates the held half-unit value only when the new value
   differs by more than one step. The whole-number candidate is
   `(held + 1) >> 1`. `0x58240` adds low-speed state handling and
   `0x582E8` applies a configured upper limit.
5. Metric/imperial integers occupy `0xFEDD2CD2/0xFEDD2CD0`.
   The processed SPI builder `0x12F08` places them at packet offsets
   **`0x88/0x8C`**, alongside the uncorrected input at `0x80` and a
   separately calibrated high-resolution metric value at `0x84`.
   `0x5838A` also publishes the selected-unit integer as nine-bit COM
   signal `0xA5` through `0x64D44/0x688B4`: **CAN `0x376` B0 bit 0
   followed by B1**, with value `((B0 & 1) << 8) | B1`. This is PDU
   `0x12`, lower TX index 4, transmit row `0x17056C`.
   **B0 bit 7 selects units: `1` mph, `0` km/h.** `0x58406` saves its unit
   selector in item `0x41F`; the zero case selects the imperial result.
   `0x5838A` tests the saved item for zero and `0x64D22/0x6888E` pack the
   boolean as signal `0xA4` at bit 7 of the same byte. On the invalid-status
   branch `0x583AE..0x583BA`, the nine-bit speed is `0x1FF` (unavailable).
   A passive decoder must exclude that value before converting to m/s.

There are **six selector slots (`0..5`): five calibration IDs and a zero
fallback**. Selector `0x58788` uses the low byte of saved item `0x131`
when it is `1..5`; after a successful read with another value, it uses
variant word 0 bits 24:27 (`0x5C50E`). A failed saved-item read selects
zero. `0x58608` bounds values above five back to zero. Digital curve pairs
below are `(imperial, metric)` ROM addresses:

| Profile | Curve addresses | Examples in native units, before whole-number rounding |
|---:|---|---|
| 0 | `0x15FFA0`, `0x15FFA0` | All output knots zero |
| 1 | `0x15FDF2`, `0x15FDCC` | Imperial `100.00 → 101.70`; metric `96.53 → 98.14` |
| 2 | `0x15FE4E`, `0x15FE18` | Metric `100.00 → 101.70`, `120.00 → 122.10` |
| 3 / 4 | `0x15FFA0`, `0x15FF12` | Imperial zero; metric `100.00 → 106.50` |
| 5 | `0x15FF76`, `0x15FF4C` | Imperial `100.00 → 106.00`; metric `96.53 → 103.77` |

The separate high-resolution path `0x57E42` uses pointer table `0x15FD6C`;
profiles 3–5 have different curves there. Profile IDs therefore identify
paired calibration policies, rather than six unique digital curves.

**No existing profile is an identity/bypass calibration.** Every nonzero
curve applies positive correction at its normal-speed knots. Slot 0's
all-zero ordinates make `0x796D2` return zero for every input; they are
absolute outputs, not additive corrections. Profiles 3/4 likewise give
zero imperial output. Profile 2 retains roughly the same uplift as profile
1, and profile 5 increases it. Writing saved selector zero on variant 1
would select the configured fallback, profile 1, through `0x58788`.
Removing the uplift while preserving unit conversion, filtering,
hysteresis and limits would require changing the calibration or calculation;
there is no stock selector value that does this.
### YC specimen: saved profile 1

The supplied DataFlash selects **profile 1**, with saved variant **1**.
`0x58648 → 0x81118(0x131)` loads `0x0101`; `0x58788` uses its low
byte directly. Variant initialization `0x5C57C → 0x811E0(0)` loads `1`.
Its ROM table `0x160ED8` has word 0 = `0x11000000`, independently
selecting profile 1 as the configured fallback. Word 27 = `0xD4440000`
selects the digital limits **140 mph / 220 km/h** at `0x15FD52`.

| Saved item | Storage / physical ID | DataFlash file offset | Header | Payload | Commit |
|---|---|---:|---|---|---|
| `0x131` | `0x237 / 0x236` | `0x8D40` | `36 02 E2 C2` | `01 01 00 00` | `AA AA AA AA` |
| `0` | `0x16 / 0x15` | `0x0500` | `15 00 BE C2` | `01 00 00 00` | `AA AA AA AA` |

Exact mapping: saved-item descriptors `0x153894/0x1517E0` identify the
storage IDs; `0xC63BC` uses service records `0x176B10/0x174900` to select
the physical IDs. `0xC25E8` uses the slot table at
`0x173708 + physical_ID * 6`; `0xC99AE` adds DataFlash base
`0xFF200000`. Both records pass the image's commit
check `0xC559A`, ID check `0xC534C`, and short-payload checksum check
`0xC51FC/0xC4E2C`: `0xC2A8 + sum(ID bytes) + sum(payload bytes)` is
`0xC2E2/0xC2BE`, matching the stored little-endian checksum.
**All three copies agree and validate.** Speed storage IDs `0x237..0x239`
map to physical IDs `0x236..0x238`, offsets `0x8D40/0x8D80/0x8DC0`,
with checksums `0xC2E2/0xC2E3/0xC2E4`. Variant storage IDs
`0x16..0x18` map to physical IDs `0x15..0x17`, offsets
`0x500/0x540/0x580`, checksums `0xC2BE/0xC2BF/0xC2C0`.
Type rows `0x151398/0x1513AC` specify three copies; `0x81382`
computes their stride and `0x83514` processes all three.
DataFlash SHA-256:
`569ef4661fb2e98a156c698e3eba160d6389cd811b41a75cebb78baa681618eb`.
The storage accessor's `0x3FCE4xxx..0x3FCE5xxx` pointers are retention
RAM, within `0x3FCE4000..0x3FCE7FFF` in hardware manual figure 5.3.

Thus the specimen's digital imperial curve is **`0x15FDF2`**, with
knots `(input mph, corrected mph)`:
`(1.09,0), (20,20.35), (40,40.70), (60,61.00), (80,81.40),
(100,101.70), (120,122.10), (140,142.40), (160,162.70)`.
It is an interpolated positive calibration, not a fixed mph addition.

For example, a stable input of **109.44 km/h** (about 68 mph) converts
to `6801` hundredths of mph, interpolates to `6917`, and produces
half-unit candidate `138`. Held values `137`, `138`, or `139` survive
the one-step deadband; the integer output is respectively **69, 69,
or 70 mph**. A previous higher speed can therefore leave 70 displayed
at this input. The exact output depends on the fourteen-sample history,
held half-unit state, and update phase. This reproduces the possible
68-to-70 difference within the verified RAV4 arithmetic; relating an
external true-speed measurement to the incoming CAN value requires a
synchronized observation.

Verification: registered decompilation corpus, original CodeFlash table
bytes, and read-only offline disassembly of `0x73504`, `0x57B5C`,
`0x58026`, `0x5819C`, `0x58326..0x587BA`, `0x796D2`, and SPI stores
`0x13386..0x133A2`. GTS `Meter_P5` supplies the DID names. The SPI peer's
final pixel rendering is outside this RH850 image. The
[Camry speed analysis](camry-2026-live-baseline.md#494-tss3-preserves-toyotas-separate-internal-and-cluster-cruise-set-speeds)
provides a cross-target lead; this report's tables and calculations are
from the RAV4 meter image.

### Factory configuration access

Private application service `0xBA` can write the saved speed-profile and
variant blocks. It selects among the existing ROM profiles; none is an
identity curve.

Service dispatch `0x19DF4 → 0x19D04 → 0x19BAA → 0x1A8FC` uses command table
`0x154668`. Write handler `0x1EECE` accepts
`2E FE <virtual-address:BE16> <value:BE16>`; read handler `0x1EF24` accepts
`22 FE <virtual-address:BE16> <length:8>`. These addresses index a private
virtual-halfword table.

Access requires application session `03`, SecurityAccess `03/04` at level 2,
and a factory-enable input qualified at startup. SID row `0x172604` specifies
the session; `0x1A9CC → 0x19E0A` applies security mask `0x0004` at
`0x154658`. Both security seed and key handlers check the factory state.

`0x118DE` samples active-low GPIO selector `0x95` at counter thresholds `0`,
`1000`, and `2000`; `0x1192C` maintains a three-count qualification.
`0x85B68` stores the result in `FEDD646B` bit 0. Scheduler `0x19BAA` latches
eligibility as `((old_flags & 0x0C) + 3) & current_flags`; once cleared, the
factory bit cannot recover within that diagnostic lifecycle. GPIO row
`0x165D88` resolves selector `0x95` to `0xFF61054C` bit 5. Its package pin,
board connection, and sampling-counter time unit are unknown.

The writer also requires `FEDC0772 == 1`. Diagnostic initializers
`0x19A50/0x19A6E/0x19A8C` reach `0x1EDEE → 0x11F0A`, which sets that byte.
`0x120B8` then requires write permission `0xFF` from `0x11F4A`. The permitted
entries in ROM table `0xDF4CA` include:

| Saved value | NvM blocks | Virtual halfwords |
|---|---|---|
| Speed profile `0x131` | `0x237`, `0x238`, `0x239` | `0x0BCC/0x0BCD`, `0x0BCE/0x0BCF`, `0x0BD0/0x0BD1` |
| Variant `0` | `0x16`, `0x17`, `0x18` | `0x0091/0x0092`, `0x0093/0x0094`, `0x0095/0x0096` |

Each pair addresses offsets 0 and 2 of a four-byte block. For example, ROM row
`0xE03F2 = CC 0B 37 02 04 00 00 00` maps `0x0BCC` to block `0x237`, offset 0.

The profile descriptor `0x153894` and variant descriptor `0x1517E0` both set
the bit-2 write-protection flag. Ordinary writer
`0x80F8C → 0x80F22 → 0x80ED0` rejects writes to those items. The private
writer instead reaches block callback `0x184F2` via
`0x124BE → 0x81BA2 → 0x81B5E`. It reads the block, replaces the selected
halfword in little-endian order (`0x12304`), queues the full block with
`0xC676A`, and verifies the readback with bounded retries
(`0x1235A/0x12386`). `0x122B0 → 0x812BC` reloads affected items; successful
completion calls `0x11D80 → 0x58648` to refresh the profile cache.

The profile has three replicas. When all are valid, `0x816E0` invokes
`0x835D2 → 0x83514`, which selects bitwise majority `0x79A3A` from the profile
descriptor. For example, `0x0102, 0x0101, 0x0101` resolves to `0x0101`.

The SPI settings path `0x12AB2 → 0x60D8E` uses fixed value keys
`0x402F..0x4047` from table `0x162728`; `0x60D32` commits eligible settings
through their configured saved-item IDs. The SPI peer receives both raw and
corrected speed values. Its rendering policy and engineering configuration
remain open.

Evidence: original CodeFlash and DataFlash tables, registered decompilation
corpus, and disassembly of the access gates, writer, and replica decoder.
Factory-mode entry and writes have not been exercised on a meter.

## Receive and diagnostic paths

Getter `0x768B4` returns `(0x3B7.B2 >> 2) & 3` through signal `0x550` at
`0x9C66A`. Its `0x768D0` call is the sole extraction covering B2 bit 2
among all 1,344 direct calls found in the image bytes. No application
caller of `0x768B4` has been identified.

The active raw-frame path `0x1537A` forwards B2 mask `04` unchanged as
SPI packet byte `0x451`, mask `04`, with a separate initial/timeout status.

`0x15BD2` builds the record. A separate scheduled callback at `0x15BA2`
services the exchange: `0x15A8E → 0x15D70 → 0x15734` sends the `0x800` bytes.
The first halfword is written to `0xFFDA5004`; DMA sends the remaining
`0x3FF` halfwords to `0xFFDA5008`. The D1L/D1M hardware manual
**R01UH0451EJ0220**, pp. 1007/1012/1024–1025, identifies these as
**CSIG2TX0W/TX0H**. The configured interface is SPI master, 16-bit,
LSB-first, with loopback disabled. The peer processor is unidentified.

The same SPI link carries **Multi Display** control. Handler `0x1F88C`
commits the `0x2831` control value to mailbox 0 through `0x16390`;
`0x162DE` places it at processed-packet offset `0x734`.
Return-control handler `0x1F8BE` sends zero through that mailbox.
GTS names `0x2831`'s controls **Multi Display All (White)** and
**Multi Display Default Screen**.

The [application DID inventory](../../data/targets/r4p-838004AD91/application_did_inventory.csv)
covers all 74 rows of `0x1568B8`. `0x2389A` reads the DID at `+18` and
calls the support function at `+0`; `0x23C36` checks the value callback at
`+4` before calling it. **34 have a value callback, 40 do not.** Sixty-three
rows have an exact `Meter_P5` monitor label. The CSV distinguishes numerical
readings, switches, feature presence, stored settings, internal data and
catalog-only entries. A separate 19-ID support list and other
dispatch paths account for services such as the total-distance read.
Readers for `0x1101/0x2041` are `0x2849C/0x2881C`.

**The meter also diagnoses other nodes.** For CAN `0x247`, receive
notification `0x1140E → 0x86364` refreshes logical record `0x16`.
The scheduled diagnostic worker `0x19BAA` evaluates it via group
`0x154534` and row `0x154430`; that group requires the relevant presence
state as well as the receive-history, age and operating-state checks.
Its event 16 resolves through `0x172F88` to `0x172E08 = 0x00C29387`:
GTS **U029387, Lost Communication with Hybrid/EV Powertrain Control
Module — Missing Message**.

GTS diagnostic bit positions are MSB-first (`extract_msb0` in
`tools/techstream/ddb_semantics.py`). **Stop Lamp Switch Function**, DID
`0x2041` bit 30, is payload byte 3 mask `02`, hence setting `0x010A`
bit **9**. Support builder `0x5CE50` never sets that mask; the application
getter `0x2ADF2` explicitly removes it with `& 0xFCFF`.

**Stop Lamp Switch**, DID `0x1101` bit 45, is payload byte 5 mask `04`.
Its callback at `0x157734` is null. The `0x5EA16 → 0x3D812` configuration
path belongs to seatbelt warnings; its bit-14 input is the **3rd Left
Seatbelt Warning Buzzer Function**.

The [complete RX route inventory](../../data/targets/r4p-838004AD91/can_receive_routes.csv)
joins each CAN row to its router destination and, where present, its raw SPI
slot and status bits. `0xA7CD4` uses the boundaries at `0x16D0A0`
(`0, 98, 171`) to search `0x1706E4`. Channel 0 has 98 rows, 46 mirrored;
channel 1 has 73 rows, 51 mirrored. Of the 171 routes, 170 lead to the COM
receive copier at `0xA4502`; channel 0 `0x00F` takes the synchronization path.
Only `0x682` occurs on both channels: different COM buffers, neither mirrored.
Channel numbers are the controller indices in this firmware.

The 97 mirror entries join by **COM PDU**. For
example, `0x3B7` is channel 0, COM `0x91`, buffer `0xFEDDB831`; mirror
row `0xE68B4` selects slot 129, payload `+0x450`, status word `+0x28`
bits 3:2. The channel 0 range contains none of `0x1B2/0x251/0x252`.
Channel 1 contains `0x230` and `0x251`, in the `0xA6..0xBC` PDU range
handled by the multi-frame record assembler `0x6230E → 0x62FB4`.
`0x62F80` selects samples with `B1 == selector && B0 != 0`;
`0x62E9C/0x62E66` assemble 30-halfword records. `0x6310A → 0x12F08`
publishes records selected by incoming SPI packet offset `0x240`.

Receive status from `0x9C618` distinguishes initial/not-received (`01`)
and timeout (`02`). Reception clears both; `0xA4280` sets timeout on expiry.
The `0x3B7` timeout is 360 scheduler ticks; `0x251` timeout is disabled.

