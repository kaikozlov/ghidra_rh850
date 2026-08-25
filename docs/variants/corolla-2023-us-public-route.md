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

A later retained range-dump session changes the evidentiary weight of any one
DataFlash image, but its physical boundary is no longer uncertain. The retained
CodeFlash identifies `R7F701383`; Renesas' P1M-E product table lists that exact
part as a DPS **1-MiB** device, and the hardware manual maps 1-MiB-device
DataFlash to `0xFF200000..0xFF207FFF` (32 KiB). The later
`0xFF200000..0xFF20FFFF` profile therefore consists of 32 KiB actual DataFlash
plus 32 KiB outside the specified DataFlash array. The upper half must not be
called or analyzed as physical DataFlash.

Across the five reads, the **actual first 32 KiB** differ by
**23.5077%-25.6470%** pairwise, and only 17,325 of those 32,768 positions are
identical across all five. The full 64-KiB host range differs by
26.2650%-27.7328%, but that number mixes physical DataFlash with off-array
P-Bus address space and is retained only as a transport/read-path observation.
This is read-to-read capture divergence, not a claim that one quarter of
physical DataFlash was genuinely rewritten. Three extended-CodeFlash captures
are byte-identical, while global RAM differs about 1.2% and PE1 local RAM about
2.8%-3.2%. `tests/verify_albinoelephant_corolla_repeatability.py` and
`data/p1me_product_memory.json` pin these boundaries.

That repeatability audit does **not** destroy the structural NvM conclusion below:
every one of the five DataFlash reads independently gives three valid copies for
objects 0/2/5 and zero valid copies for object 15. It does downgrade arbitrary
single-byte/null observations from any one capture. The original 32-KiB scan is
therefore retained as one exact captured image with an epoch-bound cryptographic
negative, not promoted to a byte-perfect physical-NvM reconstruction.

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
individual file hashes and acquisition notes. The 15 range files total 3,162,112
bytes; with the earlier 32-KiB DataFlash artifact, they contain exactly 3,194,640
sliding 16-byte **positions**. Calvin's pinned `dump/CLAUDE.md` records running
that corpus against two synchronization oracles — **6,389,280
window/oracle invocations, zero reported matches** — with a planted-key control
at offset `0x4000` recovered by the same path. This is scan geometry, not a claim
that exactly 6,389,280 CMAC operations occurred internally: `matcher.py` can
probe multiple sync samples and fully verify survivors.

The zero-match result remains external dynamic evidence and is cross-session:
the retained TSKM oracle (`TRIP=0xD0D`) and older public-route oracle
(`TRIP=0xCE9`) are not the Aug-14 dump runtime epoch. It therefore excludes raw
window equality only under the explicit assumption that the relevant key was
stable across those sessions. It does not exclude transformed/derived keys or
ICU-S-internal storage. In addition, half of every 64-KiB `dataflash` profile is
outside the specified `R7F701383` DataFlash array and must not be counted as
physical DataFlash coverage.

The CodeFlash range-dumper artifact is
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
`27 02` -> NRC `0x35`; second consecutive bad key -> NRC `0x36` plus a verified
**10-second** `200000000`-TAUJ1-tick RAM delay; `27 01` returns `0x37` until
expiry; initialization arms the same delay with the attempt counter cleared.
The normal application-to-PROGRAMMING replay is a separate lifecycle and
explicitly clears the initializer delay before synthetic boot `10 02`, which is
why Calvin's immediate successful field unlocks do not contradict the bad-key
backoff (CORR-088). None of this state is persistent NVM. See
[bootloader diagnostics](../diagnostics/bootloader.md) §2.1.

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


### 7.11 FD control interface: B6 carries the target-angle command, 025 is measured feedback, and the old torque branch is separate

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
| 254 | B3[5:0] | no | `FEBEF127` / `FEBEADB0` | 6-bit control/mode ID; `CBE6E` decodes values `1/4/10/11/19` into cooperative steering-mode flags |
| 255 | B4..B5 | **yes, 16b** | `FEBEF1CC` / `FEBEAE82` | **target steering-angle command**; `C9DB0/C9E54 -> CA138` target-vs-measured controller |
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
`FEBEADB9`; it gates `C7C70`, `C819E`, `CC7F8`, and `CCF58`. The earlier
**direct-reference-only** census missed two fixed-GP copies in `B8EEC`:
`GP+0x3927 -> GP-0xA50` is exactly `FEBEF127 -> FEBEADB0`, and
`GP+0x39CC -> GP-0x97E` is exactly `FEBEF1CC -> FEBEAE82` for
`GP=0xFEBEB800`. Thus signals 254 and 255 do not stop at staging.

Signal 255 is now a positive command result. `C9DB0` starts from
`signed16(FEBEAE82) * 2`, saturates it into target state, and `C9E54` applies
mode-dependent target history/rate conditioning. Independently, `CBD7E/CB096`
reconstruct the measured steering-angle domain from FD `0x025` signals
184/185/186. `CA138` votes both replicated domains, applies the **same
`0xB76/0x400` gain to target and measured angle**, and forms target-minus-measured
error before the active steering controller. This proves signal 255 is a
**target steering-angle command**, not a relocated `2E4 STEER_TORQUE_CMD`.

The physical relation is also closed. Signal184 is the signed12 coarse angle that
`42676 -> 488A8` carries unchanged into DID `0x1037 Steering Angle`; Techstream
P5 physical-data key 3 converts it as 1.5 deg/count. Signal185 is signed4;
`B24D0` recombines `15*signal184 + signal185`, and `B23A2` divides that combined
value by `3600` for a full-turn representation, proving a 0.1-deg fractional
unit. The measured controller state is
`trunc((15*coarse+fraction)*1787/512)`, while the B6 target begins at
`2*signal255`. Therefore one signal255 count is controller-equivalent to exactly
**`1024/17870 deg = 0.057302742... deg = 1.000121519... mrad`**. The literal OEM
B6 engineering-unit name is not directly recovered; nominal `1 mrad/count` is a
strong interpretation of this fixed-point result, not an imported Sienna scale.

Signal 254 is its companion 6-bit control/profile ID. Under communication/validity
gates, `CBE6E` decodes values `1`, `4`, `10`, `11`, and `19` into five mutually
exclusive cooperative-control profile flags plus a common active flag. Techstream's
exact `Target Lateral ID` pattern dictionary closes those values as **PCS, LDA,
Hands Off LTA, LTA/LCA, and PDA** respectively. Multiple later helpers select
distinct calibration banks from those profile flags. `C825A` also treats raw IDs
`25/27`, which the same OEM dictionary names **AP** and **Remote Parking**; only
`25/AP` is in the accepted steering-controller profile set.

The complete B6 result is therefore: `0x0B6` is a **secured steering-control and
supervisory interface**. It carries the recovered target-angle magnitude plus
mode/table/sequence/scaling/validity state. Techstream independently identifies
its immediate monitored sender relationship as **Brake System Control Module**;
that does not make the target-angle value a brake quantity. TMS-043 now identifies
the module-level upstream topology as `FRC_P5` 498 + category-435 `ABS_P5`/Brake-EPB
+ `EMPS_P5` 405, but the byte-level planner→B6 forwarding transform and SecOC signer
remain unresolved.

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
later fixed-map audit (§§7.14/7.35) resolves the missing replacement rather than
inventing it from stage similarity: protected B6 signal255 is the H target-angle
command and signal254 selects cooperative modes. The remaining architecture
question is therefore upstream ownership/transport and exact scaling, not whether
this EPS has any externally sourced autonomous steering command at all.

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


### 7.14 External supervisor ingress: corrected fixed-map census identifies B6 signal255

The steering-ingress census compares **wire fields**, not signal numbers or names.
For every H scalar receive call it resolves:

```text
CAN ID + relative PDU byte + bit length + bit offset + signedness
    -> raw COM destination
    -> periodic FEBEF* staging destination
    -> fixed GP-relative FEBEAD*/FEBEAE* snapshot
    -> consumer inside the CEDAE steering cone
```

The same wire tuple is reconstructed independently from Sienna's generated COM
configuration, so a reused CAN ID with changed field geometry remains visible.
The important correction is the third arrow. The first implementation searched
for named/direct snapshot assignments and therefore missed fixed-GP copies that
Ghidra renders only as `GP+offset` expressions.

With `GP=0xFEBEB800`, `B8EEC` proves two previously hidden B6 snapshots:

```text
signal254: FEBE7D96 -> FEBEF127 -> GP-0xA50 = FEBEADB0
signal255: FEBE7D94 -> FEBEF1CC -> GP-0x97E = FEBEAE82
```

The regenerated census now contains **22 distinct external scalar signals** in
the mapped supervisor cone. Its closure conditions are:

1. **Every H-only or wire-changed supervisor field still comes from `0x0B6`.**
   No changed non-B6 field survives the generated ingress path.
2. **B6 signal255 is the only H-only/wire-changed field at least 12 bits wide.**
   It is signed16 at B4:B5 and is consumed through the recovered target-angle
   path (`C86E8`, `C87FC`, `C9DB0`, `CB4F4`).
3. Signal254 is the companion 6-bit B3[5:0] mode/control field. The remaining
   changed B6 fields are sub-12-bit gate/table/sequence/scaling/validity state.
4. The only shared large fields remain FD `0x025` steering angle/rate sensor
   state; target-native arithmetic independently proves those are feedback, not
   a second command reference.

This reverses the earlier bounded negative. The mapped generated-COM path does
contain a replacement command-sized external scalar: **protected FD `0x0B6`
signal255**. The positive role is not inferred from width alone. §7.11 and §7.35
show that its `FEBEAE82` snapshot becomes target state, is compared against an
independently reconstructed `0x025` measured steering-angle domain with matched
gain, and enters the active steering controller. Thus the command search closes
positively as **target steering angle**, while the old `0x2E4` torque and `0x131`
wire formats remain absent.

