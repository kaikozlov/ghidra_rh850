# Application proprietary SID `0xBA`

This report closes the configured application-side proprietary `0xBA` operation
surface for Sienna calibration `8965B4512000`. It is separate from SID `0xAB`,
which is the event-record service.

## 1. Outer Dcm policy and operation table

The primary 24-byte service object at `0x25FA8` assigns SID `0xBA` direct
callback `application_proprietary_ba_callback @ 0x8D344`. The outer Dcm object
permits only extended session `3` and has configured SecurityAccess count zero.
That configured zero is **not** the complete effective security policy: operation
`F7` performs its own callback-local SecurityAccess check.

The callback enters the shared operation dispatcher through `0x8D2B2 -> 0x4C8A8
-> 0x348B4`. Byte `0x28094` fixes the table at ten 16-byte rows from `0x28098`.
Each row contains selector, required data length `6`, start callback at `+8`, and
completion callback at `+12`.

| Selector | Request data after SID | Start / complete | Bounded effect |
|---|---|---|---|
| `F1` | `F1 JTEKM` | `34B74 / 34B9A` | service/lifecycle mode-3 request |
| `F3` | `F3 TMPCL` | `34BA8 / 34BF4` | persistent object-5/6 maintenance/reset |
| `F4` | `F4 JTRM1` | `34C50 / 34C76` | service/lifecycle mode-5 request |
| `F5` | `F5 JTRM2` | `34C84 / 34CAA` | service/lifecycle mode-6 request |
| `F6` | `F6 BADIS` | `34CB8 / 34D4E` | persistent BA authorization disable |
| `F7` | `F7 BAENA` | `34DAE / 34E6C` | SA2-gated persistent BA authorization enable |
| `F8` | `F8 TZCLR` | `34EC0 / 34F08` | speed/state-gated shared persistent workflow |
| `F9` | `F9 JTRM3` | `34F1A / 34F40` | service/lifecycle mode-7 request |
| `FA` | `FA <value> VSPD` | `34F4E / 34F80` | alternate speed-like snapshot override |
| `FB` | `FB ASINC` | `34F90 / 34FAA` | filtered operational-inhibit flag |

The `FA` and `FB` strings overlap in CodeFlash: `VSPD` begins at `0x210C5`, while
`ASINC` begins at `0x210C9`. `FA` consumes its first operation byte as the value
and compares the following four bytes to `VSPD`; it is not a literal `VSPDA`
five-byte token.

The machine-derived form of the same table is
[`data/application_proprietary_ba_surface.csv`](../../data/application_proprietary_ba_surface.csv).

## 2. Persistent authorization gateway

`FUN_34882` is the bootstrap check. It recognizes only selector `F7`, required
data length `6`, and the five bytes `BAENA`; success returns `0x5A`.
`FUN_348B4` then permits descriptor dispatch when either:

- runtime marker `FEBE5F27 == 0x5A`, or
- the bootstrap check returned `0x5A`.

Otherwise it returns `-13` before descriptor dispatch. Once the marker is active,
the gateway itself does not read SecurityAccess state again. Individual
operations still retain their own fixed-token and state/precondition checks.

### F7's effective SecurityAccess gate

`application_operation_05_start @ 0x34DAE` is the only configured BA start
callback that reaches the application Dcm security-state reader. Its first edge
is:

```
34DAE -> 34D96 -> 8C8C6 -> 8FDCA
```

`34D96` requires security mask bit `0x02`. The application mask setter at
`0x9075A` stores bit `(level - 1)`, so bit `0x02` is **SecurityAccess level 2**,
the functional `27 03/04` application level. Therefore the effective initial
enable boundary is extended session plus application SA level 2 plus the
`F7/BAENA` request, even though the outer service object's configured security
count is zero.

This corrects the overly broad interpretation that `sec_count=0` means every
callback below SID `0xBA` is SecurityAccess-free. It remains true that the Dcm
service table itself has no configured SecurityAccess level.

## 3. Persistence and countdown lifecycle

F7 persists two separate NvM objects:

- ordinary/checkpoint object `24`, API ID `0x18`, 8-byte RAM mirror `FEBEF450`,
  already mapped as `persistent_countdown`;
- redundant-namespace object `5`, API ID `0x105`, 8-byte RAM mirror `FEBEF418`,
  whose first dword is marker `0xA55A5AA5` and whose second dword is zero.

