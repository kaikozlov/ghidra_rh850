# 2023 US Corolla public route — SecOC traffic and topology evidence

> **Scope:** public comma route `a74eba85c97eaf67|00000004--555953f500`,
> discussed as a 2023 US Corolla in comma `#toyota-security`
>
> **Firmware identity from tracked CodeFlash:** `8965H1202000` / `8A3111202000`,
> MCU `R7F701383`, serial `8965012N50A05G310920`
>
> **Direct UDS F181 transcript:** not retained; the live-ID blocks above are
> firmware-static evidence from the acquired image
>
> **Status:** route evidence + complete contributor memory corpus acquired;
> CodeFlash semantics now independently analyzed
>
> **Evidence source:** public logged route + pinned Panda/opendbc source +
> contributor-supplied TSKM/CodeFlash/DataFlash/RAM artifacts + external Discord
> vehicle attribution
>
> **Machine-readable summaries:**
> `data/generated/corolla_2023_public_route_summary.json` and
> `data/generated/corolla_2023_albino_dataflash_analysis.json`

This specimen must remain separate from the earlier
[`8965F1208000`](corolla-8965F1208000.md) Corolla investigation. The earlier
variant has an exact application software ID from direct field probing. This
public route still does **not** identify its physical EPS: its logged software
was deliberately forced to an old `TOYOTA_COROLLA_TSS2` fingerprint and contains
no `carFw` inventory. The later contributor memory corpus independently closes
the firmware side for this specimen: its CodeFlash live-ID blocks identify
`8965H1202000` / `8A3111202000`. An embedded `8965F1208000` string at
CodeFlash `0x20860` is a table entry and must not be mistaken for Span's distinct
`8965F1208000` ECU.

The public route is nevertheless highly useful because it resolves which CAN
traffic was genuinely received from the vehicle and which apparent steering
traffic was merely Panda's echo of openpilot's own transmissions.

## 1. Route and software provenance

The comma route API exposed 29 qlogs and 29 rlogs at analysis time. The
repository pins the route identifier, all 29 qlog SHA-256 hashes, and one full
segment-0 rlog hash in `external-references.lock.json`; expiring signed download
URLs are intentionally not retained.

The route's own `initData` reports:

```text
software: sunnypilot
version:  2026.002.001
branch:   release-mici
commit:   af744c85e7c971e7bfbc8e6ee9e2bd75452a6f00
```

Its active `carParams` reports:

```text
brand:                    toyota
carFingerprint:           TOYOTA_COROLLA_TSS2
fingerprintSource:        fixed
carFw:                    []
VIN:                      placeholder zeros
networkLocation:          fwdCamera
openpilotLongitudinal:    true
secOcRequired:            false
secOcKeyAvailable:        false
```

`CarParamsPersistent` contains the same forced Corolla-TSS2 identity; the prior
route parameter is `MOCK`, also with no firmware inventory. There is therefore
no hidden F181/firmware identity in the logged parameters.

**Consequence:** the route alone still cannot independently prove model year or
EPS calibration. The contributor's later CodeFlash is now an independent ECU
identity artifact for the same externally attributed specimen; the 2023-US
vehicle attribution itself remains an external field statement because no stock
`carFw`/VIN-bearing route inventory joins the route to the image.

## 2. Genuine incoming protected-family traffic

Full segment-0 rlog analysis distinguishes ordinary incoming CAN (`src < 128`)
from Panda returned/rejected transmit echoes.

Genuine vehicle traffic includes:

| source | CAN ID | DLC | frames | interpretation |
|---:|---:|---:|---:|---|
| 1 | `0x00F` | 8 | 588 | Toyota classic SecOC synchronization family |
| 1 | `0x116` | 8 | 2,499 | `GAS_PEDAL` in pinned classic-SecOC DBC |
| 1 | `0x24D` | 8 | 59 | `PCM_CRUISE_4` in pinned classic-SecOC DBC |
| 0 | `0x183` | 64 | 1,221 | CAN-FD traffic, **not** classic 8-byte `ACC_CONTROL_2` wire shape |
| 2 | `0x183` | 64 | 216 | same 64-byte CAN-FD ID on another bus |

Representative genuine frames:

```text
0x00F: 0ce9000e0b3e61d5
0x116: 00000011cae9d0a5
0x116: 00000011064dcdaf
0x24D: 00fb008052b1a741
0x24D: 00fb0080777f764d
```

Pinned `toyota_secoc_pt.dbc` independently identifies `0x116` and `0x24D` as
classic 8-byte protected messages with the 28-bit authenticator + reset flag +
message-counter-low2 trailer used by Toyota's known classic SecOC construction.

### Freshness-field structural check

Using each latest bus-1 `0x00F` synchronization value as the current reset
state, the low two bits of the protected frame's transmitted high-nibble agree
with `RESET_CNT & 3` for:

```text
0x116: 2476 / 2496 eligible frames = 99.20%
0x24D:   59 /   59 eligible frames = 100%
```

The small `0x116` mismatch population is consistent with capture/event ordering
near synchronization transitions and is not interpreted further without a
monotonic raw-event analysis.

This is strong **structural** evidence that these frames use the known Toyota
classic freshness trailer. It is not cryptographic proof of a production key:
that requires CMAC validation against an actual candidate key.

## 3. Apparent steering traffic was openpilot's own output

The route contains apparent `0x191` and `0x2E4`, but source metadata changes the
interpretation completely.

Pinned pandad defines:

```text
CAN_RETURNED_BUS_OFFSET = 0x80
CAN_REJECTED_BUS_OFFSET = 0xC0
```

and adds those offsets to the physical bus number when publishing CAN events.
Thus `src=128` means a returned transmission from logical bus 0, not a frame
received from the stock camera.

Segment 0 shows:

| event | source | CAN ID | DLC | frames |
|---|---:|---:|---:|---:|
| `sendcan` | 0 | `0x191` | 8 | 2,519 |
| returned `can` | 128 | `0x191` | 8 | 2,512 |
| rejected `can` | 192 | `0x191` | 8 | 6 |
| `sendcan` | 0 | `0x2E4` | 5 | 5,037 |
| returned `can` | 128 | `0x2E4` | 5 | 5,025 |
| rejected `can` | 192 | `0x2E4` | 5 | 11 |

Representative returned frames are old-profile shapes:

```text
0x191: 8c000030640000ba
0x2E4: 9600000081
```

There is no genuine incoming classic `0x131` or `0x2E4` in the pinned segment-0
summary. This independently validates the Discord correction: the steering
frames initially interpreted as stock traffic were primarily what the forced
TSS2 profile itself wanted to transmit.

## 4. The 64-byte `0x183` is a useful architecture discriminator

The known classic Toyota SecOC DBC defines `0x183 ACC_CONTROL_2` as an **8-byte**
message. This route instead has genuine **64-byte CAN-FD `0x183`** traffic.

That does not by itself identify the newer protocol or authenticate its tail,
but it is direct evidence that this vehicle's network cannot be modeled by
blindly applying the classic TSS2/SecOC message dictionary by CAN ID alone.
CAN ID reuse across a different DLC/protocol family is present in the capture.

This makes the failure of a forced 2020–22/old-TSS2 Corolla profile unsurprising
and prevents interpreting that failure as evidence about EPS SecOC acceptance.

## 5. Why TSKM reported insufficient protected traffic

The contributor supplied the actual TSKM CAN output from the same successful dump investigation:

```text
community/albinoelephant/can_oracle.ndjson
```

It contains exactly 1,232 rows, all CAN `0x00F` synchronization frames: 616 on
Panda bus 0 and the same 616 on bus 2. There are **zero protected-message rows**.
That directly explains the TSKM matcher failure without making any statement
about whether the car itself emits protected traffic. All supplied TSKM sync
frames decode to `TRIP_CNT=0xD0D`. The oracle came from the same TSKM
investigation as the dump, but it is **not proven to be the same EPS runtime
epoch**: CAN collection and DataFlash dumping are separate mutually-exclusive
jobs, and the dump path enters programming mode, performs SecurityAccess,
uploads code, and executes it. Treat `0xD0D` as the closest local
synchronization-key oracle, not as a same-session guarantee.

The public route independently supplies the missing genuine bus-1 traffic:
`0x00F`, `0x116`, and `0x24D`. The repository therefore retains a compact
CAN-only extraction from its pinned segment-0 rlog at:

```text
community/albinoelephant/public_route_secoc_oracle.ndjson
```

It contains 588 `0x00F`, 2,499 `0x116`, and 59 `0x24D` frames; only three initial
`0x116` frames precede the first observed synchronization frame. Its sync frames
have `TRIP_CNT=0xCE9`, so the public route is a **different ignition freshness
epoch** from the local TSKM capture (`0xD0D`). This replaces the old
interpretation of `0 protected` with direct evidence: the local TSKM capture was
sync-only while the separately logged vehicle traffic contains the classic
protected-family IDs that TSKM's Sienna-shaped filter did not retain. It also
means protected-key conclusions made by pairing the public route with the dump
carry an explicit cross-session key-stability assumption.

## 6. Supplied DataFlash result

The contributor also supplied the complete TSKM DataFlash artifact:

```text
community/albinoelephant/dump_ff200000_ff208000.bin
size:   32768 bytes
sha256: 8ac2a6beecb4ca2e6caf695eebffe440478171b4e093a1b2a36ab4e4ff313299
```

`tools/analyze_toyota_dataflash.py` was run against the contributor's public
route oracle with `--domain-scan --min-entropy 0`. This removes the normal
entropy heuristic entirely: all 32,753 overlapping 16-byte windows are
considered and 23,277 unique raw windows are cryptographically probed against
synchronization, `0x116`, and `0x24D` independently.

**Result: zero candidate matches in any domain.**

The same 23,277 unique raw windows were also scanned against the supplied local
TSKM `0x00F` oracle and again produced **zero synchronization-key matches**.
This is closer evidence than the older public route, but it still cannot prove
runtime-key continuity across the separate CAN-capture and programming/dump
jobs. It therefore excludes a static raw DataFlash value equal to the locally
observed synchronization key, not a session-derived key. The `0x116`/`0x24D`
protected-domain negative uses the older public-route session and carries an
even wider key-stability boundary.

As a bounded derivation check, all 23,277 unique dump windows were also tested
after each of six simple transformations — XOR55, XORAA, bitwise NOT, complete
16-byte reversal, per-32-bit byte swap, and per-16-bit byte swap — against the
public-route domains. None survived even the first cryptographic probe. This
rules out those obvious representations, not arbitrary KDF/encryption schemes.

