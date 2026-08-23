# Bootloader no-auth PC-pivot assessment

> **Target:** Sienna EPS `8965B4512000`
>
> **Question:** can the unauthenticated application XCP write primitive be
> composed with the live `10 02` programming handoff to execute attacker bytes
> in bootloader context **without** bootloader SecurityAccess?
>
> **Status:** no static PC-redirection primitive recovered. The XCP bytes do
> survive the handoff, but the audited boot ingress/dispatch/copy surfaces do
> not provide the missing jump. The practical path therefore still uses the
> separately recovered boot SecurityAccess secret. This is a bounded negative
> result, not a proof that no undocumented hardware effect can ever exist.

## 1. What the attacker already has before boot entry

COM-005 gives unauthenticated XCP `DOWNLOAD`/`MODIFY_BITS` access to
`FEBF7C00..FEBFFBFF`. The application MPU marks the corresponding shadow region
supervisor-executable. SEC-BOOT-012 then adds the cross-lifecycle fact: normal
application `10 02` is a live handoff, not a reset, and those bytes remain
resident after entering the boot programming runtime.

The exact handoff is:

```text
application XCP DOWNLOAD -> FEBF7C00..FEBFFBFF
                         -> 10 02
                         -> 0x64EC8
                         -> mov 0x31914,r6
                         -> 0x9F00
                         -> SP=FEBE8000 / GP=FEBF9800 / TP=869C / MPM=0
                         -> 0x148E (copy 9 fixed dwords -> FEBF2908)
                         -> 0x1398 -> 0x1338 boot runtime
```

The initially promising idea that `0x148E` might copy attacker-selected state is
false. `0x64EE6` loads the literal CodeFlash address `0x31914` into `r6`
immediately before the call to `0x9F00`. The nine-dword copy is therefore fixed
source data, not an arbitrary write.

So the composition begins with **retained executable bytes**, but still needs a
boot-context control-flow transfer into them.

## 2. Boot indirect-call census

A direct Ghidra-CLI census of boot-region code identified nine meaningful
indirect/code-pointer call sites. They fall into three classes:

1. **CodeFlash-owned dispatch tables.** `boot_eiint_dispatch @ 0x748`, the UDS
   service dispatcher, and the CAN/CanIf callback thunks load targets from
   immutable configuration tables. Runtime selectors are bounded before the
   target load.
2. **RAM flash-driver veneers.** `0x3552`/`0x36BE` and the flash operation path
   call RAM-resident driver entry points around `FEBF11F0/FEBF12B8`. Their
   producers install fixed driver functions; no pre-SA request forwards a
   tester pointer into those cells.
3. **The authenticated payload callback.** `flash_driver_call_block_operation`
   eventually indirect-calls `FEBF0FD0`. This is the known RAM-execution sink,
   but reaching useful mutation of the payload page/callback remains behind
   boot SecurityAccess and the authenticated payload workflow.

The generic CanIf thunk `FUN_3460` was checked separately because it looks like
an ideal pivot:

```c
(**(code **)(param_1 + 4))(param_2);
```

Its `param_1` comes from the immutable boot hardware-route table. CAN ID and IDE
are software-filter comparison values; they do not select an arbitrary
`param_1` or callback address.

A boot-only direct-data-reference census over `FEBF7C00..FEBFFBFF` found no
runtime callback/state consumer in the retained XCP window. The only boot-side
literal high-window write is the already-corrected reset initializer shape at
`0x1426`; its `FEBF7C00 -> FEBE7000` loop is zero-trip.

## 3. Boot UDS dispatcher is not an OOB jump

`uds_service_dispatch @ 0x5222` walks exactly 20 eight-byte records at
CodeFlash `0x8E54`. The selected handler pointer comes from the matching
immutable record. The loop terminates at the configured count, and addressing
mask policy is checked before the call.

The pre-SecurityAccess service surface is therefore limited to ordinary
configured handlers such as session control, reset policy, RDBI,
SecurityAccess, CommunicationControl, TesterPresent, and ControlDTCSetting.
The useful mutation paths (`2E`, `31`, `34`, `36`, `37`) retain their explicit
SecurityAccess/session gates.

No tester SID/subfunction is used as an unchecked function-table index.

## 4. Diagnostic transport does not smash the boot request buffer

The transport/reassembly path was re-derived from the boot image:

- `Dcm_StartOfReception @ 0x6374` rejects total lengths above `0x1000`;
- `Dcm_CopyRxData @ 0x6464` compares each fragment against the remaining
  `0x1000 - cursor` capacity before copying;
- `FUN_6422` independently stops its byte loop at the same 4 KiB boundary;
- successful `Dcm_TpRxIndication @ 0x64B8` dispatches directly from the bounded
  `FEBF30C0` request buffer.

This closes the obvious ISO-TP/CanTp route to a saved-`lp` overwrite.

### 4.1 Suppressed TesterPresent does not create a request-buffer race

The DCM has special handling for functional suppressed TesterPresent (`3E 80`),
which initially looked useful for concurrent-buffer corruption. The state order
closes it:

1. on successful reassembly, `Dcm_TpRxIndication` stores DCM receive state `2`;
2. only **after that store** does it call `uds_service_dispatch @ 0x5222`;
3. `Dcm_StartOfReception` checks the same state at `0x63A2` and immediately
   rejects a new reception when it equals `2`.

Therefore another request cannot reset/refill `FEBF30C0` while a synchronous
SecurityAccess handler is consuming it. The special TesterPresent recognition
does not bypass the state-2 rejection.

## 5. SecurityAccess parser is length-bounded

The remaining high-value unauthenticated parser was SID `0x27` itself.
Instruction-level review closes the simple memory-corruption variants:

- request-seed `0x5328` requires total request length `0x12` before processing
  its 16-byte tester data record;
- send-key `0x53F2` gates on SecurityAccess handshake state and requires total
  request length `0x12` before the fixed 16-byte key calculation/comparison;
- expected-key, seed, and request loops are fixed-width 16-byte operations;
- the request pointer originates from the bounded DCM buffer, not a
  tester-supplied pointer.

No request-controlled destination address, copy length, or saved-return-address
overwrite was recovered in either handler.

## 6. Fixed request-copy helper census

`FUN_67B0` is the generic request-to-local copier used by the boot handlers. Its
callers were enumerated and inspected with direct Ghidra CLI. Configured copy
sizes are fixed by the handlers and fit their local objects:

```text
614A DiagnosticSessionControl   2 bytes
60C2 ECUReset                   2
567E RoutineControl            14
5D68 RequestDownload           13
688A CommunicationControl       3
4FF8 TesterPresent              2
693A ControlDTCSetting          2
5FB8 ReadDataByIdentifier       3
69B0 unsupported-service copy   1
4948 WriteDataByIdentifier     19
5C92 RequestTransferExit        1
```

The large/mutating service families additionally retain their normal session/SA
policy. No caller passes the tester-declared transport length directly as an
unbounded stack-copy length.

## 7. Other candidates closed in the same search

The preceding application-side audit was also revisited because a pivot before
`10 02` would be equally useful. The following candidate classes did not yield
a PC transfer:

- XCP MTA auto-increment or `MODIFY_BITS` boundary crossing: complete accessed
  intervals are validated against `FEBF7C00..FEBFFBFF`; wrap/crossing is
  rejected;
- XCP CAL/PAG/STIM/DAQ: no hidden execute/write-through consumer; DAQ is a read
  source configuration primitive in this calibration;
- LocalRAM architectural aliases: no third alias maps the XCP bytes onto a
  distinct callback object;
- application RAM callback cells and ICU-S interrupt callback pair: producers
  install configuration-owned/fixed targets;
- RoutineControl parsed-value object: configured descriptors do not overrun the
  caller's value slots;
- application DCM generic callback: target provenance is the selected immutable
  CodeFlash service/subfunction descriptor;
- RSCFD receive local buffer: hardware reader copies the fixed classic-CAN data
  words, not a DLC-sized CAN-FD payload;
- CanTp 4 KiB reassembly: independently range-checked;
- indexed callback dispatchers audited from external ingress: bounds precede
  target loads.

These closures explain why the retained XCP code-placement primitive has not
been promoted to a zero-auth RCE claim.

## 8. Practical result: working host path still uses recovered boot SA

The negative zero-auth result does **not** leave the project without an
execution path. The boot SecurityAccess secret is already statically recovered,
and the exact pinned encrypted `ram_dump_payload.bin` fixture is already known
to pass the Sienna 4 KiB CRC/CMAC payload gate with DID `0201/0202` set to zero.
That means execution does not require the payload-build secret.

`exploit/ephemeral_runtime/live_installer.py` now composes the complete guarded
host workflow:

```text
F181-bound application identity
 -> programming transition
 -> recovered boot SecurityAccess
 -> DID 0203 / 0201 / 0202
 -> pinned 4 KiB encrypted fixture
 -> 10F0 authentication
 -> MEM-SAFE-001 <=15-byte raw substitutions
 -> FEBF0FD0 = FEBF0000 written last
 -> FF00 callback trigger
```

It supports the inert canary, the SecOC bridge, and the command-5 proxy. For the
command-5 variant it can wait for the XCP mailbox and issue one 7/12/36-byte
request in the same guarded process. It defaults to plan-only and requires
`--execute --bench-isolated` for hardware execution.

The host choreography is therefore complete. The unresolved questions are now
**dynamic hardware questions**:

- does the inert canary execute and advance foreground exactly as modeled?
- does the SecOC bridge deliver the marked steering records as modeled?
- does provisioned ICU-S slot 4 permit command 5 generation?

Those cannot be answered further from this firmware image alone.

## 9. Evidence boundary

The conclusion is intentionally narrower than “zero-auth execution is
impossible.” It says that the audited software-visible ingress, copy,
dispatch, callback, alias, and handoff paths contain no recovered control-flow
consumer that turns COM-005 into a zero-auth boot PC pivot. A new hardware
observation, undocumented peripheral behavior, or a newly discovered software
path can supersede this assessment.

Deterministic regression: `tests/verify_boot_noauth_pc_pivot_assessment.py`.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [SEC-BOOT-013](../reference/index.md#finding-sec-boot-013)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
