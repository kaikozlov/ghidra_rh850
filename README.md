# Ghidra RH850 analysis of `RH850_P1M-E_Firmware.bin`

Reproducible procedure and scripts for the China-market Sienna EPS firmware
(`8965B4512000`, RH850/P1M-E R7F701381).

## Repository layout

```text
docs/                 analysis reports by subsystem
firmware/             committed CodeFlash/DataFlash split images
data/                 generated analysis artifacts
ghidra/scripts/       import, seed, annotation, and investigation scripts
project/              durable annotated Ghidra project
tests/                self-contained verification, fixtures, optional corroboration
tools/                data generators and durable Ghidra rebuild tooling
external-references.lock.json  pinned public repositories/artifacts
pyproject.toml, uv.lock         locked UV verification environment
legacy/flat-import/   preserved invalid flat-import investigation
```

Install the locked Python environment and run the self-contained firmware suites:

```bash
uv sync --locked
make verify
```

`make verify` reads only tracked files. Optional checks against pinned public
repositories are separate:

```bash
make verify-external EXTERNAL_REPOS_DIR=/path/containing/the/checkouts
```

Exact repository commits, expected checkout directory names, artifact hashes,
and payload-fixture provenance are recorded in
`external-references.lock.json`. Check out those commits beneath
`EXTERNAL_REPOS_DIR`; the optional suite fails on a missing checkout, a commit
mismatch, or changed artifact bytes. It is intentionally not part of the
self-contained default target.

## Critical file-layout correction

`RH850_P1M-E_Firmware.bin` is **not** one flat block beginning at virtual address
`0x0`. Its `0x108000` bytes concatenate the MCU's two flash regions:

| File range | Size | Correct virtual range | Region |
|---|---:|---|---|
| `0x000000–0x007fff` | `0x8000` (32 KiB) | `0xFF200000–0xFF207FFF` | DataFlash |
| `0x008000–0x107fff` | `0x100000` (1 MiB) | `0x00000000–0x000FFFFF` | CodeFlash |

Evidence:

- R7F701381 has 1 MiB CodeFlash + 32 KiB DataFlash.
- The leading `0x8000` bytes match the report's cited DataFlash page bytes exactly
  (page 468 at file `0x7500`, page 475 at `0x76c0`, etc.); their corrected NvM semantics are documented in `docs/DATAFLASH_LAYOUT.md`.
- File `0x8180` contains `BOOT INFO AREA R7F701381...`, hence CodeFlash VA `0x180`.
- File `0x81F2` is the report's reset handler VA `0x1F2` and begins by setting
  `gp = 0xFEBF9800`.

The old `rh850fw` flat project is invalid. It shifted all CodeFlash addresses by
`+0x8000`, only found about 2,000 functions, and led to a false conclusion that
the two bootloader secrets were unreferenced. Use project **`rh850_p1me_mapped`**.

## Pre-built project (committed under `project/`)

The fully analyzed, annotated project is committed in `project/`
(`rh850_p1me_mapped.gpr` + `rh850_p1me_mapped.rep/`, ~29 MiB). It already
contains the discovered functions, both secret labels, the bootloader and
application diagnostic handlers, and the annotated SecurityAccess/payload-gate/
AES/SecOC/CAN transport and boot/application architecture paths — so you can
explore it directly without rebuilding.

Open it with the `ghidra` CLI. The project location must be an **absolute**
path: Ghidra 12.1+ rejects any path component beginning with `.`
(so `./project` fails; use `$PWD/project` or a full path).

```bash
ghidra --projects-dir "$PWD/project" --project rh850_p1me_mapped \
       --program RH850_P1M-E_CodeFlash.bin <subcommand>
```

> **Durability caveat.** The `ghidra` CLI bridge keeps the program in memory and
> only writes a durable snapshot when the daemon shuts down cleanly. After any
> `analyze` or `script run` whose changes you want to keep, run
> `ghidra --projects-dir "$PWD/project" --project rh850_p1me_mapped stop`
> (teardown commits to disk). Never commit `project/` while a daemon is running
> — it holds transient `.lock` / `tmp*` files (git-ignored under `project/`).

## Prerequisites

