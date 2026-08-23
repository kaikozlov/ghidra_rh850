# Toyota SecOC sender implementation and local frame signer

> **Scope:** pinned commaai/opendbc sender code and the classic-CAN receive
> profile verified in Sienna EPS `8965B4512000`
>
> **Document type:** external-source corroboration and local tooling
>
> **Status:** active
>
> **Evidence source:** mixed — firmware-static for the accepted wire format;
> external-source for opendbc's sender integration
>
> **Canonical artifacts:** `tools/toyota_secoc_signer.py`,
> `external-references.lock.json`
>
> **Verification:** `tests/verify_toyota_secoc_signer.py`; optional pinned-source
> check `tests/verify_external_corroboration.py`
>
> **Related:** [application receive chain](application-chain.md)

This report documents a public sender-side implementation without projecting
its complete vehicle architecture onto this EPS firmware. The Sienna image in
this repository implements SecOC **reception**. Comma's sender runs outside the
EPS, constructs authenticated command frames, and sends them to whichever ECU
owns each protected receive route.

The overlap is useful and exact for the classic-CAN format. It does not create a
stock EPS transmit path and it does not recover the protected AES key.

## 1. Pinned opendbc implementation

`external-references.lock.json` pins commaai/opendbc commit
`c9b31d21bc396e8958891e271936bdbdf1a6ca93`. The relevant source files are:

| File | Role |
|---|---|
| `opendbc/car/secoc.py` | Constructs ordinary protected frames and verifies the synchronization authenticator |
| `opendbc/car/toyota/carcontroller.py` | Tracks sender counters, consumes synchronization state, and invokes the signer |
| `opendbc/car/toyota/toyotacan.py` | Constructs the four authentic payload bytes before signing |
| `opendbc/dbc/generator/toyota/toyota_secoc_pt.dbc` | Binds message names to CAN IDs and trailer fields |
| `opendbc/car/toyota/values.py` | Marks the 2021–23 fourth-generation Sienna as a SecOC platform |

The public `add_mac` implementation authenticates:

```text
DataID_be16 || payload[0:4] || freshness48
```

where:

```text
freshness48 =
    trip_counter[16]
 || reset_counter[20]
 || message_counter[8]
 || reset_counter_low2[2]
 || 00b
```

It computes AES-CMAC and transmits the first 28 bits. The four-byte trailer is:

```text
message_counter_low2[2]
|| reset_counter_low2[2]
|| CMAC_msb28
```

That is the same packing independently recovered from this Sienna EPS at
`secoc_build_authenticated_input @ 0x8DB22` and
`secoc_pack_full_freshness @ 0x8EA4C`. The firmware-derived profile remains the
primary evidence; opendbc is external corroboration and a working sender
example.

### 1.1 Synchronization handling

The opendbc controller consumes CAN `0x00F` and checks its 28-bit authenticator
against:

```text
DataID_be16(0x000F) || trip_counter[16] || reset_counter[20] || 0000b
```

The synchronization frame itself is:

```text
trip_counter[16] || reset_counter[20] || CMAC_msb28
```

When the observed reset counter changes, the controller resets its independent
LKA, LTA, and acceleration message counters to zero, checks the synchronization
MAC, and then increments the corresponding counter after each protected send.
At the pinned commit, a synchronization mismatch is logged but does not gate
subsequent sends. The code consumes the synchronization source; it does not
originate `0x00F`.

A production sender must treat synchronization acceptance and counter changes as
state transitions, not just call a stateless CMAC helper. Separate protected
PDUs need separate message-counter state, and a stale or unauthenticated sync
must not silently replace the active sender epoch.

### 1.2 Direction and CAN-ID scope

The pinned controller signs three output streams:

| CAN ID | opendbc name | Intended protected send | Relation to this EPS image |
|---:|---|---|---|
| `0x2E4` | `STEERING_LKA` | steering torque command | Exact SecOC receive profile in Sienna EPS `8965B4512000` |
| `0x131` | `STEERING_LTA_2` | secondary LTA steering command | Exact SecOC receive profile in this EPS |
| `0x183` | `ACC_CONTROL_2` | acceleration command | Not an RX acceptance or SecOC record in this EPS; it is handled by a different receiving ECU |

The `0x183` sender path therefore does not contradict the EPS record census.
The public sender covers a vehicle-level control architecture, whereas the
firmware in this repository is one receiving ECU. Conversely, this EPS also
accepts protected `0x132`, `0x090`, and `0x0D7`; opendbc's controller does not
send those streams.

### 1.3 Full pinned classic-SecOC message family

The pinned Toyota SecOC DBC is broader than the three streams currently signed
by opendbc's controller. It defines the same classic 28-bit-authenticator trailer
on eight ordinary IDs:

