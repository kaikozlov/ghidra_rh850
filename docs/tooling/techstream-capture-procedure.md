# Techstream J2534 capture procedure

> **Status:** procedure verified against the pinned V18 shim/parser; no exact
> target session captured

Use this procedure only on an authorized, isolated bench with stable power and
a recoverable ECU state. It defines the evidence needed to join static
Techstream builders to labeled runtime requests; it does not authorize a
production-vehicle reflash.

## Before capture

1. Record the target's exact part/calibration number, raw `F181` response,
   region, and a pseudonymous session ID in a private instance of the target
   manifest. Do not put VIN or account identifiers in the session ID.
2. Hash the Techstream executable, shim, matching regional DDB files, VCI
   driver, and `.cuw`/calibration package. Record software versions and local
   paths privately.
3. Save complete CodeFlash and DataFlash backups where authorized and hash
   them. A reflash/programming trace is not attempted without a recovery path.
4. Configure the correct `ptshim32.dll` (J2534 v04.04) or
   `ptshim32_0500.dll` (v05.00) in front of the real VCI driver. Confirm a
   synthetic/read-only connection produces a parseable UTF-8 SaveLog.
5. Start with synchronized UTC host time and record the physical channel,
   J2534 protocol, bus wiring, ignition/power state, and bench operation label.

## Capture six separate operations

Start a fresh logger/session boundary for each operation. Do not combine them
under an inferred label.

| Capture key | Operation | Minimum label/context |
|---|---|---|
| `health_check` | health check / ECU discovery | pre/post ignition state, selected ECU, DTC read/clear choice |
| `data_list` | data-list view | exact list/page and sampling interval |
| `active_test_customization` | active test or customization | exact UI action, commanded value, duration, observed result |
| `mackey_registration` | MACKey Registration | master/slave selection and stage label; never commit VIN/account/server tokens |
| `cuw_preparation` | CUW selection and preparation | `.cuw` hash, selected calibration row, preparation stage, stop before programming if not authorized |
| `reflash_authorization_programming` | RKS authorization and programming | online/offline mode, authorization stage, erase/download/reset boundaries, recovery result |

For every operation retain Tx/Rx direction, logger elapsed timing, message
timestamp, ChannelID, J2534 protocol, flags, four address bytes, exact payload
bytes, reported/actual lengths, and any extra bytes. Preserve API-call and
status lines so connection/filter/ioctl state is reconstructible.

## Sienna ordinary-UDS motor/control observer card

For `8965B4512000`, TMS-027 already resolves the high-value observer DIDs and
engineering-unit transforms. A later labeled steering experiment should poll
these rather than spending paid-session time rediscovering Data IDs:

| Order | Request | Observer | Interpretation |
|---:|---|---|---|
| 1 | `22 1C 02` | `Command Value Torque` | signed `0.01 Nm/LSB`; general internal command torque |
| 2 | `22 11 52` | Q command | signed `0.01 A/LSB`; base Q-current command |
| 3 | `22 11 51` | Q actual | signed `0.01 A/LSB`; closed-loop follower |
| 4 | `22 11 56` | final Q limit | non-negative `0.01 A/LSB` |
| 5 | `22 10 65` | limit-positive companion | one-byte boolean; structural companion |
| 6 | `22 11 54` | D command | signed `0.01 A/LSB`; base field-axis command |
| 7 | `22 11 53` | D actual | signed `0.01 A/LSB` |
| 8 | `22 11 85` | SP1 speed | `0.01 km/h/LSB`; protected `0x0D7` source; pair with `0102` |
| 9 | `22 11 55` | motor angle | `0.01 deg/LSB`; `0xFFFF` is an internal-Dem invalid marker |

Keep exact request/response timestamps and the concurrent external CAN stimulus.
In particular, do not equate `1C02` with the external authenticated `0x2E4`
command merely because they correlate: the static result proves a general
internal torque observer and its downstream motor-current consequence, while
exact contributor provenance remains a live/static residue. The machine-readable
card and read-only XCP candidate addresses are in
`data/generated/sienna_8965B4512000_techstream_did_semantics.json`.

## CUW timing/recovery capture checklist

TMS-030/TMS-031 move the CUW timing/recovery work out of exploratory RE. For an
authorized reflash/recovery experiment, capture these artifacts as a synchronized
set:

1. **Route identity before programming:** hash the raw calibration package and
   extracted `attach.att`; retain selected factory identifier, contact type, CPU
   type/image index, prepare/flash writer names, request/response CAN IDs, and
   `F181`.
2. **SecurityAccess timing:** retain exact timestamps for `10 02`, the complete
   `27 01` request/`67 01` response, `27 02`/`67 02`, and the first following
   reprogramming command. Do not assume the legacy 100-ms seed/key timing applies
   to Unified; compare the observed spacing with the selected writer family.
3. **Reset/reconnect boundary:** retain J2534 `PassThruConnect`/disconnect,
   filter/ioctl, Tx confirmation, ECUReset response, silence interval, first
   post-reset receive, and any CAN-vs-Ethernet reconnect choice.
4. **Power/ignition observables:** sample Data IDs `0016`, `0017`, `0018`,
   `0019`, `0033`, `0034`, `0036`, `0421`, `0422`, `07D1`, `07D2`, `26AC`,
   `26AD`, `26C0`, `26C1`, and `26C3` across IG OFF/ON and retry. `0167`
   (`Engine Stall/READY OFF Control History`) is a useful companion.
5. **Recovery-file snapshots:** before the job, immediately after recovery state
   is created, after each CPU/image boundary where practical, immediately after
   an authorized interruption, after restart/recovery eligibility is shown, and
   after final success/delete, preserve hashes/copies of `Save/RecoveryInfo.ini`
   and the referenced saved calibration payload. Record whether `WriteCpuIndex`,
   `Writing`, `UseNewSoftwarePassword`, `WritingEndBlock`, and
   `PassThruErrorCode` changed.
6. **Identity check evidence:** privately retain the VIN/AssyNo/CID values used by
   the recovery screen only long enough to prove same-vehicle eligibility; do
   not commit those identifiers. The V18 client binding is procedural rather
   than cryptographic.
7. **Retry count/UI state:** timestamp every retry prompt/state and whether the
   writer executes `PrepareRetry`; preserve enough evidence to distinguish the
   static three-attempt UI model from the exact runtime counter behavior for the
   selected route.

The static expectation set is machine-readable in
`data/generated/techstream_v18/cuw_timing_recovery.json`. Any mismatch is a new
finding; do not coerce the live trace to the V18 model.

## Save, normalize, and verify

Keep the raw `j2534_MMDDYYYYhhmmss.log` private and immutable. Hash it before
parsing, then normalize it with the locked environment:

```bash
uv run --locked python tools/techstream/parse_ptshim_log.py \
  build/out/target-evidence/private/j2534_MMDDYYYYhhmmss.log \
  -o build/out/target-evidence/private/health_check.normalized.json
```

Hash the normalized JSON and record both hashes in the private manifest. Check
that the parser preserved direction, timing, channel/protocol, address bytes,
payload bytes, lengths, flags, unparsed lines, and encoding. A parser warning or
unparsed message is a capture-review item, not a reason to silently drop data.

## Redaction and committed derivatives

Raw Techstream logs and proprietary artifacts are never committed. Before any
normalized derivative is considered for Git, inspect request and response
payloads as well as API arguments and preamble text for:

- VIN and registration identifiers;
- Techstream/TIS account, license, and requester fields;
- RKS signatures, server request/session IDs, cookies, or URLs;
- SecurityAccess seeds/keys, MACKey packages, or other secret material;
- filesystem/user names and VCI serial numbers.

If byte-level redaction would destroy the diagnostic evidence, commit only a
hash/count/timing summary and keep the normalized transcript private. Record
the redaction decision, reviewer, and derivative hash in the manifest. Never
commit the pseudonym salt.

## Static joins after capture

Compare each labeled request/response sequence separately with the recovered
V18 builders and target firmware tables. A join requires exact bytes plus
operation context; vocabulary or temporal proximity alone is insufficient.
Specifically test whether generic J2534 operations transmit any SecOC/TSK
runtime frames. Until a labeled trace does so, the strongest V18 statement is
only: **no named/static `SecOC` or `VehSec` path was recovered in the pinned
V18 corpus**.

## Current blocker

No authorized exact-target bench, matching `.cuw`, or labeled official session
is available in this repository. All six capture entries therefore remain
`missing` in the committed example manifest; no runtime join is claimed.
