# Toyota Tundra EPS `8965F3401200`

Canonical plaintext application region recovered from Toyota `T-0035-22.cuw`.

- `Application.bin`: 949,744 bytes (`0xE7DF0`), SHA-256
  `c401af613cb44a70dad5ec3dba7218800bd32d94c4a47e12301b4e3a5ce33d94`
- CodeFlash load address: `0x00018000`
- Covered CodeFlash range: `0x00018000..0x000FFDEF`
- Embedded application identity: `8965F3401200` at absolute `0x00020860`

The source CUW is `T-0035-22.cuw`, SHA-256
`9882b1b6dd6acda2d142a2825eda396b0a425e41c13f822b9a18e022d4c43e81`.
The encrypted CPU-image region decrypts to `0xE7E00` bytes and CMAC-validates.
`Application.bin` omits the final 16-byte CUW authentication trailer, so it is
the firmware payload rather than the package-authentication record.

This is **not a complete 1 MiB CodeFlash dump**. The CUW CPU image begins at
`0x00018000`; bytes `0x00000000..0x00017FFF` are not reconstructed or filled in.
The manufacturer erase/program routine is separately analyzed from the same CUW
by `tools/techstream/analyze_t0035_faci_backend.py`.

## Dual-CPU programming selection

The source `T-0035-22.cuw` declares `ContactType=P5-Unified`, one node
(`Node01/DiagID=07A1`, gateway preparation `01_GatewayDiagID=07505F`), and two
CPU images. Both images start at the local address `00018000` and have length
`000E7E00`. The independent `T-0036-22.cuw` repeats the same addressing scheme
for the `8965F3403200/4200` pair.

| CUW section | NewCID | Five-byte `OffsetAddress` | Effective `CPUImage` start |
|---|---|---|---|
| `CPU11` | `8965F3401200` | `01 00 00 00 00` | `01 00 01 80 00` |
| `CPU12` | `8965F3402200` | `00 00 00 00 00` | `00 00 01 80 00` |

**Current GTS+ host evidence.** In the recovered CUWPlus
`TCUWCanUnifiedFlashWriter.dll` (SHA-256
`97cdba7f5cc57a555df27893479141632e48a41276e73c54f9c36de3e6e16647`):

- `0x100013A0` processes the selected CPU image/index, using `GetNodeIdx` to
  associate both images with the same diagnostic node.
- `0x10002AD0` transmits `2E 02 03 || OffsetAddress[5]`, then
  `2E 02 01 || SeedKey[16]`, then `2E 02 02 || Nonce[16]`.
- `0x10001BE0` builds RequestDownload with address/size format `46`, a separate
  address-space byte, and the **five-byte big-endian sum** of `OffsetAddress`
  and each area start. `0x10002060` applies the same sum to RoutineControl
  addresses. `0x10002510` supplies the address-space byte (1 for area tags
  0/2, 0 for tag 3) and data format (`SecurityProperty2` bit 3).

For the CPUImage area of `T-0035-22.cuw`, the resulting *UDS application payloads*
(excluding ISO-TP framing) are:

```text
CPU11  2E 02 03 01 00 00 00 00
       34 01 46 01 01 00 01 80 00 00 0E 7E 00
CPU12  2E 02 03 00 00 00 00 00
       34 01 46 01 00 00 01 80 00 00 0E 7E 00
```

These use the **same CAN diagnostic endpoint** (`0x7A1` request, conventional
`0x7A9` response), not separate external CAN IDs for each CPU. The gateway
preparation ID `07505F` is a distinct operation, not the second CPU endpoint.

**Important distinction:** the retained community
`community/blurbdust_secoc_flash_patcher/flash_patcher.py::run_exploit` also
uses `01 00 00 00 00` vs `00 00 00 00 00` for DID `0203`, but its RAM-exec
RequestDownload switches the separate *address-space byte* (`mem_id=01/00`)
and sends a zero-prefixed five-byte RAM address. That is **not** the factory
Unified writer's per-CPU RequestDownload construction above. The Tundra
bootloader's implementation of these address fields is not contained in the
retained CPU11 application-only extract; its precise hardware CPU-dispatch path
remains to be recovered from bootloader bytes or a live reflash trace.
