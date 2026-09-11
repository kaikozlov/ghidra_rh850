# 2026 Camry longitudinal evidence packet and status (WP4)

**Scope:** work package 4 of the Camry openpilot completion plan. The
**Milestone-A longitudinal configuration** (stock Toyota ACC retained) is the
current fork state; this names the longitudinal ownership arrangement only and
does **not** mean Milestone A itself is accepted (lateral qualification remains
blocked). This packet assembles the Camry-specific evidence matrix for native
openpilot longitudinal control. The offline wire encoder is implemented; the
remaining rows govern promotion into a live Camry controller. No injection or
interception wiring is prescribed.

## Discovery record

This Camry work predates the independent Corolla live report. Commit `6d02fc4`
documented the non-SecOC `0x160` request-plane candidate on 2026-08-31;
`d73baf5` added the offline generator later that day; `1661e5c` then recovered
and implemented the exact Profile-5 integrity contract. Commit `198d8da`
documented the native openpilot integration path on 2026-09-05. The attributed
albinoelephant Corolla field run was reported on 2026-09-10. Its contribution
is independent live validation, not the original discovery or generator.

## Current stock-ACC configuration (Milestone-A longitudinal arrangement)

`TOYOTA_CAMRY_TSS3` sets `openpilotLongitudinalControl=False`,
`pcmCruise=True`, Toyota `STOCK_LONGITUDINAL`, and the TSS3
`CarController.update()` returns after the B6/brake-cancel path — Toyota owns
acceleration. Physical RES/SET buttons and the parsed `0x08A`/`0x251`
set-speed state choose `vCruise`; `radarUnavailable=True` is not a planner
blocker (generic radar interface publishes an empty set; model-lead
`radarState` continues). Verified in the WP2 audit replay and the upstream
diff.

## Evidence matrix (candidate: native bus-1 `0x160` E2E Profile-5 B12)

| Question | Status | Evidence |
|---|---|---|
| Wire geometry | **established** (firmware-static + captures) | 32-byte PDU; B0:B1 CRC-16/CCITT, B2 mod-256 counter, Data ID = CAN ID, no secret; `tools/targets/camry/live/camry_frc_request_poc.py` clones/recomputes offline |
| Command semantics | **hypothesis** | B12 is a high-value signed-7 candidate; physical command scale and companion request fields not closed |
| Scale/sign | **unvalidated** | No independently labeled acceleration joins; correlation ≠ calibration |
| Validity/counter rules | partially bounded | Profile-5 counter/CRC observed; receiver behavior on synthetic frames unknown |
| Receiver acceptance | **unobserved** | No modified-frame acceptance test exists |
| Source ownership | **unresolved** | Producer/source direction not proved; competing interpretations retained (port report §7) |
| Physical response | **unobserved** | No bench evidence |
| Release/override | **unobserved** | — |
| Fault behavior | **unobserved** | — |
| Source suppression | **architecture identified; live validation pending** | The current lateral-development repin leaves Toyota Bus-1 on unsplit Panda CAN1. Undoing that repin restores Toyota Bus-1/`0x160` to the stock Toyota-B CAN0/CAN2 relay pair, allowing a bus-0 replacement to block the stock bus-2 copy. No added split is proposed; verify sides and forwarding after restoring the stock pin mapping. |

Supporting bounds: the two retained drives give B12↔protected-`0x0CA`
correlation r = −0.9517/−0.9894 — strong association, explicitly **not** a
command calibration. Plain set-speed state (`0x08A B10`, `0x251 B2`) is
insufficient evidence of a writable cruise command. `0x0FE` is the
SecOC-shaped switch PDU (VAR-127) and cannot be forged without the key story.

## Architecture agreed for the eventual implementation (upstream shape)

When — and only when — semantics, receiver acceptance, and suppression are
closed: `controlsd` keeps owning `CC.longActive`/`CC.actuators.accel`; the
TSS3 Toyota `CarController` encodes the recovered FRC-side request PDU;
Panda applies ordinary longitudinal command bounds and the TX whitelist;
`pcmCruise` can remain initially. Capability flags, encoder coverage, and
safety coverage must agree. Do not reuse the legacy Toyota PCM compensation
loop blindly; direct-versus-shaped `actuators.accel` mapping depends on the
final recovered `0x160` semantics. Flipping
`openpilotLongitudinalControl=True` alone transmits nothing (current TSS3
safety whitelists only `0x0B6` bus0 and `0x101` bus2).

## Next evidence steps (passive, no vehicle-control transmission)

1. Passive stock captures joined with driver events, cruise state, candidate
   values, measured speed/acceleration, braking state, and FRC diagnostic
   labels (`0x1905/0x1914` engagement oracles already validated on this car),
   with explicit timing uncertainty.
2. Record which competing interpretations remain live after each join; a
   down-gradient correlation must not silently promote B12 to "command".
3. A supported receiver interface and documented ownership arrangement are
   prerequisites for physical validation.
4. Restore the normal Toyota-B pin mapping and verify that `0x160` appears on
   both sides of the CAN0/CAN2 relay while the F33 signer sideband reaches EPS
   on unsplit Panda bus 1.

**Exit status:** the byte-exact offline message generator is implemented and
verified. Camry semantics and ownership remain hypotheses, and live Camry
controller integration is intentionally not wired. The replacement topology is
identified but not yet live-validated. Milestone B is blocked on the remaining
Camry-specific matrix rows, not on CRC/message-construction work or a need for
custom harness hardware.
