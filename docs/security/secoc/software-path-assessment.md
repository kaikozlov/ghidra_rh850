# ICU-S software-path assessment

> **Scope:** Toyota Sienna EPS `8965B4512000`, RH850/P1M-E `R7F701381`
>
> **Question:** Can attacker-controlled software behavior reach ICU-S command 13,
> expose slot 4, or provide an equivalent signing/key-recovery capability without
> physical fault injection or side-channel analysis?
>
> **Status:** Stage-7 static software-path questions closed; hardware command
> semantics, live slot permissions, and dynamic proxy behavior remain untested
>
> **Primary evidence:** firmware bytes and disposable working-project Ghidra
> analysis in `build/work/project/`; existing reports are navigation aids, not proof
>
> **Verification:** `tests/verify_icus_software_paths.py`,
> `tests/verify_payload_gate.py`, `tests/verify_secoc_application.py`

## Methodological boundary

The verified absence of a stock command-13 writer proves only that no intended
application path emits command 13. It does **not** prove that attacker-controlled
input cannot corrupt an ICU command word, activate a dormant path, redirect a
callback, gain an arbitrary call/write primitive, or reuse an initialized ICU-S
operation as an oracle.

This assessment therefore works from externally controlled inputs toward
capabilities, in this order:

1. CAN/ISO-TP and UDS parsing boundaries;
2. memory read, memory write, download, transfer, and execution services;
3. writable callbacks, function pointers, driver records, and global state;
4. dormant crypto-test activation and output transport;
5. control of ICU-S command words, selectors, FIFO buffers, and callbacks;
6. command 13 only after a software foothold and known-`RAM_KEY` baseline exist.

Physical fault injection and power/EM analysis are outside this report unless
all software paths are deterministically bounded.

## Threat model

Initial attacker capabilities are considered separately:

- unauthenticated CAN access to application diagnostic and normal receive IDs;
- diagnostic sessions obtainable through stock UDS state transitions;
- application SecurityAccess level 2 where applicable;
- bootloader diagnostic access after the stock application handoff;
- a single malformed or adversarial ISO-TP/UDS/CAN request;
- repeated requests capable of exercising races or stale asynchronous state.

A result is not called key recovery unless candidate key bytes independently
validate multiple stock SecOC frames. A MAC/AES oracle, arbitrary call, or
signing proxy is recorded as a separate capability.

## Firmware baseline

- CodeFlash SHA-256:
  `21140bbd65e530a9e518a3e84e20e5d85679675bc09cc724cb177bb7c76bafde`
- DataFlash SHA-256:
  `81d87b678784bb2a07b1fdcb3d43dd40767d4f5ca1b56867b6575cd652a9ecb8`
- Existing raw-byte census: nine direct `ICUSCMD` stores; intended command
  families are 1/3, 5, 7, 8, 11, `0x22`, `0x3f`, and `0x7000/0x7100`; no
  intended command-13 writer. This is a starting boundary, not a software
  security conclusion.

## Candidate-path ledger

