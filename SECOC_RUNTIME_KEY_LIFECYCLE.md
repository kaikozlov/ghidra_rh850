# SecOC runtime key lifecycle: corrected firmware analysis

This note re-investigates the report's headline claim that the Sienna CN EPS
`8965B4512000` derives its SecOC key inside ICU-S and exposes the plaintext key at
`0xFEBEF468`, `0xFEBFEB08`, and `0x72F58` during a dealer-triggered rekey.

The claimed path was traced completely. It is **not a cryptographic key lifecycle**.
It is an AUTOSAR NvM-backed redundancy and checkpoint subsystem used by
SecOC-associated application state.

`verify_secoc_nvm.py` independently verifies the tables and DataFlash records from
the committed split images.

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

The proposed rekey monitor would therefore capture ordinary persistent state—not
the SecOC AES key. Hooking `0x72F58` would observe NvM block reads.

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
work buffers beginning at `0xFEBFEB08`.

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

## 6. What `0x679D6 -> 0x78504 -> 0x758A0` really does

`nvm_validate_triplicate_records @ 0x679D6` resolves each configured NvM block to
a 64-byte DataFlash page and checks whether the record can be read successfully.
`0x758A0` reads into a local stack buffer and converts flash/NvM status codes.

The buffer is discarded because this particular call is a validity probe. No
buffer, metadata, or key is passed to a cryptographic engine. Therefore this call
chain is not evidence of key derivation, a fused master key, or ICU-S binding.

## 7. Where the actual SecOC key most likely lives

The MCU facts and firmware layout support a different model:

1. Renesas documents R7F701381/P1M-E as ICU-S-equipped.
2. ICU-S provides SHE-style AES/CMAC acceleration and protected key storage.
3. The normal firmware NvM configuration has 124 blocks and maps DataFlash only
   through page 479 (`0xFF2077C0`).
4. Pages 480–511 (`0xFF207800–0xFF207FFF`) are absent from that NvM map.
5. This final 2 KiB reads as only `0x00`/`0xFF`, unlike normal NvM data.
6. External RH850 programming documentation describes the last 1 or 2 KiB of
   DataFlash on ICU-S devices as an ICU-S-reserved secure region.

This is strongly consistent with the SecOC key residing in an ICU-S/SHE protected
slot in the reserved tail, selected by slot ID for CMAC operations. It does **not**
show per-boot derivation from pages 468–479.

The exact key slot and ICU-S register protocol are vendor-confidential and are not
recoverable from the ordinary CodeFlash/NvM path analyzed here. Therefore
“secure-slot storage/use” is the best-supported model, while the precise SecOC slot
remains unproven.

## 8. Injection and refresh implications

A standard SHE persistent-key update uses authenticated/encrypted M1–M3 messages.
The new AES key is encrypted inside M2 and decrypted inside SHE/ICU-S; successful
installation returns M4/M5 proof. Except for an explicit development-only
`LOAD_PLAIN_KEY` into `RAM_KEY`, plaintext persistent keys do not need to appear in
host CPU RAM.

No dealer-triggered key update, SHE `LOAD_KEY`, `LOAD_PLAIN_KEY`, M1–M5 parser, or
plaintext key handoff was identified in the report's proposed path. Consequently:

- monitoring `0xFEBEF468/478/488` captures structured NvM state;
- monitoring `0xFEBFEB08` captures raw/XOR redundant NvM copies;
- hooking `0x72F58` captures `NvM_ReadBlock` destinations and contents;
- none of these is a validated SecOC key capture point;
- the claimed 58% dealer-tool capture design has no firmware basis.

If a dealer rekey operation exists, its correct observation point must be found at
the ICU-S/SHE command interface or at the diagnostic/RTE path carrying M1–M3—not
in this NvM redundancy module. A real dealer trace or dynamic ICU-S SFR trace is
needed to identify it.

## 9. Answers to the original questions

### How is the SecOC key injected?

**Not through `0x65CD8 -> 0x66E48 -> 0x67590 -> 0x72F58`.** That is NvM state
restore/persistence. Static evidence does not identify the production provisioning
path. ICU-S/SHE authenticated key provisioning is the hardware-consistent model.

### How is it derived?

There is **no evidence** of per-boot derivation from pages 468–479 or of a fused
master-key KDF in this path. Pages 468–479 decode deterministically as redundant
application state. The report's derivation claim must be retracted.

### How is it refreshed?

No SecOC rekey state machine was found in the claimed functions. They refresh NvM
RAM mirrors after reads and persist changed state after writes. A genuine key
refresh, if supported, should use the ICU-S/SHE key-update protocol and remains to
be located dynamically.

### Is it ever in dumpable CPU RAM?

Not at any of the claimed locations. The traced CPU-visible data is fully decoded
and is not the AES key. Static analysis cannot prove that no other code ever uses
`LOAD_PLAIN_KEY`, but no such plaintext handoff has been identified. Persistent
ICU-S keys are designed not to be readable by the main CPU.

## 10. Evidence grades

| Finding | Grade |
|---|---|
| `0x72F58/0x72F84` are NvM ReadBlock/WriteBlock | **Definitive** |
| pages 468–479 are redundant encoded state, not derivation metadata | **Definitive** |
| FEBEF mirrors/workbuf do not contain the SecOC AES key in this path | **Definitive** |
| report's rekey-capture path is invalid | **Definitive** |
| report's per-boot ICU derivation claim is unsupported | **Definitive** |
| final 2 KiB is the ICU-S protected storage tail | **Strong inference** |
| SecOC key resides in a persistent ICU-S slot | **Strong inference** |
| exact SecOC slot/provisioning/rekey diagnostic | **Unknown** |

## References

- AUTOSAR, *Specification of NVRAM Manager*:
  <https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf>
- Renesas, *RH850/P1M-E Datasheet* (R7F701381 has ICUS):
  <https://www.renesas.com/en/document/dst/rh850p1m-e-datasheet>
- Renesas, *Achieving a Root of Trust ... Part 2* (ICU-S/SHE architecture):
  <https://www.renesas.com/en/blogs/achieving-root-trust-secure-boot-automotive-rh850-and-r-car-devices-part-2>
- FlashRunner RH850 programming note (ICU-S reserves final 1/2 KiB DataFlash):
  <https://smh-tech.com/remos_docs_remoto/Interfacing%20FlashRunner%20with%20RH850%20family%20MCUs.pdf>
