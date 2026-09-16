# Corolla TSS3 tester handoff: offline audit, 2026-09-16

## Disposition

**Do not treat the kit built from analysis revision `4d8006d8` as ready for a
recipient to install and then drive.** Source review exposes a Corolla-specific
post-startup attestation contradiction and incomplete tester safety checks.
Passing packaging checks and the existing unit suites did not cover these paths.
Earlier claims that the only remaining work was physical qualification were too
strong. This document records findings, not fixes or a new deployment procedure.

Reviewed revisions: analysis `4d8006d8`, kai-openpilot `53b95d0dd`, opendbc
`7dce3659`. This review performed no vehicle access, CAN transmission, resident
execution, flash operations, or signer-kit rebuild. No actuator implementation
or upload procedure was changed.

## 1. Post-startup resident attestation contradicts the Corolla memory lifecycle

Source: `exploit/ephemeral_runtime/tss3_unified_b6_signer.py:392-401,550-562` and
`exploit/ephemeral_runtime/tss3_unified_b6_signer_resident.S:47-64` at the reviewed
analysis revision.

The host Session constructor compares a hash over the entire resident memory
range to the build-time resident hash. The Corolla startup code intentionally
reclaims its own one-shot prefix as mutable state and scratch before entering
the foreground loop. It clears and writes state into that prefix.

Those are incompatible expectations: successful initialization changes bytes
inside the very range the host requires to remain byte-identical to the pristine
image. Installation calls Session after application return; status and
qualification also call it. The observed source therefore predicts rejection of
an initialized Corolla resident with `resident identity mismatch`. This is a
static lifecycle defect, not evidence that the ECU's actual firmware rejected an
installation. No live execution was attempted to reproduce it.

The current verifier tests builds, helper liveness, packaging, a mocked mailbox
probe and a nominal passive sensor fixture. It does not exercise the real Session
attestation against a post-startup Corolla memory image. A successful `doctor`
only establishes imports and bundle checks, not installed-state compatibility.

## 2. The parked-test check accepts sensor states it should not qualify

Source: `tss3_unified_b6_signer.py:175-178,201-259,393-400`.

Only passive decoding/validation functions were extracted with Python AST and
executed with an in-memory receiver. No installer/signing module was imported
and any attempted transmit was configured to fail. Results:

| Passive fixture | Actual result |
|---|---|
| Fresh READY, healthy stationary wheels, measured angle | Accepted |
| Same fixture with all four wheel fault flags asserted | Accepted |
| Wheel and angle samples at 0.01 s, READY only at 2.00 s, no refreshed wheel/angle samples | Accepted |
| READY and wheels present, no angle before timeout | Rejected |

The wheel decoder masks away the fault bits. Those bits are explicitly named in
`opendbc/dbc/generator/toyota/toyota_tss3_pt.dbc:101-109`, and the normal Corolla
CarState marks them sensor-invalid at `carstate.py:170-171`. The standalone
tester's result does not preserve that validation.

The tester also stores no per-signal receipt time. Old wheel/angle samples can be
combined with a later READY sample. It then performs resident readback and other
operations before the proposed pulse, without establishing a fresh measurement
at that later boundary. Consequently the prior claim that this check proves a
fresh, valid current-angle stationary condition was too strong. It also accepts
a nonzero stationary tolerance; it does not prove mathematically zero motion.

Park is printed as operator-confirmed, but the launcher supplies the confirmation
argument itself. The guided flow waits for Enter after a prompt; it does not
independently decode Park.

## 3. Retry, phase and cleanup semantics are not fully qualified

Source: `tss3_unified_b6_signer.py:292-327,481-547,599-634` and
`tss3_unified_b6_signer_launcher.sh:88-111`.

The probe is described as non-actuating, but it uses an active control-envelope
shape and does not first establish that no prior resident is running. The claim
of harmless stock-firmware probing must not be generalized to a blind rerun on
an already-modified runtime. This is a static lifecycle hazard; no live probe
was performed during this audit.

The guided flow invokes preflight before the install function's NRTD check.
Standalone qualification does not call the passive READY/stationary guard.
The arbitrary-target test path likewise relies on the supplied confirmation
rather than the passive guard used by the current-angle command. Thus printed
phase instructions are not equivalent to enforced prerequisites on every path.

Explicit release is reached only after the successful replacement checks.
Exceptions before that point skip it; there is no unconditional cleanup around
the operation. The resident's documented command-expiry behavior is a separate
mechanism, not proof that the promised explicit release always occurs.