- [Astral UV](https://docs.astral.sh/uv/) for the locked Python environment.
- Ghidra **12.1.2** (the tested Homebrew location is
  `/opt/homebrew/opt/ghidra/libexec`).
- Rust `ghidra` CLI **0.2.1** (`ghidra doctor` must pass).
- esaulenka's `ghidra_v850` processor extension at the exact revision below.

The processor pin in `external-references.lock.json` is:

```text
repository  https://github.com/esaulenka/ghidra_v850.git
commit      14c1b5be32b8ec741ee626c8bca9885c58f7a473
v850e3 spec 50df5bd3d5b7a23018533f126d83ea5249cb92b8645b1cd0d1a9f309a993eb15
```

The extension's calling-convention model is incomplete. Confirm register setup
in disassembly before trusting decompiled signatures.

### Install the pinned RH850 language

```bash
GH=/opt/homebrew/opt/ghidra/libexec
V850=/absolute/path/to/ghidra_v850

gh repo clone esaulenka/ghidra_v850 "$V850"
git -C "$V850" checkout 14c1b5be32b8ec741ee626c8bca9885c58f7a473
printf '%s  %s\n' \
  50df5bd3d5b7a23018533f126d83ea5249cb92b8645b1cd0d1a9f309a993eb15 \
  "$V850/data/languages/v850e3.slaspec" | shasum -a 256 -c -

"$GH/support/sleigh" "$V850/data/languages/v850e3.slaspec"
"$GH/support/sleigh" "$V850/data/languages/v850e2.slaspec"  # optional

DST="$GH/Ghidra/Extensions/Renesas_v850"
mkdir -p "$DST"
cp -R "$V850/extension.properties" "$V850/Module.manifest" \
      "$V850/data" "$V850/LICENSE" "$DST"/
```

`tools/rebuild_project.sh` refuses to run if the installed `v850e3.slaspec`
does not match this pinned source hash.

## Rebuild the complete Ghidra project

The committed split images are the only firmware inputs. Their SHA-256 values
are:

```text
DataFlash  81d87b678784bb2a07b1fdcb3d43dd40767d4f5ca1b56867b6575cd652a9ecb8
CodeFlash  21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde
Combined   0bba74d0e443f9dd3da33e3a28c3511ec31e35e8303acef7e0117fbdc91d5a86
```

Run the canonical rebuild command into the ignored `build/project/` directory:

```bash
make rebuild-project
```

Choose another absolute output path with:

```bash
make rebuild-project PROJECT_DIR=/absolute/path/to/project
```

To deliberately replace an existing output—including the committed snapshot—use
the script directly and pass `--force`:

```bash
tools/rebuild_project.sh --project-dir "$PWD/project" --force
```

The script uses four staged `analyzeHeadless` transactions, each with a durable
`-commit`. Staging matters: injecting every seed before the first analysis pass
produces a different graph and does not reproduce the committed statistics.

1. import CodeFlash without analysis and map DataFlash with `AddDataFlash.java`;
2. run `SeedEntries.java`, then the base auto-analysis;
3. run `SeedUdsServiceTable.java`, then re-run analysis;
4. seed the remaining missed functions with:
   - `SeedCanTransportFunctions.java`;
   - `SeedPayloadVerificationFunctions.java`;
   - `SeedSecocNvmFunctions.java`;
   - `SeedSecocApplicationFunctions.java`;
   - `SeedApplicationDiagnosticFunctions.java`;
   - `SeedArchitectureFunctions.java`;
5. re-run analysis and apply every annotation script:
   - `AnnotateBootloaderSecrets.java`;
   - `AnnotatePayloadGate.java`;
   - `AnnotateSecocNvmCorrection.java`;
   - `AnnotateSecocApplication.java`;
   - `AnnotateDataFlashLayout.java`;
   - `AnnotateDidModel.java`;
   - `AnnotateCanTransport.java`;
   - `AnnotateApplicationDiagnostics.java`;
   - `AnnotateArchitecture.java`;
6. open the result through the CLI, record statistics, and cleanly stop the
   daemon so the database is durable;
7. require exactly 5,554 functions, 172,946 instructions, 27,742 symbols, two
   memory sections, and `0x108000` mapped bytes.

Expected memory map:

```text
CodeFlash  00000000..000fffff  rx
DataFlash  ff200000..ff207fff  rw
```

See `docs/PAYLOAD_GATE_ANALYSIS.md` for the complete download, authentication,
and execution trace.

## Corrected result

- **5,554 functions, 172,946 instructions, 27,742 symbols**.
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

### Complete payload acceptance and execution path

The firmware-side security boundary is now fully traced in
`docs/PAYLOAD_GATE_ANALYSIS.md` and independently checked against the committed
firmware and two unique pinned payload fixtures by `tests/verify_payload_gate.py`:

```text
RequestDownload 0x34 @ 0x5D68
  -> derive payload key; initialize AES-CBC
TransferData 0x36 @ 0x4DBA
  -> decrypt ciphertext into 0xFEBF0000..0xFEBF0FFF
TransferExit 0x37 @ 0x5C92
Routine 0x10F0 @ 0x567E
  -> validate embedded address/length
  -> CRC32 plaintext[0:0xFF0] == 0xFFFFFFFF
  -> CMAC(DID_0x202_IV || plaintext[0:0xFF0]) == plaintext[0xFF0:]
  -> authorize the RAM region
Routine 0xFF00 @ 0x567E
  -> start legitimate erase path
  -> flash engine loads *(uint32_t *)0xFEBF0FD0
  -> indirect call to 0xFEBF0000 (uploaded shellcode)
```

The callback load and call are at CodeFlash `0x4350` and `0x435E`. All public
payloads deliberately store `0xFEBF0000` at plaintext offset `0xFD0`. Thus
`0xFF00` is not a direct execute-RAM service: it is an erase operation whose
RAM-resident flash callback is overwritten by the authenticated 4 KiB image.

### Corrected SecOC runtime-key investigation

`docs/SECOC_RUNTIME_KEY_LIFECYCLE.md` completely retraces the report's proposed
`0x65CD8 -> 0x66E48 -> 0x67590 -> 0x72F58` key path. It is not a key lifecycle:
it is an AUTOSAR NvM redundancy/checkpoint subsystem.

Definitive corrections, independently checked by `tests/verify_secoc_nvm.py`:

- `0x72F58` is NvM service `0x06` (`ReadBlock`), not CSM key-set.
- `0x72F84` is NvM service `0x07` (`WriteBlock`), not MAC generation.
- `0x67590` restores raw/XOR55/XORAA persistent copies into generic work
  groups rooted at `0xFEBF0B08` (the earlier `0xFEBFEB08` address was wrong).
- `0x67608` creates and persists those three copies.
- pages 468–479 decode exactly to four structured state objects; they are not
  ICU derivation metadata or raw AES keys.
- `0xFEBEF468/478/488` and the workbuf contain those state records, not the SecOC key.
- no dealer-triggered rekey, plaintext key injection, or per-boot fused-key
  derivation exists in the claimed path.

`docs/DATAFLASH_LAYOUT.md` completes the entire 32 KiB map;
`tests/verify_dataflash_layout.py` checks it and
`data/dataflash_nvm_records.csv` lists all 122 physical records.
Key corrections:

- configured normal NvM records occupy pages 256–479;
- pages 432–479 are a 48-record raw/XOR55/XORAA bank for all 16
  SecOC-associated redundancy objects—not 12 ICU key-slot pages;
- object 15 is length 32, base NvM block 41, RAM mirror `0xFEBF02E8`;
- its second field is raw `0xFF206E14`, XOR55 `0xFF206D14`, XORAA
  `0xFF206C14`, and RAM `0xFEBF02F8`;
- related Sienna/Yaris/partner EPS field evidence CMAC-verifies the operational
  SecOC key at `0xFF206E14`, but all three object-15 copies are invalid in this
  exact committed `8965B4512000` snapshot;
- DIDs `0x201/0x202/0x203` are volatile bootloader session parameters at RAM
  `0xFEBF2D08`/`0xFEBF2CF8`/special state, not DataFlash-backed values;
- the final 2 KiB remains strongly consistent with an ICU-S-reserved tail, but
  this no longer supports claiming that the SecOC key resides there.

`docs/DID_MODEL.md` completes the bootloader ReadDataByIdentifier/WriteDataByIdentifier
model; `tests/verify_did_model.py` checks it directly from CodeFlash:

- the table at `0x8F14` has exactly four descriptors;
- `F181` is the sole readable DID and returns `02 || 32*0x21`, not a VIN or
  `8965B...` identifier;
- `0201/0202/0203` are the only writable DIDs and require programming session,
  unlocked SecurityAccess, exact lengths, and order `0203 -> 0201 -> 0202`;
- `0203` ignores all five request bytes and exists only to arm the sequence;
- `0201` supplies the payload key-derivation input at `0xFEBF2D08`;
- `0202` supplies the CBC IV/CMAC prefix at `0xFEBF2CF8` and sets the
  RequestDownload crypto-ready flag;
- no VIN, serial, part-number, fingerprint, config, or DataFlash-backed DID is
  exposed by these two bootloader handlers.

The proposed FEBEF object-0/key-set interpretation remains invalid.

`docs/SECOC_APPLICATION_CHAIN.md` traces the separate generated application
receive path and is checked by `tests/verify_secoc_application.py`:

- six profiles bind CAN/Data IDs `0x0F/0x2E4/0x131/0x132/0x90/0xD7` to the
  exact application RX PDU routes;
- ordinary classic frames authenticate
  `DataID_be16 || payload4 || freshness48`, with a four-bit transmitted
  freshness value followed by the first 28 CMAC bits;
- full freshness packs trip16/reset20/message8/reset-low2 plus two zero bits;
- CMAC verification resolves CryptoIf handle 0, selects ICU-S key slot 4, and
  never reads object-15 RAM `0xFEBF02F8`;
- this calibration's slot-4 known-answer vector is exactly CMAC of 16 zero bytes
  under an erased `FF*16` key;
- `0x344` has no receive filter or SecOC record in this image.

Together with the invalid object 12–15 bank, this makes an unprovisioned/default
key state the leading explanation for this snapshot. The report
specifies the correct provisioned-unit experiment: filter NvM blocks 41/45/49,
observe asynchronous completion and the corrected work buffers, compare the RAM
mirror and post-write DataFlash, instrument ICU slot 4, and validate candidates
against synchronized CAN oracle data.

### Application diagnostics and bootloader entry

`docs/APPLICATION_DIAGNOSTICS.md` separates the application diagnostic stack from
the bootloader handlers above; `tests/verify_application_diagnostics.py` checks
the recovered tables and control-flow evidence directly from CodeFlash:

- the primary application service table at `0x25E30` contains exactly
  `10/11/14/19/22/23/27/28/2E/31/34/36/37/3E/85/AB/BA`;
- application DID records at `0x2A30C` expose `F181`, `F186`, and `F18C` through
  callbacks `0x4E8E4`/`0x4E90A`/`0x4E918`;
- application `F181` emits the real `8965B4512000` software-ID slot, while the
  bootloader's separate four-entry DID table emits the placeholder response;
- application DiagnosticSessionControl subfunctions 1/2/3 call wrappers at
  `0x93FF6`/`0x94006`/`0x94016` and share an asynchronous state machine at
  `0x93F3C`;
- application PROGRAMMING is allowed only from current session 2 or 3, rejects
  raw speed above `0x0180` with NRC `0x88`, and then requires an unresolved
  status byte, scaled supply at least `0x0A00`, and a clear handoff flag;
- the generated `0x08000200/201` lower calls are no-op stubs in this image;
  successful entry instead queues system event 9, shutdown mode `0x900`, and
  the hard-reset path while UDS remains response-pending;
- the first PROGRAMMING request in public extraction tooling is handled by this
  application path, not bootloader handler `0x614A`, and its final timeout is
  compatible with reset overtaking the final positive response;
- bootloader `0x614A` itself queues valid transitions for task `0x6244`; helper
  `0x4776` reserves transient main-loop state cleared by `0x479A` and is not a
  one-attempt-per-boot latch;
- the bootloader's functional request ID is `0x777`, not generic OBD `0x7DF`.

These findings provide strong evidence for Denso software continuity when a
related EPS returns the same application DID/service schema. They do not prove
the related MCU, byte-identical bootloader contents, retained secrets/payload
routines, or that a PROGRAMMING timeout must be external to the EPS.

### Boot/application architecture and application CAN routing

`docs/FIRMWARE_ARCHITECTURE.md` maps the broader execution architecture and
`tests/verify_architecture.py` checks its raw CodeFlash landmarks:

- the application vector/executable base is `0x20000`, where it installs
  `EBASE`; this is not a strict boundary for all calibration/metadata, and its
  384-entry EIINT pointer table begins at `0x20200`;
- boot handoff at `0x13B0` reads the entry pointer at `0xFFDB8`, whose value is
  `0x20880`, then the application initializes modules and enters the foreground
  loop at `0x64FCC`;
- that foreground loop polls TAUJ0 channel 3's `EIRF136` tick and runs the
  NvM/CSM, main application, and corrected SecOC-NvM cyclic groups;
- the application table has explicit handlers for ECM, TAUJ0 channels 0..2,
  RSCAN CAN1 RX/TX, two hardware-reserved channels, and flash completion;
- the CAN1 acceptance table at `0x231A0` contains 47 normal receive IDs plus
  `0x7A1/0x777/0x7A0/0x7F7`; `0x2E4`, `0x0F`, and `0x131` are explicit RX
  routes, while `0x344` is absent from this firmware's receive filters.

### Confirmed bootloader CAN / ISO-TP / UDS transport

`docs/CAN_TRANSPORT_ANALYSIS.md` traces the complete diagnostic path and
`tests/verify_can_transport.py` independently checks it directly against CodeFlash.
`tests/verify_external_corroboration.py` optionally checks the matching public
extraction tooling and shellcode:

- standard physical request ID **`0x7A1`** routes through channel 1/common FIFO
  0, CanIf RxPduId 0, and the physical CanTp/Dcm connection;
- standard functional request ID **`0x777`** routes through common FIFO 1 and is
  single-frame-only;
- standard response ID **`0x7A9`** uses hardware Tx handle `0x13`;
- the firmware implements classic 8-byte ISO-TP SF/FF/CF/FC reception,
  segmented responses, sequence/block/STmin handling, and a 12-bit `0xFFF`
  maximum SDU;
- `rscfd_tx_buffer_submit @ 0x36DE` writes the Tx message-buffer registers and
  requests transmission through **`CFDTMCn @ 0xFFD20250+n`**; for the diagnostic
  route, `n=16` and the command byte is `0xFFD20260`;
- the receive chain is RSCFD -> CanIf -> CanTp -> PduR/Dcm ->
  `uds_service_dispatch @ 0x5222`, and the response chain returns through CanTp,
  CanIf, and RSCFD;
- the second byte of each UDS table entry at `0x8E54` is a
  **physical/functional addressing mask**, not a session mask.

## Report observations

- The report's virtual addresses generally map to real code after correcting the
  combined-file import, but several semantic labels and its headline ICU/key
  lifecycle interpretation are wrong; see `docs/SECOC_RUNTIME_KEY_LIFECYCLE.md`.
- Appendix A says "SHA-256 hashes only," but lists 16-byte values (32 hex chars),
  not 32-byte SHA-256 values; both are the actual public secrets and validate
  cryptographically against the existing tooling/payloads.
- DataFlash page 478 is quoted as beginning `020000cb...`; this dump actually has
  `0200feca...`. The page bytes match the decoded triplicate NvM state described
  in the corrected lifecycle analysis.

## Analysis assets

| Path | Contents |
|---|---|
| `docs/` | Firmware architecture, application SecOC chain, SecOC/NvM correction, payload gate, DataFlash, application/bootloader diagnostics, DID, and CAN transport reports |
| `ghidra/scripts/import/` | DataFlash attachment/import helper |
| `ghidra/scripts/seed/` | Function and table seeds missed by auto-analysis |
| `ghidra/scripts/annotate/` | Durable names, labels, and comments for each completed investigation |
| `ghidra/scripts/investigate/` | Reusable reference/operand search helpers |
| `tests/` | Eight self-contained firmware suites, optional external corroboration, and pinned payload fixtures |
| `tools/` | DataFlash CSV generator, durable Ghidra rebuild, and project-statistics verifier |
| `external-references.lock.json` | Exact upstream commits and artifact hashes |
| `pyproject.toml`, `uv.lock` | Locked UV/PyCryptodome verification environment |
| `data/` | Generated 122-record NvM map |
| `firmware/` | Correctly split CodeFlash and DataFlash images |
| `legacy/flat-import/` | Preserved scripts from the invalid original mapping; do not use |
| `project/` | Pre-built durable Ghidra project |

Use `make rebuild-project` for a non-destructive rebuild under `build/project/`.
All seed and annotation scripts are idempotent; the rebuild script runs them in
staged durable headless transactions.
