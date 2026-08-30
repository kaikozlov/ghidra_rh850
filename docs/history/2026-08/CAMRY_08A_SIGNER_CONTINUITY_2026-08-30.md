# Camry 0x08A signer-continuity — 2026-08-30

## Question

OQ-054 asks who transmits and signs Bus-4 `0x08A`. The session's architectural
claim (maintainer): TSK AES-CMAC keys live only in RH850 ICU-S protected key
storage; the FRC cannot sign, so the FRC must forward its request to an
RH850-class chassis node that signs, and the signed frame is then published on
Bus 4.

## New evidence

The retained 2026-08-26 stationary NRTD→READY capture (pre-repin aggregated dev
plane, bus 1) carries the entire secured chassis family — `0x00F`, `0x08A`,
`0x090`, `0x0D7` — including **2,475 `0x08A` frames at `B21=0` (No Request) in
100% of frames**:

- FV4 reset-low2 tracks the live `0x00F` epoch: 2,444/2,475 = 98.75%; the
  `0x00F` reset counter advances through the capture (5212→9807).
- B26 advances `+1 mod 64` at 99.96%.
- All 16 FV4 phases cycle.
- MAC28 frame-unique (last-4 unique fraction 1.0).
- `0x0D7` shows the same always-on pattern.

Active-request contrast (relay-correct drives): B21 censuses
`{0: 18868, 11: 646, 18: 1101}` (A) / `{0: 20914, 11: 2288, 18: 797}` (B);
B26 `+1` at 0.9915/1.0000; last-4 unique 1.0. The signer's cadence is
regime-independent.

## Interpretation

The `0x08A` signer is an **always-on chassis engine**, not an on-demand
extension of the FRC request lifecycle. Signing at zero request is structurally
inconsistent with the front camera being the key holder. OQ-054 narrows to
"which always-on Bus-4 node holds the slot-class key": brake family (ABS 435 /
Brake Booster 466) or Central Gateway (VAR-096 install-set bound). FRC
pre-authentication + chassis re-signing remains formally open but downweighted.

Corroboration: current GTS+ `ADCU_P6` vocabulary names the OEM
request/arbitrate/sign pattern (`Lateral Arbitration ID`, `Lateral Control ID
of Arbitrated Result`, `Lateral Control Request Pinion Angle`) — architecture
corroboration only, no P6→P5 name transfer. A repo-wide `tools/gts search
'secoc'` returns zero hits: Toyota diagnostic vocabulary never names SecOC, so
the ICU-S domain is invisible to Techstream by design.

## Firmware-blocked censuses

FRC `8646F3315000` and Brake `F152633K0000` firmware are **not** locally
available. The brake acquisition tool already records the post-acquisition
search order (Tx `0x0B6`/DLC-32 descriptor and packer; SecOC authenticator
submission, profile/key selector, freshness extraction and commit; upstream
FRC/ADS request inputs; enable/arming/suppression gates). Both censuses remain
the deterministic OQ-054 closer once packages are acquired (TMS-049/050).

## Persisted

- Finding VAR-101; canonical `docs/variants/camry-2026-live-baseline.md` §47.
- OQ-054 updated with the always-on refinement.
- `tools/analyze_camry_2026_08a_signer_continuity.py`;
  `data/generated/camry_2026_08a_signer_continuity.json`;
  `tests/verify_camry_2026_08a_signer_continuity.py` (26 checks).

Grades: zero-request signing continuity **observed**; signer identity
(brake/CGW, FRC-excluded-as-key-holder) **hypothesis** pending producer
firmware. No output authorized.
