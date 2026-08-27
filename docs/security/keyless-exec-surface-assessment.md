# Keyless execution surface assessment

> **Target:** all tracked EPS images — Sienna `8965B4512000`, albinoelephant
> Corolla `8965H1202000`, Span Corolla `8965F1208000`.
>
> **Question:** is there an attacker-controlled arbitrary-code execution path
> that requires **no key material at all** — neither boot SecurityAccess nor the
> authenticated-payload secret — and therefore remains useful if a future EPS
> generation rotates both roots?
>
> **Status:** no software-only keyless execution path is recovered in the
> tracked images. One important keyless **credential-recovery** path is now
> verified: the application SecurityAccess root is copied into a pre-auth
> readable LocalRAM mirror on all three images. This does not bypass the
> independent boot SecurityAccess gate. The follow-up audit closed retained
> TransferData state, RequestDownload pre-SA side effects, CTBP retention,
> alternate credential-read engines, the 18 Corolla boot residuals, the
> effectively-keyless application-SA surface, live-handoff DMA state, and a
> target-native H computed-control-flow census. These are **mechanism-specific**
> closures, not a claim that all software-visible static avenues have been
> enumerated. Static parser/dataflow, copy-sink, state-composition, and variant-
> specific searches remain valid work; CORR-101 records the correction after a
> fresh re-audit found additional unaudited application transport and formatter
> surfaces. Deterministic regressions are
> `tests/verify_keyless.py` and
> `tests/verify_keyless_live_handoff_dma.py`; the fuller Sienna no-auth control-
> flow audit remains in
> [bootloader-noauth-pc-pivot-assessment.md](bootloader-noauth-pc-pivot-assessment.md).

## 0. Security boundary

The recovered authenticated RAM-execution chain has two independent secrets:

1. boot UDS `0x27` SecurityAccess, rooted at CodeFlash `0xBFE8`; and
2. the payload CMAC/KDF root at CodeFlash `0xBFD8`.

The second secret never substitutes for the first. In Sienna
`uds_request_download @ 0x5D68`, the request is parsed and range-checked, but
before useful download state is committed the handler reads boot SA state
`FEBF2B0F` and requires value `2`; otherwise it returns NRC `0x33`
(`securityAccessDenied`). The complete RequestDownload body transfers
byte-for-byte to both Corolla images at `0x5D4C`, so the same gate applies
there. RoutineControl is likewise SA-gated.

Therefore a valid/prebuilt authenticated payload fixture can replace knowledge
of the **payload-build secret only**. It still needs a valid boot-SA unlock (or
an independent boot-SA bypass) before `0x34`/`0x31` can use it. If a future
part rotates both roots and supplies no accepted fixture plus no SA solution,
the current authenticated bootstrap is lost.

## 1. Attack 1 — boot copy of the application XCP route descriptor (negative)

The application XCP route uses physical IDs `0x7F7`/`0x7F8` and packed route
records of the form `0x80000000 + (CAN_ID << 18) + attr`. A full scan of every
tracked boot region (`<0x20000`) for the exact application descriptor encoding,
in both byte orders, returns zero hits.

That result proves only that the **application's packed XCP route descriptor is
not copied into boot**. Descriptor absence alone is not a universal proof that
boot could not expose the same IDs through some different representation or
hardware route. The broader Sienna result comes from the separate boot ingress,
CanIf/dispatch, indirect-call, and retained-window consumer audit in
SEC-BOOT-013: that audit recovers no boot XCP/control-transfer consumer. H/Span
inherit the exact boot UDS handler cohort (§3), but the descriptor scan itself
must remain a descriptor-scan claim.

## 2. Attack 2 — RequestDownload interval wraparound (closed behind SA)

A 32-bit interval-wrap bug in `boot_memory_range_check_access` would be useful
*after* RequestDownload's other gates, but it cannot create initial keyless
reachability because RequestDownload itself requires boot SA state 2 as
explained in §0.

The range checker nevertheless has the correct explicit wrap guard. At Sienna
`0x32DA` and Corolla generation `0x32BE` (with a second identical occurrence
`+0x46`):

```text
32DA: add  r6,r7         c639        end = start + len
32DC: addi -0x1,r7,r18   0796ffff    end - 1
32E0: cmp  r18,r6        f231
32E2: bh   reject        ab1d        unsigned: start <= end-1 else fail
```

`start <= start + len - 1` as an unsigned comparison rejects a wrapped
interval. This is a real memory-safety bound and is pinned across all three
images, but it is **defense in depth behind SecurityAccess**, not the mechanism
that prevents unauthenticated RequestDownload writes.

## 3. Attack 3 — Corolla-generation boot UDS policy divergence (closed)

The Corolla-generation dispatch table at `0x8E34` is Sienna's table at
`0x8E54` with the same 20 records, SIDs, policy bytes, and every handler pointer
shifted by exactly `-0x1C`.