The result is therefore a strong cryptographic negative for a **static raw
CPU-visible synchronization key** in this DataFlash snapshot, with strong but
cross-session evidence against a raw protected key. It does not prove that the ECU lacks
SecOC, that the key is absent from every other storage region, or that ICU-S/HSM
cannot own or derive it internally.

### Shared NvM structure, different provisioning state

Applying the complete physical NvM geometry recovered from `8965B4512000`
produces a much stronger cross-family result than the initial triplicate-only
pass. The Corolla dump has **60 committed records** at the 122 reference
extents: 9 triplicate records and **51 checkpoint records**. All 51 committed
checkpoint records also satisfy the expected `generation/~generation` envelope
at the inverse location predicted by the reference descriptor geometry.
Forty-nine map to reference-enabled checkpoint owners.

The two exceptions are storage indexes **117** (`0xFF204280`) and **118**
(`0xFF204200`), which the `4512000` map assigns to disabled checkpoint owner 28.
In the Corolla dump they form a coherent two-slot ring: generations `0x25` and
`0x24`, exact complements at physical offset `+0x40`, and committed
`0xAAAAAAAA` trailers. Both contain nonzero data well beyond the reference
owner-28 8-byte payload boundary. This is strong evidence that the physical
storage geometry transfers while Corolla descriptor/provisioning semantics do
not exactly match `4512000`.

At the same triplicate locations, objects 0, 2, and 5 each have all three
committed raw/XOR55/XORAA copies and decode to one consensus payload. Objects
1, 3, 4, 6, 12, 13, 14, and 15 have no valid copy. The previously opaque second
header word is now recovered as a reader-enforced short-record additive
checksum, and all nine committed Corolla triplicate records satisfy it.

Two consensus payloads are byte-identical by hash to `4512000`:

- object 0: `d6775357ff967f93c5df8467e22fdc622fe0961761464776c7bff27d545cb2dc`;
- object 5: `af5570f5a1810b7af78caf4bc70a660f0df51e42baf91d4de5b2328de0e83dfc`.

Object 2 is valid at the same geometry but has a different payload. This is
strong evidence that at least part of the same physical NvM storage scheme is
present across the family rather than an accidental address coincidence.

Most importantly for the SecOC question, **object 15 has zero valid copies** and
does not reproduce the related `8965B4514000` CPU-visible key-storage result at
`0xFF206E14`.

The complete machine-readable result is
`data/generated/corolla_2023_albino_dataflash_analysis.json`.

## 7. 2026-08-18 full memory corpus and CodeFlash closure

The later contributor bundle is preserved unchanged under
`community/albinoelephant/raw-20260818/`; its own `MANIFEST.txt` pins the
individual file hashes and acquisition notes. The CodeFlash range-dumper artifact is
2 MiB because it reads `0x00000000..0x001FFFFF`, but bytes
`0x00100000..0x001FFFFF` are entirely `0xFF`. The actual one-megabyte image is
therefore the first half:

```text
source range dump SHA-256: 97f9d42d936b97a99e7ab3d3ef20c6fb4c1fc3cc2ba199f6b158675a1709aee6
normalized CodeFlash SHA-256: 0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f
MCU boot-info: R7F701383 / 72114350
ECU serial: 8965012N50A05G310920
live software IDs: 8965H1202000 / 8A3111202000
```

The image also contains `8965F1208000` at `0x20860`, but the primary live-ID
block is `8965H1202000` at `0x17D80`; the contributor manifest independently
records the same distinction. This closes the old calibration-unknown statement
for the firmware artifact without rewriting the route's still-forced identity.

### 7.1 Security roots transfer exactly

Three security roots are byte-identical to `8965B4512000` at the same CodeFlash
addresses:

| purpose | CodeFlash | value |
|---|---:|---|
| payload-build secret | `0xBFD8` | `ba052435f8843f985fd1329d2b6117b0` |
| boot SecurityAccess secret | `0xBFE8` | `f05f36b7d78c03e24ab4faef2a57d044` |
| application SecurityAccess secret | `0x20840` | `893e08418c741ffa2a9c044bffa55813` |

The foreign boot-SA stage-1 routine at `0x6FD0` is also byte-identical across its
50-byte extent to the Sienna routine at `0x6FEC`. The application root is not
merely an unreferenced constant: the foreign application path at `0x86BBC`
initializes its AES context from CodeFlash `0x20840`, and caller `0x86C2A` uses
the same `FEBF497A` / `FEBF495A` state family and 16-byte comparison shape.
This promotes the shared cryptographic architecture for `8965H1202000` from
family inference to firmware-static evidence.

The bootloader SecurityAccess state machine transfers more broadly than the AES
primitive alone: Sienna `0x5328..0x562D` is byte-identical to Corolla
`0x530C..0x5611` (`-0x1C` relocation). That span contains request-seed, send-key,
the failed-key counter, the delay worker, and SA initialization. Consequently
this tracked Corolla image has the same statically verified policy: first bad
`27 02` -> NRC `0x35`; second consecutive bad key -> NRC `0x36` plus a
`200000000`-tick RAM delay; `27 01` returns `0x37` until expiry; initialization
starts delayed with the attempt counter cleared. The shared boot timer domain
uses `20000` ticks/ms, making the nominal delay 10 seconds. None of this state is
persistent NVM. See [bootloader diagnostics](../diagnostics/bootloader.md) §2.1.

The acquisition itself is additional dynamic evidence for the authenticated-RAM
bootstrap: the contributor used TSKM range payloads to obtain CodeFlash,
DataFlash, and RAM owner-side over OBD. The contributor manifest explicitly says
no glitching, bench work, or module removal. This does **not** promote the exact
Sienna encrypted `ram_dump_payload.bin` bytes to verified on this calibration;
it proves target-built range-payload execution in the shared bootstrap family.

### 7.2 Gate-2 and CRC-resigning transfer

Running the calibration-independent Gate-2 resolver unchanged on a fresh
unannotated import returns exactly one candidate:

```text
Gate-2 function       0x88C16
CMP                    0x88C62  e0 d1
neutralized CMP        0x88C62  e0 01
preserved BNE          0x88C64  9a 0d
verified fallthrough   0x88C66
mismatch target        0x88C76
```

The independent CRC manifest builder finds two valid self-describing boot CRC
descriptors. The Gate patch lies in region 1 (`0x18000..0xFFDF0`), whose stock
fixup at `0xFFDEC` is `0xAD59D70C` and already validates to residue
`0xFFFFFFFF`. Applying only the resolved Gate CMP change gives prefix CRC
`0x22A0EB88`, fixup `0xDD5F1477`, and again residue `0xFFFFFFFF`. This is the
first tracked foreign-image proof that both the semantic Gate resolver and the
CRC-resigning backend transfer beyond `8965B4512000`.

The result is a patch for this image's **configured SecOC acceptance paths**, not
a claim that this Corolla uses Sienna's steering profiles. The profile census
below is what determines that applicability.

### 7.3 The configured SecOC queue is not Sienna's steering queue

The callback-free runtime semantic resolver also transfers far enough to recover
the foreign startup/scheduler skeleton and target-specific state:

```text
boot handoff          0x1394
startup coordinator   0x5CAAC
context init          0x6A8C4
foreground loop       0x5F30C
aggregate             0x5FAF2
GP                    FEBEB800
TP                    0x23D6C
tick counter          FEBE38EF
Com_RxIndication      0x76A3C
COM timeout helper    0x87A82
COM validity base     FEBE51C4
COM update base       FEBE5224
```

The important difference is queue 1. The generated queue helper at `0x87B72`
selects queue 1 at `0x87B92`, returning descriptor/head/raw bases
`FEBE5356/FEBE5350/FEBE5398` and an explicit **record count of 3**. Gate-2's
`index * 0x50 + TP-relative-base` machine shape independently locates the table
at `0x2572C`. Its three records are:

| index | CAN ID | PDU | raw offset | secured length |
|---:|---:|---:|---:|---:|
| 0 | `0x00F` | 9 | `0x00` | 8 |
| 1 | `0x0D7` | 40 | `0x08` | 32 |
| 2 | `0x0B6` | 42 | `0x28` | 32 |

There is no configured queue-1 `0x2E4` or `0x131` record. The correct runtime
resolver result is therefore
`semantic-resolved-steering-unsupported`, not a generic resolver failure and not
a build-ready steering bridge. This provides firmware-static support for the
earlier observation that this specimen does not look like the Sienna steering
SecOC participant: SecOC exists, but its configured protected domains differ.

### 7.4 Foreign image exposed three resolver overfits

The first implementation of the runtime resolver failed on this image despite
the architecture clearly transferring. The failures were real tooling bugs:

1. queue discovery matched one exact Sienna compiler layout instead of the
   generated queue-1 output contract;
2. table discovery required the literal six-ID Sienna order
   `00F/2E4/131/132/090/0D7` instead of deriving table base and count;
3. software-ID extraction accepted a 12-character prefix of the longer ECU
   serial `8965012N50A05G310920`.

The corrected resolver derives GP and TP from context setup, queue-1 bases/count
from the generated helper, and the record table from Gate-2's TP-relative
`index*0x50` access. `0x2E4/0x131` are now **bridge capability requirements**,
not discovery signatures. Software-ID extraction requires token boundaries. The
wrapper also accepts this exact 2 MiB range-dumper geometry only when the upper
1 MiB is all `0xFF`, normalizes it in a disposable workspace, and preserves both
source and normalized hashes in the output manifest.

The Sienna target remains byte-for-byte build-ready under the generalized code;
the tracked `8965H1202000` image is now the foreign regression proving that a
non-steering profile set resolves successfully and fails closed at capability
selection.

### 7.5 Lochuan checkpoint semantics transfer too

The eight-byte context around the old Sienna Lochuan byte at `0x664E6` occurs
exactly once in the foreign image, at `0x6081A`; the homologous status byte is
`0x6081E = 0x31`. Its containing foreign function `0x6077E` has the same
checkpoint-completion shape: a successful lower result publishes `0x10`, while
a non-`0x5A` result publishes `0x31` and separately records failure state.
Thus the earlier conclusion that `0x31 -> 0x10` is a checkpoint/NvM fail-open,
not a SecOC Gate-2 bypass, independently transfers to this Corolla image.

### 7.6 The same image closes the EPS side of the Toyota-B pin-swap anomaly

The official comma hardware schematics and this exact CodeFlash can now be
combined without projecting Sienna behavior onto the Corolla.

Official harness hardware defines CAN0/CAN2 as the car/camera intercept-relay
pair and CAN1 as a separate unsplit network. The pinned field report says the
affected Toyota-B assignment puts the desired network on CAN1 instead of the
expected 0/2 relay pair; physically swapping CAN0/CAN1 corrects that harness
assignment.

On `8965H1202000` itself, however, there is no corresponding application→boot
CAN migration:

```text
application: RSCFD channel 1 only (CAN1 RX/TX EIINT 187/188)
boot Rx:     0x7A1 / 0x777, channel 1 only
boot Tx:     0x7A9, HTH 0x13, channel 1
```

The complete application RSCFD register map and `3 × 0x34` driver configuration
are byte-identical to Sienna. The foreign boot peripheral-init implementation is
also byte-identical, and its core CAN/CanIf region transfers except for three
variant-table relocation bytes.

The foreign PROGRAMMING session independently reproduces the asynchronous reset
architecture: its five session records are byte-identical, the PROGRAMMING row
is the same async kind-2 form, the lower `0x08000200/0x08000201` operation is
backed by the same zero-return stub shape, and the policy/readiness thresholds
remain `0x0180` speed and `0x0A00` supply. A final `50 02` can therefore be
overtaken by reset; a client timeout alone is not evidence of rejection.

Consequently the physical repin is not an EPS requirement for selecting a
bootloader CAN controller, CAN ID, hidden handoff SecurityAccess domain, or
alternate programming primitive. For direct diagnostics on stock wiring, Panda's
static direct-route candidate is `ELM327 param 1 + logical bus 1`, which puts
FDCAN2 on harness CAN1 rather than the OBD mux. That does **not** recreate the
CAN0/CAN2 intercept-relay topology required by normal openpilot forwarding.

The exact reason an indirect OBD path can answer ordinary UDS yet fail to
survive/observe the reset remains external to this EPS image: gateway forwarding,
response timing, ACK/bus-off behavior, or another vehicle-network wake/topology
effect. No gateway artifact or dual-segment transition capture is pinned, so the
repository deliberately does not choose among them.

Canonical routing analysis and the complete eliminated/surviving hypothesis
matrix are in [panda-toyota-routing.md](../tooling/panda-toyota-routing.md).
Checked by `tests/verify_toyota_b_programming_topology.py`.

### 7.7 Whole-image function-body transfer census: conserved platform, divergent application domains

The earlier foreign-image work deliberately answered a few high-value transfer
questions. It did not answer the broader question: **how much of the already
mapped `8965B4512000` program is actually present in this image, and where are
the differences concentrated?** A new raw-byte census now uses the canonical
Sienna Ghidra inventory only to define 6,375 CodeFlash function bodies, then
searches the H image for exact complete-body transfers. Non-contiguous bodies
must reproduce every range under the same relocation. No software-ID offset map
or inherited H annotations are used.

The raw machine-readable result is
`data/generated/corolla_8965H1202000_function_body_transfer.json`, generated by
`tools/compare_variant_function_bodies.py` and regenerated byte-for-byte by
`tests/verify_albinoelephant_corolla_codeflash.py`. The target-native structural
pass is tracked separately in
`data/generated/corolla_8965H1202000_structural_function_transfer.json`. For
day-to-day navigation, those two evidence layers are joined into
`data/generated/corolla_8965H1202000_named_function_transfer_ledger.json`, which
classifies all 1,113 named canonical CodeFlash functions without promoting
instruction-shape similarity to semantic identity.

Across the 6,375 canonical CodeFlash functions:

- **1,017 complete bodies (15.95%) transfer exactly**, including 288 of the
  1,113 named Sienna functions;
- the dominant exact relocation is **`-0x1C`** in the boot image: 292
  independently unique exact anchors of at least 16 bytes span
  `0x770..0x834E` → `0x754..0x8332` and account for 27,078 exact function-body
  bytes;
- large application/framework islands independently resolve at `-0x5C60`
  (191 exact anchors), `-0x5C00` (97), and `-0x4FDA` (108), with smaller
  relocation islands around them;
- functions that do not transfer exactly are retained as
  `changed-or-absent`, not silently assigned a homolog. Neighboring exact
  anchors may provide a byte-similarity **triage candidate**, but those
  candidate addresses are not semantic evidence and can be wrong when target
  function boundaries/layout change.

This makes the cross-calibration architecture much less ambiguous than a simple
"similar Denso firmware" label.

#### Bootloader: overwhelmingly byte-identical

A named 126-function boot/trust/UDS/crypto cohort has **119 exact complete-body
transfers**. The exact `-0x1C` family includes peripheral/clock/flash init,
validity checking and application handoff, CanTp/CanIf/DCM transport,
SecurityAccess, RequestDownload/TransferData/TransferExit, RoutineControl,
DiagnosticSessionControl, ECUReset, communication/DTC control, the authenticated
RAM payload path, CMAC/AES support, and `payload_build_derive_key`.

Examples now proved as complete-body transfers rather than spot similarities:

```text
8965B4512000             8965H1202000
0x00000C9A  boot_peripheral_init       -> 0x00000C7E
0x0000119E  boot_validity_check        -> 0x00001182
0x000013B0  boot_application_handoff   -> 0x00001394
0x00005D68  uds_request_download       -> 0x00005D4C
0x00006FEC  security_access_stage1     -> 0x00006FD0
0x00007068  payload_build_derive_key   -> 0x0000704C
```

The exceptions are narrow rather than architectural: the large reset-startup
body changes, several tiny duplicated ISR/finalizer bodies cannot be uniquely
assigned from bytes alone, and the later application shutdown/reset path is
near-identical rather than exact. The bootloader should therefore be treated as
a strongly conserved platform layer with a small front-end/layout delta, not as
an independently implemented boot stack.

#### Application diagnostics and infrastructure: mixed, but recognizable islands

The application does not share one global relocation. Instead, generated
subsystems form relocation islands. Session/programming/WDBI machinery around
`-0x5C00` contains multiple exact handlers; the final PROGRAMMING handoff body is
99% byte-equal at the bracketed relocation. DTC and proprietary AB/BA handlers
also retain exact callback bodies. The later UDS dispatcher family around
`-0x4FDA` preserves exact session callbacks, RDBI/RMBA callbacks, SecurityAccess
subfunction stubs, communication-control subfunctions, RoutineControl dispatch,
and proprietary-AB subfunctions while several larger request workers differ in
embedded references/configuration.

This is the expected signature of shared generated middleware around changed
configuration and application glue: exact callback/dispatcher islands separated
by bodies whose constants, tables, or call targets changed.

#### ICU-S / SecOC: same engine and verify algorithm, different generated profile/configuration data

The raw-body census initially makes this area look more divergent than it really
is because generated RAM/table references changed throughout the application.
Low-level ICU-S hardware primitives are byte-identical at `-0x5C00`
(`icus_hardware_initialize`, register self-test, 128-bit read/write,
abort/recovery, and key-update operation helpers). A second, address-independent
Ghidra pass compares each complete mnemonic + instruction-length sequence and
requires that the shape be unique on both images before calling it a structural
homolog candidate. Target-native decompilation then confirms the important
SecOC matches rather than transferring their Sienna operands.

That closes the receive architecture much more strongly:

```text
8965B4512000                           8965H1202000
0x8DB22 secoc_build_authenticated_input -> 0x87FC2
0x8DF0E secoc_crypto_config_get          -> 0x884AA
0x8E024 secoc_rx_record_lookup           -> 0x885C0
0x8E0BE secoc_rx_queue_secured_pdu       -> 0x8865A
0x8E1A8 secoc_rx_split_freshness_and_tag -> 0x88744
0x8E3EA secoc_submit_cmac_verify          -> 0x88986
0x8E4BA secoc_rx_verify_worker            -> 0x88A56
```

The H verify worker is the same 132-instruction control shape as Sienna's and
still uses 0x50-byte profile records. H `0x88744` splits transmitted freshness
and tag according to profile fields; H `0x87FC2` builds
DataID||payload||freshness; H `0x88986` performs begin/update/finish through the
CryptoIf path and stores the result at `GP-0x63B0`; H `0x88A56` drives the same
freshness-return cases and submits the CMAC verify. The previously recovered
Gate-2 worker at H `0x88C16` consumes that result. The ICU-S command-7 backend
itself is also a unique full instruction-shape homolog at H `0x83BF4` and still
programs command 7.

So the important difference is **configuration, not the verification
algorithm**. H's SecOC table base is `TP+0x19C2`; its queue resolver finds exactly
three queue-1 profiles (`00F/D7/B6`) and no `2E4/131` steering profiles. That
profile-set difference is therefore a real target property layered onto a
shared SecOC/ICU-S implementation. Reusing Sienna profile IDs, queue indices,
RAM offsets, or steering assumptions remains invalid even though the underlying
verification state machine transfers structurally.

#### XCP-shaped command and 0x7F7/0x7F8 transport survive in a different descriptor encoding

The seven-record custom command table is present at H `0x2AE38` with the same
selectors `FB/FA/F5/F3/EB/EA/E4` and callbacks
`0x922CA/0x9232A/0x92462/0x92576/0x9261E/0x92698/0x92724`. Three of those
handlers (`FB`, `F3`, `E4`) are exact complete-body transfers; the other four
are 94–98% byte-equal at the same `-0x4FD0` island.

An initial plain-u32 scan appeared to show that Sienna's `0x7F7/0x7F8` route was
absent. Deeper table tracing disproves that provisional interpretation. H stores
the two special route IDs in a packed standard-ID descriptor representation:

```text
response @ 0x21EF4: 0x9FE00002 = 0x80000000 | (0x7F8 << 18) | 2
request  @ 0x21EFC: 0x9FDC0002 = 0x80000000 | (0x7F7 << 18) | 2
```

The response descriptor is referenced from H `0x21954`. The request descriptor
is referenced from the special receive-class record at H `0x21A50`, whose next
word points to callback `0x7C43E`; that callback is 41/42 bytes identical to the
Sienna `0x82042` callback. The request descriptor also retains DLC 8. The
structural scanner now reports both plain and packed standard-ID forms so this
encoding difference cannot produce the same false negative again.

The generic XCP-shaped configuration transfers even more strongly:

- its 41-byte opcode map is byte-identical at H `0x22A48` versus Sienna
  `0x22C04`;
- GET_SEED `0xF8` and UNLOCK `0xF7` remain unconfigured (`0` map entries);
- all 18 registered callback pointers relocate by one exact `-0x5C04` delta;
- the duplicate full-LocalRAM bounds remain `FEBE0000..FEBFFFFF`;
- the exclusion count remains five and the write-shadow bounds remain
  `FEBF7C00..FEBFFBFF` (32 KiB);
- the five H read exclusions are
  `FEBE0000..FEBE37FF`, `FEBE4F28..FEBE5193`,
  `FEBF0150..FEBF128F`, `FEBF4958..FEBF4B33`, and
  `FEBF6000..FEBF6CDF`.