| Path | Attacker-controlled source | Desired capability | Current grade | Evidence / next discriminator |
|---|---|---|---|---|
| Application ReadMemoryByAddress (`0x23`) | extended-session ISO-TP request, no SecurityAccess | read application RAM / DataFlash | **verified disclosure** | fixed ALFID `0x15`; memory ID 1 exposes 107,924 permitted LocalRAM bytes, memory ID 2 exposes 29,952/32,768 DataFlash bytes; protected subranges are explicitly excluded |
| Application download/transfer | ISO-TP request | executable RAM or CodeFlash foothold | bounded negative | SIDs `0x34/0x36/0x37` remain null direct callbacks |
| Bootloader payload path | bootloader UDS plus recovered gate material | arbitrary bootloader-context RAM callback; potential persistent application harness | recovered capability; ICU use untested | accepted 4 KiB image controls callback at `FEBF0FD0`; more than `0xE00` fixture space remains |
| Service `0xAB` / `0xBA` | UDS requests | event disclosure / persistent proprietary maintenance/lifecycle operations | bounded/verified surface | `0xAB` is the event-record subfunction service. `0xBA` owns a ten-operation table; F7/`BAENA` is callback-local SA2-gated and persists a bounded authorization marker/countdown. Its recovered cone has no direct conditioned-command/d/q/PWM or selected crypto/ICU target, and the blurbdust egg at `0x3485A` only forces its shared token comparator |
| RoutineControl RID `0x1010` | 64-byte M1/M2/M3 package | command-8 key update | bounded for request/copy sizes; crypto-authenticated | `31 01 10 10` fixed 64-byte input and 49-byte status/result; RID policy is extended-only and ICU-S authenticates package |
| Normal CAN/ISO-TP parsers | CAN frames | overflow/index corruption | bounded at application transport layer | declared length is capped by 256-byte Dcm route buffers; each fragment is checked against remaining length |
| Diagnostic crypto-test bank | RoutineControl RID `0x100E/0x100F` plus CAN `0x01B..0x01F` | command 5/7 oracle and output | stock activation recovered; byte-output transport absent | RoutineControl action table `0x25804` row 8 points to `0x8A782 -> 0x69018`; startRoutine is zero-payload, policy 0 has no SecurityAccess levels and is reachable in sessions `1/2/3`; stock bank still compares generated bytes locally |
| ICU callback/driver records | corruption of writable RAM | arbitrary call or command submission | bounded for stock writers | callback/complement pairs receive fixed CodeFlash targets; no request-derived pointer writer recovered |
| Command-word substitution | bootloader payload or restorable application patch | change intended command to 13 | software structure recovered; hardware untested | command-5 and command-8 tracked/submitted ID sites are exact; command shape still unknown |
| Stale FIFO/result exposure | diagnostics or copied RAM | disclose prior ICU output/key material | bounded static negative | commands 1/3/5/7 retain internal staging but outward copies are status-zero gated; command 8 clears its staging on success/failure; abort replacement nulls FIFO callbacks; malformed hardware success sequencing remains outside software-static proof |
| Direct command 13 | constructible software execution foothold | characterize possible Renesas-specific opcode/selector deviation | hardware-unknown; standard SHE slot export disproved | use a known caller-loaded `RAM_KEY` baseline; any persistent-slot copy/export effect would be a vendor extension, not expected SHE behavior |

## Investigation log

### 2026-07-28 — baseline and scope

- Confirmed a clean Git worktree before investigation.
- Confirmed the pinned CodeFlash/DataFlash hashes above.
- Established that the prior writer census is a narrow negative result only.
- Opened this report before deeper analysis so hypotheses, negative results, and
  evidence boundaries survive session compaction.
- Opened only the disposable `build/work/project/` through the repository's isolated
  V850 extension environment. That dated investigation used the then-current
  5,921-function graph; the corrected 2026-08-11 rebuild now has 6,037
  functions and the affected negatives were rerun separately.
- The first bridge attempt used the default Ghidra user home and failed before
  loading the program because `v850e3:LE:32:default` was unavailable. Retrying
  with `-Duser.home=build/cache/ghidra-home` loaded the expected processor module.

### 2026-07-28 — application CAN/ISO-TP ingress

- Firmware path: `application_can_diagnostic_rx_demux` (`0x80114`) resolves
  physical/functional diagnostic CAN IDs and invokes the application transport
  route through CodeFlash pointer `0x21AB4 -> 0x78D20 -> 0x794EA`.
- PduR group 1 resolves through table `0x21E40`. Its transport trampolines call
  `0x903A8` (start of reception), `0x9043C` (copy received data), and `0x904BC`
  (receive completion).
- The three application diagnostic route buffers at `0x26064`, `0x2606C`, and
  `0x26074` are each configured as `0x100` bytes. Start-of-reception `0x903A8`
  returns rejection status 3 when the declared request length exceeds the
  selected 256-byte capacity.
- Copy routine `0x9043C` obtains the remaining capacity from `0x92398` and calls
  byte-copy body `0x920D2` only when fragment length is less than or equal to
  that remaining count. The copy body advances the destination pointer and
  subtracts the copied length.
- **Bounded negative:** no transport-layer overflow was recovered through a
  correctly routed declared length or fragment length. This does not cover
  service-specific parsing/copies after reassembly, stale asynchronous state,
  or corruption through a separate route.
- The low-address named `Dcm_*`/`CanTp_*` bodies are in the bootloader region;
  they must not be used as evidence for the application stack.
