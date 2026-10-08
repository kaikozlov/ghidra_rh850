# Application-to-HSM command surface: exhaustive cross-target census

Scope owner for the **complete application↔secure-hardware command surface** across
every retained firmware image: the four first-class TSS3 EPS dumps, the legacy
Sienna reference, and the yc Venza airbag specimen. Per-target SecOC behavior,
key lifecycle, and exploit implications keep their existing owners
([secoc/](secoc/README.md), [../variants/README.md](../variants/README.md),
[yc-venza-airbag-reprogramming-2026-09-14.md](../variants/yc-venza-airbag-reprogramming-2026-09-14.md));
this report owns the census itself: which command words/opcodes the MainPE
application can issue, through which driver layers, from which application
features, and how the surfaces differ between the ICU-S EPS family and the
airbag's different secure subsystem.

## 1. Method

- EPS targets: instruction-level reference census against the registered Ghidra
  projects (`tools/g` / `tools/gtarget ... x-ref to 0xFFC5D000`), constants read
  from live disassembly, caller chains closed through the decompiler corpora
  (`tools/pseudo --target ...`) plus ROM configuration tables read directly from
  the CodeFlash images. Two corpus-only caller-chain walks were delegated and
  are marked corpus-static where a chain closes only through data-space
  pointers.
- Venza airbag: now the registered target `venza-8917048E30` (CodeFlash plus
  the `boot.bin` extended-user image at `0x01000000`; no DataFlash specimen
  exists; no P1M-E SFR map is applied — different RH850 type). The census was
  originally produced against a disposable ad-hoc project seeded and
  linear-swept by `ghidra/scripts/investigate/CensusVenzaSecureService.java`
  with follow-ups `FollowUpVenzaCensus.java`, `FollowUpVenzaCensus2.java`, and
  `FollowUpVenzaOpcodes.java`; every new airbag fact below is byte-pinned in
  `tests/targets/venza/verify_yc_venza_airbag_reprogramming.py`
  (`yc_venza_airbag_reprogramming` selector).
- Sienna facts are the previously verified SECOC-015 census; this audit
  confirmed the Sienna driver cluster shape still matches and adds nothing
  new there.

## 2. EPS family: the ICU-S register ABI (all five EPS targets)

Transport: direct MMIO into the ICU-S register block `0xFFC5D000..0xFFC5D0FF`.
The command register is `ICUSCMD = 0xFFC5D000`, written as a bitfield
`{ CMD[7:0], reserved[15:8], KEY_SLOT[31:16] }` — selector-bearing commands are
literally `(key_selector << 16) | cmd`. Data blocks are pushed/pulled as 128-bit
FIFO writes (`0xFFC5D004` push ×4, `0xFFC5D008..` readback), status via
`0xFFC5D00C/014`, with driver state (tracked command, completion callbacks,
per-command staging) in `0xFEBF10xx..13xx` RAM guarded by bitwise-complement
copies.

Driver layering (identical architecture in all five EPS images, target-local
addresses):

```text
issuer (writes ICUSCMD)  <-  command wrapper (installs continuation/callback
into channel slot, sets state 0xB4)  <-  channel submit/stager pair  <-
ROM service-registry record (sync/step pointers, type-1 key-selector config,
KAT function)  <-  application feature (SecOC worker, crypto-test bank, RID)
```

Completion is asynchronous: a Crypto-main/OS stepper drives the channel state
machine (`0xC3/0xD2/0xB4` states) and delivers results through installed
callbacks; the issuers also poll `0x9c4` iterations in synchronous wrappers.

## 3. EPS command-word census (register-store sites)

All five EPS targets share the same seven-family surface; Sienna additionally
has two literal command sites absent from the four TSS3 builds:

| Command word | Operation | camry F33 | crown F30 | corolla F12 | corolla H12 | sienna B4512 |
|---|---|---|---|---|---|---|
| `(sel<<16)\|1` / `(sel<<16)\|3` | AES-128 encrypt/decrypt, selector 0..14 | `0x8A63C` | `0x880DC` | `0x8394C` | `= F12` | `0x8954C` |
| `(sel<<16)\|5` | CMAC/AES-MAC generation, selector 0..14 | `0x8A720` | `0x881C0` | `0x83A30` | `= F12` | `0x89630` |
| `(sel<<16)\|7` | CMAC verification, selector 0..14 | `0x8A8E4` | `0x88384` | `0x83BF4` | `= F12` | `0x897F4` |
| `8` | SHE `CMD_LOAD_KEY` (M1/M2/M3 → M4/M5) | `0x8AA6A` | `0x8850A` | `0x83D7A` | `= F12` | `0x8997A` |
| `0x3F` (site A) | abort/reset (driver bring-up) | `0x8A26A` | `0x87D0A` | `0x8357A` | `= F12` | `0x8917A` |
| `0x3F` (site B) | abort/replace (channel teardown) | `0x8ACA8` | `0x88748` | `0x83FB8` | `= F12` | `0x89BB8` |
| `0x7000` / `0x7100` | diagnostic self-test/status (modes 1/2) | `0x8AE2E` | `0x888CE` | `0x8413E` | `= F12` | `0x89D3E` |
| `11` (`0xB`) | RNG/init family — **unreferenced generated stub (dead code)**: no stock caller, and no `jarl`/pointer/`mov32`/`ld24` reference anywhere in the image | absent | absent | absent | absent | `0x89A8A` |
| `0x22` | ID/lifecycle family — unreferenced generated stub (dead code), same audit | absent | absent | absent | absent | `0x89BB0` |

Completion handlers in the TSS3 builds still special-case tracked commands
`0xB`/`0x3F` (Camry `0x8AF10`), so the driver library understands command 11
even where no stock site issues it. Corolla F12/H12 issuer bodies are
byte-identical (all seven decompilations hash-equal) and share one build.

2026-10-08 dead-stub audit: both Sienna-only literal sites sit in store blocks
that no discovered function owns. Each registers the shared
`icus_command_finalize` (`0x89510`) callback exactly like the wired wrappers —
seven `mov32 0x89510` sites exist (cmds 1/3, 5, 7, 8, abort `FUN_00089bb8`,
plus these two) — but nothing in the 1 MiB image references the stub entries
(`0x89A4C`, `0x89B70`) by any encoding. They are library artifacts of the
generated driver's full SHE command set, not reachable operations: **no stock
runtime initializes the ICU-S PRNG on any target, and nothing anywhere issues
`CMD_RND` (`0xD`)**.

No EPS application site issues any other command word; commands 9/10 remain
reachable only through custom application-context code (the bounded
command-9/10 probe of SECOC-021), and no stock writer invokes command 13
(SECOC-015).

## 4. Application-layer owners (stock callers per command)

### Camry F33 `8965F3307000` (primary; live-project xrefs)

Four CryIf channel gateways `0x89440` (cmd5), `0x89646` (cmd7), `0x89838`
(AES), `0x89A26` (cmd8) resolve ROM channel tables at `0x27DA4/0x27DE8/
0x27E2C/0x27E50` (two, two, one, one configured jobs) to processor pointers.

| Command | Stock application owners |
|---|---|
| 5 | **Production SecOC TX signer**: `0x8F19A → 0x8FCCA → 0x89BC2 → 0x88B84 → 0x88D60 → 0x8A720`, authenticating the generated `0x030` status PDU (DataID `0x0030`, selector 4, profile at `0x2594x`). Also the crypto-test bank: RID `0x100F` action `0x8B872 → 0x6A0AE → 0x69C58 → 0x69BD8 → 0x89440`. |
| 7 | SecOC RX verify crypto step `0x8F676` (six RX profiles); startup KAT `0x6921E` (from ECU-init sequencer `0x666BC`); crypto-test bank `0x6918E`/`0x6933C`. |
| 1/3 | Crypto-test bank only (`0x69BD8 → 0x89838`; raw-AES control). No production AES user. |
| 8 | Crypto-test bank key-update sequencer `0x692D2 → 0x89A26`. **RID `0x1010` is null/null in the F33 19-RID table** — unlike Sienna, F33's stock cmd8 carrier is the bank, not a dedicated RID. |
| `0x7000/0x7100` | Startup crypto-driver init `0x666BC → 0x89D3C → 0x87EA0 → 0x8844E → 0x883E8 → 0x883CC → 0x8AE2E`. |
| `0x3F` | Driver-internal only. |

