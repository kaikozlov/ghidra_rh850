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
- `project/` — committed Ghidra project snapshot; never daemon-open directly
  (see "Working copy vs. committed snapshot" below). Update only via
  `make snapshot-project`.
- `legacy/flat-import/` — preserved invalid original analysis.

## The `ghidra` CLI is a persistent daemon — durability is the main trap

The `ghidra` CLI runs a long-lived bridge (TCP server inside Ghidra) that keeps
the program **in memory**. Edits (`analyze`, `script run`) are **not durable on
disk until the daemon shuts down cleanly**. Concretely:

1. **Always `stop` before copying or committing the working project.**
   `ghidra ... stop` triggers the teardown commit that writes the durable
   snapshot. Copying or `git add` while a daemon is running captures an
   empty/stale DB. If a fresh daemon opens the project and reports 0 functions,
   this is why — `stop`, then re-copy.
2. **Never commit while a daemon is running.** It holds transient
   `.lock` / `*.lock~` / `tmp*` files (git-ignored). Confirm
   `pgrep -f 'AnalyzeHeadless.*rh850'` is empty before snapshotting.
3. **Opening compacts the DB** (`db.N.gbf` → `db.N+1`) on each clean stop. This
   is harmless and expected; don't be alarmed that the filename changes. It is
   also why the committed snapshot must never be daemon-opened (see below).
4. **The `analyze` command's save is silently swallowed** by the bridge
   (`bridge.rs` notes the teardown commit "races the JVM kill"). Treat `stop` as
   the only reliable persist. For a guaranteed-durable rebuild, use a raw
   `analyzeHeadless -process -commit` one-shot instead of the daemon.

## Working copy vs. committed snapshot

`project/` is a **committed snapshot** — a durable, annotated reference. Rule 3
above means it must **never be opened directly by a `ghidra` daemon**: any open
compacts its DB and dirties the tree even with no analysis change. All
interactive work happens in the gitignored working copy at `build/project/`:

- `make work-project` — materialize `build/project/` from the committed
  snapshot with a fast local copy (~2s) if it does not already exist.
- `make rebuild-project` — fresh from-scratch rebuild into `build/project/`.
- `make snapshot-project` — the **only** path that mutates the committed
  `project/`. Verifies exact stats on the working copy, rsyncs
  `build/project/ → project/`, and stages it.

## Opening the working project

Use `build/project/` (run `make work-project` first if it is missing) with an
**absolute** `--projects-dir`: Ghidra 12.1+ rejects any path component starting
with `.`, so `./build/project` fails.

```bash
make work-project   # one-time: copy snapshot -> build/project
ghidra --projects-dir "$PWD/build/project" --project rh850_p1me_mapped \
       --program RH850_P1M-E_CodeFlash.bin <subcommand>
# e.g. ... stats | decompile 0x6fec | x-ref to 0xbfe8 | symbol list
```

If you re-run `analyze` or any `script run` and want to keep the result in the
working copy, run `ghidra ... stop` afterward (the changes live in the daemon
until then). To promote a finished working copy into the committed snapshot,
run `make snapshot-project`.

## Verified findings (do not re-claim the old wrong conclusions)

These are all checked by the self-contained `tests/verify_findings.py` against
the reconstructed combined firmware — trust them:

- Reset handler `0x1F2` sets `gp = 0xFEBF9800`.
- `PAYLOAD_BUILD_SECRET`: CodeFlash VA **`0xBFD8`** (file `0x13FD8`), referenced
  at `0x7070` in `payload_build_derive_key`.
- `SEED_KEY_SECRET`: CodeFlash VA **`0xBFE8`** (file `0x13FE8`), referenced at
  `0x6FF8` in `security_access_derive_stage1_key`.
