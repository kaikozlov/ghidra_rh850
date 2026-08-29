# Working journal: Camry HV TSS3 lateral funnel (GTS+ → wire)

> **Status:** living session notes, not a canonical claim ledger.
> Started 2026-08-29. Append as the investigation continues.
>
> **This document is falsifiable working memory.** Firmware bytes, Ghidra
> CLI, live logs, and `tools/gts` against the current GTS+ corpus are the
> evidence. Do not cite this file as proof.
>
> **Canonical current-state homes:**
> [camry-2026-live-baseline.md](../../variants/camry-2026-live-baseline.md)
> §§19–20, 30–33, 38–43;
> [camry-2026-tss3-opendbc-port.md](../../variants/camry-2026-tss3-opendbc-port.md);
> [OQ-054](../../status/OPEN_QUESTIONS.md);
> [gtsplus-tss3-fleet-map.md](../../tooling/gtsplus-tss3-fleet-map.md);
> [pcs-data-viewer-tss3-dictionary.md](../../tooling/pcs-data-viewer-tss3-dictionary.md).



## 0. Why this journal exists

The 2026 Camry Hybrid (`8965F3307000` / `8A3113303100`) still does not steer
under openpilot. Factory LTA does steer, and it does **not** use protected
`0x0B6` in the retained request-state intervals. The remaining split is:

1. who physically transmits Bus-4 `0x08A`, how the FRC-hosted request crosses
   the private middle, and where its CMAC is computed;
2. whether hop 2 **granted** during retained ID11 (`5265` active steering,
   `5285`/`57DE` winner vs `5282` request).

Do not treat `D0218` as a copy of the request. Do not treat ID11 alone as a
grant, or the middle as an unlisted EPS CAN ID.

This session’s method: stop treating GTS+ as “no CAN DBC, therefore unhelpful.”
Treat it the way Toyota SWEs use it: a **selector** from shared architecture
down to this model/year/option package, then walk OEM names back onto this
car’s buses and this F33’s implemented subset.

Goal of the session: fill that funnel far enough that the next firmware/log
join is forced, not guessed.

## 1. Corrections this session must not re-introduce


