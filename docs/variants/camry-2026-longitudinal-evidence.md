# 2026 Camry longitudinal evidence packet and status (WP4)

**Scope:** work package 4 of the Camry openpilot completion plan. The `tss3`
integration branch now contains a native-shape `0x160` controller and Panda
handoff for bench/vehicle testing. Corolla establishes the selected B4:B5
command mapping causally; Camry receiver acceptance remains unobserved, so the
branch is a test candidate rather than a validated Camry longitudinal port.

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

The current branch instead uses the ordinary openpilot ownership shape: it
captures the camera-side 32-byte `0x160`, emits at most once per new camera B2
counter, modifies only signed-15 B4:B5 at 0.001 m/s²/count while actively
controlling above 0.45 m/s, and otherwise relays the camera request byte-exact.
Panda blocks the camera copy only while its normal longitudinal-allowed state
authorizes the replacement and enforces the ordinary −3.5/+2.0 m/s² bounds.
The controller self-limits active requests to ±1.5 m/s².

## Evidence matrix (native bus-1 `0x160` request plane)

| Question | Status | Evidence |
|---|---|---|
| Wire geometry | **established** (firmware-static + captures) | 32-byte PDU; B0:B1 CRC-16/CCITT, B2 mod-256 counter, no secret; `tools/targets/camry/live/camry_frc_request_poc.py` clones/recomputes offline. The recovered init=`0xFFFF`/Data-ID=`0x0160` expression and the contributor's init=`0`/Data-ID=`0x444A` expression are deterministically wire-equivalent for this fixed PDU length. |
| Selected controller field | **Corolla-validated transfer hypothesis for Camry** | The independent Corolla road implementation causally establishes signed-15 B4:B5 at 0.001 m/s²/count. A direct re-read of both retained Camry drives confirms the same fine-grained field is dynamic and acceleration-related, but no modified-B4:B5 Camry response has been tested. |
| Command semantics | **strong observed candidate; synthetic causality open** | In three no-driver-input stock auto-resumes, B12 leaves its stopped baseline and ramps in the acceleration direction 351–433 ms before ego motion while the main stopped `0x160` template remains stable; the protected `0x0CA` result simultaneously rises positive. This is substantially stronger than whole-drive correlation, but a stock trace still cannot prove that modifying B12 alone controls the receiver. |
| Scale/sign | **sign strongly observed; absolute mapping unvalidated** | More-negative B12 accompanies larger positive protected `0x0CA` result and vehicle acceleration, consistent with the earlier r=−0.9517/−0.9894 cross-plane join. Exact B12-count→m/s² calibration and any shaping/nonlinearity remain open. |
| Validity/counter rules | partially bounded | Profile-5 counter/CRC observed; receiver behavior on synthetic frames unknown. |
| Receiver acceptance | **unobserved** | No modified-frame acceptance test exists on this Camry. |
| Source ownership | **FRC transmit side observed; downstream receiver unresolved** | The 2026-09-01 selective normal-Tx suppression run isolates `0x160` as a 40-Hz FRC normal-Tx PDU. Which downstream participant accepts/transforms it, and its exact replacement/fallback contract, remain open. |
| Physical response | **stock causal ordering observed; synthetic response open** | Four captured short stock stops auto-resume without gas/brake/RES/SET; in three instrumented examples B12 ramps before motion and protected `0x0CA` result exceeds +0.5 m/s² 413–503 ms before motion. No modified-`0x160` Camry response has yet been tested. |
| Release/override | **partially closed** | Short-stop auto-resume works natively. After ~5.2–9.3 s stopped, Toyota enters a delayed hold state (`0x08A` B7 `0x67`, `0x66` on accelerator override); all three retained long-hold exits require accelerator input, and hold clears before motion. The command-side hold/release semantic is not yet mapped. |
| Fault behavior | **unobserved for synthetic Camry long** | No Camry modified-`0x160` fault experiment exists. The Corolla port initially faulted at complete standstill; its 2026-09-11 contributor architecture note reports a successor frame-for-frame/camera-counter handoff plus <~1 mph stock relay that validates stop/go externally. That does not close the distinct Camry hold/release contract. |
| Source suppression | **architecture identified; live validation pending** | The stock Toyota-B mapping puts Toyota Bus-1/`0x160` on the CAN0/CAN2 relay pair, permitting ordinary stock-source blocking/replacement while the exact-F33 C7 lateral sideband uses unsplit bus 1. The software remap is implemented; parked vehicle validation is still pending. |

Supporting bounds: the two retained drives give B12↔protected-`0x0CA`
correlation r = −0.9517/−0.9894 — strong association, explicitly **not** a
command calibration. Plain set-speed state (`0x08A B10`, `0x251 B2`) is
insufficient evidence of a writable cruise command. `0x0FE` is the
SecOC-shaped switch PDU (VAR-127) and cannot be forged without the key story.

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
road-proven field and handoff. Camry must first validate modified-B4:B5 receiver
acceptance, then stop/hold release and PCS/AEB coexistence, before this branch
can be described as a working Camry longitudinal port.

## Next evidence steps

1. Run the existing synchronized FRC/Brake request capture during stock DRCC,
   including a short stop, delayed hold, release, and (if naturally observed)
   PCS intervention: FRC `0x792` `1B03..1B07`, Brake `0x7B0` `10A1..10A4`,
   `0x160`, protected `0x0CA`, and all ordinary state on one clock. This should
   bind the stop/hold permissions and request ID/acceleration to the wire without
   guessing from correlation.
2. On restored stock Toyota-B, verify parked that FRC `0x160` appears on both
   sides of the CAN0/CAN2 relay, that the exact-F33 C7 signer sideband still
   reaches EPS on unsplit bus 1, and that ordinary software forwarding preserves
   the native FD format.
3. Once the target-native request field(s) are closed, perform the smallest
   receiver-acceptance test: mutate only those fields in an intercepted live
   stock `0x160`, preserve the stock counter/context, recompute E2E Profile 5,
   and confirm the expected downstream request/result change. Do not make the
   standstill behavior a new openpilot permission system; map only the native
   vehicle semantics required by the normal longitudinal state machine.
4. Explicitly validate PCS/AEB coexistence before calling the path complete.
   The current logs show the OEM arbitration stack and ordinary stop/resume
   behavior, but they do not contain a PCS event that proves emergency authority
   survives request replacement.

**Exit status:** the historical B12 offline generator remains verified evidence,
and the test branch now implements the Corolla-validated B4:B5 request plus the
gap-free stock-Toyota-B replacement topology. For Camry, B4:B5 is an observed
transfer hypothesis: modified-frame receiver acceptance, delayed-hold release,
and PCS/AEB coexistence remain open vehicle tests.