- `APPLICATION_LEVEL2_SA_SECRET`: CodeFlash VA **`0x20840`**, the 16-byte
  application-level SecurityAccess key (`89 3e 08 41 8c 74 1f fa 2a 9c 04 4b
  ff a5 58 13`). Used by `0x8C7BC` in the level-2 key-verification pipeline.
  This is the third recovered family secret alongside `PAYLOAD_BUILD_SECRET`
  and `SEED_KEY_SECRET`.
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
    raw/XOR55/XORAA objects. This is not an ICU command path. The application-GP
    work-buffer root is `0xFEBF0B08`, not the old erroneous `0xFEBFEB08`.
  - pages 468–479 are objects 0–3; FEBEF468/478/488 contain their structured state.
  - `0x758A0/0x785D2` are NvM/DataFlash service machinery, not ICU derivation.
- Five formerly open semantics are closed in `docs/OPEN_SEMANTICS_RESOLUTION.md`:
  - `0xFEBEE81F` (`GP+0x301F`) snapshots the non-Dcm system-transition phase at
    `0xFEBEB1A4`; phase `0x11` blocks programming handoff.
  - application service groups 2/3/4 select primary `7A1->7A9`, functional
    `777->7A9`, and limited secondary `7A0->7A8` contexts; the last has SIDs
    `10/19/22/3E/AB`.
  - EIINT 292/293 are active ICU-S crypto-driver callback paths despite generic
    hardware-table `Reserved` labels.
  - pages 0–255 are currently unallocated with erased-compatible undefined
    readback; prior use is indeterminable.
  - `data/checkpoint_payload_map.csv` contains bounded structural names/layouts;
    do not invent unavailable OEM field names.
- The complete 32 KiB map is in `docs/DATAFLASH_LAYOUT.md` and is checked by
  `tests/verify_dataflash_layout.py` plus `tests/verify_dataflash_semantics.py`:
  - 122 physical records occupy pages 256–479; pages 0–255 are outside both
    configured persistent-object classes, and erased DataFlash readback is undefined.
  - the owner table at `0x2B1B0` maps every persistent block 2–123: blocks 2–49
    are the 48-record triplicate bank, while blocks 50–123 are 74 checkpoint-ring
    records for 32 logical slots (24 enabled, 8 disabled).
  - checkpoint records store generation + data/padding + inverse generation;
    all 50 physically valid enabled records have a matching complement.
  - pages 432–479 are the full 16-object SecOC triplicate bank.
  - object 15 is len32/base block41/RAM `0xFEBF02E8`; its key field maps raw
    `0xFF206E14`, XOR55 `0xFF206D14`, XORAA `0xFF206C14`, RAM `0xFEBF02F8`.
  - related-variant field evidence CMAC-verifies the SecOC key at `0xFF206E14`.
    This exact dump has three invalid object-15 copies and no verified key.
  - DIDs `0x201/0x202/0x203` are volatile bootloader inputs, not DataFlash-backed.
  - `0x4EAD8` rejects accesses overlapping pages 480–511 and optional-object
    pages 432–443. Hardware documentation identifies a final 1/2 KiB ICU-S
    reservation, but the dumped 00/FF tail does not reveal its contents or locate
    this SecOC key there.
  - the dealer/FEBEF capture design remains wrong. A generic `0x72F58` hook must
    filter blocks 41/45/49 and observe completion to see object 15 on a provisioned
    variant; the call itself is not key-set.