- Raw diagnostic-ID records at `0x21FC8`, `0x21FD0`, and `0x21FD8` contain
  standard IDs `0x7A1`, `0x777`, and `0x7A0`. The demux bounds the selected
  rule index by three CodeFlash records before routing.
- Normal frames follow `0x7FA56 -> 0x7F95E`; the queue ingress bounds the
  hardware label through `DAT_00021964`, maps it through a CodeFlash byte table,
  caps copied data at 8 bytes for classic frames or 64 for FD, and sizes queue
  records in 8-byte data quanta. The copy loop rounds to four bytes but remains
  within that 8-byte allocation quantum. No immediate normal-frame queue
  overwrite was recovered from DLC handling.

### Attacker-controlled entrypoint map

| Source | Firmware ingress | Immediate parser/dispatcher | Notes |
|---|---:|---:|---|
| physical diagnostics `0x7A1` | `0x80114` | application CanTp at `0x79454` | multi-frame request, 256-byte Dcm cap |
| functional diagnostics `0x777` | `0x80114` | same application CanTp/PduR chain | addressing policy enforced later by service dispatcher |
| secondary diagnostic route `0x7A0` | `0x80114` | same transport chain | also reaches proprietary `0xAB` wrappers per config |
| 47 normal application RX IDs | `0x80006` | route flags then PduR/COM/SecOC | includes six SecOC-bound records |
| acceptance-rule 50 / `0x7F7` | `0x7FF86` | separate configured callback | structurally separate from diagnostics |
| crypto-test inputs `0x01B..0x01F` | normal PDU route | bank collectors after diagnostic activation | bank 1 is armed by RoutineControl `31 01 10 0F` |

### 2026-07-28 — crypto-test and ICU callback state (activation corrected 2026-08-13)

- `crypto_test_bank1_activate` (`0x69018`) initializes active byte `FEBE508F`,
  state `0x11`, input/result banks, and update-counter snapshots. The original
  direct-xref census missed its stock diagnostic caller because the configured
  RoutineControl action table points one hop earlier to wrapper `0x8A782`.
- Application RoutineControl RID `0x100F`, control type `0x01` (startRoutine),
  reaches action wrapper `0x8A782`, which directly calls `0x69018`. The RID is
  enabled, consumes zero option bytes, policy index 0 has zero SecurityAccess
  levels, and both the RID policy and corrected SID-`0x31` service object allow
  sessions `1/2/3`. The stock activation request is therefore `31 01 10 0F`,
  including from the default diagnostic session.
- Direct writers of `FEBE508F` remain full crypto-test reset `0x67FCE`/startup
  clear `0x68006`, activator set-to-1 `0x69026`, and terminal finalizer write
  `0x68D32`. The activator only arms state zero and the finalizer leaves
  `0x02`/`0xFF`, so a fresh application boot remains the deterministic baseline.
  However, runtime cyclic `0x68C0C` calls the full reset when reset-request byte
  `FEBE508D==0xA5`; application transition helper `0x4F93C` can produce that
  request. Deliberate tester control of the required transition is not proved,
  so repeatable no-reset re-arm remains bounded rather than declared impossible.
- Once active, CAN inputs can select a software key selector, 16-byte message,
  and 16-byte expected result. Mode 1 reaches command-5 generation and stores 16
  generated bytes at `FEBE51AA`. No stock byte-output transport was recovered,
  but the terminal negative state is externally observable: completion error or
  full-result mismatch -> state `0x44` -> `FEBE5097=0x5A` -> monitor `0x55F1C` ->
  Dem event `0xCC` -> enabled DTC index 133 / DTC `0x00D317`, which no-SA SID
  `19 02` can enumerate (SECOC-046). This is not a pure equality oracle unless
  command execution is independently known successful.
- ICU interrupt channels 292/293 call RAM pointer `FEBF1194` only when its
  complement at `FEBF1198` matches. All recovered writers install fixed
  CodeFlash start/completion functions and their literal complements or clear
  the pair. No request-derived callback address was recovered.
- Higher crypto dispatchers select lower adapter pointers from CodeFlash driver
  records after bounds lookup; caller-controlled fields are selectors and data
  buffers, not adapter function addresses.
