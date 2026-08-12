# 2023 US Corolla public route — SecOC traffic and topology evidence

> **Scope:** public comma route `a74eba85c97eaf67|00000004--555953f500`,
> discussed as a 2023 US Corolla in comma `#toyota-security`
>
> **Exact EPS F181:** unknown
>
> **Status:** route evidence recovered; contributor DataFlash + TSKM oracle acquired;
> F181/CodeFlash still artifact-blocked
>
> **Evidence source:** public logged route + pinned Panda/opendbc source +
> contributor-supplied TSKM artifacts + external Discord vehicle attribution
>
> **Machine-readable summaries:**
> `data/generated/corolla_2023_public_route_summary.json` and
> `data/generated/corolla_2023_albino_dataflash_analysis.json`

This specimen must remain separate from the earlier
[`8965F1208000`](corolla-8965F1208000.md) Corolla investigation. The earlier
variant has an exact application software ID from direct field probing. This
public route does **not**: its logged software was deliberately forced to an old
`TOYOTA_COROLLA_TSS2` fingerprint and contains no `carFw` inventory.

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

**Consequence:** the route cannot independently prove that the physical car was
a 2023 model or identify its EPS calibration. The 2023-US attribution remains
an external field statement until F181 or another ECU identity artifact is
obtained.

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

## 7. Remaining evidence boundary

The public route and supplied DataFlash still do **not** provide:

- EPS F181 / exact calibration identity;
- a stock passive `carFw` inventory;
- CodeFlash;
- proof of where the synchronization or protected-message key is actually
  stored/derived;
- proof that this reported 2023-US specimen is architecturally identical to the
  separately probed `8965F1208000` Corolla.

The vehicle attribution therefore remains external until F181 is obtained.

## 8. Narrow artifact request after DataFlash closure

For this specimen the existing artifacts are substantially analyzed, but the
cross-session boundary reopens one narrow dynamic request. Highest-yield next
evidence is:

1. **the exact EPS F181 response** (and secondary software ID if present);
2. **CodeFlash**, if a safe/reliable acquisition path becomes available;
3. if the vehicle is revisited, a **controlled paired capture around the dump**:
   full-bus synchronization/protected CAN immediately before the programming
   transition, then repeat after recovery/reset and retain the resulting
   DataFlash dump plus exact `F181`.

The existing local TSKM oracle is useful but was collected as a separate job.
A controlled paired recapture would establish whether synchronization and
protected keys survive the programming/reset transition instead of assuming
runtime-key continuity. An unrelated additional CAN capture would not close
that boundary.
