# 2026 Camry openpilot capability matrix and qualification handoff (WP6)

**Scope:** work package 6 of the Camry openpilot completion plan: the
consolidated capability matrix, qualification-record requirements, and honest
support status for Milestones A and B. This is a tracking document; a row is
only as strong as the evidence link behind it.

Grades follow docs/status/FINDINGS.md. Software identities: fork `kai`
`43a7e4b608596a80484a3c6563d248b094f2810e` (opendbc `a13c9ee9…`, panda
`5236f370…`); recorded software that produced the September corpus: opendbc
`c7a62eaf`. Fork HEAD has since advanced past these pinned revisions with
test- and documentation-only commits; the pinned revisions remain the audited
set.
Status vocabulary: `not started / in progress / reviewable / accepted / blocked`.


| Capability | Status | Evidence link | Blocking dependency |
|---|---|---|---|
| Platform identification (F181-exact, census fallback) | reviewable | camry-2026-tss3-integration-audit.md; `test_tss3_camry.py` | — |
| Vehicle state decode (angle/torque/gear/READY/speed) | reviewable | audit doc; real-frame replays; live-baseline §4–§8 | torque sign/direction dynamic confirmation |
| Stock ACC (Milestone A longitudinal) | reviewable | audit doc; `0x0FE`/`0x08A`/`0x251` replay tests | — |
| Driver interaction (nudge → lane change) | reviewable (software) / blocked (validation) | VAR-125 fix + replay audit (0 → 171 pressed on identical input) | on-vehicle confirmation of 1.2 N.m threshold and torque sign |
| Lateral actuation (B6 command path) | blocked | VAR-124/125/126: sender wire-exact, transport exonerated, wheel tracks stock request when divergent; zero `laneChange` events under the recorded bug | EPS receiver admission/ingress (bench spec WP3); Gate-2 dependency makes current path non-deployable |
| Native openpilot longitudinal (Milestone B) | blocked | camry-2026-longitudinal-evidence.md | `0x160` semantics/ownership; receiver acceptance; source suppression |
| Radar/perception configuration | reviewable | `radarUnavailable=True` (opendbc `interface.py` TSS3 flag) with model-lead `radarState` is the upstream-normal arrangement — port report §7, WP4 doc | none for stock-ACC operation |
| Reproducible passive evidence (WP1) | accepted | `camry_20260904_stock_steering_report.json` + fixture-verified suite (50 checks) | external logs for full-corpus regeneration |
| Bench qualification (lateral) | not started | camry-2026-bench-validation-spec.md | apparatus + supported interface |
| Controlled vehicle validation | not started | this document | everything above plus operator/test-site arrangements |

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
