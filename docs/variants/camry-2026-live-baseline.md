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

The remaining blockers are narrower and concrete:

1. capture stock LTA `off -> active -> off` on this exact car while retaining all
   buses — the still-open producer-side facts are stock sender cadence, the
   active-LTA secondary-field template, freshness evolution, and
   side-of-relay producer/suppression behavior;
2. live validation, not another static pass, of the now-closed F33 constants
   (tick period, mode2 limits, sequence-gap cap, monitor thresholds) against
   observed stock behavior before constructing production Panda limits;
3. prove target-native operational signing capability/latency and any required
   application-retention carrier before relying on ICU-S command 5. The complete
   DataFlash + post-handoff LocalRAM/GlobalRAM sweep found no raw authenticating
   key, so a retained application-context ICU-S command-5 path is now the primary
   signing direction rather than plaintext-key recovery. Retention, slot-4
   command-5 permission, and completion latency/contention under live
   command-7 traffic remain live gates (§12.6);
4. synchronize actual cruise engage/cancel with FRC `0x1905/0x1914`, and repeat
   following-distance if production CarState needs that ordinary-CAN field;
5. perform relay-correct interception testing before any lateral output. Passive
   bus-1 observation does not establish exclusive B6 authority or safe stock
   sender suppression.

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
that the vehicle entered meaningful cruise/ADAS state. The remaining zero-B6 problem is
therefore architectural rather than a bus-selection problem.

Deterministic topology evidence is promoted inside
`data/generated/gtsplus_2026/camry_8965F3307000_emps_semantics.json` and verified by
`tests/verify_camry_8965F3307000_gtsplus_semantics.py`; the physical relay/capture half
remains `data/generated/camry_2026_relay_correct_capture.json`.

## 20. Existing drives recover cruise operation and strongly identify LTA/LCA active state without B6

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
supplies the dynamic semantics: B21=`11` is the long cruise-active Class-L state;
B21=`18` is a short cruise-off state; and B21=`0` is the other state. Same-segment
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

Drive B also proves cruise and lateral active state are distinct: the `0x08A B3=8`
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
accepts protected B6 on the latter. The producer of the observed Bus-4 `0x08A` is
unknown, so it must not be labeled a Bus-1 camera frame. The retained `0x08A` therefore
closes the upstream request representation without making it interchangeable with the
downstream protected-B6 frame.

Historical Toyota names `LTA_RELATED` for `0x371` and `LKAS_HUD` for `0x412` are
corroboration only; no historical signal layout is transferred. Current FRC_P5 `LTA
Indicator 1` is a fixed RoutineControl/display active-test concept (`31 01 15 83`), not a
synchronized live-state oracle, and contributes no byte label. Likewise, no physical
LTA-button carrier is recovered: the decoded `0x0FE` pulses remain only the exact
same-car MAIN/RES+/SET-/CANCEL controls. The operator's report of a green LTA indicator
and steering assistance during the first drive is retained as separate human
corroboration, not machine evidence and not part of the numeric proof.

This supersedes VAR-067's “generic lateral/HUD candidate” wording (CORR-129) and the
later state/display-only interpretation (CORR-134). It still does not identify the
`0x08A` producer byte-exactly, recover its integrity/authentication trailer, recover the
producer-side path that creates the observed Bus-4 `0x08A` and its transformation into
Brake/EPS-side protected B6, or authorize steering output.
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

Therefore the corrected statement is stronger and narrower than VAR-065's old shorthand: **many more ordinary COM values are staged and observed than the 19-signal model showed, but no non-B6 generated-COM value is recovered as a value/mode input to the shared `CC50/CC62` command funnel or as the B6 assist-activation input.** Exact F33 also contains a B6-independent internal magnitude path feeding that same funnel. CORR-130/VAR-083 now close the downstream consequence that this section originally left open: `CC62` is a real pre-slew physical-command value and continues intra-function through `D042C -> CC66`, then `CC64/AC54/EE40C -> 6AF4 -> 6E0A -> 6DEC/6DC8/6DD6`. The remaining discriminator is **upstream stock-LTA authority into this funnel while B6 is absent**, not another blind ordinary-COM or downstream motor search. This does not authorize output.

Deterministic evidence is `data/generated/camry_8965F3307000_command_cone_ingress.json`, generated by `tools/build_camry_8965F3307000_command_cone_ingress.py` and verified by `tests/verify_camry_8965F3307000_command_cone_ingress.py`.

## 30. Exact-F33 B6-independent Command-Value-Torque model path: `D0218` supplies `CC4E/CC60`; `FEBE71F2` is only the limiter

