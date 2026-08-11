# Discord static follow-up — 2026-08-10

Focused static-analysis sprint prompted by recent comma `#toyota-security`
discussion supplied as screenshots in the active research session. The
screenshots are **external-source observations**, not primary firmware evidence;
they are not archived as binary artifacts in this repository. This document
tracks what can be established from already pinned/local artifacts before
requesting new files from participants.

## Input observations to test, not assume

The screenshots report or discuss:

- a 2023 US Corolla route where genuine incoming SecOC-like traffic was
  identified on `0x00F`, `0x116`, and `0x24D`, while apparent steering traffic
  on `0x2E4`/`0x191` was later recognized as Panda-returned openpilot traffic;
- a successful 32 KiB Corolla EPS DataFlash dump after changing the physical
  CAN pair presented as Panda bus 0, followed by `0/30 protected` from the
  current extraction workflow;
- ordinary UDS responses when targeting the EPS on Panda bus 1 but programming
  timeout, versus successful programming after a physical CAN0/CAN1 harness
  pair swap and use of bus 0;
- persistent community EPS patch application on a live 2024 RAV4 Prime and
  2025 bZ4X, with the RAV4 Prime openpilot experiment later reporting
  `U023A87` / missing Image Processing Module message;
- concern that forcing an older RAV4/Corolla profile may itself be invalid for
  the newer TSS3 network regardless of SecOC bypass status.

No vehicle-specific conclusion is promoted from those screenshots alone.

## Step checklist

- [x] Step 1 — audit the current DataFlash/SecOC extractor and build a generic
  classic-Toyota offline oracle
- [x] Step 2 — statically resolve Panda ELM327/bus-routing assumptions and build
  a non-destructive bus-discovery plan/tool
- [x] Step 3 — statically audit the forced RAV4 Prime openpilot profile and
  decode the `U023A87` Techstream/firmware context
- [x] Step 4 — prepare an automated F3/F4 community patch-predicate analyzer
- [x] Step 5 — recover the public 2023-US-Corolla route, split it from the
  existing `8965F1208000` variant, and narrow the remaining artifact request

## Step 1 — community extractor and generic SecOC oracle

### Primary/pinned inputs

- `Bk2ol/tsk_extraction_by_can_log` at
  `db453752beeb7cdd024a1a9c38c6711c981e75ad`
- commaai/opendbc at `c9b31d21bc396e8958891e271936bdbdf1a6ca93`
- `opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc`
- `opendbc/car/secoc.py`
- repository firmware-derived classic SecOC construction

### Static findings

The Bk2ol workflow's **dump bootstrap** and its **post-dump oracle** have
separate portability boundaries. The current oracle is hardcoded to:

```text
collector buses:       {0, 2}
collector IDs:         {0x00F, 0x131, 0x2E4, 0x344}
protected verify IDs:  {0x131, 0x2E4, 0x344}
verify buses:          {0, 2}
EPS probe/dump bus:    0
```

Pinned opendbc defines the same classic 28-bit authenticator/reset/message-low2
trailer family on eight ordinary protected IDs:

```text
0x116  GAS_PEDAL
0x131  STEERING_LTA_2
0x177  PCM_CRUISE_3
0x183  ACC_CONTROL_2
0x24D  PCM_CRUISE_4
0x283  PRE_COLLISION
0x2E4  STEERING_LKA
0x344  PRE_COLLISION_2
```

with `0x00F` synchronization.

Therefore a literal `0 protected` result from the unmodified Bk2ol verifier
means only that no samples from **its three protected IDs on its two accepted
buses** reached verification. It cannot establish that another variant has no
SecOC traffic.

### Durable work

Added:

- `data/toyota_classic_secoc_profile.csv`
- `tools/toyota_secoc_oracle.py`
- `tests/verify_toyota_secoc_oracle.py`
- `docs/tooling/community-dataflash-secoc.md`

