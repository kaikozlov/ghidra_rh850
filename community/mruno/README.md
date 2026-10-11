# mruno Crown EPS field artifacts

**Contributor:** mruno (`@mruno`, comma Discord)
**Received:** 2026-09-13
**Vehicle attribution:** reported 2024 Toyota Crown Limited
**Application F181:** `8965F3012000`
**Static secondary F181 record:** `8A3113008000` at CodeFlash `0x17DC0`
**Auxiliary one-record identity:** `8965H3008000` at CodeFlash `0x17D80`
**MCU boot-info:** RH850/P1M-E `R7F701381`

This directory preserves the first mruno Crown EPS memory artifacts supplied from
the contributor's TSK/dump investigation. The three `.bin` files are retained
byte-for-byte. They should be treated as source evidence; do not rewrite the raw
files in place.

## Supplied artifacts

| File | Size | MD5 | SHA-256 | Interpretation |
|---|---:|---|---|---|
| `crown-eps-dataflash-dump-20260913.bin` | 32,768 | `e9865f35fce9dae03ce5438b33fd671a` | `0c7b027900d4ac12a4e665e17c0575d44efb0ccfbcb6239416a40c8260c50872` | Complete `0xFF200000..0xFF207FFF` DataFlash snapshot reported by the contributor. The MD5 is the value posted with the acquisition. |
| `dump_dataflash_ff200000_ff210000_20260913-213026.bin` | 65,536 | `f8de455bcdaf9e5a1d6cf18e828cd88d` | `5e37da024723d1d7ac1ece7a8430f8a335110db97b1f4d0f00f7e78c0fd716aa` | Separate 64-KiB host-range read. On `R7F701381`, only the lower 32 KiB is specified physical DataFlash. Its lower 32 KiB differs from the earlier snapshot in 2,880 bytes, so this is not a duplicate capture. |
| `partial_codeflash_00000000_00200000_20260913-220010_2075572of2097152.bin` | 2,097,152 | `9ebbd0051a52c0a085add483866b58bd` | `d4952d5aeb385709d6705750b59bbce46b06cc56790c09e361a7c83e746f6560` | Collector output for the `0x00000000..0x001FFFFF` host range. The contributor reports 2,075,572/2,097,152 bytes received before a Panda SPI failure and zero gaps in the populated lower 1 MiB. |

## CodeFlash completeness boundary

The CodeFlash filename reports **2,075,572 received bytes**, leaving **21,580
bytes** missing from the requested 2-MiB host range. The retained file is still
2 MiB long: the exact missing count appears as one zero-filled trailing interval
`0x001FABB4..0x001FFFFF`. Every retained byte from `0x00100000` through
`0x001FABB3` is `0xFF`.

The contributor reports that the complete populated CodeFlash is the lower
`0x00000000..0x000FFFFF` region and that all missing coverage is in the erased
upper host-range tail. The raw file is consistent with that report. For analysis,
the first 1 MiB has:

```text
SHA-256  5b89fdbc69edc2f66ef8a557f88b08c758e3146bd4e90067320d7966812b1273
MD5      ea869e7cfd2e3e40bca512afe8be2fcd
```

Do **not** treat the zero-filled final 21,580 bytes of the supplied 2-MiB file as
firmware content. No separate coverage bitmap or run JSON accompanied this
import, so the contributor's stated lower-1-MiB completeness remains the
provenance boundary.

## Identity visible in CodeFlash

The retained lower image independently contains:

```text
0x00000190  R7F701381
0x00017D80  8965H3008000
0x00017DC0  8A3113008000
0x00020860  8965F3012000
```

The low boot credential roots are also present at the same addresses used by the
tracked Toyota/Denso P1M-E EPS family (`0xBFD8` payload-build root and `0xBFE8`
boot SecurityAccess root). Exact semantic transfer to the Crown should be made
from this CodeFlash rather than assumed from part-number similarity.

## Acquisition context retained from the contributor

The contributor reports that Calvin's existing DataFlash and CodeFlash dump
payloads executed successfully on this Crown after the direct EPS diagnostic
route was corrected. The route discussed immediately before this acquisition
was the stock Toyota-B normal-harness path, `set_safety_mode(3, 1)` with Panda
logical bus 1. No machine-readable route transcript accompanied the imported
files, so `bus1,param1` is retained as contributor-reported acquisition context,
not as a locally replayed capture. The CodeFlash collection repeatedly hit
`PandaSpiNackResponse` near the end of the 2-MiB transfer, so the contributor
changed the collector to preserve the partial buffer instead of discarding it.
That collector patch and its coverage metadata were not supplied with these
three artifacts.

