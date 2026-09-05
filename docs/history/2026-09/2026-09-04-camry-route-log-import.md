# 2026-09-04 Camry long-drive route-log import

Raw `rlog.zst` files from the three substantial Camry drives recorded on
2026-09-04 were copied from the comma device for offline analysis. As with the
2026-09-01 route-37 corpus, the multi-gigabyte raw logs live outside the Git
worktree under `/Users/kai/dev/inspect/logs/`; this note records their stable
local locations.

| Route | Segments | Approx. local interval (CDT) | Comma source | Local copy |
| --- | ---: | --- | --- | --- |
| `0000003b--62262eb7a1` | 110 (`0..109`) | 09:19–11:08 | `/data/media/0/realdata/0000003b--62262eb7a1--{0..109}/rlog.zst` | `/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/0000003b--62262eb7a1/rlog-{0..109}.zst` |
| `0000003c--97b9e7a69a` | 81 (`0..80`) | 11:23–12:43 | `/data/media/0/realdata/0000003c--97b9e7a69a--{0..80}/rlog.zst` | `/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/0000003c--97b9e7a69a/rlog-{0..80}.zst` |
| `0000003d--0e812cecba` | 62 (`0..61`) | 15:23–16:24 | `/data/media/0/realdata/0000003d--0e812cecba--{0..61}/rlog.zst` | `/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/0000003d--0e812cecba/rlog-{0..61}.zst` |

A two-segment startup route, `0000003a--4a3e564277`, was present at about
09:15 CDT but was intentionally excluded because this import targets the day's
longer drives.

The import was verified by matching segment counts and compressed-byte totals
against the comma source and by testing every local Zstandard stream with
`zstd -t`.