The local oracle tracks synchronization per arbitrary bus, recognizes the full
pinned classic profile, verifies each observed protected ID independently, and
sliding-scans 16-byte DataFlash windows after a sync-CMAC prefilter. Synthetic
coverage deliberately uses bus 1 and `0x116`/`0x24D`.

### Verification

- `tests/verify_toyota_secoc_oracle.py` — 37/37 pass
- optional pinned-source `verify_external_corroboration.py` — 222/222 pass
- finding: `SECOC-032`

### Boundary

The tool is now ready to process a future Corolla dump/capture, but no Corolla
key/storage conclusion is possible without those artifacts. The eight-ID DBC
profile is a known Toyota classic-SecOC vocabulary, not proof that every listed
ID appears on the 2023 Corolla or shares one production key.

### Commit

- `64f582f9426cc4095aa6e278035fc32c4738d1b1 analysis: generalize Toyota SecOC offline oracle`

## Step 2 — Panda ELM327 and Toyota diagnostic bus routing

### Primary/pinned inputs

- Calvin Park openpilot/Panda checkout at
  `eeb87f4f9cbcba2ee9c358c8d93015a513c1f822`
- `panda/board/main.c`
- `panda/board/boards/tres.h`
- `panda/board/drivers/can_common.h`
- `opendbc_repo/opendbc/safety/modes/elm327.h`
- Bk2ol probe/dump source from Step 1

### Static findings

Pinned safety/Panda source establishes:

```text
ELM327 param 0     -> CAN_MODE_OBD_CAN2
                    -> logical bus 1 multiplexed to OBD-II CAN
ELM327 param != 0  -> CAN_MODE_NORMAL
harness flipped    -> logical bus 0/2 orientation swaps
logical bus 1      -> remains MCU CAN2
```

Tres/Red board code additionally shows that `CAN_MODE_NORMAL` versus
`CAN_MODE_OBD_CAN2` changes the physical FDCAN2 pin/transceiver selection. The
current Bk2ol dumper combines implicit ELM327 parameter 0 with hardcoded logical
bus 0; changing only its `BUS` constant does not keep the physical-routing
context fixed.

This is enough to reject a premature conclusion that the observed bus-1
programming timeout is necessarily ECU behavior. It is **not** enough to prove
that software configuration can replace the physical repin, because live ACK,
reset, gateway, and harness behavior remain unmeasured.

### Durable work

Added:

- `docs/tooling/panda-toyota-routing.md`
- `tools/toyota_eps_bus_probe.py`
- `tests/verify_toyota_eps_bus_probe.py`

The probe defaults to a dry run. With explicit `--execute`, it selects ELM327
parameter 1 (normal routing) and sends only `22 F1 81` to `0x7A1 -> 0x7A9` on
logical buses 0/1/2. It never enters programming, requests SecurityAccess,
writes a DID, downloads code, starts a routine, or resets the ECU.

### Verification

- `tests/verify_toyota_eps_bus_probe.py` — 17/17 pass
- optional pinned-source `verify_external_corroboration.py` — 247/247 pass;
  locks Panda ELM327, CAN orientation, Tres mux, and Bk2ol call-site semantics
- finding: `SECOC-033`

### Boundary

The next live routing experiment can now be a read-only `(ELM327 param, logical
bus) -> F181 response` matrix rather than another harness repin. Programming
behavior should only be retested after the physical/logical route is known.

### Commit

- `cafcf32e04f3de04dde4133027e8c2bd2fa28505 analysis: resolve Panda Toyota diagnostic routing`

## Step 3 — forced RAV4 Prime profile and U023A87

### Primary/pinned inputs

- current pinned opendbc Toyota SecOC platform/controller/DBC sources
- Calvin Park pinned Toyota safety and generic Panda safety forwarding sources
- Techstream V18 P4-family DDB corpus
- `8965B4512000` DTC table and generated Dem-event table

### Static findings

