# 2026 Camry TSS3 hands-off cancellation

This note isolates the retained road evidence for the question that replacing the
stock hands-off HUD did **not** answer: what actually cancels stock adaptive cruise
when the FRC's hands-off sequence reaches its late stage?

The source is route `00000045--805b7ca6ab` from 2026-09-07, recorded at openpilot
commit `f8bd956a4b23eb4992c6abbe899e72b27cd91d80`. The deterministic reduction is
`data/generated/camry_20260907_hands_off_cancel.json`, produced by
`tools/targets/camry/analysis/analyze_camry_20260907_hands_off_cancel.py`.

## 1. Separate actual stock cancellation from openpilot's cancel path

Route 45 contains nine native `0x08A` `CRUISE_OPERATING_LATCH` falling edges.
Four are ordinary openpilot/user cancel episodes: `buttonCancel` occurs first,
`CarControl.cruiseControl.cancel` asserts, and the historical Camry controller
injects `0x101 BRAKE_MODULE` with the cancel/brake bit set before stock `0x08A`
drops.

Five other latch falls have no such preceding `0x101` injection. Three begin from
active Target Lateral ID 11. The strongest hands-off-specific witness is segment 10
at monotonic `1041.318670 s`: it follows the complete recovered warning sequence,
has no brake or accelerator input, has no `buttonCancel`, and has no openpilot
`0x101` transmission in the preceding 250 ms. `pcmDisable` appears only **4.511 ms
after** the native `0x08A` transition. This establishes the wire ordering as stock
FRC request withdrawal first, openpilot observing cruise-disabled second.

## 2. Warning -> late state -> cancellation timeline

The segment-10 sequence is:

| time relative to cancel | native event | interpretation |
|---:|---|---|
| `-14.564 s` | `0x371 B19: 0x20 -> 0x40` | ordinary hands-off warning candidate |
| `-8.606 s` | `0x412 = 14 0c 40 44 01 ee 93 07` | recovered HUD escalation (`B2[6]=1`) |
| `-5.563 s` | `0x371 B19: 0x40 -> 0x60` | late/final-stage candidate |
| `-4.160 s` | `0x371 B20[4]` asserts and `B19 -> 0x20` | late driver-steering detection clears visible warning state |
| `0` | native FRC `0x08A` changes request state | stock cruise/lateral request withdrawal |
| `+4.511 ms` | openpilot `pcmDisable` | consequence of stock cruise dropping |
| `+20.840 ms` | chassis `0x081` lateral result ID becomes `0` | arbitration follows lateral withdrawal |
| `+50.637 ms` | chassis `0x081` longitudinal result ID becomes `63` | arbitration returns to **Driver Operation** |

`0x371 B19=0x60` is therefore a much stronger late/final-state candidate than the
previously documented `B19[6]` warning bit alone. The exact OEM bit name is not
joined. It must not yet be called the literal cancel request: other `0x60` episodes
can be recovered by driver action without an immediate cancellation. The important
fact here is that the strong forced-cancel witness passes through this state before
the FRC withdraws `0x08A`.

A notable detail is that the stock `0x412` warning presentation has already returned
to its ordinary-looking payload by the late stage. Thus replacing `0x412` can hide
the earlier cluster nag while leaving the deeper FRC timer/state machine untouched.
That matches the observed Camry behavior in which HUD suppression does not prevent
the later functional cancellation.

## 3. The cancellation is carried by the joint `0x08A` request plane

Immediately before the segment-10 cancellation, native FRC `0x08A` is:

```text
0000000880002d47000b48000b7fff007fff0013c00b10006400320015b8b069
```

Recovered fields:

```text
CRUISE_OPERATING_LATCH       1
long request A               ID 11 / allocation 1
long request B               ID 17 / allocation 3
accel A/B                    +0.011 / +0.011 m/s^2
set speed                    72 km/h
Target Lateral ID            11
lateral assist gain          1.00
sequence                     50
```

The next request is:

```text
0000000080000012fdbe00fdbe7fff007fff0016000000006400330051e15a76
```

with:

```text
CRUISE_OPERATING_LATCH       0
long request A               ID 0 / allocation 0
long request B               ID 4 / allocation 2
accel A/B                    -0.578 / -0.578 m/s^2
set speed                    0
Target Lateral ID            0
lateral assist gain          1.00
sequence                     51
```

The sequence remains continuous, so this is not sender disappearance or a stale
frame. The FRC deliberately publishes a new authenticated request state which
withdraws both stock lateral operation and the active stock-cruise request state.

The Brake/chassis result plane confirms that interpretation. The first post-edge
`0x081`, 20.840 ms later, already has lateral result ID `0` while longitudinal
result ID remains `11`. By 50.637 ms the longitudinal result ID is `63`, Toyota's
**Driver Operation** result identity. `0x081 REQUEST_LOSS_STATUS` remains clear in
both frames, so this is not the chassis reacting to loss of FRC communication.

## 4. What does *not* cancel it

At the strong witness:

- native `0x101 BRAKE_MODULE` is byte-identical immediately before and after:
  `80 00 00 01 00 00 00 8b`;
- its recovered `BRAKE_PRESSED` bit is clear;
- no openpilot/sendcan `0x101` exists in the preceding 250 ms;
- `carState.brakePressed = false` and `gasPressed = false`;
- `0x251 CRUISE_MAIN_STATE` remains `1`, so cruise availability/main remains on;
- `0x081 REQUEST_LOSS_STATUS` remains `0`.

Therefore the forced cancellation is not the normal brake/button-cancel carrier,
not a physical pedal event, not cruise-main being switched off, and not a missing
request timeout.

## 5. Integration implication

For older Toyota ports, blocking/replacing camera steering and `LKAS_HUD` was enough
because the stock camera's hands-off consequences no longer owned anything openpilot
needed. On this TSS3 Camry, the FRC's hands-off state machine still owns the protected
**joint longitudinal/lateral `0x08A` request PDU** while openpilot retains stock
longitudinal control.

That is why replacing `0x412` alone cannot solve the problem. At the functional
cancel point the FRC itself changes `0x08A`; Brake/chassis arbitration then follows
that withdrawal. The two plausible control boundaries are therefore:

1. keep the FRC from reaching the late cancellation state by satisfying its genuine
   hands-on/driver-steering detector without entering higher steering override; or
2. take ownership of the protected `0x08A` request plane and preserve the desired
   longitudinal request when the FRC would withdraw it.

The second option is not a simple HUD-message replacement: `0x08A` is authenticated
and jointly carries lateral and longitudinal requests. Its source/authentication
ownership must be handled correctly. The route-45 evidence only establishes where
the cancellation appears on the wire, not that replacing this PDU is yet the best
production solution.
