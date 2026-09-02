# 2026-09-02 Camry F33 B6 review context

This document is a context packet for an independent review of the current
`8965F3307000` protected-B6 work. It is intentionally descriptive rather than a
canonical conclusion. Re-check claims against the exact firmware, raw captures,
and tracked verification artifacts rather than treating this note as evidence.

## Reviewer task

Independently review the current model of the exact-F33 `0x0B6` receive path and
the RAM observer/bridge experiments. In particular, look for:

- code or data-flow missed because of incorrect Ghidra function boundaries;
- fall-through code, jump-table targets, callbacks, indirect calls, table fields,
  interrupt/foreground interactions, or cleanup paths that are not represented
  in the current receive-path model;
- an incorrect interpretation of a profile/route/configuration table field;
- a receive-path condition imposed before SecOC profile-2 queueing;
- a way for B6 to enter and leave the relevant queue between the observer's
  sample points;
- a mismatch between the actual CAN-FD frame emitted by Panda and the exact F33
  CanIf/RSCFD receive contract;
- a mismatch in the current B6 application/freshness construction that could
  matter before or after protected-PDU delivery;
- a problem with the observer itself: scheduler placement, retained-RAM
  assumptions, sampled addresses, telemetry lifetime, or the act of observing
  changing the path;
- a missing downstream state worth sampling before another live test.

Do not assume that the current static pipeline reconstruction or the proposed
next experiment is correct merely because it is documented below.

## Repository state at handoff preparation

Repository:

```text
/Users/kai/dev/inspect/repos/ghidra_rh850_analysis
```

Context was prepared from:

```text
b26b29d camry: add F33 B6 transaction observer
c6be66b camry: close F33 B6 receive pipeline
1513e95 camry: audit route 37 B6 construction
87bf2a1 camry: document route 37 steering state
c16002e camry: package F33 Gate-2 stage 2
```

The tree was clean before this handoff file was added.

Read `AGENTS.md` before making changes. For firmware questions, use the exact
Camry target and firmware bytes rather than narrative docs as the primary
source. The registered target tooling includes `tools/gcamry` /
`tools/gtarget camry-8965F3307000 ...`.

## Vehicle / hardware context

Vehicle under test:

```text
2026 Toyota Camry Hybrid
TSS 3.x / P5 architecture
Comma 4
Toyota B harness, manually repinned
```

Current post-repin topology used by the B6 work:

```text
EPS diagnostics: 0x7A1 -> 0x7A9 on Panda bus 0
B6 transmit:     0x0B6, CAN-FD, 32 bytes, Panda bus 0
0x08A native:    camera/upstream side, Panda bus 2, forwarded toward bus 0
0x081 native:    chassis side, Panda bus 0, forwarded toward bus 2
relay pair:      Panda CAN0 <-> CAN2
CAN1:            not split by the current harness
```

Exact EPS F181 payload:

```text
023839363546333330373030300000000038413331313333303331303000000000
```

which is:

```text
02 || 8965F3307000 || 8A3113303100
```

Exact stock CodeFlash:

```text
firmware/camry-8965F3307000/CodeFlash.bin
SHA-256 42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7
```

## Current persisted development firmware state

The physical EPS currently has the cumulative stage-5 development image
persisted. Post-reboot verification observed the expected patched bytes and CRC
state.

Current image identity:

```text
SHA-256 669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af
CRC prefix 0x1960380A
CRC fixup  0xE69FC7F5
CRC residue 0xFFFFFFFF
```

Cumulative persistent edits:

| stage | address | original | replacement | purpose of experiment |
|---|---:|---|---|---|
| 1 | `0x8F952` | `E0 D1` | `E0 01` | neutralize final comparison in `FUN_8F906` |
| 2 | `0x8F948` | `1A 38` | `00 3A` | force zero callback/result argument in `FUN_8F906` |
| 3 | `0x8F930` | `E1 0F 14 D3` | `E0 07 14 D3` | force materialized `FEBE5564 != 0` boolean to zero |
| 4 | `0x8F7E6` | `0A D8` | `00 DA` | force profile-2 freshness-callback result in `r27` to zero |
| 5 | `0x8F890` | `E0 51` | `E0 01` | make the command-7 result comparison take the zero-result branch |

