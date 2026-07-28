# ICU-S slot-4 key-recovery assessment

> **Scope:** Toyota Sienna EPS `8965B4512000`, RH850/P1M-E `R7F701381`
>
> **Document type:** recovery-method assessment and bench plan
>
> **Status:** active; no key recovered yet
>
> **Evidence source:** firmware-static plus explicitly identified external sources
>
> **Evidence profile:** mixed — verified firmware structure, bounded hardware
> interpretation, and untested physical-attack hypotheses are kept separate
>
> **Verification:** `tests/verify_icus_key_recovery_surface.py`,
> `tests/verify_icus_software_paths.py`, `tests/verify_secoc_application.py`,
> `tests/verify_secoc_security_properties.py`
>
> **Related:** [software-path assessment](software-path-assessment.md),
> [application chain](application-chain.md),
> [key storage/lifecycle](key-storage-and-lifecycle.md),
> [DataFlash](../../storage/dataflash.md),
> [RFP/RV40F](../../tooling/renesas-rfp-rv40f.md)

## Executive conclusion

No **stock application path** invokes a recovered plaintext key-export
operation. The application reaches ICU-S through nine accounted `ICUSCMD`
writers covering AES command 1/3, MAC generation command 5, CMAC verification
command 7, authenticated key update command 8, and initialization/test
operations. The final 2 KiB of captured DataFlash exposes only `00/FF`
readback, and neither normal MainPE memory access nor a serial/debug-protection
bypass is evidence that the underlying ICU-S key array becomes readable.

That firmware-static result does **not** determine the behavior of a command
issued directly by a custom harness. In particular, the restricted Renesas
ICU-S/ICUSE command manual is unavailable, so command 13's exact semantics,
selector handling, output format, lifecycle restrictions, and any undocumented
slot-to-`RAM_KEY` operation remain unknown. The proposed sequence “copy slot 4
to `RAM_KEY`, then invoke command 13/export” is therefore an untested hardware
hypothesis—not a path established by the firmware, but also not disproved by
the writer census or public SHE semantics.

The **best overall recovery route** is therefore to acquire and dump a weaker
ECU from the same vehicle that produces one of the messages this EPS verifies.
A producer must possess the same AES key or equivalent signing capability. The
forward camera is the leading candidate for the steering-related traffic, but
message ownership must be established by an in-vehicle capture or isolation
test rather than assumed from network role.

The **best first direct experiment on this EPS's existing slot 4** is now a
software-only ICU command harness inside the already-authenticated 4 KiB
bootloader callback. Repository-known gate material constructs accepted payloads,
the pinned CAN-dump payloads already provide output transport, and each leaves
more than `0xE00` bytes before its callback trailer. This can characterize known
`RAM_KEY`, command 13, selector 4, status, and output without a persistent patch.
A negative bootloader-context result does not close application lifecycle
behavior; the fallback is a restorable application hook installed through the
same authorized flash path.

The **best characterized physical fallback** is power or EM side-channel
analysis of repeated command-7 verifications. It does not depend on command-5
generation permission. The stock CAN-FD receive profiles provide an especially
useful chosen-input surface:

```text
authenticated input = DataID_be16 || payload[28] || full_freshness[6]
first AES-CMAC block = DataID_be16 || payload[0:14]
```

Thus 14 of the first block's 16 bytes can be randomized by sending isolated-bench
CAN-FD frames on `0x090` or `0x0D7`. A conventional first-round AES leakage
attack can target key bytes 2 through 15. If the two Data-ID-aligned key bytes
remain unresolved, exhaustive completion is only `2^16`; one legitimate
28-bit SecOC tag has fewer than `1/4000` expected false completions, and two or
more captured frames remove practical ambiguity.

Before building a large trace set, use the bootloader payload to characterize
command 13 with a known caller-loaded volatile key and directly test its
selector-4 behavior and any non-destructive slot-to-`RAM_KEY` copy/alias
candidate. If lifecycle or initialization blocks that context, move the same
experiment into a restorable application hook. Also test slot-4 permissions for
command 5 and the generic command-1/3 AES wrapper after normal application
initialization. If command 5 is allowed, it offers a cleaner full-tag CMAC
oracle. If command 1 is allowed, it offers an ideal chosen-plaintext AES oracle
and is cryptographically sufficient to synthesize CMAC without learning the
key. None of these hardware outcomes should be assumed from the stock call
graph.

