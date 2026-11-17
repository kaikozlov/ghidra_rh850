# GTS+ TSS3 fleet architecture and topology census

> **Scope:** current GTS+ `2026.03.002.02` (`GTS+ DB` 01.01.037) regional
> master databases (NA/EU/JP), the v18 `IT3Data_BDC_{NA,EU,JP}.vds`
> `ECU_Setting_Table`, and the Toyota master CAN Bus Check tables.
>
> **Status:** active; generator + generated JSON/CSV + deterministic verifier
> all tracked.
>
> **Evidence source:** generated-artifact over current-GTS+ master DDBs and the
> pinned v18 MDB VDS corpus (external-source-derived, deterministic to
> regenerate).
>
> **Verification:** `tests/techstream/verify_gtsplus_tss3_crossvehicle_surface.py`
> (suite `gtsplus_tss3_crossvehicle_surface`).
>
> **Artifacts:**
> `data/generated/gtsplus_2026/tss3_crossvehicle_surface.json`,
> `data/generated/gtsplus_2026/tss3_crossvehicle_fleet_install_sets.csv`,
> `data/generated/gtsplus_2026/tss3_crossvehicle_canbus_placements.csv`.
> Producer: `tools/techstream/extract_gtsplus_tss3_crossvehicle_surface.py`.

## 1. Question and result

Which vehicles carry the category-498 `FRC_P5` (Front Recognition Camera 2)
TSS3 generation, in which ECU clusters, at which diagnostic addresses, on which
Toyota network topology — and where are the region-local boundaries?

The census joins, per region:

| Join | Tables | Result |
|---|---|---|
| vehicle names | `CDbVehicleNameTable` (43) | 2,863 NA vehicle-type rows |
| vehicle → install set | `CDbEcuGroupTable` (5) | region-local install-set ids |
| install set → categories | `CDbInstallingEcuListTable` (44) | full installed ECU sets |
| category identity | `CDbEcuCategoryTable` (16) | id/generation/database/name |
| diagnostic address | v18 `ECU_Setting_Table` | ECUNo → 0x7xx request id |
| CAN topology | `CDbCanBusCarIdTable` (75), `CDbCanBusOptionTable` (77), `CDbCanBusComponentTable` (78), `CDbSubBusConfirmationCGWTable` (76), `CDbCanBusNameTable` (79), `CDbCanBusListTable` (55) | component → bus → gateway |

`CDbVehicleDecisionTable` (41) and `CDbVinVehicleDecisionTable` (59) are
present in every regional master (NA: 1,869 / 2,402 rows), but their row layout
is **not deterministically recovered**; the census joins only decoded tables
and infers no decision semantics from them.

## 2. Fleet architecture census (install sets carrying 498)

Per-region install rows (one row per vehicle type × 498-carrying install set):

| Region | install rows | model names | architectures | car topology rows | topology shapes |
|---|---:|---:|---:|---:|---:|
| NA | 256 | 51 | 5 | 251 | 114 |
| EU | 460 | 93 | 9 | 454 | 356 |
| JP | 213 | 70 | 9 | 207 | 107 |

Leading architectures (selected-category labels; full lists in the artifact):

| Architecture | NA | EU | JP |
|---|---:|---:|---:|
| `EMPS+ABS+BRKBST+FRC` (405+435+466+498) | **117** | **221** | **99** |
| `EMPS+ABS+FRC` (405+435+498) | **98** | **183** | **65** |
| `EMPS+FRC` (405+498) | **36** | **36** | **20** |
| `ABS+FRC` (435+498, no EPS row) | — | 7 | **16** |
| `EMPS+LDA+FRCAM+ABS+BRKBST+ADS+ADeU+FRC+EMPS2` | 4 | 4 | 4 |
| `FRC` alone (the NA `TEST` placeholder) | 1 | — | — |

Region-local tails (full lists in the artifact): EU adds
`EPS_P4+EMPS+ABS+FRC` (3, LS500), `EMPS+ABS+BRKBST+FRC+EMPS2` (3),
`EMPS+FRC+EMPS2` (2), `ABS+BRKBST+FRC` (1); JP adds
`EMPS+ABS+BRKBST+FRC+EMPS2` (5), `EMPS+FRC+EMPS2` (2),
`EMPS+LDA+FRCAM+ABS+BRKBST+EPB+FRC+EMPS2` (1, ZZZ4_P5C), `ABS+EPB+FRC` (1,
TEST).

