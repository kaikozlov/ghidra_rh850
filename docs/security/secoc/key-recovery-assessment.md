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

That firmware-static result does **not** determine the behavior of an otherwise
unused Renesas command issued directly by a custom harness. However, the
standard SHE architecture does settle the normal extraction question: its
export primitive operates only on a caller-loaded volatile `RAM_KEY`, and SHE
provides no command that copies or exports a nonvolatile key slot. The former
“slot 4 -> RAM_KEY -> export” route is therefore **disproved under SHE**
(SECOC-025). Because the restricted Renesas ICU-S/ICUSE command manual is
unavailable, command 13 remains worth characterizing only as a possible
vendor-specific undocumented deviation in opcode/selector/lifecycle behavior.

The **best overall recovery route** is therefore to acquire and dump a weaker
ECU from the same vehicle that produces one of the messages this EPS verifies.
A producer must possess the same AES key or equivalent signing capability. The
forward camera is the leading candidate for the steering-related traffic, but
message ownership must be established by an in-vehicle capture or isolation
test rather than assumed from network role.

The **best first direct experiment on this EPS's existing slot 4** is the
application-context command-5 permission test specified in
`sender-implementation.md`: the stock serialized wrapper already provides the
selector-4 call shape, so no direct ICU command-word manipulation is required.
Record status, CMAC output, latency, and contention against command 7. The
recovered authenticated 4 KiB bootloader callback remains useful for lower-level
ICU characterization, but command 13 is no longer the default key-extraction
route; use it only to test for a Renesas-specific deviation from SHE.

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

Before building a large trace set, test slot-4 command-5 permission after normal
application initialization. Under SHE's `KEY_USAGE` model, a slot already used
for MAC verification should also permit MAC generation; a denial would be a
Renesas-specific policy deviation worth recording. The generic command-1/3 AES
wrapper is expected to be rejected for a MAC-usage slot under SHE. Separately,
a bootloader or application harness may characterize command 13 with a known
caller-loaded `RAM_KEY` to identify Renesas opcode behavior, but any useful
persistent-slot copy/export effect would be an undocumented vendor deviation,
not a standard SHE capability. None of these hardware outcomes should be
assumed from the stock call graph.

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
| `0x8973A` | runtime selector plus command 5 | lower variable-length CMAC primitive if slot policy permits; stock diagnostic caller is fixed to 16 bytes (SECOC-069) |
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

### 1.2 Command-13 and `RAM_KEY` boundary

Public AUTOSAR SHE material describes a volatile `RAM_KEY`, a caller-supplied
plain-key load operation, and a protected **RAM-key** export operation. It does
**not** define an export or copy operation for a nonvolatile `KEY_<n>` slot.
Therefore the previously proposed standard-SHE chain
`slot 4 -> RAM_KEY -> export` is disproved (SECOC-025): normal SHE cannot pull a
persistent slot into `RAM_KEY` for exfiltration.

The remaining uncertainty is vendor-specific. The public P1M-E hardware manual
omits the ICU-S command specification and the restricted ICUSE manual has not
been obtained, so static analysis has not established:

- that Renesas command 13 maps to the SHE RAM-key export primitive at all;
- its input/output block shape or command-word selector semantics;
- whether debug/manufacturing/faulted lifecycle implements any undocumented
  persistent-slot copy/alias behavior; or
- whether Renesas intentionally deviates from SHE in a way useful for slot 4.

A direct command-13 bench experiment can still characterize that vendor surface.
A known caller-loaded `RAM_KEY` is the correct baseline. Any later effect that
copies or exports persistent slot 4 must be reported explicitly as a **Renesas
extension/deviation**, not as expected SHE behavior.

### 1.3 The available operations are oracles, not key reads

Command 7 is sufficient for normal SecOC verification and provides a yes/no
result. Command 5, if permitted, returns a 16-byte MAC. Command 1/3, if
permitted, returns transformed data. Those services expose cryptographic
capability but not the 16 key bytes.

