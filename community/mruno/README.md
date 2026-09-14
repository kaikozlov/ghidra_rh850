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


## Preflight follow-up received 2026-09-14

Two further contributor files are retained unchanged:

| File | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `crown-preflight.json` | 908 | `eedb0bd89b8f1fd62a45d8e017c4e777ea2843ddb49744c07b86fe20afd4e0e7` | Contributor preflight summary after adding diagnostic keepalive. |
| `crown_f30_sideband_preflight_heartbeat.py` | 5,415 | `cc3440d3d2b09c80b55de812b4f3ff8f14fefba0bd743e9ed332db42230e6b79` | Contributor troubleshooting copy, archived as supplied rather than installed as the canonical probe. |

The supplied summary records F181 `8965F3012000 / 8A3113008000`, a requested
5-second observation, three completed TesterPresent calls, no `0x1DA` counted
by the outer observation loop, and the sampled byte changing from 115 to 120.
Its recorded verdict is `candidate_in_use` / `safe_to_experiment=false`.
The contributor reports using checkout `68b9d8a8` and stopping before resident
installation. The report also describes a closing-read session error without
keepalive, resolved by the attached change. There is no failing-run transcript,
raw CAN capture, per-read timestamp series, Panda health/build identity, or
resident-execution result in this follow-up. The summary has no capture date.

The transferred JSON contains five literal control bytes inside `f181_ascii`
(one `0x02` and four NULs); strict JSON parsing rejects line 36. Inspection used
`json.loads(..., strict=False)` without rewriting the source file. The provided
script uses normal `json.dumps`, which would escape these characters; the
transfer/representation discrepancy is not attributed to an ECU or probe bug.

The diagnostic timing and measurement limitations are reviewed in
[the Crown target report](../../docs/variants/crown-8965F3012000.md#contributor-preflight-review-2026-09-14).
