# RAV4 Prime forced SecOC profile — static interpretation of the 2026-08-10 field experiment

> **Scope:** pinned open-source Toyota SecOC controller/safety code, Techstream
> V18 diagnostic databases, and comparative `8965B4512000` firmware evidence
>
> **Vehicle field report:** 2024 RAV4 Prime, exact EPS F181 not yet captured in
> repository evidence
>
> **Status:** bounded; no RAV4 firmware or CAN capture is available yet
>
> **Evidence sources:** external-source (Discord field report), pinned-source,
> Techstream-static, firmware-static (Sienna comparison)

Recent comma `#toyota-security` discussion reported a live 2024 RAV4 Prime EPS
CodeFlash patch followed by an openpilot experiment that forced the existing
2021–23 RAV4 Prime SecOC profile, disabled openpilot longitudinal control, and
installed a dummy SecOC key. The car subsequently reported PCS/LKAS faults and
Techstream reported EPMS `U023A87`, rendered in the field report as lost
communication with Image Processing Module "A" / missing message.

The experiment is useful, but it does **not** isolate the EPS MAC predicate.
Pinned source shows that forcing the existing profile changes a larger camera
message boundary than a single SecOC steering frame.

## 1. What the forced 2021–23 profile selects

Pinned current opendbc defines `TOYOTA_RAV4_PRIME` as a
`ToyotaSecOCPlatformConfig` documented for **2021–23**. That configuration adds
`TSS2 | NO_DSU | SECOC` and selects the classic Toyota SecOC powertrain DBC.

The controller derives outbound freshness from the vehicle's live
`SECOC_SYNCHRONIZATION` state:

- `TRIP_CNT` and `RESET_CNT` come from the received `0x00F` message;
- reset-counter changes reset three local outbound message counters;
- the configured key is used to check the synchronization authenticator;
- a synchronization-MAC mismatch is logged as `wrong key?`, but that log does
  not itself abort the controller update.

Thus a dummy key does **not** imply arbitrary trip/reset freshness. It does mean
that every locally generated SecOC MAC is cryptographically wrong unless the
key happens to match, and it does not prove that a newer vehicle expects the
same per-message counter cadence.

## 2. Stock-longitudinal SecOC substitution set

For the reported experiment, longitudinal was disabled. Pinned Toyota safety
therefore selects the stock-longitudinal SecOC transmit set rather than the
openpilot-longitudinal set.

The relevant bus-0 messages are:

| CAN ID | Known name | Length | `check_relay` | openpilot role |
|---:|---|---:|---|---|
| `0x191` | `STEERING_LTA` | 8 | true | generated replacement |
| `0x412` | `LKAS_HUD` | 8 | true | generated replacement |
| `0x1D2` | PCM/cancel family | 8 | false | permitted output |
| `0x2E4` | `STEERING_LKA` | 8 | true | SecOC-signed replacement |
| `0x131` | `STEERING_LTA_2` | 8 | true | SecOC-signed replacement |
| `0x343` | ACC cancel family | 8 | false | permitted output |

`0x183 ACC_CONTROL_2` is added only for the SecOC **openpilot-longitudinal**
transmit set; it is not part of the reported stock-longitudinal substitution.

The generic Panda safety forwarder maps bus 0 ↔ bus 2 and, before forwarding,
blocks a stock frame if its address matches a destination-bus transmit entry
with `check_relay=true`. Toyota supplies no custom forward hook that reverses
this behavior.

Therefore, when this SecOC profile is active, camera-side bus-2 copies of at
least:

```text
0x191
0x412
0x2E4
0x131
```

are statically selected for **replacement**, not transparent forwarding.

This is the central interpretation change for the live experiment. It was not
merely "send a bad-MAC `0x2E4` to a patched EPS." It substituted the older
profile's camera steering/HUD message family across the harness boundary. A
2024 TSS3 network may differ in message presence, cadence, payload semantics,
or dependencies independently of the EPS SecOC acceptance predicate.

### 2.1 Exhaustive relevant-message matrix