Every dominant architecture pairs 498 with steering 405 and brake 435; 466
Brake Booster is the main fleet split; the NA `FRC` singleton shows 498 can
appear with no selected steering/brake cluster row at all.

### Region-local measured boundaries

- **Zero co-occurrence in all regions** for PCS1 427, DSSystem 428,
  Fr_RadSen 429, RoadSign 431, PCS2 432 — the pre-498 P5 longitudinal compute
  generation is disjoint from the 498 architecture by current install sets.
  (430 Fr_Camera and 418 LDA appear only inside the small ADS/ADeU cluster.)
- **Install-set ids are region-local, provably**: NA and JP share 91 numeric
  install-set ids; 90 of them map to **different full category sets**. NA/EU
  and EU/JP 498-carrying id spaces are disjoint. Never join install-set ids
  across regions by number.
- `TEST`, `MAC`, and JP `ZZZ4_P5C` placeholder vehicle types carry 498 install
  sets but have **no CAN Bus Check topology row** (NA 5, EU 6, JP 6 vehicle
  types without topology).

### Camry HV powertrain and ADAS generations

NA vehicle types 12704, 12862 and 12984 retain the generation-20 ADAS
categories 405/435/466/498 while their powertrain generations differ:

| Vehicle type | Powertrain install set | ADAS/chassis install set |
|---|---|---|
| 12704 | 8119 (`0x1FB7`), generation 20 | 8120 (`0x1FB8`) |
| 12862 | 8593 (`0x2191`), generation 20 | 8594 (`0x2192`) |
| 12984 | 8959 (`0x22FF`), generation 22 | 8960 (`0x2300`) |

The generation-22 powertrain set contains 6000 `Engine_CM_P6`,
6026 `HE_PCM_A_P6`, 6027 `DMCM_A_P6` and 6031 `BECM_P6`.
Vehicle 12704 also lists empty install set 27706 (`0x6C3A`).

Source: NA vehicle/install-set/category records in
`data/generated/gtsplus_2026/toyota_diag_bundle_current/index.json.gz`;
the 498-carrying rows are also in
`data/generated/gtsplus_2026/tss3_crossvehicle_fleet_install_sets.csv`.

### Category families

| Family | Categories | 498 co-occurrence |
|---|---|---|
| steering_actuation | 142, 405, 499 | 405 near-universal; 499 minority; 142 EU-only |
| brake_domain | 435, 466, 485 | 435 majority; 466 ~half; 485 JP-only |
| front_perception_compute | 430, 498 | 430 only in the ADS/ADeU cluster |
| radar_lateral_periphery | 418, 429 | 418 only in the ADS/ADeU cluster; 429 never |
| pre_498_pcs_compute | 427, 428, 431, 432 | never with 498 |
| adas_supervision_ethernet | 476, 477 | only in the small ADS/ADeU cluster |

The generator asserts that selected-category identities (id, generation,
database, name) are **identical across NA/EU/JP**.

## 3. Diagnostic request addresses (v18 ECU_Setting_Table join)

The original fleet census used the v18 address join below. Current GTS+ also
resolves category/route-selector pairs through master table13
`CDbProtInfoTable`; the Camry/Corolla comparison in §4 uses that current
binding, including Brake Booster's `0x750` / extension `0x29` route.

The v18 source is the
`IT3Data_BDC_{region}.vds` `ECU_Setting_Table` (40-byte Jet rows: ECUNo u32
+0x02, phase u32 +0x06, address = 3 ASCII bytes after the FF FE marker at
+0x1A). Matched phase-5 rows: NA 26, EU 24, JP 26 (EU lacks 402 Solar and 5005
RC_P5).

| ECUNo | Database | Address | Notes |
|---|---|---|---|
| 372/373 | Engine/ECT | 700/701 | |
| 395/397/398 | MG/HV/HV Battery | 724/7D2/747 | |
| 400/401 | PluginCtrl AC/DC | 745/707 | |
| 402 | Solar | 703 | NA/JP only |
| **405** | **EMPS_P5** | **7A1** | corroborated on-wire (Camry 2026) |
| **435** | **ABS_P5** | **7B0** | corroborated on-wire (Camry 2026) |
| 438/440/449/452/454/460/470/486/489/495 | IPA/SMART/JBUnity/TPM/PSC/BSMM/CMCCM/Roof/PBD/SubBattery | 750 | shared gateway-routed address |
| 445 | StrAngleSnsr | 7B3 | |
| 450 | A_C | 7C4 | |
| 490 | FC | 7D1 | |
| 496 | NaviSystem | 7D0 | |
| **498** | **FRC_P5** | **792** | corroborated on-wire (Camry 2026) |
| 5005 | RC_P5 | 7A2 | NA/JP only |