Fault injection against serial read-range checks or ICU-S policy is a later
fallback, not the first experiment. Public P1M-E work proves that RH850 serial
programming checks can be glitched, but it does not prove that ICU-S protected
key storage is exposed after the check. Command 8 can replace a key with a valid
authenticated M1-M3 package; it cannot disclose the current key and risks
irreversibly desynchronizing the EPS from its peers.

## 1. Static boundary: what can and cannot disclose slot 4

### 1.1 Complete application command-writer census

The exact `FFC5D000` store encoding occurs at nine CodeFlash sites:

| Writer site | Recovered operation | Key-recovery relevance |
|---:|---|---|
| `0x8919C` | abort/reset command `0x3F` | none |
| `0x89628` | runtime selector plus command 1 or 3 | chosen-input AES oracle if slot policy permits |
| `0x8973A` | runtime selector plus command 5 | full CMAC oracle if slot policy permits |
| `0x8990C` | runtime selector plus command 7 | live SecOC verification and SCA stimulus |
| `0x89A2C` | command 8 | authenticated M1-M3 key update, not export |
| `0x89A8A` | command 11 | initialization/test family; no key output recovered |
| `0x89BB0` | command `0x22` | ICU initialization/lifecycle family |
| `0x89BF8` | abort/reset command `0x3F` | none |
| `0x89DDC` | diagnostic word `0x7000` or `0x7100` | self-test/status family |

The only dynamic low command IDs are constrained by their wrappers:

- `0x8954C` accepts selector `0..14` and maps an operation flag only to command
  1 or command 3;
- `0x89630` accepts selector `0..14` and emits command 5;
- `0x897F4` accepts selector `0..14` and emits command 7;
- `0x8997A` emits literal command 8 and carries no CPU-side key output.

This census is a **verified firmware-static negative result**: there is no
stock application invocation of command 13 or another recovered plaintext
persistent-slot export operation. It says nothing about what ICU-S would do if
a custom application-context harness wrote an otherwise-unused command word.

### 1.2 Command-13 and `RAM_KEY` uncertainty

Public AUTOSAR SHE material describes a volatile `RAM_KEY`, a caller-supplied
plain-key load operation, and a protected RAM-key export operation. That is a
useful architectural reference, not proof of this Renesas implementation's
command numbering or behavior. The public P1M-E hardware manual intentionally
omits the ICU-S command specification, and the restricted ICUSE manual has not
been obtained.

Consequently, static analysis has not established:

- that ICU-S command 13 is exactly the SHE RAM-key export primitive;
- whether command 13 consumes the command word's high selector bits;
- whether selector 4 is rejected, ignored, interpreted as a source slot, or
  accepted in a lifecycle/test mode;
- whether any documented or undocumented operation can copy/alias persistent
  slot 4 into `RAM_KEY` without exposing it through MainPE;
- whether a successful command-13 result is plaintext, a protected envelope,
  metadata, or another implementation-specific form; or
- whether debug, manufacturing, validation, or faulted lifecycle state changes
  those semantics.

The proposed `slot 4 -> RAM_KEY -> command 13` chain is therefore a valid bench
experiment. It has two independent unknowns: obtaining an internal copy/alias,
and obtaining useful export output. Observing normal SHE behavior with a known,
caller-loaded `RAM_KEY` would characterize the interface but would not by itself
resolve the slot-4 source question.

### 1.3 The available operations are oracles, not key reads

Command 7 is sufficient for normal SecOC verification and provides a yes/no
result. Command 5, if permitted, returns a 16-byte MAC. Command 1/3, if
permitted, returns transformed data. Those services expose cryptographic
capability but not the 16 key bytes.

Their policy is a hardware question. Software acceptance of selector 4 proves
only that MainPE will form the command. ICU-S can still reject the operation
based on the slot's provisioned usage flags. In a SHE-like policy, a SecOC MAC
key may permit MAC verification while generation is disabled; an AES
encipher/decipher request may also be incompatible with the key's usage class.

### 1.4 DataFlash, debug, and serial programming

The captured final `0x800` bytes of DataFlash contain 944 zero bytes and 1,104
`FF` bytes and no other values. The application range validator rejects requests
overlapping `0xFF207800..0xFF207FFF`. Renesas/third-party documentation identifies
this end region as ICU-S-reserved, but the observed bytes are readback behavior,
not a plaintext key dump.

