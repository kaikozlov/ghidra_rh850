# Fuzz-oracle methodology: proving the oracle before trusting the clean run

> **Scope:** target-agnostic harness method; instantiated on Camry F33 `8965F3307000`
>
> **Document type:** methodology + oracle validation record
>
> **Status:** active
>
> **Evidence profile:** primary-source research + exact-image simulation (`fuzz_camry_f33_cantp_ingress.py`, `fuzz_camry_f33_dcm_handlers.py`; DCM schema `*-v5`)
>
> **Runtime artifacts:** regenerated, untracked summaries under `build/out/targets/camry-8965F3307000/`
>
> **Durable result record:** §9 here and [Camry baseline §13.11](../variants/camry-2026-live-baseline.md)
>
> **Related:** [memory-safety audit](memory-safety-audit.md), [Camry live baseline §13.9–13.11](../variants/camry-2026-live-baseline.md)

A fuzzing campaign is only as strong as its **oracle** — the predicate that
turns a simulated run into "fault" or "clean". An envelope-diff oracle ("no
write escapes this RAM region") silently steelmans the firmware: it reports
clean on every bug class it cannot see. This document records the oracle
weaknesses we found in our own v2 harness, the checks that close them, and the
self-validation protocol that must precede any "0 findings" claim.

## Research basis and operating model

The process is intentionally not derived from what this firmware appears to
defend well. It starts from bug classes and from practices that have found bugs
in mature targets:

- MITRE's [2025 CWE Top 25](https://cwe.mitre.org/top25/archive/2025/2025_cwe_top25.html)
  ranks out-of-bounds write fifth, use-after-free seventh, out-of-bounds read
  eighth, classic buffer overflow eleventh, NULL dereference thirteenth,
  stack overflow fourteenth, and heap overflow sixteenth. Those are separate
  obligations; a write-boundary oracle does not cover the others.
- LLVM's [AddressSanitizer](https://clang.llvm.org/docs/AddressSanitizer.html),
  [MemorySanitizer](https://clang.llvm.org/docs/MemorySanitizer.html), and
  [UndefinedBehaviorSanitizer](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)
  define the source-available reference set: spatial and temporal errors,
  uninitialized uses, invalid frees, bounds/alignment/null errors, bad shifts,
  pointer overflow, integer overflow, and lossy conversions. Exact proprietary
  CodeFlash cannot be rebuilt with them, so every substitute below names the
  sanitizer property it approximates and what remains invisible.
- [OSS-Fuzz's ideal integration](https://google.github.io/oss-fuzz/advanced-topics/ideal-integration/)
  requires a maintained target, minimized coverage-producing seeds,
  dictionaries where applicable, coverage reports, sanitizer regression, and
  speed. [AFL++](https://aflplus.plus/docs/fuzzing_in_depth/) adds feedback,
  corpus optimization, comparison assistance, persistent execution, and
  fuzz-only checksum bypasses. Therefore random trial count is not evidence of
  exploration; reach and coverage are.
- [Fuzzware](https://www.usenix.org/conference/usenixsecurity22/presentation/scharnowski)
  shows that precise, use-directed MMIO models materially improve firmware
  coverage. [MetaEmu](https://arxiv.org/html/2208.03528v1), including an RH850
  case study, couples snapshots and branch coverage with memory/branch/call
  observers and warns that arbitrary satisfying peripheral values are unsound
  where peripheral behavior matters. [FirmWire](https://www.ndss-symposium.org/ndss-paper/auto-draft-200/)
  shows why full-system/API-level, stateful message injection and physical
  reproduction must complement single-function fuzzing.
- [StateAFL](https://arxiv.org/abs/2110.06253) treats protocol state as
  long-lived memory over multiple messages. Project Zero's
  [RCA template](https://projectzero.google/2020/07/root-cause-analyses-for-0-day-in-wild.html)
  requires trigger, root cause, related history, variants, structural fixes,
  and detection ideas; its
  [variant-analysis record](https://projectzero.google/2022/11/mind-the-gap.html)
  documents how often related bugs survive. Every real finding here therefore
  triggers a same-class and same-producer/consumer variant pass.
- [KARONTE](https://sites.cs.ucsb.edu/~chris/research/doc/oakland20_karonte.pdf)
  and [Operation Mango](https://www.usenix.org/conference/usenixsecurity24/presentation/gibbs)
  motivate source-to-sink analysis across component boundaries and analysis of
  all candidate binaries/sinks rather than only the easiest front end. For this
  monolithic image, the analogous boundaries are CAN → CanTp → Dcm → service
  callback → application data/MMIO and the reverse response path.

The resulting loop is: enumerate attacker-controlled sources and memory/lifetime
sinks; recover exact producer/consumer constraints; build both narrow and
end-to-end/stateful harnesses; seed every oracle; measure reach and branch
coverage; triage every deviation to firmware, model, or harness root cause;
minimize; search variants; then reproduce on physical hardware when available.
A clean run is only a result for the cells marked covered in §2.

## 1. Oracle blind-spot registry

Measured against the exact F33 harness and retained as a permanent regression
list:

| Blind spot | Why the old oracle missed it | Closure or current bound |
|---|---|---|
| Zeroing writes | A zero store into zero-filled RAM creates no post-state diff | Address-derived splitmix32 fill |
| Contiguous-envelope bleed | A write from one modeled object into another stays inside the union envelope | Untouched-slot isolation, row invariants, boundary watchpoints |
| Transient stack writes | A push/pop can be overwritten before the final dump | Access-time watchpoints at both application-stack edges |
| Uninitialized reads | Reads do not alter memory | Distinct marker propagation plus independent-fill divergence; object-local poison for output objects |
| Unwritten response bytes | A producer can leave old bytes unchanged while publishing a larger length; normalization also hid unchanged bytes | Full-dispatch RDBI audit poisons the response object twice and checks every transport-visible byte |
| Request over-read | Structured trials used to place padding after the declared request | Prime exactly the declared bytes and place a duplicate request with its final byte at the end of mapped RAM |
| Request/context overlap | The old request at `0xFEBE4200` overlapped the old context at `0xFEBE4240` for requests over 64 bytes | Context moved to non-overlapping `0xFEBE4300`; request, context, response, and slot scratch are distinct |
| Fill-period aliasing | A byte-periodic pattern makes addresses 256 bytes apart indistinguishable | Unique splitmix32 stream per aligned word; deterministic comparator seed |
| Inert structure copies | Padding can move without a live consumer | Exclude only exact bytes whose consumers were disproved; retain source poison |
| Direct-entry precondition invention | A plausible host prime can create or suppress paths | Execute reset chains, document every remaining prime at its consuming gate, and keep separate end-to-end/stateful passes |
| Missing batch terminator | One incomplete batch triggered per-trial fallback and multiplied runtime | Require `TP_END`, retain completed records, retry only unfinished indexes for at most 10 s, abort on the first still-missing result |
| Coarse reach accounting | Entry return says nothing about the intended copy/callback path | Required sink breakpoints and concrete liveness effects; branch/edge feedback remains open (§8) |
| Peripheral wishful thinking | Fabricated MMIO values can unlock impossible paths or suppress real state | Classify the exact blocking instruction and leave the path blocked until a dataflow-faithful model exists |

## 2. Memory-safety class matrix

“Covered” means the named dynamic property was exercised, not that the entire
image lacks that bug class.

| CWE / class | Exact-image check now used | Status and residual risk |
|---|---|---|
| 787, 120, 121, 122 — OOB write / stack or object overflow | Machine `memory_accesses` stores are checked at access time against Camry DCM/CanTp extents derived from `struct_layouts.json`, `data.jsonl`, and firmware receive-slot tables; stack bands have per-context watermarks; existing fences and oversized matrices remain | Covered only for selected typed objects and observed contexts; no write spanning a selected object edge occurred in the current machine batch, and this is not whole-image shadow memory |
| 125 — OOB read / over-read | Exact request objects ending at unmapped RAM; SID `0x23` address/size matrix; poison propagation/divergence; response-byte extent audit | Direct WDBI/Routine/RDBI/RMEM parsers covered at request tail; in-bounds reads from the wrong object remain observable only if they affect control/output |
| 131, 190 — wrong size, truncation, wraparound | FF 12-bit length, SID `0x23` nibble/size, response-capacity, `0/1/max/max±1`, u16 row underflow and pointer/capacity matrices | High-risk decoded lengths covered; not a general UBSan replacement for all arithmetic, shifts, alignment, or conversions |
| 457 — uninitialized use / stale disclosure | Machine `uninitialized-read` faults stop at the reading instruction; response reach is recorded before publication, alongside the existing two-fill and response-poison checks | All 288 GNU-incomplete RDBI cases reached exact `dcm_read_did_service @ 0x962F2` through machine CAN ingress, but none completed a response; no absence conclusion extends beyond those executed prefixes |
| 416, 415 — use-after-free / double free | No dynamic heap allocator was identified in these paths, but static slot reuse, stale callback, double completion, and use-after-return are still temporal classes; multi-frame lifecycle sequences exercise some | **Partial.** Absence of `malloc/free` does not close temporal safety; scheduling the [exact Camry execution contexts](../../data/generated/camry_8965F3307000_execution_contexts.json) and systematic allocate-use-release-reuse sequences remain open |
| 476 — NULL/invalid pointer | Exact return-PC/fault classification, attacker-pointer sentinels, class-edge/callback dispatch probes | Covered where the named paths consume the pointer; not whole-image |
| 843 / bad indirect target — type or callback confusion | Callback-table/class edges, exact active publication table, abnormal-PC and pointer materialization checks | Partial; no CFI/type metadata exists in the binary |
| 362 — race / asynchronous lifetime corruption | `report_camry_f33_preemption_shared_ranges.py` schedules six interrupt deliveries across four scenarios and compares shared ranges | The exact-image run found one shared byte, `0xFEBF1190`, in the crypto interrupt; the read at `0x88EDE` and write at `0x88F5A` execute with `PSW.ID=0`, `PMR=0xFF00`, so the observed access is priority-mask protected. Other interrupt/DMA schedules remain partial |
| 401/770 — resource leak/exhaustion | Stateful transport sequences inspect retained channel/slot state | Partial; no long-duration reset/retry exhaustion campaign |

## 3. Fault-at-access-time: fences

Static post-mortem diffs can miss a transient write that is later overwritten
(the EnvelopeAudit push/pop case). The harness arms **access-time watchpoints**
on boundary bytes after each trial image restore:

- `0xFEBE17FF` — stack underflow (below the app stack band)
- `0xFEBE2000` — stack overflow upward into the next band
- `0xFEBE5B30` — first byte past the modeled `0x110`-byte response buffer
- `0xFEBE4FB2` — past the CanTp channel cells

A hit stops with the faulting PC and is recorded as a finding regardless of the
final dump diff. This is the Fuzzware principle (fault detected at the moment
of the access, not at program end) applied at boundary granularity rather than
per-instruction.

The request-tail pass provides an object boundary rather than one watched byte:
it copies exactly the firmware-declared request length so the last byte lands at
`0xFEBFFFFF`, the final mapped Global RAM byte. Any sequential parser read past
the request faults at access time. Its seed calls the active DID `0x2030`
16-byte writer with destination `0xFEC00000` and must fault at `0x4F9C6`.


## 4. Fill semantics and lifecycle primes

Four state models have distinct purposes and must not be conflated:

- **Executed lifecycle baseline:** exact CodeFlash reset/init functions create
  realistic Dcm/COM/crypto state before direct-entry trials.
- **Pattern fill (broad probe):** every otherwise unprimed aligned word is
  `splitmix32(address ^ (salt << 20))`. It exposes writes and propagated
  uninitialized values, but marker-corrupted control state is not presumed
  vehicle-reachable.
- **Object-local poison (disclosure oracle):** only the response object is
  poisoned while control state stays at its executed baseline. A second salt
  confirms that a matching byte is unwritten rather than a value collision.
- **Physical request-tail guard (read oracle):** control state is zero/lifecycle
  modeled, the request contains no padding, and the object ends at unmapped RAM.

Fill-dependent faults remain findings until triage; they are never silently
reclassified as harness noise.

Pattern fill exposed that zero fill had silently supplied DCM lifecycle state.
Those values are now explicit **lifecycle primes**, each tied to the firmware
gate that requires it:
| Prime | Gate that needs it |
|---|---|
| Executed Dcm reset baseline | Before salted trials, exact CodeFlash `run_init_chain_9887c` resets all nine software timers, event-ring indices/count, callback state, active response state, communication slots, default session, response queue, and receive rows. Calling only its inner `run_init_chain_91ffa` left random RoutineControl cancellation dependent on stale event-ring state |
| Executed COM tracking baseline | Exact CodeFlash `reset_four_96_byte_tracking_arrays @ 0x8E74E` initializes the generation counters consumed by the crypto collector. Without it, RID `0x100E` copied marker-derived COM generations into `0xFEBE5044..504B` |
| Executed crypto reset baseline | Exact CodeFlash `crypto_bank_initialize_work @ 0x69064` clears test elapsed time, phase/result state, qualified mask, fragment history, and key/test material before direct crypto trials. Without it, random collect/advance trials inherited marker-derived `0xFEBE50A2`/`0xFEBE5086` state |
| `DCM_PENDING_SLOT = 0` | `dcm_arbitrate_completed_receive` route-index walk (else garbage route → crash) |
| `dcm_current_dispatch_receive_slot = 0` | receive-route lookup and TX teardown |
| `DCM_REQUEST_PHASE = 0` | `dcm_claim_receive_slot` phase check |
| Exact 32-byte reset state for all three CanTp channel cells plus three zeroed 4-byte flow rows | `reset_cantp_channels_and_seed_flow_parameters @ 0x7B2C4`; otherwise idle Rx-state bytes remain marker-derived |
| `0xFEBE59D8..59EC = 0` | `dcm_initialize_receive_buffers_and_transport_state @ 0x93ABA`; response-deadline selection otherwise incorporates marker state |
| Idle slot rows: cursor=buffer base, len=0, rem=0x100, receiving=0, **abort_pending=0** | `dcm_get_receive_slot_abort_pending` — v2's 4-byte `remaining` prime coincidentally zeroed `receiving`+`abort_pending`; the rebuilt 2-byte prime alone left `abort_pending` as marker and the slot silently bailed |
| Full 28-byte message context, session snapshot, and 8-byte security bitmap | Direct service callbacks consume response length, capacity, addressing, selector, and policy state beyond the three pointers |
| `diag_reset_routine_class_state` block at `0xFEBF3B2C..3BCA` | Routine `0x1002` action state; marker state corrupted SP in a callback return |
| memory-read callback state `01 01 00 FF 00` at `0xFEBF4598..459C` | SID `0x23` application-memory callback phase and selector |
| zeroed DTC-list continuation/scratch plus side status `0xFF` | SID `0x19` continuation and its 0x300-byte local tuple buffer |

The executable Dcm/COM/crypto reset baselines and the lifecycle primes in this
table reconstruct what reset leaves behind; each documents the gate that
consumes it, and the unprimed remainder stays marker. Explicit
peripheral-model exceptions are bounded in §8.

Scratch placement is also an invariant: request `0xFEBE4200`, context
`0xFEBE4300`, active response context `0xFEBE5630`, response object
`0xFEBE5A20`, and retained RDBI context `0xFEBE5D84` do not overlap. Structured
request primes contain exactly the declared bytes; convenient trailing zeros
are forbidden because they can hide over-reads.


## 5. Seeded-oracle validation (mandatory)

Each independent oracle has a bug that must fire through the entire collection
pipeline:

1. **Write/capacity oracle.** Sim-only NOP both capacity branches at `0x92120`
   and `0x92192` in `dcm_copy_receive_data`, then stream FF(0x108)+37 CFs.
   Stock returns clean; the seed writes attacker bytes from slot 0 into slot 1
   and reports `len=0x108`, `remaining=0xFFF8`. Removing only one guard does not
   fire because the other resets the slot.
2. **Divergence comparator.** Two start fills must normalize to no difference;
   changing one enveloped post-state byte under the two salts must be reported.
   Scheduled/compared counts must match before a summary is accepted.
3. **Response extent.** Full dispatcher request `22 20 30` reaches active
   reader `0x4F9B6`. Stock initializes all 19 published response bytes.
   A sim-only two-instruction no-write producer (`mov 0,r10; jmp lp`) preserves
   offsets 3–18, and the oracle must report all sixteen.
4. **Request-tail access.** The active DID `0x2030` writer is given destination
   one byte past mapped RAM. It must fault at the first escaping store
   (`0x4F9C6`), proving the simulator and collector preserve access faults.
5. **Machine definedness.** A sim-only no-write producer (`jmp [lp]`) feeds
   exact `memcpy_forward @ 0x89F2E` from uninitialized Global RAM
   `0xFEEF9000` into the response object. The machine stops at the first
   publication read, PC `0x89F86`, address `0xFEEF9000`, width four.
6. **Object boundary.** With `MCTL.MA=1`, a sim-only exact `sst.h`
   instruction starts at `0xFEBE5D1F`, the final byte of the 768-byte response
   object. The checker reports PC `0xFEBE000C`, width two, crossing the
   `0xFEBE5D20` end.
7. **Stack watermark.** A sim-only entry at exact
   `addi -64,sp,sp @ 0x65AC0` stops at `0x65AC4`. The trace arithmetic must
   report initial `SP=0xFEBE2000`, low `SP=0xFEBE1FC0`, and 64 bytes used.


Rule: a new oracle component ships with a deterministic positive control. A
negative result from an unseeded oracle is not evidence.

## 6. Sink-directed coverage accounting

Clean runs must also prove *reach*: a family that never executes cannot find
anything. Silent logging breakpoints sit at the transport copy/build sinks,
DCM receive/transmit copies, DID length and serialization paths, WDBI action
dispatch, routine callback dispatch and scalar packing, and SID `0x23`'s
application-memory selector and final payload copy. Every trial's summary
records which sinks it hit, grouped by family. Each harness has a
`REQUIRED_SINKS` contract and refuses a clean exit when any relevant sink is
zero; this caught a TX-tick corpus whose missing `0xFEBE4F3D=0xAA` enable
prime made its entry breakpoint look live while its segment builder never ran.
Dedicated liveness canaries also require concrete effects from the dispatcher,
WDBI, RoutineControl, crypto collector, SID `0x22` serializer, and SID `0x23`
copy. `summary.json` carries the complete `sink_hits` accounting. Karonte's
sink-directed idea, inverted: not for taint, but for coverage honesty.

## 7. Protocol fuzzing shape

Transport-level attacks from the DoCAN taxonomy map to trial families: SF/FF
override mid-reception, SN skip/repeat/wrap, surplus CFs past completion
(over-supply), FC matrices (FS × BS × STmin) against a live transmitter with
ROM-identity-correct TxState, and the TX segmenter tick across every state
char. Stateful sequences are single trials (frame chains), so state-machine
reconnaissance is explicit, not an emergent property of random frames.

## 8. Bounded scope and explicit next obligations

The original fixed-matrix GNU sim campaigns in §9 have coarse sink coverage.
The current checkout also contains
[`fuzz_camry_f33_stateful_coverage.py`](../../tools/targets/camry/research/fuzz_camry_f33_stateful_coverage.py):
exact branch tracing, a comparison dictionary, sequence mutation, edge-based
retention/minimization, plateau detection, and multi-service producer-extent
and request-tail audits. Its retained lifecycle-prefix result is in §9.
Direct-entry GNU sim trials use synthetic DCM context. The
[P1M-E machine](../tooling/rh850-build-and-sim.md#p-code-execution-engines)
reports peripheral events for its modeled devices.

### Typed-event P1M-E campaign

[`fuzz_camry_f33_machine_typed_events.py`](../../tools/targets/camry/research/fuzz_camry_f33_machine_typed_events.py)
executes exact-image machine scenarios whose identity is the tuple of four
ordered streams: channel-1 CAN receive, TAUJ0 P-Bus clock ticks, interrupt
offsets, and channel-1 CAN transmit completion. An offspring changes exactly
one stream. CAN events carry identifier, payload length, service, subfunction,
and record fields. The encoder regenerates ISO-TP SF/FF length and CF sequence
for `identifier-coherent`, service/subfunction/record substitution,
`integrity-break`, and `length-coherent` mutations. `length-broken` is the
separate declared-length violation class. The selected lifecycle requests
contain no recovered MAC or freshness field, so the campaign makes no claim
that it can recompute either; opaque records are preserved unless their named
mutation class changes them.

The real-ingress corpus uses firmware-decoded receive rules 43 (`0x7A1`) and
44 (`0x777`). The transmit-completion seed first lets the exact firmware emit
its diagnostic response, then schedules completion of channel-1 buffer 22.
Feedback combines consecutive-PC branch edges, machine peripheral-event kinds,
branch-consuming compare operands, and input-derived table indices. Compare
values and indices feed the next batch's substitution dictionary. New edges or
event kinds retain the complete stream tuple under `corpus/`. `summary.json`
records the edge set, every executed input, retained IDs, observation and
dictionary sizes, and per-source executed, mutated, and retained-offspring
counts. `--target-function` weights parents by static direct-call distance; the
summary separately states whether the named target actually executed.

Each case runs from the complete-machine checkpoint after the readiness
prelude; tracing starts at the `normal-operation` checkpoint step
(`instruction_trace_start_step`), so the prelude is not traced. Campaign cases
run for two foreground cycles, which lets segmented input complete and dispatch.
Every case is screened untraced first. A typed fault or a trial that does not
reach its configured arrival stop is recorded as an outcome, not a runner
error. Completed trial results are written atomically under `results/`; a valid
result is reused on restart and a truncated result is discarded.

The GNU-sim lifecycle corpus has 1,332 prefixes. Its 222 poll, 222 completion,
222 timeout, and 222 reuse prefixes have external machine-event equivalents.
The 222 direct-cancel prefixes and 222 pending-completion prefixes do not:
cancel and the pending completion status are internal DCM callback arguments,
not peripheral events. The campaign runs one distinct real-ingress
representative for each reproducible event shape (five executed).

The READY-state campaigns reuse capture-replay bring-up: the bootstrap plus 25
empty cycles, checkpointed after 26 completed foreground cycles with live,
desired, and active mode `0x0702`. Four 120-execution campaigns (6 seeds,
114 mutations, batch size 8, seed 20261126) ran under
`build/out/targets/camry-8965F3307000/typed-event-d4-final-20261127/`. Every
input reached `stop-after-arrivals` with no typed fault:

| Campaign | Edges | Retained | Inputs reaching target | Learned compare tokens | Mean traced rate |
|---|---:|---:|---:|---:|---:|
| `app_security_compare_key @ 0x8D91A`, directed | 34,258 | 31 | 25 | 3,177 | 3.80 M instructions/s |
| `0x8D91A`, uniform parents | 34,295 | 48 | 3 | 3,184 | 3.71 M instructions/s |
| `execute_write_did_payload_and_report_result @ 0x95674`, directed | 33,657 | 42 | 40 | 3,145 | 3.64 M instructions/s |
| `0x95674`, uniform parents | 34,365 | 49 | 5 | 3,161 | 3.70 M instructions/s |

The unmutated positive controls establish target reachability before mutation:
segmented `27 04` reaches `0x8D91A` at absolute instruction 39,686,925, and
single-frame `2E 20 12 01` reaches `0x95674` at 39,289,285 and transmits
`6E 20 12`. The directed campaigns first reach their target at execution 4,
which is the target-specific positive seed. Directed parent weighting finds 40
target-reaching inputs versus 5 with uniform parents for `0x95674`, and 25
versus 3 for `0x8D91A`. Each campaign observes 21–22 peripheral event kinds
and 439–450 distinct input-derived table indices. Its 29 timer mutations all
complete, retain 5–10 offspring, and contribute 82–150 new global edges.

A typed timer event adds one P-Bus clock cycle; bulk additions are rejected.
An earlier harness injected 400,000 P-Bus cycles at one instruction boundary,
and every campaign then stopped its 29 timer mutations and one seed with
`unsupported-csih-operation`. The first trigger launched the five-word
CSIH2/3 transfers, and the same clock event reached the next trigger before
the board fixture's relative `csih-word` input, 128 instructions after launch.
The write is the firmware's own DMA trigger:
`configure_enabled_serial_dma_descriptors @ 0x60E5A` programs DMAC0.1 from
the descriptor at `0x314AC` (`0x31404` → `CSIH2MCTL2`) and DMAC1.1 from
`0x314D4` (`0x31408` → `CSIH3MCTL2`); both source words are `0x80050005`.
The table consumed by `load_indexed_serial_register_configuration @ 0x60D8C`
sets `MCTL0.MMS=01` (dual buffer) and `BRS=0x000A`, which is 4 MHz: one
16-bit word takes 4 µs and five words 20 µs, or 3,200 instruction periods at
160 MHz (R01UH0585EJ0120 §§14.3.4, 14.3.11, and 14.3.16, pp. 540–563).
TAUJ0 counts the undivided 80-MHz P-Bus, so its 16,000-tick shortest period
is 200 µs (§24.3.2.1, pp. 1887–1889). The manual prohibits writing
`CSIHnMCTL2` while `CSIHnSTR0.TSF=1` (§14.3.18, Table 14.34, p. 567); the
device-model boundary was correct and the bulk clock advance was the defect.
`write_serial_halfword_matrix_when_idle @ 0x60EFA` applies the same rule to
buffer fills: it returns `0x5A` unless `TSF` (bit 7) is clear.

A `register-write` row's `pc` is the CPU counter at the instruction boundary
that delivered the write. In restored trials the writes to the six TSG3
compare registers and both CSIH `MCTL2` registers are DMA transfers
(`initiator` `DMAC0.5`/`DMAC1.5` and `DMAC0.1`/`DMAC1.1`), so their `pc` is
wherever the CPU was: `0x80B9E`, an `ld.bu`, or the `0x66066`/`0x6606A` wait
loop. CPU writes keep their store address, for example `CFSTS5` at `0x83D58`.
The `unsupported-csih-operation` fault is raised on the DMA channel's `MCTL2`
write and carries the same CPU position.

All 13 configured WDBI records have one- or two-byte payloads and are therefore
single-frame requests. A separate overlength segmented assertion from the
operational checkpoint covers every configured DID: each request reaches the
service dispatcher at `0x95978`, first reports its NRC through
`check_write_did_length_and_security @ 0x95734`, stages `7F 2E 13`, and never
reaches the write callback dispatcher at `0x95674`. The final-response
coordinator clears the leading `7F` after completion; the end-state assertion
therefore checks the retained service/NRC bytes `2E 13`.

The independent RID `0x100F` compare-gate benchmark reaches its target. Raw
substitution requires 28,572 executions, the former static dictionary 953, and
the eight learned operands 18.

### Cross-engine lifecycle replay

[`compare_camry_f33_lifecycle_engines.py`](../../tools/targets/camry/research/compare_camry_f33_lifecycle_engines.py)
runs every stateful-fuzzer seed plus five deterministic representatives from
each machine-representable poll, completion, timeout, and reuse class. It
records a checkpoint after every case step. GNU sim restores the same
READY-derived image used by reconstructed C. Each machine batch reuses the
firmware bring-up from the capture-replay producer, runs one bootstrap and 25
empty foreground cycles until live, desired, and active mode all equal
`0x0702`, then restores that complete checkpoint before each case. Requests are
scheduled through native FIFO ingress, one foreground cycle per step. A
segmented period takes two cycles after its frames: the first-frame step runs
the full cycle whose communication phase transmits flow control, the ECU
flow-control confirmation follows one wait-loop iteration later, and the last
consecutive-frame step runs the full cycle in which CanTp processes the
consecutive frames (`cantp_handle_consecutive_receive`), indicates the request
to Dcm (`dcm_receive_indication`) and posts the dispatch after a delay; the
period's native cycle is the dispatch cycle. With one cycle, that cycle only
processes the consecutive frames and Dcm posts the dispatch after a delay, so
the request is never dispatched inside the period; a 10,000-instruction gap
before each consecutive frame does not change that.
Each batch runs as one machine invocation with its scenario digest stored
beside its report; a rerun reuses every batch whose digest matches. Machine
registers are not compared with direct-call registers because the paths do
not share an ABI checkpoint.

```sh
uv run --locked python \
  -m tools.targets.camry.research.compare_camry_f33_lifecycle_engines \
  --out build/out/targets/camry-8965F3307000/lifecycle-cross-engine-segmented-20261126 \
  --timeout 120 --batch-size 16
```

`report.json` contains the compared ranges, first differing bytes, diagnoses,
isolated native-host faults, and the generic native oracle result. The
Dcm-contract state excludes the time-relative software-timer table
`0xFEBE39C0..0xFEBE3DDF` and five path-only ranges: communication-cycle
crypto-bank state `0xFEBE5060..0xFEBE50C0`, CanTp-owned active
transaction/message context `0xFEBE5624..0xFEBE564D`, CanTp receive-slot
payloads `0xFEBE5651..0xFEBE5950`, both CanTp channel banks
`0xFEBE4EFC..0xFEBE4FB1`, and the direct harness's synthetic proprietary
callback context `0xFEBE52BC..0xFEBE52D7`. Firmware creates the last range only
in `snapshot_seven_word_context_and_call_4d4c2_8e672`; callbacks at `0x8E6BA`
and `0x8E6D2` consume it. Generic DCM ingress does not execute that producer.
The timer and crypto-bank ranges advance on the machine's full foreground
communication cycle; direct calls have no corresponding boundary.

The run materialized a fresh normal-operation LocalRAM image, executed 318
seeds and 20 lifecycle representatives (338 cases, 392 checkpoints, 0 engine
failures), and classified every machine checkpoint against GNU sim:

| Class | Checkpoints | Equal | Foreground-cycle only | Contract-diverged |
|---|---:|---:|---:|---:|
| request | 306 | 269 | 31 | 6 |
| poll | 12 | 3 | 7 | 2 |
| completion | 10 | 1 | 4 | 5 |
| timeout | 10 | 2 | 6 | 2 |
| reuse | 54 | 13 | 22 | 19 |
| **Total** | **392** | **288** | **70** | **34** |

GNU sim equals reconstructed C at all 392 checkpoints. Foreground-cycle-only
checkpoints differ solely in the excluded per-cycle ranges (the service's
application work runs after the Dcm call on the machine; a segmented period
adds a second cycle of that drift). The 34 contract-diverged checkpoints:

| Class | Count | First differing row | Owning function |
|---|---:|---|---|
| ECUReset execution | 3 | `ecu_reset#1`: `0xFEBE5A20` GNU `51000000` / machine `00000000`, no `can-tx`, the return-to-wait step never reaches the wait point; `reset_reuse#2`, `#3`: `0xFEBE564E` GNU `000001` / machine `020001` | `dcm_dispatch_direct_service @ 0x91422` writes the response prefix, `dcm_reset_receive_slot_and_optionally_shared_response @ 0x93CA0` clears it 987 instructions later; the direct engines model the reset step as cleared session state while the machine answers `2E 20 12 01` with `6E 20 12` and keeps session `02` |
| Response-buffer lifetime | 16 | `request_download#1`: `0xFEBE5A20` GNU `74000000` / machine `00000000`; also `transfer_data#1`, `transfer_exit#1`, four `truncated_*_routine_1010_completion#2`, two `truncated_*_routine_1010_timeout#2`, `truncated_35_routine_1010_poll#2`, `session_security_sequence#2..4` (GNU holds the ECU flow-control bytes `5003003201f4`), `rdbi_0102#1` (`0xFEBE5A28` GNU `67` / machine `62`) | same prefix write at `0x91422` and reset at `0x93CA0`; the direct engines retain the response bytes after the Dcm call, the machine hands the shared buffer to the next request |
| Synthetic DCM callback action | 12 | `pending_poll_cancel_reuse#3`: `0xFEBE5D24` GNU `00000000` / machine `a5a5a5a5`; the six `three_slot_interleave#2..6` checkpoints hold the other slot's response (`7101100f…` / `6220304a…`) | the cancel, poll and completion callbacks the direct engines invoke have no external event on the machine |
| Programming admission state | 2 | `programming_null_transfer_sequence#3`, `#4`: `0xFEBE5D4C` GNU zeros / machine `a107031002010001` | `dcm_programming_pending_response_join @ 0x95BD0` builds the constructed programming request only on the machine |
| Security seed value | 1 | `security_seed#1`: `0xFEBE5A22` GNU `bdcd5f4d…` / machine `4ac14013…` | the seed bytes are not reproducible across engines |

Segmented release is no longer a diverged class: `security_key#1`,
`rmba_ram_16#1`, `routine_1010#1`, `rdbi_segmented_multi#1` and the
`session_security_sequence` seed request are released to Dcm and dispatched.

### Machine definedness, object boundaries, and stack watermarks

[`audit_camry_f33_definedness_boundaries.py`](../../tools/targets/camry/research/audit_camry_f33_definedness_boundaries.py)
has two distinct execution sets. The retained direct-call set restores the
normal-operation LocalRAM image and calls the exact reset/init, session,
communication, and DCM routines; it preserves the original 288
GNU-incomplete-RDBI access-time observations.

The transport-complete set restores the full 26-cycle machine checkpoint for
each case and enters through FIFO5/GAFL rule 43. It executes all 242 configured
RDBI DIDs in the operational session, all 13 configured WDBI DIDs with
multi-frame records, all 19 configured RoutineControl RIDs with records longer
than seven bytes, and seven directed ISO-TP shapes: undersupplied FF, CF
overrun, FC Wait, FC Overflow, and block sizes zero, one, and two. ECU flow
control, tester flow control, and channel-1 buffer-22 completions are scheduled
as separate typed events. A response is complete only after its declared
single-frame payload or its first frame and every required consecutive frame
appear on `can-tx` rows.

Machine `uninitialized-read` faults retain PC, address, width, and publication
reach. Every `memory_accesses` store is checked against 98 selected Camry
DCM/CanTp extents. Each case result is written atomically; valid results resume
and truncated results rerun. The five Sienna `ApplyRamTypes` rows remain naming
precedent only; no Sienna address is applied to Camry.

```sh
uv run --locked python \
  -m tools.targets.camry.research.audit_camry_f33_definedness_boundaries \
  --ingress-only \
  --out build/out/targets/camry-8965F3307000/d5-ingress-final
```
The transport-complete run (281 executions, each ending at its instruction
budget with no `MachineFault`) produced:

| Corpus | Executions | Completed responses | Uninitialized reads | Crossing stores | Stores checked |
|---|---:|---:|---:|---:|---:|
| FIFO5 RDBI | 242 | 242 | 0 | 0 | 65,496,663 |
| FIFO5 long WDBI | 13 | 13 | 0 | 0 | 3,541,395 |
| FIFO5 long RoutineControl | 19 | 19 | 0 | 0 | 5,175,505 |
| ISO-TP length/flow-control shapes | 7 | 5 | 0 | 0 | 1,902,658 |
| **Transport-complete total** | **281** | **279** | **0** | **0** | **76,116,221** |
| Direct-call RDBI cells (separate execution set; no transport) | 288 | 0 | 0 | 0 | 1,238,835 |

The direct-call set is a different execution set, not a transport result: its
288 cells reach `dcm_read_did_service @ 0x962F2` and write response bytes, but
the direct sequencer publishes no `can-tx` row. Its figures stay separate from
the 281 ingress executions.

All service cases completed through `can-tx`. The two shapes without a
complete response:

| Case | Last observation |
|---|---|
| `shape-ff-declared-more-than-supplied` | FF `10402e2001000102` (64 declared) and CF `2103040506070809` popped; ECU flow control `5003003201f4` transmitted and confirmed; no service response or NRC through the 6,000,000-instruction budget |
| `shape-response-fc-overflow` | response FF `102462f181023839` (36 declared) transmitted; tester FlowControl Overflow `3200000000000000` popped; no consecutive frame or NRC through the 4,000,000-instruction budget |

Oracles on the transport-complete set: definedness 0 uninitialized reads;
object boundary 0 crossing stores in 76,116,221 stores against the 98 selected
extents; stack watermark not evaluated (the ingress runs carry no instruction
trace). The three controls fired: the first uninitialized publication read is
PC `0x89F86`, address `0xFEEF9000`, width four; the crossing store is PC
`0xFEBE000C`, address `0xFEBE5D1F`, width two, one past the end of
`dcm_shared_response_buffer`; the stack control uses 64 bytes from
`0xFEBE2000`, lowest SP `0xFEBE1FC0`, 1,984 bytes of lower-edge margin, no
finding.

The execution-context artifact producer computes stack depth from exact
instruction traces. A finding margin is 256 bytes from the lower edge of the
named stack band.

| Context trace | Initial SP | Lowest SP | Widest use | Lower-edge margin | Finding |
|---|---:|---:|---:|---:|---|
| TAUJ0 channel 0 / EIC133 | `FEBE2000` | `FEBE1FA4` | 92 | 1,956 | no |
| TAUJ0 channel 1 / EIC134 | `FEBE2000` | `FEBE1FA4` | 92 | 1,956 | no |
| TAUJ0 channel 2 / EIC135 | `FEBE2000` | `FEBE1FA4` | 92 | 1,956 | no |
| native foreground at `0x66062` | `FEBE7800` | `FEBE77F8` | 8 | 2,040 | no |

Remaining obligations:

- Establish a retained, reproducible campaign baseline: covered branch edges,
  state transitions, semantic sinks, completed/blocked cases, and minimized
  seeds. Distinguish direct-entry tests from peripheral-to-consumer execution.
- Extend cross-engine replay through all scheduled interrupts and peripheral
  completion events in the [exact execution-context catalog](../../data/generated/camry_8965F3307000_execution_contexts.json);
  concurrency, resource ownership, and asynchronous lifetime properties need
  their own checks.
- Exact proprietary CodeFlash cannot be built with ASan/MSan/UBSan/CFI.
  Fences, redzones, poison, invariants and faults approximate selected
  properties, not general byte-granular address/definedness/lifetime shadow
  memory. Sanitized reconstructed C can supplement, but not replace, exact
  original-byte execution.
- Audit response extent and completeness by service and continuation state;
  retain results from the implemented multi-service audit and account for
  asynchronous and transport-visible output, incomplete cases and genuine
  peripheral dependencies.
- Prefer typed event streams for separate input sources, with deterministic
  schedules and minimized reproductions. Relevant precedents are
  [Hoedur](https://www.usenix.org/conference/usenixsecurity23/presentation/scharnowski),
  [MultiFuzz](https://www.usenix.org/conference/usenixsecurity24/presentation/chesser),
  [AidFuzzer](https://www.usenix.org/conference/usenixsecurity25/presentation/wang-jianqiang),
  and [GDMA](https://www.usenix.org/conference/usenixsecurity25/presentation/scharnowski).
  Measure silent corruption at access time as motivated by
  [Muench et al. (NDSS 2018)](https://doi.org/10.14722/ndss.2018.23166).
  Hardware validation belongs on an isolated non-actuating bench, not an
  installed safety-critical ECU.
- Of 726 RDBI DID/session executions, 288 remained incomplete in the modeled
  state and expose no completed response span to judge. Only the 429 completed
  positives support the no-stale-byte result.
- The request-tail guard covers direct WDBI, RoutineControl, RDBI, and RMEM
  requests up to 0x100 bytes. It does not prove arbitrary parser reads that
  remain within a larger legitimate object or reads on unmodeled services.
- Direct callback entry bypasses parser, transport, the
  [cataloged scheduler contexts](../../data/generated/camry_8965F3307000_execution_contexts.json),
  and concurrent state. Stateful CanTp frame chains and the full-dispatch RDBI
  pass reduce, but do not eliminate, that reachability gap.
- Returned stack scratch `0xFEBE1800..1FFF` remains excluded from final-state
  divergence; edge watchpoints and escaped marker propagation still apply.
  Three retained context bytes (`0xFEBE5D96..5D97`, `0xFEBE5D9D`) remain
  excluded only because exact-target consumers were disproved.
- PMR save/restore thunks are simulator-only replaced, so priority-mask
  effects are not observed.

These are work queues, not footnotes to a whole-image “clean” claim.

## 9. Executed validation and resumed analysis

The 2026-10-25 campaigns execute exact CodeFlash SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.

| Harness/pass | Executions | Completed/compared | Firmware findings | Explicitly blocked |
|---|---:|---:|---:|---:|
| CanTp ingress main, seed `49831` | 487 | 487 returns | 0 | 0 |
| CanTp independent fill | 10 | 10 comparisons | 0 | 0 |
| DCM/crypto/TX main v5, seed `53628` | 13,163 | 13,163 returns | 0 | 0 |
| DCM independent fill | 132 | 132 comparisons | 0 | 0 |
| Exact request-tail guard | 6,199 | 6,190 returns | 0 | 9 DCRA1 |
| Full-dispatch RDBI response extent | 726 (242 DIDs × 3 sessions) | 429 completed positives; 288 incomplete | 0 unwritten published bytes | 9 DCRA1 |
| Lifecycle-prefix memory-access audit | 1,554 | 1,554 lifecycle completions | 4 read mechanisms (218 events) | 0 |
| Machine RDBI definedness | 288 | 288 service entries; 0 completed responses | 0 uninitialized reads | 288 incomplete responses |
| Machine object boundaries | 315 | 1,347,615 stores compared | 0 crossings | 0 |
| Context stack watermarks | 4 traces | 4 contexts compared | 0 within 256-byte margin | 0 |
| Machine ingress definedness, transport-complete | 281 | 279 completed responses | 0 uninitialized reads | 2 shapes without a complete response |
| Machine ingress object boundaries | 281 | 76,116,221 stores compared | 0 crossings | 0 |

All required main-pass sinks were nonzero. All seven positive controls in §5
fired. The response audit had zero first-pass poison candidates and zero
poison-value collisions. The nine blockers in each new pass are the same three
DIDs (`0x0105`, `0x010B`, `0xF18C`) in sessions 1, 2, and 3 at `0x67066`;
exact disassembly classifies them as unmodeled CRC MMIO, not an OOB event.

This also tests the cross-target stale-response bug class without copying a
foreign conclusion: the Camry's exact 242-row active publication table at
`0x2927C` was enumerated, and every byte in every completed positive response
was overwritten. The Sienna `8965B4512000` no-write callback result remains a
Sienna fact; it is not present on these completed Camry paths.

The DCM harness writes `summary.json` with schema
`camry-f33-dcm-handlers-original-rh850-fuzz-v5`. The
[Camry baseline](../variants/camry-2026-live-baseline.md) records the
lifecycle-prefix findings.

### Gallia reference comparison

The reference is [Gallia 2.2.0](https://github.com/Fraunhofer-AISEC/gallia),
called in process through `UDSServerTransport.handle_request`.

```sh
uv run --locked --with gallia==2.2.0 python -m tools.targets.camry.research.compare_camry_f33_uds_reference compare
```

The GNU-sim DCM harness supplies the firmware response for every cell in the
eleven-service static policy: 23 `(service, session, security)` cells and three
requests per cell, for 69 comparisons. Each cell receives a minimal
well-formed request, that request truncated by one byte, and an unsupported
subfunction, DID, memory identifier, or RID. SID `14`, which has no selector,
uses an overlength request for the third case. The static table configures no
current SecurityAccess gate, so every cell uses security level zero.

The comparison covers response class, echoed response SID, echoed subfunction,
DID or RID, NRC, and total response length. Record payload bytes unavailable
to the reference are excluded. RDBI lengths come from the exact 242-row DID
table; RoutineControl record lengths come from the recovered routine report;
ReadMemoryByAddress uses the requested size. The seed requests `2703` and
`2701` are both complete two-byte requestSeed messages; `2703` compares equal
in class, echo, and length as `67 03 <16-byte seed>`.

| SID | Cells | Compared | Equal | Class b | Class c |
|---|---:|---:|---:|---:|---:|
| `10` | 3 | 9 | 9 | 0 | 0 |
| `14` | 2 | 6 | 6 | 0 | 0 |
| `19` | 2 | 6 | 6 | 0 | 0 |
| `22` | 3 | 9 | 9 | 0 | 0 |
| `23` | 1 | 3 | 3 | 0 | 0 |
| `27` | 2 | 6 | 5 | 0 | 1 |
| `28` | 1 | 3 | 3 | 0 | 0 |
| `2E` | 2 | 6 | 6 | 0 | 0 |
| `31` | 3 | 9 | 9 | 0 | 0 |
| `3E` | 3 | 9 | 9 | 0 | 0 |
| `85` | 1 | 3 | 3 | 0 | 0 |
| **Total** | **23** | **69** | **68** | **0** | **1** |

There is no class **b** row. The one class **c** row is caused by a
firmware-specific compiled stub that the reference model does not represent:

| Request | Session / security | Firmware response | Reference response | Static row and handler cause | Source |
|---|---|---|---|---|---|
| `2701` | `2 / 0` | `7f2713` | `6701 (00×16)` | `0x25C30:01` admits level-1 requestSeed in programming session; `bne 0x9697A @ 0x9695C` enters the error path and `movea 19, r0, r7 @ 0x96982` selects NRC `0x13`; the level-1 handler is the compiled stub named by the diagnostics report | [diagnostics report](../diagnostics/application.md#level-dispatch-level-1-is-a-compiled-stub); [Gallia request model](https://github.com/Fraunhofer-AISEC/gallia/blob/v2.2.0/src/gallia/services/uds/core/service.py#L770-L814) |

The JSON result is
`build/out/targets/camry-8965F3307000/gallia-reference/report.json`.

## 10. Throughput and fail-fast contract

Every batch requires a completion record. A missing `TP_END` retries only
unfinished indexes; each singleton retry has a 10 s timeout. The first
incomplete singleton aborts the run.