### Crown F30 `8965F3012000` (corpus-static)

| Command | Stock application owners |
|---|---|
| 5 | **SecOC TX MAC engine** `0x69810 → 0x8CA98 → … → 0x8D830 → 0x8D76A → 0x87662 → … → 0x881C0` (0x44-stride TX profiles at `0x25676+`, first DataID field `0x0030`); crypto-test bank KAT `0x68FD4` (fixed 16-byte vector). |
| 7 | SecOC RX verify worker `0x8D1E6` (0x50-stride profiles at `0x25586+`); **startup authenticated-data verify** `0x6861A → 0x6858A` (ROM-gated by `0x30A13=='Z'`); crypto-test KATs `0x6878A/0x68B7C → 0x68738`. |
| 1/3 | Crypto-test raw-AES KAT only (`0x68FD4 → 0x872D8`). Software KAT banks (`0x687FA`, `0x68BF0`) never touch ICU-S. |
| 8 | Crypto-test key-update banks `0x686CE → 0x874C6 → 0x859F2` (64-byte M1/M2/M3 staging; two 0x40-byte key banks at `0xFEBE4CF2/0xFEBE4D72`). |
| `0x7000/0x7100` | Startup: `startup_coordinator 0x62BEE → 0x65ABC → 0x877DC → 0x85940 → 0x85EEE → 0x85E88 → 0x85E6C → 0x888CE` (three sub-modes 0/1/2). |

No `0x100E/0x100F/0x1010` RID constants exist in Crown code; its test banks
dispatch through ROM routine tables (RID numbers not derivable from the
corpus).

### Corolla F12 `8965F1208000` / H12 `8965H1202000` (corpus-static + live xrefs)

| Command | Stock application owners |
|---|---|
| 5 | Channel exists (wrapper `0x82070 → 0x83A30`) and its sync API `0x820CC`/step `0x821D0` are registered in the ROM service registry (records at `0x27C9C/0x27CBC`); the SecOC engine block (`0x87000..0x8B000`) joins the service layer through runners (`0x881F8/0x88986/0x88FDA → 0x826xx..0x830xx`). A 0x44-stride TX descriptor table exists at `0x2581E+` with the same first-record shape as Crown (DataID field `0x0030`). **No diagnostic crypto-test RID bank exists** (no `0x100E/0x100F/0x1010` constants; all matches are bitmask tests) — the "never calls command 5" canary statement holds for text-level callers, not for the pointer-wired channel. |
| 7 | SecOC RX engine: three 0x50-stride RX profiles at `0x25750` (`0x00F/0x0D7/0x0B6` per ARCH-015), queue helper `0x87B72`, verify join via the same service runners; sync API `0x824DC` registered at `0x27CE0/0x27D00`. |
| 1/3, 8 | Channels registered with KAT functions (`0x27D24 → 0x81C98` AES, `0x27D48 → 0x814A8` cmd8) and a 16-byte KAT-vector table at `0x27C50..`; no application text caller recovered (ROM self-test module at `0x635xx` is the registered consumer). |
| `0x3F`, `0x7000/0x7100` | Startup: `0x5CAAC → 0x5F9D4 → 0x8304C → 0x811B0 → 0x8175E → 0x837DE/0x816DC` (three diagnostic modes 0/1/2 → `0x00/0x70/0x71`) — the **only** ICU-S reach of the stock corolla application outside the SecOC/service-runner wiring. |

### Sienna B4512000 (previously verified)

Six-RX-profile receive-only SecOC graph; cmd5 stock caller is only the
RID `0x100F` crypto-test bank; cmd8 via RID `0x1010` and the RID `0x100E`
CAN-assembled bank; AES cmd1/3 in the bank (raw-AES control); `0x7000/0x7100`
and literal 11/`0x22` are init/test-family sites. See
[key-recovery-assessment.md §1.1](secoc/key-recovery-assessment.md).