| CAN ID | DBC name |
|---:|---|
| `0x116` | `GAS_PEDAL` |
| `0x131` | `STEERING_LTA_2` |
| `0x177` | `PCM_CRUISE_3` |
| `0x183` | `ACC_CONTROL_2` |
| `0x24D` | `PCM_CRUISE_4` |
| `0x283` | `PRE_COLLISION` |
| `0x2E4` | `STEERING_LKA` |
| `0x344` | `PRE_COLLISION_2` |

`0x00F` is the companion synchronization message. Every ordinary block carries
`AUTHENTICATOR`, `RESET_FLAG`, and `MSG_CNT_LOWER`; the common sender formula is
DataID-generic. This establishes a useful **known Toyota classic-SecOC profile**,
not a claim that every listed ID appears on every vehicle or belongs to the same
receiving ECU/key domain.

The machine-readable profile is `data/toyota_classic_secoc_profile.csv`, and the
community-extractor implications are canonical in
[community-dataflash-secoc.md](../../tooling/community-dataflash-secoc.md).

### 1.4 Key boundary

The public algorithm requires raw key bytes supplied by its integration. The
pinned source does not recover the key from the vehicle, provision ICU-S, or
load a production key by itself. Its base controller placeholder is
`b"00" * 16`, which is 32 ASCII bytes rather than a valid representation of the
Sienna's protected 16-byte slot-4 AES key. Opendbc's documentation likewise says
a valid key must be supplied to a development build or custom fork.

Accordingly, the public implementation answers **how to construct the frame
once the key and synchronized counters are known**. It does not answer how to
obtain the existing key.

## 2. Independent repository signer

`tools/toyota_secoc_signer.py` is an independent implementation written from the
firmware-derived format above; it is not a copy of opendbc's source. It exposes:

```python
pack_normal_freshness(trip_counter, reset_counter, message_counter)
build_normal_authenticated_input(can_id, payload, trip, reset, message)
sign_classic_frame(key, can_id, payload, trip, reset, message)
build_sync_authenticated_input(trip, reset, can_id=0x00F)
sign_sync_frame(key, trip, reset, can_id=0x00F)
```

The signer deliberately:

- requires a 16-byte AES-128 key;
- requires exactly four authentic payload bytes for an ordinary classic frame;
- bounds trip/reset/message counters to 16/20/8 bits;
- bounds IDs to standard 11-bit CAN;
- returns an exact eight-byte frame payload;
- performs no CAN transmission, key extraction, synchronization tracking, or
  control scheduling.

### 2.1 Command-line use

Pass the key through the environment to avoid placing it directly in the command
line:

```bash
export TOYOTA_SECOC_KEY=000102030405060708090a0b0c0d0e0f

uv run --locked python tools/toyota_secoc_signer.py sign \
  --can-id 0x2e4 \
  --payload 11223344 \
  --trip 0x1234 \
  --reset 0x56789 \
  --message 0xab

# 2E4#11223344D7BD232C
```

A synchronization-frame known answer for the same test key is:

```bash
uv run --locked python tools/toyota_secoc_signer.py sync \
  --trip 0x1234 \
  --reset 0x56789

# 00F#12345678957BC857
```

These are synthetic deterministic vectors, not captured vehicle material.
The tool prints candump-compatible text but does not send it.

## 3. Generic capture and DataFlash oracle

`tools/toyota_secoc_oracle.py` extends the independent implementation from frame
construction into offline verification. Unlike the current pinned community
DataFlash verifier, it does not assume steering IDs or Panda buses 0/2. It:

- tracks `0x00F` synchronization independently per observed bus;
- recognizes the full pinned classic-SecOC profile by default;
- verifies candidate keys separately for sync and every protected ID present;
- derives the 64 possible full message counters consistent with the transmitted
  two counter bits rather than brute-forcing unrelated counter values;
- scans every sliding 16-byte DataFlash window with a sync-CMAC prefilter; and
- reports only candidate offset/address hashes and match counts, not raw keys.

`tests/verify_toyota_secoc_oracle.py` includes a synthetic bus-1 capture with
`0x116` and `0x24D` specifically to prevent regression to the Sienna-only
`0x131/0x2E4/0x344` assumption.

## 4. Evidence and applicability boundaries

