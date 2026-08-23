# ghidra-findcrypt (vendored extension + signature database)

Vendored [antoniovazquezblanco/GhidraFindcrypt](https://github.com/antoniovazquezblanco/GhidraFindcrypt)
v3.1.9 (commit `fcaa49e545b131e2cc631168c6c168c1aec862a6`). Upstream v3.1.9
predates Ghidra 12.1.3, so the extension zip is rebuilt locally from that
exact tagged source against Ghidra 12.1.3.

## What's vendored

- `ghidra_12.1.3_PUBLIC_20260822_GhidraFindcrypt.zip` — local rebuild of the
  pinned upstream v3.1.9 source. Its `GhidraFindcrypt.jar` is byte-identical to
  the official upstream 12.1.2 v3.1.9 build; only Ghidra extension-version
  packaging differs. Installed by `tools/install_findcrypt_extension.sh` into
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

## Rebuilding for the pinned Ghidra release

```bash
rm -rf /tmp/GhidraFindcrypt
git clone https://github.com/antoniovazquezblanco/GhidraFindcrypt.git /tmp/GhidraFindcrypt
git -C /tmp/GhidraFindcrypt checkout v3.1.9
GHIDRA_INSTALL_DIR=/opt/homebrew/opt/ghidra/libexec \
  /tmp/GhidraFindcrypt/gradlew -p /tmp/GhidraFindcrypt buildExtension

cp /tmp/GhidraFindcrypt/dist/ghidra_12.1.3_PUBLIC_*_GhidraFindcrypt.zip \
  ghidra/ghidra-findcrypt/
```

After rebuilding, update `PROVENANCE.json` with the source commit, artifact
hash, JAR hash, and database hash. `tests/verify_findcrypt_database.py` pins all
of those identities and verifies the packaged extension declares Ghidra 12.1.3.
