# yc R4P 2024 meter firmware

## Specimen

Registered target: **`r4p-838004AD91`**, reference role, software identifier
`838004AD9110` at CodeFlash `0x156898`.
The [canonical artifacts](../../firmware/r4p-838004AD91/README.md) record
the hashes, mapped bases, and original `community/yc/r4p/meter/` captures.

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
tools/gtarget r4p-838004AD91 decompile 0x7AA30
tools/pseudo --target r4p-838004AD91 0xFEDC6D56
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
contract.

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

`0x15BD2 → 0x15A8E/0x15D70 → 0x15734` sends the complete `0x800`-byte packet.
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

Diagnostic dispatch table `0x1568B8` has 20-byte rows with the DID at
offset `+18` (`0x2389A` disassembly). The `0x1101` and `0x2041` read
callbacks are `0x2849C` and `0x2881C`, respectively.

GTS diagnostic bit positions are MSB-first (`extract_msb0` in
`tools/techstream/ddb_semantics.py`). **Stop Lamp Switch Function**, DID
`0x2041` bit 30, is payload byte 3 mask `02`, hence setting `0x010A`
bit **9**. Support builder `0x5CE50` never sets that mask; the application
getter `0x2ADF2` explicitly removes it with `& 0xFCFF`.

**Stop Lamp Switch**, DID `0x1101` bit 45, is payload byte 5 mask `04`.
Its callback at `0x157734` is null. The `0x5EA16 → 0x3D812` configuration
path belongs to seatbelt warnings; its bit-14 input is the **3rd Left
Seatbelt Warning Buzzer Function**.

The receive channels must be distinguished. Dispatcher `0xA7CD4` uses
`0x16D0A0 = {0, 98, 171}` to select separate ranges of the receive table
at `0x1706E4`. Channel 0 contains `0x3B7` (PDU `0x91`, buffer
`0xFEDDB831`); its range contains none of `0x1B2/0x251/0x252`.
Channel 1 contains `0x230` and `0x251`, in the `0xA6..0xBC` PDU range
handled by the multi-frame record assembler `0x6230E → 0x62FB4`.
`0x62F80` selects samples with `B1 == selector && B0 != 0`;
`0x62E9C/0x62E66` assemble 30-halfword records. `0x6310A → 0x12F08`
publishes records selected by incoming SPI packet offset `0x240`.

Consumer `0x4F944` combines `0x411` fields with `0x3B7` B1 bits 4:3.
Its cached output is consumed by the selector table at `0x15E5A4` and
serialized into the processed SPI packet.

Receive status from `0x9C618` distinguishes initial/not-received (`01`)
and timeout (`02`). Reception clears both; `0xA4280` sets timeout on expiry.
The `0x3B7` timeout is 360 scheduler ticks; `0x251` timeout is disabled.

