# openpilot vehicle-port quality benchmarks

> **Document type:** architecture / current-upstream survey
>
> **Status:** design reference
>
> **Snapshot date:** 2026-09-13

This report steps outside Toyota-specific reverse engineering and asks a more
basic question: **what does a good openpilot vehicle integration look like?**
The purpose is to keep TSS3 work anchored to the quality bar of mature upstream
ports instead of treating successful message injection as the end goal.

The distinction matters because two different questions are often collapsed:

1. **Is this a good car to own and use with openpilot?** This is the consumer
   question answered by comma's recommended/favorite vehicles.
2. **Is this a technically complete, upstream-shaped vehicle port?** This is an
   integration question about control ownership, tuning, radar, identification,
   safety, fault behavior, hardware, and release support.

A vehicle can score highly on one axis without being the strongest example on
the other. Ram 1500 is an explicit comma favorite while retaining stock ACC and
a substantial low-speed steering limitation; conversely, some technically very
complete integrations are not featured in comma's short consumer recommendation
list.

## 1. Current upstream reference

The survey used current upstream on 2026-09-13:

| Repository | Revision | Note |
|---|---|---|
| `commaai/openpilot` | `5f50bda7ba1a78862d0886c75f03125446bc6f1b` | Current `master`; pins opendbc below |
| `commaai/opendbc` as pinned by openpilot | `a3d3b7c6ca76ed4c97f606e9b2a0e371e8fa52af` | Vehicle integration reference actually consumed by openpilot |
| `commaai/opendbc` current master checked during survey | `057aee25b5eee7530f0b95b5b508c8c3247b0cd7` | Newer checksum cleanup; no relevant support-model change found |

The generated openpilot support table contains **335 upstream-supported car
rows** at this snapshot. The broader opendbc inventory contains **402 known car
rows** across all support levels.

### 1.1 What opendbc itself calls a complete port

Current `opendbc/README.md` gives a useful formal baseline. Steering alone is a
basic port. A **complete** port includes:

- lateral control;
- longitudinal control;
- good lateral and longitudinal tuning;
- radar parsing when the vehicle has usable radar data;
- fuzzy fingerprinting; and
- the rest of the production integration required around those features.

The README also states the social/upstreaming model explicitly: most ports come
from the community, while comma performs final safety and quality validation;
more complete and more popular ports are more likely to be selected for that
validation.

That definition is substantially stronger than "we can command the EPS."

## 2. Support level is part of integration quality

Current opendbc defines the following support states:

| Support type | Meaning for this survey |
|---|---|
| **Upstream** | Actively maintained by comma and plug-and-play in release openpilot |
| **Under review** | Merged but not yet release-supported pending safety/quality validation |
| **Custom** | Upstream software exists, but install/configuration is non-standard; not ordinary release support |
| **Dashcam mode** | Recognition/software may exist, but openpilot does not engage on release |
| **Community** | Supported in a community fork, not validated/maintained as upstream support |
| **Not compatible** | Known fundamental blocker such as unsupported network/security architecture |

At the snapshot there are 335 Upstream, 31 Dashcam, 17 Community, 16 Not
compatible, and 3 Custom rows; no rows currently use Under review.

The three Custom rows are instructive for Toyota work: RAV4 Prime 2021-23,
Sienna 2021-23, and non-US Yaris 2020/2023. They use the recoverable-key Toyota
SecOC path. Upstream software support therefore does **not** automatically imply
release/plug-and-play support when the vehicle still requires owner-specific key
recovery or an unusual setup.

## 3. What comma recommends to users

comma's public vehicle page (updated 2026-08-30 when checked) says that newer
Hyundai and Toyota models are generally great openpilot choices and gives the
following favorites:

| Segment | comma favorites |
|---|---|
| EV | Kia EV6; Hyundai Ioniq 5; Toyota Prius 2021-22 |
| SUV | Toyota Highlander 2020-23; Hyundai Palisade 2020-22 |
| Sedan | Toyota Corolla 2020-22; Hyundai Sonata 2020-23 |
| Truck | Ram 1500 2019-24; Chevrolet Silverado 1500 2020-21 |