| Wrong                                                 | Accurate                                                                                                                                                                  |
| ----------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| “GTS+ does not contain a CAN DBC.”                    | GTS+ **is** the OEM signal dictionary. It is keyed by **UDS DID / FFD recorder ID**, not by vehicle CAN arbitration ID. It cannot by itself emit `BO_ 138` / `BO_ 182`.   |
| Family `.ddb` = this Camry.                           | `EMPS_P5.ddb` is the **generation-20 EMPS catalog**. Runtime `GetSupportP5` / `GetSupportMultiP5` intersects that catalog with **this ECU’s** supported DID list.         |
| Stock LTA uses `0x0B6`.                               | Retained drives contain **73.3 s / 237k frames** of ID11 LTA/LCA **request state** with zero B6. Request state alone is not a winner/grant oracle. |
| `0x08A` is a native Bus-1 camera frame.               | Every retained `0x08A` is on captured **Bus 4** and absent from Bus 1. The physical transmitter, private transport, and signer remain open; Bus-1 trailer absence does not identify FRC crypto capability. |
| `0x08A → B6` is how stock LTA works.                  | **CORR-135 / OQ-054.** Matching milliradian scale plus exact F33 excluding `0x08A` as Rx does **not** prove a transform. B6 is a separate candidate ingress. |
| P6 ADCU DIDs are on this car.                         | Camry HV **12984** moved **powertrain** to gen-22 P6. ADAS/chassis on 12704/12862/**12984** stays **gen-20 P5 FRC/EMPS**. Use P6 as a vocabulary oracle only. |
| Treating `D0218` as the LTA request input.            | `D0218` default-bank terms are conventional EPS assist (driver torque × speed-sensitive maps, return, dither), not the published milliradian. Retained ID11 proves request state, not winner/grant. |
| The middle is a mystery CAN ID EPS must be receiving. | Recovered PCS dictionary: request `5282`/`5631` vs winner `5285`/`57DE` vs grant `5265` vs EPS-copy `1B40_3`. `0x08A` is truncated **request**, not the winner.           |


Production output remains `SafetyModel.noOutput` / zero CAN. Former B6
development sender stays removed (`opendbc@b9e86924`, `kai-openpilot@abf3ca70a`).
This journal does not authorize steering output.

## 2. How Toyota funnels knowledge (the SWE model)

```
region (NA)
  vehicle type (12704 / 12862 / 12984 = "Camry HV")
    install sets (option packages — not one blob)
      ECU category + generation   (405 EMPS gen20, 498 FRC gen20, …)
        shared family .ddb        (EMPS_P5.ddb is every EMPS_P5 car)
          functions + plugins     (Data List, DTC, RoB, TSS3 FFD, …)
            runtime GetSupport    (this ECU’s supported DID list)
              live DID / FFD bytes
```

Arbitration IDs are **not** a column in that tree. Diagnostic addresses
(`7A1` / `792` / `7B0`) come from the v18 `ECU_Setting` join. Application CAN
packing is recovered by joining a **family name** to **this car’s firmware +
bus + logs**.

Toyota’s specialization order:

1. Vehicle type (model/year) → install sets (which ECU *families* are present).
2. Category → generation + shared `.ddb` (family **superset**).
3. Category functions (Data List `0x1E`, DTC `0x2`, Active Test `0x3`,
  Utility `0xA`, RoB `0x1D`; FRC also `0x2A`).
4. Plugins by role. FRC TSS3-only leaves:
  `0xE9 GetTSS3ImageFFDP5_DT.dll`, `0xEA GetTSS3OperationFFDP5_DT.dll`.
5. Runtime `GetSupportP5` (role `0x67`) + `GetSupportMultiP5` (`0xD5`) hide
  family rows this ECU does not implement.
6. CAN Bus Check topology is a **separate** master-table join (component →
  Toyota bus → Central Gateway). Same topology key for all three Camry HV
   types: `0x00A7D910`.
7. Diagnostic addressing is yet another join (v18 `ECU_Setting_Table`).

That is why “search EMPS_P5 for Target Lateral ID” is necessary but
insufficient: it stops at layer 2.

## 3. This Camry at the vehicle-type layer

Three NA “Camry HV” types. All three keep the **same gen-20 ADAS/chassis
cluster**. They are not the same car above that:


| Vehicle type | Powertrain install set                | ADAS/chassis set                   | Body/gateway set                               |
| ------------ | ------------------------------------- | ---------------------------------- | ---------------------------------------------- |
| **12704**    | gen20 Engine/MG/HV/Battery (`0x1FB7`) | `0x1FB8`                           | `0x1FB9` (Central GW, radar, meter, airbag, …) |
| **12862**    | same gen20 powertrain                 | `0x2192` identical ADAS membership | same pattern                                   |
| **12984**    | **gen22 P6** Engine/HV/MG/Battery     | `0x2300` still gen20 FRC/EMPS      | body + P6 navi                                 |


This car’s EPS F181 `8965F3307000` is gen-20 EMPS → 12704/12862 ADAS world
even if a sibling Camry HV already moved powertrain to P6.

12704 also has empty placeholder install set `0x6C3A`. Ignore it.

Fleet-map row for the 498-carrying set:

```text
NA,12704,Camry HV,8120,0x1FB8,EMPS+ABS+BRKBST+FRC,405 435 466 498
```

Architecture label `EMPS+ABS+BRKBST+FRC` is the **dominant NA TSS3 shape**
(117 NA install rows). This Camry is not a special snowflake at that grain.

### 3.1 ADAS/chassis set `0x1FB8`


| Cat     | Database          | Role on this car                                                                      |
| ------- | ----------------- | ------------------------------------------------------------------------------------- |
| **498** | `FRC_P5`          | TSS3 perception/compute. Unique plugins `GetTSS3OperationFFDP5` / `GetTSS3ImageFFDP5` |
| **405** | `EMPS_P5`         | steering actuator                                                                     |
| **435** | `ABS_P5`          | skid / Brake-EPB                                                                      |
| **466** | `Brk_Bst_P5`      | brake booster                                                                         |
| **445** | `StrAngleSnsr_P5` | steering angle sensor / spiral cable                                                  |
| 452     | TPM               | tires                                                                                 |
| 470     | CMCCM             | surround cameras                                                                      |
| 492     | DMC               | driver monitor                                                                        |
| 5005    | RC_P5             | rear camera                                                                           |




### 3.2 Body/gateway set `0x1FB9` (selected)

Central Gateway, Front Radar (`Fr_RadSen` cat 429), BSM, meter, IPA, SRS,
Main Body, A/C, SMART, navi, front side radars. Radar is colocated with the
**camera domain**, not with EPS.

Pre-498 P5 compute (`PCS1` 427, `DSSystem` 428, `RoadSign` 431, `PCS2` 432)
has **zero co-occurrence** with category 498 in current install sets. Do not
transfer those DIDs onto this TSS3 car as if they were on-wire here.

### 3.3 CAN Bus Check topology (car id `0x00A7D910`)

Toyota `Bus N` is a **Central-Gateway network identity**, not a Panda bus
number.


| Toyota bus | Behind          | Members that matter for lateral                                                |
| ---------- | --------------- | ------------------------------------------------------------------------------ |
| **Bus 1**  | Central Gateway | FCM `0x6D` (FRC)                                                               |
| **Bus 4**  | Central Gateway | Skid `0x29`, EPS `0x32` (**via EBU**), SAS/spiral `0xF0`, Brake Booster `0x28` |


Brake-family Data List names wheel-speed/G/yaw replicas “**(EBU node)**”. Read EPS-via-EBU as: the steering actuator hangs off the chassis/brake stub of Bus 4, not as a third mystery ECU.

Live-corroborated diagnostic addresses: EPS `0x7A1`, FRC `0x792`, Brake `0x7B0`.

**Topology implication for** `0x08A`**:** it is observed on **Bus 4** (EPS/Brake/SAS
domain). FRC is on **Bus 1**. So `0x08A` is not “the camera’s native-bus
frame.” Either CGW republishes a camera request onto Bus 4, or a Bus-4 ECU
produces it. GTS+ topology **forces that split**; it still does not name the
producer.

## 4. Family dictionary vs this F33 (GetSupport)

`EMPS_P5.ddb` Data List still has DID `0x1CEE` Target Lateral ID. Exact F33’s
241-entry RDBI table does **not** implement it.

That is the intended GTS+ behavior: role `0x67` `GetSupportP5` / role `0xD5`
`GetSupportMultiP5` ask the connected ECU which DIDs it implements, then hide
the rest. Tracing “GTS+ name → this car” **always** needs that intersection
(firmware RDBI or a live support list).

What F33 *does* implement as cooperative ingress: protected `0x0B6`.
GTS+ names B6 loss **U012987 Lost Communication with Brake System Control
Module**. Family-level claim: EPS expects that request from the **brake
domain**, not from FRC.

Exact F33 protected Rx: `0x00F`**,** `0x0D7`**,** `0x0B6` **only**. Generated COM Tx:
`0x030 / 0x351 / 0x394 / 0x4A3 / 0x4C8`. It does **not** accept `0x08A` as
normal Rx.

## 5. OEM lateral contract (GTS+ leaves)

Toyota’s TSS3 lateral **request object** is one four-field schema. It appears
in TSS request `5282`, LDA `5531`, and LTA `5631` with the same recorder
layout (PCS Data Viewer / Operation FFD):


| Field                   | Recorder layout     | Scale                     |
| ----------------------- | ------------------- | ------------------------- |
| Target / TSS lateral ID | byte 1, 8-bit       | physical range **0–63**   |
| Pinion angle request    | bytes 2–3, signed16 | LSB `0.001`               |
| Steering assist gain    | byte 4, u8          | LSB `0.01` (`100` = 1.00) |
| Damping control gain    | byte 5, u8          | LSB `0.01`                |


GTS+ Target Lateral ID physical range is `[0, 63]`, so 6-bit CAN packing is
**dictionary-backed**, not an encoding guess. (OQ-054 still notes B21/B26
upper two bits are zero in all retained `0x08A` copies; the diagnostic field
is 8-bit.)

### 5.1 Which leaf owns which name


| GTS+ leaf                          | OEM name                                                                                                                 | What it is                                            | This Camry wire / F33                                                   |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------- | ----------------------------------------------------------------------- |
| FRC Data List `0x1601`             | LTA Switch (`0=OFF/1=ON`); LTA Control (`0=Enabled/1=Disabled`); Hands-Off customize + control                           | switch + enabled/disabled                             | FRC DID, not a CAN PDU                                                  |
| FRC Data List `0x1202`             | LTA/LCA/LDA installation bits                                                                                            | option presence                                       | FRC DID                                                                 |
| FRC Data List `0x1308`             | Steering Wheel Information                                                                                               | `0=Unused 1=Left 2=Right 3=Default`                   | LCA side cue; not pinion                                                |
| FRC Data List `0x1914`             | ACC Control in Operation Flag                                                                                            | cruise operating                                      | FRC DID                                                                 |
| FRC FFD `5282`/`5631`              | 4-field lateral request                                                                                                  | **the request contract**                              | FRC RAM; **not** on sniffed Bus-1 CAN (VAR-094); published on Bus 4 as `0x08A` |
| FRC `0x1B03`..`0x1B07`             | ISA / longitudinal request IDs                                                                                           | **longitudinal**, not lateral                         | paired with brake `0x10A1`..`0x10A4`                                    |
| SAS `0x1004`                       | 12-bit angle 1.5 deg + 4-bit 0.1 deg fraction                                                                            | measured angle                                        | CAN `0x025`                                                             |
| EMPS family `0x1CEE`               | Target Lateral ID + cooperative flag + target angle 1.5 deg/count                                                        | family observer                                       | **absent from exact F33 RDBI**                                          |
| EMPS family `0x1C02`               | command torque                                                                                                           | family                                                | this calibration is a subset — confirm before using                     |
| EMPS U012987                       | Lost Communication with Brake System Control Module                                                                      | B6 missing                                            | `0x0B6` (absent in stock LTA)                                           |
| ABS/BrkBst `0x107E` / RoB `0x507E` | ADS Control EPS Pinion Angle2                                                                                            | observer, 0.00025 rad/count                           | brake diagnostic; weak/negative join for stock LTA command              |
| ABS/BrkBst `0x10A1`..`0x10A4`      | TSS upper/lower accel request                                                                                            | longitudinal sink                                     | not the pinion command                                                  |
| FFD `5285` / `57DE`                | Arbitration result lateral ID / pinion angle                                                                             | **winner after arbitration**, same 0.001 pinion scale | not yet joined to a Bus-4 PDU                                           |
| gen-22 `ADCU_P6` `0x1E19`          | Lateral Control Request Pinion Angle (**deg**, LSB 0.001) **and** Pinion Angle Of Arbitrated Result (**rad**, LSB 0.001) | successor names the request/result split in one DID   | **not an ECU on 12704’s ADAS set**                                      |
| gen-22 `ADCU_P6` `0x1ED3`          | Lateral Control ID of Arbitrated Result                                                                                  | winner ID                                             | vocabulary oracle only                                                  |
| gen-22 `ADCU_P6` `0x1EC2`          | PDA-SA request ID + guide angle + system gain `[0,100]` + damping gain `[0,100]`                                         | same four-field contract, PDA-SA flavour              | `18` means “Request” here, **not** EMPS SDG                             |


FRC ordinary Data List has LTA *installation* and *switch/control condition*,
**not** the four-field pinion command. That contract lives in **TSS3 Operation
FFD**, not ordinary SID-22.

Brake ordinary RoB has **no** named TSS request/arbitration-result field that
closes producer/executor. The specialized FRC-hosted PCS Operation FFD remains
the only current P5 host surface that explicitly names request and arbitration
results (see `tss3_control_ownership_surface.json`).

## 6. Wire mapping already recovered on this Camry



### 6.1 `0x08A` `TSS3_LATERAL_REQUEST` — observe only

Bus 4, 32 bytes, 44,613 deduped frames. EPS does **not** receive it.


| Field                   | Bytes            | Live behavior                                                                            |
| ----------------------- | ---------------- | ---------------------------------------------------------------------------------------- |
| `TARGET_LATERAL_ID`     | B21              | logs exactly `{0, 11, 18}`                                                               |
| `LATERAL_REQUEST_ANGLE` | B18:B19 signed16 | scale `1024/17870` deg/count (~1 mrad); tracks `0x025` in manual; leads angle under ID11 |
| `LATERAL_REQUEST_LEVEL` | B24              | `100` every LTA/LCA frame, `50` every SDG — matches assist-gain 0.01 shape               |
| cruise latch            | B3[3]            | `0x08` when cruise latched                                                               |
| set speed               | B10              | set-speed byte                                                                           |
| trailer                 | B28–B31          | strong ordinary-P5 `FV4 || MAC28` structural match; key/profile unknown                  |


Damping gain is **not** on `0x08A`.

Target Lateral ID dictionary (EMPS family, 19 values): `0` manual, `11` LTA/LCA,
`18` SDG, … Full `VAL_` is already in `toyota_tss3_pt.dbc`.

### 6.2 `0x0B6` `TSS3_LATERAL_CONTROL` — EPS ingress / possible OP send path

Never seen in stock LTA on this car.

- sig 261 B3[5:0] Target Lateral ID; **11** = LTA/LCA mode 2
- sig 262 B4:B5 signed16, same milliradian scale, clamp ±1745 raw (~±100°)
- sig 269/270 B8/B9 `/100` contribution terms (numeric cousins of assist/damping;
**order not live-proven**)
- sequence mod 64, ≤78 raw/gap, 5 ms, 35 ms timeout
- needs valid SecOC (ICU-S slot 4)



### 6.3 Other useful state already in DBC

`0x025` angle/rate, `0x030` driver torque, `0x127` P/R/N/D/B, `0x51E` Ready,
`0x0FE` cruise buttons, `0x00F` SecOC sync.

`CarState` now reads Camry cruise from `0x08A` (latch + set speed) and
exposes assist gain as `tss3_steering_assist_gain` (`B24/100`). Still
`dashcamOnly` / `noOutput`. Do **not** rename B6 `CONTRIBUTION_PCT_*` to OEM
gain names without a live B6 frame.

### 6.4 Two EPS command paths (corrected)

Both write the same funnel (`CC50/CC62 → motor`). They are not two LTA strategies.

**Path A — cooperative LTA (**`0x0B6`**).** Chassis-supervisor pattern: FRC computes the
request → Brake arbitrates/signs → EPS tracks target vs `0x025`. GTS+ names B6 loss
U012987 (Brake). This is “LTA actually enabled” at the actuator. **Not observed** in
the retained drives.

**Path B — conventional EPS assist (**`D0218`**).** Driver torque × speed-sensitive maps,
return-to-center, dither. Context is vehicle speed / driver torque, not lane. The
eight B6-inactive terms have **no recovered lane-target**. This is parking-lot “mouse
acceleration,” always available.

The 73 s of `0x08A` B21=11 with zero B6 is **FRC requesting LTA**, not Path A running
and not Path B becoming lane-aware. VAR-072 already refused to call the Class-L motor
floor “LTA authority.”

## 7. What GTS+ physically contains (and what it does not)

GTS+ install has **no** `.dbc` / `.arxml`.


| Surface                           | What it actually is                                         |
| --------------------------------- | ----------------------------------------------------------- |
| `A_B_CAN_P5.ddb`                  | **SRS Airbag**, not a vehicle CAN map                       |
| `CDbCustSignList` / `CDbCustItem` | body customize menus                                        |
| `CDbCommInfoCanTable`             | **diagnostic** addressing / comm sets, not application PDUs |
| CAN Bus Check tables              | component → Toyota bus → gateway **topology**               |
| Family `.ddb` Data List           | UDS DID names, scales, dictionaries                         |
| Operation/Image FFD plugins       | recorder IDs (`5282`, `5631`, …) and field layouts          |
| v18 `ECU_Setting_Table`           | diagnostic request IDs (`0x7xx`)                            |


That last row is why “GTS+ has no DBC” was too shallow: Toyota stored the
signal dictionary in the **diagnostic/recorder** domain and the **network
placement** in CAN Bus Check. Application arbitration IDs are a third join,
done in ECU firmware and (for us) in logs + COM tables.

## 8. Successor generation as a naming oracle

Gen-22 `ADCU_P6` collapses the distributed P5 stack into one ADAS domain
controller and names `Lateral Control Request Pinion Angle` / `Lateral Control ID of Arbitrated Result` directly.

Camry 12984 moved **powertrain** to P6; ADAS on all three Camry HV types is
still `FRC_P5`. Use P6 for vocabulary, not as this car’s producer.

Pre-498 high-end stack (`PCS1+DSSystem+Fr_RadSen+RoadSign+PCS2`) is LS500 /
LS500h / MIRAI only in NA. Do not mix it into TSS3 FRC ownership.

## 9. Openpilot / opendbc current state (this session’s snapshot)

- DBC: `opendbc_repo/opendbc/dbc/generator/toyota/toyota_tss3_pt.dbc`
already has full `0x08A` census + B6 receiver layout + Target Lateral ID `VAL_`.
- Helpers: `opendbc_repo/opendbc/car/toyota/tss3.py`
- `TOYOTA_CAMRY_TSS3` is dashcam / `noOutput`.
- Controller may compute a **shadow** B6 application but does not send
(except research `ephemeral_secoc_bridge`, which is not the path).
- Camry `CarState` reads `0x08A` cruise latch + set speed and assist gain.
  Still `dashcamOnly` / `noOutput`. Corolla TSS3 cruise stays unpromoted.

Forks:

- openpilot: `/Users/kai/dev/inspect/repos/kai-openpilot/`
- opendbc: `/Users/kai/dev/inspect/repos/kai-openpilot/opendbc_repo/`
- this analysis repo: `/Users/kai/dev/inspect/repos/ghidra_rh850_analysis`

Logs: `targets/camry-2026/raw-20260827/camry_relay_lta_confirm_route_can_20260827.ndjson.gz`
and related captures.

Tools: `tools/gts`, `tools/g` / `tools/gtarget camry-8965F3307000`,
`tools/pseudo`, `tools/know`.

## 10. Forced next joins (do these, in this order)

The funnel is now specific enough that the next work is **not** another
family-dictionary survey. Ranked:

1. **Treat `0x08A` as a Bus-4 publication of the FRC request object, not as
  FRC’s native-bus frame.** Post-repin panda bus 1 is Toyota Bus 1
   (camera/radar, `0x180..0x18C`) and has **zero** `0x08A`. Producer is a
   Bus-4 transmitter (Brake, CGW-as-Bus-4 origin, or another Bus-4 node).
   CentralGW_P5.ddb will not name the PDU — it has no routing DIDs.
2. **Join FFD request vs FFD arbitration vs wire.** `5282`/`5631` = request
  (ID + pinion + assist + damping). `5285`/`57DE` = arbitrated result.
   `0x08A` matches the **request** (ID `{0,11,18}`, angle, assist-shaped B24;
   **no damping**). B6 is a separate cooperative ingress EPS expects from
   Brake. Do not collapse these three into one PDU.
3. `GetSupport` **intersection for this car’s FRC and Brake**, not just EMPS.
  Which FRC Data List / FFD IDs does *this* FRC (`8646F3315000`) actually
   implement? Same for `F152633K0000` Brake/EPB.
4. **F33** `D0218` **authority selector** (firmware, independent of `0x08A`
  producer). Mode/gain/authority state across B21 `0 → 11 → 18`. Do not
   search only for another angle-shaped CAN field. Exact F33 does **not**
   implement `U023A87`, so it is not watching an Image-Processing-Module PDU
   the way Sienna watched `0x2E4`.
5. **Do not** infer `0x08A → B6`. Do not enable output.

---



## Work log



### 2026-08-29 — session start / funnel reconstruction

Documented everything above from the prior chat stretch:

- Rejected “no CAN DBC” as the stopping claim.
- Rejected stopping at shared family dictionaries.
- Reconstructed vehicle type → install sets → gen-20 P5 family DBs →
GetSupport subset → F33/logs.
- Identified `0x1FB8` as the TSS3-relevant Camry HV ADAS package and
`0x00A7D910` as the shared topology key.

Continuation starts immediately below this line.

### 2026-08-29 — funnel walk: category plugins, DTC graph, CGW emptiness, P6 split

Working doc created. Then walked GTS+ as a selector rather than as a DBC.

#### Category plugins on this install set (NA master)

Confirmed by `tools/gts category`:


| Cat        | DB                          | Distinctive plugins / functions                                                                                                                       |
| ---------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| 498 FRC    | `FRC_P5.ddb` gen20          | **only** ECU here with `0xE9 GetTSS3ImageFFDP5` + `0xEA GetTSS3OperationFFDP5`; extra function `0x2A` (string name empty in master). Has Active Test. |
| 405 EMPS   | `EMPS_P5.ddb` gen20         | Data List / DTC / Utility / RoB only. **No Active Test.** GetSupport `0x67`/`0xD5`.                                                                   |
| 445 SAS    | `StrAngleSnsr_P5.ddb` gen20 | Same shape as EMPS (no Active Test).                                                                                                                  |
| 443 CGW    | `CentralGW_P5.ddb` gen20    | Extra function `0x24` (no DLL role binding). CID plugin is `GetCID_SID22_GearShiftControl_DT.dll`.                                                    |
| 435 ABS    | `ABS_P5.ddb` gen20          | Active Test. CID plugin is `GetCID_SID22_SAS_DT.dll` — brake’s identity/support path is SAS-aware. Extra function `0x20`.                             |
| 466 BrkBst | `Brk_Bst_P5.ddb` gen20      | Active Test. Ordinary CID plugin.                                                                                                                     |


Master function names for `0x1E/0x2/0x3/0xA/0x1D/0x2A/0x24` came back **empty strings**. Do not invent UI labels; the plugin roles are the recoverable names.

`tools/gts command FRC_P5 0xEA` binds Operation FFD as `direct_transport` (talks to the ECU). Role `0xE9` Image FFD is `no_recovered_shared_transport_edge` in the current CLI surface table — the plugin still exists; the shared-runtime edge is unrecovered.

#### Central Gateway is not a diagnostic CAN map

`CentralGW_P5.ddb` Data List is ignition, odometer, clock, ethernet-1 status, DTC count. One DTC: `B102004` Central Gateway ECU system internal failure. **No lost-communication DTCs. No steering/lateral/CAN-ID monitors.**

Earlier `tools/gts search --ecu CentralGW_P5` also hit `CentralGW_P5FHI.ddb` (Subaru EyeSight / FHI vocabulary). That is a **different database**. Do not use FHI U-codes as Camry CGW evidence.

Implication: Toyota did not put the Bus-1→Bus-4 PDU republish table in GTS+. CGW firmware (not this diagnostic DB) would own it, if CGW is the hop.

EPS on CAN Bus Check is “Power Steering (EPS) via **EBU**”; Skid/Brake Booster are “via No. 2 Global CAN Junction Connector”; SAS/Airbag via No. 7. EBU is a topology label, not decoded here. FCM `0x6D` sits on Bus 1 with no junction suffix.

#### Lost-communication graph (family dictionaries, then F33 subset)

Family-level (superset — GetSupport/firmware must still intersect):


| Who complains | Code                        | About whom                                                                                               |
| ------------- | --------------------------- | -------------------------------------------------------------------------------------------------------- |
| EMPS          | **U012987**                 | Brake System Control Module — **exact F33 maps B6 loss here**                                            |
| EMPS          | U012687                     | Steering Angle Sensor — **exact F33 also has this code**                                                 |
| EMPS          | U023A87                     | Image Processing Module A — **not in exact F33 generated fault-status U-list**                           |
| EMPS          | U013187 / U110487 / U118487 | Power Steering (self/rear), Driving Support ECU, Advanced Drive — family residue unless F33 events exist |
| FRC           | U013187                     | Power Steering Control Module A                                                                          |
| FRC           | U012987                     | Brake System Control Module A                                                                            |
| FRC           | U012687                     | Steering Angle Sensor                                                                                    |
| FRC           | U023587                     | Front radar (Cruise Control Front Distance Range Sensor)                                                 |
| ABS / BrkBst  | U013187                     | Power Steering                                                                                           |
| ABS / BrkBst  | **U11B187**                 | Power Steering **(ch2)** — second EPS channel in the brake-family dictionary                             |
| ABS           | `0x102F` DID                | `EPS/Steering Control Actuator ECU Communication Open` (`0=Normal 1=Under intermittent`)                 |


Exact F33 configured U-codes in `camry_8965F3307000_fault_status.json` that matter here: **U012987, U012687**, plus software-incompatibility `U0300`* / `U0319*` / `U0328*` / `U1306*`. **No U023A.** Same pattern as Corolla H: Image-Processing-Module camera-PDU monitoring was removed rather than remapped. Do not treat family `U023A87` as proof this EPS listens to a camera frame.

SAS `StrAngleSnsr_P5` search for “Lost Communication” returned **empty**. The angle sensor is a producer of `0x025`, not a rich comm-monitor ECU in GTS+.

#### FRC ordinary Data List still has no pinion command

Confirmed with `tools/gts did`:

- `0x1B03..0x1B07` are **ISA longitudinal** (vertical ID, accel upper limit, speed, brake-hold flags). Pair with brake `0x10A1..0x10A4`. Not lateral.
- `0x1308` Steering Wheel Information is **Left/Right/Unused/Default** — LCA side, not angle.
- `0x1909` Forward Vehicle Lateral Position is perception (meters).
- Zero hits for pinion / “Target Lateral” in `FRC_P5.ddb` Data List.
- `tools/gts search 'Target Lateral' --kind did` hits **only** `EMPS_P5` and `EMPS2_P5` (`0x1CEE` / System-2 `0x1CEF`). This Camry install set `0x1FB8` has **no category 499 EMPS2**.

The four-field request remains FFD-only on FRC (`5282`/`5631`), read by Operation FFD `AB/EB` against diagnostic address `0x792`. FRC **stores** the request object. That does not make FRC the Bus-4 `0x08A` transmitter.

#### P6 ADCU names the request vs arbitration split (oracle)

`ADCU_P6` DID `0x1E19` (same record) contains **both**:

- `Lateral Control Request Pinion Angle` — signed, LSB 0.001, **deg**
- `EDSS Lateral Control Request ID`
- `Pinion Angle Of Arbitrated Result` — signed, LSB 0.001, **rad**

Plus `0x1ED3` `Lateral Control ID of Arbitrated Result`.

That is the same split already in the TSS3 recorder:

- request: `5282` / LDA `5531` / LTA `5631`
- result: `5285` lateral ID, `57DE` pinion angle

P6 PDA-SA DID `0x1EC2` even keeps assist/damping as `System Gain` and `Damping Gain` in `[0, 100]`. Trap: its request-ID dictionary is `0=No Request, 18=Request`, which is **not** the EMPS 19-value Target Lateral ID table (where 18 is SDG).

Unit trap (already seen on P5): request pinion in **deg×0.001** (FFD / P6 request); arbitrated/observer pinion in **rad** (P6 result, ABS `0x107E`).

#### Live `0x08A` sits on the request side of that split


| Object                    | ID              | Angle           | Assist                               | Damping     |
| ------------------------- | --------------- | --------------- | ------------------------------------ | ----------- |
| FFD `5282`/`5631` request | byte1           | bytes2-3, 0.001 | byte4, 0.01                          | byte5, 0.01 |
| FFD `5285`/`57DE` result  | yes             | pinion 0.001    | no                                   | no          |
| Bus-4 `0x08A`             | B21 `{0,11,18}` | B18:B19 ~1 mrad | B24 `100`/`50`                       | **absent**  |
| Protected `0x0B6`         | B3[5:0]         | B4:B5 same mrad | B8/B9 `/100` cousins, order unproven | same        |


`0x08A` is a **truncated request publication** (no damping), on Toyota Bus 4 only. Post-repin panda mapping (live-baseline §19): panda bus 0/2 = Toyota Bus 4 chassis (EPS `0x030`, `0x025`, `0x0D7`, `0x08A`); panda bus 1 = Toyota Bus 1 camera/radar (`0x180..0x18C`) with **zero** `0x08A`.

Producer ranking after this walk:

1. **Bus-4 native transmitter** (Brake/Skid or CGW originating onto Bus 4 with no Bus-1 copy). Topology + capture both allow this.
2. **Transparent ID-preserving CGW republish of a Bus-1 frame** — **disfavoured**: panda bus 1 would then show `0x08A` unless the camera bus capture is incomplete. The 22-ID ADAS-FD family is present there; a missing `0x08A` is a real negative, not an empty bus.
3. **FRC transmitting** `0x08A` **on Bus 1** — **rejected** by the same zero count.

This still does not name the signer. Trailer remains ordinary-P5 `FV4||MAC28` structurally.

EMPS family `0x1CEE` Target Lateral ID dictionary (range `[0,63]`), for wire joins already using `{0,11,18}`:

```
0  No Request (Manual Operation)
1  PCS
4  LDA
10 Hands Off LTA
11 LTA/LCA
13 DESA (Slow Deceleration Control)
15 DESA (Deceleration Stop Control)
18 SDG
19 PDA
25 AP
27 Remote Parking
35/37/39 AD/EM/DES (Lv.3)
41/43/45 AD/EM/DES (Lv.4)
49 Self-Propelled Transport
63 Driver Operation
```



#### Dual-channel residue (do not project onto this car)

EMPS `0x1CEF` is Target Lateral ID **(System 2)**. ABS `U11B187` is Power Steering **(ch2)**. Those belong to dual-steer / EMPS2 architectures. `0x1FB8` does not include category 499. Useful as a reminder that Toyota sometimes runs two cooperative channels; not evidence this F33 has a second B6.

#### Full CAN Bus Check for 12704 (car id `0x00A7D910`)

Seven Toyota buses, all behind Central Gateway. Lateral-relevant:

- **Bus 1:** Front Radar `0x0F`, Front Side Radar Master `0x10`, BSM `0x41`, IPA `0x67`, Rear Camera `0x68`, **FCM** `0x6D`, CMCCM `0x7B`
- **Bus 4:** Brake Booster `0x28`, Skid `0x29`, **EPS** `0x32`, Airbag `0x47`, **SAS** `0xF0`
- Bus 2 = HV powertrain; Bus 3 = meter/navi/DCM; Bus 5 = body; Bus 6 = TPM/AVAS; Bus 7 = remote start

Radar is on the **camera bus**, not the EPS bus. Longitudinal TSS request FRC→Brake already has to cross CGW; lateral request FRC→Bus 4 has to do the same.

#### What this walk closed vs what it did not

Closed (working-level, still not FINDINGS.md until tests exist):

- Family `.ddb` ≠ this ECU; F33 does not implement `U023A` or DID `0x1CEE`.
- CGW GTS+ DB cannot name `0x08A`.
- FRC Data List cannot name the pinion command; Operation FFD can.
- P6/FFD both distinguish **request** vs **arbitrated result**; `0x08A` looks like request; B6 is a different cooperative ingress.
- `0x08A` is not on Toyota Bus 1 in the relay-correct capture.

Not closed:

- Who transmits `0x08A` on Bus 4 (Brake vs CGW-origin vs other).
- Who signs it (key/slot).
- Who consumes it besides the logger (HUD/meter/ABS?); EPS does not.
- What selects F33 `D0218` during ID11.
- Whether FFD `5285`/`57DE` has a Bus-4 twin distinct from `0x08A`.

Next probe: look at brake-family Data List / RoB for anything that could be a **published** TSS lateral request (not just `0x107E` observer), and at meter/navi (`0x1FB9`) for a HUD consumer of Target Lateral ID. In parallel, keep the F33 `D0218` snapshot walk independent.

### 2026-08-29 — SID-22 census: request/gains are not on P5 Data List; EBU named; meter is LDA telltales

`tools/gts search` across current NA ECU `.ddb` files:

**Target Lateral ID as a SID-22 DID exists only on EMPS_P5 / EMPS2_P5.** 4WD “Lateral Identification” is coupling hardware, ignore it.

**Pinion as SID-22** on this generation: ABS/BrkBst/EPB `0x107E` ADS observer (rad); EMPS `0x112D` Absolute Angle (Pinion Angle) in rad at 0.25 mrad/count — that’s the **measured** pinion, not the request. The **request** pinion DID is P6 `ADCU_P6 0x1E19` only (plus FFD recorder IDs).

**Steering assist gain / damping gain as SID-22:** no P5 FRC/EMPS/ABS hits. Only `ADCU_P6 0x1EC2` PDA-SA System/Damping Gain, plus meter buzzer “damping” (audio, irrelevant). On gen-20 TSS3 the four-field gains live in **Operation FFD**, not ordinary Data List.

**Brake “lateral” Data List** is accelerometer `Lateral G` / `Lateral G (EBU node)` plus the `0x107E` observer. `0x10A1..0x10A4` remain longitudinal TSS accel request (upper/lower + 6-bit IDs). Brake SID-22 does **not** publish a TSS lateral request. If Brake transmits `0x08A`, GTS+ does not expose that PDU as a DID.

**EBU is a brake-domain node name, not a mystery ECU.** ABS/BrkBst DIDs `0x108D..0x1093` are wheel speed/accel, G, yaw “**(EBU node)**”. CAN Bus Check places EPS “via **EBU**” on Bus 4 next to Skid/Brake Booster. Read that as: EPS hangs off the chassis/brake stub of Bus 4. It does not make EBU the `0x08A` author by itself.

**Meter_P5 (cat 409, gen20, Toyota Bus 3)** is a telltale/installation surface, not a command surface:

- `0x15A1` option bits: LDA/PCS/ICS/Radar Cruise/IPA/RSA With/Without — **no LTA-named bit in the rows dumped**
- `0x2951` live indicators: PCS warning, Radar Cruise, Cruise, SET, **LDA Steering Control Indicator**, left/right LDA indicator/warning
- `0x10A6` `Steering ECU` is **With/Without**, not a missing-message monitor

Meter sits on Bus 3. A HUD consumer of `0x08A` would require CGW Bus-4→Bus-3 republish; GTS+ does not prove that join. LDA-named telltales can still light for LTA (Toyota kept the LDA indicator family). Do not treat meter as the `0x08A` producer.

Negative that matters: after vehicle-type → `0x1FB8`/`0x1FB9` → family DBs, **no gen-20 SID-22 DID on FRC, Brake, CGW, SAS, or Meter is the four-field lateral request.** The request object is FRC Operation FFD + the Bus-4 `0x08A` wire copy. Ordinary Data List will not give another name for it.

Next probe remains producer-side (Brake/CGW firmware or a Bus-4 Tx census against known ECU Tx tables) and F33 `D0218` independently.

### 2026-08-29 — Brake↔EPS as GTS+ names it, then F33 processing (P5 only)

FRC is **Front Recognition Camera 2**, category 498, `FRC_P5.ddb`, generation 20. This car’s ADAS/chassis set is gen-20 P5. P6 ADCU names are oracles only.

#### What GTS+ says Brake and EPS say about each other

Symmetric missing-message + software-incompatibility, **no CAN IDs**:


| Direction                                  | Family DTC / DID                                              | Meaning                                                     |
| ------------------------------------------ | ------------------------------------------------------------- | ----------------------------------------------------------- |
| EPS watches Brake                          | EMPS **U012987** Missing Message                              | Lost Communication with Brake System Control Module         |
| EPS watches Brake                          | EMPS U031857                                                  | Software incompatibility with Brake                         |
| EPS RoB                                    | X2605                                                         | Software Inconsistency with Brake Control Module            |
| Brake watches EPS                          | ABS/BrkBst **U013187** Missing Message                        | Lost Communication with Power Steering Control Module       |
| Brake watches EPS                          | U032057                                                       | Software incompatibility with Power Steering                |
| Brake RoB                                  | X208E                                                         | Power Steering Control Module Malfunction                   |
| Brake watches EPS pinion                   | C159F1C / C159F2A                                             | EPS pinion-angle sensor voltage / stuck                     |
| Brake DID                                  | `0x102F` EPS/Steering Control Actuator ECU Communication Open | `0=Normal 1=Under intermittent`                             |
| Brake DID                                  | `0x107E` ADS Control EPS Pinion Angle2                        | signed24, `25/1`, **rad** — observer, not a command         |
| Brake DID                                  | `0x107F` EPS Motor Angle Zero Point Value                     | rad                                                         |
| EPS DID (this F33 **does** implement)      | `0x106A` Cooperation Control State                            | `0=Cooperation Control`, `1=Other than Cooperation Control` |
| EPS DID (this F33 **does** implement)      | `0x1C02` Command Value Torque                                 | signed16 Nm — diagnostic mirror of the command funnel       |
| EPS DID (family; **not** on this F33 RDBI) | `0x1CEE` Target Lateral ID + coop flag + target angle         | the four-monitor cooperative observer                       |


Exact F33 communication-monitor **row 5** maps protected `0x0B6` **/ PDU44** loss → DTC index 82 → **U012987**. That is the only firmware-positive “Brake → EPS” **command** attribution. GTS+ never writes `BO_ 182`.