- The application SecOC receive profile is in `docs/SECOC_APPLICATION_CHAIN.md`
  and checked by `tests/verify_secoc_application.py`:
  - six records bind `0x0F/0x2E4/0x131/0x132/0x90/0xD7` to exact RX PDU routes;
    `0x344` has no receive filter or SecOC record in this image.
  - ordinary classic frames authenticate `DataID_be16 || payload4 || freshness48`;
    the trailer is four freshness bits followed by the first 28 CMAC bits.
  - full freshness packs trip16/reset20/message8/reset-low2 plus two zero bits.
  - CMAC verify resolves CryptoIf handle 0, uses ICU-S slot 4, and has no
    object-15 RAM consumer.
  - this calibration's slot-4 known-answer vector equals CMAC of 16 zero bytes
    under `FF*16`; together with invalid objects 12–15 this strongly indicates an
    unprovisioned/default key state. A provisioned unit must be tested dynamically.
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
- The remaining bootloader services/routines are complete in
  `docs/BOOTLOADER_DIAGNOSTICS.md` and checked by
  `tests/verify_bootloader_diagnostics.py`:
  - `0x10` queues default/programming/extended transitions; default-to-programming
    and programming-to-extended return NRC `0x7E`;
  - `0x11` accepts hardReset only in unlocked programming session and coordinates
    reset with response confirmation;
  - functional-only `28 01 01` and `85 02` only acknowledge—the stored request
    bytes have no consumer beyond their response builders;
  - `3E 00/80` is accepted in sessions 1/2/3 but has no service-local S3 timer;
  - `0x10F1` aliases RAM verifier `0x10F0`; `0x10F2` verifies CodeFlash and
    programs marker `5A A5 A5 5A`; `0x10F3` arms operation-bit-5 read-back compare.