This is a consumer shortlist, not an engineering completeness ranking. The
current generated support metadata makes that visible:

| Vehicle | Release ACC path | ACC floor | ALC floor | steering authority star | auto-resume |
|---|---|---:|---:|:---:|:---:|
| Toyota Prius 2021-22 | openpilot | 0 mph | 0 mph | full | yes |
| Toyota Highlander 2020-23 | openpilot | 0 mph | 0 mph | full | yes |
| Toyota Corolla 2020-22 | openpilot | 0 mph | 0 mph | full | yes |
| Kia EV6 2022-24 | stock on release; openpilot alpha available | 0 mph | 0 mph | full | yes |
| Hyundai Ioniq 5 2022-24 | stock on release; openpilot alpha available | 0 mph | 0 mph | full | yes |
| Hyundai Palisade 2020-22 | stock on release; openpilot alpha available | 0 mph | 0 mph | full | yes |
| Hyundai Sonata 2020-23 | stock on release; openpilot alpha available | 0 mph | 0 mph | full | yes |
| Ram 1500 2019-24 | stock | 0 mph | 32 mph | full | yes |
| Chevrolet Silverado 1500 2020-21 | stock on release; openpilot alpha available | 0 mph | 6 mph | full | no |

`openpilot available` in generated docs means alpha longitudinal is available
behind the development-only toggle on non-release branches such as
`nightly-dev`; it is not the normal release longitudinal path.

Thus comma's favorites answer "which vehicles make attractive openpilot cars?"
They should not be used unmodified as the architecture benchmark for a new port.

## 4. Cross-family integration survey

The useful comparison is by platform architecture, not merely by number of
supported model names.

### Toyota / Lexus: mature TSS2 is the strongest Toyota benchmark

Mature TSS2 is unusually complete in release openpilot. The best variants have:

- production openpilot longitudinal control rather than an alpha-only path;
- all-speed lateral control;
- all-speed longitudinal control and automatic resume from stop;
- parsed Toyota radar data where equipped;
- strong measured lateral authority;
- normal Toyota harnessing and the ordinary Toyota Panda safety model;
- standard CarState/CarController ownership and normal openpilot engagement;
- no separate vehicle-specific runtime permission state machine.

Examples in the current table include Corolla 2020-22, Prius 2021-22,
Highlander 2020-23, Camry 2021-24, Avalon 2022, and several Lexus TSS2 models.
The current measured `maxLateralAccel` metadata is particularly strong on
Avalon TSS2 (~2.78 m/s²) and Camry TSS2 (~2.37 m/s²); Corolla, Highlander, and
Prius TSS2 are all comfortably above the 1.0 m/s² threshold used for the docs'
full steering-authority star.

This family is the most directly relevant **gold standard for Toyota TSS3**:
the wire protocol and security can change completely while the final openpilot
integration should still look this boring from the rest of the stack.

### Ford: excellent control-contract benchmark

Ford's mature C2/CD6-era platforms are among the cleanest non-Toyota references.
The interface uses angle control, permits steering to zero speed, marks steering
as available at standstill, parses radar on radar-equipped variants, and uses
production openpilot longitudinal control where the radar architecture supports
it. Automatic-transmission vehicles provide the all-speed/auto-resume behavior
expected of a top-tier integration.

Representative complete release rows include Bronco Sport 2021-24, Escape
2020-22, Explorer 2020-24, Focus Mk4, Kuga 2020-23, Maverick 2022-24, and the
Lincoln Aviator. Newer CAN-FD Ford platforms such as F-150 2021-23 and Mustang
Mach-E remain excellent all-speed lateral examples but expose openpilot
longitudinal as alpha rather than the normal release path.

Ford is especially useful as a benchmark for the principle that the OEM's
native actuator interface should be represented directly in `CarParams` and the
controller rather than normalized through ad-hoc application policy.

### Volkswagen MEB: technically very complete

