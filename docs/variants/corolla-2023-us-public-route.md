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

## 8. Remaining evidence boundary

The new corpus closes CodeFlash identity and much of the firmware-static
transfer question, but it still does **not** provide:

- a direct UDS `F181` transcript from the same acquisition;
- a stock passive `carFw` inventory joining the public route to the firmware;
- proof of where the `0x00F` / `0x0D7` / `0x0B6` runtime authentication keys are
  stored or derived;
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