Failures are printed to stderr, while structured output is written only after a
successful result is constructed. Existing output directories are reused. An
older success JSON can therefore remain alongside a later failed attempt. The
advertised evidence handoff is not an attempt-isolated failure record.

## 4. Broader port findings independently confirmed

### Steering fault reporting

At opendbc `7dce3659`, `carstate.py:188-197` handles driver-torque validity but
sets both temporary and permanent steering-fault outputs to false. The selected
EPS fault/inhibit field in the DBC is not used by this Corolla path. Distinguishing
that aggregate from a complete OEM fault taxonomy is necessary, but leaving both
outputs constant is not a completed fault-handling contract. This observation
does not imply Toyota's internal EPS protection is absent.

### Automatic stock-cruise cancellation

At kai-openpilot `53b95d0dd`,
`openpilot/selfdrive/controls/controlsd.py:161-163` requests cancellation when
stock cruise is enabled and openpilot is disabled. The TSS3 branch in opendbc
`carcontroller.py:80-113` returns before the ordinary Toyota cancellation path
starting at line 118, without handling that request. Lateral release is not
stock ACC cancellation. This does not establish any failure of the physical
brake pedal or factory cancel switch.

### Gear-source and identity claims

The current primary-source choices work for the retained traces. However,
`carstate.py:33-38,375-395` selects exactly one gear parser from the HYBRID flag;
it does not implement a general hybrid fallback to the one-hot carrier. A
synthetic known-hybrid diagnostic identity with the ordinal gear carrier absent
selects the ordinal parser and does not parse the one-hot carrier. This is a
claim/coverage mismatch, not an observed failure in Span's retained log.

The GTS vehicle-ID split and corrected enum comparison do not directly pass the
OEM powertrain subtype into CarParams. `values.py:560-572` returns platform
identities; runtime subtype still comes from diagnostic ECU/CAN evidence.

A fresh `tools/gts did HV_P5 0x1061 --json` read again returned the diagnostic
P/R/N/D/B domain `0/2/4/6/8`. That corroborates meanings, not a CAN-ID/bit-layout
join. The actual ordinal CAN parser uses Motorola start bit 47, width 4 (the
high nibble of byte 5); historical low-nibble prose is not the implemented DBC.

## 5. Positive checks and their limits

Existing suites rerun without syncing or changing dependencies:

```sh
uv run --no-sync python -m pytest -q opendbc/car/toyota/tests \
  opendbc/car/tests/test_fw_fingerprint.py \
  opendbc/safety/tests/test_toyota.py
```

Result: **324 passed, 262 skipped, 8,106 subtests passed**. Skips are not coverage.
These results support the tested exact identity matches, subtype handling,
existing safety assertions and deliberately stock-owned longitudinal settings.
They do not test the tester-handoff defects above.

Receive-only replays selected the Corolla platform explicitly and derived the
powertrain flag from the incoming CAN census, with no diagnostic identities
supplied. Both raw inputs were checked against their retained SHA-256 values.
No CarInterface.apply call was made.

| Retained input | Full duration | Samples after 5 s warmup | CAN-valid after warmup | Sensor-invalid after warmup |
|---|---:|---:|---:|---:|
| Span-attributed 2025 segment | 59.990073 s | 5,500 | 5,500 | 0 |
| Public 2023 segment 0 | 61.099784 s | 5,610 | 5,610 | 0 |

The 2025 replay used original CAN batch timestamps. The 2023 replay used 10 ms
updates and original batches up to each update, with empty timestamped updates
when needed. The latter decoded 150 Park, 936 Reverse and 4,524 Drive cycles in
the counted window; the 2025 input stayed in Drive. Span's trace contains 3,662
ordinal gear samples all at raw 3 and 60 one-hot samples all at the Drive value.

Sources are the existing `community/spanconstant/` rlog and ignored
`REFERENCE/public_route_corolla_2023_segment0_rlog.zst`. The latter was not added
to Git. The retained generated evidence already records the raw source hashes
and the missing exact firmware-to-route joins. These were decoder replays, not
successful automatic-fingerprinting replays or physical dashboard oracles.

Nominal decoding does not prove main-switch OFF/ON discrimination, hold/resume,
fault classification, dynamic steering response, or the new resident's operation
on either car. In particular, both retained replays keep cruise availability
true, so they cannot independently qualify the present request-ID-based
availability rule. A diagnostic enum or high signal correlation is not a direct
wire-semantic proof.

## Qualification boundary

