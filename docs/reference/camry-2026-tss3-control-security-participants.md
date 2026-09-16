# 2026 Camry TSS3 control/security participant inventory

This is the compact lookup table for the maintainer's 2026 Camry Hybrid TSS3
control path. It exists so ECU roles, network planes, and TSK/SecOC status do
not have to be re-derived from the longer Camry/GTS+/firmware reports.

The table deliberately separates four different claims:

1. an ECU is installed on the vehicle;
2. an ECU participates in the TSS longitudinal/lateral control path;
3. an ECU participates in Toyota ECU Security Key / TSK provisioning; and
4. an ECU actually owns a SecOC AES-CMAC key and generates/verifies a protected
   vehicle-network PDU.

Those are not interchangeable.

## Current network/control overview

Toyota's Vehicle Movement Manager architecture and the exact Camry topology now support
a more specific model than the older proxy graph. Keep **logical Toyota bus identity**
separate from a claim of one electrically transparent pair.

```text
Toyota Bus 1: ADAS / application side

  FRC / Front Recognition Camera 2 (498, 0x792)
        |
        | application request semantics / recorder ownership
        | native observed periodic family = AUTOSAR E2E Profile 5
        v
  request-side publication / handoff
        |
        v

Toyota logical Bus 4: chassis / Vehicle-Movement-Manager domain

  Panda-visible shared/trunk side
        |
        +-- No. 2 Global CAN Junction Connector
        |       +-- Brake Booster (0x28)
        |       +-- Skid Control / Brake-EPB (0x29, category 435)
        |               |
        |               | VMM arbitration + request generation [leading owner]
        |               +---- 0x081 result/status publication
        |               +---- final protected B6 steering target [leading path]
        |                              |
        |                              v
        +--------------------- EPS attachment labelled `EBU` by GTS
                                       |
                                       v
                            EPS / EMPS_P5 (0x32, 0x7A1)
                            one exact-F33 application CAN controller

  0x08A = TSS request-side control envelope
  0x081 = Brake-owned arbitration/result/reference envelope
  B6    = final steering-controller target/instruction
```

`EBU` is **not an installed ECU component row** on the exact Camry. It is the
`CDbCanBusComponentTable` junction/attachment string on the EPS row. Toyota-authored
US20210323519A1 uses the phrase **"electronic brake module or unit" (EBU)**; current
GTS itself does not spell the acronym out. Brake-family DDBs independently expose
`(EBU node)` dynamics. Successor `BSCM_A_P6 = Brake/EPB` exposes native wheel/G
values while `BSCM_B_P6 = Brake Booster` exposes their `(EBU node)` copies, strongly
favoring the EBU node as the Brake/EPB / skid-control side rather than a third ECU.
`ABS_P5` additionally distinguishes ordinary Power Steering communication from
**Power Steering Control Module "A" (ch2)** and exposes
`EPS/Steering Control Actuator ECU Communication Open`. Thus the leading physical
model is an upstream Brake/Skid local-routing boundary feeding F33's single CAN input,
not a second EPS CAN controller and not a separately installed EBU filter ECU. Exact
`F152633K0000` producer firmware is still required to prove the concrete channel,
filter, signing and freshness implementation.

**Important bus-name warning:** Panda bus 2 is not Toyota Bus 2. The Toyota-B
harness relay pair exposes the Toyota Bus-4 chassis segment on Panda buses 0/2;
Toyota's separately named Bus 2 contains Hybrid Vehicle Control and Motor
Generator and is not the split relay segment.

## Participant table

