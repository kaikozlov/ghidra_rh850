# RH850 bootloader CAN / ISO-TP / UDS transport analysis

This document traces the complete diagnostic transport path in the correctly
mapped `8965B4512000` CodeFlash, from RSCFD hardware receive through CanIf,
CanTp, PduR, and Dcm/UDS, and back to RSCFD transmission.

All virtual addresses are CodeFlash addresses. `tp` is initialized to `0x869C`
at reset (`0x1F8`), so the configuration offsets used by the code can be
resolved directly into CodeFlash tables. `verify_can_transport.py` checks the
static data and instruction evidence without using Ghidra.

## Result

The bootloader uses standard 11-bit, classic 8-byte CAN frames:

| Purpose | CAN ID | Hardware path | Upper PDU |
|---|---:|---|---:|
| physical diagnostic request | **`0x7A1`** | channel 1 common FIFO 0 / HRH `0x10` | CanTp RxPduId 0 |
| functional diagnostic request | **`0x777`** | channel 1 common FIFO 1 / HRH `0x11` | CanTp RxPduId 1 |
| diagnostic response | **`0x7A9`** | channel 1 Tx object / HTH `0x13` | CanIf TxPduId 0 |

The `0x7A1 -> 0x7A9` pair used by every public extraction tool is therefore
confirmed by the firmware. `0x777` is an additional functional request address
not present in the local tooling. The functional CanTp channel rejects First
Frames and is consequently single-frame-only, as required for functional
ISO-TP addressing.

## Static configuration

### CanIf

The CanIf roots are stored relative to `tp = 0x869C`:

| Runtime read | CodeFlash word | Value |
|---|---:|---:|
| `tp+0x29C` | `0x8938` | Rx PDU table `0x8920` |
| `tp+0x2A0` | `0x893C` | Tx PDU table `0x8948` |
| `tp+0x2A4` | `0x8940` | HRH route table `0x898C` |
| `tp+0x2A8` | `0x8944` | one Tx PDU |

The 12-byte Rx entries at `0x8920` are:

```text
00 00 00 00  a1 07 00 00  00 00 00 00   upper PDU 0, CAN 0x7A1, standard ID
01 00 00 00  77 07 00 00  00 00 00 00   upper PDU 1, CAN 0x777, standard ID
```

The sole Tx entry at `0x8948` is:

```text
00 00 00 00  a9 07 00 00  00 00 13 00   PDU 0, CAN 0x7A9, standard ID, HTH 0x13
```

`CanIf_Transmit @ 0x4606` accepts only lengths below nine, looks up this Tx
entry, and calls `Can_Write @ 0x374E`. `CanIf_RxIndication @ 0x4678` software-
filters the received CAN ID and IDE flag against the Rx table, then invokes the
configured upper-layer callback.

### Driver channel/rule routing

The RSCFD roots are:

| Runtime read | CodeFlash word | Value |
|---|---:|---:|
| `tp+0x2D0` | `0x896C` | channel config `0x8978` |
| `tp+0x2D4` | `0x8970` | hardware-object config `0x8B0C` |
| `tp+0x2D8` | `0x8974` | rule pointer table `0x8918` |

There are three six-byte channel records at `0x8978`; only channel 1 has enable
bit `0x80`. The rule pointer table contains `0x8954` and `0x8960`, whose IDs are
`0x7A1` and `0x777` respectively.

The relevant eight-byte HRH/HTH routing entries are:

```text
HRH 0x10 @ 0x8A0C: descriptor 0x88F8, first Rx config 0, count 1
HRH 0x11 @ 0x8A14: descriptor 0x88F8, first Rx config 1, count 1
HTH 0x13 @ 0x8A24: descriptor 0x88F0, Tx config 0, count 1
```

Descriptor `0x88F8` points to the receive adapter at `0x1EEE`; descriptor
`0x88F0` points to the Tx-confirmation adapter at `0x1F0C`.

## RSCFD hardware access