Bypassing serial-programming prohibition or an ID code grants a more capable
MainPE/flash access path. It does not by itself defeat an ICU-S hardware read
barrier. A debugger is still valuable for installing a deterministic trigger or
calling the recovered wrappers, but success must not be reported as key access
unless the candidate key validates stock SecOC frames.

### 1.5 Command 8 is rekey, not recovery

DID `0x1010` passes an opaque SHE-compatible `M1[16] || M2[32] || M3[16]`
package to command 8 and returns `M4[32] || M5[16]`. ICU-S authenticates and
unwraps the package. MainPE never receives the current key or plaintext new key.

A captured provisioning exchange is valuable only if it leads to a weaker
endpoint: a backend log containing plaintext, an authorization key in a tool, or
a peer ECU holding the installed key. M1-M5 alone do not make the new AES key
public. Random command-8 probing is specifically excluded from the initial bench
plan because a valid or faulted update may alter counters, flags, or the live
key irreversibly.

## 2. Ranked recovery methods

| Rank | Method | Expected value | Cost/risk | Current evidence |
|---:|---|---|---|---|
| 1 | Extract from a same-vehicle producer/peer ECU | Highest overall: may reduce the problem to ordinary flash/RAM analysis | Requires identifying and acquiring the exact peer; peer may also use an HSM | **Hypothesis**, compelled by shared signing capability but producer/storage unobserved |
| 2 | Characterize command 13 and test `slot 4 -> RAM_KEY -> export` | First direct experiment: cheap discriminator that could expose an undocumented copy/export capability | Start with a constructible one-shot bootloader CAN payload; use a restorable application hook only if lifecycle/context requires it | **Software foothold verified; hardware behavior unknown** |
| 3 | Power/EM SCA on EPS command 7 | Best characterized physical slot-4 recovery path; unlimited chosen-input verifications are structurally available | Lab equipment, trace alignment, possible masking/noise | **Recovered attack surface**, leakage unobserved |
| 4 | Test command 5 and command 1 under selector 4 | Can yield cleaner SCA stimulus or a usable in-ECU oracle | Requires application-context harness; slot policy may reject | **Verified software support**, hardware permission unknown |
| 5 | Capture factory/dealer provisioning ecosystem | A tool/backend or manufacturing station may expose plaintext or authorization material | Opportunistic and access-dependent; M1-M5 capture alone is insufficient | **Recovered command-8 route**, production use unknown |
| 6 | Fault serial protected-tail read or ICU-S access check | Could work if protection is a skip-able software range check | Destructive tuning; hardware blanking may still return `00/FF` | **Public P1M-E FI precedent**, no protected-key read precedent |
| 7 | DFA on command-1/5 output or targeted ICU-S policy fault | Potentially fewer traces than SCA if faulty ciphertext/MAC pairs are observable | Precise fault location/timing; depends on an output-producing command | **Hypothesis** |
| 8 | Invasive decap, laser/EMFI, microprobing | Last resort against hardware-enforced storage | Highest cost and device-loss risk | **Hypothesis** |
| — | Brute force, CAN replay, command-8 replacement | Does not recover the existing random AES-128 key | Unreliable, availability-only, or desynchronizing | **Rejected** |

## 3. Best overall route: recover from a peer key holder

### 3.1 Why a producer is equivalent for this goal

The EPS verifies all six configured SecOC profiles with one ICU-S configuration
that selects slot 4. Any ECU that produces a valid protected frame for one of
those profiles must possess the same AES key or an equivalent protected signing
service. The key's storage security can differ sharply between ECUs even when
the on-wire SecOC profile is shared.

The previous `8965B4514000` result demonstrates the practical importance of this
variation: a related EPS exposed the usable vehicle-specific key in CPU-visible
object 15, while this `8965B4512000` snapshot does not. A camera, gateway, or
other producer may use another MCU, another HSM generation, a CPU-visible NvM
object, or a provisioning cache.

### 3.2 Peer workflow

1. Capture the exact vehicle's protected traffic, including synchronization and
   several frames for `0x2E4`, `0x131`, `0x132`, `0x090`, and `0x0D7`.