On successful completion F7 sets `FEBE5F27=0x5A` and `FEBE5F28=30`. F6/BADIS
updates the same two objects and clears both runtime bytes.

Startup/restore helper `0x347B0` reloads object `0x105`, validates
`0xA55A5AA5`, reloads object `0x18`, bounds its byte against the fixed maximum
`30`, and reconstructs `FEBE5F27/28`. The authorization state therefore survives
a reset while its persisted countdown remains valid.

`checkpoint_persistent_countdown_step @ 0x34FB6` decrements the count by one per
worker invocation, persists object `0x18`, and clears redundant object `0x105`
and the authorization marker when the count reaches zero. The static graph proves
**30 worker invocations**, not a wall-clock duration; no seconds/minutes claim is
made.

This pair is distinct from the related-variant SecOC key object. Redundant object
`15` / API ID `0x10F` is 32 bytes at `FEBF02E8` and is not written by F6/F7.

## 4. Other operation families

### `JTEKM/JTRM1/JTRM2/JTRM3`

F1/F4/F5/F9 share the `FE024 -> B201A` request path and the `FE150 -> B209C`
completion path. Their modes 3/5/6/7 map to lifecycle request state
`FEBEB112=0x5A` and `FEBEB113=0x11/0x22/0x44/0x88` respectively. These states
feed system-mode/telemetry workers, not a recovered numeric steering-command
input.

### `TMPCL`

F3 completion reaches `3B252`, `38DCA`, and `47958`. The recovered lower paths
reset runtime groups and persist ordinary objects 6 and 5. This is a
maintenance/reset workflow, not a direct actuation primitive.

### `TZCLR`

F8 is locally gated by `application_vehicle_speed_raw @ FEBEE892 <= 0x04B0` plus
transition/state checks. Its completion reaches `FDE30 -> B7D26(0x22,2)`, the
same persistent state-machine family used by RoutineControl RID `0x1109`.

### `VSPD`

FA installs `FEBEB116=0x5A` plus tester-selected byte `FEBEB117`; operational
worker `BC5BC` uses the pair to substitute a 16-bit internal value with
`value << 7` and writes the neighboring channel `FEBEB6F6`.

This is **not** the diagnostic vehicle-speed gate. `application_input_snapshot_update
@ 0xBCB3A` separately maps:

```
FEBEB6F2 -> application_vehicle_speed_raw @ FEBEE892
FEBEB6F6 -> FEBEE894
```

`FEBEE894` has one runtime reader, an RDBI callback. The established WDBI,
RoutineControl, session-transition, and F8 speed gates read `FEBEE892`, so FA
does not directly bypass those gates.

### `ASINC`

FB completion sets `FEBEB118=0x5A`. `B80EE` consumes that flag as one branch
condition in a filtered operational calculation. The recovered BA cone contains
no direct conditioned-steering-command or d/q/current-PI/PWM state reference.

## 5. Security and control boundary

The supported security statement is narrow:

1. Initial BA authorization requires extended session, F7/BAENA, and application
   SecurityAccess level 2.
2. F7 persists an authorization marker and a bounded 30-invocation countdown.
3. While that marker is active, the generic BA gateway no longer requires a
   fresh SecurityAccess check; registered operations still require their own
   static request token and local state gates.
4. The marker is reconstructed from NvM after reset.
5. The recovered 41-function BA cone has no direct join to the proved
   conditioned-command, d/q-reference, current-PI, or TSG3-PWM state set.

This is a **persistent proprietary diagnostic authorization/freshness downgrade**
and a maintenance/lifecycle surface. It is not an initial SecurityAccess bypass,
not a write to the SecOC key object, and not a recovered arbitrary
steering-current primitive.

## 6. Verification

- `tests/verify_application_proprietary_ba.py` pins the raw service/table bytes,
  request contracts, F7 SA2 gate, persistent object identities, restore/countdown
  behavior, and lower semantic joins.
- `tests/verify_application_proprietary_ba_live.py` plus
  `AssertApplicationProprietaryBaSurface.java` pin exact live table ownership,
  marker-reader topology, VSPDA/SP1 separation, and the 41-function direct
  actuation negative.
- `tests/verify_motor_actuation_boundary.py` remains the independent global motor
  boundary.