Their policy is a hardware question, but the AUTOSAR SHE specification sets a
strong prior. SHE key-slot usage is governed by a single binary flag,
`KEY_USAGE` (spec §4.4.1.5 "Key usage determination" and §4.4.2.4 `KEY_<n>`):
a key is either an **encryption/decryption** key or a **MAC generation/verification**
key — there is no separate "verify but not generate" permission. The five
provisionable security flags (spec §4.9, the key-update `FID` field) are
`WRITE_PROTECTION | BOOT_PROTECTION | DEBUGGER_PROTECTION | KEY_USAGE | WILDCARD`;
no verify-only bit exists, and a disallowed operation returns `ERC_KEY_INVALID`
(spec §4.8.4).

Slot 4 is a MAC-usage key (it is used for `CMD_VERIFY_MAC`/command 7, SECOC-002),
so under SHE semantics it may run **both** `CMD_GENERATE_MAC` (command 5) and
`CMD_VERIFY_MAC` (command 7). The earlier statement that "a SecOC MAC key may
permit MAC verification while generation is disabled" is **not supported by the
SHE specification** and is retracted (CORR-017). The polarity is the reverse of
the prior AES-oracle fallback: it is command 1/3 (raw encipher/decipher) that a
MAC-usage slot would reject, while command 5 (MAC generation) is the
spec-permitted primitive — which makes a command-5 signing oracle the
SHE-aligned path, not a likely-denied one.

Caveat, kept separate: this is the AUTOSAR SHE architectural reference. Renesas
public P1M material calls ICU-S SHE-compliant and explicitly lists CMAC
generation and verification, but the restricted `ICUSE` manual is unobtained
(SECOC-018). Real SHE-adjacent implementations can add policy: Vector documents
an additional `CMAC USAGE` flag that can make a MAC key verification-only. That
does not prove P1M-E has the same extension; it proves only that standard-SHE
flag semantics cannot substitute for the hardware experiment. The default prior
remains that command 5 should work on a MAC-use slot, while live slot-4 policy
is dynamic. See [command5-oracle-assessment.md](command5-oracle-assessment.md).

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

### 1.6 Community extraction toolchain and the RAM-mirror route

The repository pins two working SecOC-key-extraction-by-CAN implementations
(`external-references.lock.json`: I-CAN-hack/secoc, Bk2ol/tsk_extraction_by_can_log).
Their authenticated-RAM-exec bootstrap is exactly this image's SEC-BOOT-005/006/007
gate on the identical `SEED_KEY_SECRET` (`f05f36b7…`, CodeFlash `0xBFE8`,
`verify_findings.py`) — cross-validated, so the foothold is a solved, reusable
toolchain across the `8965B4x` family, not something to rebuild (SECOC-024).

Neither tool issues any ICU-S command. Both read a CPU-visible key copy via the
RAM-exec payload and transmit it over CAN:

- **I-CAN-hack/secoc (Technique A)** dumps a RAM mirror of the SHE key-slot table
  at `0xFEBE6E34` on `8965B4209/B4233/B4509100`: 704 bytes of 32-byte structs
  (key@0x0C, checksum@0x1D), KEY_1 (master) at `0xFEBE6E60`, KEY_4 (SecOC) at
  `0xFEBE6EC0`.
- **Bk2ol (Technique B)** dumps DataFlash `0xFF1FF000..0xFF209000` and brute-scans
  for a CMAC-verifying 16-byte window. It is `8965B4514000`-only (its README excludes
  `8965B4512000`); it depends on the object-15 CPU-visible leak that is absent here.

This confirms §1.3 operationally: no SHE command can exfiltrate slot 4 (SECOC-025 —
`CMD_EXPORT_RAM_KEY` is `RAM_KEY`-only/plain-only; no nonvolatile KEY has an export
or copy command). Community Technique A therefore succeeds only where firmware or
its runtime environment exposes a CPU-visible key copy (SECOC-026).

**Resolution for `8965B4512000` (SECOC-027).** The formerly open transfer check is
closed negative: this firmware has no firmware-maintained sibling-style RAM key-slot
mirror.
The ICU-S driver is a selector-based hardware-accelerator interface — the key reaches the
engine only as a SELECTOR written to `0xFFC5D004`, never as a value; AES blocks move through
`0xFFC5D008`/`0x090-BC`; driver state at `0xFEBF13**` is callback/command/status only. The
ICU-S register footprint is exactly `0xFFC5D000-0xFFC5D0FF` with no key-RAM window, and the
sibling mirror addresses `0xFEBE6E**` hold motor-signal data here (`FUN_000389C0`/`FUN_0003926E`),
not keys. Combined with the SHE read-prohibition (SECOC-025), the slot-4 key is ICU-S-only on
this calibration: extraction requires a bus-level/hardware read or SCA, or a weaker peer ECU.

