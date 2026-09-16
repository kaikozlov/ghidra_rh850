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
has no analogous third 128-bit acceptance root.

The separate **ECU Security Key / rekey** question is now closed much further.
This image contains configured SecOC in **both directions**: four receive
verification profiles and two transmit MAC-generation profiles. All six resolve
crypto-config ID `0` to one 20-byte type-1 config whose logical key selector is
**4**. That config object is byte-identical to the selector-4 object used by the
tracked EPS family, even though the airbag's secure-engine ABI is different.
The network-authentication key itself is represented only by that selector at
the application boundary. The crypto request is queued through shared `0xFE...`
RAM and the RH850 system-reserved `0xFF1F...` window to the P1x-C secure
subsystem. More importantly, application RoutineControl RID `0x1010` accepts exactly the
**standard AUTOSAR SHE `CMD_LOAD_KEY` Memory Update Protocol** request
`M1[16] || M2[32] || M3[16]` and returns status plus the standard
`M4[32] || M5[16]` verification proof. The asynchronous worker routes that
64-byte package through the same secure subsystem instead of manipulating a
plaintext key in CodeFlash. Toyota has supplied the UDS carrier and backend
orchestration; the cryptographic M1--M5 construction itself is standard SHE.

Current GTS+ independently closes the host side of that path. Its
`UtilityExNK2.dll` `MAC_01` implementation contains a direct
`31 01 10 10 || M1 || M2 || M3` start followed by `31 03 10 10` result polling,
in addition to the newer `0x3002` transport already recovered from Techstream.
Toyota's public ECU Security Key bulletin includes 2021 Venza HV in the key-write
procedure, and Toyota's Techstream known-bugs page explicitly lists a 2021 Venza
HV “ECU Security Key write process” failure mode. The firmware, host utility,
and service procedure therefore agree on the architecture: **“rekey” means
provisioning the HSM-backed network authentication credential, not satisfying
RPRG SecurityAccess.** Sections 5.4–5.7 give the bounded static join.

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

The glitch-acquisition method is contributor-provided. The vehicle/ECU
attribution is now independently corroborated by the raw identity and dealer OEM
parts data: CodeFlash contains `8917048E30`, and Toyota parts catalogs identify
`89170-48E30` as the 2021–2022 Venza air-bag sensor/diagnostic unit. The exact
RH850 MCU part number is still not established by the supplied metadata. Do not
transfer airbag SFR addresses or this DCM layout to P1M-E merely because both
ECUs are RH850.

External service-procedure corroboration is likewise bounded but unusually
specific. Toyota T-SB-0111-20, “ECU Security Key Writing,” covers 2021 Venza HV
and states that replacement of covered ECUs can require an ECU Security Key to
be written before normal network communication. Toyota's Techstream known-bugs
page separately names 2021 Venza HV in an “ECU Security Key write process ends
with error” item. Neither public item exposes key material or proves which
internal GTS protocol branch a particular SRS part selects; the protocol join
below comes from the supplied firmware plus the pinned local GTS+ binary.

Public corroboration used here:

1. Toyota Motor Sales, USA, [T-SB-0111-20 Rev1 — ECU Security Key Writing](https://static.nhtsa.gov/odi/tsbs/2022/MC-10224141-9999.pdf), revised July 8, 2022.
2. Toyota Motor Sales, USA, [Techstream Known Bugs, Version 18.00.008](https://techinfo.toyota.com/techInfoPortal/staticcontent/en/techinfo/html/prelogin/tsrss/ts_known_bugs.html), updated March 15, 2023.
3. Camelback Toyota Parts, [89170-48E30 SDM Module](https://parts.camelbacktoyota.com/oem-parts/toyota-sdm-module-8917048e30), identifying the part as a 2021–2022 Venza air-bag sensor/diagnostic unit.

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

### 5.4 No plaintext operational SecOC key is present in the supplied dump — and the runtime explains why

A raw/structured search still does **not** identify a plaintext operational
SecOC key in either contributor artifact. That negative is now meaningful
rather than merely inconclusive. The two CodeFlash roots recovered above have
complete, independent callers in the reprogramming path; neither is passed to
the application SecOC implementation. The known EPS roots are also absent.

The application SecOC callers instead carry a small key/configuration selector
through generated crypto records. No 16-byte key crosses the application-side
MAC generation or verification adapters. That is exactly the shape expected
when the actual network key is owned by a secure subsystem rather than ordinary
CodeFlash.

The live SecOC configuration is also concrete, including the key selector and
both directions of traffic.

Application startup sets `TP=0x24050`. SecOC initialization at `0xDD6F4` passes
`TP-0x69A8 = 0x1D6A8` to the only configured crypto-config setter. The exact
20-byte object is:

```text
01 00 00 00  04 00 00 00  00 00 00 00  00 00 00 00  00 00 00 00
```

That is the same generated shape used in the tracked P1M-E EPS images:
`type=1`, logical key selector **4**, with the remaining 15 bytes zero. This is
an exact byte-level structural join, not a guessed semantic transfer. The
important boundary is the next layer: on P1M-E EPS firmware selector 4 is
literally encoded into the ICU-S command-7 command word; on this airbag the same
logical selector is copied into a request descriptor for a different local
secure-service/HSM interface. Therefore **logical selector 4 is proven here;
physical secure-storage slot numbering equivalence to P1M-E ICU-S is not.**

The value `4` is also not an arbitrary application allocation. AUTOSAR SHE's
standard four-bit key-ID namespace reserves `0x0` for `SECRET_KEY`, `0x1` for
`MASTER_ECU_KEY`, `0x2` for `BOOT_MAC_KEY`, and `0x3` for `BOOT_MAC`;
**`0x4` is `KEY_1`, the first general-purpose nonvolatile application key**.
`0x5..0xD` are `KEY_2..KEY_10` and `0xE` is `RAM_KEY`. Renesas publicly states
that both ICU-S and ICU-M secure-boot designs can be based on the AUTOSAR/HIS
SHE model. Combined with this airbag's standard SHE M1/M2/M3 -> M4/M5
`CMD_LOAD_KEY` protocol, the selector-4 match strongly supports the
interpretation that Toyota is using the standard SHE logical namespace and
placing its TSK/SecOC key in
`KEY_1`, not choosing an unexplained fourth Toyota-specific slot.

That does **not** reveal the actual contents of IDs `1..3` on this specimen.
Those values live behind the ICUM secure boundary and were not part of yc's
MainPE CodeFlash/RPRG dump. Their standardized roles are `MASTER_ECU_KEY`,
`BOOT_MAC_KEY`, and `BOOT_MAC`; whether each is populated, empty, or superseded
by an ICU-M-specific secure-boot policy requires the secure-side firmware/data
or a legitimate key-update transcript. The MainPE SecOC graph itself selects
only `KEY_1`/ID `4`; it has no configured production SecOC profile selecting
IDs `1`, `2`, or `3`.

The MainPE MAC adapters themselves do not impose that SHE-role policy. The
crypto-config setter validates the config type but does not range-filter the
selector byte, and the Tx/Rx adapters copy config byte `+4` directly into their
secure-service requests. Thus MainPE can syntactically request selectors
`0x0..0x3`; acceptance is left to ICUM. Standard SHE predicts: no MAC generate
or verify for IDs `0`/`1`/`3`, and **verify-only** for ID `2` (`BOOT_MAC_KEY`).
The literal P1M-E command-5/7 numbers do not transfer to this different ICUM ABI;
the corresponding airbag operations are its recovered MAC-generate/MAC-verify
secure-service requests.

The generated route-set helper at `0xDD23A` exposes two Tx routes and four Rx
routes. The four receive profiles are `0x50` bytes each:

| Record | SecOC DataID field | Configured PDU/buffer length | Crypto config |
|---:|---:|---:|---:|
| `0x1D6C8` | `0x00F` | 8 | 0 -> selector 4 |
| `0x1D718` | `0x090` | 32 | 0 -> selector 4 |
| `0x1D768` | `0x0D7` | 32 | 0 -> selector 4 |
| `0x1D7B8` | `0x024` | 32 | 0 -> selector 4 |

The receive worker at `0xDE09E` uses a `0x50`-byte stride, resolves each row's
config ID through the common config getter, and reaches the MAC-verification
adapter. So this is a configured production receive-verification graph, not
merely crypto library residue.

Transmit uses a distinct `0x44`-byte generated descriptor type, not another
`0x50`-byte receive record. There are exactly two profiles:

| Record | Authenticated SecOC DataID field | Crypto config |
|---:|---:|---:|
| `0x1D808` | `0x0326` | 0 -> selector 4 |
| `0x1D84C` | `0x0024` | 0 -> selector 4 |

The Tx worker at `0xDE9F0` uses a `0x44`-byte stride and places the `u16` at
record `+0x0C` into the authenticated material as the SecOC DataID before
calling the MAC-generation dispatcher. Both Tx rows likewise select config ID
0. The table DataID is a SecOC authentication-domain value; this report does
not promote it to a physical CAN arbitration ID without the separate Com/CAN
routing join.

This makes the directional comparison with the EPS family unusually sharp:
**the tracked Sienna/P1M-E application graph is configured receive-only, while
this Venza airbag is configured bidirectionally — four protected receives and
two protected transmits — and both directions use logical selector 4.**

This closes the earlier search question in the useful direction: **absence of a
plaintext SecOC key from CodeFlash is expected for this implementation and is
not evidence that the airbag lacks SecOC.**

### 5.5 The actual SecOC backend is a local P1x-C secure-service path

The airbag does not use the P1M-E EPS's `0xFFC5D000` ICU-S command-register ABI.
Instead it uses a second, self-contained local crypto stack whose final service
boundary is the RH850 `0xFF1F...` system-reserved window plus shared `0xFE...`
RAM. Public P1x-C documentation identifies the corresponding security block as
ICUMC, a dedicated secure RH850/G3K subsystem with Secure DataFlash; the detailed
security-hardware command semantics live in the separate Renesas Security
Hardware Manual. Therefore the observed request opcodes below are intentionally
left as numeric protocol values rather than assigned proprietary command names.

The application-side paths are:

```text
SecOC TX worker  0xDE9F0
  -> MAC-generation dispatcher 0xBCCF4
  -> lower adapter 0xBDC7A
       request descriptor @ FEFF02B8
       observed opcode 0x12
       key selector from config+4

SecOC RX worker  0xDE09E
  -> MAC-verification dispatcher 0xBCEFA
  -> lower adapter 0xBDE88
       request descriptor @ FEFF0330
       observed opcode 0x12
       key selector from config+4
```

For both paths, the lower adapter copies byte `+4` of the recovered 20-byte
crypto config into the secure request descriptor. Since every configured Rx/Tx
profile selects config ID 0, both verification and generation reach the secure
subsystem with logical selector **4**.

Both lower adapters converge on `0xBD69E`, which submits through `0x8A18A`.
`0x8A18A` records the current PE identity and passes the descriptor into the
secure-service queue. `0x89E60` reads the service's shared-RAM pointer from
`0xFF1F0014`, derives the `0xFE000000` shared address, and enqueues the request
in a four-entry ring. `0x89F6E` then writes the service trigger at `0xFF1F0044`.
Initialization at `0x864E4/0x86510` configures the same boundary.

The key observation is the interface itself: ordinary application code supplies
message/tag buffers, lengths, callbacks, and a selector; it does **not** supply
plaintext AES key bytes. This is the firmware-static reason the operational
network key is not recoverable by scanning the supplied CodeFlash/RPRG images.
It may reside in ICUMC Secure DataFlash or other security-owned state, but its
actual secure-storage slot contents are outside these artifacts.

### 5.6 RoutineControl RID `0x1010` is the airbag's authenticated ECU Security Key update

The application has 19 configured RoutineControl RIDs. The exact table at
`0x255E4` contains, at index 9, **RID `0x1010`**. Its generated dispatchers are
not generic reprogramming code: their input/output geometry joins directly to
the secure key-update path.

StartRoutine stages exactly 64 bytes:

```text
31 01 10 10 || M1[16] || M2[32] || M3[16]
        |
        v
RID table index 9
  -> start dispatcher 0xC1C06 case 9
  -> wrapper 0xCB18A
  -> 0x69458 -> 0x7B306
       copy 0x40 request bytes to FEFF0168
       mark operation pending
       return status byte + 48 zeroed result bytes
  -> asynchronous worker 0xB76D4
  -> key-update dispatcher 0xBD2EC, record 0
  -> lower adapter 0xBE0CC
       require 0x40-byte input
       require >=0x30-byte result buffer
       split input as +0x00 / +0x10 / +0x30
       split result as +0x00 / +0x20
       observed secure-service opcode 0x31
  -> 0xBD69E -> secure-service boundary
```

The offsets make the standard SHE envelope explicit: the 64-byte request is
`16 + 32 + 16`, and the successful 48-byte proof/result is `32 + 16`, exactly
matching AUTOSAR `CMD_LOAD_KEY` (`M1/M2/M3` in, `M4/M5` out). The result path is:

```text
31 03 10 10
  -> result dispatcher 0xC1B00 case 9
  -> 0xCADF4 -> 0x69476 -> 0x7B3A6
  -> status || M4[32] || M5[16]
  -> terminal read clears the staging bank
```

A second worker mode routes through record 1 and a small opcode-`0x04` secure
request. Its exact proprietary meaning is not assigned here. It is not needed
to establish the 64-byte authenticated update and 48-byte proof geometry.

This resolves the service-information terminology. The ECU can be placed into
RPRG programming mode using the separate `10 02`/SecurityAccess path described
above, but **that does not install the network authentication key**. ECU Security
Key writing is a separate application RoutineControl operation that asks the
secure subsystem to authenticate and commit a key-update package.

### 5.7 Current GTS+ contains the matching official `MAC_01` RID-`0x1010` host path

The local 2026 GTS+ install provides the missing host-side join in
`UtilityExNK2.dll` (SHA-256
`d9868c8a9a69ffbab26ea7d4431e290372cd207e84e7b4aed27446aeb4c12ec1`).
This is the same DLL family that exports the official `Ex2MAC_01_*` ECU Security
Key operations.

One helper at VA `0x100F9FE0` constructs exactly:

```text
31 01 10 10 || M1[16] || M2[32] || M3[16]
```

and sends `0x44` bytes. A paired helper at VA `0x100F9EF0` sends
`31 03 10 10`, validates the response, and copies a 32-byte field plus a 16-byte
field. Worker `0x100FA9C0` runs start then polls that result path. More strongly,
exported `Ex2MAC_01_ComProcess @ 0x10028590` selects the `0x100F9740` state
machine containing that worker for one supported MACKey protocol family.
Therefore RID `0x1010` is not merely a firmware-private routine: current Toyota
service software contains a first-class `MAC_01` implementation of the same
wire protocol and M1–M5 geometry.

The same current GTS+ binary also contains the newer `0x3002` form recovered
from Techstream V18:

```text
31 01 30 02 || M1 || M2 || M3
31 03 30 02 -> state || M4 || M5
```

So the correct host conclusion is **multi-generation protocol support**, not
“Toyota tooling uses only `0x3002`.” Static GTS analysis alone does not tell us
which branch a live 2021 Venza SRS session selects. The exact airbag firmware,
however, implements `0x1010`, making that GTS branch the structurally matching
candidate.

This also defines the remaining barrier to arbitrary rekeying. The ECU-side
primitive is callable, but an accepted `M1/M2/M3` package is cryptographically
authenticated by the secure subsystem. The recovered RPRG roots do not supply
that authorization. Without the existing update/authentication key, secure
storage contents, or a valid Toyota server-produced exchange-key package, we
cannot synthesize an arbitrary new network key merely from this CodeFlash dump.
A live GTS key-write capture is now the highest-value way to bind the exact
2021 Venza service transaction and server material.

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
