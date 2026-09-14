# yc Venza airbag RH850 reprogramming path, 2026-09-14

## Result

The two yc artifacts close the original Discord question more narrowly than the
initial hypothesis suggested.

`boot.bin` is **not evidence of an immutable boot stage that simply executes
before CodeFlash `0x00000000` at every power-up**. The airbag CodeFlash itself
maps it into the `0x01000000..0x01007FFF` extended-user region, validates that
region, and copies the executable portion into RAM as one segment of a split
runtime image. The trailer identifies the component as
`AUBIST_RPRG_201902`. Its entry assumes an already-established runtime context
and returns to the surrounding RAM-loaded software.

The application does, however, contain a real DiagnosticSessionControl
programming route. One configured SID `0x10` service group accepts subfunction
`0x02`, applies explicit live preconditions, starts an asynchronous transition,
writes a retained 32-byte handoff record plus `0x5AA5A55A` magic, and then enters
a halt path after two hardware-control writes. Reset/startup code preserves that
record through destructive RAM test, detects the magic, clears it, and folds the
result into a programming-mode boolean before the RAM runtime and RPRG module
are initialized.

So the useful model is:

```text
normal DCM 10 02
  -> policy / asynchronous transition
  -> retained RAM record + 5AA5A55A
  -> hardware-control / halt transition
  -> startup recognizes retained state
  -> common RAM runtime receives programming-mode boolean
  -> extended-user RPRG image is loaded into the RAM runtime
```

This is **not** a recovered “spam `10 02` during power-up and stay in boot”
shortcut. The request is handled by ordinary DCM configuration and is subject to
policy before the retained handoff is created.

A follow-up crypto pass also recovers the two independent 128-bit RPRG roots:
`8af2c4708cd9cdec494da7acdaa9a8f7` is the payload-build root used to derive the
RequestDownload payload key from DID `0x0201`, while
`8f69e6dc2a4b80b45054b4827a5ab622` is the 16-byte boot/RPRG SecurityAccess root.
The ordinary application SID `0x27` instead uses inline two-byte arithmetic and
has no analogous third 128-bit acceptance root. Section 5 gives the complete
firmware-static chains.

For the exact F33 EPS, this is useful architectural evidence but not a code
transfer. Exact complete-function comparison found only generic/library overlap
and no named semantic transfer into the airbag image. The F33's known normal
application-to-PROGRAMMING handoff is a different implementation, and the
current poisoned F33 application still faults before its scheduled DCM worker
and normal handoff execute. P1M-E FLMD serial programming remains a separate
on-chip hardware recovery mechanism; yc's `boot.bin` is not that on-chip boot
firmware.

## Artifacts and evidence boundary

Contributor artifacts are retained unchanged under `community/yc/venza/`:

| Artifact | Size | SHA-256 |
|---|---:|---|
| `boot.bin` | `0x8000` | `943934abc9a5c676eff46f51f008baa39e4f533e66650ffcce54d7bfb6e6e6e2` |
| `cflash.bin` | `0x300000` | `2dfaf7ce21cb04af1126192f574103f63802352f8717fa0f03986d5a11d067f9` |

The vehicle/ECU attribution (“Venza airbag sensor”) and glitch-acquisition method
are contributor-provided. The exact RH850 MCU part number is not established by
the supplied metadata. Do not transfer airbag SFR addresses or this DCM layout
to P1M-E merely because both ECUs are RH850.

The CodeFlash contains raw identity strings at `0x17FFC6` and `0x17FFD0`:

```text
8917048E30
8917F48692
```

Formatting those as Toyota part-like identifiers is an interpretation; the raw
bytes above are the evidence. Meaningful/non-fill CodeFlash ends around
`0x17FFFF`; `0x180000..0x2AFFFF` is `0xFF` fill and
`0x2B0000..0x2FFFFF` is `0x00` fill in this capture.

Portable byte assertions for the critical findings are in
`tests/verify_yc_venza_airbag_reprogramming.py`.

## 1. `boot.bin` is the `0x01000000` extended-user image

The address is established by the airbag CodeFlash, not inferred from the
filename.

Startup integrity code covers the extended-user range
`0x01000000..<0x01007FFC` and uses the final dword at `0x01007FFC` as the stored
check value. More decisively, the runtime relocation tables contain the source
addresses directly.

The copy-group headers are:

```text
0x1914: count=3, table=0x1954
0x191C: count=3, table=0x1978
```

Relevant `<destination, source, source_end>` rows are:

```text
0x1954: FEBEA7B0  00004190  0000A304
0x1960: FEBF0924  01000000  01007588
...
0x1984: FEBFBF90  01007588  01007BD0
```

Thus `boot.bin[0x0000:0x7588]` is copied to `FEBF0924`, and
`boot.bin[0x7588:0x7BD0]` is copied to `FEBFBF90`. The final `0x430` bytes are a
flash-resident trailer rather than part of the copied executable payload. That
trailer contains:

```text
boot.bin + 0x7FD0: AUBIST_RPRG_201902
boot.bin + 0x7FFC: 25 44 D8 FB
```

The first adjacent CodeFlash segment ends at logical address `0xA304`; its RAM
destination ends at exactly `FEBF0924`, where the extended-user image begins.
The call at CodeFlash `0x83E0` is decoded by the RH850 processor as a direct call
to logical `0xA304`. After that caller's relocation, the same relative call lands
at `FEBF0924`: the first instruction copied from `0x01000000`.

This is a split linked image, not two independent programs. The `boot.bin` entry
at `0x01000000` calls several helpers but does not establish GP/TP itself, and
its apparently high `0x00FFxxxx` direct-call targets relocate back into adjacent
RAM-loaded CodeFlash sections. That shape is consistent with an RPRG component
linked into the common RAM runtime.

The generic RH850/P1M-E manual independently calls `0x01000000..0x01007FFF` the
Code Flash **extended user area**, but the airbag mapping above comes from the
airbag's own bytes and does not depend on assuming the airbag MCU is P1M-E.

## 2. A configured DCM endpoint really accepts `10 02`

The application contains several DCM service groups. The group beginning at
`0x23C18` has a 24-byte SID `0x10` descriptor whose subfunction table is
`0x237D0` and whose subfunction count is five.

The five 16-byte subfunction rows are:

| Row | Subfunction | Callback | Allowed current sessions |
|---:|---:|---:|---|
| `0x237D0` | `0x01` | `0xC18EC` | `01 03 02 40` |
| `0x237E0` | **`0x02`** | **`0xC190C`** | **`01 03 02`** |
| `0x237F0` | `0x03` | `0xC18FC` | `01 03` |
| `0x23800` | `0x04` | `0xC192E` | `04` |
| `0x23810` | `0x40` | `0xC191C` | `01 40` |

The wrapper family only selects the requested target session. In particular:

```c
0xC190C: FUN_000c32d8(phase, context, 2);
```

The core at `0xC32D8` separates start/cancel/poll phases. On the start phase,
`0xC30B4` runs the configured policy callback and selects a per-session runtime
record. Session `0x02` is unique in the six-record session configuration at
`0x24C06`: its record at `0x24C1A` has transition kind `2`, whereas the ordinary
sessions use kind `0`. That causes the DCM operation to become asynchronous and
use response-pending state rather than completing as an ordinary immediate
session switch.

### Programming-session policy is not unconditional

The policy callback for target session `0x02` is `0xC772C`. Its recovered
conditions are intentionally left structural because the source signals have
not been assigned trustworthy OEM names:

- one sampled `uint16` must be `<= 300`; otherwise the callback returns NRC
  `0x88`;
- another call result must not be `0xA5` or `0x5A`; that failure uses NRC
  `0x22`; and
- a third sampled `uint16` must satisfy unsigned
  `(value - 0x015E) < 0x0148`; otherwise the callback uses NRC `0x22`.

Therefore the existence of the `10 02` table row does not imply that arbitrary
power-up traffic can force programming mode.

## 3. `10 02` creates a retained programming handoff

The asynchronous callout chain resolves through fixed RTE-style tables:

```text
0xCA7F4 -> 0xBE1DC -> [0x17FF04] -> 0xC76C6
0xCA800 -> 0xBE1F0 -> [0x17FF08] -> 0xC772C   # policy
0xCA80E -> 0xBE206 -> [0x17FF0C] -> 0xC780E
```

`0xC76C6` writes a 32-byte record to `0xFEF0FFD0..0xFEF0FFEF`:

```text
+00  02 00 00 07 80 00 00 00
+08  00 10 01 02 00 00 00 00
+10  00 00 00 00 00 00 00 00
+18  00 00 00 00 00 00 00 00
```

and then writes:

```text
FEF0FFF0 = 5AA5A55A
```

The exact field meanings of that record are not named in the firmware evidence,
so only the bytes and their role in this transition are asserted.

When the asynchronous state machine emits event `6`, `0xC780E` performs:

```c
Ramfff80768 = 0x200;
Ramfff80868 = 0x200;
__disable_irq();
__halt();
for (;;) {}
```

Those two SFR names are intentionally not guessed. The exact airbag MCU has not
been established, so calling them “reset registers” from a different RH850
manual would be an unsupported transfer. The firmware-static result is that the
programming transition writes both hardware locations, disables interrupts,
and stops ordinary execution.

## 4. Startup explicitly recognizes the retained state

This is not ordinary volatile scratch that startup happens to leave alone.
Startup RAM-test code copies exactly `0x20` bytes from
`0xFEF0FFD0..0xFEF0FFEF` aside, performs destructive testing over the containing
RAM region, and restores those 32 bytes afterward.

The helper at `0x17BC` tests `FEF0FFF0` against `0x5AA5A55A`; `0x17D2` clears the
magic. `0xE9E` calls both. Under its other reset/hardware predicates, magic
presence contributes the `0xE0` mode component; the function ultimately returns
true only for the complete `0xE9` state. Magic is therefore necessary in this
recovered path but not by itself sufficient.

The reset/startup caller at `0xBD0` passes that boolean into `0x10AC`. After the
runtime relocation, `0x10AC` calls the body sourced from CodeFlash `0x921E`; the
function stores a value `0` or `1` in its GP-relative runtime state. Reset setup
establishes `GP=FEC0102C`, placing that byte at runtime `FEBF9809`.

The same startup then loads the RAM segments described in §1. The RPRG module's
entry is called through the split-image seam at logical `0xA304` / runtime
`FEBF0924` during subsystem initialization. The exact downstream consumer of the
programming-mode byte has not yet been assigned a semantic name, so the evidence
boundary is “startup passes the mode into the common RAM runtime,” not “this
specific RPRG function is proven to branch on that byte.”

## 5. SecurityAccess and payload-build roots are recoverable from this image

The airbag image contains two adjacent 16-byte roots in the common CodeFlash
portion immediately before the AES tables:

```text
CodeFlash 0xC3AC  8af2c4708cd9cdec494da7acdaa9a8f7
CodeFlash 0xC3BC  8f69e6dc2a4b80b45054b4827a5ab622
```

They are not the three roots shared by the tracked P1M-E EPS images. None of the
EPS payload-build (`ba052435...`), boot-SA (`f05f36b7...`), or application-SA
(`893e0841...`) values occurs in either yc artifact. The two airbag roots each
occur exactly once in `cflash.bin`.

The relocation row `0xBBAC..0xC3CC -> FEBFB770` places the two roots at runtime
`FEBFBF70` and `FEBFBF80`. Static pointer indirection and the actual crypto call
chains establish different roles for them.

### 5.1 Payload-build root: `8af2c4708cd9cdec494da7acdaa9a8f7`

This first root is the payload-build root for the RPRG RequestDownload path, not
merely an unused AES-looking constant.

The WDBI dispatcher at CodeFlash `0x654A` explicitly recognizes DIDs `0x0201`,
`0x0202`, and `0x0203`. Its `0x0201` handler at `0x64DE` stores exactly 16 bytes
at the first credential slot; the `0x0202` handler at `0x6514` stores another
16 bytes at the second slot. The KDF path then does:

```text
0x66C8  copy DID 0x0201[16] into KDF input
0x62A6  AES-128-ECB-ENC(root @ FEBFBF70, DID0201) -> derived key
0x6716  copy DID 0x0202[16] into crypto setup input
0x630A  initialize payload crypto context with derived key + DID0202 IV
```

The runtime lookup used by `0x62A6` is `TP-0x735C = FEBFBCC4`. That cell is the
relocated form of CodeFlash `0xC100`, whose dword points to `FEBFBF70`, exactly
the relocated first root. Its AES wrapper reaches the recovered forward AES
block primitive at CodeFlash `0xA38A`.

The resulting KDF is therefore:

```text
Kpayload = AES-128-ECB-ENC(
    8af2c4708cd9cdec494da7acdaa9a8f7,
    DID_0201[16]
)
```

`DID_0202[16]` is installed as the 16-byte IV in the payload crypto context.
This KDF is reached from the RPRG RequestDownload setup (`0x01004036 ->
0x01003F14` on the normal branch) through the relocated `0x7A4C -> 0x635C`
call. That closes the role strongly enough to call the first value the
**payload-build root**, rather than only a generic crypto key.

This is notably the same *construction shape* as the P1M-E EPS payload gate —
AES(root, DID0201), with DID0202 supplying the IV — but the root value is
rotated and the implementation is not byte-identical.

