# Application-level SecurityAccess (SID 0x27, levels 03/04)

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS SEC-APP-001 … SEC-APP-004
>
> **Canonical artifacts:** —
>
> **Verification:** `tests/verify_application_diagnostics.py`
>
> **Related:** [payload-gate](bootloader-payload-gate.md), [application diagnostics](../diagnostics/application.md)

> **Calibration scope:** All findings apply to the Sienna EPS firmware
> `8965B4512000` (RH850/P1M-E R7F701381). The Corolla EPS (`8965F1208000`)
> is the same Denso/RH850 software family but a different calibration;
> its Dcm policy tables, secrets, and gating behavior may differ.

## 1. Separation from bootloader SecurityAccess

The Sienna EPS has two independent SecurityAccess implementations:

| | Bootloader | Application |
|---|---|---|
| **Code location** | `0x5516` (UDS handler) | `0x25C30` (subfn table), `0x9497C`/`0x94A72` (workers) |
| **Secret name** | `SEED_KEY_SECRET` | `APPLICATION_LEVEL2_SA_SECRET` |
| **Secret address** | CodeFlash `0xBFE8` | CodeFlash `0x20840` |
| **Secret value** | (16 bytes, separately recovered) | `89 3e 08 41 8c 74 1f fa 2a 9c 04 4b ff a5 58 13` |
| **Session** | Programming (0x02) | Extended (0x03) |
| **Subfunctions** | `01`/`02` | `03`/`04` (level 1 `01`/`02` compiled to stubs) |
| **Algorithm** | `AES-ENC(AES-DEC(SEED_KEY, data_record), seed)` | identical construction, different key |
| **Entry path** | Direct UDS dispatch | `10 03` → `27 03` → `27 04` (no bootloader reset) |

The two paths share the same two-stage AES-128-ECB construction but use
different secrets, different CodeFlash addresses, and different entry
requirements. The application path never transitions to the bootloader;
it runs entirely within the AUTOSAR Dcm diagnostic stack.

A third secret (`PAYLOAD_BUILD_SECRET` at `0xBFD8`) is used for bootloader
payload encryption and is unrelated to either SecurityAccess path.

### 1.1 The application-SA root is disclosed pre-authentication

The Sienna application root at CodeFlash `0x20840` is copied into readable
LocalRAM during normal application startup. `FUN_00062662`, called by
`application_startup_coordinator @ 0x62758`, copies exactly 64 bytes from
CodeFlash `0x20810..0x2084F` to `FEBF7BB0..FEBF7BEF`; consequently the 16-byte
root at `0x20840..0x2084F` appears at `FEBF7BE0..FEBF7BEF`.

That mirror is outside the final application LocalRAM exclusion interval
`FEBF6C00..FEBF78DF`. Two independent unauthenticated read surfaces can reach
it: extended-session SID `0x23` ReadMemoryByAddress has no configured
SecurityAccess list, and XCP `SHORT_UPLOAD` is configured without an XCP
GET_SEED/UNLOCK gate. The application-SA root can therefore be recovered before
performing `27 03/04`; knowing it in advance is not a prerequisite on this
calibration.

The H/F Corolla generation has the same construction with copier `0x5C9B6` and
destination `FEBF7B50..FEBF7B8F`, placing the same root at `FEBF7B80`. This
cross-image result is owned by
[keyless-exec-surface-assessment.md](keyless-exec-surface-assessment.md)
(`KEYLESS-006`) and is pinned directly from all three raw CodeFlash images. It
does not disclose or bypass the independent boot SecurityAccess root at
`0xBFE8`.

The practical application-side consequence is narrower than "all diagnostics
become unlocked." The configured Dcm service objects, RDBI policies, all 19
RoutineControl RIDs, and recovered WDBI policy records already have no effective
nonzero application-SA requirement. The material callback-local exception is
proprietary BA selector `F7/BAENA`: its local helper checks application-SA level
2 before establishing the reset-persistent BA authorization state. Once the
root above is read, that check is a recoverable protocol step rather than a
secret-dependent barrier. The downstream BA state machine still supplies no
recovered boot-SA write, low-CodeFlash credential read, or attacker-selected PC
(`KEYLESS-012`; `tests/verify_application_proprietary_ba.py`).

## 2. Algorithm

