# Verification architecture cleanup — 2026-08-23

## Problem

The repository's nominal fast gate had accumulated nearly every deterministic
verifier plus every locally available proprietary Techstream verifier.  Its
runtime therefore depended on ignored local files: a clean clone skipped those
checks, while a developer with the full reverse-engineering corpus paid their
full cost on every `make verify`.

A timed baseline on the normal development checkout was:

- `make verify`: **263.38 s wall**, 197 test-program executions, all passing.
- 16 tests at or above 2 s consumed **228.14 s (87%)** of test wall time.
- 25 tests belonging to declared external suites consumed **177.93 s**.
- 158 tests below 0.5 s consumed only **12.8 s** total.  Python process startup
  was therefore not the principal bottleneck.
- The single tracked-only outlier was the exhaustive Corolla DataFlash key-domain
  scan at about 33 s.  It tests 23,277 unique 16-byte candidate windows and, for
  protected samples, many candidate message counters per window.

The previous arrangement was also semantically undesirable: several portable
verifiers opportunistically opened `Techstream/unpacked/` when it happened to be
present, so identical tracked commits did not execute identical `make verify`
workloads on different machines.

## Resulting tiers

`verification.toml` now defines three normal tiers:

- **core** — fast, tracked-only edit-loop verification (`make verify`).
- **full** — exhaustive portable/tracked-only verification (`make verify-full`).
- **local** — full plus locally available proprietary/external and live-project
  suites (`make verify-local`).

Suites without an explicit `modes` field belong to all three tiers.  Declared
external suites are explicitly local-only.  Expensive tracked-only checks can be
full/local; currently the exhaustive Corolla DataFlash domain scan is the only
such exception.  `make verify-changed` still selects owning suites regardless of
tier, and `make verify-required-external` still selects all declared external
suites and fails rather than skips when prerequisites are absent.

`make verify-agent` is the compact-JSON form of the **core** gate, not an alias
for the expensive local superset.  Agents that need the complete local corpus
must request `make verify-local` explicitly.

The runner sets `RH850_VERIFY_EXTERNAL=0` for core/full children and enables it
only for local/required-external execution.  Three hybrid tests that contain both
portable assertions and optional raw Techstream corroboration honor that switch:
`verify_diagnostic_vocabulary.py`, `verify_secoc_fd_sensor_correlations.py`, and
`verify_techstream_ptshim.py`.

## Performance after tiering

Measured on the same checkout after the change:

- `make verify`: **32.16 s wall**, 171 passes, no skips/failures — **8.2x faster**
  than the 263.38 s baseline.
- `make verify-full`: **63.76 s wall**, 172 passes, no skips/failures.  The
  DataFlash exhaustive scan accounts for about 31.4 s of this total.

The DataFlash scanner also now chooses its one probe per protected CAN ID once
before walking candidate windows rather than regrouping the same capture for
every candidate.  This removes needless repeated list construction, although the
cryptographic counter search remains the dominant and intentionally exhaustive
cost.

No default parallel test execution was introduced.  The profile showed that it
would address a minority of the original runtime, while this test corpus contains
shared build-workspace lifecycle tests and subprocess-driven regeneration checks
for which concurrency would add race risk.  Tiering removes the unnecessary work
without weakening evidence independence.

## CI

CI runs `make verify-full`, preserving all portable evidence gates even though
local edit loops use core.  Proprietary external suites remain explicit and are
not required on public GitHub runners.

The existing macOS processor/project and fresh-rebuild gates remain intact,
including their `main`, pull-request, manual, and nightly coverage.  They overlap
in setup but prove different invariants, so this cleanup does not trade fresh
rebuild assurance for CI runtime.