### 1.7 Blurbdust fork lineage and persistent CodeFlash extension (SECOC-028)

The August-2026 Discord bundle is not a second independent implementation of the
authenticated-RAM-exec bootstrap. Git archaeology now pins its public lineage:
`blurbdust/secoc` is a fork of `I-CAN-hack/secoc` at parent
`4ce19cc31ff560b697bcd59cc3db55711f50b7b3`, and blurbdust added the persistent
patcher in `dbfd991bc817deca0c5c94e2fb5171d1142682c1` (2026-04-28), followed by
`846866d...` and `47d2824...`. A separate pinned I-CAN-hack `tundra` precursor
`b80d9104...` (2025-07-13) already carries the exact F3401200/2200 version
record, CPU0 `0203=01 00 00 00 00`, and `45 01` grammar later generalized by
blurbdust; those pieces are inherited lineage rather than CUW-provenance clues.
The retained `community/.../main.c` is
byte-identical to public `shellcode/main_flash_patch.c @ 47d2824`; the retained
`flash_patcher.py` differs from the public file only in the two progress-frame
`struct.unpack` endian format strings. Therefore the inherited SA/download/
routine-control bootstrap is **same-lineage corroboration**, not independent
evidence. Blurbdust's new evidence is the persistent FACI writer/patch host plus
the separately shared CUW extractor.

The CUW and writer chronology are tightly coupled. The optskug timeline preserves
blurbdust Discord message `1496150355224952995` (Discord snowflake timestamp
2026-04-21 14:07:21 UTC), where he says he has a script extracting the TechInfo
`.cuw` flash driver and computing `0x201`/`0x202`. Seven days later his first public patcher commit adds the persistent FACI writer.
Its F3401200/2200 host target is not an independent clue: Willem's 2025 Tundra
branch already contained the exact target record and much of the new-UDS
plumbing. The retained
`decrypt.T-0035-22.py` does exactly the described job: it parses `CPUImageN` and
`EraseRoutineN`, recovers DID `0x0201`/`0x0202`, decrypts and CMAC-checks the
regions, and writes `{NewCID}_erase.pt.bin`. No April attachment hash survives,
so the retained file is strongly consistent with the script he described but
not proved byte-identical to that April copy.

The first public `main_flash_patch.c` also already contains almost the full raw
manufacturer-shaped FACI sequence: FSTATR-ready at `0xFFA10080/0x8000`, FASTAT
command-lock at `0xFFA10010/0x10`, `FENTRYR=0xAA01`, the
`FHVE15/FHVE3/FAREASELC/FPROTR` entry sequence, `FPSADDR/FSADDR` erase
`0x20,0xD0`, and page program `0xE8,0x80,...,0xD0`. Its symbolic register names
are shifted, and two important semantics are wrong/incomplete: it polls reserved
FSTATR bit 21 instead of Toyota's bit 11/SUSRDY (`0x800`) per halfword, and it
omits the manufacturer `0x7040` FSTATR error mask / Status Clear `0x50` recovery.
This pattern is consistent with raw behavior reconstructed from disassembly
without a correct symbolic register map. Combined with the April-21 extractor statement, a CUW-informed FACI origin is
**plausible and worth pursuing**, but the inherited F340 target identity does not
strengthen authorship provenance and line-level derivation remains unproved until the actual
`T-0035-22.cuw` or plaintext manufacturer `*_erase.pt.bin` is acquired and
diffed. The full provenance/semantic matrix is in `community/README.md`.
The retained extractor also does not implement the V18 outer
`\0CALIBRATION\0` magic/CRC/size/member validation recovered later in
`tools/techstream/parse_cuw_container.py`; it opportunistically scans its input
for INI/S-record content. Until a real T-0035 specimen is available, whether it
expects the raw package or an exposed inner/package-specific layer remains
specimen-bound. Preserve and validate the raw CUW before applying it.