Thus **the physical 0x7F7/0x7F8 ingress and the unauthenticated command-map
shape both survive** on H; what changed is the descriptor encoding and several
RAM exclusion boundaries. Target-native decompilation now closes the generic
memory-command semantics too:

- H `0x7BF72` (`SET_MTA`) stores the supplied address;
- H `0x7BE2A` (`SHORT_UPLOAD`) bounds the requested span to LocalRAM,
  rejects overlap with the five H read-exclusion ranges via H `0x92202`, then
  copies bytes directly from the selected MTA;
- H `0x7B30E` (`DOWNLOAD`) validates the MTA/span against full LocalRAM plus the
  write-shadow validator H `0x9223C`, stores the request bytes directly, and
  advances MTA;
- H `0x7B3D4` (`MODIFY_BITS`) performs the same shadow-validated read/modify/write
  on the byte at MTA;
- the exact custom `E4` handler H `0x92724` calls exact H `0x92700`, which copies
  CodeFlash `0x10000..0x17DEF` into the 32-KiB shadow beginning at
  `FEBF7C00`;
- the opcode map still has no GET_SEED (`F8`) or UNLOCK (`F7`) callback, so this
  memory-command path has no XCP challenge/response gate to transfer.

The H custom dispatcher at `0x92190` checks its connection/channel state and
scans the seven-entry selector table before invoking the callback; the read and
write validators above use the H-specific configuration rather than inherited
Sienna addresses. The static conclusion can therefore be upgraded from
"XCP-shaped code survives" to **the same unauthenticated LocalRAM read and
shadow-write architecture, with the same low-CodeFlash-to-shadow E4 primitive,
exists in this exact H image**. The five read exclusions are target-specific and
must remain H-specific in any tooling or exploitability analysis.

#### NvM: storage framework transfers more strongly than provisioning semantics

The function census agrees with the independent DataFlash geometry result.
Queue/read/write/synchronous NvM helpers transfer exactly in the `-0x5C60`
island, while checkpoint/triplicate persistence workers around `-0x5CC8` are
generally about 88–94% byte-equal. That combination explains why the physical
record geometry transfers while specific H owners/provisioning differ from the
Sienna descriptor map.

#### Steering/motor-control: shared control architecture, different orchestration/data layout

This remains the clearest counterexample to **byte-offset** transfer, but the
follow-up target-native work changes the semantic conclusion substantially.
Among the named Sienna steering/motor-control cohort, zero complete bodies are
byte-identical in H. That is because operands, RAM layout, calibration addresses,
and several orchestration functions changed—not because the entire control
architecture was replaced.

An address-independent structural pass exports every Ghidra function as its
complete mnemonic + instruction-length sequence, ignores operands, and accepts a
candidate only when that complete shape is unique on both images. A clean H
import yields 2,542 unique exact-shape matches overall (2,324 with at least eight
instructions). Target-native decompilation was then used to validate the
high-value control candidates rather than inheriting Sienna operands or names.
The following core stages survive with unique complete instruction shape:

```text
8965B4512000                                      8965H1202000
0x35960 dual_motor_clarke_park_feedback          -> 0x314FE
0x36742 dual_motor_rotating_frame_command_limit  -> 0x32314
0x36902 dq_current_pi_axis_a                     -> 0x324D4
0x37644 dual_motor_dq_feedback_combine           -> 0x33160
0x37712 dual_motor_dq_current_reference          -> 0x3322E
0x3875A dual_motor_phase_duty_publish            -> 0x33F66
0x47C3C dual_motor_phase_current_conditioning    -> 0x43528
0x4FB02 dual_motor_phase_sample_publish          -> 0x4B1B6
0x569A8 dual_motor_phase_duty_select             -> 0x52012
0x60BFA tsg3_phase_compare_compute               -> 0x5B7CC
0x60DDC tsg3_pwm_compare_commit                  -> 0x5B9AE
0xBC766 fd090_steering_angle_speed_plausibility  -> 0xBB50C
0xC07FA steering_command_plausibility_monitor    -> 0xBF1F0
0xC853A steering_torque_command_clamp_gain       -> 0xC91B6
0xC85B6 steering_torque_command_rate_limit       -> 0xC9232
0xCAC6A steering_command_secondary_gain_clip     -> 0xCD440
```

The H motor scheduler is target-natively recoverable as well. The unique
146-byte scheduler homolog `S 0x5784C -> H 0x52DBA` dispatches H phase-sampling
and motor-control workers. H `0x58226` then calls the recovered d/q feedback,
reference, PI, rotating-frame limit, inverse-transform, phase-duty publish and
phase-duty select chain. H `0x5FA96` calls H `0x5B9AE` in the TSG3 commit path
before returning through the same scheduler family. H `0x5B9AE` writes the TSG3
hardware compare registers from H-local state, so the recovered chain reaches
the physical PWM boundary rather than ending at a mathematical look-alike.

The high-level steering pipeline is **not** an exact structural transplant. The
Sienna 12-byte wrapper `0xCBA72` maps cleanly to H `0xCF028`, but H's wrapper
calls a real 534-byte pipeline at `0xCEDAE`; Sienna's corresponding pipeline at
`0xCB86E` is only 424 bytes. H's pipeline has a larger/reordered stage set, while
still directly calling H `0xC91B6` and `0xC9232` for the recovered steering
clamp/gain and rate-limit stages. This gives a target-native anchor for the
steering command-control chain while proving that its orchestration changed.

This work also supplies a useful negative-control example. The raw neighboring-
anchor heuristic proposed H `0xCEE24` as a possible relocation of Sienna
`0xCB86E`; target-native disassembly rejects `0xCEE24` as a valid function. The
real pipeline is `0xCEDAE`. That is why the generated byte-similarity candidates
remain explicitly non-semantic.

Operand-level differences still matter even when instruction shape is identical.
For example, the H steering clamp/gain homolog indexes its mode table with
`mode & 3`, whereas the Sienna body uses `mode & 0xF`; both also use different
calibration/data addresses. The correct cross-variant classification is
therefore **shared motor-control algorithms and hardware actuation architecture,
with target-specific RAM/calibration layout and a materially changed high-level
steering pipeline**. Reusing Sienna addresses or assuming one application-wide
relocation remains unsound, but redoing the mathematical control analysis from
scratch would now also be wasteful.

Overall, the new image is best classified as **the same boot/security platform
and much of the same generated middleware/control architecture, with substantial
target-specific configuration, RAM/calibration layout, and high-level steering
orchestration differences**. The exact-body and structural-transfer passes now
tell us both where direct reuse is safe and where operand/control-flow validation
is mandatory.

### 7.8 Boot memory-safety transfer is stronger than family resemblance

The whole-image census closes an important security-transfer question. The H
bootloader preserves not only the same RAM window and routine names observed in
the acquisition workflow, but the **critical implementation bodies and policy
tables** behind Sienna MEM-SAFE-001/002/003.

Raw CodeFlash proves:

- the three-row boot access policy at Sienna `0x8DA0` is byte-identical at H
  `0x8D80`, including the class-1 `FEBF0000..FEBF0FFF` RAM window;
- the five-entry `10F0/10F1/10F2/10F3/FF00` RoutineControl table at Sienna
  `0x8F44` is byte-identical at H `0x8F24`;
- the three boot region descriptors preserve all start/end/fixup/marker/class
  geometry at H `0x8DE0`; only their pointers to the relocated CRC descriptors
  move by `-0x20`;
- the TransferData partial-block gate (`B 0x4B7C → H 0x4B60`), RoutineControl
  dispatcher (`0x567E→0x5662`), `10F0` CRC/CMAC authorization worker
  (`0x5936→0x591A`), decrypt/transfer worker (`0x6BDE→0x6BC2`), CMAC endpoint
  setup/step (`0x7122→0x7106`, `0x7170→0x7154`), and `10F3` byte-compare worker
  (`0x6C8E→0x6C72`) all transfer as exact complete function bodies.

Those are the exact code and configuration elements on which the Sienna
MEM-SAFE-001 missing AES-block-alignment write primitive, MEM-SAFE-002 malformed
CMAC-range read, and MEM-SAFE-003 CodeFlash equality oracle depend. For this
tracked H image, those three findings therefore **transfer statically**, rather
than remaining family hypotheses.

MEM-SAFE-004 initially failed the stricter raw-byte transfer test, but the
follow-up structural + target-native pass closes it as well. Sienna command-8
prepare/copy-result/driver-dispatch map uniquely by complete instruction shape to
H `0x81262`, `0x812E8`, and `0x82D36`. H `0x812E8` preserves the exact semantic
defect: successful completion copies 32+16 bytes and stores returned length
`0x30`; nonzero completion instead calls H zero helper `0x83444` with the saved
caller output pointer and the caller's **original** length. H `0x62574`, the
configured key-update submit worker, initializes that capacity to exactly
`0x30` before its call to H `0x82D36`; Ghidra's incoming-reference census finds
`0x62574` as the sole direct caller of that driver dispatcher. Thus the defect
transfers as the same **latent** primitive and remains bounded by the configured
48-byte caller in this image, matching the Sienna disposition rather than
becoming a remotely controllable write primitive.

The important methodological point is that failure of exact raw-body transfer
was not evidence of a fix: every instruction role survived while GP-relative
state addresses and call displacements changed. This is exactly the class of
variant question for which structural matching must be followed by target-native
operand/dataflow inspection.

### 7.9 Target-native GP/TP context and generated COM topology

The foreign-project bootstrap exposed one analysis trap that matters beyond this
one image. `ApplyP1MDeviceProfile.java` carries the canonical Sienna GP/TP values,
which are valid for the canonical project but must **not** be assumed for a
foreign calibration. H's own startup/context-init instructions recover the exact
runtime values:

```text
                         8965B4512000       8965H1202000
boot GP                  FEBF9800           FEBF9800
boot TP                  0000869C           0000867C
application GP           FEBEB800           FEBEB800
application TP           00023EE4           00023D6C
```

H loads the application pair literally at `0x6A8DC/0x6A8E2` and repeats it at
`0x6AD94/0x6AD9A`; the boot pair appears at `0x9F4A/0x9F50`. Foreign-image imports
now run `ApplyRecoveredGpTpContext.java` before semantic analysis. It recovers the
target pair only from the repeated startup idiom `mov immediate,gp` followed by
`mov immediate,tp`, rather than from the most common write to `tp` (RH850 uses
that register as ordinary scratch state elsewhere). It independently recovers
Sienna `FEBF9800/869C` + `FEBEB800/23EE4` and H
`FEBF9800/867C` + `FEBEB800/23D6C`. `ApplyVariantGpTpContext.java` remains the
explicit exact-image override for review/debugging, but target values no longer
need to be inherited or entered manually in the normal disposable workflow.

