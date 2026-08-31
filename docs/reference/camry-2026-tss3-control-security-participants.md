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

## Network/control overview

```text
Toyota Bus 1: ADAS/request side

  FRC / Front Recognition Camera 2 (498, 0x792)
        |
        | request/object traffic
        | observed native Bus-1 family = reproducible E2E integrity
        | + alive counter, no secret-bearing MAC
        v
  private / differently-packed downstream handoff
        |
        v

Toyota Bus 4: chassis protected-control side

  Central Gateway / Skid-ABS / Brake Booster   <- exact proxy still unresolved
        |
        | ordinary Toyota-P5 FV4 || MAC28 protected publications
        | e.g. lateral 0x08A, longitudinal 0x0CA
        +--------------------------+
        |                          |
        v                          v
      EPS                      brake / longitudinal arbitration
  (0x7A1, proven              (0x7B0 Brake/EPB is the positively
   ICU-S verifier)             attributed immediate B6 source domain)
                                   |
                                   v

Toyota Bus 2: propulsion side (confirmed HV/MG placement)

        Hybrid Vehicle Control (397, 0x7D2)
                  |
                  v
        Motor Generator (395, 0x724)

  Engine (372, 0x700) is a separate live powertrain endpoint; its exact
  canonical bus-placement row is not promoted here.
```

**Important bus-name warning:** Panda bus 2 is not Toyota Bus 2. The Toyota-B
harness relay pair exposes the Toyota Bus-4 chassis segment on Panda buses 0/2;
Toyota's separately named Bus 2 contains Hybrid Vehicle Control and Motor
Generator and is not the split relay segment.

## Participant table