### Directionality finding

**Every TSS3-generation EPS (Camry/Crown/Corolla) wires command 5 into a
production SecOC transmit signer for a `DataID 0x0030`-field TX profile, while
the Sienna reference is receive-only.** This supersedes any blanket reading of
SECOC-008 (a Sienna-scoped statement) as a family-wide property, and it means
the practical signing surface on the current generation is stock hardware
behavior, not only a diagnostic oracle.

## 5. Venza airbag: the ICUMC secure-service ABI

Different subsystem and ABI: no `0xFFC5Dxxx` ICU-S access at all. The boundary
is a shared-RAM request ring plus an `0xFF1F...` system window (single-writer
census):

- `0xFF1F0014` (shared-RAM queue pointer): read by ring helper `0x89E60`,
  initialized/managed by `0x8A04E`;
- `0xFF1F0044` (service trigger): single writer `0x89F6E`;
- every request flows convergence `0xBD69E → 0x8A18A → 0x89E60` (four-entry
  ring) — `0x8A18A` has exactly one caller (`0xBD69E`).

The exhaustive census (test-pinned) finds **exactly five lower request
builders**, each a ROM-registered service (registry `0x1C7E4..`, sync-pointer
cells at `0x1C7FC/0x1C840/0x1C884/0x1C8A8/0x1C8C8`):

| Entry | Descriptor base | Opcode | Shape | Stock consumer |
|---|---|---|---|---|
| `0xBDC7A` | `FEFF02B8` | `0x12` | MAC generation (SecOC TX DataIDs `0x0326/0x0024`, selector 4) | SecOC TX worker `0xDE9F0 → 0xBCCF4` |
| `0xBDE88` | `FEFF0330` | `0x12` | MAC verification (four RX profiles incl. `0x00F/0x090/0x0D7/0x024`, selector 4) | SecOC RX worker `0xDE09E → 0xBCEFA` |
| `0xBD8C8` | `FEFF01E8` | **`0x10`** (new) | 16-byte-block-count input + logical key selector from a type-1 config; callback delivers a 4-byte result | unresolved (engine-table-mediated; see OQ) |
| `0xBE0CC` | `FEFF0398` | `0x31` | authenticated 64-byte key update (SHE `CMD_LOAD_KEY` M1/M2/M3 → M4/M5) | RID `0x1010` worker (`0x7C13E` staging, `0xB76D4` async, dispatcher `0xBD2EC`) |
| `0xBDA6E` | `FEFF0250` | **`0x04`** | mode-mapped query: caller byte `{1→0, 2→1, 4..14→n−2}` (SHE key-ID-like domain) | RID `0x1010` worker mode 2 (via `0xBD2EC` record 1) |

So the airbag application-facing secure-service opcode set is
`{0x04, 0x10, 0x12, 0x31}` — five registered services, two more than the
previously documented three (§5.5/§5.6 of the airbag report documented 0x12 and
0x31 plus an unnamed 0x04 mode; this census adds the 0x10 service, both
descriptor bases, and the registry). The opcodes stay numeric: they belong to
the Renesas security-hardware protocol, not to the SHE command numbering used
by the EPS ICU-S.

## 6. Cross-target comparison

