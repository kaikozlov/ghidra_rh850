# Multi-agent security audit — 2026-08-21

Full-chain key/authentication vulnerability sweep across the Sienna
`8965B4512000` firmware and the pinned external targets (Techstream V18 tree,
Renesas Flash Programmer install). This journal preserves scope, method,
consolidated results, and the claims that were refuted along the way. Current
state lives in the canonical reports and `status/FINDINGS.md`; this document
does not override them.

## Method

Orchestrated fan-out of subagents with structured outputs, followed by
adversarial verification and an orchestrator-side raw-byte recheck:

1. **Recon (8 scouts)** — one per area: bootloader transition, payload gate,
   application diagnostics auth, SecOC/ICU-S chain, key-material census,
   Techstream crypto, Renesas RFP, plus a blind fresh-eyes corpus sweep.
2. **Deep-dive (8 analysts)** — targeted questions per open gap, working from
   `tools/pseudo` output, `build/pseudocode/*.c`, and raw split-image bytes.
3. **Adversarial verify (5 skeptics)** — instructed to refute the five most
   load-bearing new claim clusters from primary evidence; several corrections
   resulted (below).
4. **Completeness critic** — reconciled coverage against
   `status/OPEN_QUESTIONS.md`.

Address convention used throughout: in the split
`firmware/RH850_P1M-E_CodeFlash.bin`, **VA == file offset** (verified: AES
S-box at `0x8FF1`, UDS service table at `0x8E54`, secrets at `0xBFD8/0xBFE8`).
The `-0x8000` rule applies only to the original combined dump layout
(DataFlash prefix), as encoded in `tests/verify_findings.py`.

## Consolidated attack-path ranking

| # | Path | Class | Status |
|---|---|---|---|
| 1 | Boot SA algebra defeated offline (`SEED_KEY_SECRET @0xBFE8`; `expected = AES-ENC(AES-DEC(secret, record), seed)`) | extract | verified (`verify_findings.py` §7; Willem sample reproduced); canonical SEC-BOOT-002/003 |
| 2 | Payload forgery offline (`PAYLOAD_BUILD_SECRET @0xBFD8` → derived AES-CBC+CMAC key) | extract | verified; public fixtures already accepted with zero DID inputs (SECOC-062) |
| 3 | RAM-only ephemeral SecOC bridge (authenticated 4 KiB exec + MEM-SAFE-001 substitution → resident scheduler) | bypass | statically end-to-end constructible; bench validation outstanding |
| 4 | Peer-ECU RAM-mirror slot-4 key extraction (704-byte table `0xFEBE6E34` class) | extract | route verified on siblings; requires acquired second ECU |
| 5 | Command-5 signing proxy via dormant RID `0x100F` harness | bypass | software chain verified; slot-4 generation permission is the single hardware unknown |
| 6 | Persistent Gate-2 patch `0x8E6C6 e0d1→e001` | bypass | known (SECOC-043/045); externally corroborated; causal bench proof pending |
| 7 | Native serial programming (RV40F) as independent flash channel | bypass | host side fully recovered; gated on boot-pin wiring, target authentication state, and P1M-E mask-ROM support; all-FF ID is only a transfer hypothesis |
| 8 | MAC28 online guessing (28-bit tag, no effective lockout) | bypass | oracle-grade only (~2^27 mean per frame); not practical for steering |
| 9 | Kmaster derivation for SHE rekey | derive | dead end statically: CPU is a blob-forwarder; OEM master secret exists in no analyzed binary |

## Results by area (new or sharpened this pass)

### Bootloader transition and degraded runtime

- New **SEC-BOOT-011** (canonical §4.1 of
  `architecture/boot-validity-and-flash-lifecycle.md`): failed-validity and
  normal programming converge on the same long-lived bootloader/DCM runtime,
  but a later review corrected their entry-state equivalence. Application
  programming jumps live `FUN_00064EC8 → 0x9F00 → 0x148E(@0x31914) → 0x1398`
  without CRC failure or reset. `FUN_000069D2` arms diagnostics for retained
  word0 ∈ {`0x00`,`0xFF`}; `FUN_00005086` initializes session 1. Only word0
  `0x00` runs `0x6504→0x5148→0x630C` and injects the retained synthetic
  `10 02`. Failed-validity word0 `0xFF` remains in default session, where a
  direct `10 02` receives NRC `0x7E` (CORR-089).
- Refuted again with writer censuses: no erase/write/RAM-exec path in the
  degraded state skips SecurityAccess level 2; reset windows cannot leave UDS
  privileged (sanitize ordering precedes IRQ enable).

### Payload gate / RAM exec

- MEM-SAFE-001 re-derived including the two-stage landing handoff
  (`0x4DF2`: op 1 → op 2) that commits raw bytes post-auth.
- XCP standalone bypass re-disproved: the `0xFEBF7C00..FEBFFBFF` window has no
  control-transfer consumer and excludes all SecOC state cells; its value is
  read observer + mailbox only.

### SecOC / ICU-S

- Command-5 engine `0x89630` caller chain re-confirmed unique
  (`0x68B42→0x88350→0x87CCC→0x87C70`); RID `0x100F` arms bank 1 with no
  SecurityAccess requirement (default session suffices).