Deterministic cumulative image identities:

```text
stock   42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7
stage 1 272843a2c1d179f91105d7f103f213034f850dc476c96dad48067fbf3afd9f65
stage 2 6a371a2a17641ee5408777f06d303e34699d65dbde01e94cf89ffece7578d59c
stage 3 67f4aaa803f9f3df3e5b2bf31d2c8950ebbb3870fa3f5d439f585caae3a8313c
stage 4 2e2f0819ab328b8733c604eee3952ba4f774e4344a60184b7eea99927236640e
stage 5 669cedf8c8465ebfd02318cb7708b897b817bc3b40925c89743b64ce49aa01af
```

Builders/tests:

```text
tools/build_camry_f33_gate2_semantic_patch.py
tools/build_camry_f33_gate2_root_result_patch.py
tools/build_camry_f33_freshness_result_patch.py
tools/build_camry_f33_crypto_result_patch.py

tests/verify_camry_f33_gate2_root_result_patch.py
tests/verify_camry_f33_freshness_result_patch.py
tests/verify_camry_f33_crypto_result_patch.py
```

Programming-session entry succeeded in NRTD during the field work and returned
NRC `0x22` in READY. Persistent patch preflight/APPLY/post-reboot verification
was therefore performed in NRTD; B6 behavior tests were performed separately
in READY/Park/stationary.

## Live persistent-patch experiment chronology

### Stage 1

The installed image had only `0x8F952=E001` relative to stock.

READY/Park/zero-wheel-speed ID11/current-angle phase:

```text
85 B6 sends
85 Panda TX echoes
ADB0 = 0
AE90 = 64 while command target raw = 66
CB00 = 7
ADB9 = 0
CAFF = 1
ACBD = 0
probe verdict: payload_not_delivered
no steering offset run
```

Evidence:

```text
targets/camry-2026/raw-20260901/f33-b6-admission/
```

### Stage 2

`0x8F948 1A38 -> 003A` was added and stage 1 retained. NRTD preflight,
APPLY, and post-reboot persistence verification completed with stage-2 SHA and
CRC state matching the deterministic package.

READY/Park/zero-wheel-speed ID11 phase:

```text
84 sends / 84 echoes
ADB0 = 0
CB00 = 7
ADB9 = 0
CAFF = 1
ACBD = 0
no steering offset run
```

Evidence:

```text
targets/camry-2026/raw-20260901/f33-gate2-stage2/
```

### Stage 3

`0x8F930 E10F14D3 -> E00714D3` was added and persisted with exact stage-3
SHA/CRC state.

In READY/Park, ID11 did not replace the direct generated-COM B6 values:

```text
FEBE80BC remained ID0
FEBE80B8 remained the prior current-angle payload
```

A separate authority-isolation test opened the CAN0/CAN2 relay and disabled
automatic forwarding for the short B6 phase. The same direct-COM result was
observed. The isolation run sent 41 B6 frames and observed 41 Panda echoes.

Evidence includes:

```text
targets/camry-2026/raw-20260901/f33-gate2-stage3/
```

One retained clean stage-3 READY admission file pair is:

```text
targets/camry-2026/raw-20260901/f33-gate2-stage3/ready-admission/
  camry-f33-b6-stage3-ready-admission.ndjson
  camry-f33-b6-stage3-ready-admission.txt
```

### Stage 4

`0x8F7E6 0AD8 -> 00DA` was added to force the freshness-callback result
status used by the `8F746` dispatcher to zero. The callback still executes.
Stage 4 was applied and post-reboot verified as:

```text
SHA-256 2e2f0819ab328b8733c604eee3952ba4f774e4344a60184b7eea99927236640e
CRC prefix 0x7029A5F8
fixup 0x8FD65A07
residue 0xFFFFFFFF
```

The subsequent READY/Park ID11 test still did not replace direct COM
`FEBE80BC/FEBE80B8` with the transmitted ID11/current-angle payload.

### Stage 5

`0x8F890 E051 -> E001` was added. The stock sequence around the site is:

```text
8F88C  call FUN_8F676
8F890  cmp  r0,r10
8F892  be   8F8B6
```

The patch changes the comparison to `cmp r0,r0` while leaving the following
branch and native-success continuation intact.

Stage 5 was applied and post-reboot verified with the current SHA/CRC state
listed above. The following READY/Park ID11 test again left direct COM on the
prior ID0/current-angle values. No nonzero steering-offset phase was run.

## B6 wire/application context

Exact F33 has a protected B6 receive profile. Current recovered/configured
properties used by the sender/probes are:

```text
CAN ID             0x0B6
wire length         32 bytes CAN-FD
SecOC profile       index 2
PduR/application ID 44
application bytes   B0..B27
trailer              B28..B31
B28[7:4]             transmitted freshness nibble FV4
B28[3:0]+B29..B31    CMAC-MSB28
Target Lateral ID    B3 low 6 bits
Target angle         signed BE16 B4:B5
application sequence B7 low 6 bits
```

Target-angle scale used by the current sender:

```text
1024 / 17870 degrees per raw count
~= 0.057302742 deg/count
```

Target Lateral IDs recovered/observed in the F33 application bank mapping
include:

```text
1, 4, 10, 11, 18, 19
```

ID11 is the LTA/LCA bank used by the current openpilot candidate.

Current zero-MAC sender companion shapes:

```text
inactive: ID0,  B6=0x04, B8=0,   B9=0,   B10=0
active:   ID11, B6=0x00, B8=100, B9=100, B10=0
```

The current test sender deliberately sets the MAC28 bits to zero. The FV4 nibble
is populated from the sender's message-low2/reset-low2 state.

No native accepted F33 B6 transcript has been captured. The current active
companion bytes are derived from receiver/application semantics, not from a
stock B6 payload capture.

## Route 37 log used during this work

Exact path supplied by the operator:

```text
/Users/kai/dev/inspect/logs/camry-2026/2026-09-01/00000037--dec6fe39cb/
```

Seven rlogs are retained there.

B6 census from those rlogs:

```text
18,456 sendcan B6 frames
18,447 can/src=128 Panda successful TX echoes
9      can/src=192 reject-return records
0      native B6 on src=0/1/2
```

Therefore route 37 contains the openpilot-generated B6 corpus and its Panda TX
results, not a native stock B6 transcript.

The sender audit over all 18,456 route-37 B6 sends found:

```text
FV4 reset-low2 agrees with nearest native bus0 0x00F: 18,456 / 18,456
B7 application sequence +1 mod64:                   18,455 / 18,455
FV4 message-low2 +1 mod4:                           18,455 / 18,455
all 16 FV4 values occur
targets stay inside +/-1745 raw envelope
zero active-ID11 violations of 78*effective_gap target slew bound
```

Relevant note:

```text
docs/history/2026-09/2026-09-01-camry-route37-steering-speed-gate.md
```

Route 37 also contains periods where the vehicle's Toyota lateral request-plane
state (`0x08A` B21) is ID0 and periods where it is ID11. Those observations are
separate from B6 application admission. Exact F33 does not list `0x08A` in its
normal Rx descriptors/acceptance surface.

## Other Toyota lateral context relevant to review

Two retained stock-LTA drives contain machine-identified `0x08A` ID11 request
state with zero B6. Exact F33 also has a B6-inactive internal assist/current path.
Current project work therefore treats the stock Toyota lateral request plane and
B6 as separate interfaces; the exact stock chassis/arbitration handoff remains a
separate investigation.

Related current findings include VAR-087 through VAR-101 and OQ-054. Useful
starting points:

```text
docs/variants/camry-2026-live-baseline.md sections 38-47
docs/status/OPEN_QUESTIONS.md OQ-054
```

## Current reconstructed B6 receive path

The following is the current reconstruction to be independently checked.
Several relevant entry points were initially not promoted as functions by
Ghidra and were recovered by disassembling raw bytes from known table/call
targets.

### RSCFD / CanIf ingress

Current table joins:

```text
RSCFD controller-1 acceptance rule 39: 0x0B6
CanIf normal descriptor 39:             identifier field 0x400000B6
configured length:                      32
route-base value:                       5
5 + descriptor index 39:               PduR route 44
```

Reference rule comparison retained during the audit:

```text
rule 36 / 0x0D7: d700000000002d000200000000000000
rule 39 / 0x0B6: b6000000000030000200000000000000
```

The generic CanIf receive function recovered around `0x810F2` derives the route
and eventually dispatches a PduInfo to PduR.

Route44 has the generic Toyota checksum-hook flag, but the B6 row in the
checksum table has its per-route enable byte clear in the current decoding.
The all-frame CanIf checks include the configured FD/length constraints.

### PduR -> SecOC profile 2

Current reconstruction:

```text
CanIf/PduR route44
  -> 8EE7C
  -> 8F34A
  -> 8E9C6
  -> SecOC profile2 level-1 record
```

Important profile-2 RAM:

```text
queue record / length  FEBE547A
secured 32-byte buffer FEBE54D4
```

Current recovered ROM profile/table data include:

```text
secured length       32
buffer displacement  40
mode/trailer config  2
application route    44
freshness callback   0x903A0
post-verify callback 0x90448
other callback field 0x6A218
```

### Freshness / crypto processing

Current reconstructed processing path:

```text
8F98C
  -> 8F746(profile)
       -> freshness preparation / callback 903A0
       -> 903A0 -> 90B8A ... freshness reconstruction
       -> crypto input build
       -> 8F676
            -> 89C98
            -> ICU-S command 7 verification
       -> result dispatch
  -> if 8F746 returns zero: 8F906(profile)
```

The callback at `0x903A0` and post-verify callback at `0x90448` were among the
regions initially missing useful function boundaries. Current recovery has:

```text
903A0 -> 90B8A ... candidate freshness reconstruction/staging
90448 -> 90D6A ... pending-to-committed freshness copy
```

Current analysis of `90D6A` found freshness-state copying but no queue clear.
This should be independently checked.

Relevant RAM/result cells currently used by the observer/probe:

```text
FEBE5564  SecOC/verification result state consumed around 8F906
FEBF13BE  ICU-S done/result-adjacent byte
FEBF13BF  ICU-S status/result-adjacent byte
FEBE55DC..FEBE560B  four 12-byte freshness-state slots (48 bytes total)
```

### Native-success delivery path

Current reconstructed native-success route:

```text
8F906
  -> 8F546
  -> 90204
  -> 81CA6(route44)
  -> 7D72C
```

`0x7D72C` was also initially absent as a normal Ghidra function and was recovered
from the configured PduR group-0 receive-callback pointer.

Current reconstruction of route44 delivery:

```text
7D72C copies the received PduInfo into the route44 COM window
  -> 32-byte COM window begins FEBE4BFF
  -> new-data/bookkeeping calls 8E772(44)
  -> FEBE5364 publication generation changes
```

Current downstream application path:

```text
4BD46
  reads publication generation vs consumed generation
  unpacks B6 signals
  -> FEBE80BC Target Lateral ID
  -> FEBE80B8 target angle

58074
  -> staged application cells

BCD66
  -> FEBEADB0 Target Lateral ID snapshot
  -> FEBEAE90 target angle snapshot
  -> FEBEADB9 receive/status snapshot

CEFA4 / CEFFC
  -> FEBECAFF B6 controller enable
  -> FEBECB00 controller-bank selection
```

The current ID11 positive ladder expected by the stationary probe is:

```text
FEBE80BC = 11
FEBE80B8 = transmitted target raw
FEBEADB0 = 11
FEBEAE90 = transmitted target raw
FEBEADB9 = 0
FEBECAFF = 1
FEBEACBD = 0
FEBECB00 = 2
```

## Downstream steering/current state currently exposed to the host probe

The current stationary probe also reads these exact F33 cells so the same live
run can show state after B6 application admission:

| name in probe | address | size |
|---|---:|---:|
| `secoc_verify_result` | `FEBE5564` | 1 |
| `assist_addend` | `FEBEC81A` | 2 signed |
| `cooperative_contribution` | `FEBECB38` | 2 signed |
| `d0218_output` | `FEBECC48` | 4 signed |
| `command_pre_scale` | `FEBECC50` | 2 signed |
| `command_limited` | `FEBECC60` | 2 signed |
| `command_value` | `FEBECC62` | 2 signed |
| `current_funnel_pre_override` | `FEBECC66` | 2 signed |
| `current_funnel` | `FEBECC64` | 2 signed |
| `motor_command_mirror` | `FEBEAC54` | 2 signed |
| `diagnostic_command_mirror` | `FEBEAC56` | 2 signed |

It also records raw CAN witnesses `0x08A`, `0x081`, and `0x030` during the
stationary phase.

Implementation:

```text
exploit/behavioral_proof/camry_f33_b6_stationary_probe.py
```

## RAM-only non-bypassing transaction observer

The current observer is intended to sample transient receive/security state
without reinjecting B6.

Tracked files:

```text
exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.c
exploit/ephemeral_runtime/build_camry_f33_b6_transaction_observer.py
exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.py
exploit/ephemeral_runtime/camry_f33_b6_transaction_observer_install.py
exploit/ephemeral_runtime/audited/camry_f33_b6_transaction_observer.bin
exploit/ephemeral_runtime/audited_camry_f33_b6_transaction_observer_build.json
tests/verify_camry_f33_b6_transaction_observer.py
```

Exact audited build:

```text
staged shellcode size: 594 bytes
shellcode SHA-256:     42af3133034ab9a95858e6dd189bb847f2b3ac7d57df4dc4c02652beb1e7aa3f
resident base:         FEBFF9F0
resident end:          FEBFFBFC exclusive
resident code+slack:   494 bytes
telemetry base:        FEBFFBE0
telemetry size:        28 bytes
combined retained use: 522 / 524 bytes
ELF relocations:       0
```

Deterministic authenticated 4-KiB RAM payload:

```text
SHA-256 29841b4965c7a690d76e641efd2d950ab291cfb6332a8d806fa6930fdaecbbbb
CRC residue 0xFFFFFFFF
CMAC self-check valid
load/callback address FEBF0000
```

The observer runs the stock foreground sequence and calls stock aggregate
`0x667E6` once. The tracked verifier checks that the observer binary does not
contain the route44 callback `0x7D72C` immediate used by the bridge.

Telemetry layout (`FEBFFBE0`, little-endian):

| offset | field |
|---:|---|
| `0x00` | `heartbeat` u32 |
| `0x04` | `queue_seen` sticky u8 |
| `0x08` | `pre_secoc_result` u8 |
| `0x09` | `pre_publication_generation` u8 |
| `0x0A` | `post_queue_length` u16 |
| `0x0C` | `post_secoc_result` u8 |
| `0x0D` | `post_publication_generation` u8 |
| `0x0E` | `icus_done` u8 |
| `0x0F` | `icus_status` u8 |
| `0x10..0x14` | last queued B6 B3..B7 |
| `0x18..0x1B` | last queued B6 B28..B31 |

The security/wire fields are latched only after `queue_seen` becomes set. The
observer samples around the foreground call to stock `0x667E6`; review whether
that sampling point is sufficient to observe every relevant ingress lifetime.

The host probe in `--require-observer` mode additionally reads the 48-byte
freshness block and the COM/application/current cells listed above.

## RAM-only route44 bridge

This is a separate experiment from the observer and occupies the same retained
high-tail region, so the two residents are not used simultaneously.

Tracked files:

```text
exploit/ephemeral_runtime/camry_f33_b6_bridge.c
exploit/ephemeral_runtime/build_camry_f33_b6_bridge.py
exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py
exploit/ephemeral_runtime/audited/camry_f33_b6_bridge.bin
exploit/ephemeral_runtime/audited_camry_f33_b6_bridge_build.json
tests/verify_camry_f33_b6_bridge_install.py
```

Current audited bridge build:

```text
raw bridge SHA-256 f968447af229bdc2c8c8c700fb743f0acfb77063b17348f4c357c97aad238084
authenticated payload SHA-256 e83c40e3332b55571a526c0b45952c3944b3c9c4f65f5f2bb6e566c1aeba1f04
zero relocations
```