| ECU / role | Exact Camry identity / endpoint | Toyota network | Control role | TSK / SecOC status | MCU / security-hardware status |
|---|---|---|---|---|---|
| **Front Recognition Camera 2 / FRC_P5 (498)** | `0x792 -> 0x79A`; F181 `8646F3315000`; DID0105 `8646C06091` | **Bus 1** | Sole installed TSS3 ADAS compute ECU on this architecture. Hosts the TSS3 Operation/Image FFD recorder and the normalized lateral/longitudinal request vocabulary (`5280..5285`, `57DB`, `57DE`, etc.). | **Not a TSK key-holder/signing participant in the current recovered architecture.** Native observed Bus-1 periodic traffic has reproducible non-secret E2E integrity plus rolling freshness, not Toyota FV4/MAC28 SecOC. A semantic FRC request therefore has to cross into a downstream TSK-capable proxy before authenticated Bus-4 publication. | Exact application MCU/HSM remains outside the current firmware corpus. Do not infer ICU-S merely because the FRC supervises ECU Security Key state or records security DTCs. |
| **Skid Control / Brake-EPB / ABS_P5 (435)** | `0x7B0 -> 0x7B8`; F181 `F152633K0000`; DID0105 `8954147040`; F18C `8954147040CFC1800985` | **Bus 4** | Brake/VSC/TRAC domain. Exposes Toyota-Safety-Sense upper/lower acceleration-request observers `10A1..10A4`. Exact EPS B6-loss semantics attribute the immediate protected B6 source domain to **Brake System Control Module/category 435**. | **Strongest confirmed brake-side protected-control participant family.** B6 source-domain attribution is positive; exact `F152633K0000` CMAC-generation/key ownership is still unproved because its application firmware is not local. It is also a leading `0x08A`/`0x0CA` proxy candidate, not yet the uniquely identified transmitter. | Exact silicon unknown. An ICU-S/ICUSE-capable RH850 chassis MCU is a current hardware hypothesis if this exact ECU proves to own the Toyota TSK CMAC path; do not promote the derivative without firmware or package marking. |
| **Brake Booster / Brk_Bst_P5 (466)** | Installed in exact Camry architecture; exact physical diagnostic address/F181 not yet resolved | **Bus 4** | Separately installed brake actuator/booster participant. Its GTS DDB exposes the same TSS upper/lower acceleration observer family `10A1..10A4`. | **Downstream proxy/signer candidate.** Exact Camry TSK roster membership, CMAC ownership, and `0x08A`/`0x0CA` Tx ownership remain unproved. | Exact silicon unknown. If it is the TSK signer, the recovered Toyota implementation implies ICU-S/ICUSE-class SHE functionality or an equivalent implementation; this is not yet a part-number identification. |
| **Electric Power Steering / EMPS_P5 (405)** | `0x7A1 -> 0x7A9`; F181 `8965F3307000`; second SW `8A3113303100`; F18C `8965033K9011J2740743` | **Bus 4** | Steering actuator / protected external steering-request receiver. | **Proven TSK/SecOC participant and verifier.** Exact firmware implements ICU-S command 7 CMAC verify, command 5 CMAC generate capability, command 8 SHE-compatible M1/M2/M3 key update with M4/M5 result, protected key-slot selection, and Toyota FV4/MAC28 receive handling. | **Renesas RH850/P1M-E**, exact known target family; ICU-S/ICUSE security block recovered directly from firmware/MMIO behavior. |
| **Central Gateway** | Installed topology role; Techstream security logic performs a related gateway check at `0x7A2`, but `0x7A2` is **not** treated here as a proven Central-Gateway identity | Gateway between Toyota network domains | Carries/interconnects the Bus-1/Bus-4 topology and remains a plausible request repacker/proxy. | **Candidate only** for `0x08A`/`0x0CA` assembly/signing. No current evidence selects it over Skid/Brake Booster as the AES-CMAC owner. | Exact security MCU/HSM unresolved. Do not assume ICU-S until firmware/hardware or exact TSK-provisioning evidence identifies it. |
| **Hybrid Vehicle Control / HV_P5 (397)** | **`0x7D2`** live diagnostic endpoint | **Bus 2** | High-level hybrid propulsion coordinator. GTS exposes `Target Engine Power`, `Request Engine Torque`, `Directly Transmitted Engine Torque`, and requested/executed regenerative-brake torque. This is the strongest current candidate for the final **positive-driving-force coordinator** downstream of the TSS acceleration arbitration. | **Exact Camry TSK membership is unresolved.** Older/current P5 Toyota security vocabulary explicitly includes `Communication Error by ECU Security Key Not Registered (Hybrid/EV Powertrain Control Module)`, so HV control is a real ECU-Security-Key participant class in Toyota P5 architectures; do not yet promote that cross-vehicle fact to the exact Camry roster. | Exact MCU/HSM unresolved. If the exact Camry HV ECU is on the TSK roster, identify whether it uses ICU-S/SHE or another implementation from firmware/part evidence rather than assuming from function. |
| **Engine / Engine_P5 (372)** | **`0x700`** live diagnostic endpoint | Powertrain domain; exact canonical component placement should be treated separately from the confirmed HV/MG Bus-2 rows | Combustion propulsion executor. Current GTS includes `Requested Engine Torque`, `Request Engine Torque`, actual torque, and related hybrid engine-demand signals. | **Exact Camry TSK membership unresolved.** Toyota P5 security vocabulary explicitly includes `Communication Error by ECU Security Key Not Registered (Engine Control Module)`, proving that Engine is a key-provisioned participant class on relevant P5 architectures, not that this exact Camry endpoint has already been enumerated in the live roster. | Exact MCU/HSM unresolved. |
| **Motor Generator / MG_P5 (395)** | **`0x724`** live diagnostic endpoint | **Bus 2** | Electric propulsion/inverter-side executor under hybrid control. | Exact Camry TSK/ECU-Security-Key membership is **unknown**. No current evidence should promote it merely because it executes positive torque. | Exact MCU/HSM unresolved. |
| **HV Battery / HV_Battery_P5 (398)** | **`0x747`** live diagnostic endpoint | Powertrain/HV domain | Energy/storage participant; not currently implicated as the direct TSS driving-force actuator or SecOC proxy. | Exact TSK membership unknown and currently not required by the recovered TSS control-path model. | Exact MCU/HSM unresolved. |

## Message/security planes

### FRC-side / pre-protection candidate: `0x160/32`

The retained relay-correct drives place `0x160` only on native Toyota Bus 1.
Across the complete observed Bus-1 periodic family, committed VAR-107 proves a
wire-reproducible, non-secret integrity relation plus an 8-bit rolling freshness
counter. The same visible suffix does not produce competing integrity words, and
retained complete counter cycles repeat. This is **not** the ordinary Toyota
`FV4 || MAC28` SecOC boundary seen on Bus 4.

