# 2023 US Corolla public route — SecOC traffic and topology evidence

> **Scope:** public comma route `a74eba85c97eaf67|00000004--555953f500`,
> discussed as a 2023 US Corolla in comma `#toyota-security`
>
> **Exact EPS F181:** unknown
>
> **Status:** route evidence recovered; DataFlash/F181 still artifact-blocked
>
> **Evidence source:** public logged route + pinned Panda/opendbc source +
> external Discord vehicle attribution
>
> **Machine-readable summary:**
> `data/generated/corolla_2023_public_route_summary.json`

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

## 5. Reinterpretation of the community `0 protected` result

The Discord report says the DataFlash workflow later produced a successful dump
but `0/30 protected` in its verification phase.

That result is now statically explained without needing the dump:

- current Bk2ol verification ignores Panda bus 1;
- it only treats `0x131`, `0x2E4`, and `0x344` as protected;
- the public route's genuine classic protected-family traffic is on bus 1 and
  uses `0x116`/`0x24D`;
- the apparent `0x2E4` is returned openpilot traffic, not a stock protected
  oracle.

Therefore `0 protected` is a **tool-profile false negative**, not evidence that
this Corolla lacks SecOC.

The repository-local generic oracle added in SECOC-032 is already prepared for
this exact capture shape.

## 6. What the public route does not contain

The route does **not** provide:

- the actual 32 KiB DataFlash dump reported in Discord;
- EPS F181 / exact calibration identity;
- a stock passive `carFw` inventory;
- a candidate key;
- cryptographic CMAC validation;
- CodeFlash;
- proof that synchronization, `0x116`, and `0x24D` share one key domain.

The route does, however, remove the need to request a separate CAN capture for
the basic SecOC-oracle question.

## 7. Narrow artifact request after static/public-route closure

For this specimen the highest-yield request is now only:

1. **the completed 32 KiB DataFlash dump** produced by the successful workflow;
2. **the exact EPS F181 response** (and secondary software ID if present);
3. optionally the setup state/output that records which logical/physical bus
   was used for the successful dump.

A new CAN capture is not required to test the DataFlash key hypothesis: the
public route already supplies substantial `0x00F` + `0x116` + `0x24D` oracle
traffic. If the dump arrives, `tools/toyota_secoc_oracle.py` can test every
sliding 16-byte DataFlash window against that classic traffic after export to
its NDJSON input format.