The corrected boundary is now narrower and more useful. The EPS-side command
magnitude, its controller-equivalent physical scale, and its companion mode/control
ID are identified. What remains open is the literal OEM B6 engineering-unit name,
the vehicle-level left/right sign convention, exact request/validity field meanings,
and the SecOC sender freshness/key contract. The FRC/Brake/EPS module topology
is now closed by TMS-043; the still-open upstream piece is the byte-level planner→B6
transform and signing/forwarding owner. B6 nonscalar block/group/full-PDU alternatives and D7's large-field
alternative remain negative; no second command-sized path was recovered in the
audited scalar/descriptor surfaces.

The machine-readable census is
`data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json`,
generated by `tools/extract_corolla_h_supervisor_external_ingress_census.py` from
the complete target-native H decompiler corpus. Every cited consumer and source
unpacker carries an exact raw-body SHA-256, and
`tests/verify_corolla_8965H1202000_supervisor_external_ingress.py` explicitly
regresses the `FEBEF1CC -> FEBEAE82` fixed-map correction.

### 7.15 Named-function coverage denominator

The cross-variant work now has an explicit **coverage denominator** rather than
using the raw function-body diff as a proxy for semantic understanding. The
canonical Sienna project contains 1,113 semantically named CodeFlash functions.
The H coverage overlay classifies them only when tracked evidence justifies the
promotion:

```text
named canonical functions                 1113
verified exact-body transfers              288
target-native inspected unique-shape      126
target-native role-recovered                238
complete target-surface recensuses          461
structural candidates only                    0
genuinely unresolved                          0
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
supervisor comparison. A raw structural candidate with no later H-native evidence would stay
structural-only; after §7.33, none remain. There are now **zero genuinely-unresolved
canonical named functions and zero structural-only rows**. CORR-101's later
keyless re-audit promotes three former direct-call-surface rows (`0x54910`,
`0x549FA`, `0x54A7E`) to explicit H-native event-formatter roles, producing the
current 238/461 role-recovered/surface-recensused split without changing the
1,113-function denominator. The 126 inspected unique-shape rows preserve the
boundary between target-native operand/dataflow
inspection and stronger semantic role recovery.

This matrix is intentionally conservative. It does **not** mean every promoted
function has an OEM-level semantic name, and it does not turn domain-wide
findings into one-to-one function equivalence. Conversely, a canonical function
that disappeared because H regenerated the whole table should not remain counted
as an unexplained firmware difference merely because its exact body no longer
exists. H-native functions with no unique canonical S pair are counted separately
(582 currently have tracked target-native evidence) rather than being forced
into the 1,113-function Sienna denominator.

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
At this checkpoint the `secoc_icus` residue fell 44→42; §7.21 subsequently closes those remaining 42 roles.

### 7.19 XCP custom commands and H-specific read boundary

The four remaining XCP command-handler gaps are now target-native:

```text
S 972FA XCP 0xFA -> H 9232A
S 97432 XCP 0xF5 -> H 92462
S 975EE XCP 0xEB -> H 9261E
S 97668 XCP 0xEA -> H 92698
```

The generated custom-command table proves the roles independently of byte
alignment. Sienna and H have the identical selector sequence
`FB, FA, F5, F3, EB, EA, E4`; H's pointer fields resolve to
`922CA/9232A/92462/92576/9261E/92698/92724`. None of these four commands is
compiled out on H.

H `FA` retains the indexed-identifier limit `< 5` and uses the relocated
`2AE10/2AE14` metadata pair. H `F5` retains eight-byte requests with upload
length restricted to **1..7 bytes**, then calls range helper `9238A` and copy/MTA
advance helper `92436`. The outer read policy remains LocalRAM
`FEBE0000..FEBFFFFF` with five exclusion intervals, but three exclusion windows
move with H's RAM layout:

```text
FEBE0000..FEBE37FF
FEBE4F28..FEBE5193
FEBF0150..FEBF128F
FEBF4958..FEBF4B33
FEBF6000..FEBF6CDF
```

`9238A` also retains the special `length == 0x7DEC` CodeFlash rule spanning
`0x10000..0x17DEF`. Thus the application-side bounded upload/read primitive
survives on H, but Sienna's exact exclusion addresses must not be reused.
External gateway/connector reachability remains a separate topology/dynamic
question.

A security-relevant consequence is now firmware-static rather than merely
observed in the contributor RAM captures. Startup copier `0x5C9B6` copies
CodeFlash `0x20810..0x2084F` to `FEBF7B50..FEBF7B8F`, so the application
SecurityAccess root at `0x20840` is materialized at **`FEBF7B80`** on every
startup. That address is outside the H exclusion intervals above. H SID `0x23`
is likewise extended-session-only with configured SecurityAccess count zero.
Therefore either no-SA RMBA or XCP `F4` can recover the application-SA root
without first authenticating. This is a credential-disclosure result, not a
boot-SA or RAM-execution bypass; see `KEYLESS-006`.

The `EB/EA` pair likewise survives as a shared page-state writer/reader, relocated
from Sienna `FEBE5E9C/5E9D` to H **`FEBE5DB0/5DB1`**. `EB` still validates a
0/1 value and flag mask `&3`; `EA` still reads selector 1 or 2. `E4` remains in
the same custom-command table at H `92724`, preserving the surrounding page-copy
family.

Machine-readable ownership is `data/generated/corolla_8965H1202000_xcp.json`
plus its compact decompiler evidence;
`tests/verify_corolla_8965H1202000_xcp.py` pins the four roles, selector table,
H-specific F5 bounds/exclusions, page-state cells, and E4 presence. The `xcp`
tag now has **zero genuinely-unresolved named functions**.

### 7.20 Motor-control pipeline and calibration state machine

The five remaining changed `motor_control` roles are now target-native mapped:

```text
S 32B80 motor_coord_transform_calib_handler       -> H 2E780
S 36A44 dq_current_pi_axis_b                      -> H 32616
S 38464 motor0_inverse_rotating_frame_transform   -> H 33C70
S 38554 motor1_inverse_rotating_frame_transform   -> H 33D60
S 5D18C tauj0_ch0_motor_control_worker            -> H 58226
```

The coordinate-transform calibration mapping is anchored by the state machine,
not raw address proximity. Sienna `33198` and H `2EDE6` are both **1004-byte**
six-channel calibration state machines. In each, lifecycle state `0x33` invokes
the large transform/filter phase: S `32B80` (1560 B), H `2E780` (1638 B). The H
preceding phase `2E44C` publishes completion state `0x22`; `2E780` publishes
`0x44`. The transition and steady dispatchers retain both version domains
`0x512` and `0x600`: `S 5CC08/5CE0C -> H 57CEA/57EEE`, with the H branches calling
`2EDE6` in exactly those domains.

The d/q current pair also keeps its pipeline position but not identical internals.
H axis A is `324D4`, a **304-byte** unique complete-shape analogue of S `36902`;
that existing structural candidate is now independently target-native inspected.
H axis B is `32616`. The steady CH0 worker calls `32616 -> 324D4`, preserving
Sienna's **axis-B -> axis-A** order. Both H loops share the same fault/reset gate
`0x40004`, signed ±`0x7FFF` error saturation, direction gating, calibrated gain
selection, and saturated 32-bit integrator form. Their H data are separated as:

```text
axis A: reference FEBE6BBE - feedback FEBE6BB0, gains 2D5A4..2D5B0
axis B: reference FEBE6BBC - feedback FEBE6BAC, gains 2D5B4..2D5BC
```

There is a real generation change here: Sienna axis B is 404 bytes and contains
an additional cross-integrator/state-coupling path; H axis B is only **280 bytes**.
The role and outer PI behavior transfer, but Sienna's axis-B internal state
semantics must not be copied wholesale to H.

The inverse rotating-frame pair is much more literal. H `33C70/33D60` are twin
**226-byte** functions and retain the same fixed-point formula constants
`0x6EDA`, `0x6883`, divisors `0x8000/0x2000`, and `0x7FFF/0x8001` output bounds.
Their H banks are:

```text
motor 0: input 6A80/6A82, angle 7A54/7A56 -> phase 6C78/6C7A/6C7C
motor 1: input 6A84/6A86, angle 7A60/7A62 -> phase 6C80/6C82/6C84
```

Finally, the high-rate worker maps `S 5D18C (216 B) -> H 58226 (192 B)`. Their
mode wrappers are both 146 bytes (`S 5784C`, H `52DBA`), and H's wrapper invokes
transition dispatcher `57FC8` on mode changes and steady worker `58226` otherwise.
Within both transition and steady H paths the anchor order is
`PI-B -> PI-A -> inverse0 -> inverse1`; the worker retains the `>0x1FF` motor
control gate and `>0x100` phase-duty side path. H's stage list is shorter, so
unmapped intermediate calibration/state helpers remain H-specific rather than
being assigned Sienna names by sequence alone.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_motor_control.json` plus compact H-native
decompiler evidence. `tests/verify_corolla_8965H1202000_motor_control.py` pins
the five roles, 0x33 state-machine path, PI pair/order, fixed-point inverse
transforms, CH0 wrapper/worker topology, and the axis-B semantic boundary. The
`motor_control` tag now has **zero genuinely-unresolved functions**. Axis A also
moves structural-only -> inspected unique-shape, so the global denominator becomes
**384 genuinely unresolved**, 26 inspected unique-shape, 78 role-recovered, 227
surface-recensused, 110 structural-only, and 288 exact canonical functions; 374
H-native evidence functions lack a unique Sienna pair and remain separately
counted after the SecOC/ICU-S closure below.

### 7.21 SecOC / ICU-S residual surface

The remaining **42** named `secoc_icus` functions are now target-native mapped,
closing that tag's genuinely-unresolved residue completely. This pass extends the
earlier verify-worker and slot-4 findings to the whole named receive/crypto
surface instead of assuming the lower middleware transfers wholesale.