2. Establish each message's physical producer by controlled bus isolation,
   connector isolation, gateway routing evidence, or transmitter-side capture.
   Treat the forward camera as a lead, not a fact.
3. Record exact peer part and software numbers before sourcing a donor. A
   different calibration or vehicle will normally have a different key.
4. Dump all CPU-visible CodeFlash, DataFlash/EEPROM, external flash, and retained
   RAM available from the peer. Search both direct 16-byte candidates and
   redundant/XOR-encoded object formats.
5. Validate every candidate against multiple captured stock frames with the
   existing CMAC/freshness implementation. Entropy or location alone is not
   evidence of a key.
6. If the peer also uses protected HSM storage, repeat the command-surface and
   physical-leakage triage there. Its package and power layout may still be
   easier than the EPS.

A CAN signing oracle cannot derive an arbitrary AES-128 key by itself. Its value
is deterministic candidate validation and, if latency permits, temporary
message generation.

## 4. Best direct route: chosen-input side-channel analysis

### 4.1 Why command 7 is sufficient

A side-channel attack needs known or chosen inputs and repeated execution under
the same key; it does not require the correct MAC output. Failed SecOC
verification reaches ICU-S command 7, returns false, and does not commit
freshness. No per-PDU authentication-failure lockout was recovered. This permits
repeating a fixed freshness candidate with many payloads on an isolated bench.
The candidate must first pass the freshness pre-check: begin from an observed
legitimate synchronization/ordinary-frame state, retain or advance the
transmitted freshness nibble as the receiver expects, and confirm dynamically
that each test frame actually submits command 7. Because a failed tag does not
commit the candidate, the same accepted candidate can then be reused.

For CAN-FD `0x090` and `0x0D7`:

```text
secured PDU:          payload[28] || trailer[4]
trailer:              transmitted_freshness[4 bits] || CMAC[28 bits]
full freshness:       46 bits reconstructed by receiver
authenticated input:  DataID_be16 || payload[28] || freshness[6]
```

AES-CMAC starts with a zero chaining value, so its first full block is processed
as ordinary `AES_K(first_block)`. The first block is:

```text
byte 0..1:   fixed Data ID (00 90 or 00 D7)
byte 2..15:  attacker-selected payload bytes 0..13
```

A first-round Hamming-weight or Hamming-distance CPA can therefore test
`SBox(input_byte XOR key_byte)` for key bytes 2..15. The exact leakage model,
byte ordering, and point of interest remain experimental because the ICU-S AES
implementation is undocumented and may include masking, hiding, duplication,
or other countermeasures.

### 4.2 Completing the fixed bytes

If first-order leakage recovers only the 14 payload-aligned bytes, enumerate all
65,536 values for key bytes 0 and 1. For each full candidate:

1. reconstruct a legitimate captured frame's full freshness;
2. calculate AES-CMAC over the exact authenticated input;
3. compare the transmitted 28 bits using the established bit packing;
4. retain matches and test them against additional legitimate frames.

The expected number of wrong candidates matching one 28-bit tag is:

```text
(2^16 - 1) / 2^28 ~= 0.00024414
```

One frame should therefore be unique with probability above 99.97%; multiple
frames are mandatory in practice to catch trace-analysis, byte-order, freshness,
or capture mistakes.

### 4.3 Acquisition ladder

Use the least invasive setup that gives measurable leakage:

1. **EM reconnaissance.** Scan above the MCU while alternating fixed and random
   payloads. Use fixed-vs-random Welch t-tests to identify a repeatable
   payload-dependent window before attempting key recovery.
2. **Stock-frame trigger.** Trigger from the CAN-FD frame edge/end and align
   traces around the later ICU activity. This requires no firmware change but
   includes interrupt/scheduler jitter.
3. **Analog re-alignment.** Correlate or dynamically time-warp traces on the
   repeatable ICU activity pattern rather than only the CAN edge.
4. **Application harness.** On a sacrificial EPS, call command 7 directly after
   normal initialization and toggle an unused GPIO immediately before the ICU
   request. Restore the original image after measurement.
5. **Core-rail measurement.** If EM SNR is insufficient, instrument the actual
   MCU core rail and measure across a shunt or suitable current probe. Preserve
   stability and all required supply pins.
6. **Higher-order/profiling methods.** Escalate only if TVLA shows leakage but
   first-order CPA does not recover stable bytes.