The level-2 key verification at `0x8C82A` is a two-stage AES-128-ECB
pipeline:

```
intermediate = AES-128-ECB-DEC(APPLICATION_LEVEL2_SA_SECRET, data_record)
expected_key = AES-128-ECB-ENC(intermediate, seed)
```

The 16-byte expected key is compared byte-by-byte against the tester's key.

### Crypto primitives

| Function | Address | Role |
|---|---|---|
| `0x865D4` | AES-128 key expansion | Standard S-box + Rcon, NIST FIPS-197 |
| `0x853EE` | AES-128 single-block decrypt (application copy) | 4582 bytes. Inverse S-box + Td tables. Separate from bootloader's `0x7470`. Called only by `0x8C7BC` (SA stage 1). |
| `0x8496C` | AES-128 encrypt round function (application copy) | 2372 bytes. Te tables. Called only by `0x852B0` (SA stage 2 wrapper). Separate from bootloader's `0x7352`. |
| `0x852B0` | AES-128 single-block encrypt wrapper | Calls `0x8496C` round function |
| `0x869D2` | AES context clear | Zeroes the round-key buffer |

### AES tables (all FIPS-197 verified by content)

| Table | Address | Size | Notes |
|---|---|---|---|
| Forward S-box | `0x8FF1` | 256 B | Standard `63 7c 77 7b f2 6b 6f c5 ...` |
| Inverse S-box | `0x25628` | 256 B | Standard `52 09 6a d5 30 36 a5 38 ...` |
| Rcon | `0x23615` | 10 B | Standard `01 02 04 08 10 20 40 80 1b 36` |
| Te0–Te3 | `0x23628`–`0x24228` | 4 × 1 KiB | Byte-swapped LE storage |
| Td0–Td3 | `0x24628`–`0x25228` | 4 × 1 KiB | Td0[0]=0 (INV_SBOX[0x63]=0) |

No ICU-S hardware crypto is involved in key derivation. The ICU-S is used
only for seed generation (`0x8C65A`).

### Dispatch chain

```
0x8C82A (orchestrator)
  ├── 0x8C7BC (stage 1: AES-DEC)
  │     ├── 0x865D4  key expansion with secret @ 0x20840
  │     ├── 0x853EE  decrypt data_record @ FEBF497A
  │     └── 0x869D2  clear context
  ├── 0x8C7F6 (stage 2: AES-ENC)
  │     ├── 0x865D4  key expansion with intermediate
  │     ├── 0x852B0  encrypt seed @ FEBF495A
  │     │     └── 0x8496C  T-table round function
  │     └── 0x869D2  clear context
  └── byte-by-byte compare vs tester key
```

All call edges verified by exact `jarl` instruction bytes at exact
call-site addresses (`verify_application_diagnostics.py`).

## 3. Data-record source (FEBF497A)

The `data_record` input to AES-DEC is **tester-controlled**.

### Producer chain

The seed worker `0x8C734` loads the data-record source pointer via
`ld.w -0x5a54[gp], r7` at `0x94996`. With `APP_GP = 0xFEBEB800`:

```
*(0xFEBEB800 - 0x5A54) = *(0xFEBE5DAC) = request_state[0]
```

`request_state[0]` is the pointer into the Dcm RX PDU buffer, already
advanced past SID and subfunction by the Dcm DSP dispatcher (`0x8F750`).
So `0x8C734` copies 16 bytes from `PDU_buffer[2:18]` into `FEBF497A`.

### No request-length validation

The Dcm seed-path handler (`0x94BCC`) performs no request-data-length
check. The config value `0x10` at `0x26360` validates *response buffer
space* (enough room for the 16-byte seed response), not request length.

### Attack protocol

The tester controls the data record by sending 16 bytes after the
subfunction:

```
10 03                               # extended session
27 03 00 00 00 00 00 00 00 00       # request seed with chosen data_record = zeros
      00 00 00 00 00 00 00 00
# receive: 67 03 <16-byte seed>
# compute:
#   K_inter = AES-128-ECB-DEC(SECRET, data_record)
#   key     = AES-128-ECB-ENC(K_inter, seed)
27 04 <16-byte key>                 # send key
# expected: 67 04 (positive response)
```

For a bare `27 03` (no padding), the 16 bytes depend on PDU buffer state
and are not statically provable. The recommended protocol is to always
send `27 03` followed by 16 zero bytes.

