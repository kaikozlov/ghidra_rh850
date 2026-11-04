# Toyota Tundra EPS `8965F3401200`

Canonical plaintext application region recovered from Toyota `T-0035-22.cuw`.

- `Application.bin`: 949,744 bytes (`0xE7DF0`), SHA-256
  `c401af613cb44a70dad5ec3dba7218800bd32d94c4a47e12301b4e3a5ce33d94`
- CodeFlash load address: `0x00018000`
- Covered CodeFlash range: `0x00018000..0x000FFDEF`
- Embedded application identity: `8965F3401200` at absolute `0x00020860`

The source CUW is `T-0035-22.cuw`, SHA-256
`9882b1b6dd6acda2d142a2825eda396b0a425e41c13f822b9a18e022d4c43e81`.
The encrypted CPU-image region decrypts to `0xE7E00` bytes and CMAC-validates.
`Application.bin` omits the final 16-byte CUW authentication trailer, so it is
the firmware payload rather than the package-authentication record.

This is **not a complete 1 MiB CodeFlash dump**. The CUW CPU image begins at
`0x00018000`; bytes `0x00000000..0x00017FFF` are not reconstructed or filled in.
The manufacturer erase/program routine is separately analyzed from the same CUW
by `tools/techstream/analyze_t0035_faci_backend.py`.

## Dual-CPU programming selection

The source `T-0035-22.cuw` declares `ContactType=P5-Unified`, one node
(`Node01/DiagID=07A1`, gateway preparation `01_GatewayDiagID=07505F`), and two
CPU images. Both images start at the local address `00018000` and have length
`000E7E00`. The independent `T-0036-22.cuw` repeats the same addressing scheme
for the `8965F3403200/4200` pair.

| CUW section | NewCID | Five-byte `OffsetAddress` | Effective `CPUImage` start |
|---|---|---|---|
| `CPU11` | `8965F3401200` | `01 00 00 00 00` | `01 00 01 80 00` |
| `CPU12` | `8965F3402200` | `00 00 00 00 00` | `00 00 01 80 00` |

**Current GTS+ host evidence.** In the recovered CUWPlus
`TCUWCanUnifiedFlashWriter.dll` (SHA-256
`97cdba7f5cc57a555df27893479141632e48a41276e73c54f9c36de3e6e16647`):

- `0x100013A0` processes the selected CPU image/index, using `GetNodeIdx` to
  associate both images with the same diagnostic node.
- `0x10002AD0` transmits `2E 02 03 || OffsetAddress[5]`, then
  `2E 02 01 || SeedKey[16]`, then `2E 02 02 || Nonce[16]`.
- `0x10001BE0` builds RequestDownload with address/size format `46`, a separate
  address-space byte, and the **five-byte big-endian sum** of `OffsetAddress`
  and each area start. `0x10002060` applies the same sum to RoutineControl
  addresses. `0x10002510` supplies the address-space byte (1 for area tags
  0/2, 0 for tag 3) and data format (`SecurityProperty2` bit 3).

For the CPUImage area of `T-0035-22.cuw`, the resulting *UDS application payloads*
(excluding ISO-TP framing) are:

```text
CPU11  2E 02 03 01 00 00 00 00
       34 01 46 01 01 00 01 80 00 00 0E 7E 00
CPU12  2E 02 03 00 00 00 00 00
       34 01 46 01 00 00 01 80 00 00 0E 7E 00
```

These use the **same CAN diagnostic endpoint** (`0x7A1` request, conventional
`0x7A9` response), not separate external CAN IDs for each CPU. The gateway
preparation ID `07505F` is a distinct operation, not the second CPU endpoint.

**Important distinction:** the retained community
`community/blurbdust_secoc_flash_patcher/flash_patcher.py::run_exploit` also
uses `01 00 00 00 00` vs `00 00 00 00 00` for DID `0203`, but its RAM-exec
RequestDownload switches the separate *address-space byte* (`mem_id=01/00`)
and sends a zero-prefixed five-byte RAM address. That is **not** the factory
Unified writer's per-CPU RequestDownload construction above. The Tundra
bootloader's implementation of these address fields is not contained in the
retained application-only extracts; its precise hardware CPU-dispatch path
remains to be recovered from bootloader bytes or a live reflash trace.

## Application-side evidence from both CPUs