Start with thousands of fixed/random traces to characterize leakage and jitter,
then scale only after a point of interest is reproducible. Record payload,
Data ID, trailer, reset count, acquisition settings, and command status for every
trace. Never retain an unlabeled waveform corpus.

### 4.4 Power-rail caveat specific to `R7F701381`

Renesas' P1M-E datasheet classifies `R7F701381` as the 1 MiB **DPS** variant and
lists a 1.25 V core supply. For the 100-pin DPS table, pins 11, 66, and 98 are
`VDD`; the corresponding eVR package uses `VCL` on 11/66. This makes an external
core rail a promising power-analysis point if the board and marking match the
profile.

However, the public R7F701381 read-protection glitch report describes VCL/eVR
injection on pins 11 and 66. That conflicts with the Renesas variant table.
Before removing capacitors, cutting traces, installing a shunt, or crowbarring a
rail, verify the physical chip marking, package, continuity, regulator topology,
and voltage on the actual board. Do not transfer a published VCL setup by part
number alone.

## 5. Oracle-permission experiment before SCA

Run this only on an isolated, recoverable bench unit. Start with a one-shot
authenticated bootloader payload that polls ICU-S directly and reports raw output
over its existing CAN transport. Treat bootloader lifecycle as a discriminator,
not a definitive negative. If an operation rejects or initialization differs,
repeat from a restorable hook after the stock application has initialized ICU-S;
that context has different interrupts, global pointers, RAM, and driver state.

### 5.1 Required tests

| Test | Input | Success observation | Value if successful |
|---|---|---|---|
| command 7 / selector 4 | known legitimate input/tag, then one-bit-bad tag | good succeeds, bad fails | proves harness fidelity and measures verify latency |
| command 5 / selector 4 | chosen 16- or 36-byte message | 16-byte returned MAC matching known capture/model | cleaner CMAC/SCA oracle; possible signing proxy |
| command 1 / selector 4 | chosen 16-byte block | returned AES block, stable across repeats | ideal CPA/DFA oracle; AES primitive can synthesize CMAC |
| command 3 / selector 4 | chosen 16-byte block | returned AES inverse block | secondary oracle, unlikely to be needed |
| candidate command 13 with known caller-loaded `RAM_KEY` | known 16-byte volatile key, then candidate export command | status, exact output length/content, reset behavior | establishes actual command mapping and baseline RAM-key semantics |
| candidate command 13 with selector 4 | no preceding persistent-key write | status and output compared with known-RAM baseline | directly tests whether selector 4 is accepted, ignored, or rejected |
| candidate slot-4-to-`RAM_KEY` copy/alias sequence | only after identifying non-destructive source/destination semantics | changed command-13 output that validates as slot 4 | tests the proposed recovery chain |

For each operation, record:

- immediate software return;
- ICU completion/error status;
- exact latency distribution and jitter;
- whether output is written and its length;
- command-7 contention and application watchdog effects;
- behavior with debug attached versus detached;
- persistence across warm reset and cold power cycle.

A software return showing the command was submitted is not proof of slot
permission. A command-5 result is valid only if it matches a known CMAC; a
command-1 result is valid only if repeated calls and inverse/independent checks
are consistent. A command-13 experiment must distinguish command rejection,
empty/unchanged output, plaintext, and a deterministic or randomized protected
envelope. Any apparent 16-byte slot-4 result must validate stock SecOC frames;
output shape or entropy is not sufficient.

### 5.2 Command-13 experiment controls

1. Run first from a non-persistent bootloader payload, then repeat after normal
   application ICU-S initialization when bootloader behavior rejects or differs.
2. Establish the candidate command's behavior first with a known volatile key
   loaded through the corresponding non-persistent operation, if that operation
   can be identified safely.
3. Repeat across warm reset and cold power cycle to distinguish volatile state,
   stale staging data, and deterministic hardware output.
4. Test command-word high selector values separately, including the expected
   RAM selector and selector 4; do not infer selector semantics from commands
   1/3/5/7.
5. If an internal copy/alias command is identified, prove it with two different
   known source values before targeting slot 4.
6. Preserve raw status registers and all output words even when the high-level
   driver reports failure; an undocumented result may not match stock wrapper
   expectations.