The transfer is stronger than table geometry alone. All 13 unique handlers
referenced by those 20 records are byte-identical at that relocation in both H
and Span: DiagnosticSessionControl, ECUReset, SecurityAccess,
CommunicationControl, TesterPresent, ControlDTCSetting, RDBI, the unsupported
service stub, WDBI, RoutineControl, RequestDownload, TransferData, and
RequestTransferExit. The SecurityAccess request-seed/send-key helpers and the
payload verification/decrypt workers used by the relevant paths also transfer
exactly.

This is sufficient to transfer the audited UDS gate behavior, including the
RequestDownload SA requirement. It does not transfer unrelated application
behavior or prove that every non-UDS boot ingress is identical.

## 4. Attack 4 — authentication state through the retained XCP window (closed)

Boot uses `GP = FEBF9800`, numerically inside the application XCP write window
`FEBF7C00..FEBFFBFF`. The relevant boot security state, however, is below that
window at negative GP displacements:

- `FEBF2B0F` — boot SecurityAccess state (`2` means unlocked);
- `FEBF2B55` — SecurityAccess request-seed/send-key handshake state;
- `FEBF2B24` / `FEBF2B34` — SecurityAccess seed/key work buffers;
- `FEBF2B11` — authenticated-region authorization bitfield used by the
  RequestDownload/RoutineControl flow;
- `FEBF2BDE` — payload-decrypt **queue/busy flag**, not an authentication latch.

The canonical Sienna non-flow reference graph has exactly one boot-context
reference into the XCP window: `FUN_00001404 WRITE -> FEBF7C00`. It is the
already-documented reset-startup clear-shaped loop whose end `FEBE7000` is below
its start, so the unsigned loop condition is false and the store body is
zero-trip. There are zero boot READ/PARAM references into the window.

The complete 116-byte startup body containing that zero-trip shape transfers
exactly to H/Span at `0x13E8` (`-0x1C`), and the security/download handlers that
access the state listed above also transfer exactly. Thus the known
application-XCP placement window does not overlap the recovered boot
authentication state on any tracked image. This closes the specific "flip SA or
payload-authorization state instead of finding a PC pivot" shortcut; it is not
a claim that every possible H/Span boot object has been globally recensused.

## 5. Alternate failure runtime

Failing the validity gate does not enter a new unaudited programming context:
the failure main loop `0x1398` is the programming runtime already covered by
SEC-BOOT-013 (see
`../architecture/boot-validity-and-flash-lifecycle.md` §4.1).

## 6. Reusable triage screen for future dumps

For a new RH850/P1M-E-family image, these four checks are useful early warning
signals:

1. **Boot route descriptor scan** — search boot for the application's packed
   diagnostic-route descriptors in both byte orders. A hit warrants immediate
   route/callback analysis; absence is only a descriptor negative.
2. **RequestDownload gate + interval guard** — verify both the boot-SA state
   check/NRC `0x33` and the unsigned wrap detector. A missing SA gate is much
   more important than a changed range-check shape.
3. **UDS table plus handler bodies** — compare both dispatch metadata and the
   actual referenced handler bodies. Table equality alone is not enough to
   transfer semantics.
4. **Writable-window/state intersection** — recover boot GP/state addresses and
   enumerate references into every tester-writable retained RAM window. Any
   new live READ/WRITE consumer or security-state overlap deserves direct
   control-flow analysis.

These checks are deliberately discriminators, not an exhaustive exploit search.
A future image that differs should be escalated into the full ingress,
indirect-call, lifecycle, and hardware-route audit rather than declared
vulnerable from one signature alone.

## 7. Keyless recovery of the application SecurityAccess root

The application SecurityAccess secret at CodeFlash `0x20840` is not actually a
secret from an unauthenticated application-side tester. Application startup
explicitly copies the 64-byte CodeFlash interval `0x20810..0x2084F` into
LocalRAM, and the final 16 bytes of that interval are the complete application
SA root. The destination differs by variant:

| image | startup copier | destination | application-SA mirror |
|---|---:|---:|---:|
| Sienna `8965B4512000` | `0x62662` | `FEBF7BB0..FEBF7BEF` | `FEBF7BE0..FEBF7BEF` |
| Corolla H `8965H1202000` | `0x5C9B6` | `FEBF7B50..FEBF7B8F` | `FEBF7B80..FEBF7B8F` |
| Corolla F `8965F1208000` | `0x5C9B6` | `FEBF7B50..FEBF7B8F` | `FEBF7B80..FEBF7B8F` |

The H/F copy body is byte-identical and the Sienna body differs only in the
LocalRAM destination immediate. This is firmware-static provenance for the
previously observed H/F RAM mirror; it is not an artifact of the authenticated
RAM-dump payload.

Both application-side memory readers can reach the mirror **before
SecurityAccess**:

- UDS SID `0x23` ReadMemoryByAddress is extended-session-only but has no
  configured SecurityAccess list on all three images. Its LocalRAM read class
  covers `FEBE0000..FEBFFFFF`, subject to the compiled exclusion intervals.
- XCP `SHORT_UPLOAD` (`0xF4`) is configured while XCP `GET_SEED`/`UNLOCK` are
  unconfigured. It applies the same LocalRAM exclusion policy.

The Sienna mirror at `FEBF7BE0` is above the final Sienna exclusion
`FEBF6C00..FEBF78DF`; the H/F mirror at `FEBF7B80` is above the final H/F
exclusion `FEBF6000..FEBF6CDF`. Therefore the complete 16-byte root is readable
without first knowing it. `SHORT_UPLOAD` has a 7-byte maximum payload, so the
root requires multiple reads there; SID `0x23` can return it in one request.

**Consequence:** rotation of the *application* SecurityAccess root does not, by
itself, strand a tester on this implementation if the startup-copy and read
policies remain. A future image should be checked for this copy before treating
an unknown application-SA key as a dumping/glitching requirement. This result
does **not** recover the boot-SA root at `0xBFE8`, does not set boot SA state
`FEBF2B0F`, and does not make boot `0x34`/execution RoutineControl keyless.

Deterministic proof is in `tests/verify_keyless.py`
(`KEYLESS-006`). The Sienna subsystem-level interpretation is also recorded in
[application-security-access.md](application-security-access.md).

## 8. Retained TransferData state does not skip RequestDownload

A second composition was checked explicitly: pre-position the application XCP
payload, carry boot download state across the live `10 02` handoff, and start at
`TransferData (0x36)` instead of the SA-gated `RequestDownload (0x34)`.

That fails because the normal programming-runtime initialization reinitializes
the DCM transfer state before requests are serviced. The live path is
`0x64EC8 -> 0x9F00 -> 0x148E -> 0x1398 -> 0x1338 -> 0x770 ->
0x69D2/0x6A22 -> 0x5086`. `FUN_00005086` writes boot SA state
`FEBF2B0F=1`, clears authorization `FEBF2B11`, active transfer state
`FEBF2B13`, payload-ready state `FEBF2B16`, and transfer status `FEBF2B17`.
`uds_transfer_data @ 0x4DBA` dispatches only when `FEBF2B13` has subsequently
been armed by a successful download setup.

The destination and remaining-length cells `FEBF2B00/04` are likewise reset and
are not recovered from application-retained data. The complete TransferData and
initialization cohort transfers to H/F with the established boot relocation.
`KEYLESS-007` pins the chain and state reset.

## 9. RequestDownload has a pre-SA near-miss, not a bypass

`uds_request_download @ 0x5D68` is slightly more subtle than a simple
"nothing happens until SA" description. On one request class it can perform
flash-operation setup and write transfer-status `FEBF2B17=2` before the final
`FEBF2B0F == 2` comparison at `0x5EFC`.

That side effect is not independently reachable from a locked bootloader. The
pre-SA branch first requires `FEBF2B16 == 1`. The complete writer census for
`FEBF2B16` has only boot initialization (`0x50AE`, writing zero) and boot WDBI
`0x4A76`, and that WDBI path has its own exact `SA == 2` gate at `0x49C6`.
Furthermore RequestDownload does not commit the attacker-supplied destination
and length (`FEBF2B00/04` at `0x5F1E/0x5F22`) until after the final SA check.
Thus the ordering is a real pre-SA side effect but cannot bootstrap a fresh
locked ECU into TransferData/programming. H/F carry the complete WDBI and
RequestDownload bodies at `-0x1C`; `KEYLESS-009` pins this prerequisite chain.

## 10. Live handoff CPU control state: CTBP is not attacker-retained

`0x9F00` explicitly establishes most boot CPU state: it disables interrupts,
masks them, writes fixed PSW/EBASE/INTBP values, installs boot SP/GP/TP, and
sets `MPM=0`. It does not itself write CTBP, so the retained CALLT base was
audited separately rather than assumed safe.

Across all three images the raw instruction `ldsr r0,CTBP` occurs exactly once,
at reset startup `0x25E`. There is no application CTBP writer. Therefore the
live application-to-boot handoff inherits `CTBP=0`, not tester-selected state.
The Sienna boot CALLT at `0x1D5C` uses selector `0x22`; with CTBP zero the table
entry is the fixed CodeFlash halfword at `0x44`, target `0x1E1E`. H/F relocate
the call site to `0x1D40` and the table target to `0x1E02`, exactly `-0x1C`.
This closes the otherwise plausible "retain a system-register call-table base"
pivot. `KEYLESS-008` pins the raw instruction/table facts.

## 11. Failed boot-SA computation does not expose a response-stack oracle