This correction is important but also reassuring: **application GP is unchanged**.
The GP-relative H RAM/dataflow conclusions above remain valid. The application
TP moves by `-0x178`, so every TP-relative generated table had to be re-resolved.
With H TP `0x23D6C`, the generated COM layout becomes internally exact:

- signal-property table: H `0x222E8`;
- signal→PDU map: H `0x223FC`;
- PDU table: H `0x22620`;
- the signal→PDU map therefore contains exactly **274 signal IDs (`0..273`)** and
  ends exactly at the PDU table;
- the PDU table contains **45 entries: 5 Tx + 40 Rx**.

That is a substantial generated-configuration change from Sienna rather than a
simple relocation.

#### Receive configuration: 47 → 40, with the classic steering routes removed

`data/generated/corolla_8965H1202000_application_rx_diff.json` is generated from
raw CodeFlash by `tools/compare_variant_application_rx.py`. It locates the normal
8-byte `software_id,length` descriptor run independently in each image.

Sienna has 47 normal Rx descriptors at `0x22018`; H has 40 at `0x21F94`. **39 are
shared.** Of those 39 shared PDUs, 28 retain the same configured signal count
and 11 change it, so even a retained CAN ID is not sufficient evidence that its
generated signal layout is identical. H removes exactly:

```text
2E4  191  131  2FD  132  423  020(FD)  1DA(FD)
```

and adds one 32-byte CAN-FD descriptor:

```text
0B6(FD)
```

This closes an ambiguity left by the SecOC-only comparison. `2E4/131` are absent
not merely from H's Gate-2 queue; they are absent from the normal application Rx
descriptor set itself. Conversely, `0B6` is a real configured application PDU,
not only a SecOC profile. The corrected signal→PDU map assigns H PDU 42 (`0B6`)
a contiguous 16-signal block `252..267`. H `0x46A10` is its generated unpacker;
it calls the COM receive primitive for the configured scalar fields and writes
H-local raw state. H `0x5262C` stages those fields into the per-cycle application
snapshot, and the H telemetry copier at `0xB8EEC` propagates several of them into
control/status state consumed later by the `0xCEDAE` steering pipeline. For
example the B6-derived snapshot at `GP-0xA47` is read by H `0xC7C70`, and that
worker is called directly inside `0xCEDAE`.

This proves **B6 participates in the H control/status path**. Its generated COM
buffer begins at PDU offset `0x1A7`; the scalar unpacker reads the active field
cluster from bytes `+3..+10`: a 6-bit field, one signed 16-bit field, several
1/2/3/6/8-bit status fields, and a final 3-bit field. The configured signal block
is larger (`252..267`) than the scalar calls (`254..265`), just as the D7 wrapper
has configured metadata/group signals that are not individual scalar extracts.
Accordingly the repo does not invent meanings for `252/253/266/267` or promote
numeric signal-ID similarity across calibrations. It also does not yet prove that
any particular B6 field is the external steering-torque command; that semantic
assignment still requires signal-level provenance.

The old Sienna `2E4` request path can nevertheless be bounded more strongly. H
retains the same GP address for the old request staging cell:

```text
GP + 0x382A = FEBEF02A
GP - 0x0B01 = FEBEACFF
```

but target-native H `0x5262C` writes zero to `GP+0x382A` every periodic staging
cycle, and H initialization also zeroes it. H `0xB8EEC` still copies
`GP+0x382A -> GP-0x0B01`. Across the recovered H decompiler corpus there is no
other direct GP-relative writer to `GP+0x382A`. Thus the Sienna
`2E4 STEER_REQUEST -> FEBEF02A -> FEBEACFF` ingress **does not transfer**; the
surviving downstream slot is a defaulted compatibility/state cell, not evidence
that the removed `2E4` route still exists. An indirect pointer write would have
to be proved separately before overriding that bounded conclusion.

The old torque-shaped staging also changes, but the deeper target-native pass
corrects its role. Instead of Sienna's raw `2E4` torque cell feeding `FEBEF184`,
H `0x5262C` writes `GP+0x3956` from H-internal state `GP-0x4A86`, and `0xB8EEC`
snapshots that value to `FEBEAE20`. H `0xC80C4` consumes `FEBEAE20` only in a
threshold/plausibility predicate. The retained Sienna-shaped clamp/gain worker
`0xC91B6` reads **`FEBEAE12` instead**, so `FEBEAE20` must not be described as
H's active clamp/torque-command input. Section 7.11 pins the separate `AE12`
source and the stronger FD-field census.

#### Transmit configuration: 260/262 collapse into a new 32-byte FD 030 PDU

The Tx side changes just as clearly. Sienna has six application Tx I-PDUs;
H has five. The H CanIf descriptor run at `0x21F04` is:

```text
0: 030  CAN-FD
1: 351  classic
2: 394  classic
3: 4A3  classic
4: 4C8  classic
```

The classic Sienna `260` and `262` transmit routes disappear. H introduces a
32-byte CAN-FD `030` PDU with cycle count 2; `351/394/4A3/4C8` retain their
4/3/8/8-byte sizes and 200/60/100/196 cycle counts. The corrected signal map
allocates the first **55 Tx signal IDs** as `37/2/4/8/4` across those five PDUs.
For comparison, Sienna has 58 Tx signal IDs allocated `10/28/2/6/8/4` across
`260/262/351/394/4A3/4C8`. Thus the new FD `030` carries 37 configured signals
where legacy `260+262` carried 38 total; `351` retains two signals, `394` drops
from six to four, and `4A3/4C8` retain eight/four. The total COM configuration
shrinks from **300 signals on Sienna to 274 on H**.

H `0x4766A` is the generated `030` packer. It packs the new PDU from a broad set
of H-local steering/status snapshot cells, computes/inserts its generated byte,
and triggers PDU 0. H `0x4749A/0x475D0/0x47ADA/0x47BA2` are the four remaining
Tx packers. The new 37-signal FD PDU occupies the same generated-signal ID region
that Sienna split across its first two `260/262` PDUs, which is strong evidence
of a generation-level consolidation/replacement. The bit widths and H-local
sources changed, so the repo does **not** claim a field-for-field `260+262=030`
wire equivalence without a signal specification or matched capture.

The practical variant rule is now explicit: **do not transfer Sienna COM signal
IDs, TP-relative table addresses, `2E4/131` steering ingress, or `260/262` Tx
assumptions into H.** Reuse the common COM implementation, but resolve the
foreign GP/TP context and generated descriptor/signal maps from that image.


### 7.10 Application diagnostics: same outer stack, different generated DID/RID behavior

The application diagnostic stack also transfers at the framework level but not
at the generated-content level. A deterministic raw-table comparison plus a
compact target-native decompiler evidence set now covers the complete primary
service table, all readable-DID producers, and all RoutineControl callbacks:

```text
                                      8965B4512000   8965H1202000
primary 17-SID service table          0x25E28        0x25B38
readable-DID table                    0x2941C        0x28F34
readable DID rows                     242            226
unique nonzero read producers         —              180
RoutineControl RID table              0x26AEC        0x267FC
RoutineControl callback table         0x25804        0x255C0
```

The outer 17-service sequence is unchanged (`10/11/14/19/22/23/27/28/2E/31/
34/36/37/3E/85/AB/BA`). The presence/absence of direct callbacks and subfunction
tables, session/security counts, and subfunction counts are identical after
relocation; all 17 outer service objects still have configured security count
zero. This is a framework/configuration transfer, not proof that every callback
behind those objects has the same semantics.

#### RDBI generation: 242 → 226, and the stale-response set changes identity

H removes exactly the contiguous 16-DID block `1CF4..1D03` and adds no readable
DIDs. The only declared-width change among the 226 shared rows is `F181`, which
expands from 17 to **33 bytes**. H-native `0x4A328` writes count byte `02`, then
two 16-byte software-ID records from CodeFlash `0x20860` and `0x17DC0`; on its
fallback path it fills both records with `0x21`. Thus the two live H identity
records are part of the application diagnostic implementation itself, rather
than merely strings observed elsewhere in CodeFlash.

The Sienna stale-response result does **not** transfer as a selector list. Every
one of H's 180 unique nonzero readable-DID producers has now been classified by
its target-native output behavior. The audit accepts only fixed-offset stores,
the recovered 2-/4-byte endian helpers, declared-length-bounded bitmap/record
engines, explicitly bounded fixed loops, and F186's one-byte session delegate.
The result is:

```text
Sienna stale-response DIDs                 48
H stale-response DIDs                      32
shared stale selectors                     19
Sienna stale selectors fixed/removed on H  29
new H stale selectors                      13
H non-stub underwriters                     0
H producer overruns                         0
```

Every H underwriter is the **same exact four-byte return-success body**
`00 52 7F 00`; no non-stub producer underwrites. H's exact stale set is:

```text
0111
1066 106A
10C7 10C8 10C9
10F7 10F8 10F9
1121 1122 1123 112A 112B 112C 112E 1132 1133
11BC 11C8
1C81 1C99 1C9A 1C9B 1C9C 1C9D 1C9E 1C9F 1CA0 1CAC
2013 2014
```

This is a useful generation-level warning: even a vulnerability class that
survives across both images must be re-censused from the foreign producer table.
H fixes/replaces several old Sienna stale producers (`1124..1129`, `112F`,
`1130/1131`, `1F03/1F04`, `2030..2032`) while introducing different no-op
producers such as `1121..1123`, `112A..112E`, `1132/1133`, `1C81/1CAC`, and
`2013/2014`.

#### RoutineControl: identical policy geometry, materially different actions

All 19 Sienna RIDs remain configured in H, in the same order. Decoding the
foreign policy-index/count/pointer tables and all control-type descriptor tables
shows **identical enable state, policy index, security count, session lists,
control-type 1/2/3 support, and input/output widths for every RID**. The callback
implementations are nevertheless not interchangeable.

The largest H-specific changes are:

- `1009`: H directly starts its lifecycle worker and latches result state; the
  Sienna feature/aggregate conditional start and request-results clear behavior
  do not transfer.
- `1106`: H keeps the speed gate and reaches the structurally matched
  multigroup lifecycle-reset family (`H 0xB3C04` is the unique complete
  instruction-shape homolog of Sienna `0xB3974`), but the H action no longer
  conditions start/clear on Sienna's aggregate-health cell.
- `110A`, `110C`, and `110D`: both the H precondition and action callbacks are
  exact four-byte success stubs. Sienna's service-mode actions behind those
  three RIDs therefore **do not transfer** even though their generated policy
  rows still advertise the same control types and widths.
