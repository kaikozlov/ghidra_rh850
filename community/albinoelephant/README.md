# albinoelephant Corolla field artifacts

**Contributor:** albinoelephant (`@albinoelephant`, comma Discord)
**Received:** initial DataFlash/oracle 2026-08-12; complete memory corpus 2026-08-18; eps-telescope probe 2026-08-26
**Vehicle attribution:** reported by the contributor as a 2023 US Toyota Corolla
**Direct application F181:** `8965F1208000` / `8A3111202000` (retained eps-telescope transcript)
**Auxiliary one-record identity:** `8965H1202000` (DID `0x2032`, CodeFlash `0x17D80`)
**MCU / serial:** RH850/P1M-E `R7F701383`; `8965012N50A05G310920`

This directory preserves the raw field artifacts supplied from the contributor's
TSK Manager investigation, the contributor-supplied `eps-telescope` output under
`telescope/`, plus one repository-derived CAN-only oracle from the contributor's
already-public comma route. The complete 2026-08-18 bundle is preserved byte-for-byte
under `raw-20260818/`, including its contributor-supplied `MANIFEST.txt`.

The model-year/vehicle attribution remains external field evidence. The public
route itself was run with a forced `TOYOTA_COROLLA_TSS2` fingerprint and contains
no `carFw`, so the route alone still does not identify its physical EPS. The later
same-car telescope probe closes the diagnostic identity instead: application F181
returns count `2` with `8965F1208000` from CodeFlash `0x20860` and
`8A3111202000` from `0x17DC0`. `8965H1202000` at `0x17D80` belongs to the
separate one-record DID `0x2032` path. The historic `8965H1202000` filenames are
kept as stable corpus labels, not as a claim about the wire-visible F181 primary.
This remains a distinct physical specimen from Span's Corolla despite sharing the
same F181 primary software record.


## 2026-08-26 eps-telescope live probe

`community/albinoelephant/telescope/probe.json` and `probe.md` were sent by the
contributor from this car and are direct outputs of the pinned
`lochuan/eps-telescope` workflow. The probe is unusually valuable because it joins
the previously retained static corpus to a later live bootloader session:

- application F181 is directly captured as `8965F1208000 / 8A3111202000`; boot
  F181 is the expected `02 || 32*0x21` placeholder;
- live `PRDNAME1..4` decodes to `R7F701383`;
- all 384 streamed CodeFlash bytes at `0x8E6A0`, `0xFFDE0`, and `0x17D80`
  match the tracked normalized image exactly;
- boot SecurityAccess succeeds, RoutineControl `0x10F0` accepts the authenticated
  `FEBF0000` envelope, and the shellcode stream validates end-to-end. This is an
  independent clean replay of the boot-RAM execution already required by the
  contributor's earlier range-dump acquisition, not its first demonstration;
- the live flash-wide scan finds the SecOC Gate-2 egg at `0x88C62`. Telescope did
  not stream the relocated candidate's 64-byte context (`NO_DATA`), but the tracked
  image independently shows that `0x88C43..0x88C82` has the exact pinned Sienna
  Gate-2 fingerprint SHA-256 `50d793a2...7350`, including `e0d1` at `0x88C62`;
- live `0xFFDEC=AD59D70C` joins the tracked stock-valid CRC image, whose
  `[0x18000,0xFFDF0)` CRC32 residue is `0xFFFFFFFF`;
- the streamed `FEBF2CF8..FEBF2DF7` window exposes zero DID `0202`, zero DID
  `0201`, the expected derived payload key `80d221a0...e6c78d1`, the payload-CMAC
  work/tag buffer, and a fresh boot SecurityAccess seed snapshot. Optional replay
  against pinned eps-telescope reconstructs the exact tag as
  `a5ebde539a7147cd61f21b4a5b222e1f` and CRC fixup `0x6DAAE993`, matching live
  `FEBF2D28` and `DCRA1CIN`. These are boot/payload crypto values, **not** the
  operational SecOC slot-4 key.

The deterministic correlation is generated in
`data/generated/corolla_2023_albino_telescope_analysis.json` and verified by
`tests/verify_albinoelephant_telescope_probe.py`.


## Complete 2026-08-18 memory corpus

`raw-20260818/` is the immutable extraction of the contributor bundle. It contains
the earlier 32 KiB DataFlash/oracle pair plus a later session with the full
CodeFlash range, five 64 KiB DataFlash reads, three extended-CodeFlash reads,
three global-RAM reads, and three local-RAM PE1 reads. See
`raw-20260818/MANIFEST.txt` for the exact acquisition notes and every supplied
file hash.

The CodeFlash range artifact is:

```text
raw-20260818/albinoelephant-corolla-2023.20260814-0023/
  dump_codeflash_00000000_00200000_20260814-025814.bin
source size:    0x200000
source SHA-256: 97f9d42d936b97a99e7ab3d3ef20c6fb4c1fc3cc2ba199f6b158675a1709aee6
```

Its upper 1 MiB is entirely `0xFF`; the actual first-1-MiB CodeFlash has SHA-256
`0b47bdc1217835c839e3543e52eab40eb793650a9c159e46f6a9b365ea41a67f`.
Repository tooling preserves both identities: a 2 MiB range dump is accepted
only when the upper half is all `0xFF`, and normalization occurs in a disposable
workspace without modifying this source artifact.

Static analysis of that image establishes:

- the payload-build, boot-SA, and application-SA roots at `0xBFD8`, `0xBFE8`,
  and `0x20840` are byte-identical to `8965B4512000`;
- the calibration-independent Gate-2 resolver uniquely finds `0x88C62` (`e0d1 -> e001`);
- the stock region-1 CRC is valid and the Gate patch re-signs with fixup
  `0xDD5F1477`;
- the configured Gate-2 queue has only three records: `0x00F`, `0x0D7`, and
  `0x0B6`; there is no queue-1 `0x2E4` or `0x131`, so the Sienna steering bridge
  is not applicable to this image;
- the homolog of Lochuan's `0x31 -> 0x10` checkpoint byte is `0x6081E`, and its
  containing function has the same checkpoint-failure semantics rather than
  SecOC acceptance semantics.
- application and boot/programming diagnostics remain on RSCFD channel 1 in
  this exact image; boot retains `0x7A1/0x777 -> 0x7A9`, so the post-pin-swap
  success is not explained by an EPS application-to-boot CAN-controller change;
- the foreign PROGRAMMING session reproduces the asynchronous reset handoff and
  `0x0180` speed / `0x0A00` supply policy thresholds. A `10 02` timeout by itself
  can therefore represent reset overtaking the final positive response rather
  than ECU rejection.

Canonical interpretation and exact resolver anchors are documented in
[`docs/variants/corolla-2023-us-public-route.md`](../../docs/variants/corolla-2023-us-public-route.md).

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
