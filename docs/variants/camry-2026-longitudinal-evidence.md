# 2026 Camry longitudinal evidence packet and status (WP4)

**Scope:** work package 4 of the Camry openpilot completion plan. The `tss3`
integration branch now contains a native-shape `0x160` controller and Panda
handoff for bench/vehicle testing. Corolla establishes the selected B4:B5
command mapping causally. The September 11 dead-EPS drive establishes that the
protected Camry longitudinal plane responds partially to combined B4:B5+B12
replacement while stock DRCC is unavailable, but the response is clamped and
does not track the requested stopping deceleration. A downstream DRCC-mode gate
therefore remains a live explanation rather than a closed negative.

## Discovery record

This Camry work predates the independent Corolla live report. Commit `6d02fc4`
documented the non-SecOC `0x160` request-plane candidate on 2026-08-31;
`d73baf5` added the offline generator later that day; `1661e5c` then recovered
and implemented the exact Profile-5 integrity contract. Commit `198d8da`
documented the native openpilot integration path on 2026-09-05. The attributed
albinoelephant Corolla field run was reported on 2026-09-10. Its contribution
is independent live validation, not the original discovery or generator. The
contributor's 2026-09-11 architecture/change reference is now retained under
`community/albinoelephant/`;
it documents the Corolla-specific B4:B5 request, Data ID `0x444A`, and the
post-fault handoff design, but the exact source checkout and rlog are still
external.


## Historical stock-ACC configuration (Milestone-A longitudinal arrangement)

Before the current test branch, `TOYOTA_CAMRY_TSS3` set `openpilotLongitudinalControl=False`,
`pcmCruise=True`, Toyota `STOCK_LONGITUDINAL`, and `autoResumeSng=False`; the
current TSS3 `CarController.update()` emits only the exact-F33 C7 lateral
sideband and returns, so Toyota still owns acceleration. Physical RES/SET
buttons and the parsed `0x08A`/`0x251` set-speed state choose `vCruise`;
`radarUnavailable=True` is not a planner blocker (generic radar interface
publishes an empty set; model-lead `radarState` continues). Verified in the WP2
audit replay and stock-harness opendbc `3c79d935`.

The current branch instead uses the ordinary openpilot ownership shape, gated
by the standard Alpha Long toggle: it captures the camera-side 32-byte `0x160`
and emits at most once per new camera B2 counter. Corolla retains its validated
signed-15 B4:B5 mapping at 0.001 m/s²/count. Camry modifies B4:B5 and the
additional inverse signed-7 B12 candidate at 0.1 m/s²/count, while otherwise
relaying the camera request byte-exact. Panda blocks the camera copy only while
its normal longitudinal-allowed state authorizes the replacement and bounds
both Camry request quantities independently. The 2026-09-11 trial below proved
the transport path and disproved B4:B5 alone as a sufficient Camry mapping; the
later dead-EPS trial then observed a limited protected-result response to the
combined encoder under conventional cruise, without the requested physical
stopping behavior.

## Evidence matrix (FRC `0x160` request plane)

