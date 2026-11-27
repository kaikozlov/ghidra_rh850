# Bootloader payload authentication and execution path

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades.
>
> **Canonical artifacts:** pinned payload fixtures
>
> **Verification:** `tests/runtime/verify_payload_gate.py`
>
> **Related:** [bootloader diagnostics](../diagnostics/bootloader.md), [bootloader-dids](../diagnostics/bootloader-dids.md), [R4P meter payload comparison](../variants/yc-r4p-2024-meter.md#payload-decryption-and-authentication)

This note traces the complete firmware-side path used by the public RH850/P1M-E
payload toolchain: UDS download, AES-CBC decryption, CRC + CMAC authentication,
and the `0xFF00` execution trigger. Addresses are CodeFlash virtual addresses.

`tests/runtime/verify_payload_gate.py` independently checks the static tables,
callback instructions, and the two unique encrypted payload fixtures represented
by four pinned public upstream copies. Fixture provenance and upstream hashes are
in `external-references.lock.json`.

## Executive result

The bootloader does **not** directly implement an "execute RAM" routine.
Instead, an authenticated 4 KiB image overwrites a flash-driver callback slot at
RAM `0xFEBF0FD0`. The legitimate `0xFF00` erase path loads that callback and
calls it indirectly. Builders put `0xFEBF0000` in the slot, so execution starts
at the first byte of the uploaded plaintext.

Before this can happen, routine `0x10F0` must validate the RAM image:

1. Embedded address and length fields must match firmware-owned descriptors.
2. CRC32 over plaintext `[0xFEBF0000, 0xFEBF0FF0)` must have residue
   `0xFFFFFFFF`.
3. AES-CMAC over `DID_0x202_IV || plaintext[0:0xFF0]` must match the final
   16-byte tag at `0xFEBF0FF0`.
4. Only then is the RAM-region authorization bit set, allowing `0xFF00`.

The cryptographic key is:

```text
derived_key = AES-128-ECB-ENC(PAYLOAD_BUILD_SECRET, DID_0x201)
```

The normal tooling uses zero for DID `0x201` and DID `0x202`, but the secret is
still required to create a valid CMAC/ciphertext.

## 1. Static policy tables

### Download-access table at `0x8DA0`

Three 16-byte entries are consumed by the range checker at `0x32D2`:

```text
0x00010000..0x00017DFF  opmask 0x33  class 0
0x00018000..0x000FFDFF  opmask 0x33  class 0
0xFEBF0000..0xFEBF0FFF  opmask 0x33  class 1
```

Thus the only downloadable RAM window is exactly 4 KiB, including callback slot
`0xFEBF0FD0` and trailer/tag area `0xFEBF0FE0..0xFEBF0FFF`.

### Region table at `0x8E00`

The RAM row is:

```text
start             0xFEBF0000
end               0xFEBF0FFF
CMAC tag address  0xFEBF0FF0
CRC descriptor #  1
CRC descriptor *  0x00008DF0
```

The CRC descriptor at `0x8DF0` is:

```text
data address              0xFEBF0000
CRC length                 0x00000FF0
embedded-address pointer   0xFEBF0FE0
embedded-length pointer    0xFEBF0FE4
```

This table explains the builder format without relying on source comments.

### Routine table at `0x8F44`

Five 12-byte records describe RIDs `0x10F0`, `0x10F1`, `0x10F2`, `0x10F3`, and
`0xFF00`. All are StartRoutine-only. `0x10F0`, `0x10F1`, `0x10F2`, and `0xFF00`
require a 10-byte option record (`45 00 || address_be32 || length_be32`), while
`0x10F3` has no option record. `../diagnostics/bootloader.md` completes the
`0x10F1`–`0x10F3` behavior: `0x10F1` aliases `0x10F0`, `0x10F2` validates a
CodeFlash region and programs its validity marker, and `0x10F3` arms an
operation-bit-5 read-back comparison transfer.

## 2. RequestDownload (`SID 0x34`, handler `0x5D68`)

The request used by all available tooling is:

```text
34 01 46 01 00 FEBF0000 00001000
```

The handler requires the SA-unlock state byte `0xFEBF2B0F == 2` (detailed in
[§ SecurityAccess gates RequestDownload](#securityaccess-gates-requestdownload)
below), validates the range against `0x8DA0`, records the current destination
and remaining byte count, and initializes payload crypto when enabled:

```text
payload_build_derive_key       0x7068
payload_crypto_initialize      0x70D4
```

### SecurityAccess gates RequestDownload

RequestDownload's security check compares one gp-relative SA-unlock byte to
`2`:

```text
0x5efc  ld.bu -0x6cf1[gp], r19   ; byte @ 0xFEBF2B0F   (gp = 0xFEBF9800)
0x5f00  cmp   0x2, r19
0x5f02  be    <pass>
0x5f04  movea 0x33, r0, r6        ; NRC securityAccessDenied
```

`0xFEBF2B0F` is the bootloader SA-unlock state. It is written to `2` by exactly
one site — the success path of `uds_security_access_send_key` (`0x54dc`, reached
only when a `27 02` key matches `security_access_compute_expected_key`); a key
mismatch takes the `0x35` (invalidKey) branch at `0x54d4` instead. Boot init
(`0x5090`, `FUN_00005086`) and the diagnostic-session-change handler (`0x561e`,
`FUN_000055fc` called from `bootloader_set_diagnostic_session`) only ever write
`1`. Therefore DiagnosticSessionControl (`10 0x`) alone cannot satisfy the gate;
the `SEED_KEY_SECRET`-based SecurityAccess (SEC-BOOT-002/003) is mandatory.

The same byte gates two sibling services identically — `WriteDataByIdentifier`
(read `0x49c6`) and `ECUReset` (read `0x610c`), both `cmp 2 / be / NRC 0x33`.
Writer/reader provenance is re-runnable via `ghidra x-ref to 0xFEBF2B0F`, and the
byte behaviour at every site is asserted in `tests/tooling/verify_security_gate.py`
(SEC-BOOT-007).

There is one ordering nuance important for keyless-execution analysis. On one
RequestDownload class the handler can perform flash-operation setup and write
transfer-status `FEBF2B17=2` before reaching the final SA comparison at
`0x5EFC`. That does **not** make the operation independently pre-authenticated:
the branch first requires payload-ready byte `FEBF2B16==1`, whose only non-init
writer is WDBI `0x4A76`, after WDBI's own `SA==2` check at `0x49C6`. Boot init
clears both bytes, and RequestDownload commits destination/remaining length only
after its final SA gate (`FEBF2B00/04 @ 0x5F1E/0x5F22`). Thus the exact claim is
"SA is mandatory for a usable download context," not "RequestDownload has zero
pre-SA side effects." See KEYLESS-009.

Its positive response is `74 20 04 02`, advertising maximum block length
`0x0402`: SID + block counter + at most `0x400` data bytes.

## 3. TransferData (`SID 0x36`, handler `0x4DBA`)

The active-download path enters `0x4B7C`:

- validates monotonically increasing 8-bit block counters;
- accepts a duplicate previous counter as a retransmission and repeats the
  positive response without consuming data;
- requires each non-final data chunk to be exactly `0x400` bytes;
- allows a final chunk of at most `0x400` bytes;
- rejects overflow, bad length/sequence, or an overrun of the declared size;
- queues ciphertext source, plaintext destination, and byte count at `0x6BB4`.

The periodic task at `0x6BDE` consumes one 16-byte block per invocation:

```text
AES-128-CBC-DECRYPT(ciphertext, derived_key, DID_0x202_IV)
```

`0x7108` wraps the CBC primitive at `0x8162`. The plaintext is copied directly
to the requested address, so the four public `0x400` chunks fill
`0xFEBF0000..0xFEBF0FFF`.

Important: TransferData decrypts but does **not** authenticate the image.

## 4. RequestTransferExit (`SID 0x37`, handler `0x5C92`)

TransferExit succeeds only when the declared remaining byte count is zero. It
clears the CBC/CMAC contexts and download state. Authentication still has not
occurred; the separate `0x10F0` routine is mandatory.

## 5. Routine `0x10F0`: CRC then CMAC

`uds_routine_control @ 0x567E` parses the RAM address/size, checks class 1, and
queues the CRC job at `0x47BA`. The recovered asynchronous worker is `0x5936`.

### CRC stage

`0x4874` resolves the descriptor for the requested range and calls `0x481A`.
For the RAM image, `0x481A`:

1. verifies `*(uint32_t *)0xFEBF0FE0 == 0xFEBF0000`;
2. verifies `*(uint32_t *)0xFEBF0FE4 == 0x00000FF0`;
3. computes the hardware CRC over the first `0xFF0` bytes through `0x47EA`;
4. accepts the residue generated by the builders (`0xFFFFFFFF` under Python's
   `binascii.crc32`).

CRC failure eventually returns NRC `0x72` and does not authorize the region.

### CMAC stage

After CRC success, `0x5936` re-derives the payload key and calls the recovered
functions:

```text
payload_cmac_verify_enqueue  0x6EBA
payload_cmac_verify_setup    0x7122
payload_cmac_verify_step     0x7170
AES-CMAC block engine        0x7E0C
```

Setup gets tag address `0xFEBF0FF0` from the region table and first feeds the
16-byte DID `0x202` IV into CMAC. It then scans plaintext blocks from
`0xFEBF0000` through `0xFEBF0FEF`; the final computed 16-byte MAC is compared
byte-for-byte with `0xFEBF0FF0..0xFEBF0FFF`.

Therefore the exact authenticated message is:

```text
DID_0x202_IV || plaintext[0:0xFF0]
```

On success, `0x5936` sets authorization bit 0 for the class-1 RAM region and
returns a positive `0x71` RoutineControl response. On failure it clears state
and emits NRC `0x72`.

## 6. Routine `0xFF00`: the execution transfer

The tooling sends:

```text
31 01 FF 00 45 00 000E0000 00008000
```

The `0xFF00` branch at `0x567E` requires the authorization state created by the
successful `0x10F0` pass. It starts a flash erase operation through `0x41E0`.
Its asynchronous response worker is `0x5B70`; however, normal completion is
preempted by the uploaded callback.

The main loop at `0x137A` runs the payload crypto/transfer worker and then the
flash-operation task `0x4428`. The erase engine reaches `0x4332`, whose exact
instructions are:

```text
0x434C  movhi 0xFEBF, r0, r29
0x4350  ld.w  0x0FD0[r29], r29   ; r29 = *(uint32_t *)0xFEBF0FD0
0x435E  jarl  r29, lp
```

A second programming path repeats the callback load/call at `0x4402/0x440E`.

Every public builder deliberately writes this at plaintext offset `0xFD0`:

```text
*(uint32_t *)(0xFEBF0000 + 0xFD0) = 0xFEBF0000
```

Consequently `jarl r29` jumps to the shellcode at the beginning of the uploaded
image. The shellcode disables interrupts, performs its CAN dump, and jumps to
bootloader reset code. This explains why clients send `0xFF00` manually and do
not wait for a normal UDS response.

## 7. Exact 4 KiB plaintext format

```text
0x000..shellcode_end  shellcode
...                  zero padding
0xFD0                 uint32_le 0xFEBF0000  (flash callback target)
0xFD4..0xFDF          zero padding
0xFE0                 uint32_le 0xFEBF0000  (CRC descriptor address)
0xFE4                 uint32_le 0x00000FF0  (CRC descriptor length)
0xFE8                 uint32_le 0
0xFEC                 uint32_le CRC patch
0xFF0..0xFFF          AES-CMAC tag
```

The full plaintext is encrypted with AES-128-CBC using the derived key and DID
`0x202` IV before TransferData.

## 8. Security interpretation

The actual trust sequence is:

```text
SecurityAccess secret
  -> programming session unlocked
PAYLOAD_BUILD_SECRET + tester-provided DID 0x201/0x202
  -> ciphertext decrypted
  -> CRC descriptor validated
  -> CMAC validated
  -> RAM region authorized
0xFF00 erase path
  -> indirect callback at 0xFEBF0FD0
  -> authenticated shellcode executes at 0xFEBF0000
```

Thus the payload-build secret is a genuine code-execution gate. The CRC is only
an integrity/format check; CMAC provides the cryptographic authorization. The
critical execution primitive is the overlap between the allowed 4 KiB download
window and the flash driver's callback slot at offset `0xFD0`.

### Key-material lifetime and residue boundary

The root and the derived payload key have materially different lifetimes.
`payload_build_derive_key @ 0x7068` initializes an AES-128 context from the
16-byte `PAYLOAD_BUILD_SECRET @ 0xBFD8`, placing the raw root plus expanded
round-key state in the temporary context rooted at `0xFEBF2D48`. It then
computes

```text
Kpayload = AES-128-ECB-ENC(PAYLOAD_BUILD_SECRET, DID_0x201)
```

and writes the 16-byte result to `0xFEBF2D18..0xFEBF2D27`. Immediately after
that block operation, `aes128_clear_context @ 0x76C6` clears the temporary
root-derived AES context (`0xC4` bytes after its state flag). No recovered
software reader exposes the low-CodeFlash root at `0xBFD8`, and the transient
root key schedule is therefore not a recovered disclosure surface.

The derived key is handled less strictly. `payload_crypto_init_cbc_cmac @
0x709A` uses `0xFEBF2D18` to initialize both the CBC-decrypt context at
`0xFEBF2EF0` and the CMAC context at `0xFEBF2C00`; AES context initialization
copies the 16-byte raw key into each context before expanding it. Thus an active
payload operation has CPU-visible derived-key material at the persistent
`0xFEBF2D18` slot and in both live crypto contexts. `payload_crypto_clear @
0x70E4` clears the CBC/CMAC contexts, but does not clear the standalone
`0xFEBF2D18` slot. Retained zero-DID sessions independently observe the expected
value `80d221a05622b4f9d4f287922e6c78d1` at that address.

This matters because application SID `0x23` ReadMemoryByAddress permits reads of
`0xFEBF2D18` in both the canonical Sienna policy and the exact F33 policy; the
cell lies outside their LocalRAM exclusion ranges. Knowledge of `Kpayload` for a
chosen DID `0x201` is sufficient to construct the corresponding CBC ciphertext
and CMAC without separately recovering `PAYLOAD_BUILD_SECRET`. The neighboring
`0xFEBF2D08..0xFEBF2D17` buffer is only tester-provided DID `0x201` input and is
not itself secret-derived material.

The obvious residue composition is nevertheless closed by reset lifetime. The
reset-only startup initializer `0x1404` zeroes the full
`0xFEBE8000..0xFEBFFFFF` LocalRAM interval before the boot validity gate calls
the application, which necessarily destroys `0xFEBF2C00`, `0xFEBF2D18`,
`0xFEBF2D48`, and `0xFEBF2EF0`. Exact F33 is byte-identical to canonical Sienna
over the reset-clear neighborhood (`0x13E0..0x1477`), payload KDF/init/clear
neighborhood (`0x7068..0x70F7`), and AES init/clear neighborhood
(`0x7680..0x76D9`), so the same boundary applies there.

Therefore the stock software paths currently form a split capability:

```text
boot programming runtime: can derive Kpayload, but has no recovered arbitrary reader
reset/startup:             wipes Kpayload and its crypto contexts
application extended mode: can RMBA-read the address, but only after the wipe
```

No recovered stock boot-runtime operation returns to application execution
without traversing that reset/startup clear. A future no-reset boot→application
control transfer would immediately make `0xFEBF2D18` a high-value disclosure
candidate and should be re-audited before attempting to recover the root itself.

### Persistent-trust consequence

The boot-time application handoff does not establish OEM code provenance. It
checks CRC32 descriptors and fixed `0x5AA5A55A` markers for the two CodeFlash
regions. The high region covers application entry/vector code, but neither the
startup CRC nor the marker is keyed or signed.

Consequently, once the model-wide SecurityAccess and payload-build secrets have
been compromised and the authenticated RAM callback is executing, the remaining
boot boundary is consistency rather than authenticity. The payload executes in
the same CPU privilege domain as the boot flash sequencer, and the firmware
contains program/erase/marker machinery for the application-covered region. A
payload that obtains a durable CodeFlash write and recomputes the CRC fields and
markers can in principle install an application-resident hook that survives
reset. This repository has not built or bench-tested such a persistent patch.

This distinction is central to a comma design. A one-shot boot callback is in the
wrong GP/TP/RAM/interrupt context for the initialized ICU and CAN application
drivers. A persistent application hook would solve that context mismatch, but it
would also replace an OEM safety boundary and must be engineered and validated as
safety-critical firmware.


## 9. Exact F33 verification matrix

The following matrix applies to Camry `8965F3307000` CodeFlash SHA-256
`42dce8efc42f6ae31718e7713fa2d26bb9191b4a82439778aee4d7afded9b0e7`.
The cited boot neighborhoods are byte-identical to the canonical Sienna
specimen where this report already records that comparison.

| Stage | Authenticity, integrity, freshness, compatibility | Time and key | Flag lifetime | Erase/write relation and reset-vector use | Evidence | Open items |
|---|---|---|---|---|---|---|
| RequestDownload `34` | no payload authenticity or integrity check; no freshness; compatibility is only memory-class/range/format admission | once per request; requires DCM SecurityAccess state 2, but uses no payload-verification key | initializes resettable transfer state | accepts its own address/length; does not compare them with the preceding `FF00` erase request | `boot_service_request_download @ 0x5D68`, exact decompilation/disassembly | none |
| RequestUpload `35` | unsupported; therefore no authenticity, integrity, freshness, or compatibility decision | not dispatched; no key | no state | no erase/write relation | absent from the exact 20-record resident service table at `0x8E54` | none |
| TransferData `36` | enforces an 8-bit monotonic block sequence, duplicate retransmission, `<=0x400` block length and range bounds; CBC decryption is confidentiality, not authenticity; no freshness beyond the transfer-local counter; no version/part check | per block; AES-128-CBC with `Kpayload = AES-128-ECB(PAYLOAD_BUILD_SECRET,DID_201)` and tester IV `DID_202` | counter and transfer state are resettable RAM | programs the admitted download range; no automatic comparison with the independently requested erase range | `boot_service_transfer_data @ 0x4DBA` and payload KDF `0x7068`, exact decompilation/disassembly | none |
| RequestTransferExit `37` | checks that remaining length is zero; performs no CMAC, signature, freshness, or compatibility check | once at transfer exit; no key | clears transfer/crypto contexts; no one-time latch | does not compare erased and written ranges | `boot_service_transfer_exit @ 0x5C92`, exact decompilation/disassembly | none |
| RIDs `10F0/10F1` | verifies embedded address/length, CRC32 over `0xFF0` plaintext bytes, then AES-CMAC over `IV || plaintext`; no freshness or software-version check | after transfer, when requested; CMAC uses `Kpayload` derived from `PAYLOAD_BUILD_SECRET` and `DID_201` | RAM authorization bit 0 is set only after success and is cleared on failure/cleanup/reset; it is not set-once persistent state | authorizes the fixed RAM callback region; independent of the erase range and variable reset vector | worker `boot_advance_crc_authentication_routine_5936 @ 0x5936` and marker/auth worker `0x5A04`, exact decompilation | none |
| RID `10F2` | validates the selected CodeFlash region by CRC and, where its descriptor enables it, CMAC; then programs marker `5A A5 A5 5A`; no freshness/version/rollback check | after write, when requested; CRC is unkeyed | marker is persistent but erasable/reprogrammable, not a monotonic one-time flag | validates the caller-selected region; it does not prove that the same range was erased and written | `boot_advance_crc_authentication_marker_routine_5a04 @ 0x5A04`, marker check `0x6C5A`, exact decompilation | identify the configured CodeFlash-CMAC key source with `tools/g inspect 0x5936 --decompile --callers --disasm 140` followed through the class-0 descriptor |
| RID `10F3` compare mode | byte-for-byte integrity comparison only; no authenticity, freshness, or compatibility decision | optional post-program TransferData mode; no key | transfer state `8→9→10`, resettable RAM | compares tester-supplied bytes with a separately selected CodeFlash range; it is not automatically bound to `FF00` or the ordinary download | `boot_transfer_compare_progress @ 0x6C8E`, exact decompilation; resident service report records the state transitions | none |
| Reset boot path | CRC32 descriptors, UCFD status, and fixed markers for both application regions; no signature/keyed authenticity, freshness, software-version, part-number, or rollback check | every reset before application handoff; no key | markers persist until erased; boot rechecks them each reset | successful checks call the application entry pointer at `0xFFDB8`. The tracked dump contains the image reset path but not the hardware Configuration Setting Area that selects the variable reset vector | `boot_validate_application_images @ 0x119E`, `boot_select_application_or_resident @ 0x13B0`, exact decompilation/disassembly | obtain the Configuration Setting Area bytes and decode the active variable-reset-vector option |

The P1M-E flash manual, R01UH0615EJ0120 section 8.4.1, states that the
Configuration Setting Area can select a variable CPU reset vector and that OTP
configuration can prevent changing it. The tracked CodeFlash dump does not
include the `0xFF300040..0xFF30008F` configuration range. Consequently the
active hardware reset-vector option cannot be determined from this image.

### Absence-search record

| Claim | Image / SHA-256 | Pattern and tool | Matches | Classification | Exact query |
|---|---|---|---|---|---|
| no payload verification in `34/36/37` | F33 / `42dce8e…b0e7` | complete decision graphs for the three handlers, KDF and crypto cleanup | range/state/counter/CBC checks only; CMAC is reached only from the separate RoutineControl worker | true checks are listed above; no hidden verification call in the handler graphs | `tools/g inspect 0x5d68 0x4dba 0x5c92 --decompile --callers --disasm 45` and `tools/toyota decomp source 0x5d68 0x4dba 0x5c92` |
| no automatic erase/write range identity check | F33 / `42dce8e…b0e7` | compare all address/length writes and consumers in `FF00`, `34`, transfer, and compare-mode handlers | independent `FF00` and `34` address/length acceptance; one optional `10F3` tester-directed compare | two true independent range owners; `10F3` is a false positive for automatic linkage | `tools/g inspect 0x567e --decompile --callers --disasm 120`; `tools/toyota decomp source 0x41e0 0x5d68 0x6c8e` |
| no keyed/fresh/compatible reset decision | F33 / `42dce8e…b0e7` | complete boot-validation and handoff graphs | two CRC regions, two markers, UCFD status, one fixed application pointer; zero key/version/freshness consumers | all five observed checks are true boot gates; no false positives | `tools/g inspect 0x119e 0x13b0 --decompile --callers --disasm 45` |

### Variant closure

The matrix applies to F33. The Sienna byte comparisons cover only the
neighborhoods identified above.
