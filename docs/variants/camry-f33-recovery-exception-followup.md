# F33 recovery follow-up: exception masks, reset state, and transport execution

2026-09-11. Offline analysis of exact `8965F3307000` firmware and the retained
Renesas P1M-E hardware manual. No vehicle connection, CAN transmission, reset,
RAM upload, or flash write was performed. No working CAN-only recovery method
was established.

## Image-state check

The canonical stock CodeFlash is
`firmware/camry-8965F3307000/CodeFlash.bin` (VA equals file offset), SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.
The local reconstruction of the incident image hashes to
`aba6867f244dda42b754d6f455f25a226ee95025dee6a2d98b07b3ac550f2d74`,
the expected post-write image from the incident record. It is not a new live
whole-flash readback.

Comparing that reconstruction with stock shows that these reviewed regions
are unchanged: boot `00000..0FFFF`, CAN/DCM tables `21000..2BFFF`, startup and
exception code `60000..71FFF`, diagnostic workers `90000..98E7F`, the reviewed
XCP parser/gate body `98E80..98EF3`, MPU configuration `3167C..31787`, and
XCP-disable byte `30D68`. Earlier SecOC modifications are distinct from these
regions. The pre-hook stage-6 image is not an untouched factory image.

## 1. `ei` does not clear the separate FE-exception mask

Raw default application exception handler `62E1E` saves state, executes `ei`
at `62E36`, calls the register-save helper `712CE`, and spins at `62E42`.
There is no boot diagnostic call, exception return, or `PSW.NP` clear in that
reviewed path.

Renesas **R01UH0585EJ0120**, *RH850/P1M-E Hardware Rev.1.20*, p.198, distinguishes
`PSW.NP` from `PSW.ID`: acknowledgement of an FE-level exception sets NP and
inhibits the relevant EI/FE exception acknowledgements; `ei` clears ID, not NP.
Thus, **for an FE-level fault, `ei` alone does not prove that ordinary CAN/timer
interrupts remain serviceable**. The PSW table was visually checked in the PDF.

The exact incident exception remains unobserved. At `7A272`, the recorded four
bytes and next stock halfword form `FF 02 92 5B 24 36`, a six-byte JARL to
`362BFE04`. Hardware Table 4.1 (p.257) marks that address reserved, but the
firmware's MPU region 0 spans `00000000..FEBDFFFF` and has attribute `B8` in both
recovered contexts. It permits supervisor execution when its ASID condition
matches. Therefore an out-of-CodeFlash address alone does not establish a
specific MPU instruction-protection exception. Reserved-region fetch behavior,
privilege/ASID state, and live FEIC/FEPC must not be conflated.

Sources: raw `62E1E..62E43`, `712CE`; MPU loader `6586A/65984`, bounds `31688`,
attributes `31708/31748`; manual pp.198, 215, 219–220, 244, 257. The separate
vector-90 handler `65BD4` returning through saved `FEPC+4` is not evidence that
this fault returns through the malformed call's `LP`.

## 2. A receive callback can run without executing its diagnostic request

`79EDE -> 809FE -> 808D6 -> 80884` performs receive/deferred-indication work
before the bad call inside `7A254`. The normal foreground diagnostic worker
`988C2` and system-mode worker `58B5E` are later calls in `667E6`.

All three configured diagnostic routes use the same upper callback family:

| CAN ID | ISO-TP RX record | Lower handle | Upper PDU |
|---|---:|---:|---:|
| `7A1` | `22BDE` | `0804` | `0802` |
| `777` | `22BFE` | `0805` | `0803` |
| `7A0` | `22C1E` | `0806` | `0804` |

The reviewed single-frame chain is
`81200 -> 79DB0 -> 7A57A -> 7A4E4 -> 7ADF8 -> 7AD96`, through fixed PDU-router
callbacks and `7BE58/7BE6C/7BE90` to DCM `920BE/92152/921D2`.

