# Calvin TSKM `dump` archaeology — 2026-08-21 re-audit

## Scope and evidence rule

This note audits Calvin Park's pinned `openpilot` `dump` tip
`42d1120395877e96ed440646a765157a0ad7646b`, including still-readable rewritten
commits that are no longer reachable from the visible branch. The checkout is
pinned as `calvinpark_openpilot_dump` in `external-references.lock.json`.

The first pass over this material trusted both Calvin's `CLAUDE.md` and this
repository's existing interpretations too readily. This re-audit uses the
repository evidence hierarchy explicitly:

1. firmware bytes and deterministic tests;
2. retained raw captures and generated artifacts;
3. official Renesas product/hardware documentation pinned by hash;
4. deterministic external Git artifacts;
5. Calvin's `CLAUDE.md` field journal;
6. interpretation/inference.

`CLAUDE.md` is valuable chronology and field evidence, but it is not firmware
truth. Where Calvin reports an experiment whose raw before/after artifacts are
not retained here, this note labels it **BOUNDED** even when the report is
internally credible.

## Claim-by-claim audit

| claim from the first pass | disposition | corrected evidence boundary |
|---|---|---|
| visible `dump` history hides rewritten development commits | **VERIFIED** | orphan commits and GitHub repository events reconstruct the `tskm -> wide -> dump` sequence |
| the first rebase generations changed only `env.py` | **CORRECTED** | Calvin's own `tsk/` delta is essentially `env.py`-only; the full repository tree also changes because the upstream openpilot base moved |
| six current range payload packages authenticate under the recovered BFD8 payload root | **VERIFIED** | all six 4-KiB ciphertexts independently pass decrypt/CRC/CMAC/callback/descriptor checks |
| the six plaintexts differ at only six bytes | **CORRECTED** | the executable body below `0xFD0` differs at six encoded range bytes; the CRC fixup `0xFEC..0xFEF` also differs, for ten varying bytes through `0xFEF` |
| Calvin's family introduced a newer reset-return dumper | **CORRECTED** | Calvin differs from Willem's 32-KiB DataFlash self-loop artifact, but Willem's older RAM payload already uses boot reset `0x157E` |
| Bk2ol source/toolchain reproduces Calvin global-RAM package | **VERIFIED** | global-RAM source substitution with the pinned GCC13.2/binutils2.41 family reproduces the complete encrypted package; this proves family equivalence, not original authorship |
| Bk2ol ladder establishes authorship | **BOUNDED** | Bk2ol contains an exact public precursor/common-lineage `.5/.7/1.0 s + repeated PROGRAMMING` sequence; sequence identity does not establish who first authored it |
| `FF00` is being used as a callback/control-flow trigger | **VERIFIED** | CPU static path enters the legitimate erase state machine and dispatches through `FEBF0FD0 -> uploaded FEBF0000` |
| `FF00` therefore never physically erases | **CORRECTED** | CPU-side static analysis does not prove zero FCU erase side effect; Calvin's “did not erase” statement is an external field observation without retained before/after sector evidence |
| five H 64-KiB captures are five 64-KiB DataFlash captures | **CORRECTED** | official P1M-E data identifies `R7F701383` as a 1-MiB DPS part with **32 KiB DataFlash**, `FF200000..FF207FFF`; the upper `FF208000..FF20FFFF` half is outside the specified DataFlash array |
| actual H DataFlash has poor byte repeatability | **VERIFIED** | restricting all five host reads to the real first 32 KiB gives 23.5077%-25.6470% pairwise divergence; cause is not assigned to real NVM writes |
| H object-15 invalidity was a one-dump conclusion | **VERIFIED FALSE** | every one of the five reads independently decodes objects 0/2/5 as three-valid-copy and object 15 as zero-valid-copy |
| `R7F701383` DataFlash size remained unsettled | **CORRECTED** | retained official Renesas datasheet + hardware manual settle it at 32 KiB for this 1-MiB part |
| `FEDE`/`FEBE` aliasing should not transfer from `R7F701381` to `R7F701383` without another dump | **CORRECTED** | P1M-E hardware maps both 128-KiB PE1/self windows while the part has only 128 KiB total local RAM; the self window is an architectural self view, not a second bank. Calvin's live test is dynamic confirmation, not the sole basis |
| `FF206ED4` is object-14's raw second field | **CORRECTED** | `FF206E14` is object-15 `+0x14`; `FF206ED4` is three `0x40` strides later but maps to object 12 raw `FF206EC0 + 0x14`; object 14's corresponding field is `FF206E54` |
| Calvin's ID/AuthID/master-key labels are locally established | **BOUNDED** | the `0x40` stride and `+0x14` placement align with local physical geometry; table-wide semantic labels remain Calvin field terminology |
| dealer rekey left the prior factory key in plaintext | **BOUNDED** | retained only as Calvin's external field observation; no local before/after artifact proves it |
| the corpus contains exactly 3,194,640 16-byte windows and two-oracle geometry of 6,389,280 | **VERIFIED** | file-size arithmetic reproduces the window count and two-oracle invocation count exactly |
| 6,389,280 means exactly that many literal CMAC calculations and proves no key exists | **CORRECTED** | it is scan-position/oracle-invocation geometry; matcher internals may evaluate multiple samples. The zero-match run is external dynamic, both oracles are cross-session relative to the Aug-14 dumps, and the result excludes only stable raw-window matches under that epoch assumption |
| successful SecurityAccess ~1 s after PROGRAMMING disproves a 10-s delay | **CORRECTED** | the bad-key backoff is independently **10 seconds** from TAUJ1 clocking. The ordinary retained PROGRAMMING replay explicitly clears the separate initializer delay before synthetic `10 02`; Calvin exercised that clear path, not the two-bad-key backoff |
| final preflight fixes the Span route-selection bug | **VERIFIED code / BOUNDED field result** | final source probes answering routes through PROGRAMMING; in-car `param=1` PROGRAMMING remains unmeasured |
| final preflight is mock-tested | **BOUNDED** | `CLAUDE.md` says it was mock-tested; no committed preflight test at the pinned tip independently demonstrates that claim |