The existing `TOYOTA_RAV4_PRIME` profile is explicitly the 2021–23 SecOC
platform. With stock longitudinal, Toyota safety authorizes generated bus-0
messages `0x191`, `0x412`, `0x2E4`, and `0x131` with `check_relay=true`.
Generic Panda bus-2→0 forwarding blocks stock frames whose address matches such
a destination transmit entry. Toyota has no custom forward hook that undoes
that behavior. Therefore forcing this profile substitutes an old camera
steering/HUD message family; it is not a single `0x2E4` MAC experiment.

`0x183 ACC_CONTROL_2` belongs to the SecOC openpilot-longitudinal transmit set,
not the reported stock-longitudinal experiment. The sender still derives
TRIP/RESET state from the live `0x00F` synchronization frame even when the
configured key is wrong; the dummy key invalidates the generated MACs but does
not make trip/reset freshness arbitrary.

Techstream uses base U023A for front-camera/image-processing communication loss
across P4-family databases. More importantly, the analyzed Sienna firmware
itself contains adjacent enabled records:

```text
DTC index 92 @ 0x30CBC: failure type 00, base C23A -> U023A
DTC index 93 @ 0x30CC4: failure type 87, base C23A -> U023A87
```

The generated 0x180-entry Dem-event table maps no configured event directly to
index 92. Five events map specifically to index 93:

```text
0xB0, 0xB3, 0x138, 0x13C, 0x13D
```

`FUN_00050f56` and `FUN_00051268` independently establish that event-record
byte 2 selects the DTC-table index. The exact event-to-PDU meanings remain
unresolved.

The diagnostic vocabulary generator previously collapsed byte 0 as an opaque
flag. It now preserves `failure_type`, emits full subtype names such as
`U023A87`, and follows Dem-event links.

### Durable work

- `docs/variants/rav4-prime-forced-secoc-profile.md`
- failure-type/Dem-event support in `tools/diagnostics/correlate_vocabulary.py`
- regenerated `diagnostic_vocabulary.json`
- expanded `verify_diagnostic_vocabulary.py`
- pinned source assertions for the forced-profile substitution boundary
- finding: `SECOC-034`

### Verification

- `tests/verify_diagnostic_vocabulary.py` — 243/243 pass
- optional pinned-source `verify_external_corroboration.py` — 264/264 pass

### Boundary

The reported RAV4 `U023A87` is compatible with a profile/network substitution
failure independently of EPS MAC acceptance. Without that vehicle's firmware or
capture, it cannot identify the actual missing RAV4 message or prove/disprove
the persistent patch's MAC behavior.

### Commit

- `aec04e7cb0aea77f006cfb508645228c17b42e0b analysis: explain forced-profile U023A87 failure`

## Step 4 — future F3/F4 patch-target analyzer

### Static/tooling result

The community egg remains a location signature only. A raw triage tool now
reports every egg occurrence, bounded context, image identity, and the exact
`01 52 7F 00` immediate-success replacement, but deliberately refuses to infer
function ownership or callers from raw halfwords.

That boundary was validated during implementation: a naive short-JARL scan of
the Sienna bytes produced 11 apparent candidates, while Ghidra's
instruction-aware reference manager proves exactly two real call references to
`0x3485A`. Raw callsite attribution was therefore removed rather than retained
as weak evidence.

The companion read-only Ghidra script reports the containing function, true
callers/callees, direct `0xFFC5D000..0xFFC5D0FF` ICU-S references, and a full
decompilation. Against `4512000` it reproduces the known false-positive result:

```text
FUN_0003485a @ 0x3485A
callers: FUN_00034882, application_proprietary_ab_f1_start
callees: 0
direct ICU-S refs: 0
```

### Durable work

- `tools/analyze_secoc_patch_target.py`
- `ghidra/scripts/investigate/AnalyzeCommunityPatchTarget.java`
- `data/generated/community_patch_target_4512000.json`
- `tests/verify_community_patch_target_analyzer.py`
- `docs/tooling/community-patch-target-analysis.md`
- finding: `SECOC-035`

