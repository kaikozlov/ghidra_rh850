# 2026 Camry steering bench-validation specification and interface inventory (WP3)

**Scope:** work package 3 of the Camry openpilot completion plan. This is a
specification and evidence-inventory document, not a validation result. No
bench work has been performed; availability of a legitimate control interface
remains the external dependency that gates execution. Nothing here authorizes
steering transmission.

## Boundary definitions and required evidence

Each record must keep firmware/software/harness identities, operating state,
clock domain, synchronization uncertainty, raw evidence, and an explicit
`unknown` when an instrument cannot observe a boundary. Stock-firmware
evidence and modified-firmware evidence are distinct and never transfer
automatically.

| Boundary | Required evidence | Insufficient substitute |
|---|---|---|
| Physical reception | Independent capture at the intended receiver connection (e.g., a second interface on the EPS CAN segment observing the B6 frame with correct ACK) | Host send request or Panda TX return |
| Receiver acceptance | Supported receiver status (F33 queue/admission observables from the non-bypassing resident observer) or documented bench instrumentation | Healthy bus or absence of visible faults |
| Application consumption | Time-correlated application evidence attributable to the accepted transaction (protected-D7 queue progression, internal phase state) | An unchanged matching scalar baseline |
| Physical response | Independently measured steering-column/wheel angle attributable to that interface | Similar stock/openpilot targets, or `0x030 B22:B23` motor feedback alone |
| Release and override | Measured behavior under ID0/inactive and driver-input conditions across power transitions | A positive response in one active interval |

Current status against these boundaries, from retained evidence only:
physical reception is bounded by Panda TX returns plus same-bus native traffic
(VAR-126 transport exoneration); receiver acceptance, application
consumption, physical response, and release/override are all **unobserved** —
the 2026-09-04 corpus shows silent non-admission of 751,664 well-formed B6
frames (port report §4.4–§4.5). The corrected non-bypassing queue/freshness
observer remains the designated discriminator (§5 of the port report).

## Interface inventory

| Interface | Legitimacy / status | Notes |
|---|---|---|
| Panda bus-0 `0x0B6` (DLC 32, CAN FD) | Supported by the installed Gate-2 development patch on the maintainer EPS only | Zero-MAC28 development candidate, `stock_validated=false`; not a stock interface; not deployable |
| Native `0x08A` request plane (bus 2) | Read-only passive observable | Never a command ingress; OQ-054 signer/handoff still open |
| `0x081` reference word (bus 0) | Passive observable | Mirror of `0x08A` (VAR-129); direction unresolved |
| UDS on `0x7A1/0x7A9` (EPS) | Read-only supported (F181 identity, DIDs) | Write/control services not exposed by this plan |
| FRC P5 diagnostics `0x792/0x79A` | Read-only oracles validated on this car [live-baseline §7.1] | Observation only; `0x0FE` is SecOC-shaped and not forgeable |
| XCP `0x7F7/0x7F8` | Route correct, admission untested (CONNECT timed out) | Not an approved control path |
| Bench power/rig | **Not yet defined** | Blocking dependency for physical-response boundaries |

## Bench apparatus requirements (to be finalized with a qualified controls engineer)

1. Legitimate command interface: the Gate-2-patched EPS on a bench fixture, or
   an equivalent supported receiver arrangement; identity recorded per stage.
2. Independent angle measurement: separate rotary encoder or equivalent on
   the steering output, clock-synchronized to the CAN capture within a stated
   uncertainty budget (target ≤ one 20 ms control period; record actual).
3. Driver-input measurement: torque applied via a calibrated column load
   source, independently read.
4. Fixture/load conditions: documented rack, power supply, and any
   pseudo-load on the steering output; wheels unloaded variant first.
5. Operating envelope: supply voltage, temperature, session state, and
   READY-equivalent state pinned per case.

## Test cases (verification cases, not runtime interlocks)

Acceptance limits must be selected from the supported interface and
engineering requirements **before** outcome data is examined; no universal
allowable tracking error is invented here.

| Case | Procedure | Pass criterion (to set before data) |
|---|---|---|
| Response sign/scale | ID11 with a small bounded nonzero target step (both signs) | Measured angle moves in the correct direction with a scale consistent within pre-set bounds; no fault latch |
| Delay | Step response, repeated | Latency distribution within pre-set bound |
| Repeatability | ≥10 identical steps | Variation within pre-set bound |
| Saturation | Ramp to ±1745 raw envelope and beyond | Envelope respected; graceful clip |
| Release | ID0 / stream stop / power down | Return to uncommanded state within pre-set time; no latch |
| Communication loss | Stop B6 mid-active | Defined timeout behavior observed |
| Driver override | Apply column torque during active command | Command yields / degrades as specified |
| Power transitions | Ignition-cycle during active/inactive states | State restored or safely defaulted |
| Fault recovery | Inject loss/restart after a faulted condition | Recovery per specification |
| Freshness A/B | First-in-epoch message-low2 = 0 vs = 1 (stock phase) | Admission difference recorded (VAR-126 cheap A/B variable) |

VAR-129's passive witnesses supply reference baselines only; its highway
filters and correlations are not stationary pass/fail criteria. Native ID4 is
request activity, `0x030` motor feedback can include ordinary assist, and
neither proves a grant.

**Exit status:** blocked on the bench apparatus and the supported-interface
confirmation (items 1–2). This document is the specification those runs will
be judged against; until then, no code patch may be reported as completing
steering support.
