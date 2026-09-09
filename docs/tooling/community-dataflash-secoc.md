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

A later contributor corpus now supplies CodeFlash and identifies that firmware
artifact as `8965H1202000` / `8A3111202000` on `R7F701383`; see
[`../variants/corolla-2023-us-public-route.md`](../variants/corolla-2023-us-public-route.md).
The public route still lacks a stock `carFw`/direct-F181 join, so vehicle-to-image
attribution remains external. This specimen must also remain separate from the
distinct directly probed `8965F1208000` Corolla. The DataFlash key-search result
above is unchanged by the new CodeFlash evidence.

## 6. Calvin `dump` range-dumper archaeology and repeatability

The exploratory range dumper is now pinned independently at
`calvinpark/openpilot@42d1120395877e96ed440646a765157a0ad7646b`. Its six
current 4-KiB authenticated payloads cover:

```text
00000000..00200000  CodeFlash
01000000..0100C000  CodeFlash extended area
FEBE0000..FEC00000  PE1 local RAM
FEDE0000..FEE00000  self local-RAM window
FEEF8000..FEF08000  global RAM
FF200000..FF210000  64-KiB host range (DataFlash only through FF207FFF on R7F701383)
```

`data/p1me_product_memory.json` now pins the Renesas product/address geometry:
`R7F701383` is a 1-MiB DPS part with 32-KiB DataFlash, 128-KiB total local RAM,
and 64-KiB global RAM. The hardware manual exposes both `FEBE0000..FEBFFFFF`
(PE1 area) and `FEDE0000..FEDFFFFF` (self view) as 128-KiB local-RAM mappings;
with only 128 KiB physical local RAM, the self window is an architectural view
of the same PE-local memory, not an additional bank. Calvin's repeated Sienna
experiment is useful dynamic confirmation, not the sole basis for the alias.

All six payload packages independently decrypt/authenticate with the recovered
payload-build secret at CodeFlash `0xBFD8`, have CRC residue `0xFFFFFFFF`, and
carry callback/descriptor `FEBF0000` / length `0xFF0`. In the executable body
below `0xFD0`, exactly six bytes vary, encoding four range-immediate fields; the
CRC fixup at `0xFEC..0xFEF` also varies as expected. The range binaries use a
reset-return body distinct from Willem's 32-KiB DataFlash self-loop artifact,
but reset-return itself is older: Willem's earlier RAM dumper already returns
through boot reset `0x157E`. A source/toolchain cross-check closes that lineage
more tightly: rebuilding Bk2ol's later-public
`payload_source/shellcode/main_ff1ff000_ff209000.c` with its GCC 13.2/binutils
2.41 V850 toolchain and substituting the global-RAM range reproduces Calvin's
**entire encrypted** `payload_global_ram_feef8000_fef08000.bin` byte-for-byte
(SHA-256 `43d00fda...`). The other shipped ranges preserve one long-body binary
layout and patch fixed immediates, so recompiling each source variant can select
shorter instruction encodings and is not expected to byte-reproduce every
package. This proves source/compiler-family equivalence, not original authorship:
Vance's candidate-f05 artifact predates Bk2ol's public source, so the pre-public
source provenance remains bounded by SECOC-031.

The branch history is also rewritten. The original July `Range dumper` and
`mo-dump` commits were first pushed on `tskm`; `wide` was created only during the
2026-08-12/13 history split and was renamed `dump` on 2026-08-19. Orphaned
commits preserve an abandoned 288-KiB DataFlash payload
`FF200000..FF238000`, split 1-MiB CodeFlash payloads, and an older wide RAM
profile. The final six payload blobs themselves remained byte-identical through
the later rebases/amends. Full chronology is in
[`CALVIN_TSKM_DUMP_ARCHAEOLOGY_2026-08-21.md`](../history/2026-08/CALVIN_TSKM_DUMP_ARCHAEOLOGY_2026-08-21.md).

One provenance question in Calvin's journal can also be closed from public Git.
The `DEFAULT -> sleep(.5) -> EXTENDED -> sleep(.7) -> PROGRAMMING ->
sleep(1.0) -> PROGRAMMING` ladder appears verbatim in Bk2ol's pinned
`steps/step_dump_dataflash.py`; Calvin's current `dump_range.py` preserves that
exact timing as a declarative four-step ladder. This gives the timing ladder a concrete public Bk2ol precursor/common lineage
point; byte-for-byte sequence identity does not by itself establish who copied
or authored it first.

### Repeatability changes how dump negatives are graded

Calvin's Sienna journal first recorded two complete **64-KiB range reads** 21
seconds apart differing in 16,703 bytes (25.487%). For H we can now separate the
physical region from the host profile: official P1M-E product data identifies
`R7F701383` as a DPS 1-MiB device with **32 KiB DataFlash** at
`FF200000..FF207FFF`. The `FF208000..FF20FFFF` upper half of Calvin's 64-KiB
profile is outside the specified DataFlash array and must not be used as
DataFlash evidence.

The retained H corpus still independently demonstrates poor repeatability in the
**actual first 32 KiB DataFlash**:

| range | retained repeats | pairwise divergence |
|---|---:|---:|
| actual DataFlash `FF200000..FF207FFF` | 5 | 23.5077%-25.6470% |
| full 64-KiB host range (includes off-array half) | 5 | 26.2650%-27.7328% |
| extended CodeFlash 48 KiB | 3 | 0 bytes |
| global RAM 64 KiB | 3 | 1.1932%-1.2070% |
| PE1 local RAM 128 KiB | 3 | 2.8053%-3.2166% |

Only 17,325/32,768 physical-DataFlash byte positions are identical across all
five retained reads. The cause is deliberately left open; “read-to-read capture
divergence” is the observation. Do not interpret the off-array upper half as
flash noise, an extra array, or a harmless region: the hardware manual classifies
the enclosing area as P-Bus address space and warns against unspecified/reserved
accesses.

The useful distinction is between **single-byte content** and **repeated
structure**. Every one of the five DataFlash reads still independently decodes
objects 0/2/5 with three valid copies and object 15 with zero valid copies. That
structural conclusion therefore survives; an isolated candidate or null byte in
one read does not. `tests/verify_albinoelephant_corolla_repeatability.py` pins
these exact dispositions and divergence ranges.

One host-tool limitation also remains explicit at the pinned tip:
`matcher.ORACLE_BUSES={0,2}` is Sienna-shaped and discards a bus-1-only Corolla
oracle. It fails closed as `insufficient_oracle` rather than installing a bad
key, but it can misleadingly ask for “more CAN” forever on a vehicle whose
protected traffic is on bus 1. Repository-local `toyota_secoc_oracle.py` already
avoids that restriction.