A deliberately wrong boot `27 02` does cause useful secret-dependent
computation internally: the handler forms a working key from the boot-SA root,
then computes the expected response before deciding the supplied key is wrong.
The AES context at `FEBF2D48` is wiped after use, while the working-key and
expected-response temporaries are stack-local.

Two exfiltration routes were checked. First, application startup clears/reuses
the relevant boot stack before application RMBA/XCP becomes useful. Second,
boot response construction does not hand stack pointers to the transport:
every recovered boot `Dcm_TransmitResponse` caller transmits from the fixed
DCM response buffer rather than an uninitialized stack-local response object.
Consequently the failed-key computation does not currently give a software-only
credential leak. This remains a useful pattern to recheck on a future bootloader
because a single uncleared global AES/key-schedule buffer or uninitialized
response copy would change the result.

## 12. Alternate read engines do not reach the boot roots

The application-SA leak in §7 prompted a second question: can another pre-SA
reader reach the two more valuable low-CodeFlash roots at `0xBFD8/0xBFE8`?
A command-by-command census closes that shortcut on all three tracked images.

For Sienna, XCP `SHORT_UPLOAD (F4)` and `UPLOAD (F5)` are LocalRAM readers after
range/exclusion validation. The F5 helper has a second CodeFlash class, but it
accepts only `0x10000..0x17DEF`; F5 itself is limited to 1..7 bytes, while the
special `0x7DEC` length belongs to the checksum path. `E4` is a fixed copy from
`0x10000..0x17DEF` to `FEBF7C00`, and `F3` uses the same CodeFlash interval.
DAQ pointer installation is LocalRAM-bounded before the sampler dereferences it.
Application SID `0x23` likewise has no active low-CodeFlash class. The boot
`0x10F3` compare/oracle and RequestDownload range table also begin CodeFlash at
`0x10000`; neither admits `0xBFD8` or `0xBFE8`.

H carries the same command classes with target-native handlers (`F5 @ 0x92462`,
`F3 @ 0x92576`, `E4 @ 0x92724`) and the same boot access-table geometry at
`0x8D80`. Its E4 copy is fixed to `0x10000..0x17DEF`. Span differs from H only
inside `0xA004..0x17DFF`, so its diagnostic/XCP code and boot access table are
byte-identical. Fixed application copy engines, DMAC descriptors, and the
P1M-E tuning-memory overlay were also checked; none provides a CPU-visible
flash-to-RAM alias for low CodeFlash. Thus no recovered pre-SA reader discloses
the boot-SA or payload-build root. This is `KEYLESS-010`; the underlying command
bounds are independently pinned by the XCP, RMBA, payload-gate, and Corolla
variant suites.

## 13. Corolla H/F boot residuals do not add a keyless primitive

The broad boot transfer in §3 left 18 functions that were not simple bodies at
the dominant `-0x1C` relocation. They have now been closed individually. H and
F are byte-identical through `0xA003`, so the complete residual disposition is
shared by both specimens.

The differences are startup/peripheral/linkage changes: the default exception
thunk relinks `0x1E1E -> 0x1E02`; cold startup moves TP
`0x869C -> 0x867C`, changes PSW/EIPSW/FEPSW `0x18020 -> 0x8020`, zeroes FPIPR,
and removes the Sienna FPU-init block; CSIH moves to the target's other
peripheral instance; EIC/TAUJ helpers are exact or direct re-links; the RAM
configuration copier moves its immutable source table `0x8370 -> 0x8350` with
all `0x32C` bytes preserved; and the pinned `0x9F00` live handoff differs only
in the same PSW/TP values plus direct call `0x148E -> 0x1472`.

None of the 18 introduces a request parser, tester-derived pointer, new DMA
endpoint, retained vector base, credential reader, or alternate boot entry.
`tests/verify_keyless.py` pins the raw-byte closure
(`KEYLESS-011`).

## 14. Recovering application SA mainly unlocks BA F7, not boot execution

The application root disclosure changes how the application SecurityAccess
surface should be described. A tester can recover the root, perform normal
application SecurityAccess, and therefore satisfy any genuine application-SA
condition without prior secret possession. That does **not** mean every
application service suddenly becomes newly privileged: the primary Dcm service
objects have security count zero, the 242 RDBI policies contain no effective
nonzero level, all 19 RoutineControl RIDs have zero configured security levels,
and the recovered WDBI policy records are likewise empty.

The material callback-local exception is proprietary BA selector `F7/BAENA`.
Sienna `0x34D96` calls the application security-state reader and tests level-2
mask bit `0x02`; successful F7 then creates the already-documented persistent
BA authorization window. H/F retain `BAENA` at `0x21078` and the same target-
native level-2 bit-test tail at `0x30984`. The downstream BA operations remain
fixed-token/state-machine operations; the separate lifecycle audit recovers no
attacker-selected PC or boot credential read from them.