### Verification

- raw/tool contract verifier — 27/27 pass
- Ghidra Java script compiles successfully
- Ghidra execution on the known Sienna target reports exactly two callers and
  zero direct ICU-S refs

### Boundary

The F3/F4 semantic question is now reduced to a missing-image blocker. Once a
CodeFlash image arrives, raw target discovery and instruction-aware semantic
triage can be run immediately without inventing meaning from the egg.

### Commit

- `331d5aa41441d3134cdece52b9a2cf5a605a9278 analysis: prepare F3 F4 patch target triage`

## Step 5 — public 2023 US Corolla route

### Public source recovered

The route ID posted in the Discord discussion is still public:

```text
a74eba85c97eaf67|00000004--555953f500
```

The route API exposed 29 qlogs and 29 rlogs. All 29 qlog hashes and one full
segment-0 rlog hash are pinned in `external-references.lock.json`; expiring
signed download URLs are intentionally not retained.

The route's own `initData` identifies the generating software as sunnypilot
`2026.002.001`, branch `release-mici`, commit
`af744c85e7c971e7bfbc8e6ee9e2bd75452a6f00`.

### Metadata boundary

The active and persistent `carParams` are deliberately forced:

```text
carFingerprint = TOYOTA_COROLLA_TSS2
fingerprintSource = fixed
carFw = []
VIN = placeholder zeros
secOcRequired = false
secOcKeyAvailable = false
```

The previous-route CarParams is `MOCK`, also with no firmware inventory. The
route therefore cannot identify the physical EPS F181/calibration or
independently prove the Discord-reported model year.

### Genuine versus returned CAN traffic

Full segment-0 rlog analysis recovers genuine bus-1 traffic:

```text
0x00F  DLC8   588 frames
0x116  DLC8  2499 frames
0x24D  DLC8    59 frames
```

and genuine 64-byte CAN-FD `0x183` traffic on buses 0 and 2. The 64-byte DLC is
itself a discriminator from the classic 8-byte `ACC_CONTROL_2` definition.

Apparent steering traffic is instead predominantly Panda-returned output:

```text
sendcan bus0 0x191 DLC8   2519
returned src128 0x191     2512
rejected src192 0x191        6

sendcan bus0 0x2E4 DLC5   5037
returned src128 0x2E4     5025
rejected src192 0x2E4       11
```

Pinned pandad source defines returned source offset `0x80` and rejected offset
`0xC0`, so these are not stock camera frames. No genuine incoming classic
`0x131` or `0x2E4` is claimed by the pinned segment summary.

### Classic SecOC structural check

Pinned opendbc already classifies `0x116` and `0x24D` as classic Toyota
protected messages. Relative to the latest bus-1 `0x00F` reset state, the
transmitted trailer reset-low2 bits align on:

```text
0x116: 2476 / 2496 eligible frames (>99%)
0x24D:   59 /   59 eligible frames
```

This is structural freshness evidence, not cryptographic key proof.

### Consequence for the reported `0 protected`

The public route plus Step 1 closes the interpretation: the current Bk2ol
verifier ignores bus 1 and only recognizes `0x131/0x2E4/0x344` as protected,
while this route's genuine classic protected-family traffic is bus-1
`0x116/0x24D`. The reported `0 protected` is therefore a tool-profile false
negative, not evidence of SecOC absence.

### Durable work

- `data/generated/corolla_2023_public_route_summary.json`
- route/hash provenance in `external-references.lock.json`
- `tests/verify_corolla_2023_public_route_summary.py`
- `docs/variants/corolla-2023-us-public-route.md`
- explicit cross-specimen warning in `corolla-8965F1208000.md`
- pinned pandad returned/rejected source semantics
- finding: `VAR-004`
- updated open questions and roadmap

