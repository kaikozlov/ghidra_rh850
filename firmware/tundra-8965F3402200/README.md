# Toyota Tundra EPS secondary CPU `8965F3402200`

`Application.bin` is the canonical `CPU12` application region decrypted from
Toyota `T-0035-22.cuw` (SHA-256
`9882b1b6dd6acda2d142a2825eda396b0a425e41c13f822b9a18e022d4c43e81`).
Its plaintext is CMAC-validated using the EPS payload-build derivation in
`tools/techstream/analyze_t0035_faci_backend.py`.

- File length: `0xE7DF0` (949,744) bytes; last 16-byte CMAC trailer removed.
- SHA-256: `54c84ac25db1dfdb73e982c3ec9b379febe56229310ad07cd171eec333ac87f8`.
- CodeFlash load: `0x18000..0xFFDEF`.
- Software identity at `0x20860`: `8965F3402200`.

The bootloader region `0x00000..0x17FFF` is absent from this CUW. The separate
`EraseRoutine12` is a `0x1000`-byte executable RAM flash driver at `0xFEBF0000`,
not a CodeFlash bootloader. For both CPUs' programming offsets, application
UDS/DID evidence, and the precise unresolved bootloader dispatch boundary, see
[the Tundra dual-CPU report](../tundra-8965F3401200/README.md).

## SecOC Gate 2

The exact RAV4 Prime/Camry Gate-2 context `E0 D1 9A 0D 1A 38 BF FF` occurs once
at `0x809E4`, inside the 134-byte receive-verification worker at `0x80998`.
Result zero takes the normal status/delivery arm and nonzero takes the
retry/failure arm, matching CPU11 and the named Camry Gate-2 structure. Its
`0x80000..0x87FFF` stock erase-block SHA-256 is
`8a196b3ac98ea9eb581aa4b57f60c9ea3a0395f7817910365a0b25bf7a925c3b`.
