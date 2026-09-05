# Verification fixtures

`payloads/` contains the three unique 4 KiB encrypted payloads used to verify the
bootloader's payload format, AES-CBC decryption, CRC residue, CMAC, and callback
slot. Keeping these small immutable inputs in-tree makes `make verify`
independent of neighboring checkouts.

| Fixture | Public upstream copies | SHA-256 |
|---|---|---|
| `payloads/ram_dump_payload.bin` | `I-CAN-hack/secoc:payload.bin`; `calvinpark/openpilot:tsk/lib/payload.bin` | `d972d4bf432685217591768600a9abd7820d35b04a72270edc87074365356be2` |
| `payloads/dataflash_dump_payload.bin` | `calvinpark/openpilot:tsk/lib/payload_dataflash_ff200000_ff208000.bin`; `Bk2ol/tsk_extraction_by_can_log:payload_dataflash_ff200000_ff208000.bin` | `d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34` |
| `payloads/candidate_f05_dataflash_payload.bin` | Vance `20260531_othersienna_secoc_bundle{,_v2,_v3}.zip:payload_candidate_f05_dataflash_ff200000_ff208000.bin` | `296d87d2e89b9c7e800122e4c7f6d3b9c876362e52586530cdd53c86ba1116f5` |

Repository URLs, exact commits, upstream paths, and source-file hashes are in
[`../../external-references.lock.json`](../../external-references.lock.json).
`make verify-external` confirms that pinned external checkouts still match these
fixtures and re-runs the source-level corroboration checks.

`techstream/` contains small **synthetic** cross-version `ptshim32` log samples.
They are not vehicle captures and contain no real ECU data; they exercise the
recovered v04.04 `PTWriteMsgs` and v05.00 `PTQueueMsgs` grammars, including
ChannelID, Tx/Rx headers, flags, timestamps, raw address/data bytes, status,
extra-data boundaries, and the v05 per-message handle. Pinned external shim
binaries provide the independent format/body evidence when the ignored
Techstream tree is present.

## camry_20260904/

Compact JSONL excerpts from the 2026-09-04 Camry driving-corpus rlogs (routes
`0000003b--62262eb7a1`, `0000003c--97b9e7a69a`, `0000003d--0e812cecba`), used
by `tests/verify_camry_20260904_stock_steering.py`. Each file carries a
provenance header pinning the original `rlog-<segment>.zst` compressed
SHA-256, byte size, first-live-event timestamp, and extraction window; only
the analysis address set (`0x025/0x030/0x081/0x08A/0x0B6`), matching
`carState`/`controlsState` events, and sendcan frames are retained — no
GPS, video, or unrelated loggerd services. The excerpts cover the five
native-ID4 episode windows and the route-3c segment-43 divergent-request
witness. Full-corpus regeneration requires the external logs at
`/Users/kai/dev/inspect/logs/camry-2026/2026-09-04/`; these fixtures keep the
reducer's verification portable.