Therefore KEYLESS-006 converts application SA2 from a secret-dependent gate
into a recoverable protocol step, with BA F7 as the important newly practical
capability. It still does not write boot SA state, expose `0xBFD8/0xBFE8`, or
create application arbitrary-code execution. `KEYLESS-012` pins the Dcm and F7
facts; the complete Sienna BA semantics remain in
`tests/verify_application_proprietary_ba.py`.

## 15. Live handoff retains peripheral state, but DMAC endpoints are fixed

The normal application-to-boot transition is a live call, not a hardware reset.
`FUN_00064ec8` calls `0x9F00` first; `system_hard_reset()` is a fallback after a
non-returning path. It would therefore be incorrect to dismiss DMA/peripheral
state merely because reset values are safe.

The application DMAC programmer at `0x5F796` takes source/destination fields
from descriptor records, but every recovered caller supplies one of seven fixed
CodeFlash descriptor families (`0x31234`, `0x313E8`, `0x31438`, `0x31638`,
`0x31688`, `0x316D8`, `0x317A8`). The reachable 22 records use fixed peripheral,
GlobalRAM/LocalRAM, or ordinary CodeFlash endpoints. None points to the tester-
writable XCP window and none points to `0xBFD8/0xBFE8`. The application Dcm table
also has no SID `0x3D` WriteMemoryByAddress; the recovered generic tester write
primitive remains the separately bounded XCP shadow window.

Boot startup does touch the DMAC global control through `0x121A`, so retained
channel state is not assumed quiescent. The security conclusion instead rests
on endpoint provenance: without an application arbitrary-SFR/descriptor write,
a tester cannot arm a retained DMA transfer whose source is a boot credential
or whose destination is a control-flow cell. `tests/verify_keyless_live_handoff_dma.py`
pins the live-call ordering, fixed descriptor provenance, endpoint census, and
absence of an application WriteMemoryByAddress service (`KEYLESS-013`). This is
a software-visible conclusion; undocumented peripheral behavior remains outside
the static model.

## 16. Target-native H computed-control-flow census finds no XCP-window PC source

A disposable H Ghidra project was used for a target-native whole-image computed-
control-flow census rather than transferring Sienna names. The analyzed graph
contained 5,621 functions / 178,058 instructions and 589 computed control
transfers (519 call-like, 70 jump-like). Of the **function-owned** computed
transfers, only nine target-def chains read a LocalRAM cell: boot payload cell
`FEBF0FD0`; fixed application callback cells `FEBF6B04`, `FEBF1040`,
`FEBF1058`, and `FEBE5514`; the crypto job families around
`FEBF1240..FEBF1260` appear in adjacent currently-unowned body fragments. Every
one of these cells is below the XCP write window `FEBF7C00..FEBFFBFF`.

The census also produced 98 decoded computed transfers outside a recognized
function body. Their definition chains were reviewed separately: 16 are in the
`0x10000..0x1FFFF` calibration region, two in the `0x20000` vector/identity
area, and the remainder are auto-analysis gaps/data or target-specific callback
fragments. None of their target-definition chains reads the XCP window. The
real CALLT concern is independently closed by §10: CTBP is fixed to zero.
Configured H XCP/async callback tables are separately raw-byte pinned by
`tests/verify_corolla_h.py`.

The result is therefore a **bounded target-native negative**, not a claim that
Ghidra has perfect function ownership for every H byte: no recovered H computed
control-transfer target is sourced from tester-writable XCP RAM, and no target
into that RAM is recovered. Span's executable code is byte-identical to H
outside its calibration-only `0xA004..0x17DFF` delta, so this control-flow result
transfers to F. This is `KEYLESS-014`.

## 17. Application saved-PC/control-object search closes the obvious XCP-to-PC compositions

The unauthenticated XCP write primitive is already unusually strong: a tester
can place arbitrary bytes in executable LocalRAM `FEBF7C00..FEBFFBFF`. The
remaining application-RCE problem is therefore control transfer, not code
placement. A fresh pass widened the earlier computed-call census to include
exception returns, saved PCs, stack geometry, near-window callbacks, MPU
contexts, and the PE-local/self LocalRAM alias.

Sienna has eight decoded exception-return sites: seven `eiret` and one `feret`.
The common EIINT restore path at `0x70292` really does reload EIPC from a RAM
frame before `eiret`, and the fast-exception path likewise spills/restores FEPC.
However, the recovered live frames are on fixed application stacks in the
`FEBE...` view (`FEBE0800`, `FEBE1000`, `FEBE1800`, with foreground stack
`FEBE2000`), not inside the XCP shadow. The raw instruction census also finds
zero direct CodeFlash flow edges into `FEBF7C00..FEBFFBFF`.