Current bridge behavior in source:

```text
before stock 667E6:
  detect profile-2 queued length 32
  snapshot full 32-byte B6
  count queue presence
  count zero-MAC marker candidates

after stock 667E6:
  for saved zero-MAC candidate, call recovered stock route44 receive callback
  0x7D72C with the saved PduInfo
  count reinjections
```

Bridge telemetry:

```text
FEBFFBEC heartbeat
FEBFFBF0 queue-present count
FEBFFBF4 zero-MAC-seen count
FEBFFBF8 injected count
```

The bridge has not yet been live-tested on the vehicle.

## Current field runbook already in the repository

```text
exploit/ephemeral_runtime/camry_f33_b6_observer_runbook.md
```

It contains commands for:

```text
NRTD RAM observer install
NRTD -> READY without OFF
stationary --require-observer probe
fresh NRTD RAM bridge install if desired
NRTD -> READY without OFF
stationary --require-bridge probe
optional 0.5-degree phase only after ADMITTED
```

The observer and bridge are RAM-only; a full reset/power-off removes the resident.
The physical EPS remains on the persisted stage-5 development CodeFlash image
unless separately restored.

## Items that remain directly unmeasured

At the time of this handoff:

- the transaction observer has not been installed/run on the physical Camry;
- the hardened route44 bridge has not been installed/run on the physical Camry;
- there is no native accepted F33 B6 capture to use as a stock payload template;
- the live EPS profile-2 queue has not yet been observed while the current B6
  sender is transmitting;
- the ICU-S done/status bytes have not yet been captured for one of the current
  injected B6 frames using the new observer;
- no current zero-MAC ID11 has been shown to advance `FEBE5364` or update
  `FEBE80BC/FEBE80B8`;
- no nonzero steering-offset test has been run after any positive ID11 admission;
- a moving live read of the internal B6 admission ladder has not been performed;
- stock B6 companion bytes/template and a valid F33 slot-4 B6 CMAC remain
  unavailable;
- exact Toyota stock request/arbitration/signer ownership remains separate and
  unresolved (OQ-054).

## Specific questions for independent review

These are questions, not current answers:

1. Is RSCFD rule39 -> CanIf descriptor39 -> PduR44 the complete live ingress for
   `0x0B6`, including interrupt and DMA interactions?
2. Does the `0x400000B6` CanIf identifier/configuration encode an on-wire format
   condition that our Panda frame may not satisfy even though payload/DLC are
   correct?
3. Are FDF/BRS and forwarded/native Panda frame attributes being treated exactly
   as the F33 receiver expects?
4. Can profile2 be queued and consumed/cleared between the observer's
   pre-`0x667E6` sample and the point at which the resident sees it?
5. Is `0x667E6` the only foreground aggregate invocation/path that can process
   this B6 queue?
6. Are there interrupt-driven or concurrent consumers/producers of
   `FEBE547A/FEBE54D4` that the current foreground model misses?
7. Are profile record 2 and the pointer fields `0x903A0`, `0x90448`, `0x6A218`,
   route44, and the buffer/length fields decoded with the correct record stride
   and semantics?
8. Does any raw/unpromoted code between the known functions change the queue,
   result state, or PduInfo before `8F546`?
9. Is there any alternate result path after the stage-5 comparison that reaches
   a different cleanup/delivery sequence than the reconstructed one?
10. Is `0x7D72C` definitively the exact receive callback used for PduR44 on this
    calibration, including its length/check/counter semantics?
11. Can `FEBE5364` or the COM window be overwritten by another producer before
    `4BD46` samples it?
12. Are the observer's ICU-S addresses `FEBF13BE/BF` and result cell `FEBE5564`
    sampled at the correct point to interpret one B6 transaction?
13. Does the observer alter scheduler timing enough to change an asynchronous
    SecOC/ICU-S result that it is intended to observe?
14. Should the resident record any additional state before the first live run,
    given the 524-byte retained-tail constraint?
15. Is there a better way to instrument the exact CanIf/PduR ingress edge in RAM
    without modifying the protected-PDU behavior?
