# Audited runtime executables

These binaries are the exact executable bytes pinned by the adjacent
`audited*_build.json` manifests. Target-specific experiments keep their own
`audited/` directory beside their builders under
`tools/targets/{camry,corolla,crown}/research/ram_runtime/`.

The binaries and manifests are frozen checkpoint evidence. The manifests retain
their original source paths, source hashes, and toolchain identities, including
paths from the former `exploit/ephemeral_runtime/` layout. Those paths describe
the audited build, not the current checkout. Moving a builder does not create a
new audit or transfer its historical hardware result to a rebuilt payload.

Builders write disposable output under `build/out/`. Verification binds the
reviewed binary bytes and exercises their contracts; promotion of new bytes
requires review of the matching new build manifest.

The Camry B6 audit directory also retains
`generic_shellcode_template.bin` (`sha256:74d22b4116ce212a43090d76ba00ed4d97e7a3f082e45c5bcb4921e2ecc5fb22`).
The persistent-patch builder consumes those reviewed 4,048 bytes directly;
rebuilding that historical template with the current compiler would substitute
different bytes under the old review record.

For the split F33 signer family, reviewed promotion remains explicit:
`tools/targets/camry/research/ram_runtime/b6/build_camry_f33_b6_inline_signer.py --mode MODE --promote-audited`.
The flag writes only that mode's tracked artifact subset and matching manifest.
