# SecOC runtime key lifecycle: corrected firmware analysis

This note re-investigates the report's headline claim that the Sienna CN EPS
`8965B4512000` derives its SecOC key inside ICU-S and exposes the plaintext key at
`0xFEBEF468`, `0xFEBFEB08`, and `0x72F58` during a dealer-triggered rekey.

The claimed path was traced completely. It is **not a CSM/ICU command chain**.
It is an AUTOSAR NvM-backed redundancy and checkpoint subsystem used by
SecOC-associated objects. The initial analysis decoded only objects 0–3 and
incorrectly generalized that every object was non-key state. The full DataFlash
map in `DATAFLASH_LAYOUT.md` shows that object 15 is a 32-byte triplicate object
whose second half is the field-verified SecOC-key location on related variants.

`verify_secoc_nvm.py` verifies the original NvM correction. The broader 16-object
map and key-location correction are checked by `verify_dataflash_layout.py`.

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

Pages 480–511 remain strongly consistent with an ICU-S-reserved 2 KiB tail, but
that hardware/layout fact no longer supports placing this SecOC key there. Secure
ICU-S storage may hold other material.

## 8. Injection and refresh implications

No dealer-triggered update state machine was identified. The traced path is generic
NvM restore/persistence, but generic does not mean non-key: object 15 is key-bearing
on field-verified related variants.

Consequently:

- monitoring `0xFEBEF468/478/488` still captures objects 0/1/3, not the key;
- object 15's known related-variant locations are DataFlash `0xFF206E14` and RAM
  `0xFEBF02F8`;
- `0xFEBFEB08` can temporarily hold any currently processed triplicate object,
  including object 15, but it is not a fixed key staging address;
- hooking `0x72F58` identifies generic reads; a useful monitor must filter block
  41/45/49 and observe completion, not treat the call as ICU key-set;
- none of those locations contains a valid key in this exact committed snapshot;
- the original dealer/FEBEF capture design remains unsupported.

## 9. Answers to the original questions

### How is the SecOC key injected?

The production provisioning command remains unknown. On related variants the
result is persisted as object 15's raw/XOR55/XORAA NvM copies. No SHE M1–M5 parser
or ICU key-set path was established in the functions originally claimed.

### How is it derived?

There is no evidence of per-boot derivation from pages 468–479 or of a fused-key KDF
in this path. Pages 468–479 are redundant application objects. Related variants
store the already usable AES key in object 15; this exact dump has no valid copy.

### How is it refreshed?

`0x65CD8/0x66E48/0x67608` can update and persist any configured redundancy object,
including object 15 when addressed through namespace `0x100`. The diagnostic or
RTE source that would authorize/populate object 15 was not identified, so a dealer
rekey trigger remains unknown.

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
| exact key source/provisioning path for captured `8965B4512000` | **Unknown** |

## References

- AUTOSAR, *Specification of NVRAM Manager*:
  <https://www.autosar.org/fileadmin/standards/R22-11/CP/AUTOSAR_SWS_NVRAMManager.pdf>
- Renesas, *RH850/P1M-E Datasheet* (R7F701381 has ICUS):
  <https://www.renesas.com/en/document/dst/rh850p1m-e-datasheet>
- Renesas, *Achieving a Root of Trust ... Part 2* (ICU-S/SHE architecture):
  <https://www.renesas.com/en/blogs/achieving-root-trust-secure-boot-automotive-rh850-and-r-car-devices-part-2>
- FlashRunner RH850 programming note (ICU-S reserves final 1/2 KiB DataFlash):
  <https://smh-tech.com/remos_docs_remoto/Interfacing%20FlashRunner%20with%20RH850%20family%20MCUs.pdf>
