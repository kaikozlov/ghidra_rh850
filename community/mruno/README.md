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
route was corrected. The CodeFlash collection repeatedly hit
`PandaSpiNackResponse` near the end of the 2-MiB transfer, so the contributor
changed the collector to preserve the partial buffer instead of discarding it.
That collector patch and its coverage metadata were not supplied with these
three artifacts.

The contributor also reports an offline SecOC-key scan over the 32-KiB DataFlash
using more than 12,000 signed Crown frames (`0x090`, `0x0D7`, `0x116`, `0x24D`)
with zero key matches. The CAN oracle is **not** part of this import, so that
zero-match result remains external-source context rather than a locally
reproducible repository result.