| Claim | Source | Confidence |
|---|---|---|
| This Sienna EPS accepts the documented classic authenticated-input and trailer format | firmware-static | verified by `verify_secoc_application.py` |
| Pinned opendbc independently implements the same ordinary and sync formulas | external-source | recovered from pinned source; hashes checked by optional external verification |
| The local signer reproduces fixed ordinary and sync known answers | generated-artifact | verified by `verify_toyota_secoc_signer.py` |
| The pinned DBC defines eight ordinary classic protected IDs (`0x116/0x131/0x177/0x183/0x24D/0x283/0x2E4/0x344`) with the same trailer field family | external-source | verified by optional pinned-source checks |
| The generic local oracle accepts arbitrary observed buses and verifies `0x116`/`0x24D` independently of steering IDs | generated-artifact | verified by `verify_toyota_secoc_oracle.py` |
| Pinned opendbc signs `0x2E4`, `0x131`, and `0x183` with separate counters | external-source | recovered from pinned controller/DBC source |
| `0x183` is a SecOC input to this exact EPS | firmware-static | disproved by the six-record census; it belongs to a different receiving ECU |
| The local signer recovers, exports, or proves possession of the live slot-4 key | — | disproved; a key is an explicit input |
| The same IDs/profile apply to every Toyota SecOC calibration | — | unsupported; verify each receiving firmware or dynamic route independently |

## References

- commaai/opendbc pinned source:
  <https://github.com/commaai/opendbc/tree/c9b31d21bc396e8958891e271936bdbdf1a6ca93>
- opendbc SecOC implementation:
  <https://github.com/commaai/opendbc/blob/c9b31d21bc396e8958891e271936bdbdf1a6ca93/opendbc/car/secoc.py>
- opendbc Toyota controller:
  <https://github.com/commaai/opendbc/blob/c9b31d21bc396e8958891e271936bdbdf1a6ca93/opendbc/car/toyota/carcontroller.py>

## 5. Application-resident command-5 signing proxy — RAM implementation

The software architecture is now implemented as a **RAM-only** application-
context proxy. It does not require a persistent CodeFlash hook and does not
claim that slot 4 permits command 5 on live Renesas ICU-S hardware. Installation
reuses the separately verified authenticated bootloader-RAM execution chain; once
resident, individual command-5 requests require no application SecurityAccess.

### 5.1 Use the stock serialized command-5 path

The safest statically justified entry is **not** `ICUSCMD` and not the low-level
engine `0x89630`. The generated crypto-test harness already proves the complete
calling convention:

```text
RAM proxy
  -> crypto_generate_driver_dispatch @ 0x88350
  -> driver record 0 @ 0x27F78
  -> icus_command5_mac_generate_adapter @ 0x87CCC
  -> shared ICU driver
  -> command 5
```

The stock mode-1 test at `0x68B42` remains useful as calling-convention proof,
but the resident proxy deliberately uses **record 0**, not diagnostic record 1.
Both records use adapter `0x87CCC` and asynchronous worker `0x87DD0`; record 0's
completion callback `0x88B5C` merely stores status to `FEBF13BD` and sets done
flag `FEBF13BC`, whereas record 1 callback `0x6926A` invokes the diagnostic
16-byte expected-result comparer. The lower prepare `0x87A94` accepts lengths
below `0x51` and converts the byte count to an ICU bit length, so the proxy
supplies the exact 12-byte classic or 36-byte FD authenticated input and fixes
**selector 4**. The lower engine accepts selectors `0..14`; no plaintext key
crosses MainPE. The distinction and CMAC-length proof are canonical in
[command5-oracle-assessment.md](command5-oracle-assessment.md).

For classic protected `0x2E4` or `0x131`, the command-5 message is the already
recovered 12-byte authenticated input:

```text
DataID_be16 || payload[0:4] || freshness48
```

The proxy keeps the full 16-byte CMAC result internally and uses its first 28
bits when constructing the four-byte Toyota SecOC trailer. This is an
engineering composition of already recovered primitives, not evidence that
slot 4 has been observed generating a MAC.

### 5.2 Arbitration and command-7 contention

Command 5 and the production SecOC **command-7 contention** path share the same
serialized ICU driver state (`FEBF1190/FEBF136C`) and interrupt machinery. A
proxy must therefore obey the stock adapter result rather than bypass
arbitration:

1. submit command 5 only through `crypto_generate_driver_dispatch`;
2. if the driver reports busy, defer the signing request;
3. never abort or replace a production command-7 verification merely to obtain
   a signing slot;
4. allow the stock asynchronous completion path to release the shared driver;
5. impose a bounded application-side queue so incoming signing requests cannot
   starve SecOC receive verification.

This makes command-7 receive verification the conservative priority. Actual
latency and whether the workload is schedulable at vehicle message cadence are
dynamic measurements.

### 5.3 RAM-resident foreground owner and XCP mailbox

