# F33 EPS incident: offline recovery-path audit, 2026-09-11

## Result and scope

**No working CAN-only repair was established. The earlier claim that all
network-only recovery routes were closed was broader than the evidence.** This
pass resolves specific missing paths rather than inferring impossibility from
diagnostic silence or a function-name census.

The work used the exact `8965F3307000` stock CodeFlash, the recorded malformed
hook, target-native Ghidra output, raw RH850 disassembly where Ghidra had no
function, and the Renesas P1M-E hardware manual. The vehicle was off. No vehicle
connection, CAN transmission, ECU reset, RAM upload, or flash operation occurred.
The reconstructed instruction is an offline interpretation of the recorded
write; it is not a new post-incident whole-flash readback.

### Sources and reproduction

- Firmware: `firmware/camry-8965F3307000/CodeFlash.bin`, VA equals file offset.
- Existing incident observations: `targets/camry-2026/raw-20260911/eps-recovery/`.
- Raw structural extraction: `data/generated/camry_f33_recovery_structure.json`.
- Manufacturer: `REFERENCE/r01uh0585ej0120_manual.pdf`, **RH850/P1M-E Hardware
  Rev.1.20**, printed pages 215, 219–220, 244–250, 257, 261, 2530, 2860–2861,
  and 2867. The address-space, operating-mode, ECC and MPU tables were also
  visually checked in rendered pages, not just text extraction.
- Manufacturer cross-check: **RH850/P1M-E Datasheet R01DS0505ED0100**, pp.1–2,
  master/checker lockstep and the R7F701381 product row.

Regenerate the compact structural report without Ghidra, Docker, or ECU access:

```sh
uv run python tools/targets/camry/analysis/analyze_f33_recovery_structure.py \
  --output data/generated/camry_f33_recovery_structure.json
```

The extractor reports actual bytes and fixed table values; it is **not** an
execution emulator or an exhaustive computed-call proof. For raw disassembly,
use `v850-elf-objdump -D -b binary -m v850e3v5` with the slice's correct VMA.
`-m v850:rh850` alone misdecoded several E3 instructions in this pass and was
not used for the conclusions below.

## 1. The hook's guard does not provide an external off switch

The malformed instruction is inside `0x7A254`, not the first instruction of
the main loop. The caller tests `uint16(FEBE3DF2) == FE01`. That initially looked
like a possible way to retain diagnostics while avoiding the hook.

Exact initialization `0x7A132` starts that state at `FD02`, runs the communication
initializers, and unconditionally stores `FE01` at `0x7A184`. The recovered
references to this cell are the two initialization writes and the checks in
`0x7A232` and `0x7A254`. No normal CAN-controlled setter was recovered. Failing
to complete initialization does not create an independently initialized
recovery server.

Source: `0x7A132..0x7A188`, `0x7A258..0x7A261`, and the canonical data-reference
owners of `FEBE3DF2`; the actual guard and terminal assignment are in the JSON.

## 2. Reception can precede the fault; service execution is later

The previous wording “before the CAN/DCM service becomes functional” conflated
reception with request execution. The order inside `0x7A254` is:

```text
7BE3C → 7BBC2 → 7C43C → 79EDE → [malformed call at 7A272]
```

`0x79EDE → 0x809FE → 0x808D6 → 0x80884` can drain received frames before the bad
call, subject to its ordinary initialized-state/ring conditions. This is a
static ordering result, not proof that a particular incident request arrived
in time.

The exact owner-0 table at `0x21A24` dispatches six callback classes. Class 2
is the diagnostic path: records at `0x21FA0` contain `7A1`, `777`, and `7A0`;
the callback is `0x79DB0`. Class 5 leads to XCP staging. The other two special
class slots, 3 and 4, resolve to `0x814AC`, a literal `jmp [lp]` stub. Class 1
has an empty configured owner-0 range.

The diagnostic receive chain was followed beyond the transport label:

```text
81200 → 79DB0 → 7A57A → 7A4E4
      → single-frame handling 7ADF8 → 7AD96
      → PDU routing tables → adapters 7BE58 / 7BE6C / 7BE90
      → DCM 920BE / 92152 / 921D2
```

All three configured transport channels converge on the same upper callback
family. `0x920BE` allocates/starts reception; `0x92152 → 0x93DE8` copies the
request. On successful completion, `0x921D2 → 0x91F72 → 0x92B4A` initializes
request state and writes `FEBE5964 = 10` through `0x92A86`. Timer arming through
`0x98B3A` writes deadlines/state. `0x989EC` appends an event to a ring; it does
not execute the event inline. These paths prepare a request, not an immediate
programming handoff.

The ordinary foreground ordering is independently present in raw calls:

```text
667EE: call 7A254     # malformed call is inside this aggregate
667F2: call 988C2     # normal diagnostic processing
667FA: call 58B5E     # normal system-mode processing / handoff
```

`0x988C2` runs `0x91FBE`, the timer worker `0x98AE4`, and event worker `0x98946`.
The actual application-to-boot call is `0x65F5E → 0x9F00`. Its recovered caller
is `0x56CF6`, reached through `0x5F464/0x5F91C` from `0x58B5E` for the
programming system-mode band. Thus both request processing and the eventual
handoff depend on work after the corrupted call. No boot handoff was recovered
in the reviewed receive-completion path.

**Consequence:** pre-queuing a request, suppressing its positive response, or
choosing another of these diagnostic addresses does not remove the recovered
execution dependency. The failed catcher's faster session ladder is not a
firmware-supported repair procedure.

## 3. Missing interrupt functions were reviewed from raw instructions

The stored 6,065-function corpus does not define every real interrupt entry or
callback. Missing functions included transport adapters used above. This makes
“not in the recovered function graph” insufficient as a negative result.

The nine distinct non-default targets referenced by the reviewed application
interrupt slots were decoded directly:

| Target(s) | Recovered continuation |
|---|---|
| `713B0`, `7145A`, `71506` | Context/stack wrappers reaching `65FAE`, `65FEA`, `66026` and their three periodic task aggregates |
| `660BE`, `66100` | `66806 → 8583E` and `66812 → 83F30` peripheral service paths |
| `66142`, `66184` | `88700/88726`, a guarded driver callback through `FEBF1194` |
| `661C6` | `79316`, flash-operation completion handling |
| `71AE4` | ECM error handling, selected error handlers, or reset fallback |

The `FEBF1194` installers select fixed driver callbacks (`880E0`, `888D0`,
`88D04`, `89114`) with complement guards; initialization also clears the cell.
They did not reveal an alternate diagnostic interpreter or boot handoff.
The periodic communication path `667B6 → 7A232` is separate from the poisoned
foreground aggregate, but its reviewed children are peripheral/ring maintenance,
not the normal DCM worker.

The canonical direct callers of `988C2`, `98946`, `58B5E`, and `667E6` remain
the foreground chain above. A whole-image literal-pointer check found no ROM
function-pointer occurrence for those four entries. This strengthens the
specific dependency; it does not prove absence of arbitrary computed aliases
or unmodeled execution. Adjacent non-vector data was not counted as interrupt
handlers.

## 4. The exact post-branch exception was not captured

The recorded four bytes plus the untouched next halfword decode as:

```text
7A272: FF 02 92 5B 24 36   JARL 362BFE04, LP
```

Hardware manual Table 4.1 places that destination in reserved address space.
It is not the intended resident address. However, a reserved address alone is
not sufficient to declare a specific live exception vector or reset cadence.
There is no post-incident PC/FEIC/FEPC capture.

The exception paths are not all identical. Most application direct vectors
point to `0x62E1E`, which saves context, enables EI interrupts, calls the save
helper `0x712CE`, and loops at `0x62E42`; it does not start boot diagnostics.
The direct vector at `0x20090` instead targets `0x65BD4`, which restores saved
`FEPC + 4` and returns with `FERET`, rather than returning through `LP` or
entering the bootloader. Neither should be described as an automatic return to
the instruction after the malformed call.