The import still splits cleanly into two functional layers: infrastructure that
transfers strongly, and an exploit signature that does not transfer to this
calibration.

#### Infrastructure (bootstrap, FCU RMW, and CRC resigning transfer strongly)

- **`flash_patcher.py`** — host tool. Structurally identical to the
  inherited I-CAN-hack/Bk2ol bootstrap: same `SEED_KEY_SECRET`, same `0x203→0x201→0x202`
  DID order, same `0xFEBF0000` download window, same `0x10F0`/`0xFF00` routine
  triggers, all-zero data_record protocol. The structural cross-validation is
  pinned in `verify_community_tooling.py`. Its version
  table covers `8965B4209000`, `8965B4233100`, `8965B4509100`, and new parts
  `8965F3401200` (dual-CPU), `8965F4207000`, `8965F4201000`.
- **Flash RMW + CRC resigning** — `main.c` uses FCU registers (`FACI` at
  `0xFFA1xxxx`) for 32 KiB read-modify-write of CodeFlash blocks, then computes
  CRC from the live flash prefix and writes `crc_pre_adj ^ 0xFFFFFFFF` at
  `0xFFDEC`. The geometry exactly matches the Sienna boot-validity region
  (`0x18000..0xFFDF0`, marker `0xFFE00`). The CRC algorithm is also verified:
  stock region 0 uses the identical CRC-32/Ethernet terminal-fixup construction
  (`0xEC0CD6CF → 0x13F32930 → final 0xFFFFFFFF`). The published region-1
  mismatch is instead explained by a unique single-bit artifact correction at
  `0xBB1C4`, `0xA2→0x82`; after that reconstruction, its existing
  `0x0962887F` fixup validates exactly. The same bit repairs the local RH850
  store displacement from `0x22` to `0x02`, making six destination stores an
  exact permutation of offsets `0..5` (SECOC-044/CORR-042).
- **`decrypt.T-0035-22.py`** — CUW decryption. Documents the per-byte
  SeedKey/Nonce obfuscation (`out[i] = (raw[i] − i) mod 256` → ASCII hex →
  16 bytes) and the `AES-ECB(BL_KEY, DID_201)` key derivation matching
  SEC-BOOT-003.

#### Exploit signature (does NOT transfer — cross-calibration collision)

`main.c` performs no semantic validation: it scans for the 8-byte egg
(`88 00 01 52 00 0A E5 0D`), requires exactly one occurrence, replaces its first
4 bytes with an immediate-success return (`01 52 7F 00` = `mov 1, r10; jmp [lp]`),
and treats the matched function as the patch target.

On `8965B4512000` the egg matches exactly once at VA `0x3485A` (verified).
Firmware analysis now closes that address as the prologue of
`FUN_0003485A` — the shared 5-byte comparator used by the proprietary SID
`0xBA` operation table:

- `FUN_00034882 @ 0x34882` uses it for the F7/length-6/`BAENA` bootstrap check.
- The currently named `application_proprietary_ab_f1_start @ 0x34B74` is
  semantically the SID-`0xBA` F1/`JTEKM` start callback; its historical symbol
  name predates corrected AB/BA service ownership.
- F3-FB operation callbacks reuse the same comparator for their embedded fixed
  request tokens; FA compares four bytes `VSPD` after its tester-selected value.

Replacing the comparator prologue with `mov 1,r10; jmp [lp]` therefore makes BA
token comparisons succeed. It does **not** bypass the independent F7 local
SecurityAccess check `0x34DAE -> 0x34D96 -> 0x8C8C6 -> 0x8FDCA`, where
`0x34D96` requires mask bit `0x02` = application SA level 2. Before the
persistent BA marker exists, the generic gateway still requires selector F7 and
length 6; after successful F7, forcing the comparator true weakens the remaining
registered operations' token checks while their local state gates remain.

The `0xAB` service is separately classified as an event-record service (list,
per-ID state, per-ID detail). Neither the BA comparator nor the closed AB graph
is the SecOC receive-verify worker at `0x8E4BA`; its prologue is
`a4 07 e1 f0 c6 00 e6 ee`, completely different from the egg.

