# 2026 Camry openpilot capability matrix and qualification handoff (WP6)

**Scope:** work package 6 of the Camry openpilot completion plan: the
consolidated capability matrix, qualification-record requirements, and honest
support status for Milestones A and B. This is a tracking document; a row is
only as strong as the evidence link behind it.

Grades follow docs/status/FINDINGS.md. Final audited software identities on
2026-09-05: fork `kai` `45b57159ed004405004f95403dbd9912d26ace90`,
opendbc `8c1124fe37f146e2282ba68676ffa82cac4902f8`, Panda
`5236f3708bfd833942c0e0f79a7fc6d8255fbe60`; recorded software that produced
the September corpus: opendbc `c7a62eaf7a9d5049aa7c64b7788e80a80668a35c`.
The current upstream design pins are openpilot `a4f7c50d2a52a5865a40da2ebc5004c82929a0ef`
and opendbc `3e92d112129507debe45364891954db70238997a`; the detailed comparison is in
the WP2 audit. Status vocabulary: `not started / in progress / reviewable /
accepted / blocked`.


| Capability | Status | Evidence link | Blocking dependency |
|---|---|---|---|
| Platform identification (F181-exact, census fallback) | reviewable | camry-2026-tss3-integration-audit.md; `test_tss3_camry.py` | — |
| Vehicle state decode (angle/torque/gear/READY/speed) | reviewable | audit doc; real-frame replays; live-baseline §4–§8 | torque sign/direction dynamic confirmation |
| Stock ACC (Milestone A longitudinal) | reviewable | audit doc; `0x0FE`/`0x08A`/`0x251` replay tests | — |
| Driver interaction (nudge → lane change) | reviewable (software) / blocked (validation) | VAR-125 fix + replay audit (0 → 171 pressed on identical input) | on-vehicle confirmation of 1.2 N.m threshold and torque sign |
| Lateral actuation (B6 command path) | blocked | VAR-124/125/126: sender wire-exact, transport exonerated, wheel tracks stock request when divergent; zero `laneChange` events under the recorded bug | EPS receiver admission/ingress (bench spec WP3); Gate-2 dependency makes current path non-deployable |
| Native openpilot longitudinal (Milestone B) | blocked | camry-2026-longitudinal-evidence.md | `0x160` semantics/ownership; receiver acceptance; source suppression |
| Radar/perception configuration | reviewable | `radarUnavailable=True` (opendbc `interface.py` TSS3 flag) with model-lead `radarState` is the upstream-normal arrangement — port report §7, WP4 doc | none for stock-ACC operation |
| Reproducible passive evidence (WP1) | accepted | `camry_20260904_stock_steering_report.json` + source manifest + tracked source-derived fixtures + exact original-output/health verifier (**93/93** checks) | external private logs only for regenerating the already-pinned full corpus |
| Bench qualification (lateral) | blocked | camry-2026-bench-validation-spec.md | no legitimate supported steering command interface identified; qualified bench apparatus + independent angle/driver-input instruments also missing |
| Controlled vehicle validation | blocked | this document | bench acceptance first, then qualified operator/test-site arrangements |

## Completion-plan work-package closure

This table closes the implementation plan without converting unavailable
physical evidence into software success:

| Deliverable | Owner | Source revision / corpus | Evidence link | Status | Blocking dependency |
|---|---|---|---|---|---|
| WP1 — reproducible September report | analysis repository | three 2026-09-04 routes; 253 compressed rlogs individually SHA-pinned in the manifest; parser fork `45b57159…` | `tools/analyze_camry_20260904_stock_steering.py`; generated manifest/report; tracked fixtures; `tests/verify_camry_20260904_stock_steering.py` | **accepted** | External private rlogs are required only to regenerate the already pinned full-corpus result. The previously "unlocated" original reducer was recovered under disposable `build/tmp/` and used to restore its exact grid/predicates. |
| WP2 — interface replay/upstream review | kai-openpilot/opendbc integration | proposed fork `45b57159…` / opendbc `8c1124fe…` / Panda `5236f370…`; recorded opendbc `c7a62eaf…`; upstream openpilot `a4f7c50d…`, opendbc `3e92d112…` | camry-2026-tss3-integration-audit.md; `tools/replay_camry_tss3_carstate_revisions.py`; Camry/opendbc/libsafety tests | **reviewable** | Physical `0x030` torque sign/direction and final driver threshold remain unvalidated. |
| WP3 — steering evidence and bench specification | maintainer + qualified controls/bench owner | exact F33/VAR-124–129 evidence; stock and Gate-2-modified firmware explicitly separated | camry-2026-bench-validation-spec.md | **blocked (valid WP3 exit)** | No legitimate supported steering command interface satisfying the plan; qualified bench apparatus, independent output-angle measurement, and calibrated driver-input measurement also missing. |
| WP4 — native longitudinal milestone | analysis first; kai-openpilot/opendbc only after evidence closes | retained Camry captures + FRC diagnostics; candidate bus-1 `0x160` Profile-5 evidence | camry-2026-longitudinal-evidence.md | **blocked; implementation intentionally withheld** | `0x160` semantics/scale, receiver acceptance, producer/ownership, physical response, and stock-source suppression unresolved. Stock ACC remains the Milestone-A longitudinal arrangement. |
| WP5 — car-kit documentation/packaging | analysis repository | exact F33 historical stage/observer/bridge artifacts already pinned by the kit manifest | `exploit/ephemeral_runtime/camry_f33_b6_observer_runbook.md`; `tools/build_camry_f33_car_kit.py`; stationary-probe verifier | **accepted for packaging scope** | None for documentation/packaging; the package deliberately does not establish physical control or deployability. |
| WP6 — qualification and handoff | integration maintainer | the WP1–WP5 source revisions/evidence above | this capability matrix + WP2/WP3/WP4 packets | **reviewable; physical validation blocked** | WP3 bench/interface acceptance first, then controlled-vehicle qualification with exact tested software/firmware/harness identities and an agreed test specification. |

Thus every repository-side action in the plan has a durable implementation or
an explicit evidence-backed blocked exit. `blocked` is not treated as
`accepted`: Milestones A and B remain incomplete.

## Qualification-record requirements

Any controlled vehicle validation combines the replay evidence with bench
acceptance first, uses a qualified operator and an appropriate closed test
environment with an agreed test specification, and records:

- tested software (exact fork/submodule revisions), EPS firmware state
  (stock vs Gate-2-patched — never conflated), harness arrangement;
- supported operating envelope (speed, load, temperature, session state);
- response, release, override, fault-recovery results against pre-set limits;
- known limitations and recovery behavior observed.

Tuning happens only after the intended controller demonstrably influences the
plant; any material interface or safety change triggers a retest of affected
behavior. Ordinary driving logs never substitute for missing bench
acceptance, and this repo's packaging-suite pass (WP5) is never reportable as
physical validation.

## Verification surface for future changes

Upstream checks for modified opendbc/openpilot code (fork `test.sh`,
libsafety suites, `car_diff.py`); in this repository `tools/test list`,
`tools/test plan`, `tools/test` with the existing verification registry — no
new Make wrapper or registry was added by this work. New RE conclusions go to
the owning canonical report plus FINDINGS with scope and grade; disproved
durable claims go to CORRECTIONS. Generated evidence regenerates from tracked
or explicitly declared external inputs (the 2026-09-04 corpus path is
declared in the WP1 manifest).

## Honest support statement (as of 2026-09-05)

- **Milestone A (validated lateral + stock ACC): not complete.** The software
  side is reviewable (identification, state decode, stock ACC, driver-state
  fix with regression tests), but lateral *actuation* has no receiver
  acceptance and no bench validation; the lane-change interaction fix is
  pending physical threshold/sign confirmation.
- **Milestone B (native longitudinal): not complete; no physical evidence.**
  The candidate carrier is pinned; semantics/ownership/acceptance/suppression
  remain hypotheses per the WP4 matrix.
- Public/upstream acceptance is a separate review outcome and is not implied
  by anything here. The Gate-2 zero-MAC28 dependency additionally means the
  current actuation path is a development-only configuration on the
  maintainer's vehicle.
