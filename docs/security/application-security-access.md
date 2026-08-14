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

**No configured SecurityAccess gating was found at the service, RDBI, or WDBI
policy layers in this Sienna calibration.** The complete configured `0xAB`
event-record graph likewise contains no direct sensitive target. The
security-state machinery is wired up and exercised, but the policy tables are
empty.

| Scope | Check | Result |
|---|---|---|
| All 17 services (Dcm dispatch layer) | `sec_count=0` at `0x25E28 + i*0x18 + 0x12` | No service is security-gated |
| All 242 readable DIDs (RDBI) | Policy table at `0x261A4`, bounded scan of recognized policy records | No DID requires level > 0 |
| RDBI callback disclosure boundary | Firmware table `0x2941C` (242 rows / 196 unique callbacks), exact dispatch at `0x4CB8A→0x4CBB2`, depth-4 direct-call audit | No recovered path into command-5 output, key-update result bank, payload-derived key material, or application-SA seed/data/temp RAM; selected hits reduce to generic NvM workspace plus status accumulator `FEBE5050` |
| All 19 writable DIDs (WDBI) | Policy table at `0x26420`, flag at `0x26B8D` | All have `level_count=0` |
| `0xAB` operation-F1, event worker, 75 snapshot descriptors, six detail descriptors | Resolve configured indirect tables, then census direct descendants and GP key displacements | Zero matches to crypto/NvM/ICU-S/SecOC/security-policy targets |

The architecture is:

```
Generic Denso/AUTOSAR diagnostic stack:
    full SecurityAccess implementation
    unlock bitmask machinery
    per-service / per-DID security hooks

Sienna 8965B4512000 calibration:
    level-2 crypto enabled (real secret, real AES)
    security policy tables unpopulated
```

The algorithm and unlock state are real; the policy tables are empty. The
unlock may be a dormant platform feature rather than an intentional
protection boundary on this firmware.

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

- **CommunicationControl (`0x28`)** is available in extended session. Its real
  callback `0x93C62 → 0x93B56/0x95154` applies generated communication-mode
  updates; this is not one of the null-callback echo services. No speed gate is
  recovered in that service path. A bus-local tester can therefore exercise a
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
- **All 19 WDBI records** are free of Dcm SA levels. The generated lower-request
  hook at `0x8A01C` is compiled to `return 0`, so there is no second external
  authorization manager behind the Dcm policy. The surface is now substantially
  classified rather than merely structural: 18 records share policy index 0
  (effective programming/extended access after the outer SID-`0x2E` gate).
  `0x1007/0x1008` are zero-payload, one-shot live lifecycle reinitializers whose
  local preconditions omit the explicit vehicle-speed check used by neighboring
  `0x1002/0x1106`; extended-session policy also has no stationary gate because
  `application_session_transition_policy @ 0x4C942` applies its speed rejection
  only to requested session 2. Their workers execute in the normal per-tick
  scheduler for modes `>0x102`, including operational `0x300/0x400/0x500`.
  Separately, `0x110A/0x110C/0x110D` can request internal service modes 2/3/4
  and transition the coordinator into special submode `0x520` under runtime
  preconditions. Exact graph closure keeps both diagnostic state families
  separate from the independently proved d/q current/PWM cone, so the supported
  impact is unauthenticated availability/control-state exposure rather than
  arbitrary steering actuation. DID `0x1010` is safer than the Dcm table suggests
  because ICU-S independently authenticates its SHE M1–M3 package and counter. See
  [../diagnostics/application-wdbi-surface.md](../diagnostics/application-wdbi-surface.md).
- **ControlDTCSetting and proprietary `0xAB`** are also session-only. `0xAB`
  exposes event-record list/state/detail reads through an asynchronous worker;
  the recovered graph does not perform the formerly hypothesized motor-control,
  calibration, flash, or provisioning writes.

For a comma integration this policy weakness is not a clean control interface.
It is primarily an availability/configuration surface, and the unknown WDBI
semantics make it too fragile for steering control. A purpose-built,
authenticated, bounded application interface would be safer than depending on
these diagnostic side effects.

## 7. `0xAB` event-record closure

`0xAB` is structurally recovered as an event-record service. Selector 1 lists
active IDs from a checkpoint-backed 64-slot catalogue; selectors 2 and 3 query
per-ID state and detail. The complete configured indirect closure consists of
75 snapshot descriptors and six detail descriptors. It contains no known
crypto, NvM, ICU-S, SecOC, flash, or security-policy target and no GP-relative
SecOC key-buffer access.

The 13 RID callback pairs at `0x25768` are separate. Their lookup's only direct
caller belongs to a dormant RoutineControl worker; stock SID `0x31` has a null
callback, and there is no edge from `0xAB` to the RID lookup. The canonical
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

Rules: do not send writes, resets, `0xAB`, or routines. Send `27 03` as
the first UDS request or include explicit padding bytes.

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
| WDBI: all level_count=0 | `verify_security_consumers.py`: 19 write-DID checks |
| `0xAB` configured direct/indirect closure: no sensitive targets | `verify_application_ab_service.py`: operation-F1, event-catalogue, 75-record snapshot table, six-record detail table, and callback-target assertions |
| Consumer set is exhaustive | `verify_security_consumers.py`: exact address-set assertion (11 addresses) |