Applying the supplied patch would make the event-token comparator always return
"match," distorting `0xAB` dispatch. It would not alter SecOC verification.

This is a **cross-calibration signature collision**: the egg was designed for
an `8965F3`/`8965F4` calibration where the authors report that forcing the
matched predicate to succeed bypasses a packet-verification check. The available
files establish an effective behavioral patch point on those calibrations, but
do not establish that the matched function is itself the cryptographic MAC
verifier — it could be a status translator, a combined authentication/freshness
predicate, a downstream acceptance gate, or a generic comparison helper used by
the SecOC path. The same compiler-generated instruction sequence begins the
unrelated `0xAB` event-record token comparator on the Sienna image. The flash
RMW and CRC-resigning mechanism does transfer; only the egg-selected semantic
target does not. The Sienna-specific Gate-2 patch point has now been
independently recovered from control flow as SECOC-043, and the published
CodeFlash region-1 CRC anomaly is independently explained by SECOC-044.

A patch point may be empirically effective without being semantically identified.
"Forcing this predicate to succeed causes protected frames to pass" is distinct
from "this function performs the cryptographic MAC verification." Raw byte
signatures must therefore be re-established from control flow and callers for
every calibration.

#### Evidence grading

| Claim | Source | Grade |
|---|---|---|
| Egg count (1) and address (`0x3485A`) | firmware-static | verified |
| Function semantics (5-byte comparator) | firmware-static (decompilation) | verified |
| SID `0xBA` comparator membership and callers | firmware-static (descriptor table/x-ref + `verify_application_proprietary_ba.py`) | verified |
| No static edge from BA comparator/surface to SecOC chain | firmware-static (`verify_application_proprietary_ba.py` + live direct-reference audit) | verified |
| CRC repair geometry matches Sienna | firmware-static (`verify_boot_trust.py` + `verify_community_tooling.py` §7) | verified |
| Community CRC-32/Ethernet terminal-fixup construction matches boot-validity behavior | stock region-0 fixture + reconstructed region 1 (`verify_codeflash_crc_reconstruction.py`; `verify_community_tooling.py` §7) | verified |
| Published region-1 mismatch has unique single-bit correction `0xBB1C4 A2→82`, also repairing local store semantics | CRC syndrome + instruction semantics (`verify_codeflash_crc_reconstruction.py`) | verified correction; acquisition-error attribution is strong inference |
| Reported behavioral effect of the patch on `8965F3/F4` | external-source (author statement + version table) | external-source |
| Semantic identity of the patched function on `8965F3/F4` | — | not established (available files do not identify the function) |
| Direct transfer of egg-based patch to `8965B4512000` | firmware-static | disproved |

The author notes this is "largely untested." The 8965F3 dual-CPU part is a new
family that may differ in flash controller geometry or callback layout.

A fail-closed pre-acquisition workflow is now tracked in
[community-patch-target-analysis.md](../../tooling/community-patch-target-analysis.md).
`tools/analyze_secoc_patch_target.py` performs raw egg/context triage only;
`AnalyzeCommunityPatchTarget.java` owns instruction-aware caller/callee/ICU-S
classification after a future F3/F4 image is imported. Raw halfword scanning is
explicitly not used for caller attribution because it overcounted the known
Sienna target (11 apparent JARLs versus 2 real Ghidra call references).

### 1.8 Stage-7 software-path closure

Two remaining software-side extraction ideas are now statically bounded rather
than left open:

- **Stale ICU result/FIFO reuse:** commands 1/3, 5, and 7 can leave prior result
  bytes resident in their private staging buffers, but every recovered outward
  wrapper copies only on completion status zero. Command 8 additionally clears
  its 64-byte input and 48-byte result staging after success or failure. Shared
  driver serialization, command-ID matching, and callback-nullification before
  abort command `0x3F` prevent the obvious cross-command replacement path. No
  diagnostic/unrelated reader of the result staging was recovered. This is a
  bounded software negative; abnormal hardware sequencing that reports clean
  completion without delivering the specified output blocks is outside the
  static software model. Canonical: [software-path-assessment.md](software-path-assessment.md).
