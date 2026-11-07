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
(`0x89A4C`, `0x89B70`) by any encoding. They are unreachable library artifacts of
the generated driver's full SHE command set: **no stock runtime initializes the
ICU-S PRNG on any target, and nothing anywhere issues `CMD_RND` (`0xD`)**.

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
| 8 | Crypto-test bank key-update sequencer `0x692D2 → 0x89A26`. **RID `0x1010` is null/null in the F33 19-RID table**. Sienna has a dedicated RID; F33 carries stock cmd8 through the bank. |
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
| 5 | Channel exists (wrapper `0x82070 → 0x83A30`) and its sync API `0x820CC`/step `0x821D0` are registered in the ROM service registry (records at `0x27C9C/0x27CBC`); the SecOC engine block (`0x87000..0x8B000`) joins the service layer through runners (`0x881F8/0x88986/0x88FDA → 0x826xx..0x830xx`). A 0x44-stride TX descriptor table exists at `0x2581E+` with the same first-record shape as Crown (DataID field `0x0030`). **No diagnostic crypto-test RID bank exists** (no `0x100E/0x100F/0x1010` constants; all matches are bitmask tests). |
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
the practical signing surface on the current generation includes production
stock hardware behavior.

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
| `0xBD8C8` | `FEFF01E8` | **`0x10`** | Key-selected, 16-byte-aligned input/output buffer transform; completion returns the output byte length through a 4-byte caller field | **diagnostic crypto-test** handler `0x7C05A` via engine thunk `0xBD44A` (compares 16 output bytes against a reference; exact algorithm and direction open) |
| `0xBE0CC` | `FEFF0398` | `0x31` | authenticated 64-byte key update (SHE `CMD_LOAD_KEY` M1/M2/M3 → M4/M5) | RID `0x1010` worker (`0x7C13E` staging, `0xB76D4` async, dispatcher `0xBD2EC`) |
| `0xBDA6E` | `FEFF0250` | **`0x04`** | mode-mapped key-ID service: `{1→0, 2→1, 4..13→n−2}` (compact SHE key-slot index) | RID `0x1010` worker mode 2 (via `0xBD2EC` record 1) |

So the airbag application-facing secure-service opcode set is
`{0x04, 0x10, 0x12, 0x31}` — five registered services, two more than the
previously documented three (§5.5/§5.6 of the airbag report documented 0x12 and
0x31 plus an unnamed 0x04 mode; this census adds the 0x10 service, both
descriptor bases, and the registry). The opcodes stay numeric because they use
the Renesas security-hardware protocol. The EPS ICU-S uses separate SHE
command numbering.

### Driver programming model (recovered from the Venza driver)

Same Denso driver skeleton as the EPS (channel-state cells `0xE1`/`0xD2`,
complement guards, per-service state pairs), but the lowest layer swaps
register pokes for a **shared-memory descriptor ring a second core reads**.

**Control/status window** (`0xFF1F00xx`, plus shared flags in `0xFEFF00Fx`):

| Address | Recovered role |
|---|---|
| `0xFF1F0010` | control/pointer word: low bits = shared-memory base (driver masks `&0xFFFFFF \| 0xFE000000`), bit 26 = config flag (`0x8A04E`), bit 27 = **HSM-ready** (`0x86008`/`0x89E22` poll it) |
| `0xFF1F0014` | ring index (four entries, wraps `0→3`; decremented then stored per submit) |
| `0xFF1F0028` | boot: `\|= 4` by `0x114C` (interrupt/enable path) |
| `0xFF1F0044` | trigger doorbell: `2` = descriptor queued; `4/8/0x10/0x20` = other kicks; `0x40` = HSM start (written once at driver start `0x86510` after setting the pointer) |
| `0xFEFF00F4` | HSM status: bit 0 = ready gate for submits (`0x89F6E` → error `0x404` if clear) |
| `0xFEFF00FC` | shared spinlock: bit 1 = submit lock (`0x89E60`, `__snooze` backoff), bit 3 = completion/config lock (`0x8A04E`) |

**Descriptor layout** (`0xFEFF00xx` shared RAM; offsets relative to the
opcode address in the table above):

- `+0x00`: opcode dword; `+0x05`: submit-state byte set to 1;
  `+0x06`: queued flag set to 1 (4 on ring-full);
  `+0x07`: completion-state byte initialized to `0x7F` (pending);
  `+0x08`: HSM result-code word initialized to sentinel `0xFFF1` by `0x8A18A`;
  `+0x10`: application-side finisher callback (e.g., `0xBDC3E`/`0xBDE24`).
