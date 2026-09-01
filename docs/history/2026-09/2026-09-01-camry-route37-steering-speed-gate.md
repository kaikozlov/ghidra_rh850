# 2026-09-01 Camry route 37 — apparent steering speed gate

**Status:** observational route analysis. This note is deliberately bounded to the pulled loggerd route and the immediately preceding F33 admission probe. It does not promote `0x08A` to an EPS input or an arbitration/grant signal.

## Source

The newest comma route after the 2026-09-01 Gate-2 stage-2 field work was:

- route: `00000037--dec6fe39cb`
- comma source: `/data/media/0/realdata/00000037--dec6fe39cb--{0..6}/rlog.zst`
- local copy: `/Users/kai/dev/inspect/logs/camry-2026/2026-09-01/00000037--dec6fe39cb/rlog-{0..6}.zst`
- first segment file time: `2026-09-01 23:11:28 UTC` (`18:11:28 America/Chicago`)

SHA-256, in segment order 0..6:

```text
f5a5d50958047dcab53956254b11672ad607385d712b1e525cc7b58e68676634
8cb2eb3f2358971bc0feda816fbff35c69f0d6c0b5073f7020f9fe6bbf302530
da6af2b9e12076eaf801c8b3bc902100a10a3cfde14028b7bf43bb4f2cb8d798
99d0aba120fe9df779ce06b356d229973c6aa2a277799fef8dbacb2428e58658
88f5744d3048acc7821c179f76bfbcd9dad5515494f2dfa5909315aec58d78c7
821ce90c225ddf4a53e07920f7899afd947838aa2c018ca7342f5f38af13916d
687e8ea8608ccd13325f8befee2b281ad6d678a6955843f6abd3702f80ad5eb3
```

The route contains seven `carControl.latActive` intervals. Speeds below are nearest `carState.vEgo` converted to mph; `0x08A` state is B21 low 6 bits on the retained upstream/request-plane publication.

| interval | route-relative time | speed | observed `0x08A` request state |
| --- | ---: | ---: | --- |
| 1 | 23.868–31.061 s | 24.5–26.2 mph | ID0 initially; switches to ID11 at 25.611 s / 25.83 mph |
| 2 | 62.813–111.040 s | 42.9–45.5 mph | ID11 throughout |
| 3 | 130.823–165.355 s | 22.6–26.3 mph | ID0 throughout |
| 4 | 171.827–199.478 s | 23.0–24.6 mph | ID0 throughout |
| 5 | 222.989–253.442 s | 43.1–46.2 mph | ID11 throughout |
| 6 | 254.538–286.938 s | 42.3–45.7 mph | ID11 throughout |
| 7 | 306.443–321.945 s | 26.2–27.6 mph | ID0 throughout |

The same split is independently visible in the neighboring native state carriers: the ID0 neighborhood windows use the `0x412=0x12` / `0x371=(0x20,1)` family, while the sustained ID11 road-speed windows use `0x412=0x14` / `0x371=(0x30,3)`.

## Openpilot is not applying a ~25 mph lateral cutoff

The exact Camry TSS3 implementation loaded for this route explicitly advertises `minSteerSpeed = 0` and `steerAtStandstill = True`; the TSS3 Camry controller sets `lat_active = CC.latActive` and builds active B6 ID11 without a vehicle-speed predicate. The route agrees with the implementation:

- B6 is transmitted whenever `latActive` is true in both low- and high-speed intervals.
- The route contains 18,456 B6 `sendcan` frames.
- `can` contains 18,447 successful Panda B6 TX echoes (`src=128`) and only 9 rejected echoes (`src=192`).
- 11,329 successful B6 TX echoes occur below 30 mph.
- There are zero native incoming B6 frames on `src=0/1/2`; all route B6 observations outside `sendcan` are Panda TX results.
- `onroadEvents` contains **no `belowSteerSpeed` event**.

The only steering-specific control events are two `steerSaturated` events during low-speed interval 3, when openpilot is still actively requesting steering and the Toyota request-plane witness is ID0:

- 144.418 s: 22.99 mph, desired `-25.2 deg`, actual `-6.5 deg`
- 144.810 s: 22.92 mph, desired `-26.8 deg`, actual `-20.3 deg`

Those events are consistent with openpilot asking for angle without obtaining the expected tracking. They are not evidence by themselves that B6 was partially admitted, because `carState.steeringAngleDeg` also contains manual/plant motion.

## The 25-versus-45 mph observation is confounded with Toyota request state

The sustained high-speed intervals in which steering was perceptible all coincide with Toyota's existing request-plane state ID11. The long neighborhood intervals in which steering was not perceptible coincide with Toyota request-plane ID0 even though openpilot keeps transmitting active B6 ID11.

The first active interval is especially important because it contains ID11 at only about 25–26 mph: openpilot is already active before the request-plane transition, B6 is already being transmitted, and `0x08A` changes ID0→ID11 at 25.83 mph while speed stays in the same narrow neighborhood-speed band. This is incompatible with a simple explanation of “the steering path is hard-disabled until roughly 45 mph.” It does **not** prove the final actuator grant follows `0x08A`; current project evidence classifies `0x08A` as a request-plane witness, not an EPS input or arbitration-result/active-grant record.

Exact F33 static recovery is consistent with that bounded conclusion. `CEFA4` handles B6 communication/status health and `CEFFC` maps an already-delivered B6 Target Lateral ID to `FEBECB00`; neither recovered function contains a vehicle-speed predicate. Other downstream speed-dependent conditioning is not globally excluded by this observation.

## Join to the immediately preceding Gate-2 experiment

