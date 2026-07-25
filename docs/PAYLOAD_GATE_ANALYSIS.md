# Bootloader payload authentication and execution path

This note traces the complete firmware-side path used by the public RH850/P1M-E
payload toolchain: UDS download, AES-CBC decryption, CRC + CMAC authentication,
and the `0xFF00` execution trigger. Addresses are CodeFlash virtual addresses.

`../tests/verify_payload_gate.py` independently checks the static tables,
callback instructions, and the two unique encrypted payload fixtures represented
by four pinned public upstream copies. Fixture provenance and upstream hashes are
in `../external-references.lock.json`; `make verify-external` compares them to
optional external checkouts.

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
`0xFF00`. Both `0x10F0` and `0xFF00` accept only StartRoutine and require a
10-byte option record (`45 00 || address_be32 || length_be32`).

## 2. RequestDownload (`SID 0x34`, handler `0x5D68`)

The request used by all available tooling is:

```text
34 01 46 01 00 FEBF0000 00001000
```

The handler requires programming session + unlocked SecurityAccess, validates
the range against `0x8DA0`, records the current destination and remaining byte
count, and initializes payload crypto when enabled:

```text
payload_build_derive_key       0x7068
payload_crypto_initialize      0x70D4
```

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