| ECU / role | Exact Camry identity / endpoint | Toyota network | Control role | TSK / SecOC status | MCU / security-hardware status |
|---|---|---|---|---|---|
| **Front Recognition Camera 2 / FRC_P5 (498)** | `0x792 -> 0x79A`; F181 `8646F3315000`; DID0105 `8646C06091` | **Bus 1** | Sole installed TSS3 ADAS compute ECU on this architecture. Hosts the TSS3 Operation/Image FFD recorder and the normalized lateral/longitudinal request vocabulary (`5280..5285`, `57DB`, `57DE`, etc.). | **ECU-Security-Key provisioning participant at the FRC family level; exact runtime key use/CMAC ownership unresolved.** Current `FRC_P5` owns `0x10AF` **ECU Security Key Registered Incomplete Flag** and `XF01B ECU Security Key Not Registered`, while Toyota's camera-replacement procedure requires updating that key. Current GTS+'s selected network key-update frontend is now recovered as `10 4F` + RID `0x3002` SHE M1--M5 per admitted ECU; a live `0x792` transcript is still required to prove how this FRC appears in that special participant namespace. Native observed Bus-1 periodic traffic is exact non-secret E2E Profile 5, not Toyota `FV4||MAC28` SecOC, so a downstream Bus-4 participant must still proxy/physically publish the protected chassis PDU. | Same-generation Denso/TSS3 hardware uses Toshiba **TMPV7706XBG / Visconti5**. DTS Insight's TMPV770 startup guide explicitly names hidden Core0 **`HSM_CM3`**, with dedicated `SDAUTH.DAPSEL` secure-debug selection: an on-die Cortex-M3 HSM is therefore the concrete platform security backend. Exact Camry board identity and the UDS/R4/A53 -> HSM mailbox/service ABI remain unproved. M1--M5 is standard AUTOSAR SHE `CMD_LOAD_KEY`, not an ICU-S-specific format. |
| **Skid Control / Brake-EPB / ABS_P5 (435)** | `0x7B0 -> 0x7B8`; F181 `F152633K0000`; DID0105 `8954147040`; F18C `8954147040CFC1800985` | **Bus 4 via No. 2 Global CAN Junction Connector** | Brake/VSC/TRAC domain and leading exact-Camry Vehicle-Movement-Manager/request-generation owner. Exposes TSS upper/lower acceleration-request observers `10A1..10A4`, `EPS/Steering Control Actuator ECU Communication Open`, and separate ordinary/ch2 Power-Steering missing-message vocabulary. Exact EPS B6-loss semantics attribute the immediate protected B6 source domain to **Brake System Control Module/category 435**. | **Strongest confirmed brake-side protected-control participant family.** Contemporary Toyota brake-actuator procedures require ECU-Security-Key update when the skid-control ECU/brake-actuator assembly is replaced, consistent with this serviceable domain owning authenticated local-network relationships. Exact `F152633K0000` B6 CMAC/freshness ownership remains unproved until its application firmware is acquired. | Exact silicon unknown. An ICU-S/ICUSE-capable RH850 chassis MCU remains a hardware hypothesis if this ECU proves to own Toyota TSK CMAC; do not promote a derivative without firmware/package evidence. |
| **Brake Booster / Brk_Bst_P5 (466)** | Installed in exact Camry architecture; exact physical diagnostic address/F181 not yet resolved | **Bus 4 via No. 2 Global CAN Junction Connector** | Separately installed brake actuator/booster participant. Its GTS DDB exposes `10A1..10A4` and `(EBU node)` dynamics. | Protected-control/signing participant candidate, but category 435 Skid/Brake is now the leading B6 request-generation/routing owner. Exact Camry TSK roster membership and CMAC ownership remain unproved. | Exact silicon unknown. |
| **Electric Power Steering / EMPS_P5 (405)** | `0x7A1 -> 0x7A9`; F181 `8965F3307000`; second SW `8A3113303100`; F18C `8965033K9011J2740743` | **Bus 4 via GTS attachment `EBU`** | Steering actuator / protected final-target receiver. Exact F33 has one configured application CAN controller; B6 is ordinary rule39/PDU44 on that controller. `EBU` is an attachment label, not a separate installed ECU. | **Proven TSK/SecOC participant and verifier.** Exact firmware implements ICU-S command 7 CMAC verify, command 5 CMAC generate, command 8 SHE `CMD_LOAD_KEY`, protected key-slot selection, and Toyota FV4/MAC28 receive handling. | **Renesas RH850/P1M-E**, exact known target family; ICU-S/ICUSE recovered directly from firmware/MMIO. |
| **Central Gateway** | Installed topology role; Techstream security logic performs a related gateway check at `0x7A2`, but `0x7A2` is **not** a proven Central-Gateway identity | Interconnects Toyota network domains | Still relevant to Bus-1 -> Bus-4 application-request transport/proxying. It is **not** the leading immediate B6 filter/source after the Vehicle-Movement-Manager, B6-loss-DTC, EBU-attachment and Brake `ch2` joins. | `0x08A` publication/signing/private-preauth participation remains possible where not otherwise closed; exact key ownership unresolved. | Exact security MCU/HSM unresolved. |
| **Hybrid Vehicle Control / HV_P5 (397)** | **`0x7D2`** live diagnostic endpoint | **Bus 2** | High-level hybrid propulsion coordinator. GTS exposes `Target Engine Power`, `Request Engine Torque`, `Directly Transmitted Engine Torque`, and requested/executed regenerative-brake torque. This is the strongest current candidate for the final **positive-driving-force coordinator** downstream of the TSS acceleration arbitration. | **Exact Camry TSK membership is unresolved.** Older/current P5 Toyota security vocabulary explicitly includes `Communication Error by ECU Security Key Not Registered (Hybrid/EV Powertrain Control Module)`, so HV control is a real ECU-Security-Key participant class in Toyota P5 architectures; do not yet promote that cross-vehicle fact to the exact Camry roster. | Exact MCU/HSM unresolved. If the exact Camry HV ECU is on the TSK roster, identify whether it uses ICU-S/SHE or another implementation from firmware/part evidence rather than assuming from function. |
| **Engine / Engine_P5 (372)** | **`0x700`** live diagnostic endpoint | Powertrain domain; exact canonical component placement should be treated separately from the confirmed HV/MG Bus-2 rows | Combustion propulsion executor. Current GTS includes `Requested Engine Torque`, `Request Engine Torque`, actual torque, and related hybrid engine-demand signals. | **Exact Camry TSK membership unresolved.** Toyota P5 security vocabulary explicitly includes `Communication Error by ECU Security Key Not Registered (Engine Control Module)`, proving that Engine is a key-provisioned participant class on relevant P5 architectures, not that this exact Camry endpoint has already been enumerated in the live roster. | Exact MCU/HSM unresolved. |
| **Motor Generator / MG_P5 (395)** | **`0x724`** live diagnostic endpoint | **Bus 2** | Electric propulsion/inverter-side executor under hybrid control. | Exact Camry TSK/ECU-Security-Key membership is **unknown**. No current evidence should promote it merely because it executes positive torque. | Exact MCU/HSM unresolved. |
| **HV Battery / HV_Battery_P5 (398)** | **`0x747`** live diagnostic endpoint | Powertrain/HV domain | Energy/storage participant; not currently implicated as the direct TSS driving-force actuator or SecOC proxy. | Exact TSK membership unknown and currently not required by the recovered TSS control-path model. | Exact MCU/HSM unresolved. |