- **Implication:** stock diagnostics already supply the missing activation
  primitive. Characterizing selector-4 command 5 no longer requires an
  activation hook; only an observation path for `FEBE51AA` remains necessary.

### 2026-08-14 — corrected application memory/read boundary

The old application-memory negative was caused by the eight-byte-shifted service
parser (CORR-053/CORR-054). Correct runtime object `0x25EA0` binds SID `0x23` to
`application_read_memory_by_address_callback @ 0x948AA`; only SIDs
`0x34/0x36/0x37` remain null download/transfer callbacks.

The recovered SID-`0x23` contract is unusually explicit:

- service object `0x25EA0` is **extended-session-only** and has zero service-level
  SecurityAccess entries;
- format descriptor `0x26204 -> 0x26128 -> 0x26130` permits exactly ALFID
  `0x15`: one byte of size and a five-byte address field;
- the first address byte is a memory identifier and the remaining four bytes are
  a big-endian absolute address, so requests are
  `23 15 <memory-id> <address:4> <size:1>`;
- memory ID `1` permits `FEBE0000..FEBFFFFF`; memory ID `2` permits
  `FF200000..FF207FFF`; both configured read-range records have security count
  zero and no write-range counterpart;
- the one-byte size field caps a single request at 255 bytes; the copy primitive
  `0x4EB1C` independently rejects size `0` and every size `>= 256` (unsigned
  `(size - 1) < 0xFF`), so the effective single-request size domain is
  `1..min(255, remaining response capacity)`.

The raw copy helpers then enforce hard exclusion tables. LocalRAM excludes:

```text
FEBE0000..FEBE37FF
FEBE5030..FEBE529B
FEBF0288..FEBF13CB
FEBF4958..FEBF4B33
FEBF6C00..FEBF78DF
```

leaving **107,924 readable bytes** in five intervals. DataFlash excludes:

```text
FF206C00..FF206EFF
FF207800..FF207FFF
```

leaving exactly **29,952 / 32,768 bytes** readable in
`FF200000..FF206BFF` and `FF206F00..FF2077FF`. The exclusions are security
meaningful: they cover the command-5/key-update result neighborhood, application
SecurityAccess state, object-15 RAM, the DataFlash object-12..15 bank, and the
ICU-S tail. They do **not** make SID `0x23` non-security-relevant: most live
application RAM and DataFlash remain directly observable without SID `0x27`.

One notable allowed address is bootloader payload-derivation buffer
`FEBF2D08..FEBF2D17`. Bootloader handoff calls application entry directly and no
application static writer/clearer of that address is recovered. Whether useful
programming-session material survives the resets/transitions required to reach
application SID `0x23` is therefore a **dynamic residue question**, not a proven
key disclosure.

The read-only host implementation is
`exploit/followups/application_rmba_probe.py`. It models the exact exclusion
rules, defaults to planning/simulation, requires explicit isolated-bench consent
for live reads, and can acquire the 29,952-byte readable DataFlash subset in 119
requests. `tests/verify_application_read_memory_by_address.py` pins the firmware
configuration and `tests/verify_exploit_followups.py` pins the host protocol.

### 2026-08-15 — RMBA memory-safety closure (purpose-built audit)

`tests/verify_application_rmba_memory_safety.py` audits the entire
tester-controlled address/length chain for memory-safety defects and pins the
boundary matrix. The result is a **verified bounded negative**: no integer
overflow/wrap, signedness/truncation defect, range-boundary inconsistency,
requested-vs-emitted mismatch, or async state TOCTOU exists on this path.

- **Length contract:** gate order in `0x9479A` is `len < 3` → NRC `0x13`,
  ALFID whitelist (`0x92E92`, config `0x2612C`/`0x26130` == `{0x15}`) → NRC
  `0x31`, then exact `len == (ALFID>>4) + (ALFID&0xF) + 1` (= 7) → NRC `0x13`.
  No parsing ever runs past the request.
- **Size domain:** the upper gate rejects `size == 0` and
  `remaining < size`; the copy primitive `0x4EB1C` re-rejects everything
  outside unsigned `(size-1) < 0xFF`. Effective domain `1..255` (bounded above
  by the runtime response capacity, see OPEN_QUESTIONS).