ABS `U11B187` Power Steering (ch2) and EMPS System-2 brake DTCs stay family residue; `0x1FB8` has no EMPS2.

EMPS Data List has **no DID whose name is a brake inbound PDU**. Brake Data List has **no DID whose name is a lateral request to EPS**. The bidirectional contract GTS+ will admit is: they monitor each other’s **presence/compat**, Brake **observes** EPS pinion, EPS **raises U012987 if B6 dies**.

#### Messages on this P5 car (firmware + logs, not GTS+ IDs)

Same Toyota Bus 4 (EPS via EBU, Skid `0x29`, Brake Booster `0x28`, SAS `0xF0`):

**Into EPS (accepted generated-COM, selected):**

- SAS `0x025` — measured angle/rate (DID `0x1037` 1.5 deg + 0.1 deg fraction)
- Brake-domain protected `0x0D7` — vehicle speed family (same SecOC slot-4 set as B6)
- `0x00F` — SecOC sync
- `0x0AA` wheels, `0x127` gear, `0x51E` Ready, `0x0FE` cruise buttons, …
- Protected `0x0B6` — cooperative target angle + Target Lateral ID. **Zero frames in stock LTA.**

**Out of EPS (only five generated-COM Tx IDs):** `0x030` (driver torque + motor-feedback proxy), `0x351`, `0x394`, `0x4A3` (angle/torque telemetry), `0x4C8`. Brake `U013187` is “some EPS message disappeared”; the natural candidates are this Tx set, not a GTS+ named ID.