| Property | Sienna B4512 | Camry F33 | Crown F30 | Corolla F12/H12 | Venza airbag |
|---|---|---|---|---|---|
| Secure HW | ICU-S (`0xFFC5D000` MMIO) | ICU-S | ICU-S | ICU-S | ICUMC-style queue (`0xFF1F` window + `FEFF` ring) |
| Command set | 1/3, 5, 7, 8, 0x3F×2, 0x7000/0x7100, **11**, **0x22** | 1/3, 5, 7, 8, 0x3F×2, 0x7000/0x7100 | same as F33 | same as F33 (both builds identical) | opcodes 0x04, 0x10, 0x12×2, 0x31 |
| Selector encoding | `(sel<<16)\|cmd` | same | same | same | selector byte copied from type-1 config into request descriptor |
| SecOC direction | RX-only (6 profiles) | RX (6) + **TX 0x030** | RX + **TX (0x44-stride, DataID 0x30 field)** | RX (3, incl. `0x00B6`) + TX table (0x44-stride, DataID 0x30 field) | **bidirectional**: 4 RX + 2 TX, both selector 4 |
| cmd5 stock carrier | RID `0x100F` test bank only | production TX signer + RID `0x100F` bank | production TX signer + test bank | service-runner wired (no diagnostic RID bank) | opcode `0x12` MAC-gen (production TX) |
| cmd8/`0x31` carrier | RID `0x1010` + RID `0x100E` | crypto-test bank (RID `0x1010` null) | crypto-test key-update banks | ROM-registered, self-test consumer | RID `0x1010` (stock, 64-byte M1/M2/M3) |
| RNG/ID services | literal 11 + `0x22` sites | none (ISR still handles 0xB) | none | none | `0x10` block service (semantics open) + `0x04` mode query |

Structural note: the ROM-service-registry pattern (records with sync/step
pointers + type-1 key-selector config + KAT function) appears in Camry
(`0x27DA4+`), Corolla (`0x27C8C+`), Crown (`0x27AE0+`), and the airbag
(`0x1C7E4+`) — one generated AUTOSAR-era Denso crypto-service layer across
both ABI families, with only the lowest adapter swapped (ICU-S register
writes vs secure-service queue).

## 7. ICU-S driver programming model (recovered from the Sienna driver)

The stock driver is a complete, self-contained ICUS programming reference —
including for command words the application never issues (the §3 dead stubs
are working templates). Everything below is Sienna-verified firmware-static;
the TSS3 builds use the same idiom at the §3 addresses.

### Register map (`0xFFC5D0xx`)

| Address | Name (corpus) | Recovered role |
|---|---|---|
| `0x00` | `ICUSCMD` | command word `(selector<<16)\|cmd`; the write **starts** the engine |
| `0x04` | `ICUSDAT` | input FIFO push port (one 32-bit word per write; blocks are 4 words) |
| `0x08` | `ICUSOUT` | output FIFO pop port (4 words per 128-bit result block) |
| `0x0C` | `ICUSSTS` | status; bit `BUSY` (checked as bit 0) |
| `0x10` | (error) | result/error code, low 12 bits; `0` = success (`icus_command_finalize`, decoder `0x89C8A` maps bits 0–11 to `idx+1\|0x1000`) |
| `0x14` | `ICUSSTS2` | interrupt/status 2; bits 0/1 gate issue and drive the stream callbacks in the poll engine |
| `0x18` | (init) | read `&1` at driver init (`icus_driver_initialize`) |
| `0x1C` | `ICUSPARAM` | command parameter word (commands 1/3 load block count here instead of via `ICUSDAT`) |
| `0x20` | (done) | bit 0 polled as completion latch (`FUN_00089F28`) |
| `0x24` | (irq ack) | written by finalize/fifo-steps/hw-init to acknowledge |
| `0x90–0xBC` | (staging) | 12-word block written by `FUN_00089C26` (self-test/key-update staging) |
| `0xC0` | | set `0x600` at hardware init |
| `0xE0` | `ICUSCTL` | block handshake: `1` = input block ready, `2` = output block consumed, `3` = command complete |
| `0xE4` | | set 1 at hardware init; also written by the poll engine |
| `0xF0–0xFC` | | cleared at init, reused by self-test |

### Driver state cells (`0xFEBF131C–136D`, pointer/complement guarded)

`131C/1320/1324` = stream callbacks (`icus_input_fifo_step` `0x89448`,
`icus_output_fifo_step` `0x894BE`, `icus_command_finalize` `0x89510`) with
complements at `1360/1364/1368`; `1328` = tracked command word; `132C/1334` =
total input/output block counts; `1330/1338` = block indices; `1340/1344` =
input/output pointers with complements at `1350/1354`; `136C` = channel state
(`0`=uninitialized, `0xE1`=ready, `0xD2`=command in flight, `0xC3`=aborted →
finalize returns `0x20`); `136D` = guard-failure flag; `1194/1198` = ISR-layer
callback + complement, dispatched by EIINT channels **292/293** (marked
reserved in the generic P1M-E table but active in this firmware).