The residual command branch from §29 is now positively recovered far enough to correct its provenance. `FUN_000D0382` loads dynamic `FEBECC4E` and limit `FEBEAC52`, then computes `FEBECC60 = clamp(FEBECC4E, +/-FEBEAC52)`. `FEBEAC52 <- FEBEEF8E <- FEBE71F2` is therefore a **saturation bound**, not command magnitude. Exact runtime writer `0x3BDC6` chooses the minimum active value from ROM table `0x317E0` — entries are only `0x2B4D`, `0x3A75`, or `0x569A`, with `0x569A` as the default — from an internally protected status mask before storing `FEBE71F2`. The former “peripheral planner/magnitude” interpretation is rejected by CORR-128.

The dynamic B6-independent magnitude enters earlier. `D0218` writes `FEBECC48`; `D0284` scales it by `FEBEAC64/0x8000` and clamps it to calibration `+/-B1334` as `FEBECC4C`; `D02DA` optionally slew/filters that value into `FEBECC4E`; `D0382` applies the limit above; then `D039E -> D042C` carries the result into `FEBECC62`. `D0AAE -> FEBEAC56 -> BF33E/FEBEE40A -> 1C02` is Toyota's recovered **pre-slew Command Value Torque diagnostic mirror**, while CORR-130/VAR-083 prove the same newly computed `CC62` value continues inside `D042C` through `CC66 -> CC64 -> AC54/EE40C` into the physical current-control funnel. The `D0284` multiplier is internal calibration state as well: `BCBD8` snapshots `FEBEB140 -> FEBEAC64`, while the complete `FEBEB140` writer census is `B3866/B389C/B38D2/BF97A`. The first three derive it from exact ROM u16 `0xAEF4C=0x5571` as `floor(0x2774564E/0x5571)=0x7636`; reset/default writer `BF97A` uses adjacent rounded constant `0x7637`. Thus no generated-COM/CAN value enters through the scale factor either.

`D0218` has three exact branches. When internal diagnostic flag `FEBEAC2B==0x5A`, it reduces to `FEBEC4C0 + FEBEC3BA + FEBEBF3C`. When B6-selected `FEBEC7BF==1`, it reduces to `FEBEC4C0 + FEBEBF3C`. In the ordinary B6-inactive branch it computes:

`FEBEC43C + FEBEC4C0 + FEBEC3BA + FEBECC2C + FEBEBF3C + clamp(FEBECB38 + FEBEC5EE, +/-B132C/2) + FEBECBE8`.

The direct runtime writers are all internal C/D-family algorithm state: `CF2B2 -> FEBECB38`, `C9A84 -> FEBEC5EE`, `C7E36 -> FEBEC43C`, `C8678 -> FEBEC4C0`, `C74AC -> FEBEC3BA`, `D0162 -> FEBECC2C`, `C2B64 -> FEBEBF3C`, and `CFCD4 -> FEBECBE8`. `FEBEAC2B` is an internal diagnostic/control snapshot (`BCBD8 <- FEBEB112`; `B338C` sets `0x5A`, `B330A/B3314` clear it), while `CB73A` can set `FEBEC7BF=1` only with B6 sig261 snapshot `FEBEADB0=='1'`. The complete generated-COM denominator in §29 therefore remains intact: this is an **EPS-internal baseline-assist path**, not a second generated-COM target ingress.

This also bounds the retained-drive interpretation. VAR-075 pins the `FEBEC5EE` moving-mode contribution to zero in both retained drives because its `0x0D5` s213 source is identically zero; the other `D0218` terms remain live and, through the now-verified `CC62 -> CC66/CC64 -> AC54/EE40C` chain, can have a real current-control consequence with B6 absent. But semantic closure of all eight terms finds no independently recovered **lane-target** magnitude: they reduce to measured torque, torque+speed maps, internal aggregation/ROM state, `|torque|` curves, and angle return/dither/excitation. VAR-081 identifies the interval as LTA/LCA active. The unresolved question is therefore what upstream state/value gives this shared funnel factory lane-centering authority with B6 absent, not whether `CC62` reaches the motor. Nothing here authorizes output.

Deterministic evidence is the `baseline_internal_assist_path` section of `data/generated/camry_8965F3307000_command_cone_ingress.json`, generated from the exact 6,065-function F33 corpus and verified by `tests/verify_camry_8965F3307000_command_cone_ingress.py`.

## 31. Baseline-assist parameter-bank selector: ordinary COM selector inputs are route-wide zero/absent in both retained Class-L drives

