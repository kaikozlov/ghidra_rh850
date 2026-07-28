# Renesas Flash Programmer RV40F interface

> **Scope:** Renesas Flash Programmer V3.24.00 `macos-arm64`
>
> **Document type:** external-source reverse engineering
>
> **Status:** active
>
> **Evidence source:** external-source
>
> **Evidence profile:** recovered/bounded — each claim below is scoped to the
> pinned host library, not the Sienna firmware or a live R7F701381
>
> **Canonical artifacts:** `renesas-rfp.lock.json`,
> `data/renesas_rfp_rv40f_icu_commands.csv`
>
> **Verification:** `tests/verify_renesas_rfp.py` (`make verify-rfp`)
>
> **Related:** [workflow](../WORKFLOW.md),
> [SecOC key lifecycle](../security/secoc/key-storage-and-lifecycle.md)

## Executive conclusion

The Renesas Flash Programmer (RFP) package is a useful primary source for the
host side of the RH850 serial-programming protocol. Its `libRFP.dylib` retains
C++ symbols for a large older/common `BootRV40F` implementation and a separate
`BootRH850Gen2` implementation. The former contains connection, frequency,
baud-rate, signature, memory-area, read, write, erase, checksum, authentication,
option-byte, protection, and ICU-S-related operations.

The ICU-S functions recovered so far configure and validate chip security
state. They do **not** expose a demonstrated SecOC key-slot provisioning API:

- `SetICUSOptionByte` carries four bytes;
- `GetICUSOptionByte` returns four bytes;
- `ValidateICU_S` has no payload;
- `CheckICUMode` probes one-byte mode values;
- `SetICUM` serializes a structured legacy extended-option record through two
  commands.

The files shipped alongside RFP do not fill that gap. All 68 images under
`Firmwares/` identify themselves as SEGGER J-Link/J-Trace/Flasher probe
firmware. Explicit target-resident resources are confined to DA and RA
families. The only packaged secure-provisioning image is an RA6B1 artifact
handled by `BootRATZ_B`, and there is no corresponding RH850 resource or
`BootRV40F::DownloadImage` path.

In particular, `SetICUM` is not shaped as `slot || AES-128 key`. No named
`BootRV40F` key-load or key-update function is present in the retained symbol
table. That is a bounded negative result: an unnamed primitive, target-resident
provisioning payload, manufacturing-only program, or Toyota/Denso service can
still exist.

Nothing in this report proves that an R7F701381/P1M-E accepts every recovered
command. That requires a live signature/capability query or a captured RFP
session.

## 1. Pinned source

The analyzed distribution identifies itself as:

```text
Renesas Flash Programmer CLI V1.17
module V3.24.00.000
package V3.24.00
release 1 July 2026
platform macos-arm64
```

The analyzed package snapshot is stored under `Renesas/` and exact hashes,
sizes, function virtual addresses, function-body hashes, and embedded-data
prefixes are pinned in `renesas-rfp.lock.json`. The default path is:

```text
Renesas/renesas_flash_programmer_macos-arm64/
```

Run:

```bash
make verify-rfp
```

to verify the distribution against the lock. Ordinary `make verify` validates
the committed command model, wire fixtures, package inventory, and analyzed
function bodies.

## 2. Device-family split

`Devices.xml` defines three distinct user-facing RH850 entries:

| Entry | Mode entry | Interfaces |
|---|---|---|
| `RH850` | `MODEENTRY_DEFAULT` | UART1/UART2 through E2/E2 Lite/E1/E20; UART2 through COM |
| `RH850/E2x` | `MODEENTRY_RH850_E2` | CSI/UART2 |
| `RH850/U2x` | `MODEENTRY_RH850_E2` | CSI/UART2 |

The host library separately retains:

```text
BootRV40F::Inquiry
BootRV40F::SetFrequency
BootRV40F::SetBaudrate
BootRV40F::GetSignature
BootRV40F::Read / ReadEX
BootRV40F::Erase / AreaErase
BootRV40F::WriteCommand / WriteData
BootRV40F::CheckCRC / CheckSum
BootRV40F::CheckIDAuth / CheckPassword
BootRV40F option, protection, and ICU-S families
```