VW ID.4 2021-25 and CUPRA Born are unusually clean modern examples: production
openpilot longitudinal control, curvature lateral control, steering at
standstill, zero low-speed floors, automatic resume, and strong measured lateral
authority (~2.5 m/s² in current metadata).

Most MQB-family VW rows are also strong laterally and all-speed, but their
openpilot longitudinal path is generally alpha and depends on the J533 gateway
harness; camera-harness installations retain stock ACC. That install topology is
part of the quality story and is documented rather than hidden behind runtime
heuristics.

### Rivian R1: small family, very complete surface

R1S/R1T 2022-24 are upstream, all-speed, full steering-authority, automatic
resume, and documented with openpilot longitudinal control. They do not provide
a useful radar-parsing comparison because radar is unavailable to the port, but
they are a strong example of a small modern platform whose supported surface is
coherent rather than broad-but-partial.

### Hyundai / Kia / Genesis: arguably the best consumer family, not the best release-longitudinal benchmark

Hyundai-family support is enormous and the vehicles generally provide strong,
all-speed steering and stop-and-go stock SCC. Current metadata contains 99
upstream rows across Hyundai/Kia/Genesis under the internal Hyundai family, and
75 rows expose openpilot longitudinal as an alpha option.

That makes these vehicles excellent openpilot cars, and explains comma's strong
consumer recommendation. It also means they are not the cleanest benchmark for
**production release longitudinal integration**: release normally retains stock
SCC, while experimental openpilot longitudinal lives behind the development
alpha toggle.

This distinction is important for TSS3. A port can provide a very good user
experience with stock longitudinal and still be technically incomplete by
opendbc's own "complete port" definition.

### Honda: broad support with important longitudinal tradeoffs

Honda spans multiple generations. Older Nidec ports can provide production
openpilot longitudinal but frequently have weaker/low-speed-limited steering.
Modern Bosch cars can have excellent all-speed steering, but openpilot
longitudinal is commonly alpha. Current source and docs explicitly warn that on
applicable Bosch cars enabling alpha longitudinal disables CMBS functionality,
including AEB and FCW. Bosch CAN-FD does not currently expose that openpilot
longitudinal path.

This is a useful negative benchmark: feature count alone is not enough. A port
that gains longitudinal control by sacrificing important stock safety behavior
has a materially different integration quality profile.

### GM: capable but not a zero-compromise benchmark

Current supported GM camera platforms expose alpha longitudinal control. Their
metadata generally carries a low-speed steering floor and no automatic resume;
the Silverado favorite is 6 mph for ALC and has no resume-from-stop star. Older
ASCM/gateway architecture can provide direct openpilot longitudinal but has its
own minimum engagement/steering constraints and validation history.

### Subaru, Chrysler/Ram, Mazda, Nissan

These are useful examples of why "supported" is only the first bar:

- Subaru currently retains stock EyeSight longitudinal; alpha longitudinal is
  disabled while speed-dependent limits are being resolved, and docs do not
  claim automatic resume.
- Chrysler/Ram retains stock ACC and several platforms have substantial minimum
  steering speeds; radar parsing is explicitly unfinished in current source.
- Mazda currently uses stock longitudinal; CX-5 2022-25 is nevertheless an
  excellent simple all-speed lateral integration.
- Nissan uses stock longitudinal; its supported ProPILOT cars provide strong
  angle-control lateral behavior down to zero but do not claim automatic
  resume.

These can all be good supported vehicles without being the architecture we want
to emulate for a new full-control port.

## 5. Practical quality model for a new port

A production-quality openpilot vehicle integration should be evaluated across
all of these layers together:

1. **Release support and install:** upstream, ordinary release branch, normal
   harness/install, deterministic startup, no developer-only arming procedure.
2. **Identification:** reliable CAN/FW identification, platform-code handling,
   and fuzzy fingerprinting where appropriate.
3. **Vehicle state:** complete and correctly owned cruise, pedals, wheel speeds,
   steering angle/torque, driver override, buttons, gear, faults, standstill,
   availability, and actuator state.
4. **Lateral:** native OEM control API, enough measured authority, appropriate
   all-speed behavior, good tuning, driver override, rate/torque/angle limits,
   and recovered temporary/permanent fault behavior.