The register naming and offsets match Renesas RSCAN-FD/RSCFD and the public
`rcar_canfd.c` definitions. The local dump shellcode independently uses the
same Tx registers.

### Receive: common FIFO

`rscfd_common_fifo_rx_callback @ 0x400A` receives an encoded hardware object:

```text
channel = (object & 0x7F) >> 4
fifo    = object & 0x0F
```

Thus HRH `0x10` is channel 1/common FIFO 0 and HRH `0x11` is channel 1/common
FIFO 1. It calls `rscfd_common_fifo_read @ 0x3F96`, then forwards the decoded
frame to `CanIf_RxIndication @ 0x4678`.

For `(channel, fifo)`, `0x3F96` accesses:

```text
CFSTS   = 0xFFD20178 + 0x0C*channel + 4*fifo
CFPCTR  = 0xFFD201D8 + 0x0C*channel + 4*fifo
CFID    = 0xFFD23400 + 0x180*channel + 0x80*fifo
CFPTR   = CFID + 0x04
CFFDCSTS= CFID + 0x08
CFDF0   = CFID + 0x0C
CFDF1   = CFID + 0x10
```

It tests CFSTS bit 3, acknowledges the FIFO status, extracts IDE from ID bit 31,
masks the ID to 29 bits, extracts DLC from CFPTR bits 31:28, copies two data
words, and writes `0xFF` to CFPCTR to advance the FIFO.

### Transmit: message buffer

`rscfd_tx_buffer_submit @ 0x36DE` checks `CFDTMSTSn`, then writes:

```text
CFDTMIDn     = 0xFFD24000 + 0x20*n
CFDTMPTRn    = CFDTMIDn + 0x04       (DLC in bits 31:28)
CFDTMFDCTRn  = CFDTMIDn + 0x08       (written zero: classic CAN frame)
CFDTMDF0n    = CFDTMIDn + 0x0C
CFDTMDF1n    = CFDTMIDn + 0x10
CFDTMSTSn    = 0xFFD202D0 + n
CFDTMCn      = 0xFFD20250 + n
```

It finally sets `CFDTMCn.TMTR` bit 0 at instruction `0x3744`. The configured
HTH `0x13` decodes to channel 1/object 3 and normalizes to message-buffer index
`n=16`, so the diagnostic response uses message RAM `0xFFD24200` and command
byte `0xFFD20260`.

No CAN-FD payload is used despite the FD-capable peripheral: CanIf rejects DLC
above 8, CanTp always constructs eight-byte frames, and CFDTMFDCTR is cleared.

## ISO-TP / CanTp

### Receive callback and PCI dispatch

The CanIf callback descriptor reaches:

```text
CanIf route descriptor 0x88F8
  -> cantp_rx_indication_callback @ 0x1EEE
  -> CanTp_RxIndication           @ 0x2B8A
```

`CanTp_RxIndication` accepts RxPduId 0 or 1 and DLC 2..8. It classifies the PCI
high nibble and dispatches exactly:

| PCI | Frame | Handler |
|---:|---|---:|
| `0x0` | Single Frame | `cantp_handle_single_frame @ 0x242A` |
| `0x1` | First Frame | `cantp_handle_first_frame @ 0x27D8` |
| `0x2` | Consecutive Frame | `cantp_handle_consecutive_frame @ 0x2946` |
| `0x3` | Flow Control | `cantp_handle_flow_control_frame @ 0x2AE4` |

Normal addressing is configured, so Single Frames carry at most seven payload
bytes. First Frames use the classic 12-bit length and require an eight-byte CAN
frame. The physical channel accepts First Frames; the functional channel's
configuration type causes `0x27D8` to reject them. Consecutive Frames validate
the sequence nibble modulo 16 before copying data.

The receiver emits all three standard FC states:

- CTS (`0x30`) at `0x1F98`, with configured block size/STmin;
- WAIT (`0x31`) at `0x24D0`;
- OVERFLOW (`0x32`) at `0x2636`.