The closest recovered writable-control object is more interesting:
`FEBF7704`, only `0x4FC` below the XCP lower bound, is loaded at `0x72E52` and
called indirectly at `0x72E56`. It has one canonical writer, `0x72E72` in the
setter at `0x72E5E`; that setter can install only fixed CodeFlash targets
`0x75664` or `0x7575A`. This is not an exploit today, but it is a concrete
high-value target for any future four-byte write escape.

The MPU context loader at `0x648EE` was also checked because an externally
controlled selector could reinterpret adjacent CodeFlash as MPAT values. All
11 recovered call sites obtain their selector from fixed CodeFlash bytes
`0x3180C..0x31813`, whose values are only 0 or 1. No tester-derived selector
feeds the loader.

Finally, the second LocalRAM mapping does not create a hidden overlap. The PE1
view `FEBE0000..FEBFFFFF` and self view `FEDE0000..FEDFFFFF` are same-offset
aliases separated by `0x200000`; XCP address `FEBF7C00` therefore aliases
`FEDF7C00`, not a lower `FEBE...` stack or `FEBF7704`. Span's paired PE1/self
RAM captures are consistent with this same-offset mapping. These facts are
pinned by `tests/verify_keyless.py` (`KEYLESS-015`).

## 18. Complete configured XCP composition does not escape the write window

The XCP audit was repeated as a command-composition problem rather than only a
`DOWNLOAD` range check. The standard dispatcher has 18 fixed CodeFlash
callbacks and a bounded command-to-slot map. `GET_SEED`/`UNLOCK` remain
unconfigured; `DOWNLOAD` and `MODIFY_BITS` resolve to fixed handlers and the
compiled writable interval remains exactly `FEBF7C00..FEBFFBFF`.

DAQ does not provide a write-around. `WRITE_DAQ` installs validated addresses
that the runtime sampler dereferences as **sources** into DTO staging. The
configured `SET_DAQ_LIST_MODE` rejects the XCP direction/STIM bit, and the
STIM-like command slots are absent. Thus an attacker-selected DAQ pointer is a
read/exfiltration primitive, not a receive destination.

The custom command family is likewise fixed. Selectors
`FB/FA/F5/F3/EB/EA/E4` map to immutable CodeFlash handlers. `EB/EA` only alter
page state 0/1; `E4` hardcodes a copy from CodeFlash `0x10000..0x17DEF` to the
XCP shadow; `F3` uses the same bounded CodeFlash interval for checksum/read.
Page selection is not fed into a destination calculation. Arithmetic edge
cases were also checked: multi-byte XCP writes reject interval overflow, and
the word-aligned `MODIFY_BITS` case cannot wrap `0xFFFFFFFC + 3` through zero.

`tests/verify_keyless.py` pins this closure (`KEYLESS-016`).
It materially narrows the remaining application-RCE search: a useful future
primitive must come from a different writer/corruption path, not from reversing
DAQ direction or composing the currently configured XCP commands.

## 19. Reset and alternate software-entry paths do not expose a keyless PC selector

The application reset/re-entry machinery was traced separately from the live
`0x9F00` programming handoff. `FUN_00061AFA` stores a reset sentinel in the
triple-copy hardware area `FFC0A000/4/8` as raw, XOR-`0x55555555`, and
XOR-`0xAAAAAAAA`; known producers supply fixed values such as
`3E3E3E3E`, `6D6D6D6D`, and `D6D6D6D6`. The consumer at `0x61B18` moves these
into ordinary application status state and replaces the hardware words with
fixed sentinels. They are reset-cause/status bookkeeping, not a PC or ROM-loader
address.

The reset-mode translator `0x60870` has only three canonical callers and maps
fixed internal mode values to fixed reset codes. The startup coordinator at
`0x62BC6` is likewise internal and uses fixed action constants
`11/22/33/44`. The normal application-to-boot programming path at `0x64EC8`
explicitly zeroes `FFC0A000/4/8/C`, synchronizes, and directly calls `0x9F00`;
`system_hard_reset()` remains fallback after that non-returning path.

No software-visible tester-derived selector was recovered that chooses an
alternate ROM monitor, serial/bootstrap entry, or attacker-selected reset PC.
This is intentionally a **bounded** static conclusion (`KEYLESS-017`): boot-pin
straps, undocumented on-chip ROM behavior, and fault-injection-only entry modes
are outside the CodeFlash model. The software facts are pinned by
`tests/verify_keyless.py`.

## 20. Authenticated RAM execution is functional architecture across all three dumps

The currently known authenticated path is not a one-image accident. Sienna
boot SecurityAccess, RequestDownload, TransferData, RequestTransferExit,
RoutineControl, request-seed/send-key helpers, and payload decrypt/verify logic
all transfer to H/F at the dominant `-0x1C` relocation; H and F are byte-
identical over the relevant boot domain. The three security roots remain
byte-identical as documented in §0.