- **Address/memid:** `0x94672` consumes data[1] as the memory id (selector
  `0x26328 == 1`) and parses exactly `BE32(data[2..5])`; of the five-byte
  address field only four bytes are address. The range table match
  (`0x92ECC`) is an exact-byte memid match against two enabled records, so
  memid is pinned to `1`/`2` and the `0x8C456` `memid>>4 == 1` chunked/
  programming branch is unreachable from SID `0x23` (pinned by boundary cases
  for memid `0x11`/`0x21`/`0xFF`).
- **Boundary consistency:** configured ranges are inclusive
  `[low, high]`; the end-fit test `(uint32)(high - addr) < size - 1` and the
  copy-time windows `addr >= FEBE0000 && addr <= FEC00000 - size` (RAM) /
  `addr >= FF200000 && addr <= FF208000 - size` (DF) are arithmetically
  identical to `addr + size - 1 <= high` — for all in-range operands neither
  subtraction can wrap (`size <= 255`, `addr <= high`), and the exclusion
  overlap formula `addr <= hi && lo + 1 - size <= addr` cannot underflow
  (`min(lo) = 0xFEBE0000`). Every wrap candidate (`0xFFFFFFFF`, `0x7FFFFFFF`,
  `0x80000000` addresses) is cut by the configured-range gate before any
  address arithmetic runs.
- **Requested vs emitted:** the read is single-shot — `0x4EABA`/`0x65DE6`
  copy exactly the parsed size bytes and the response cursor `FEBE5D90`
  advances by the requested size only on completion; no chunked re-basing of
  the source address exists on the reachable path.
- **Async/TOCTOU:** a corpus census pins that every writer of the RMBA private
  state block (`FEBE5D78/7C/80/81/82`, request mirror `FEBE5D84..9F`, worker
  state `FEBF4598..9C`) lies inside the RMBA call graph (start `0x9479A`,
  poll, cancel `0x8C3E4 -> 0x8C3BE`, workers `0x9462E`/`0x94672`/`0x92ECC`/
  `0x8C456`); the shared response cursor/capacity (`FEBE5D8C/90/98`) is
  Dcm-owned (initializer `0x946FA`) and only read here. Copy-time revalidation
  independently re-enforces bounds identical to the start-time gates, so even a
  hypothetical inter-phase mutation cannot widen the read set.
- **No write behavior:** both range records have `wr_ptr == 0`/`wr_cnt == 0`
  (no write-range counterpart), and the only memory-writing worker branch
  requires the unreachable `memid>>4 == 1` selector.


Real SID `0x2E` WDBI is a separate generic DID-record write path. The 19-entry
`0x26AEC` table is SID `0x31` RoutineControl; its exact sizing still bounds the
largest configured option record at 64 bytes (RID `0x1010` startRoutine) and
result capacity at 49 bytes. No diagnostic request-length overwrite was recovered.

### 2026-07-28 — bootloader authenticated RAM execution foothold

- Bootloader `RequestDownload` (`0x5D68`), `TransferData` (`0x4DBA`), and
  `TransferExit` (`0x5C92`) feed the downloaded image through AES-CBC decryption
  and CRC/CMAC verification.
- The only RAM download region is `FEBF0000..FEBF0FFF`. The authenticated image
  includes callback word `FEBF0FD0`; flash engine bodies `0x4332` and `0x43BE`
  load that word and call it indirectly.
- Existing pinned accepted payloads place `FEBF0000` in the callback word, so
  execution begins in tester-supplied plaintext at the start of the download
  window. This is arbitrary bootloader-context code execution after satisfying
  the payload gate, not merely a data-download facility.
- Payload key derivation at `0x7068` is
  `AES-ECB(PAYLOAD_BUILD_SECRET, DID_0x201)`. In the pinned flow DID `0x201` and
  DID `0x202` are all-zero, and the fixed build secret is already recovered from
  CodeFlash. CRC and CMAC are ordinary reproducible constructions. Therefore an
  accepted custom callback image is constructible from repository-known
  material; no physical fault is required for this foothold.
- **Boundary:** this executes in bootloader context. Static firmware does not yet
  establish slot-4 ICU permissions or state there. The high-value bridge is to
  use the authorized flash machinery to install a restorable application-context
  harness, or to determine whether persistent ICU slot state is directly usable
  from a polling bootloader payload. Neither outcome is claimed yet.

