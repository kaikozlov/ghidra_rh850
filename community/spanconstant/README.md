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
`8965F1208000 / 8A3111213000`. The repository intentionally does **not** infer
which raw block supplies F181 until that producer is recovered target-natively.

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