The lower ICU-S/CryptoIf block is the cleanest part of the result. Twenty-five
canonical roles map at one exact relocation island, **H = Sienna - 0x5C00**, and
every mapped H function has the same reported body size as its canonical role.
That set includes command-8 start/adapter/completion, command-5
copy/finish/interrupt/start/adapter/completion, command-7 interrupt/start/adapter/
completion, both ICU interrupt dispatchers, key-update driver lookup/completion,
CryptoIf begin/update/completion, the generate completion callback, both FIFO
steps, and the ICU command finalizer. Target-native call edges independently pin
the material adapters: H `814A8 -> 81262` (command 8), `820CC -> 81E94`
(command 5), and `824DC -> 822D0` (command 7).

The generated receive front-end is preserved but not at one global relocation.
H `secoc_rx_init @ 88024` installs the already-proven config-0/slot-4 state. The
actual H RxIndication is **`8818C`**: it checks initialized state and a non-null,
non-empty PDU, calls record lookup `885C0` with receive queue selector 0, then
queues the resolved secured PDU through `8865A`. This boundary was recovered from
the only target xrefs to those two functions; the superficially Sienna-relative
`88104` is not code and is explicitly rejected.

The freshness graph is also complete from the configured H profile callbacks:

```text
S 8E80A freshness profile lookup       -> H 89558
S 8E8E6 get Rx freshness               -> H 896B0
S 8E942 commit Rx freshness            -> H 89758
S 8EECA reconstruct normal freshness   -> H 89E9A
S 8EF9E reconstruct sync freshness     -> H 89F6E
S 8F084 commit normal freshness        -> H 8A07A
S 8F112 commit sync freshness          -> H 8A130
```

All three H receive profiles point to `896B0` for freshness retrieval and
`89758` for commit. The get callback resolves the profile and dispatches normal
versus sync reconstruction; the commit callback resolves the same profile and
dispatches normal versus sync state commit. The architecture therefore transfers,
but the H freshness state addresses and profile population remain target-specific.

Application-side ICU interrupt wrappers map independently as `S 650AC/650EE -> H
5F3EC/5F42E`, each still 66 bytes and calling H lower dispatchers `81A10/81A36`.
The five crypto-test callbacks are also recovered at their true H starts
`633A0/63542/63564/6357E/635A2`. Their disposable-project Ghidra bodies are partly
fragmented by earlier forced overlaps, so the tracked evidence intentionally pins
canonical-size raw windows plus recovered decompiler semantics instead of
pretending those reported fragment sizes are authoritative. The command-5 result
comparator still checks 16 bytes and returns `0x44` on mismatch / `0x33` on
match; the command-5 completion invokes that comparator on successful lower-layer
completion.

Finally, the protected D7 generated unpacker is **regenerated**, not a literal
Sienna signal-map transfer. H's D7 SecOC record routes to application PDU 40;
raw COM configuration assigns PDU 40 signals `240..247`, and H unpacker `468FA`
reads scalar signals `240/243/246`. Its body is 140 bytes versus Sienna's 194-byte
D7 unpacker. Thus the protected D7 role survives while Sienna's signal IDs and
individual field population do not.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_secoc_surface.json` plus the compact
42-role target-native evidence file. `tests/verify_corolla_8965H1202000_secoc_surface.py`
pins the core relocation island, Rx front-end, configured profile/freshness
callbacks, ICU ISRs, crypto-test callbacks, and regenerated D7 unpacker. With
these 42 promotions, `secoc_icus` has **zero genuinely-unresolved named
functions**, the overlapping `crypto` residue falls to **7**, and the global
1,113-function denominator becomes **384 genuinely unresolved**, 26 inspected
unique-shape, 78 role-recovered, 227 surface-recensused, 110 structural-only, and
288 exact-body transfers after the crypto closure below.

### 7.22 Remaining crypto helpers and test-bank generation

The final **seven** named `crypto` residues are now target-native mapped, closing
that tag's genuinely-unresolved count to zero. They split into three independent
classes rather than one crypto-library block.

The boot cleanup wrapper is `S 70FC payload_crypto_finalize -> H 70E0`. Its 12
bytes are exactly equal, but that body is globally non-unique, so the mapping is
not promoted from bytes alone. The surrounding clear helper independently maps
`S 70E4 -> H 70C8` (`-0x1C`), and H `70E0` directly calls `70C8`; this binds the
same TransferExit/verify-cleanup role without relying on the ambiguous body.

Both application crypto-test banks retain their activation/snapshot architecture
at one `-0x5CC8` island:

```text
S 68F0C bank0 counter snapshot -> H 63244
S 68F92 bank0 activate         -> H 632CA
S 68FC2 bank1 counter snapshot -> H 632FA
S 69018 bank1 activate         -> H 63350
```

Bank 0 still snapshots eight COM update counters before entering state `0x11`;
bank 1 still snapshots five. The generated counter indices are H-specific: Sienna
uses `12..19` / `20..24`, while H uses `10..17` / `18..22`, an exact **−2** shift
consistent with the changed preceding H Rx generation. H bank-0 activation uses
`FEBE4F82/4F83`; bank 1 uses `FEBE4F87/4F88`. The state machine roles transfer,
but Sienna's counter numbers and RAM cells do not.

The remaining lower-driver record lookups are `S 88302 -> H 82702` and `S 88508
-> H 82908`, both at the same `-0x5C00` ICU/CryptoIf relocation as §7.21. Each
still scans exactly two records with stride `0x20`; H's generated bases are
`27C88` and `27CCC`.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_crypto_residue.json` plus the compact
seven-function evidence file. `tests/verify_corolla_8965H1202000_crypto_residue.py`
pins all mappings, the boot call-chain disambiguation, counter cohorts/lifecycle,
and driver-record geometry. `crypto` now has **zero genuinely-unresolved named
functions**. After the steering closure in §7.23, the global denominator is
**375 genuinely unresolved**, 27 inspected unique-shape, 84 role-recovered, 230
surface-recensused, 109 structural-only, and 288 exact-body transfers.

### 7.23 Remaining steering roles: nested conditioning and classic-command replacement

The final nine `steering`-tagged named residues are now closed without forcing
one-to-one equivalence where H removed the classic command architecture. Six
roles have direct target-native mappings:

```text
S C8D62 lta_internal_command_rate_limit          -> H C9C16
S CA6B8 steering_command_mode_select_stage       -> H CB8BA
S CA75E steering_command_slew_gain_limit_stage   -> H CB9B6
S CAC14 steering_command_secondary_select_stage  -> H CD3CC
S CB86E steering_control_cycle_pipeline          -> H CEDAE
S CBA72 steering_control_cycle_wrapper           -> H CF028
```

The mappings are call-graph anchored. S `C8DC8` and H `C9CD2` are paired
four-call LTA-control wrappers, with the mapped limiter occupying the terminal
position. S `CA7F0` and H `CBA40` each contain six ordered conditioning stages;
H `CB8BA` occupies the old mode-select position and `CB9B6` the terminal
slew/gain/limit position. The H pair uses regenerated state (`FEBEC278`,
`FEBEC2A6`, `FEBEC2A8`) rather than Sienna's `FEBEC144/16E/170`.

The old source-arbitration/latch trio is different and is intentionally **not**
assigned fake homologs:

```text
S CA354 steering_request_source_arbitration
S CA3B8 steering_lta_mode_latch
S CA3F8 steering_lka_torque_mode_latch
```

Those functions jointly selected authenticated `0x131` LTA versus authenticated
`0x2E4` torque mode. H has neither classic Rx descriptor. The paired root-stage
position collapses to wrapper `CB68A -> CBE6E`, where `CBE6E` decodes H-specific
supervisory state (`FEBEACBD`, `FEBEC26D`, `FEBEADB0`) into six local mode flags
`FEBEC26E..273`. These three canonical roles are therefore closed by a complete
**replacement-surface recensus**, not role transfer.

The separate secondary-command branch is also target-mapped. S
`BA3DA -> CBA42 -> CB49C` corresponds to H `B8E84 -> CEFF8 -> CE974`. Inside
that branch, `CAC14 -> CD3CC` remains immediately upstream of the independently
matched gain/clip stage `CAC6A -> CD440`. H `CD3CC` publishes the analogous
secondary conditioned state at `FEBEC3B8`, after additional H-specific
conditioning.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_steering_nested.json` plus compact H-native
evidence. `tests/verify_corolla_8965H1202000_steering_nested.py` pins the six
role mappings, three-function replacement recensus, wrapper order, H mode
decoder, secondary chain, and raw/decompiler hashes. `steering` now has **zero
genuinely-unresolved named functions**. After §7.24, the global denominator is **316 unresolved**, 29 inspected unique-shape, 111 role-recovered, 262 recensused, 107 structural-only, and 288 exact-body transfers.

### 7.24 Diagnostic residue: H WDBI is a 12-DID surface

The remaining 59 `diagnostics`-tagged named functions are now closed by 27
target-native role mappings plus 32 complete-surface recensuses. The generic DCM
layer is highly conserved: H recovers the CAN diagnostic demux, session policy and
request lifecycle, ClearDiagnosticInformation, WDBI request/class wrappers, RDBI
request worker, and all four generic RoutineControl validation/request roles at
exact canonical body sizes with relocated generated tables/state.

The lower WDBI implementation is a real generation change. Sienna's active table
at `0x25768` has 13 rows; H lookup `877CC/87816` uses a 12-row table at `0x25530`:

```text
H WDBI: 0204 2001 2002 2005 2006 2007 2008 2009 2010 2012 2013 2014
removed relative to Sienna: 200D
```

`2013` and `2014` remain table members but are statically disabled: their H start
callbacks `4A8B8/4A8C0` return internal result `5`, while result callbacks
`4A8BC/4A8C4` are four-byte success no-ops. `2012` remains live with unconditional
start `4A89A` and result `4A89E` reaching H lifecycle helper `B2B6E`. `0204` still
arms pending tag `0x2E10`; the remaining maintenance/persistence callbacks are
regenerated around H-specific state and helper addresses. The old DID-specific
function identities are therefore closed by exhaustive H table/callback recensus,
not S-relative address assignment.

Machine-readable ownership is `data/generated/corolla_8965H1202000_diagnostic_residue.json`
plus compact H-native evidence. `tests/verify_corolla_8965H1202000_diagnostic_residue.py`
pins all 59 dispositions, WDBI table membership, disabled/live DIDs, generic DCM
roles, and raw/decompiler hashes. `diagnostics` now has **zero genuinely unresolved
named functions**. The only remaining genuinely unresolved canonical names are the
**316 untagged functions**; the global denominator is 316 unresolved, 29 inspected
unique-shape, 111 role-recovered, 262 recensused, 107 structural-only, and 288 exact.

### 7.25 Deadline-monitor generated callback surface

The largest remaining untagged family is now closed at its actual generated
configuration boundary. Sienna's deadline subsystem uses three callback tables:
variant-D A (one 13-pointer row), a 28-row simple table (three pointers per row),
and variant-D B (one 13-pointer row). Corolla H preserves the same three-table
geometry and exactly the same callback cardinalities:

```text
                 Sienna base   H base    nonzero / unique
