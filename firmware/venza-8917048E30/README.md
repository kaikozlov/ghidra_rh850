# 2021–2022 Venza airbag sensor `8917048E30`

Canonical reference firmware inputs for the yc-contributed Venza airbag
sensor/diagnostic unit (RH850, P1x-C family; exact MCU part not established).

- `cflash.bin`: 3,145,728 bytes, SHA-256
  `2dfaf7ce21cb04af1126192f574103f63802352f8717fa0f03986d5a11d067f9`
- `boot.bin`: 32,768 bytes, SHA-256
  `943934abc9a5c676eff46f51f008baa39e4f533e66650ffcce54d7bfb6e6e6e2`

Both files are byte-identical copies of the retained contributor artifacts
under `community/yc/venza/` (glitch acquisition; method is
contributor-provided). `cflash.bin` has meaningful code through ~`0x17FFFF`
(`0x180000..0x2AFFFF` is `0xFF` fill, `0x2B0000..0x2FFFFF` is zero fill);
`boot.bin` is the `AUBIST_RPRG_201902` extended-user image the CodeFlash maps
at `0x01000000..0x01007FFF`. No DataFlash dump exists for this specimen.

Analysis-target metadata is pinned in `data/analysis_targets.json`; the
registration rationale and command-surface census live in
`docs/security/icu-hsm-command-surface.md` and
`docs/variants/yc-venza-airbag-reprogramming-2026-09-14.md`.