- For **both** opcode-`0x12` MAC descriptors, `+0x14` is the input pointer,
  `+0x18` is the generated/expected MAC pointer, `+0x1C` is input bit length,
  `+0x20` is set to 3, `+0x24` is the logical key selector (configured 4),
  `+0x25` is tag bit length, and `+0x2C` is timeout `0x2580`.
  **`+0x28` selects direction:** TX generation sets 0 (`0xBDC7A`,
  `FEFF02E0`); RX verification sets 1 (`0xBDE88`, `FEFF0358`). The RX finisher
  `0xBDE24` reads a separate verification-result word at descriptor `+0x34`.
- The opcode-`0x10` adapter (`0xBD8C8`) supplies separate input/output
  pointers, a block count `input_bytes >> 4`, and a key selector, with timeout
  `0xE10`. Its finisher (`0xBD86C`) returns the input byte count as the
  output length on success. The key-update adapter (`0xBE0CC`) points to
  M1/M2/M3 at offsets `+0/+0x10/+0x30` in the caller's 64-byte package and
  M4/M5 at `+0/+0x20` in the 48-byte output.

**Submit sequence**: service adapter validates (global driver-ready cell
`0xFEBFA298 == 0xE1` via `0xBD690`, per-service state pair) → builds the
descriptor in shared RAM, sets service state `0xD2` (`0xE1` instead when the
caller requested async mode) → `0xBD69E → 0x8A18A` (4-byte alignment check,
state bytes, callback sentinel) → `0x89F6E(2,desc)` gates on `0xFEFF00F4`
bit 0 → `0x89E60` takes the `0xFEFF00FC` bit-1 spinlock, decrements the ring
index (wrap 3), claims the 4-byte slot at `shared_ptr + idx*4` if free,
stores the descriptor pointer, marks `+0x06 = 1`, releases the lock (ring
full → `0x401`) → trigger word `2` written to `0xFF1F0044`.

**Completion** (2026-10-08 closure): **task-polled, no interrupt dispatcher**. The
HSM updates the shared descriptor's completion/result fields; the finisher
callback at `+0x10` runs in the polling owner's MainPE context, interpreting
the HSM result word at `+0x08` via `0xBD728`. Evidence: no code outside the five adapters
and three driver primitives references the FEFF flag window, ring registers, or
descriptor addresses anywhere in the image (corpus + full disassembly);
descriptors carry caller-side poll timeouts (`0x2580`/`0xE10`); init wraps in
IRQ-disable critical sections (`0x89DC8/0x89DE8`); the `0x7CA68` application
bring-up clears the FEFF ring under `di` and gates on status bits 31 then 28 of
`0xFF1F0010` before enabling; the nine-runner table (`0x1C7C0`) is the
scheduler-driven bracket set that moves the per-service `0xE1/0xD2` cells.
`0x8A26A` is a two-instruction status-read helper (`return *0xFF1F0010`).
Submission uses the common chain `0xBD69E → 0x8A18A → 0x89F6E → 0x89E60`.
Result classification: nonzero result byte = error index, plus submit-layer
codes `0x401` (ring full), `0x404` (HSM not ready), `1` (bad trigger mode).
Vector-level EIINT analysis was not performed; the `0x114C` boot sequence
(`0x4001` enables at `0xFFC64200/0xFFC65400`, `0xA5`-unlock handshakes through
`0xFFF8xxxx`) remains recorded but not decoded register-by-register.

Runtime-facing contrast with the EPS ICU-S: there is no register FIFO or
`ICUSCMD` poke — a caller writes a descriptor into shared RAM, queues its
pointer, and rings the doorbell. That makes the airbag ABI the *easier* one to
drive from a RAM runtime (no per-block handshake), but also the more opaque
one: opcode semantics live entirely in the HSM-side firmware we do not hold.

### Inferred ICUMC firmware contract

- The ICU-M security CPU must have a descriptor consumer and the ability to
  read/write the permitted `0xFE...` shared-RAM regions: the MainPE queues
  pointer-valued requests, not message bytes. The matching HSM endpoint must
  interpret opcode, buffer addresses, lengths, selector and operation mode,
  process the request, and publish completion/result fields. It is not
  necessary for the secure CPU to know CAN arbitration IDs, SecOC freshness,
  or truncated on-wire tag placement: the MainPE SecOC layer handles those.