variant-D A      28524         280B4       4/3 S, 3/3 H
simple           28558         280E8      83/82 both
variant-D B      286D0         28260       4/3 both
unique union                                88 both
```

The H simple table retains the final duplicated start callback and null third
slot. Its dispatcher is the unique full-instruction-shape homolog
`S 6962A -> H 639CA` (138 bytes), while the 13-pointer variant-D dispatcher is
`S 6A28A -> H 6462A` (1208 bytes). The simple setup likewise maps by unique
shape `S 3DC88 -> H 387E4` and directly uses H table `280E8`.

All 88 H callback targets were forced only in a disposable project and then
raw-body/decompiler hashed into compact evidence. The canonical 88 named
`deadline_*` callbacks are therefore closed by a **complete target-table
recensus**, not by assigning Sienna callback names to H rows. H-specific monitor
IDs, thresholds, and operands remain target-native configuration.

Machine-readable ownership is
`data/generated/corolla_8965H1202000_deadline_monitor_surface.json` plus compact
evidence. `tests/verify_corolla_8965H1202000_deadline_monitor_surface.py` pins
table geometry/cardinality, dispatcher homologs, all callback hashes, and the
no-fake-one-to-one boundary. The global named residue drops **316 -> 228**.

### 7.26 Nine-channel plausibility monitor family

The 11 named plausibility-monitor residues are now target-native role mapped. The
nine channel steps preserve both generated dispatcher order and their status-index
permutation:

```text
channel:       0      1      2      3      4      5      6      7      8
status index:  7      8      3      4      0      1      2      5      6
H function:   3E118  3E1CA  3E27C  3E42C  3E5DC  3E7CC  3E87A  3E928  3EA16
```

Each channel's 13-pointer callback table moves by exactly `-0x470` from Sienna
(`28984..28B24 -> 28514..286B4`). Every H channel calls common status publisher
`3ECCC`, which remains an 18-byte `<9` indexed byte store (H vector `FEBE76EC`).
The owning generated Rx group calls the channels in the same channel4/5/6/2/3/7/8/0/1
order before aggregation.

The aggregate maps `S 43F28 (436 B) -> H 3EAE8 (484 B)`. It preserves the nine-state
diagnostic/event aggregation but adds one H-specific status publication path. Thus
channel role/table/status semantics transfer, while H thresholds, callback operands,
RAM locations, and the added aggregate output remain target-specific.

Machine-readable ownership is `data/generated/corolla_8965H1202000_plausibility_monitor.json`.
The global genuinely-unresolved named residue drops **228 -> 217**.

### 7.27 Generated packet, record, and bounded-API adapters

Eighteen remaining small adapter roles are now mapped from their owning target
configuration rather than local byte similarity. The six bounded wrappers map
`7ADC8..7AE28 -> 75168..751C8` at `-0x5C60` with identical body-size/signature
pattern `20,18,18,20,20,18`. Their H indirect-call table is `21838`; all six
underlying API targets preserve a separate `-0x4FDA` relocation from Sienna.

The 44-entry low-selector callback table is uniquely recovered at H `269FC`. Its
configured selector set is identical to Sienna's 21 selectors. The seven formerly
unresolved selector callbacks map by selector identity:
`6→90E22, 15→8FA78, 16→8FB8C, 22→91B32, 38→903D0, 39→8B69C, 43→8C362`.

The five-record operation table is H `25F28`, still five `0x1C` records. Its
callback word maps rows 0..4 to `8E5E0/8E610/8E640/8E670/8E6A0`; all five are
48-byte wrappers with the same operation-phase dispatch shape.

These are direct role mappings because selector/record/API-slot identity comes
from target-native configuration. Callback-internal data and the remaining table
payload fields stay H-specific. The global unresolved denominator falls
**217 -> 199**.

### 7.28 Fixed high-page veneer bank regeneration

The remaining veneer-derived annotation cohort is now closed from the raw fixed
slot bank rather than forced decompiler boundaries. The bank spans
`FDE08..FE2A4` in `0x14`-byte slots. A standard veneer is exactly the eight-byte
form `2C 06 <target32-le> 6C 00`. Across all 60 slots, Sienna has 44 such
veneers and H has 38; 36 slot addresses are shared, eight Sienna veneers are
removed, and H adds two veneers at `FE178/FE18C`.

For the 11 previously unresolved canonical veneer/low-target pairs, six slots
persist and directly bind new H low targets:

```text
slot      S target   H target
FDEA8     B7AAE      B6556
FE074     B47F6      B4882
FE088     B482E      B4886
FE0B0     B55E2      B5364
FE1A0     B20CC      B1F4A
FE1DC     B20DC      B1F5A
```

The five unresolved slots `FE164/FE1F0/FE204/FE218/FE22C` are literal
`40 00` fill in H, so both each old high-page veneer annotation and the old
low target name derived from that slot are closed by **replacement-surface
recensus**, not by inventing a new homolog. This proves removal of those fixed
veneer roles only; it does not prove the old low-level operation is absent
elsewhere in H.

The complete bank diff is
`data/generated/corolla_8965H1202000_veneer_bank.json`, verified directly from
both CodeFlash images by `tests/verify_corolla_8965H1202000_veneer_bank.py`.
The 22-name cohort closes as 12 preserved-slot role recoveries plus 10 removed-slot
recensuses, reducing the genuinely-unresolved named denominator **199 -> 177**.

### 7.29 Application command and asynchronous-operation callback tables

The application callback residue is now bound from raw target configuration.
Sienna's 18-entry application command table at `22C30` maps to H `22A74`; H
command 0 is independently anchored by the unique structural mapping
`81970→7BD6C`, and that target pointer occurs exactly once in H CodeFlash at the
table base. All command IDs 0..17 remain configured, so the 17 named command
callbacks map directly by command ID.

The asynchronous operation descriptors materially shrink. Sienna rows `6F3..6FB`
start at `280A0`; H starts at `27DB0` but contains only `6F3,6F6,6F7,6F8,6F9,6FA,6FB`,
followed by the special operation-9 row. Thus the proprietary-F1 callback pair and
operations 3..9 survive, while operation rows `6F4/6F5`—canonical operations 1
and 2—are absent. Their four canonical start/completion names are closed by
complete descriptor-surface recensus rather than invented H homologs.

`data/generated/corolla_8965H1202000_application_callback_tables.json` pins every
raw pointer and discriminator. The cohort closes as 33 target-native roles plus
four removed descriptor roles, reducing genuinely unresolved named functions
**177 -> 140**. Missing descriptor rows prove removal of those configured roles
only, not absence of their lower-level behavior elsewhere in H.

### 7.30 Application transport and interrupt ownership closure

The remaining application transport/interrupt wrappers are now target-native.
The H normal-Rx descriptor table shrinks `47 -> 40` and removes classic CAN
`0x2E4`; the Tx set changes from `260/262/351/394/4A3/4C8` to
`030/351/394/4A3/4C8`. The surviving `0x394` packer is H `47ADA`, PDU index 2,
and now packs four configured signals. The obsolete canonical `2E4` unpacker and
`260/262` packers are therefore closed by complete PDU-surface recensus rather
than assigned false homologs. The special/normal Rx demux and PduR Tx/Rx routers
map to `7A382/7A402/7ADC2/7B040` respectively.

Application EIINT identity is pinned directly by the 384-entry table at `20200`.
Channels `8,133,134,135,187,188,379` map the ECM, TAUJ0 CH0/1/2, CAN1 RX/TX,
and flash-end wrappers to `6ADF4,6A6C0,6A76A,6A816,5F3AA,5F368,5F470`.
Following those wrappers recovers TAUJ bodies `5F258/5F294/5F2D0` and CAN1
interrupt bodies `7D240/7EB4E`; the latter retain literal channel-1
specialization. These roles are hardware-channel/configuration identities, not
address-offset transfers.

Machine-readable ownership is in
`corolla_8965H1202000_application_transport_residue.json`,
`corolla_8965H1202000_application_interrupt_vectors.json`, and
`corolla_8965H1202000_application_interrupt_bodies.json`.

### 7.31 Clean H direct-call graph recensus

The generic canonical names `direct_call_target_*` are discovery provenance from
`SeedDirectCallTargets.java`, not stable semantic names. A clean H import was
therefore censused directly rather than forcing one-to-one Sienna pairings. The
tracked compact evidence contains **5,425 functions, 159,192 instructions,
9,509 literal call edges, and 5,151 unique literal call targets**; every in-image
literal target resolves to a function in the same clean H corpus. This complete
call-graph recensus closes the 153-name canonical direct-call-seed class at the
provenance level. Exact-body and independently recovered semantic roles retain
higher precedence; the recensus itself does **not** imply behavioral homology.

### 7.32 Final canonical named-residue closure

The last 34 genuinely-unresolved canonical names are now closed by target-native
owner/configuration evidence. Thirty-three have concrete H successors; one is a
real target-generation removal:

- boot EIINT dispatcher `748 -> 72C`; its non-contiguous owned blocks and shared
  loop region transfer byte-for-byte at `-0x1C`;
- boot default/secondary exception handlers `1E1E -> 1E02` and `1E2A -> 1E0E`;
- **boot TAUJ0 CH2 is removed**: Sienna EIINT code `1087 -> 1E44` is absent from
  H's shortened boot table, which contains only `10BC`, `10C0`, `10C1`, and the
  default row. H `1E5E` belongs to `10BC` and is not a TAUJ0 homolog;
- CRC result/busy/compute `47DE/47E4/47EA -> 47C2/47C8/47CE`, preserving the
  fixed `FFD51020/004/000` hardware engine;
- application entry remains `20880`; programming reset/stub helpers map to
  `482AE/8441C`; RAM-range validation maps `4EA78 -> 4A4D4` with its five-entry
  exclusion table regenerated at `28F0C`;
- proprietary `0xAB` selector/event/query cone maps through
  `9193E -> ... -> 87384`, with event-query/detail/active-list/state at
  `4AF74/5031A/4FE70/4FFD8`; RMBA start/poll map by SID `0x23` phase order to
  `8F7C0/8F720`;
- expiry slot 7 maps `94B86 -> 8FBAC`; programming mode `0x900` entry maps
  `B20EA -> B1F68` from the unchanged `AEB00` transition-table geometry;
- the generated Rx consumer, RAM init, and RTE staging copies map by preserved
  owner-call order to `5262C`, `5316C`, and `56BAC/5722E/5778E`;
- application default/vector-`0x90` exception handlers map directly from vector
  words to `5C0F2/5EE7E`; timer reload maps to `5F812` and adds H's `FFE21008`
  channel; the TAUJ0 CH0 sample snapshot maps to regenerated `5FB30`;
- the ECM shutdown jump maps `7059E -> 6A93E`; input snapshot and substate map
  `BCB3A -> BBA48` and `CBCC8 -> CF27E`;
- `fd0d7_status_fault_monitor B6396 -> B5EA4` is a **consolidated successor**:
  H still configures `0x0D7`, the expanded stage remains in the per-tick fault
  cluster, calls the system-event setter, and still emits event `0x2D`, but its
  internal qualification logic is not asserted equivalent.

The evidence-graded 1,113-function denominator is therefore now fully classified:

```text
verified exact-body transfers              288
target-native role-recovered                238
complete target-surface recensuses          461
target-native inspected unique-shape        126
structural candidates only                    0
genuinely unresolved                          0
```

`data/generated/corolla_8965H1202000_final_named_residue.json` owns the final
33-successor/1-removal closure, with raw-bound compact support in
`corolla_8965H1202000_final_named_residue_evidence.json`. Zero genuinely
unresolved names is now complemented by target-native inspection of every former
shape-only candidate; no structural-only rows remain. The inspected-unique-shape
class still remains deliberately weaker than semantic role recovery.

### 7.33 Final unique-shape target-native inspection

The last 96 `structural-candidate-only` rows were all **unique-exact-shape**
matches, not ambiguous candidates. Every corresponding H target is now compacted
from the existing target-native decompiler corpus and bound to the raw H body and
decompiler hash in
`data/generated/corolla_8965H1202000_structural_residue_decompiler_evidence.json`.
All 96 targets decompile successfully, their target addresses/body sizes agree
with the independent structural-transfer artifact, and the evidence set is stable
across regeneration.

This promotion is intentionally narrow: it records H operands/dataflow for each
unique complete-instruction-shape candidate and moves those rows to
`target-native-inspected-unique-shape`; it does **not** upgrade them to semantic
role equivalence. The final 1,113-function evidence distribution is therefore:

```text
verified exact-body transfers              288
target-native role-recovered                238
complete target-surface recensuses          461
target-native inspected unique-shape        126
structural candidates only                    0
genuinely unresolved                          0
```

Thus every canonical named function is now backed by exact bytes, independently
recovered target role, complete target-surface recensus, or target-native
operand/dataflow inspection. Remaining uncertainty is claim-specific (for example
field-for-field equivalence of regenerated code, runtime reachability, or behavior
that needs live/bench evidence), not missing comparative static coverage.

### 7.34 Techstream semantic join: DID 1C02 is the live internal Command Value Torque observable

The initial H static-coverage pass did not repeat the Techstream/DDB correlation
that had been unusually productive on Sienna. Doing that target-specific join
changes the steering interpretation in a useful way.

`GetDatMonListP5_DT.dll` constructs the ECU support-data-ID list and filters P5
monitor exposure through `CheckSupportPid`. Raw `EMPS_P5.ddb` type-62 records
contain a primary/alternate Data-ID pair at `+0x36/+0x38`: every nonzero
alternate word resolves in the same database's type-61 `DataIdForDm` table, and
every nonzero primary does as well except the deliberate `0xFFFE` sentinel.
Techstream monitor **402 `Command Value Torque`** is 16-bit, resolves through the
physical-data/unit chain to **Nm**, and carries primary Data ID **`0x1C02`**
(alternate `0x3C02`).

That is an exact target join rather than vocabulary transfer. H independently
implements RDBI DID `0x1C02` as live two-byte callback `0x495A0`. The callback
uses the same dimensional formula shape as Sienna's corresponding diagnostic
producer and the H-local source traces into the active steering pipeline:

```text
H CE974 active steering pipeline
  -> CD55A  compose/bound local command precursor -> FEBEC3C0
  -> CD5DC  FEBEC3C0 * FEBEAC5A / 0x400 -> FEBEC3D2
  -> CE928  FEBEC3D2 -> FEBEAC56
  -> BB9E8  FEBEAC56 -> FEBEE40A
  -> 56892 / 57692  FEBEE40A -> FEBE65F2
  -> 495A0  scale FEBE65F2 by FEBEE8A6, clamp +/-20000, emit DID 1C02
