# Corrected Ghidra RH850 analysis of `RH850_P1M-E_Firmware.bin`

Reproducible procedure and scripts for the China-market Sienna EPS firmware
(`8965B4512000`, RH850/P1M-E R7F701381).

## Critical file-layout correction

`RH850_P1M-E_Firmware.bin` is **not** one flat block beginning at virtual address
`0x0`. Its `0x108000` bytes concatenate the MCU's two flash regions:

| File range | Size | Correct virtual range | Region |
|---|---:|---|---|
| `0x000000–0x007fff` | `0x8000` (32 KiB) | `0xFF200000–0xFF207FFF` | DataFlash |
| `0x008000–0x107fff` | `0x100000` (1 MiB) | `0x00000000–0x000FFFFF` | CodeFlash |

Evidence:

- R7F701381 has 1 MiB CodeFlash + 32 KiB DataFlash.
- The leading `0x8000` bytes match the report's DataFlash key-slot pages exactly
  (page 468 at file `0x7500`, page 475 at `0x76c0`, etc.).
- File `0x8180` contains `BOOT INFO AREA R7F701381...`, hence CodeFlash VA `0x180`.
- File `0x81F2` is the report's reset handler VA `0x1F2` and begins by setting
  `gp = 0xFEBF9800`.

The old `rh850fw` flat project is invalid. It shifted all CodeFlash addresses by
`+0x8000`, only found about 2,000 functions, and led to a false conclusion that
the two bootloader secrets were unreferenced. Use project **`rh850_p1me_mapped`**.

## Prerequisites

- Ghidra 12.x (here: `/opt/homebrew/opt/ghidra/libexec`).
- Rust `ghidra` CLI (`ghidra doctor` passes). `$GHIDRA` need not be set.
- `../ghidra_v850`, esaulenka's processor extension providing
  `v850e3:LE:32:default` (V850E3 / RH850).

The extension is incomplete upstream, and its calling-convention model often
mis-infers argument counts/order. Confirm register setup in disassembly before
trusting decompiled signatures.

## Import procedure

### 1. Build/install the RH850 language

```bash
GH=/opt/homebrew/opt/ghidra/libexec
cd ../ghidra_v850/data/languages
"$GH/support/sleigh" v850e3.slaspec
"$GH/support/sleigh" v850e2.slaspec       # optional

DST="$GH/Ghidra/Extensions/Renesas_v850"
mkdir -p "$DST"
cp -R ../../extension.properties ../../Module.manifest ../../data ../../LICENSE "$DST"/
```

Adjust the copy paths to the repository root if running from another directory.

### 2. Split the combined dump

```python
from pathlib import Path
src = Path("../RH850_P1m-E/RH850_P1M-E_Firmware.bin").read_bytes()
assert len(src) == 0x108000
Path("RH850_P1M-E_DataFlash.bin").write_bytes(src[:0x8000])
Path("RH850_P1M-E_CodeFlash.bin").write_bytes(src[0x8000:])
```

Current split-file SHA-256 values:

```text
DataFlash  81d87b678784bb2a07b1fdcb3d43dd40767d4f5ca1b56867b6575cd652a9ecb8
CodeFlash  21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde
```

### 3. Import CodeFlash and attach DataFlash

```bash
PROJDIR="$HOME/Library/Caches/ghidra-cli/projects"
AN=/absolute/path/to/ghidra_rh850_analysis

"$GH/support/analyzeHeadless" "$PROJDIR" rh850_p1me_mapped \
  -import "$AN/RH850_P1M-E_CodeFlash.bin" \
  -processor v850e3:LE:32:default \
  -noanalysis \
  -scriptPath "$AN" \
  -postScript AddDataFlash.java "$AN/RH850_P1M-E_DataFlash.bin"
```

Expected memory map:

```text
CodeFlash  00000000..000fffff  rx
DataFlash  ff200000..ff207fff  rw
```

### 4. Seed report entry points and analyze

```bash
ghidra --project rh850_p1me_mapped --program RH850_P1M-E_CodeFlash.bin \
  script run "$AN/SeedEntries.java"
ghidra --project rh850_p1me_mapped --program RH850_P1M-E_CodeFlash.bin analyze
```

### 5. Parse/seed the bootloader UDS service table

`SeedUdsServiceTable.java` parses the 20-entry table at CodeFlash `0x8E54`, creates
and names each handler, and adds explicit data references from table entries.