- `110B`: the reverse change. Sienna's callbacks are no-ops, while H makes this
  RID active and speed-gated. H action `0x4AE92` calls `0xFE18C -> 0xB5D92`,
  setting state `FEBEB32C=0x11`. Periodic H worker `0xB5D2C` advances
  `0x11 -> 0x22`, polls operation `0x1C`, publishes completion through the
  generated selector/status dispatcher, and terminates at `0x44` on success or
  `0x88` on abnormal completion. No exact whole-instruction-shape counterpart
  exists in Sienna, so the OEM physical meaning of this H-only lifecycle is left
  unnamed pending a stronger external correlation.

The machine-readable sources are
`data/generated/corolla_8965H1202000_application_diagnostics_diff.json` and
`data/generated/corolla_8965H1202000_application_diagnostic_decompiler_evidence.json`.
The latter is deliberately compact: it stores only the 180 RDBI producers, 35
nonzero RoutineControl callbacks, and the 25 helper/downstream functions needed
for the bounds and lifecycle claims, with each function tied to the exact H raw
body SHA-256. `tests/verify_corolla_8965H1202000_application_diagnostics.py`
regenerates the comparison and pins the evidence boundary.


### 7.11 FD control interface: B6 is supervisory, 025 is shared, and the retained torque branch is zero-fed

A full target-native field/consumer pass now closes the obvious "the command
must have moved to one of the new FD frames" hypothesis much more strongly.
The normal application FD-Rx sets are:

```text
8965B4512000:  025  090  0D7
8965H1202000:  025  090  0D7  0B6
```

Thus **`0x0B6` is the only H-only FD receive descriptor**. `0x025` is not a new
H command transport: Sienna already has the same 32-byte FD PDU. Three complete
instruction-shape joins are unique on both images:

```text
S 0x4AD82  025 generated unpacker      -> H 0x4636A
S 0x4B7BA  025-to-4A3 producer         -> H 0x46D9A
S 0x4BB1E  CAN 0x4A3 packer            -> H 0x4749A
```

The operand-level H check agrees with that architectural transfer. H `0x4636A`
extracts signed-12 signal 184 to `FEBE7D34`; H `0x46D9A` splits that value into
its high nibble/low byte, and H `0x4749A` emits those bytes directly as CAN
`0x4A3` B1/B2. This is the same pre-existing `025 -> 4A3` telemetry/state join
that Sienna implements with signal 221. It therefore cannot by itself explain
the disappearance of the Sienna-only `2E4/131` command modes.

#### B6 scalar map and downstream use

H PDU 42 (`0x0B6`) has COM-buffer base `0x1A7`, configured signal IDs
`252..267`, and exactly twelve scalar extracts (`254..265`). The target-native
map is:

| signal | wire field | signed | staged / snapshot | recovered role |
|---:|---|:---:|---|---|
| 254 | B3[5:0] | no | `FEBEF127` / none | staged only; no direct runtime consumer |
| 255 | B4..B5 | **yes, 16b** | `FEBEF1CC` / none | staged only; no direct runtime consumer |
| 256 | B6[7] | no | `FEBEF147` / `FEBEADDD` | snapshot only; no direct runtime consumer |
| 257 | B6[6:4] | no | `FEBEF128` / `FEBEADB1` | snapshot only; no direct runtime consumer |
| 258 | B6[2] | no | `FEBEF129` / `FEBEADBB` | steering-cone gate (`CBEEE`) |
| 259 | B6[1:0] | no | `FEBEF12A` / none | staged only; no direct runtime consumer |
| 260 | B7[7:6] | no | `FEBEF12B` / `FEBEADC2` | mode/table selector (`C89D2/C8D42`) |
| 261 | B7[5:0] | no | `FEBEF12C` / `FEBEADBC` | modulo/sequence delta (`CB246`) |
| 262 | B8 | no | `FEBEF12D` / `FEBEADBD` | percentage/scaling input (`CC442`) |
| 263 | B9 | no | `FEBEF12E` / `FEBEADBE` | percentage/scaling input (`CBFCE`) |
| 264 | B10[7] | no | `FEBEF12F` / `FEBEADC1` | validity/reset gate (`C819E`) |
| 265 | B10[2:0] | no | `FEBEF141` / `FEBEADD9` | validity-gated mode/status (`CCF58`) |

The queue/update validity state is separately staged to `FEBEF132` and reaches
`FEBEADB9`; it gates `C7C70`, `C819E`, `CC7F8`, and `CCF58`. The active
B6 consumers above have target-native call paths inside the `0xCEDAE` supervisor
cone. In contrast, the **only signed 16-bit B6 scalar is signal 255, and its
staging cell has no direct runtime consumer in the complete H decompiler
reference census**. Signals 254/259 likewise stop at staging; 256/257 stop at
the copied snapshot. These are bounded direct-reference negatives: a future
computed-pointer/alias proof could override them, but there is no static basis
to rename signal 255 as a relocated `2E4 STEER_TORQUE_CMD`.

The positive B6 result is therefore narrower and more useful: `0x0B6` is a
**secured supervisory/control-status interface** supplying gates, mode/table
selection, a sequence-like delta, percentage/scaling inputs, and validity state.
It is not statically demonstrated to carry the removed Sienna torque/angle
command payloads.

#### The retained Sienna-shaped torque branch is dormant on H

Following the actual H operands corrects a second tempting cross-variant
mistake. H `0xC91B6`, the unique instruction-shape homolog of Sienna's
clamp/gain worker, reads `FEBEAE12`, not `FEBEAE20`. `FEBEAE12` is produced by
`0xB8EEC` through scale helper `0xCF12A` from staging word `FEBEF166`. The
complete H direct-writer census finds only two writes to that staging word:

```text
0x5262C: FEBEF166 = 0
0x5389C: GP+0x3966 / FEBEF166 = 0
```

For the fixed `0x100/100` call, `0xCF12A` preserves zero input as zero output.
Consequently the retained clamp/gain branch is **zero-fed in this calibration**
under the recovered direct-writer evidence. The old Sienna-shaped `FEBEAE20`
path is separate: H internal controller family `0x35526/0x355CE/0x35710` produces
`FEBE6D7A`, `0x5262C` stages it at `FEBEF156`, `0xB8EEC` copies it to
`FEBEAE20`, and `0xC80C4` uses it in a plausibility/status predicate. This is a
monitor/status branch, not the active `C91B6` clamp input.

This does **not** prove that all H steering actuation is zero or absent. It proves
that the specific Sienna external-torque branch retained in H is not supplied by
a recovered nonzero source. The ordinary EPS assist/motor-control chain and
other H supervisor states remain separate.

#### FD 030 transmit field map

The H transmit generation likewise can now be described at field level. PDU 0
is `CAN-FD 0x030`, 32 bytes, cycle/raw count 2, with configured signal IDs
`0..36`. H `0x4766A` directly packs only **signals 0..34**; configured IDs
35/36 have no recovered direct pack call and remain unassigned rather than being
given invented wire fields.

The direct packer covers bytes B0 through B22. Runtime producers are
`0x470C6`, `0x47074`, `0x46C4C`, `0x46EE0`, `0x46FD0`, and `0x4746A` plus
initial/default state. The complete source-writer census distinguishes normal
runtime-produced fields from init-only fields and from four runtime-constant-zero
bits (signals 20/21/29/30). Signal 9 at B7 is computed inside the packer itself:

```text
B7 = (B0 + B1 + ... + B6 + 0x38) & 0xFF
```

That exact additive behavior is recovered from code; the repository does not
promote the `0x38` constant into an OEM checksum name or infer protocol lineage
from the constant alone.

The configuration-level conclusion remains that FD `0x030` occupies the H Tx
slot where Sienna used classic `0x260/0x262`, but the field-level pass reinforces
why `030 == concatenate(260,262)` is wrong: H has 37 configured fields, 35 direct
packer calls, different widths/positions/sources, and several default/constant
fields. It is a generation-level consolidation/replacement, not a bytewise wire
translation.

Machine-readable evidence is in
`data/generated/corolla_8965H1202000_fd_control_interface.json`, with compact
H-native decompilation evidence in
`data/generated/corolla_8965H1202000_fd_control_decompiler_evidence.json` and
the bounded full-corpus direct-reference census in
`data/generated/corolla_8965H1202000_fd_control_reference_census.json`.
`tests/verify_corolla_8965H1202000_fd_control.py` regenerates and pins the report.


### 7.12 Steering supervisor: every direct stage is now classified

The larger H steering supervisor is now treated as a finite stage inventory rather
than as a monolithic "different pipeline." Raw/Ghidra function boundaries give
Sienna `0xCB86E` a 424-byte body and H `0xCEDAE` a **534-byte (`0x216`)** body.
Their complete direct-call denominators are 94 and 123 stages respectively.

A global order alignment uses complete per-function instruction sequences plus
body-size compatibility. It is deliberately evidence-graded: order alignment is
only navigation, while a pair is promoted when the independent whole-image
structural artifact proves a unique complete instruction-shape match. The result
is:

```text
Sienna direct stages                        94
H direct stages                            123
order-paired                                83
  unique exact instruction-shape pairs      33
  high-similarity nonexact pairs             24
  weaker order-aligned candidates            26
H order-unpaired insertions                  40
Sienna order-unpaired stages                 11
```

The 40 H insertions are all explicitly dispositioned in
`data/generated/corolla_8965H1202000_steering_supervisor_stage_ledger.json`.
They cluster into four bounded families rather than one hidden command decoder:

1. **Supervisor plausibility/mode/fault expansion.** The block around
   `0xC7BE8..0xC8B02` adds activation debounce, validity gates, history/delta and
   rate checks, mode/table selection, scaling/correction, and three explicit
   fault-monitor paths. B6-derived state enters this family through the already
   recovered gate/mode/sequence/scaling/validity fields.
2. **Dual-channel motion/plausibility estimation.** H adds a large later block
   around `0xC2296..0xC3DC6`: three motion-state estimator stages, paired
   channel-A/channel-B statistical/window classifiers, consistency/debounce,
   health arbitration, and a five-stage local wrapper. The repository gives
   these algorithmic role names only; it does not infer an OEM sensor/system
   label from the math alone.
3. **Geometry/residual estimation.** `0xC4536/0xC4696` construct paired means,
   residuals, and bounded multi-channel geometry state used by the late H
   supervisor.
4. **Calibration/status postprocessing.** `0xC9466`, `0xC5DEC`, `0xCD15A` and
   late wrappers add operating-state interpolation and status propagation;
   `0xCCF58` is the B6-validity-gated status export already mapped in §7.11.