## 1. Git chronology and rewritten history

The visible branch contains four Calvin commits above its upstream base:

| commit | author date | commit date | subject |
|---|---|---|---|
| `7f207ac644d...` | 2026-07-03 | 2026-08-12 | `TSKM Web` |
| `ce279fcb5cad...` | 2026-07-26 | 2026-08-12 | `Range dumper` |
| `725f84756dda...` | 2026-07-29 | 2026-08-12 | `mo-dump` |
| `42d112039587...` | 2026-08-18 | 2026-08-20 | `spanconstants` |

Still-readable orphan objects and retained GitHub events recover earlier
presentations:

```text
original TSKM line
  37181a271...  TSKM Web
  a7b90ffb4...  Range dumper
  28ff8452e...  mo-dump

rebased/cleaned TSKM line
  5feb4f4ca...  TSKM Web
  9a18846ef...  Range dumper
  6ffa39e634...  mo-dump

2026-08-13
  branch wide created

2026-08-19
  wide deleted
  dump created
  823d9293c...  save          parent 725f8475
  60d4ec550...  spanconstants parent 725f8475

2026-08-20
  42d112039...  spanconstants parent 725f8475
```

`823d`, `60d`, and `42d` share the same parent and are therefore replacement
amendments, not one descendant sequence. The full-tree rebase also moves the
upstream openpilot base; only Calvin's own `tsk/` delta is nearly
content-preserving apart from `env.py`. This distinction matters whenever an
orphan snapshot is compared with the visible branch.

## 2. Authenticated range-payload corpus

The six current packages are 4,096-byte encrypted bootloader payloads. Direct
package verification establishes, for each file:

- AES-CBC decryption under the key derived from the recovered BFD8 payload-build
  secret;
- CMAC over `zero_iv || plaintext[0:0xFF0]`;
- CRC-32 residue `0xFFFFFFFF` over the authenticated `0xFF0` bytes;
- callback `0xFEBF0000` at `+0xFD0`;
- descriptor `{0xFEBF0000, 0xFF0}` at `+0xFE0`.

