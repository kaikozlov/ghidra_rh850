# Community DataFlash/SecOC extraction tooling — static audit and generic oracle

> **Scope:** pinned `Bk2ol/tsk_extraction_by_can_log` commit
> `db453752beeb7cdd024a1a9c38c6711c981e75ad`, pinned commaai/opendbc SecOC
> profile, and repository-local analysis tooling
>
> **Status:** active
>
> **Evidence source:** external-source plus generated-artifact
>
> **Verification:** `tests/verify_toyota_secoc_oracle.py`; optional pinned-source
> verification `tests/verify_external_corroboration.py`
>
> **Canonical local tool:** `tools/toyota_secoc_oracle.py`

The community DataFlash extractor is valuable because it reuses the solved
Toyota/Denso authenticated-RAM-execution bootstrap and can recover a complete
32 KiB DataFlash dump. Its current capture/key-verification layer is narrower
than that bootstrap, however: several assumptions are hardcoded for the Sienna
traffic profile and Panda routing used by its authors.

Those assumptions matter when interpreting a negative result on another Toyota
variant. In particular, a report such as `0 protected` is only a statement about
the IDs and buses that the current script counted. It is **not** evidence that
the vehicle has no SecOC traffic.

## 1. Pinned hardcoded assumptions

The following are pinned in `external-references.lock.json` and asserted by the
optional external-source verifier:

| File | Static assumption |
|---|---|
| `steps/step_dump_dataflash.py` | EPS diagnostic endpoint `0x7A1 -> 0x7A9`; Panda `BUS = 0`; `set_safety_mode(3)` |
| `steps/step_eps_probe.py` | Panda `BUS = 0` |
| `steps/step_collect_can.py` | oracle buses exactly `{0, 2}` |
| `steps/step_collect_can.py` | oracle IDs exactly `{0x00F, 0x131, 0x2E4, 0x344}` |
| `steps/step_extract_verify_key.py` | protected IDs exactly `{0x131, 0x2E4, 0x344}` |
| `steps/step_extract_verify_key.py` | verification buses exactly `{0, 2}` |

The DataFlash dumping bootstrap itself is not tied to those three protected
CAN IDs; they are only used later to validate candidate key material against a
capture.

Therefore, on a variant whose protected traffic uses another known Toyota
classic-SecOC ID such as `0x116` or `0x24D`, the current verifier can produce
zero protected samples even while a valid synchronization stream and valid
protected traffic are present.

## 2. Full pinned Toyota classic-SecOC profile

Pinned `toyota_secoc_pt.dbc` defines the following eight ordinary protected
classic-CAN messages plus synchronization:

| CAN ID | DBC name | Kind |
|---:|---|---|
| `0x00F` | `SECOC_SYNCHRONIZATION` | synchronization |
| `0x116` | `GAS_PEDAL` | protected |
| `0x131` | `STEERING_LTA_2` | protected |
| `0x177` | `PCM_CRUISE_3` | protected |
| `0x183` | `ACC_CONTROL_2` | protected |
| `0x24D` | `PCM_CRUISE_4` | protected |
| `0x283` | `PRE_COLLISION` | protected |
| `0x2E4` | `STEERING_LKA` | protected |
| `0x344` | `PRE_COLLISION_2` | protected |

Each ordinary DBC block carries the same `AUTHENTICATOR`, `RESET_FLAG`, and
`MSG_CNT_LOWER` trailer fields. Pinned `opendbc/car/secoc.py` independently
implements the common authenticating construction:

```text
DataID_be16 || payload4 || freshness48
```

with a 28-bit truncated AES-CMAC. This is the same classic wire construction
independently recovered from the analyzed Sienna EPS, but the **set of IDs used
by a particular vehicle or receiving ECU must still be established per
variant**.

The machine-readable repository profile is
`data/toyota_classic_secoc_profile.csv`.

## 3. Repository-local generic oracle

`tools/toyota_secoc_oracle.py` removes the Sienna-specific analytical
assumptions without modifying the pinned external checkout.

It:

- accepts synchronization and protected traffic on any observed Panda bus;
- tracks synchronization state independently per bus;
- recognizes the complete pinned classic-SecOC ID profile by default;
- can be restricted to explicit buses or IDs for a controlled experiment;
- never associates a protected frame with synchronization state from another
  bus;
- verifies a supplied 16-byte key independently for synchronization and each
  protected CAN ID;
- reconstructs the full message-counter candidate set from the transmitted
  low-two counter bits and reset-low-two bits;
- scans every sliding 16-byte window in a dump after a synchronization-CMAC
  prefilter;
- reports candidate address/hash and per-ID match counts without printing raw
  key bytes.