## Message/security planes

### Bus-1 FRC state: `0x160/32`

`0x160` is FRC-origin Bus-1 state, but the former Camry command interpretation is
withdrawn. Its signed B4:B5 field follows measured/ego acceleration and lags motion
on clean resumes; it is not the recovered longitudinal command. The native Bus-1
FRC family uses AUTOSAR E2E Profile 5 rather than Toyota `FV4 || MAC28` SecOC.

Canonical evidence: VAR-107 and the current Camry longitudinal evidence packet.

### Unified TSS request plane: `0x08A/32`

`0x08A` is the recovered **FRC-side TSS control-request envelope**. It carries both
lateral request semantics and the core lower/upper longitudinal request packages:

- lateral request ID + requested pinion angle + assist gain;
- two packed longitudinal request-ID/allocation-method fields;
- two signed16 `0.001 m/s^2` acceleration-request words;
- request/hold state and protected freshness/authentication trailer.

Toyota US20200070849A1 supplies the architecture that explains this shape: applications
publish standardized lower/upper longitudinal bounds and a lateral request to the Vehicle
Movement Manager. FFD `5280/5281/5282` independently names those request packages. The
physical Bus-1 application-data -> protected Bus-4 publication/signing hop remains open;
that is a transport/security-ownership question, not a missing semantic command.

### Brake arbitration/result plane: `0x081/32`

`0x081` is Brake-owned and persists when FRC normal transmission is suppressed. Its
lateral result ID/reference closely follows the selected `0x08A` request; request loss
sets an independent Brake supervision bit. Longitudinally, B6[5:0] is the strongest
`5284 Arbitration result_longitudinal ID` candidate and B20:B21 the strongest `57DB`
result-acceleration candidate. This is the result/status side of Toyota's Vehicle
Movement Manager, not a passive relay.

### Other protected longitudinal/chassis state: `0x0CA/32`

`0x0CA` remains a protected chassis->upstream longitudinal-state/result-related PDU,
but its old "upper/lower/result triplet" interpretation is superseded by the much
cleaner `0x08A` request / `0x081` result architecture. Its exact field assignments and
producer remain useful secondary RE targets; do not use it as the primary TSS request.

### Final steering-controller instruction: protected `0x0B6/32`

B6 is downstream of application arbitration. Patent Figure 6's steering instruction and
EMPS DID `0x1CEE` independently name **Target Lateral ID** and final target steering
quantity, matching exact-F33 B6. F33 maps B6 loss to U012987 **Lost Communication with
Brake System Control Module**. Sep-10 receiver instrumentation proves native B6 reaches
F33 while a Panda-injected B6 on the shared/logical Bus-4 side disappears before
successful F33 controller admission.