### 2026-07-28 — command-control reuse and software experiment ladder

#### One-shot bootloader payload (preferred first discriminator)

The two accepted encrypted payload fixtures contain only `0x1B5` and `0x18A`
bytes of nonzero shellcode before a zero-filled tail ending at callback offset
`0xFD0`; each leaves more than `0xE00` bytes for an ICU experiment. The pinned
fixtures are existing RAM/DataFlash CAN-dump payloads with output/reset logic.

A modified authenticated payload can therefore:

1. initialize only the required ICU-S control registers (application hardware
   initializer `0x893B8` provides the observed register sequence);
2. load a known candidate `RAM_KEY` operation, if its direct command mapping is
   first characterized;
3. issue command 13 with RAM selector and selector 4 separately;
4. poll command/status registers without relying on application EIINT vectors;
5. return raw command, status, timing, and all captured output blocks over the
   payload's existing CAN transport.

This avoids persistent CodeFlash modification. A rejection in bootloader
lifecycle does **not** close application-context behavior.

#### Payload source and toolchain availability

External reference `Bk2ol/tsk_extraction_by_can_log` at commit `db45375`
contains the complete implementation rather than only the fixture binary:

- `payload_source/shellcode/main_ff1ff000_ff209000.c` directly drives RSCFD Tx
  message buffer 16, sends address/data frames on `0x7A9`, and calls bootloader
  reset `0x157E`;
- `payload_source/shellcode/Dockerfile` builds a freestanding
  `v850-elf-gcc`/binutils toolchain, and `build.sh` emits raw `.text`;
- `payload_source/build_payload.py` pads shellcode to `0xFD0`, installs callback
  and CRC descriptors, computes the CRC/CMAC, and AES-CBC encrypts using
  caller-supplied secret/DID key/IV; and
- `steps/step_dump_dataflash.py` implements session transition, SecurityAccess,
  DID `0x201/0x202`, upload, `0x10F0` verification, `0xFF00` trigger, and CAN
  result collection.

As an external-source reproducibility check, extracting the nonzero shellcode
prefixes (`0x18A` and `0x1B5` bytes) from both committed fixtures and running
that builder with the recovered secret and zero DID inputs reproduced both
4 KiB ciphertexts byte-for-byte, including SHA-256
`d4898836...a06e34` and `d972d4bf...356be2`. The next experiment can therefore
be implemented by adapting C and the existing uploader, not by hand-encoding
RH850 instructions.

#### Reusing command 5 for selector plumbing

Low-level command-5 function `0x89630` already validates selector `0..14`,
constructs `(selector << 16) | 5`, streams input, reads one 16-byte output block,
and uses guarded polling/completion state.

A characterization-only patch would need both of these command-ID changes:

- tracked ID at `0x896DC`: `mov 5,r1` (`05 0A`) -> candidate 13;
- submitted ID at `0x89736`: `ori 5,r18,r1` immediate (`05 00`) -> candidate 13.

Completion helper `0x89DE6` compares the low 16 bits read back from `ICUSCMD`
with the tracked ID, so patching only the submitted literal fails in software.
This reuse preserves selector 4 and selector 14 plumbing and a 16-byte output
buffer, but the stock dormant caller does not transmit generated bytes.

#### Reusing DID `0x1010` for output transport

The command-8 route already supplies extended-session/no-Dcm-SA diagnostics,
64 input bytes, asynchronous ICU completion, and 48 returned bytes. Candidate
ID substitution would likewise require both tracked `mov 8` at `0x899E4` and
submitted `mov 8` at `0x89A2A` to change.

This is **not** yet a safe two-byte experiment:

- command 8 configures four input blocks at `0x899C2` and three output blocks at
  `0x899C8`;
- its staging/result copy is fixed to 64 input and 48 output bytes;
- its command word carries no selector high bits;
- an unknown command-13 block shape can stall, reject, or overrun staging if
  counts are changed without allocating a correspondingly bounded buffer.

It is valuable as an application-context transport template, not evidence that
literal substitution alone is safe.

#### Remaining literal commands