The contributor also reports an offline SecOC-key scan over the 32-KiB DataFlash
using more than 12,000 signed Crown frames (`0x090`, `0x0D7`, `0x116`, `0x24D`)
with zero key matches. The CAN oracle is **not** part of this import, so that
zero-match result remains external-source context rather than a locally
reproducible repository result.

## Read-only preflight artifacts received 2026-09-14

Both files below are retained unchanged. The Python file is the contributor's
troubleshooting variant, not the current shipped implementation; it was read and
compared, not executed against a vehicle during this review.

| File | Size | SHA-256 | Interpretation |
|---|---:|---|---|
| `crown-preflight.json` | 908 | `eedb0bd89b8f1fd62a45d8e017c4e777ea2843ddb49744c07b86fe20afd4e0e7` | Contributor heartbeat-preflight result: exact Crown F181, requested five-second interval, three TesterPresent calls, generation byte 115 to 120, empty outer-loop `0x1DA` counts, and `candidate_in_use`. No raw CAN transcript or per-sample timestamps are included. |
| `crown_f30_sideband_preflight_heartbeat.py` | 5,415 | `cc3440d3d2b09c80b55de812b4f3ff8f14fefba0bd743e9ed332db42230e6b79` | Local modification adding TesterPresent about every two seconds and before the closing read; also adds heartbeat reporting. The contributor reports that this resolved the closing SID23 session error. |

The supplied `.json` contains literal unescaped control characters in
`target.f181_ascii` (including four NUL bytes), so strict `json.loads` rejects it.
A control-character-tolerant parse (`json.loads(raw, strict=False)`) recovers the
reported fields and exact F181 hex. The raw artifact is not silently repaired;
its hashes above cover the supplied bytes. The contributor script uses
`json.dumps`, which would escape those characters, so the point at which the
serialization changed is not established by these files.

The contributor reports stopping after preflight: no resident installation or
subsequent control test was run. The original failing transcript and raw UDS
responses are not supplied; session expiration is supported by the original
source's idle interval and the contributor's successful keepalive experiment,
not by a retained exact ECU session-timeout measurement.