### 5.2 Boot/RPRG SecurityAccess root: `8f69e6dc2a4b80b45054b4827a5ab622`

The second root belongs to the 16-byte RPRG SecurityAccess service. The RPRG SID
`0x27` configuration exposes `0x01/0x02` request-seed/send-key with 16-byte
material. Its lower send-key path at CodeFlash `0x7820` derives a 16-byte
expected key and byte-compares all 16 bytes before accepting the unlock.

The root lookup in `0x77B4` is `TP-0x7290 = FEBFBD90`. That is the relocated
form of CodeFlash `0xC1CC`, whose dword points to `FEBFBF80`, exactly the second
root. The two-stage construction is:

```text
0x77B4: initialize AES with root @ FEBFBF80;
        inverse AES block transform over the 16-byte request-seed auxiliary block
0x77EC: initialize AES with that 16-byte result;
        forward AES block transform over the retained 16-byte seed
0x7820: compare the resulting 16 bytes against the tester's 27 02 key
```

The forward and inverse block implementations are the same recovered AES core at
`0xA38A` / `0xA4A8`. In compact form, for the buffers used by this RPRG:

```text
Ktmp     = AES-128-ECB-DEC(BOOT_SA_ROOT, request_seed_aux[16])
expected = AES-128-ECB-ENC(Ktmp, seed[16])
```

with:

```text
BOOT_SA_ROOT = 8f69e6dc2a4b80b45054b4827a5ab622
```

The request-seed routine stores the request's 16-byte auxiliary block and the
returned 16-byte seed separately, so these are not inferred aliases of one
buffer.

### 5.3 Application SecurityAccess does not use another hidden 128-bit root

The ordinary airbag application also has SID `0x27`, but its configured levels
are a different design. The recovered send-key workers use two-byte seeds and
inline transforms:

| Subfunctions | Expected two-byte key |
|---|---|
| `03/04` | `(~seed + 0x4544) & 0xFFFF` |
| `05/06` | `(~seed + 0x4C6E) & 0xFFFF` |
| `07/08` | `(~seed + 0x61A4) & 0xFFFF` |
| `1F/20` | bytewise `~seed` |
| `5F/60` | bytewise `~seed` |

The relevant workers are `0xCAA2C`, `0xCAA94`, `0xCAAFE`, `0xCAB66`, and
`0xCABB4`. Thus no third 16-byte application-SA secret analogous to the EPS
`0x20840` root is present in the configured application unlock algorithm. The
application's seed-generation machinery does use AES internally, but the
SecurityAccess acceptance secret is the inline arithmetic above, not another
hidden 128-bit CodeFlash root.

The important transfer boundary remains unchanged: these two recovered airbag
roots are **airbag-specimen credentials**. Their values must not be projected
onto the Camry EPS merely because both systems use Toyota/Denso RH850
reprogramming architecture.

### 5.4 No plaintext SecOC key is identified in the supplied dump

A separate search for an operational SecOC/AES-CMAC key does **not** identify
one in either supplied artifact. The two unexplained-looking 16-byte constants
at `0xC3AC` and `0xC3BC` cannot be repurposed as SecOC candidates: the call
chains above already assign them independently to RequestDownload payload
construction and RPRG SecurityAccess. Known comparison credentials from the
tracked EPS specimens likewise do not occur in `cflash.bin` or `boot.bin`.

There is additional application-side AES material in CodeFlash: a second
standard forward/inverse AES table set begins at `0x22EE1` / `0x22FE1`, distinct
from the RPRG AES tables at `0xC3FD` / `0xC4FD`. That establishes more AES
capability in the image, but not SecOC by itself. The current static project has
no recovered direct reference from executable code into the second table set,
and a focused search did not recover a software-CMAC subkey path around the
standard `0x87` reduction constant. Therefore neither those tables nor any
adjacent 16-byte data are assigned as an operational SecOC key.

This negative is deliberately scoped to the supplied artifacts. yc provided
CodeFlash plus the extended-user RPRG image, **not DataFlash or protected
security-hardware contents**. A live SecOC key could therefore reside in a
non-CodeFlash persistent object or a hardware-backed key slot without appearing
as plaintext in these files. The exact airbag MCU/security peripheral is still
unresolved, so this note does not assume the EPS ICU-S implementation transfers
to the airbag ECU.

### 5.5 No ICU-S/HSM SecOC call path is recovered

