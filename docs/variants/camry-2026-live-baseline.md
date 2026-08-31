# 2026 Camry live TSS3/EPS baseline

## Scope and evidence

On 2026-08-26 the maintainer's 2026 Toyota Camry produced an identity-bound TSK
baseline covering EPS diagnostics, a stationary READY CAN segment, a bounded
PROGRAMMING handoff, and an XCP CONNECT-only probe. Raw/privacy-minimized source
evidence is retained under `targets/camry-2026/raw-20260826/`; the
reproducible compact analysis is
`data/generated/camry_2026_tsk_baseline.json`.

Sections 1–8 preserve the original **dynamic field evidence**, not a Camry CodeFlash analysis. Corolla H/F names there are used only where the wire behavior itself strongly transfers. Section 9 adds the subsequently acquired exact `8965F3307000` CodeFlash and replaces the firmware-transfer boundary only for facts proved target-natively there; remaining timing/limit/signer questions stay explicit.

## 1. Exact EPS identity and route

The application answers F181 with two 16-byte records:

- primary `8965F3307000`;
- secondary `8A3113303100`.

Exact same-image code fixes the secondary record as software/compatibility identity,
not a neighboring-blob label. F181 callback `0x4FA26` emits count 2 and copies its two
16-byte records from `0x20860` and `0x17DC0`. Startup `0x637EE -> 0x62D5E` compares
`JB1BA101` at `0x17DA0` against `0x20850`, then the five-byte `8A311` prefix at
`0x17DC0` against `0x20870`; either mismatch sets the protected error value passed to
`0x70A92`, while the JB mismatch additionally writes `0x5A` to `FEBF066C`. Callback
`0x4F9DE` is separately DID2032's one-record producer from `0x17D80`
(`8965H33030A00`) and is not an F181 record.

F18C returns ECU serial `8965033K9011J2740743`. The observed normal-harness
route is ELM327 parameter 1, logical bus 1, physical request `0x7A1`, response
`0x7A9`. The identity probe received responses from its bounded checks of SIDs
`0x10`, `0x22`, `0x23`, `0x27`, `0x3E`, and `0x19`; this is not a complete
application service-table census.

No prior tracked source in this repository contains exact F181
`8965F3307000`, so no firmware-static Corolla/Sienna result is promoted by
identity alone.

## 2. Initial PROGRAMMING handoff — bootstrap boundary later superseded by §9

The bounded DEFAULT -> EXTENDED -> PROGRAMMING probe succeeds and the diagnostic
endpoint reappears on the same explicit route. Bootloader F181 is exactly
`02 || 32*0x21`, matching the placeholder shape directly observed on the tracked
Denso EPS family. Functional `0x777` also receives a session-control response
around the handoff.

For this **initial** baseline, that was useful family evidence but intentionally
stopped short of boot SecurityAccess, DID `0201/0202/0203`, RequestDownload,
`0x10F0`, `0xFF00`, or RAM-exec claims; the TSK recovery gate correctly refused
to copy H/F/Sienna geometry by family resemblance. Section 9 later supersedes
that acquisition boundary with direct F33 evidence: the exact old-stack
authenticated bootstrap and read-only RAM payload path are now proven. The
application-retention/operational-signer boundary remains separate.

## 3. Vehicle CAN topology is strongly TSS3-like

The stationary READY capture spans 59.98 seconds and contains 134,989 incoming
CAN rows. The stream census is 22 ID/DLC streams on bus 0, 179 on bus 1, and the
same 22-ID/DLC set on bus 2. Buses 0/2 reproduce the familiar TSS3 CAN-FD family
including `0x123/16` and `0x180..0x18C`; only `0x189/64` has a non-identical
payload sequence between the two observed logical buses in this segment.

The steering/state network on bus 1 contains the same important carrier family
seen on Corolla H/F-era routes:

| ID | DLC | frames | observed rate |
|---|---:|---:|---:|
| `0x00F` | 8 | 619 | ~10.31 Hz |
| `0x025` | 32 | 6,188 | ~103.15 Hz |
| `0x030` | 32 | 6,188 | ~103.15 Hz |
| `0x090` | 32 | 6,187 | ~103.14 Hz |
| `0x0AA` | 8 | 6,187 | ~103.13 Hz |
| `0x0D7` | 32 | 3,094 | ~51.57 Hz |
| `0x101` | 8 | 3,095 | ~51.58 Hz |
| `0x116` | 8 | 2,627 | ~43.79 Hz |
| `0x127` | 8 | 3,777 | ~62.97 Hz |
| `0x176` | 8 | 1,949 | ~32.48 Hz |
| `0x51E` | 8 | 61 | ~1.02 Hz |

Classic `0x131/8` and `0x2E4/8` steering commands are absent. `0x0B6/32` is
also absent, but stock LTA was not deliberately transitioned during the segment;
zero B6 is therefore **not** evidence that this Camry lacks the H/F-style
protected lateral command.

## 4. H/F state formats transfer unusually well

### 4.1 `0x030`

All **6,188/6,188** frames satisfy the exact H/F packer relation
`B7 = low8(sum(B0..B6) + 0x38)`. Applying the H/F steering-wheel-torque layout
produces a dynamic `-1.75..+1.80 N.m` value with 143 unique samples, while the
coarser H/F truncation field spans `-1.7..+1.8 N.m`. That is substantially
stronger than an ID/DLC coincidence.

The transferred H/F B6 status locations are behaviorally plausible but are not
yet assigned Camry firmware semantics. B6[0] begins high and clears at about
0.202 s; B6[1] toggles in two short intervals around 4.9-5.8 s; B6[2] and B6[3]
stay clear. In H/F these locations have specific validity/fault/current-monitor
provenance, but those code-level names remain **candidate transfers** until Camry
firmware or independent diagnostic joins support them.

### 4.2 `0x025`

The H/F DBC geometry decodes coherently: steering angle spans `-12.0..+19.5 deg`,
fraction exercises all signed 0.1-degree nibble values from `-0.7..+0.7`, and
the signed rate field spans `-80..+70` in the existing prior-art deg/s
interpretation. This is strong wire-layout continuity, not a substitute for the
Camry receiver/producer code.

### 4.3 legacy checksum/state carriers

The ordinary Toyota checksum validates every retained `0x101` (3,095/3,095),
`0x127` (3,777/3,777), and `0x176` (1,949/1,949) frame. The capture is stationary:
all H/F-compatible wheel-speed fields decode zero with clear wheel-fault bits,
brake/gas remain inactive, and the `0x127` gear field is raw `0` throughout.
Raw `0` is prior-art-compatible with `P`; the same repository previously observed
raw `3` while a Corolla was driving and treated it as D. The later controlled
Camry READY/selector pass in §8 supersedes this initial bound and directly closes
all five values `P=0, R=1, N=2, D=3, B=4` on this exact vehicle.

## 5. `0x51E B0[7]` Ready transition

The strongest new state result is a real transition on the wire already joined
statically in H/F to Techstream DID `0x1033 Ready Status`:

| capture time | B0[7] | payload |
|---:|---:|---|
| 0.0176 s | 0 | `0000610000000000` |
| 0.9943 s | 1 | `8000610000000000` |
| 16.0042 s | 1 | `8000620000000000` |

Thus this Camry starts the retained READY segment with the bit clear and then
asserts it about one second later. This strongly corroborates `0x51E B0[7]` as a
cross-vehicle TSS3 Ready-status carrier and supplies the first retained `0 -> 1`
transition in this repository. The later controlled NRTD→READY pass in §8
independently reproduces the transition with the passive logger already active
before the operator is told to enter READY, closing the remaining causal ambiguity
for state decoding while still bounding exact button-to-frame latency.

## 6. XCP timed out on the correct normal-harness route (CORR-124)

A CONNECT-only probe on `0x7F7` over the identified EPS normal-harness route
timed out waiting for `0x7F8`; no XCP writes were exposed or attempted. Later
exact-F33 static routing closes the interpretation that this was a wrong-route
negative: receive-rule 46 at `0x23398` and transmit handle `0x37` independently
resolve `0x7F7/0x7F8` to **RSCFD controller 1**, the same EPS channel exposed as
Panda bus 1 on the identity-bound normal harness. The retained timeout therefore
bounds live XCP admission/response state, not physical route selection.

## 7. NRTD P5 identities and cruise-control wire joins

A second stationary **Not Ready to Drive** pass used only diagnostic reads, one
bounded EXTENDED-session read check, and passive CAN observation. It closes the
Camry-native FRC and Brake/EPB identities that VAR-051 left open:

| module | bus | request -> response | exact F181 | supporting identity |
|---|---:|---|---|---|
| `FRC_P5` | 1 | `0x792 -> 0x79A` | `8646F3315000` | `0105=8646C06091`; F18C `TN69400026030404235J`; `1FFF=06000000000000000000` |
| category-435 Brake/EPB | 1 | `0x7B0 -> 0x7B8` | `F152633K0000` | `0105=8954147040`; F18C `8954147040CFC1800985` |

The same physical requests timed out on logical buses 0 and 2 in the bounded
sweep. Both exact software IDs are new to the tracked local openpilot firmware
corpus even though their `8646F33...` / `F152633...` families are familiar; they
are therefore retained as Camry-native identities rather than forced into an
older platform match.

### 7.1 FRC cruise diagnostic oracles work on this exact car

The current-GTS+ SID-`0x22` transport recovered in TMS-057 transfers directly to
this FRC. `0x1901`, `0x1905`, `0x1906`, `0x1912`, `0x1914`, `0x1918`, `0x1928`,
and `0x1202` all return positive data in NRTD. Isolated operator button presses
then make the named control states observable without inference from timing:

- **MAIN:** `0x1906 e080e0008000 -> e0c0e0008000 -> baseline`;
- **RES+:** `e080e0008000 -> e080e0808000 -> e0a0e0808000 -> baseline`;
- **SET-:** `e080e0008000 -> e080e0408000 -> baseline`;
- **CANCEL:** `e080e0008000 -> e080e0208000 -> baseline`;
- **following distance:** `0x1912` changes persistently (`03 -> 04` in the
  isolated run and `04 -> 01` in the synchronized run).

This validates the FRC P5 diagnostic vocabulary dynamically on the exact Camry.
The engagement-state oracles (`0x1905` permission and `0x1914` ACC control in
operation) stay in their non-engaged NRTD states, so actual cruise engagement
still requires a later READY/driving observation.

### 7.2 `0x0FE/32` is the momentary cruise-switch CAN carrier

A single-Panda synchronized run retained 1,742 FRC oracle samples and 90,932
passive CAN frames while MAIN, RES+, SET-, CANCEL, and following-distance were
pressed sequentially. The four momentary `0x1906` edges join directly to bus-1
`0x0FE/32` at about **33.19 Hz**. Ignoring independently rolling integrity/counter
bytes, the stable data tuple `(B3,B4,B6,B7)` is `(3F,00,C3,62)` and becomes:

| operator input | event tuple `(B3,B4,B6,B7)` | XOR from baseline |
|---|---|---|
| MAIN | `(3F,00,C3,66)` | `B7 ^= 04` |
| RES+ | `(BF,00,43,62)` | `B3 ^= 80`, `B6 ^= 80` |
| SET- | `(3F,80,C3,22)` | `B4 ^= 80`, `B7 ^= 40` |
| CANCEL | `(3F,40,C3,42)` | `B4 ^= 40`, `B7 ^= 20` |

Each event returns to the same baseline around the corresponding FRC diagnostic
edge. That is a direct dynamic CAN/Techstream join; it does not by itself name
the producer ECU or authorize transmitting `0x0FE`.

Following-distance is a different, persistent state. When FRC DID `0x1912`
changed `04 -> 01` at 16.874632 s, two low-transition passive candidates changed
within about 12 ms and stayed changed: bus-1 `0x251/8` B5 `88 -> 28` at
16.885741 s, and bus-1 `0x5AF/32` B24 `F0 -> E4` at 16.886393 s. Those are
**candidate ordinary-CAN distance-state carriers only** pending an independent
repeat/enum sweep; no Toyota signal name or producer is assigned yet.

### 7.3 Corolla Brake `0x107E` does not directly transfer

The Camry Brake/EPB ECU answers DID `0x102F` (`f700fd007c00a9000000`), but
`0x107E` returns `requestOutOfRange` both in the tested default session and after
a positive EXTENDED-session entry. The ECU was returned to DEFAULT immediately
after the check. Therefore the Corolla `ABS_P5` `ADS Control EPS Pinion Angle2`
monitor is **not** a usable Camry live oracle under these tested sessions, and it
must not be copied into Camry integration assumptions.

The deterministic interpretation is
`data/generated/camry_2026_nrtd_p5.json`, generated by
`tools/analyze_camry_2026_nrtd_p5.py` and verified by
`tests/verify_camry_2026.py`. Raw source identities are pinned separately
in `targets/camry-2026/raw-20260826/NRTD_MANIFEST.txt` so VAR-051's READY
baseline remains independently reproducible.

## 8. Controlled NRTD→READY and complete `0x127` gear enum

A third passive field pass was started while the vehicle was stationary and
**Not Ready to Drive**. Only `Panda.can_recv()` was used after route/safety-mode
configuration; the retained capture scripts contain no CAN transmit call, UDS,
SecurityAccess, RoutineControl, reset, download, or vehicle-control path. After
the logger was confirmed running, the operator was explicitly told to enter
READY and then exercise the selector while holding the brake.

### 8.1 `0x51E B0[7]` is now controlled NRTD→READY evidence

The first 60-second capture directly records:

| capture time | B0[7] | payload |
|---:|---:|---|
| `0.070314 s` | 0 | `0000640000000000` |
| `5.213083 s` | 1 | `80006e0000000000` |

Because the logger was already active in NRTD before the READY instruction, this
is stronger causal evidence than VAR-051's earlier startup segment: `0x51E B0[7]`
is directly suitable as the Camry Ready-state carrier. The operator's physical
button press itself was not machine-timestamped, so exact action→frame latency is
still not claimed.

### 8.2 `0x127` closes `P=0, R=1, N=2, D=3, B=4`

The first selector run was intended to include B, but the operator immediately
reported afterward that B had been missed. The wire sequence therefore provides
a clean reversible P/R/N/D round trip rather than an inferred missing event:

| time | raw `0x127` gear | operator state | representative payload |
|---:|---:|---|---|
| `0.016697 s` | 0 | P | `00100000000ebe0c` |
| `12.560082 s` | 1 | R | `00100000001e8deb` |
| `14.443866 s` | 2 | N | `00100000002e8dfb` |
| `17.525321 s` | 3 | D | `00100000003e8d0b` |
| `21.129039 s` | 2 | N | `00100000002e8dfb` |
| `23.014504 s` | 1 | R | `00100000001e8deb` |
| `25.192386 s` | 0 | P | `00100000000e8edc` |

A second 25-second READY/stationary capture was then started specifically for B.
After its initial P baseline, the operator performed D→B→D:

| time | raw `0x127` gear | operator state | representative payload |
|---:|---:|---|---|
| `5.107709 s` | 3 | D | `00100000003e8d0b` |
| `9.480908 s` | 4 | B | `00100000004e8d1b` |
| `13.626834 s` | 3 | D | `00100000003e8d0b` |

The Toyota checksum validates **3,777/3,777** first-run `0x127` frames and
**1,634/1,634** B-run frames. Bus-1 `0x0AA` is also byte-identical at
`1a6f1a6f1a6f1a6f` for all 6,187 + 2,677 retained frames, matching the earlier
zero-motion Camry baseline and independently supporting the stationary condition.

Therefore the complete prior-art enum is now **directly validated on this exact
Camry**: `P=0`, `R=1`, `N=2`, `D=3`, `B=4`. This closes the Camry read-only gear
measurement boundary. It does not authorize transmitting any frame or automatically
transfer the validation to a different Toyota platform.

The deterministic artifact is `data/generated/camry_2026_ready_gear.json`, built
by `tools/analyze_camry_2026_ready_gear.py` and checked by
`tests/verify_camry_2026.py`. Exact capture/script hashes and the
operator-sequence correction are pinned in
`targets/camry-2026/raw-20260826/READY_GEAR_MANIFEST.txt`.

## 9. Exact `8965F3307000` CodeFlash and target-native steering contract

The fourth stationary/NRTD pass acquired the exact EPS CodeFlash rather than
continuing to transfer H/F firmware semantics. The successful identity- and
Ready-guarded collector returned the complete configured 2-MiB transport range:
524,288/524,288 unique words, zero conflicts, zero duplicates, and zero SPI
errors. The raw dump SHA-256 is
`b588c7258699beee77669d1f5f09bb17ef8b189b941b46f344a07378c3aaa727`.
The lower 1 MiB is populated while the upper 1 MiB is entirely erased `0xFF`, so
the deterministic normalized CodeFlash is the exact lower half, SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.

The acquisition also replaces VAR-051's boot-family boundary with direct F33
evidence. Stock boot SID `0x23` CodeFlash access rejects the read, but boot
SecurityAccess succeeds; DID `0x0203` returns the old-stack selector, zero
`0x0201/0x0202` records are accepted, RequestDownload accepts
`FEBF0000/0x1000`, `0x10F0` accepts the authenticated envelope, and `0xFF00`
starts the retained read-only range payload. These are exact Camry bootstrap
facts. They do **not** prove that a Corolla H/F application-retention carrier or
operational command-5 permission survives unchanged after boot-to-application
handoff.

### 9.1 Application Rx continuity and target-native SecOC

The generated normal-Rx descriptor table is at `0x21FE8` with 43 descriptors.
Every one of the 40 Corolla-H descriptors exists on this target; Camry adds only
`0x116/8`, `0x0D8/8`, and `0x1DA/8`. Relative to the older Sienna image, Camry
removes the old `2E4/191/131/2FD/132/423/020` receive set and adds
`116/D8/B6`. This is configuration continuity, not a blanket semantic-transfer
claim.

The exact three-record protected receive table is at **`0x25848`** and contains
only `0x00F`, `0x0D7`, and `0x0B6`. The shared crypto configuration immediately
before it selects `{type=1, selector=4}`; target-native `0x8A8E4` programs ICU-S
**command 7**. B6 is regenerated as **PDU44**: 32 secured bytes, 28 application
bytes plus an FV4/CMAC28 trailer, full FV46, full CMAC128, freshness ID 2, and
crypto handle 0. Thus the earlier H/F conclusion that B6 belongs to the same
slot-4 authenticated receive family as `00F/D7` is now independently true for
F33 itself.

### 9.2 B6 wire layout: Target Lateral ID + target steering angle

Camry's COM scalar extractor is at `0x7D12A`; target-native code fixes TP at
`0x23DFC`, signal-to-PDU table `0x22488`, PDU table `0x226C0`, and PDU-buffer
offset table `0x22840`. PDU44 begins at COM offset `0x1B7` and owns configured
signals 259..275. Its scalar unpacker `0x4BD46` recovers, among the companion
fields:

- **signal 261 = B3[5:0]**, unsigned six-bit selector;
- **signal 262 = B4:B5**, signed 16-bit steering target;
- signals 263..273 occupy B6..B10;
- B28..B31 remain the SecOC trailer rather than application fields.

Signal 261 is now nameable rather than merely structurally analogous to H.
`0x58074` stages B3 and `0xBCD66` snapshots it; target-native `0xCEFFC` consumes
that snapshot and recognizes values `1/4/10/11/18/19`. Toyota's P5 EMPS
**Target Lateral ID** dictionary assigns those exact values
`PCS/LDA/Hands Off LTA/LTA-LCA/SDG/PDA`. A second target-native consumer
`0xCB73A` recognizes raw 49, which the same Toyota dictionary names
`Self-Propelled Transport`. The numeric/consumer join therefore closes B3 as
**Target Lateral ID** on this Camry.

Signal 262 is staged `gp-0x3748 -> gp+0x39FA -> gp-0x970` and consumed by
**`0xCCF0E`**, which computes a saturated `2 * signed16(B4:B5)` target followed
by interpolation/history; `0xCCFB6` applies mode-dependent target limits and
`0xCEE80` independently supervises the same target snapshot. The remaining
question was whether this target quantity was specifically steering angle or a
more generic steering-domain scalar. The Camry's own feedback path closes that
question.

### 9.3 Camry-native `0x025` measured Steering Angle closes signal 262

CAN-FD `0x025` is target-native PDU35 at COM offset `0x127`. Its unpacker
`0x4B59E` extracts signal 187 as signed12 coarse angle and signal 188 as signed4
fraction. `0x47AE0` consumes the exact coarse field, and the target's own DID
`0x1037` table row at `0x293AC` points to callback `0x4DBF8`, which consumes that
same value. Toyota P5 names DID `0x1037` **Steering Angle** and gives the coarse
raw value a `1.5 deg/count` conversion.

The normal control path independently reconstructs the same feedback:
`0xB3B06` forms `15*coarse + signed_fraction`, and `0xCE9EA` converts it through
`*0x6FB/0x200`; the signed nibble therefore supplies the `0.1 deg` fraction of
the coarse 1.5-degree representation. `0xCEADA` republishes the valid measured
angle into a redundant triple. The corrected complete comparator at `0xCD128`
then votes the B6-derived target triple and the `0x025`-derived measured-angle
triple, applies the **same `0xB76/0x400` gain to each, and subtracts measured
from target**. This target-native closed loop is direct evidence that B6
**signal 262 / B4:B5 is the target steering-angle command**.

The integer gains also give an exact linearized controller-equivalent scale:
one B6 count corresponds to `1024/17870 deg`, approximately `0.0573027 deg` or
`1.0001215 mrad`. That is a derived relation between the two target-native
controller domains, including Toyota's DID `0x1037` degree scale; the firmware
does not literally label B6's wire engineering unit "mrad", and integer
truncation/saturation still applies.

PDU44's target-native receive supervision reloads to **seven foreground ticks**.
The exact F33 TAUJ0 CH3 tick period and the resulting wall-clock timeout are now
closed target-natively in §12.1; the H 5-ms figure is no longer transferred.

The compact artifact is `data/generated/camry_8965F3307000_codeflash.json`,
bound to exact target-native decompiler bodies in
`data/generated/camry_8965F3307000_decompiler_evidence.json` and independently
checked by `tests/verify_camry_8965F3307000.py`. Raw acquisition
provenance is retained in `raw-20260826/CODEFLASH_MANIFEST.txt`.

## 10. Exact DataFlash + CPU-visible RAM SecOC-key recovery result

A fifth exact-target NRTD experiment used the already-proven F33 authenticated
`FEBF0000/0x1000 -> 0x10F0 -> 0xFF00` range-reader family to collect the
physical 32-KiB DataFlash, the complete 128-KiB PE1 LocalRAM view, and the
complete 64-KiB GlobalRAM view. Every acquisition was identity-bound to
`8965F3307000 / 8A3113303100`, required bus-1 `0x51E` Ready=0 before the
PROGRAMMING handoff, re-observed the exact boot placeholder, used the old-stack
zero-`0201/0202` authenticated payload contract, and completed with zero range
conflicts. The retained hashes are:

- DataFlash `FF200000..FF207FFF`:
  `231fbdde4ef317931d8f1ff20ff131650f7d773c124a179b0ae3dc98bf8e4432`;
- PE1 LocalRAM `FEBE0000..FEBFFFFF` / 128 KiB:
  `0ddef478b15bcf3241c56573463eda25ba018081629daf0042fcae1204c435a7`;
- GlobalRAM `FEEF8000..FEF07FFF` / 64 KiB:
  `53c8370237c681d4105c513be5096461ac735ffcb9577995c7203216165006a4`.

The DataFlash storage result is unambiguous at the already-recovered NvM
geometry. Object 15 occupies the familiar raw/xor55/xoraa records at
`0xFF206E00/0xFF206D00/0xFF206C00`, but **all three copies are invalid** and
there is no valid decoded consensus. More specifically, the corresponding
16-byte second/key fields at **`0xFF206E14`, `0xFF206D14`, and `0xFF206C14`
are all raw zero bytes**. Thus the 4514000-era plaintext-object-15 result does
not transfer to this exact F33 ECU.

The PE1 LocalRAM snapshot independently validates why the generic legacy
extractor correctly refused F33 instead of projecting the old `FEBE6E34`
layout. Interpreting `FEBE6E34..FEBE6FF3` as fourteen 0x20-byte legacy key
records gives **0/14 valid record checksums**. The old KEY_1 field at
`0xFEBE6E60` is zero; the old KEY_4 field at `0xFEBE6EC0` belongs to a
checksum-invalid record; and the old `0xFEBF42E0` factory-key record is zero.
Conversely, the exact F33 application-SecurityAccess root
`893e08418c741ffa2a9c044bffa55813` appears exactly once at **`0xFEBF7B80`**,
matching the H/F startup-mirror position and demonstrating that the LocalRAM
stream is structured target state rather than an empty/broken acquisition.
Neither the payload-build root nor the boot-SA root appears as a raw 16-byte
LocalRAM or GlobalRAM value.

One acquisition caveat is explicit: the LocalRAM range reader itself is loaded
at `FEBF0000..FEBF0FFF`, so those 4096 bytes are overwritten before the range
is read. They are excluded from key-search conclusions. The rest of PE1
LocalRAM had 100% word coverage (32,768/32,768); GlobalRAM likewise had 100%
coverage (16,384/16,384), with zero conflicts, duplicates, or stream-time SPI
errors in both retained runs.

The READY oracle collected alongside this experiment is healthy and directly
contains the F33-native protected domain: bus 1 has 618 `0x00F/8`, 6,190
`0x090/32`, 3,095 **`0x0D7/32`**, 2,629 `0x116/8`, and 63 `0x24D/8` frames
over about 59.98 seconds. `0x0B6` was not exercised in this stationary
capture. `kai-openpilot` matcher commit
`2bfbef37fddbdf4e499a4adc55005474f3c5ffcf` parsed 208 sync samples plus 813
protected samples (including capped `0x0D7` FD samples) and exhaustively tested
every eligible sliding 16-byte window:

- DataFlash: **32,753 / 32,753**, zero survivors;
- PE1 LocalRAM: **126,946** eligible windows after excluding the payload span,
  zero survivors;
- GlobalRAM: **65,521 / 65,521**, zero survivors.

This closes the simple CPU-visible-key hypothesis for the retained post-handoff
memories: **no raw 16-byte window in the complete DataFlash, non-clobbered PE1
LocalRAM, or GlobalRAM authenticates the captured Camry SecOC traffic under the
recovered Toyota CMAC formats.** It does *not* imply that ICU-S slot 4 is empty.
Exact F33 firmware already proves command-7 verification selects slot 4, and the
live `0x0D7` stream demonstrates an operational protected domain. The natural
interpretation is therefore that the active slot-4 secret is not present as a
raw CPU-visible value in these retained stores. A transient application-only
RAM value could also be cleared by the application-to-boot handoff, so the RAM
negative is scoped to the post-handoff snapshots rather than every instant of
application runtime.

Raw acquisition, payload, oracle, and retained matcher provenance live under
`targets/camry-2026/raw-20260826/secoc-recovery/`; deterministic compact
interpretation is `data/generated/camry_8965F3307000_secoc_recovery.json`.

## 11. What this changes for openpilot work

The exact Camry image removes the largest firmware-transfer uncertainty from the
lateral path. `0x025`, B6, the protected `00F/D7/B6` set, ICU-S slot-4 receive
verification, Target Lateral ID, and the target-vs-measured steering-angle loop
are now F33-native facts rather than Corolla assumptions. Section 12
subsequently closes the exact F33 lateral/runtime prerequisites statically: the
5.000-ms foreground tick, the mode2 limit calibration, the companion control
fields, the monitor/torque/current feedback oracles, the application runtime
anchors, and the static carrier geometry. The earlier read-only CarState
evidence (`0x030` torque, `0x51E` Ready, `0x127` gear, FRC cruise oracles)
remains complementary live evidence.

The original stock-B6-capture blocker in this section is superseded by
VAR-081/CORR-134. The retained relay-correct drives already contain complete
LTA/LCA-active intervals with zero B6 and recover Bus-4 `0x08A` as the lateral-
request representation. The current blockers are therefore narrower and
producer-directed:

1. identify who produces the observed Bus-4 `0x08A`; its absence from Panda bus 1
   means the retained capture does not distinguish a Bus-1-side request transformed
   before observation from a Bus-4-side producer/echo;
2. recover `0x08A` integrity/authentication and the producer-side transformation
   into exact-F33 protected B6, including the companion-state mapping;
3. identify the B6 signer/freshness owner plus suppression/fallback and lateral
   authority/arbitration semantics before claiming an exclusive controllable source;
4. only after that chain is known, validate signing latency/jitter, driver-override
   and motor-current response policy, and `0x351/0x394/0x4A3` fault/recovery behavior;
5. perform a bounded relay-correct steering experiment only after those producer,
   protection, arbitration, and safety gates close. FRC `0x1601/0x1914` remains
   useful independent corroboration, not a prerequisite for identifying the retained
   LTA/LCA interval.

Production output remains disabled. The exact firmware substantially reduces the
remaining work, but it does not by itself authorize steering transmission.

## 12. Exact F33 static lateral/runtime prerequisite closure

This section is the canonical home for the target-native static closure of the
remaining F33 lateral prerequisites (ledger: **VAR-056**): foreground timing,
the B6 mode2 limit calibration, companion control fields, feedback monitors,
application runtime anchors, and the static carrier geometry. All claims are
exact `8965F3307000` firmware-static results on the retained CodeFlash from
§9; none is transferred from Corolla H/F or Sienna. Static closure does not
authorize transmitting any frame.

### 12.1 Foreground timing: TAUJ0 CH3 steady 5.000 ms

Foreground timer `0x66062` (TAUJ0 channel 3) is configured for a **steady
5.000-ms period after one 5.125-ms first interval**. The startup interval is a
deliberate first-reload artifact, not jitter. PDU44's seven-tick receive
supervision (§9.2/§9.3) therefore expires at a **nominal 35 ms** after the last
authenticated B6 delivery. This is the exact-F33 replacement for the H/F timing
boundary and is the number the live stock-sender cadence capture must confirm
before any sender schedule is fixed.

### 12.2 Target Lateral ID 11 selects supervisor mode2; exact mode2 calibration

Target Lateral ID (signal 261, §9.2) directly selects the steering supervisor's
**mode2** control family: value `11` (LTA-LCA) is consumed as the mode2
selector. The exact mode2 limit calibration is:

- **±1745 B6 counts (~±100 deg)** absolute target limit;
- **78 counts (~4.47 deg)** per effective modulo-64 sequence gap;
- the effective sequence gap is **capped at 8**.

These are target-native constants, not H/F transfers; the H/F ±1745/78 figures
are now independently corroborated as the exact-F33 values rather than copied.

### 12.3 Companion B6 control fields

The companion-field semantics recovered in the mode2 consumers are:

- **signal 265 = 1** suppresses one additive contribution term;
- **signals 269/270** are `/100` percentage contributions; **zero removes**
  the term entirely;
- **signal 268** is the application-side modulo-64 sequence counter (the
  receiver-side sequence state was already closed in §9);
- the remaining secondary fields stay **unnamed** — no OEM field name is
  assigned without firmware or diagnostic evidence.

### 12.4 Feedback oracles: angle-velocity monitor, torque, and Q current

Exact F33 diagnostic joins close the feedback side:

- `0x025` **signal 189 is Steering Angle Velocity**, via the exact DID1036
  callback `0x4DBBC`. The LTA/LCA monitor uses **abs(raw) > 100** with
  **79-cycle persistence**.
- DID1035 **Steering Wheel Torque** callback `0x4DB70` scales **raw/256 N.m**
  with validity magic `0xA5AA5AA5`. The **±2109 raw (~±8.238 N.m)** bound is an
  **acquisition/representation clamp, not an override threshold**.
- DID1151 **Motor Actual Current Q Axis** callback `0x4E394` computes
  **(raw*100)/0x80**. The first-class 6,065-function Ghidra graph resolves
  `GP-0x5158` to `FEBE66A8` and finds **9 direct driver-torque references
  (7 reads / 2 writes)**; it resolves `GP-0x50F2` to `FEBE670E` and finds
  **6 direct Q-current references (4 reads / 2 writes)**. **Neither exact
  address has a direct Ghidra reference inside the cooperative `C8xxx-D1xxx`
  B6 control cone.** This supersedes the scratch-project 4→5 textual census
  (CORR-122). Computed aliases without a Ghidra data reference, DMA, hardware
  mutation, and unrecovered code remain outside the bounded negative.

### 12.5 Application runtime anchors

For runtime construction against this exact image:

- context init `0x715B4` loads EBASE=`20000`, INTBP=`20200`, GP=`FEBEB800`,
  TP=`23DFC`, SP=`FEBE2000`;
- coordinator `0x637EE` performs 21 startup calls `0x637F6..0x63846`, with the
  final call `0x701EA(0)`, then `ei`, then foreground `0x66062`;
- boot calls C9A/E54/F80/10C6, validity 119E.

### 12.6 Live carrier correction: `FEBF0000` rejected, high tail verified

The later live startup-retention probes supersede the static low-pocket carrier
assumption from VAR-056. The real stock application startup **overwrites** the
`FEBF0000..FEBF0307` candidate; `stock-retention-20260826.json` has
`prefix_648_byte_exact=false` and `shell_retained=false`. That pocket remains
useful as authenticated boot staging, but it is not a production resident
application carrier.

A separate high-tail probe closes the actual retained executable geometry on this
exact F33:

- **`FEBFF9F0..FEBFFBFB`**, exactly **524 bytes**;
- live marker execution from the tail succeeded;
- after the real stock application startup, all 524 bytes survived byte-for-byte;
- retained SHA-256
  `89ffed31c24e746a57171e6f3e22f99d1e78d57b63bccb8778c7fe715d18800c`;
- application F181 `8965F3307000 / 8A3113303100` reappeared normally;
- Panda `safety_tx_blocked_delta=0`.

This tail is inside MPU region 1 `FEBF7C00..FEBFFBFC`: context 0 MPAT `0xB8`
(supervisor R/W/X), context 1 MPAT `0xA8` (supervisor R/X). It is now recorded as
exact-target dynamic evidence in `data/variant_ram_exec_requirements.json`. The
old audited low-linked canary/proxy binaries remain reproducible static build
evidence only and must not be treated as post-startup production residents.

The live evidence is pinned under `targets/camry-2026/raw-20260826/`;
`tests/verify_camry_8965F3307000.py` and the corrected
`tests/verify_camry_8965F3307000.py` prevent regression.

## 13. Non-persistent application-mode signer installation

The production question is narrower after the high-tail result: can stock F33,
already online in the application, accept arbitrary bytes into that tail and then
transfer control there without the PROGRAMMING handoff? Exact firmware closes the
**placement** half and leaves the **control-transfer** half open.

### 13.1 Rank 1 — stock application XCP `DOWNLOAD` plus a separate volatile pivot

F33 contains the standard XCP command map at `0x22B24` and callback table at
`0x22B50`. Exact target-native callbacks include:

- `SET_MTA` `0x82C62`;
- `DOWNLOAD` `0x81FFE`;
- `MODIFY_BITS` `0x820C4`;
- `SHORT_UPLOAD` `0x82B1A`;
- write-range validator `0x98F2C`;
- CAN receive adapter `0x8312E`.

`DOWNLOAD @ 0x81FFE` obtains the current MTA, validates the transfer, enters its
critical section, performs direct byte stores from tester request data, and advances
the MTA. F33's configured software window is exactly
**`FEBF7C00..FEBFFBFF`** (`0x2B21C/0x2B220`), so the full live-proven high tail is
inside the stock writer. The map has no configured GET_SEED (`0xF8`) or UNLOCK
(`0xF7`) callback. This is therefore the strongest available application-mode
loader primitive: if its transport is reachable, bytes can be placed while the
stock application handler is executing, without `10 02`, a reset, or persistent
flash modification.

The physical endpoint also exists in F33. Toyota/Denso stores it in packed CAN
descriptors rather than plain u32 IDs:

- request `0x7F7`: packed `0x9FDC0002` at `0x21F50` and `0x23398`;
- response `0x7F8`: packed `0x9FE00002` at `0x21F48`.

The physical route is now target-natively closed. The second `0x7F7` descriptor at
`0x23398` is receive-rule **46** in the 16-byte rule array at `0x230B8`; exact
controller-span configuration assigns rules 0..46 to **RSCFD controller 1**. On
transmit, XCP family 5 resolves through route record `0x21AF4` to hardware handle
`0x37`; the handle table at `0x22DB8` maps `0x37 -> {controller=1, resource=8}`.
The transport is classic standard CAN with max receive length 8. Thus RX and TX
independently bind application XCP to controller 1, which is the identity-bound
normal-harness Panda bus 1 EPS channel used by the retained CONNECT timeout.

The timeout is therefore reclassified by **CORR-124** as a **correct-route,
no-response runtime observation**. Exact transport admission explains the remaining
ambiguity: `FEBE4EE6` is `0x69` disabled / `0x5A` enabled; `0x82F18` promotes it
only when communication-owner state admits the channel. Owner active predicate
`0x7F23C` requires `FEBE491B == 0xE1`; source/propagated communication masks use
bit 4 (`0x10`), and the owner has a configured three-foreground-tick (15-ms) delay.
The actual online-event byte `FEBE4919` is event-driven, so static initialization
does not prove what state held during the old live run. `xcp_runtime_state_probe.py`
now reads only those exact admission cells via application SID `0x23` before a new
CONNECT attempt. Production viability therefore has two remaining gates: close live
transport admission/write reachability on the already-proven route, and recover a
safe application-mode control-transfer object.

### 13.2 Why the tail begins exactly at `FEBFF9F0`

The seven-selector custom calibration/XCP family at `0x2B250` maps
`FB/FA/F5/F3/EB/EA/E4` to
`0x98FBA/0x9901A/0x99152/0x99266/0x9930E/0x99388/0x99414`. The final four are the
standard calibration-page operations **BUILD_CHECKSUM (`F3`)**, **SET_CAL_PAGE
(`EB`)**, **GET_CAL_PAGE (`EA`)**, and **COPY_CAL_PAGE (`E4`)**. SET/GET_CAL_PAGE
mutate/report the two lower-RAM page-state bytes `FEBE5EC4/5EC5`. `0x991D2` is the
page-address translator: the recovered path uses it from BUILD_CHECKSUM to translate
between CodeFlash `0x10000..0x17DEF` and the RAM shadow. No recovered use feeds an
instruction fetch or branch target.

The E4 handler invokes `0x993F0`, which copies CodeFlash `0x10000..0x17DEF` to
LocalRAM `FEBF7C00..FEBFF9EF`. Normal stock application startup independently does
the **same copy**: entry `0x20880 -> 0x637EE`, then callsite `0x63822 -> 0x636D4`.
The `0x636D4` and `0x993F0` 36-byte copy loops are byte-identical and the startup
copy occurs before the later interrupt-enable point. The source page is therefore
materialized as ordinary calibration data during every stock startup, not only by
a diagnostic request.

A target-native recovered-function census finds **zero function entries** in the
32,240-byte source page and **zero function-owned flow edges** into it; the mirrored
`FEBF7C00..FEBFF9EF` range likewise has **zero recovered flow edges**. No application
consumer of the page-state bytes outside this calibration/XCP machinery is recovered.
This closes the tempting "calibration overlay executes from RAM" composition as a
**data-shadow path, not a recovered control-transfer primitive**.

The verified carrier begins on the very next byte:

```text
FEBF7C00 + 0x7DF0 = FEBFF9F0
```

Thus the 524-byte region is the residual tail above the stock calibration shadow
and immediately below the MPU-region-1 upper bound, not an arbitrary guessed hole.

### 13.3 Rank 2 — stock RID `0x100F` really reaches command 5, but is not a signer API

The exact application RoutineControl table at `0x26918` contains RID `0x100F`.
Its row in callback table `0x256DC` is
`{0x100F, precondition 0x8B858, action 0x8B872}`. The action reaches the stock
crypto state machine:

```text
0x8B872 -> 0x6A0AE -> 0x69C58 -> 0x69BD8 -> command-5 dispatcher 0x89440
```

This is a real stock application command-5 path and is valuable as a permission /
hardware oracle. It does **not** expose a general SecOC signing service. The
command-5 arm at `0x69BD8` uses a fixed **16-byte** internal input at
`FEBE5186` and private result at `FEBE51B6`; neither cell is inside the XCP write
window and the result is not returned as an arbitrary tester-controlled MAC API.
It therefore cannot directly sign the 7-byte `0x00F` authenticated input or the
36-byte protected-FD inputs needed by `0x0D7/0x0B6`.

### 13.4 Ordinary application UDS does not supply an alternative loader

The exact application service table at `0x25C54` configures
`10/11/14/19/22/23/27/28/2E/31/34/36/37/3E/85/AB/BA`. There is no SID `0x3D`
WriteMemoryByAddress. SID `0x23` is the bounded RMBA reader; SID `0x2E` is the
configured DID-write engine rather than arbitrary memory access. SIDs `0x34/0x36/0x37`
have null direct application callbacks and are admitted only in session 2; the real
download state belongs to the already-known disruptive PROGRAMMING path. SID `0x11`
ECUReset is weaker still in this exact calibration: its service object has a null
direct callback, session-2-only policy, no subfunction table, and zero subfunctions,
so there is no ordinary application reset worker to compose with retained RAM.

The remaining application diagnostic classes have now been enumerated target-natively
for the PC-pivot question rather than dismissed by service name:

- **WDBI `0x2E`** resolves through a six-class static table and then an exact
  13-entry DID table at `0x25640`: `0204, 2001, 2002, 2005, 2006, 2007, 2008,
  2009, 200D, 2010, 2012, 2013, 2014`. Every precondition/write callback is a fixed
  CodeFlash target; the generic lower worker caps its internal payload staging at
  `<8` bytes. None of the 13 write callbacks treats payload bytes as an address or
  performs request-derived indirect control flow.
- **RoutineControl `0x31`** has all 19 F33 rows reconstructed from `0x256DC`.
  Every non-null precondition/action is fixed CodeFlash; RID `0x1010` is null/null.
  RID `0x100F` remains the crypto oracle described above, but no RID accepts a tester
  PC/address or installs a callback.
- **Proprietary SID `0xBA`** copies at most 64 request bytes into fixed state, then
  dispatches through exactly ten 16-byte CodeFlash operation records at `0x27EC4`
  (`F1/F3/F4/F5/F6/F7/F8/F9/FA/FB`). All 20 start/finish callbacks are fixed
  CodeFlash functions; none reinterprets request bytes as an executable address.
- **Proprietary SID `0xAB`** has three fixed selector callbacks at `0x25AFC` and a
  64-slot event catalogue at `0x2AB70`, with exactly 51 populated IDs and type bytes
  `11/22/33/44/55`. Request state lives at `FEBF45D0..FEBF45E3`, below the XCP
  writer. The selectors format/read bounded event IDs and merge event-data buffers
  into the DCM response; the catalogue is not a function-pointer/address table.

Thus every **recovered configured application diagnostic class with plausible
write/control semantics** is now bounded away from a tester-chosen PC transfer.
This is not a general memory-safety proof of undiscovered code, but there is no
remaining known UDS/proprietary/factory-test service to mine for a straightforward
runtime call primitive. No Techstream engineering/calibration operation recovered
to date improves this bound. The current Techstream/GTS+ host corpus also supplies no OEM-facing name
that turns F33 RID `0x100F` into a general signer service. Its relevant `0x7F7`
host evidence is instead bounded to Unified CUW/reset choreography: after ECU
reset an EachArea writer emits raw `0x7F7 || FE 10 81` as one post-reset tail
frame. That proves Toyota tooling knows the route family, but not that Techstream
exposes the application's arbitrary XCP `DOWNLOAD` as a normal runtime engineering
function; the F33 firmware bytes above remain the authority for that write path.

### 13.5 Control-transfer audit: the missing primitive

CORR-123 refreshes this audit against the current first-class **6,065-function**
F33 project. `ExportIndirectControlTransfers.java` now reports **496** decoded
indirect transfers total (**403 `jarl` + 93 `jmp`**) and **487** in application
CodeFlash (**395 `jarl` + 92 `jmp`**). `ClassifyComputedCallTargets.java` classifies
**495 / 487** respectively; the one total-count difference is the reset thunk
`jmp 0x1E1E[r0] @ 0x32`, which has no containing function and is outside the
application region. This supersedes the older 312/305 scratch-corpus denominator.

Of the 495 classifier sites, **161** have a nearest defining load with a direct
operand reference: 152 reference CodeFlash/data objects, **9** reference lower-RAM
cells, and **zero** reference `FEBF7C00..FEBFFBFF`. Another 330 have a locally
resolved register/field definition without an operand reference; the remaining
four exceed the local 24-instruction backtracker and are closed separately below.
The nine directly referenced lower-RAM sites reduce to five concrete cells, all
below the XCP floor: boot-only `FEBF0FD0` (`0x435E/0x437C/0x440E`), `FEBF6B04`
(`0x73EE6`, with writer `0x73EEE` selecting only fixed CodeFlash `0x766F4/0x767EA`),
`FEBF117C`, `FEBF1194`, and `FEBE5628`. The `FEBE5628` service callback is derived
from fixed CodeFlash service configuration; recovered request bytes do not become
a function address. Thus the stronger current census adds lower-RAM dispatch state
but still recovers **no XCP-writable call-source cell**.

A separate Ghidra reference census finds no recovered static reference into
`FEBF7C00..FEBFFBFF`, and a raw whole-CodeFlash u32 census finds **zero embedded
pointers into `FEBFF9F0..FEBFFBFB`**. In particular, no recovered scheduler/task,
diagnostic, CAN Tx/Rx, PDU, CryptoIf/ICU-S, OS, interrupt/vector, or saved-PC cell
inside the XCP-writable region is currently available to hook as
`original -> RAM trampoline -> signer -> original`.

The four application computed-call sites that the local 24-instruction provenance
backtracker could not initially close (`0x8863E`, `0x8AF7A`, `0x8AF88`, `0x8AFAA`)
are now resolved too. Their targets come from callback cells
`FEBF117C/FEBF1180` and `FEBF131C/FEBF1320/FEBF1324`, all far below the XCP write
floor. Recovered writers install only fixed CodeFlash callback addresses and matching
bitwise-complement guards; no tester-derived callback address reaches those cells.

The exception-return route is likewise bounded. The current decoded census is exactly
**eight** returns: `eiret @ 0x20102`, `feret @ 0x65C60`, and `eiret` at
`0x71372/0x71456/0x71502/0x715AE/0x71A90/0x71C40`. The old scratch address
`0x200C8` is not an instruction in the first-class project and is superseded by
CORR-123. Application context initialization starts at `SP=FEBE2000`; the FERET
wrapper `0x65BD4` saves FEPC/FEPSW/FEIC/FEWR on the interrupted stack, while
wrappers around `0x713B0/0x7145C/0x71508` save EIPC/CTPC state and use fixed
temporary ISR stacks `FEBE0800`, `FEBE1000`, `FEBE1800`, and `FEBE2800`. Every
recovered saved-PC frame is therefore below `FEBF7C00`, and the direct-flow census
still reports zero edges into the XCP window.

The obvious DMA composition is now closed target-natively as well. Seven fixed
F33 application DMAC descriptor families (22 total 0x28-byte records, **88 endpoint
fields**) are consumed by the recovered setup callers around
`0x60462/0x60C20/0x61B90/0x628B2`; `0x60A6A` is the only recovered application
channel-register programmer and `0x60A10` performs fixed global setup. **Zero** of
the 88 endpoint fields enters `FEBF7C00..FEBFFBFF`, so the recovered fixed-DMA
paths cannot synthesize a callback/PC object there.

CALLT-base retargeting is now closed against the **entire exact 1-MiB image**, not
merely the discovered Ghidra listing. Decoding the repository RH850/E3 LDSR format
(`op0510=0x3F`, system-register id 20, `op1626=0x20`, selector 0) at every 2-byte
aligned image offset finds exactly one CTBP writer: `ldsr r0,CTBP @ 0x25E`. It sets
CTBP to zero. There is no nonzero CTBP writer in the image, so CALLT cannot be turned
into an XCP-RAM dispatch table by application/tester state.

The other CPU-routing-register composition is closed too. Application context setup
at `0x715B4..0x715E3` loads the **fixed immediate** `0x20200` into `INTBP` at
`0x715BC`, the **fixed immediate** `0x20000` into `EBASE` at `0x715C8`, then installs
fixed `GP=FEBEB800`, `TP=0x23DFC`, and `SP=FEBE2000`. It is not a parameterized
vector-base setter. Raw FEPC-like opcode patterns found in undiscovered/data bytes
were not promoted because they are absent from the recovered instruction stream.

Finally, the **entire configured standard XCP DAQ bank** has been decompiled. The
configured DAQ commands are `E3/E2/E1/E0/DE/DD/DA/D9/D8/D7`; `WRITE_DAQ @ 0x82510`
stores a tester-selected *measurement source address* in lower-RAM ODT state, while
`0x82368` later dereferences that source and copies one byte into DTO staging.
`SET_DAQ_LIST_MODE @ 0x82616` rejects the recovered STIM/direction mode bits. There
is no recovered write-through, callback installation, or branch through a DAQ address.
The potentially useful standard commands `SET_REQUEST`, `USER_CMD`,
`TRANSPORT_LAYER_CMD`, `DOWNLOAD_NEXT`, `DOWNLOAD_MAX`, and `SHORT_DOWNLOAD` are
unmapped in this F33 command map.

At this point the **recovered stock application pivot classes are statically
exhausted**: direct/indirect callbacks, exception saved PCs, CALLT/CTBP, EBASE/INTBP,
fixed DMA, calibration paging, full XCP/DAQ, ECUReset, WDBI, all RoutineControl RIDs,
and proprietary `AB/BA` have no route from tester-controlled state to the high-tail
PC. The remaining negative is deliberately narrower: synthesized/computed aliases
not represented by recovered references, a memory-safety bug not represented by the
recovered CFG/dataflow, a separate undiscovered DMA/hardware mutation mechanism, or
undiscovered code. The repository therefore does not emit an execution PoC that
guesses a branch target.

### 13.6 Concrete production disposition and minimum next observations

Ranked disposition:

1. **Application XCP `DOWNLOAD` + future volatile callback pivot** — best design.
   Byte placement, tail retention/execution, MPU geometry, zero-persistence lifetime,
   and exact controller-1 physical routing are closed; live transport admission/write
   reachability and PC transfer remain open.
2. **RID `0x100F` stock command-5 path** — real and non-disruptive, but only an
   internal fixed-16-byte crypto test/oracle, not a general SecOC signing API.
3. **UDS `34/36/37` / programming loader** — rejected for production because it
   requires the network-visible PROGRAMMING transition.
4. **Persistent flash hook** — fallback only; current evidence does not justify
   taking it while the application-mode XCP placement surface remains promising.

We do **not** yet have enough evidence to implement the complete installer,
because the execution half is missing. The recovered static stock surface no longer
contains an obvious next pivot candidate, so the minimum useful live work separates
**placement** from **execution discovery**:

1. on the statically proven normal-harness bus-1/controller-1 route, snapshot the
   exact XCP admission state with read-only SID `0x23` (`FEBE3DE5/FEBE3DF2`,
   `FEBE4914..493A`, `FEBE4EE6`, `FEBE4FAE`) and then repeat CONNECT only if the
   transport is observed admitted;
2. if CONNECT responds, use a bounded `SET_MTA + DOWNLOAD + SHORT_UPLOAD` readback
   inside the already-proven high tail to close actual application-context write
   reachability without executing those bytes;
3. for the execution blocker, collect a non-executing runtime RAM/control-flow
   discriminator capable of exposing a mutable continuation/callback/task object or
   a previously unrecovered hardware/software trigger. A useful observation is a
   before/after RAM snapshot plus control-flow/registration trace around benign stock
   diagnostic/task activity, with special attention to lower-RAM callback/task state;
4. do **not** attempt an arbitrary PC write or RAM execution until such a concrete
   mutable object has a known setter, invocation condition, and restore semantics.

In other words, additional broad static searching is now lower-value than a targeted
runtime discriminator. XCP reachability/readback can close the placement transport,
but it cannot by itself solve the execution half.

The deterministic assessment is
`data/generated/camry_8965F3307000_application_ram_loader_assessment.json`, generated
by `tools/build_camry_8965F3307000_application_ram_loader_assessment.py` and locked
by `tests/verify_camry_8965F3307000.py`.

Production steering output remains disabled.

## 14. Exact F33 persistent Gate-2 development patch