The same CUW's `CPU12` application is now retained at
[`firmware/tundra-8965F3402200/Application.bin`](../tundra-8965F3402200/Application.bin)
(SHA-256 `54c84ac25db1dfdb73e982c3ec9b379febe56229310ad07cd171eec333ac87f8`).
Both images have the same local CodeFlash range, but 544,648 of their 949,744
application bytes differ. The images were examined independently as raw
`v850e3:LE:32:default` Ghidra programs loaded at `0x18000`.

The application diagnostic configuration distinguishes the two CPU roles:

| Evidence | CPU11 `8965F3401200` | CPU12 `8965F3402200` |
|---|---|---|
| Software ID | `0x20860`: `8965F3401200` | `0x20860`: `8965F3402200` |
| `F181` descriptor | `0x29B60`, length `0x41` | `0x28830`, length `0x20` |
| `F181` callback | `0x47B18` | `0x4604E` |
| `2032` descriptor | `0x29B40`, length `0x21` | `0x28810`, length `0x10` |
| `2032` callback | `0x47ABA` | `0x4600C` |

In CPU11, `0x47B18` initializes the `F181` output with `0x3F` and fills
`0x04 || 16 bytes at 0x20860 || 16 bytes at 0x17DC0`. CPU12's `0x4604E`
fills 32 bytes with the corresponding two local software-identification
fields, without a count prefix. The `2032` handlers have the same complementary
shape: CPU11 initializes a 33-byte output and supplies `0x02 || 16 bytes at
0x17D80`; CPU12 supplies 16 bytes without a prefix. The lengths reserve exactly
enough space for both CPUs' records. The secondary-ID sources at `0x17D80`
and `0x17DC0` are in the missing lower CodeFlash region.

CPU11 also carries explicit external CAN diagnostic configuration: `0x7A1`
physical receive at `0x21EB8` (acceptance rule `0x23004`), `0x7A9` transmit
at `0x21E98`, and a full application SID object table starting at `0x25B10`
(SID `0x22` at `0x25B70`, callback `0x8E2BC`). CPU12 has its own DID handlers
but lacks that primary CAN endpoint configuration and the corresponding SID
object table. This is consistent with CPU11 receiving tester traffic and
providing an internal path to CPU12; the transport and response-composition
implementation remain to be traced.

The CUW's separate `CPU11`/`CPU12` logical address ranges are host-side proof
of how programming requests are *formed*. The application images do not contain
the bootloader's `0x0203`, RequestDownload `0x34`, or RoutineControl `0x31`
CPU-selection dispatch. The exact Tundra selection mechanism among `0x0203`,
the six-byte RequestDownload address, and CPU-to-CPU forwarding requires the
Tundra bootloader or a programming trace.

## CPU11 application: entry to programming mode

The Tundra CPU11 application SID `10` service at `0x25B10` uses a
subfunction table at `0x258A8`. Its wrappers are `01 -> 0x8DCD6`,
`02 -> 0x8DCE6`, and `03 -> 0x8DCF6`. The current-session allow lists are
`01:{01,02,03}`, `02:{02,03}`, and `03:{01,03}`. The session records at
`0x26016` show transition kinds `0`, `2`, and `0` respectively, so EXTENDED
`10 03` is an ordinary immediate transition while PROGRAMMING `10 02` uses the
asynchronous handoff. Decompilation and disassembly recover the programming
chain:

- `0x8DCE6 -> 0x8DC1C -> 0x8DA10 -> 0x8DCC8 -> 0x83D82 ->
  0x45AAE`: a request for session 2 is rejected when the application speed
  snapshot `uint16(GP+0x3092)` exceeds `uint16(CodeFlash[0x2D290]) = 0x0180`.
  The policy returns internal code `0x0B` on that branch.
- The asynchronous handoff at `0x83BC6` and `0x83C76` uses system operations
  `0x08000200` and `0x08000201`. `0x83B92 -> 0x45ACC` admits it only if the
  system-transition snapshot `GP+0x301F` is not `0x11`, the supply snapshot
  `uint16(GP-0x4B4A)` is at least `uint16(CodeFlash[0x2D292]) = 0x0A00`,
  and `GP-0x3372` is clear. Rejection returns internal 1; the application
  session worker at `0x8DB5A` maps that path to NRC `0x22`.