### Narrow remaining request

A separate CAN capture is no longer necessary for the basic key-oracle test.
The remaining high-value ask is only:

1. the already-reported completed 32 KiB DataFlash dump;
2. the exact EPS `F181` response / software identity;
3. optionally the setup state recording the successful diagnostic bus route.

The generic oracle from Step 1 is ready to test the dump immediately against
public `0x00F/0x116/0x24D` traffic once the capture is exported to its NDJSON
input format.

### Commit

- `614123e671c3664b8e7b2fd685dba9d9c453c6b4 analysis: recover 2023 Corolla public route evidence`

## Final static closure

All five Discord-derived static stages are complete. The remaining questions
are now cleanly separated into missing-artifact or live-behavior boundaries:

- 2023-US-Corolla key/storage result: needs the already-produced 32 KiB
  DataFlash dump; the CAN oracle is public and already recovered.
- 2023-US-Corolla physical calibration identity: needs exact EPS `F181`.
- F3/F4 persistent-patch predicate semantics: needs one F3/F4 CodeFlash image;
  pre/post patch are both usable because the original egg bytes are known.
- Toyota-B physical-repin replacement: needs one read-only live routing matrix
  using the prepared F181 probe before any programming-session test.
- RAV4 Prime patch efficacy versus profile mismatch: needs a controlled live
  test or vehicle capture after preserving the stock/new-TSS3 message set; the
  old-profile substitution confounder is now statically established.

Final repository verification before closure: `make verify` = **440 assertions,
0 failures**. The interrupted ptshim Stage-3 files remain untracked and
untouched for the original `/goal` continuation.

# Original-eight completion pass

A later audit against the original eight-item static plan found four scopes that
needed further closure. This section records that completion work without
redefining the original goal.

## Completion A — explicit cross-variant TSK/SecOC session (original item 1)

The earlier work generalized the offline cryptographic oracle but did not make
all workflow assumptions durable. `tools/toyota_secoc_session.py` now records:

- EPS endpoint;
- diagnostic bus (`auto` until the read-only F181 probe resolves it);
- explicit ELM327 routing parameter, defaulting to normal routing;
- oracle buses 0/1/2;
- the complete configurable classic protected-ID profile;
- target car for fingerprint review;
- F181 identity;
- per-bus/per-ID capture counts.

It consumes `toyota_eps_bus_probe.py --execute` output, fails closed when more
than one F181 responder exists unless explicitly disambiguated, filters a full
capture without dropping bus 1 or `0x116/0x24D`, and produces a review-only
fingerprint plan plus an offline oracle command. It contains no ECU-mutating
UDS/Panda operation.

- focused verification: `verify_toyota_secoc_session.py` — 33/33 pass
- finding: `SECOC-036`
- commit: `063edd29238514002c9dfd17b8c33499f71ef4a3 analysis: make Toyota SecOC session assumptions explicit`

## Completion B — exhaustive forced RAV4 Prime message matrix (original item 4)

`data/rav4_prime_forced_profile_matrix.csv` now records the complete relevant
message boundary for the reported 2021–23 RAV4 Prime SecOC profile with
longitudinal disabled: stock forwarding, replacement, controller transmit
cadence, SecOC treatment, and comparative receiver ownership.

The exact camera replacement set is `0x191/0x412/0x2E4/0x131`. Only the two
steering SecOC messages are CMAC-signed in this configuration; `0x183` is signed
only when openpilot longitudinal is enabled. RAV4 Prime lacks `UNSUPPORTED_DSU`,
so cancel selects `0x343 ACC_CONTROL` rather than `0x1D2 PCM_CRUISE`. `0x344`
is forwarded and not generated by this controller path.

Comparative `4512000` evidence is kept explicitly separate: `0x2E4/0x131` are
protected EPS RX, `0x191` is ordinary EPS RX, while `0x183/0x344/0x412` are
absent from the application RX map. No 2024-RAV4 physical ownership is inferred
from those Sienna facts.

