# SecOC runtime key lifecycle: corrected firmware analysis

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS SECOC-003, SECOC-005, SECOC-009
>
> **Canonical artifacts:** `data/dataflash_nvm_records.csv`
>
> **Verification:** `tests/verify_secoc_nvm.py`, `tests/verify_icus_key_update.py`
>
> **Related:** [application-chain](application-chain.md), [dataflash](../../storage/dataflash.md)

This note re-investigates the report's headline claim that the Sienna CN EPS
`8965B4512000` derives its SecOC key inside ICU-S and exposes the plaintext key at
`0xFEBEF468`, `0xFEBFEB08`, and `0x72F58` during a dealer-triggered rekey.

The claimed path was traced completely. It is **not a CSM/ICU command chain**.
It is an AUTOSAR NvM-backed redundancy and checkpoint subsystem used by
SecOC-associated objects. The initial analysis decoded only objects 0–3 and
incorrectly generalized that every object was non-key state. The full DataFlash
map in `../../storage/dataflash.md` shows that object 15 is a 32-byte triplicate object
whose second half is the field-verified SecOC-key location on related variants.
The distinct application verification path, ICU-S slot-4 selection, compiled-out
known-answer vector, command-5 generation family, command-8 authenticated key
update, and provisioned-unit experiment are in
`../../security/secoc/application-chain.md`.

`../tests/verify_secoc_nvm.py` verifies the original NvM correction. The broader 16-object
map and key-location correction are checked by `../tests/verify_dataflash_layout.py`.

## Executive conclusion

The prior labels were wrong:

| Address | Report interpretation | Corrected interpretation |
|---:|---|---|
| `0x65C60` | SecOC/crypto cyclic task | scheduler for SecOC-associated NvM state |
| `0x65C84` | request-side SecOC twin | request dispatcher; namespace `0x100` queues an NvM restore |
| `0x65CD8` | PDU/key ingress | update dispatcher for configured state objects |
| `0x66DB2` | queue key-set request | queue a triplicate NvM restore |
| `0x66E48` | copy plaintext key to FEBEF | copy changed structured state to its RAM mirror and queue persistence |
| `0x67590` | key-set from workbuf | submit three `NvM_ReadBlock` operations |
| `0x67608` | triple MAC/key verification | create raw/XOR55/XORAA copies and submit three `NvM_WriteBlock` operations |
| `0x67C34` | key update commit | reconcile asynchronous triplicate NvM reads |
| `0x674A8` | submit MAC generation | build/checkpoint an NvM block and submit `NvM_WriteBlock` |
| `0x71D9E` | CSM/ICU job queue | generic NvM asynchronous service queue |
| `0x72F58` | CSM key-set | `NvM_ReadBlock`-style submit, service ID `0x06` |
| `0x72F84` | CSM MAC generation | `NvM_WriteBlock`-style submit, service ID `0x07` |
| `0x758A0` | ICU key derivation | synchronous/status-mapped NvM/DataFlash read |
| `0x785D2` | ICU opcode validator | NvM service-ID validator/state setter |

The report's proposed FEBEF object-0 monitor would capture ordinary persistent
state, not the SecOC AES key. `0x72F58` is still generic `NvM_ReadBlock`, not a
key-set operation; however, a block-aware monitor can observe object 15 reads on
a provisioned variant. In this exact dump object 15 has no valid persistent copy.

