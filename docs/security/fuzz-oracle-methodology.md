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

The audit also found malformed direct SID `0x22`/`0x23` payloads, incoherent
synthetic queue/TX state, non-reused GDB breakpoint numbers, and a divergence
pass that deleted its alternate dump before comparing it. Those were harness
defects, not firmware findings. Each now has an executable liveness or
self-test. No harness anomaly is downgraded merely because it is inconvenient.

## 2. Memory-safety class matrix

“Covered” means the named dynamic property was exercised, not that the entire
image lacks that bug class.

| CWE / class | Exact-image check now used | Status and residual risk |
|---|---|---|
| 787, 120, 121, 122 — OOB write / stack or object overflow | Whole-window diff, untouched-slot isolation, row invariants, four access-time fences, oversized transport/service matrices | Covered for named entries and modeled objects; no byte-granular shadow memory for every global/stack object |
| 125 — OOB read / over-read | Exact request objects ending at unmapped RAM; SID `0x23` address/size matrix; poison propagation/divergence; response-byte extent audit | Direct WDBI/Routine/RDBI/RMEM parsers covered at request tail; in-bounds reads from the wrong object remain observable only if they affect control/output |
| 131, 190 — wrong size, truncation, wraparound | FF 12-bit length, SID `0x23` nibble/size, response-capacity, `0/1/max/max±1`, u16 row underflow and pointer/capacity matrices | High-risk decoded lengths covered; not a general UBSan replacement for all arithmetic, shifts, alignment, or conversions |
| 457 — uninitialized use / stale disclosure | Address-distinct whole-state markers, two-fill divergence, object-local two-salt response poison | Consumer-visible propagation covered in named state/output objects; no instruction-level definedness shadow |
| 416, 415 — use-after-free / double free | No dynamic heap allocator was identified in these paths, but static slot reuse, stale callback, double completion, and use-after-return are still temporal classes; multi-frame lifecycle sequences exercise some | **Partial.** Absence of `malloc/free` does not close temporal safety; interrupt/task scheduling and systematic allocate-use-release-reuse sequences remain open |
| 476 — NULL/invalid pointer | Exact return-PC/fault classification, attacker-pointer sentinels, class-edge/callback dispatch probes | Covered where the named paths consume the pointer; not whole-image |
| 843 / bad indirect target — type or callback confusion | Callback-table/class edges, exact active publication table, abnormal-PC and pointer materialization checks | Partial; no CFI/type metadata exists in the binary |
| 362 — race / asynchronous lifetime corruption | None beyond ISR-band canaries | **Open:** interrupts, DMA, timer ordering, and task races are not scheduled |
| 401/770 — resource leak/exhaustion | Stateful transport sequences inspect retained channel/slot state | Partial; no long-duration reset/retry exhaustion campaign |

The old statement “no allocator, therefore no UAF” is withdrawn. Firmware
frequently encodes lifetimes in static pools, ownership flags, callback slots,
and asynchronous completion state; those can fail temporally without a heap.

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

- There is no basic-block/edge feedback yet. Required sink hits prove coarse
  reach, not branch saturation. The next fuzzer architecture must collect
  branch edges, retain/minimize new-coverage inputs, use UDS/DoCAN dictionaries
  and comparison assistance, and stop by a coverage plateau rather than a
  trial count.
- No source build exists for ASan/MSan/UBSan/CFI. Fences, redzones, poison,
  invariants, and faults approximate selected properties; they are not
  byte-granular address/definedness/lifetime shadow memory.
- No interrupt, DMA, timer, or task scheduling is modeled. ISR stacks are
  canaries only; races and asynchronous use-after-release remain open.
- No dataflow-faithful DCRA1/FACI/DataFlash model exists. Nine response trials
  and the same nine request-tail trials stop at `dcra1_crc_raw_words +
  0x6 @ 0x67066`, whose exact instruction is `sst.b 0x1c,ep,r0` after loading
  `ep=0xFFD51004`. They are **peripheral-blocked**, not clean and not firmware
  memory faults. SID `0x23` memory ID 2 likewise reaches the real
  latched-driver rejection path, not a successful DataFlash read.
- The full-dispatch extent pass covers RDBI only. WDBI, RoutineControl,
  negative responses, asynchronous pending/completion responses, and transport
  segmentation need equivalent producer-extent checks.
- Of 726 RDBI DID/session executions, 288 remained incomplete in the modeled
  state and expose no completed response span to judge. Only the 429 completed
  positives support the no-stale-byte result.
- The request-tail guard covers direct WDBI, RoutineControl, RDBI, and RMEM
  requests up to 0x100 bytes. It does not prove arbitrary parser reads that
  remain within a larger legitimate object or reads on unmodeled services.
- Direct callback entry bypasses parser, transport, scheduler, and concurrent
  state. Stateful CanTp frame chains and the full-dispatch RDBI pass reduce,
  but do not eliminate, that reachability gap.
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

All required main-pass sinks were nonzero. All four positive controls in §5
fired. The response audit had zero first-pass poison candidates and zero
poison-value collisions. The nine blockers in each new pass are the same three
DIDs (`0x0105`, `0x010B`, `0xF18C`) in sessions 1, 2, and 3 at `0x67066`;
exact disassembly classifies them as unmodeled CRC MMIO, not an OOB event.

This also tests the cross-target stale-response bug class without copying a
foreign conclusion: the Camry's exact 242-row active publication table at
`0x2927C` was enumerated, and every byte in every completed positive response
was overwritten. The Sienna `8965B4512000` no-write callback result remains a
Sienna fact; it is not present on these completed Camry paths.

The current durable artifact is
`build/out/targets/camry-8965F3307000/dcm-handlers-fuzz/summary.json`, schema
`camry-f33-dcm-handlers-original-rh850-fuzz-v5`. It is reproducible output, not
committed evidence. The bounded conclusion is: no candidate surfaced under the
named checks and completed paths. It is not an absence proof for the image.

The lifecycle-prefix pass answers the "clean run" objection differently: its
oracle sensitivity is proven by the real defects it found, not only by seeded
controls. Strict truncation of every seed, paired with asynchronous and
slot-reuse lifecycle actions, exposed four distinct declared-length read
mechanisms — including a one-byte subfunction read reproduced through real
CanTp ingress and a six-byte stale token consumption — while confirming zero
writes outside the corrected object envelopes and zero hangs across 1,554
cases in 292 s. Findings, exact sites, and consequence closures are recorded
in [camry-2026-live-baseline §13.12](../variants/camry-2026-live-baseline.md).

## 10. Throughput and fail-fast contract

Speed is a security property because a harness that falls into retry
amplification stops exploring. Optimization may not remove the corpus, 128 KiB
restore/dump, fences, sink breakpoints, or host oracles.

The retained optimizations are:

- equal checked spans take the C-level `bytes` fast path before bytewise
  finding construction;
- independent 512-trial batches run through four bounded workers;
- sparse second-fill samples are packed into one dense batch; and
- missing `TP_END` retries only unfinished indexes, caps each singleton at 10 s,
  and aborts after the first still-incomplete singleton.

The prior equivalent schema-v3 DCM main pass fell from about 683 s to 53.29 s
(275 main launches plus 132 sparse launches became 26 plus 1). The v5 resumed
run added 6,925 dedicated object-boundary executions while retaining the
13,163-trial main corpus. It produced 45 batch logs, no singleton-retry logs,
and 95.30 s from the first new batch-log timestamp to `summary.json`. That span
is not represented as full process wall time; it is direct evidence that the
45-minute retry-amplification failure is gone.

Every batch remains completion-checked. Parallel execution cannot convert a
missing trial record into a clean summary.