- On acceptance `0x45AF8` queues system event 9, while the session handler
  can remain pending (`0x78`), so disappearance or a client timeout during the
  transition is not a SecurityAccess lockout observation.

These are **application system-state gates**, not a failed-key counter or a
CAN-traffic-volume gate. The effect of missing or additional CAN messages on
the underlying status/speed snapshots is a separate dependency to trace. A
Tundra bootloader SecurityAccess anti-bruteforce policy cannot be read from the
CUW's application images because its first `0x18000` CodeFlash bytes are absent.

## SecOC Gate 2 and the CPU1 recovery-risk overlap

The RAV4 Prime/Camry compare-neutralization signature
`E0 D1 9A 0D 1A 38 BF FF` occurs exactly once in each Tundra application. Ghidra
places each occurrence inside the same 134-byte SecOC receive-verification worker
shape as the named Camry Gate-2 function:

| CPU | Worker | Gate-2 compare | 32-KiB erase block |
|---|---:|---:|---|
| CPU11 `8965F3401200` | `0x883BA` | `0x88406` | `0x88000..0x8FFFF` |
| CPU12 `8965F3402200` | `0x80998` | `0x809E4` | `0x80000..0x87FFF` |

At both compare sites, result zero falls through to the normal status/delivery
calls while nonzero branches to the retry/failure call. The two-byte operation
`E0 D1 -> E0 01` changes `cmp r0,r26` to `cmp r0,r0`, so the following BNE cannot
take the nonzero-result arm.

CPU11 has an important flash-recovery property: its application diagnostic
session machinery is in the **same `0x88000..0x8FFFF` erase block** as Gate 2.
This includes the `0x8DCF6` EXTENDED-session wrapper, so a rack that still
answers application F181 but times out on `10 03` matches a failure localized
away from the independent F181 callback/table and into this sector or its
session state path.
That block contains the session wrappers `0x8DCD6/0x8DCE6/0x8DCF6`, common
session worker `0x8DC1C`, request worker `0x8DA10`, and asynchronous worker
`0x8DB5A`. The stock CUW-derived block SHA-256 is
`a082fa7685573b6784c32ce4ca02f1ca87f398f8c85e1bb530dab52ae3331cf8`.
CPU12's stock Gate-2 block SHA-256 is
`8a196b3ac98ea9eb581aa4b57f60c9ea3a0395f7817910365a0b25bf7a925c3b`.

A logical two-byte CPU1 Gate-2 patch therefore requires read-modify-erase-program
of a sector that also owns `10 01/02/03` application session code. Collateral
sector corruption can leave the independent F181 path operational while breaking
session transitions. A writer that computes the terminal CodeFlash CRC from the
post-write flash contents can also make such collateral changes boot-valid.

The retained blurbdust persistent writer is evidence that this failure mode was
possible in community tooling, not evidence that it occurred on a particular
rack. It rewrites whole `0x8000` blocks and its historical program loop used the
wrong FACI halfword-pacing condition; Toyota's exact T-0035 manufacturer routine
uses post-write `FSTATR & 0x400` (`DBFULL`). The exact writer and target bytes
used in the reported Tundra attempt are not retained here, so attribution
requires that patch script or a post-patch CPU11 dump.

### Reported Tundra incident context

Tim clarified on Discord on 2026-11-02 that his CPU1 patch was the culmination
of multiple earlier attempts and left the rack in a semi-bricked state; it was
not yc's later RAV4 Prime compare-neutralization patch. He described two live
hypotheses for the vehicle faults: the unpatched second CPU eventually faulting,
or ICU-S becoming stuck through contention, with the observed errors occurring
at startup. He also described yc's proposed explanation for the failed
bootloader re-entry as a **bus-contention theory** and said that theory had not
been tested on his rack.

Accordingly, the historical incident does not establish that the clean Gate-2
patch damages UDS, nor that SecurityAccess entered a lockout state. The exact
historical patch bytes/writer and a post-patch CPU1 sector remain the evidence
needed to explain that rack's recovery failure.

For a rack that still answers application F181 but no longer enters EXTENDED,
the highest-value artifact is the current CPU11 `0x88000..0x8FFFF` sector. A
byte diff against the CUW stock sector would distinguish a clean Gate-2 edit
from collateral programming damage or an unrelated patch target.