**On Bus 4 but not into EPS:** `0x08A` (FRC-authored request object, truncated). FRC lives on Bus 1.

#### How this F33 turns inputs into steering — CORRECTED

Do not read Path B as “how factory LTA steers.” See the next work-log entry.

**Path A — cooperative (B6).** FRC request, Brake as signer/supervisor, EPS
`target − measured` vs `0x025`. This is LTA actuation.

**Path B —** `D0218`**.** Conventional speed-sensitive EPS assist. Not lane-aware.

The retained drives have Path-A idle (zero B6) while FRC still published ID11
on `0x08A`. That is request without cooperative grant, not proof that Path B
did the lane keeping.

### 2026-08-29 — Path A/B correction (chassis supervisor vs conventional assist)

The previous write-up inferred: LTA identified + B6=0 + `D0218` reaches motor
⇒ `D0218` is the LTA path. That collapses two Toyota functions.

**Path A (LTA actuation):** `FRC → Brake → EPS` via protected `0x0B6`.
Brake is the chassis supervisor allowed to command EPS (VSC/dynamics can
suppress). F33 `CD128` is a tracking loop: B6 target vs SAS `0x025`. Target
Lateral ID 11 selects LTA/LCA supervisor mode2. GTS+ U012987 is this link.
`0x106A=0` would mean EPS is in Cooperation Control.

**Path B (always-on assist):** `D0218` B6-inactive sum is driver-torque maps,
speed maps, return, dither, aggregation. Same idea as speed-sensitive power
steering. Vehicle speed (`0x0D7` SP1) is an input; there is no recovered
lane/camera term. Section 27 already showed the moving-mode/assist family is
**cruise-generic**, not a Class-L discriminator, and its live contribution
was zero when `0x0D5` s213 was zero.