```bash
ghidra --project rh850_p1me_mapped --program RH850_P1M-E_CodeFlash.bin \
  script run "$AN/SeedUdsServiceTable.java"
ghidra --project rh850_p1me_mapped --program RH850_P1M-E_CodeFlash.bin analyze
```

### 6. Apply secret/crypto annotations

```bash
ghidra --project rh850_p1me_mapped --program RH850_P1M-E_CodeFlash.bin \
  script run "$AN/AnnotateBootloaderSecrets.java"
```

## Corrected result

- **5,445 functions, 170,833 instructions, 27,350 symbols**.
- Reset handler `0x1F2` sets `gp=0xFEBF9800`, matching the report.
- Report functions such as `0x66E48`, `0x674A8`, `0x730D4`, `0x758A0`, and
  `0x77E98` resolve/decompile at their stated addresses.
- AES S-box is CodeFlash `0x8FF1` (combined-file offset `0x10FF1`).
- UDS service table is CodeFlash `0x8E54`, with SecurityAccess SID `0x27`
  pointing to handler `0x5516`.

## Recovered family-secret references

The 16-byte constants are in CodeFlash, not at their combined-file offsets:

| Secret | Combined-file offset | CodeFlash VA | Real xref |
|---|---:|---:|---|
| `PAYLOAD_BUILD_SECRET` | `0x13FD8` | **`0xBFD8`** | `payload_build_derive_key` instruction `0x7070` |
| `SEED_KEY_SECRET` | `0x13FE8` | **`0xBFE8`** | `security_access_derive_stage1_key` instruction `0x6FF8` |

Both addresses are USER_DEFINED primary labels in the corrected Ghidra project.

### UDS SecurityAccess algorithm recovered from CodeFlash

The UDS table leads to:

```text
SID 0x27 handler                  uds_security_access             @ 0x5516
request-seed path                uds_security_access_request_seed @ 0x5328
send-key/verify path             uds_security_access_send_key     @ 0x53F2
stage 1                          security_access_derive_stage1_key @ 0x6FEC
stage 2                          aes128_ecb_encrypt_with_runtime_key @ 0x701E
composed expected-key operation  security_access_compute_expected_key @ 0x704C
```

The code implements Willem's documented construction:

```text
derived_key = AES-128-ECB-DECRYPT(SEED_KEY_SECRET, tester_data_record)
expected_key = AES-128-ECB-ENCRYPT(derived_key, ecu_seed)
```

`uds_security_access_send_key` compares the computed 16-byte value to the tester's
request and implements NRC `0x35` / lockout `0x36` behavior.

### Payload-build path

`payload_build_derive_key @ 0x7068` loads `PAYLOAD_BUILD_SECRET @ 0xBFD8` and uses
the forward AES block primitive. `uds_write_data_by_identifier @ 0x4948`
independently confirms the `0x201`/`0x202`/`0x203` DID sequence. The construction
matches:

```text
derived_payload_key = AES-128-ECB-ENCRYPT(PAYLOAD_BUILD_SECRET, DID_0x201)
```

## Report observations

- The report's function/virtual addresses are correct; the initial local analysis
  was wrong because the combined file was imported flat.
- Appendix A says "SHA-256 hashes only," but lists 16-byte values (32 hex chars),
  not 32-byte SHA-256 values; both are the actual public secrets and validate
  cryptographically against the existing tooling/payloads.
- DataFlash page 478 is quoted as beginning `020000cb...`; this dump actually has
  `0200feca...`. Other cited key-slot signatures match.

## Scripts

- `AddDataFlash.java` — attach DataFlash at `0xFF200000`.
- `SeedEntries.java` — seed report-named reset/SecOC/CSM entry points.
- `SeedUdsServiceTable.java` — parse/seed/name the bootloader UDS table.
- `AnnotateBootloaderSecrets.java` — name secrets and verified AES/UDS functions.
- `FindMappedSecretRefs.java` — verify direct references to both corrected secret VAs.
- `FindMappedRegionRefs.java`, `FindBootloaderDiagnostics.java`,
  `FindHandlerRegistrations.java` — investigation helpers.
- `legacy-flat-import/` — preserved scripts from the invalid flat-import analysis;
  do not use them for current results.

The valid project is stored at:
`~/Library/Caches/ghidra-cli/projects/rh850_p1me_mapped`.
