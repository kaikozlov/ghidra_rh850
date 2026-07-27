# Application SecOC receive chain and provisioned-unit experiment

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence profile:** mixed — claims carry individual grades; see FINDINGS SECOC-001, SECOC-002, SECOC-004
>
> **Canonical artifacts:** —
>
> **Verification:** `tests/verify_secoc_application.py`
>
> **Related:** [key-storage](key-storage-and-lifecycle.md), [dataflash](../../storage/dataflash.md)

This note traces the application-side SecOC receive configuration in the
China-market Sienna EPS image `8965B4512000`. It also specifies the dynamic
experiment needed to determine how a **provisioned** `12000` unit relates the
CPU-visible object-15 key field to ICU-S key slot 4.

The central correction is that the premise “object 15 feeds the CMAC routine” is
not true for this image. Object 15 is a generic triplicate NvM object whose second
field is a field-verified key location on related variants, but this CodeFlash has
no static consumer of `0xFEBF02F8`. The compiled SecOC verification path resolves
CryptoIf handle 0 and selects **ICU-S key slot 4**. In this snapshot, the slot-4
known-answer vector corresponds to an erased `FF*16` key and all four 32-byte
objects 12–15 are uncommitted. The most defensible conclusion is therefore
“hardware-backed receive profile with an unprovisioned/default key state in this
snapshot,” not an object-15-to-CMAC CPU data flow.

`../tests/verify_secoc_application.py` checks the configuration, routing,
known-answer vector, key-slot selection, freshness/MAC profile, and object-15
state directly from the committed images.

## 1. Six configured receive profiles

Application `tp` is `0x23EE4`. Six `0x50`-byte SecOC receive records begin at
CodeFlash `0x25970` (`tp + 0x1A8C`):

| CAN/Data ID | CAN format | Application RX PDU | Secured length | Trailer | Payload | Full freshness | Transmitted freshness | CMAC | Transmitted CMAC | CSM handle |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `0x00F` | classic | 11 | 8 | 8 | 0 | 36 bits | 36 bits | 128 bits | 28 bits | 0 |
| `0x2E4` | classic | 6 | 8 | 4 | 4 | 46 bits | 4 bits | 128 bits | 28 bits | 0 |
| `0x131` | classic | 26 | 8 | 4 | 4 | 46 bits | 4 bits | 128 bits | 28 bits | 0 |
| `0x132` | classic | 35 | 8 | 4 | 4 | 46 bits | 4 bits | 128 bits | 28 bits | 0 |
| `0x090` | CAN FD | 46 | 32 | 4 | 28 | 46 bits | 4 bits | 128 bits | 28 bits | 0 |
| `0x0D7` | CAN FD | 47 | 32 | 4 | 28 | 46 bits | 4 bits | 128 bits | 28 bits | 0 |

The hardware acceptance index maps to application PDU `6 + index`, exactly
matching the records' receive-PDU field:

```text
CAN 2E4: acceptance 0  -> PDU 6
CAN 00F: acceptance 5  -> PDU 11
CAN 131: acceptance 20 -> PDU 26
CAN 132: acceptance 29 -> PDU 35
CAN 090: acceptance 40 -> PDU 46
CAN 0D7: acceptance 41 -> PDU 47
```

`0x344` is different. It has no application RX acceptance rule, no SecOC record,
no aligned 32-bit literal in CodeFlash, and no statically assigned route in this
image. It may be transmitted by another ECU, transmitted by a related EPS, or
belong to a different calibration, but the external four-ID oracle must not be
projected onto this firmware as an EPS receive route.

## 2. Receive and authenticated-input data flow

The configured receive path is:

```text
CAN1 RX interrupt / queue
  -> application_can_normal_rx_demux @ 0x80006
  -> application_pdu_rx_router       @ 0x80C44
  -> SecOC ingress                    @ 0x8DC64
  -> record lookup                    @ 0x8E024
  -> queue/dispatch                   @ 0x8E0BE
  -> verification worker             @ 0x8E4BA
  -> split payload, freshness, tag    @ 0x8E1A8
  -> reconstruct full freshness       @ 0x8E8E6 / 0x8EECA
  -> build authenticated input        @ 0x8DB22
  -> CSM/CryptoIf wrappers            @ 0x8E3EA -> 0x88B6A/0x88B9C/0x88BA8
  -> lower crypto dispatch            @ 0x88556
  -> ICU-S CMAC-verify implementation @ 0x880DC -> 0x88080 -> 0x897F4
```