**What the 73 s actually showed:** `0x08A` B21=11 (FRC request + HUD/state
carriers `0x412`/`0x371`) with **zero B6**. That is layer 1 (camera
requesting), not layer 2 (Brake granting cooperative control). Calling it
“factory LTA steered through `D0218`” over-read VAR-081’s request-state
label.

**What §24 still is (do not throw away, do not over-promote):** inside those
ID11 intervals the motor-feedback proxy had a hands-light floor vs
speed-matched cruise, and short opposing-driver runs. VAR-072 already
bounded that as **not proof of LTA authority** — a changed damping/assist
map looks the same, and there was **no** hands-light autonomous sweep.
Compatible with Path B changing feel under cruise/LTA *state*, not with Path
B growing a lane target.

CORR-135 remains right that `0x08A → B6` is not proved. It overstated that
zero-B6 “factory LTA” is therefore Path-B actuation. Working correction:
zero B6 means Path A did not run; it does not mean Path B did the keeping.

Openpilot steering is Path A (valid Brake-signed B6), not Path B. Next live
discriminator: poll `0x106A` when B21=11. Expected under this model: `1`
(other than cooperation) until Brake emits B6.

### 2026-08-29 — missing B6 is not a post-repin panda/pinning miss

Question: the car was clearly doing TSS3 steering; logs have no cooperative
command. Was panda/pinning on the wrong bus?

**No.** The 2026-08-27 drives are the post-repin relay-correct pair. After
the Toyota-B CAN0/CAN1 swap, chassis (EPS/Brake/SAS) sits on the panda
**CAN0/CAN2 relay pair** (logical bus 0 and 2, same ID set, same frame
counts). The 22-ID camera/radar FD family moved to bus 1. That is the
orientation `interface.py` calls “production relay-correct bus-0 placement.”
`TSS3_PT_BUS1` is only set if `0x025/32` and `0x0AA/8` are on bus 1 **and
not** bus 0 — the old unmodified-harness layout. These drives have `0x025`
on bus 0, so CarState also reads bus 0.

On that chassis pair the capture is healthy:

- Brake-domain protected `0x0D7/32` present (thousands/segment)
- SecOC sync `0x00F/8` present
- EPS TX `0x030`, SAS `0x025`, request `0x08A/32` present
- `0x0B6` **at any DLC on any bus: 0 / 3,574,703 frames**

Exact F33 accepts `0x00F`, `0x0D7`, and `0x0B6` on the **same** RSCFD
controller. `0x08A/32` proves 32-byte CAN-FD is logged. If Brake had
transmitted B6 on the EPS bus, it would sit next to `0x0D7`. It did not.

`SafetyModel.noOutput` blocks panda **TX** and sets `disable_forwarding`.
That can isolate camera vs car across the intercept relay; it does not
delete chassis-local Brake→EPS frames. B6 is supposed to be that
chassis-local frame. Isolation is therefore not an explanation for zero B6
while `0x0D7`/`0x030`/`0x08A` remain.

Two different “no steering in the logs” meanings:

1. **Raw CAN (what the census used):** steering *observables* are there
  (angle, driver torque, motor proxy, `0x08A` request). The missing object
   is the Path A **command** (`0x0B6`).
2. **openpilot `CarState`:** Camry now publishes cruise enabled/speed from
   `0x08A`. `steeringTorqueEps` and `steeringPressed` stay forced off.
   ID11 is `tss3_target_lateral_id`, not `cruiseState`.

So: pinning got us onto the right Brake↔EPS wire; panda did not filter B6;
Path A simply did not run in those drives. The felt TSS3 steering is still
the ID11 request + conventional assist / driver, unless a later capture
shows B6.

### 2026-08-29 — operator constraint: the car was self-steering; triage 1/2/3

Operator statement (this session): the car was steering itself, 100%.
Treat that as a constraint, not a vibe. Then zero B6 is one of:

1. **Wrong object** — stock LTA actuation is not `0x0B6`.
2. **Wrong place** — `0x0B6` exists on a net panda never had.
3. **Right object, right place, panda/comma hid or broke it.**

**What the same logs already show that we under-read.** Drive B
hands-light core (`|torque|≤0.5 N·m` **and** `|rate|≤2`) inside Class-L:
n=4292, median `|B22:B23|` **120 vs 20** in speed-matched cruise, r(current,
torque) ≈ 0. The “no autonomous sweep” test required `|rate|≥2` for ≥0.5 s
— that **throws away lane-hold**. Holding with light hands and a 6× current
floor is exactly what LTA looks like on-center. We set the bar wrong.

**3, checked.** `noOutput` sets `disable_forwarding`. Panda only ever
forwards **0↔2**; **bus 1 is never forwarded**. After repin, chassis is 0/2
(identical 153-ID mirrors) and the 22-ID FRC/radar FD family is **bus 1**.
That *can* starve FRC→Brake if that path needed panda. It cannot hide a
frame that was on 0, 1, or 2: B6 is **zero on all three**, next to healthy
`0x0D7/32`. noOutput has no RX ID filter. 3 does not explain missing B6
**in the log**. It *can* explain Brake never emitting B6, if Brake’s enable
input lives on un-forwarded bus 1. Then 3 and 1 collapse: we broke Path A
and watched Path-B-plus-something else.

**2, checked for B6.** F33 has one app CAN controller. It accepts `0x00F`,
`0x0D7`, and `0x0B6` together. Those first two are on bus 0/2 with EPS
`0x030`. A second physical tap into the same controller is not in the
image. Remaining 2 is only “a different ID/encoding we never grepped,” not
“B6 on a bus we weren’t on.”

**1 is the live one if self-steer is real and B6 is really absent.** EPS
applied non-driver current during ID11. No accepted F33 bit flips at the
ID11 edge (§21). No bus1 field leads the motor (§26). `0x08A` is not EPS
Rx. So the actuator moved without the object we named “the command.”

**Experiment that splits 3 from 1:** one more drive, **relay open /
passthrough** (stock FRC–CGW–Brake–EPS electrically whole), hands clearly
off, log `pandaState.safetyModel` + all buses. If B6 appears, 3 was the
bug. If B6 stays zero and the wheel still holds, 1 — stop hunting `0x0B6`
as the stock LTA PDU and find what actually moved `B22:B23` in those 4292
hands-light samples.

### 2026-08-29 — the retained drives already show closed-loop tracking of `0x08A`

The premature stop was the 50 ms “does any CAN field lead the motor”
screen. A tracking loop does not look like that. The plant follows
**error** (`target − measured`), contemporaneously. Raw `0x08A[18]` vs
motor can even *lag*, because B18 is a slow path angle and B22:B23 has
assist transients. Conditioning on the hands-light core (`|torque|≤0.5`,
`|rate|≤2`) and forming that error is the analysis that was missing.

Drive B (the confirm drive; 57 s of ID11, 4292 core samples, matched
cruise control exists):


| stratum                         | n    | med |motor| | r(mot, torque) | r(B18, angle) | r(mot, error)            | sign(mot, error) |
| ------------------------------- | ---- | ----------- | -------------- | ------------- | ------------------------ | ---------------- |
| Class-L hands-light             | 4292 | **120**     | **−0.29**      | **0.49**      | **0.79 OLS / 0.73 mrad** | **95% / 78%**    |
| cruise, same speed, hands-light | 1200 | **20**      | −0.03          | **0.96**      | −0.25 / 0.06             | 14% / 59%        |
| cruise, any hands               | 3376 | 54          | **+0.85**      | 0.98          | ~0                       | ~chance          |


OLS error = `B18 − (a·angle + b)`: the part of the published target
**not** explained by the current wheel. Milliradian error uses the
already-recovered `B18 × 0.001 rad` scale. Same conclusion both ways.

Residual after a torque model fit on cruise (`motor ≈ 138·τ + 0.4`):
Class-L core median |residual| **128**, `r(residual, mrad-error) = 0.74`.
Control core residual does not follow that error (`r = 0.13`).

Error leads motor by **~50 ms** (`r = 0.74` at +50 ms). 43 of 51
one-second core windows move **<0.4 deg** with median |motor| still
200–350: on-center hold against a persistent ~0.26 deg target error,
not a steer sweep. B8:B9 (the duplicated request word previously
dismissed on whole-drive joins) is **dead** vs motor in this stratum
(`r ≈ −0.06`). `0x394`/`0x351`/`0x4C8`/`0x4A3` grow no Class-L-only
payload. `0x0D7` s16 fields do not shift. Bus-1 18x vs residual does
not reproduce (drive A |r|~0.65 on n=352; drive B max 0.35 on n=4292).

Drive A is the dirty one (median driver torque 0.85 N·m, 33 deg of
wheel travel in the “core”). The error join is weaker, as expected
when the driver is also steering. Do not average A and B.

What this is **not**: proof that F33 *receives* `0x08A`. Exact F33
still excludes it. The plant is tracking the **published request**.
Ingress into `D0218`/`CC50` is still unnamed (VAR-084 hidden-ingress
residue / ID11-selected internal path). B6 remains absent and unused
in these drives. EPS TX does not advertise cooperation (`0x394`
unchanged) — consistent with `0x106A` staying “other than cooperation”
if that DID is B6-gated.

Wrong object, more precisely: we hunted a *cooperative PDU into EPS*.
Stock LTA in these logs is EPS current following the Bus-4 request
error with B6 idle. Wrong screen: lead(motor), not corr(motor, error)
inside hands-light. Panda/pinning is not required to explain this
pattern; it is already on bus 0 next to `0x0D7`.

### 2026-08-29 — stop ignoring the recovered PCS Data Viewer

Yesterday's CP recovery (`tools/gts recover-aux-bodies`, commit
`60f16f0` / `b6b7464`) is the other half of this problem. The shipped
`PCS Data Viewer.exe` is a stub; the recovered analysis PE at
`build/out/gts-aux-unprotected/PCS Data Viewer/PCS Data Viewer.exe`
has **22,447/22,447** method bodies. Read it with
`tools/techstream/inspect_dotnet_il.py`. Image-FFD payload decrypt is
`plain = reverse_bits8(cipher) XOR 0xAA` (key `0xAA`, skip when
`622081` status is `01`).

That program is Toyota's TSS3 **control-model / flight-recorder**
software, keyed by recorder DID, not CAN ID. The extractors already
pinned the tables; we were not using them as the model for the
0x08A-tracking result.

FRC-side objects that name the split the CAN logs just showed:


| Recorder        | OEM name                                                         | Why it matters now                                                                                                                     |
| --------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `5282`          | TSS request: lateral ID + pinion `0.001` + assist/damping `0.01` | same four-field shape as `5631` LTA / `5531` LDA. `0x08A` is this **truncated** (ID + angle + level; no damping)                       |
| `5285` / `57DE` | Arbitration result lateral ID / pinion `0.001`                   | the **winner**, distinct from the request. Not yet identified on Bus 4                                                                 |
| `5273` / `5274` | Steering angle / rate **(arbitration)**                          | float observers of the arbitrated plant, not the request                                                                               |
| `5246` / `5247` | Pinion angle / **EPS torque** (+ sensor)                         | FRC's view of the actuator we correlated as `0x030 B22:B23`                                                                            |
| `5265` B14[7]   | **Active steering under-control flag**                           | sits next to ABS/VSC/VDM/MCB under-control bits. This is the FRC-side "is the chassis actually steering" bit, analogue of EPS `0x106A` |
| `5601`          | LTA SW / **LTA Control Status** / hands-off flags                | feature state, not the Bus-4 request latch                                                                                             |
| `560D`          | driver-steer detect, LTA DDR control state, EPS pinion `0.001`   | plant + override inside LTA                                                                                                            |
| `5632`          | Hands-Off State / Hands-Off LTA Continue Request                 | the "car steering itself" condition Toyota named                                                                                       |
| `57A3`          | PCS steering output phase (3 bits)                               | `SupportDID=0` in the current table — PCS-family RoB, not LTA                                                                          |


Host fetch is already closed: `GetTSS3OperationFFDP5` selector `0x66`,
`AB11/12/13 → EB11/12/13` on FRC `0x792`, EB13 = `[DID16][len8][data…]`.
`tools/camry_tss3_request_capture.py` still only SID-22's longitudinal
ISA DIDs. It does not pull this recorder. That is the next live join:
during ID11, read `5282` vs `57DE` vs `5265` vs `5601`/`560D`/`5632`
and sit them next to `0x08A` + `B22:B23`. If `5265` is set and `57DE`
tracks the motor while B6 stays zero, Path A as "B6 actuation" is the
wrong object and the supervisor grant is this arbitration result, not
protected `0x0B6`.

### 2026-08-29 — B24 is 5282 assist gain; 57DE is not on Bus 4; ADU names the missing slots

Kept digging the same logs + recovered PCS dictionary. Native host plugins
still do not know CAN IDs (the `0x8A00` hit in `GetTSS3OperationFFDP5` is
`jnz +0x8A`, not arbitration ID `0x08A`; CommandCommon's `5282`/`57DE`
immediates are code offsets). GTS+ remains DID/FFD-keyed.

**B24 OEM-join (recovered).** TSS3 recorder `5282` / LTA `5631` / LDA `5531`
are the same four-field layout: lateral ID, pinion s16 `0.001`, **steering
assist gain** u8 `0.01`, damping u8 `0.01`. Live `0x08A` B24 is `100` in
every ID11 frame and `50` in every ID18 (SDG) frame. That is gain `1.00` /
`0.50`, not an unnamed percent. ADU resource `2A04_3` names the same slot
**Steering support gain**. Damping (`5282_4` / `5631_4` / `2A04_4`) is
**not on this PDU** (B25 is identically zero). Live-baseline §39 / opendbc
`LATERAL_REQUEST_LEVEL` still say "percent unit bounded, not OEM-joined";
this session's name is the FFD one.

**The two** `0x7FFF` **s16 slots are the unpublished second pinion.** ADU
`1B40` keeps *two* LTA angle requests in one record: `1B40_2` LTA steering
angle request **(ADU)** and `1B40_3` LTA steering angle request **(EPS)**.
`2A04` is the generic ADAS request (ID + pinion + support gain + damping);
`2A06` / `1E19_3` / `57DE` are the **arbitrated result**, a different
object. `0x08A` publishes one live milliradian pinion (B18:B19) and fills
B13:B14 and B16:B17 with the signed16 invalid sentinel. That is the
truncated-request shape: FRC/ADU copy on the wire, EPS-facing copy and
damping not published here. Do not project P6 ADCU as present on this
P5 car; the names are the layout oracle.

ADU `(CAN)` observers that already match Bus-4 packing:


| ADU resource           | OEM name                                        | Bus-4 twin                                   |
| ---------------------- | ----------------------------------------------- | -------------------------------------------- |
| `2E8D_1` / `2E8D_2`    | Steering angle (CAN) + expanded LSB (CAN)       | SAS `0x025` 12-bit ×1.5 deg + 4-bit ×0.1 deg |
| `2E94`                 | EPS torque (CAN)                                | `0x030` driver-torque family                 |
| `2A04_1` / `_2` / `_3` | ADAS lateral ID / pinion request / support gain | `0x08A` B21 / B18:B19 / B24                  |