| Question | Status | Evidence |
|---|---|---|
| Wire geometry | **established** (firmware-static + captures) | 32-byte PDU; B0:B1 CRC-16/CCITT, B2 mod-256 counter, no secret; `tools/targets/camry/live/camry_frc_request_poc.py` clones/recomputes offline. The recovered init=`0xFFFF`/Data-ID=`0x0160` expression and the contributor's init=`0`/Data-ID=`0x444A` expression are deterministically wire-equivalent for this fixed PDU length. |
| Selected controller field | **B4:B5-alone disproved; combined B4:B5+B12 reaches the protected plane but is insufficient without DRCC** | The independent Corolla road implementation causally establishes signed-15 B4:B5 at 0.001 m/s²/count. Route `000000d1--ad906be282` replaced 10,228 Camry frames with B4:B5 modifications while leaving B12 stock; the protected result continued tracking B12. In route `000000d4--327b2c4bb8`, 1,249 combined replacements changed B4:B5 and inverse signed-7 B12. Protected `0x0CA` responded, but strong requested braking was clamped and did not produce the requested stop-sign response while stock DRCC was unavailable. |
| Command semantics | **partial protected-result influence observed; full command authority open** | In three no-driver-input stock auto-resumes, B12 ramps in the acceleration direction 351–433 ms before ego motion. At the start of the combined trial, openpilot's B12 and protected `0x0CA` moved in the expected direction, but across strong-braking samples requested acceleration correlated only `r=0.276` with the protected result and `r=0.176` with measured acceleration. |
| Scale/sign | **sign supported; conventional-mode shaping/gating unresolved** | Synthetic B12 and protected `0x0CA` result correlate negatively across the complete replacement windows, but when openpilot requested as much as −1.2 m/s² under conventional cruise, the protected result remained roughly −0.15 to −0.34 m/s². This does not prove a literal 0.1 m/s²/count physical scale or full authority. |
| Validity/counter rules | **synthetic frames reach downstream processing** | Profile-5 counter/CRC are observed; one-for-one synthetic frames paced from the live camera counter influence the protected plane without an integrity fault. Gap, replay, authority, and fault thresholds remain untested. |
| Receiver acceptance | **partial processing observed; DRCC-mode gate remains open** | FRC DRCC attempts were rejected and the successful cruise latch was conventional (`0x251` B0=`0x90`). Panda suppressed the stock downstream copy and transmitted the combined replacements, but the requested stopping deceleration was not applied. The explicit observed mode states are `0x251` B0 `0x88/0x90` for conventional available/active versus `0xA0/0xC0` for DRCC available/active. |
| Source ownership | **FRC transmit side observed; downstream receiver unresolved** | The 2026-09-01 selective normal-Tx suppression run isolates `0x160` as a 40-Hz FRC normal-Tx PDU. Which downstream participant accepts/transforms it, and its exact replacement/fallback contract, remain open. |
| Physical response | **combined synthetic stopping response negative without DRCC** | Four captured short stock stops auto-resume without gas/brake/RES/SET; in three examples B12 ramps before motion and protected `0x0CA` exceeds +0.5 m/s² 413–503 ms before motion. In the combined trial, measured acceleration closely followed the limited protected result (`r=0.912` over strong-braking samples), not openpilot's substantially stronger requested deceleration; the driver directly observed that the car did not slow for the modeled stop sign. |
| Release/override | **partially closed** | Short-stop auto-resume works natively. After ~5.2–9.3 s stopped, Toyota enters a delayed hold state (`0x08A` B7 `0x67`, `0x66` on accelerator override); all three retained long-hold exits require accelerator input, and hold clears before motion. The command-side hold/release semantic is not yet mapped. |
| Fault behavior | **no request-path fault observed; standstill remains open** | The moving combined-request trial completed without an observed request-integrity/system-malfunction fault. The Corolla port initially faulted at complete standstill; its 2026-09-11 contributor architecture note reports a successor frame-for-frame/camera-counter handoff plus <~1 mph stock relay that validates stop/go externally. That does not close the distinct Camry hold/release contract. |
| Source suppression | **live transport validated** | Route `000000d1--ad906be282` retained all camera-side bus-2 templates while the active replacement windows had no competing native bus-0 copy. Across segments 3–6 and 9–12, openpilot emitted 10,259 bus-0 `0x160` frames paced by the camera counter; 10,228 carried modified B4:B5, and only 13 transient Panda rejects occurred at control transitions. Route `000000d4--327b2c4bb8` repeats the one-for-one handoff for 1,249 combined replacements. |

## 2026-09-11 live B4:B5 replacement trial

Route `000000d1--ad906be282`, segments 3–6 and 9–12, is the first retained
Camry drive with active synthetic `0x160` replacement on restored stock
Toyota-B. Both driver attempts occurred in this one ignition route. The branch
at the time incorrectly forced `openpilotLongitudinalControl=True`, so changing
the Alpha Long setting between attempts did not distinguish them; the branch
was subsequently corrected to advertise `alphaLongitudinalAvailable` and honor
the standard toggle on the next `CarParams` initialization.

The software control and transport path did run:

- `CC.longActive` covered about 160 seconds in segments 3–6 and about 178
  seconds in segments 9–12; Panda `controlsAllowed` followed the stock cruise
  latch.
- The planner/controller requested −1.28 to +0.542 m/s².
- 10,259 bus-0 `0x160` replacements were sent. Of these, 10,228 differed from
  the nearest stock camera template only in the Profile-5 CRC and B4:B5; their
  decoded B4:B5 request matched `CC.actuators.accel` to 0.001 m/s² rounding.
- The camera-side bus-2 source remained observable as the live template while
  the competing stock downstream copy was suppressed. Panda recorded 19,197
  bus-0 TX returns and 13 rejected transition-race attempts across the eight
  analyzed segments.

The downstream result did not support the Corolla-to-Camry field transfer. In
two continuous representative active minutes, protected `0x0CA` B7:B8 had
correlation `r=0.596` and `r=0.507` with injected B4:B5, but `r=-0.916` and
`r=-0.890` with the untouched stock signed-7 B12. The moderate B4:B5
correlation is expected because openpilot and Toyota were responding to the
same vehicle-speed error; it is not evidence of synthetic causality. Together
with the driver's direct observation that behavior did not change, this is
strong negative evidence for **B4:B5 alone** as the Camry command. The corrected
test encoder therefore retains the fine B4:B5 request and also changes B12 as
`round(-accel / 0.1)`. The sign and 0.1-unit choice are supported by both the
stock cross-plane regressions and the GTS+ FRC output-acceleration vocabulary;
synthetic causality and any additional companion semantics still require the
next controlled drive.