### Standalone keygen

`tools/sienna_application_sa_keygen.py` computes the expected key:

```
python3 tools/sienna_application_sa_keygen.py <seed_hex> [data_record_hex]
```

## 4. Seed generation

Level-2 seed generation (`0x8C734` → `0x8C65A`) uses the ICU-S crypto
hardware through `0x84850`/`0x84874`/`0x8488C` with RAM `FEBF4A50`.
The 16-byte seed is stored at `FEBF495A` and `FEBF496A`.

If already provisioned (`FEBF4958 == 0x5A`), the existing seed is reused
without regeneration. If the session matches the requested session, the
seed buffer is zeroed before generation (fresh challenge).

On failure, the worker returns `0x22` (conditionsNotCorrect).

## 5. Attempt counter and unlock state

- **Attempt counter**: per-level byte in RAM near `FEBE5DA4`, incremented
  on each mismatch. Compared against configured max at
  `DAT_00023EE4 + level*0x18 + 0x2469`.
- **Delay timer**: enforced by `0x96E24` when the configured delay word
  is non-zero. RAM-only.
- **Unlock state**: `0x900FC` → `0x9075A` sets bit `(level - 1)` in a
  2-dword bitmask. Reader `0x8FDCA` → `0x906F8` scans and returns the
  current level. Cleared on session change (`0x90834`) or timeout
  (`0x908C6`).
- **NRC mapping**: mismatch → `0x35` (invalidKey) or `0x36`
  (exceededNumberOfAttempts); delay active → `0x37`
  (requiredTimeDelayNotExpired).

## 6. Security-level consumers (what the unlock gates)

**No configured SecurityAccess gating was found at the service, bounded RDBI-policy, or 19-RID RoutineControl policy layers in this Sienna calibration.** That statement is limited to Dcm policy tables, not arbitrary callback-local checks. The complete configured `0xAB` event-record graph contains no direct sensitive target, while SID `0xBA` operation F7/`BAENA` independently reads the live Dcm security mask and requires application SecurityAccess level 2. The policy tables are empty even though this callback-local protection is real.

| Scope | Check | Result |
|---|---|---|
| All 17 services (Dcm dispatch layer) | `sec_count=0` at `0x25E28 + i*0x18 + 0x12` | No service is security-gated |
| All 242 readable DIDs (RDBI) | Policy table at `0x261A4`, bounded scan of recognized policy records | No DID requires level > 0 |
| RDBI callback disclosure boundary | Firmware table `0x2941C` (242 rows / 196 unique callbacks), exact dispatch at `0x4CB8A→0x4CBB2`, depth-4 direct-call audit | No recovered callback-local path into command-5 output, key-update result bank, payload-derived key material, or application-SA seed/data/temp RAM; selected hits reduce to generic NvM workspace plus status accumulator `FEBE5050` |
| RDBI transport-buffer lifetime | 48 success-stub DIDs across classes 0/2/3; fixed Dcm response buffer `FEBE59F8`; direct-mode path through `0x9434A→0x92810→0x935BA/0x9361A/0x9364A→0x8A374` | Each row declares 1..45 bytes but its producer returns success without writing; those bytes come from prior response-buffer contents. Maximum oracle: `62 1C F4 ‖ prior_RMBA_data[2:47]` |
| All 19 configured RoutineControl RIDs | Policy table at `0x26420`, flag at `0x26B8D` | All have `level_count=0`; 18 policy-0 RIDs are effective in sessions `1/2/3` |
| SID `0xAB` event worker, 75 snapshot descriptors, six detail descriptors | Resolve corrected service ownership and bounded descendants | Zero direct matches to selected crypto/NvM/ICU-S/SecOC/security-policy targets |
| SID `0xBA` ten-operation table | Outer service `sec_count=0`; exact callback-local scan | F7/`BAENA` alone reaches SecurityAccess reader and requires mask bit `0x02` = level 2; successful F7 persists the BA authorization marker/countdown |

The architecture is:

```
Generic Denso/AUTOSAR diagnostic stack:
    full SecurityAccess implementation
    unlock bitmask machinery
    per-service / per-DID security hooks

Sienna 8965B4512000 calibration:
    level-2 crypto enabled (real secret, real AES)
    Dcm service/DID/RoutineControl policy tables unpopulated
    callback-local SecurityAccess checks can still exist (BA F7 is one)
```

