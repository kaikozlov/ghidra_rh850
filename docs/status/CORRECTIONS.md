# Corrections

Superseded conclusions and why. Each entry names the wrong claim, the correct
one, and the canonical report that now owns the truth. These are retained so
the mistakes are not re-made.

## Evidence-grade: disproved

### CORR-001 — Flat firmware import

- **Wrong:** `RH850_P1M-E_Firmware.bin` is one flat block at VA `0x0`.
- **Right:** It is two regions — DataFlash (file `0x0–0x7FFF` →
  `0xFF200000`) followed by CodeFlash (file `0x8000–0x107FFF` → `0x0`).
  CodeFlash VA = file offset − `0x8000`.
- **Consequence of the error:** all CodeFlash addresses shifted `+0x8000`;
  only ~2,000 functions found; the false conclusion that the two bootloader
  secrets were unreferenced and lived in a separate image.
- **Canonical:** root `README.md` §"File layout";
  [../storage/dataflash.md](../storage/dataflash.md). The invalid analysis is
  preserved in `legacy/flat-import/` (do not use).

### CORR-002 — SecOC runtime-key command path

- **Wrong:** `0x65CD8 → 0x66E48 → 0x67590 → 0x72F58` is a SecOC runtime-key
  lifecycle (CSM key-set / MAC generation / ICU derivation).
- **Right:** `0x72F58`/`0x72F84` are AUTOSAR NvM `ReadBlock`/`WriteBlock`;
  `0x67590/0x67608/0x67C34` generically restore, persist, and reconcile
  raw/XOR55/XORAA objects; `0x758A0/0x785D2` are NvM/DataFlash service
  machinery. Not a key lifecycle at all.
- **Canonical:** [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md);
  `tests/verify_secoc_nvm.py`.

### CORR-003 — Application GP work-buffer root

- **Wrong:** application-GP work-buffer root `0xFEBFEB08`.
- **Right:** `0xFEBF0B08`.
- **Canonical:** [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

### CORR-004 — System-transition phase snapshot address

- **Wrong:** `GP+0x301F` evaluated using the boot GP.
- **Right:** `0xFEBEE81F` (application GP), snapshot of the non-Dcm
  system-transition phase at `0xFEBEB1A4`; phase `0x11` blocks programming
  handoff.
- **Canonical:** [../diagnostics/application.md](../diagnostics/application.md).

### CORR-005 — Pages 468–479 as ICU key-slot pages / raw keys

- **Wrong:** pages 468–479 are 12 ICU key-slot pages holding raw AES keys or
  ICU derivation metadata.
- **Right:** pages 432–479 are the full 16-object SecOC raw/XOR55/XORAA
  triplicate bank; pages 468–479 decode to four structured state objects.
- **Canonical:** [../storage/dataflash.md](../storage/dataflash.md);
  [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

### CORR-006 — Dealer/FEBEF object-0 key-set capture design

- **Wrong:** hooking `0x72F58` alone captures a dealer key-set of object 0.
- **Right:** `0x72F58` is generic NvM `ReadBlock`. A capture must filter blocks
  41/45/49 and observe asynchronous completion on a provisioned variant; the
  call itself is not key-set.
- **Canonical:** [../security/secoc/key-storage-and-lifecycle.md](../security/secoc/key-storage-and-lifecycle.md).

### CORR-007 — Large-function motor-control classifications

- **Wrong:** seven of the eight large functions in the motor cluster were
  annotated as motor-control state machines.
- **Right:** structural re-classification (several are RAM-init / glue); see
  the per-domain distribution. Commit `22279b5`.
- **Canonical:** [../architecture/firmware-architecture.md](../architecture/firmware-architecture.md) §9
  and the per-domain files.

### CORR-008 — Bootloader DID `F181` returns VIN / part number / `8965B4512000`

- **Wrong:** bootloader `F181` exposes VIN, part number, `BOOT INFO AREA`, or
  `8965B4512000`.
- **Right:** bootloader `F181` synthesizes `02 ‖ 32*0x21` — a placeholder. The
  real software ID comes from the *application* `F181` callback.
- **Canonical:** [../diagnostics/bootloader-dids.md](../diagnostics/bootloader-dids.md).

### CORR-009 — Slot-4 `FF*16` KAT proves an erased/default live key

- **Wrong:** the embedded `B290FA2E…E540` vector is an active slot-4
  known-answer test and, together with invalid objects 12–15, strongly
  indicates an erased/default live SecOC key.
- **Right:** both functions that reference the vector gate their crypto bodies
  on fixed `CodeFlash[0x30EF3] == 0x5A`. This calibration stores `0x00`, so
  both branch directly to report-only tails and never submit command 7. The
  `FF*16` vector is latent dead data and places no constraint on protected
  slot 4.
- **Physical check:** no production application path has been identified that
  reloads slot 4 on every boot. An unconditional `FF*16` KAT would therefore
  be incompatible with a personalized nonvolatile slot; compiling it out is
  consistent with either personalized or unprovisioned hardware state.
- **Canonical:** [../security/secoc/application-chain.md](../security/secoc/application-chain.md)
  §"Compiled-out slot-4 known-answer check"; `tests/verify_secoc_application.py`.