There is also acquisition provenance, not only static similarity. Albino's
raw manifest records owner-side OBD acquisition with TSK Manager using the
public payload-build secret and explicitly rules out glitching, bench work, and
module removal; the retained bootstrap profile separately grades the target-built
range-payload execution as observed. Span's retained `security_access_log.json`
records accepted `send_key` operations for CodeFlash, LocalRAM, and DataFlash
range dumps, while the same bootstrap profile records the observed target-built
`FEBF0000/0x1000 -> 10F0 -> FF00` range-payload architecture.
`tests/verify_keyless.py` pins both the raw body transfer and
this retained field provenance (`KEYLESS-018`).

The portability conclusion is deliberately precise: **the authenticated RAM-
execution architecture is functional on all three tracked dumps**. It does not
make a payload/key from one target portable to an arbitrary future ECU whose
boot credentials or payload policy have changed.

## 20.1 Application CanTp/DCM reassembly is bounded, but was not part of the prior closure

The application has a separate diagnostic transport/reassembly stack below the
individual UDS service handlers. That surface was not established by the
XCP/boot mechanism audits and therefore had to be checked independently.

The CanTp First-Frame parser accepts the protocol/configuration ceiling
`CodeFlash[0x22D20] = 0x0FFF`. Three configured diagnostic TP connections route
upper PDU IDs `0x802/0x803/0x804`. PduR then maps receive allocation/copy to
`StartOfReception @ 0x903A8` and `CopyRxData @ 0x9043C`; the superficially
interesting generic byte copier `0x90916` is instead below `CopyTxData @
0x909BC` and belongs to ECU response transmission.

The actual DCM receive allocation is much smaller and independently bounded:
three fixed 256-byte slots at `FEBE5629`, `FEBE5729`, and `FEBE5829`.
`StartOfReception` rejects a nonzero requested total length above the selected
slot's `0x100` capacity. Every later `CopyRxData` obtains the per-slot remaining
capacity through `0x92398` and requires `chunk_length <= remaining` before the
copy helper `0x920D2` advances the destination and subtracts the copied length.
The CanTp CF path at `0x79FDA` separately clips the current transport chunk to
the remaining TP total.

Thus ordinary segmented application diagnostics do not provide a pre-SID
buffer overflow on this image. The important methodological result is that this
was a **new static avenue**, not something implied by KEYLESS-015/016. It is
pinned as `KEYLESS-019` by
`tests/verify_keyless.py`.

## 20.2 The event snapshot formatter is structurally unchecked but configuration-safe on S/H/F

A second reopened path found a real bounds asymmetry. Sienna
`direct_call_target_00054910` appends event snapshot records by
`3 + descriptor.length` with no capacity argument/check inside the record loop.
Its wrapper `0x549FA` can append both retained snapshot banks and compares the
final total against the supplied capacity only **after** those formatter calls.
The neighboring formatter `0x54A7E`, by contrast, performs an in-loop
`capacity < current + 3 + length` check before each callback/copy.

This is not an overflow on any tracked image because the configured event masks
bound the reachable record subsets well below the `0x300` AB staging capacity:

| Image | Formatter / helper | Descriptor count | Max one bank | Conservative two-bank max | Headroom in `0x300` |
|---|---:|---:|---:|---:|---:|
| Sienna `8965B4512000` | `0x54910` / `0x555E8` | 75 | 207 | 414 | 354 |
| Corolla H `8965H1202000` | `0x50038` / `0x50D10` | 78 | 202 | 404 | 364 |
| Corolla F `8965F1208000` | H-byte-identical path | 78 | 202 | 404 | 364 |

The Corolla conclusion is target-native, not inferred only from Sienna. A fresh
H Ghidra recovery shows `0x50038` retains the unchecked append loop,
`0x50122` retains the two-bank/post-write total check, `0x501A6` retains the
bounded sibling, `0x50D10` selects 78 descriptors at `0x29F1C`, and the AB
worker `0x87384` resets the staging capacity to `0x300`. H and F are
byte-identical for these functions and descriptor/event tables.

Therefore the current images are safe, but the safety is **configuration-
dependent rather than structural**. A future or alternate calibration that
changes event-mask membership, descriptor count/length, or staging capacity can
invalidate the arithmetic without changing the unchecked formatter itself.
This is `KEYLESS-020`, pinned by
`tests/verify_keyless.py` and the compact H-native
artifact
`data/generated/corolla_8965H1202000_keyless_event_formatter_decompiler_evidence.json`.

## 20.3 What the reopened static audit does and does not establish

CORR-101 corrects the earlier analysis mistake: closing a collection of known
compositions is not equivalent to exhausting the firmware's software-visible
attack surface. The exploit-interest ranking itself is explicitly a candidate
generator, not an absence proof. Its reviewed-candidate ledger covers selected
cohorts, not every one of the 1,055 pre-SA-reachable ranked functions.

