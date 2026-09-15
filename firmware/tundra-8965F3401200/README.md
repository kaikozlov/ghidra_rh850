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