In particular, the firmware's MPU region 0 spans `00000000..FEBDFFFF` and has
attribute `B8` in both recovered contexts. It geometrically includes the bad
destination and grants supervisor execution for the matching ASID. An
out-of-CodeFlash address therefore does not by itself prove an MPU instruction
violation. Physical reserved-region behavior, privilege/ASID state, and the
actual exception remain distinct questions.

**Consequence:** hardware activity or an interrupt can survive a foreground
failure without supplying an operational diagnostic server. Conversely, the
failed identity requests alone do not prove every peripheral or interrupt is
dead. An exact fault-state model remains a legitimate unresolved part of the
incident, not an established recovery route.

## 5. Boot selection is more than CRC, but not a crash counter

Cold startup `1B0 → 1404 → 13B0` was checked in raw bytes. Earlier BIST/ECM
failure branches lead to sentinel writes and halt loops, not a hidden CAN
programming window. Cold C initialization clears the upper LocalRAM region
before reaching `0x13B0`; an old volatile boot request cannot simply be assumed
to survive this path.

At `0x119E`, the boot choice depends on descriptor/CRC checks, flash-error state,
and the two `5AA5A55A` validity markers at `FFE00` and `17E00`. If those checks
succeed, the boot code calls the entry stored at `FFDB8` (`20880`) without first
running the bootloader's normal CAN diagnostic loop. The known bad hook was
written with a valid application CRC, so CRC integrity does not detect its
incorrect control flow.

The separate check at `0x115A` reads `FFC62030` and tests bits 0 and 2. Renesas
identifies that register as **UCFDERSTR**, the CodeFlash double-bit-ECC/address-
parity status register; it is cleared through `FFC62008`. It is **not RESF**, a
failed-start counter, or a software-selected recovery flag. An erroneous branch
is not evidence of a flash ECC/parity fault. No recovered normal CAN request
sets a boot recovery latch before the malformed call.

## 6. Independent ROM, core, and XCP alternatives

The MCU's two G3M cores are a master/checker **lockstep pair**, not two independent
application processors with separate diagnostic servers (manufacturer datasheet
pp.1–2; hardware manual p.250). This does not rule out another processor
elsewhere in the steering assembly; its existence, wiring, and ability to
recover this target would require independent evidence.

The manufacturer documents serial programming selected by hardware mode pins
at pin-reset release. Its documented transports are one-wire UART, two-wire
UART, and CSI (hardware manual pp.261 and 2867), not a CAN-ROM listener available
merely because the application stopped. No network-controlled entry to that
mode was established. This is not a claim that every possible board-level
programming arrangement is known.

Stock XCP remains disabled by the fixed CodeFlash byte `30D68 = 5A` before
protocol dispatch (`821D6 → 830C0 → 98E80`). Receiving bytes through `8312E →
830D0` into `FEBE4C34` does not execute XCP commands. Its ordinary service path
also lies after the corrupted foreground call. It is not a recovery writer in
this state.

## 7. Pre-fault memory-safety audit: one real stale-DLC defect, no recovered write primitive

The recovery-specific memory-safety pass widened the executable surface beyond the
foreground `79EDE` drain.  Exact F33 has a real RSCFD interrupt path that can run
independently of the doomed `667E6 -> 7A254` foreground aggregate:

- RFIFO receive: `71508 -> 66026 -> 667B6 -> 7A232 -> 79EBA -> 83CE4 -> 83EDA -> 83E0C`;
- diagnostic CFIFO receive: the `66812 -> 83F30 -> 83EF2 -> 83EDA -> 83D40` path;
- RSCFD error handling also has a separate interrupt stub at `66806`.

That matters because a corruption primitive in these paths would not need the DCM
foreground worker to run first.