- finding: `SECOC-037`
- commit: `261eae6ed01a99db15b8c7b7694085f9518ed18e analysis: complete RAV4 Prime forced profile matrix`

## Completion C — Techstream `0x87` semantics and U023A87 monitor context (original item 5)

Techstream's P5 section type 65 is now decoded as a 68-byte DTC/failure table.
The recovered fields include full UTF-16 DTC code, packed base+failure byte,
base-description string index, failure-description string index, and enabled
word. Scanning all 131 P5 databases with that record shape proves:

```text
0x81 -> Invalid Serial Data Received
0x82 -> Alive / Sequence Counter Incorrect / Not Updated
0x83 -> Value of Signal Protection Calculation Incorrect
0x84 -> Signal Below Allowable Range
0x85 -> Signal Above Allowable Range
0x86 -> Signal Invalid
0x87 -> Missing Message
0x88 -> Bus Off
```

For `0x87`, 1,519 records use the canonical `M_English` index 64829 = `Missing
Message`; all 20 nonzero-tail `U023A87` P5 records resolve to Missing Message.
No pinned consumer proves the `+0x40` tail word is an enable flag. The
exact `EMPS_P5` row combines `Lost Communication with Image Processing Module
"A"` with `Missing Message`, so the field-reported suffix is now statically
proved by Techstream rather than inherited from the screenshot.

The comparative Sienna firmware can also map four of its five U023A87 events to
specific missing receive monitors through the 11-entry table at `0x28278`:

```text
0xB0  -> Rx selector 0 -> unpacker 0x4A244 -> CAN 0x2E4
0x138 -> Rx selector 7 -> unpacker 0x4A5A2 -> CAN 0x131
0x13C -> Rx selector 6 -> unpacker 0x4A4BC -> CAN 0x191
0x13D -> Rx selector 8 -> unpacker 0x4A68A -> CAN 0x2FD
0xB3  -> configured for U023A87 but absent from this monitor table
```

The direct/thunk reporter census did not yield a defensible static PDU identity
for `0xB3`, so it remains explicitly configured-unresolved rather than guessed.
These are `4512000` monitor assignments and are not projected onto the 2024
RAV4.

Durable outputs:

- `data/generated/techstream_v18/dtc_failure_types.json`
- `data/generated/u023a87_monitor_map.json`
- `generate_dtc_failure_types.py`
- `generate_u023a87_monitor_map.py`
- failure-entry support in `parse_ddb.py`
- focused verifiers for both artifacts
- finding `TMS-015`

Commit: `4aa492e7a9b5e38ebf7c7d3cade647849adc643b analysis: resolve Techstream U023A87 semantics`

## Completion D — full Corolla/DataFlash structural and key-domain analyzer (original item 7)

`tools/analyze_toyota_dataflash.py` now closes the remaining pre-artifact
DataFlash work:

- ranks every sliding 16-byte window, not only aligned candidates;
- uses the generated physical NvM record map to evaluate the proved validity
  rule (storage-index header + `AAAAAAAA` trailer);
- retains the second physical header word as opaque because its checksum/CRC
  semantics remain unproved;
- decodes every enabled raw/XOR55/XORAA triplicate object and reports physical
  validity, decoded-copy agreement, majority consensus, and valid-copy
  consensus;
- makes the complete object-15 geometry explicit (`FF206E14`, `FF206D14`,
  `FF206C14`, restored `FEBF02F8`) and records alignment with the related
  `4514000` field without claiming runtime equivalence;
- can independently scan every unique high-entropy 16-byte window against sync
  and each protected CAN ID rather than requiring one universal key;
- emits explicit classifications including `sync only`, `0x116 only`, `0x24D
  only`, shared `0x116+0x24D`, and shared `sync+protected`;
- reports only candidate hashes/addresses, not raw key bytes.