The supplied airbag CodeFlash/RPRG also does not show the runtime hardware-CMAC
shape recovered from the tracked P1M-E EPS family. On those EPS images, the
Renesas ICU-S path is unambiguous: command 5 (MAC generation) and command 7
(CMAC verification) stage data through `ICUSDAT` at `0xFFC5D004`, poll status
at `0xFFC5D00C` / `0xFFC5D014`, and finally write `(key_selector << 16) | 5`
or `(key_selector << 16) | 7` to `ICUSCMD` at `0xFFC5D000`.

A complete executable-reference census of the yc CodeFlash finds **zero**
references anywhere in `0xFFC5D000..0xFFC5D03F`. A raw-byte search of both
`cflash.bin` and `boot.bin` likewise finds no 32-bit literal from that register
block. The whole high-MMIO reference census contains no `0xFFC5Dxxx` page at
all. Therefore this image is not calling the same ICU-S interface used by the
known P1M-E EPS implementation.

The nearby `0xFFC5B000` accesses in the airbag image are not evidence for
ICU-S. They are startup/system-control accesses: the airbag toggles that register
during early initialization and memory/protection setup, and the known Sienna
and Camry P1M-E images independently use the same `0xFFC5B000` family while
their actual ICU-S crypto engine remains at `0xFFC5D000`.

A second structural pass searched every high-MMIO write for the characteristic
`(selector << 16) | command` construction used by ICU-S commands 5/7/8. The
matches resolve to ordinary flash/controller/channel-register setup; none forms
a crypto command/data/status sequence. The software side is negative as well:
the application contains a second AES table set, but no executable references
to it are currently recovered and no AES-CMAC subkey path using the standard
`0x87` reduction step was found.

The bounded conclusion is therefore: **no SecOC signing or verification call
path is recovered from the supplied airbag image, either through the known
P1M-E ICU-S interface or through an identified software-CMAC implementation.**
This is not proof that the ECU cannot participate in SecOC. The exact airbag MCU
and security peripheral are unresolved, so another HSM interface remains
possible, and DataFlash / protected hardware-key contents were not supplied. A
future DataFlash key candidate would still need a runtime consumer or live-CMAC
validation before being called the operational SecOC path.

## 6. What the yc image changes for F33 EPS recovery

### It disproves one tempting interpretation

The received `boot.bin` is not the RH850 on-chip serial-programming firmware and
is not evidence that an external `10 02` packet is interpreted before ordinary
CodeFlash startup. The airbag's own bytes show a normal DCM-mediated programming
transition and a RAM-loaded extended-user RPRG module.

Blindly spamming `10 02` at F33 power-up is therefore not supported by this
artifact. On the currently poisoned F33 image, the scheduled application DCM
worker and normal programming handoff are after the malformed foreground call,
so the known failure still prevents that ordinary path from executing.

### It does establish a useful Toyota/RH850 implementation pattern

A Toyota RH850 ECU can combine:

1. normal application DCM programming-session policy;
2. a retained handoff record deliberately preserved through startup RAM test;
3. startup mode selection based on that retained state; and
4. an RPRG component stored in extended-user flash and relocated into RAM.

That is a concrete pattern to search for in other Toyota RH850 families, but it
must be searched from each target's bytes rather than transferred by analogy.

### It sharpens the hardware-boot distinction

For the exact Camry F33 MCU, R7F701381/P1M-E manufacturer documentation provides
a separate serial-programming mode selected by FLMD pins at pin-reset release.
That on-chip boot firmware does not depend on the application CodeFlash being
healthy. It is therefore still the interesting hardware bypass if a safe,
externally accessible FLMD/reset route can be established from the exact rack
hardware. The yc `boot.bin` neither proves nor disproves that physical access.

No pin should be shorted based on the airbag artifact. The remaining physical
question is connector/test-pad identification and electrical qualification on
the exact F33 EPS.

## 7. Cross-image transfer boundary

A complete-body comparison against the first-class F33 corpus found 63 exact
complete-function matches among 6,065 F33 functions, with the largest relocation
cluster in generic/library-looking code. No named semantic F33 function
transferred exactly into the airbag image. A structural fingerprint comparison
likewise found no named exact-shape transfer.

That is enough to reject “same boot code” as a working assumption. The airbag
image is valuable as an implementation example, not as an address or patch map
for F33.

The contributor's RH850/glitch-acquisition statement remains relevant in a
different way: a clean exact-F33 read of its extended-user region would be useful
new evidence if obtainable without relying on the poisoned application, because
ordinary CodeFlash dumps do not establish what, if anything, the F33 stores
there.