The result is **not** proof of a one-Hz counter, an entirely silent bus, or an
ICU-S consumer. The byte delta is five modulo 256. The count dictionary filters
only `0x1DA`, and this script does not count frames that the UDS client consumes
from the shared Panda receive queue during its own requests. See the
[preflight review](../../docs/variants/crown-8965F3012000.md#contributor-preflight-review-2026-09-14)
for the narrowed interpretation and read-only tooling fix.

## 2026-10-10/11 request-signer bringup logs

The retained ZIPs below are contributor-supplied startup/request-signer runs after
physically repinning the Toyota-B CAN0/CAN1 pairs onto the CAN0/CAN2 intercept
path. They are source evidence and are retained unchanged.

| File | Size | SHA-256 | Context |
|---|---:|---|---|
| `bringup-logs/tss3-bringup-runs-20261010.zip` | 18,373 | `a2aae02f7af3343a18ed50f3b40f356d9b6b9224e5ab68d118a8518dcc28fbf7` | Three runs while the contributor reported Sunnypilot `release-tizi`; startup PROGRAMMING catch and application F181 return succeeded, while the request-signer probe received no `0x7A9` signer response. |
| `bringup-logs/tss3-bringup-runs-20261011-c3x-debug.zip` | 20,154 | `a06fb54d72fb68082c5d7bef8f434ccd413015bbf241d9e5fec08ec4c759c1cd` | Three repeat runs after the contributor reported Panda `DEV-92eb5651-DEBUG`, hardware type 9 / C3X SPI. The same payload and request-signer timeout reproduced. |
| `bringup-logs/tss3-bringup-terminal-output.txt` | 3,852 | `bce1237b417c79adee74da573b181cdcc1f4c6582e9ab60af0d030ea8745b07e` | Contributor-collated terminal output and harness context for the first batch. |

Across all six retained install records the authenticated payload SHA-256 is
`c1cfd265611feb8e47438f81a3f4c508afea52a2be98c55ccf8d2346d7398a5d`.
The startup catcher reaches PROGRAMMING and the application subsequently answers
exact F181 `8965F3012000 / 8A3113008000`; the recurring failure is the absence of
a successful request-signer response. The later debug-Panda reproduction means
the earlier release-Panda `SAFETY_ALLOUTPUT -> SILENT` behavior is not sufficient
to explain the Crown failure.

`execution.telemetry_frames == 0` is **not** a census of CAN traffic during the
request-signer probe. That field belongs to the short authenticated RAM-exec
handoff window and counts only its selected `0x7A9` telemetry events. The old
bundle also carries no resident activation-state readback, so these runs do not
establish whether the request resident initialized, consumed `0x777`, reached
command 5, or attempted the `0x7A9` response.

The startup logs are not relay-side attribution evidence: startup uses ELM327
with the intercept relay bypassed. In the 2026-10-11 captures, selected ordinary
chassis frames `0x030`, `0x101`, and `0x51E` appear on logical bus 2 while the
EPS diagnostic `0x7A9` response is observed on both buses 0 and 2. This asymmetry
is a discriminator candidate, not proof of EPS-side ownership. The maintained
read-only next test is `tools/toyota eps-probe --open-relay --execute`, which
opens the relay with debug allOutput passthrough and polls F181 independently on
logical buses 0 and 2 before restoring the bypassed ELM327 state.

### C3X SPI transport review (2026-10-10)

The contributor's C3X reports Panda hardware type 9 (`TRES`) over SPI. A source
review of the exact `kai-openpilot/tss3-expand` Panda pin does not identify a
C3X-specific four-frame transport defect:

- Both `TRES` (comma 3X) and `CUATRO` (comma four) Panda board definitions set
  `has_spi = true` and share the same Panda SPI endpoint implementation.
- The four classic 8-byte request frames occupy only 56 bytes including Panda's
  6-byte CAN header per frame, far below the 4032-byte Python SPI transfer
  payload bound.
- `Panda.can_send_many()` intentionally emits the whole 56-byte batch as one SPI
  endpoint-3 write. Panda firmware's `comms_can_write()` explicitly loops over
  every packed CAN record in one endpoint write and calls `can_send()` for each;
  this is not a one-CAN-frame-per-SPI-transfer interface.
- Endpoint 3 NACKs when its CAN-TX flow-control gate is not ready. Python's
  `PandaSpiHandle.bulkWrite()` propagates/retries those NACKs; the retained Crown
  failure is instead `no request-signer response`, not a SPI NACK/timeout from
  the send operation.
- Panda HITL contains bulk `can_send_many()` stress/integrity coverage in
  addition to explicit SPI control/bulk transfer tests.

Therefore C3X SPI is currently a low-probability root cause. The missing host
witness is one layer later: the signer probe discards Panda TX-return/rejection
rows while waiting for `0x7A9`, so the retained run does not tell us whether all
four `0x777` records were accepted onto CAN (`bus+128`) or rejected by Panda
(`bus+192`). Capturing those TX receipts is the direct transport discriminator;
it does not require changing the resident.

### Historical host mode and exact-machine cross-check (2026-10-10)

Do not infer the failed 2026-10-10/11 request-signer safety mode from current
HEAD. The retained original `build/out/mruno/tss3-oracle-mruno.zip` contains the
pre-`2b72792f` host and its `RequestSignerSession` explicitly calls
`set_alloutput_mode()`. Commit `2b72792f` later changed that recurring signer
session to release-safe ELM327. Thus the original failed bundle and current
source have different Panda safety-mode behavior even though the authenticated
EPS payload is unchanged.

Current exact-machine verification also narrows the EPS-side implementation
risk. `tools/test rh850_firmware` passes the eight generated request-signer
scenarios for every registered exact image. For Crown `8965F3012000`, the
resolved response ABI is handle 51 -> RSCFD controller 1 / local resource 7.
Commit `937a7a7f` adds that exact resource to the P1M-E model; the Crown response
scenario now executes the exact firmware transmit primitive and records one
classic `0x7A9` transmit from absolute RSCFD buffer 23. Separate exact Crown
scenarios execute native post-filter `0x777` reception through IRQ187 into the
software ring with the expected `0x00000408` record and execute the recovered
freshness / ICU-S command-five submit and callback primitives.

This is strong functional evidence for the recovered stock primitives and their
addresses, but it is not silicon/vehicle proof and is not one monolithic
resident-from-reset simulation. A prior throwaway execution of the assembled
Crown helper already reached `request_count=1` and the real lower CAN writer;
its response check failed before resource 7 was modeled, which is consistent
with a simulator coverage gap rather than evidence of a helper defect.