The absence of a stock command-13 wrapper means a harness must supply correct
FIFO counts, callbacks/interrupt handling, status clearing, and timeout logic.
A failed first attempt may indicate malformed driver setup rather than rejected
hardware semantics.

### 5.3 Safety exclusions

- Do not issue command 8 with experimental packages on the only original unit.
- Do not write ICU-S option bytes, invoke unknown validation/lifecycle actions,
  or use a destructive debug-unlock command.
- Do not run random CAN-FD payload campaigns with the steering motor/power stage
  capable of producing torque.
- Keep the EPS off the vehicle network. Repeated invalid authentication is also
  an availability load and may set diagnostic state.
- Preserve full CodeFlash/DataFlash dumps, option values, firmware hashes, and a
  restorable programming path before patching.

## 6. Fault-injection fallbacks

### 6.1 Serial read of the protected tail

Public work on P1M-E `R7F701381` bypassed serial-programming prohibition by
voltage-glitching the synchronize check and then read ordinary CodeFlash and
DataFlash. The same report suggests faulting a protected read command as future
work; it does not demonstrate ICU-S key extraction.

A protected-tail experiment has a clear discriminator:

- if mask ROM performs a software range check and the underlying flash bus can
  return the physical words, a precisely timed skip may expose non-`00/FF` data;
- if the ICU-S region is hardware-isolated, access-filtered below mask ROM, or
  stores encoded material, bypassing the command check still returns blanked
  data or unusable state.

Because the target region is only the final 2 KiB, this is more bounded than a
whole-flash campaign, but it still requires repeatable faults and independent
validation. Any 16 high-entropy bytes are merely candidates until they verify
stock SecOC frames.

### 6.2 Faulting command policy

Potential targets include selector/usage checks, verify-only enforcement, and
output gating. A fault that merely changes command-7 false to true is an
authentication bypass, not key recovery. A fault that enables command 5 yields a
MAC oracle, not plaintext. The most useful fault outcome would enable command 1
or produce a correct/faulty full AES/MAC pair suitable for differential fault
analysis.

DFA is attractive only when an output-producing command is available and the
fault reaches the AES datapath late enough to fit a known model. Blind voltage
sweeps against command 7 are lower value because the verifier does not return
faulty ciphertext or a full computed tag.

### 6.3 Invasive methods

EMFI, backside laser faulting, decapsulation, and internal-bus probing are last
resorts. They may target the secure key-array read barrier more directly, but
cost, localization effort, package preparation, and device-loss probability are
all substantially higher than first testing peer storage and side-channel
leakage.

## 7. Provisioning capture: useful but not self-sufficient

Passively capture complete ISO-TP requests and responses around DID `0x1010`
whenever dealer or factory reprogramming is available. Preserve M1-M5 securely
and decode the operation with `tools/decode_icus_key_update_trace.py`.

The most valuable follow-up targets are:

- diagnostic-tool process memory before package encryption;
- local caches, logs, databases, or calibration bundles;
- authorization-key material or a backend API capable of forming M1-M3;
- the same package delivered to another ECU with weaker storage;
- pre- and post-provisioning peer dumps that reveal a changed CPU-visible object.

M1-M5 should not be advertised as a recovered SecOC key. SHE deliberately
protects the new key and authenticating key inside that envelope.

## 8. Decision tree

```text
Have exact-vehicle protected CAN capture and identified producer?
  no  -> capture synchronization + protected traffic; isolate producers
  yes -> dump/search easiest producer and validate candidates
           |
           +-- valid candidate -> confirm on >=2 frames; stop physical EPS work
           |
           +-- no candidate / peer also protected
                   |
                   +-- one-shot boot payload: known RAM_KEY + candidate command 13
                   |      |
                   |      +-- selector 4/copy produces useful output
                   |      |       -> validate against stock SecOC frames
                   |      +-- boot-context rejection / ordinary RAM-only behavior
                   |              -> repeat in application context; test command 5 and command 1
                   |                    +-- command 1 -> AES oracle/SCA
                   |                    +-- command 5 -> CMAC oracle/SCA
                   |                    +-- both reject -> command-7 FD path
                   |
                   +-- fixed/random leakage visible?
                          |
                          +-- yes -> CPA bytes 2..15, brute-force 2 bytes,
                          |          validate against multiple stock frames
                          +-- no  -> improve trigger/EM localization/core-rail
                                     measurement, then consider higher-order SCA
                                     and only later fault injection
```