`0x8DB22` constructs the authenticated input as:

```text
DataID_be16 || authentic_payload || full_freshness
```

For `0x2E4`, `0x131`, and `0x132`, this is exactly 96 bits:

```text
2-byte CAN/Data ID || first 4 CAN bytes || 6-byte full freshness
```

For `0x090` and `0x0D7`, the same rule authenticates 28 payload bytes, producing
a 36-byte input. The `0x00F` synchronization frame has no authentic payload; its
input is the big-endian ID plus the five-byte, left-aligned 36-bit sync freshness.

The trailer is bit-packed rather than byte-separated:

- normal profiles: 4 freshness bits followed by the 28 most-significant CMAC bits;
- sync profile: 36 freshness bits followed by the 28 CMAC bits;
- consequently a classic protected frame is `payload[0:4] || freshness_nibble || tag28`;
- a sync frame is `trip16 || reset20 || tag28`.

The 28-bit value occupies the low nibble of byte 4 and bytes 5–7 in an eight-byte
frame. This matches the independent CAN oracle, but the static evidence above is
sufficient to establish the configured widths and bit extraction.

## 3. Freshness representation

`0x8EA4C` packs normal full freshness into six bytes as 46 meaningful bits followed
by two zero pad bits:

```text
trip_counter[16]
|| reset_counter[20]
|| message_counter[8]
|| reset_counter_low2[2]
|| 00b
```

Equivalently:

```python
freshness = pack_be16(trip) + pack_be32(
    (reset20 << 12) | (message8 << 4) | ((reset20 & 3) << 2)
)
```

The ordinary transmitted four-bit FreshnessValue is separately packed as
`message_counter_low2 || reset_counter_low2` in the high nibble of trailer byte 0.
`0x8EBC2` splits those two fields; `0x8EE5C` combines them with the receiver's
retained trip/reset state and counter window to reconstruct a candidate full value.
The transmitted nibble is therefore not simply a contiguous four-bit slice of the
six-byte full-freshness representation.

The `0x00F` synchronization profile transmits the 36-bit prefix directly:

```text
trip_counter[16] || reset_counter[20]
```

Successful authentication commits the reconstructed freshness through
`0x8E942`, with normal and synchronization state handled by `0x8F084` and
`0x8F112` respectively.

## 4. The CMAC key is ICU-S slot 4, not an object-15 pointer

The SecOC crypto configuration initialized at `0x25950` is:

```text
algorithm/type word = 1
ICU-S key selector  = 4
remaining bytes     = 0
```

`0x8DF0E` copies this record into the job configuration. `0x87F70` reads byte
`config + 4` and places it in the ICU request descriptor. `0x897F4` then starts
ICU-S command `7` (MAC verify) by writing:

```text
FFC5D000 = (key_slot << 16) | 7
```

The CPU supplies the authenticated message, its bit length, the received tag,
and the 28-bit tag length. It does **not** supply key bytes. No instruction in
this chain reads `0xFEBF02F8`, and no direct or generic object-15 owner call was
found outside the redundancy framework.

### Slot-4 known-answer check

Startup code at `0x680F8` and `0x682A6` verifies a fixed 16-byte message through
CryptoIf jobs 0/1 and the same ICU-S slot-4 selector:

```text
message @ 0x215E4: 00000000000000000000000000000000
CMAC    @ 0x215F4: B290FA2EA7B6B52EB124134522A6E540
config  @ 0x21604: type 1, slot 4
```

The embedded tag is exactly:

```text
AES-CMAC(key=FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
         msg=00000000000000000000000000000000)
```

This is strong static evidence that this calibration expects an erased/default
slot-4 key, consistent with the uncommitted object-15 bank. It does not prove the
contents of protected ICU-S storage at the instant the external dump was made,
because that storage is not present in the readable snapshot.