VAR-079 closes the next discriminator immediately upstream of several `D0218` baseline-assist terms. Exact F33 does contain a parameter-bank selector, but its **ordinary generated-COM inputs do not change with the retained Class-L state**.

**Static selector chain.** The complete scalar-value subset recovered into this selector is seven signals: `0x51E/8` sig160 `B0[3:0] -> FEBE8030 -> FEBEF050`, sig163 `B1[3:0] -> FEBE8033 -> FEBEF14A`, and sig166 `B5[7:6] -> FEBE8032 -> FEBEF141`; `0x13B/8` sig224 `B2[3:0] -> FEBE8082 -> FEBEF14B`; `0x490/1` sig280 `B0[6:4] -> FEBE80D2 -> FEBEF168` and sig281 `B0[3:0] -> FEBE80D3 -> FEBEF0A1`; and `0x1DA/8` sig282 `B0[3:0] -> FEBE80D6 -> FEBEF156`. `0x58074` stages these cells. The debouncers additionally consume resolved COM-receive validity/gate state: `FEBEF0C2 <- FEBE8081 <- FUN_000498E0(0x15)` for the `0x13B` companion path, `FEBEF0A0 <- FEBE80D5 <- FUN_000498E0(0x1C)` for `0x490`, `FEBEF157 <- FEBE80D8 <- FUN_000498E0(0x1D)` for `0x1DA`, plus shared gate `FEBEF000 <- FEBE7F68`. These companions can suppress extraction/qualification but carry no selector value and do not choose a bank directly; absent `0x490/0x1DA` traffic cannot provide a fresh valid selector value. `B3430/B3686` debounce the `FEBEF050` family into `FEBEB124`; `B34D4/B3538` qualify companion fields; `B35DC/B372A` reduce that state into `FEBEB121`; `BCBD8` snapshots `FEBEB121 -> FEBEAC2F`; `C54A2` selects `FEBEC158`; `C5554` maps `FEBEC158` values `0x77/0x44/0x88` to `FEBEC156=1/2/3`; and `C28FC` uses `FEBEC158/FEBEC156` to choose the calibration block consumed by baseline-assist terms such as `C2B64`. This is parameter selection, not a steering-target magnitude.

The other selector branches are explicitly internal. `C54A2` can choose `0x66` from diagnostic state `FEBEAC2B`, `0x11` from an internal `0x5AA5A55A` magic-state path, or `0x55` from internal status `FEBEAC30/FEBEAC40` under its validity gates. `FEBEAC50`, another validity mask, is copied by `BCAA6` from `FEBEEF88 <- FCC00 <- FEBE71EC`; it is not generated COM. The `FEBEAC3C&1` table-bank bit is also not drive mode: `BCBD8 <- FEBEB354`, while `B7374 -> FF254 -> 62E12` reports the TMR-protected `FEBF0668` verdict produced by `62D5E` after comparing the ROM compatibility/parameter block at `0x17DA0/0x17DC0...` against its working copy at `0x20850/0x20870...`. That bit is parameter-copy integrity.

**Retained-drive join.** The two relay-correct CAN-only captures directly reject the ordinary-COM selector as the Class-L discriminator. In drive A, all **519** observed `0x51E` frames have sig160=sig163=sig166=0, including all **16** samples inside the 16.119256-s Class-L interval; all **17,176** `0x13B` frames have sig224=0, including **537** inside Class-L. In drive B, all **600** `0x51E` frames have those three signals zero, including all **57** Class-L samples; all **20,000** `0x13B` frames have sig224=0, including **1,906** inside Class-L. `0x490` and `0x1DA` are absent in both captures. Every populated three-second pre/post Class-L edge window has the same selector value support on both sides.

Therefore the directly recovered ordinary-COM parameter-bank inputs cannot explain the retained LTA/LCA transition or its motor-feedback shift. Exact calibration now strengthens that negative: healthy selector1 is the only distinct `C28FC/C2B64` normal bank, selectors0/2/3 alias, all fallback banks alias, and route-zero sig160 can reach only equivalent selector0/2. Combined with VAR-081/083, the remaining discriminator has moved upstream into **internal/special selector state or another as-yet-unrecovered authority/value producer feeding `CC50`**, not the ordinary COM selector. The 0x51E observations are only about one sample per second, so they do not establish high-rate timing; their stronger fact is that the relevant fields are zero for the entire retained routes. VAR-081 already supplies the LTA/LCA state identification; FRC `0x1601` is independent corroboration, not a naming prerequisite. Nothing here authorizes output.

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