and:

```text
BootRH850Gen2::Inquiry
BootRH850Gen2::SetFrequency
BootRH850Gen2::SetBaudrate
BootRH850Gen2::GetSignature
BootRH850Gen2 read/write/erase/checksum/area operations
```

The task names and family split make `BootRV40F` the leading host protocol for
the generic/older RH850 entry. Applying it specifically to the P1M-E remains
**bounded** until the device response selects or exhibits this path.

### Shipped firmware and target-resource triage

The package contains three different classes of executable material. They must
not be conflated:

| Location | Count / example | Recovered role | P1M-E relevance |
|---|---:|---|---|
| `Firmwares/*.bin` | 68 | SEGGER J-Link/J-Trace/Flasher **probe** firmware | no RH850 target payload found |
| `Resources/DA*`, `Resources/RA6W1` | target boot/programming images | DA/RA target-resident loaders | different MCU families |
| `Resources/ProvisioningSW/RA6B1/provsw_sec_enc.bin` | one `imag` container | encrypted or encrypted+signed RA6B1 provisioning software | architectural analogy only |

The first printable identification in every `Firmwares/*.bin` names J-Link,
J-Trace, or Flasher hardware. Two large S-records embedded in `libRFP.dylib`,
`SFD_BfwE20RFP_s @ 0x11D124` and `SFD_BfwE2LRFP_s @ 0x13F7E0`, are also not
target payloads. `Driver_E1E2::_UpdateEmulator @ 0x37748` selects them according
to attached E1/E2/E2 Lite hardware and programs them into the emulator.

The embedded symbol `FlashLibrary::SFD_RV40F_CM4_hex @ 0x2F3E12` is another
misleading name. Its bytes are ARM Thumb code, its suffix is `CM4`, and it is
selected by `UtilitySWD_A::GetFLMFileName`/`LoadFLM`. It is an SWD Cortex-M4
flash algorithm, not V850/RH850 code and not an ICU-S agent.

Conversely, when this RFP build needs a secure target-side provisioning program,
it is explicit: `UtilityRA_B::SetupProvisioningSW @ 0xB1984` loads the RA6B1
resource and `BootRATZ_B::DownloadImage @ 0x135A8` transfers it. The retained
RV40F symbol/task census has no analogous provisioning-image setup or download
function, and the resource tree has no RH850/RV40F/P1M/ICU-named payload.

This is a **bounded negative result**, not proof that no RH850 manufacturing
agent exists. Such an agent may be supplied separately by Renesas or
Toyota/Denso, encrypted under an opaque name, embedded without a retained
symbol, or implemented by target mask ROM.

## 3. RV40F framing

`ProcessCommand @ libRFP 0x19C94` constructs the common request:

```text
01 || length_be16 || command || payload || checksum || 03
```

where:

```text
length   = 1 + payload_length
checksum = -sum(length_be16 || command || payload) mod 256
```

`SendRecvFrame @ libRFP 0x1B37C` requires the received frame to begin with
`0x81`, parses its big-endian length, reads the remaining bytes, and validates
the packet against the command byte.

Examples pinned by `verify_renesas_rfp.py`:

```text
ValidateICU_S:
01 00 01 70 8F 03

CheckICUMode(FF):
01 00 02 71 FF 8E 03

CheckICUMode(00):
01 00 02 71 00 8D 03

SetICUSOptionByte(11 22 33 44):
01 00 05 6E 11 22 33 44 E3 03

SetICUM auxiliary(01 02 03 04):
01 00 05 75 01 02 03 04 7C 03
```

These are host-library frames, not Toyota UDS messages.

## 4. ICU-related command family

The machine-readable census is
`data/renesas_rfp_rv40f_icu_commands.csv`.

| Command | Host function | Recovered request |
|---:|---|---|
| `0x6E` | `SetICUSOptionByte @ 0x1C4DC` | four option bytes |
| `0x6F` | `GetICUSOptionByte @ 0x1CA90` | no payload; four-byte result |
| `0x70` | `ValidateICU_S @ 0x1D5E8` | no payload |
| `0x71` | `CheckICUMode @ 0x1D688` | one mode byte |
| `0x74` | `SetICUM @ 0x1C5AC` | 15-byte main record |
| `0x75` | `SetICUM @ 0x1C5AC` | four-byte auxiliary field |