5. **Longitudinal:** clear stock/openpilot ownership, smooth tuning, correct
   acceleration limits, stop-and-go, resume behavior, and preservation of stock
   safety functions where possible.
6. **Perception inputs:** radar/object parsing when the vehicle exposes usable
   data, or an explicit architecture explaining why it does not.
7. **Stock-source replacement:** the original command producer and suppression
   point are known; openpilot is not racing or averaging against an uncontrolled
   stock producer.
8. **HUD/coexistence:** alerts, cruise state, lane state, cancel/resume, and
   stock-visible behavior remain coherent.
9. **Panda safety:** ordinary vehicle safety hook and TX whitelist enforce
   actuator limits and driver override. Panda does not become a second
   application policy engine.
10. **Fault/recovery behavior:** startup, disengagement, ECU reset, CAN loss,
    actuator rejection, and restart behavior are known and testable.
11. **Architecture quality:** normal `CarInterface`/`CarState`/`CarController`
    boundaries, minimal target-specific branches, reusable platform flags, and
    no speculative permission state machine layered over `controlsd`.
12. **Validation:** routes, replay coverage, safety tests, tuning data, and enough
    real driving to support comma's final safety/quality validation.

A port that satisfies only command delivery is at the beginning of this list,
not the end.

## 6. What this means for Toyota TSS3

The right target is not merely "TSS3 steering works." The useful benchmark is:

> **Make a TSS3 Camry look as ordinary to openpilot as a mature TSS2
> Corolla/Camry/Highlander does, even if the transport and authentication below
> that boundary are radically different.**

Concretely, SecOC/freshness, CAN-FD routing, stock-source suppression, and the
new Toyota command vocabulary are target-specific mechanisms. They should be
contained below the ordinary openpilot control contract. They are not reasons to
invent a parallel engagement system.

The benchmark therefore argues against promoting bring-up scaffolding into the
final design: private arming Params, diagnostic-oracle gating, controller-side
permission state, debug-only Panda modes, receiver-semantics policy in Panda, or
special TSS3-only engagement rules. If a target-specific requirement is real,
it should appear at the same architectural layer where an equivalent upstream
vehicle requirement lives.

For the current Camry work the maturity ladder should be read roughly as:

| Stage | Meaning |
|---|---|
| Message accepted | Useful RE milestone only |
| Repeatable lateral actuation | Basic port milestone |
| Correct feedback/fault/driver contract + stock-source suppression | Viable lateral integration |
| Normal CarState/CarController/Panda ownership + tuned all-speed lateral | Good lateral port |
| Correct longitudinal ownership/control + stop-and-go + perception inputs | Complete control integration |
| Normal install/startup/fingerprinting/recovery + validation | Upstream-quality vehicle port |
| Release plug-and-play with ordinary hardware/configuration | Full upstream support |

The current upstream Toyota SecOC taxonomy also gives a useful honesty check:
if a valid installation still requires owner-specific secret recovery, EPS
firmware modification, an unusual cable topology, or another manual provisioning
step, the software may be technically capable while the vehicle remains closer
to **Custom** than ordinary **Upstream** support.

## 7. Primary upstream sources

The important current source locations are:

- `opendbc/README.md` — definition of a complete car port and validation model.
- `opendbc/car/docs_definitions.py` — support taxonomy and generated support
  metrics, including the 1.0 m/s² steering-authority threshold.
- `openpilot/selfdrive/car/docs.py` and `docs/CARS.md` — release-supported vehicle
  surface shown to users.
- `opendbc/car/<brand>/interface.py` — actual per-family control ownership,
  low-speed behavior, alpha-longitudinal availability, radar, and safety setup.
- `opendbc/car/<brand>/values.py` — platform generations, hardware, footnotes,
  feature flags, and model grouping.
- Panda/opendbc safety hooks and tests — the vehicle-specific actuation safety
  contract.

For Toyota-specific implementation details, pair this survey with
[`toyota-openpilot-porting-contract.md`](toyota-openpilot-porting-contract.md).
