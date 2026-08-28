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
Toyota/GTS+ gives a direct oracle: FRC DID **`0x1601`** contains `LTA Switch
Condition Flag` in bits 0-7 and **`LTA Control Condition`** in bits 8-15, with
Hands-Off customize/control in bits 16-31. Useful companion reads are `0x1501`
(LDA customize/control), `0x1681` (LCA customize/control), and `0x1903` (`Control
Mode`). The current P5 Data List transport is ordinary `22 <DID>` / `62 <DID>`;
response bytes must be independently checked against the requested DID.

A separate direct-Panda logger attempted during the drive collided with the
already-running `pandad` and terminated on Panda USB **`CHECKSUM_ERROR`**. It is
not used as evidence. All drive conclusions above come from normal `loggerd` rlogs
reduced deterministically to the tracked CAN-only artifacts. Future synchronized
diagnostic captures must use one Panda owner rather than opening a second direct
Panda stream alongside `pandad`. Deterministic interpretation lives in
`data/generated/camry_2026_relay_correct_capture.json` and is verified by
`tests/verify_camry_2026.py`. Production steering output remains disabled.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [TMS-060](../reference/index.md#finding-tms-060), [VAR-051](../reference/index.md#finding-var-051), [VAR-052](../reference/index.md#finding-var-052), [VAR-053](../reference/index.md#finding-var-053), [VAR-054](../reference/index.md#finding-var-054), [VAR-055](../reference/index.md#finding-var-055), [VAR-056](../reference/index.md#finding-var-056), [VAR-057](../reference/index.md#finding-var-057), [VAR-060](../reference/index.md#finding-var-060), [VAR-061](../reference/index.md#finding-var-061), [VAR-063](../reference/index.md#finding-var-063)
- Corrections with this document as canonical home: [CORR-119](../reference/index.md#correction-corr-119), [CORR-123](../reference/index.md#correction-corr-123), [CORR-124](../reference/index.md#correction-corr-124)
<!-- knowledge-cross-references:end -->
