# 2026 Camry live TSS3/EPS baseline

## Scope and evidence

On 2026-08-26 the maintainer's 2026 Toyota Camry produced an identity-bound TSK
baseline covering EPS diagnostics, a stationary READY CAN segment, a bounded
PROGRAMMING handoff, and an XCP CONNECT-only probe. Raw/privacy-minimized source
evidence is retained under `community/kai/camry-2026/raw-20260826/`; the
reproducible compact analysis is
`data/generated/camry_2026_tsk_baseline.json`.

This is **dynamic field evidence**, not a Camry CodeFlash analysis. Corolla H/F
names are used below only where the wire behavior itself strongly transfers.
Anything that depends on code, calibration constants, SecOC slot configuration,
or authenticated RAM execution remains untransferred until `8965F3307000`
CodeFlash or an independent Camry-native oracle closes it.

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

## 2. PROGRAMMING transfer: family-positive, bootstrap still unknown

The bounded DEFAULT -> EXTENDED -> PROGRAMMING probe succeeds and the diagnostic
endpoint reappears on the same explicit route. Bootloader F181 is exactly
`02 || 32*0x21`, matching the placeholder shape directly observed on the tracked
Denso EPS family. Functional `0x777` also receives a session-control response
around the handoff.

That is useful family evidence, but the boundary is important. This session did
**not** prove Camry boot SecurityAccess, DID `0201/0202/0203` semantics,
RequestDownload address/length/memory-ID geometry, routine `0x10F0`, callback
`0xFF00`, or application-retained executable RAM. The TSK recovery gate correctly
stops at exact-F181 RAM-exec geometry instead of copying `FEBF0000` from H/F or
Sienna.

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

## 6. XCP is negative on the tested route

A CONNECT-only probe on `0x7F7` over the identified EPS normal-harness route
timed out waiting for `0x7F8`. No XCP writes were exposed or attempted. This
makes the Sienna/H/F XCP observer route unavailable under the tested Camry
route/session conditions; it does not prove another physical route or ECU could
never expose that ID pair.

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
`tests/verify_camry_2026_nrtd_p5.py`. Raw source identities are pinned separately
in `community/kai/camry-2026/raw-20260826/NRTD_MANIFEST.txt` so VAR-051's READY
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
`tests/verify_camry_2026_ready_gear.py`. Exact capture/script hashes and the
operator-sequence correction are pinned in
`community/kai/camry-2026/raw-20260826/READY_GEAR_MANIFEST.txt`.

## 9. What this changes for openpilot work

The initial read-only Corolla TSS3 DBC is a useful **measurement scaffold** for
this Camry: `0x025`, `0x030`, `0x0AA`, `0x101`, `0x116`, `0x127`, and `0x51E`
all have strong continuity evidence. It is not yet a production Camry platform.
The exact EPS F181 differs, H/F's additional EPS Tx `0x351/0x394/0x4A3/0x4C8`
are absent from this segment, and no stock B6 transition has yet been captured.

Highest-value next evidence is therefore targeted rather than broad. The FRC and
Brake/EPB identities, NRTD cruise-button oracles, and the `0x0FE` momentary switch
carrier are now closed dynamically. What remains is:

1. capture stock LTA `off -> active -> off` on this exact car while retaining all
   buses; if B6 appears, measure stock cadence, secondary bytes, freshness, and
   physical side-of-relay visibility;
2. while READY, synchronize cruise main plus actual engage/cancel with `0x1905`
   permission and `0x1914` ACC-control-in-operation;
3. repeat/cycle following-distance if production CarState needs its ordinary-CAN
   carrier, to distinguish `0x251` from `0x5AF` and close the enum;
4. acquire exact `8965F3307000` CodeFlash before transferring H/F boot-RAM,
   command-5, steering-limit, SecOC-receiver, or Panda-safety conclusions as
   firmware facts.

Until those are closed, production output remains disabled.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [VAR-051](../reference/index.md#finding-var-051), [VAR-052](../reference/index.md#finding-var-052), [VAR-053](../reference/index.md#finding-var-053)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