- **Command-5 test activation (corrected 2026-08-13):** the earlier direct-pointer
  census missed a one-hop stock diagnostic edge. Application RoutineControl RID `0x100F`
  startRoutine points to wrapper `0x8A782`, whose call at `0x8A786` directly invokes
  `crypto_test_bank1_activate @ 0x69018`. The selector consumes zero data fields;
  policy 0 has no SecurityAccess-level entries and allows session records 1/2/3,
  while the outer SID-`0x2E` gate permits programming/extended. Thus
  `31 01 10 0F` arms bank 1 in stock application diagnostics, including default session. CAN
  `0x01B..0x01F` still cannot arm it alone. Startup clears `FEBE508F`, while the
  finalizer leaves a terminal state, so a fresh application boot is required for
  a deterministic repeat.

These negatives do **not** remove the signing-oracle route. The application
already contains a serialized command-5 path and a viable foreground hook
architecture; [sender-implementation.md](sender-implementation.md) §5 specifies
the minimum design, including selector 4, command-7 contention, freshness, Tx,
and teardown. What remains unknown is live hardware permission and runtime
performance, not basic software plumbing.

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
| application SID `0x23` is a verified bounded RMBA disclosure; SIDs `0x34/0x36/0x37` remain null direct callbacks; RoutineControl sizing is exact (maximum 67 bytes after SID) | **verified, scoped to this image** | firmware-static/test |
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

## 11. Strategic framework: two independent layers and cross-ECU attack surface

> **Document type:** strategic analysis, not a verified firmware finding.
> Synthesizes the recovery methods above with external evidence to frame the
> broader research direction. This section is scoped as **hypothesis** unless a
> specific claim references a FINDINGS-grade result. It does not modify or
> supersede the carefully bounded conclusions in
> [sender-implementation.md](sender-implementation.md) or
> [variants/](../../variants/).

### 11.1 The two layers are independent

The vehicle's SecOC system presents two independent security layers. They do
not have to fail together on the same ECU, and the cheapest path to a shared
SecOC key may target different layers on different ECUs:

| Layer | Mechanism | Secret | Scope | Evidence |
|---|---|---|---|---|
| **1 — Bootloader payload gate** | Denso RH850/P1M-E UDS download, AES-CBC/CMAC, CRC32, callback execution | `PAYLOAD_BUILD_SECRET` | This image deterministically accepts the same pinned payload used by public tooling for several EPS versions; operation on those other versions is reported externally. **Untested across ECU types** (camera, sonar, gateway, clearance warning). | **verified** (this image); **external-source** (other listed EPS versions); **hypothesis** (cross-ECU) |
| **2 — SecOC key storage** | Per-ECU firmware generation: plain DataFlash, RAM, or ICU-S hardware boundary | Vehicle-specific 16-byte AES-128 | Storage differs across related EPS variants/calibrations. | **verified** (`12000` has no valid object-15 copy); **external-source/observed** (`14000` key); **hypothesis** (non-EPS ECUs) |

Layer 1 is a Denso AUTOSAR bootloader mechanism with no ICU-S involvement. It
gates *code execution* — the ability to upload and run arbitrary shellcode on
the target ECU. Layer 2 gates *key access* — whether that shellcode can read
the SecOC key from the ECU's memory.

We observe layer-2 variation *within* the EPS family: the `8965B4514000`
exposes a key candidate at CPU-visible DataFlash object 15 (`0xFF206E14`),
while this `12000` calibration has **no valid key copy** in object 15. The
three triplicate copies are uncommitted/invalid (raw field:
`00000000040000808202000000000000`), not erased-blank, and the runtime
verification path selects ICU-S slot 4 (SECOC-002/003). The exact production
relationship between object 15 and the live slot-4 key remains unknown.
Whether similar variation exists across different ECU types on the same vehicle
is **hypothesis** — no non-EPS ECU has been analyzed.

### 11.2 Cross-ECU payload portability: untested hypothesis

If layer 1's `PAYLOAD_BUILD_SECRET` is shared across ECU types (not just EPS
part variants), all Denso RH850/P1M-E ECUs on the vehicle bus are potential
code-execution targets, not just the EPS.