Supporting bounds: the two retained drives give B12↔protected-`0x0CA`
correlation r = −0.9517/−0.9894 — strong association, explicitly **not** a
command calibration. Plain set-speed state (`0x08A B10`, `0x251 B2`) is
insufficient evidence of a writable cruise command. `0x0FE` is the
SecOC-shaped switch PDU (VAR-127) and cannot be forged without the key story.

## 2026-09-11 combined-request trial with stock DRCC unavailable

Route `000000d4--327b2c4bb8` was captured after the EPS stopped providing its
normal `0x030` traffic. MAIN attempts first produced the already-observed
DRCC-unavailable/rejection state; the later successful latch was conventional
cruise (`0x251` B0=`0x90`), not stock DRCC. This makes the route a direct test
of whether the downstream longitudinal stack requires the FRC's healthy-DRCC
state before granting full authority to a replaced request.

During two `CC.longActive` windows, openpilot emitted **1,249**
combined B4:B5+B12 `0x160` frames at the camera-counter rate. The Panda relay
continued to expose the live camera-side `0x160` template and made the
replacement the sole downstream copy while longitudinal control was allowed.
No synthetic EPS `0x030`, FRC health response, or broad cruise-status spoof was
present.

At the start of the first control window, the relationship is directly visible:

```text
openpilot requested accel       -0.542  ...  +0.360 m/s²
synthetic 0x160 B12                  +5  ...      -4 counts
protected 0x0CA result          -0.320  ...  +0.397 m/s²
```

Across both windows, synthetic B12 versus the protected result gives
`r=-0.705` at nearest time and `r=-0.730` at +100 ms. That proves influence on
the protected plane, not full authority. Over the strong-braking subset,
openpilot requested as much as `-1.2 m/s²`, while the protected result remained
roughly `-0.15..-0.34 m/s²`; requested acceleration correlates only `r=0.276`
with the protected result and `r=0.176` with measured acceleration. Measured
acceleration instead tracks the limited protected result at `r=0.912`. The
driver's direct observation closes the practical consequence: the car did not
perform the modeled stop-sign deceleration.

The explicit normal-CAN mode discriminator is `0x251` B0: retained healthy
DRCC uses `0xA0/0xC0` for available/active, while the dead-EPS route uses
`0x88/0x90` for conventional available/active. The next middleman experiment
therefore preserves the live conventional operating latch and request context,
but follows each live `0x251` with a byte-exact clone changing only
`0x88 -> 0xA0` or `0x90 -> 0xC0`. A positive result would identify downstream
DRCC mode as the missing authority gate without requiring the faulted FRC to
change its internal state.

### 2026-09-11 retained stop/resume audit

The long 2026-09-04 routes contain more longitudinal state than the original WP4
matrix used. A direct rlog reduction of routes `0000003b--62262eb7a1` and
`0000003c--97b9e7a69a` finds seven cruise-enabled stops longer than 0.4 s. Four
short stops, lasting **2.893–4.288 s**, resume with cruise still enabled and
with **no gas, brake, RES+, or SET- input within one second of motion**. Three
longer stops, lasting **6.941–13.079 s**, enter Toyota's delayed stock-ACC hold
state after **5.223–9.254 s** stopped. Those are the already-source-real
`0x08A` `CRUISE_SUBSTATE_2=0x67` episodes (`0x66` during accelerator override).
All three long-hold exits clear on accelerator input before ego motion; none has
a RES+/SET- edge.

The short no-input resumes are especially useful for `0x160`. In three examples
with complete local context:

| route / motion time | stopped B12 baseline | first persistent B12 departure | protected `0x0CA` result > +0.5 m/s² | driver input |
|---|---:|---:|---:|---|
| `3b` / 5122.256 s | −1 | **351 ms before motion** | **463 ms before motion** | none |
| `3c` / 9068.054 s | +1 | **404 ms before motion** | **413 ms before motion** | none |
| `3c` / 9147.517 s | 0 | **433 ms before motion** | **503 ms before motion** | none |