### `SetICUM` structure

`SetOptionByteEx @ 0x1C164` calls `SetICUM` only in its legacy format branch.
The caller obtains this input as option type `2`, the host's extended-option
record.

`SetICUM` consumes the record as follows:

```text
command 0x75 payload:
    input[0x10:0x14]                        # four bytes

command 0x74 payload:
    FF if input[3] > EF else 00            # one flag-like byte
    input[0x08:0x0C]                       # four bytes
    input[0x0C:0x10]                       # four bytes
    input[0x04:0x08]                       # four bytes
    FF if input[2] > EF else 00            # one flag-like byte
    FF if input[1] > EF else 00            # one flag-like byte
```

This is a structured option/configuration record. It does not transport an
arbitrary contiguous 16-byte AES key, and it carries no recovered slot selector.
The exact OEM meanings of its three flags and four 32-bit fields remain unknown.

### ICU-S enable/validation is separate

RFP's CLI documentation exposes `-fo flags icus` as “Enable ICU-S.” The RH850
option-writing task represents that request as security flag `0x00010000`. If
selected, `Task_WriteOption_RV40F::_WriteOptionRH850 @ 0xC152C` invokes the
payload-free `ValidateICU_S` command, unless the connection setup already
recorded the target in the relevant ICU mode.

During setup, `Task_SetupBaudrate_RV40F::Run @ 0xBEF4C` calls `CheckICUMode` only
when the target capability record advertises feature `0x1106`. `CheckICUMode`
tries mode `0xFF`; on one particular target error it retries with `0x00` and
records which form succeeded.

`SetICUSOptionByte` is an exported four-byte primitive, but the Ghidra
cross-reference census finds no internal code caller in `libRFP`; only its
external entry and symbol/data references remain. The standard high-level
RH850 option task recovered above does not call it. This makes command `0x70`,
not command `0x6E`, the concrete lead for the documented ICU-S enable
transition in this build.

This supports a chip-lifecycle/configuration interpretation. It does not prove:

- that `ValidateICU_S` loads a key;
- that the four ICU-S option bytes encode any key-slot contents;
- that `SetICUM` addresses protected key slot 4;
- that standard RFP can export or replace a SecOC key;
- that Toyota dealer rekeying uses the serial boot protocol.

## 5. What RFP can contribute

The retained RV40F implementation can guide a reproducible acquisition client
for:

1. boot-mode entry and synchronization;
2. oscillator/frequency and baud-rate negotiation;
3. device signature and capability discovery;
4. ID-code authentication;
5. CodeFlash/DataFlash area discovery;
6. blank check, read, erase, program, verify, and checksum;
7. option-byte and serial-programming protection state;
8. ICU-S enable/mode configuration.

The shipped payload triage also provides a useful pattern for future artifacts:
a real RFP-managed secure provisioning agent should have a family-specific
resource, a setup routine, and a target-image download path comparable to the
RA6B1 chain. None is present for RV40F in this package.

The next useful static pass is a complete RV40F command census, followed by the
mode-entry/connection task, the signature capability-field parser, and the
source of feature key `0x1106`.

## 6. What remains unproven

- Whether the R7F701381/P1M-E selects the RV40F path.
- Which ICU commands the P1M-E mask ROM advertises and permits.
- The field meanings in the legacy `SetICUM` record.
- The exact state transition caused by `ValidateICU_S`, including whether it is
  irreversible and what preconditions it checks.
- Whether any standard RFP path provisions protected AES slots.
- How Toyota/Denso dealer tooling replaces the per-vehicle SecOC key.
- Whether provisioning is a ROM command, RAM-resident manufacturing payload,
  secure key-update package, or application/bootloader diagnostic service.

These questions must not be collapsed into a claim that command `0x74`,
`0x75`, or `SetICUM` writes SecOC slot 4.
