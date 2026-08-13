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
> analysis in `build/project/`; existing reports are navigation aids, not proof
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
| Application UDS memory services | ISO-TP request | read/write ICU driver RAM or install code | bounded negative | SID `0x23` is a null-callback response; no application memory handler |
| Application download/transfer | ISO-TP request | executable RAM or CodeFlash foothold | bounded negative | SIDs `0x34/0x36/0x37` are null-callback responses |
| Bootloader payload path | bootloader UDS plus recovered gate material | arbitrary bootloader-context RAM callback; potential persistent application harness | recovered capability; ICU use untested | accepted 4 KiB image controls callback at `FEBF0FD0`; more than `0xE00` fixture space remains |
| Service `0xAB` | UDS RID payload | indirect arbitrary call/write | bounded by prior branch census; semantics incomplete | no sensitive direct/jump-register targets in 13 callback pairs; shared state machine remains long-tail work |
| WDBI DID `0x1010` | 64-byte opaque package | corrupt command-8 staging or async result banks | bounded for request/copy sizes | exact 67-byte total request and fixed 49-byte result contract; semantic command abuse remains possible |
| Normal CAN/ISO-TP parsers | CAN frames | overflow/index corruption | bounded at application transport layer | declared length is capped by 256-byte Dcm route buffers; each fragment is checked against remaining length |
| Dormant crypto-test bank | CAN `0x01B..0x01F` plus state | command 5/7 oracle and output | strong bounded static activation negative | no external x-ref to entry/interior, no CodeFlash pointer into the 42-byte activator, and only the activator writes active value `1`; external debug/hardware activation is not excluded |
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
- Opened only the disposable `build/project/` through the repository's isolated
  V850 extension environment. That dated investigation used the then-current
  5,921-function graph; the corrected 2026-08-11 rebuild now has 6,037
  functions and the affected negatives were rerun separately.
- The first bridge attempt used the default Ghidra user home and failed before
  loading the program because `v850e3:LE:32:default` was unavailable. Retrying
  with `-Duser.home=build/ghidra-home` loaded the expected processor module.

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
| crypto-test inputs `0x01B..0x01F` | normal PDU route | dormant bank collectors | activation reachability audited separately |

### 2026-07-28 — dormant crypto-test and ICU callback state

- `crypto_test_bank1_activate` (`0x69018`) initializes active byte `FEBE508F`,
  state `0x11`, input/result banks, and update-counter snapshots. Ghidra finds no
  call xref or CodeFlash function-pointer xref to this activator.
- The complete `FEBE508F` xref set contains the activator, initialization/reset
  clear at `0x67FCE`, periodic reads, and terminal finalize writes. The normal
  CAN collector does not set the active byte. Thus `0x01B..0x01F` cannot arm the
  harness by themselves in the recovered stock graph.
- Once active, CAN inputs can select a software key selector, 16-byte message,
  and 16-byte expected result. Mode 1 reaches command-5 generation and stores 16
  generated bytes at `FEBE51AA`, but stock logic only compares them locally and
  exposes pass/fail state; no byte-output transport was recovered.
- ICU interrupt channels 292/293 call RAM pointer `FEBF1194` only when its
  complement at `FEBF1198` matches. All recovered writers install fixed
  CodeFlash start/completion functions and their literal complements or clear
  the pair. No request-derived callback address was recovered.
- Higher crypto dispatchers select lower adapter pointers from CodeFlash driver
  records after bounds lookup; caller-controlled fields are selectors and data
  buffers, not adapter function addresses.
- **Implication:** a pre-existing arbitrary call can invoke `0x69018` or the
  command-5 dispatcher, but the dormant harness does not independently create
  that primitive. An application-resident hook can bypass the dormant bank and
  call the initialized wrappers directly.

### 2026-07-28 — application memory/write/download services

- Raw 24-byte service records show application SIDs `0x23`, `0x34`, `0x36`, and
  `0x37` have null service callbacks and no subfunction processing flag. The
  dispatcher at `0x8F850` therefore reaches the generic response body `0x8F6FA`
  rather than a memory-range or transfer worker. These are not application
  memory/download implementations in this image.
- The 19-entry WDBI table is index-bounded before selector dispatch. Generic
  parser `0x95624` computes the exact configured input width and requires
  equality with the request length; `0x956C6` independently checks response
  capacity. CodeFlash descriptor evaluation gives a maximum configured input of
  64 bytes (DID `0x1010` selector 1), or 67 bytes including selector and DID.
- Eighteen selector-1 WDBI wrappers call one bounded generic operation with a
  literal table index. DID `0x1010` is the sole distinct wrapper and passes fixed
  lengths `0x40` input / `0x31` status-result to the ICU key-update operation.
- **Bounded negative:** no application arbitrary-address read/write/download
  service or WDBI request-length overwrite was recovered. This does not yet
  cover semantic abuse of individual operations, asynchronous-state races, or
  corruption originating outside the diagnostic parser.

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

Temporary function seeding in `build/project/` recovered command 11 as a
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

## 2026-08-10 — dormant bank-1 activator closure

The former "no caller" observation for `crypto_test_bank1_activate @ 0x69018`
is now a whole-image static reachability result:

- Ghidra has no external code or data reference to `0x69018` or any interior
  instruction in `0x69018..0x69041`; the sole interior reference is the
  activator's own conditional branch `0x69022 -> 0x6903E`;
- a bytewise scan of all CodeFlash finds no little-endian 32-bit pointer to the
  entry or any interior address, covering ordinary function-pointer tables;
- the complete `FEBE508F` reference set has exactly three writers: startup
  initialization `0x68006` clears it, the activator `0x69026` writes active
  value `1`, and `crypto_test_bank1_finalize @ 0x68D0E` writes terminal state
  `0x02` or `0xFF`; no second function emulates activation;
- the periodic test-bank step/finalize functions are genuinely scheduled by
  foreground wrapper `0x65750`, but both merely consume an already-active bank;
  and
- registered command-5/7 test completion callbacks exist elsewhere in
  CodeFlash tables, demonstrating that the absence of an activator pointer is
  not a generic failure to recover callback tables.

Thus normal CAN `0x01B..0x01F`, startup/lifecycle code, and recovered static
function-pointer dispatch cannot arm bank 1. A debugger, fault, runtime memory
corruption originating from an as-yet-unknown primitive, or other hardware
mechanism could still set `FEBE508F=1`; those are not disproved by static
reachability.

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

The useful **static software** questions in this report are now closed. Repository-known gate material still provides arbitrary bootloader-context execution, and the application has a fully specified serialized command-5 proxy architecture. The dormant stock bank has no recovered static activation route, and the ICU result path has no recovered software-controlled stale-output disclosure. Hardware-only behavior remains separate: live slot-4 command-5 permission, undocumented ICU commands, physical leakage, and fault-induced sequencing require dynamic work rather than another broad static pass.

## External references

These establish only public SHE/CSE command numbering, not Renesas ICU-S
semantics:

- Bk2ol, `tsk_extraction_by_can_log`, payload source/toolchain at commit
  `db45375`: <https://github.com/Bk2ol/tsk_extraction_by_can_log>
- NXP, *Using the Cryptographic Service Engine (CSE)*, AN4234:
  <https://www.nxp.com/docs/en/application-note/AN4234.pdf>
- NXP, *Getting Started with CSEc Security Module*, AN5401:
  <https://community.nxp.com/pwmxy87654/attachments/pwmxy87654/S32K/3002/1/AN5401.pdf>