- The separate application diagnostic stack is documented in
  `docs/APPLICATION_DIAGNOSTICS.md` and checked by
  `tests/verify_application_diagnostics.py`:
  - the 17-entry primary application service table is at `0x25E30` and contains
    `10/11/14/19/22/23/27/28/2E/31/34/36/37/3E/85/AB/BA`;
  - `data/application_diagnostic_map.csv` (from
    `tools/generate_application_diagnostic_map.py`) records per-SID routing,
    session policy, callbacks/subfunction tables, and evidence status for all 17;
  - `data/tss3_eps_variant_matrix.csv` consolidates Sienna/Corolla and other
    TSS 3 EPS variants into a structured comparison (populated rows are
    evidence-graded; unobserved fields are `unknown`, not fabricated);
  - application DID table `0x2941C` has 242 read records; write-DID table
    `0x26AEC` has 19; routine-ID table `0x25768` has 32 start/result pairs;
  - application DID records at `0x2A30C` expose real `F181`, `F186`, and `F18C`
    responses through callbacks `0x4E8E4`/`0x4E90A`/`0x4E918`;
  - application session callbacks `0x93FF6`/`0x94006`/`0x94016` share the
    asynchronous state machine at `0x93F3C`; PROGRAMMING is allowed only from
    current session 2/3, rejects raw speed above `0x0180` with NRC `0x88`, and
    requires status != `0x11`, scaled supply >= `0x0A00`, and a clear handoff flag;
  - SIDs `14/23/31/34/36/37/BA` have null service-table callbacks and
    `byte[9]==0`; the generated Dcm DSP start-phase is **globally disabled**
    (flag `@0x25DCC=0x00`); these services receive only simple positive
    responses (`SID|0x40` + request echo) via `0x8F6FA` — no hidden DSP handler;
  - application SecurityAccess level 1 (`01/02`, programming) is a compiled
    stub (`0x94E0E`/`0x94E22`: `return 1`); only level 2 (`03/04`, extended) is
    functional. Seed generated via crypto hardware (`0x8C65A`) and stored at
    `FEBF495A`. Key verification (`0x8C82A`) uses a two-stage AES-128-ECB
    pipeline identical in structure to bootloader `0x704C`: stage 1 decrypts
    `FEBF497A` under the 16-byte secret at CodeFlash `0x20840` via
    `0x865D4`→`0x853EE` (AES key expansion + single-block decrypt), stage 2
    encrypts the seed under the intermediate key via `0x865D4`→`0x852B0`
    (single-block encrypt). All AES tables (S-box `0x8FF1`, inverse S-box
    `0x25628`, Rcon `0x23615`, Te tables `0x23628`, Td tables `0x24628`) are
    NIST FIPS-197 standard. The `FEBF497A` data-record is the 16 bytes at
    `PDU_buffer[2:18]` — tester-controlled via `27 03` + 16 padding bytes, or
    stale/zero for a bare `27 03`. The Dcm performs no request-length check
    on the seed path (the config value `0x10` at `0x26360` validates response
    space). This makes the keygen fully deterministic and attacker-controlled.
    Attempt counter and delay are RAM-only. Unlock state is a 2-dword bitmask
    set by `0x900FC`→`0x9075A`;
    **the level-2 unlock gates no diagnostic functionality in this Sienna
    calibration** — all 17 services have `sec_count=0` at the Dcm dispatch
    layer; all 242 readable DIDs have no security level > 0 (strict scan of
    the RDBI policy table); all 19 writable DIDs have `level_count=0` in the
    WDBI policy table at `0x26420`; all 13 `0xAB` RID callbacks contain zero
    references to crypto/NvM/SecOC machinery (checked by
    `verify_security_consumers.py` and `verify_ab_rid_callbacks.py`); the
    security-state machinery (`0x8FDCA`/`0x92FEE`/`0x900FC`) is wired up and
    exercised but the policy tables are empty. The Corolla (`8965F1208000`)
    is a different calibration and may populate these fields — the algorithm,
    secret location, and consumer machinery are the template to check against
    when its firmware becomes available;
  - proprietary `0xAB` is an asynchronous control service: subfn `01`=start
    (0 bytes), `02`=reset (2 bytes, clears state block at `FEBF45D0`, mode
    `0x300`), `03`=configure (4 bytes, two `u16` params). Worker `0x96918`
    copies 28-byte context to `FEBE5E0C`. RID lookup `0x8D3CC` scans 13 entries
    (RIDs `0x0204..0x2014`), all with non-zero start/result callbacks. Response
    includes vendor byte from `FEBF493C`. Secondary `0x7A0→0x7A8` endpoint uses
    same handlers; its record fields at `0x26104`/`0x26110` are CAN routing IDs
    (`0x7A1`/`0x7A0`), not code pointers. **The 13 RID callbacks contain zero
    references** to AES/CMAC, ICU-S, NvM ReadBlock/WriteBlock, or SecOC key
    material (`FEBF02E8`/`FF206E14`). They are vehicle-speed gates (RID
    `0x0204`/`0x2002`/`0x2006`/`0x2007`/`0x2008`), handoff/session-state
    writers (RID `0x2001`/`0x2013`/`0x2014`), and state-block configure
    operations (RID `0x2005`/`0x2009`/`0x200D`/`0x2010`). The state machine
    at `0x8CF84` manages byte-stream processing through `FUN_0004f8ba` with
    no crypto or provisioning calls. `0xAB` is not a SecOC provisioning or
    key-update interface in this calibration. 'Calibration/flash control'
    remains a hypothesis, not proven;
  - instruction-proved absolute RAM roots: ControlDTC store `FEBF45A8`, ReadDTC
    request mirrors `FEBF3BFC/3F24/4248/457C`, AB mirrors `FEBF48EC` and
    `FEBF48EC+0x50` (`FEBF493C`); buffers stay opaque;
  - the `0x08000200/201` callees are compiled no-op stubs; successful PROGRAMMING
    queues system event 9, shutdown mode `0x900`, and hardware reset while UDS
    remains pending. The first `10 02` in extraction tooling is therefore an
    application reset/handoff, not a call to bootloader handler `0x614A`;
  - bootloader handler `0x614A` also queues valid transitions for task `0x6244`;
    `0x4776` reserves transient main-loop state cleared by `0x479A` and is not a
    per-boot one-shot latch;
  - bootloader functional diagnostics use CAN `0x777`, not generic OBD `0x7DF`;
  - matching application tables in a related EPS are strong software-family
    evidence, but do not prove its MCU, bootloader payload path, or an external
    gateway explanation for silence.