The three rows that were still explicitly `open` when this re-audit began are
now individually closed as bounded negatives: `0x539A8` is a parameterless
fixed-state/NvM-object-`0x0E` reset helper; `0x58404` is a parameterless AUTOSAR
OS task with a fixed caller; and `0x7C7C2` is COM-Tx maintenance called with an
internally generated index bounded by the one-entry Tx-PDU configuration. Zero
`open` rows in that **reviewed ledger** still does not imply that every ranked
function or every possible cross-function composition has been manually
reviewed.

Static work therefore remains legitimate and potentially productive. New
candidate discovery can come from previously unmodeled parser/reassembly
layers, configuration-dependent copy/formatting paths, indirect dataflow,
state-machine compositions, target-native variant deltas, or other software
mechanisms. Hardware/ROM/fault evidence is an additional class of evidence, not
a prerequisite for making further progress.

## 21. Techstream Unified recovery does not reveal a target-compatible no-SA retry

The two V18 CUW rows whose prepare+flash grammar is byte-compatible with the
tracked EPS bootloader are `P5-Unified.ini` and `P5-Unified10.ini`. Both set
`PrepareRetryFlag=0` while retaining the host's broader IG-off retry support.
The DLL export sets are also exact: `TCUWCanUnifiedPrepareWriter.dll` exports
only `StartPrepareWrite`; the two matching flash writers export only
`StartFlashWrite`. None exposes a separate PrepareRetry entrypoint.

That matters because the recovered `StartPrepareWrite` target grammar includes
the same exact 18-byte SecurityAccess exchange required by firmware:
`27 01 || testerData[16]`, followed by `27 02 || key[16]`. The generic CUW
`UseNewSoftwarePassword`/RecoveryInfo state is therefore host persistence, not
evidence that these target-compatible rows resume a fresh locked ECU without
SecurityAccess. `TMS-036` and
`tests/verify_techstream_cuw_timing_recovery.py` pin this V18-specific closure.

## 22. Payload fixtures and key rotation

A payload fixture proves possession of a payload accepted by the CMAC gate for
the conditions under which that fixture was built. It can therefore avoid
re-deriving the payload-build secret for an identical target/fixture context.
It **cannot** bypass boot SecurityAccess: `0x34` and the execution-relevant
RoutineControl path remain gated on the independent boot-SA state.

Consequently key rotation has two separate effects:

- rotating only the payload-build secret may still leave an old accepted
  fixture useful after a legitimate/otherwise-solved boot-SA unlock;
- rotating the boot-SA secret removes access to the authenticated download and
  execute path even if a valid payload fixture is available, unless boot SA is
  separately solved or bypassed.

This distinction is the reason the repository keeps boot-SA and payload-build
roots separate throughout the bootstrap documentation.

## 23. Evidence boundary

This is a set of bounded negative static results over **enumerated mechanisms**
in three images, not a universal impossibility proof and not proof that the
software-only static search is exhausted. CORR-101 is the controlling
methodological boundary: an unmodeled software parser, copy sink, state
composition, indirect-control chain, or target-native variant difference can
still change the result without requiring new hardware evidence. New boot
generations, undocumented peripheral effects, alternate hardware routing, and
physical fault injection can also change the result, but they are not the only
remaining research directions. Hardware glitching remains out of scope for the
software-only question in this document.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [KEYLESS-001](../reference/index.md#finding-keyless-001), [KEYLESS-002](../reference/index.md#finding-keyless-002), [KEYLESS-003](../reference/index.md#finding-keyless-003), [KEYLESS-004](../reference/index.md#finding-keyless-004), [KEYLESS-005](../reference/index.md#finding-keyless-005), [KEYLESS-006](../reference/index.md#finding-keyless-006), [KEYLESS-007](../reference/index.md#finding-keyless-007), [KEYLESS-008](../reference/index.md#finding-keyless-008), [KEYLESS-009](../reference/index.md#finding-keyless-009), [KEYLESS-010](../reference/index.md#finding-keyless-010), [KEYLESS-011](../reference/index.md#finding-keyless-011), [KEYLESS-012](../reference/index.md#finding-keyless-012), [KEYLESS-013](../reference/index.md#finding-keyless-013), [KEYLESS-014](../reference/index.md#finding-keyless-014), [KEYLESS-015](../reference/index.md#finding-keyless-015), [KEYLESS-016](../reference/index.md#finding-keyless-016), [KEYLESS-017](../reference/index.md#finding-keyless-017), [KEYLESS-018](../reference/index.md#finding-keyless-018), [KEYLESS-019](../reference/index.md#finding-keyless-019), [KEYLESS-020](../reference/index.md#finding-keyless-020)
- Corrections with this document as canonical home: [CORR-101](../reference/index.md#correction-corr-101)
<!-- knowledge-cross-references:end -->
