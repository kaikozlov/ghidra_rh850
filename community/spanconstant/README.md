# spanconstant Corolla field artifacts

**Contributor/specimen:** Span (`spanconstant` corpus), reported 2025 Toyota Corolla Hybrid
**Acquired:** 2026-08-21
**Observed application F181:** `8965F1208000` / `8A3111213000`
**ECU serial:** `8965012N50E12H030731`
**MCU boot-info:** RH850/P1M-E `R7F701383`

This directory persists the 2026-08-21 TSKM acquisition used by the Span Corolla
variant analysis. `spanconstant_tsk.zip` is retained byte-for-byte as the source
bundle (SHA-256 `a5744b4c4627d3e5c20d590bb882d25b9b40c0679cbc3e9660140c7f2ef5262b`). `raw-20260821/` is a deterministic exact-byte
extraction of the analysis-relevant memory and provenance members; see its
`MANIFEST.txt` for every member path, size, and SHA-256.

The normalized subset intentionally excludes duplicate macOS resource forks,
`.DS_Store`, and the large UDS sweep captures. Those bytes remain preserved in
the source ZIP, so normalization is lossless with respect to provenance while
keeping the directly analyzed corpus compact.

## Separate July-29 driving rlog

`span_67fd5b833889fedf_00000010--17084916da--3--rlog.zst` is a **separate**
Span-supplied comma Discord artifact, not a member of `spanconstant_tsk.zip`.
It was recorded 2026-07-29 and added to this corpus on 2026-08-24. SHA-256:
`f1ae7c40ad8e9ff8c462a3f5367d914873e93575d902ccb82f2c74984acd439f`.
Embedded `initData` records `spanconstant5/openpilot`, branch `tskdash`, commit
`7e78a9d89728c4bd106838d40b5891ce3931de43`, dongle `67fd5b833889fedf` and
mici hardware. Embedded `carParams` is `MOCK`, so the rlog has no usable F181
identity join; its dongle also differs from the later dump-preflight Panda
`23257862c6bf2f83`. Contributor attribution therefore does not make it an exact
`8965F1208000` firmware-to-route join.

The rlog is nevertheless high-value whole-vehicle evidence. Raw incoming CAN
shows real motion plus dynamic brake/gas/steering, and the opendbc extraction is
persisted as `data/generated/corolla_2025_span_discord_rlog_opendbc_evidence.json`.
All 599 Panda-state samples are `ELM327 param=1`, `harnessStatus=flipped`, controls
disallowed. The maintainer reports Span had **not physically repinned** the
Toyota-B CAN0/CAN1 pairs for this capture. `harnessStatus=flipped` is Panda harness
orientation, not that physical repin: param1 + logical bus1 directly observes the
normal unsplit harness CAN1 network, while the absent repin means the network is
not on the CAN0/CAN2 relay pair for normal comma interception/suppression.

## Memory corpus

The tracked subset contains:

- one 2 MiB CodeFlash range dump;
- three independent 64 KiB DataFlash reads;
- one 49,152-byte extended-CodeFlash read;
- one 64 KiB global-RAM read;
- one 128 KiB PE1 LocalRAM read and one later 128 KiB self-view LocalRAM read;
- the corrected direct-route preflight, route record, and SecurityAccess log.

The CodeFlash range SHA-256 is
`b8fa3d951f59fb75c190ce1b2c73164adb952f871650cfcd3b7656f08a9c448d`. Its upper
1 MiB is all `0xFF`; the normalized first 1 MiB SHA-256 is
`fdb35b76891cf84a8b89e0a05c9c7c5cfcd27994cf85ccc01ff32828f53091f6`.

The firmware boot-info identifies `R7F701383`. Raw CodeFlash strings contain
`8965H1213000` at `0x17D80`, `8A3111213000` at `0x17DC0`, and `8965F1208000` at
`0x20860`. The live preflight independently observed F181 as
`8965F1208000 / 8A3111213000`. Target-native closure now resolves the producer:
byte-identical `FUN_0004a328` reads the two F181 records from `0x20860` and
`0x17DC0`; `0x17D80` belongs to a separate one-record identity path.

## Comparative static closure

Against albino's tracked 2023 Corolla, the normalized first-MiB CodeFlash differs
in exactly 2,190 bytes, all below `0x17E00`; the high CRC/application image is
byte-identical. A fresh clean Span Ghidra import independently produced the same
5,425-function structural fingerprint corpus as H, and a direct Span→Sienna run
reproduced H's full exact-body, structural, named-function, and normal-Rx results.
The resolved Span SecOC queue is `00F/D7/B6`, not Sienna's `2E4/131` steering
profiles.

The 2,190-byte low delta is now exhausted rather than left as a generic
calibration caveat. Exactly 863 changed bytes belong to a nine-record `0xA000`
unit-calibration/identity family, whose active consumers include three
mode-selected motor-rotation-angle correction LUTs and selected angle-offset
coefficients; 1,311 changed bytes lie in the structured `0x10000..0x17DEF`
shadow-copy source; the remaining 16 bytes are the opaque post-CRC field
`0x17DF0..0x17DFF`. The active calibration differences are specimen-specific
evidence, **not** proof of a 2023→2025 tuning revision, and the semantic CPU
consumer of the `0x10000+` shadow bank remains bounded.

The non-CodeFlash corpus is also compared directly. Span's 48-KiB extended
CodeFlash is byte-identical to all three albino reads. All three physical
first-32-KiB DataFlash prefixes retain the same NvM geometry and zero valid
object-15 copies; Span adds committed checkpoint slot 104 and carries different
mutable object-2 state. Runtime RAM differences are separately treated as
snapshot state.

## XCP / PROGRAMMING retention result

The persisted image independently reproduces the tracked `8965H1202000`
XCP/PROGRAMMING lifetime architecture. Its generic XCP opcode/callback map,
`0x7F7/0x7F8` route descriptors, high-LocalRAM write geometry, application
PROGRAMMING handoff, `0x9F00` boot-entry stub, retained-state copy, and
reset-only initializer are byte-identical at the relevant locations. Thus
unauthenticated XCP code placement in `FEBF7C00..FEBFFBFF` survives the live
application-to-boot `10 02` handoff on this firmware too. This is a retained
code-placement primitive, **not** a proven no-auth PC pivot/RCE.

The corrected direct `(bus 1, ELM327 param 1)` preflight opened PROGRAMMING,
received a SecurityAccess seed, accepted the key, and the subsequent acquisition
completed CodeFlash/DataFlash/RAM dumps. This supersedes the older route record
where PROGRAMMING had accidentally been attempted through `param=0`.

Canonical interpretation lives in
[`docs/variants/corolla-8965F1208000.md`](../../docs/variants/corolla-8965F1208000.md).
