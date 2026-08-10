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
- [ ] Step 5 — split the new 2023 US Corolla evidence from the existing
  `8965F1208000` variant and reconcile status/requests

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

- pending