Temporary function seeding in `build/work/project/` recovered command 11 as a
no-caller-buffer/no-selector operation using only finalization, and command
`0x22` as a one-input/two-output-block initialization/lifecycle-shaped operation
with no selector. Neither body establishes persistent-slot-to-`RAM_KEY` copy or
plaintext export semantics.

#### External command-numbering boundary

Public SHE/CSE material commonly assigns `EXPORT_RAM_KEY` to command `0x09`
and `0x0D` to secure boot or reserved behavior. This firmware's Renesas ICU-S
mapping already differs (for example, its verify and key-update writers are 7
and 8), so public numbering neither proves nor disproves Renesas command 13.
GitHub code search found no public non-repository `ICUSCMD` definition. The
restricted ICU-S/ICUSE specification or bench behavior remains authoritative.

### Software-first priority order

1. Adapt the existing C/Docker **non-persistent** bootloader payload using the
   recovered payload gate and CAN transport.
2. Use the initialized application wrapper to test slot-4 command-5 generation
   permission first; record status/output/latency without bypassing serialization.
3. For command-13 characterization, establish a known caller-loaded `RAM_KEY`
   baseline and treat any persistent-slot effect as a Renesas-specific deviation.
4. If bootloader lifecycle blocks lower-level characterization, use the authorized
   flash capability to install a restorable application-context hook and reuse the
   initialized command-5/DID-`0x1010` machinery.
5. Validate any candidate output against multiple stock SecOC frames; otherwise
   classify it as metadata, protected envelope, oracle, or rejection.

#### Bounded live stimulus transport

The first live wrapper incorrectly retained stock Panda ELM327 safety while
calling `panda.can_send()` for application inputs `0x01B..0x01F`; unmodified
ELM327 safety permits diagnostic IDs only, so every input would have been
blocked before reaching the EPS. The corrected local experiment extends ELM327
with parameter flag `0x8000`: only five eight-byte input IDs on one encoded bus
are added to the existing diagnostic allowlist. The host selects this mode only
while sending the five input PDUs, checks `safety_tx_blocked == 0`, and restores
ordinary ELM327 mode before polling DID `0x1010`. The exact external
opendbc/superproject commits and patch are pinned under `exploit/command5/`.

This closes the host/Panda transport defect mechanically. It does not replace
the still-required initialized-application hardware observation.

## 2026-08-10 — Stage-7 stale FIFO/result exposure closure

The command-specific output paths are now traced through success, hardware
error, timeout, abort/replacement, and asynchronous completion:

| ICU command | Internal result staging | Normal outward result | Failure/timeout behavior | Internal clear |
|---|---|---|---|---|
| 1 / 3 | `FEBF11C4` | at most **16 bytes**, only when completion status is zero | wrapper `0x87712` does not copy | no routine clear recovered |
| 5 | `FEBF1274` | at most **16 bytes**, only when completion status is zero | wrapper `0x87B46` does not copy | no routine clear recovered |
| 7 | `FEBF12B4` | one verification-result byte, only when completion status is zero | wrapper `0x87F7C` does not copy | no routine clear recovered |
| 8 | `FEBF113C` + `FEBF115C` | fixed **48 bytes** on success | caller output is zero-filled on failure | 64-byte input and 48-byte result staging are cleared after both success and failure |

The absence of routine clearing for commands 1/3/5/7 means old output can
remain **resident in private driver RAM**. That is not itself an exposure. The
complete direct-reference census finds no diagnostic or unrelated reader of
those staging areas; the only outward readers are the command-specific result
wrappers above.

The shared driver also closes the obvious cross-command race:

- command engines serialize through shared state at `FEBF1190/FEBF136C`; a new
  adapter cannot simply replace an active command;
- `FUN_00089DE6` compares the hardware command ID with the tracked software ID
  and returns `0x12` on mismatch before an output callback is dispatched;
- abort/replacement `0x89BB8` sets both input and output FIFO callbacks to zero
  before issuing command `0x3F`;
- command-5/7/8 timeout workers finish through status `1`, so the normal result
  wrappers take their no-copy/error branches; and
- caller-provided output lengths are clamped by the wrappers rather than used
  as lower FIFO block counts.

