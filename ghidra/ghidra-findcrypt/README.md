# ghidra-findcrypt (vendored extension + signature database)

Vendored [antoniovazquezblanco/ghidra-findcrypt](https://github.com/antoniovazquezblanco/ghidra-findcrypt)
v3.1.9 (commit `bdccc22`), prebuilt for Ghidra 12.1.2.

## What's vendored

- `ghidra_12.1.2_PUBLIC_20260608_GhidraFindcrypt.zip` — the full prebuilt
  Ghidra extension. Installed by `tools/install_findcrypt_extension.sh` into
  the isolated user-home Extensions directory during rebuild.
- `data/database.json` — 130 cryptographic constant signatures (AES S-boxes,
  Rijndael T-tables, SHA/MD constants, DES S-boxes, CRC32 table, Blowfish,
  Camellia, ChaCha, Ed25519, Whirlpool, and more). Also used directly by
  `GhidraCliBridge.handleFindCrypto()` for CLI-based queries.

## How it works

Two complementary paths:

1. **Auto-analyzer (Ghidra extension)** — installed by
   `tools/install_findcrypt_extension.sh` during `tools/rebuild_project.sh`.
   Runs automatically during Ghidra auto-analysis, labeling crypto constants
   in the listing with plate comments. No manual invocation needed.

2. **CLI query (`ghidra find crypto`)** — `handleFindCrypto()` in
   `GhidraCliBridge.java` loads the same `database.json` at runtime and
   scans program memory for all occurrences of every signature, with
   automatic 32-bit byte-swap detection for endian-variant tables.

## Updating

```bash
# Download the latest release zip for Ghidra 12.1.2
gh release download <tag> --repo antoniovazquezblanco/ghidra-findcrypt \
  --pattern 'ghidra_12.1.2_PUBLIC_*' --dir /tmp/findcrypt-update

# Replace the zip and database
cp /tmp/findcrypt-update/ghidra_12.1.2_PUBLIC_*.zip \
   ghidra/ghidra-findcrypt/
gh api repos/antoniovazquezblanco/ghidra-findcrypt/contents/data/database.json \
  --jq '.content' | base64 -d > ghidra/ghidra-findcrypt/data/database.json

# Update PROVENANCE.json with the new commit SHA and zip filename
# Update tools/install_findcrypt_extension.sh with the new zip filename
```