All six profiles pass CryptoIf handle `0` from record offset `+0x20`.
`0x88508` resolves this to lower record 0, whose callback is `0x880DC`; record 1
is used by the asynchronous phase of the slot-4 known-answer state machine. The
values `8` and `32` at record offset `+0x24` are buffer/PDU lengths, not job IDs.
Thus there is no lower-job mismatch: the generated path reaches the ICU-S verify
adapter when its runtime gates permit processing.

## 5. Why all object-15 copies are invalid

Object 15 remains structurally definitive:

```text
length 32, base NvM block 41, RAM mirror 0xFEBF02E8
raw:   block 41 / page 440 / key field 0xFF206E14
XOR55: block 45 / page 436 / key field 0xFF206D14
XORAA: block 49 / page 432 / key field 0xFF206C14
RAM second field: 0xFEBF02F8
```

In this dump:

- none of blocks 41/45/49 has the expected physical header and committed
  `AAAAAAAA` trailer;
- decoding the three payloads with raw/XOR55/XORAA does not produce a consensus;
- objects 12, 13, and 14 are also wholly invalid, so this is the state of the
  entire optional 32-byte bank rather than isolated corruption of object 15;
- the raw candidate field is low entropy and matches no captured CMAC oracle;
- the compiled ICU slot-4 known-answer value corresponds to `FF*16`;
- no application owner reads or updates object 15 through IDs `0x0F`/`0x10F`.

Together these facts make an unprovisioned or disabled feature bank the leading
explanation. They do not distinguish factory policy, a pre-provisioning capture,
a masked/incomplete acquisition, or a different production calibration. The
claim remains an inference until measured on a provisioned `12000` unit.

A separate address correction follows from the application GP value
`0xFEBEB800`: the restore work-buffer root is `gp + 0x5308 = 0xFEBF0B08`, **not**
`0xFEBFEB08`. Object 15 uses group `15 & 3 = 3`, hence:

```text
raw destination:   0xFEBF0C28
XOR55 destination: 0xFEBF0C48
XORAA destination: 0xFEBF0C68
```

The persistence source buffers at `0x67608` are `0xFEBF06A8/06C8/06E8`.

## 6. Correct dynamic experiment on a provisioned `12000`

The experiment must correlate NvM **submission and asynchronous completion**,
CPU RAM, post-write DataFlash, ICU slot selection, and CAN behavior. An entry hook
at `0x72F58` alone is not sufficient.

### 6.1 Preconditions and baseline

1. Record the exact CodeFlash/DataFlash hashes and software ID. Do not combine
   results from a `14000`, a different `12000` calibration, or a modified image.
2. Save a complete pre-test 32 KiB DataFlash image.
3. Capture timestamped CAN/CAN-FD frames with bus, ID, DLC, flags, and full payload.
   Include `0x00F`, `0x2E4`, `0x131`, `0x132`, `0x090`, `0x0D7`, and external
   candidate `0x344`; do not assume `0x344` is an EPS receive route.
4. Start from a true cold boot so the NvM restore and slot-4 known-answer checks
   are observed from initialization.

### 6.2 NvM restore instrumentation

Log these events with monotonic timestamps and call stacks:

1. `secoc_nvm_restore_triplicate @ 0x67590`, filtered to object index 15.
2. `nvm_read_block_submit @ 0x72F58`, filtered to blocks **41, 45, and 49**.
   Record block ID, destination pointer, immediate return, and request/queue ID.
3. `secoc_nvm_triplicate_read_complete @ 0x67C34` for those three blocks.
   Record the completion status argument and snapshot the corresponding destination
   only after completion—not at submit time.
4. When reconciliation returns completion (`0x5A`), dump:
   - `0xFEBF0C28..0xFEBF0C87` (object-15 raw/XOR55/XORAA work group),
   - `0xFEBF02E8..0xFEBF0307` (RAM mirror),
   - `0xFEBF02F8..0xFEBF0307` (candidate key),
   - object-15 validity/status byte `0xFEBF0367`.

Verify independently that raw, `XOR55 ^ 55`, and `XORAA ^ AA` agree before calling
the mirror field a key.