Synthetic tests deliberately place `0x00F`, `0x116`, and `0x24D` on **bus 1**
and prove that the local oracle verifies them while refusing to associate an
orphan `0x2E4` frame from bus 2.

### Example

```bash
uv run --locked python tools/toyota_secoc_oracle.py scan \
  --capture can.ndjson \
  --dump dump_ff200000_ff208000.bin
```

The result separates:

- synchronization matches;
- `0x116` matches;
- `0x24D` matches;
- every other protected ID actually present in the capture.

This makes a future Corolla DataFlash/capture pair a direct cryptographic test
rather than another heuristic entropy search.

## 4. Explicit cross-variant research session

`tools/toyota_secoc_session.py` turns the remaining implicit workflow
assumptions into durable session state without performing ECU mutation. It
records:

- EPS UDS endpoint (`0x7A1 -> 0x7A9` by default);
- diagnostic Panda logical bus once discovered;
- explicit ELM327 routing parameter (default `1`, normal CAN routing);
- oracle buses (default `0/1/2`);
- the complete configurable protected-ID profile;
- target openpilot car enum for review-only fingerprint planning;
- observed F181/software identity;
- per-bus/per-ID capture counts and retained oracle location.

The session consumes execution output from the existing read-only
`toyota_eps_bus_probe.py`. A unique F181 responder is persisted as the diagnostic
bus; multiple responders fail closed unless the analyst explicitly selects one.
It can then ingest a full NDJSON CAN capture, retain the configured sync/protected
profile across any selected buses, and hand the resulting oracle to
`toyota_secoc_oracle.py`.

Example:

```bash
uv run --locked python tools/toyota_secoc_session.py init session \
  --target-car CAR.TOYOTA_COROLLA_TSS2

uv run --locked python tools/toyota_eps_bus_probe.py --execute > probe.json
uv run --locked python tools/toyota_secoc_session.py record-probe session probe.json
uv run --locked python tools/toyota_secoc_session.py ingest-can session all_can.ndjson
uv run --locked python tools/toyota_secoc_session.py fingerprint-plan session
uv run --locked python tools/toyota_secoc_session.py oracle-plan session --dump dump.bin
```

The fingerprint step is deliberately a **plan**, not an automatic source patch:
it records the observed EPS address/F181 against the selected target car so an
analyst can review the appropriate openpilot fingerprint entry without silently
injecting Sienna defaults into another vehicle.

`tests/verify_toyota_secoc_session.py` proves that the manager contains no
programming-session, SecurityAccess, DID-write, RequestDownload, RoutineControl,
CAN-send, or Panda-safety mutation path. Device-side mutating dump behavior
remains in the separately pinned community tooling; the repository-local
cross-variant layer is read-only/offline.

## 5. 2023-US-Corolla field closure

The previously missing field artifacts are now retained under
`community/albinoelephant/` for the separately reported 2023 US Corolla
specimen described in `docs/variants/corolla-2023-us-public-route.md`.

The contributor's own TSKM oracle is sync-only: 1,232 `0x00F` rows, split as 616
on Panda bus 0 and 616 on bus 2, with no protected-message rows. That directly
explains the TSKM matcher failure. A repository-derived CAN-only oracle from the
contributor's already-pinned public route adds the genuine bus-1 protected
traffic (`0x116` and `0x24D`) without retaining route metadata.

The complete 32 KiB DataFlash dump was then scanned with
`tools/analyze_toyota_dataflash.py --domain-scan --min-entropy 0`. All 32,753
overlapping 16-byte positions are considered (23,277 unique raw windows after
deduplication), and no candidate passes the synchronization, `0x116`, or
`0x24D` cryptographic probe.

This closes the raw-DataFlash key hypothesis for this snapshot at the strongest
current offline boundary: **no raw 16-byte window in the supplied DataFlash is
a key for any of the three observed classic domains**. It does not exclude an
ICU-S/HSM-owned key, a key stored outside this 32 KiB range, or a different
transformation/derivation not represented by a raw window or the known NvM
triplicate decode.

The same dump independently corroborates part of the `4512000` physical NvM
layout: objects 0, 2, and 5 have three committed raw/XOR55/XORAA copies at the
same addresses and decode to valid consensus payloads, while object 15 has no
valid copy. Thus the related `4514000` CPU-visible object-15 key-storage result
does not reproduce here even though part of the storage geometry itself does.

Machine-readable result:
`data/generated/corolla_2023_albino_dataflash_analysis.json`.

The exact EPS F181 and CodeFlash remain unavailable, so this evidence must stay
separate from the exact `8965F1208000` Corolla calibration investigation.
