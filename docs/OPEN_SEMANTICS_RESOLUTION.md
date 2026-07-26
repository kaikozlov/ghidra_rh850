# Resolution of five previously open application semantics

This note closes five bounded questions left by the architecture, diagnostics,
and DataFlash reports. All addresses are CodeFlash virtual addresses unless a
full RAM/DataFlash address is shown. The conclusions use firmware evidence names,
not invented Toyota/Denso identifiers.

## 1. `0xFEBFC81F`: system-transition phase snapshot

`application_input_snapshot_update @ 0xBCB3A` performs the exact copy:

```text
live source  GP-0x65C = 0xFEBEB1A4
snapshot     GP+0x301F = 0xFEBFC81F
```

The live byte is initialized and advanced by `0xB28AC/0xB2912`. This generated
state machine coordinates system modes `0x300/0x400/0x500` and event `0x23`; the
recovered phase values are `0`, `0x11`, and `0x22`. Adjacent flags use `0x5A`,
but the copied phase byte does not. The programming-handoff prerequisite at
`0x4C960` rejects snapshot phase `0x11`.

**Resolution:** this is a system-transition phase snapshot, not a Dcm-produced
"programming status" byte. Exact OEM names for the three phase values remain
unavailable.

## 2. Secondary application diagnostic configuration

The directory at `0x25DE0` selects three service groups through global record
indexes:

| Key | Index list | CAN context | Effective SIDs |
|---:|---|---|---|
| 2 | `0x25DF8`, `0..16` | physical `0x7A1 -> 0x7A9` | `10,11,14,19,22,23,27,28,2E,31,34,36,37,3E,85,AB,BA` |
| 3 | `0x25DC0`, `17,2,7,9,13,14` | functional `0x777 -> 0x7A9` | `10,14,28,31,3E,85` |
| 4 | `0x25E1C`, `18..22` | secondary physical `0x7A0 -> 0x7A8` | `10,19,22,3E,AB` |

Six extra service records begin at `0x25FC8`. The functional context uses one of
them and reuses five primary records; the secondary physical context uses the
other five. The block is therefore not one standalone five-service linear table.

**Resolution:** `0x7A0 -> 0x7A8` is a real, restricted secondary physical
diagnostic endpoint. Its intended manufacturing/tester role and proprietary SID
`0xAB` meaning remain unknown.

## 3. EIINT channels 292/293

The application INTBP table points channels 292/293 to wrappers `0x650AC` and
`0x650EE`. They dispatch through byte-identical adapters `0x87610/0x87636`, which:

- read a callback and its complement at GP `+0x5994/+0x5998`;
- call it only when the complement guard is valid;
- set driver error byte GP `+0x5991` otherwise.

Driver initialization at `0x8735E` initializes those fields and calls `0x8913C`.
That routine masks/unmasks `EIC292 @ 0xFFFFB248` and `EIC293 @ 0xFFFFB24A`
together. The same driver family accesses the `0xFFC5D000` ICU-S command/status
bank used by the proven CMAC path.

**Resolution:** both are active ICU-S cryptographic-driver interrupt callback
paths despite being labelled reserved in the generic P1M-E source table. Static
analysis does not distinguish which channel is completion versus error.

## 4. DataFlash pages 0–255

No configured storage record, owner descriptor, or credible runtime object
reference reaches `0xFF200000..0xFF203FFF`. The lower half has no valid configured
record envelope. Its 4,096 words are 2,250 all-zero, 1,306 all-one, and 540 mixed.
Renesas specifies undefined direct readback for erased DataFlash words, and the
observed page/word patterns are erased-compatible rather than a recoverable
record population.

**Resolution:** the defensible present classification is currently
unallocated/erased-compatible raw capacity. The dump cannot distinguish never
used from factory-tested, previously raw-used then erased, or retired history.
Claims of a recoverable prior object store are unsupported.

## 5. Checkpoint payload fields

The checkpoint table at `0x2AF2C` has 32 descriptors, 24 enabled. Every enabled
object was traced to its direct object-indexed producer or bounded as lacking one.
The complete machine-readable result is
[`data/checkpoint_payload_map.csv`](../data/checkpoint_payload_map.csv), generated
by [`tools/generate_checkpoint_payload_map.py`](../tools/generate_checkpoint_payload_map.py).

The defensible naming families are:

- monitor aggregate/banks and event-counter groups: objects `0..4`, `10`;
- multi-channel numeric/validity state with exact widths but unknown physical
  units: objects `5..9`, `11`, `13`, `15`;
- incident/condition/event histories: objects `12`, `14`, `17..23`;
- persistent one-byte countdown: object `24`;
- enabled 72-byte configured orphan with no static object-specific writer:
  object `27`.

Directly recoverable schemas include object 4's `u16[18] + u16[10]` counters,
object 5's two signed 16-bit values with a `32000` sentinel, object 12's
dual incident entries, object 14's 12 trigger counters plus three condition
entries, and object 24's countdown. Whole-buffer producers remain `u8[length]`
where no consumer establishes field boundaries.

**Resolution:** structural/evidence names are now complete; OEM physical names
are intentionally retained as unknown where the firmware does not establish
them. The generic `secoc_nvm_*` storage implementation does not make these
payloads MAC or key objects.