Boundary: **none of 466 Brake Booster, 476 ADS, 477 ADeU, 499 EMPS2, 418/427/
428/429/430/431/432, 485 EPB carries an ECU_Setting row.** ADS/ADeU
are Ethernet-phase categories by database name (`ADS_Eth_P5`/`ADeU_Eth_P5`);
how the remaining unaddressed categories are reached is an open question
(hypothesis: via the shared 0x750 gateway address or simply not exposed in
this table). Cross-generation stability of each address is only *observed*
where repo captures corroborate it (Camry 2026: FRC 0x792, EPS 0x7A1, skid
0x7B0).

## 4. CAN Bus Check topology join

For every 498-carrying vehicle type, the census resolves
vehicle → `CDbCanBusCarIdTable` car id → option group → per-component
placements (bus index, bus name, gateway names, junction), deduplicated into
placement shapes (shape = full placement vector).

**Universal structural result.** In every placement shape that contains both
Power Steering (EPS, `0x32`) and Skid Control (`0x29`), the two are colocated
on one bus and the Front Camera Module (`0x6D`) sits on a different bus:
NA 114/114 shapes, EU 328/328 shapes carrying both, JP 99/99 shapes carrying
both. No shape anywhere in the fleet splits EPS from Skid Control. The Camry
Bus-4-chassis / Bus-1-camera split documented in
[variants/camry-2026-live-baseline.md](../variants/camry-2026-live-baseline.md)
follows the generic TSS3 topology pattern.

Worked example (asserted by the verifier): the three NA Camry HV vehicle types
12704/12862/12984 share car id `0x00A7D910`; its shape places FCM `0x6D` on
`Bus 1` (index 29) and Skid `0x29` + EPS `0x32` on `Bus 4` (index 32), both
behind `Central Gateway`.

### Camry / Corolla HV harness-discrepancy comparison (2026-11-17)

**GTS+ and the supplied Toyota drawings establish different camera/radar
attachments, not the packet path responsible for the reported Panda bus-2
control.** Their external network order is CGW → FRC → radar for Corolla
and CGW → radar → FRC for the Camry comparison. Both diagnostic maps place
the camera on Toyota Bus 1 and EPS/brakes on Toyota Bus 4. Connecting these
facts to the intercepted SecOC traffic requires the exact pair and internal
ECU routing; attachment order alone does not establish that connection.

This comparison re-read the pinned NA/Gen DDBs through `tools/gts`, inspected
each raw option/component row, and traced the supplied OEM drawings against
the Toyota-B schematic. The [source comparison](../../data/external/toyota_camry_corolla_camera_topology.json)
retains the selected vehicle/install identities, every relevant option,
raw component records and drawing identities.

| Source selection | Corolla HV | Camry HV |
|---|---|---|
| CAN topology key (table75) | `0x00A7D901` | `0x00A7D910` |
| Vehicle-type rows sharing key | 20 | 3: 12704/12862/12984 |
| Options (table77) | 1, component group `0x004DD237` | 18 |
| Bus-membership shapes | 1 | 1 |
| Shapes including attachment strings | 1 | 12 |
| Front Camera Module `0x6D` | Toyota Bus 1, index29 | Toyota Bus 1, index29 |
| EPS `0x32`, Skid Control `0x29`, Brake Booster `0x28` | Toyota Bus 4, index32 | Toyota Bus 4, index32 |

The Corolla key covers types 12514/12515/12584/12585, 12614–12617,
12719–12722, 12823–12826, and 12939–12942. Ten carry category498 in an
install set: 12514/12515, 12614/12616, 12719/12720, 12823/12824,
12939/12940. The common topology result does not depend on choosing a
particular one of those types.

The **attachment/junction strings** in table78 differ:

| Component | Corolla HV, group `0x004DD237` | Camry HV, all 18 options |
|---|---|---|
| Front Radar `0x0F` | `FCM` | `No. 1 Global CAN Junction Connector`, `No. 8 Global CAN Junction Connector`, or `-` |
| Front Camera Module `0x6D` | `No. 18 CAN Junction Connector` | `FRD` or `-` |
| EPS `0x32` | `No. 13 CAN Junction Connector` | `EBU` |
| Skid Control `0x29` / Brake Booster `0x28` | `No. 10 CAN Junction Connector` | `No. 2 Global CAN Junction Connector` |
| Steering-angle sensor `0xF0` | `No. 13 CAN Junction Connector` | `No. 7 Global CAN Junction Connector` |