This also sharpens what was **removed** from the Sienna generation. Eleven Sienna
stages are unpaired at their ordered positions. Several are ADF6/AE4A-indexed
command-shaping/gain stages. Most importantly,
`lta_angle_command_smoothing @ 0xC8DE0`—the recovered stage that consumes the
authenticated `0x131 STEERING_LTA_2` angle and writes the smoothed command—is
order-unpaired on H. That independent code result agrees with both H's normal-Rx
and SecOC configuration: `0x131` is absent. The classic torque clamp/rate workers
*do* survive as unique exact-shape pairs (`C853A/C85B6 -> C91B6/C9232`), but §7.11
proves their H input is zero-fed.

The combination matters more than any one address: **H retains generic steering
supervisor/control framework code while removing the two known Sienna external
command modes and inserting substantial supervisor/estimator machinery.** The
repo therefore does not invent a replacement steering-command frame merely
because the physical EPS obviously still performs normal steering assist. The
remaining question is narrower: whether any other nonzero externally sourced H
supervisor input constitutes a remotely commanded mode, or whether this
calibration's externally authenticated interfaces are supervisory/status-only.

The order-alignment boundary is explicit. A nonexact order-paired row is not
semantic transfer proof, and an order-unpaired row is not proof that no analogous
function exists elsewhere in the other image. The machine-readable ledger and
its two compact structural-evidence files retain enough information to audit all
123 H stages without reopening the disposable Ghidra project.


### 7.13 SecOC key provenance: all H profiles select one protected ICU-S slot 4

The H SecOC key question can now be separated cleanly into **profile selection**,
**CPU-visible configuration**, and **opaque ICU-S key state**. The three H
queue-1 records are `00F/D7/B6`, and target-native `secoc_rx_verify_worker @
0x88A56` reads two generated fields from each 0x50-byte record before CMAC:

```text
record + 0x16 -> SecOC crypto-config ID
record + 0x20 -> CryptoIf job handle
```

All three records contain **config ID 0 and job handle 0**. The per-profile
values elsewhere in the records are therefore not separate key handles.

H `secoc_rx_init @ 0x88024` installs config 0 from CodeFlash `0x2570C`. Its
exact 20-byte value is:

```text
01 00 00 00 | 04 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
```

The first word is generated config type 1. `secoc_crypto_config_set @ 0x88458`
validates that type and copies the following 16-byte config payload into runtime
state; the payload is **not a 16-byte AES key**: only its first byte is nonzero,
`0x04`. The object is byte-identical to the canonical Sienna slot-4 config at
`0x25950`.

The selector flow is recovered end-to-end rather than inferred from that shape:

1. `0x88A56` fetches config 0 and submits CryptoIf job 0.
2. `cryptoif_job_begin @ 0x82F6A` requires config type 1 and stores the config
   pointer at `FEBF1274`.
3. `cryptoif_job_finish @ 0x82FA8` forwards that pointer through generic driver
   dispatch `0x82956`.
4. `icus_command7_prepare @ 0x822D0` requires `*config == 1` and copies
   **config byte +4**—the `0x04` above—into ICU request descriptor word 4.
5. `icus_command7_cmac_verify @ 0x83BF4` requires descriptor word 4 `< 0x0F`
   and writes `(word4 << 16) | 7` to `ICUSCMD`.

Thus the application asks ICU-S command 7 to verify with **protected slot 4**.
No 16-byte raw key is copied into the command-7 CPU request descriptor. Because
all three H profiles use config 0 / job 0, the correct static model is **one
shared slot-4 key selection for `00F/D7/B6`**, not three independently selected
runtime keys.

The disabled H known-answer path independently corroborates the selector. H
`0x62430` invokes job 0 using another exact `{type=1, selector=4}` config at
`0x215B0`, but its fixed compile gate `CodeFlash[0x2CA9F]` is `0x00`, not
`0x5A`, so the KAT body is inactive and places no constraint on the current live
slot-4 key value.

#### Provisioning/refresh is package-authenticated, not a raw application key write

The separately recovered ICU-S command-8 path survives on H. `0x81262` requires
exactly 64 input bytes and stages them as `16 + 32 + 16`; `0x83D7A` launches
`ICUSCMD=8`; success returns 48 bytes. The CPU-side command-8 descriptor carries
pointers/lengths for that authenticated package and has **no fixed raw target-slot
selector field analogous to command 7**. In the already established SHE-style
M1/M2/M3 memory-update model, target/key identity is authenticated inside the
package rather than supplied as a plaintext application key buffer.

That provides a concrete firmware-static lifecycle model:

```text
boot / normal SecOC:
  install {type=1, slot=4} selector config
  -> verify using opaque ICU-S slot 4

provision / refresh:
  authenticated 64-byte command-8 package
  -> ICU-S protected key-update machinery
```

No mapped H SecOC initialization path loads or derives 16 raw key bytes in CPU
software before command 7.

#### DataFlash does not expose the live key as an obvious CPU-visible 16-byte value

The contributor's 32 KiB DataFlash snapshot has a committed exhaustive raw-window
scan with **23,277 tested unique 16-byte candidates and zero matches** against the
retained SecOC oracle set. That tracked artifact does not independently preserve
the richer temporary per-domain/simple-transform scan, so those stronger negatives
are not carried forward here.

That negative is useful but remains correctly bounded: CAN collection and
DataFlash dumping were separate jobs/epochs, so it excludes an exact raw candidate
in the tested snapshot, not transformed/derived values, arbitrary KDFs, or
undocumented ICU-S-internal storage. Combined with the command-7 path, however,
the strongest
static model is now straightforward: **the application selects protected ICU-S
slot 4; the raw slot-4 AES key is opaque to the mapped CPU verification path and
can be refreshed through authenticated command 8.**

Machine-readable evidence is in
`data/generated/corolla_8965H1202000_secoc_key_provenance.json` and the compact
H-native function set
`data/generated/corolla_8965H1202000_secoc_key_provenance_decompiler_evidence.json`.
`tests/verify_corolla_8965H1202000_secoc_key_provenance.py` regenerates and pins
the result.


### 7.14 External supervisor ingress: no hidden H command-sized wire field remains in the mapped COM path

The final steering-ingress pass removes one remaining loophole in the earlier
argument. It is not enough to observe that `0x0B6` is the only new CAN ID: H
could in principle have reused a Sienna CAN ID while changing one field into a
new command. The complete generated-COM provenance census therefore compares
**wire fields**, not signal numbers or names.

For every H scalar receive call, the census resolves:

```text
CAN ID + relative PDU byte + bit length + bit offset + signedness
    -> raw COM destination
    -> periodic FEBEF* staging destination
    -> FEBEAD*/FEBEAE* supervisor snapshot
    -> direct reference inside the CEDAE call cone
```

The same wire tuple is reconstructed independently from Sienna's generated COM
configuration. An H field is classified `shared_wire_field` only when the same
CAN ID carries the same relative byte/bit/signed shape on Sienna. This catches
CAN-ID reuse with changed field geometry.

Two closure conditions are then enforced by the extraction tool and regression:

1. **Every H-only or H-wire-changed scalar that reaches the mapped supervisor
   cone comes from `0x0B6`.** No changed field on a shared non-B6 CAN ID survives
   the generated raw→staging→snapshot provenance into the supervisor.
2. **No H-only/wire-changed scalar of 12 bits or wider reaches that cone.** In
   particular, B6's signed-16 signal 255 is absent from the resulting consumer
   census, agreeing with the independent §7.11 direct-xref negative.

The B6 fields that *do* survive are the already classified sub-12-bit
supervisory inputs: gate, mode/table selector, modulo/sequence delta,
percentage/scaling inputs, and validity/status. Non-B6 supervisor inputs that
survive the census are wire-shape matches to Sienna's corresponding CAN fields;
shared FD `0x025` remains a shared field source rather than an H-only transport.

This closes the static **obvious replacement-command ingress** question much
more strongly than an ID census alone. Within the mapped scalar COM path feeding
`0xCEDAE`, H has neither:

- a new/reformatted large torque/angle-like scalar on a shared CAN ID; nor
- an active large scalar on H-only `0x0B6`.

Combined with the raw removal of `2E4/131`, the order-unpaired Sienna `0x131`
angle stage, and the zero-fed retained torque clamp branch, the supported static
interpretation is that this exact H calibration **does not expose a recovered
Sienna-style external steering-command mode through its mapped application COM
supervisor ingress**. That statement is intentionally narrower than "the EPS
cannot be commanded": opaque/group signals, computed-pointer flows outside the
modeled generated-copy chain, undocumented hardware paths, or a different ECU
remain separate hypotheses. The normal local motor/assist control system is also
unaffected by this negative.

The machine-readable census is
`data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json`,
generated by `tools/extract_corolla_h_supervisor_external_ingress_census.py` from
the complete target-native H decompiler corpus. Every cited consumer and source
unpacker carries an exact raw-body SHA-256 so
`tests/verify_corolla_8965H1202000_supervisor_external_ingress.py` can bind the
tracked result back to the immutable H CodeFlash without committing the full
disposable corpus.

### 7.15 Named-function coverage denominator

The cross-variant work now has an explicit **coverage denominator** rather than
using the raw function-body diff as a proxy for semantic understanding. The
canonical Sienna project contains 1,113 semantically named CodeFlash functions.
The H coverage overlay classifies them only when tracked evidence justifies the
promotion:

```text
named canonical functions                 1113
verified exact-body transfers              288
target-native inspected unique-shape       25
target-native role-recovered                 20
complete target-surface recensuses          227
structural candidates only                  111
genuinely unresolved                        442
```

`target-native inspected unique-shape` means a unique complete-instruction-shape
H candidate is also present in one of the committed compact H-native decompiler
evidence sets. `target-native role-recovered` is separate: the H role was
independently reconstructed and raw/evidence pinned even though regenerated
function boundaries prevent exact/unique-shape transfer. `target-surface recensused`
is different: the old S function may
not have a one-to-one H homolog, but the entire foreign generated surface has
been independently enumerated—for example all H RDBI producers, all 19
RoutineControl callback rows, or every direct stage in the 94→123 steering
supervisor comparison. A raw structural candidate with no later H-native evidence
stays structural-only. Everything else remains genuinely unresolved.

This matrix is intentionally conservative. It does **not** mean every promoted
function has an OEM-level semantic name, and it does not turn domain-wide
findings into one-to-one function equivalence. Conversely, a canonical function
that disappeared because H regenerated the whole table should not remain counted
as an unexplained firmware difference merely because its exact body no longer
exists. H-native functions with no unique canonical S pair are counted separately
(353 currently have
tracked target-native evidence) rather than being forced into the 1,113-function
Sienna denominator.

The machine-readable owner is
`data/generated/corolla_8965H1202000_static_coverage_matrix.json`; it joins the
raw transfer ledger, the unique structural map, compact H-native evidence sets,
and the explicitly complete RDBI/RoutineControl/supervisor censuses.
`tests/verify_corolla_8965H1202000_static_coverage.py` pins the promotion rules.

