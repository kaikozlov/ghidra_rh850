# ghidra-findcrypt (vendored extension + signature database)

Vendored [antoniovazquezblanco/GhidraFindcrypt](https://github.com/antoniovazquezblanco/GhidraFindcrypt)
v3.1.9 (commit `fcaa49e545b131e2cc631168c6c168c1aec862a6`). The integration
requires Ghidra **12.2**; rebuild the pinned upstream source against the installed
Ghidra 12.2 SDK after applying the small tracked compatibility patch below.

## What's vendored

- One `ghidra_12.2_PUBLIC_<build-date>_GhidraFindcrypt.zip` — the local rebuild
  recorded in `PROVENANCE.json`. Installed by
  `tools/project/install_findcrypt_extension.sh` into the isolated user-home
  `Library/ghidra/ghidra_12.2_PUBLIC/Extensions` directory during rebuild.
- `data/database.json` — 130 cryptographic constant signatures (AES S-boxes,
  Rijndael T-tables, SHA/MD constants, DES S-boxes, CRC32 table, Blowfish,
  Camellia, ChaCha, Ed25519, Whirlpool, and more). Also used directly by
  `GhidraCliBridge.handleFindCrypto()` for CLI-based queries.
- `patches/ghidra-12.2-task-monitor.patch` — the only source change from the
  pinned upstream commit. Renames both `TaskMonitor.checkCanceled()` calls to
  `checkCancelled()` without changing cancellation behavior.

## How it works

Two complementary paths:

1. **Auto-analyzer (Ghidra extension)** — installed by
   `tools/project/install_findcrypt_extension.sh` during `tools/project/rebuild_project.sh`.
   Runs automatically during Ghidra auto-analysis, labeling crypto constants
   and adding comments and array data. No manual invocation needed.

2. **CLI query (`ghidra find crypto`)** — `handleFindCrypto()` in
   `GhidraCliBridge.java` loads the same `database.json` at runtime and
   scans program memory for all occurrences of every signature, with
   automatic 32-bit byte-swap detection for endian-variant tables.

## Rebuilding for Ghidra 12.2

Requirements: JDK 25+ and `/opt/homebrew/opt/ghidra/libexec` containing Ghidra
12.2. The pinned upstream Gradle wrapper uses Gradle 9.5.1; the installed
Ghidra SDK requires Gradle 9.1 or later and compiles extensions for Java 25.
The installed SDK's
`Ghidra/Framework/Utility/lib/Utility-src.zip:ghidra/util/task/TaskMonitor.java`
declares `checkCancelled() throws CancelledException`, not `checkCanceled()`.
Apply the tracked patch to preserve both cancellation checks and their existing
exception propagation.
The integer `Listing.setComment(Address, int, String)` overload used upstream
is still present in 12.2, deprecated for removal since 11.4.

From the repository root, use a fresh temporary directory. Keep the checkout's
basename **GhidraFindcrypt**: Gradle derives the project, JAR, and extension
names from it because upstream has no `settings.gradle`.

```bash
BUILD_ROOT=$(mktemp -d /tmp/ghidra-findcrypt-12.2.XXXXXX)
REPO_ROOT=$PWD
git clone --no-checkout https://github.com/antoniovazquezblanco/GhidraFindcrypt.git \
  "$BUILD_ROOT/GhidraFindcrypt"
git -C "$BUILD_ROOT/GhidraFindcrypt" checkout --detach \
  fcaa49e545b131e2cc631168c6c168c1aec862a6
git -C "$BUILD_ROOT/GhidraFindcrypt" apply \
  "$REPO_ROOT/ghidra/ghidra-findcrypt/patches/ghidra-12.2-task-monitor.patch"
GHIDRA_INSTALL_DIR=/opt/homebrew/opt/ghidra/libexec TZ=UTC \
  "$BUILD_ROOT/GhidraFindcrypt/gradlew" -p "$BUILD_ROOT/GhidraFindcrypt" \
  --no-daemon clean buildExtension
```

The SDK places `ghidra_12.2_PUBLIC_<current-UTC-date>_GhidraFindcrypt.zip` in
`dist/`. Archive hashes can differ across build dates or environments.

Copy the single output ZIP into this directory and remove its superseded ZIP.
Update `PROVENANCE.json` with the actual filename, Ghidra version, build command,
and hashes below; retain the pinned upstream version, tag, commit, and
`source_patches` record. Keep the patch in `vendored_files` alongside the database
and new archive. Record the patch application as part of the build command.
Set `PACKAGE` to the new ZIP's complete path:

```bash
shasum -a 256 "$PACKAGE"
unzip -p "$PACKAGE" GhidraFindcrypt/lib/GhidraFindcrypt.jar | shasum -a 256
unzip -p "$PACKAGE" GhidraFindcrypt/data/database.json | shasum -a 256
```

Set `local_rebuild.artifact_sha256`, `jar_sha256`, and `database_sha256` to
those results. The database must remain byte-identical to `data/database.json`
and retain SHA-256
`8f7bdbc5f9bbe48a4ed93792adab67fca6f103384165ed1917d883870ee6f471`.

`tests/tooling/verify_findcrypt_database.py` checks the package and patch
provenance, archive/JAR/database hashes, declared Ghidra version, and Java 25
class version. The existing database-location checks run unchanged. After packaging:

```bash
tools/test findcrypt_database
uv run --locked tools/project/install_findcrypt_extension.sh
```

Use an isolated scratch project for analyzer discovery/loading checks.