`FCM`, `FRD`, `EBU`, and `-` above retain Toyota's literal strings. The
Camry EPS attachment is invariant across the 18 options. Its radar/camera
attachments have six combinations; the body-controller attachment accounts
for the remaining split into 12 complete attachment shapes. The existing
`canbus` placement grouping compares component/domain/bus, **not attachment
strings**, so its `placement_variants=1` must not be read as identical wiring
across all options. The particular Camry option requires vehicle option
selection; do not promote the first option to the owner's exact wiring.

Current master tables5/44/16 also bind both families to the same P5 categories:
405 `EMPS_P5`, 435 `ABS_P5`, 466 `Brk_Bst_P5`, and 498 `FRC_P5`.
For example Corolla type12823/set8477 and Camry type12862/set8594 carry all
four. Current table13 gives the same `(category, route_selector)` routes:
405/`0x12` → `0x7A1`, 435/`0x12` → `0x7B0`, 498/`0x12` → `0x792`,
466/`0x22` → `0x750` extension `0x29`. Front radar429/`0x22`, in the
separate radar install sets, uses `0x750` extension `0x0F` in both. These
are diagnostic transport bindings, not Panda bus assignments.

The shared `FRC_P5` dictionary includes `U012987` (Brake), `U013187` (EPS),
and `U131757` (software incompatibility with Gateway E). `ABS_P5` includes
`U013187` and `U11B187` (EPS ch2). Those are dictionary entries, not live
fault observations or proof of a model-specific forwarding policy. No inspected
GTS record supplies a Corolla FRC forwarding rule for `0x030`, `0x081`,
`0x777`, or `0x7A9`. The EPS `EBU` versus junction difference is relevant
when investigating an EPS-local leg; it does not establish a reversal of the
comma relay endpoints.

#### Pin-level reconciliation with the supplied wiring drawings

The Toyota-B adapter labels CAN2 as camera-facing and CAN0 as car-facing.
Those labels describe the two ends of the **intercepted pair**, not every
network reachable through the camera assembly. Its 2025-03-07 schematic
also carries other CAN pairs straight through:

| Toyota camera connector pins | Stock Toyota-B connection | After the discussed 9/10 ↔ 11/12 pair repin |
|---|---|---|
| 9/10 (`CA1N`/`CA1P`) | Panda CAN1, blue/pink | Camera-facing CAN2 ↔ relay ↔ car-facing CAN0 |
| 11/12 (`CANL`/`CANH` on the Camry EWD) | Panda CAN2/CAN0, green/orange | Unsplit Panda CAN1 |
| 1/2 (`CA2L`/`CA2P`) | PT5/PT4, green-white/purple | Unchanged straight-through connection |
| 3/4 (`CA3L`/`CA3H` on the Camry EWD) | PT6/PT7, purple-brown/red-black | Unchanged straight-through connection |

Toyota's CA1/CA2 names are not Panda bus numbers. In particular, Toyota
pins1/2 are **not** the Panda CAN1 pair moved by this repin.

The supplied Corolla CAN-system drawing (`image.png`, identified by SHA-256
in the comparison artifact) shows:

- CGW I173-28/27 (`CA1H/L`) → I192 No.18 CAN junction → FRC T21-2/1
  (`CA2P/L`);
- FRC T21-10/9 (`CA1P/N`) → radar A128-10/9 (`CA3H/L`);
- radar A128-4/3 (`CA2H/L`) → O203 No.19 junction → O95 termination
  and the optional O57 blind-spot monitor.

This agrees with GTS+'s radar attachment `FCM` and camera attachment
`No. 18 CAN Junction Connector`. The T21 labels match the user-supplied
Corolla terminal page; the cropped network drawing carries no complete
model-year header, so its applicability is joined by these connector and
GTS attachment identities rather than an invented production date.

The supplied Camry `MPX-C.pdf`, pp.3 and 8, places the same T4-10/9 pair on
radar B5-10/9; it separately connects T4-12/11 to B5-8/7. Its pp.2–8 and the
supplied Bus-1 overview put the gateway-facing network before the radar,
then the FRC, then the BSM/end-of-bus network. GTS+ independently records
camera attachment `FRD` for the applicable equipment variants and every
`202509-` option. The earlier `w/o BSM and w/o R-CA` options must retain
their separate `-` camera attachment.