### Issue recipe (generalized from the four wired wrappers)

1. Gate: `state == 0xE1` **and** `ICUSSTS.BUSY == 0` **and**
   `(ICUSSTS2 & 3) == 0`.
2. Set block counts (`132C` in / `1334` out), pointers + complements
   (`1340/1350`, `1344/1354`), stream callbacks + complements, tracked command
   (`1328`).
3. Preload per command family: commands 1/3 write `ICUSPARAM = block_count`;
   command 5 pushes its 16-byte length header through `ICUSDAT` (three
   zero/BE32-length words) before the message stream; command 8 stages its
   64-byte request as 4 input blocks (M1/M2/M3) with 3 output blocks
   (M4/M5).
4. `state = 0xD2`, then write `ICUSCMD = (selector<<16)|command` — the write
   is the trigger.
5. Completion: hardware raises EIINT 292/293 → `*_dispatch` calls the guarded
   callback; the poll engine (`0x89E20`, or the `0x9C4`-iteration polled
   fallback `0x87484`) dispatches on `ICUSSTS2`: bit 0 → input step
   (`ICUSCTL=1`, push 16 bytes), bit 1 → output step (`ICUSCTL=2`, pop 16
   bytes), completion → finalize (`ICUSCTL=3`, ack `0x24`, decode `0x10`).
6. Zero-I/O commands (the dead `0xB`/INIT_RNG stub, any future `0xA`/`0xD`
   probe) need no stream cells: register the finalize callback, set `1328`,
   `state = 0xD2`, write the command word, poll `ICUSSTS.BUSY == 0`, then
   classify via `FFC5D010 & 0xFFF`.

The runtime-facing consequence: the existing F33 RAM-resident callers
(`exploit/ephemeral_runtime/`) already exercise steps 1–5 through the stock
driver for command 5; issuing the unexercised opcode family is the same
sequence with different counts and command word — the Sienna orphan stubs
(`0x89A4C` cmd-11, `0x89B70` cmd-`0x22`) are byte-level templates for
zero-I/O and 1-in/2-out shapes respectively.

## 8. Boundaries and open questions

- The opcode-`0x10` airbag service's application consumer is engine-mediated
  (runner table `0x1C7C0..0x1C7E0`); its semantics (4-byte result over
  16-byte-block input, config selector) are recovered shape only — see
  OPEN_QUESTIONS.
- Corolla/Crown TX descriptor *wire* joins (which physical PDU carries the
  `0x0030`-field authenticated frame, freshness source) are table-shape
  evidence; the Camry `0x030` join is the only live-observed one
  (`analyze_camry_f33_030_secoc_tx.py`).
- Crown/Corolla chains marked corpus-static close through data-space pointers;
  the register-site census itself is live-project verified.
- The airbag census covers the MainPE application image only; the separate
  `boot.bin` RPRG module uses CPU-side AES (payload/SA roots) and does not
  reach the secure-service boundary.
- Nothing here observes hardware: slot-4 generation permission/latency and all
  live opcode behavior remain dynamic questions (OQ-012/OQ-021 unchanged).

## 9. Reproduction

```text
tools/test yc_venza_airbag_reprogramming     # airbag census byte pins
tools/g x-ref to 0xFFC5D000                  # EPS register-site census (per target)
tools/pseudo --target <T> <issuer-addr>      # issuer constants per corpus
```

The registered airbag target rebuilds and queries like any other:
`make rebuild-project TARGET=venza-8917048E30`, `tools/gtarget
venza-8917048E30 ...`, `tools/pseudo --target venza-8917048E30 ...`. The
census sweep scripts under `ghidra/scripts/investigate/` remain one-shot
workspace tooling, not evidence.