The physical model is therefore request-side `0x08A` -> Brake/Skid VMM arbitration and
request generation -> result/status `0x081` + final B6 -> EPS. Exact GTS attaches Brake
Booster and Skid Control to Bus 4 through No.2 Global CAN Junction, but attaches EPS to
Bus 4 through `EBU`; `EBU` is an attachment value, not a separate installed ECU. The
leading implementation is category-435 Skid/Brake generating/routing B6 onto an EPS-local
leg feeding F33's single CAN controller. Exact `F152633K0000` firmware is still needed
to prove the concrete channel/filter/signing implementation.

Canonical evidence: VAR-161/162, CORR-195/196/197, OQ-054.

## Current TSK roster: what is actually known

Use these buckets rather than one undifferentiated "TSK participant" list:

**Proven exact-Camry TSK/SecOC participant**

- EPS / EMPS_P5 `0x7A1`: ICU-S/SHE implementation recovered directly.

**Positively attributed protected-control source family, exact signer still open**

- Brake System Control / ABS_P5 category 435 `0x7B0`: exact EPS B6-loss
  semantics identify the immediate protected B6 source domain; exact
  `F152633K0000` CMAC-generation ownership awaits producer firmware.

**Physical publication / routing boundary**

- **B6 immediate source/routing:** category-435 Skid/Brake is the leading target. Exact
  F33 names the missing B6 peer Brake System Control Module; GTS puts category 435 on
  Bus 4 through No.2 Global CAN Junction and EPS on an `EBU`-labelled attachment;
  `ABS_P5` has a separate Power-Steering `ch2` communication DTC.
- **Request-plane protected publication/signing (`0x08A` and related families):**
  Skid/ABS 435, Brake Booster 466, Central Gateway, and FRC private-preauthentication
  remain distinguishable until producer firmware/trace closes the exact path.

Do not convert the `EBU` attachment token into another ECU in the roster.

**FRC ECU-Security-Key status**

- FRC / Front Recognition Camera 2 is the request-side ADAS compute node on
  observed Bus 1. Current `FRC_P5` owns the camera-local ECU-Security-Key
  incomplete flag / not-registered behavior, and Toyota replacement procedure
  requires an ECU Security Key update for the camera family. Current
  `UtilityPlusFrontNK -> UtilityGene` closes the selected network updater as
  per-participant `10 4F` + `31 01/03 30 02` SHE M1--M5. The generic discovery
  phase uses `22 1000` bit0 plus a 16-byte `22 1010` identity, but ordinary
  `FRC_P5` uses DID `0x1010` for FOE/roll calibration and exposes no ordinary
  `0x1000` monitor row, so the FRC's special key-management admission/namespace
  remains a live-trace/firmware question. Same-generation TMPV7706 hardware
  supplies an on-die `HSM_CM3`; the remaining implementation question is the
  camera software's UDS/application-core -> HSM service boundary and runtime key
  use, not whether a secure backend exists. Observed Bus-1 output remains E2E
  Profile 5 and does not exclude private FRC pre-authentication.

**Toyota P5 ECU-Security-Key participant classes whose exact Camry roster
membership still needs to be read**

- Engine Control Module;
- Hybrid/EV Powertrain Control Module.

**Installed propulsion participant with no current key-roster proof**

- Motor Generator.

## Brake CUW shape / acquisition boundary

The exact Camry category-435 package is **not yet local**, so do not assign it
an EPS or FRC encryption grammar by analogy. What is fixed today is:

- exact live Brake/EPB endpoint `0x7B0 -> 0x7B8`;
- F181 `F152633K0000`, DID0105/assembly `8954147040`;
- any accepted package must identify `Node01/DiagID=07B0`;
- Toyota's official 24TC01 2023-Corolla Skid-Control/Brake-EPB campaign proves
  a contemporary category-435 software-update family
  `F152612A5100/5200/5300 -> F152612A5400`; this is a related Brake precedent,
  **not** the Camry package;
- current CUWPlus has a generic `P5-Unified` route using
  `TCUWCanUnifiedCIDGetter` + Unified prepare/flash writers and generic CAN-ID
  lookup, but the unavailable Brake descriptor must itself prove whether the
  exact package selects that route;
- the 26-package corpus contains zero `07B0` packages, so we currently have no
  Brake-side `SeedKey`, Nonce, `ReproMethod`, image format, or plaintext decode
  to transfer.