| profile | host range | ciphertext SHA-256 |
|---|---|---|
| CodeFlash | `00000000..001FFFFF` | `860f8a3418d23ccfd0861a97efdb9e1d23a8854c3a629b8d7b6821eb93d0b588` |
| extended CodeFlash | `01000000..0100BFFF` | `9882860dffe746217f776ef69d93f40bc4405c62bc009f156f87c6a444ae7b2c` |
| PE1 local view | `FEBE0000..FEBFFFFF` | `fbb1f5bd352c3f0bf416d6b1ef6a7696f97cad2b9f49570ca859207f3269e44f` |
| self local view | `FEDE0000..FEDFFFFF` | `fba7950a62939f75d7b06e08fc1fe4ceea5fd2109b8fe4677494a3777543a35d` |
| global RAM | `FEEF8000..FEF07FFF` | `43d00fdaf790c6deb230d3a4e7b8f8bd17e077a100fa53ebb194532f55c510fd` |
| 64-KiB FF20 host range | `FF200000..FF20FFFF` | `9545c4192797a4800d675c454892a787f1df88683522eefb6b47915cf9c7a4eb` |

The six executable bodies below `0xFD0` vary only at:

```text
0x06A 0x06B 0x06F 0x182 0x183 0x187
```

Those six encoded bytes represent four range-immediate fields. The authenticated
CRC fixup at `0xFEC..0xFEF` also differs for every package, so the entire
plaintext does **not** differ by only six bytes.

The range body eventually returns through boot reset `0x157E`. That distinguishes
it from the older Willem/Bk2ol 32-KiB DataFlash artifact that self-loops, but it
is not evidence that Calvin invented reset-return behavior: Willem's older RAM
payload (`d972d4bf...`) already contains the reset-return sequence.

The strongest deterministic lineage result is narrower and cleaner. Rebuilding
Bk2ol's later-public `main_ff1ff000_ff209000.c` with its pinned GCC 13.2 /
binutils 2.41 V850 toolchain, substituting Calvin's global-RAM range, reproduces
Calvin's complete encrypted global-RAM package byte-for-byte. This establishes
source/compiler/package-family equivalence. It does not establish pre-public
original authorship.

Likewise, Bk2ol's `steps/step_dump_dataflash.py` contains the exact public
precursor/common-lineage ladder:

```text
DEFAULT -> 0.5 s -> EXTENDED -> 0.7 s -> PROGRAMMING -> 1.0 s -> PROGRAMMING
```

Calvin's current host retains the same sequence. No authorship direction is
inferred from that equality alone.

## 3. `FF00`: verified callback dispatch, bounded erase side effect

Calvin's host sends StartRoutine `FF00` with an address/range payload. Firmware
static analysis proves that this request enters the legitimate erase state
machine and that the operation dispatches through the authenticated callback
word at `FEBF0FD0`, which Calvin's package points at uploaded code
`FEBF0000`.

That makes `FF00` a verified control-flow entry mechanism for the payload.
However, the CPU call graph does **not** prove that the flash controller has
performed zero physical erase activity before, during, or after the callback.
Calvin's journal says repeated use did not erase the chosen application sector;
without retained before/after raw sector evidence, that remains an external
field observation rather than a firmware-static property.

The safe static statement is therefore:

> `FF00` reaches the ordinary erase machinery and dispatches attacker-controlled
> authenticated callback code; do not infer physical erase solely from the
> request range, and do not infer absence of erase solely from the callback edge.

## 4. `R7F701383` memory geometry closes two former uncertainties

The retained official P1M-E datasheet explicitly lists `R7F701383` as a **DPS
1-MiB** product. Its table gives 1-MiB parts **32 KiB DataFlash**. The hardware
manual Table 4.1 / Figure 35.2 maps that array as:

```text
FF200000..FF207FFF  32 KiB DataFlash on a 1-MiB device
FF200000..FF20FFFF  64 KiB DataFlash only on a 2-MiB device
```

Therefore Calvin's `FF200000..FF20FFFF` payload is a 64-KiB **host read range**
when used on the H Corolla. Only the lower half is specified DataFlash;
`FF208000..FF20FFFF` must not be described as DataFlash on `R7F701383`.

The same official sources settle the local-RAM interpretation. P1M-E exposes:

```text
FEBE0000..FEBFFFFF  Local RAM (PE1 area), 128 KiB
FEDE0000..FEDFFFFF  Local RAM (self),     128 KiB
```

while the product has only **128 KiB total local RAM**. The `FEDE` range is an
architectural self view of PE-local RAM, not an additional 128-KiB physical
bank. Calvin's live `R7F701381` FEDE/FEBE result is useful dynamic confirmation
of the documented architecture; it is not the sole reason to apply that
architecture to the explicitly listed `R7F701383` P1M-E part.

The product/address facts, source hashes, and TAUJ1 timer facts are tracked in
`data/p1me_product_memory.json` and asserted by
`tests/verify_p1me_product_memory.py`.

## 5. Repeatability: use only the physical 32-KiB DataFlash for DataFlash claims

Calvin reported that two Sienna **64-KiB host-range reads** 21 seconds apart
differed in 16,703 bytes (25.487%). That remains Calvin field evidence.

For H, retained raw files let us recompute the result. Across five 64-KiB host
reads:

| range | repeats | pairwise divergence |
|---|---:|---:|
| physical `R7F701383` DataFlash `FF200000..FF207FFF` | 5 | **23.5077%-25.6470%** |
| complete 64-KiB FF20 host range, including off-array half | 5 | 26.2650%-27.7328% |
| extended CodeFlash | 3 | 0 bytes |
| global RAM | 3 | 1.193%-1.207% |
| PE1 local view | 3 | 2.805%-3.217% |

Only 17,325 of the 32,768 physical-DataFlash byte positions are identical in all
five captures, and 2,506 positions exhibit more than one distinct nonzero value.
The cause is deliberately not assigned to physical NVM writes. The observation
is only that the returned DataFlash bytes are not repeatable enough for a
single-image byte/null claim to be strong evidence.

The structural NvM result is much stronger. Parsing every retained host read
yields the same disposition each time:

```text
objects 0 / 2 / 5: three valid copies
object 15:          zero valid copies
```

Thus object-15 invalidity is a repeated record-integrity result, not a one-dump
null-byte inference.

## 6. Broad no-key scan: exact geometry, bounded conclusion

The 15 retained Aug-14 range files total 3,162,112 bytes. Adding the earlier
32-KiB capture produces exactly **3,194,640 overlapping 16-byte window
positions** when counted per file. Two synchronization oracles therefore give
**6,389,280 window/oracle invocations**.

That number is geometry, not a guarantee of exactly 6,389,280 low-level CMAC
operations: the matcher may evaluate multiple oracle samples for a candidate.
Calvin's journal reports zero matches and a planted-key positive control at
`0x4000`; the historical run itself is external dynamic evidence.

The epoch boundary matters. Both retained oracles are from sessions different
from the Aug-14 memory acquisition. One retained oracle is `TRIP=0xD0D`; the
public-route oracle is `TRIP=0xCE9`. Therefore the broad negative assumes that
the relevant operational key was stable between those sessions. Even under that
assumption, it excludes only a **raw 16-byte value present in the scanned host
ranges**. It does not exclude transformed/derived storage, ICU-S-internal
storage, a changed key, or a CPU-invisible source. On H, the upper half of the
64-KiB FF20 host range is additionally outside the specified DataFlash array.

## 7. Calvin KEY-table and dealer-rekey claims versus the exact NvM map

Calvin's Sienna journal reports a repeating structure:

```text
+0x00  record index
+0x04  ID       (Calvin label)
+0x08  AuthID   (Calvin label)
+0x14  16-byte value/key
stride 0x40
```

He reports two already-known plaintext values at `FF206E14` and `FF206ED4`,
three `0x40` strides apart. The stride and `+0x14` placement are genuinely
interesting against our exact physical map:

```text
object 15 raw record: FF206E00 -> second field FF206E14
object 14 raw record: FF206E40 -> second field FF206E54
object 13 raw record: FF206E80 -> second field FF206E94
object 12 raw record: FF206EC0 -> second field FF206ED4
```

So `FF206ED4` is **object 12's** corresponding field under exact `4512000`
geometry, not object 14's. The alignment corroborates a `0x40` physical stride
and a `+0x14` value position. It does not establish Calvin's table-wide ID,
AuthID, or “ECU master key” semantics for `4512000`.