The nested completion path `921D2 -> 91F72 -> 92B4A -> 92AB0/92A86` was also
inspected: it prepares request buffers/state, not the requested service.
`98B3A` writes timer deadlines and flags. Timer slot 6's callback `922EA`
queues event 0 through `989EC`; the latter writes an event ring, not an inline
service call. Timer worker `98AE4` and event consumer `98946` run under `988C2`.

The recovered application-to-boot handoff remains
`58B5E -> 5F464/5F91C -> 56CF6 -> 65F5E -> 9F00 -> 148E -> 1398`.
Thus, even granting surviving receive interrupts, the reviewed normal service
and handoff paths still require foreground execution past the corrupted call.
Suppressing a positive response does not remove that dependency. No direct
boot entry was found in the reviewed receive-completion chain.

Primary tables: `21FA0`, `22C4C`, `21CE8/21CEC/21CF4`, `2188C/21890/21898`.
Several real adapter/interrupt entries are absent as functions in the canonical
corpus, so their instruction bytes were read instead of treating a missing
function as proof that no code exists.

## 3. Cold startup clears flash-error status before boot selection

There is a relevant ordering edge before the already-known `119E` gate:

```text
1404 -> 802:  FFC62004 = 0F; FFC62008 = 1
     -> remaining cold startup
     -> 13B0 -> 119E -> 115A: read FFC62030, test bits 0 and 2
```

The manufacturer identifies `FFC62030` as **UCFDERSTR**, the CodeFlash
ECC-double-bit/address-parity status register, cleared through `FFC62008`.
It is not RESF, a failed-start counter, or a persistent application-crash flag
(manual p.2530, visually checked). The cold initializer clears that state
before the later validity check. A genuine new flash error can affect the
check; an erroneous but correctly stored branch is not evidence of one.

The three-attempt loops in `119E` retry validity checks during one invocation;
they are not a multi-boot crash counter. Backup words `FFC0A000/4/8/C` are used
as guarded error/reset records in the reviewed startup paths, not a recovered
network-controlled programming selector. Cold upper-RAM clearing must also
not be confused with retention across the application's live handoff.

Primary firmware: `802`, raw `1404..1477`, `E54`, `F80`, `10C6`, `115A`, `119E`,
`13B0`, `62BAE`. No electrical fault or deliberate integrity failure is proposed
as a recovery procedure.

## 4. XCP's fixed gate is decisive independently of scheduling

`8312E -> 830D0` copies a bounded frame to `FEBE4C34`. Subject to transport state,
`82FEC` directly calls the fixed pointer at `22B14`, which is `821D6`.
`821D6 -> 830C0 -> 98E80` reads CodeFlash byte `30D68=5A`, returns nonzero, and
prevents protocol command processing. That byte and the reviewed gate code are
unchanged in the incident reconstruction.

The callback relationship should not be replaced by a blanket assumption that
all XCP interpretation waits for DCM. Conversely, even granting that the
callback runs, reaching staging does not enable CONNECT/DOWNLOAD. This pass
does not claim a particular incident frame reached the parser before the
fault. The custom resident is not an independent listener: the malformed call
does not reach its intended entry.

## 5. Recovery boundary

The documented Renesas ROM programming mode is selected by hardware mode pins
at pin-reset release and uses UART/CSI, not a documented CAN-ROM listener
(manual pp.261–263 and 2867). The lockstep master/checker pair is not a second
independent application CPU with its own diagnostic service (p.2684). This
does not rule out another processor or connection elsewhere in the assembly.

Current local `tools/gts route P5-Unified --json` reports `PrepareRetryFlag=0`
for both `P5-Unified` and `P5-Unified10`, with no configured repro-gateway-mode
writer in those rows. This is a configuration observation, not an exhaustive
current-DLL or assembly-level proof.

An actual recovery lead must provide legitimate recovery execution independent
of returning from the corrupted foreground call. The exact live fault state,
unacquired ROM/extended-region contents, and complete assembly-level wiring
remain unknown. They are neither demonstrated recovery routes nor evidence
for an absolute impossibility claim. Known inverse bytes alone do not supply
an accessible way to perform the repair. No new vehicle job was left running.