- The boot validity gate, flash lifecycle, and object-15 reachability proof are
  documented in `docs/BOOT_VALIDITY_AND_FLASH_LIFECYCLE.md` and checked by
  `tests/verify_boot_trust.py`:
  - `boot_application_handoff` at `0x13B0` calls four setup functions in fixed
    order, then `boot_validity_check` at `0x119E`; success calls `*(0xFFDB8)`
    = `0x20880`, failure enters the non-returning failure main loop at `0x1398`;
  - the validity gate has two retry-bounded phases (ceiling 3): CRC descriptor
    verification for both CodeFlash regions + flash status check at `0x115A`,
    then validity-marker comparison at `0x6C5A` (`!= 0x5AA5A55A`);
  - three region descriptors at `0x8E00` define the checked ranges: region 0
    `0x10000..0x17DFF` (marker `0x17E00`), region 1 `0x18000..0xFFDFF` (marker
    `0xFFE00`), region 2 RAM payload (null marker); both CodeFlash markers
    currently hold `0x5AA5A55A`;
  - the failure loop at `0x137A` keeps `flash_operation_task` (`0x4428`) and CRC
    verification alive for diagnostic re-flash; `program_region_validity_marker`
    (`0x5280`) writes the `0x5AA5A55A` marker consumed by the next-reset gate;
  - `tools/generate_object15_reachability.py` produces an exhaustive caller
    census: index `0x10F` (SecOC triplicate object 15) has **no static producer**
    in this calibration — 27 direct + 19 wrapper callsites, two dynamic-index
    maps, and no AB/BA call edge; the observed namespace-`0x100` indices are
    `0x100..0x103`/`0x105`/`0x106`.
- The broader execution map is in `docs/FIRMWARE_ARCHITECTURE.md` and checked by
  `tests/verify_architecture.py`:
  - application vector/executable base `0x20000`; entry pointer `0xFFDB8 -> 0x20880`;
  - application `EBASE=0x20000`, `INTBP=0x20200`, and foreground loop `0x64FCC`;
  - the foreground loop polls TAUJ0 CH3 `EIRF136`; CH0..2 use EIINT 133..135;
  - application RSCAN CAN1 uses EIINT 187/188 and 51 acceptance rules at `0x231A0`;
  - `0x2E4`, `0x0F`, and `0x131` are explicit RX routes; `0x344` is not in the
    application RX acceptance table and must not be projected onto it.
- The complete application receive map is in `docs/APPLICATION_RECEIVE_MAP.md`
  and checked by `tests/verify_application_receive.py` plus
  `AssertApplicationReceiveMap.java` in `make verify-processor`:
  - 47 normal Rx I-PDUs and 242 COM signals 58..299; CSV from
    `tools/generate_application_rx_map.py` driven by
    `data/application_rx_signal_evidence.csv`;
  - six SecOC envelopes stay inside the 47 (IDs from `0x25970`); diagnostic
    `7A1/777/7A0/7F7` stay out;
  - 145 signals recovered with per-unpacker body hashes + immediates/dest checks;
    97 configured-unresolved with bounds;
  - CAN `0x344` remains absent from acceptance, descriptors, and the CSV.

The prior "secrets are unreferenced / separate bootloader image" conclusion was
an artifact of the wrong flat import and is **false**. The scripts that produced
it live in `legacy/flat-import/` — do not use them for current results.

## Scripts and verification

- `ghidra/scripts/import/` contains the split-image import helper and the
  P1M-E device profile (`ApplyP1MDeviceProfile.java`, `ApplyP1MSfrTypes.java`,
  `ApplyRamTypes.java`).
- `ghidra/scripts/seed/` contains all function/table seeds missed by analysis.
- `ghidra/scripts/annotate/` contains the durable labels/comments for completed
  work, plus `RecoverVectorHandlers.java` for INTBP/EBASE/`__interrupt`,
  `ApplyCallingConventions.java` for explicit `__stdcall` on non-ISR functions,
  and `RecoverSwitchTables.java` for in-function RH850 `switch` jump tables.
- `ghidra/scripts/investigate/` contains operand/reference search helpers.
- `ghidra/scripts/verify/` contains asserting processor/project gates used by
  `make verify-processor`.
- `make verify` runs twenty self-contained suites through UV; it must not require
  sibling repositories or Ghidra.
- `make verify-sleigh` compiles the vendored processor module into an isolated
  extension under `build/ghidra-home/` from a disposable source copy (does not
  generate in the vendored tree or mutate `$GHIDRA_HOME`).