This drive began only about seven minutes after the post-stage-2 stationary B6 admission probe. The stage-2 patch had persisted correctly, but the 18:04 local admission run still sent/echoed 84/84 B6 frames without delivering the candidate into the exact-F33 application snapshot:

- requested ID11, target raw `-10`
- snapshot Target Lateral ID remained `0`
- snapshot target raw remained `7`
- controller bank remained `7`
- controller enabled and communication status healthy
- verdict: `payload_not_delivered`, `admitted=false`

Therefore there was no demonstrated general B6 admission immediately before route 37. Joined with the route's low-speed behavior, the best-supported explanation is that the steering perceived in the 43–46 mph intervals was the vehicle's existing Toyota lateral-control path operating while Toyota's own request plane was active, rather than openpilot acquiring authority only above a speed threshold.

A narrower alternative remains open: some moving-only condition could change B6 admission after the stationary probe. Route logging cannot decide that because it does not record the internal F33 ladder cells while moving. The decisive moving discriminator would be synchronized observation of the generated-COM cells and application snapshot (`FEBE80BC/80B8 -> FEBEADB0/FEBEAE90 -> FEBECB00`) while preserving the request-plane state and speed context.

## Conclusion

For route `00000037--dec6fe39cb`, there is **no evidence of an openpilot/Panda ~25 mph steering gate**. Openpilot remains lateral-active and transmits B6 below 30 mph. The apparent speed dependence tracks Toyota's own lateral request-state changes almost perfectly, and the same route contains an ID11 interval near 25 mph. The unresolved problem remains B6 admission/authority, not a configured minimum steering speed.

## Follow-up: B6 construction audit versus the exact-F33 receiver

A direct audit of all 18,456 route-37 B6 sends does not reveal a concrete application/wire-construction error in the fields whose receiver contract is closed. Relative to the nearest native bus0 `0x00F`, the transmitted FV4 reset-low2 matches **18,456/18,456** frames. The B6 application sequence advances exactly `+1 mod 64` on **18,455/18,455** consecutive pairs, and the transmitted FV4 message-low2 likewise advances `+1 mod 4` on **18,455/18,455** pairs. All 16 FV4 values occur. No target exceeds the exact-F33 `±1745` raw envelope, and there are **zero** active-ID11 target-delta violations of the exact `78 * effective_gap` bound. The only two application companion shapes are the intended cleaned forms: inactive `ID0 / B6=0x04 / B8=B9=0`, and active `ID11 / B6=0 / B8=B9=100`; B10 is zero in both.

The exact-F33 protected profile independently confirms the wire partition: B0..B27 are the authenticated application, B28[7:4] is FV4 (`message_low2 || reset_low2`), and B28[3:0] plus B29..B31 are CMAC-MSB28. Target Lateral ID is B3[5:0], target steering angle is signed B4:B5, and the application sequence is B7[5:0]. Thus the current sender agrees with the recovered receiver geometry. The secondary fields remain **not stock-template-validated** because no native accepted F33 B6 has been captured; `B6[2]=0, B8/B9=100/100` is a deliberate controller candidate derived from receiver semantics, not a Toyota stock transcript. Those fields are consumed after protected-PDU delivery and currently provide no static explanation for failure before PDU44 reaches generated COM.

The intentionally invalid part of the current candidate is still the CMAC28: `build_b6_zero_marker_frame` transmits a correct-looking FV4 with the other 28 trailer bits zero. Fresh read-only recovery now identifies an earlier control-flow boundary that is more important than the later Gate-2 patches. `FUN_0008F98C` calls `FUN_0008F746(profile)` and calls `FUN_0008F906(profile)` **only if `8F746` returns zero**. `FUN_0008F746` submits command 7 through `FUN_0008F676 -> FUN_00089C98`; `89C98` bounded-polls the crypto completion and returns `0` for successful verification, `1` for a completed nonzero result, and `2` for timeout/busy. `8F746` converts the ordinary nonzero result into its `0x101` failure path and returns before `8F906`. Therefore an ordinary synchronous zero-MAC28 verification failure can bypass **all** of the development modifications at `8F930/8F948/8F952`; those sites are downstream of the earlier return. This is presently a stronger explanation for non-delivery than any known B3..B10 construction mismatch.

One live-probe interpretation also needs caution. The current stage-3 stationary probe labels ID0 `com_payload_delivered=true` when the COM target is within ±1 raw of the requested target. In that run the baseline was already `ID0/raw104` and the transmitted ID0 target was `raw105`, so an unchanged stale baseline satisfies the predicate. The later ID11 phase clearly did **not** update COM (`ID0/raw104` remained), but the apparent positive ID0-vs-negative-ID11 contrast is not by itself proof of content-dependent acceptance.

Finally, there is a latent issue for any future **real-CMAC** sender: the current Camry TSS3 branch maintains a full local `message_counter` but returns before the generic SecOC reset-counter re-anchor path. That is immaterial to the present zero-MAC28 experiment because only the low two message bits are transmitted and the MAC is intentionally zero. It would matter for correct CMAC generation after a new authenticated `0x00F` reset epoch, because the receiver seeds the new epoch's full B6 message8 from the transmitted low2 rather than preserving an arbitrary sender-local high six bits.

Current conclusion: do not attribute the rejection to a known application-field mismatch. The first unresolved boundary is the **pre-`8F906` command-7 failure path** (or, alternatively, generation of a genuinely valid slot-4 CMAC); stock B6 companion/template capture remains useful for post-authentication semantics but is not the leading explanation for the present PDU non-delivery.