```

This resolves a conceptual ambiguity from the Sienna-only correlation. The same
H image has no configured SecOC or normal-COM `0x2E4/0x131` steering ingress, and
the complete H external-supervisor-ingress census finds no replacement large
external scalar in the mapped COM cone. Nevertheless **Command Value Torque
remains live**. Monitor 402 therefore labels an **internal EPS command-value
torque observable**; it is not intrinsically the external `0x2E4` field. On
Sienna, `0x2E4` is one recovered upstream command source. On H, the source is
composed by H-local steering logic and its ultimate external/LTA provenance is
still the missing question.

The broader join is also useful. Of H's 226 readable RDBI DIDs, **124** occur in
`EMPS_P5`'s type-61 Data-ID table, yielding **137 named monitor rows across 121
primary Data IDs**. This supplies firmware-joined names for commanded and actual
d/q current, motor phase current/duty, torque sensors, steering angle, motor
rotation, and other internal states rather than requiring address-based guesses.
`EMPS2_P5` has a weaker 112-DID overlap. The newer target-angle vocabulary in
`EMPS_P5`—`Target Lateral ID`, `Target Steering Angle After Output
Compensation`, `Advanced Drive Target Steering Angle`, and System-2 variants—is
grouped under primary DIDs `0x1CEE/0x1CEF`; **neither DID exists in H RDBI**.

The current-domain rows close a second, more important join that the firmware-only
pass had left open. Techstream names `0x1151/0x1152/0x1153/0x1154` as actual-Q,
command-Q, actual-D, and command-D motor current respectively, all 16-bit in A,
and `0x1156` as `Final Motor Current Limited (Q Axis)`. Target-native H dataflow
then proves the command-Q path:

```text
FEBEC3D2                    # DID 1C02 Command Value Torque source
  -> CD5DC -> FEBEC3D6      # gate / symmetric bound
  -> CD644 -> FEBEC3D4      # normal pass-through, bounded override on fault state
  -> CE928 -> FEBEAC54
  -> BB9E8 -> FEBEE40C
  -> 312F0 -> -FEBEE40C -> FEBE6964
  -> 336EE -> FEBE6C1A
  -> 3322E -> FEBE6BC0      # Techstream-visible base Q-current command
             + FEBE6BE4
             -> FEBE6BB8    # compensated Q-current command
  -> 33160 supplies raw Q feedback aggregate FEBE6BB4
  -> 32934: FEBE6BB8 - FEBE6BB4 -> bounded Q-current error
  -> 32958 / 329A0          # Q-current PI / integrator
  -> 58226 high-rate motor worker
  -> already-mapped transform / duty / TSG3 PWM chain
