# AGENTS.md — ghidra_rh850_analysis

Ghidra analysis of the China-market Sienna EPS firmware
(`8965B4512000`, RH850/P1M-E R7F701381). This repo holds the corrected split
images, analysis scripts, pinned payload fixtures, and the pre-built Ghidra
project; core verification does not require the original sibling checkout. Read `README.md`
for the full procedure and evidence — the notes below are the parts that are
easy to get wrong.

## File layout (the thing that was originally wrong)

`RH850_P1M-E_Firmware.bin` (`0x108000` bytes) is **two flash regions**, not one
flat block. Always split before importing:

| File range | Size | Virtual range | Region |
|---|---:|---|---|
| `0x000000–0x007fff` | `0x8000` | `0xFF200000–0xFF207FFF` | DataFlash |
| `0x008000–0x107fff` | `0x100000` | `0x00000000–0x000FFFFF` | CodeFlash |

Mapping CodeFlash VA = `file_offset − 0x8000`. The committed images under
`firmware/` are already split; `tests/verify_findings.py` re-checks their hashes,
reconstructs the combined image in memory, and verifies every base finding.

## Repository layout

- `docs/` — subsystem analysis reports.
- `firmware/` — committed CodeFlash/DataFlash split images.
- `data/` — generated analysis artifacts.
- `ghidra/scripts/{import,seed,annotate,investigate}/` — Ghidra scripts by role.
- `tests/` — self-contained raw-firmware suites plus optional external corroboration.
- `tools/` — generators and the durable project rebuild workflow.
- `external-references.lock.json` — pinned upstream commits and artifact hashes.
- `pyproject.toml` / `uv.lock` — locked verification environment.
- `project/` — durable annotated Ghidra project; do not move transient state here.
- `legacy/flat-import/` — preserved invalid original analysis.

## The `ghidra` CLI is a persistent daemon — durability is the main trap

The `ghidra` CLI runs a long-lived bridge (TCP server inside Ghidra) that keeps
the program **in memory**. Edits (`analyze`, `script run`) are **not durable on
disk until the daemon shuts down cleanly**. Concretely:

1. **Always `stop` before copying or committing the project.**
   `ghidra ... stop` triggers the teardown commit that writes the durable
   snapshot. Copying or `git add project/` while a daemon is running captures an
   empty/stale DB. If a fresh daemon opens the project and reports 0 functions,
   this is why — `stop`, then re-copy.
2. **Never commit `project/` while a daemon is running.** It holds transient
   `.lock` / `*.lock~` / `tmp*` files (git-ignored under `project/.gitignore`).
   Confirm `pgrep -f 'AnalyzeHeadless.*rh850'` is empty before committing.
3. **Opening compacts the DB** (`db.N.gbf` → `db.N+1`) on each clean stop. This
   is harmless and expected; don't be alarmed that the filename changes.
4. **The `analyze` command's save is silently swallowed** by the bridge
   (`bridge.rs` notes the teardown commit "races the JVM kill"). Treat `stop` as
   the only reliable persist. For a guaranteed-durable rebuild, use a raw
   `analyzeHeadless -process -commit` one-shot instead of the daemon.

## Opening the project

The project is committed under `project/`. Use an **absolute** `--projects-dir`:
Ghidra 12.1+ rejects any path component starting with `.`, so `./project` fails.

```bash
ghidra --projects-dir "$PWD/project" --project rh850_p1me_mapped \
       --program RH850_P1M-E_CodeFlash.bin <subcommand>
# e.g. ... stats | decompile 0x6fec | x-ref to 0xbfe8 | symbol list
```

If you re-run `analyze` or any `script run` and want to keep the result, run
`ghidra ... stop` afterward (the changes live in the daemon until then).

## Verified findings (do not re-claim the old wrong conclusions)

These are all checked by the self-contained `tests/verify_findings.py` against
the reconstructed combined firmware — trust them:

- Reset handler `0x1F2` sets `gp = 0xFEBF9800`.
- `PAYLOAD_BUILD_SECRET`: CodeFlash VA **`0xBFD8`** (file `0x13FD8`), referenced
  at `0x7070` in `payload_build_derive_key`.
- `SEED_KEY_SECRET`: CodeFlash VA **`0xBFE8`** (file `0x13FE8`), referenced at
  `0x6FF8` in `security_access_derive_stage1_key`.
- UDS service table @ `0x8E54` (20 entries, `SID:u8 mask:u8 rsv:u16 handler:u32`);
  SID `0x27` → handler `0x5516`.
- AES-128 S-box @ `0x8FF1`, Rcon @ `0x8FE1` (note the `+1`).
- SecurityAccess algorithm: `expected = AES-ENC(AES-DEC(SEED_KEY, data_record), ecu_seed)`.
- The complete payload gate is documented in `docs/PAYLOAD_GATE_ANALYSIS.md` and
  independently checked by `tests/verify_payload_gate.py` against two unique
  pinned public payload fixtures:
  - TransferData decrypts AES-CBC ciphertext into `0xFEBF0000..0xFEBF0FFF`.
  - Routine `0x10F0` checks embedded address/length, CRC32 residue, then
    `CMAC(DID_0x202_IV || plaintext[0:0xFF0])` against the final 16 bytes.
  - Success authorizes the RAM region; failure returns NRC `0x72`.
  - Routine `0xFF00` starts a flash erase path which loads the function pointer
    at RAM `0xFEBF0FD0` (CodeFlash instruction `0x4350`) and calls it indirectly
    at `0x435E`. Public payloads store `0xFEBF0000` at offset `0xFD0`.
  - `0xFF00` is therefore not a direct execute-RAM routine; execution occurs by
    replacing the legitimate flash-driver callback inside the authenticated image.
