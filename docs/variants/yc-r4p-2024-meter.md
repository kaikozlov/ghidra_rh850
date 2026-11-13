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

