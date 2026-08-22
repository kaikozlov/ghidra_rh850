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
> tracked images. Four focused hypotheses were re-audited on 2026-08-22 against
> raw CodeFlash plus the canonical Sienna control/data-flow graph. The checks
> below are a fast **triage/regression screen**, not a substitute for the fuller
> no-auth control-flow audit in
> [bootloader-noauth-pc-pivot-assessment.md](bootloader-noauth-pc-pivot-assessment.md).
> Deterministic regression: `tests/verify_keyless_exec_surface.py` (suite
> `keyless_exec_surface`).

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

## 7. Payload fixtures and key rotation

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

## 8. Evidence boundary

This is a bounded negative static result over the software-visible surface of
three images, not a universal impossibility proof. New boot generations,
undocumented peripheral effects, alternate hardware routing, or physical fault
injection can change the result. Hardware glitching is out of scope here; the
question is a software-only keyless path.
