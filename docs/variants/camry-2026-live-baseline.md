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
raw `3` while a Corolla was driving and treated it as D. This Camry result makes
P/D reuse substantially stronger, but P/R/N/D/B must still be captured on this
exact target before production CarState uses the complete enum.

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
transition in this repository. The exact causal alignment to the operator's
physical READY action was not independently timestamped, so a later controlled
READY/Not-Ready transition capture is still useful for policy.

## 6. XCP is negative on the tested route

A CONNECT-only probe on `0x7F7` over the identified EPS normal-harness route
timed out waiting for `0x7F8`. No XCP writes were exposed or attempted. This
makes the Sienna/H/F XCP observer route unavailable under the tested Camry
route/session conditions; it does not prove another physical route or ECU could
never expose that ID pair.

## 7. What this changes for openpilot work

The initial read-only Corolla TSS3 DBC is a useful **measurement scaffold** for
this Camry: `0x025`, `0x030`, `0x0AA`, `0x101`, `0x116`, `0x127`, and `0x51E`
all have strong continuity evidence. It is not yet a production Camry platform.
The exact EPS F181 differs, H/F's additional EPS Tx `0x351/0x394/0x4A3/0x4C8`
are absent from this segment, and no stock B6 transition has yet been captured.

Highest-value next evidence is therefore targeted rather than broad:

1. identify the Camry's Brake/EPB and FRC software/diagnostic endpoints instead
   of assuming Corolla category/address ownership transfers;
2. capture stock LTA `off -> active -> off` on this exact car while retaining all
   buses; if B6 appears, measure stock cadence, secondary bytes, freshness, and
   physical side-of-relay visibility;
3. capture stationary P/R/N/D transitions to close the target gear enum;
4. synchronize cruise main/engage/cancel with Camry-native diagnostic oracles;
5. acquire exact `8965F3307000` CodeFlash before transferring H/F boot-RAM,
   command-5, steering-limit, SecOC-receiver, or Panda-safety conclusions as
   firmware facts.

Until those are closed, production output remains disabled.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [VAR-051](../reference/index.md#finding-var-051)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