16. Does the route-37 sender audit miss any field that exact F33 checks before
    PduR44 publication?
17. Are the current active companion bytes (`B6=0`, `B8/B9=100`) potentially
    relevant to a pre-COM validation path despite the current reconstruction?
18. Is the current sender's full freshness/message-counter handling relevant to
    zero-MAC testing in any way not captured by the transmitted FV4 low bits?
19. Is there evidence elsewhere in the retained corpus or Techstream/GTS+
    artifacts for an actual stock/native B6 that has not been connected to this
    analysis?
20. Is there a simpler single RAM hook/tracepoint that would distinguish
    CanIf receipt, SecOC queueing, verify result, and route44 publication more
    directly than the current observer design?

## High-value files for review

Firmware / target registration:

```text
firmware/camry-8965F3307000/CodeFlash.bin
data/analysis_targets.json
AGENTS.md
```

Current static/live narrative and raw field notebook:

```text
docs/variants/camry-2026-live-baseline.md
docs/history/2026-09/2026-09-01-camry-live-communication-characterization-notebook.md
docs/history/2026-09/2026-09-01-camry-route37-steering-speed-gate.md
docs/status/FINDINGS.md          # VAR-114..VAR-117 especially
docs/status/CORRECTIONS.md       # CORR-154..CORR-157 especially
docs/status/OPEN_QUESTIONS.md    # OQ-054 and B6-related questions
```

Receive-path / observer / bridge implementation:

```text
exploit/behavioral_proof/camry_f33_b6_stationary_probe.py
exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.c
exploit/ephemeral_runtime/build_camry_f33_b6_transaction_observer.py
exploit/ephemeral_runtime/camry_f33_b6_transaction_observer.py
exploit/ephemeral_runtime/camry_f33_b6_transaction_observer_install.py
exploit/ephemeral_runtime/camry_f33_b6_bridge.c
exploit/ephemeral_runtime/build_camry_f33_b6_bridge.py
exploit/ephemeral_runtime/camry_f33_b6_bridge_install.py
exploit/ephemeral_runtime/camry_f33_b6_observer_runbook.md
```

Persistent experiment builders:

```text
tools/build_camry_f33_gate2_semantic_patch.py
tools/build_camry_f33_gate2_root_result_patch.py
tools/build_camry_f33_freshness_result_patch.py
tools/build_camry_f33_crypto_result_patch.py
```

Verification:

```text
tests/verify_camry_8965F3307000.py
tests/verify_camry_f33_b6_stationary_probe.py
tests/verify_camry_f33_b6_transaction_observer.py
tests/verify_camry_f33_b6_bridge_install.py
tests/verify_camry_f33_gate2_root_result_patch.py
tests/verify_camry_f33_freshness_result_patch.py
tests/verify_camry_f33_crypto_result_patch.py
verification.toml
```

Live evidence:

```text
targets/camry-2026/raw-20260901/f33-b6-admission/
targets/camry-2026/raw-20260901/f33-gate2-stage2/
targets/camry-2026/raw-20260901/f33-gate2-stage3/
/Users/kai/dev/inspect/logs/camry-2026/2026-09-01/00000037--dec6fe39cb/
```

## Useful starting commands

```bash
cd /Users/kai/dev/inspect/repos/ghidra_rh850_analysis
cat AGENTS.md
git status --short
tools/gtarget show camry-8965F3307000
```

For exact firmware inspection, use the registered Camry target rather than a
generic Ghidra daemon. Examples:

```bash
tools/gcamry inspect 0x8F746 --decompile --callers --callees --xrefs --disasm 160
tools/gcamry inspect 0x8F906 --decompile --callers --callees --xrefs --disasm 160
tools/gcamry inspect 0x7D72C --decompile --callers --callees --xrefs --disasm 160
tools/pseudo --data-ref 0xFEBE547A
tools/pseudo --data-ref 0xFEBE54D4
tools/pseudo --data-ref 0xFEBE5364
```

Do not limit review to known function entry points; inspect raw bytes and branch
or table targets around the receive path where Ghidra function recovery is
missing or questionable.