In each case B12 ramps more negative as the protected result rises positive and
the vehicle starts. During the last roughly one second stopped, the primary
`0x160` application template is otherwise stable (`B3=0x82`, `B4:B5=0x8000`,
`B6=0x40`, `B7=0x03`, `B8:B9=0x4DE8`, `B11=0`, `B15=0x80`, `B16=2`; B10
is route/state dependent, and B13/B14 continue their independent dynamic
pattern). This does not turn a stock correlation into a modified-frame receiver
proof, but it materially strengthens B12 as the request-related scalar: the
change precedes physical motion without any driver resume command.

The delayed-hold transition is a separate state boundary. At the exact
`0x08A` B7 `0x47 -> 0x67` edge, two of the three episodes have no `0x160`
application-byte change at all; the third changes only already-dynamic/cyclic
fields. The protected `0x0CA` result is already zero before hold and remains
zero through it, with the other two acceleration-like words settled near
`+3.75` and `+0.665 m/s²`. An all-Bus-4 bit sweep finds no one ordinary CAN bit
that makes a repeatable high-confidence transition at all three hold onsets.
Likewise, the apparent Bus-1 `0x230` candidates are ramps/counters rather than a
discrete hold edge. The captured hold therefore is not presently encoded as a
simple newly identified `0x160` or `0x0CA` flag; it may be downstream/local or
carried in a still-unmapped/request-side field.

That distinction matters to openpilot stop-and-go. Current `LongControl` will
stay in its stopping state while `CarState.cruiseState.standstill` remains true.
The current Camry parser intentionally maps the delayed Toyota hold state to
that standard field. The retained logs prove that ordinary **short-stop
stop-and-go is already compatible with the stock request pipeline**, because
four stops restart automatically before delayed hold. They do **not** yet prove
openpilot can automatically release Toyota's delayed long-stop hold. Current
GTS+ gives the exact semantic leads to close that gap: FRC DID `0x1B07` exposes
Brake-Hold Control Prohibited, Stop Control Permission, and Brake-Usage-Limit
Permission, while PCS request record `5280` additionally carries EPB, accelerator-
override-prohibition, low-priority, shift-range, and braking/driving-force
fields.

The retained normal rlogs do not contain synchronized `0x1B03..0x1B07` /
Brake `0x10A1..0x10A4` reads, nor a PCS/AEB intervention suitable for proving
that PCS wins over a replaced cruise request. Those remain targeted-live
questions. For implementation, the least-destructive candidate is therefore a
1:1 relay replacement of each live FRC `0x160`: preserve the current stock
application/context fields and B2 counter, modify only the request field(s) that
are positively recovered, recompute E2E Profile 5, and leave Toyota's downstream
arbitration/SecOC participants untouched.

## Branch implementation and validation boundary

`controlsd` owns `CC.longActive`/`CC.actuators.accel`; Toyota `CarController`
owns encoding and camera-counter pacing; Panda owns the TX whitelist, normal
longitudinal bounds, and selective forwarding. No second permission state or
legacy Toyota PCM compensation loop was added. Corolla can exercise the
road-proven field and handoff. Camry combined-request influence is observed at
the protected plane under conventional cruise, but full requested authority is
not. The exact-Camry/dead-EPS test branch now adds a bounded `0x251` middleman:
one follow-up per live stock display frame, only the observed conventional-to-
DRCC B0 mapping, and active state permitted by Panda only while the genuine
`0x08A` operating latch authorizes longitudinal control.

## Next evidence steps

1. Parked first, engage conventional cruise and verify that each native
   `0x251 0x88/0x90` is followed by the synthetic `0xA0/0xC0` state without a
   system fault. Then repeat the bounded moving test and join synthetic `0x251`,
   synthetic `0x160`, protected `0x0CA`, wheel-speed acceleration, and pedals.
   The discriminator is whether the prior conventional-mode braking clamp clears.
2. Run the existing synchronized FRC/Brake request capture during stock DRCC,
   including a short stop, delayed hold, release, and (if naturally observed)
   PCS intervention: FRC `0x792` `1B03..1B07`, Brake `0x7B0` `10A1..10A4`,
   `0x160`, protected `0x0CA`, and all ordinary state on one clock. This should
   bind the stop/hold permissions and request ID/acceleration to the wire without
   guessing from correlation.
3. Explicitly validate PCS/AEB coexistence before calling the path complete.
   The current logs show the OEM arbitration stack and ordinary stop/resume
   behavior, but they do not contain a PCS event that proves emergency authority
   survives request replacement.

**Exit status:** the historical B12 offline generator remains verified evidence,
and the test branch now implements the Corolla-validated B4:B5 request plus the
gap-free stock-Toyota-B replacement topology. For Camry, combined B4:B5+B12
influence is observed at the downstream protected plane, but the requested
stopping authority is absent without DRCC. The bounded `0x251` mode-middleman,
delayed-hold release, and PCS/AEB coexistence remain open vehicle tests.
