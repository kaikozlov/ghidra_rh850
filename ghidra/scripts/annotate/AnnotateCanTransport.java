//@author kaikozlov
//@category Analysis
// Name/comment the verified RSCFD -> CanIf -> CanTp -> Dcm/UDS transport path.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateCanTransport extends GhidraScript {
    private void renameFunction(long addr, String name, String comment) throws Exception {
        Address a=toAddr(addr);
        Function f=currentProgram.getFunctionManager().getFunctionAt(a);
        if (f==null) throw new IllegalStateException("no function at "+a+" for "+name);
        f.setName(name,SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(String.format("function 0x%x -> %s",addr,name));
    }

    private void labelData(long addr, String name, String comment) throws Exception {
        Address a=toAddr(addr);
        SymbolTable st=currentProgram.getSymbolTable();
        Symbol s=st.getPrimarySymbol(a);
        if (s!=null) s.setName(name,SourceType.USER_DEFINED);
        else {
            s=st.createLabel(a,name,SourceType.USER_DEFINED);
            s.setPrimary();
        }
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(String.format("data 0x%x -> %s",addr,name));
    }

    private void comment(long addr, String text) {
        currentProgram.getListing().setComment(toAddr(addr),CodeUnit.EOL_COMMENT,text);
    }

    @Override
    public void run() throws Exception {
        labelData(0x23000L,"rscfd_register_address_table",
            "RSCFD SFR address table. Includes CFSTS 0xFFD20178, CFPCTR 0xFFD201D8, " +
            "CFDTMC 0xFFD20250, CFDTMSTS 0xFFD202D0, common-FIFO RAM 0xFFD23400, and Tx RAM 0xFFD24000.");
        labelData(0x88F0L,"cantp_tx_confirmation_callback_descriptor",
            "CanIf Tx-confirmation callback descriptor; callback pointer at +4 is 0x1F0C.");
        labelData(0x88F8L,"cantp_rx_indication_callback_descriptor",
            "CanIf Rx-indication callback descriptor; callback pointer at +4 is 0x1EEE.");
        labelData(0x8918L,"rscfd_rule_pointer_table",
            "Pointers to channel-1 receive rules: 0x8954 for standard ID 0x7A1 and 0x8960 for standard ID 0x777.");
        labelData(0x8920L,"canif_rx_pdu_config",
            "Two 12-byte CanIf Rx records: physical CAN 0x7A1 -> RxPduId 0; functional CAN 0x777 -> RxPduId 1.");
        labelData(0x8948L,"canif_tx_pdu_config",
            "Sole CanIf Tx record: TxPduId 0 -> standard CAN 0x7A9 through hardware Tx handle 0x13.");
        labelData(0x8954L,"rscfd_rule_can_7a1",
            "RSCFD channel-1 receive rule for standard physical diagnostic request ID 0x7A1.");
        labelData(0x8960L,"rscfd_rule_can_777",
            "RSCFD channel-1 receive rule for standard functional diagnostic request ID 0x777.");
        labelData(0x8978L,"rscfd_channel_config",
            "Three six-byte channel records. Only channel 1 has enable bit 0x80.");
        labelData(0x898CL,"canif_hardware_route_table",
            "CanIf HRH/HTH routes. HRH 0x10 -> Rx config 0, HRH 0x11 -> Rx config 1, HTH 0x13 -> Tx config 0.");
        labelData(0x8D50L,"cantp_rx_channel_config",
            "CanTp Rx channel 0 is physical/multiframe; channel 1 is functional/single-frame-only. Both use normal addressing.");
        labelData(0x8D80L,"cantp_tx_channel_config",
            "CanTp Tx channel for normal-addressed, zero-padded classic 8-byte ISO-TP responses through CanIf PDU 0.");
        labelData(0x8E54L,"uds_service_table",
            "20 entries x 8 bytes: SID, physical/functional addressing mask, reserved u16, handler pointer u32. Not a session mask.");
        labelData(0x8F04L,"dcm_rx_pdu_config",
            "Two Dcm connection records: CAN 0x7A1/addressing class 1 (physical), CAN 0x777/class 0 (functional).");

        renameFunction(0x1EC0L,"cantp_canif_transmit",
            "CanTp lower-layer transmit adapter; calls CanIf_Transmit at 0x4606.");
        renameFunction(0x1EEEL,"cantp_rx_indication_callback",
            "CanIf receive callback adapter; forwards RxPduId and frame PduInfo to CanTp_RxIndication at 0x2B8A.");
        renameFunction(0x1F0CL,"cantp_tx_confirmation_callback",
            "CanIf Tx-confirmation callback adapter; forwards confirmation to CanTp_TxConfirmation at 0x2F1C.");
        renameFunction(0x1F98L,"cantp_send_flow_control_cts",
            "Emit ISO-TP Flow Control CTS (PCI 0x30) with configured block size and STmin.");
        renameFunction(0x20E4L,"cantp_send_consecutive_frame",
            "Build next classic ISO-TP Consecutive Frame (PCI 0x20 | sequence nibble), zero-pad to eight bytes, and transmit.");
        renameFunction(0x242AL,"cantp_handle_single_frame",
            "Validate and deliver a normal-addressed ISO-TP Single Frame (maximum seven-byte payload).");
        renameFunction(0x24D0L,"cantp_send_flow_control_wait",
            "Emit ISO-TP Flow Control WAIT (PCI 0x31).");
        renameFunction(0x2636L,"cantp_send_flow_control_overflow",
            "Emit ISO-TP Flow Control OVERFLOW (PCI 0x32).");
        renameFunction(0x27D8L,"cantp_handle_first_frame",
            "Validate classic 12-bit ISO-TP First Frame, reject the functional channel, start upper-layer reception, and return FC.");
        renameFunction(0x2946L,"cantp_handle_consecutive_frame",
            "Validate ISO-TP sequence number modulo 16 and append Consecutive Frame data to the upper-layer SDU.");
        renameFunction(0x2AE4L,"cantp_handle_flow_control_frame",
            "Handle received ISO-TP FC CTS/WAIT/OVERFLOW and normalize STmin for segmented response transmission.");
        renameFunction(0x2B8AL,"CanTp_RxIndication",
            "CanTp receive entry. Accepts RxPduId 0/1 and DLC 2..8; dispatches PCI nibbles 0/1/2/3 to SF/FF/CF/FC handlers.");
        renameFunction(0x2C16L,"cantp_send_first_frame",
            "Build classic 12-bit ISO-TP First Frame and begin a segmented response.");
        renameFunction(0x2CD4L,"cantp_send_single_frame",
            "Build normal-addressed ISO-TP Single Frame, zero-pad to eight bytes, and transmit.");
        renameFunction(0x2D88L,"CanTp_Transmit",
            "CanTp transmit entry for TxPduId 0 and SDU lengths 1..0xFFF; selects Single Frame for <=7 bytes or First Frame otherwise.");
        renameFunction(0x2F1CL,"CanTp_TxConfirmation",
            "Advance ISO-TP response state after CanIf confirmation and notify the upper layer on completion/error.");

        renameFunction(0x36DEL,"rscfd_tx_buffer_submit",
            "Write ID, DLC, classic-frame control, and eight data bytes to RSCFD Tx message buffer n; then set CFDTMCn.TMTR at 0xFFD20250+n.");
        renameFunction(0x374EL,"Can_Write",
            "Decode configured hardware Tx handle, select RSCFD message-buffer index, and call rscfd_tx_buffer_submit.");
        renameFunction(0x3F96L,"rscfd_common_fifo_read",
            "Read one RSCFD channel/common-FIFO frame via CFSTS/CFID/CFPTR/CFDF, decode IDE/ID/DLC, and advance CFPCTR.");
        renameFunction(0x400AL,"rscfd_common_fifo_rx_callback",
            "Decode HRH into RSCFD channel/FIFO, read one frame, and call CanIf_RxIndication.");
        renameFunction(0x4606L,"CanIf_Transmit",
            "Validate classic CAN DLC <=8, select Tx PDU config (CAN 0x7A9/HTH 0x13), and call Can_Write.");
        renameFunction(0x4678L,"CanIf_RxIndication",
            "Resolve HRH route, software-filter standard CAN ID/IDE against 0x7A1 or 0x777 config, and invoke CanTp callback.");

        renameFunction(0x5222L,"uds_service_dispatch",
            "Walk the 20-entry table at 0x8E54, enforce its physical/functional addressing mask, and indirectly call the matching SID handler.");
        renameFunction(0x6374L,"Dcm_StartOfReception",
            "Dcm transport-buffer allocation/start callback for the selected physical or functional connection.");
        renameFunction(0x6464L,"Dcm_CopyRxData",
            "Copy reassembled CanTp request bytes into the Dcm 4 KiB request buffer.");
        renameFunction(0x64B8L,"Dcm_TpRxIndication",
            "On successful CanTp reassembly, dispatch the received UDS SID/payload through uds_service_dispatch at 0x5222.");
        renameFunction(0x66BEL,"Dcm_TpTxConfirmation",
            "Dcm completion callback for a transmitted diagnostic response.");
        renameFunction(0x66FAL,"Dcm_CopyTxData",
            "Supply response bytes from the Dcm buffer to CanTp during segmented transmission.");
        renameFunction(0x674AL,"Dcm_TransmitResponse",
            "Submit the prepared UDS response to CanTp_Transmit, which returns it on standard CAN ID 0x7A9.");
        renameFunction(0x6B4CL,"PduR_CanTpStartOfReception",
            "PduR adapter forwarding CanTp StartOfReception to Dcm_StartOfReception.");
        renameFunction(0x6B6CL,"PduR_CanTpCopyRxData",
            "PduR adapter forwarding CanTp CopyRxData to Dcm_CopyRxData.");
        renameFunction(0x6B7AL,"PduR_CanTpRxIndication",
            "PduR adapter forwarding completed CanTp reception to Dcm_TpRxIndication.");
        renameFunction(0x6B8AL,"PduR_CanTpCopyTxData",
            "PduR adapter forwarding CanTp CopyTxData to Dcm_CopyTxData.");
        renameFunction(0x6B98L,"PduR_CanTpTxConfirmation",
            "PduR adapter forwarding CanTp TxConfirmation to Dcm_TpTxConfirmation.");

        comment(0x3744L,"Set CFDTMCn.TMTR bit 0; CFDTMC base is 0xFFD20250.");
        comment(0x4030L,"Read one RSCFD common-FIFO frame.");
        comment(0x4040L,"Forward decoded frame to CanIf_RxIndication.");
        comment(0x64FCL,"Dispatch successfully reassembled UDS request.");
        comment(0x5250L,"Indirect call to UDS handler selected from table 0x8E54.");
    }
}