The audit found one genuine low-level memory-safety defect.  F33 writes
`RSCFD0CFDGCFG = 0xFFFF0020`.  P1M-E `RSCFDnCFDGCFG` semantics decode bit 5
`CMPOC=1`, bit 2 `DRE=0`, and bit 1 `DCE=0`: an oversized receive is stored while
payload bytes beyond the configured FIFO storage are discarded, the received DLC
is retained, and DLC checking is disabled.  F33's exact DLC table at `22E28` is
`0,1,2,3,4,5,6,7,8,12,16,20,24,32,48,64`.

This composes badly with Toyota's receive helpers:

- ordinary/XCP rule traffic routed to RFIFO1 uses eight 32-bit payload words, or
  32 physical bytes, but can propagate logical DLC 64 through `83E0C`;
- the diagnostic CFIFO reader `83D40` initializes only two 32-bit payload words,
  or 8 physical bytes, while likewise propagating logical DLC 64.

A DLC64 frame can therefore cause the software queue producer to read stale,
uninitialized bytes from the ISR's 64-byte local payload object: up to 32 bytes on
RFIFO1 and up to 56 bytes on the diagnostic CFIFO.  This is a **verified stale
ISR-stack ingestion/source-over-read condition**.  The present evidence does not
prove tester control of those stale bytes; RFIFO and CFIFO reach their leaf readers
through different call depths, so equal local layouts do not establish a reusable
physical stack slot.

The defect does **not** currently cross a recovery-relevant consumer boundary:

- the exact 48-entry class-0 COM table has maximum configured PDU length 32, and
  `7D72C` copies `min(received_len, configured_len)`;
- `830D0` rejects XCP input lengths above its configured 8-byte staging cap before
  copying to `FEBE4C34`;
- ISO-TP dispatch reads PCI byte 0 before selecting a handler; SF/FF/CF validation
  rejects oversized diagnostic descriptors before phantom bytes are consumed, and
  FlowControl accepts `len >= 8` but only reads bytes 0..2;
- `92152 -> 93DE8` copies into one of three fixed 0x100-byte DCM buffers only after
  `chunk_len <= remaining` succeeds; `93C9A` reloads those pointers/capacities from
  fixed CodeFlash configuration (`FEBE5651`, `FEBE5751`, `FEBE5851`).

The software RX ring does not turn the over-read into an overwrite.  Controller 0
has `DAT_21966 = 0x228` **words** of capacity; its fixed backing store is
`FEBE4038..FEBE48D7`, and a logical 64-byte record consumes 19 words.  The ring
uses 16-bit word indices and its mutation is wrapped by
`7A2DA -> 98B8A -> 6A45E`, which saves IMSR and installs mask `0xFF00`, with
`7A2E8 -> 6A4C4` restoring the prior mask.  The outer RSCFD ISR may enable nested
interrupts, but these queue updates are explicitly serialized.

Two additional write/pivot-looking cases also close under exact configuration:

- `85112 -> 8549E` indexes byte-length tables at `2345A/2349B` before copying to
  a 64-byte local.  The complete reachable input domain is 0..64; `2349B` rounds
  each length to a four-byte boundary and has maximum 64.  There is no valid-RX
  stack overflow here.
- `80884`'s six-way indirect callback mask is not supplied by payload bytes.
  `80B42` loads it from the fixed 47-byte per-acceptance-label table at `219DC`;
  the masks are `1` for normal rules 0..42, `4` for diagnostic rules 43..45, and
  `0x20` for XCP rule46.  The six callback targets themselves are the fixed
  CodeFlash vector at `21A24`.

The remaining transport/route pointer stores likewise reduce to small fixed RAM
islands.  `7A5C2/7A620` can return only exact configured 0x20-byte transport
records whose `record[1]` state indices are `{0,2}` inside a three-slot state
block; therefore the strided `7B18A/7BB0E` destinations are configuration-derived,
not CAN-payload indexed.  Controller 0 has five exact route records at `21ACC`
with state indices `{0,1,2,3,4}`, confining `803B0/8043C/806A4/807D8` mutable
state to `FEBE48DA..48F5`, `FEBE4909..490D`, and `FEBE3E94..3E98`.