A **separate real key-update path** has now been recovered elsewhere in the
application. Enabled RoutineControl RID `0x1010` transports a 64-byte authenticated request
to ICU-S command 8 and returns a 48-byte proof/result. A second, dormant
command-8 submitter — the RID-`0x100E` bank-0 crypto test fed by CAN
`0x13..0x1A` — is recovered in
[application-chain.md §5.10](application-chain.md#510-bank-0-crypto-test-rid-0x100e--can-0x130x1a--command-8-secoc-047048). The lower driver splits
the request as `16+32+16` and the response as `32+16`, exactly matching the
AUTOSAR SHE M1/M2/M3 → M4/M5 memory-update protocol. This corrects the prior
claim that the image had no SHE-shaped parser or ICU key-update route. It does
not rehabilitate the old `0x65CD8 → 0x72F58` NvM misclassification.

## 1. Conclusive NvM service identification

Application `tp` is initialized to `0x23EE4`. The service table is therefore:

```text
tp + 0x38BC = 0x277A0
```

At `0x277B0` and `0x277B8`:

```text
service 0x06 -> magic 0xA1A62093
service 0x07 -> magic 0x22AA8A36
```

The complete accepted set seen at `0x785D2` is:

```text
06 07 08 0C 0D 16 17 18
```

These are the AUTOSAR NvM APIs:

```text
0x06 NvM_ReadBlock
0x07 NvM_WriteBlock
0x08 NvM_RestoreBlockDefaults
0x0C NvM_ReadAll
0x0D NvM_WriteAll
0x16 NvM_ReadPRAMBlock
0x17 NvM_WritePRAMBlock
0x18 NvM_SetRamBlockStatus
```

This mapping is independently confirmed by the AUTOSAR NVRAM Manager
specification. It is not an ICU crypto-opcode set.

The wrappers agree exactly:

```c
// 0x72F58
nvm_queue_service_request(0xA1A62093, block_id, destination, 0);

// 0x72F84
nvm_queue_service_request(0x22AA8A36, block_id, 0, source);
```

Thus `0x72F58` reads persistent data **into** the caller's buffer; it does not send
that buffer as a key to ICU-S.

## 2. The object descriptor table

The 16-entry table at `0x2B0AC` has this layout:

```c
struct RedundantObject {
    uint16_t length;
    uint16_t base_nvm_block;
    uint32_t ram_mirror;
};
```

The first four objects are:

| Object | Length | Base block | RAM mirror |
|---:|---:|---:|---:|
| 0 | 16 | 2 | `0xFEBEF468` |
| 1 | 16 | 3 | `0xFEBEF478` |
| 2 | 8 | 4 | `0xFEBEF400` |
| 3 | 16 | 5 | `0xFEBEF488` |

Each object uses three NvM blocks:

```text
base + 0: raw copy
base + 4: each byte XOR 0x55
base + 8: each byte XOR 0xAA
```

This is software redundancy/TMR encoding, not three cryptographic key slots.

## 3. Boot restore lifecycle

`secoc_nvm_state_init @ 0x67162` explicitly zeroes four groups of three 32-byte
work buffers beginning at `0xFEBF0B08` (`application GP 0xFEBEB800 + 0x5308`).
The earlier `0xFEBFEB08` rendering was an address-calculation error.

`secoc_nvm_restore_all @ 0x6728E` then submits `NvM_ReadBlock` for all configured
blocks. For a redundant object, `secoc_nvm_restore_triplicate @ 0x67590` submits:

```text
ReadBlock(base + 0, workbuf + 0x00)
ReadBlock(base + 4, workbuf + 0x20)
ReadBlock(base + 8, workbuf + 0x40)
```

`secoc_nvm_triplicate_read_complete @ 0x67C34` handles completion and retries. Once
all three reads finish, it:

1. reverses XOR55 and XORAA;
2. compares the three decoded values;
3. selects/repairs a valid consensus where possible;
4. copies the consensus into the configured FEBEF/FEBF RAM mirror;
5. updates validity/checksum state.

This explains why the buffers are initially zero: they are read destinations.
They are not zero keys being installed.

## 4. Runtime update lifecycle

`secoc_nvm_object_update @ 0x65CD8` dispatches three ID namespaces. The `0x100`
namespace reaches `secoc_nvm_redundant_object_update @ 0x66E48`.

`0x66E48` obtains length and destination from `0x2B0AC`, copies changed words from
the caller into the RAM mirror, and queues a persistence request. It never calls
a crypto primitive or ICU-S register interface.

The scheduler eventually invokes `secoc_nvm_persist_triplicate @ 0x67608`, which:

1. copies the RAM mirror into workbuf copy 0;
2. creates copy 1 by XORing every byte with `0x55`;
3. creates copy 2 by XORing every byte with `0xAA`;
4. submits three `NvM_WriteBlock` requests through `0x72F84`.

The sibling scheduler at `0x66374` and submitter at `0x674A8` similarly persist
ordinary checkpoint blocks. `0x674A8` builds a block containing a counter,
payload, padding, and complement before calling `NvM_WriteBlock`; it performs no
CMAC operation.

## 5. DataFlash proves the encoding

NvM jobs map the first four objects as follows:

| Object | Raw | XOR55 | XORAA |
|---:|---:|---:|---:|
| 0 | job 2 / page 479 | job 6 / page 475 | job 10 / page 471 |
| 1 | job 3 / page 478 | job 7 / page 474 | job 11 / page 470 |
| 2 | job 4 / page 477 | job 8 / page 473 | job 12 / page 469 |
| 3 | job 5 / page 476 | job 9 / page 472 | job 13 / page 468 |

Decoding the three copies yields exact matches:

```text
object 0: a55a5aa5000800080008000800000000
object 1: a55a5aa5025a0000ffffffff00ffff00
object 2: aa5555aa5aa55aa5
object 3: a55a5aa55aa55aa5ffffffffff4affff
```

For example, object 0 begins:

```text
raw:   A5 5A 5A A5
xor55: F0 0F 0F F0
xorAA: 0F F0 F0 0F
```

These values are structured marker/counter/configuration state. They are plainly
not an unknown high-entropy AES-128 SecOC key.

The report called pages 468–479 “key-slot metadata” and interpreted their differing
patterns as derivation parameters. The differences are instead exactly explained
by the raw/XOR55/XORAA encoding implemented at `0x67608`.

The complete table has 16 objects, not four. Objects 12–15 are 32-byte records in
pages 440–443 (raw), 436–439 (XOR55), and 432–435 (XORAA).
Object 15 is base block 41 with RAM mirror `0xFEBF02E8`; its raw second field is
`0xFF206E14`, the CMAC-verified SecOC-key location on related EPS variants. All
three object-15 copies are invalid/uncommitted in this particular dump.

## 6. What `0x679D6 -> 0x78504 -> 0x758A0` really does

`nvm_validate_triplicate_records @ 0x679D6` resolves each configured NvM block to
a 64-byte DataFlash page and checks whether the record can be read successfully.
`0x758A0` reads into a local stack buffer and converts flash/NvM status codes.

The buffer is discarded because this particular call is a validity probe. No
buffer, metadata, or key is passed to a cryptographic engine. Therefore this call
chain is not evidence of key derivation, a fused master key, or ICU-S binding.

## 7. Where the SecOC key is represented

The full object table provides a concrete model that the earlier four-object pass
missed:

```text
object 15: length 32, base NvM block 41, RAM mirror 0xFEBF02E8
raw copy:   page 440, second field 0xFF206E14
XOR55 copy: page 436, second field 0xFF206D14
XORAA copy: page 432, second field 0xFF206C14
RAM field:  0xFEBF02F8
```

Vance's partner `8965B4514000` dump and Calvin's later in-car Sienna experiment
independently CMAC-verified the operational SecOC key at `0xFF206E14`. Thus this
is a real key-bearing NvM object on related variants, and a valid restore makes its
second field CPU-visible at `0xFEBF02F8`.

All three copies are invalid/uncommitted in the committed `8965B4512000` dump and
the raw field has zero CMAC matches. Static evidence does not establish whether
that reflects product policy, provisioning state, a masked/incomplete snapshot,
or another operational source. The exact key source for this captured image is
therefore unknown.

Pages 480–511 remain strongly consistent with an ICU-S-reserved 2 KiB tail. In
this capture the entire tail exposes only `00/FF` readback. That supports a
protected-storage boundary; it does not expose plaintext slot bytes or prove the
physical encoding beneath the read filter.

The complete application `ICUSCMD` writer census also closes the normal
software-export lead. Nine direct writers cover abort/reset, initialization,
diagnostic self-test, command 1/3 AES, command 5 MAC generation, command 7 CMAC
verification, command 8 authenticated update, and command 11. The dynamic
wrappers constrain their selectors/operation IDs, and no stock application
writer invokes command 13 or a recovered persistent-slot export command.

That negative result is scoped to the firmware's existing call graph. The
restricted Renesas ICU-S/ICUSE command manual is unavailable, so it does not
establish command 13's exact semantics or rule out a custom harness invoking an
undocumented selector, slot-to-`RAM_KEY` copy/alias, or export behavior. Public
AUTOSAR SHE descriptions of volatile `RAM_KEY` are architectural evidence, not
proof that direct command 13 on this implementation cannot involve slot 4. The
proposed `slot 4 -> RAM_KEY -> command 13` sequence remains an explicit bench
question.

This leaves peer-ECU extraction, direct command characterization, and physical
leakage as the leading existing-key routes. In particular, the CAN-FD
command-7 path authenticates
`DataID_be16 || payload[28] || freshness[6]`, placing 14 chosen payload bytes in
CMAC's first AES block. The ranked methods and isolated-bench plan are canonical
in [the key-recovery assessment](key-recovery-assessment.md).

## 8. Injection and refresh: command 8 via RoutineControl RID `0x1010`

The recovered provisioning candidate is independent of the object-15 NvM path:

```text
RoutineControl RID 0x1010
  -> 0x96354: fixed 64-byte request / 49-byte status+result contract
  -> 0x8AA1E -> 0x68E16: asynchronous diagnostic state
  -> 0x6823C -> 0x88936: command-8 driver dispatch
  -> record 0x28024
  -> 0x870A8 -> 0x86E62: require 64 input / >=48 output
  -> 0x8704C -> 0x8997A
  -> ICUSCMD = 8
```

Preparation copies the request into ICU staging as:

```text
M1: 16 bytes
M2: 32 bytes
M3: 16 bytes
```

Successful completion copies:

```text
M4: 32 bytes
M5: 16 bytes
```

Those widths and directions exactly match the AUTOSAR SHE authenticated memory
update used by `CMD_LOAD_KEY`. M1 identifies the target slot and AuthID; M2
protects the new key, counter, and flags; M3 authenticates M1/M2; M4/M5 provide
proof of completion. The target key selector is therefore inside the
cryptographic package rather than a separate CPU argument. Command 8 is capable
of targeting slot 4 if M1 names slot 4 and ICU-S accepts the AuthID, counter,
flags, and lifecycle policy.

The RoutineControl RID entry at `0x26B34` is enabled. Its per-RID policy permits only
extended session `0x03` and has zero Dcm SecurityAccess levels. This is not an
unauthenticated raw-key write: a caller still needs a valid M1–M3 package
authorized by a key already known to ICU-S, and replay protection is carried by
the protected update counter. The application never sees the plaintext new key
or the authorization key.

The diagnostic result bank at `0xFEBE523A` can return all 48 M4/M5 bytes after
completion. The 64-byte request bank is `0xFEBE51BA`. The application exposes
these through two control types of service `0x31`: control type `0x01` starts the
operation and control type `0x03` reads its status/result. The production dealer
backend, package-generation algorithm inputs, AuthID, and current slot-4 counter
remain unobserved. Consequently RID `0x1010` is the strongest static candidate
for dealer rekey, not proof that a particular dealer tool invokes it.

### 8.1 Exact diagnostic transport contract

This application uses standard RoutineControl framing for this operation. The
RID-`0x1010` configuration enables control types `0x01` (startRoutine) and
`0x03` (requestRoutineResults):

```text
start request:
  31 01 10 10 || M1[16] || M2[32] || M3[16]       68 UDS bytes

start positive response:
  71 01 10 10 || status[1] || result[48]            53 UDS bytes

result request:
  31 03 10 10                                         4 UDS bytes

result positive response:
  71 03 10 10 || status[1] || result[48]            53 UDS bytes

negative response:
  7F 31 NRC
```

The static field descriptors prove one 512-bit control-type-1 input field and one
392-bit output field. Control type 3 has the same 392-bit output shape and no input
field. The status values recovered from the operation state machine are:

| Status | Meaning | Following 48 bytes |
|---:|---|---|
| `0x01` | accepted/pending | zero-filled |
| `0x02` | complete | M4[32] + M5[16] |
| `0xFF` | failed | zero-filled |

`0x68E16` returns status `0x01` when it accepts and arms a new operation.
`0x68EA8` returns the current status, copies proof bytes only for status `0x02`,
and clears the diagnostic request/result banks after either terminal status
`0x02` or `0xFF` is read. Starting another package while status remains
`0x01` returns internal result `8`, which maps to NRC `0x24`
(`requestSequenceError`); an external inhibit maps to NRC `0x22`
(`conditionsNotCorrect`).

This is application-level polling, not one long RoutineControl request that eventually
returns M4/M5. A trace must retain both control types to distinguish acceptance
from completion. **Composition caveat (CORR-062):** status `0x02` proves only
that *some* command-8 job completed while `FEBE5085` was active — the
RID-`0x100E` bank-0 test can submit its own envelope first and have its
completion attributed to the diagnostic, whose zeroed result bank is then
returned as "proof". See
[application-chain.md §5.10](application-chain.md#510-bank-0-crypto-test-rid-0x100e--can-0x130x1a--command-8-secoc-047048).

The passive decoder implements this exact contract and reassembles normal
ISO-TP on the Sienna diagnostic IDs:

```bash
uv run --locked python tools/decode_icus_key_update_trace.py capture.log --json
```

It defaults to request `0x7A1` and response `0x7A9`, accepts compact and
bracketed `candump` lines, and hashes M1–M5 by default. `--show-package` exposes
the vehicle-specific package bytes and should be used only with controlled
artifacts.

### 8.2 What this firmware does with the package

MainPE is a transport, scheduling, and status layer for this operation. It does
not construct an update package and does not interpret the package fields:

1. `0x96354` fixes the generated diagnostic operation to 64 input bytes and a
   49-byte internal status/result contract.
2. `0x68E16` copies the 64 input bytes into `0xFEBE51BA`, clears the 48-byte
   result bank at `0xFEBE523A`, marks the operation active, and enters state
   `0x22`.
3. The cyclic worker `0x682F8` waits for the surrounding system/driver readiness
   predicates. `0x6823C` then submits driver record 0 with 64 input bytes and 48
   bytes of output capacity, advancing to state `0x33`.
4. `0x86E62` performs only pointer, exact-length, and output-capacity checks,
   then copies bytes `[0:16]`, `[16:48]`, and `[48:64]` into three ICU staging
   regions. There is no CPU-side target-slot argument, key unwrap, AuthID
   comparison, counter comparison, or package-derived branch in this path.
5. `0x8997A` configures four 128-bit input transfers and three 128-bit output
   transfers, then writes literal `8` to `ICUSCMD`. ICU-S is therefore the
   boundary that must interpret and authenticate the package.
6. On hardware success, `0x86EE8` copies 32+16 result bytes to
   `0xFEBE523A`, sets the returned length to 48, and clears both the 64-byte ICU
   input staging and 48-byte ICU result staging.

The success state progression is:

```text
0x22 queued
  -> 0x33 submitted
  -> 0x44 command-8 completion success
  -> 0x46 compiled-out post-update KAT skipped
  -> 0x55 complete
  -> diagnostic status 0x02
```

Command failure reaches internal state `0x66`, which maps to diagnostic status
`0xFF`. The control-type-3 result wrapper returns one status byte plus the 48-byte
proof only when status is `0x02`; terminal reads then clear the diagnostic
request/result banks. No independent operation deadline has yet been recovered
from this state machine; live timing and any surrounding Dcm/session timeout
remain to be measured.

Consequently, this dump answers how the EPS **consumes** an authenticated
update. An external provisioning system must still supply the already formed
M1–M3 package. If M1 names slot 4 and ICU-S accepts its AuthID, counter, flags,
and lifecycle policy, this route can request a slot-4 update; nothing in MainPE
rewrites the target to slot 4. No edge from this command-8 path to object-15 NvM
persistence has been recovered.

The generic NvM restore/persistence path remains separately relevant because
object 15 is key-bearing on field-verified related variants. The H-variant pass
now independently confirms that `8965H1202000` retains the same 16-object restore
namespace and exact `FF206C00..FF206EFF` protected geometry, but the supplied H
DataFlash has **zero valid object-15 copies**. That strengthens the separation
between generic persistence and the live ICU-S slot-4 verifier on this unit without
proving that other H units cannot carry a valid object 15.

Consequently:

- monitoring `0xFEBEF468/478/488` still captures objects 0/1/3, not the key;
- object 15's known related-variant locations are DataFlash `0xFF206E14` and RAM
  `0xFEBF02F8`;
- generic work groups rooted at `0xFEBF0B08` can temporarily hold currently
  processed triplicate objects; object 15 specifically uses
  `0xFEBF0C28/0xFEBF0C48/0xFEBF0C68`, but these are not fixed key-set buffers;
- hooking `0x72F58` identifies generic reads; a useful monitor must filter block
  41/45/49 and observe completion, not treat the call as ICU key-set;
- none of those locations contains a valid key in this exact committed snapshot;
- the original dealer/FEBEF capture design remains unsupported.

## 9. Answers to the original questions

### How is the SecOC key injected?

The image contains a concrete SHE-compatible provisioning candidate: enabled
RoutineControl RID `0x1010` submits M1/M2/M3-shaped input to ICU-S command 8 and returns
M4/M5-shaped proof. A valid package can identify slot 4 without exposing the new
key to MainPE. Static analysis does not prove that Toyota's dealer workflow
actually invokes this DID, nor does it reveal the required authorization key,
slot counter, or accepted policy flags.

On related variants, a usable SecOC key is also persisted in object 15's
raw/XOR55/XORAA NvM copies. Whether those variants use the same command-8 path
and then mirror/export the key to object 15 is unknown. This exact image's
runtime CMAC path selects ICU-S slot 4 without reading object 15. The embedded
`FF*16` vector is referenced only by two KAT bodies compiled out by
`CodeFlash[0x30EF3]=0x00`, so it does not constrain the live slot.

The pinned Renesas Flash Programmer host library exposes RV40F commands for
ICU-S option configuration, validation, and mode selection, but no named
key-load API. Its packaged `Firmwares/` images are SEGGER probe firmware, and
its only explicit secure-provisioning payload is for RA6B1; no RH850
target-side provisioning image is shipped. The documented high-level “Enable
ICU-S” path reaches a payload-free validation command, not a key-bearing
request. Its legacy `SetICUM` path serializes a structured extended-option
record rather than `slot || AES key`. Those mask-ROM programming operations are
separate from the application RoutineControl RID-`0x1010` M1–M5 route recovered here. RFP
therefore constrains chip lifecycle setup but does not reveal the Toyota/Denso
backend inputs used to authorize a slot-4 update. See
[the RFP/RV40F report](../../tooling/renesas-rfp-rv40f.md).

### How is it derived?

There is no evidence of per-boot derivation from pages 468–479 or of a fused-key KDF
in this path. Pages 468–479 are redundant application objects. Related variants
store the already usable AES key in object 15; this exact dump has no valid copy.

### How is it refreshed?

For protected ICU-S slots, RoutineControl RID `0x1010` plus command 8 is the recovered
refresh candidate. Control type `0x01` submits the M1–M3 package; control type `0x03`
polls the one-byte state and returns M4/M5 on status `0x02`. Whether production
tooling uses it for slot 4 requires a dynamic diagnostic trace.

Separately, `0x65CD8/0x66E48/0x67608` can update and persist any configured
redundancy object, including object 15 when addressed through namespace `0x100`.
No static bridge from command-8 success to object-15 persistence was found.

### Is it ever in dumpable CPU RAM?

On a provisioned variant using object 15, yes: triplicate reconciliation copies the
32-byte consensus to `0xFEBF02E8`, placing its key field at `0xFEBF02F8`. The
previously proposed FEBEF addresses are wrong. This exact dump does not establish
that the RAM field held a valid key at capture time.

## 10. Evidence grades

| Finding | Grade |
|---|---|
| `0x72F58/0x72F84` are NvM ReadBlock/WriteBlock | **Definitive** |
| pages 468–479 are redundant objects 0–3, not derivation metadata | **Definitive** |
| object 15 is len32/base41/RAM `0xFEBF02E8` | **Definitive** |
| `0xFF206E14` maps to object 15's RAM field `0xFEBF02F8` | **Definitive** |
| this dump's three object-15 copies are invalid and contain no verified key | **Definitive** |
| related variants store a CMAC-verified SecOC key at `0xFF206E14` | **Strong field evidence** |
| report's FEBEF/key-set/derivation path is invalid | **Definitive** |
| final 2 KiB is an ICU-S protected storage tail | **Strong inference** |
| application CMAC path selects ICU-S slot 4, not object-15 RAM | **Definitive** |
| all nine application `ICUSCMD` writers are accounted for | **Definitive** |
| stock application invokes command 13 or a plaintext persistent-slot export | **Disproved for this image** |
| direct command 13 semantics and selector-4 behavior | **Unknown; not constrained by the writer census** |
| an undocumented slot-4-to-`RAM_KEY` copy/alias exists | **Unknown; bench/restricted manual required** |
| command-1/3 software accepts selectors `0..14`; slot-4 hardware permission | **Definitive / unknown** |
| FD command-7 input places 14 chosen payload bytes in CMAC block 1 | **Definitive** |
| RoutineControl RID `0x1010` reaches literal ICU-S command 8 | **Definitive structural behavior** |
| command-8 request/result widths are 16+32+16 / 32+16 | **Definitive** |
| RID `0x1010` wire contract is control-type-1 start plus control-type-3 result read | **Definitive structural behavior** |
| result status `01/02/FF` means pending/complete/failed; proof is exposed only with `02` | **Definitive** |
| command 8 is a SHE-compatible authenticated memory/key update | **Recovered** |
| RID `0x1010` per-RID policy is extended session, no Dcm SA level | **Definitive** |
| command 8 is statically fixed to slot 4 | **Disproved; target is package-carried** |
| Toyota dealer tooling invokes RoutineControl RID `0x1010` for slot 4 | **Unknown; dynamic trace required** |
| both slot-4 KAT bodies are compiled out; the `FF*16` vector is latent | **Definitive** |
| CPU-visible objects 12–15 are invalid/inactive in this snapshot | **Definitive for the captured NvM bank** |
| protected ICU-S slot 4 is personalized or erased | **Unknown** |
| exact production backend/AuthID/counter/package for slot 4 | **Unknown** |

## References

- AUTOSAR, *Specification of NVRAM Manager*:
  <https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf>
- AUTOSAR, *Specification of Secure Hardware Extensions*, §4.9:
  <https://www.autosar.org/fileadmin/standards/R21-11/FO/AUTOSAR_TR_SecureHardwareExtensions.pdf>
- Renesas, *RH850/P1M-E Datasheet* (R7F701381 has ICUS):
  <https://www.renesas.com/en/document/dst/rh850p1m-e-datasheet>
- Renesas, *Achieving a Root of Trust ... Part 2* (ICU-S/SHE architecture):
  <https://www.renesas.com/en/blogs/achieving-root-trust-secure-boot-automotive-rh850-and-r-car-devices-part-2>
- Detailed existing-key recovery assessment and physical experiment plan:
  [key-recovery-assessment.md](key-recovery-assessment.md)
- FlashRunner RH850 programming note (ICU-S reserves final 1/2 KiB DataFlash):
  <https://smh-tech.com/remos_docs_remoto/Interfacing%20FlashRunner%20with%20RH850%20family%20MCUs.pdf>
