# Complete bootloader DID model

> **Scope:** Sienna EPS `8965B4512000`
>
> **Document type:** subsystem analysis
>
> **Status:** active
>
> **Evidence grade:** verified
>
> **Canonical artifacts:** —
>
> **Verification:** `tests/verify_did_model.py`
>
> **Related:** [bootloader](bootloader.md), [payload-gate](../security/bootloader-payload-gate.md)

This note maps every DataIdentifier accepted by the bootloader handlers
`uds_read_data_by_identifier @ 0x5FB8` and
`uds_write_data_by_identifier @ 0x4948` in the `8965B4512000` image.

The scope is specifically this bootloader dispatcher. It does not claim that an
application-mode diagnostic stack or related EPS variant exposes the same DIDs.

## Summary

There is one descriptor table and exactly four entries. The bootloader exposes
no VIN, serial-number, spare-part-number, fingerprint, calibration, or
DataFlash-backed DID through these two handlers.

| DID | Standard/local meaning | Access | Length | Backing / generated value |
|---:|---|---|---:|---|
| `F181` | ApplicationSoftwareIdentification | read | `32` plus one prefix byte | generated as `02 || 21*32`; no storage pointer |
| `0201` | payload key-derivation input | write | 16 | volatile RAM `0xFEBF2D08` |
| `0202` | payload AES-CBC IV / CMAC prefix | write | 16 | volatile RAM `0xFEBF2CF8` |
| `0203` | payload-DID sequence arm | write | 5 | data ignored; advances internal state `0 -> 1` |

`21*32` means 32 bytes of literal `0x21` (`'!'`). For `F181`, the injected
`0x02` is consistent with a count followed by two 16-byte software-ID fields,
but the firmware proof is only that it emits that exact byte sequence.

## 1. Descriptor table

The table begins at CodeFlash `0x8F14`; both handlers use `tp + 0x878` and loop
over exactly four 12-byte records.

```c
struct bootloader_did_descriptor {
    uint32_t destination;   // direct-write destination, if any
    uint16_t data_length;
    uint16_t did;
    uint8_t  access;        // bit 0 readable; bit 1 writable
    uint8_t  write_mode;    // 0 queued memory service; 1 direct RAM copy
    uint8_t  read_prefix;   // 0xFF none, otherwise prepend this literal byte
    uint8_t  reserved;
};
```

Raw records:

```text
VA 0x8F14  00000000 2000 81f1 01 00 02 00
VA 0x8F20  082dbffe 1000 0102 02 01 ff 00
VA 0x8F2C  f82cbffe 1000 0202 02 01 ff 00
VA 0x8F38  00000000 0500 0302 02 01 ff 00
```

The halfwords are little-endian, so `81f1` is DID `F181`, etc. The read handler
tests access bit 0; the write handler tests access bit 1. No second DID table is
consulted by either function.

## 2. ReadDataByIdentifier (`SID 0x22`)

### Policy

`uds_read_data_by_identifier @ 0x5FB8` requires:

- an exact three-byte request (`22 DID_hi DID_lo`);
- current diagnostic session in the table `{1,2,3}` at `0x8F00`;
- a matching descriptor whose access bit 0 is set.

The loop bound is four, making `F181` the only readable entry. Unknown DIDs and
write-only `0201/0202/0203` return NRC `0x31`. Other failure paths are:

| Condition | NRC |
|---|---:|
| unsupported active session | `0x7F` |
| wrong request length | `0x13` |
| unknown/not-readable DID | `0x31` |
| generation failure | `0x72` (unreachable for the configured filler) |

### Exact `F181` response

For the `F181` descriptor, `read_prefix = 0x02`. The function at `0x5F3E`
then writes literal `0x21` for all 32 data bytes. `0x5F7C` adds positive-response
SID `0x62`.

Thus this bootloader deterministically produces:

```text
62 F1 81 02 21 21 21 21 21 21 21 21
            ... 32 total 0x21 bytes ...
```

This is not the `BOOT INFO AREA` string at CodeFlash `0x180`, nor does it contain
`8965B4512000`. Tooling that expects `F181` to identify the EPS part number is
assuming an application-mode stack or another firmware variant. In this exact
bootloader, common identification DIDs `F180`, `F182`, `F187`, `F188`, `F189`,
`F18C`, and VIN `F190` all miss the four-entry table and receive NRC `0x31`.