- The report's proposed SecOC runtime-key command path is **wrong**. Read
  `docs/SECOC_RUNTIME_KEY_LIFECYCLE.md`; `tests/verify_secoc_nvm.py` checks it:
  - `0x72F58`/`0x72F84` are AUTOSAR NvM `ReadBlock`/`WriteBlock`, not CSM key-set/MAC.
  - `0x67590/0x67608/0x67C34` generically restore, persist, and reconcile
    raw/XOR55/XORAA objects. This is not an ICU command path.
  - pages 468–479 are objects 0–3; FEBEF468/478/488 contain their structured state.
  - `0x758A0/0x785D2` are NvM/DataFlash service machinery, not ICU derivation.
- The complete 32 KiB map is in `docs/DATAFLASH_LAYOUT.md` and is checked by
  `tests/verify_dataflash_layout.py`:
  - 122 physical records occupy pages 256–479; pages 0–255 are not in the map.
  - pages 432–479 are the full 16-object SecOC triplicate bank.
  - object 15 is len32/base block41/RAM `0xFEBF02E8`; its key field maps raw
    `0xFF206E14`, XOR55 `0xFF206D14`, XORAA `0xFF206C14`, RAM `0xFEBF02F8`.
  - related-variant field evidence CMAC-verifies the SecOC key at `0xFF206E14`.
    This exact dump has three invalid object-15 copies and no verified key.
  - DIDs `0x201/0x202/0x203` are volatile bootloader inputs, not DataFlash-backed.
  - the final 2 KiB is likely ICU-S-reserved, but linking this SecOC key to that
    tail is unsupported. The exact operational source for this snapshot is unknown.
  - the dealer/FEBEF capture design remains wrong. A generic `0x72F58` hook must
    filter blocks 41/45/49 and observe completion to see object 15 on a provisioned
    variant; the call itself is not key-set.
- The complete bootloader DID model is in `docs/DID_MODEL.md` and is checked by
  `tests/verify_did_model.py`:
  - handlers `0x5FB8`/`0x4948` search exactly four descriptors at `0x8F14`;
  - `F181` is the only readable DID and synthesizes `02 || 32*0x21`; it does not
    return VIN, part number, `BOOT INFO AREA`, or `8965B4512000` in this bootloader;
  - `0201/0202/0203` are the only writable DIDs and require programming session,
    SecurityAccess state 2, exact lengths, and strict order `0203 -> 0201 -> 0202`;
  - `0203` ignores its five bytes and merely arms state 0 -> 1;
  - `0201` copies to `0xFEBF2D08`; `0202` copies to `0xFEBF2CF8`, sets the crypto-ready
    flag at `0xFEBF2B16`, and returns the sequence to state 0;
  - no VIN, serial, spare-part, configuration, or DataFlash-backed DID exists in
    these bootloader handlers. Do not project application-mode/related-variant
    probe expectations onto this table.

The prior "secrets are unreferenced / separate bootloader image" conclusion was
an artifact of the wrong flat import and is **false**. The scripts that produced
it live in `legacy/flat-import/` — do not use them for current results.

## Scripts and verification

- `ghidra/scripts/import/` contains the split-image import helper.
- `ghidra/scripts/seed/` contains all function/table seeds missed by analysis.
- `ghidra/scripts/annotate/` contains the durable labels/comments for completed work.
- `ghidra/scripts/investigate/` contains operand/reference search helpers.
- `make verify` runs six self-contained suites through UV; it must not require
  sibling repositories.
- `make verify-external EXTERNAL_REPOS_DIR=...` checks optional public checkouts
  against `external-references.lock.json`.
- `tools/generate_dataflash_layout.py` regenerates `data/dataflash_nvm_records.csv`;
  run `make generate-dataflash`.
- `legacy/flat-import/` is historical only and must not be used.

## Rebuilding the project from scratch

Run `make rebuild-project` for a non-destructive rebuild under `build/project/`.
`tools/rebuild_project.sh` imports both regions, runs every seed and annotation
in four staged durable headless commits, cleanly stops the stats daemon, and
verifies exact project statistics. Do not collapse the stages: seed timing
changes Ghidra's recovered graph. Use `--project-dir "$PWD/project" --force` only when
deliberately replacing the committed snapshot.

## Tooling notes

- Ghidra 12.1.2 at `/opt/homebrew/opt/ghidra/libexec`; RH850 language
  `v850e3:LE:32:default` from esaulenka/ghidra_v850 commit
  `14c1b5be32b8ec741ee626c8bca9885c58f7a473`. The rebuild script verifies the
  installed `v850e3.slaspec` hash. The extension's calling-convention model is
  incomplete — confirm register setup before trusting decompiled signatures.
- `ghidra` CLI project resolution: `GHIDRA_PROJECT_DIR` env, config
  `ghidra_project_dir`, `--projects-dir`, else `~/Library/Caches/ghidra-cli/projects`.