The algorithm and unlock state are real. The generic policy tables are empty,
but F7 proves the unlock is not wholly dormant: selected application callbacks
can consume the live security mask directly.

The empty RDBI policy therefore exposes a broad read surface, but the recovered
callback graph now supports a narrower confidentiality boundary than the policy
scan alone. All 196 unique callbacks are represented as exact functions. A
four-hop path-insensitive direct-call audit over selected high-value crypto/SA
RAM regions reports four observations, but three are statically infeasible:
DIDs `0105`, `010B`, and `F18C` pass literal checkpoint IDs `0x204`, `0x20A`, and
`0x207` into `0x65D66`, which routes the `0x2xx` family to `0x66172`; their
apparent `FEBF0308` hit lies behind the mutually exclusive `0x000` branch
through `0x668B2`. The actual `0x66172` closure has zero selected sensitive
references. The only branch-feasible selected observation is DID `0110` reading
`FEBE5050`, whose exact xrefs bound it to reset/saturating status bookkeeping,
not key or generated-MAC material. This does **not** prove the full 242-DID
corpus contains no privacy, diagnostic-history, or other sensitive information;
it specifically closes the currently recovered key/MAC/SA-buffer disclosure
candidates.
That callback-local result does not close the Dcm transport-buffer lifetime.
Forty-eight DIDs use configured producers that immediately return success without
writing. Their declared widths are 1..45 bytes; the exact set is pinned by the
stale-response verifier. Dcm reuses fixed response buffer `FEBE59F8`; only byte
0 is cleared by the two reset sites, while positive-service dispatch and RDBI
overwrite only the SID and DID before the unwritten declared value is counted as
valid. Consequently all 48 expose prior response-buffer bytes without
SecurityAccess. A 47-byte RMBA seed demonstrates the maximum-width case:
`22 1C F4` should return prior RMBA data bytes `2..46`. The static chain is verified and the read-only isolated-bench
probe is prepared; hardware confirmation remains open.

A separate fixed-write census over the same four-hop graph finds no
RAM write at any RDBI callback root. The only transitive fixed RAM writes belong
to DID `F186`'s balanced Dcm critical-section helpers (`FEBE39DC/FEBE39E0`)
around a read of current session state `FEBE5934`; no persistence, SecOC,
lifecycle, or steering-control mutation is recovered from an RDBI read.

**Corolla caveat:** The Corolla EPS (`8965F1208000`) is a different
calibration. Its Dcm configuration tables are generated separately and may
populate the same security-level fields. The algorithm, secret location
pattern, and consumer machinery identified here are the template to check
against when Corolla firmware becomes available.

## 6.1 Security impact of the empty policy tables

The empty policy is not merely dead SecurityAccess UI. Several live application
operations remain reachable after session checks with no cryptographic tester
authorization:

- **CommunicationControl (`0x28`)** is available in extended session. It is
  subfunction-table driven (`0x9542C/0x9543C/0x9544C -> 0x95306 -> 0x95154`)
  and applies generated communication-mode updates. No speed gate is recovered
  in that service path. A bus-local tester can therefore exercise a
  safety-relevant communication availability surface without unlocking SID
  `0x27`. The reversible bench experiment is now implemented under
  `exploit/followups/communication_control_probe.py`: it uses only
  enable-Rx/disable-normal-Tx, restores enable-Rx/enable-Tx unconditionally,
  and requires every baseline-active Tx ID to recover. A live result is still
  hardware-gated.
- **Programming handoff (`0x10 02`)** is not SA-gated. It is constrained by
  vehicle speed, supply, transition phase, and handoff state, so it is not an
  unrestricted at-speed reset primitive. At permitted conditions it can still
  reset the EPS into its boot transition without proving tester identity.