### 7.16 System / scheduler orchestration

The largest high-level `scheduler_system` residue is now target-native rather than
address-transferred. All eight formerly genuinely-unresolved canonical roles have
concrete H implementations:

```text
Sienna 0x001F2 reset decision             -> H 0x001F2 (non-contiguous Ghidra body)
Sienna 0x58404 periodic signal task       -> H 0x5389C
Sienna 0x62758 startup coordinator        -> H 0x5CAAC
Sienna 0xB0518 mode coordinator           -> H 0xB05D0
Sienna 0xB28AC transition-phase init      -> H 0xB2692
Sienna 0xBA43A telemetry snapshot         -> H 0xB8EE4
Sienna 0xBD10E subsystem init             -> H 0xBBFE6
Sienna 0xBEC4C full per-tick dispatcher   -> H 0xBD954
```

The mode coordinator is stronger than a size/call-count analogy. Sienna and H
execute the exact same **38-event query sequence** and **24-event clear sequence**
through their relocated generated helpers, with the same `0x100..0x700` mode-band
comparisons. The high-level event-driven mode policy therefore survives the
generation change even though its state addresses and helper addresses moved.

The full per-tick dispatcher is where target-specific wiring differs. Sienna has
74 ordered guard tests and H has 64. Sequence alignment produces exactly one
contiguous deletion of ten Sienna guards after the mode-coordinator call. That
removed block contains both Sienna `param == 0x520` entry/steady-state pairs plus
additional `0x103` and `0x200..0x522` guarded work; H has **no `0x520` guard** in
this dispatcher. The deleted call region includes canonical `B763C`, already
proved on Sienna as part of the WDBI-`2013` numeric-control cone. This is consistent
with the H diagnostic-generation changes (`2013/2014` stale producers and
`110A/110C/110D` no-op control callbacks), but the other deleted helpers are not
assigned OEM semantics merely from adjacency. H still preserves the late major
order `B8EE4 telemetry snapshot -> B05D0 mode coordinator -> BBA48 input snapshot`;
the reduced/current-mode companion likewise maps `S BF17E -> H BDE28` and keeps
the same trio.

Startup and one-shot orchestration also transfer by role: H `5CAAC` is a flat
startup sequence that enables EI interrupts and tails into the foreground cyclic
loop; `FDC14 -> BBFE6` is the subsystem-init veneer and `FDD40 -> BD954` forwards
the three per-tick arguments. H `B2692` retains the 26-byte generated
four-argument transition-state initializer shape. The reset-decision continuation
at `0x1F2` is explicitly treated as a non-contiguous Ghidra body: fixed raw windows
pin the same FCU status/key-command logic, `FFC0A000/004/008/00C` marker constants,
and terminal reset loop without pretending its reported body size is contiguous.

The lower generated COM/RTE surface is intentionally not forced into a false
one-to-one transfer. H splits the old large Rx consumer across a shared fragment
`524B8` called by five generated paths (`5389C/58450/5886A/589A8/58B3C`), and its
RTE copy banks are separately wrapped around `56970/5701E/5722E`. This closes the
high-level scheduler/system roles while leaving individual changed COM helpers
available for later, hypothesis-driven audit. In the named-function matrix the
`scheduler_system` tag now has **zero genuinely-unresolved functions**, and the
global unresolved denominator falls from 462 to **454**.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_system_orchestration.json` plus the compact
image-bound decompiler evidence file;
`tests/verify_corolla_8965H1202000_system_orchestration.py` pins the eight role
mappings, event schedules, guard delta, reset windows, wrapper chains, and
regenerated COM/RTE boundary.

### 7.17 CAN / COM transport and generated receive dispatch

The remaining nine named `can_com` transfer gaps are now target-native recovered.
The two large generated receive groups retain their high-level state schedules:
Sienna group B `5D3CE` maps to H `58450` with an exact **29/29** normalized guard
sequence, while group A `5DB6E` maps to H `58BBC` at 2136→2060 bytes and 97→96
guards. After normalizing local variable and branch-label names, group A differs
by one deleted nested `if (uVar != 0)` guard; the PDU/unpacker population around
those guards is target-specific and remains owned by the exact COM-topology/FD
reports rather than inferred from function similarity.

The low-level transport roles are stronger because the generated configuration
tables point directly at them:

```text
role                         Sienna config/target       H config/target
PduR Tx confirmation         21980 -> 7E30C            2192C -> 78708
CanIf get Tx CAN ID          21EDC -> 7E5F2            21E68 -> 789EE
CanIf Tx confirmation        21ED0 -> 7F002            21E5C -> 793FE
COM RxIndication             21E28 -> 7C640            21DB4 -> 76A3C
PduR transmit router         21CE4 -> 809C6            21C70 -> 7ADC2
PduR receive router          21D04 -> 80C44            21C90 -> 7B040
```

That table join corrects an earlier triage-only navigation hit: H COM
`RxIndication` is **`0x76A3C`**, not the nearby copy fragment around `0x769E0`.
H `76A3C` preserves the complete 212-byte generated behavior: optional filter
bit `0x10`, secondary gate bit `0x08`, bounded frame copy, state-byte clear with
`& 0xDC`, and timeout refresh when flag `0x04` is set. H normal receive demux
`7A402` terminates through `7B026 -> [21C90] 7B040`; transmit adapter `7AD8E`
uses `[21C70] 7ADC2`. CanIf Tx-ID lookup `789EE` and confirmation `793FE` retain
the same six route classes (`0000/6000/0800/B800/C000/F800`). Hardware Tx
completion is joined by `7EB4E -> 7EB10`.

`com_signal_deadline_monitor_c` is a useful ambiguity case. Its 1182-byte body is
byte-identical at H `6418C`, but the same body also exists at H `CF27E`; exact
identity alone therefore cannot choose the live role. Target-native monitor
caller `3E118 -> 6418C` disambiguates the active COM deadline-monitor instance,
so the coverage promotion is use-site backed rather than duplicate-body guessed.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_can_com.json` plus compact target-native
decompiler evidence. `tests/verify_corolla_8965H1202000_can_com.py` pins all nine
role mappings, both receive-group guard schedules, the duplicate deadline-body
boundary, raw configuration-pointer joins, COM Rx behavior, and the normal
Rx/PduR/CanIf confirmation chains. The `can_com` tag now has **zero genuinely
unresolved functions**. Incorporating this evidence also promotes two structural
candidates to inspected unique-shape status.

### 7.18 Storage / NvM restore and DataFlash exclusion

The three genuinely-unresolved `storage_nvm` roles are now target-native mapped:

```text
S 4EAD8 application_dataflash_range_allowed -> H 4A534
S 65C84 secoc_nvm_restore_request            -> H 5FFBC
S 66DB2 secoc_nvm_queue_restore              -> H 610EA
```

All three H bodies retain the exact canonical sizes (68/84/150 bytes). More
important, their data/config semantics transfer directly. H `4A534` uses the
exact same two-entry protected-range table as Sienna, relocated from `293E4` to
`28EFC`:

```text
FF207800..FF207FFF
FF206C00..FF206EFF
```

The second interval contains the known related-variant object-15 key-field
geometry: raw `FF206E14`, XOR55 `FF206D14`, and XORAA `FF206C14`. Thus H preserves
the same DataFlash exclusion geometry around the entire triplicate object-15
region. This proves the range filter's protected geometry; it does not by itself
prove every caller/API path through that helper.

H `5FFBC` retains the same request namespaces: `0x000`, `0x100`, and `0x200`.
Namespace **`0x100` calls `610EA`**, which is the generic triplicate NvM restore
queue—not an ICU key-set command. H and Sienna both configure **16 restore
objects**, so object 15 remains addressable by the generic persistence machinery.
`610EA` retains queue state `0x11` and invokes the three-copy worker `69D1A`; this
is the same raw/XOR55/XORAA restore architecture already established on Sienna.

The contributor H DataFlash snapshot closes the current-state boundary. Object 15
exists at the expected roots `FF206E00/FF206D00/FF206C00`, but **all three copies
are invalid** and there is no valid consensus. This agrees with the separate SecOC
result: the mapped runtime verifier selects ICU-S slot 4 directly, while command 8
is the authenticated provisioning interface. Generic NvM restore can process
object 15, but this supplied H snapshot cannot supply a valid persisted object-15
key to explain the live slot-4 state. Runtime equivalence of related-variant
object-15 key fields and the H ICU-S slot remains explicitly unproven.

`data/generated/corolla_8965H1202000_storage_nvm.json` and its compact decompiler
evidence own this conclusion; `tests/verify_corolla_8965H1202000_storage_nvm.py`
pins the three roles, protected ranges, 16-object namespace, queue state/worker,
and object-15 validity. `storage_nvm` now has **zero genuinely-unresolved named
functions**; because two of these functions are also tagged SecOC/NvM, the
`secoc_icus` residue falls 44→42 and the global named residue falls **445→442**.
The current denominator is therefore 288 exact, 25 inspected unique-shape, 20
role-recovered, 227 surface-recensused, 111 structural-only, and 442 genuinely
unresolved canonical functions.

## 8. Remaining evidence boundary

The new corpus closes CodeFlash identity and much of the firmware-static
transfer question, but it still does **not** provide:

- a direct UDS `F181` transcript from the same acquisition;
- a stock passive `carFw` inventory joining the public route to the firmware;
- proof of where the selected slot-4 key value is physically stored or internally derived inside ICU-S;
- same-runtime-epoch proof between the CAN oracles and any DataFlash read;
- proof that this `8965H1202000` specimen is architecturally identical to
  Span's separately probed `8965F1208000` Corolla.

The firmware artifact identifies itself strongly; the vehicle/model-year link
remains contributor attribution rather than route-contained identity.

## 9. Highest-value next evidence

For this specimen, another generic CodeFlash request is no longer useful. If the
vehicle is revisited, the remaining high-value dynamic evidence is a controlled
paired capture: full-bus synchronization/protected CAN immediately before the
programming/range-dump transition, then repeat after recovery/reset and retain
the corresponding memory snapshot plus a direct `F181` response. That would
resolve runtime-key continuity without assuming it across separate jobs.

For steering-bridge portability, the higher-value next CodeFlash is instead a
foreign EPS whose Gate-2 queue actually contains classic `0x2E4/0x131` records
—for example Span's distinct `8965F1208000` if that image becomes available.
The `8965H1202000` corpus has already served its purpose as a negative-capability
regression: the resolver transfers, discovers the target's real three-profile
queue, and correctly refuses to construct a Sienna-shaped steering bridge.