Calvin also reports that a dealer rekey left the previous factory SecOC key
readable in plaintext. No retained before/after artifact lets us reproduce that
claim. Keep it as an external field observation and as a future acquisition
requirement, not as a generalized Toyota storage rule.

## 8. SecurityAccess: ten-second bad-key backoff and normal handoff are separate

Firmware proves the bootloader failure state machine:

```text
first bad 27 02
  attempt counter 0 -> 1
  NRC 35

second consecutive bad 27 02
  record current timer
  duration = 200000000 ticks
  delay flag FEBF2B56 = 1
  counter -> 0
  NRC 36

27 01 while delayed
  NRC 37
```

The wall-clock duration is independently recoverable from the actual timer.
`0x1D24` reads `TAUJ1CNT0 @ FFE51010`. Boot timer setup programs
`TAUJ1TPS=FFF2`, whose `PRS0=2` selects `PCLK/4`, and `TAUJ1CMOR0=0156` selects
CK0 counting. The P1M-E peripheral/P-Bus domain is 80 MHz. Therefore TAUJ1
channel 0 runs at 20 MHz and:

```text
200000000 / 20000000 = 10 seconds
```

The initial archaeology mistake was to merge this bad-key backoff with a
separate initializer state. `0x55AA` does arm the same delay during diagnostic
initialization, but the ordinary retained application-to-PROGRAMMING handoff has
CodeFlash record:

```text
0x31914: kind = 0
         diagnostic ID = 0x7A1
         requested session = 0x02
```

Its boot replay follows `0x6504 -> 0x5148 -> 0x562A`; `0x562A` explicitly clears
`FEBF2B56` before the synthetic bootloader `10 02` is replayed. Calvin's
successful seed/key exchanges roughly one second after ordinary PROGRAMMING are
therefore consistent with this handoff-clear path. They do **not** test the
post-two-bad-key backoff.

Operationally: do not sleep ten seconds after every normal PROGRAMMING handoff.
Request SecurityAccess normally; if NRC `0x37` is actually returned, respect the
verified ten-second anti-bruteforce interval.

## 9. Span routing result: code correction is real; the decisive field test remains

Calvin's Aug-19 field journal reports that Span's Corolla answered EPS DEFAULT
on logical bus 1 under both ELM327 `param=0` and `param=1`, with buses 0/2 silent.
The preflight implementation used in that run selected the first answering
route, which—given those observations—was `(bus1,param0)`. PROGRAMMING then went
silent and the subsequent five dump attempts inherited that route.

That makes those five failures **gateway/param0-route observations** if Calvin's
field report is accurate. They cannot decide whether the direct `param=1` route
will open PROGRAMMING.

Final `42d1120` source fixes the selection logic: it probes answering routes
through the diagnostic ladder and selects a route only after PROGRAMMING opens.
`CLAUDE.md` says this revision was mock-tested, but no committed preflight test
at the pinned tip independently proves that statement. More importantly, the
corrected selector has not been demonstrated in-car in the retained record.

The high-value experiment remains:

> On Span's car, does PROGRAMMING and bootloader reappearance succeed on logical
> bus 1 with ELM327 `param=1`?

## 10. What remains externally sourced

The following observations are useful but remain field-report grade until their
source captures are acquired:

- Calvin's complete Sienna 52-file Aug-13 corpus;
- the exact repeated Sienna FEDE/FEBE byte-identity experiment (architecture is
  already documented; this would reproduce the dynamic observation);
- the dealer-rekey before/after DataFlash images;
- the claimed no-erase before/after sector evidence for repeated `FF00` use;
- the original broad zero-key scan runtime artifacts and exact oracle epoch join;
- the Aug-19 Span in-car preflight transcript beyond what the journal records.

The branch is still valuable, but its strongest contributions after this audit
are narrower: authenticated range-payload/package evidence, rewritten-history
archaeology, a reproducible warning about read repeatability, a route-selection
confound, and field observations that identify exactly which raw artifacts would
most improve the next analysis.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [SECOC-067](../../reference/index.md#finding-secoc-067), [VAR-040](../../reference/index.md#finding-var-040)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