The sender handles CTS/WAIT/OVERFLOW at `0x2AE4`, normalizes ISO-TP STmin, and
builds Consecutive Frames at `0x20E4`. The maximum transport SDU is the classic
12-bit limit, `0xFFF` bytes. Padding is zero and every transmitted CAN frame is
eight bytes.

### Transmit

`CanTp_Transmit @ 0x2D88` accepts TxPduId 0 and lengths `1..0xFFF`:

- length `<=7`: `cantp_send_single_frame @ 0x2CD4`;
- length `>7`: `cantp_send_first_frame @ 0x2C16`;
- subsequent data: `cantp_send_consecutive_frame @ 0x20E4`.

Tx confirmations return through descriptor `0x88F0`:

```text
cantp_tx_confirmation_callback @ 0x1F0C
  -> CanTp_TxConfirmation       @ 0x2F1C
```

This advances the First/Consecutive Frame state machine or reports completion to
the upper layer.

## PduR, Dcm, and UDS dispatch

The AUTOSAR-shaped upper callback chain is:

```text
CanTp
  -> PduR_CanTpStartOfReception @ 0x6B4C -> Dcm_StartOfReception @ 0x6374
  -> PduR_CanTpCopyRxData       @ 0x6B6C -> Dcm_CopyRxData       @ 0x6464
  -> PduR_CanTpRxIndication     @ 0x6B7A -> Dcm_TpRxIndication   @ 0x64B8
```

Dcm owns a 4 KiB request buffer. On successful reassembly,
`Dcm_TpRxIndication` calls `uds_service_dispatch @ 0x5222` with the received SID
and payload length. The dispatcher walks exactly 20 eight-byte records at
`tp+0x7B8 = 0x8E54` and indirectly calls the matching handler.

### Correction: service-table byte 1 is an addressing mask

The table format is:

```text
SID:u8, addressing_mask:u8, reserved:u16, handler:u32
```

It is not a session mask. Dcm's two Rx PDU records at `0x8F04/0x8F0C` assign
addressing class 1 to the physical `0x7A1` connection and class 0 to functional
`0x777`. The dispatcher evaluates:

```text
entry.addressing_mask & (1 << current_addressing_class)
```

Therefore `0x02` is physical-only, `0x01` functional-only, and `0x03` permits
both. Diagnostic-session/security restrictions are checked inside service
handlers, independently of this table.

Responses use:

```text
UDS handler
  -> Dcm_TransmitResponse @ 0x674A
  -> CanTp_Transmit       @ 0x2D88
  -> cantp_canif_transmit @ 0x1EC0
  -> CanIf_Transmit       @ 0x4606       (select CAN ID 0x7A9)
  -> Can_Write            @ 0x374E
  -> rscfd_tx_buffer_submit @ 0x36DE
```

The upper Tx callbacks are `PduR_CanTpCopyTxData @ 0x6B8A` ->
`Dcm_CopyTxData @ 0x66FA` and `PduR_CanTpTxConfirmation @ 0x6B98` ->
`Dcm_TpTxConfirmation @ 0x66BE`.

## End-to-end physical request

```text
CAN 0x7A1, channel 1 common FIFO 0
  -> rscfd_common_fifo_rx_callback 0x400A
  -> rscfd_common_fifo_read 0x3F96
  -> CanIf_RxIndication 0x4678
  -> callback adapter 0x1EEE
  -> CanTp_RxIndication 0x2B8A
  -> SF/FF/CF handler; PduR/Dcm reassembly
  -> Dcm_TpRxIndication 0x64B8
  -> uds_service_dispatch 0x5222
  -> service handler from table 0x8E54
  -> Dcm_TransmitResponse 0x674A
  -> CanTp / CanIf / Can_Write
  -> RSCFD CAN 0x7A9
```

## Evidence limits

This is static proof of the configured firmware path. It does not establish
which vehicle bus exposes channel 1 or whether gateway routing can alter IDs at
runtime. The local extraction tooling and captures independently corroborate
`0x7A1/0x7A9`. No local tool currently uses the firmware's `0x777` functional
path.
