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