A persistent CodeFlash hook is unnecessary. The already implemented ephemeral
runtime owns the normal TAUJ0 CH3 foreground loop after reproducing the stock
boot transition, `application_cpu_context_init @ 0x70524`, startup JARL sequence,
and final initializer. `command5_proxy.c` adds command-5 service after the normal
foreground calls, outside the TAUJ0 CH0 motor-current ISR.

The compiled Sienna proxy is **546 bytes** with zero relocations, so it fits the
verified 776-byte retained application-RWX interval `FEBF0000..FEBF0307` with
230 bytes headroom. Its tester mailbox is `FEBFFB80..FEBFFBFF`, a 128-byte
interval with zero canonical application direct xrefs, above the startup shadow
copy, and inside the unauthenticated COM-005 XCP read/write window. The mailbox
supports 80 input bytes and 16 output bytes. Request sequence is committed last;
response sequence is published only after record-0 completion has copied the
result.

`exploit/command5/ram_proxy.py` is the matching offline planner / bench-gated
live client. It fixes record 0 and selector 4, defaults to the configured
authenticated-domain lengths `7/12/36`, and uses existing XCP SET_MTA/DOWNLOAD
and SHORT_UPLOAD rather than inventing a new CAN protocol.

### 5.4 Freshness state for `0x2E4` and `0x131`

A stateful proxy cannot sign arbitrary payloads with a stateless CMAC call. It
must preserve the sender rules already pinned in §1:

- accept an authenticated `0x00F` synchronization epoch containing the current
  trip counter and reset counter;
- retain separate 8-bit message counters for `0x2E4` and `0x131`;
- reset each PDU counter when the accepted reset epoch changes;
- build the full six-byte freshness value before command 5;
- increment only the corresponding PDU counter after a signed frame is
  committed for transmission; and
- fail closed on stale/unverified synchronization instead of silently changing
  epochs.

The stock EPS receiver is not the source of `0x00F`, so a proxy that signs on
behalf of an external controller must obtain the same live synchronization
state that controller would otherwise consume.

### 5.5 Existing CAN Tx primitive

`application_canif_transmit @ 0x7EE0C` is a usable existing application Tx
primitive, but it resolves only configured generated PDU routes. The cleanest
non-COM demonstration route already present is the special wrapper `0x8206C`,
which forces generated class `0xF800`; that class resolves to **CAN `0x7F8`**.
It can carry a proxy response on an isolated bench without inventing a new
lower-driver interface.

`0x7F8` is **not an unused production ID**: it is the Tx half of the existing
XCP-shaped `0x7F7/0x7F8` channel analyzed in
[`../../communications/xcp-command-dispatch.md`](../../communications/xcp-command-dispatch.md).
Therefore production integration must either allocate and verify a new CanIf
route or separately audit a direct enqueue design; repurposing `0x7F8` is
justified only as a controlled bench transport with the stock special service
disabled/not in use.

Likewise, the stock CanIf table has no configured `0x2E4` or `0x131` Tx route.
An EPS-resident proxy that directly transmits those secured frames needs a new
route (or a separately reviewed lower-level enqueue record). A simpler proxy
returns the 16-byte CMAC to an external sender, which then constructs and sends
the protected frame.

### 5.6 Error handling and teardown

Normal **teardown** should remain inside the recovered asynchronous wrapper:
completion copies the result only on status zero, timeout/error finishes through
the no-copy path, and the shared driver returns to ready state. The proxy should
not call the `0x3F` abort path to preempt command 7. Its application state can be
cleared only after the configured completion callback has run or the stock
worker has completed its own timeout/recovery sequence.

A reversible experiment can disable the two foreground proxy hooks and clear
only proxy-owned queue/freshness RAM; it does not need to alter ICU key state.
Command 8 is explicitly outside the design. Dynamic acceptance criteria are:
slot-4 command-5 success, bounded latency without command-7 starvation, correct
CMAC against independently known frames, and clean recovery after forced busy /
timeout cases.

### Evidence boundary

The addresses, call shapes, scheduler placement, arbitration, and existing Tx
route are firmware-static. Slot-4 command-5 permission, timing, actual vehicle
freshness cadence, and safe production use of any Tx route are not established
statically.

<!-- knowledge-cross-references:begin -->
## Knowledge cross-references

Generated by `tools/build_knowledge_index.py` from the status ledgers;
do not edit this block by hand.

- Findings with this document as canonical home: [SECOC-022](../../reference/index.md#finding-secoc-022), [SECOC-032](../../reference/index.md#finding-secoc-032), [SECOC-041](../../reference/index.md#finding-secoc-041), [SECOC-070](../../reference/index.md#finding-secoc-070)
- Corrections with this document as canonical home: —
<!-- knowledge-cross-references:end -->
