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
52.3, supplies the flash address map. The exact MCU part remains unknown;
the target imports no P1M-E peripheral map.

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
belong to a separate crypto path. The four application bytes in
`0x24D` remain undecoded.

## Receive and diagnostic paths

**The brake-graphic display predicate remains unresolved.** Getter
`0x768B4` returns `(0x3B7.B2 >> 2) & 3` through signal `0x550` at
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
The independent pedal input has not been identified.

Consumer `0x4F944` combines `0x411` fields with `0x3B7` B1 bits 4:3.
Its cached output is consumed by the selector table at `0x15E5A4` and
serialized into the processed SPI packet.

Receive status from `0x9C618` distinguishes initial/not-received (`01`)
and timeout (`02`). Reception clears both; `0xA4280` sets timeout on expiry.
The `0x3B7` timeout is 360 scheduler ticks; `0x251` timeout is disabled.