A separate computed-store audit then attacked the recovery targets directly.  The
Ghidra direct-call closure rooted at the pre-fault receive path plus RSCFD RX/error
interrupt stubs contains **151 functions / 275 STOREs** (268 computed STORE rows,
37 with statically recovered ranges).  The whole-image known-range store census
has 62 unique rows whose coarse ranges can touch `FEBE3DF0..3DF5` or any of the
recovered lower-RAM indirect-call source cells (`FEBE5628`, `FEBF0FD0`,
`FEBF117C/1180`, `FEBF1194/1198`, `FEBF131C/1320/1324`, `FEBF6B04`).
Intersecting those with the executable pre-fault cone still leaves exactly one
function, `8E7BA`; its real code checks `(index & 0xffff) < 0x60` and writes only
`FEBE5398..FEBE53F7`.  Thus the negative covers known RAM control objects as well
as the hook guard itself.

The coarse communication-manager hits that looked capable of reaching `FEBE3DF2`
also collapse under exact calibration dimensions: `DAT_2183C=1`, `DAT_2183D=0`,
`DAT_21864=2`, `DAT_21865=1`, and `DAT_21BE1=1`.  The route-slot writer base is
`FEBE3E80`; even an unrestricted u8 slot would end at `FEBE407E`, above the hook
guard and far below the `FEBF` callback cells.  The RSCFD pointer row used by the
parameterized `83xxx..85xxx` driver helpers resolves entirely to `FFD2....` MMIO
for the one configured controller.

Finally, the whole-image statically ranged STORE census has **zero** intervals
intersecting `FEBE1700..FEBE2020` (the dedicated interrupt/saved-context region
through the initial application stack), and zero through the broader
`FEBE0000..FEBE2200` lower-LocalRAM interval.  Combined with the bounded 64-byte
ISR locals, no recovered receive copy reaches the saved `EIPC/FEPC/lp` frames.

The result is therefore narrower than "the parser is safe": **we found a real
pre-fault memory-safety defect, but not the write primitive needed to recover the
ECU.**  The remaining software route must be an unrecovered destination-write or
control-flow side effect, not the obvious CAN-FD DLC/FIFO mismatch, standard
ISO-TP length handling, normal COM copy, XCP staging, or the recovered software
ring.

Canonical evidence:

- `data/generated/camry_8965F3307000_prefault_store_audit.json`
- `data/generated/camry_8965F3307000_prefault_memory_safety.json`
- `ghidra/scripts/investigate/AuditCallConeStores.java`
- `tests/verify_camry_8965F3307000_prefault_memory_safety.py`

## 8. Expanded pre-fault control-flow/reset audit: synchronous CAN ingress is bounded

The memory-safety pass in §7 attacked wire-controlled **STORE destinations**.  A
second pass widened the question to every other way a network event could avoid
the poisoned foreground: immediate reset, ECM/NMI routing, CAN error interrupts,
watchdog starvation, RSCFD DMA/DTS, payload-dependent indirect calls, synchronous
upper-layer callbacks, a legitimate communication-state transition, or a cold-boot
CAN race.

The executable denominator is now larger than the first store audit.  In addition
to the normal/XCP receive paths and CAN1 RX/TX/periodic service, the Ghidra closure
is rooted at all six resolved DCM transport callbacks (`920BE`, `92152`, `926D2`,
`921D2`, `92836`, `92946`).  The resulting cone contains **307 functions / 412
STOREs**; 366 STOREs are computed and 283 have a destination that is
intraprocedurally parameter-dependent.  A companion operation census sees **854
LOADs**, 20 indirect transfers, and exactly **five** parameter-dependent indirect
call sites.  There are **zero** integer divide/remainder operations in the cone.