### 6.3 Update/persistence instrumentation

Monitor for the full test period, including any legitimate provisioning action:

1. `secoc_nvm_object_update @ 0x65CD8` and
   `secoc_nvm_redundant_object_update @ 0x66E48`, filtered to object 15
   (namespace ID `0x10F`). Record the caller and 32-byte source.
2. `secoc_nvm_persist_triplicate @ 0x67608`, filtered to index 15. Snapshot
   `0xFEBF06A8`, `0xFEBF06C8`, and `0xFEBF06E8`.
3. `nvm_write_block_submit @ 0x72F84`, filtered to blocks 41/45/49, plus the
   corresponding asynchronous completion/status events.
4. After confirmed write completion and power-cycle, acquire a second full
   DataFlash image and verify physical headers, trailers, three-way decode, and
   restore into `0xFEBF02E8`.

This identifies the actual diagnostic/RTE caller if provisioning occurs; it does
not mislabel a generic NvM API as a dealer key-set command.

### 6.4 ICU and CAN correlation

1. Observe the startup slot-4 known-answer paths at `0x680F8`/`0x682A6`. Record
   jobs 0/1, result status, message/tag/config pointers, and whether the embedded
   vector differs from this image.
2. At `ICU MAC verify @ 0x897F4`, record command, key-slot selector, authenticated
   input pointer/bit length, received-tag pointer/bit length, and result. The
   expected selector is 4; ICU key bytes are not CPU-readable through this API.
3. For each valid object-15 candidate `K`, first check:

   ```text
   CMAC_K(16 zero bytes) == embedded slot-4 known-answer tag
   ```

4. Then validate `K` against multiple synchronized CAN samples:
   - sync input: `be16(0x000F) || trip16 || reset20<<4`;
   - classic protected input:
     `be16(CAN_ID) || payload[0:4] || freshness48`;
   - FD protected input:
     `be16(CAN_ID) || payload[0:28] || freshness48`;
   - compare the first 28 CMAC bits with the packed frame tag.
5. Require repeated matches across sync and protected frames, not one accidental
   28-bit match. Keep `0x344` as a separate oracle class until its transmitter and
   direction are independently established.

### 6.5 Outcomes that distinguish the hypotheses

| Observation | Interpretation |
|---|---|
| Valid 41/45/49 consensus; RAM field matches slot-4 KAT and CAN oracle | Object 15 represents the operational slot-4 SecOC key on that unit/calibration |
| Object 15 remains invalid; slot-4 KAT and CAN verification succeed | Operational key is in ICU-S or another source; object 15 is unused/unprovisioned |
| Valid object 15 but it fails slot-4 KAT/CAN oracle | Object 15 belongs to another key domain or stale provisioning state |
| No 41/45/49 submissions despite the descriptor | Runtime policy/configuration disables object-15 restore |
| Writes appear only after a specific caller/action | That caller is the provisioning trigger; capture it rather than inferring a dealer command |
| Same CodeFlash selects slot 4 with only the `FF*16` KAT and emits no valid protected traffic | This captured state is unprovisioned/default or SecOC is operationally unused |

## 7. Evidence grades

| Finding | Grade |
|---|---|
| Six receive profiles and their CAN/PDU IDs and widths | **Definitive** |
| Authenticated input is DataID || payload || reconstructed freshness | **Definitive** |
| Normal profile is 4-bit FV + 28-bit CMAC trailer | **Definitive** |
| Full freshness packs 16+20+8+2 meaningful bits plus two zeros | **Definitive** |
| Compiled CMAC verify selects ICU-S slot 4 | **Definitive** |
| No static object-15 RAM-to-CMAC consumer exists | **Definitive for this image** |
| Slot-4 KAT equals CMAC under `FF*16` | **Definitive** |
| SecOC handle 0 resolves to lower ICU driver record 0 | **Definitive** |
| This snapshot has an unprovisioned/default key state | **Strong inference** |
| A provisioned `12000` mirrors the same key in object 15 and ICU slot 4 | **Requires the dynamic experiment** |
| `0x344` is a protected EPS message in this calibration | **Unsupported** |