- New **SECOC-068**, corrected by follow-up review (CORR-090): ordinary
  wrong-MAC handling uses global counter `FEBE550E` against record `+0x10`
  (0 sync / 1 ordinary ×5), but this is a retry budget for the **current queued
  PDU**. Fresh-PDU admission in `0x8E166` resets both retry counters, so
  distinct guesses remain unthrottled. Record `+0x2E=2` bounds the separate
  `FEBE550C` path when CryptoIf submit returns result 2. Callback routing is
  also split: ordinary mismatch uses `6911C`; `69116` is freshness-result-0x24;
  cap-exceeded generic failure additionally uses per-profile `69182` and global
  `691EA`. Regression coverage now locks the reset and routing distinction.
- Freshness facts reconfirmed against primary evidence: RAM-only freshness
  zeroed each boot (`secoc_rx_init` chain), no forward-delta clamp on sync
  acceptance (wrap floor from config byte at `0x2596C`), CMAC truncation at
  `secoc_rx_split_freshness_and_tag 0x8E1A8` + descriptor build `0x87ED0`.
- Command-8/Kmaster negatives reconfirmed (blob-forwarder `0x96354`; no
  Kmaster/UID/KDF anywhere in image, DataFlash, Techstream, or RFP).

### External targets

- Techstream: five host-side AES constants confirmed at pinned IT3ACNK offsets
  (`0x834C/0x8324/0x82FC/0x8310/0x8020`); four consumed by IT3ACNK exports,
  the fifth (`bCVa…`) bounded-presence there — matching the existing CORR
  entry. New precision documented in `tooling/techstream.md`: NeoNK consumes
  the full 32-character literal as a **strlen-keyed AES-256-ECB** key (raw
  literal + NUL verified at NeoNK file offset `0x3A7D4`).
- RFP/RV40F: framing, auth model, 52-command census, unencrypted writes, no
  SHE-provisioning commands, and no P1M-E device record all survived
  refutation attempts. Pre-capture recon steps appended to the serial-boot
  entry in `status/OPEN_QUESTIONS.md` (driver mode-entry pattern extraction,
  read-only fingerprint order, and an explicitly hypothesis-grade all-FF
  `CheckIDAuth` first probe; generic RFP examples do not prove P1M-E blank-ID
  state — CORR-092).
- CUW grammar cross-check reconfirmed: unified prepare's `27 01 ‖ ECUAuthKey[16]`
  (length exactly `0x12`) is the same tester-chosen record our SA algebra
  consumes; OEM flashing proves the offline path end-to-end once the
  calibration package supplies `ServiceAuthKey` — unnecessary given both
  extracted roots.

## Claims refuted during this audit (not persisted to canon)

- **"Doubly dead" slot-4 KAT anomaly** — refuted by direct byte read:
  config `@0x21604` begins `01 00 00 00 04 …`, so `icus_cmac_verify_prepare`
  validation (`*config != 1`) passes. The gate byte `0x30EF3 == 0x00`
  (SECOC-004) remains the sole kill switch. A regression check was added to
  `verify_findings.py` §8.
- **Bank-1 latch threshold "13 stable frames"** — wrong; the shared constant
  `CodeFlash[0x30FBB]` is `0x03` (bank 0's threshold was already canonical;
  bank 1 shares it).
- **Harness mode-record routing ("record 0 → command-1/3 adapter")** — could
  not be reconciled against the dispatch words at `0x27F78/0x27F98/0x28000`;
  dropped rather than documented. The authoritative call shape remains
  SECOC-041 / application-chain.md §crypto-test.
- **Kmaster/Techstream plaintext-MACK4 leakage** — no such material exists in
  any analyzed binary (extends TMS-012/TMS-014 negatives to the RFP tree).
- **XCP window as standalone SecOC neutralizer**, **unauthenticated
  failure-loop mutation**, **reset-window privilege retention** — all
  re-disproved (consistent with prior canon).

## Persisted deltas

- `SEC-BOOT-011` — FINDINGS row + canonical §4.1 +
  `exploit/findings_coverage.json` disposition.
- `SECOC-068` — FINDINGS row + application-chain.md §5.7 qualifier +
  `verify_findings.py` §8 byte checks. Follow-up review corrected the counters
  to per-queued-PDU / CryptoIf-submit retry budgets and split the callback
  routes (CORR-090).
- `docs/tooling/techstream.md` — bCVa AES-256 strlen-keyed live-use paragraph;
  follow-up review corrected the padding wording and added raw NeoNK regression
  anchors (CORR-091).
- `docs/status/OPEN_QUESTIONS.md` — serial-boot pre-capture steps appended;
  all-FF ID probing remains a P1M-E transfer hypothesis (CORR-092).
- This journal + history index entries.

Everything else the audit surfaced was already canonical (SEC-BOOT-001..010,
MEM-SAFE-001..004, SECOC-002/004/006..011/040/043/045/046/060..063,
TMS-003/004/008/011/012/014/016/019, COM-005/007, RFP-001..008); this pass
independently re-verified those claims under adversarial instructions and
found no contradictions.