The optskug community timeline reports a TechInfo-derived list of ECU types
covered by the "ECU Security Key" procedure for the RAV4 Prime (forward camera,
clearance warning ECU, No. 2 skid control ECU, combination meter, etc.). That
secondary report does not by itself prove SecOC message authentication, nor
does it confirm the same bootloader payload format or the same
`PAYLOAD_BUILD_SECRET`. Those are separate, untested claims.

**No public test has been identified** in which a payload signed with the EPS
`PAYLOAD_BUILD_SECRET` was uploaded to a non-EPS ECU. Such an experiment would
be the cheapest discriminator: acquire an inexpensive donor ECU, attempt the
existing signed payload, and observe whether routine `0x10F0` accepts it.
Acceptance by one ECU type would demonstrate portability **to that ECU only** —
it would not establish compatible bootloaders across all ECU types, nor would
it prove weak key storage on that ECU.

### 11.3 Key-sharing topology: external evidence, not firmware proof

Pinned opendbc's sender uses a single `self.secoc_key` field for both steering
(`0x2E4`, `0x131`) and acceleration (`0x183`) output streams. This is an
implementation interface that **treats** those streams as sharing one key, but
it is external-source evidence with a placeholder key (`b"00" * 16`), not a
firmware-derived proof of production key topology. See
[sender-implementation.md](sender-implementation.md) §1.2–1.3 for the bounded
opendbc analysis.

The I-CAN-Hack report concerns the RAV4 Prime EPS and states that its extracted
SecOC key enabled sending messages to other ECUs and controlling LKA, ACC, and
AEB. That is **external-source** evidence consistent with one key serving
multiple control paths on that RAV4 Prime, but it is not a firmware-static proof
that one key opens every protected PDU on every Toyota SecOC vehicle.

For this Sienna EPS, the firmware verifies that all six configured receive
profiles select ICU-S slot 4 (SECOC-001/002), which is **firmware-verified**
evidence of a single key slot for the profiles this ECU receives. It does not
constrain the key topology of PDUs this ECU does not receive.

### 11.4 EPS as native SecOC signing oracle: lower API yes, stock bank no

SECOC-069 separates two previously conflated paths. Stock RID `0x100F` can
activate a tester-controlled command-5 test without SecurityAccess, but that
caller fixes the CMAC input to 16 bytes and keeps output private; it therefore
is **not directly congruent** with the configured 7/12/36-byte SecOC domains.
The lower command-5 prepare at `0x87A94`, however, accepts 0..80 input bytes, so
application-context code can request the exact 12-byte classic or 36-byte FD
authenticated input. If ICU-S slot 4 permits MAC generation, that lower path can
turn the EPS into a native SecOC signing oracle without plaintext key recovery.
It remains gated by hardware policy and application-context execution:

1. **Does ICU-S slot 4 permit MAC generation?** Command 5's software plumbing
   accepts selector 4 and handles output (SECOC-006, **verified structure**).
   Hardware slot-4 generation permission is **unobserved**. Under standard SHE semantics the same MAC-usage flag permits generation and verification (SECOC-023/CORR-017); a rejection would therefore indicate a Renesas-specific restriction or lifecycle condition, not a standard "verification-only" key policy.
2. **Is ICU-S operational in bootloader context?** The authenticated callback
   runs before application init. Whether ICU-S is initialized and slot 4 is
   loaded at that point is unknown. A restorable application-context hook is
   the fallback (SEC-BOOT-008, **recovered** but not bench-tested).

The remaining supporting elements are independently verified:

- **Code execution**: the authenticated bootloader callback path
  (SEC-BOOT-005/006) is **verified** and constructible from repository-known
  material.
- **CAN TX**: proven by the pinned CAN-dump payloads, which transmit data over
  CAN. This is a **verified** transport mechanism.
- **Input format**: the authenticated-input and trailer packing for ordinary
  classic frames is **verified** from both firmware and the independent signer
  ([sender-implementation.md](sender-implementation.md)).

### 11.5 Sender freshness is a separate unsolved problem

A signing oracle based on this EPS needs independent *sender* counters
synchronized to the intended receiving ECU. The EPS tracks freshness only as a
*receiver* — SECOC-012 describes receive-window initialization and sync
acceptance for this EPS's inbound paths, not a transmit-side freshness manager.