The non-persistent signer architecture in §13 remains the preferred production
design, but it is no longer a prerequisite for **development lateral**. A fresh
bare-CodeFlash import of exact `8965F3307000` (SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`) now
recovers the same SecOC Gate-2 predicate shape target-natively. The resolver finds
exactly one candidate, owner `0x8F906`, and resolves the final predicate as:

- `0x8F952: e0 d1` — `cmp r0,r26`;
- `0x8F954: 9a 0d` — branch to the mismatch arm when the materialized verify result
  is nonzero;
- verified-result zero falls through at `0x8F956`; both arms retain their stock
  calls and converge at `0x8F96E`.

The deterministic development bypass is therefore **`0x8F952 e0d1 -> e001`**,
turning the compare into same-register `cmp r0,r0` while leaving the BNE and both
arm bodies intact. This is the same *operation* recovered on older P1M-E images,
but the address and integrity repair are derived from the exact F33 bytes rather
than transferred from another calibration. The semantic result is retained in
`data/generated/secoc_gate_resolution_8965F3307000_minimal.json`.

F33's own two self-describing boot CRC regions are both stock-valid. The Gate-2
word lies in `[0x18000,0xFFDF0)`, whose stock terminal fixup at `0xFFDEC` is
`0xD8C376EB`. After the two-byte predicate change, the exact recomputed prefix CRC
is `0x2650CC50` and the required terminal fixup is **`0xD9AF33AF`**, restoring the
Toyota residue to `0xFFFFFFFF`. `data/generated/secoc_patch_manifest_8965F3307000.json`
binds the image SHA, patch preimage, `0x88000` erase block, CRC geometry, and
repaired residue. Offline apply followed by the generated inverse restore returns
byte-for-byte to the original 1-MiB image and its original fixup.

The persistent-write backend is now closed one level farther as well. Exact F33
boot routine `0x78E2A` writes each FACI program halfword and then tests
`FSTATR & 0x400`; target-native helpers retain FRDY `0x8000`, Status Clear `0x50`,
and Forced Stop `0xB3`. Independently, locally retained Toyota `T-0035-22.cuw`
decrypts/CMAC-validates both manufacturer F340 erase routines and proves the same
post-write **DBFULL bit10 / `0x400`** pacing plus `0x7040` FSTATR error family,
correcting the earlier external bit11/SUSRDY interpretation. The generic backend
now performs bounded post-write DBFULL polling; see SECOC-074/CORR-121. T-0035 is
still a Tundra F340 package, not an exact F33 full-reflash package.

This closes the **offline patch construction** and recovery contract, not the live
behavioral proof. The generic patcher can validate the exact preimage/CRC in RAM
before any flash operation and is restore-gated for APPLY. A live F33 run must still
perform zero-write preflight first, bind application F181/route to the exact car,
retain a separately validated restore artifact, apply the target block and CRC block,
then prove the intended SecOC consequence with an unsigned/invalid-MAC B6 experiment.
Until that live causal step, `SecOC bypass works on F33` is not promoted beyond the
recovered Gate-2 semantics.

A 2026-08-30 sequence of live validate-only attempts exposed several independent
tooling defects before any flash write. The old-stack DID `0x0203` selector was wrong,
the generic patcher had been linked at VMA 0 despite absolute intra-payload addresses,
the shared FF00 path omitted the retained pre-trigger Panda RX clear/10-ms settle, the
generic callback had transferred unverified boot-RAM helper/scratch assumptions, and the
shared handoff duplicated a retained successful helper. Each issue is fixed on its own
static or retained-success evidence.

A full OFF→READY power cycle after the persistent APPLY is now also dynamically closed. A dedicated validate-only post-reboot payload, bound to the independently simulated patched-image SHA-256 `272843a2c1d179f91105d7f103f213034f850dc476c96dad48067fbf3afd9f65`, observed exact application F181 `8965F3307000 / 8A3113303100`, patch bytes `E0 01` at `0x8F952`, fixup `D9AF33AF` at `0xFFDEC`, patched CRC prefix `2650CC50`, and full residue `FFFFFFFF`, with zero mismatches and `verified=true`. This proves persistence of the write+CRC repair across reboot; it does not yet prove that an invalid/zero-MAC28 B6 is accepted by the patched Gate-2 path. The retained artifact is under `targets/camry-2026/raw-20260830/secoc-patch-post-reboot-verify/`; see SECOC-083.

The critical telemetry interpretation changed afterward. Current Panda Python returns raw
CAN rows as **3-tuples `(address, data, bus)`**, but `execute_ram_payload()` required
`len(row) >= 4`; it therefore discarded every current Panda frame before testing for
`0x7A9`. Consequently, all earlier shared-run `telemetry_frames=0` results are invalid as
payload-execution negatives and cannot establish which of the independently found defects
was causal. The collector now accepts length>=3 and decodes address from field 0 and
data/bus from the last two fields, retaining compatibility with wider historical tuples.

A positive control independently proves the current physical/software route. The exact
retained Aug-26 Calvin payload was changed at only three plaintext bytes so its loop upper
bound became zero; callback/descriptor/CRC/CMAC remained valid. Through the retained
Aug-26 host lifecycle on the current post-repin **Panda bus 0**, it returned address
`0x00000000` / CodeFlash word `0x06E0001F` in **6 ms** with zero SPI errors. On-device
hashes confirm opendbc ISO-TP/UDS, Panda Python/submodule, and `tsk/lib/programming.py`
match the working Aug-26 versions. The repin, bus0 callback transport, and dependency
stack are therefore exonerated. The shared runner now also reuses that retained handoff
helper, but CORR-145 withdraws the earlier claim that the duplicate handoff itself caused
the zero counts because that comparison used the blind collector. See SECOC-078/079 and
CORR-144/145. No persistent flash write has occurred.

The first retry after fixing the collector closes the zero-write preflight dynamically. On
post-repin Panda bus 0, the exact F33 application and boot identities matched, the patcher
emitted **35** host-visible telemetry events, and the run reached `SUCCESS` then `DONE`.
Every live value matched the offline manifest/image with no mismatches: patch VA `0x8F952`,
patch block `0x88000`, block size `0x8000`, CRC range `0x18000..0xFFDF0`, fixup VA
`0xFFDEC`, fixup block `0xF8000`, preimage `E0 D1`, stored fixup `D8C376EB`, CRC prefix
`273C8914`, and residue `FFFFFFFF`. The retained `preflight.json` therefore records
`boot_crc_valid=true`, `payload_success=true`, and **`apply_ready=true`**. This is the
first dynamic proof that the current F33 target/route and generic patcher agree on all
read-only APPLY prerequisites; it is not yet proof of a persistent write or SecOC bypass.
The run is retained under
`targets/camry-2026/raw-20260830/secoc-patch-preflight-f33-collector-fixed/`; see SECOC-080.

Before persistent APPLY, the recovery side is now executable rather than artifact-only.
`exploit/patcher/restore.py` validates the exact hash-bound RESTORE package and can use
the ordinary field-proven application→boot handoff or, specifically for the unavoidable
two-block power-loss window, an already-running bootloader **only after exact boot F181
match**. Its prepare-only F33 plan validates restore payload `d8c5b3dc…`, semantic
preimage `E0 01`, replacement `E0 D1`, and the same `FEBF0000/0x1000` authenticated
geometry. Direct-boot recovery remains implementation-verified rather than dynamically
exercised because intentionally creating an invalid-CRC power-loss state would be unsafe;
see SECOC-081.

A later 2026-08-30 **persistent APPLY** then completed after the successful collector-fixed preflight authorized the exact same image/manifest/template/restore tuple. The live payload reported target readback `E0 01` at `0x8F952`, CRC prefix `0x2650CC50`, computed and stored terminal fixup `0xD9AF33AF`, final residue `0xFFFFFFFF`, and terminal `SUCCESS`/`DONE`, with 65 telemetry events and no errors. The run is retained under `targets/camry-2026/raw-20260830/secoc-patch-apply-f33-final/`. This proves the target-byte and CRC write sequence completed, but **does not yet prove reboot persistence or SecOC bypass behavior**; those remain explicitly gated on post-power-cycle verification and an invalid/zero-MAC28 B6 causal test. See SECOC-082.

For the lateral project this changes ordering: the persistent development patch can
remove signing from the first-actuation critical path. The RAM-only signer work in
§13 remains the clean production replacement after B6 construction, relay source
suppression, steering response, override/current policy, and fault recovery have
been validated.


## 15. Current GTS+ `EMPS_P5` semantic join

Current GTS+ provides a direct Toyota naming join for the exact F33 diagnostic table
without transferring names from a related calibration. The current Toyota master maps
Camry-HV vehicle types **12704, 12862, and 12984** to generation-20 category **405
`EMPS_P5`**. Relative to V18, current `EMPS_P5` expands type 62 from 222×64-byte
records to 230×80-byte records while preserving a 214-key mirrored Data Monitor
subset. The exact F33 RDBI table at `0x2928C` contains 241 records, of which **121**
have names in current GTS+. High-value exact joins include DID1035 Steering Wheel
Torque (`0x4DB70`), DID1036 Steering Angle Velocity (`0x4DBBC`), DID1037 Steering
Angle (`0x4DBF8`), DID1151 Motor Actual Current (Q Axis) (`0x4E394`), DID1152
Command Value Current (Q Axis) (`0x4E3D0`), DID1185 CAN Vehicle Speed (SP1)
(`0x4E5A8`), DID1C02 Command Value Torque (`0x4E7D6`), and DID1C03 Control State
Information (`0x4E81E`).

DIDs `0x1C05` and `0x1C0C` both use exact callback `0x4E848`. Current GTS+ names
the low/high 32-bit halves **ASIC State Information / ASIC State Information 2**
(and System-2 equivalents). Canonical Ghidra references prove the callback reads
`FEBE8298` and `FEBE829C`; the retained post-handoff RAM snapshot contains
`40 00 C0 00 00 00 00 00` across those words. Individual bit meanings are not
resolved, and that post-handoff value is not promoted as READY-mode state.

Two important non-transfers remain explicit. Current-only `Target Lateral ID` DIDs
`0x1CEE/0x1CEF` are **absent** from exact F33, so those names are not assigned to
this calibration. Current GTS+ also adds behavior `X2436 = Beta Cooperative Control
Transmission Counter Malfunction`; this is diagnostic vocabulary, not proof of a
wire-field or SecOC-signer implementation. The complete machine-readable join is
`data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json`.

## 16. Relay-correct 2026-08-27 captures: topology closed; B6 repeatedly not observed

The maintainer physically exchanged the Toyota-B CAN0/CAN1 pairs before this
pass. A passive 10.000003-second census immediately closes the hardware effect:
the steering/state family that the unmodified harness exposed on logical bus 1
now appears on **both sides of the harness CAN0/CAN2 relay pair**. The first post-repin capture
counts are 13,910 / 3,938 / 13,910 frames on buses 0/1/2 with 153 / 22 / 153
ID-DLC streams; buses 0 and 2 are byte-for-byte sequence-identical. Exact
`0x00F/8`, `0x025/32`, `0x030/32`, and `0x0D7/32` counts are respectively
100, 1000, 1000, and 500 on each relay side and zero on bus 1. A separate
READY/parked pass retains the same split at 165 / 22 / 165 streams and observes
`0x51E B0[7]=1` on both relay sides. This is the first direct Camry proof that
the physical repin puts the exact F33 steering network on comma's intercept
topology rather than merely reaching it diagnostically.

The normal comma logger then retained nine route segments. To avoid retaining
location/video/private route metadata, the tracked evidence is reduced to exactly
**1,656,656 incoming CAN frames** (`src < 128`) in
`targets/camry-2026/raw-20260827/camry_relay_route_can_20260827.ndjson.gz`.
Raw `0x0AA` wheel-speed decoding proves continuous movement in segments 4-6;
segment 5 is entirely D (`0x127` raw 3) and spans 32.66..42.88 km/h. The exact
same-car FRC diagnostic/CAN join from §7.2 independently recognizes factory
`0x0FE/32` interaction in that moving segment: MAIN toggles at about 16.54 s
and 33.40 s from the first segment-5 `0x0FE`, while SET- is pressed around
19.53 s and 20.10 s. Thus this is not another stationary/no-input negative.

The surprising result is exact: there is **zero `0x0B6` at every DLC on every
incoming bus across all nine segments**. In the same route, protected `0x00F`
and `0x0D7` remain healthy on both buses 0 and 2 in every segment (for example,
segment 5 has 600 `0x00F` and 3000 `0x0D7` frames per relay side). A structural
`0x08A/32` state changes around the validated MAIN/SET interactions, but exact
F33's receive descriptor table does not accept `0x08A`; it is therefore retained
only as cross-ECU state corroboration, **not** promoted as an EPS lateral command.
No alternative steering-command carrier is assigned from this capture.

A second deliberately requested drive then reproduced the negative rather than
resolving it. Its privacy-minimized artifact retains **1,918,047 incoming CAN
frames across ten additional loggerd segments (16..25)**. Segments 18 and 20-22
are continuously moving above 2 km/h; segment 20 alone spans 65.310..72.493 km/h.
The same-car `0x0FE` join sees repeated MAIN interactions in segments 16/18/19/20,
and the structural `0x08A/32` tuple changes in segments 18-21. Nevertheless the
second drive again contains **zero `0x0B6` at every DLC on every incoming bus**,
while every segment retains protected `0x00F` and `0x0D7` on both relay sides.
Across the two drives the exact retained total is therefore **3,574,703 incoming
CAN frames / 19 route segments / zero B6**. This makes the live absence a repeated
bounded negative rather than a one-route acquisition accident.

The acquisition boundary still matters. The operator reported apparent factory steering
assistance during the first drive and deliberately retried the experiment on the
second, but neither capture simultaneously polled an OEM-named LTA-active state.
Raw CAN proves movement, D, control-button interaction, healthy protected traffic,
and the complete repeated B6 negative; it does **not machine-prove the exact
interval in which factory lane centering was actively applying steering**. Exact
F33 firmware independently still configures `0x0B6/32` as protected PDU44 and
unpacks its selector/target-angle fields into the recovered cooperative-control
path, so the repeated negative does not retract §§9.1-9.3. It changes the next
dynamic step: before assuming that an active-LTA B6 template merely remains
uncaptured—or before concluding stock LTA uses some other path—we must synchronize
the FRC's own P5 lateral state with the relay-correct CAN.

That was the §16 acquisition-time boundary. CORR-129/VAR-081 later re-enumerate the
same raw logs and strongly identify their two B21=`11` intervals as LTA/LCA active
from the current EMPS Target-Lateral numeric dictionary plus the repeated three-state
dynamic join. They still do not prove byte-exact producer mapping or isolate when
lane-centering torque was applied; synchronized FRC state remains an independent
cross-check and term-attribution experiment rather than a prerequisite for naming
the captured state.

Toyota/GTS+ gives a direct oracle: FRC DID **`0x1601`** contains `LTA Switch
Condition Flag` in bits 0-7 and **`LTA Control Condition`** in bits 8-15, with
Hands-Off customize/control in bits 16-31. Useful companion reads are `0x1501`
(LDA customize/control), `0x1681` (LCA customize/control), and `0x1903` (`Control
Mode`). The current P5 Data List transport is ordinary `22 <DID>` / `62 <DID>`;
response bytes must be independently checked against the requested DID.

A separate direct-Panda logger attempted during the drive collided with the
already-running `pandad` and terminated on Panda USB **`CHECKSUM_ERROR`**. It is
not used as evidence. All drive conclusions above come from normal `loggerd` rlogs
reduced deterministically to the tracked CAN-only artifacts.

The next synchronized capture is now implemented without repeating that ownership
mistake. `kai-openpilot@248777d0a` adds DEVELOPMENT_ONLY
`ToyotaTSS3FrcOracleCapture` inside passive exact-F33 `card`: it reuses `card`'s
single existing `sendcan` publisher while normal `pandad`/`loggerd` stay alive,
requires `ControlsReady=false` at configuration plus one runtime Panda in ELM327
parameter 1 with controls disallowed, and can emit only fixed post-repin Panda-bus0 `0x792` SID-`0x22` reads for
`0x1601` and `0x1914`. A two-second exact-positive watchdog for each DID stops
failed/stale polling. The bus is fixed rather than probed because VAR-064's
relay-correct 2026-08-27 sweep directly reaches FRC `0x792` on Panda bus0. VAR-052's
older normal-harness bus1 route was pre-repin, while VAR-066/current-GTS+ “Bus 1” is
a Central-Gateway topology label rather than a Panda bus number. These namespaces
must not be conflated. `tools/extract_camry_frc_lta_rlog.py` reduces explicit normal
rlog segments into the same privacy-minimized `can.bin`/`oracle.ndjson` shape used
by `tools/analyze_camry_frc_lta_capture.py`; the reducer retains incoming CAN and
only those two matching FRC requests. This is verified capture **tooling**, not a
new live-car result: no synchronized `0x1601/0x1914` driving artifact is claimed yet.
Deterministic interpretation of the two completed blind drives remains
`data/generated/camry_2026_relay_correct_capture.json`, verified by
`tests/verify_camry_2026.py`. Production steering output remains disabled.

## 17. 2026-08-27 live DTC clear: physical UDS plus legislated OBD Mode 04

A parked/READY live pass after the EPS development experiments closes the exact
DTC source behind the maintainer car's `Hybrid System Malfunction` warning and
also closes the practical Comma-side clear route. The direct post-repin P5 sweep
found 11 responding ECUs on bus 0. Before clearing, exactly five records carried
any failure/pending/confirmed/failed-since-clear/warning status bit (`status &
0xAF != 0`). Four were raw DTC `C13187`, which current GTS+ names **U0131-87
`Lost Communication with Power Steering Control Module` / `Missing Message`**:
Hybrid Control `0x7D2` status `0x28`, Brake/EPB `0x7B0` status **`0xAC`**, Air
Conditioner `0x7C4` status `0x28`, and Front Recognition Camera `0x792` status
`0x28`. Brake's `0xAC` includes `warningIndicatorRequested` (bit 7), while the
current-failure bits 0/1 are clear; this is exactly the shape expected for a
historical EPS-offline event that can continue requesting a dash warning after
communication has recovered. A fifth non-U0131 record (`561854`, status `0x20`)
was present at `0x7A2`.

The clear transport is not uniform across these controllers. Physical UDS
`ClearDiagnosticInformation` **`14 FF FF FF`** succeeded directly on `0x7A1`,
`0x7B3`, `0x7C4`, `0x7D0`, `0x792`, and `0x7A2`. It was explicitly rejected as
service-not-supported, in both default and extended diagnostic sessions, by
Engine `0x700`, Motor Generator `0x724`, Hybrid Control `0x7D2`, HV Battery
`0x747`, and Brake/EPB `0x7B0`. Sending raw service `04` physically to those same
addresses was also rejected, and sending it one-at-a-time to their VDS
`FuncAddress` values (`7E0/7E6/7E2/7E3/7E5`) timed out. Those negative routes are
retained because they prevent us from regressing back to the tempting but wrong
"just use SID 14 everywhere" or "send Mode 04 to each FuncAddress" implementations.

Techstream/GTS+ explains the split. Current GTS+ binds categories 372 Engine,
395 Motor Generator, 397 Hybrid Control, 398 HV Battery, and 435 Brake/EPB to
role-`0x19` (25) **`DelDiagCodeP4.dll`**. Its current master exposes clear selector `0x01`
for all five and selector `0x102` for Hybrid/Brake. The independently decoded V18
master resolves selector `0x01` exactly to **send `04`, expect `44`**; its
Hybrid/Brake `0x102` fallback resolves to **send `14 FF FF FF`, expect `54`**.
The exact car then closes the transport interpretation dynamically: a harmless
functional OBD Mode-01 PID-00 probe on **`0x7DF`** receives replies from `0x7E8`,
`0x7EA`, `0x7EB`, `0x7ED`, and `0x7EE`. Sending the standard single-frame
functional **Mode 04** request `01 04 00 00 00 00 00 00` on `0x7DF` receives
positive `01 44 ...` replies from all five IDs. The existing VDS Address/
FuncAddress join identifies them respectively as Engine, Hybrid Control, HV
Battery, Brake/EPB, and Motor Generator. Thus on this exact Camry the Techstream
P4 clear for the legislated controllers is a **functional `0x7DF` OBD Mode-04
broadcast**, not a physical `7D2/7B0` UDS transaction.

The final direct sweep is the acceptance criterion rather than the positive clear
response alone. All 11 responding ECUs report **zero records with `status & 0xAF
!= 0`** after the physical-UDS plus functional-Mode-04 sequence. In particular,
the U0131 confirmed/failed-since-clear/warning state is gone. The retained source
JSONs and privacy-safe live manifest are under
`targets/camry-2026/raw-20260827/dtc-clear/`; deterministic summary is
`data/generated/camry_2026_dtc_clear.json`.

For a reusable Comma maintenance tool, the exact-vehicle safe shape is therefore:
read and preserve DTC status first; use physical `14 FF FF FF` where supported;
use functional `0x7DF` Mode 04 for the legislated P5 responder set; then re-read
all reachable controllers and fail the operation if any fault-status bit remains.
This live operation performed no steering transmission, SecurityAccess,
RoutineControl, firmware write, flash erase, or programming operation.

## 18. Exact-F33 inverse lateral ingress audit: no observed ordinary-COM alternative to B6

The repeated zero-B6 drives in §16 justify the inverse question: instead of assuming a
stock steering CAN ID, start from the exact F33 steering-command implementation and ask
which external generated-COM fields can reach it, then intersect those candidates with
the retained relay-correct traffic. This pass uses the exact 43-record application Rx
table at `0x21FE8`, all **116** scalar `FUN_0007D12A` receive extractions, the
signal-to-PDU and PDU-offset tables, the GP-relative `0x58074 -> 0xBCD66` staging/snapshot
maps, current GTS+ names, and both retained drives.

The hardware acceptance denominator is also exact, not inferred from the COM table.
RSCFD controller 1 owns exactly 47 rules at `0x230B8`: rules **0..42** match the 43
normal Rx descriptors one-for-one and in the same arbitration-ID order; rules 43..45 are
only physical/functional/secondary diagnostics `0x7A1/0x777/0x7A0`; rule 46 is packed
application XCP `0x7F7`. Thus there is no hidden direct CAN acceptance ID on the exact
steering/diagnostic controller outside the normal-COM denominator.

The receiver also answers the more important source-domain question directly. Exact F33
communication-monitor dispatcher `0x3CBE8` / scheduler `0x3CCBE` walks the six rows at
`0x280A4`. Row 5 is `00004301051aa506`: status slot `0x1A`. The exact status-map table
at `0x28FE4` maps slot `0x1A -> PDU44`, and PDU44 is protected `0x0B6/32`. Loss of that
row selects Dem event `0x0143`; its exact F33 event record selects DTC index 82 / packed
`0xC12987`. Current GTS+ names that DTC **U012987 `Lost Communication with Brake System
Control Module` / `Missing Message`**. So this is not merely an H transfer: the exact Camry
EPS itself expects B6 as **Brake System Control Module traffic** on its controller-1
receive network. CAN has no source-node field, so the receiver cannot identify the unique
transmitter implementation beyond that monitored module relationship. Section 19 now
closes the stronger topology fact independently: Toyota's own current Camry CAN model
places Skid Control and EPS together on Central-Gateway Bus 4, while the front-camera
sensor domain is on Bus 1. The DTC therefore identifies the immediate logical source
domain, not by itself the ECU that computes, transforms, or signs the lane target.

The corrected pinned copy-edge census starts from all **116** exact scalar extracts and
follows only exact raw→`0x58074` stage→`0xBCD66` snapshot edges and their consumers. It
has exactly **19 nonempty signals**:
`{130,141,186,187,188,189,211,212,213,223,243,261,262,263,265,268,269,270,273}`;
the remaining **97 are empty under this model**. B6 signal261 is the sole recovered mode
selector and B6 signal262 the sole recovered command magnitude. The other B6 members are
gates, sequencing, or contribution state; every non-B6 member is feedback, monitor,
plausibility, or gate state. In particular signal243 (`0x0D7` B0[7]) uses the explicit
stack RMW at `0x4BB62`, then the exact chain
`FEBE80A0 -> FEBEF094 -> FEBEACCD`. This census replaces the older nine-field
signed-width filter: that filter remains a useful candidate view, but it is not the
command-cone denominator or result. Its observed non-B6 candidates are closed without
assigning semantics from correlation alone:

- `0x025` signal187 is the already-proved **Steering Angle** feedback and signal189 is
  **Steering Angle Velocity**; they are measured-state inputs, not a command target.
- `0x115` signal134 is signed16 B0:B1. Exact dataflow is
  `FEBE8014 -> FEBEF194 -> BE622/BE65C -> FEBEBE82 -> BF3AA -> FEBEE890`, and exact F33
  RDBI callback `0x4DAEE` exposes that terminal as current-GTS+ DID `0x1032`
  **Engine Revolution**. The two drives exercise 47,384 bus-0 samples, raw range
  `0..2884`, with 1,743 distinct values. This is engine-domain input, not lateral command.
- `0x0D5` signals212/213 are signed16 B1:B2 and B3:B4. Their GP-relative staging uses
  saturating copies `FEBE8072/8074 -> FEBEF1BC/F1BE -> FEBEAE04/AE06`; consumers
  `0xC9D18/0xC9CAA` are absolute/threshold monitor paths with exact thresholds 100/1000
  and DEM event calls `0xC9/0xC8`. Both exact F33 event records are unpopulated
  (`class=0`, DTC index 0). Live signal212 remains only `-5..11`; signal213 is exactly
  zero over all 55,793 bus-0 samples. These are monitor/plausibility channels, not a
  recovered target or torque command.
- `0x1C5` and both `0x64F` command-sized fields are accepted by exact F33 but have zero
  frames in both relay-correct drives, so they cannot explain steering observed in those
  logs.

The non-scalar escape hatch is also bounded. Exact F33's generic COM group-copy primitive
`0x7E72A` is called only by `0x693FE/0x697F4`; its configured signal IDs `0x5A..0x67`
map only to CAN `0x013..0x01F`. Every one of those PDUs is absent in both drives. This
prevents replacing the scalar result with an opaque/group payload on an observed normal
EPS CAN frame.

Conversely, the B6 branch gains a downstream target-native check. The protected B6 target
snapshot `FEBEAE90` enters `0xCBA80`; the selected command composition/scaling chain then
reaches `FEBECC62 -> FEBEAC56 -> FEBEE40A -> FEBE6772`, and exact callback `0x4E7D6`
exports the terminal through current-GTS+ DID `0x1C02` **Command Value Torque**. This is
not merely a width/name inference: it is a positive code path from the already-proved B6
target-angle state toward Toyota's named steering-command observable.

Therefore **no observed ordinary EPS generated-COM field other than B6 is identified as a
value/mode input to the recovered `FEBECC50/FEBECC62` Command-Value-Torque model cone**,
controller-1 hardware acceptance contains no extra direct-CAN candidate outside that COM
surface, and exact F33 independently labels B6 loss as **Brake System Control Module /
Missing Message**. CORR-130 now makes the important downstream boundary explicit: this
proves an internal Toyota-named command-value observable/model path, **not** that
`FEBECC62/FEBEAC56` is the universal physical motor-current/PWM actuation convergence.
DMA/peripheral mutation, diagnostic/debug paths, computed aliases outside the recovered
maps, and downstream/current-reference paths remain separate questions. The separate
bus-1 `0x180..0x18C` CAN-FD family remains a plausible *upstream* FRC/Brake planning or
transfer surface, but none of those arbitration IDs exists in exact F33's normal Rx table,
so it cannot directly be the EPS normal-CAN steering command.

FRC DID `0x1601` remains a useful independent exact OEM-state oracle. Current GTS+ resolves its value
dictionary as **`LTA Switch Condition Flag=1 (ON)` plus `LTA Control Condition=0 (LTA
Enabled)`**; `1=LTA Disabled`. Current GTS+ also resolves `0x1914` bit8 as **0=“Cruise
Control Not in Operation” / 1=“Cruise Control in Operation”**. Section 20 now supersedes
the older need to use `0x1914` merely to prove cruise operation: the retained CAN itself
recovers that state from `0x08A` plus its set-speed behavior. The prepared normal-loggerd
poller remains useful to cross-check VAR-081's independently identified LTA/LCA-active
state and to corroborate `0x1914`; it is mechanically read-only (`22 16 01` /
`22 19 14` only) and stops if either exact positive response stream is absent/stale for
two seconds. Do **not** wait for that independent capture before investigating the actual
steering path: §20 already establishes zero B6 during machine-recovered cruise operation
and the two complete LTA/LCA-active intervals. Move the RE boundary outward to the
FRC/Brake transformation and inward to the residual non-COM/internal EPS paths in
parallel. Deterministic evidence is
`data/generated/camry_8965F3307000_external_lateral_ingress.json`, generated by
`tools/build_camry_8965F3307000_external_lateral_ingress.py` and verified by
`tests/verify_camry_8965F3307000_external_lateral_ingress.py`. Production output remains
disabled.

## 19. Current GTS+ CAN topology closes the B6 bus question

The zero-B6 result in §16 raised a hardware-topology alternative: perhaps the Toyota-B
camera connector exposes only an ADAS/gateway view while protected B6 actually lives on
a separate Brake↔EPS segment that the comma cannot see. Current GTS+ contains Toyota's
own **CAN Bus Check** topology tables, so this can be tested against the exact current
Camry family instead of inferred from message names.

The relevant current master tables are now class-resolved as
`CDbCanBusCarIdTable` (75), `CDbSubBusConfirmationCGWTable` (76),
`CDbCanBusOptionTable` (77), `CDbCanBusComponentTable` (78),
`CDbCanBusNameTable` (79), plus `CDbCanBusListTable` (55). The three current
Camry-HV vehicle types already joined to category-405 `EMPS_P5` in §15 —
**12704, 12862, and 12984** — each select the same CAN topology key
**`0x00A7D910`**. That key has 18 option variants. Every variant resolves to the
same 31 component placements; the three steering/ADAS placements that matter here are
invariant:

| Toyota component | component | Central-Gateway bus |
|---|---:|---:|
| Front Camera Module | `0x6D` | **Bus 1** (index 29) |
| Skid Control (ABS/VSC/TRAC) | `0x29` | **Bus 4** (index 32) |
| Power Steering (EPS) | `0x32` | **Bus 4** (index 32) |

The neighboring membership makes the split unambiguous at the topology-model level.
Bus 1 also contains Front Radar, Front Side Radar Master, blind-spot and camera/parking
sensor domains. Bus 4 also contains Brake Booster, the steering-angle sensor/spiral
cable, Airbag, Skid Control, and EPS. `CDbCanBusNameTable` names indices 29/32
`Bus 1`/`Bus 4`, while `CDbCanBusListTable` independently assigns both to
**Central Gateway**. This is Toyota's own current Camry network model, not a CAN-ID
correlation.

Exact F33 independently collapses the EPS-side escape hatch. The target has one configured
CanIf controller (`0x21970 = 1`), and its normal receive/transmit interrupt wrappers at
`0x83F30` and `0x8583E` both invoke their workers with controller/channel argument **1**.
B6 is controller-1 acceptance rule 39 inside the same 47-rule span whose tail contains
EPS diagnostics `0x7A1/0x777/0x7A0`. Thus the exact EPS does **not** have a second
application CAN controller on which B6 could secretly arrive.

Joined to the retained harness evidence, this closes the practical wiring question. Before
the physical Toyota-B CAN0/CAN1 exchange, the large steering/chassis network was exposed
on the unsplit Panda bus 1 while the separate 22-ID ADAS-FD family occupied the relay
pair. After the exchange, the steering/chassis family moved onto CAN0/CAN2 and the 22-ID
family moved to bus 1. The moved family contains exact-F33-produced `0x030`, protected
Brake-domain `0x0D7`, `0x025` steering state and the EPS diagnostic route; the 22-ID
family contains the `0x180..0x18C` 64-byte sensor/object vocabulary. That composition is
exactly the direction predicted by Toyota's **Bus 4 chassis / Bus 1 camera-radar** split.
The repin therefore moved the B6-capable Brake/EPS network onto the comma relay pair as
intended; a simple wrong-Panda-bus or hidden-second-EPS-bus explanation for the repeated
zero-B6 capture is rejected.

There is one deliberately retained boundary. GTS+ `Bus 1`/`Bus 4` are Central-Gateway
network identities, not connector cavity numbers, and passive CAN cannot mathematically
exclude a perfectly transparent external gateway that republishes an entire native EPS
bus. The retained data provide no positive evidence for such a mirror: post-repin
CAN0/CAN2 have identical stream sets with only small per-port receive-loss differences,
exact F33 `0x030` and EPS UDS responses are present on that network, and the Toyota model
already places Brake/Skid and EPS on one shared Bus-4 segment. The supported engineering
conclusion is therefore **Bus 4 is the Brake/EPS B6 segment and the relay-correct Toyota-B
capture reaches it**. Section 20 subsequently recovers cruise operation and a repeated
lateral/HUD state directly from the retained CAN while B6 remains absent. What still lacks
machine synchronization is Toyota's exact **`LTA Control Condition` name**, not evidence
that the vehicle entered meaningful cruise/ADAS request state. Whether that request won
and received active-steering grant remains a separate Operation-FFD question.

Deterministic topology evidence is promoted inside
`data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json` and verified by
`tests/verify_camry_8965F3307000_gtsplus_semantics.py`; the physical relay/capture half
remains `data/generated/camry_2026_relay_correct_capture.json`.

## 20. Existing drives recover cruise operation and strongly identify LTA/LCA request state without B6

The two §16 routes contain more operating-state information than the original bounded
analysis used. The same-car stationary FRC/`0x0FE` join from §7 gives exact momentary
MAIN/RES+/SET-/CANCEL bits, so those button edges can be used as synchronization anchors
without adding a diagnostic poller. A deterministic re-analysis of the retained incoming
CAN finds that bus-0 `0x08A/32` byte 3 is not merely a structural correlator: value
**`0x08` is a reproducible cruise operating-state latch**. Six rising edges follow six
effective MAIN presses by 0.17..0.29 s. Two CANCEL presses clear byte3 `08→00` within
0.03..0.07 s. A MAIN press in P/R near the end of confirmation segment16 is a useful
negative control: the momentary `0x0FE` press is present but no `0x08A` cruise latch
follows.

Byte 10 independently closes the state as cruise/set-speed rather than a generic ADAS
flag. At the six `00→08` activations it is within **1.39 km/h** of independently decoded
`0x0AA` wheel speed: representative joins are 31 versus 31.793, 42 versus 42.280, 37
versus 38.250, 70 versus 69.775, 38 versus 39.390, and 66 versus 66.547 km/h. The first
drive's two SET- presses change byte10 **42→40→39** at +0.23/+0.16 s. In the confirmation
drive, three RES+ presses change it **66→67→68→70** at +0.13/+0.16/+0.21 s. CANCEL
clears both byte3 and byte10 to zero. Across the two routes the recovered `0x08A byte3=8`
intervals total **158.846096 s / 511,760 incoming frames**, and **B6 count is zero on all
buses throughout those intervals**. Thus the earlier statement that the logs lacked a
machine-visible *cruise-operating* interval is superseded: they do. FRC DID `0x1914`
remains a useful OEM-named corroboration, not a prerequisite for proving that cruise was
operating in these retained drives.

A fresh byte-level reconciliation materially strengthens the second state class. Its raw
inputs are the compressed drive-A artifact **SHA-256 `be0c0294…c7553db5`, 1,656,656
frames** (uncompressed `91ee1c9b…9e506a`) and drive-B artifact **SHA-256
`641eee57…9bb3a`, 1,918,047 frames** (uncompressed `4bdf3d49…7a0c65`). Across every
bus-0 `0x08A/32` row, B21's value set is exactly **`{0,11,18}` in each drive**: A counts
`18,868 / 646 / 1,101`; B counts `20,914 / 2,288 / 797`. The complete joint tuple census
shows that B21=`11` occurs only with cruise active (`B3=8`) and B24=`100`; B21=`18`
occurs only with cruise off (`B3=0`) and B24=`50`, with B23=`0x20` in all 1,898 observed
rows. B21 is zero in the remaining tuple classes. This is a state enumeration, not a
one-value coincidence.

The retained **current** GTS+ registry supplies the independent numeric vocabulary.
Generation-20 category 405 `EMPS_P5.ddb` (source SHA-256 `fb793322…e329e`) defines DID
`0x1CEE` byte 0 as **Target Lateral ID**, with the exact dictionary **`0 = No Request
(Manual Operation)`, `11 = LTA/LCA`, `18 = SDG`**. The raw CAN sequence independently
supplies the dynamic semantics: B21=`11` is the long cruise-active LTA/LCA request state;
B21=`18` is a short cruise-off SDG request state; and B21=`0` is no request.
nearest-frame joins (absolute delta <=25 ms) show `0x081/32` B13 mirrors B21 in
**20,442/20,479 = 99.8193271%** paired A rows and **23,991/23,999 = 99.9666653%**
paired B rows. The exact mirror confusion matrices, including the 32 drive-A startup
`B13=128` rows, are pinned in the generated artifact and verifier.

The same reconciliation now identifies a value field, not only an operating-state
enumeration. Interpreting `0x08A` B18:B19 as signed big-endian and scaling it by exact
F33's protected-B6 target-angle factor **`1024/17870 =
0.05730274202574147 deg/count`** makes the manual (`Target Lateral ID=0`) samples track
measured `0x025` steering angle with best lag **-25 ms** in both drives: fitted scales are
`0.05731251` (A, `r=0.9987`, **0.017046%** error) and `0.05731821` (B, `r=1.0000`,
**0.026993%** error). In the retained ID11 intervals the same field changes character
from feedback-shaped to forward-correlated: the best measured-angle lag shifts to
**+50 ms** in drive A (a broad plateau — `r` varies only 0.8746..0.8755 across 0..75 ms)
and **+225 ms** in drive B (weaker, `r=0.4467`, over a narrow target range). These are
correlation-shape observations, not exact causal lead times. Current category-405 `EMPS_P5` DID
`0x1CEE` independently places
**Target Steering Angle After Output Compensation** immediately after Target Lateral ID.
The byte position is not transferred from that diagnostic DID; the CAN position, scale,
and dynamics are recovered from the retained route and exact F33 contract.

Two further messages reconstruct one three-state carrier without transferring any old
layout:

| state tuple | `0x412/8` B0 | `0x371/32` B9 | `0x371/32` B20 low 2 |
|---|---:|---:|---:|
| state 0 | `0x10` | `0x10` | `0` |
| state 1 | `0x12` | `0x20` | `1` |
| state 3 / Class-L | `0x14` | `0x30` | `3` |

Using the nearest same-segment `0x371` frame within 100 ms for every `0x412` frame,
drive A has **518/520 canonical pairs matching** and drive B **630/631**. The full A
confusion counts are `(412,371B9,371B20low2): 00/00/0=2, 00/20/1=1,
02/20/1=3, 10/10/0=5, 10/20/1=2, 12/20/1=496, 14/20/3=1,
14/30/3=17`; drive B is `10/10/0=216, 12/20/1=357, 14/20/1=1,
14/30/3=57`. The noncanonical cells are confined to startup/transition sampling; the
complete transition timelines are also asserted exactly rather than summarized by modal
payload.

The Class-L edge timeline is especially discriminating:

| drive | B21=`11` onset | `0x412 B0=14` | `0x371=30/3` | B21 clear | carrier clear |
|---|---|---|---|---|---|
| A | seg5 +16.834568 s | +16.944992 (**+0.110424**) | +17.014128 (**+0.179560**) | +32.984427 | `371 20/3` +0.029970, canonical `20/1` +0.189708; `412 10` +0.491876 then `12` +0.994339 |
| B | seg20 +13.239624 s | +13.339979 (**+0.100354**) | +13.440058 (**+0.200434**) | seg21 +10.435632 | `412 12` at the clear; `371 20/1` +0.070336 |

Drive B also proves cruise and lateral **request** state are distinct: the `0x08A B3=8`
cruise rise is segment20 +1.546326 s, exactly **11.693298 s before** B21=`11` begins.
The five-frame segment21 CANCEL pulse starts at +10.406004 s; after **0.029628 s** the
same captured time clears cruise B3, B21=`11`, and `0x412 B0=14`, and after
**0.099964 s** `0x371` is back at `20/1`. Thus CANCEL supplies a second dynamic join
across cruise, Target-Lateral numeric state, and the HUD/state carrier.

The combined B21=`11` intervals remain exactly **73.303384 s / 237,097 incoming frames
/ zero B6 at every DLC on every bus**. Exact F33's complete 43-descriptor normal-Rx list
is independently pinned by the firmware-derived ingress artifact; it excludes **all of
`0x08A`, `0x371`, and `0x412`**. Thus `0x08A` is not direct EPS ingress. The joined
evidence instead identifies an **upstream lateral request carrier**: B21 is Target
Lateral ID and B18:B19 is its signed target angle at the exact downstream B6 scale.
B21/B26 upper two bits are zero in all 89,231 retained frames and the current GTS+
diagnostic field is 8-bit, so any 6-bit field boundary is an encoding assumption, not a
proved producer layout. Every retained `0x08A` frame is on the Bus-4 capture itself
(Panda bus 0: 44,614 / relay mirror bus 2: 44,617 / bus 1: zero); current GTS+ topology
places Front Camera on Toyota Bus 1 and Brake/EPS together on Bus 4, while exact F33
accepts protected B6 on the latter. Physical transmitter and signer are unknown, so
`0x08A` must not be labeled a native Bus-1 frame. The retained bytes close the request representation without making it an EPS ingress or grant oracle. Exact F33's B6-independent internal path explains why zero B6 needs no missing packet; it does not prove autonomous lane-centering authority in these intervals (CORR-137 / VAR-095).

Historical Toyota names `LTA_RELATED` for `0x371` and `LKAS_HUD` for `0x412` are
corroboration only; no historical signal layout is transferred. Current FRC_P5 `LTA
Indicator 1` is a fixed RoutineControl/display active-test concept (`31 01 15 83`), not a
synchronized live-state oracle, and contributes no byte label. Likewise, no physical
LTA-button carrier is recovered: the decoded `0x0FE` pulses remain only the exact
same-car MAIN/RES+/SET-/CANCEL controls. The operator's report of a green LTA indicator
and steering assistance during the first drive is retained as separate human
corroboration, not machine evidence and not part of the numeric proof.

This supersedes VAR-067's “generic lateral/HUD candidate” wording (CORR-129), the later state/display-only interpretation (CORR-134), and the interim `0x08A -> B6` stock-LTA assumption (CORR-135). The trailer is now structurally much tighter: B28 candidate reset-low2 matches preceding authenticated `0x00F` on 19,868/20,615 drive-A frames and 23,093/23,996 eligible drive-B frames, comparable to known protected `0x0D7/0x090`; on all 18,727 A / 21,989 B same-reset, same-segment B26+1 pairs, candidate message-low2 advances +1. B27 is always zero and the remaining 28 trailer bits are effectively frame-unique. This strongly supports Toyota ordinary-P5 `FV4 || MAC28` framing while leaving exact sender profile/key/CMAC and producer ownership unrecovered. It does not establish or require an `0x08A -> B6` stock-LTA transform, and it does not authorize steering output.
Deterministic evidence is
`data/generated/camry_2026_lta_state_reconciliation.json`, regenerated by
`tools/analyze_camry_2026_lta_state_reconciliation.py` and verified by
`tests/verify_camry_2026_lta_state_reconciliation.py`; the older cruise/set-speed census
remains independently verified by `tests/verify_camry_2026.py`.

## 21. Class-L EPS/upstream correlation is negative under persistent-edge matching

A deterministic follow-up conditions the same two drives on the exact §20 Class-L
intervals, including the continuous-logMonoTime segment20→21 interval of **57.184128 s**.
For every observed exact-F33-accepted bus-0 stream other than absent B6, a bit is counted
as an edge only when it is persistent in at least 95% of both three-second windows and
changes value. No accepted bit flips at the Class-L rise in either drive. EPS transmit
`0x030` is analyzed separately and likewise has zero persistent flips at either edge.
The decoder preserves the exact DBC formulas: torque is
`signed_be(71|8)*0.1 + signed_be(139|4)*0.01`; angle is
`signed_be(3|12)*1.5 + signed_be(39|4)*0.1`; rate is `signed_be(35|12)`.

The upstream `0x180..0x18C` family remains outside F33's acceptance rules. `0x18A` has no
rise flip reproduced across both matched intervals; an isolated drive-B B27 high-nibble
flip remains visible in the artifact and is not promoted. Literal `0x18C` staircase
parsing yields record count **3 in every frame on both sides of all four edges**. The
`0x181 bytes[35:37]` signed little-endian field peaks at -200/-240 ms against measured
steering in the two drives, so it lags steering and is steering-derived rather than a
command precursor. The exploratory `0x090` correlation is now closed and retired in
§28: its best field was a synthetic composite outside the exact-F33 receive surface.
These negatives do not prove absence of invisible EPS-internal state and do not authorize
production output.

Deterministic evidence is
`data/generated/camry_2026_class_l_upstream_correlation.json`, generated by
`tools/analyze_camry_2026_class_l_upstream.py` and verified by
`tests/verify_camry_8965F3307000_external_lateral_ingress.py`.

## 22. Exact Brake/EPB producer acquisition is identity-directed and locally blocked

The producer-side target is now exact rather than a generic category-435 request:
the same-car read-only response at physical `0x7B0 -> 0x7B8` carries one F181
software record **`F152633K0000`**, DID `0105` ECU assembly **`8954147040`**, and
F18C serial `8954147040CFC1800985`. Current GTS+ independently identifies category
435 as generation-20 `ABS_P5.ddb` **Brake/EPB**. This pass did not contact the car or
transmit any vehicle traffic.

The pinned local CUW corpus is an acquisition blocker, not producer firmware. An
independent raw `attach.att`/CRC census of all **26** packages reproduces DiagID counts
`blank=12, 0724=1, 07500F=1, 07506D=1, 0792=6, 07A1=3, 07D2=2` and finds zero
`Node01/DiagID=07B0`, zero descriptor values equal to `F152633K0000`, and zero values
equal to `8954147040`. The sole local package whose `VehicleName` is `CAMRY`,
`T-0051-26.cuw`, is a valid 2025–26 AXVH85 `P5-Unified` package but targets
**DiagID `0724`** with `8A28/8A29/8A2A` Engine/MG calibration families. It is not a
Brake package and is not a usable producer surrogate. The tracked Toyota campaign
metadata contains only the Corolla-specific 24TC01 `F152612A...` Brake family; that
family is not transferred to this Camry identity.

The local-negative proof is now stronger than the descriptor census. A full byte-level
census scans every one of the 26 CUWs in raw form using direct ASCII, UTF-16, inverted,
and textual-hex representations, then scans every recognized recoverable CPU member as
logical bytes. Correctly framed S1/S2/S3 streaming covers **33,567,972 records /
538,136,128 data bytes** across the corpus; ZV/LZF decoding adds **6,976 records /
28,573,696 bytes**, for 46 decoded members total. Neither exact identity appears anywhere.
The only raw `F152633` prefix occurrences are at package offsets `5,001,412` in
`T-0015-20.cuw` and `251,781,836` in `T-0150-24.cuw`; both are seven hex nibbles inside
unrelated S-record text, not an encoding of `F152633`/`F152633K0000`, and neither decoded
image contains the exact identity.

The lock-pinned retained GTS+ runtime state also contains no hidden offline package route.
The AgentLite completion trace contains exactly 11 **host-software** components and no
`T-xxxx-xx` calibration-package reference; `GTSPlusDataSync.db` has zero rows in
`hash_info`, `logging_history`, and `process_info`; `AgentLite/DOWNLOAD` is empty;
`GTSPlus/UserData/AutoSave` contains only `READ ME.txt`; and the retained tree contains
zero `.tse`, `.gtse`, `.vdas`, `.cuw`, `.cal`, or `.xxz` files. This proves only that the
pinned local distribution retained no reusable vehicle package/session specimen. It does
**not** prove Toyota/TIS lacks the exact Brake calibration.

Accordingly, no honest code search was performed for the `0x0B6/32` Tx descriptor,
SecOC generation/profile/freshness, upstream FRC inputs, or enable/arming conditions.
All four require a decoded category-435 runtime application. Searching an opaque or
unrelated CUW body for executable constants would not establish firmware behavior.

The highest-confidence acquisition route is the already-verified Toyota/TIS
ECU-supply-change flow, using the exact vehicle VIN at authenticated query time and
category-435 identities:

- `ecuAssyNo = 8954147040` from DID `0105`;
- `baseSwNoLst/baseSwNo = [F152633K0000]` from the counted DID F181 response;
- accept only a result returned for that exact query, then independently require the
  CUW descriptor to identify `Node01/DiagID=07B0` and validate its container/member
  CRCs and provenance before decoding.

No calibration URL is known. In particular, do **not** synthesize a
`/t3Portal/calibration/F152633K0000` path: the observed F181 is a current software
identity/search input, not a proved downloadable target CID. Current GTS+ exposes a
`P5-Unified` host route through `TCUWCanUnifiedCIDGetter.dll`,
`TCUWCanUnifiedPrepareWriter.dll`, and `TCUWCanUnifiedFlashWriter.dll`, but only the
eventual package descriptor can select its actual contact type. If acquisition yields
decoded executable producer bytes, then register a separate analysis target and search,
in order, the B6 Tx packer, authenticator/freshness path, FRC/ADS transform, and
enable/suppression/recovery gates.

Deterministic evidence is
`data/generated/gtsplus_2026/camry_f152633k0000_brake_acquisition.json`, generated by
`tools/techstream/build_camry_f152633k0000_brake_acquisition.py`, with the full byte/runtime
census implemented by `tools/techstream/cuw_identity_census.py`, and verified by
`tests/verify_camry_f152633k0000_brake_acquisition.py`. The Toyota/TIS host dataflow and
result-selection mechanics remain independently verified by TMS-049/TMS-050.

## 23. Current category-435 lateral/authentication fields are observers

The exact current GTS+ category **435** identity is generation-20
`ABS_P5.ddb` **Brake/EPB**. Its 80-byte type-62 Data Monitor table contains 554
static candidates, all of which role `0x05` sends through runtime
`CheckSupportPid`; consequently a DDB row is vocabulary, not proof that this exact
Camry supports the DID.

Two rows bound the steering/authentication language precisely. DID `0x107E`
**ADS Control EPS Pinion Angle2** (alternate `0x307E`) is bits 0..23, signed,
with display conversion `raw * 25 / 100000 rad` (0.00025 rad/count). It is an
observer, not a steering target or writer. The exact Camry returned
`requestOutOfRange` in both tested default and extended sessions, so even its live
availability does not transfer from the DDB. DID `0x10AF` **Software Number for
Authentication** is bits 0..135: an opaque **17-byte** unitless field with no
value dictionary. Its live support/value was not measured. The label does not make
it a SecurityAccess secret, authentication command, CMAC/freshness owner, or B6
producer identifier.

This adds no producer or acquisition shortcut. In particular, `0x10AF` does not
replace the exact F181/0105 Toyota/TIS search inputs in §22, and neither observer
identifies category-435 transmit/signing code. Deterministic evidence is
`data/generated/gtsplus_2026/camry_brake_observer_vocabulary.json`, generated by
`tools/techstream/build_camry_brake_observer_vocabulary.py` and verified by
`tests/verify_camry_brake_observer_vocabulary.py`; no vehicle request was sent.


## 24. 0x030 B22:B23 motor-feedback proxy: Class-L floor and opposing-driver runs, bounded against LTA authority

Exact same-image code now closes what the `0x030` bytes 22:23 actually are (§9-family
carrier detail in the TSS3 port report): a signed big-endian 16-bit **mapped
motor-feedback/current-family proxy** — signal 33, staged by `0x4C490` from the
GP-0x50E8 mapped current through a runtime scale, packed by `0x4C97A`. Its upstream is
target-natively joined to DID `0x1151`'s **pre-clamp** Q-axis aggregate
(`0x37E48 -> 0x38678 -> 0x3879E -> 0x59448/0x5D12C -> 0x4C490`), so it is
motor-current family, but a sibling-axis-conditioned lookup and a runtime scale
intervene: it is **not** DID1151 in wire units, not amperes, and not commanded torque
(VAR-071).

A deterministic offline analyzer decodes this field across the same two relay-correct
drives with the exact DBC torque/angle/rate formulas, nearest-frame joins, the §20
Class-L intervals (recomputed and asserted equal to the VAR-067 census), the cruise
latch (`0x08A B3==0x08`, count and duration asserted equal), `0x0AA` wheel speed, and
the §23 B6 census (**B6 = 0 on all buses in both drives**). The bounded results:

1. **Class-L hands-light current floor.** In the rate-controlled hands-light core
   (|driver torque| <= 0.5 N.m, |rate_raw| <= 2), drive B carries a **6.0x median
   |B22:B23| floor inside Class-L versus its speed-matched cruise control** (120 vs 20
   counts; rank-sum z = +39.6; lag-1 autocorrelation 0.91 vs 0.69). The control stratum
   is driver-proportional (r(current, torque) = +0.85); Class-L is not
   (r = -0.10, rate +0.18, angle +0.01). This proves a smooth **non-driver-proportional
   motor-feedback component inside Class-L**, not a stepping edge: the cruise-clean
   drive-B rise shows comparable 3 s pre/post medians (84 vs 102), and the floor falls
   after Class-L ends (77 -> 38). It does **not** uniquely label the component LTA
   torque: a mode-changed EPS damping/assist map produces the same signature.
2. **Opposing-driver/motion runs.** With |B22:B23| >= 150, |driver torque| >= 0.2 N.m,
   |rate_raw| >= 2, sign(current) == sign(rate) and sign(current) == -sign(torque),
   bridging <= 1 sample dropout: drive A Class-L holds **214 qualifying samples / 5
   runs >= 100 ms**, longest **0.914 s** (starting +4.699 s into Class-L; median
   current -445.5, median driver torque +0.91 N.m, median rate -10, angle +3.7 -> -6.2
   deg at ~40.6 km/h) — the motor proxy drives in the steering-motion direction while
   opposing the driver's hands, with B6 absent. Drive B holds 28 samples / 1 run
   (0.224 s). The speed-matched non-Class-L comparison is weaker or absent (drive A max
   0.151 s over 3 runs; drive B zero). Consistent with active EPS assist applying
   torque against the driver, but driver assist, damping, friction/road-load
   compensation, and lane-keeping-class functions are **not separable** from two drives:
   this is **not proof of LTA authority** (VAR-072).
3. **No hands-light autonomous-looking sweep.** No sustained >= 0.5 s hands-light
   steering-motion sweep occurs inside Class-L in either drive (max 0.463 s / 0.292 s);
   the speed-matched non-Class-L stratum contains one such sweep (drive A). The
   Class-L signature is a smooth current floor with episodic opposition, not
   self-steering-shaped motion.

Motor feedback is never by itself proof of an external lateral command: driver EPS
assist also creates current. These results are the strongest bounded live evidence yet
that EPS behavior **changes mode inside Class-L while B6 = 0**, and they sharpen the
VAR-063/065/066 discriminator question without resolving it. Deterministic evidence is
`data/generated/camry_2026_motor_feedback_correlation.json`, generated by
`tools/analyze_camry_2026_motor_feedback.py` and verified by `tests/verify_camry_2026.py`.

## 25. D5/snapshot/group-input provenance: sensor/DMAC acquisition + internal state, no COM/CAN route

The remaining unclassified snapshot surface around the `0x5Dxxx` mirror trio is now
closed target-natively (VAR-073). `0x58B5E` (magic `0xA55A` checksum block plus a
counter/inverse-counter handshake) drives `0x58B1A`, which runs mirrors `0x5D12C` /
`0x5D5E0` / `0x5D6DC` under selector switches `0xFFC0/0xFF80/0xFF00`, copying staging
`FEBE822C..FEBE8260` and producer cells into the working-cell block `FEBE6450..6794`.

Staging provenance is fully classified:

- `0x50B6A` copies the **group-input getter** output (`0x6217E` = channels 0/8) from
  acquisition block `FEBE5EC8..5EDE`. The getter consumes 16-channel descriptors at
  `FEBE3C00+idx*0x40` and GlobalRAM rings (`FEEF80A0`/0x50, `FEEF81E0`/0x1B0,
  `FEEF88A0`/0x60, `FEEF8A20`/0x1B0, contiguous through head counters
  `FEEF90E0..F4`); entry value is `(entry & 0x7ff8) << 1` and consumption clears the
  low halfword.
- `0x50BBC` copies packed **serial torque-sensor records**: `0x629A2` packs the two
  12-byte records that `0x62488` unpacked from 5-byte sequence-checked/CRC-verified
  frames (14/14/12-bit) fetched by `0x61008` from per-channel 20x u16 FIFOs at
  `FEEF8050/FEEF8078`; channel type `0x11` (flash table `0x31678`) negates channel 1.
- `0x50C38` only **zeroes** `FEBE8260..8263`; `0x50C58` OR-aggregates them into the
  error cell `FEBE8274`. The second staging writer `0x58C9A` from VAR-071 is
  **init/reset only** — it seeds `FEBE822C..8242` with invalid marker `0x8000` and
  constants, closing that bounded question.
- No application-code writer posts fresh ring/FIFO payloads anywhere in
  `FEEF80A0..FEEF9130`: every direct writer is init zeroing/marker seeding
  (`0x5FA3A`, `0x5FA84`, `0x60AA8`) or the consume-side ack (`0x60C60`). The channel
  initializer `0x6082C` programs the descriptors **and DMAC primary/secondary
  trigger-select SFRs `0xFFF99000/0xFFF99004`**; the same driver family carries
  ADCG0/ADCG1 scan, CSIH1 serial, and CRC0/CRC1 unit config. Producer class is
  therefore **hardware/peripheral-fed shared memory (DMAC)**; exact per-channel
  trigger identity is bounded, not asserted.

The three command/driver families export through Techstream-named DIDs from
internal-state terminals: steering-wheel torque DID `0x1035` ← `FEBE66A8` ←
`FEBE7E0C` ← the four-sensor decode `0x484F0` (staging raw − learned zero points ×
flash gains) with `0x4845E` mode selection; torque-sensor outputs DIDs
`0x1091..0x1094` mirror the same decode; command current DIDs `0x1152/0x1154` ←
`FEBE6724/6726` ← `FEBE6D84/6D86` ← field-weakening clamp (`0x37F16/0x384D8/
0x38396/0x3835E`) of the internal current-limit envelope; command torque DID
`0x1C02` ← `FEBE6772` ← `FEBEE40A` ← `0xBF33E` ← `FEBEAC56`, the already-proved
B6-selected internal cone. A reference guard over all 21 path functions shows the
only READ into the generated-COM staging (`FEBE7F00..80E0`), control-snapshot
(`FEBEAC00..AEFF`), or `FEBEF000..F200` regions is that same `0xBF33E` terminal;
`0x59448`'s `FEBE7Fxx` references are WRITEs only. The `1C02` chain here is the **diagnostic sibling of a proved physical
current-control join**, not an isolated observer/model cone. CORR-130/VAR-083 close the
same-function edge that a direct-reader census misses: `D042C` writes pre-slew
`FEBECC62` and immediately reuses that value to form/slew `FEBECC66`; `D047C` selects
`FEBECC64`, which is copied through `FEBEAC54 -> FEBEE40C -> FEBE6AF4 -> FEBE6E0A ->
FEBE6DEC -> FEBE6DC8/FEBE6DD6` into the motor-control transform. In parallel,
`D0AAE` copies pre-slew `CC62 -> AC56`, and `BF33E` mirrors that sibling as
`EE40A -> FEBE6772 -> DID 0x1C02`. Thus `1C02` is a diagnostic mirror of a physically
relevant pre-slew command value, while `AC54/EE40C` is the motor-driving sibling. The
remaining unresolved question is upstream of `CC50/CC62`: what state/value grants
factory-LTA lane authority there while B6 is absent. RH850/P1M-E has **exactly one
RS-CANFD unit** (`RSCFD0`, base `0xFFD20000`; R01UH0585EJ0120 §17), so a second CAN
controller does not exist on this MCU, and combined with the VAR-065 47-rule
exhaustion no second-CAN route can feed this path.

Consequently, with controller-1 B6 absent, the D5/snapshot/group-input surface cannot
carry hidden lateral command/state: it moves sensor/ASIC acquisition (serial torque
interface, ADC scan), internal control state, and structural constants (the
`0x50B00`-written `0x8000` invalid markers, zeroed error words) only. The negative is
scoped to the canonical direct data-reference graph: computed aliases, DMA/hardware
mutation of LocalRAM outside the GlobalRAM rings, and unrecovered code remain outside
the proof. Deterministic evidence is
`data/generated/camry_8965F3307000_d5_snapshot_provenance.json`, generated by
`tools/build_camry_8965F3307000_d5_snapshot_provenance.py` and verified by
`tests/verify_camry_8965F3307000_d5_snapshot_provenance.py` (VAR-073).

## 26. Exhaustive bus1 field census: no lateral planner candidate leads the EPS motor proxy

Section 21's upstream negative rested on persistent-bit edge scans plus one hand-picked
`0x181` lag probe, and Section 24 proved the EPS motor proxy changes mode inside Class-L
while B6 = 0. The remaining question — whether some *analog* bus1 field behaves like the
lateral target/planner input that mode change would need — is now closed by exhaustive
field enumeration over the same two relay-correct drives (VAR-074).

Method: for every periodic bus1 stream (22 per drive: the full `0x180..0x18C` family plus
`0x020/0x123/0x160/0x1A0/0x200/0x201/0x230/0x440/0x450`), every byte-aligned
(u/s8, u/s16 BE+LE, u/s24 BE+LE), nibble, bit, and per-frame delta candidate is
enumerated. Constants, low-diversity scalars, duplicate series, and **nonzero** rolling
counters are suppressed first: byte 2 on every periodic stream except low-rate
`0x440/0x450`, byte 3 on the 18x family and `0x020/0x1A0/0x200/0x201`, and byte 7 on
`0x1A0`. The corrected checksum heuristic requires a nontrivial head-sum/XOR relation;
constant-zero trailer bytes are not self-evidence, and no such checksum carrier is
detected. That leaves **15,367 kept candidates (drive A) / 14,130 (drive B)**, each zero-order-hold
resampled onto a 25-ms grid spanning Class-L ± 8 s, screened against seven bus0 targets
— the exact `0x030 B22:B23` motor-feedback proxy, |motor|, driver torque, `0x025`
angle and rate, wheel speed, and the Class-L indicator — with a coarse ±500-ms lag
sweep, then fine-swept at 25-ms resolution with a speed-matched cruise
(non-Class-L) control region. Promotion requires |r| ≥ 0.40 in **both** drives with a
peak lag ≥ +50 ms in both; positive lag means the field **leads** the target.

Result: of **2,929** fields fine-swept in both drives, **exactly 0 reproduce as
leading** the motor-feedback proxy. Drive B — the drive with the clean 57.2-s Class-L
window — has zero leading fields among its 48 strong (|r| ≥ 0.40) motor correlates at
all; drive A's 69 single-drive leads among 246 strong correlates are the multiple-testing
tail and none reproduce. The corrected filter exposes 26 reproduced lagging encodings
(and seven strong delayed angle echoes), still feedback/derived-like rather than planner
leads. A particularly clear **steering-angle echo**, `0x160[22]` (s8/s16be), tracks `0x025` angle at
r = +0.9963 (−75 ms) and r = +0.8698 (−100 ms) in the two drives and correlates with
the motor proxy equally strongly in drive-B's ordinary cruise control (r = +0.78), so
bus1 demonstrably carries *delayed steering feedback*, not commands. Section 21's
`0x181 bytes[35:37]` signed-LE field does not reproduce as a stable correlate over the
full windows (|r| < 0.40 in both, inconsistent peak lags), further weakening any
command reading of it.

Boundaries: drive A contributes no local speed-matched control points (its cruise
interval 2 begins exactly at the Class-L rise and ends 0.56 s after the fall), so
in-drive Class-L specificity rests on drive B. The declared tested lead range is
±500 ms at 25-ms resolution; weak fields peaking at that boundary are window-scale
trends, and a Toyota lateral command consumed by a 100-Hz EPS leads by control frames,
not half-seconds. This negative covers observed periodic bus1 traffic only: it does
not touch the EPS-internal mode explanation of Section 24 and does not authorize
production output.

Deterministic evidence is `data/generated/camry_2026_bus1_field_leadlag.json`, generated
by `tools/analyze_camry_2026_bus1_field_leadlag.py` and verified by
`tests/verify_camry_2026_bus1_field_leadlag.py`.

## 27. Exact-F33 internal assist/mode/gain census: the moving-mode family is cruise-generic and cannot produce the Class-L B22:B23 shift

This section is the canonical home for the static decode of the EPS-internal assist-mode
state around the `C9590/C9650/C973A` moving-mode chain and its consumers
(`C6AF6/C8124/C854A/C878A/C8EF4/C9B04/C9D86/D0D7C/D0218`), asked directly by the §24
question: which internal state could change assist behavior inside Class-L while B6=0?
All addresses are exact-F33 CodeFlash (file offset = VA; the Sienna `+0x8000` rule does
not apply to this image).

**The latch family.** `C9590` (re)initializes the block, loading one-shot primer
`FEBEC5E5=1`. `C9650` arms pre-latch `FEBEC5F2` when `FEBEACCE=1` for a calibrated count
(ROM `[0xB0186]=40`, enabled by `[0xB0187]=1`) plus magic `FEBEAF08==0x55AAAA55`, then
sets one-shot moving-mode latch `FEBEC5F3` when additionally `FEBEACBD=0`,
`FEBEACBE=1`, `FEBEC601=FEBEC602=0`, `FEBEC5AC=0`, `FEBEAD19=0`, and
`FEBEADFC&0x1FF=0`; consuming the primer (C5F3 cannot re-arm after a clear without
re-init). Clears: `FEBEC601/602`, `FEBEACBE=0`, `FEBEC5AC&2`, `FEBEC603`,
`FEBEAD19∈{0x22,0x44}`, `FEBEADFC&0x1FF≠0`. `C973A` derives sub-latch `FEBEC5F4`
(= C5F3 ∧ C5AC=0 ∧ FEBEACCE=1 ∧ FEBEACCD=0 ∧ FEBEACBD=0) and slews crossfade weight
`FEBEC5B8` toward `[0xB016C]=1024` when C5F4 (else `[0xB016E]=0`) at rate
`1024/[0xB017E]=[0xB0180]=0x1800` per cycle, snapping inside a 20-count deadband.
`C9812` maps `|FEBEC5FC|` through a table selected by `FEBEC156&3` into `FEBEC5EC`
under a speed latch (`FEBEADF6 ≥ [0xB0170]=13` = 0.13 km/h set, `==[0xB0172]=0` clear).
`C9A84` emits `FEBEC5EE = clamp(C5B8,0,1024)/1024 × clamp(C5EC-integrator, ±[0xB017C])`.
`C9B04` qualifies the block on `|FEBEC600|` (`≤[0xB0188]=10`, `≥[0xB0189]=1`,
counter `[0xB0184]=200`); `C9D86`/`C9E44` supervise (`[0xB0446]=5000`,
`[0xB0448]=1`, `768/1024/600/600`) and `C9EEA/C9E18/C9F1E` persist a one-shot
activation counter trio.

**Every external input to the family, traced to source.**

| Working byte | Source | Origin | Grade |
|---|---|---|---|
| `FEBEACCE` | `0x0D5` signal211 B0[3] (`0x4B86E`→`FEBEF097`) | CAN, brake-domain monitor gate | verified (§18 census) |
| `FEBEC5FC`/`FEBEC600` | `0x0D5` s213/s212 monitor pair `FEBEAE06`/`FEBEAE04` (clamp ±1000/±100, trips `[0xB044A]=1000`/`[0xB044C]=100`, Dem 200/201) | CAN monitor channels | verified |
| `FEBEADF6` | filtered `0x0D7` signal283 SP1 speed (`0xBECF4` clamp 30000 → `0xBEDC4/0xBEE2C`, status `FEBEBEF0`) | CAN, 0.01 km/h; UDS `0xBA` op `FA` tester override | verified |
| `FEBEACBD` | `FEBEF000 ← FEBE7F68` | internal ComM communication-mode {0..3} | verified internal |
| `FEBEAD19` | `FEBEF014 ← FEBE687B ← FEBE7FC8` | internal service/lifecycle state | verified internal |
| `FEBEACBE` | `FEBEB1A4==0x11` | internal system-transition phase | verified internal |
| `FEBEADFC` | `FEBEB354` | boot-time same-image software identity | verified internal |
| `FEBEC5AC` | `C9562/C956A` from `FEBEACCC/FEBEAD6F` | internal fault bitfields | verified internal |
| `FEBEC156&3` map selector | `C54A2/C5554` ← `FEBEAC2F ← FEBEB121` = shift-position decode (`B35DC/B372A` over gear enum `FEBEB124`, S-range submodes `FEBEB125/12F`), diag override `FEBEB112` (`B3314/B338C`) | gear/diagnostic; **not live CAN** | verified internal |

**The selector is a calibration no-op in this exact image.** All four entries of every
`FEBEC156&3` pointer table alias one table: `0xD39DC→0xB018A ×4`, `0xD3A1C→0xB01D2 ×4`,
`0xD3A5C→0xB01E6 ×4`, `0xD3A9C→0xB01FA ×4`, `0xD3ADC→0xB019A ×4`, `0xD3B1C→0xB01B2 ×4`.
Gear-position map selection therefore cannot change assist in `8965F3307000` even if the
selector moved.

**Consumers reach the command path, but their magnitude input is pinned live.** All
C5F4-family outputs feed the assist pipeline (`C6AF6→C69EC→…→C72C0→D0162`,
`C854A/C878A/C8124/C8EF4→…→D0162/D0218`) whose sum `FEBECC48` scales through
`D0284/D02DA/D0382/D039E/D042C` to `FEBECC62/FEBEAC56` (DID 1C02 **Command Value
Torque** model/observable family), and `D0D7C` exports `C5F4` itself (`FEBEACF1`) plus
`FEBEC5EE×scale` telemetry. But `FEBEC5EE`'s only magnitude source is `FEBEC5EC =
interp(table 0xB018A over |0x0D5 s213|)`, and **s213 is identically zero across both
retained drives** (55,793 bus-0 `0x0D5` samples), so the family's commanded contribution
is deterministically zero in these logs; s212 (cruise `[−2,2]`, Class-L `[−2,2]`/`[−1,1]`)
never approaches its ±100/±1000 monitor thresholds either.

**Live pinning (deterministic, both drives).** `0x0D5` s211 is set in **100% of frames
inside cruise-active intervals and inside Class-L intervals alike** (2,291/807 drive A;
5,655/2,860 drive B), `0x0D7` s243 is **never** set (0/25,798, 0/29,999), so with ComM
mode 0 and no faults the entire `FEBEC5F3/FEBEC5F4` family is a **generic
normal-communication driving mode — active in all moving/cruise driving, not a Class-L
discriminator**. This directly answers the live `0x0D5` s211 observation that motivated
the census.

**Verdict.** No non-B6 external state accepted by exact F33 can select a different
assist behavior while cruising in this calibration: the only map selector is
gear/diagnostic-derived and its four tables alias; the C5F4 family's assist contribution
is zero whenever `0x0D5` s213 is zero; and every other enumerated cone member
(`0x025` angle feedback, engine RPM `0x115`, gates `0x127/0x13B/0x1C5`) is feedback,
engine, or gate state (§18 census). The §24 Class-L B22:B23 mode shift therefore cannot
be attributed to the enumerated external assist/mode/gain selector cone; the mechanism
remains bounded to EPS-internal dynamics outside this cone, unobserved accepted PDUs
(`0x1C5`, `0x64F`: zero frames in both drives), or surfaces outside the recovered
census. This is a static-census negative bounded exactly like VAR-068's live matched
negative; it does not authorize production output.

Deterministic evidence is the `eps_latch_inputs` section of
`data/generated/camry_2026_cruise_lta_edge_census.json`, generated by
`tools/analyze_camry_2026_cruise_lta_edges.py` and verified by
`tests/verify_camry_2026.py`; the static decode is reproduced from the tracked
decompiler corpus `data/generated/camry-8965F3307000/decompilations.jsonl`.

## 28. Exact-F33 `0x090` (PDU40) receive closure: sig235 is the strongest angle-like feedback; sig232 feeds the integrator; the exploratory B12/B13 composite is retired

Section 21 left the exploratory `0x090` nibble-scan correlation (best field
`B12[3:0]+B13`, r = 0.9931 at -60 ms in drive A) explicitly unresolved. Exact-F33
generated-COM geometry now closes that ambiguity (VAR-076) and corrects the temporary
in-flight byte-index interpretation used while this section was being built.

**Geometry (firmware-static).** Unpacker `FUN_0004B9F4 -> FUN_0007D12A` calls scalar
windows `0x167/0x169/0x16B/0x183`. The exact PDU-offset table at `0x22840` gives
PDU40 base `0x167`, therefore those windows begin at PDU bytes **B0/B2/B4/B28**.
`FUN_0007D12A` loads four bytes and assembles them as a big-endian window word; for the
10-bit, bit-offset-0 fields this yields `(Bstart & 3) << 8 | Bstart+1`. The complete
firmware-defined surface is therefore:

| Signal | Exact wire geometry | Raw / recentered or flag cell |
|---|---|---|
| sig229 | `B0[1:0]+B1`, 10-bit unsigned | `FEBE8084` / `FEBE808A` |
| sig227/228 | B0 bits 7/6 | `FEBE8090/91` |
| sig232 | `B2[1:0]+B3`, 10-bit unsigned | `FEBE8086` / `FEBE808C` |
| sig230/231 | B2 bits 7/6 | `FEBE8092/93` |
| sig235 | `B4[1:0]+B5`, 10-bit unsigned | `FEBE8088` / `FEBE808E` |
| sig233/234 | B4 bits 7/6 | `FEBE8094/95` |
| sig241 | `B28[7:4]` | `FEBE8096` |
| freshness | — | `FEBE8097` + `FUN_000498E0(0x16)` |

`FUN_0004AFCC(0,0x200,v,dst)` is exactly a signed-16 saturating recenter `v - 512`.
Bytes B6..B27 are not touched by the PDU40 unpacker. The sig241 extractor fetches the
B28..B31 four-byte window but only B28[7:4] survives its mask; B29..B31 do not affect the
signal value.

**Receiver chain (firmware-static).** `FUN_00058074` distributes the recentered cells as
`FEBE808A -> FEBEF1C6`, `FEBE808C -> FEBEF1C8`, and `FEBE808E -> FEBEF1CA`, with the
six flags staged at `FEBEF0A4..FEBEF0AE`. Runtime constants in this image pin
`FEBEF098=FEBEF099=0`, `FEBEF09C=1`, and `FEBEF0AA=0`. Under those constants,
`FUN_000BE846`'s active combination reduces to the **sig232** branch:
`FEBEBE96 = clamp((sig232-512)*0x931/0x100, +/-3763)`; the sig229 contribution is
suppressed by the `FEBEF0AA&2` branch. `FUN_000BCD66` copies `FEBEBE96 -> FEBEAE0C`, and
`FUN_000C310E` leak-integrates that value (`FEBEBF58 += FEBEAE0C - FEBEBFA0`, then
`FEBEBFA0 = FEBEBF58*0x400/8672` when its validity gate is open). Thus the previously
posed `FEBEBE96 -> FEBEAE0C -> C310E` chain is exact, but its source is **sig232**, not
the strongest angle-correlated field. Sig235 follows the separate `FEBEF1CA` consumer
family instead.

**Dynamic classification (both retained Class-L intervals, 10-ms grid, +/-120-ms lag
sweep).** Sig235 is the strongest angle-like exact field: drive A r = **+0.9924 at
-60 ms**, slope **0.9569 count/deg**; drive B r = **+0.7428 at -70 ms**, slope
**1.1976 count/deg**. In the analyzer's convention, negative lag means the `0x090` field
follows the `0x025` measured angle, so this is feedback-shaped. Sig232 is weaker and does
not reproduce as the dominant angle channel (A **+0.8934 at -40 ms**, B **+0.3331 at
+10 ms**); nevertheless its motor-proxy correlations peak at **-120 ms in both drives**
(A +0.5397, B +0.4631), again lagging rather than leading. Sig229 is weak/unstable
(A +0.1831 at +120 ms, B +0.4115 at -120 ms vs angle). All six flag bits are zero inside
both Class-L intervals. Across the three exact 10-bit fields there is **no reproducible
strong lead of the `0x030 B22:B23` motor-feedback proxy**.

**Retirement of the exploratory composite.** The old scan winner `B12[3:0]+B13`
reproduces exactly (r = 0.9931/-60 ms drive A; 0.7615/-70 ms drive B), but B12/B13 lie
inside the B6..B27 region the exact EPS receive logic never touches. B12:B13 is
byte-identical to B14:B15 in every inside-Class-L frame, so that result is a duplicated
fine-scale angle-correlated observer riding in the CAN payload, not a field consumed by
this EPS code. The scan-ranked `B4[3:0]+B5` is different: while B4 <= 3 inside both
Class-L intervals it is numerically identical to exact **sig235**, which explains its
strong angle correlation without inventing another signal.

Boundaries: sig229/sig232/sig235 OEM names remain unknown; the angle interpretation is a
dynamic classification, not an OEM label. Nothing here authorizes production output.

Deterministic evidence is the `firmware_exact_0x090` and
`exploratory_0x090_reproduction` sections of
`data/generated/camry_2026_class_l_upstream_correlation.json`, generated by
`tools/analyze_camry_2026_class_l_upstream.py` and verified by
`tests/verify_camry_8965F3307000_external_lateral_ingress.py`.

## 29. Complete generated-COM-to-Command-Value-Torque denominator: VAR-065's 19/116 framing is superseded

CORR-127 closes the denominator question raised by the broader `0x58074` staging audit. The old VAR-065 `19/116 nonempty, 97 empty` count was a count through one fixed raw→stage→snapshot model, not an exhaustive census of every staged COM value and consumer. The exact-F33 pipeline is larger but still converges to the same external-command result.

**L1/L2 denominator.** Exact `FUN_0007D12A` literal calls provide **116 scalar raw cells** (including signal243's stack-RMW path `0x4BB62 -> FEBE80A0`). The table-driven callers `0x693FE/0x697F4` add **14 configured extracts**, signals 90..103, spanning CAN `0x013..0x01F`; their qualification/forwarding state remains inside the communications-manager family and does not become a lateral magnitude. `FUN_00058074` stages **98 of the 116 scalar raw cells over 105 exact copy edges**. The other 18 raw cells have no consumer beyond their unpacker/staging/init machinery.

**Stage/snapshot denominator.** The exact COM-derived stage-space has **52 reader functions**; **15** sit inside the recovered steering cluster and the highest direct stage reader is `0xBF0EC`. No C/D-family command-composition function reads those stage cells directly: it consumes the later snapshot bank. Six exact copiers — `0xBC96A`, `0xBCA08`, `0xBCAA6`, `0xBCBD8`, `0xBCD62`, `0xBCD66` — account for **306 unique snapshot destinations**. This is the denominator the old 19-signal shortcut omitted.

**What reaches the steering cluster without B6.** Four non-B6 COM families survive far enough to matter, but none is an external command magnitude: `0x090` is the observer/plausibility family closed in §28; `0x0D7` contributes speed-class gating and a handler-pointer selector; `0x675` contributes configuration/telemetry/plausibility cells; and `0x13B` contributes gate state whose relevant qualifier branch is itself invalidated/gated by B6 signal243. These are real inputs and are why the old “empty” wording was too strong.

**Command-value composition.** The recovered `1C02` model/observable path is much narrower. `D039E` composes `FEBECC50`, later scaled/clamped through `D042C` into `FEBECC62 -> FEBEAC56`, and `BF33E` publishes the command-model/status block `FEBEE400..418` (including the Command Value Torque observable family at `FEBEE40A`). The only **generated-COM** value/mode inputs recovered at this level are B6: `CBA80` writes `FEBEC81A` from B6 sig262 snapshot `FEBEAE90`, while `CB73A` can raise the B6 assist-active state only when B6 sig261 snapshot `FEBEADB0=='1'`. Gain pairs are ROM-installed and internally adapted; without sig261 that B6-selected adaptation cannot activate. CORR-128 corrects one important distinction in the other branch: `FEBE71F2 -> FEBEEF8E -> FEBEAC52` does **not** supply the `FEBECC60` magnitude. `D0382` uses `FEBEAC52` only as a symmetric saturation limit on dynamic `FEBECC4E`; the actual B6-independent value comes from the internal `D0218 -> D0284 -> D02DA` chain closed in §30.

Therefore the corrected statement is stronger and narrower than VAR-065's old shorthand: **many more ordinary COM values are staged and observed than the 19-signal model showed, but no non-B6 generated-COM value is recovered as a value/mode input to the shared `CC50/CC62` command funnel or as the B6 assist-activation input.** Exact F33 also contains a B6-independent internal magnitude path feeding that same funnel. CORR-130/VAR-083 close the downstream consequence that this section originally left open: `CC62` is a real pre-slew physical-command value and continues intra-function through `D042C -> CC66`, then `CC64/AC54/EE40C -> 6AF4 -> 6E0A -> 6DEC/6DC8/6DD6`. CORR-135 supersedes the subsequent attempt to move this negative into an `0x08A -> B6` transform. Bus-4 `0x08A` is a secured-looking request representation, while exact F33 already has a B6-independent internal magnitude path into the same physical funnel. The current discriminators are `0x08A` producer/SecOC ownership and, independently, the exact external/local state that selects or modulates the internal stock-LTA path. This does not authorize output.

Deterministic evidence is `data/generated/camry_8965F3307000_command_cone_ingress.json`, generated by `tools/build_camry_8965F3307000_command_cone_ingress.py` and verified by `tests/verify_camry_8965F3307000_command_cone_ingress.py`.

## 30. Exact-F33 B6-independent Command-Value-Torque model path: `D0218` supplies `CC4E/CC60`; `FEBE71F2` is only the limiter

The residual command branch from §29 is now positively recovered far enough to correct its provenance. `FUN_000D0382` loads dynamic `FEBECC4E` and limit `FEBEAC52`, then computes `FEBECC60 = clamp(FEBECC4E, +/-FEBEAC52)`. `FEBEAC52 <- FEBEEF8E <- FEBE71F2` is therefore a **saturation bound**, not command magnitude. Exact runtime writer `0x3BDC6` chooses the minimum active value from ROM table `0x317E0` — entries are only `0x2B4D`, `0x3A75`, or `0x569A`, with `0x569A` as the default — from an internally protected status mask before storing `FEBE71F2`. The former “peripheral planner/magnitude” interpretation is rejected by CORR-128.

The dynamic B6-independent magnitude enters earlier. `D0218` writes `FEBECC48`; `D0284` scales it by `FEBEAC64/0x8000` and clamps it to calibration `+/-B1334` as `FEBECC4C`; `D02DA` optionally slew/filters that value into `FEBECC4E`; `D0382` applies the limit above; then `D039E -> D042C` carries the result into `FEBECC62`. `D0AAE -> FEBEAC56 -> BF33E/FEBEE40A -> 1C02` is Toyota's recovered **pre-slew Command Value Torque diagnostic mirror**, while CORR-130/VAR-083 prove the same newly computed `CC62` value continues inside `D042C` through `CC66 -> CC64 -> AC54/EE40C` into the physical current-control funnel. The `D0284` multiplier is internal calibration state as well: `BCBD8` snapshots `FEBEB140 -> FEBEAC64`, while the complete `FEBEB140` writer census is `B3866/B389C/B38D2/BF97A`. The first three derive it from exact ROM u16 `0xAEF4C=0x5571` as `floor(0x2774564E/0x5571)=0x7636`; reset/default writer `BF97A` uses adjacent rounded constant `0x7637`. Thus no generated-COM/CAN value enters through the scale factor either.

`D0218` has three exact branches. When internal diagnostic flag `FEBEAC2B==0x5A`, it reduces to `FEBEC4C0 + FEBEC3BA + FEBEBF3C`. When B6-selected `FEBEC7BF==1`, it reduces to `FEBEC4C0 + FEBEBF3C`. In the ordinary B6-inactive branch it computes:

`FEBEC43C + FEBEC4C0 + FEBEC3BA + FEBECC2C + FEBEBF3C + clamp(FEBECB38 + FEBEC5EE, +/-B132C/2) + FEBECBE8`.

The direct runtime writers are all internal C/D-family algorithm state: `CF2B2 -> FEBECB38`, `C9A84 -> FEBEC5EE`, `C7E36 -> FEBEC43C`, `C8678 -> FEBEC4C0`, `C74AC -> FEBEC3BA`, `D0162 -> FEBECC2C`, `C2B64 -> FEBEBF3C`, and `CFCD4 -> FEBECBE8`. `FEBEAC2B` is an internal diagnostic/control snapshot (`BCBD8 <- FEBEB112`; `B338C` sets `0x5A`, `B330A/B3314` clear it), while `CB73A` can set `FEBEC7BF=1` only with B6 sig261 snapshot `FEBEADB0=='1'`. The complete generated-COM denominator in §29 therefore remains intact: this is an **EPS-internal baseline-assist path**, not a second generated-COM target ingress.

This also bounds the retained-drive interpretation. VAR-075 pins the `FEBEC5EE` moving-mode contribution to zero in both retained drives because its `0x0D5` s213 source is identically zero; the other `D0218` terms remain live and, through the now-verified `CC62 -> CC66/CC64 -> AC54/EE40C` chain, can have a real current-control consequence with B6 absent. But semantic closure of all eight terms finds no independently recovered **lane-target** magnitude: they reduce to measured torque, torque+speed maps, internal aggregation/ROM state, `|torque|` curves, and angle return/dither/excitation. VAR-081 identifies the interval as LTA/LCA active. The unresolved question is therefore what upstream state/value gives this shared funnel factory lane-centering authority with B6 absent, not whether `CC62` reaches the motor. Nothing here authorizes output.

**`CEFFC` / `CB00` is the recovered D0218 map-bank selector, and it is B6-fed.** Exact `FUN_000CEFFC` writes `FEBECB00`. Default is `7`. When `FEBEACBD==0` and `FEBECAFF==1`, B6 signal 261 snapshot `FEBEADB0` (Target Lateral ID, B3[5:0]) maps `1→0`, `4→1`, `0x0A→3`, `0x0B→2` (LTA/LCA), `0x12→5` (SDG), `0x13→4`. `CD094` and `CDFF8` then index return/dither tables as `(CB00&7)+(AC3C&1)*8`. That is how F33 would change D0218 angle-domain maps **if B6 carried ID 11/18**. Runtime writers of `FEBEADB0` are only snapshot copier `BCD66` and reset `BF97A`; `0x08A` is not a source. In the retained drives B6 is absent, so `ADB0` stays 0 and `CB00` stays **7**. The ID11/18 D0218 banks therefore do not run. `CEFFC` does not import the `0x08A` milliradian target; it only switches internal maps from B6's copy of the same Target Lateral ID dictionary. Hands-light motor tracking of `0x08A` error remains a separate plant observation, not this selector. VAR-090.

**Default-bank terms themselves have no unpublished milliradian.** With `CB00=7`, `C43C` is `clamp(C472+C45A+C44C)` from driver-torque snapshot `AC44`, speed `ADF6`, and filtered measured-angle rate `C172` (delta of `AC88`). `C4C0` is a torque×speed map. `C3BA`/`CC2C`/`BF3C` stay inside the torque family. `CD094` blends return state `CA36` toward `C172` under that default bank; dither/return copies peripheral `EC14`/`EC18`. None of the eight term writers reads B6 `ADB0` or the B6 COM window. Combined with VAR-077 (only B6 supplies COM value/mode into `CC50/CC62`), the retained hands-light motor correlation with published `0x08A` error is **not an F33 COM input** (VAR-092). The command is adjacent to EPS, not into it.

Deterministic evidence is the `baseline_internal_assist_path` section of `data/generated/camry_8965F3307000_command_cone_ingress.json`, generated from the exact 6,065-function F33 corpus and verified by `tests/verify_camry_8965F3307000_command_cone_ingress.py`.

## 31. Baseline-assist parameter-bank selector: ordinary COM selector inputs are route-wide zero/absent in both retained Class-L drives

VAR-079 closes the next discriminator immediately upstream of several `D0218` baseline-assist terms. Exact F33 does contain a parameter-bank selector, but its **ordinary generated-COM inputs do not change with the retained Class-L state**.

**Static selector chain.** The complete scalar-value subset recovered into this selector is seven signals: `0x51E/8` sig160 `B0[3:0] -> FEBE8030 -> FEBEF050`, sig163 `B1[3:0] -> FEBE8033 -> FEBEF14A`, and sig166 `B5[7:6] -> FEBE8032 -> FEBEF141`; `0x13B/8` sig224 `B2[3:0] -> FEBE8082 -> FEBEF14B`; `0x490/1` sig280 `B0[6:4] -> FEBE80D2 -> FEBEF168` and sig281 `B0[3:0] -> FEBE80D3 -> FEBEF0A1`; and `0x1DA/8` sig282 `B0[3:0] -> FEBE80D6 -> FEBEF156`. `0x58074` stages these cells. The debouncers additionally consume resolved COM-receive validity/gate state: `FEBEF0C2 <- FEBE8081 <- FUN_000498E0(0x15)` for the `0x13B` companion path, `FEBEF0A0 <- FEBE80D5 <- FUN_000498E0(0x1C)` for `0x490`, `FEBEF157 <- FEBE80D8 <- FUN_000498E0(0x1D)` for `0x1DA`, plus shared gate `FEBEF000 <- FEBE7F68`. These companions can suppress extraction/qualification but carry no selector value and do not choose a bank directly; absent `0x490/0x1DA` traffic cannot provide a fresh valid selector value. `B3430/B3686` debounce the `FEBEF050` family into `FEBEB124`; `B34D4/B3538` qualify companion fields; `B35DC/B372A` reduce that state into `FEBEB121`; `BCBD8` snapshots `FEBEB121 -> FEBEAC2F`; `C54A2` selects `FEBEC158`; `C5554` maps `FEBEC158` values `0x77/0x44/0x88` to `FEBEC156=1/2/3`; and `C28FC` uses `FEBEC158/FEBEC156` to choose the calibration block consumed by baseline-assist terms such as `C2B64`. This is parameter selection, not a steering-target magnitude.

The other selector branches are explicitly internal. `C54A2` can choose `0x66` from diagnostic state `FEBEAC2B`, `0x11` from an internal `0x5AA5A55A` magic-state path, or `0x55` from internal status `FEBEAC30/FEBEAC40` under its validity gates. `FEBEAC50`, another validity mask, is copied by `BCAA6` from `FEBEEF88 <- FCC00 <- FEBE71EC`; it is not generated COM. The `FEBEAC3C&1` table-bank bit is also not drive mode: `BCBD8 <- FEBEB354`, while `B7374 -> FF254 -> 62E12` reports the TMR-protected `FEBF0668` verdict produced by `62D5E` after comparing the ROM compatibility/parameter block at `0x17DA0/0x17DC0...` against its working copy at `0x20850/0x20870...`. That bit is parameter-copy integrity.

**Retained-drive join.** The two relay-correct CAN-only captures directly reject the ordinary-COM selector as the Class-L discriminator. In drive A, all **519** observed `0x51E` frames have sig160=sig163=sig166=0, including all **16** samples inside the 16.119256-s Class-L interval; all **17,176** `0x13B` frames have sig224=0, including **537** inside Class-L. In drive B, all **600** `0x51E` frames have those three signals zero, including all **57** Class-L samples; all **20,000** `0x13B` frames have sig224=0, including **1,906** inside Class-L. `0x490` and `0x1DA` are absent in both captures. Every populated three-second pre/post Class-L edge window has the same selector value support on both sides.

Therefore the directly recovered ordinary-COM parameter-bank inputs cannot explain the retained LTA/LCA transition or its motor-feedback shift. Exact calibration now strengthens that negative: healthy selector1 is the only distinct `C28FC/C2B64` normal bank, selectors0/2/3 alias, all fallback banks alias, and route-zero sig160 can reach only equivalent selector0/2. This removes the ordinary COM selector as a candidate. CORR-135 supersedes the later `0x08A -> B6` inference: the current F33 discriminator is which external/local state selects or modulates the B6-independent internal assist path, while `0x08A` producer/SecOC/arbitration ownership is a separate network question. The 0x51E observations are only about one sample per second, so they do not establish high-rate timing; their stronger fact is that the relevant fields are zero for the entire retained routes. VAR-081 already supplies the LTA/LCA state identification; FRC `0x1601` is independent corroboration, not a naming prerequisite. Nothing here authorizes output.

Deterministic evidence is `data/generated/camry_2026_baseline_selector_live.json`, generated by `tools/analyze_camry_2026_baseline_selector.py` and verified by `tests/verify_camry_2026_baseline_selector.py`; static selector provenance is in `data/generated/camry_8965F3307000_command_cone_ingress.json`.

## 32. Exact-F33 passive internal-assist RDBI oracles: term proxies exist; selector state does not

VAR-080 closes the most useful read-only diagnostic observability around the B6-independent `D0218` baseline-assist path. The exact 241-record F33 RDBI table resolves to **195 unique callbacks reading 136 distinct `>=FEBE0000` RAM source cells**, and has **no callback that directly reads `FEBEC158` or `FEBEC156`**. The canonical graph has 34 direct selector-reader functions; their write targets intersect those 136 direct RDBI source cells **zero times**. Thus the recovered `C54A2/C5554` parameter-bank selector is not directly enumerable through an exact DID. This is a canonical direct-reference negative: pointer/indexed copies and downstream-derived diagnostic effects remain bounded.

Two `D0218` terms do have exact passive RDBI projections. `D0D7C` computes `FEBEAE12 = clamp(FEBEC5EE * FEBEAE3C / 0x8000, +/-0x569A)` and `FEBEAE6E = clamp(FEBECB38 * FEBEAE3C / 0x8000, +/-0x569A)`; `BF3AA` snapshots those to `FEBEE8B6` and `FEBEE8C2`. DID `0x1C3E` / callback `0x4EA90` returns `(FEBEE8B6*100)/0x80`, while DIDs `0x1C38`, `0x1C4A`, and `0x1C50` / callbacks `0x4EA06`, `0x4EB7C`, and `0x4EC06` all return `(FEBEE8C2*100)/0x80`; every callback saturates to signed16 before emitting the two-byte payload. `FEBEAE3C <- FEBEB140` is the internal calibration-derived scale already closed by VAR-078. These DIDs are therefore exact **scaled/clamped term proxies**, not raw `D0218` terms and not OEM-named engineering units. Current target-native `EMPS_P5` names none of these four exact F33 DIDs; Toyota's named downstream reference remains DID `0x1C02` **Command Value Torque**.

A tempting selector join also collapses under exact calibration bytes. `C9812` syntactically indexes `PTR_DAT_000D39DC[FEBEC156&3]` on the path to `FEBEC5EC -> C9A84 -> FEBEC5EE`, but all four exact pointer entries are the same `0xB018A`; VAR-075 also proves the resulting `FEBEC5EE` contribution is zero in both retained drives. `C8678` similarly indexes `PTR_LAB_000D3630[FEBEC156&3]` plus selector-strided `D3670/D3674` tables on the path to `FEBEC4C0`, but the exact maps alias (`0xB1208` x4; the pair family repeats `0xB1248/0xB121C` for all four banks), and no exact RDBI callback directly reads `FEBEC4C0`. So `0x1C3E` is a useful moving-assist/control oracle, **not** a selector-state discriminator. The selector's meaningful exact-image effect remains elsewhere, notably the `C28FC -> C2B64 -> FEBEBF3C` parameter-block path, for which no direct exact RDBI term readout is recovered.

For any future passive validation capture, the most discriminating EPS reads remain: **`0x1C38` first** as a direct proxy for `FEBECB38`; **`0x1C02` second** as Toyota-named **pre-slew Command Value Torque diagnostic state**; and **`0x1C3E` as a control** expected to stay quiet under the retained-drive moving-mode conditions. VAR-083 now gives `1C02` a stronger interpretation: its `CC62` source is physically relevant because the same value continues intra-function into `CC66/CC64`, even though the `AC56/EE40A/1C02` copy itself is the diagnostic sibling rather than the motor-driving `AC54/EE40C` branch. These reads can be synchronized with FRC `0x1601`/`0x1914`; none requires or authorizes steering output.

Deterministic evidence is `data/generated/camry_8965F3307000_internal_assist_oracles.json`, generated by `tools/build_camry_8965F3307000_internal_assist_oracles.py` and verified by `tests/verify_camry_8965F3307000_internal_assist_oracles.py`.


## 33. Exhaustive Bus-4 field census: no ordinary external CAN field reproduces as the steering carrier

The retained state is now strongly identified as LTA/LCA active (VAR-081), so the
relay-correct Toyota Bus-4 capture can be searched without the old generic-Class-L
ambiguity. A new unrestricted field census enumerates **every periodic bus-0 ID/DLC
stream**, not merely F33's 43 accepted generated-COM IDs, across each LTA/LCA interval
plus an eight-second margin. The candidate family includes byte-aligned u/s8, u/s16
BE+LE, u/s24 BE+LE, exact 10/12-bit windows, nibbles, bits, and per-frame deltas; rolling
counters/checksum candidates, constants, and duplicate series are suppressed before a
25-ms, +/-500-ms lead/lag sweep against the exact `0x030 B22:B23` motor-feedback proxy,
`0x025` steering angle/rate, driver torque, and speed.

Drive A contributes **200 bus-0 streams / 5,021 kept candidates / 2,221 refined**; drive
B contributes **153 / 5,448 / 1,803**. The cross-drive intersection is **930** refined
fields, with **69** reproducing at `|r_motor| >= 0.40`. Exactly **zero external fields
reproduce as leading the motor proxy by >=50 ms**, and exactly zero fields reproduce as
leading steering rate by that threshold. The angle-lead pass is a useful positive
control: every reproduced field that leads measured steering angle is inside **`0x030`**,
the exact F33 EPS transmit frame. `0x030[8]s8` (the steering-torque family) leads measured
angle by roughly +350/+250 ms in A/B, while `0x030[22]s16be` is the expected motor-proxy
identity at lag zero. The method therefore detects actuator-before-motion relations; it
just does not find one on an external CAN ID.

The strongest external families are feedback-shaped instead: `0x081[16]` and
`0x08A[18]` reproduce smooth angle/motor correlations but lag the motor by roughly
200–250 ms and remain strongly correlated in ordinary cruise; `0x025` is measured-angle
identity; exact `0x090` candidates are already closed as observer/feedback state. The
known `0x0D7`, `0x13B`, and `0x127` families do not produce a cross-drive command-like
lead. Streams below 50 frames in the analysis window are excluded from correlation; that
is at most roughly 1–1.5 Hz and cannot be a continuous steering carrier for the
millisecond-scale EPS control path. Low-rate `0x412` remains useful as display/state
corroboration, not a command candidate.

This is a strong **ordinary-CAN matched negative**, not by itself an explanation of stock
LTA authority. In particular, it must not be used to conclude that factory LTA was merely
internal damping. CORR-130/VAR-083 now independently close the physical command/current
convergence: `CC62` is the pre-slew value feeding `CC66/CC64 -> AC54/EE40C -> 6AF4 ->
6E0A -> 6DEC/6DC8/6DD6`, while `AC56/EE40A/1C02` is its diagnostic sibling. The
remaining search therefore moves **upstream of `CC50/CC62`** and into the two hidden-
ingress residuals bounded by VAR-084, not into another Bus-4 or downstream motor sweep. Deterministic evidence is
`data/generated/camry_2026_bus4_field_leadlag.json`, generated by
`tools/analyze_camry_2026_bus4_field_leadlag.py` and verified by
`tests/verify_camry_2026_bus4_field_leadlag.py` (VAR-082). No vehicle traffic is sent and
production output remains unauthorized.

## 34. Exact F33 physical steering-current convergence: `CC62` is pre-slew; `AC56/EE40A/1C02` is its diagnostic mirror

A motor-side re-audit corrects the direct-reference-only reading of `FEBECC62`. The
important subtlety is inside `D042C`: it **writes** `FEBECC62` from `FEBECC50 *
FEBEAC5A / 0x400`, immediately reloads that same value into a local, and then uses it to
form/slew `FEBECC66`. Canonical cross-function data references therefore show only
`C4F04` and `D0AAE` as direct *readers* of `CC62`, but that reader census misses the
same-function `CC62 -> CC66` value-flow. The physical command/current chain is:

`D039E/FEBECC50`
→ `D042C/FEBECC62` (pre-slew value)
→ `D042C/FEBECC66` (slew/gate)
→ `D047C/FEBECC64` (normal copy, or bounded internal `CC94/CC98` override)
→ `D0AAE/FEBEAC54`
→ `BF33E/FEBEE40C`
→ `35C4C/FEBE6AF4`
→ `387BA/FEBE6E0A`
→ `38502/FEBE6DEC`
→ `3835E/FEBE6DC8` + `384D8/FEBE6DD6`
→ downstream motor-control transform `38162`.

The writer sets are narrow and mechanically pinned in the exact 6,065-function corpus.
`CC64` is written by `D047C` plus reset/clear `D01B4`; `AC54` by `D0AAE` plus reset;
`EE40C` by `BF33E` plus reset; `6AF4` by `35C4C` plus the common state consolidator;
`6E0A` by `387BA` plus consolidator; `6DEC` by `38502` plus consolidator; `6DC8` by
`3835E` plus consolidator; and `6DD6` by `384D8` plus consolidator. `38162` directly
reads both `6DC8` and `6DD6`. In the normal branch `35C4C` sets `6AF4=-EE40C`; its
service/limit branches can substitute a bounded internal `6AF8` value before the **same**
`6AF4 -> 6E0A` funnel. `D047C` likewise has an internal `CC94/CC98` return/limit
override. Neither is a recovered second additive external lateral target.

This also explains the Toyota diagnostic observables cleanly. `D0AAE` simultaneously
copies the pre-slew `CC62` to **`AC56`** while copying the motor-driving post-slew/override
`CC64` to **`AC54`**. `BF33E` mirrors those as `EE40A` and `EE40C`, respectively.
The `AC56/EE40A` branch continues to `FEBE6772 -> DID 0x1C02 Command Value Torque`; its
motor-side sibling `EE40A -> 35C4C/6AF6 -> 387CE/6E22/6E24` terminates in
snapshot/report consumers. By contrast, **`EE40C` is the value consumed into `6AF4` and
the physical current-control funnel**. Likewise `37F16` copies the downstream current
states `6DD6/6DC8` to `6D84/6D86`, the recovered `1152/1154` diagnostic family; those are
observers of the downstream current command, not its upstream source.

So CORR-130 is not “`1C02` is unrelated to actuation.” The exact statement is:
**`1C02` is a diagnostic mirror of the pre-slew `CC62` value, and that same `CC62` value
really does feed physical actuation through an intra-function `D042C -> CC66` edge and
then the sibling `CC64/AC54/EE40C` branch.** This is why a pure cross-function
reader census was misleading.

The B6-inactive `D0218` contribution is also preserved rather than re-derived. Its eight
value terms reduce structurally to measured steering torque (`C43C`, `C3BA`),
torque+speed map/gain state (`C4C0`), internal assist aggregation (`CC2C`), a
nonnegative `|torque|` calibration term (`BF3C`), angle-domain ramp/return/dither
(`CB38`), retained-drive-zero moving-mode term (`C5EE`), and phase-window angle
excitation/return (`CBE8`). The `C28FC/C2B64` normal selector is likewise closed:
healthy selector 1 is the only distinct 0x220-byte bank, selectors 0/2/3 alias, all
fallback banks alias, and route-zero ordinary sig160 can reach only equivalent selector
0/2. None of those ordinary model inputs supplies an independently recovered lane target.

The former “upstream contradiction” framing is now superseded by CORR-135. These exact functions themselves show how 73.303384 s of LTA/LCA-active operation can steer with zero B6: the B6-inactive internal assist value reaches the same physical current funnel. CORR-134/VAR-081 separately recover Bus-4 `0x08A` Target Lateral ID plus target angle while exact F33 excludes `0x08A`. The current questions are therefore **which exact external/local state selects or modulates this internal path during LTA/LCA** and, independently, **who produces/security-protects `0x08A`**. No `0x08A -> B6` stock-LTA transform is established or required. Nothing here authorizes output.

Deterministic evidence is carried by
`data/generated/camry_8965F3307000_internal_assist_oracles.json` and
`tests/verify_camry_8965F3307000_internal_assist_oracles.py` (VAR-083 / CORR-130).

## 35. Hidden-ingress false-negative audit: no concrete alternate producer found; residuals closed in §36

This audit was originally launched because zero-B6 factory steering was treated as tension with the firmware model. CORR-135 removes that premise: the exact B6-independent `D0218` path already reaches physical actuation. The audit remains useful as a bounded false-negative census of hidden mutation/ingress mechanisms, but those mechanisms are no longer required to explain the retained LTA/LCA observation.

Several blind-spot classes were checked directly against exact F33 CodeFlash, the canonical
corpus, and the retained LocalRAM/GlobalRAM snapshots:

- **Pointer/index tables:** a full CodeFlash scan found no ROM-resident address value that
  points into the widened command/motor/D0218/B6-snapshot region. The retained live RAM
  snapshots likewise contain no word aliasing a command/motor-cone cell; the only
  ROI-adjacent address-looking values are three self/buffer pointers inside the already-known
  COM staging region (`FEBE7E94→FEBE7F05`, `FEBE7EE0→FEBE7F08`,
  `FEBE7FBC→FEBE7FBC`). This sharply bounds descriptor/pointer-indexed hidden copies.
- **Interrupt entry code:** fixed `INTBP=0x20200` / `EBASE=0x20000` exposes nine
  non-default unrecovered ISR entries. Statement-level disassembly shows those entries
  delegate into recovered timer/serial/acquisition functions; the transitive delegate set
  contributes no command/motor ROI writer. This closes a real canonical-corpus blind spot:
  the ISR entry bodies themselves were not recovered as ordinary functions.
- **Fixed DMA:** descriptor-shaped SFR-source→RAM-destination records in the exact image
  route on-chip peripheral/serial sources into the known GlobalRAM rings/FIFOs/heads
  (`FEEF80A0..FEEF9128`); **no fixed descriptor targets LocalRAM**. That strengthens
  VAR-073's old boundary. A runtime rewrite of a DMA destination register is still a
  separate residual below.
- **Indirect callbacks:** the checksummed `FEBF1194/FEBF1198` callback family installs
  fixed CodeFlash targets; the existing control-transfer audit already bounds the wider
  indirect-call surface. No diagnostic/WDBI writer into the shared `CC50/CC62` funnel was
  recovered.
- **CAN/controller escape:** the 47 exact RSCFD acceptance rules remain exhausted by the
  43 normal records + diagnostic/XCP tail, and the MCU still has one RS-CANFD unit. There
  is no second hidden normal-CAN ingress to invoke.
- **Large unrecovered flash gaps:** spot/structure review classifies the major gaps as
  calibration/crypto/data tables rather than a hidden second application-control program;
  the executable unrecovered islands relevant here are the ISR entries above.

No concrete alternate external steering-value ingress emerged from those classes. At this
stage two static false-negative modes remained worth keeping explicit rather than
rediscovering; §36 / VAR-085 now closes both within their declared static scope:

1. **register-arithmetic computed store target:** a pointer/value assembled through runtime
   arithmetic could evade canonical direct-reference recovery even when no stored ROM/RAM
   pointer equals the destination;
2. **runtime DMA destination reprogramming:** the fixed descriptor tables are closed, but an
   application path that rewrites a DMAC destination register after initialization has not
   yet been exhaustively disproved.

The clean static falsifiers were correspondingly narrow. **E1:** adapt the existing computed
call-target backtracker into a store-target resolver and classify every recovered STORE whose
effective address is not already resolved, reporting any arithmetic chain that can land in
the command/motor ROI. **E2:** census every recovered writer of the DMAC destination-address
SFRs and prove that every runtime value derives only from the fixed ROM descriptor tables.
Those falsifiers have now been executed and are preserved below rather than left as future
work.

The direct vehicle observation remains evidence to explain, but it no longer demands a hidden command ingress. The supported conclusion is narrower: **ordinary CAN, the known fixed DMA and pointer/callback paths do not supply a second external lateral magnitude into `CC50/CC62`; exact F33 nevertheless has a B6-independent internal assist path that can actuate.** VAR-085 removes E1/E2 as hidden-mutation escape hatches. The remaining F33 question is which external/local authority or mode state selects/modulates that internal path during LTA/LCA.

## 36. E1/E2 closure: computed STORE arithmetic and runtime DMAC destination provenance are clean

VAR-085 executes the two falsifiers left open by §35 against the exact F33 image and the
canonical **6,065-function** decompiler corpus. The reusable target-native resolver is
`ghidra/scripts/investigate/AuditComputedStoreTargets.java`. It works on HighFunction STORE
pointer expressions, recovers conservative unsigned-32 address ranges through constants,
casts, adds/subtracts, masks, shifts, multiplies, `PTRADD/PTRSUB`, and bounded PHIs, and
reports only target intersections that are not already represented by a canonical write
reference. Unknown/unbounded pointers are deliberately not converted into false certainty;
that general memory-corruption class remains separate from E1/E2.

**E1 — register-arithmetic STORE targets.** Across **13,493** recovered STORE operations,
**5,011** have a statically bounded target range. Scanning the command/current/D0218 target
set produces **100 candidate STORE rows in 46 functions** before exact runtime/configuration
bounds are applied. Every candidate collapses outside the target cell it only overlapped
under the coarse range analysis:

- the `FEBE71F2` candidates are ordinary indexed status arrays: `3B8E4` receives only
  literal lane indices **0..7**, while `3C108/3C116/3C184/3C19C` are bounded to
  indices `<0x18`;
- generated-COM bookkeeping candidates are confined by exact manager/event/route counts to
  `FEBE48xx..FEBE4Fxx`; the five route buffers are fixed at
  `FEBE3DF8/FEBE3E2C/FEBE3E48/FEBE3E64/FEBE3EA0`;
- XCP/CAN-manager scratch candidates are confined to `FEBE493E..FEBE503A` by the exact
  state/rule counts; diagnostic-event state is bounded below `FEBE5527`;
- the logical-block family has exactly three state rows and backing buffers
  `FEBE5651/FEBE5751/FEBE5851`; the apparent wide indexed motor/snapshot families are
  called only with the exact five-channel domain **0..4**; and the remaining `CBxx`
  helpers carry explicit `<=0x13` / `<3` bounds.

The result is **zero recovered register-arithmetic STORE path that can land on an audited
steering command/current target after exact index provenance is applied**. This closes
VAR-084 **E1** as defined. It does not assert that an arbitrary corrupted pointer can never
write there.

**E2 — runtime DMAC destination reprogramming.** Exact F33 uses a `0x40`-byte channel
slice at `0xFFFF8400`; the two destination-address registers are offsets **`+0x04` and
`+0x14`**. Running the same resolver against all 32 destination-register addresses yields
only **5 candidate STOREs in 3 functions**: `607FE`, `6080E`, and `609B0`. Their actual
per-channel offsets are `+0x20`, `+0x2C`, or `+0x38`, so modulo the `0x40` stride they
cannot be either destination register. Exact recovered writer provenance then leaves:

- destination `+0x04`: writer `6082C` only; `6091E` is a read-only accessor;
- destination `+0x14`: writers `6082C` and runtime refresher `60A6A` only;
- `60A6A` has exactly four recovered callers (`60462`, `60C20`, `61B90`, `628B2`),
  and every callsite passes one of the seven already-pinned fixed CodeFlash descriptor
  families (`310A8`, `3125C`, `312AC`, `314AC`, `314FC`, `3154C`, `3161C`).

Those seven tables contain **22 descriptor rows / 44 destination fields / 22 distinct
destinations**. Both destination copies in each row agree, and **none of the 44 fields is
in LocalRAM `FEBE0000..FEBFFFFF`**. Therefore the recovered runtime updater can refresh
known peripheral/GlobalRAM routes but cannot retarget DMA into the steering-command cone.
This closes VAR-084 **E2 within recovered application dataflow**. Arbitrary unknown-pointer
corruption or a hardware fault remains outside the claim; no separate destination-register
programmer is recovered.

Together E1+E2 remove two strong “Ghidra missed a hidden writer” explanations inside F33. CORR-135 corrects the later network-boundary interpretation: `0x08A` carries Target Lateral ID plus a target angle and strongly matches Toyota ordinary-P5 SecOC framing, but exact F33 does not accept it and **no `0x08A -> B6` stock-LTA transform is proved or needed**. The B6-inactive `D0218` path itself reaches actuation. Current work therefore traces F33 authority/mode state into that path and tracks `0x08A` producer/security ownership separately.

Deterministic evidence is
`data/generated/camry_8965F3307000_hidden_ingress_residuals.json`, backed by the two
promoted target-native STORE censuses and
`tests/verify_camry_8965F3307000_hidden_ingress_residuals.py` (VAR-085).

## 37. OQ-052 longitudinal discriminator: synchronized read-only Brake/FRC request capture is turnkey

The next OQ-052 read-only oracle identified by TMS-085/VAR-069/070 — Brake `0x7B0`
RDBI `22 10 A1..A4` synchronized with FRC `0x792` `22 1B 03..1B 07` plus all-bus
CAN — now has its acquisition tooling complete and deterministically verified, so
the live step needs no further code work.

`tools/camry_tss3_request_capture.py` is the single-USB-owner poller. It schedules
the nine pinned `(ECU, DID)` reads in responder-interleaved order on one monotonic clock,
with independent per-DID due deadlines at a configurable target rate (default 2 Hz) so a
busy target cannot increase another DID's cadence. It enforces **at most one unresolved
RDBI per responder**: a busy
ECU is skipped until its response resolves, and receive traffic is drained before another
query is selected. It reuses the LTA capture tool's pandad ownership guard, ELM327
safety configuration, and compact `can.bin` all-bus writer rather than duplicating
them. Routes are fixed, not probed: FRC `0x792->0x79A` is the VAR-064 live-proven
post-repin bus-0 route, and Brake `0x7B0->0x7B8` is the pair VAR-069 pins, on the
same bus 0 that the 2026-08-27 DTC sweep live-reached (§17). The poll set, signal
geometry, and value decoding are loaded from
`data/generated/gtsplus_2026/toyota_diag_registry_camry_2026.json` and decoded
through the canonical `p5-linear-msb0-v1` contract in
`tools/techstream/ddb_semantics.py`; the tool fails closed if the registry's
profile, bus, addresses, or decoder drift, and no ad-hoc scale exists in the tool.

Transmit discipline is fixed: the only requests are the nine single-frame
`03 22 <DID>` reads in the default diagnostic session — no DiagnosticSessionControl,
SecurityAccess, RoutineControl, or write — plus exactly one ISO-TP flow-control
frame (`30 00`) per **expected** multiframe response, required because FRC DID `0x1B05`
declares a five-byte value record whose positive response cannot fit a classic single
frame; an unsolicited first frame is retained but cannot trigger flow control. Responses
are reassembled single-frame or first/consecutive-frame PDUs; positives are decoded to
timestamped raw + converted values with OEM pattern labels. ISO 14229 negatives still do
not echo a DID, but the one-outstanding invariant now lets the artifact safely record the
sole `request_did` that was outstanding without claiming it appeared on wire. NRC `0x78`
**Response Pending** is interim: it keeps that sole request outstanding and refreshes its
500-ms response window rather than releasing the ECU for another DID. A request that
otherwise remains unresolved for 500 ms, or any ISO-TP assembly timeout/sequence error,
**quarantines that responder for the rest of the capture** so a late response can never be
mis-associated with a retry. Raw error/timeout evidence is retained. Passive buses 0..2
are recorded throughout.

`tools/analyze_camry_tss3_request_capture.py` summarizes a capture directory
deterministically: per-DID query/response census, NRC and raw histograms,
per-signal decoded-value histograms and cadence; nearest-sample cross-ECU joins
(`0x10A3`↔`0x1B03` request IDs, `0x10A1`↔`0x1B04`, `0x10A1`↔`0x1B05` variation-no-limit)
reporting pair counts, |Δt|, and joint value tuples; and the exact `0x0AA`
wheel-speed moving context reused from the LTA analyzer. A DID with zero
positives is reported as unmeasured, exactly as captured.

This is verified capture **tooling**, not a live result
(`tests/verify_camry_tss3_request_capture.py`, suite
`camry_2026_tss3_request_capture`): no synchronized driving artifact exists yet,
live PID support on this car remains unmeasured, and the join output is
co-observation only — the FRC→brake copy/transform, cadence, arbitration
executor, and SecOC/integrity ownership remain OQ-052's open questions.

## 38. First-principles stock-LTA correction: secured `0x08A` and F33 internal assist are separate planes

CORR-135 removes the architecture assumption that accumulated after the `0x08A` target-angle recovery. Three exact evidence surfaces now have to be held simultaneously:

1. **`0x08A` is a real secured-looking lateral-request PDU, but not exact-F33 normal CAN.** B21 carries the Target Lateral ID state and B18:B19 the signed target-angle quantity. Every retained frame is on the Toyota Bus-4 capture; exact F33's 43 normal Rx descriptors exclude `0x08A`, its generated-COM Tx IDs are only `0x030/0x351/0x394/0x4A3/0x4C8`, and its 47-rule acceptance surface adds only diagnostics/XCP. The trailer strongly matches ordinary Toyota P5 SecOC: candidate reset-low2 agrees with preceding authenticated `0x00F` at 96.376% A / 96.237% B, candidate message-low2 advances +1 on every same-reset B26+1 pair, B27 is zero, and the remaining 28 bits are effectively frame-unique. This supports `FV4 || MAC28` structurally, not an exact sender/key/profile claim.
2. **Zero B6 does not require a missing cooperative packet.** Exact `FUN_000D0218` has an ordinary B6-inactive branch that computes `FEBECC48` from eight internal assist terms, and the exact `CC48 -> ... -> motor-control` chain reaches physical current control. The retained 73.303384 s is machine-identified **request state** (`0x08A` ID11/LTA-LCA), not a direct grant oracle: zero B6 is architecturally consistent with F33 continuing to actuate, but the logs do not prove that this internal path carried autonomous lane-centering authority. Operation FFD `5285/57DE/5265` is the missing grant discriminator.
3. **B6 remains a separate protected external cooperative-control ingress.** Exact F33 really does accept B6 and consume its target/mode when active. That makes B6 a possible future openpilot actuation interface, but stock LTA does not prove that Toyota converts `0x08A` into B6. If B6 is chosen, its signer/freshness/suppression/arbitration contract must be recovered on its own evidence.

The current work is therefore three-way. VAR-091/CORR-149 close observed bus placement **and the FRC side of the TSK boundary**: the FRC is the request-side participant, not the TSK key holder, so the remaining stock-path question is which downstream Brake/Skid/CGW proxy receives the request and publishes the authenticated Bus-4 PDU. VAR-090/092 close default-bank `D0218` as not an F33 COM copy of the published milliradian. Synchronized FRC Operation FFD must separately determine whether the retained ID11 request was selected/granted. Protected B6 remains an independent candidate openpilot ingress.

**Regression rule:** do not infer or document an `0x08A -> B6` stock-LTA transform from matching scale, bus topology, or F33's `0x08A` exclusion. Such a transform may be considered only if producer firmware or synchronized evidence positively recovers it.

Deterministic evidence is `data/generated/camry_2026_lta_state_reconciliation.json`, `data/generated/camry_8965F3307000_internal_assist_oracles.json`, and their verifiers; the correction is recorded as CORR-135 / VAR-087.

## 39. Complete `0x08A` field census, EMPS `0x1CEE` record join, and opendbc entry completion (VAR-088)

A dedicated deterministic pass over the same two relay-correct drives closes every
application byte of `0x08A/32` (44,613 deduped bus-0 frames; per-B21-state census):

| bytes | closure |
|---|---|
| B0,B1,B2,B5,B15,B25,B27 | identically zero in every retained frame |
| B3[3] | cruise operating-state latch (value `8`); VAR-067's MAIN/CANCEL joins |
| B6,B7 | cruise sub-state pair `(0,18)` off, `(45,71)` LTA/LCA-active, `(44,70)` second sub-mode, `(0,146)` 33 transitional frames |
| B8:B9 and B11:B12 | **byte-identical duplicated signed16 in 100% of frames**; raw range −1146..995; four negative joins bound semantics (`\|r\|<=0.07` vs speed-derived acceleration, `0x025` angle, `0x030` driver torque, and B18:B19 target-angle rate) |
| B10 | latched cruise set speed, 1 km/count (RES+ 66→67→68→70; FRC `0x1901` Memory Vehicle Speed concept corroboration) |
| B13:B14, B16:B17 | constant `0x7FFF` sentinel slots in every frame |
| B20[7:6], B22[4] | cruise-state mirrors of B3[3] (44,587/44,613 agreement; 26 transition frames) |
| B21 | Target Lateral ID, value set exactly `{0,11,18}` in both drives |
| B23[5] | set in every SDG row (1,898/1,898); toggles inside LTA/LCA (605/2,934 set) |
| B24 | request level `0/50/100`: **100 in every LTA/LCA frame (2,934/2,934)**, **50 in every SDG frame (1,898/1,898)**, 0/50/100 in manual; percent unit bounded, not OEM-joined |
| B26[5:0] | modulo-64 application sequence (six-bit boundary an encoding assumption) |
| B28..B31 | ordinary-P5 `FV4 \|\| MAC28` trailer (CORR-135): message-low2 tracks B26+1, reset-low2 tracks authenticated `0x00F` |

Current GTS+ joins the naming side. **EMPS_P5 DID `0x1CEE` is one four-monitor
structured record**: 2069 *Target Lateral ID* (bits 0-7; full **19-value**
generation-20 dictionary — 0 No Request (Manual Operation), 1 PCS, 4 LDA,
10 Hands Off LTA, 11 LTA/LCA, 13/15 DESA, 18 SDG, 19 PDA, 25 AP, 27 Remote
Parking, 35-39 Lv.3, 41-45 Lv.4, 49 Self-Propelled Transport, 63 Driver
Operation), 2070 *Cooperative Control in Progress Flag* (bits 8-15, 0=OFF/1=ON),
2071 *Target Steering Angle After Output Compensation* (bits 16-31, signed16,
1.5 deg/count diagnostic view), 2072 *Advanced Drive Target Steering Angle*
(bits 32-47). TMS-060 already bounds the live-oracle consequence: `0x1CEE` is
**absent from exact F33's 241-record RDBI table**, so the EPS-side cooperative
target is not directly pollable on this car; `0x1C3E/0x1C38/0x1C4A/0x1C50`
remain the internal-assist RDBI proxies (§32).

Producer attribution gained a bounded negative: the Bus-4 ECU dictionaries
(`ABS_P5`, `Brk_Bst_P5`, `EPB_P5`, `BSCM_A_P6`) carry **no lateral-request DID
vocabulary** (only Lateral-G observers and Vehicle-Motion-Control longitudinal
limits), and "Cooperative" DIDs exist only in `EMPS/EMPS2`. GTS+ therefore
cannot name the `0x08A` producer from DID semantics — consistent with
`tss3_control_ownership_surface`'s exhausted static search. Producer/SecOC
ownership and the F33 stock-LTA authority selector remain OQ-054's open
questions; the B6 DTC attribution to the Brake System Control Module domain
(§"external lateral ingress") remains the only positively attributed immediate
source domain.

The fork's opendbc `toyota_tss3_pt` `0x08A` entry (`TSS3_LATERAL_REQUEST`) now
carries the complete census-bounded field set — cruise latch/sub-states,
duplicated request word, set speed, sentinel slots, cruise mirrors, cooperative
substate flag, request level, sequence, and the `FV4+MAC28` trailer geometry —
with the full 19-value Target Lateral ID `VAL_` dictionary on both `0x08A` and
protected B6. Passive observables only; no output authorized.

Deterministic evidence: `tools/analyze_camry_2026_upstream_request_census.py`,
`data/generated/camry_2026_upstream_request_field_census.json`, and
`tests/verify_camry_2026_upstream_request_census.py` (suite
`camry_2026_upstream_request_census`).

## 40. Zero-MAC28 receive-bridge candidate: F33 COM splice geometry pinned and audited (VAR-089)

The exact-F33 static path to a replacement B6 sender is now closed as an
audited build-time candidate. The stock generated-COM receive plane was
decoded end-to-end: the PDU44 window base table at `0x22840` places B6
application bytes B0..B27 at `0xFEBE4BFF..0xFEBE4C1A` (windows
`0x1BA/0x1BB` resolve through `FEBEB800 − 0x6DB8 + window`), the SecOC
level-1 queue keeps the B6 pending record at `0xFEBE546A + 2*8 =
0xFEBE547A` with the 32-byte secured frame at `0xFEBE54AC + 40 =
0xFEBE54D4` (ROM record idx2: length 32, displacement 40, trailer config
2 = asynchronous ICU-S verify), and the periodic unpacker `0x4BD46` gates
solely on the per-PDU new-data inequality `0xFEBE5364 != 0xFEBE80C8`.

`camry_f33_b6_bridge.c` + `build_camry_f33_b6_bridge.py` compile a
RAM-only scheduler-ownership bridge on the audited toolchain (Sienna
byte-equivalence gate): it reproduces the exact boot → application-context
→ startup-JARL transition, **relocates its resident loop into the
live-proven 524-byte high tail before app-context init** (stock startup
overwrites the low staging pocket), runs the stock foreground scheduler
with the comm/SecOC aggregate `0x667E6` in place, snapshots any queued B6
whose 28 transmitted MAC bits (`B28[3:0]|B29|B30|B31`, mask `0xFFFF0F0F`
little-endian) are all zero, and re-injects its 28 application bytes into
the COM window buffer plus new-data toggle after the aggregate rejects the
frame — so the stock unpacker, mode-2 activation, slew/limit chain, and
motor funnel run exactly as if SecOC had verified it. No stock code is
patched and no key is recovered; a reset restores the unmodified path.

Audited identity: 528-byte staged blob (SHA-256 `ab38df4f…ae576d7`), 428
bytes resident-inclusive bound vs. the 508-byte budget before the
`0xFEBFFBEC` heartbeat cell, zero relocations, PIC, entry offset 0. The
builder re-derives every firmware pin from the pinned CodeFlash image
before compiling and refuses to emit on drift.

Boundary: **static candidate, not live-validated**. Hardware activation
requires the maintainer-held boot secret, a stationary ID11/zero-angle
acceptance check, and the fork's dev-only openpilot sender (`ToyotaTss3DevLateral`
+ exact-F181-bound ephemeral bridge params, ALLOW_DEBUG panda build with
the B6-only `TSS3_DEV_LATERAL` whitelist). opendbc-side sender, ramp-down
release semantics, and the real-C-hook acceptance test landed with this
section (`opendbc.car.toyota.tests.test_tss3_camry`, 27 tests).

Deterministic evidence: `exploit/ephemeral_runtime/camry_f33_b6_bridge.c`,
`exploit/ephemeral_runtime/build_camry_f33_b6_bridge.py`,
`exploit/ephemeral_runtime/audited/camry_f33_b6_bridge.bin`,
`exploit/ephemeral_runtime/audited_camry_f33_b6_bridge_build.json`, and
`tests/verify_camry_8965F3307000.py --section b6_receive_bridge`.

## 41. `0x08A` placement/authentication bounds: downstream proxy transmitter/signer remains open (VAR-091 / CORR-136 / CORR-149)

The two relay-correct drives plus GTS+ canbus for Camry HV type **12984** close bus placement and the observed trailer shape. Combined with the recovered Toyota TSK hardware architecture, they also close the FRC side of the trust boundary: **the FRC is not a TSK key-holder/signing participant; a downstream TSK-capable chassis/gateway participant must proxy the FRC request into the authenticated Bus-4 domain.** The remaining identity question is which downstream participant performs that assembly/signing and physical publication.

**Placement.** Every retained `0x08A/32` is on the Toyota Bus-4 capture (panda bus 0 / relay mirror 2); Bus 1 count is **zero**. GTS+ `canbus 12984` places **Front Camera Module on Bus 1 only**. Bus 4 native application nodes are Airbag, Brake Booster, Power Steering (EPS), Skid Control, and SAS, all behind Central Gateway. This is a topology candidate set, not an arbitration-ID source map. Post-repin FRC UDS `0x792` on panda bus 0 is diagnostic gatewaying, not proof that FRC is a Bus-4 application node.

**Not EPS.** Exact F33's generated-COM Tx set is only `0x030/0x351/0x394/0x4A3/0x4C8`; its normal Rx and complete acceptance surface also exclude `0x08A`.

**Rlog timing cannot attribute the source.** The observed `0x08A` rate is 38.122 / 39.997 Hz. The apparent 20/30 ms gap mix is not a physical CAN timing fingerprint: each rlog `Event.logMonoTime` timestamps a complete CAN publication batch. Median bus-0 batch size is 14 frames in both drives, and 20,607/20,615 A plus 23,999/23,999 B `0x08A` frames share their timestamp with another frame. CAN arbitration delay, same-controller scheduling, TX-queue identity, oscillator skew, and transmitter identity are not recoverable from those gaps. The former “not Skid's `0x0D7` queue” claim is invalid.

**Observed Bus-1 envelope.** Bus 1 contains zero `0x00F`. Every periodic Bus-1 stream (n≥50) has a near-constant last-4 (max unique fraction <0.002); FRC vision `0x180/64` last-4 is constant. These observed PDUs do not end in ordinary-P5 `FV4||MAC28`. Bus-4 `0x08A` does: B28..B31 remain on the vehicle `0x00F` reset domain (CORR-135) and the last-4 is frame-unique.

**Authentication boundary.** Toyota's recovered TSK path keeps the AES-CMAC key in protected Renesas ICU-S storage on TSK-capable network participants. The FRC request domain is not such a key-holder/signing participant, and its observed Bus-1 output is E2E-protected rather than SecOC-wrapped (VAR-107). Therefore the FRC cannot be the source of the Bus-4 TSK authenticator: its semantic request must cross a private or differently packed handoff into a downstream TSK-capable participant, which then constructs/authenticates the chassis-domain publication.

**Closed vs open.** The FRC-hosted recorder carries `5282/5631`; Bus-4 `0x08A` carries the same ID/pinion/assist subset; exact F33 is neither transmitter nor consumer; native Bus-1 CAN does not carry `0x08A`. The downstream proxy/transmitter candidates by topology are Skid Control, Brake Booster, and Central Gateway, but none is selected. OQ-054 is now specifically to identify **which of those downstream participants receives the FRC request, arbitrates/repacks it, owns the TSK profile/key selection, and publishes `0x08A`**. Do not send `0x08A` to EPS.

Deterministic evidence: `tools/analyze_camry_2026_08a_producer_bounds.py`, `data/generated/camry_2026_08a_producer_bounds.json` schema v4, `tests/verify_camry_2026_08a_producer_bounds.py`.

## 42. Bus-1 camera/radar output is plaintext; GTS+ names the quantities, not a CAN DBC (VAR-093)

Panda bus 1 is sniffed in both retained drives. The 22 periodic streams are readable as raw bytes. GTS+ still has **no** `BO_ 384` field map: it is DID/FFD keyed. The decode is a join from those OEM scales onto the wire.

**Inventory** (drive B; drive A is the same ID/DLC set): `0x180..0x18B/64` and `0x18C/48` at ~20 Hz, `0x160/32` at ~40 Hz, plus `0x020/12`, `0x123/16`, `0x1A0/48`, `0x200/0x201/64`, `0x230/64`, `0x440/0x450/32`. Authenticated `0x00F` is absent. Last-4 of `0x180` is constant `00000000` (not ordinary-P5 MAC28).

**CAN-FD framing.** `0x180..0x18B`: B0-B1 unique per frame (checksum/CRC), B2-B3 a shared rolling counter across the burst, last four bytes zero. `0x18C` uses the same header/trailer at DLC 48.

**Object slots on `0x180/0x181/0x182`.** After the 4-byte header sit **eight 7-byte slots**, then a 4-byte zero trailer. Empty slot is exactly `fff8000000ffff` (Toyota `0xFFF8`/`0xFFFF` invalid-style sentinels). Occupied slot bytes 0-1 as unsigned big-endian × **0.01 m** match FRC Data List `0x190A` Forward Vehicle Distance (mul 100, two decimal places, metres) and Operation-FFD `5A22` vertical distance (unsigned, LSB 0.01 m). Both drives: every occupied slot is in (0, 500] m; median 26.06 m A / 37.12 m B; max 384.37 / 439.11 m. That is perception range, not the Bus-4 `0x08A` milliradian.

FFD `5A24` (s16 lateral × 0.01 m) and `5A26` (s16 relative speed × 0.05 m/s) are **not** 1:1 overlays on slot bytes 2-5: those reads span hundreds of metres / thousands of m/s. Slot bytes 2-6 remain packed. The old 8-byte TSS2 radar DBC does not transfer.

**The rest of the family.** `0x160` is a ~40 Hz camera/radar-domain stream,
but CORR-138 retracts the former standing `0x160[22]` SAS-echo identity: its
full-drive correlation collapses and the field remains unnamed. `0x183/0x184`
use a different typed-record schema with float-shaped words (FFD Type-`f` /
32-bit FRC geometry vocabulary) but are not a copy of FFD `590C`.
`0x185/0x188/0x18B` are often idle zeros. `0x186/0x189/0x18A` are structured
and still unpacking. `0x18C/48` is the VAR-068 staircase/status PDU. GTS+ Bus 1
also contains Front Radar, so per-ID FRC-vs-radar TX is not named by CAN ID.

The native camera family contains perception plus other bounded state/observer
data. How FRC's TSS **request** is built, handed to chassis, and whether any of
that angle reaches EPS is §43 / VAR-094.

Deterministic evidence: `tools/analyze_camry_2026_bus1_camera_output.py`, `data/generated/camry_2026_bus1_camera_output.json`, `tests/verify_camry_2026_bus1_camera_output.py` (VAR-093/094).

## 43. Middle hop: FRC-hosted `5282`; no consecutive Bus-1 layout; authenticated request appears beside EPS (VAR-094)

This bounds camera-bus contents and EPS ingress. It does not identify the private transport, physical Bus-4 transmitter, or signer.

**Recorder object.** FRC is the TSS recorder host. Operation-FFD `5282` / LTA `5631` (LDA `5531` has the same shape) stores Target Lateral ID, signed pinion at 0.001 LSB, assist gain at 0.01, and damping gain at 0.01. Ordinary FRC Data List exposes LTA switch/control (`0x1601`) but not this four-field object. Named CAN observers include measured SAS `0x025` (FFD `2E8D` / `5273`) echoed onto Bus 1 as `0x160[22]`, EPS torque `0x030` (FFD `2E94` / `5247`), and the perception objects in VAR-093. Diagnostic `0x792` serves the recorder. Host location does not by itself prove final arbitration, wire packing, or CMAC ownership.

**Observed route boundary.** The consecutive recorder layout `ID || pinion_s16be || assist` is absent from native Bus 1: 200 spread ID11 samples with `|B18|≥20` per drive yield zero hits inside ±25 ms and zero global four-byte hits. Scattered two-byte collisions (22/200 A, 40/200 B) never concentrate on one `(CAN ID, offset)`. Bus 4 separately carries the matching subset in `0x08A`. The transport between the FRC-hosted object and Bus 4 may be private or differently packed; retained CAN does not select **which downstream CGW/Skid/Brake proxy receives, repacks/arbitrates, and signs it**.

**Observed packing relation.** `0x08A` retains ID + pinion + assist as B21 / B18:B19 / B24, omits damping (B25=0), adds a cruise sidecar, and carries ordinary-P5 `FV4||MAC28`. That structural relation does not prove which ECU performed each step. Dual-pinion record `1B40_2` is the live milliradian at B18; `1B40_3` is unpublished (`0x7FFF` at B13:B14 and B16:B17). Winner `5285`/`57DE` is not a distinct Bus-4 s16. Grant `5265` remains FFD-only.

**Steering angle, and whether any of it is relayed to EPS.**

| Quantity | On the camera bus | Relayed to EPS? |
|---|---|---|
| `0x160[22]` candidate | Former SAS-echo reading is retracted by CORR-138: full-drive correlation is only +0.086/-0.091 and the field remains unnamed. | No F33 ingress join; do not use it as a request or plant oracle. |
| Requested pinion | No consecutive `5282` layout is observed. | Bus 4 publishes the quantity as `0x08A` B18 **beside** EPS. Exact F33 does not Rx `0x08A`; protected B6 is idle in the retained ID11 intervals; `1B40_3` is unpublished; default-bank `D0218` is not this milliradian. The captures therefore do not show this requested angle entering F33 as COM. |

Remainder: private request transport, downstream Bus-4 proxy/transmitter identity, exact SecOC profile/key-selection owner, and whether ID11 was actually granted. The proxy identity needs producer/private-link evidence; the grant needs synchronized Operation FFD `5282/5285/57DE/5265`. Do not hunt another EPS CAN field or send `0x08A` to EPS.

Deterministic evidence: same artifact/test as VAR-093 (`request_object_on_bus1` in schema v2).

## 44. Install-set closure: the FRC is the sole diagnostically present ADAS compute ECU; the authenticated transmitter must be brake-family or gateway (VAR-096)

The "which box processes TSS" question is closed at install-set granularity by current
GTS+ master data, composing three already-verified surfaces
(`data/generated/gtsplus_2026/p5_adas_p6_migration.json`,
`tss3_crossvehicle_surface.json`, and the fleet map):

- **Older P5 compute split.** `PCS1_P5 (427) + DSSystem_P5 (428) + Fr_RadSen_P5 (429) +
  RoadSign_P5 (431) + PCS2_P5 (432)` co-install as one architecture — exactly the
  LS500/LS500h/MIRAI family. `DSSystem_P5` is the arbitration peer (small monitor
  surface, dependency-heavy lost-communication DTC graph); `PCS2_P5` owns the named
  request outputs including **PCS Steering Request**.
- **FRC generation absorbs them.** Across all five NA category-498 install
  architectures, those five compute-peer categories have **zero co-occurrence**
  (EU/JP likewise, `no_frc_join`). The Camry HV architecture is exactly
  `EMPS_P5 (405) + ABS_P5 (435) + BrakeBooster_P5 (466) + FRC_P5 (498)`
  (117 NA install rows, 28 models). The remaining production architectures only drop
  peers (405+435+498: 98 rows; 405+498: 36 rows); the two extras are the non-production
  `MAC` row set (4 rows, transitional: adds ADCU_P6 6037, LDA_P5 418, Fr_Camera_P5 430,
  Steering Actuator 499, 476/477) and `TEST` (1 row).
- **Consequence (bounded composition).** No separate arbitration/request ECU is
  diagnostically present on this car. The FRC is the consolidated compute unit — it
  demonstrably computes lateral and longitudinal requests (recorder `5282/5280/5281`,
  monitors `0x1B03..0x1B07`) — and the only co-installed peers are actuation/chassis
  ECUs. Therefore the MAC-authenticated Bus-4 transmission role (`0x08A`, and protected
  B6 per the U012987 brake-domain attribution) must live in the co-installed **brake
  family (ABS 435 / BrakeBooster 466) or the Central Gateway**, not in any ADAS peer.
  This narrows OQ-054's candidate set; it does not identify the transmitter.
- **Generation-22 direction.** `ADCU_P6` re-consolidates compute plus direct camera
  links (LVDS/GVIF/MIPI), internally dropping the Driving Support ECU / Pre-Collision
  Control / Image Processing / Cruise Control module vocabulary — a successor oracle
  only, never transferable onto this P5 car.

External architecture lineage (fork opendbc, external-source observation; it grades the
industry pattern, not this car's wire): `toyota_adas.dbc`/`toyota_radar_dsu_tssp.dbc`
carry a separate radar (`OBJECT_0/1`) plus **DSU** arbiter (`LEAD_INFO`, `ACC_CONTROL`);
`toyota_nodsu_pt_generated.dbc` deletes the DSU and puts **plaintext**
`STEERING_LKA (0x2E4, 5 bytes)` torque commands on the PT bus — the camera is brain and
mouth, which is exactly why openpilot TSS2 lateral is a message spoof;
`toyota_secoc_pt_generated.dbc` retains the names into the MAC era; our
`toyota_tss3_pt_generated.dbc` defines `0x08A` passively. The trajectory — separate
arbiter, then camera absorbs it and commands plaintext, then camera keeps compute but
loses the authenticated mouth, then ADCU re-consolidates — frames VAR-091/094: compute
stayed in the camera while transmission moved behind a key holder. Hyundai documents
the same split inside opendbc itself (HDA2: "Camera sends LKA steering message, ADAS
DRV ECU forwards it as LFA to MDPS"), supporting — not proving — the relay hypothesis
(hypothesis grade).

Deterministic evidence: `tests/verify_gtsplus_p5_adas_p6_migration.py` (498 install
architecture assertions); zero co-occurrence is additionally asserted by
`tests/verify_gtsplus_tss3_crossvehicle_surface.py`.

## 45. FRC request pipeline and absorbed `DSSystem_P5` / `PCS2_P5` roles: no Bus-1 self-loop; final arbiter remains FRC versus Brake (VAR-097)

This section is grounded in direct current-GTS+ DDB/plugin queries and the
recovered PCS initializer, not the narrative architecture alone. The
deterministic comparison now lives in
`data/generated/gtsplus_2026/p5_adas_p6_migration.json` schema v2 and is
regenerated by `tools/techstream/extract_gtsplus_p5_adas_p6_migration.py`.
Representative discovery commands are `tools/gts category 428/432/498 --json`,
`tools/gts did FRC_P5 --limit 1000 --json`, `tools/gts dtc FRC_P5 --json`, and
`tools/gts canbus 12984 --json`.

### 45.1 The recorder exposes a normalized request pipeline, not a proven ECU boundary

The recovered `DIDDataDefine::.cctor` rows distinguish four stages:

| Stage | Recorder evidence |
|---|---|
| feature requests | LDA `5531`, LTA `5631`, and PDA/OAA `5A09/5A0A/5A0D` each carry a lateral ID, requested pinion angle, assist gain, and damping gain |
| normalized TSS request | `5282` carries the same four ingredients; its layout is exactly equal to `5531` and `5631` |
| arbitration result | `5285` is result lateral ID; `57DE` is result pinion angle |
| execution/plant feedback | `5265` includes `Active steering under-control flag`; `560D` includes EPS pinion angle and LTA driver/control state |

This supports an internal software grammar
`feature request -> generic request -> arbitration result -> feedback`. It does
**not** locate final arbitration. The FRC-hosted recorder also contains
unambiguously external ABS/VSC and EPS observations, so recorder presence is
not producer evidence.

There is no observed CAN self-loop. On Toyota Bus 1, the retained captures
contain the plaintext `0x180..0x18C` perception family and other camera-domain
state; CORR-138 retracts the former standing `0x160[22]` delayed-SAS-echo
identity. They contain **zero `0x08A`** and
zero consecutive `5282` `ID || pinion || assist` layouts. Thus no evidence
supports “FRC serializes its request onto Bus 1, reads the same frame back, and
then produces a final package.” The simpler bounded model is that the FRC uses
its internal vision/object state directly, combines it with received plant
observers, and hands a compact request to an unobserved private/inter-ECU
boundary. Whether that handoff already contains an arbitration result or is
only a candidate request remains open.

### 45.2 `DSSystem_P5` is a sparse supervisor; its dependency and request roles continue in FRC

Direct parsing of NA `DSSystem_P5.ddb` (7,484 bytes) yields only **17 monitor
rows / 13 unique names**, all housekeeping (absolute time, key cycle, IG-on
elapsed time, master sync, distance, DTC count), **33 DTCs**, no routine Active
Tests, and no Operation-FFD plugin. Its useful architecture is the DTC graph:
it watches ECM/HV, multi-axis acceleration, SAS, Brake, Steering Effort, EPS
front/rear, body, IPC, side-obstacle, center/front-side radar, and Image
Processing Module A. It is a supervision/arbitration shell, not a payload
dictionary.

The FRC generation carries a much wider host surface: **283 monitor rows, 58
DTCs, 69 routine Active Tests**, TSS3-specific Image/Operation-FFD roles
`0xE9/0xEA`, and explicit internal domains for **Main Microcomputer in Front
Recognition Camera**, **Image Processing Microcomputer in Front Recognition
Camera**, LVDS, ADC, and image-processing-module/watchdog failures. Exact DTC
identity continuity from the disjoint pre-498 peers into `FRC_P5` is:

| Pre-498 ECU | exact DTC codes retained by `FRC_P5` |
|---|---:|
| `LDA_P5` | 18 / 21 |
| `PCS2_P5` | 16 / 31 |
| `DSSystem_P5` | 15 / 33 |
| `Fr_RadSen_P5` | 11 / 31 |
| `RoadSign_P5` | 9 / 11 |
| `PCS1_P5` | 3 / 32 |

Plugin continuity sharpens the division. `DSSystem_P5` has only generic
monitor/DTC/CID/support roles. `PCS2_P5`, which names `PCS Steering Request`
and pre-collision brake requests, adds active-test, RoB, and generic
`GetOperationFrzFrmDatP5_DT.dll` role `0xBA`. `FRC_P5` retains the same
monitor/active-test/RoB family but replaces that generic recorder with
`GetTSS3ImageFFDP5_DT.dll` and `GetTSS3OperationFFDP5_DT.dll`. Combined with
the zero-co-occurrence install-set result in §44, this is strong role-migration
evidence: the FRC assembly absorbed the old DSS/PCS/LDA/RSA compute and
supervision surfaces. Assigning the former DSS arbiter specifically to the FRC
main microcomputer is **recovered/inferred**, not firmware-proved code identity.
The physical front and front-side radars remain separate Bus-1 nodes.

### 45.3 Current bounded architecture

```mermaid
flowchart LR
  IMG["FRC image-processing MCU"] --> STATE["internal object / lane state"]
  RAD["front + side radar"] --> B1["Toyota Bus 1<br/>plaintext perception + plant feedback"]
  B1 --> STATE
  STATE --> MAIN["FRC main MCU<br/>LDA/LTA/PDA feature requests"]
  MAIN --> REQ["generic request 5282"]

  REQ --> A["Model A<br/>FRC selects 5285 / 57DE"]
  A --> TX["Brake / Skid / CGW<br/>signing or physical-Tx boundary"]

  REQ --> B["Model B<br/>Brake / Skid selects winner<br/>and signs"]
  B --> TX

  TX --> O8["Bus-4 0x08A<br/>secured request publication<br/>not F33 ingress"]
  TX -. "separate cooperative-control contract" .-> B6["protected B6<br/>known EPS external ingress"]

  CHASSIS["Brake / EPS chassis state"] --> FB["recorder result / status observations<br/>5285 / 57DE / 5265 / 560D"]
  FB --> MAIN
```

The diagram is deliberately two-model. Exact F33/B6 evidence makes Brake the
only positively attributed immediate protected-command source domain, while
the `0x08A` physical transmitter, final arbitration executor, and downstream
TSK proxy's CMAC/freshness ownership remain unidentified. FRC-side TSK
pre-authentication is not a live branch. `0x08A` must not be drawn as an EPS
input or as an established `0x08A -> B6` transform. The
retained ID11 intervals are request state without a verified `5285/57DE/5265`
winner/grant and contain zero B6.

The decisive dynamic discriminator is one synchronized FRC Operation-FFD +
all-bus capture comparing `5531/5631`, `5282`, `5285/57DE`, `0x08A`, and
`5265/560D`.
If the result settles before the Bus-4 publication, FRC-local arbitration
strengthens; if request leads the Bus-4 publication and result returns later,
external Brake/Skid arbitration strengthens. The decisive static discriminator
remains matched category-435 Brake firmware plus the exact `0x792` FRC image.

Deterministic guards:
`tests/verify_gtsplus_p5_adas_p6_migration.py`,
`tests/verify_gtsplus_pcs_data_viewer_tss3_managed_semantics.py`,
`tests/verify_camry_2026_bus1_camera_output.py`, and
`tests/verify_camry_2026_08a_producer_bounds.py`.

## 46. Exhaustive lateral flow trace: bounded carrier negative on the reached Bus-4 segment (VAR-098/099/100, CORR-138/139)

A five-stage multi-pass sweep over both retained drives (request/state, value echo,
boundary-conditioned flips, full census + anomalies, B6-signature, bus-1 domain),
adversarially verified and closed on 2026-08-29, pins the whole lateral flow
artifact-side. Everything below regenerates byte-identically from the retained
drives via `tools/analyze_camry_2026_lateral_flow_trace.py` and is asserted by
`tests/verify_camry_2026_lateral_flow_trace.py`.

### 46.1 Absence result: no separate stock-LTA actuation/grant carrier identified (VAR-099/CORR-139)

`0x351/0x394/0x4A3/0x4C8` (the exact-F33 configured telemetry Tx PDUs) are **zero
frames in every retained capture** — both drives, both parked censuses, oracle
runs, diagnostic logs — on every bus and DLC, while `0x030` (10.0–10.5 ms,
DLC 32) and `0x081` stream throughout as controls. `0x0B6`, legacy `0x131`, and
legacy `0x2E4` stay zero. A +0.5..+5.0 s post-onset sweep across all sixteen
DLC-32 bus-0 streams finds zero >=95%-persistent byte flips at either clean ID11
onset, and the boundary census identifies only request-side mirrors.

This identifies no separate stock-LTA actuation/grant CAN carrier within the
declared search. It does **not** prove that the reached network is an incomplete
EPS interface or an EBU-private stub. Section 19 / VAR-066 already joins GTS+
topology, exact-F33 one-controller routing, UDS, and the physical repin: the
reached `CAN0/CAN2` relay pair is Toyota Bus 4's Brake/EPS segment, and B6 belongs
on it. The missing configured telemetry IDs are therefore presence/schedule
observations, not a routing discriminator. Exact F33's B6-inactive internal path
into motor-current control also explains why stock LTA need not publish B6.

**Routing decision:** keep the current repin. For openpilot's candidate external
cooperative-control ingress, the physical route remains `0x0B6` DLC 32 on Panda
bus 0 across the current `CAN0/CAN2` relay pair. Receiver authentication is not an
unknown prerequisite for development: VAR-060 already provides the exact-F33
Gate-2 compare-neutralization and deterministic CRC repair, so a patched/bridged
EPS can accept the fork's deliberately zero-MAC28 B6 frames. The unfinished work
is deploying and arming that bypass, completing and enabling the fork sender and
Panda safety path, validating source suppression/relay behavior, and exercising a
bounded live response — not discovering another EPS CAN pair or recovering the
slot-4 key. Production output remains unauthorized.

### 46.2 `0x081` is a second Bus-4 carrier of the steering-reference word (VAR-098)

Nearest-time pairing puts `0x081` B16:B17 (s16BE) equal to `0x08A` B18:B19 in
89.36/83.67% of static-word pairs (duplicate-word equality <=0.20%), and batch
medians agree within +/-1 count in 92.06% of drive-B ID11 batches. Drive A's fast
slew drops batch agreement to 50.68%, and moving-frame strata disagree enough to
reject blanket byte equality. In the manual state the same `0x081` word has a
near-unity fit to measured `0x025` coarse angle times the exact F33 B6 scale:
implied 0.057346/0.057321 deg/count vs 0.0573027, r=0.998737/0.999911. Together
these observations strongly support one mode-switching steering-reference
quantity — measured angle without a request, request-tracking under LTA —
republished at ~32 Hz beside EPS. They do not prove a winner, grant, or actuation
command. Producer identity stays open (OQ-054); F33's Rx set excludes `0x081`
(`0x081` mirrors are display/state plane).

### 46.3 `0x08A` is byte-complete (VAR-098)

Constants B0/B1/B2/B5/B15/B25/B27=0x00, B13/B16=0x7F, B14/B17=0xFF; B6[0]/B7[0]/
B20[7] mirror the B3[3] cruise latch; B22[4]/B4[7] assert in every ID11 frame;
B23[5] differs by drive (0.582/0.100 of ID11 frames). B26[5:0] is overwhelmingly
`+1 mod 64` across chronological frames; drive A contains 175 non-`+1` breaks and
drive B contains 0. Batched capture ordering does not classify those breaks as
sender resets versus omitted/interleaved publications. This supports a
message-freshness role, not an LTA-state field, beside the B28:B31 `FV4|MAC28`
trailer. B24 is the only byte with the recorder assist `{0,50,100}` alphabet; no
other `0x08A` byte carries that same alphabet. The bounded conclusion is that no
separate damping-gain field was identified on `0x08A`, not that no differently
encoded or off-PDU carrier can exist.

### 46.4 SDG is a steering request; the plant shows request-associated response (VAR-100)

SDG (B21=18) intervals publish nonzero dynamic steering targets tracking SAS
(A: r=0.816961/0.908715; B long interval: r=0.754389; blips carry 12–20-count
trims). Inside ID11 the request word leads measured angle (A plateau r≈0.868,
best +50 ms, plant gain 1.248945 mrad/mrad; B small-signal, first-30 s r=0.561663
collapsing to 0.139101), and the EPS motor proxy follows the reference word at
least as well as SAS (A 0.587897 vs 0.456945; B 0.591181 vs 0.126883). These are
request-associated plant correlations, not causal command-path or winner/grant
oracles (CORR-137).

### 46.5 Session-internal refutations retained

`0x19C`'s apparent "LTA cadence flip" is phase dilution: the stream idles at 10 Hz
and runs ~20 Hz inside drive phases A 263.9–503.9 s / B 1104.7–1494.7 s, and ID11
lies wholly inside the fast phase in both drives. The drive-A bus-1 "5.3% rate
deficit" is capture-side frame deletion (wire cadence unchanged). A first-round
"camera angle estimate" reading of `0x160[22]` was refuted by the same window
logic as CORR-138.

### 46.6 Untestable on retained data

PCS `57A3`, LDA `5531`, and PDA `5A09/5A0A/5A0D` recorder shadows (states never
exercised), the `1B40_3` EPS-copy shadow (every EPS telemetry PDU absent), the B6
SecOC key (OQ-054), and damping gain (recorder layouts and B6 sig269/270 only).
The decisive live ownership discriminator remains the synchronized FRC
Operation-FFD capture (`REFERENCE/CAMRY_TSS3_OPERATION_FFD_PLAN.md`); it is no
longer a physical-routing oracle.

## 47. The 0x08A signer is always-on: the secured family signs at zero lateral request (VAR-101)

### 47.1 Observed result

The retained 2026-08-26 stationary NRTD→READY capture — pre-repin, so the
aggregated development plane carries the secured chassis family alongside the
camera plane — holds **2,475 `0x08A` DLC-32 frames with `B21` (Target Lateral
ID) equal to 0 (No Request) in every single frame**. The vehicle is stationary
throughout; there is no lane-centering request, no LTA, no cooperative control.
Yet the secured envelope runs exactly as in the active drives:

- FV4 reset-low2 tracks the live `0x00F` epoch (2,444/2,475 = 98.75%; the
  `0x00F` reset counter visibly advances through the capture, span 5212→9807);
- B26 advances `+1 mod 64` at 99.96%;
- all 16 FV4 phases cycle evenly;
- MAC28 is frame-unique (last-4 unique fraction 1.0).

`0x0D7` shows the same always-on signing pattern in the same capture. The
relay-correct drives supply the active-request contrast — B26 `+1` at
0.9915/1.0000 and last-4 unique 1.0 across B21 0/11/18 regimes — so the
signer's structural cadence is **regime-independent**.

### 47.2 Interpretation and boundary

The recovered TSK hardware boundary independently excludes the front camera
from the SecOC key-holder/signing role: the FRC is the request producer, while a
downstream ICU-S-equipped participant must own the protected chassis publication.
The zero-request capture then adds an orthogonal dynamic result: that downstream
publisher is **always-on**, maintaining authenticated `0x08A` cadence even while
FRC Target Lateral ID is 0. OQ-054 therefore narrows from "who signs" to "which
always-on Bus-4 node holds the slot-class key": the brake family (ABS 435 /
Brake Booster 466) or the Central Gateway (VAR-096's install-set bound). Current GTS+ ADCU_P6 vocabulary names the OEM request/arbitrate/sign
pattern explicitly (`Lateral Arbitration ID`, `Lateral Control ID of Arbitrated
Result`); that is architecture corroboration only —
P6 names are not transferred onto this gen-20 P5 car.

The observed continuity does not identify the signer. The decisive evidence
remains exact producer firmware: decode the brake-family Tx descriptors and
SecOC generation profile (search order tracked in
`data/generated/gtsplus_2026/camry_f152633k0000_brake_acquisition.json`;
acquisition route TMS-049/050). A `0x08A` Tx descriptor plus SecOC generation
in `F152633K0000` or Skid Control firmware closes OQ-054 deterministically.

Signer identity is **hypothesis**; zero-request signing continuity is
**observed**. No output authorized.

Canonical evidence: `data/generated/camry_2026_08a_signer_continuity.json`;
`tests/verify_camry_2026_08a_signer_continuity.py`.
### 2026-08-30 — F33 dev-lateral relay/forwarding correction

Live READY testing of the exact-F33 development lateral path initially produced FRC communication-loss DTCs U014087, U010187, U029387, U010087, U110687, U012987, and U015587 when Panda entered Toyota safety param 4096 with the harness intercept relay open and software bus0<->bus2 forwarding active. The failures were reproducible after a clean FRC DTC clear; several returned with current TEST_FAILED + WARNING_INDICATOR_REQUESTED status.

The first successful workaround was relay-closed/no-software-forwarding (`panda@927d3e78`, `opendbc@886b32a9`): after a clear and 15 s in dev mode, the FRC retained zero fault-status records. **That workaround is superseded and is not the final topology.** Analysis of the failing relay-open rlogs proved the forwarded frames were genuinely transmitted with byte-identical payloads and zero CAN-controller overflow/bus-off/error counts, which forced the failure below the payload/whitelist layer.

The forwarding failure is frame-format-sensitive, with a concrete latent mechanism in clean upstream Panda/openpilot. Pandad enables `canfd_auto` on every bus; Panda RX records each frame's FDF bit and the software forwarder copies it, but the FDCAN TX path ignores that per-frame FDF while auto mode is active and instead uses sticky bus-global CAN-FD/BRS state. The retained openpilot rlogs do not carry per-frame FDF/BRS metadata, so they cannot directly prove that a particular Toyota classic frame was promoted to CAN-FD or isolate FDF from BRS as the attribute that triggered the FRC faults. The live A/B is narrower and sufficient for integration: relay-close removed the communication faults, and `panda@dad7ae23` preserving the original RX FDF/BRS format for forwarded packets allowed relay-open forwarding without the prior malfunction. `panda@99b6f09c` restores the normal comma relay-open topology, with `opendbc@11a0c049` / parent `kai-openpilot@9af322518` restoring software forwarding. With the car in READY after those commits, relay-open forwarding runs both directions with zero bus-off, zero CAN errors, zero TX loss, and zero RX loss; the operator restarted comma again and the prior dash/FRC malfunction did not return.

The relay-open rlogs also resolve an integration-routing bug that was invisible with the relay closed. On route `00000029--bae47e927f`, `0x08A/32` has **21,636 native bus-2 RX frames**, only **439 startup bus-0 RX frames**, and **21,196 bus-0 returned TX echoes (`src=128`)**. Thus after interception is active, `0x08A` must be consumed from native Panda bus 2; its forwarded bus-0 copy is not a bus-0 RX event available to `CarState` or Panda's RX safety hook. The same route contains 3,592 native `0x08A` frames with cruise operating and stock lateral ID0, plus 76 with cruise operating and ID11. Replaying the route through the corrected `CarState` yields 8,943 update cycles with `cruiseState.enabled=true` while stock lateral ID is 0 and 189 while it is 11. Historical `opendbc@7a0f9fd5` therefore moved Camry `0x08A` observation and the then-development Panda cruise/stock-lateral interlock to bus 2; parent `kai-openpilot@13ca9285c` carried that fix. CORR-147/CORR-148 later remove the interlock as non-native policy; the durable result here is the native bus-2 origin. The focused Camry TSS3 suite passed 31/31.

**Current rule:** exact-F33 development uses normal comma topology — physical relay open, native-format software forwarding, B6 injection on bus 0, and native camera-side `0x08A` observation on bus 2. Do not restore the relay-closed workaround and do not parse the forwarded `0x08A` TX echo as bus-0 state.

## 48. B6-vs-internal steering arbitration: no receiver-side exclusion, no blockable stock-LTA carrier (VAR-104)

Session question: can stock lateral remain active while an external B6 command is
accepted, does `0x08A` ID11 carry actual authority, and is there an exact-F33-accepted
CAN frame whose Panda-forwarding suppression could disable the stock
B6-independent internal path? Every claim below is a direct read of the exact
`8965F3307000` canonical corpus (VA = file offset; image `42dce8ef…d9b0e7`),
extending §29/§30 rather than transferring from H/F.

### 48.1 The shared funnel has exactly one external authority ingress, and stock passes it by

- `FUN_000D039E` composes `FEBECC50 = clamp(base×CB9C8()/0x100 + (FEBEC797==0 ? CB9AE()×FEBEC81A/0x100 : 0), ±B1334)`, with `FEBEAC28` selecting base `FEBECC60` (the `D0218` path) or `FEBECC5A`.
- Guarded-factor fallbacks pin the stock state: `FUN_000CB9C8` falls back to ROM `0xB04C4 = 0x100` (base ×1.0) and `FUN_000CB9AE` to `0xB04D4 = 0` (addend ×0), so with B6 absent `CC50 = CC60` exactly. `FUN_000CB82C` holds the base-scale target at `0x100` in **both** `C7BF` states (`0xB04C2 == 0xB04C4 == 0x100`); only the addend factor `FEBEC7BC` targets `0 ↔ 0x100`. The base is never scaled away — native power assist survives any B6 state.
- The addend payload `FEBEC81A` (`FUN_000CBF9E`) is composed from measured angle-rate `FEBEC172`, a ROM-gain damping product, and cone integrators — not a raw B6 angle pass-through; `FUN_000CBC80/CBCB8` derive their request from Δ(`FEBEAC88`) and a speed class.

### 48.2 The only displacement machine is a self-terminating transient, not LTA/LCA

`FUN_000CB73A` raises `FEBEC7BF` only with `C7B4 && !C7BE && C795 && !C7B3 && ADB0 == 0x31 && AE02 < ROM[bank]` after a 300-tick (`0xB04C0 = 0x12C`) qualification. The decompiler literal `'1'` is **0x31, not numeric 1**: `FUN_000CEFFC`'s bank cases for the same snapshot cell are exactly `0x01/0x04/0x0A/0x0B/0x12/0x13`, so the arming value lies outside the documented Target Lateral ID alphabet. The hold path requires `ADB0 == 0x31` continuously, and `FUN_000CB396` latches `FEBEC797` after ≥5 ticks (`0xB04B6 = 5`, magnitude gate `0xB04B4 = 0x280`), which removes the addend in `D039E` and lets `FUN_000CB664` clear `C7B4` — the machine self-terminates. When it does run, `D0218` collapses to `C4C0 + BF3C` (verified), dropping the driver-torque and return/dither terms: a bounded cooperative pulse profile, not a sustained steering authority. Any future B6 sender must not assume dictionary IDs arm this path.

### 48.3 Verdicts and the remaining open state

- **B6 with ID11 co-modulates the ordinary branch**: `CEFFC` banks (`CB00=2`) re-index the `CD094`/`CDFF8` tables whose outputs `CA7A/CA88` feed the supervisor family (`CC9AC/CE144/CE26E`) that drives the `CF2B2` ramp of `CB38` from `CB08/CB20`. No receiver-side exclusion between external B6 and the internal authority state is recovered; the `CA7A/CA88 → CB08` edge is statement-unclosed and the stock authority selector remains the CORR-135 open question. This bounds coexistence as an unresolved receiver behavior; it does not identify a separate openpilot authority signal.
- **`0x08A` ID11 stays request-plane only** (F33's 43-Rx/47-rule/5-Tx surfaces exclude it; grant discriminator remains Operation-FFD `5265`, VAR-095/OQ-054). It therefore must not be promoted into a Panda or `CarController` lateral-permission/interlock signal.
- **No Panda-forwarding suppression frame can be justified.** F33's accepted surface contains no stock-LTA carrier; `0x08A`/`0x081` are not accepted by F33, and suppressing them would only destroy `CarState` inputs and OQ-054 producer evidence; the stock request crosses the private middle (VAR-094). The native openpilot integration therefore keeps authority in the normal stack (`controls_allowed`/`CC.latActive`) rather than inventing a request-plane engage veto. Passive DID readback (`0x1C02/0x1C38/0x1C3E`) remains useful for observing arbitration behavior without becoming an engagement gate.

Deterministic evidence: `tests/verify_camry_8965F3307000_command_cone_ingress.py` (VAR-104 corpus-join block) against
`data/generated/camry-8965F3307000/decompilations.jsonl` and `firmware/camry-8965F3307000/CodeFlash.bin`.
No output authorized.


## 49. Final native openpilot port boundary and route-2A disposition (VAR-105 / CORR-148)

The final integration audit deliberately separates **Toyota/F33 protocol facts** from
**openpilot control policy**. Target-specific decoding, B6 construction, the exact
angle scale/range, fixed bus topology, and the zero-MAC28 trailer required by the
already-installed Gate-2 patch remain platform code. Bring-up-only policy and
instrumentation do not.

The normal driving path is now:

`controlsd -> CC.latActive -> Toyota CarController -> standard angle shaping -> F33 B6 -> ordinary Toyota Panda safety -> EPS`.

There are no private F33 arming Params, runtime FRC diagnostic oracle, fake
`secOcKeyAvailable`, separate `ALLOW_DEBUG` steering mode, Python shadow safety,
dynamic harness selection, controller-side `0x08A` authority veto, custom Panda
B6 sequence-gap/35-ms/`0x00F` admission policy, or raw steering-rate veto. Panda
uses the normal Toyota safety model, a B6-only transmit whitelist, normal
`controls_allowed`, measured angle, and shared `steer_angle_cmd_checks()`. The
request-plane `0x08A` state remains an observed Toyota state and is not promoted
to an EPS grant or forwarding-block signal (VAR-104).

### 49.1 Route `0000002a--c5647fd694` explains the old zero-steering result

The complete copied route contains **13,410 active B6 send attempts**. Panda
returned **8,051** as transmitted and rejected **5,359** under the superseded
custom safety policy. Every active old command used Target Lateral ID 11 and
100/100 contribution fields but B6 byte6=`0x04`. Exact-F33 signal265 is that bit;
its mode2 consumer proves value 1 suppresses one target-derived contribution.
Thus the road-test failure is consistent with two already-removed implementation
errors: an active command shape that explicitly suppressed a contribution and a
custom Panda admission policy that discarded about 40% of active attempts. It is
not evidence for restoring those policies or inventing another receiver gate.

The cleaned sender uses active ID11 with signal265=0 and 100/100 contributions.
Inactive output uses ID0 with inert companions. Application sequence/freshness
remain protocol-construction state in the sender; they are not duplicated as
Panda control policy.

### 49.2 Standard semantics are mapped only where the target closes them

The port exposes the target's physical steering angle/rate and driver torque.
The first-class F33 evidence explicitly leaves the **driver-override numeric
threshold** unresolved (the ~8.238 N.m figure is representation saturation, not
an override threshold), so `steeringPressed` is not synthesized from a guessed
number. Likewise, the exact fault/status work does not close openpilot
`steerFaultTemporary` versus `steerFaultPermanent`; those policy fields remain
neutral until live asserted/recovery dynamics establish the mapping.

Cruise engagement follows normal Toyota `pcmCruise` semantics using the recovered
Camry operating state. Physical MAIN/RES+/SET-/CANCEL are exposed as standard
read-only button events. Door, belt, brake/hold, parking brake, blinkers, BSM,
traction-control state, generic high-beam toggle, gear/Ready, speed and cruise set
speed flow through ordinary `CarState` fields. No TSS3 HUD sender or legacy Toyota
ACC/LKA frame is fabricated without a target contract.

### 49.3 Supported output versus bounded unsupported features

Lateral output is supported on the **exact maintainer Camry with the persistent
Gate-2 patch already installed and reboot-verified**. This support does not claim
a recovered SecOC key and does not generalize to unpatched F33 EPS software or
other TSS3 platforms. The Corolla TSS3 target remains read-only.

System-generated stock-ACC cancel is now recovered through the ordinary brake-status
carrier rather than by spoofing the protected/rolling physical switch carrier. In
route `0000002c--c784367b7e`, two brake presses while cruise remained engaged begin
at 228.156866 s and 245.843896 s. The native bus-0 `0x101/8` Brake Module frame
changes only B0 bit3 at the initiating edge (`80 -> 88`) plus the ordinary Toyota
checksum; the first native bus-2 `0x08A` frame with `CRUISE_OPERATING_LATCH=0`
follows **70.229 ms** and **82.528 ms** later respectively. Native `0x101` is
forwarded bus0->bus2, while native `0x08A` is produced on bus2, so the replacement
cancel is injected on bus2. Across the complete copied route, all **30,044/30,044**
native bus-0 `0x101` frames satisfy the ordinary Toyota checksum; B0 is exactly
`0x80/0x88`, B2/B4/B5/B6 are always zero, while B1/B3 are live fields and must be
preserved rather than guessed. Current GTS+ independently exposes Hybrid Control
category 397 DID `0x1043` bit14 as **Brake Cancel Switch** (OFF/ON), corroborating
the brake-cancel semantic boundary without proving the DID is sourced uniquely
from `0x101`.

The openpilot implementation therefore clones the live `0x101` fields, asserts
only `BRAKE_PRESSED`, recomputes the Toyota checksum, and transmits the result on
Panda bus2 when the normal `CC.cruiseControl.cancel` contract requests a stock-ACC
cancel. Panda admits only the observed 8-byte stock shape with the brake bit set
and a valid checksum. `0x0FE`, `0x0C9`, and `0x0CA` remain unsent by this path.

The preferred RAM-only/reset-to-stock signer architecture is also future research
for eliminating the persistent development patch. It is not part of the current
openpilot runtime and must not reintroduce private Params/oracles or alternative
safety authority.

## 50. Longitudinal cross-plane join: `0x0CA` is already protected; Bus-1 `0x160 B12` is a pre-protection candidate (VAR-106)

The retained relay-correct drives now give the first concrete target-native bridge
between Toyota's plaintext camera/radar network and the protected longitudinal
chassis plane. The result is useful precisely because it corrects the tempting
interpretation of `0x0CA`: **`0x0CA` itself is not the unsigned FRC→signer
request. It is already downstream-looking protected traffic.** The interesting
upstream lead is a field on native Bus 1.

### 50.1 `0x0CA/32` has the ordinary Toyota-P5 protected envelope

`0x0CA/32` is present on Panda bus 0 and its bus-2 relay mirror and absent from
native bus 1 (drive A 21,879 / 21,880 / 0; drive B 25,475 / 25,475 / 0). Its
application byte B2 advances `+1` in 21,729 drive-A and 25,465 drive-B
same-segment pairs. Applying the same bounded P5 trailer geometry used for
`0x08A` gives:

- B27 is always zero and B28[7:4] visits all 16 FV4 values;
- B28[5:4] matches the preceding authenticated `0x00F` reset-low2 on
  **85.5706385% / 85.8903894%** of eligible A/B frames;
- whenever B2 advances and the candidate reset-low2 stays constant, candidate
  B28[7:6] message-low2 advances `+1 mod 4` in **20,026/20,026** A and
  **23,465/23,465** B pairs;
- the candidate MAC28 in B28[3:0]|B29|B30|B31 is nearly frame-unique:
  **21,878/21,879** A and **25,473/25,475** B.

That is a strong ordinary-P5 `FV4 || MAC28` structural match. It does not recover
the key/profile/CMAC inputs, but it is enough to reject using `0x0CA` as evidence
for an unsigned pre-sign PDU.

### 50.2 The application words look like longitudinal upper/lower/result arbitration

During the stock-cruise latch, signed big-endian words B3:B4, B5:B6, and B7:B8
all occupy physically plausible acceleration ranges at **0.001 m/s²/count**.
B7:B8 lies between B5:B6 and B3:B4 in **1,906/1,947 = 97.8941962%** of
drive-A cruise frames and **4,537/4,804 = 94.4421316%** of drive-B cruise
frames. The misses remain close to a bound (maximum observed under-run 0.007
m/s² A and 0.017 m/s² B).

B7:B8 is also the measured-acceleration-like member of the triplet. Against the
existing exact `0x0AA` wheel-speed decode and a 1.0-s centered derivative, its
best stock-cruise correlation is **r=0.519733 at +0.6 s** in drive A and
**r=0.785714 at +0.3 s** in drive B. These are correlation shifts only; the
rlog publication timestamps remain unsuitable for a precise causal-latency
claim.

The shape is independently consistent with current GTS+ vocabulary:

- Brake `0x10A1` = **Request Acceleration of Upper Limit from Toyota Safety Sense**,
  signed16 ×0.001 m/s²;
- Brake `0x10A2` = the corresponding **Lower Limit**;
- FRC-hosted PCS recorder `57DB` = **Arbitration result Acceleration**, signed16
  ×0.001 m/s²;
- FRC recorder `5280/5281` separately carries lower/upper request IDs,
  accelerations, force allocation, shift priority, EPB/override/priority state.

This supports an **upper/lower/result-like** interpretation of the three `0x0CA`
words. It still does not assign `10A1`, `10A2`, and `57DB` byte-for-byte until a
synchronized diagnostic/Operation-FFD capture overlays the values directly.

### 50.3 Native Bus-1 `0x160 B12` is the first serious pre-protection candidate

`0x160/32` is the inverse placement: it appears only on native Panda bus 1
(**20,510 / 23,998** A/B frames), has a B2 rolling counter, and its last four
bytes are exactly `00 00 00 00` in every retained frame. It therefore does not
carry the ordinary P5 trailing SecOC envelope seen on `0x0CA`.

During stock cruise, B12 is confined to raw `0..127`; interpreting it as signed
7-bit two's complement and nearest-time joining it (≤30 ms) to protected
`0x0CA B7:B8` produces a very strong and reproducible relation:

- drive A: **n=1,834, r=-0.951664**, `B7:B8[m/s²] ≈ -0.097299*s7 + 0.092474`;
- drive B: **n=4,526, r=-0.989396**, `B7:B8[m/s²] ≈ -0.118673*s7 + 0.179956`.

The relation remains strong after excluding samples within 0.05 m/s² of the
candidate upper/lower arbitration bounds: A **n=1,218, r=-0.911523**, slope
`-0.099274`; B **n=3,826, r=-0.986808**, slope `-0.119391`.

This is substantially stronger than generic same-drive correlation and makes
`0x160 B12` a **high-value plaintext/non-SecOC cross-plane candidate upstream of
protected longitudinal arbitration**. The evidence does **not** yet prove that
FRC transmits `0x160`, that B12 is the Toyota request acceleration, or even the
direction of the relation. `0x160` remains only source-bounded to the native
camera/radar domain; feedback/perception or another correlated arbitration input
remain live alternatives.

### 50.4 What this means for an OEM-signer interception architecture

The desired architecture is now plausible for longitudinal control but not yet
closed:

`openpilot request -> replace OEM pre-protection request -> stock brake/gateway arbitration + signer -> protected chassis output`.

If the candidate is source-attributed and the diagnostic join proves that it is
the FRC request, this would let Comma reuse Toyota's own trust boundary rather
than implement/store the SecOC/TSK signing material itself. That is **not** a
cryptographic bypass; it is an upstream request-plane replacement that leaves the
OEM protected output path intact.

Two target-native constraints remain before any such implementation:

1. current Toyota-B topology gives CAN0/CAN2 the intercept-relay pair while
   CAN1 is **unsplit**. The present harness can observe/inject native Bus 1 but
   cannot selectively remove an FRC-produced `0x160`; source replacement needs
   an inline Bus-1 interception point or discovery of a later transformed handoff
   on the already intercepted gateway/brake plane;
2. the longitudinal result does not solve lateral. VAR-104/105 still prove there
   is no justifiable Panda-forwarding stock-LTA block on the current F33 path;
   `0x08A` is request-plane and not accepted by F33, and the stock LTA authority
   selection remains inside the unresolved private middle/B6-independent path.

The decisive next step is already read-only and implemented:
`tools/camry_tss3_request_capture.py` should be run during stock DRCC while
capturing all buses. Join FRC `0x792` DIDs `1B03..1B07`, Brake `0x7B0` DIDs
`10A1..10A4`, native Bus-1 `0x160`, and protected `0x0CA`; preserve a PCS
Operation-FFD/VDAS specimen if available. Exact overlays of `10A1/10A2` onto the
`0x0CA` triplet and an FRC request quantity onto `0x160 B12` would materially
close request source, transform direction, and the location of the signing
boundary.

Deterministic evidence:
`tools/analyze_camry_2026_longitudinal_request_plane.py`,
`data/generated/camry_2026_longitudinal_request_plane.json`, and
`tests/verify_camry_2026_longitudinal_request_plane.py`. No control output is
authorized by this finding.

## 51. Native Bus-1 framing is exact AUTOSAR E2E Profile 5, not cryptographic authentication (VAR-107)

The retained Bus-1 corpus now closes the request-plane E2E format exactly. The
native camera/radar family uses **AUTOSAR E2E Profile 5**: B0:B1 is a
little-endian CRC-16/CCITT word, B2 is the 8-bit alive counter, and the implicit
16-bit Data ID equals the CAN identifier. The protected bytes are B2..end in
wire order, followed in the CRC calculation by `CAN_ID_low, CAN_ID_high`.
Across both retained drives the exact generator matches **438,380/438,380**
periodic Bus-1 frames across all 22 stream IDs with zero mismatches. No
cryptographic authenticator is present on this interface.

### 51.1 B0:B1 is exact AUTOSAR E2E Profile 5

For every one of the **22 periodic Bus-1 streams** in both retained drives,
identical bytes B2..end always imply identical B0:B1; there are zero suffixes
with two different integrity words. More strongly, treating B2..end as a GF(2)
input vector and B0:B1 as a 16-bit output yields **zero affine conflicts** on
every periodic stream.

`0x160/32` gives the strongest high-rank witness. Across both drives it contains
**44,508 frames** and spans an observed input-difference rank of **111** with
zero conflicts. Training the affine model on every fifth frame gives rank 110;
it covers **35,605/35,606** held-out frames and predicts **35,605/35,605** of
the covered integrity words exactly. This is not the behavior of a
cryptographic MAC over the visible PDU.

The transform is also common across PDUs rather than a per-ID opaque tag:

- equal-DLC `0x160`, `0x440`, and `0x450` have the **same eight B2-bit -> B0:B1
  XOR contributions**;
- for 64-byte frames with an identical B2..end suffix, changing CAN ID
  `0x184 -> 0x185` changes B0:B1 by fixed XOR `0x3133` on all 257 overlaps;
  `0x18A -> 0x18B` produces the same `0x3133` on all 256 overlaps.

The exact generator is:

`CRC = CRC16_CCITT(init=0xFFFF, B2..end || CAN_ID_low || CAN_ID_high)`

with polynomial **`0x1021`** (`x^16 + x^12 + x^5 + 1`), non-reflected input and
output, no final XOR, and the resulting 16-bit CRC stored **little-endian** in
B0:B1. The E2E header offset is zero, so B2 is exactly Profile-5's one-byte
counter. This is byte-for-byte the AUTOSAR Profile-5 computation rather than a
Toyota-specific opaque checksum.

The recovery is independently visible from the learned syndromes: after
byte-swapping B0:B1 into the CRC register value, adjacent bit contributions
follow the `0x1021` recurrence exactly, and the B2->B12 bit-0 contributions are
separated by precisely 80 CRC shifts. The fixed CAN-ID term also closes: every
same-suffix `0x18x` cross-ID pair matches the CRC effect of appending the 16-bit
CAN ID low byte then high byte. There is no secret input.

### 51.2 `0x160 B2` is the visible alive/freshness counter

On drive B, B2 advances **+1 modulo 256 on all 23,988 same-segment consecutive
`0x160` pairs**. Drive A is +1 on **20,351/20,501 = 99.2683284%**; every retained
non-+1 example is accompanied by a capture gap of multiple nominal cycles (for
example +90 across 2.236 s and +26 across 0.655 s), consistent with missed
logging rather than sender rollback. Median observed `0x160` spacing is about
22.8-22.9 ms.

This provides a straightforward freshness/alive marker, but sender traces alone
do **not** recover the downstream receiver's accepted counter window, timeout,
or restart policy.

The wrap boundary is visible directly on constant `0x020/12`. Its body is zero
apart from the Profile-5 B2 counter, a B3 application byte that mirrors B2 in
this stream, and the B0:B1 CRC word. Across each drive it
has exactly **256 complete wire images**; the counter->integrity mapping passes
all **65,536/65,536** affine pair identities with zero violations, and the same
complete frame repeats byte-for-byte after the 8-bit counter wraps. Median exact
recurrence is **12.802331357 s / 12.802446447 s** in drives A/B. Therefore there
is no observed long-lived epoch or nonce on this Bus-1 framing. A receiver may
reject an immediate replay from local counter state, but the wire image itself
contains nothing beyond the modulo-256 state to distinguish a post-wrap replay.

### 51.3 Exact Profile-5 generation replaces the learned `0x160 B12` delta patch

The earlier affine recovery already solved the B12 and B2 checksum deltas:
B12 bits 0..6 contributed
`D86D/B0DB/41A7/A35E/46BD/AD6A/5AD5`, while B2 bits 0..7 contributed
`4659/8CB2/3975/72EA/C5C4/AB99/7723/EE46` in transmitted B0:B1 order. Those
values remain useful regression witnesses, but they are now derived consequences
of the recovered Profile-5 generator rather than the implementation method.

`tools/camry_frc_request_poc.py` now recomputes the **full exact Profile-5 CRC**
instead of applying a B2/B12-specific delta table. It takes an observed 32-byte
`0x160`, verifies its existing CRC using Data ID `0x0160`, sets the signed-7 B12
candidate, preserves the intercepted B2 by default (or explicitly advances/sets
it for next-frame synthesis), and recomputes B0:B1 from the entire PDU. The
retained same-payload oracle still reconstructs **23,083** frame pairs including
81 B12-changing pairs with **0 mismatches**, while the exact generator also
validates every retained periodic Bus-1 frame. The CLI contains no CAN transmit
path; source attribution, B12 OEM identity, receiver `MaxDeltaCounter`/timeout
behavior, and downstream acceptance remain separate live questions.

This is an **analysis result**, not yet a vehicle-control contract. VAR-106 still
leaves `0x160` physical transmitter/direction and B12 OEM identity open, and no
live experiment has shown how the downstream ECU reacts to a synthetically
modified request. The important security conclusion is narrower: the native Bus-1 family exposes
**standard AUTOSAR Profile-5 CRC integrity + rolling freshness, not the ordinary
Toyota P5 SecOC/TSK authentication boundary** seen on Bus 4.

Deterministic evidence:
`tools/analyze_camry_2026_bus1_e2e.py`,
`data/generated/camry_2026_bus1_e2e.json`, and
`tests/verify_camry_2026_bus1_e2e.py`; implementation witness:
`tools/camry_frc_request_poc.py` / `tests/verify_camry_frc_request_poc.py`. No
control output is authorized by this finding.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [SECOC-075](../reference/index.md#finding-secoc-075), [SECOC-076](../reference/index.md#finding-secoc-076), [SECOC-077](../reference/index.md#finding-secoc-077), [SECOC-078](../reference/index.md#finding-secoc-078), [SECOC-079](../reference/index.md#finding-secoc-079), [SECOC-080](../reference/index.md#finding-secoc-080), [SECOC-081](../reference/index.md#finding-secoc-081), [SECOC-082](../reference/index.md#finding-secoc-082), [SECOC-083](../reference/index.md#finding-secoc-083), [TMS-060](../reference/index.md#finding-tms-060), [VAR-051](../reference/index.md#finding-var-051), [VAR-052](../reference/index.md#finding-var-052), [VAR-053](../reference/index.md#finding-var-053), [VAR-054](../reference/index.md#finding-var-054), [VAR-055](../reference/index.md#finding-var-055), [VAR-056](../reference/index.md#finding-var-056), [VAR-057](../reference/index.md#finding-var-057), [VAR-060](../reference/index.md#finding-var-060), [VAR-061](../reference/index.md#finding-var-061), [VAR-063](../reference/index.md#finding-var-063), [VAR-064](../reference/index.md#finding-var-064), [VAR-065](../reference/index.md#finding-var-065), [VAR-066](../reference/index.md#finding-var-066), [VAR-067](../reference/index.md#finding-var-067), [VAR-068](../reference/index.md#finding-var-068), [VAR-069](../reference/index.md#finding-var-069), [VAR-070](../reference/index.md#finding-var-070), [VAR-072](../reference/index.md#finding-var-072), [VAR-073](../reference/index.md#finding-var-073), [VAR-074](../reference/index.md#finding-var-074), [VAR-075](../reference/index.md#finding-var-075), [VAR-076](../reference/index.md#finding-var-076), [VAR-077](../reference/index.md#finding-var-077), [VAR-078](../reference/index.md#finding-var-078), [VAR-079](../reference/index.md#finding-var-079), [VAR-080](../reference/index.md#finding-var-080), [VAR-081](../reference/index.md#finding-var-081), [VAR-082](../reference/index.md#finding-var-082), [VAR-083](../reference/index.md#finding-var-083), [VAR-084](../reference/index.md#finding-var-084), [VAR-085](../reference/index.md#finding-var-085), [VAR-086](../reference/index.md#finding-var-086), [VAR-087](../reference/index.md#finding-var-087), [VAR-088](../reference/index.md#finding-var-088), [VAR-089](../reference/index.md#finding-var-089), [VAR-090](../reference/index.md#finding-var-090), [VAR-091](../reference/index.md#finding-var-091), [VAR-092](../reference/index.md#finding-var-092), [VAR-093](../reference/index.md#finding-var-093), [VAR-094](../reference/index.md#finding-var-094), [VAR-095](../reference/index.md#finding-var-095), [VAR-096](../reference/index.md#finding-var-096), [VAR-097](../reference/index.md#finding-var-097), [VAR-098](../reference/index.md#finding-var-098), [VAR-099](../reference/index.md#finding-var-099), [VAR-100](../reference/index.md#finding-var-100), [VAR-101](../reference/index.md#finding-var-101), [VAR-103](../reference/index.md#finding-var-103), [VAR-104](../reference/index.md#finding-var-104), [VAR-105](../reference/index.md#finding-var-105), [VAR-106](../reference/index.md#finding-var-106), [VAR-107](../reference/index.md#finding-var-107), [VAR-108](../reference/index.md#finding-var-108)
- Corrections with this document as canonical home: [CORR-119](../reference/index.md#correction-corr-119), [CORR-123](../reference/index.md#correction-corr-123), [CORR-124](../reference/index.md#correction-corr-124), [CORR-125](../reference/index.md#correction-corr-125), [CORR-126](../reference/index.md#correction-corr-126), [CORR-127](../reference/index.md#correction-corr-127), [CORR-128](../reference/index.md#correction-corr-128), [CORR-129](../reference/index.md#correction-corr-129), [CORR-130](../reference/index.md#correction-corr-130), [CORR-131](../reference/index.md#correction-corr-131), [CORR-134](../reference/index.md#correction-corr-134), [CORR-135](../reference/index.md#correction-corr-135), [CORR-136](../reference/index.md#correction-corr-136), [CORR-137](../reference/index.md#correction-corr-137), [CORR-138](../reference/index.md#correction-corr-138), [CORR-139](../reference/index.md#correction-corr-139), [CORR-141](../reference/index.md#correction-corr-141), [CORR-142](../reference/index.md#correction-corr-142), [CORR-143](../reference/index.md#correction-corr-143), [CORR-144](../reference/index.md#correction-corr-144), [CORR-145](../reference/index.md#correction-corr-145), [CORR-146](../reference/index.md#correction-corr-146), [CORR-147](../reference/index.md#correction-corr-147), [CORR-148](../reference/index.md#correction-corr-148), [CORR-149](../reference/index.md#correction-corr-149), [CORR-150](../reference/index.md#correction-corr-150)
<!-- knowledge-cross-references:end -->