The committed `4512000` reference artifact reproduces six valid triplicate
consensuses (`0/1/2/3/5/6`) and zero valid copies for `4/12/13/14/15`. A
synthetic provisioned object 15 proves correct raw/XOR55/XORAA reconstruction,
and synthetic captures prove all requested independent/shared key-domain
classifications.

The public Corolla route already supplies `0x00F/0x116/0x24D`, so the initial
Corolla key/storage experiment is now reduced to the missing 32 KiB DataFlash
artifact plus F181 identity; another CAN capture is unnecessary.

- focused verification: `verify_toyota_dataflash_analyzer.py` — 35/35 pass
- finding: `SECOC-038`
- commit: `015d79f692708da329fb619206910e8642862bde analysis: complete Toyota DataFlash domain analyzer`

## Literal original-eight reconciliation

The original eight-item plan is now closed at the static/offline boundary:

| # | Original scope | Final static status | Remaining non-static/artifact boundary |
|---:|---|---|---|
| 1 | Generalize TSK extraction assumptions | **Complete for repository-local static/read-only/offline research:** bus auto-discovery is read-only, diagnostic bus/ELM routing/profile/target identity are durable session properties, all-bus/all-ID capture ingestion is generic, fingerprint handling is review-only, and the generic oracle consumes the result | The external community tool's programming/download implementation remains external rather than being automatically rewritten by this repository |
| 2 | Generic Toyota classic-SecOC oracle | **Complete**: full pinned eight-ID classic profile + `0x00F`, arbitrary buses, independent sync/per-ID verification, all-window scan | Actual vehicle key result needs dump/capture material |
| 3 | Toyota-B bus/pin-swap software side | **Complete statically**: ELM327 param-0 OBD-CAN2 mux, normal-routing alternative, bus0/2 harness orientation, and read-only F181 discovery are recovered/tested | Whether software routing fully eliminates physical repinning needs one live read-only routing matrix |
| 4 | Forced RAV4 Prime profile audit | **Complete statically**: exhaustive receive/forward/replace/transmit/cadence/SecOC/comparative-receiver matrix | 2024 RAV4 physical message ownership/actual fault cause needs its capture/firmware or a controlled live test |
| 5 | Techstream `U023A87` | **Complete to a bounded residual**: P5 corpus proves `0x87 = Missing Message`; four of five comparative Sienna U023A87 events map to concrete CAN monitors (`2E4/131/191/2FD`) | Sienna event `0xB3` remains configured-unresolved; 2024 RAV4 event assignments cannot be inferred from Sienna |
| 6 | F3/F4 patch predicate preparation | **Complete pre-acquisition**: raw egg triage + instruction-aware Ghidra target/caller/callee/ICU-S classification; known Sienna false positive is pinned | Exact F3/F4 predicate needs one F3/F4 CodeFlash image |
| 7 | Corolla DataFlash analysis pipeline | **Complete pre-acquisition**: every sliding window, entropy ranking, known NvM validity, raw/XOR55/XORAA redundancy/consensus, object-15 geometry, independent sync/per-ID domain scan and requested classification states | Actual Corolla storage/key conclusion needs the already-produced 32 KiB dump |
| 8 | Corolla variant model | **Complete**: 2023-US public-route specimen is separate from `8965F1208000`; public route itself is recovered/pinned, genuine vs returned traffic is resolved, and requests are narrowed | Exact physical calibration still needs F181 |

The only intentionally bounded item inside the static corpus itself is event
`0xB3`; its DTC association is proved but no defensible event-to-PDU reporter
was recovered after direct, thunked, variable-argument, and communication-table
censuses. It remains unresolved rather than receiving a guessed CAN identity.

The full repository gate after all analytical stages is `make verify` = **448
assertions, 0 failures**. The Ghidra daemon is stopped and the committed project
snapshot is unchanged. The three interrupted ptshim Stage-3 paths remain the
only untracked files and were not modified by this completion pass.
