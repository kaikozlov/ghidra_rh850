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
protected traffic even though synchronization collection succeeded.

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

The structural analyzer also finds that the Sienna-derived physical NvM layout
partially transfers: objects 0, 2, and 5 have three committed
raw/XOR55/XORAA copies that decode to valid consensus payloads at the same
physical locations. Objects 1, 3, 4, 6, 12, 13, 14, and 15 have no valid copy
under the proved storage-index + `0xAAAAAAAA` validity rule. Object 15 therefore
does not reproduce the `8965B4514000` CPU-visible key-storage observation in
this dump.

This is strong evidence against a **raw CPU-visible SecOC key in this DataFlash
snapshot**. It does not prove that no key exists elsewhere, inside ICU-S/HSM,
or in a transformed/derived representation not covered by a raw 16-byte
window or the known triplicate decode model.