The larger STORE census introduces coarse false positives in the DCM state family
(`93C6C/93C9A/93DE8/93E5C/93EF6/93F4E/9405C`) because a local range solver sees a
16-bit index multiplied by a stride.  The index is not arbitrary.  Exact `93F0E`
searches three configured external routes and returns only internal channel
`0/1/2` or `FFFF`; callers reject `FFFF` before using the strided helpers.  The
three external route IDs are **2, 3, and 4**.  This also corrects the previous
generated VAR-155 artifact's route labels, which had accidentally read the
ushort-stride table as a six-byte-stride table; the three 0x100-byte destination
buffers themselves were already correct (`FEBE5651`, `FEBE5751`, `FEBE5851`).

### 8.1 CAN/ECM errors do not provide a reset interrupt

Application ECM initialization first clears all three maskable-interrupt, NMI,
and internal-reset configuration words (`63338`).  `63738` then enables exactly
`ECMMICFG0 = 0x100B001E`, i.e. sources `{1,2,3,4,16,17,19,28}`.  P1M-E's
RS-CANFD-related ECM sources 22 (uncorrectable CAN RAM ECC), 37 (peripheral RAM
ECC address-overflow, including RS-CANFD), and 54 (correctable CAN RAM ECC) are
therefore not routed to the application ECM EIINT, NMI, or ECM internal reset.

The interrupt table contains a useful-looking default CAN error entry at
`0x62E1E`: it saves context, enables nested EIINTs, calls `712CE`, and ends in a
permanent self-loop at `62E42`.  But exact interrupt-controller configuration
makes it unreachable from ordinary CAN errors.  CAN1 error EIINT186 and global
CAN error/RFIFO EIINT189/190 are masked (`0x80CF`); only CAN1 RX/TX EIINT187/188
are enabled as table-reference priority-8 interrupts (`0x8048`).

The controller settings independently agree.  CAN1 enters operation with
`CCTR=0x00A00001`: `BOM=01`, so bus-off entry autonomously places the channel in
halt mode, but `BEIE/EWIE/EPIE/BOEIE/BORIE/OLIE/BLIE/ALIE/TAIE` and the remaining
channel-error interrupt enables are all zero.  Global `GCTR=0x00010001` likewise
has `DEIE/MEIE/THLEIE/CMPOFIE=0`.  A hostile bus participant can therefore force
bus-off/halt, but not the default non-returning CAN error ISR.  The software
channel-recovery state machine is reached only later at `7A254 -> 79F16`, **after**
the malformed transfer, while the independent `7A232` service path does not
restart the halted channel.  Transmit-abort does not create a side door either: its
interrupt is gated by `TAIE=0`.

### 8.2 Watchdog starvation and RSCFD DMA do not bridge the gap

The exact 1-MiB CodeFlash corpus has **zero references** to WDTA0's MMIO block
`FFD74000..FFD7400C`.  `WDTA0TERR` is ECM source 0, and source 0 is absent after
the application clears IRCFG/NMICFG/MICFG and installs `0x100B001E`.  The flash
option bit controlling automatic WDTA startup is outside the retained
CodeFlash/DataFlash dumps, so its boot value remains explicitly unknown; the
running application nevertheless exposes no recovered watchdog-service/starvation
reset path.

Hardware-initiated memory transfer is also closed for CAN.  RS-CANFD's DMA/DTS
request control is `CFDCDTCT @ FFD20490`, pointed to by exact configuration at
`2309C`.  Its only application writers are `8488C` and `84E16`, and both write
zero; `84C2C` treats a nonzero low16 value as a configuration mismatch.  CAN FIFO
events therefore cannot bypass the CPU STORE bounds by triggering an RSCFD DMA/DTS
transfer.

### 8.3 Every synchronous accepted-frame callback is bounded

The five parameter-dependent indirect call sites are finite and configuration
bounded.  Three are the already-closed CanIf callback selectors at
`80884/810F2`.  `81938` and `81D30` split a 16-bit PduR ID into
`group=id>>11` and `index=id&0x7FF`, require `group < 12`, and then require the
index below that group's configured count before reading the callback.  No payload
byte becomes an unchecked function-pointer selector.