For that comparison, the 9/10 interception is:

```text
Camry:   CGW … radar — CAN0 | open relay | CAN2 — FRC … termination
Corolla: CGW — FRC pins1/2 — FRC — CAN2 | open relay | CAN0 — radar … termination
```

These are external network-order diagrams, not asserted internal ECU
shorts or forwarding implementations. The important physical fact is that
**Corolla FRC pins1/2 retain their gateway-facing connection while the
9/10 relay is open**. They pass through the adapter independently of Panda
CAN1 and the CAN0/CAN2 relay.

**Unresolved packet path:** the untouched 1/2 connection is a lead for
alternate reachability, not an established explanation. The drawings do not
show forwarding between the FRC's 1/2 and 9/10 interfaces or forwarding of
`0x030`, `0x081`, `0x777`, `0x7A9`, or host `0x08A`. Such a mechanism would
need to carry chassis traffic toward CAN2 and accepted host commands back
toward the chassis. It would not, by itself, explain native FRC output
originating on the opposite relay endpoint. The supplied Camry overview draws
Toyota Bus 4 separately, terminating at CGW/EPS; it is not evidence that the
camera/radar Bus-1 chain is the same electrical segment as the control link.

The checked `spanconstant5/openpilot` Star revision
`3a1063ceb801e8f7f3eed35cfabd2e8fe48b383a` configures both the Corolla PT
parser and camera `CONTROL_REQUEST` parser on `TSS3_SOURCE_BUS` (bus2), in
`opendbc_repo/opendbc/car/toyota/carstate.py:427–447`. The November-14 audit
at `db66343e9276042202ad77e1015dce0e380db2c4` also describes native `0x08A`
on bus2 (`docs/tss3-port-audit.md:624–628`). Those sources do not establish a
clean native-source swap of FRC→bus0 and chassis→bus2. Keep their reported
observations separate from an independently inspected raw capture.

**Source-isolation consequence:** blocking the FRC-to-radar 9/10 leg does
not establish that native FRC `0x08A` is excluded from the separate
FRC-to-gateway 1/2 leg. Determine that route before treating a bus-constant
swap as complete source replacement or assessing PCS handoff. This comparison
contains no new live traffic, continuity measurement or PCS test.

Reproduction:

```sh
tools/gts canbus 'Corolla HV' --json
tools/gts canbus 12862 --json
tools/gts category FRC_P5 --json
tools/gts dtc FRC_P5
tools/gts dtc ABS_P5 'Power Steering'
```

Raw anchors in `NA/DB/Gen/Toyota.ddb` (zero-based ordinals): table75
row585 is Corolla12823, row617 is Camry12862. In table78, Corolla group
`0x004DD237` has radar24216, camera24218, brake24228, EPS24229, and
steering-angle24231. Camry's first group `0x004DD26A` has radar26085,
camera26090, brake26102, EPS26103, and steering-angle26105; inspect all
18 table77 groups for the attachment comparison. Source SHA-256:
`Toyota.ddb` = `f11e820968ac383a8fc5105b65322f0b9c3673df2c8dac46c9847e3d691b39b1`;
`M_English.ddb` = `458a7039851fc66dc2385fff2efa910337218b8b23985b3c1afc0db7bc5f8014`.

### Identity namespaces — Toyota vs panda

`bus_index`/`bus_name`/`gateway_names` are **Toyota
`CDbCanBusNameTable`/`CDbCanBusListTable` network-model identities** ("Bus 1",
"Bus 4", "Central Gateway"). They are:

- **not comma panda bus numbers** (panda buses 0/1/2 are harness/controller
  queues — see [panda-toyota-routing.md](panda-toyota-routing.md) for the four
  naming layers), and
- **not connector cavity numbers**.

The component→domain name join (`component_index+1` → table-76 name) establishes
a naming correspondence. The Camry
`0x6D/0x29/0x32` membership is independently pinned by repo evidence.

## 5. Boundaries

- Install-set ids, architectures, and topology shapes are **facts of the
  pinned 2026.03.002 GTS+ masters**. They describe Toyota's diagnostic data
  model.
- Per-vehicle conclusions still require the vehicle's own master row; model
  families span multiple vehicle types (e.g. three NA Camry HV types).
- The address join is v18-derived. Cross-generation stability is established
  only for the observed addresses.
- Placeholder vehicle types (TEST/MAC/ZZZ4_P5C) carry real install sets but no
  topology; keep them out of production-fleet denominators.