- **All 19 configured RoutineControl RIDs** are free of Dcm SA levels. The
  corrected SID-`0x31` outer service object permits sessions `1/2/3`; therefore
  the 18 policy-0 RIDs are reachable directly from the default diagnostic
  session, subject to their individual runtime preconditions. `0x1007/0x1008`
  are zero-payload, one-shot live lifecycle reinitializers whose local
  preconditions omit the explicit vehicle-speed check used by neighboring
  `0x1002/0x1106`; `0x1009` is a state-gated variant. Their workers execute in
  normal per-tick scheduling for modes `>0x102`, including operational
  `0x300/0x400/0x500`. Two repeatable policy-0 persistence paths are especially
  weak-gated. RID **`0x1004`** is default-session reachable as `31 01 10 04 FF FF`;
  its precondition has no recovered vehicle-speed reference, operation 5 forces
  dirty event-log/history flags, and RoutineControl completion waits on NVM
  rewrites of objects 17/18/19/20/21/23. RID **`0x1108`** is a zero-payload,
  repeatable persistent checkpoint-reset trigger whose precondition has
  no recovered vehicle-speed reference: default-session `31 01 11 08` starts or
  queues operation 2, whose initializer resets/reinitializes state and persists
  checkpoint objects 9/11/12/14/15. Selector 10 reports completion; operation 6
  is coalesced through the same completion helper, so the path is not a narrow
  queue race. Separately, `0x110A/0x110C/0x110D` can request internal service
  modes 2/3/4 and transition the coordinator into special submode `0x520` under
  runtime preconditions. Exact graph closure keeps these diagnostic state
  families separate from the independently proved d/q current/PWM cone.
  RID `0x1010` is the exception to policy-0 reachability: its own policy is
  extended-session-only, and ICU-S independently authenticates its SHE M1–M3
  package and replay counter. See
  [../diagnostics/application-routine-control-surface.md](../diagnostics/application-routine-control-surface.md).
- **WriteDataByIdentifier (`0x2E`) has 13 implemented writable DIDs and no Dcm
  SecurityAccess requirement.** The corrected active chain is
  `0x93C62 -> 0x93B56 -> 0x92A70 -> 0x936AA/0x936D6 -> 0x8A630 -> 0x25768`.
  Eight DIDs (`2001/2002/2005/2006/2007/2008/2009/200D`) arm state machines
  that submit NvM object updates `0x101/0x102/0x103`; twelve of thirteen WDBI
  starts have a vehicle-speed gate. DID `0204` is also persistent but through a
  distinct asynchronous maintenance path: payload-byte-1 bit 7 selects mode
  request `0x11` versus `0x22`; both can persist checkpoint object 7
  (`three_phase_mode_latch`) before WDBI completion. The `0x22` completion path
  additionally starts queue operation 6, whose 12-callee initializer resets
  subsystem/runtime state and persists checkpoint objects 9/11/12/14/15. A
  complete direct-reference audit of that recovered cone has no conditioned
  steering-command or d/q-reference/current-PI/PWM join. DID `2010` is one of
  the gated writes but
  is statically bounded to write-only diagnostic residue: `B7C0E` writes
  `FEBEB48E/49C/4A0`, whose exact project xrefs have no runtime readers. Its
  apparent `FEBE816A=0x2E10` pending branch is unreachable because valid input
  produces mapper input `0` and invalid input `-12`, which `0x4C4A4` maps to
  `0/4`; only mapper input `-1` yields result `2`. DID `2012` is the exception
  to the speed-gated set: its start
  callback is unconditional, payload `01` sets `FEBEB18F=0x5A`, and extended
  session entry itself is not speed-gated because `0x4C942` checks speed only
  for requested programming session `02`. The downstream effect is now bounded:
  once the shared scaled-supply source reaches `0x0900`, `2012` forces logical
  transition-mask bit `0x08`; redundant encoding `mask^0xAA` clears physical
  bit 3 in `FEBEB18E`, and the same-tick transition worker takes `bnc` past the
  mode-specific lifecycle block. That inhibits the block that otherwise clears
  task/signal slots and submits object `5/6/8/9` reset/default NvM actions in
  modes `0x300/0x500` or advances phase in `0x400`. Separately, `2012` can force
  `FEBEB192=0x5A`, which causes `B30E0` to clear the alternate rotor-observer
  selector `FEBEB1D1`. Exact xref closure keeps both branches outside the direct
  d/q-reference/current-PI/TSG3-PWM producer set. DIDs `2013/2014` retain the
  common vehicle-speed plus two-state-flag start gate. `2013` propagates its
  16-bit parameter through `FEBEB434 -> 448 -> 452 -> 41A -> FEBEE416` and can
  enter motor-worker fields `FEBE6DCA/6DCC`, but their only readers are
  task/RTE staging and the resulting `66CE/66D0/63CE/63D0` mirrors are
  write-only. `2014` selects calibrated thresholds through `FEBEB3EE`; the
  same `B70D0` threshold result participates in RoutineControl start
  preconditions for RIDs `110A` and `110C`, while selector `3` used by `110D`
  skips that helper. Neither cone has a recovered direct d/q/PI/PWM join. See
  `data/application_wdbi_surface.csv` and
  [../diagnostics/application.md](../diagnostics/application.md).
