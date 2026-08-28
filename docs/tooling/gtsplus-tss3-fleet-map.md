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
> **Verification:** `tests/verify_gtsplus_tss3_crossvehicle_surface.py`
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

### Region-local boundaries (facts, not projections)

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

### Category families

| Family | Categories | 498 co-occurrence |
|---|---|---|
| steering_actuation | 142, 405, 499 | 405 near-universal; 499 minority; 142 EU-only |
| brake_domain | 435, 466, 485 | 435 majority; 466 ~half; 485 JP-only |
| front_perception_compute | 430, 498 | 430 only in the ADS/ADeU cluster |
| radar_lateral_periphery | 418, 429 | 418 only in the ADS/ADeU cluster; 429 never |
| pre_498_pcs_compute | 427, 428, 431, 432 | never with 498 |
| adas_supervision_ethernet | 476, 477 | only in the small ADS/ADeU cluster |

Selected-category identities (id, generation, database, name) are **identical
across NA/EU/JP** — asserted by the generator, not assumed.

## 3. Diagnostic request addresses (v18 ECU_Setting_Table join)

Current GTS+ ships no ECUNo→address table; the deterministic join is the v18
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
428/429/430/431/432, 485 EPB carries an ECU_Setting row.** Absence means "no
phase-5 ECU_Setting row in this table", not "no diagnostic address". ADS/ADeU
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
is the generic TSS3 topology pattern, not a Camry quirk.

Worked example (asserted by the verifier): the three NA Camry HV vehicle types
12704/12862/12984 share car id `0x00A7D910`; its shape places FCM `0x6D` on
`Bus 1` (index 29) and Skid `0x29` + EPS `0x32` on `Bus 4` (index 32), both
behind `Central Gateway`.

### Identity namespaces — Toyota vs panda

`bus_index`/`bus_name`/`gateway_names` are **Toyota
`CDbCanBusNameTable`/`CDbCanBusListTable` network-model identities** ("Bus 1",
"Bus 4", "Central Gateway"). They are:

- **not comma panda bus numbers** (panda buses 0/1/2 are harness/controller
  queues — see [panda-toyota-routing.md](panda-toyota-routing.md) for the four
  naming layers), and
- **not connector cavity numbers**.

The component→domain name join (`component_index+1` → table-76 name) is a
naming correspondence, not an ECUNo key join; only the Camry
`0x6D/0x29/0x32` membership is independently pinned by repo evidence.

## 5. Boundaries

- Install-set ids, architectures, and topology shapes are **facts of the
  pinned 2026.03.002 GTS+ masters**; they describe Toyota's diagnostic data
  model, not necessarily production wiring.
- Per-vehicle conclusions still require the vehicle's own master row; model
  families span multiple vehicle types (e.g. three NA Camry HV types).
- The address join is v18-derived; treat per-address stability across
  generations as observed, not guaranteed.
- Placeholder vehicle types (TEST/MAC/ZZZ4_P5C) carry real install sets but no
  topology; keep them out of production-fleet denominators.