`57DE` **is not a distinct Bus-4 s16.** Drive B hands-light Class-L core
(n=4292): among bus-0 s16be fields, nothing tracks `0x025` tighter than
the request besides SAS itself. `0x5AE[20]` reaches r≈0.70 and is not a
plant twin (`r` vs `0x025`'s 12-bit word is 0.45). Bus-1 `0x160[10]/[22]`
looks like angle (r≈0.83) because it **is** the already-closed SAS echo
(live-baseline §26, r=+0.9963 delayed). `0x081` B16 vs `0x08A` B18 is
r=0.995 / 74% exact in this core — a low-pass of the **request**, not the
result. B8:B9 is still not `57DE`: ID0 r(B8, angle)=0.08; ID11 r=0.20;
ID18 r=−0.42 and r(B8, B18)=−0.66. ID0 B18 ≈ `17.44·deg` recovers the
milliradian scale when the request is following the wheel; ID11 is the
hold-error case already logged.

`0x0D7` **B1 is not an LTA grant.** F33 COM signal 246 is u16 at B1:B2
(SP1, 0.01 km/h). B1≈27 during ID11 is the high byte of ~70 km/h
(`0x1Bxx`), i.e. the set-speed band, not a mode nibble. Speed-class
gating already closed in the command-cone ingress artifact.

`5601` **/ ADCU** `0x1B10` **LTA Control Status** is `{0..4}` Not
Equipped/OFF/Standby/Active/Fault. That is not `0x08A` B6:B7
`(45,71)`. Those stay the census cruise-substate pair.

**PCS PE caveat.** `build/out/gts-aux-unprotected/PCS Data Viewer/PCS Data Viewer.exe`
matches the aux manifest (`9d7f0f75…`) but that entry has
`phase5c_done: false`. MethodDef RVAs currently point at zeros;
`inspect_dotnet_il` cannot parse ADU cctors from that copy. The tracked
TSS3 JSON was extracted from a recovery that materialized 22,447 bodies.
Re-recovering that EXE (not using the stale aux copy) is required before
ADU `2A04`/`2A06`/`1B40` **byte** layouts can be read the same way as
`5282`. Resource *names* above do not need that PE.

B8:B9 remains unnamed. Whole-drive `|r|≤0.07` vs angle was the wrong
screen (ID0 dominates); the ID-split still does not make it a pinion or
`57DE`. Do not send it as a command.

### 2026-08-29 — ADU bit layouts from a fresh PCS recovery (`phase5c_done: true`)

The committed aux copy of `PCS Data Viewer.exe` is the incomplete
`phase5c_done: false` image (`9d7f0f75…`, MethodDef RVAs land on zeros).
A fresh `tools/gts recover-aux-bodies --only "PCS Data Viewer"` writes
`fc0841df…` with **22,447/22,447** parseable bodies. ADUDetailInfo `.cctor`
is then the same kind of table as TSS3 `DetailBitAssignInfo`. Inner ctor
is `(DataSize, Support, BytePosition, BitPosition, BitLength)`; invalid
sentinels are a list on that object; physical is `(Type, Lsb, Offset)`.

`2A04` **is** `5282` **byte-for-byte** (5-byte ADAS request record):


| field    | byte | type | invalid  | LSB   | OEM name                        |
| -------- | ---- | ---- | -------- | ----- | ------------------------------- |
| `2A04_1` | 1    | u8   |          | 1     | ADAS lateral control request ID |
| `2A04_2` | 2    | s16  | `0x7FFF` | 0.001 | ADAS pinion angle request       |
| `2A04_3` | 4    | u8   | `0xFF`   | 0.01  | Steering support gain           |
| `2A04_4` | 5    | u8   | `0xFF`   | 0.01  | Damping control gain            |


`2A06` is the 3-byte **result**: byte1 u8 ID, byte2 s16 pinion `0.001`
invalid `0x7FFF`. `1620` is the standalone result pinion with the same
sentinel. That is why `0x08A` B13:B14 and B16:B17 sit at `0x7FFF` in
every retained frame: Toyota's unpublished signed16 pinion is that
exact sentinel. B18:B19 is the one **populated** `2A04_2`/`1B40_2`
slot (live milliradian, not `0x7FFF`). Damping `2A04_4` has no twin
on the PDU.

`1B40` **is the 12-byte LTA client record** with the dual angle the
CAN frame only half-publishes:


| field       | byte  | type | invalid  | LSB   | OEM name                                                 |
| ----------- | ----- | ---- | -------- | ----- | -------------------------------------------------------- |
| `_1`        | 1     | u8   |          | 1     | LTA lateral control request ID                           |
| `_2`        | 2     | s16  | `0x7FFF` | 0.001 | LTA steering angle request **(ADU)**                     |
| `_3`        | 4     | s16  | `0x7FFF` | 0.001 | LTA steering angle request **(EPS)**                     |
| `_4`        | 6     | u8   | `0xFF`   | 0.01  | LTA steering assist gain                                 |
| `_5`        | 7     | u8   | `0xFF`   | 0.01  | LTA damping control gain                                 |
| `_6`..`_10` | 8..12 | u8   | `0xFF`   | 1     | indicator2 / VLO / Track / gradual / driver-coordination |


Two milliradian pinions, same invalid, one of them named **(EPS)**.
`0x08A` putting one live pinion + two `0x7FFF` slots is that record
with the EPS copy and the `2A06` result left unpublished. It is not
proof F33 receives either copy.

`2E8D` **/** `2E92` **(CAN observers) are SAS-style, not** `0x08A`**.**
Byte1 s16 LSB **1.5** (Decimal 15 scale 1) + byte3 s8 LSB 0.1, invalid
`0x7FFF` / `0x7F`. That is the `0x025` / `0x4A3` 1.5-deg family, not
the milliradian request. `2E94` EPS torque (CAN) is s16 LSB 0.01.

`1E19` **in this ADU FFD table is float32**, not the SID-22 s16
0.001-deg/rad view: `_1` byte1 f32 request pinion invalid
`0xFFFFFFFF`, `_2` byte5 u8 EDSS ID, `_3` byte6 f32 arbitrated
pinion. Do not pack `0x08A` as `1E19`.

P6 ADCU is still not on this car. These layouts are the dictionary
for the truncated Bus-4 publication, not a claim that F33 implements
`1B40`.

### 2026-08-29 — B8:B9 is the cruise speed-error term, not a second pinion

The whole-drive `|r|≤0.07` vs angle was right for the wrong reason: B8
is **not lateral**. Whenever cruise is latched (`B3=8`, `B10` = set
speed), B8 tracks `(B10 − 0x0AA km/h)`:


| stratum (drive)          | n    | r(B8, set−v) | slope (counts per km/h) | MAE   |
| ------------------------ | ---- | ------------ | ----------------------- | ----- |
| ID11 LTA, B              | 2288 | **+0.995**   | 130.8                   | 12.0  |
| ID0 cruise-on LTA-off, A | 1188 | **+0.991**   | 121.7                   | 10.1  |
| ID0 cruise-on LTA-off, B | 2238 | +0.801       | 23.3                    | 113.6 |
| ID11 LTA, A (dirty)      | 646  | +0.861       | 116.4                   | 32.4  |


Drive A cruise-on with **B21=0** is the split: LTA is off and B8 still
follows set-speed error at 0.991. It is a longitudinal sidecar on the
same PDU as the lateral request. B11:B12 remains the 100% byte-identical
duplicate. Intercept is not zero (+28..+83), slope sits near **128
counts/km/h**, so this is bounded as a Q7-ish speed-error / ACC P-term,
not OEM-joined. `5281` "TSS request acceleration (upper limit)" is s16
`0.001` and is collinear with a P-on-speed-error during a hold; do not
promote that identity yet.

That also explains ID18 (cruise off, B10=0): B8 is not a speed-error
against a setpoint, so the angle anti-correlation was a red herring.

`0x081` is **not** a byte clone of `0x08A`. Same-offset equality is only
the leading zeros. During ID11 it carries a filtered copy of B8 at
offsets 4 and 18 (r=0.999, 7% exact) and of B18 at offset 16 (r=0.994,
70% exact). Previously recovered B13↔B21 mirror stands; constants
(B21/B24/B6/B7) have no Pearson.

`0x08A` is therefore a **combined TSS chassis publication**: cruise latch

- set speed + speed-error (longitudinal half of `5280`/`5281`) plus
lateral ID / milliradian pinion / assist gain (truncated `5282`), with
the EPS pinion copy and damping left at `0x7FFF` / omitted. FRC records
those as separate DIDs; someone on Bus 4 packed them into one 32-byte
SecOC frame. Exact F33 still does not accept that frame. B8 cannot be
the D0218 ingress — F33 already has `0x0D7` SP1 for speed.



### 2026-08-29 — arbitration middle is named, not spooky

Stop collapsing `eyes → EPS`. Toyota already named the box in the recovered
PCS Operation-FFD dictionary
(`data/generated/gtsplus_2026/pcs_data_viewer_tss3_managed_semantics.json`,
PE `fc0841df…`, 1,130 `DetailBitAssignInfo` rows / 623 recorder DIDs). GTS+
is keyed by recorder ID, not `BO_`. This section is that object model joined
to this car’s buses. It does **not** name the CPU that runs the mux and does
**not** authorize output.

#### The pipeline (four objects, not one frame)

```
clients (same 4-field contract)
    → mux / arbitration
        → winner (ID + pinion only)
            → chassis grant (under-control bits)
                → EPS tracks granted pinion vs SAS 0x025
```

**1. Clients / request (eyes).** Identical geometry
`u8 ID + s16 pinion 0.001 + u8 assist 0.01 + u8 damping 0.01`
except PDA-OAA, which splits across three DIDs and packs ID as **6 bits**:


| Client         | Recorder                                         | Notes                                                  |
| -------------- | ------------------------------------------------ | ------------------------------------------------------ |
| generic TSS    | `5282`                                           | the canonical 5-byte request                           |
| LDA            | `5531`                                           | byte-identical to `5282`                               |
| LTA            | `5631`                                           | byte-identical to `5282`                               |
| PDA (OAA)      | `5A09` ID (6-bit) / `5A0A` pinion / `5A0D` gains | same ingredients, split DIDs                           |
| PDA (SA) / SDG | `5D81` status; RoB `SystemType=6` = SDG          | live wire ID **18**; not a 4-field tuple here          |
| PCS            | `57A3` steering output **phase** (3 bits)        | not the 4-field tuple; `SupportDID=0`                  |
| LCA            | `5202` presence bit only                         | **no** dedicated request tuple in this 1,130-row table |


ADU P6 oracle (not on this car): `2A04` **is** `5282` byte-for-byte, invalid
pinion `0x7FFF`. `1B40` is the 12-byte LTA client with **two** pinions:
`(ADU)` and `(EPS)`, same `0x7FFF` sentinel, then assist / damping /
indicator2 / VLO / Track / gradual / driver-coordination.

EMPS family Target Lateral ID (range `[0,63]`, already in `toyota_tss3_pt.dbc`):
`0` manual, `1` PCS, `4` LDA, `10` Hands Off LTA, `11` LTA/LCA, `18` SDG,
`19` PDA, `49` Self-Propelled Transport, `63` driver. Live `0x08A` B21 is
exactly `{0, 11, 18}`.

**2. Winner / arbitration result (the middle).** Different record. No assist,
no damping:


| Axis         | Winner ID | Winner value              | Valid flag                        |
| ------------ | --------- | ------------------------- | --------------------------------- |
| lateral      | `5285`    | `57DE` pinion s16 `0.001` | *(no lateral twin in this table)* |
| longitudinal | `5284`    | `57DB` accel s16 `0.001`  | `57D3` (`SupportDID=1`)           |


ADU P6 names the same split: `2A06` / `1620` = result pinion, invalid
`0x7FFF`. `1E19_3` is the float32 **arbitrated** pinion; do not pack `0x08A`
as `1E19`.

**3. Chassis grant.** `5265` is a packed under-control word, `SupportDID=1`
on every bit (host always considers these). Byte positions 2,4,6,8,10,12,14
bit 7:


| Field | OEM name                                   |
| ----- | ------------------------------------------ |
| `_1`  | ABS under-control                          |
| `_2`  | VSC under-control                          |
| `_3`  | Throttle TRC request / TRC brake operation |
| `_4`  | VDM under-control                          |
| `_5`  | MCB under-control                          |
| `_6`  | TSC operating                              |
| `_7`  | **Active steering under-control flag**     |


If `_7` is clear, ID 11 on the request is eyes without chassis grant.
`560D` is the LTA-side plant view sitting on the far side of that grant:
driver-steer detect / prohibited, DDR state, **EPS pinion** `0.001`,
following flags. `5632` is hands-off continue / DESA / TD reasons.
`5601` is LTA SW / **LTA Control Status** / hands-off customize+judgment
— feature state, not the Bus-4 request latch.

**4. Feature presence (what this FRC even has).** `5202`, all
`SupportDID=1`: PCS, FCTA, Radar Cruise, Cruise, **LDA, LTA, LCA**, AHB,
RSA, TMN, **PDA**, Speed Limiter, DESA. LCA is installed as a bit and
still has no dedicated request tuple; it rides the LTA ID `11` on the
wire (`B21=11` = LTA/LCA in the EMPS dictionary).

#### Longitudinal twin (no Brake firmware required)

GTS+ already shows the same mux on accel. That is the architecture proof.


| Hop                    | Longitudinal (named on Brake SID-22)                | Lateral (Brake SID-22 silent)                                |
| ---------------------- | --------------------------------------------------- | ------------------------------------------------------------ |
| FRC request            | `5280` lower / `5281` upper                         | `5282` / LTA `5631`                                          |
| Chassis Data List sink | ABS `0x10A1..0x10A4` **“from Toyota Safety Sense”** | **none** (RoB `0x507E` is an observer pinion, not a request) |
| Winner ID / value      | `5284` / `57DB`                                     | `5285` / `57DE`                                              |
| Grant                  | `5265` ABS/VSC/…                                    | `5265` active steering                                       |
| Recorder host          | FRC category 498, `0x792`                           | same                                                         |


`tss3_control_ownership_surface.json`: ordinary P5 FRC/Brake RoB has **zero**
named TSS lateral request or arbitration-result fields. The specialized
FRC-hosted Operation FFD is the only current P5 host surface that names
both. Brake is the named **long** sink, not a named **lat** SID-22 sink.

#### What is on this car’s Bus 4 vs unpublished vs FFD-only

Joined to the two relay-correct drives (3.57M frames, chassis on panda 0/2):


| Object                            | Where it lives on this Camry                                                                                 |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `5282` ID + pinion + assist       | **Not** on sniffed Bus-1 CAN (VAR-094). Bus 4 `0x08A` B21 / B18:B19 / B24. Damping **omitted** (B25=0). |
| `5280`/`5281` sidecar             | same PDU: cruise latch B3, set speed B10, speed-error B8:B9                                                  |
| `1B40_2` ADU pinion               | the live milliradian at B18:B19                                                                              |
| `1B40_3` EPS pinion               | **unpublished** — B13:B14 and B16:B17 are the s16 invalid `0x7FFF`                                           |
| `2A06` / `57DE` result            | **not** a distinct Bus-4 s16 (hands-light census). `0x081` is a low-pass of the **request**, not the winner. |
| `5265` / `5285` / `5631` / `560D` | FFD-only so far. No live Operation-FFD grab in the retained logs.                                            |
| EPS ingress                       | F33 does not accept `0x08A`. The published request is next to EPS, not into EPS.                             |


`0x08A` is request-shaped (has assist gain). The winner is result-shaped
(ID + pinion only). Mixing them is how the middle stayed “spooky.”

RoB `SYSTEM_TYPE` (`0=None 1=AHBAHS 2=LDA 3=PCS 4=IDA 5=URSM 6=SDG`)
classifies **triggers**, not the ECU that produces a DID. LTA/LCA/LCS
cancel RoBs are `SystemType=2` (LDA family). That is recorder grouping,
not “LDA ECU transmits `0x08A`.”

#### Who hosts vs who executes (bounded, not unknown)


| Role                  | What GTS+ actually proves on this car                                                                                                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Recorder host         | **FRC** category 498 only. Master `CDbDllTable` binds `GetTSS3OperationFFDP5` / `GetTSS3ImageFFDP5` to `0x792`. Identical NA/EU/JP.                                                                                     |
| Request publisher     | Bus-4 native transmitter (Brake/Skid or CGW-origin). Consecutive `5282` is **absent** from sniffed Bus 1 (VAR-094). FRC-on-Bus-1 TX of `0x08A` is **rejected** (bus 1 count = 0). Signer/profile still open. |
| Long sink             | Brake SID-22 `10A1..10A4` “from TSS”.                                                                                                                                                                                   |
| Lat sink on Data List | **none**.                                                                                                                                                                                                               |
| P5 DSS / P6 ADCU      | **not installed.** `FRC_P5` category-498 rows have zero co-occurrence with `DSSystem_P5` / `PCS1_P5` / `PCS2_P5`. Camry 12704/12862/12984 ADAS stays gen-20 P5 FRC/EMPS. P6 `1B40` dual-pinion is a layout oracle only. |


Static GTS+ therefore **names the mux** and **refuses to name the CPU**.
The two remaining candidates are FRC (holds every object in RAM the
recorder can dump) and Brake (named long sink + chassis grant word +
F33’s B6 source-domain DTC). Picking between them is a live
`5282` vs `5285`/`57DE` vs `5265_7` join on `0x792`, not another CAN
census of IDs EPS already does not accept.

Host fetch is already decoded: selector `0x66`, `AB11/12/13 → EB11/12/13`,
EB13 blocks = `[DID16][len8][data…]`. Image-FFD decrypt remains
`plain = reverse_bits8(cipher) XOR 0xAA`.
`tools/camry_tss3_request_capture.py` still only SID-22’s longitudinal ISA
DIDs. It does not pull this recorder.

#### How to use it (read vs actuate)

- **Read hop 1:** already have it. `0x08A` is the truncated TSS request
publication. That is CarState / HUD / “LTA was requested.”
- **Read hop 2:** FRC Operation FFD during ID11. Forced comparisons:
`5282` vs `5285` (did LTA win?), `57DE` vs `0x08A` B18 (did the winner
equal the published request?), `5265_7` (did chassis grant?),
`560D` EPS pinion vs `0x025` (plant). If `5265_7=0` while B21=11,
the 73 s is request-without-grant.
- **Actuate:** copying `0x08A` onto the bus does not feed EPS. The
request is not the granted pinion. Stay `noOutput`.

Evidence grades: **recovered** for the named object model, layouts, scales,
invalid sentinels, recorder host, and Bus-4 request join; **bounded** for
executor CPU and `0x08A` signer; **verified** for zero `57DE`-shaped
distinct Bus-4 s16 in the retained drives and F33 not accepting `0x08A`.

### 2026-08-29 — later Operation-FFD live plan

Host protocol is decoded; this car has never been sent `AB11`. Later
execution plan (ignored context, not a claim ledger):
`REFERENCE/CAMRY_TSS3_OPERATION_FFD_PLAN.md`.

Trap already in that plan: category-498 selector `0x66` is master
`send=3e00` (TesterPresent comm-cache slot), **not** the recorder
payload. The plugin then sends `AB11/12/13`. Operation FFD is a RoB
time-series, not a SID-22 poll. Offline EB13 decoder against the 1,130-row
table first; parked `AB11` next; Image FFD / SecurityAccess never.

Same bus ≠ already in the logs. Post-repin, FRC `0x792→0x79A` is on panda
bus 0 next to chassis. Operation FFD is still **tester-polled**, not a
broadcast. The two LTA drives are passive CAN: no `AB11/EB11` exchange
(TMS-086 / TSE notes already record that negative). You cannot decode
`57DE`/`5265` out of those rlogs because nobody asked the camera.

What the logs *do* decode is hop 1: `0x08A` is truncated `5282`. Hop 2
winner/grant was already searched as ordinary Bus-4 fields and is not
there as a distinct s16. An Operation-FFD grab is only required if we
need FRC-RAM winner/grant; it is not required to read the published
request.

FFD is not the hot path. It is a diagnostic recorder of those objects, not  
the chassis command bus. Driving commands that moved the car are on CAN  
(and inside EPS). `0x08A` is the live request publication we already have.  
Operation FFD is an optional FRC-RAM oracle for winner/grant, not an  
actuation interface. Do not treat `AB11` as the next steering problem.

### 2026-08-29 — CarState reads the live `0x08A` request

Hot-path progress in `kai-openpilot/opendbc_repo` (not this tree): Camry
`_update_tss3` now sets `cruiseState.enabled` / `available` from
`CRUISE_OPERATING_LATCH` and `cruiseState.speed` from `SET_SPEED`. Assist
gain is `tss3_steering_assist_gain = B24/100`. DBC comments join B24 to
`5282` assist and B8 to cruise speed-error. Still `noOutput`. Corolla
unchanged. Latch-off fixture test added.

### 2026-08-29 — `CEFFC`/`CB00` is the D0218 map bank, and it is B6-only

Walked the unnamed `D0218` ingress instead of another FFD detour.

`FUN_000CEFFC` writes `FEBECB00` (default **7**). When `ACBD==0` and
`CAFF==1`, B6 sig261 snapshot `FEBEADB0` maps Target Lateral ID
`1/4/10/11/18/19` onto `CB00=0/1/3/2/5/4`. `CD094` and `CDFF8` index
return/dither tables as `(CB00&7)+(AC3C&1)*8`. That is the F33 decoder
already named in live-baseline §9.2, now joined to the actual D0218
angle-domain maps.

`ADB0` has only snapshot/reset writers. F33 still does not accept
`0x08A`. In these drives B6 count is 0, so `CB00` stays 7: the ID11
bank (`CB00=2`) does **not** run. `CEFFC` can change D0218 stiffness
maps when B6 carries 11/18; it cannot import the milliradian target
from Bus-4 `0x08A`. Hands-light motor tracking of `0x08A` error is
still a plant fact without that selector. Canonical: live-baseline
§30 / VAR-090. Still `noOutput`.

### 2026-08-29 — who TXes `0x08A`, and default-bank `D0218` cannot be the tracking command

Two streams, no new capture.

**Stream 1 (VAR-091, corrected by CORR-136).** GTS+ `canbus 12984` puts
Front Camera Module on **Bus 1 only**; exact F33 does not Tx/Rx `0x08A`.
Retained `0x08A` is present on Bus 4 and absent on Bus 1. Its observed mean
rate is ~38–40 Hz, but the 20/30 ms gaps come from multi-frame rlog
publication timestamps and cannot identify arbitration, a TX queue, or an
ECU. Bus-4 trailer structure remains ordinary-P5 `FV4||MAC28`; physical
transmitter, private transport, and signer remain open.

**Stream 2 (VAR-092).** Walked the eight default-bank `D0218` writers with
`CB00=7`. They read driver torque `AC44`, speed `ADF6`, measured-angle
rate from `AC88`, peripheral `EC14`, and ROM maps. None reads `ADB0` or
the B6 COM window. ID11 maps do not run (VAR-090). Accept the published
command is **not an F33 COM input**. The plant can still follow a request
EPS does not receive. Stay `noOutput`.

Canonical: live-baseline §§30,41 / VAR-091/092 / CORR-136.

### 2026-08-29 — camera Bus-1 output lacks the ordinary-P5 trailer; signer remains open

Both retained drives sniff Bus 1. Zero `0x00F`; every periodic stream
(n≥50) has near-constant last-4 (max unique fraction 0.000978 A /
0.000834 B), while Bus-4 `0x08A/32` last-4 is frame-unique ordinary-P5
`FV4||MAC28`.

This proves an envelope difference between the observed buses. It does not
prove FRC lacks a CMAC primitive, cannot pre-authenticate over private
transport, or owns/does not own the `0x08A` key. A Bus-4 node physically
transmits the frame; CMAC computation may happen there or upstream. Grade:
**verified** for observed trailers and bus placement, **bounded** for
transmitter/signer/HSM/key. Still `noOutput`.

### 2026-08-29 — Bus-1 camera frames are readable; GTS+ names range, not a DBC

The logs contain every camera-bus PDU. GTS+ still has no `BO_ 384`.
It has FRC Data List geometry (`0x190A` Forward Vehicle Distance,
`0x1804/0x1805` control-target distance/side position, `0x1909`
lateral position) and Operation-FFD object layouts (`5A22` 0.01 m
unsigned range, `5A24` 0.01 m lateral, `5A26` 0.05 m/s rel-speed,
`590C` Type-f ACC target floats, `5A30/5A33` lane offset/yaw).

Join onto the wire (VAR-093):

- 22 periodic panda-bus-1 streams. No `0x00F`. Last-4 of `0x180` is
  `00000000`.
- `0x180..0x18B`: checksum + shared counter + 4-byte zero trailer.
- `0x180/181/182`: **eight 7-byte object slots**. Empty =
  `fff8000000ffff`. Occupied bytes 0-1 u16be × 0.01 m is range
  (median 26 / 37 m). `5A24`/`5A26` are not 1:1 on bytes 2-5.
- `0x160[22]` is still the inbound SAS steering-angle echo.

Canonical: live-baseline §42. Still `noOutput`.

### 2026-08-29 — middle hop: how the camera request is built, routed, transformed, and whether any angle reaches EPS

The camera's native CAN is perception plus inbound plant. The TSS **request** is a different object.

**Build.** FRC (main TSS processor) writes `5282`/`5631` in camera RAM: Target Lateral ID, milliradian pinion, assist, damping. Inputs: vision objects on its own bus, measured SAS via `0x025`/`0x160` echo, EPS torque `0x030`. Ordinary Data List does not expose this four-field command.

**Route.** Consecutive `5282` layout `ID || pinion_s16be || assist` is **absent** from sniffed Bus 1: 0/200 ID11 `|B18|≥20` samples per drive in ±25 ms, 0 hits anywhere on that bus for those 4-byte patterns. Two-byte pinion collisions are noise. CGW does not copy a Bus-1 5282 PDU. A Bus-4 origin origin-TXes the truncated request as `0x08A`.

**Transform.** Drop damping; pack ID/pinion/assist as B21/B18/B24; cruise sidecar; `FV4||MAC28`; 20/30 ms mix. `1B40_3` EPS copy unpublished. Winner `57DE` not on Bus 4.

**To EPS?** Measured angle on the camera bus is SAS → FRC, not a command. Requested pinion is not on camera CAN. `0x08A` sits **beside** EPS; F33 does not Rx it; B6 idle; `D0218` is not this milliradian. Stock LTA does not relay the camera-computed angle into F33 as COM.

Canonical: live-baseline §43 / VAR-094. Still `noOutput`. Do not send `0x08A` to EPS.

### 2026-08-29 — handoff audit: rlog batching invalidates transmitter timing; Bus-1 plaintext does not identify the signer

The first VAR-091 draft overclaimed the new evidence.

**Timestamp falsifier.** The NDJSON uses rlog `Event.logMonoTime`, shared by
all CAN frames in one publication. Bus-0 median batch size is **14** in both
drives. `0x08A` shares its timestamp with another bus-0 frame in
**20,607/20,615** A and **23,999/23,999** B samples. Therefore its apparent
20/30 ms gaps are publication timing, not per-frame wire timestamps. They
cannot establish arbitration delay, a shared/different TX queue, oscillator,
scheduler, or ECU. The “not Skid's `0x0D7` queue” conclusion is removed.

**Authentication boundary.** Zero Bus-1 `0x00F` and near-constant last-4 on
all periodic Bus-1 streams prove those observed PDUs do not end in ordinary-P5
`FV4||MAC28`. They do **not** prove that FRC lacks ICU-S or another CMAC
primitive, nor exclude a private link carrying a pre-authenticated `0x08A`
image. Physical Bus-4 transmission and CMAC computation may occur in different
ECUs. FRC pre-authentication remains possible alongside CGW/Skid/Brake
assembly/signing.

**Request vs grant.** The retained classifier sees `0x08A` ID11 request state.
GTS+ explicitly separates request `5282/5631`, winner `5285/57DE`, and grant
`5265`. With no Operation-FFD capture, those 73.3 s are not a grant oracle.
The next decisive log is synchronized FRC Operation FFD; the next decisive
signer evidence is exact candidate firmware or a source-identifying physical
capture. Still `noOutput`.

Canonical correction: CORR-136; VAR-091/094; live-baseline §§38,41–43.

### 2026-08-29 — Operation-FFD EB13 decoder complete

Added `tools/decode_camry_tss3_operation_ffd.py`. It decodes reassembled
`EB13` blocks from offset 6 through the tracked 1,130-row PCS semantics:
MSB0 bit geometry, signed/unsigned/float conversion, physical LSB/offset,
invalid encodings, unknown-DID retention, and DID filtering.

Synthetic fixture verification pins `5282` request, `5285/57DE` winner,
`5265` active-steering grant, `560D` EPS pinion, invalid `0501`, malformed
length rejection, and CLI JSON. Live `AB11/12/13` acquisition is the
remaining step; no car I/O was performed.