- Opcode `0x12` is a **single MAC service with an explicit generate/verify
  discriminator** (`+0x28 = 0/1`). A likely internal handler branches on this
  field and uses the same selected key for either full-MAC production or
  supplied-tag verification. The host-provided byte selector `4` is a logical
  `KEY_1` reference, not key material.
- The `0x31` request passes an unchanged SHE `M1||M2||M3` envelope and returns
  `M4||M5`, requiring the secure endpoint to validate and execute the
  protected key update. After that submission, the MainPE worker `0xB76D4`
  extracts the **high nibble of M1 byte 15** (`FEFF0177`) as the target SHE
  key ID and calls opcode `0x04`. Its adapter `0xBDA6E` maps SHE IDs
  `1→0`, `2→1`, and `4..13→2..11`: a **12-entry compact index** consistent
  with `MASTER_ECU_KEY`, `BOOT_MAC_KEY`, and `KEY_1..KEY_10`. The result-only
  callback and sequencing suggest a post-update key-state/status check;
  what the HSM actually tests remains an inference.
- Opcode `0x10` uses the same key-selecting service layer but requires an
  input size divisible by 16 and output capacity at least that many bytes. Its
  diagnostic callback compares the 16-byte output with a reference. This
  strongly suggests a block-cipher transformation, but the precise
  algorithm and operation are not identified in the MainPE code.