This matters for the recovered EPS payload root. The same
`ba052435f8843f985fd1329d2b6117b0` root CMAC-validates every encrypted body and
erase region in two independent F340 EPS CUWs (`T-0035-22` and `T-0036-22`),
while an older RAV4 EPS package rejects it. If an acquired `07B0` Brake CUW
contains the same `SeedKey + Nonce` grammar, test that root immediately. If it
omits `SeedKey` like the current ReproStd FRC/HV/MG packages, recover the
package's KDF/image-transform layer before concluding that the backend root is
different.

Canonical acquisition evidence: TMS-047..052, VAR-069, and TMS-088.

## Hardware implication

Toyota's recovered TSK implementation uses a SHE-like symmetric AES-CMAC key
model: protected key selectors, MAC generation/verification, and M1-M5
authenticated key update. On the exact EPS this is Renesas ICU-S/ICUSE.
Therefore **an ECU proven to be the actual Toyota TSK CMAC owner is a strong
ICU-S/ICUSE-class hardware target**, but AES-CMAC capability alone is not enough
to identify a Renesas derivative and topology alone is not enough to prove key
ownership.

Current silicon status:

- EPS: RH850/P1M-E + ICU-S, proven;
- FRC: ECU-Security-Key registration participation is proven at the camera-family
  level, but exact SoC/HSM and live Camry roster membership are unresolved; do
  not infer Renesas/ICU-S from the vendor-neutral M1--M5 provisioning contract;
- Brake/ABS: ICU-S-capable RH850 chassis family is a strong hypothesis; exact
  derivative unproved;
- Brake Booster / Central Gateway / HV / Engine / MG: unresolved.

## Best remaining discriminator

The cleanest way to stop guessing the exact ECU Security Key roster is the
read-only key-registration topology path already recovered from Techstream:
query the master security endpoint (`0x763`) for topology DID `0x1033` and map
its slave addresses to the live ECU identities above. This `0x763:0x1033`
security-topology DID is endpoint-specific and must not be confused with the EPS
`0x1033` Ready Status DID. Optional read-only
`0x1010` / `0x102E` / `0x1100..0x1108` values can further identify roster
records. Do **not** run the `0x3002` registration routine or any key write merely
to enumerate participants.

### Live read-only security characterization

Current GTS+ exposes two especially useful brake-domain read-only fingerprints:

- category 435 `ABS_P5` and category 466 `Brk_Bst_P5` both define DID `0x10AF`
  as the 17-byte **Software Number for Authentication**;
- category 498 `FRC_P5` defines DID `0x10AF` (alternate `0x30AF`) as **ECU
  Security Key Registered Incomplete Flag**, with the OEM 0/1/2 enum.

On the exact Camry, category 435 is already live-pinned at `0x7B0`. The Brake
Booster physical diagnostic request address is still unresolved; do not invent
one from the Toyota topology component index `0x28`. Use the `0x763` roster to
identify any additional security slave endpoint first.

With ignition/READY awake, the first characterization pass should remain
read-only and use the Comma Toyota diagnostic CLI:

```text
# Toyota MACKey-registration master / exact roster
tools/toyota uds raw 0x763 0x22 1033
tools/toyota uds raw 0x763 0x22 1010
tools/toyota uds raw 0x763 0x22 102E
tools/toyota uds raw 0x763 0x22 1100
... through 1105, then 1107 and 1108

# exact live Brake/EPB endpoint
tools/toyota did read brake 0x10AF
tools/toyota uds raw brake 0x22 1010

# FRC security-registration observer
tools/toyota did read frc 0x10AF
tools/toyota uds raw frc 0x22 1010
```

`kai-openpilot@25f6909ea` extends `uds raw` so an unregistered numeric 11-bit
endpoint such as `0x763` is accepted **only for read-only UDS services**. Mutation
to an unregistered address remains forbidden even with `--force`. Once
`0x763:1033` identifies a Brake-Booster/security-slave address, read its `F181`,
`F18C`, `0x10AF`, and `0x1010` by that exact numeric endpoint before assigning a
role.

An ignition-off attempt on 2026-08-31 timed out for both known-good Brake
`0x7B0` and `0x763`; because the known Brake endpoint was asleep too, that run is
**not evidence** that `0x763` or any security DID is unsupported. Repeat only with
the vehicle diagnostic network awake. Do not send `27 xx`, `31 01 30 02`,
`2E 10 35`, session changes, resets, downloads, or Active Tests during this
characterization pass.

For control ownership rather than provisioning membership, the next decisive
artifacts remain exact `F152633K0000` Brake firmware and a synchronized stock
DRCC capture joining FRC `1B03..1B07`, Brake `10A1..10A4`, Operation FFD, and
all-bus CAN.
