# Verification fixtures

`payloads/` contains the two unique 4 KiB encrypted payloads used to verify the
bootloader's payload format, AES-CBC decryption, CRC residue, CMAC, and callback
slot. Keeping these small immutable inputs in-tree makes `make verify`
independent of neighboring checkouts.

| Fixture | Public upstream copies | SHA-256 |
|---|---|---|
| `payloads/ram_dump_payload.bin` | `I-CAN-hack/secoc:payload.bin`; `calvinpark/openpilot:tsk/lib/payload.bin` | `d972d4bf432685217591768600a9abd7820d35b04a72270edc87074365356be2` |
| `payloads/dataflash_dump_payload.bin` | `calvinpark/openpilot:tsk/lib/payload_dataflash_ff200000_ff208000.bin`; `Bk2ol/tsk_extraction_by_can_log:payload_dataflash_ff200000_ff208000.bin` | `d48988366b5e6d2ddd7438caca5e6f6f02daba9b650263c323a2ffd770a06e34` |

Repository URLs, exact commits, upstream paths, and source-file hashes are in
[`../../external-references.lock.json`](../../external-references.lock.json).
`make verify-external` confirms that pinned external checkouts still match these
fixtures and re-runs the source-level corroboration checks.