- `make verify-processor` runs synthetic RH850 fixtures and, when
  `build/project/` exists, read-only asserting audits.
- `make verify-ghidra` runs firmware + SLEIGH + processor gates together.
- `make verify-external EXTERNAL_REPOS_DIR=...` checks optional public checkouts
  against `external-references.lock.json`.
- `tools/generate_dataflash_layout.py` regenerates `data/dataflash_nvm_records.csv`;
  run `make generate-dataflash`.
- `legacy/flat-import/` is historical only and must not be used.

## Rebuilding the project from scratch

Run `make rebuild-project` for a non-destructive rebuild under `build/project/`.
`tools/rebuild_project.sh` installs the isolated processor extension, imports
both regions (with the P1M-E device profile), runs every seed and annotation
in four staged durable headless analysis commits (including vector and
switch-table recovery), then a separate `-noanalysis` calling-convention
finalizer, cleanly stops the stats daemon, writes `processor_manifest.json`,
and verifies project statistics. Do not collapse the four analysis stages:
seed timing changes Ghidra's recovered graph. The finalizer exists because
two ordinary bodies (`0x3b0be`, `0x6f0d0`) appear only after the annotate-stage
reopen and would otherwise stay on `unknown`. To promote a finished rebuild
into the committed `project/` snapshot, run `make snapshot-project` (never
point rebuild directly at `project/`).

## Tooling notes

- Ghidra 12.1.2 at `/opt/homebrew/opt/ghidra/libexec`; the RH850 language
  `v850e3:LE:32:default` is the **vendored in-tree fork** at
  `ghidra/ghidra_v850/` (forked from esaulenka/ghidra_v850 at commit
  `14c1b5be32b8ec741ee626c8bca9885c58f7a473`; see
  `ghidra/ghidra_v850/PROVENANCE.json`). `tools/install_v850_extension.sh`
  copies the module to `build/processor-extension-src/`, compiles there with
  `sleigh`, and installs into
  `build/ghidra-home/.../Extensions/Renesas_v850/` via `-Duser.home`, not into
  `$GHIDRA_HOME/Ghidra/Extensions`. The in-tree `v850.cspec` models the
  RH850/G3 calling convention (r6-r9 args, r10 return, callee-saved r20-r29,
  lp link register, `__interrupt` proto); `ApplyCallingConventions` pins
  `__stdcall` onto recovered non-ISR functions so they are not left on
  Ghidra's anonymous `unknown`. Processor audits are documented in
  `docs/PLUGIN_AUDIT.md`.
- `ghidra` CLI project resolution: `GHIDRA_PROJECT_DIR` env, config
  `ghidra_project_dir`, `--projects-dir`, else `~/Library/Caches/ghidra-cli/projects`.
  Headless rebuild/verify always use the isolated extension. Interactive
  `ghidra` CLI analysis that needs the vendored language should source
  `build/ghidra-processor.env` (written by the installer) or set
  `JAVA_TOOL_OPTIONS=-Duser.home=.../build/ghidra-home` accordingly.
- CI (`.github/workflows/ci.yml`) always runs `make verify`. Processor-path
  changes run SLEIGH, synthetic fixtures, and committed-project audits on
  macOS with pinned Ghidra 12.1.2 / ghidra CLI 0.2.1. Processor, script, and
  snapshot changes—as well as `main`, manual, and nightly runs—execute the full
  four analysis-stage rebuild (plus convention finalizer) and project invariants,
  and upload normalized audit artifacts.

## Final safe workflow

1. `make verify` — firmware evidence, no Ghidra.
2. `make verify-sleigh` — compile + isolated install + fingerprint.
3. `make work-project` (or `make rebuild-project` after language/script changes).
4. `make verify-processor` — fixtures + asserting audits on `build/project/`.
5. Interactive work only against `$PWD/build/project` with an absolute
   `--projects-dir`; always `ghidra ... stop` before copying or committing.
6. Promote only with `make snapshot-project` (stats + fingerprint + stopped
   daemon). Never daemon-open committed `project/`.