The normal receive map can now be stated exhaustively.  Rules 0..42 feed PduR IDs
5..47.  Exactly three accepted protected IDs enter SecOC synchronously:
`0x00F` (rule4), `0x0D7` (rule36), and `0x0B6` (rule39).  The other **40 accepted
CAN IDs** all select raw-COM callback `7D72C`.  Every configured PDU record 5..47
has selector 0 and flags `0x0C`; none sets the `0x10` optional pre-copy-hook bit.
Consequently raw COM performs only its bounded copy/state update and calls
`8E772`, which for `PDU<0x60` clears one status byte and increments one generation
byte.  Signal unpacking and application control state machines occur later in the
foreground and never execute synchronously from ingress.

The other accepted classes stop even earlier: protected traffic is queued for the
later SecOC consumer, diagnostics mutate only the bounded DCM transport/event
state, and XCP reaches its staging buffer but not command dispatch before the
poisoned foreground call.

### 8.4 The guard has no runtime off writer, and valid cold boot has no CAN race

`FEBE3DF2` has exactly **two writers in the image**, both in one-time startup
`7A132`: `FD02` at `7A13A`, then `FE01` at `7A184`.  `7A232` and `7A254` only
read it.  Thus there is no legitimate asynchronous communication-disable state
transition we can provoke after startup.  At `7A254`, the sole guard branch at
`7A260` skips the whole aggregate when the value is not `FE01`; once it is `FE01`,
`79EDE` returns directly into the malformed six-byte sequence at `7A272`
(`80 FF EE 1C 24 36`) with no intervening conditional branch.

A power-cycle CAN race is unavailable for the same structural reason.  `13B0` runs
the descriptor/CRC/marker decision first.  A valid application result calls the
entry pointer at `FFDB8` (`0x20880`) directly.  The bootloader CAN stack
`1398 -> 1338 -> 3B3C` is initialized only on the validation-failure branch.
Continuously transmitting programming/session traffic during an ordinary power
cycle therefore has no listener to catch while the current CRC-valid application
is selected.

The combined result is stronger than §7 alone: **no recovered network event can
write the guard, invoke an attacker-selected synchronous callback, route a CAN
error into reset/fault handling, trigger CAN DMA, starve a recovered watchdog reset,
or hold the stock bootloader before the CRC-valid application starts.**  The exact
post-`7A272` exception context remains unobserved, and mechanisms outside the
retained firmware/hardware configuration (board-level reset/debug/serial paths,
unrecovered silicon behavior, or undiscovered hardware state) remain the honest
boundary.

Canonical evidence:

- `data/generated/camry_8965F3307000_prefault_control_flow.json`
- `data/generated/camry_8965F3307000_prefault_control_flow_store_audit.json`
- `data/generated/camry_8965F3307000_prefault_control_flow_ops.json`
- `ghidra/scripts/investigate/AuditCallConeMemoryOps.java`
- `tests/verify_camry_8965F3307000_prefault_control_flow.py`

## What is established, and what would actually change the answer

The direct, functional, and subaddressed diagnostic paths examined here do not
supply a stock recovery entry independent of the blocked foreground work.
The documented ROM programming mode is a different interface, not another
CAN session. No vehicle experiment is justified by simply making the previous
catcher faster or adding guessed messages.

A useful new lead must establish an entry that **does not depend on returning
from the corrupted foreground call**: an actual independently operating
manufacturer recovery mechanism, or concrete evidence that the post-fault
execution model differs in a way that reaches a legitimate recovery service.
The unknown precise fault state, unacquired on-chip ROM/extended-region content,
and unverified assembly-level connections must remain explicit unknowns; they
are neither working recovery methods nor grounds for an absolute impossibility
claim.

The inverse hook operation and the last pre-hook image are already known, but
having repair bytes does not establish a way to execute the repair. The
pre-hook stage-6 image contains earlier modifications and is not an untouched
factory image. Removing this one hook would not, by itself, certify the
steering software or the vehicle as safe to drive.