A sender must:

- maintain per-PDU message counters;
- consume the synchronization frame (`0x00F`) to align trip/reset counters;
- increment the correct counter after each protected send;
- handle reset-counter changes as state transitions.

These requirements are identical to those documented for the opendbc sender
in [sender-implementation.md](sender-implementation.md) §1.1, which notes that
"separate protected PDUs need separate message-counter state, and a stale or
unauthenticated sync must not silently replace the active sender epoch." That
analysis applies equally here.

The receiver-freshness observation in SECOC-012 (initialization zeroes windows,
accepts forward sync) describes what the EPS would accept as a *receiver*. It
does not by itself establish that a compromised EPS can *originate* valid
sender freshness. The startup-race dynamics described in OPEN_QUESTIONS
("reset-window replay") remain open for the sender case as well.

Stage 7 now makes the latency/contention architecture concrete: command-5 generation and command-7 verification share the same serialized ICU-S driver. The proxy design therefore treats a busy result as defer, never preempts a production verify with the abort path, and bounds its own queue. Whether this arbitration meets live message cadence remains dynamic.

### 11.6 Implications for recovery strategy

If the shared-key hypothesis holds and cross-ECU payload portability is
confirmed, the recovery effort broadens from "extract the key from this
hardened EPS" to "find the cheapest path to the shared key or an equivalent
signing capability across the vehicle's SecOC ecosystem." The ranked methods
in §2 can then be evaluated against the full vehicle surface rather than this
one ECU.

These are **hypotheses**, not established facts. The framework motivates
specific experiments:

1. Test whether the EPS `PAYLOAD_BUILD_SECRET` is accepted by an inexpensive
   non-EPS donor ECU (§11.2).
2. Test whether command 5 with selector 4 produces output after normal
   application initialization (§11.4, already the rank-4 method in §2).
3. If command 5 succeeds, prototype a sender that maintains independent
   per-PDU freshness and validates against a live receiver (§11.5).

Variant-specific outcomes should be recorded in [docs/variants/](../../variants/),
not here.

## References

Firmware-internal:
- [sender-implementation.md](sender-implementation.md) — opendbc sender analysis
- [application-chain.md](application-chain.md) — receive-chain and freshness boundary
- [docs/variants/](../../variants/) — variant-specific comparison

External (cited in §11):
- Willem Melching, *Extracting SecOC keys from a 2021 Toyota RAV4 Prime*:
  <https://icanhack.nl/blog/secoc-key-extraction/>
- Willem Melching, *Bypassing the Renesas RH850/P1M-E read protection using
  fault injection*:
  <https://icanhack.nl/blog/rh850-glitch/>
- commaai/opendbc SecOC sender (pinned commit
  `c9b31d21bc396e8958891e271936bdbdf1a6ca93`):
  <https://github.com/commaai/opendbc/blob/c9b31d21bc396e8958891e271936bdbdf1a6ca93/opendbc/car/secoc.py>
- optskug/docs community timeline (accessed 2026-07-30):
  <https://github.com/optskug/docs>

Hardware/reference manuals:
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

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [SECOC-015](../../reference/index.md#finding-secoc-015), [SECOC-016](../../reference/index.md#finding-secoc-016), [SECOC-017](../../reference/index.md#finding-secoc-017), [SECOC-018](../../reference/index.md#finding-secoc-018), [SECOC-023](../../reference/index.md#finding-secoc-023), [SECOC-024](../../reference/index.md#finding-secoc-024), [SECOC-025](../../reference/index.md#finding-secoc-025), [SECOC-026](../../reference/index.md#finding-secoc-026), [SECOC-027](../../reference/index.md#finding-secoc-027), [SECOC-028](../../reference/index.md#finding-secoc-028)
- Corrections with this document as canonical home: [CORR-013](../../reference/index.md#correction-corr-013), [CORR-017](../../reference/index.md#correction-corr-017), [CORR-042](../../reference/index.md#correction-corr-042), [CORR-087](../../reference/index.md#correction-corr-087)
<!-- knowledge-cross-references:end -->
