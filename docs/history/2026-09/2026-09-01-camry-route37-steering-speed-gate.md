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