```

`FEBE6BC0` is therefore not being promoted to "the final PI input" merely because
Techstream calls it `Command Value Current (Q Axis)`. It is the OEM-visible base
Q command. The same source term `FEBE6C1A` also contributes to compensated
command `FEBE6BB8`, which is explicitly compared against raw Q feedback
`FEBE6BB4` before the dedicated PI stage. That closes the actual closed-loop
motor consequence.

The same motor-feedback combiner `33160` publishes saturated diagnostic
`FEBE6BAE/FEBE6BAC`, which `5722E` snapshots to `FEBE6592/FEBE6590` and the
`1151/1153` callbacks expose as actual Q/D current. `CD5DC -> FEBEC3D8 -> CE928
-> BB9E8 -> FEBEE414 -> FEBE65FC -> 49298` independently closes DID `0x1156`
as the selected Q-axis current-limit observer. The D-axis **command** is separate:
`3364E` updates an internal auxiliary state through `335EE/33622`, `3322E`
publishes it as `FEBE6BC2`, and DID `0x1154` observes it. No static edge from the
`1C02` command-torque chain into that D-axis command was recovered.

So the old downstream question is closed: H's **general internal command-value
torque state really reaches the closed-loop Q-current controller**. That does not
make `1C02` an autonomous-lateral command. The remaining question is specifically
which, if any, external/LTA contribution is added upstream of that general EPS
command.

The Techstream surface also closes two tempting diagnostic shortcuts. The
master-routed category-405 / generation-20 `EMPS_P5` database contains section
types `61/62/63/80/87/88/90/91`, not classic type-11/type-12 Active Test tables;
its eight routed DLLs are data-monitor, DTC, support, CID/SID22, and RoB roles,
with no Active-Test- or Routine-named DLL. And H DID `0x106A`, which Techstream
calls `Cooperation Control State`, is an exact success stub that emits no byte.
The package therefore supplies excellent observation vocabulary but no recovered
dealer steering-command primitive for this calibration.

Machine-readable ownership:
`data/generated/corolla_8965H1202000_techstream_correlations.json` and
`data/generated/corolla_8965H1202000_techstream_steering_decompiler_evidence.json`;
`tests/verify_corolla_8965H1202000_techstream_correlations.py` regenerates the
join and raw-binds all cited H functions and Techstream databases.

### 7.35 Autonomous-lateral command closure: protected B6 carries target steering angle

The deepest fixed-map audit corrects the last important negative in the H steering
analysis. The retained Sienna-homolog conditioner is live, and protected CAN-FD
`0x0B6` supplies the external target that drives it.

The representation bug was specific: H snapshots generated COM state through the
fixed application `GP=0xFEBEB800`, so direct-symbol searches miss stores/copies that
Ghidra renders only as `GP+offset`. Two such aliases close the B6 command surface:

```text
signal254 B3[5:0]:  FEBE7D96 -> FEBEF127 -> GP-0xA50 = FEBEADB0
signal255 B4:B5:    FEBE7D94 -> FEBEF1CC -> GP-0x97E = FEBEAE82
```

Signal254 is the unsigned 6-bit **Target Lateral ID** request selector. Techstream's
exact P5 pattern dictionary gives `0=No Request (Manual Operation)` and closes H's
accepted active values as `1=PCS`, `4=LDA`, `10=Hands Off LTA`, `11=LTA/LCA`, and
`19=PDA`; H-special IDs `25/27` are `AP/Remote Parking`. `CBE6E`, once
`FEBEACBD==0` and communication gate `FEBEC26D==1` hold, asserts the common active
flag only for the five supported active IDs.

Signal255 is the command magnitude. `C9DB0/C9E54` turn signed16 `FEBEAE82` into a
replicated target state. Independently, `CBD7E/CB096` reconstruct the measured
steering-angle domain from FD `0x025` signals184/185/186. `CA138` applies the same
`0xB76/0x400` gain to target and measured state and forms target-minus-measured error.
That target-native symmetry is the decisive semantic proof: **B6 signal255 is a
target steering-angle command**, not torque and not an opaque supervisory value.

The controller path then continues through the already recovered H pipeline:

```text
B6 signal255 target
  -> C9DB0/C9E54 target state
  -> CA138 target - measured-angle error
  -> CAC24/CA614/CA83A/CAA44/CAD1C selection and conditioning
  -> CC18E/CC2EC/CAD62 replicated magnitude
  -> C9C16/CB8BA/CB9B6 -> C2A8
  -> CD3CC general command composition
  -> C3B8 -> C3BC -> C3BE -> C3D0 -> C3C0 -> C3D2
  -> DID 1C02 Command Value Torque
  -> Q-current command path -> DID 1152 Command Value Current (Q Axis)
