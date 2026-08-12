# albinoelephant Corolla field artifacts

**Contributor:** albinoelephant (`@albinoelephant`, comma Discord)
**Received:** 2026-08-12
**Vehicle attribution:** reported by the contributor as a 2023 US Toyota Corolla
**Exact EPS F181 / calibration:** unknown

This directory preserves the raw field artifacts supplied from the contributor's
`optskug/openpilot` TSK Manager (`tskm` branch) run, plus one repository-derived
CAN-only oracle from the contributor's already-public comma route.

The model-year/vehicle attribution is external field evidence. The public route
itself was run with a forced `TOYOTA_COROLLA_TSS2` fingerprint and contains no
`carFw`, so neither the route nor these DataFlash bytes independently establish
an exact EPS software ID. Keep this specimen separate from the exact
`8965F1208000` Corolla investigation until F181 is obtained.

## Raw supplied artifacts

| File | Origin | Size | SHA-256 |
|---|---|---:|---|
| `dump_ff200000_ff208000.bin` | TSKM `/cache/tsk/dataflash/` after the successful DataFlash dump | 32,768 | `8ac2a6beecb4ca2e6caf695eebffe440478171b4e093a1b2a36ab4e4ff313299` |
| `can_oracle.ndjson` | TSKM `/cache/tsk/can-messages/can_oracle.ndjson` from the same investigation | 97,768 | `8863398a98875a853e722a6ba83fc10563d5764cea33719c8af34225efa189a3` |

The TSKM oracle contains 1,232 rows, all CAN `0x00F` synchronization frames:
616 on Panda bus 0 and the same 616 on bus 2. It contains no protected-message
rows, which explains why the TSKM post-dump matcher could report insufficient
protected traffic even though synchronization collection succeeded. All of
these frames carry `TRIP_CNT=0xD0D`. They come from the same TSKM investigation
as the supplied dump, but **not a provably identical EPS runtime epoch**: CAN
collection and DataFlash dumping are separate mutually-exclusive jobs, and the
dump path subsequently drives the EPS through programming-session/SecurityAccess
and RAM-exec. The oracle therefore provides a close local synchronization-key
comparison, not a same-session proof.

## Derived public-route oracle

`public_route_secoc_oracle.ndjson` is **not** a second attachment from the
contributor. It is a repository-derived, CAN-only extraction from segment 0 of
the public route the contributor supplied in the same Discord investigation:

```text
a74eba85c97eaf67|00000004--555953f500
```

The source `rlog.zst` is already provenance-pinned in
`external-references.lock.json` with SHA-256
`d246a55988889253c8d155f04b132b1bb443fdd74f1e6bad68eef8879a5c477b`.
The derived oracle contains only genuine source-bus-1 classic SecOC-family
frames required for offline testing:

- `0x00F`: 588 synchronization frames;
- `0x116`: 2,499 frames;
- `0x24D`: 59 frames.

Derived-file SHA-256:
`a9bf3f279001b8b77e96acfc186944a962c59cc7bedf739d902d971ff4b03f15`.

No VIN, `carParams`, camera data, or other route metadata is retained in this
compact oracle.

## Current offline result

`data/generated/corolla_2023_albino_dataflash_analysis.json` is generated with:

```bash
uv run python tools/analyze_toyota_dataflash.py \
  community/albinoelephant/dump_ff200000_ff208000.bin \
  --capture community/albinoelephant/public_route_secoc_oracle.ndjson \
  --domain-scan --min-entropy 0 \
  --output data/generated/corolla_2023_albino_dataflash_analysis.json
```

The scan tests every unique sliding 16-byte raw DataFlash window, with no
entropy cutoff, independently against synchronization and the observed
`0x116`/`0x24D` protected domains. No candidate passes even the first
cryptographic probe for any domain.

The full `4512000` reference storage geometry transfers much more strongly than
the initial triplicate-only pass suggested. The Corolla dump has **60 committed
records** at those physical extents: 9 triplicate records and **51 checkpoint
records**. Every one of the 51 checkpoint records also has a valid
`generation/~generation` pair at the inverse location predicted by the
reference geometry. Forty-nine map to reference-enabled checkpoint owners.
The remaining two are storage indexes **117/118** (`0xFF204280` and
`0xFF204200`), which map to reference-disabled owner 28 but form a coherent
two-slot ring with adjacent generations `0x25/0x24`. Both contain nonzero data
well beyond the reference owner-28 8-byte payload, proving that the physical
geometry transfers while the descriptor/provisioning semantics differ.

In the triplicate bank, objects 0, 2, and 5 have three committed
raw/XOR55/XORAA copies that decode to valid consensus payloads at the same
physical locations. Objects 1, 3, 4, 6, 12, 13, 14, and 15 have no valid copy.
The former opaque header word is now independently validated as the
reader-enforced short-record additive checksum; all nine committed Corolla
triplicate records satisfy it. Object 15 therefore does not reproduce the
`8965B4514000` CPU-visible key-storage observation in this dump.

The local TSKM `0x00F` oracle was also scanned independently with no entropy
cutoff: all 23,277 unique raw 16-byte dump windows were tested and **none
matches the synchronization-key domain**. This does not rely on the older
public route, but it still cannot prove runtime-key continuity across the
separate capture and programming/dump jobs. It therefore excludes a static raw
DataFlash value equal to the locally observed synchronization key, not a
session-derived key.

The public-route oracle has `TRIP_CNT=0xCE9`, so it is a **different ignition
freshness epoch** from the local TSKM oracle (`0xD0D`). Its exhaustive zero-match result for
`0x116`/`0x24D` remains strong historical same-vehicle evidence, but interpreting
it as a protected-key negative for this exact dump assumes the protected key did
not change between sessions. Six simple whole-window transforms (XOR55, XORAA,
bitwise NOT, full-byte reversal, per-32-bit byte swap, per-16-bit byte swap)
were additionally tested against the public-route domains with zero first-probe
survivors across all 23,277 unique windows per transform.

This is strong evidence against a **static raw CPU-visible synchronization key
in this DataFlash snapshot**, plus more distant cross-session evidence against a
raw protected key.
It does not prove that no key exists elsewhere, inside ICU-S/HSM, or through a
more complex/unmodeled derivation.