The machine-readable source of truth is
`data/rav4_prime_forced_profile_matrix.csv`, verified by
`tests/verify_rav4_prime_forced_profile_matrix.py` plus pinned-source assertions.
It covers the complete relevant control/SecOC set rather than only the four
blocked camera messages:

| ID | stock bus2→0 | openpilot TX with stock longitudinal | cadence | SecOC | comparative receiver boundary |
|---:|---|---|---|---|---|
| `0x00F` | forwarded | none | — | synchronization consumed for TRIP/RESET | Sienna EPS sync input |
| `0x191` | **blocked/replaced** | yes | every 2 frames | no | Sienna EPS ordinary RX |
| `0x412` | **blocked/replaced** | yes | every 20 frames or UI edge | no | not recovered as Sienna EPS RX |
| `0x2E4` | **blocked/replaced** | yes | every frame | 28-bit CMAC | Sienna EPS protected RX |
| `0x131` | **blocked/replaced** | yes | every 2 frames | 28-bit CMAC | Sienna EPS protected RX |
| `0x343` | forwarded | cancel-only | on cancel | no | not Sienna EPS SecOC RX |
| `0x1D2` | forwarded | no on this RAV4 Prime branch | — | no | not Sienna EPS SecOC RX |
| `0x183` | forwarded | **no** with stock longitudinal | every 3 frames only with openpilot longitudinal | 28-bit CMAC when active | external receiving ECU; absent from Sienna EPS RX |
| `0x344` | forwarded | none | — | known classic SecOC vocabulary, no controller signing here | absent from Sienna EPS RX |
| `0x116` | forwarded | none | — | received by SecOC safety checks | external input |

RAV4 Prime's `ToyotaSecOCPlatformConfig` sets `TSS2 | NO_DSU | SECOC` but does
not add `UNSUPPORTED_DSU`. Therefore the stock-longitudinal cancel branch uses
`ACC_CONTROL` (`0x343`) rather than `PCM_CRUISE` (`0x1D2`), even though both
addresses are allowed by the safety whitelist.

The matrix also distinguishes **wire-shape conversion** from mere replacement:
classic non-SecOC Toyota uses 5-byte `0x2E4`, while the SecOC platform sends an
8-byte `0x2E4` containing the protected trailer. `0x131` is an additional
8-byte protected steering companion on the SecOC path. `0x183` is the third
signed stream in opendbc, but is absent from the longitudinal-disabled field
experiment.

This exhausts the relevant static forwarding/transmit boundary available from
the pinned source. Physical 2024 RAV4 ownership is not projected from the
comparative Sienna column; only the two steering protected IDs have direct EPS
receiver proof in the analyzed firmware.

## 3. `U023A87` in Toyota/firmware evidence

### 3.1 Techstream vocabulary

Techstream V18 uses base `U023A` across several P4-family ECU databases with
closely related labels:

- `EMPS_P4.ddb`: **Lost Communication with Front Camera Module**
- `EPS_CAN_P4DK.ddb`: **CAN communication error (SCM)**
- `AFS_P4.ddb`, `Front_Camera_P4.ddb`, `LDA_P4.ddb`, `PCS2_P4.ddb`, and others:
  **Lost Communication with Image Processing Module "A"**

The field report supplied the full `U023A87` code and the `Missing Message`
rendering. Techstream's P5 section-65 DTC/failure table now independently proves
that suffix: the record stores packed `0xC23A87` and resolves failure byte
`0x87` through `M_English` to **Missing Message**. Across the complete pinned P5
corpus, 1,519 failure-`0x87` records use the canonical `Missing Message` string
index and all 20 enabled `U023A87` records resolve to that text. `EMPS_P5.ddb`
contains the exact combination `Lost Communication with Image Processing Module
"A"` + `Missing Message`.

### 3.2 Exact `U023A87` exists in `8965B4512000`

The comparative Sienna firmware gives stronger structural evidence that the
suffix is meaningful to this EPS software family.

Its 0xA0-entry DTC table contains adjacent enabled records:

| DTC-table index | Address | failure type | base ID | full code |
|---:|---:|---:|---:|---|
| 92 | `0x30CBC` | `0x00` | `0xC23A` | `U023A` |
| 93 | `0x30CC4` | `0x87` | `0xC23A` | **`U023A87`** |

The generated Dem-event table at `0x2FDDC` links **no event directly to index
92**, while five configured events point specifically to index 93:

```text
0x0B0
0x0B3
0x138
0x13C
0x13D
```

The event records are:

```text
0x0B0 -> 42 00 5D 11 00 00 00 00
0x0B3 -> 42 00 5D 11 00 00 00 00
0x138 -> 43 00 5D 11 00 00 00 00
0x13C -> 43 00 5D 11 00 00 00 00
0x13D -> 43 00 5D 11 00 00 00 00
```

where byte 2 `0x5D` is DTC-table index 93. `FUN_00050f56` and
`FUN_00051268` independently establish that event-record byte 2 is the DTC
index used to aggregate/report diagnostic state.

This does **not** prove that the RAV4 Prime uses identical Dem event IDs or
identical PDU monitors. It establishes that `U023A87` is a concrete configured
failure subtype in the analyzed Denso EPS family rather than a UI-only suffix.

Four of the five Sienna event IDs can now be taken one step further through the
11-entry communication-monitor table at `0x28278`. Each table row carries a Dem
event ID at `+2` and an Rx-state selector at `+5`; the same selector is consumed
by `FUN_00048e4c`, and the corresponding COM unpackers bind it to concrete CAN
IDs:

| U023A87 Dem event | monitor row | Rx-state selector | unpacker | CAN ID |
|---:|---:|---:|---:|---:|
| `0xB0` | 6 | 0 | `0x4A244` | **`0x2E4`** |
| `0x138` | 8 | 7 | `0x4A5A2` | **`0x131`** |
| `0x13C` | 7 | 6 | `0x4A4BC` | **`0x191`** |
| `0x13D` | 9 | 8 | `0x4A68A` | **`0x2FD`** |
| `0xB3` | — | — | — | configured-unresolved |

This is a useful comparative Sienna result: U023A87 can be raised by missing
traffic in a group that includes both protected steering streams (`0x2E4`,
`0x131`), ordinary `0x191`, and `0x2FD`. It does **not** mean the 2024 RAV4 uses
identical event-to-PDU assignments. Event `0xB3` is configured for the same DTC
but is absent from this recovered monitor table; its specific reporter remains
bounded rather than guessed.

Machine-readable evidence:
`data/generated/u023a87_monitor_map.json`.

## 4. What the live failure does and does not show

The live result is compatible with at least two independent failure classes:

1. **EPS authentication failure:** the dummy-key `0x2E4`/`0x131` MACs are wrong,
   and the persistent patch may not bypass the exact gate assumed.
2. **Profile/network substitution failure:** activating the 2021–23 profile
   suppresses stock camera copies of `0x191/0x412/0x2E4/0x131` and replaces them
   with older-profile constructions. A newer TSS3 ECU may legitimately diagnose
   a missing/incompatible camera message even if the EPS accepts steering.

The observed `U023A87` cannot distinguish those classes by itself. It does make
profile/network mismatch a first-class explanation that must be controlled
before using the experiment as a test of the SecOC patch.

## 5. Static boundary before requesting artifacts

Already established without RAV4 files:

- exact old-profile substitution set for stock-longitudinal mode;
- live synchronization is consumed by the sender even with a dummy key;
- `0x183` is not part of the reported stock-longitudinal experiment;
- Toyota's own Techstream vocabulary associates base U023A with front-camera /
  image-processing communication loss;
- the exact `U023A87` subtype exists and is actively event-backed in the
  analyzed `8965B4512000` firmware.

Still artifact-blocked:

- which specific 2024 RAV4 messages differ from the old profile;
- which RAV4 ECU actually raised `U023A87` and which receive monitor caused it;
- whether the patched F4 predicate bypasses MAC only, combined packet validity,
  or some downstream acceptance predicate;
- whether a correctly preserved stock message set with an intentionally bad MAC
  is accepted after the patch.