The remaining contradiction is therefore **upstream of this now-closed physical
convergence**, not downstream: during 73.303384 s of strongly identified factory
LTA/LCA-active operation the actual Brake/EPS Bus-4 capture contains zero B6, yet the
operator directly observed the car steering under factory LTA. VAR-082 simultaneously
finds no second ordinary external CAN field that leads the steering response. The next
question is exactly **what state/value makes the shared `CC50/CC62` funnel carry factory
LTA authority with B6 absent, or which still-unclosed indirect producer changes that
funnel's inputs.** Nothing here authorizes output.

Deterministic evidence is carried by
`data/generated/camry_8965F3307000_internal_assist_oracles.json` and
`tests/verify_camry_8965F3307000_internal_assist_oracles.py` (VAR-083 / CORR-130).

## 35. Hidden-ingress false-negative audit: no concrete alternate producer found; residuals closed in §36

Because the retained physical observation and the firmware model are now in direct tension,
a second read-only audit attacked the ways the canonical Ghidra graph could have missed a
non-B6 producer instead of assuming the observation was wrong. The result is a much tighter
negative, but not an absolute proof.

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

This audit does **not** resolve the contradiction by reclassifying the observed factory LTA
steering as generic assist. The direct vehicle observation is retained as evidence to be
explained. The supported conclusion is narrower: **ordinary CAN, the known fixed DMA and
pointer/callback paths, and the recovered downstream physical actuation funnel do not yet
explain how stock LTA authority enters `CC50/CC62` with B6 absent.** That is now the one
steering-command problem to solve (VAR-084). VAR-085 removes E1/E2 as remaining static
escape hatches; it does not supply the missing stock-LTA authority source.

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

Together E1+E2 remove the two strongest “Ghidra missed the producer” explanations inside
F33. Subsequent route reconciliation (VAR-081/CORR-134) resolves the apparent
contradiction at the network boundary instead: upstream `0x08A` carries Target Lateral ID
plus a target angle at the exact B6 scale, but F33 does not accept `0x08A`; Brake/EPS-side
integrity/authentication contract and the producer-side `0x08A`-to-B6 transform, signer,
freshness, and arbitration path—not another F33 hidden-ingress census.

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

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-060](../reference/index.md#finding-tms-060), [VAR-051](../reference/index.md#finding-var-051), [VAR-052](../reference/index.md#finding-var-052), [VAR-053](../reference/index.md#finding-var-053), [VAR-054](../reference/index.md#finding-var-054), [VAR-055](../reference/index.md#finding-var-055), [VAR-056](../reference/index.md#finding-var-056), [VAR-057](../reference/index.md#finding-var-057), [VAR-060](../reference/index.md#finding-var-060), [VAR-061](../reference/index.md#finding-var-061), [VAR-063](../reference/index.md#finding-var-063), [VAR-064](../reference/index.md#finding-var-064), [VAR-065](../reference/index.md#finding-var-065), [VAR-066](../reference/index.md#finding-var-066), [VAR-067](../reference/index.md#finding-var-067), [VAR-068](../reference/index.md#finding-var-068), [VAR-069](../reference/index.md#finding-var-069), [VAR-070](../reference/index.md#finding-var-070), [VAR-072](../reference/index.md#finding-var-072), [VAR-073](../reference/index.md#finding-var-073), [VAR-074](../reference/index.md#finding-var-074), [VAR-075](../reference/index.md#finding-var-075), [VAR-076](../reference/index.md#finding-var-076), [VAR-077](../reference/index.md#finding-var-077), [VAR-078](../reference/index.md#finding-var-078), [VAR-079](../reference/index.md#finding-var-079), [VAR-080](../reference/index.md#finding-var-080), [VAR-081](../reference/index.md#finding-var-081), [VAR-082](../reference/index.md#finding-var-082), [VAR-083](../reference/index.md#finding-var-083), [VAR-084](../reference/index.md#finding-var-084), [VAR-085](../reference/index.md#finding-var-085), [VAR-086](../reference/index.md#finding-var-086)
- Corrections with this document as canonical home: [CORR-119](../reference/index.md#correction-corr-119), [CORR-123](../reference/index.md#correction-corr-123), [CORR-124](../reference/index.md#correction-corr-124), [CORR-125](../reference/index.md#correction-corr-125), [CORR-126](../reference/index.md#correction-corr-126), [CORR-127](../reference/index.md#correction-corr-127), [CORR-128](../reference/index.md#correction-corr-128), [CORR-129](../reference/index.md#correction-corr-129), [CORR-130](../reference/index.md#correction-corr-130), [CORR-131](../reference/index.md#correction-corr-131), [CORR-134](../reference/index.md#correction-corr-134)
<!-- knowledge-cross-references:end -->