```

The propagation is conditional on the recovered mode/output gates, as expected for a
cooperative controller. `1C02` remains a general multi-contributor torque observer;
it is not a wire echo of signal255. B6 signals262/263 also remain live percentage-like
modifiers of internal contributor families through `CC442/CBFCE`.

The B6 **receiver-loss path is also closed in scheduler ticks**. Status slot `0x18`
flows through `44744(0x18) -> FEBE7DA0 -> FEBEF132 -> FEBEADB9`; `CC7F8` requires
`ADB9==0` before it can assert `FEBEC26D`. PDU42's raw descriptor at `0x22770` is
`060000002000000c`: successful reception reloads its deadline to `6+1 = 7` foreground
ticks and clears activity[PDU42], while `7683C -> 87AA0` marks it `0x5A` when that
countdown expires. Because the lower deadline and higher status paths run in the
same TAUJ0-CH3 foreground tick, the first expiry makes B6 status nonzero and drops
cooperative selection immediately. The slower slot-18 row `2a00000bb8010200` has a
configured threshold of `440` ticks for an extended status state; it is not the first
steering cutout. The CH3 wall-clock period remains statically unsupported, so the
receiver timeout is **7 ticks, not a claimed number of milliseconds**.

B6 signal261 (B7[5:0]) is a 6-bit rolling sequence counter: `CB246` computes the
modulo-64 delta, normalizes delta `0/1` to an effective gap of `1`, and caps larger
gaps at `8` before plausibility/supervision consumes them. Signal258 gates one
profile-dependent controller contribution when equal to `1`; signal260 is a
four-state controller selector; signal264 participates in the AP/Remote-Parking
validity/inhibit state; and signal265 is republished only while B6 communication is
healthy. Their literal OEM names are not assigned from family vocabulary alone.

The **entire 32-byte receiver envelope is now byte/bit classified**, rather than
leaving the rest of the CAN-FD payload as an opaque tail. H SecOC record 2 at
`0x257CC` is a normal-freshness profile for Data ID `0x00B6`, application/route PDU
42, secured length 32, full freshness 46 bits, transmitted freshness 4 bits, and
transmitted authenticator 28 bits. Thus B0..B27 are the 28-byte authenticated
application region and B28..B31 are the four-byte security trailer. Target-native
`88744` extracts that trailer exactly as:

```text
B28[7:4]              FV4 = message_counter_low2 || reset_counter_low2
B28[3:0] + B29..B31  transmitted CMAC_MSB28
```

The normal-freshness path is exact too. `89A46/89E2C/89E9A/89876` reconstruct and
pack six bytes as
`trip16 || reset20 || message8 || reset_low2 || 00b`, i.e. 46 meaningful bits
left-aligned with two zero pad bits. `87FC2` then constructs the CMAC verification
input as exactly **36 bytes**:

```text
00 B6 || B0..B27 || reconstructed_freshness[6]
```

The receiver computes AES-CMAC-128 through generated config/job 0 and ICU-S slot 4
and compares the transmitted MSB28. The **slot selector** is closed; the live
slot-4 key value remains CPU-opaque. Successful verification routes through
`88856 -> 89514 -> 7AFB6`, whose raw PduR tables resolve route 42 to `76A3C`
(COM RxIndication PDU42). The queue/COM path retains a 32-byte PDU geometry, so the
static proof deliberately does **not** claim that the trailer is physically stripped
before COM RAM. Instead, the application-consumer census proves what matters: there
is no recovered application consumer for the trailer.

The application side is much smaller than the authenticated envelope:

| Wire bytes | Recovered EPS-application use |
|---|---|
| B0..B2 | authenticated; no recovered application consumer |
| B3 | bits5:0 = signal254 Target Lateral ID; bits7:6 have no recovered consumer |
| B4..B5 | signal255 signed target steering angle |
| B6 | signal256 B7 and signal257 B6:4 are extracted/snapshotted but have no recovered downstream consumer; signal258 B2 is a live steering-cone gate; signal259 B1:0 is staged but has no recovered downstream consumer; B3 has no scalar extraction |
| B7 | signal260 B7:6 four-state selector; signal261 B5:0 modulo-64 sequence |
| B8 | signal262 live percentage-like contributor modifier |
| B9 | signal263 live percentage-like contributor modifier |
| B10 | signal264 B7 validity/inhibit and signal265 B2:0 valid-gated mode/status; B6:3 have no recovered consumer |
| B11..B27 | authenticated; no recovered application consumer |
| B28..B31 | SecOC only under the recovered application surface: FV4 + CMAC28 as above |

Across all 256 wire bits this partitions to **51 bits with recovered downstream EPS
semantics, 6 bits extracted but with no recovered downstream consumer, 167
authenticated application bits with no recovered application consumer, and 32 SecOC
trailer bits**. That negative is not based only on the generated scalar unpacker: a
5,138-function application-corpus scan finds no B6 use through the literal block/group
receive API, no full-PDU PDU42 copy, no raw absolute B6-buffer pointer, and no
named/absolute/simple-GP-alias constant-displacement reference into
`FEBE4AF4..FEBE4B13`. Arbitrary value-set/computed-base aliases and hardware/DMA
access remain outside that bounded static proof.

This distinction matters for a future sender. The EPS imposes no **recovered
application-semantic** constraint on most of B0..B2/B11..B27, but those bytes are not
cryptographically irrelevant: every B0..B27 bit is in the CMAC input. Upstream
producer-side formatting may also constrain reserved/unused values, so this is not a
claim that openpilot may fill those bytes arbitrarily. It does show that the receiver
contract is far narrower than the raw 32-byte DLC suggests.

Techstream independently classifies `0x0B6` missing-message ownership as U012987
**Lost Communication with Brake System Control Module / Missing Message**. That pins
the immediate monitored sender relationship. Techstream now also closes the
module-dependency topology: Corolla P5 installs category 498 `FRC_P5`, category 435
**`ABS_P5` = Brake/EPB**, and category 405 `EMPS_P5`; FRC carries X216E `Front
Recognition Camera => BRK Communication Invalid`, while ABS monitors EPS communication
and exposes DID `0x107E ADS Control EPS Pinion Angle2` at signed 0.00025 rad/count.
FRC also monitors EPS directly and both FRC/ABS reference an Automated Driving System
Interface module, so this still does not prove that category 435 forwards or transforms
the planner bytes into B6. Techstream's P5 steering vocabulary also contains
**Target Lateral ID** and **Target Steering Angle After Output Compensation**, but
exact H implements neither corresponding `0x1CEE/0x1CEF` observer DID, so those names
are corroboration rather than a one-to-one B6 signal-name transfer.

The negative residue is now useful and narrow. D7's only 16-bit scalar is still
`CAN Vehicle Speed (SP1)`; B6/D7 nonscalar block/group/full-PDU alternatives remain
negative; the shared command-sized `0x025` fields are proved measured angle/rate; and
the separate retained Sienna `0x2E4` torque-clamp input remains zero-fed. The recovered
scalar and literal block/group/full-PDU surfaces expose no second command-sized ingress
comparable to signal255; the new exact COM-window census also finds no
named/absolute/simple-GP-alias constant-displacement B6-buffer reference anywhere in
5,138 application functions. Arbitrary value-set/computed-base aliases and
DMA/peripheral mutation remain outside this static proof.

The exact **H/F receiver-side B6 contract is therefore closed under the repository's
bounded CPU/application evidence model**: protected FD `0x0B6` signal254 selects the
OEM Target Lateral request, signal255 commands target steering angle at a closed
controller-equivalent scale, signal261 supplies modulo-64 sequence state, missing B6
cuts cooperative control after seven foreground ticks, all 32 wire bytes are assigned
to authenticated application data versus SecOC trailer, and the normal-freshness/
CMAC verification input and ICU-S slot selection are exact. Every table/function used
for this result lies inside H/F's byte-identical application region, so the receiver
wire/application/SecOC contract transfers exactly to `8965F1208000`.

What remains before production use is now **sender-side or control-policy work**, not
another receiver-payload search: the literal signal255 OEM unit and exact names for
secondary live fields, sender wall-clock cadence, sender freshness-state ownership,
the slot-4 secret value, normal target/rate/driver limits, stock-source suppression,
and the upstream byte-level producer/forwarding transform despite the now-closed
FRC/`ABS_P5`/EPS module topology. Receiver freshness **format and reconstruction** are
no longer open.

Machine-readable ownership:
`data/generated/corolla_8965H1202000_b6_target_angle_ingress.json`,
`data/generated/corolla_8965H1202000_b6_receiver_contract.json`,
`data/generated/corolla_8965H1202000_b6_full_receiver_contract.json`,
`data/generated/corolla_8965H1202000_b6_full_receiver_decompiler_evidence.json`,
`data/generated/corolla_8965H1202000_b6_secoc_verification.json`,
`data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json`,
`data/generated/corolla_8965H1202000_lta_command_provenance.json` v8, and
`data/generated/corolla_8965H1202000_supervisor_external_ingress_census.json` v2;
`tests/verify_corolla_8965H1202000_b6_target_angle_ingress.py`,
`tests/verify_corolla_8965H1202000_b6_full_receiver_contract.py`,
`tests/verify_corolla_8965H1202000_b6_secoc_verification.py`,
`tests/verify_corolla_8965H1202000_lta_command_provenance.py`, and
`tests/verify_corolla_8965H1202000_supervisor_external_ingress.py` pin the exact raw
bodies, GP aliases, 256-bit wire partition, freshness/trailer arithmetic, complete
freshness-window/CMAC/commit state machine, field geometry, controller path, H/F
identity, and bounded alternatives.

### 7.36 Protected-B6 SecOC verification closure: authenticated epoch, window, CMAC, and commit

The previous receiver-envelope closure established what B6 authenticates. The remaining
question was whether the receiver's **stateful verification policy** could be recovered
well enough to reproduce the authenticated envelope rather than merely its byte layout.
It can. The exact H target-native path is now closed from B28 FV4 extraction through
freshness candidate selection, ICU-S command 7, post-CMAC state commit, and PDU42
release. The corresponding H/F application bytes are identical, so the result transfers
byte-for-byte to `8965F1208000`.

B6 is SecOC record 2 at `0x257CC`, but freshness ID 2 is the second **ordinary**
freshness slot because record 0 (`0x00F`) is the synchronization profile and records 1
(`0x0D7`) and 2 (`0x0B6`) are ordinary profiles. `0x89558` performs that distinction
explicitly while walking the three records. Therefore B6's committed 12-byte state is
`FEBE54D4..FEBE54DF`, its pre-authentication candidate is staged at
`FEBE54EC..FEBE54F7`, and each slot is laid out as `trip_u32`, `reset_u32`,
`message_u16`, plus two auxiliary/pad bytes. Global authenticated synchronization state
from `0x00F` lives separately at `FEBE54AC`/`FEBE54B0` (current trip/reset) and
`FEBE54B4`/`FEBE54B8` (pending trip/reset). Application initialization `0x89812`
zeros those current/pending cells and both ordinary current/pending slots; this is an
exact initialization write, not a whole-program claim that no external/NvM restoration
could ever exist.

The four transmitted freshness bits are exactly `B28[7:4]`:

- `B28[7:6]` = the low two bits of the SecOC **8-bit message counter**;
- `B28[5:4]` = the low two bits of the **20-bit reset counter**.

`0x89CDA` reconstructs reset freshness around the current authenticated `0x00F` reset
counter. Its trial order is exact:

1. current reset;
2. current - 1;
3. current + 1;
4. current - 2;
5. current + 2,

with the 20-bit domain bounded to `0..0xFFFFF`. A trial is eligible only when its low
two reset bits equal the transmitted `reset_low2`. The same-PDU authentication retry
counter at `FEBE5406` selects the Nth eligible trial. With only two reset bits on the
wire, the only ambiguity inside this five-candidate window is `current-2` versus
`current+2`: both have the same low two bits. Attempt 0 therefore tries `current-2`,
and B6 record `+0x10=1` permits exactly one retry capable of trying `current+2`.
This gives the otherwise opaque retry count a concrete protocol role.

Within an unchanged trip/reset epoch, `0x89D58` reconstructs the next message counter
as the strictly forward value congruent with the received low two bits:

`candidate = (committed & ~3) | received_low2`, adding 4 when
`received_low2 <= (committed & 3)`.

The ordinary accepted advance is therefore 1..4 counts, not an arbitrary modulo-4
match. When the epoch changes, the candidate must be lexicographically newer under
`global_trip > committed_trip` or `global_trip == committed_trip && candidate_reset >
committed_reset`; its initial message counter is then the received low-two-bit value
`0..3`. An older/equal candidate returns `0x23` while another reset trial can still be
attempted, then `0x22` once the reset search is exhausted.

The message/reset terminal boundary has a non-obvious behavior that is now pinned.
When the next congruent 8-bit message value would exceed `0xFF`, or the selected reset
is already `0xFFFFF`, the reconstructed message is forced to `0xFF`; outer
`0x89E9A` returns status `0x24`. **`0x24` is not a rejection.** `0x88A56` invokes the
configured freshness-boundary callback through `0x88908`, leaves the queue in verify
state C3, and falls through to the same CMAC-build/command-7 path as status 0. By
contrast, `0x22` moves to freshness-failure A5 and never submits command 7, while
`0x23` requests another reset candidate through `0x8891E(...,0x201)`.

The authenticated synchronization profile also handles 16-bit trip wrap explicitly.
H's threshold byte is `0x0F`: when current trip is at least `0xFFFF-15`, a nonzero
new trip through 16 can be considered forward wrap by `0x89F6E`. A successful sync
CMAC causes `0x8A130` to commit the pending global trip/reset. If wrap was accepted,
`0x8A130` calls `0x8A0AE(0)`, which clears both current and pending ordinary freshness
slots whose internal record `+0x04` linkage field is zero. That includes both D7 and
B6. The receiver therefore does not carry a stale lexicographic B6 epoch across an
authenticated trip wrap.

Once a candidate is accepted by the freshness layer, `0x89E9A` stages it in the B6
pending slot **before** authentication. The generic worker then builds the already
recovered 36-byte input

`00 B6 || B0..B27 || freshness[6]`

and submits AES-CMAC verification with a 28-bit received tag. B6 selects SecOC config
0 / CryptoIf job 0; the exact config bytes at `0x2570C` are type 1 with protected
ICU-S selector 4. `0x822D0` moves that selector into the driver descriptor and
`0x83BF4` issues command word `(4 << 16) | 7 = 0x00040007`. There is no separately
recovered source/profile identifier concatenated into the CMAC input: the authenticated
prefix is the 16-bit DataID `0x00B6`; freshness ID 2 selects receiver state rather
than adding another CMAC field. The slot-4 **secret value** remains opaque to mapped
CPU/application code.

Command-7 polarity is closed independently two ways. Live post-CMAC gate `0x88C16`
treats `FEBE5450 != 0` as mismatch. The target-native disabled command-7 KAT at
`0x62430` initializes its verify-result byte to 1 and only reports success if command 7
changes it to zero. Therefore command-7 result `0` means CMAC match.

The post-authentication state ordering is exact:

- `0x88C9C` calls post-CMAC gate `0x88C16` only when verify worker `0x88A56`
  returns 0;
- `0x88C16` invokes `0x88BE2` **before** upper delivery;
- on CMAC match, `0x88BE2` passes freshness ID 2 with high16 clear to `0x89758`,
  which resolves ordinary slot 1 and `0x8A07A` copies the 12-byte pending B6
  freshness into committed state;
- only after that commit does the verified-PDU path release route/PDU42 to COM at
  `0x76A3C`;
- on CMAC mismatch, `0x88BE2` sets high16 in the callback argument, so `0x8A07A`
  does **not** commit the pending freshness, `0x8891E(...,0x200)` may retry the same
  queued PDU, and PDU42 is not delivered.

Freshness-valid but MAC-invalid B6 therefore cannot advance committed freshness and
cannot reach the steering application.

The two retry counters are also different mechanisms. B6 record `+0x10=1` bounds the
same-queued-PDU freshness-candidate/CMAC-mismatch retry at `FEBE5406`; record
`+0x2E=2` separately bounds CryptoIf submit/busy-result-2 retries at `FEBE5404`.
`0x88702` resets both counters when a **new** PDU transitions D2→C3. Its B4→C3 path
itself performs no additional reset, but the authentication-retry scheduler `0x8891E`
has already incremented `FEBE5406` **and cleared `FEBE5404`** before entering B4.
By contrast, `0x889C2` increments only `FEBE5404` on CryptoIf result 2, so B4→C3
preserves that busy count across retries of the current authentication candidate. The
exact scopes are therefore: one auth/candidate retry for the current queued PDU, and up
to two CryptoIf-busy retries per authentication candidate/verification attempt. Neither
is a cross-frame guess throttle.

Finally, B6 has two independent rolling counters. SecOC's message counter is 8 bits
internally and only low2 is transmitted in FV4. Signal261 is a separate application
counter in `B7[5:0]`, modulo 64 with the already recovered effective-gap cap 8. It is
inside authenticated B0..B27, but it is unpacked/consumed only after verified PDU42
delivery and does not participate in freshness candidate selection. A conforming sender
must therefore maintain **both** the SecOC trip/reset/message state and the independent
signal261 application sequence; matching one does not synchronize the other.

The exact receiver-required sender envelope is consequently known:

1. maintain a full freshness tuple consistent with authenticated `0x00F` trip/reset
   state and B6's 8-bit message progression;
2. encode FV4 as `message_low2||reset_low2` in `B28[7:4]`;
3. build freshness48 as `trip16||reset20||message8||reset_low2||00b`;
4. compute AES-CMAC-128 over `00 B6 || B0..B27 || freshness48` with the protected
   key selected by ICU-S slot 4;
5. transmit CMAC_MSB28 in `B28[3:0],B29,B30,B31`; and
6. independently maintain signal261's modulo-64 application sequence.

This closes the **EPS receiver-side verification algorithm**, not the upstream sender.
Still open are the slot-4 secret or an available approved ICU-S operation that can
produce the tag, sender-side ownership/source of the live trip/reset/message state,
stock B6 wall-clock cadence, and the upstream FRC/Brake/gateway payload/signing
producer. Those are now the actual sender blockers; another generic pass over the H/F
receiver path is not.

Machine-readable proof:
`data/generated/corolla_8965H1202000_b6_secoc_verification.json` and
`data/generated/corolla_8965H1202000_b6_secoc_verification_decompiler_evidence.json`;
`tests/verify_corolla_8965H1202000_b6_secoc_verification.py` independently regenerates
the model and pins the H/F bytes, profile geometry, RAM slots, reset/message candidate
arithmetic, `0x24` and trip-wrap edge cases, command-7 result polarity, retry scopes,
commit-before-delivery ordering, slot-4 selector, and signal261 separation.

## 8. Remaining evidence boundary

### Static closure criterion

For this `8965H1202000` CodeFlash specimen, the comparative static-analysis
objective is now closed under the repository's evidence model: all 1,113
canonical named functions have target-native evidence; there are zero genuinely
unresolved rows and zero structural-only rows; all generated foreign surfaces
that replaced one-to-one functions are explicitly recensused; and H-native
successors are kept at the weakest justified confidence class rather than being
promoted by address similarity. Another undirected pass over the same CodeFlash
would therefore repeat already-covered evidence rather than answer a remaining
static question.

The remaining questions require **different evidence**, not more generic static
coverage of this image. The corpus still does **not** provide:

- a same-vehicle capture of a known **stock LTA steering interval** synchronized
  to protected B6 signal254/255/258/260/261/262/263/264/265, measured angle,
  `1C02`, `1152`, and actual Q current; the receiver-side request IDs, 7-tick loss
  cutoff, and sequence arithmetic are already static facts, while the capture is
  still needed for sender wall-clock cadence, secondary-field naming, and operational
  target/rate bounds;
- proof of the upstream feature producer and route that causes the Brake System
  Control Module to emit the recovered B6 target-angle command;
- a direct UDS `F181` transcript from the same acquisition;
- a stock passive `carFw` inventory joining the public route to the firmware;
- proof of where the selected slot-4 key value is physically stored or internally derived inside ICU-S;
- same-runtime-epoch proof between the CAN oracles and any DataFlash read;
- a retained Techstream transcript proving that this exact vehicle session chose
  category-405 `EMPS_P5` (the 124-DID overlap and exact `1C02` join make it the
  strongest static vocabulary fit, not a captured session-selection proof);
- proof that the low boot/calibration differences between `8965H1202000` and
  Span `8965F1208000` do not alter any vehicle-level limit or calibration needed
  for a production command implementation; their entire application region is
  already byte-identical.

The firmware artifact identifies itself strongly; the vehicle/model-year link
remains contributor attribution rather than route-contained identity.

## 9. Highest-value next evidence

For **Corolla steering support**, the highest-value experiment is now a
same-vehicle B6 **parameter-recovery capture**, not another firmware-wide static pass:

1. establish an interval where factory LTA is visibly applying steering;
2. record protected `0x0B6` and measured-angle `0x025` without openpilot-generated
   echoes being mistaken for stock traffic;
3. simultaneously read `1C02 Command Value Torque`, `1152 Command Value Current
   (Q Axis)`, and actual Q current with read-only XCP/DAQ if `7F7/7F8` is reachable;
4. validate the statically closed signal254 request map, 7-foreground-tick receiver
   loss cutoff, and signal261 modulo-64/gap-cap-8 rule against stock traffic while
   recovering sender wall-clock cadence, exact secondary-field semantics, and
   rate/target bounds; and
5. join the captured B6 producer to FRC/Brake/gateway state so the upstream routing
   and SecOC source contract is explicit.

That experiment turns the recovered receiver semantics into the quantitative limits
needed for a safe openpilot/Panda implementation.

For the separate key/provisioning question, retain the controlled paired capture:
full-bus synchronization/protected CAN immediately before the programming/range-
dump transition, then repeat after recovery/reset and retain the corresponding
memory snapshot plus a direct `F181` response. That resolves runtime-key
continuity without assuming it across separate jobs.

For Sienna-style steering-bridge portability, the higher-value next EPS CodeFlash
is still a foreign calibration whose Gate-2 queue actually contains classic
`0x2E4/0x131` records—for example Span's distinct `8965F1208000` if that image
becomes available. The `8965H1202000` corpus has now served two purposes: it is a
negative-capability regression for the classic `0x2E4/0x131` bridge **and** a fully
analyzed positive example of the replacement protected-B6 target-angle architecture.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [COM-012](../reference/index.md#finding-com-012), [SECOC-042](../reference/index.md#finding-secoc-042), [SECOC-045](../reference/index.md#finding-secoc-045), [SECOC-063](../reference/index.md#finding-secoc-063), [SECOC-071](../reference/index.md#finding-secoc-071), [TMS-020](../reference/index.md#finding-tms-020), [TMS-021](../reference/index.md#finding-tms-021), [TMS-022](../reference/index.md#finding-tms-022), [TMS-023](../reference/index.md#finding-tms-023), [VAR-004](../reference/index.md#finding-var-004), [VAR-005](../reference/index.md#finding-var-005), [VAR-007](../reference/index.md#finding-var-007), [VAR-008](../reference/index.md#finding-var-008), [VAR-009](../reference/index.md#finding-var-009), [VAR-010](../reference/index.md#finding-var-010), [VAR-011](../reference/index.md#finding-var-011), [VAR-012](../reference/index.md#finding-var-012), [VAR-013](../reference/index.md#finding-var-013), [VAR-014](../reference/index.md#finding-var-014), [VAR-015](../reference/index.md#finding-var-015), [VAR-016](../reference/index.md#finding-var-016), [VAR-017](../reference/index.md#finding-var-017), [VAR-018](../reference/index.md#finding-var-018), [VAR-019](../reference/index.md#finding-var-019), [VAR-020](../reference/index.md#finding-var-020), [VAR-021](../reference/index.md#finding-var-021), [VAR-022](../reference/index.md#finding-var-022), [VAR-023](../reference/index.md#finding-var-023), [VAR-024](../reference/index.md#finding-var-024), [VAR-025](../reference/index.md#finding-var-025), [VAR-026](../reference/index.md#finding-var-026), [VAR-027](../reference/index.md#finding-var-027), [VAR-028](../reference/index.md#finding-var-028), [VAR-029](../reference/index.md#finding-var-029), [VAR-030](../reference/index.md#finding-var-030), [VAR-031](../reference/index.md#finding-var-031), [VAR-032](../reference/index.md#finding-var-032), [VAR-033](../reference/index.md#finding-var-033), [VAR-034](../reference/index.md#finding-var-034), [VAR-035](../reference/index.md#finding-var-035), [VAR-036](../reference/index.md#finding-var-036), [VAR-037](../reference/index.md#finding-var-037), [VAR-038](../reference/index.md#finding-var-038), [VAR-040](../reference/index.md#finding-var-040)
- Corrections with this document as canonical home: [CORR-070](../reference/index.md#correction-corr-070), [CORR-073](../reference/index.md#correction-corr-073), [CORR-074](../reference/index.md#correction-corr-074), [CORR-075](../reference/index.md#correction-corr-075), [CORR-076](../reference/index.md#correction-corr-076), [CORR-077](../reference/index.md#correction-corr-077), [CORR-078](../reference/index.md#correction-corr-078), [CORR-105](../reference/index.md#correction-corr-105), [CORR-106](../reference/index.md#correction-corr-106), [CORR-107](../reference/index.md#correction-corr-107)
<!-- knowledge-cross-references:end -->