`0x160 B12` interpreted as signed 7-bit correlates very strongly with the
protected longitudinal `0x0CA B7:B8` quantity during stock cruise
(`r=-0.951664` / `-0.989396` in the two retained drives). It is therefore a
high-value **pre-protection cross-plane candidate**, but its exact OEM field
name, transmitter, direction, and receiver acceptance contract remain open.
Do not call it the FRC acceleration command until synchronized diagnostics or
producer firmware proves that mapping.

Canonical evidence: VAR-106, VAR-107.

### Protected longitudinal plane: `0x0CA/32`

`0x0CA` is present on the captured Toyota Bus-4 relay pair and absent from
native Bus 1. Its trailer has the ordinary Toyota-P5 protected shape:

- FV4 phases 0..15;
- reset/message freshness behavior linked to the protected `0x00F` epoch;
- candidate 28-bit authenticator that is nearly frame-unique;
- B27 zero before the `FV4 || MAC28` trailer.

The application contains three signed big-endian words at Toyota's exact
`0.001 m/s^2` diagnostic scale. During stock cruise they behave as an
upper/lower/result-like triplet, with the result-like word bounded by the other
two on 97.9% / 94.4% of retained frames. It is genuinely bidirectional:
retained stock-cruise `B7:B8` reaches **+1.693 m/s^2**, so this protected plane
carries positive acceleration as well as deceleration.

GTS independently names the architecture that explains this:

- FRC/PCS recorder: lower request `5280`, upper request `5281`, arbitration
  result longitudinal ID `5284`, result acceleration `57DB`, validity `57D3`;
- FRC ordinary monitor: longitudinal request/permission/allocation surface
  `1B03..1B07`;
- Brake-domain observer: `10A1/10A2` upper/lower TSS request acceleration and
  `10A3/10A4` upper/lower request IDs;
- Toyota's **Braking Force and Driving Force Allocation Method** explicitly
  distinguishes `Engine Only`, `Engine and Brake 1`, `Engine and Brake 2`, and
  `Brake Only`.

Therefore the TSS3 longitudinal domain is not a brake-only controller: it
requests acceleration and chooses braking/driving-force allocation. The exact
`0x0CA` byte-to-GTS-field assignment, physical transmitter, final arbitration
executor, SecOC profile/key owner, and Bus-4 -> powertrain handoff remain open.

Canonical evidence: TMS-085, VAR-106.

### Protected lateral plane: `0x08A/32`

`0x08A` is the corresponding observed Bus-4 lateral request publication with
ordinary-P5 `FV4 || MAC28` structure. Exact F33 EPS neither transmits nor
receives it. The FRC hosts the matching request object but its observed native
Bus-1 family uses non-secret E2E integrity/freshness rather than Toyota SecOC. Current topology therefore bounds the
proxy/transmitter candidates to **Skid Control / Brake Booster / Central
Gateway**. Do not infer `0x08A -> B6`; that stock transform is disproved.

Canonical evidence: VAR-091, VAR-094, VAR-101, VAR-107, CORR-149.

## Current TSK roster: what is actually known

Use these buckets rather than one undifferentiated "TSK participant" list:

**Proven exact-Camry TSK/SecOC participant**

- EPS / EMPS_P5 `0x7A1`: ICU-S/SHE implementation recovered directly.

**Positively attributed protected-control source family, exact signer still open**

- Brake System Control / ABS_P5 category 435 `0x7B0`: exact EPS B6-loss
  semantics identify the immediate protected B6 source domain; exact
  `F152633K0000` CMAC-generation ownership awaits producer firmware.

**Exact-Camry downstream signer/proxy candidates**

- Skid/ABS 435;
- Brake Booster 466;
- Central Gateway.

**Toyota P5 ECU-Security-Key participant classes whose exact Camry roster
membership still needs to be read**

- Engine Control Module;
- Hybrid/EV Powertrain Control Module.

**Installed propulsion participant with no current key-roster proof**

- Motor Generator.

**Explicitly not the TSK signer in the recovered Camry architecture**

- FRC / Front Recognition Camera 2. It is the request-side ADAS compute node;
  observed native output uses non-secret E2E integrity/freshness rather than
  Toyota SecOC, and authenticated chassis publication requires a downstream
  TSK-capable proxy.

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

For control ownership rather than provisioning membership, the next decisive
artifacts remain exact `F152633K0000` Brake firmware and a synchronized stock
DRCC capture joining FRC `1B03..1B07`, Brake `10A1..10A4`, Operation FFD, and
all-bus CAN.