## 3. WriteDataByIdentifier (`SID 0x2E`)

### Access policy

`uds_write_data_by_identifier @ 0x4948` requires:

- programming session `0x02` (policy byte at `0x8EF8`);
- SecurityAccess state `0x02` (unlocked);
- exact length `descriptor.data_length + 3`;
- descriptor access bit 1;
- the payload-DID sequence described below.

Responses are built by `0x4900`/`0x4914`; successful `0201/0202` direct copies
complete asynchronously through `0x4A9A`.

| Condition | NRC |
|---|---:|
| service unavailable in active session | `0x7F` |
| malformed length | `0x13` |
| unknown/not-writable DID | `0x31` |
| SecurityAccess locked | `0x33` |
| DID sequence out of order | `0x22` |
| copy/worker failure | `0x72` |

### Required sequence

The state byte at RAM `0xFEBF2AB2` begins at 0. The only accepted order is:

| State before | DID | Action | State after |
|---:|---:|---|---:|
| 0 | `0203` | ignore all five payload bytes; synchronously acknowledge and arm sequence | 1 |
| 1 | `0201` | copy 16 bytes to `0xFEBF2D08` | 2 |
| 2 | `0202` | copy 16 bytes to `0xFEBF2CF8`; set ready flag `0xFEBF2B16 = 1` | 0 |

Any other ordering returns NRC `0x22`. Initialization at `0x4A90` clears both
the sequence state and the asynchronous-write pending flag.

This resolves the comment in `secoc/extract_keys.py`:

> Write something to DID 203, not sure why but needed for state machine

`0203` is precisely the state-machine arm. Its five bytes are copied into the
handler's local request buffer but are never read, compared, stored, or passed
to a callback. Any five-byte value is equivalent in this firmware.

## 4. Consumers and persistence

### DID `0201`

`bootloader_did_direct_ram_copy @ 0x6D3A` writes the 16 request bytes to
`0xFEBF2D08` (`gp - 0x6AF8`). `payload_build_derive_key @ 0x7068` is its only
semantic consumer:

```text
derived_key = AES-128-ECB-ENC(PAYLOAD_BUILD_SECRET, DID_0201)
```

### DID `0202`

The second 16-byte buffer is `0xFEBF2CF8` (`gp - 0x6B08`). It is used as:

1. the AES-CBC IV in `payload_crypto_init_cbc_cmac @ 0x709A`;
2. the first CMAC block in `payload_cmac_verify_setup @ 0x7122`.

### Ready flag and RequestDownload

Successful `0202` sets `0xFEBF2B16` (`gp - 0x6CEA`) to 1. RequestDownload at
`0x5D68` checks that flag before initializing or accepting encrypted download
paths. Diagnostic initialization at `0x5086` clears it.

None of `0201`, `0202`, `0203`, their state bytes, or their ready flag maps to
DataFlash/NvM. They are volatile bootloader-session state.

## 5. What is absent

The complete table proves the bootloader has no readable/writable entries for:

- VIN (`F190`);
- ECU serial (`F18C`);
- spare-part/software numbers (`F187`–`F189`);
- boot/application data IDs (`F180`, `F182`);
- calibration/configuration or SecOC NvM objects.

This does not contradict field tools reading such identifiers before entering
the bootloader: those responses can come from another execution mode or related
variant. It does mean those meanings must not be projected onto handlers
`0x5FB8`/`0x4948` in this image.

## 6. Evidence grades

| Finding | Grade |
|---|---|
| exactly four descriptors and no hidden VIN/config entries in these handlers | **Definitive** |
| access bits, lengths, destination pointers, session/security checks | **Definitive** |
| `0203 -> 0201 -> 0202` state transitions and ignored `0203` data | **Definitive** |
| `0201` key derivation and `0202` CBC-IV/CMAC consumers | **Definitive** |
| all three proprietary DIDs are volatile, not DataFlash-backed | **Definitive** |
| `F181` exact response is `02 || 32*0x21` | **Definitive** |
| interpreting `0x02` as a two-record count | **Standard-based inference** |

`../tests/verify_did_model.py` independently checks the table, loop bounds,
policies, state transitions, RAM consumers, and response bytes from the raw
CodeFlash image. The optional `make verify-external` suite checks public-tool
ordering and the upstream UDS enum against commits pinned in
`../external-references.lock.json`.