**Stage-7 conclusion:** no request-controlled software path was recovered that
returns stale ICU output across error, timeout, abort, or command replacement.
This is a bounded static negative, not a proof about impossible **hardware sequencing** behavior. `icus_command_finalize @ 0x89510` checks the ICU error/status result
but does not independently assert in software that every expected output block
was observed before accepting a hardware-reported clean completion. A hardware
fault or undocumented sequencing violation that reports success without the
specified output-ready events is therefore outside this software-static proof.

Deterministic coverage is in `tests/verify_icus_stage7_static.py` and
`AssertIcusStage7Static.java`.

## 2026-08-13 — bank-1 diagnostic activation correction

The 2026-08-10 "whole-image activator closure" overreached. Its raw facts were
narrowly correct—there is no 32-bit CodeFlash pointer directly into
`0x69018..0x69041`, and the `FEBE508F` writer census is still exact—but those
facts do **not** prove the activator is unreachable.

The missing edge is a one-hop RoutineControl callback:

- the 19×12-byte callback table at `0x25804` has RID `0x100F` in row 8 and action
  pointer `0x8A782` at `0x2586C`;
- wrapper `0x8A782` directly `jarl`s `crypto_test_bank1_activate @ 0x69018` from
  `0x8A786` and returns success;
- paired precondition callback `0x8A768` is an unconditional-success stub;
- startRoutine is enabled for RID `0x100F` and consumes zero option bytes; and
- policy index 0 and corrected SID-`0x31` both permit sessions `1/2/3` with no
  SecurityAccess-level entry.

Consequently `31 01 10 0F` is the stock bank-1 activation request, including in
the default session. CAN `0x01B..0x01F` still cannot arm the bank by themselves,
but diagnostics plus those CAN inputs can reach the stock command-5 test path.
The direct-pointer census is retained only as a narrow structural fact. The
Ghidra rebuild now seeds both RoutineControl callback columns so the wrapper and
its direct call are persistent in the recovered graph.

## 2026-08-10 — application signing-proxy static boundary

The minimum application-resident command-5 architecture is now fully specified
from existing firmware components. The canonical engineering design is in
[sender-implementation.md](sender-implementation.md) §5. Static analysis does
**not** implement the persistent hook or claim live slot-4 command-5 permission.
The important software result is that no invented direct-ICU protocol is
needed: the stock harness at `0x68B42` already proves the serialized
command-5 argument/configuration shape, the foreground scheduler offers a
non-CH0 hook site, and the application has existing CanIf transmit machinery.

## Current conclusion

The useful **static software** questions in this report are now mostly closed, but the corrected service-object audit materially expands the application-side disclosure boundary. Repository-known gate material still provides arbitrary bootloader-context execution; additionally, stock SID `0x23` exposes 107,924 LocalRAM bytes and 29,952 DataFlash bytes without SecurityAccess, subject to explicit protected subranges. The application has a fully specified serialized command-5 path, and RoutineControl RID `0x100F` supplies stock diagnostic activation for bank 1. SECOC-069 now pins the stock caller to exactly 16 input bytes, while the configured SecOC authenticated domains are 7/12/36 bytes; CMAC length semantics therefore keep the unmodified diagnostic bank from being a direct production SecOC signer. Generated bytes at `FEBE51AA` remain inside an RMBA exclusion and are not returned, but SECOC-046 recovers a no-SA Dem/DTC side channel for the terminal negative state (`0x00D317`); command failure and compare mismatch are intentionally kept conflated, so this is not a byte-output or standalone equality oracle. The ICU result path still has no recovered software-controlled stale-output disclosure. Hardware-only behavior remains separate: live slot-4 command-5 permission, undocumented ICU commands, physical leakage, and fault-induced sequencing require dynamic work rather than another broad static pass.

## External references

These establish only public SHE/CSE command numbering, not Renesas ICU-S
semantics:

- Bk2ol, `tsk_extraction_by_can_log`, payload source/toolchain at commit
  `db45375`: <https://github.com/Bk2ol/tsk_extraction_by_can_log>
- NXP, *Using the Cryptographic Service Engine (CSE)*, AN4234:
  <https://www.nxp.com/docs/en/application-note/AN4234.pdf>
- NXP, *Getting Started with CSEc Security Module*, AN5401:
  <https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/S32K/3002/1/AN5401.pdf>