## 9. Success criteria

A recovery is complete only when one 16-byte candidate:

1. reproduces transmitted 28-bit tags for multiple legitimate frames from at
   least two freshness values;
2. reproduces both `0x090`/`0x0D7` and a classic protected profile where captures
   permit, demonstrating the expected shared slot rather than a capture error;
3. remains valid after independently reimplementing the CMAC/freshness packing;
4. can generate a frame accepted by an isolated EPS while malformed controls are
   rejected;
5. is handled as vehicle-specific secret material and is not committed to this
   repository.

A successful command-5 or command-1 oracle is a useful fallback but is not
plaintext-key recovery. A command-13 result is recovery only if its semantics
are characterized and the resulting candidate independently validates stock
SecOC frames; mere output or a SHE-shaped envelope is insufficient. A
successful serial/debug bypass is instrumentation access but is not key
recovery. A changed slot-4 key is rekeying, not recovery of the original.

## 10. Evidence summary

| Claim | Grade | Source |
|---|---|---|
| slot 4 verifies all configured protected RX profiles | **verified** | firmware-static/test |
| all nine application `ICUSCMD` writers are accounted for | **verified** | firmware-static/test |
| no stock application writer invokes command 13 or persistent-slot plaintext export | **verified, scoped to this image** | firmware-static/test |
| accepted 4 KiB bootloader payloads provide a constructible callback and existing CAN transport with more than `0xE00` bytes spare | **verified** | firmware-static/fixtures/test |
| application SIDs `0x23/0x34/0x36/0x37` are null-callback responses and WDBI input sizing is exact (maximum 67-byte request) | **verified, scoped to this image** | firmware-static/test |
| command-5 preserves selector plumbing for a candidate command-ID substitution; DID `0x1010` preserves output transport but has fixed command-8 block shape and no selector | **verified structure; untested patch** | firmware-static/test |
| command 13's exact Renesas operation, selector semantics, and output format | **unknown** | restricted manual or bench required |
| an internal slot-4-to-`RAM_KEY` copy/alias exists | **unknown; not disproved** | restricted manual or bench required |
| command 13 can return useful slot-4 material after such a copy/alias | **unknown; not disproved** | bench required |
| command 1/3, 5, and 7 accept software selectors `0..14` | **verified** | firmware-static/test |
| slot 4 permits command 1 or command 5 | **unknown** | bench required |
| FD command-7 input provides 14 chosen bytes in CMAC block 1 | **verified** | firmware-static/test |
| 14-byte CPA plus `2^16` completion is mathematically sufficient | **verified construction; leakage unobserved** | firmware structure/model |
| command-7 activity has exploitable power/EM leakage | **hypothesis** | physical measurement required |
| a specific forward-camera part is the producer/key holder | **hypothesis** | vehicle isolation required |
| serial read fault can expose ICU-S key storage | **hypothesis** | public FI reaches ordinary flash only |
| command 8 or M1-M5 discloses the current key | **disproved** | recovered data flow/SHE contract |

## References

- Renesas, *RH850/P1M-E Datasheet*:
  <https://www.renesas.com/en/document/dst/rh850p1m-e-datasheet>
- Renesas, *RH850/P1M-E User's Manual: Hardware*:
  <https://www.renesas.com/en/document/mah/rh850p1m-e-users-manual-hardware>
- Renesas, *Achieving a Root of Trust with Secure Boot in Automotive RH850 and
  R-Car Devices – Part 2*:
  <https://www.renesas.com/en/blogs/achieving-root-trust-secure-boot-automotive-rh850-and-r-car-devices-part-2>
- AUTOSAR, *Specification of Secure Hardware Extensions*:
  <https://www.autosar.org/fileadmin/standards/R21-11/FO/AUTOSAR_TR_SecureHardwareExtensions.pdf>
- Willem Melching, *Bypassing the Renesas RH850/P1M-E read protection using
  fault injection*:
  <https://icanhack.nl/blog/rh850-glitch/>
- Quarkslab, *Bypassing debug password protection on the RH850 family using
  fault injection*:
  <https://blog.quarkslab.com/bypassing-debug-password-protection-on-the-rh850-family-using-fault-injection.html>
