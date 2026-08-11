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

## Save, normalize, and verify

Keep the raw `j2534_MMDDYYYYhhmmss.log` private and immutable. Hash it before
parsing, then normalize it with the locked environment:

```bash
uv run --locked python tools/techstream/parse_ptshim_log.py \
  build/target-evidence/private/j2534_MMDDYYYYhhmmss.log \
  -o build/target-evidence/private/health_check.normalized.json
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