This is the **MainPE-exposed service subset**, not a complete inventory of the
ICUMC's programmable secure firmware. Renesas describes the P1x-C ICUMC as a
dedicated RH850 G3K with hardware-separated secure memory and peripherals:
[RH850/P1x-C datasheet](https://www.renesas.com/en/document/dst/rh850p1x-c-datasheet),
[secure-boot architecture](https://www.renesas.com/en/blogs/achieving-root-trust-secure-boot-automotive-rh850-and-r-car-devices-part-2).

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

### Shared SecOC engine layer — byte-level join across both ABI families

The profile records above the crypto adapters carry the same authentication
block in **all three profile families** (Sienna legacy EPS, TSS3 EPS, Venza
airbag ICUMC), regardless of which crypto unit executes the MAC:

```text
u16 0x0080 | u16 0x001C | u16 0x0000 | LEN | FLAG | [u16 0x0002 TX only] | DataID
```

- `0x001C` = **28-bit MAC truncation** — the Toyota MAC-28 domain, identical
  everywhere;
- `LEN` = **SecOC trailer length / minimum secured length** —
  `(transmitted freshness + transmitted MAC)/8`: 8 for classic `0x00F`
  (36+28 bits), 4 for CAN-FD/TX rows (4+28 bits), matching the Sienna profile
  table's Trailer column; the RX worker `0xDE09E` uses it as a reject threshold
  and payload base (`received < LEN` → reject, `payload = received − LEN`);
- `FLAG` = `0x0180` (classic RX `0x00F`), `0x0080` (CAN-FD RX), TX rows insert
  `0x0002` before the DataID;
- RX tables are **0x50-stride in all three families** (Sienna `0x25970+` six
  rows, Corolla `0x256E8+` three, airbag `0x1D6C8+` four); TX rows are
  **0x44-stride** in Corolla/Crown and the airbag. The EPS generation places
  the block at the record tail (record `+0x46`), the airbag generation at the
  record head — same fields, different phase;
- marker constants `0x2424`/`0x2E04` appear in record bodies of both families.

Verified instances (shared-DataID rows are byte-identical modulo DataID):
Corolla TX `80 00 1C 00 00 00 04 00 80 00 02 00 | 00 30` vs airbag TX
`… | 03 26` / `… | 00 24`; Sienna RX `… 08 00 80 01 | 00 0F` = Corolla RX
`0x00F` = airbag RX `0x00F`.

**DataID overlap across ECU types and vehicle lines** (same authentication
domain, same selector-4/`KEY_1`, same MAC-28):

| DataID | Sienna EPS RX | Corolla EPS RX | Venza airbag RX |
|---|---|---|---|
| `0x00F` | ✓ | ✓ | ✓ |
| `0x0D7` | ✓ | ✓ | ✓ |
| `0x090` | ✓ | — | ✓ |

The `0x00F`/`0x0D7` rows are byte-identical auth blocks in a 2020 Sienna-family
EPS, a 2023-25 Corolla EPS, and a 2021-22 Venza airbag sensor — three ECU
types, two crypto-unit families, one generated SecOC engine configuration
family. Implementation detail therefore maps across the ABI boundary: profile
walking, DataID insertion, MAC-28 truncation, and freshness assembly are the
same generated layer; only the MAC adapter below differs.

## 7. ICU-S driver programming model (recovered from the Sienna driver)

The stock driver is a complete, self-contained ICUS programming reference —
including for command words the application never issues (the §3 dead stubs
are working templates). The register map and recipe below are Sienna-verified
firmware-static; §7.1 separately traces the exact Camry lifecycle.

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
(`tools/targets/camry/research/ram_runtime/`) already exercise steps 1–5 through the stock
driver for command 5; issuing the unexercised opcode family is the same
sequence with different counts and command word — the Sienna orphan stubs
(`0x89A4C` cmd-11, `0x89B70` cmd-`0x22`) are byte-level templates for
zero-I/O and 1-in/2-out shapes respectively.

### 7.1 Exact F33 SecOC verification lifecycle

For Camry `8965F3307000`, CodeFlash SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`,
the transport completion and MAC verdict are separate values. SecOC
`8F676 -> 89C98 -> 89646` submits handle0. Its original ROM record at
`27DE8` contains completion `89CFA`, submit `891CC`, service `892CC`,
and readiness pointer `27DE4` (byte1). Handle1 at `27E08` instead uses
test-bank callback `6A2DC` and readiness pointer `27DE5` (byte0).

#### Input composition and admission

B6's original profile2 record supplies DataID`00B6`, trailer length4,
received MAC length28 bits, and reconstructed freshness length46 bits
(`258E8..2591F`). `8F434` extracts the trailer's high freshness nibble and
left-aligns the remaining28 tag bits at `FEBE5554`. `8ECB2` builds
`BE16(DataID) || payload_without_trailer || packed_full_freshness` at
`FEBE552C`; `5528` is its **byte** length. For an eight-byte B6 PDU this
is2+4+6=12 bytes. `8F676` forwards that length and the28-bit tag length
from `5550`; it does not inspect tag content.

`88FC0` requires descriptor word0=`1`, nonnull input/tag/result pointers,
input length≤`50` bytes and tag length1..`80` bits. It copies the input
to `FEBF12B8`, zero-pads it to a16-byte boundary, and copies
`ceil(tag_bits/8)` received-tag bytes to `1308`. Its descriptor at `12A0`
is `{input_pointer, input_bits, tag_pointer, tag_bits&7F, descriptor_byte4}`;
`1298/129C` point to that descriptor and output word`12B4`. The selector
is runtime software-descriptor byte4, copied by `8F19A`; its configured
value and the corresponding installed ICU key require provenance.
`88F92` initially clears the full tag staging area; `88FC0` itself does
not clear the unused tail of a shorter replacement tag.

On accepted staging, `8A8E4` writes ICU parameter words
`{0, byte_swap32(input_bits), tag_bits&7F, 0}` and then
`ICUSCMD=(selector<<16)|7`. It requires channel`136C=E1`, BUSY=0,
`STS2&3=0`, selector≤14 and staged tag length<128. The command-register
store at `8A9FC` also executes when that readiness gate returns2; it is
not evidence that the input/callbacks were staged. `8A832` subsequently
feeds `ceil(input_bits/128)` padded input blocks, then one16-byte block
from the received-tag staging pointer. Each block is four unchanged
little-endian RAM words written to `ICUSDAT`. `8A898` is the separate
four-word output reader.

Upstream admission is also stateful: `89C5A -> 89E72` requires all four
service markers (`1378/1384/1390/139C`, prefix`FEBF`) to aggregate as
idle`E1`. Service lock`1386` and scheduler lock`116C` must be unlocked`D2`;
service selection must be`E1`, and scheduler state must be`E1` or prepared`C3`.
An active owner makes a new `8F676` return2 before replacing its descriptor.

NvM service/paired guards at `FEBF6CCD/6CCE` must both be nonzero for
`7995C` to attempt suspension. Otherwise it records deferred0 and produces
wait input1 itself. Original guard exit`79A94` drains that deferred request
through `7990E -> 7812A -> 789E2`; no injected suspension callback is needed.
With explicit offset20 bit0=0, initialized DataFlash phase`6CB2=0E` and
no active P/E operation (`6CB0!=2`), the native request returns10, changes
phase to`10`, sets suspend state/mirror2, and produces readiness input0.
An active P/E operation additionally needs the selected FACI suspension
policy and completion; suspension result2 remains waiting. `87EF6` saves
FHVE3/FHVE15 on readiness0 and `87EDC` restores them before native NvM
resume. These are required software/hardware inputs, not inferred reset
values.

#### Ownership and completion


`891CC` installs guarded scheduler start/completion callbacks
`FEBF117C=89170` / `1180=890BA`; the starter installs guarded ISR/poll
callback `1194=89114`. The NVM suspension result travels through
`79D38 -> 87EF6 -> 885B2`: input1 retains wait state`D2`, input0 makes
the request prepared`C3` and starts it if already waiting, and other
inputs release a waiting owner and report transport failure1. `89170`
changes `C3 -> B4` before issuing command7.
For a waiting request, `885E2..885EE` snapshots both scheduler callback
pointers and complements before selecting the reply branch. Even pending
and error callback fixtures therefore retain the complete active-request
callback set installed by `891CC`.

`88FC0` retains caller result pointer `FEBF1318` and its complement
`FEBF128C`, copies input/tag into bounded staging, and installs the
command7 output destination `FEBF12B4`. SecOC supplies `FEBE5564`
as the caller result pointer. The completion chain is:

```text
8A898: consume four ICU output words; retain first at FEBF12B4
8AF10 -> 8A600: finalize channel (1=transport completed, 2=error, 20=abort)
89114 -> 890BA -> 8906C: route transport status; copy verdict only on status0
896E0 -> ROM[27DEC]=89CFA: consume service owner; set 13BF=status, 13BE=1
89C98: return0 only for completed status0; return1 error, 2 busy/poll timeout
8F746 -> 8F906 -> 8F8D2 -> ROM[25918]=90448: consume FEBE5564 for B6
```

`13BE/13BF` above have RAM prefix `FEBF`. `89CFA` is a raw
14-byte callback, `4437bf5b010a440fbe5b00527f00`: store status byte,
store completion1, return0. `8906C` copies only the low byte of the
staged output. Thus transport success and a rejected MAC verdict can
coexist; a transport error preserves the previous caller result byte.
`8F746` admits `8F906` only after submit returns0.

| Boundary | Native software behavior |
|---|---|
| Invalid handle/request, unavailable job, busy descriptor/lock | Return1/2 without producing a MAC verdict. `89C98` resets `13BE=0,13BF=1` even before a busy return. |
| Accepted request but no callback within `E07` polling iterations | Return2; the polling wrapper neither cancels the job nor releases its selected descriptor. |
| Poll-only timeout followed by native service | `89C98` only reads its completion flag; it does not call the ICU poller. Later `89114` still owns the command and can feed it, remain pending, or finalize an explicitly indicated hardware error through the original callback chain. |
| `89114` receives poll result0 or `12` | Retain pending wrapper state `FEBF1190=B4`; no completion. A channel-validation error such as `10` instead releases the wrapper and reports transport error1. |
| Deferred completion | `890BA` queues status at `1294=E1/1295` when readiness is not1. `892CC` consumes that queue on its next invocation without rechecking readiness. |
| Waiting/prepared/running deadlines | `892CC` expires `D2` at tick7, `C3` at tick12, or `B4` when either running counter reaches12; reports transport error1. The running case invokes bounded abort/reinitialization `88574`; the prepared case requires no crypto execution. |
| Abort | `8ACA8` replaces streaming callbacks with null, retains finalizer `8A600`, tracks command`3F`, and sets channel`C3`. An abort request alone supplies no reply. Finalizer return`20` is cancellation, not verified MAC output. |
| Service owner and duplicate notification | `896E0` requires selection state`A5` and a complemented pointer, then resets selection **before** invoking the configured callback. A duplicate at this boundary is ignored. |
| Late low-level output callback | `8906C` copies the output **before** `896E0` checks selection ownership. Resetting selection alone does not revoke the result pointer; `88F92` clears it and the staging buffers, making a late callback report error instead. |
| Reuse after selection-only reset | `8961A` clears service selection but leaves scheduler`B4`, channel`D2`, and the result pointer intact. A replacement submit still returns2 at the scheduler and issues no new command. Reuse is not a generation-based cancellation mechanism. |

There is no generation/token check at the selected-service callback boundary:
ownership is its current state and complemented pointer. Retain both ownership
layers when interpreting late or duplicate callback experiments.

Exact authority: reconstructed source for `88FC0`, `8906C..89386`,
`895A4..8972A`, `89C98`, `8A898`, `8ACA8`, `8AF10`, and `8F676..8F906`;
disassembly at `8906C`, `892CC`, `896E0`, `8A600`, `8A8E4`; raw ROM
`27DE0..27E2B`, `258E0..2591F`, and callback bytes `89CFA..89D07`.
The `8A8E4` gate controls staging and its return value: its command-register
store at `8A9FC` is also reached on return2, after valid arguments, even
when the idle/BUSY/STS2 staging gate fails.

Eighteen standalone `camry_f33_secoc_crypto_*.json` fixtures retain native
submission failures, pointer/owner guards, deferred/duplicate/late callbacks,
buffer-reset recovery, NVM suspend pending/error inputs, a software-only
prepared deadline, a reset-channel error producer, and abort without a reply.
Callback-entry scenarios explicitly
inject transport status and, where copied, a rejected synthetic output byte;
the abort-finalizer scenario also explicitly invokes its callback. These are
distinct from continuous submit-to-hardware completion. True crypto evidence
requires a real command7 transaction with its input/tag and slot provenance,
output FIFO words, completion/error indications, and uninterrupted propagation
through `89114/89C98` into SecOC. All eighteen scenarios passed original-byte
execution (`secoc-crypto-wave1`, with the two completed suspension preconditions
verified in `secoc-crypto-wave2`, under `build/out/firmware-question-campaign/`).

Fifteen strict standalone `camry_f33_secoc_native_*.json` scenarios retain
the continuous producer/submission path and pending-only register admission.
Eleven execute original `8F148/8F19A`, `8F434`, `90566`, `8ECB2`, then
`8F676 -> 89C98 -> 89646 -> 891CC`; subsequent original poll/service calls
share the same RAM. Their checkpoints cover command issue without a reply,
two native input-block feeds, BUSY/STS2 staging rejection, deferred NvM
guard exit, the waiting deadline, a running deadline with bounded abort,
an explicit hardware error after wrapper timeout, resubmission, and both
selection-only and buffer-reset ownership boundaries. Four focused
register-store scenarios cover admitted status/error preservation and
unsupported command/selector rejection. They contain no output-FIFO
input and no injected callbacks.

The retained synthetic example is PDU`11 22 33 44 AB CD EF 12`,
freshness record`1234/ABCDE/9A/2`: native serialization produces
`00 B6 11 22 33 44 12 34 AB CD E9 A8`, and native extraction produces
tag`BC DE F1 20` with28 significant bits. Software selector4 is an explicit
fixture input, not a recovered key or observed installed-slot value.

The strict model accepts exact command7 words for selectors0..14 and bare
abort`3F` as **pending register writes only**, retaining existing width checks
and preserving supplied BUSY/STS2/error words. It creates no hardware
transition or output. Error scenarios explicitly supply BUSY=0, STS2=2
and error bit0; original `8AF10 -> 8A600 -> 89114` then produces transport
error1 and preserves the caller-result canary. The running deadline supplies
BUSY=1 and no abort reply; native bounded polling/reset revokes the result
pointer and reports failure. The acceptance boundary remains the real ICU-S
transaction: key/slot provenance, input consumption, output FIFO words,
and completion/error indications. All fifteen scenarios passed exact-image
execution in `build/out/firmware-question-campaign/secoc-native-wave1`.

## 8. Boundaries and open questions

- The opcode-`0x10` airbag service is diagnostic-crypto-test-driven
  (callback `0x7C05A`). Its 16-byte-block input/output shape is recovered;
  precise block-cipher algorithm, direction and test-mode mapping remain open.
- Airbag completion is task-polled (no interrupt dispatcher found; see §5
  closure). Vector-level EIINT analysis was not performed on this project, and
  the `0x114C` boot enable sequence remains recorded but not decoded
  register-by-register — those bound the "no ISR" claim without proving it at
  the vector-table level.
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
  live opcode behavior remain dynamic questions.

## 9. Reproduction

```text
tools/test yc_venza_airbag_reprogramming     # airbag census byte pins
tools/g x-ref to 0xFFC5D000                  # EPS register-site census (per target)
tools/pseudo --target <T> <issuer-addr>      # issuer constants per corpus
```

The registered airbag target rebuilds and queries like any other:
`make rebuild-project TARGET=venza-8917048E30`, `tools/gtarget
venza-8917048E30 ...`, `tools/pseudo --target venza-8917048E30 ...`. The
census sweep scripts under `ghidra/scripts/investigate/` are one-shot workspace
tooling.