- **ControlDTCSetting and proprietary `0xAB`** are also session-only. `0xAB` exposes event-record list/state/detail reads through subfunction workers; the recovered graph does not perform the formerly hypothesized motor-control, calibration, flash, or provisioning writes.
- **Proprietary `0xBA`** is extended-session only and has ten fixed operation descriptors. Its outer service object has no configured SecurityAccess level, but F7/`BAENA` has a callback-local level-2 gate. F7 persists a BA authorization marker plus 30-invocation countdown; while active, the generic gateway admits the remaining tokenized operations without a fresh SA read. The recovered effects are lifecycle/maintenance/persistent-state operations and bounded operational overrides, not a direct steering-current primitive. See [the dedicated BA report](../diagnostics/application-proprietary-ba.md).

For a comma integration this policy weakness is not a clean control interface.
It is primarily an availability/configuration surface, and the partially unnamed RoutineControl/OEM diagnostic semantics make it too fragile for steering control. A purpose-built,
authenticated, bounded application interface would be safer than depending on
these diagnostic side effects.

## 7. `0xAB` event-record closure

`0xAB` is structurally recovered as an event-record service. Selector 1 lists
active IDs from a checkpoint-backed 64-slot catalogue; selectors 2 and 3 query
per-ID state and detail. The complete configured indirect closure consists of
75 snapshot descriptors and six detail descriptors. It contains no known
crypto, NvM, ICU-S, SecOC, flash, or security-policy target and no GP-relative
SecOC key-buffer access.

The 13 callback pairs at `0x25768` belong to active SID `0x2E` WDBI. Their
lookup remains separate from SID `0xAB`, while SID `0x31` independently owns
direct callback `0x95DCE` and its 19-RID table at `0x26AEC`. CORR-056 records the
former dormant-RoutineControl/SID-`0x28` attribution error. The canonical
control-flow and table evidence is in
[the application diagnostics report](../diagnostics/application.md).

## 8. Hardware-validation status

Not yet validated on hardware. The protocol is documented for when a
matching ECU or bench setup is available:

1. Send `10 03` (extended session)
2. Send `27 03` + 16 zero bytes
3. Compute key with `sienna_application_sa_keygen.py`
4. Send `27 04` + key
5. Expect `67 04`

Rules: do not send writes, resets, `0xAB`, `0xBA`, or routines. Send `27 03` as
the first UDS request or include explicit padding bytes.

## 8.1 Cross-security-state composition audit (SEC-APP-008)

An explicit composition model
(`tools/generate_security_state_composition.py`, verified by
`tests/verify_security_state_composition.py`) composes the firmware-proven
state machines — UDS sessions (both contexts), application SA level 2, the BA
persistent authorization (SEC-APP-007), the programming handoff phase,
CommunicationControl, the XCP `0x7F7` connection, and the bootloader SA byte —
and queries privilege carryover and stale authorization across transitions.
Result:

- **No privilege composition stronger than the existing SEC-APP-007 BA
  reset-persistent downgrade exists.** Application SA and XCP are disjoint
  privilege domains: no XCP command reads the Dcm security mask or BA state.
- The programming handoff performs **no SA transfer** — no shared privilege
  byte exists between the application and bootloader contexts, and the boot SA
  byte re-arms locked at boot init (`0x5090` writes `1`), downgrading any
  unlock on session change (`0x561E` writes `1`).
- Exactly **one stale-authorization window** exists (BA dispatcher `0x348B4`
  skipping the fresh SA read while `FEBE5F27 == 0x5A`), bounded by the
  30-invocation countdown and requiring a prior legitimate SA2 enable.
- CommunicationControl composes communication **availability** only, not
  privilege.