The work is beyond a speculative parser, but not beyond all offline blockers.
The reviewed tarball should remain an unqualified development artifact. The
post-startup lifecycle, sensor validity/freshness, phase/retry behavior, failure
recording, and fault/cancel handling need resolution before calling the handoff
ready. Signing agreement alone does not prove steering acceptance or safe
vehicle behavior. Current comma safety documentation separately describes
software-in-the-loop, hardware-in-the-loop, and in-vehicle testing:
<https://docs.comma.ai/concepts/safety/>.

## Independent recheck of the unchanged runtime

A subsequent review of the same runtime/opendbc revisions reran the Toyota,
firmware-fingerprinting and Toyota safety suites: **324 passed, 262 skipped,
8,106 subtests passed**. No live interface or controller output was exercised.

A receive-only CarInterface fixture explicitly asserted the decoded
`EPS_FAULT_INHIBIT` field and preserved the additive-byte increment. The parser
reported the field as 1 and `canValid=true`, while both `steerFaultTemporary`
and `steerFaultPermanent` remained false. This confirms the missing fault
reporting as executable behavior, not just a source-comment concern.

AST-isolated passive tester functions independently reproduced acceptance of
all four asserted wheel-fault flags, and acceptance of wheel/angle samples
approximately 1.99 seconds older than READY. The healthy fixture was accepted
and the missing-angle fixture was rejected. No signer module, payload, Panda
connection or transmit path was used. The HYBRID-identity/absent-ordinal-carrier
fixture again selected only the ordinal gear parser, not the one-hot fallback.

These checks leave the disposition unchanged. Existing green tests do not
cover all required behavior; the kit and port are not ready for an
install-then-drive assurance. The architecture and runtime README now link
this audit at the previously advertised tester handoff. No runtime fixes,
kit rebuild or vehicle validation are claimed by this documentation update.


## Post-audit resolution

The audit findings above describe analysis/openpilot revisions `4d8006d8` /
`53b95d0dd` / `7dce3659`. Subsequent same-day fixes close the host-side defects
without changing the resident/helper wire contract:

- Corolla post-startup attestation no longer hashes the intentionally reclaimed
  one-shot prefix as immutable code. It requires live state magic in the mutable
  prefix and byte-exact equality from the compiled `foreground_entry` through
  the end of the resident. Split Camry/Crown residents retain full-image
  attestation.
- `preflight` now proves NRTD before the functional-mailbox probe and refuses the
  probe when the same unified resident is already installed.
- Qualification and both replacement commands use the same live vehicle guard.
  The guard rejects asserted `0x0AA` wheel fault flags, requires fresh wheel and
  `0x025` angle samples, and on Corolla requires a fresh decoded Park value from
  `0x127` (`P=0`) or the retained one-hot `0x3BF` (`P=0x80`).
- Any path that has transmitted an active C7 generation performs best-effort
  explicit sequence-zero cleanup in `finally`; successful pulses still require
  the released state to be observed.
- Requested output files are overwritten with a structured failure record when
  the command fails, and guided `bringup` refuses a non-empty evidence directory.
- Exact H/F `EPS_FAULT_INHIBIT` is now mapped to openpilot
  `steerFaultTemporary`; `steerFaultPermanent` remains false because the retained
  evidence does not justify a restart-required/permanent taxonomy.

`tools/test tss3_unified_b6_signer` passes with executable regressions for the
post-startup mutable-prefix attestation, immutable-code rejection, healthy
READY/Park/current-angle acceptance, wheel-fault rejection, non-Park rejection,
and stale motion/angle rejection. The broader Toyota/fingerprint/safety suite
passes **325 tests, 262 skipped, 8,106 subtests** after the fault-reporting fix.

These fixes change the disposition from “do not use the reviewed kit” to
**stationary qualification candidate**. They do not close two broader vehicle
contracts identified by the audit:

1. `controlsd` can request software cancellation of stock ACC, but the Corolla
   TSS3 controller has no qualified source-real cancel transmit path. Retained
   Corolla `0x101` is a native ~50-Hz bus-1 producer; unlike the separately
   qualified Camry relay-side cancel shape, injecting a competing same-ID source
   on Corolla is not justified by the evidence. `0x24D` also lacks a retained
   button-transition contract. No cancel PDU is guessed.
2. The current Corolla cruise-availability rule and some hold/display semantics
   remain evidence-bounded. Both retained passive replays keep availability true
   and therefore do not independently exercise main-OFF versus main-ON.

Physical qualification also remains mandatory: live F/H installation,
NRTD-to-READY survival, native B6 arrival/cadence, command-5 native-MAC equality,
signed replacement, steering response, driver override, recovery behavior, and
stock LTA/LDA/LCA/AEB coexistence are not established by these offline fixes.