## 9. Variant limitations

| Assumption | Status |
|---|---|
| Secret `893e08...5813` is universal | **Not assumed.** May be calibration-specific, market-specific, or software-version-specific |
| Corolla uses same algorithm | **Plausible but unproven.** Corolla responds to `27 03` with a seed and rejects `27 04` with NRC 0x35 — consistent with the same `03/04` mechanism but not proof of identical crypto |
| Corolla policy tables are also empty | **Unknown.** Must be checked against Corolla firmware when available |
| Data-record is always tester-controlled | **Proven for Sienna.** The Dcm dispatch code is the same Denso AUTOSAR stack; likely holds for Corolla but requires firmware verification |

## 10. Evidence

| Claim | Verification |
|---|---|
| AES-128 tables are FIPS-197 standard | `verify_application_diagnostics.py`: S-box, inverse S-box, Rcon, Te0[0] content checks |
| Crypto call chain | `verify_application_diagnostics.py`: 9 jarl call-edge assertions (exact bytes) |
| Data-record = PDU_buffer[2:18] | `verify_application_diagnostics.py`: ld.w instruction bytes at `0x94996`/`0x94A88` |
| No request-length check | `verify_application_diagnostics.py`: config value `0x10` at `0x26360` |
| Secret at `0x20840` | `verify_application_diagnostics.py`: exact 16-byte assertion |
| Services: all sec_count=0 | `verify_security_consumers.py`: 17 service-table checks |
| RDBI: no DIDs require level > 0 | `verify_security_consumers.py`: 242-DID bounded policy scan |
| RoutineControl: all 19 RIDs level_count=0 | `verify_security_consumers.py`: 19-RID policy checks |
| `0xAB` event closure: no selected sensitive targets | `verify_application_ab_service.py`: corrected service objects plus event catalogue/snapshot/detail closure |
| `0xBA` ten-operation surface and persistent authorization boundary | `verify_application_proprietary_ba.py` + live Ghidra assertion: exact table/tokens, F7 SA2 gate, object-24/object-5 persistence, restore/countdown, VSPD/SP1 separation, and no direct conditioned-command/d/q join |
| Consumer set is exhaustive | `verify_security_consumers.py`: exact address-set assertion (11 addresses) |

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [DIAG-APP-009](../reference/index.md#finding-diag-app-009), [DIAG-APP-010](../reference/index.md#finding-diag-app-010), [DIAG-APP-011](../reference/index.md#finding-diag-app-011), [DIAG-APP-012](../reference/index.md#finding-diag-app-012), [DIAG-APP-013](../reference/index.md#finding-diag-app-013), [DIAG-APP-015](../reference/index.md#finding-diag-app-015), [DIAG-APP-016](../reference/index.md#finding-diag-app-016), [DIAG-APP-017](../reference/index.md#finding-diag-app-017), [DIAG-APP-018](../reference/index.md#finding-diag-app-018), [DIAG-APP-019](../reference/index.md#finding-diag-app-019), [DIAG-APP-020](../reference/index.md#finding-diag-app-020), [DIAG-APP-021](../reference/index.md#finding-diag-app-021), [DIAG-APP-022](../reference/index.md#finding-diag-app-022), [DIAG-APP-024](../reference/index.md#finding-diag-app-024), [KEYLESS-006](../reference/index.md#finding-keyless-006), [KEYLESS-012](../reference/index.md#finding-keyless-012), [SEC-APP-001](../reference/index.md#finding-sec-app-001), [SEC-APP-002](../reference/index.md#finding-sec-app-002), [SEC-APP-003](../reference/index.md#finding-sec-app-003), [SEC-APP-004](../reference/index.md#finding-sec-app-004), [SEC-APP-005](../reference/index.md#finding-sec-app-005), [SEC-APP-007](../reference/index.md#finding-sec-app-007), [SEC-APP-008](../reference/index.md#finding-sec-app-008)
- Corrections with this document as canonical home: [CORR-053](../reference/index.md#correction-corr-053), [CORR-055](../reference/index.md#correction-corr-055), [CORR-056](../reference/index.md#correction-corr-056), [CORR-057](../reference/index.md#correction-corr-057), [CORR-058](../reference/index.md#correction-corr-058)
<!-- knowledge-cross-references:end -->
