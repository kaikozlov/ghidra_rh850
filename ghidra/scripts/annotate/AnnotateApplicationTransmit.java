//@author kaikozlov
//@category Analysis
// Name and document the verified application COM/PduR/CanIf/RSCFD transmit map.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateApplicationTransmit extends GhidraScript {
    private void renameFunction(long addr, String name, String comment) throws Exception {
        Address a = toAddr(addr);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) throw new IllegalStateException("no function at " + a + " for " + name);
        f.setName(name, SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, comment);
        println(String.format("function 0x%x -> %s", addr, name));
    }

    private void labelData(long addr, String name, String comment) throws Exception {
        Address a = toAddr(addr);
        SymbolTable symbols = currentProgram.getSymbolTable();
        Symbol symbol = symbols.getPrimarySymbol(a);
        if (symbol != null) symbol.setName(name, SourceType.USER_DEFINED);
        else {
            symbol = symbols.createLabel(a, name, SourceType.USER_DEFINED);
            symbol.setPrimary();
        }
        currentProgram.getListing().setComment(a, CodeUnit.PLATE_COMMENT, comment);
        println(String.format("data 0x%x -> %s", addr, name));
    }

    private void eol(long addr, String comment) {
        currentProgram.getListing().setComment(toAddr(addr), CodeUnit.EOL_COMMENT, comment);
    }

    @Override
    public void run() throws Exception {
        labelData(0x21a68L, "application_pdur_tx_class_counts",
            "Six generated route-class counts: 6 COM, 0, 4 transport, 0, 0, 1 special.");
        labelData(0x21f78L, "application_com_canif_tx_pdu_table",
            "Six 8-byte CanIf Tx records: standard IDs 260,262,351,394,4A3,4C8 for generated source PDUs 0..5.");
        labelData(0x21fa8L, "application_diagnostic_canif_tx_pdu_table",
            "Four 8-byte class-2 CanIf Tx records: 7A9,7A9,7A8,7A8 for generated source PDUs 0800..0803.");
        labelData(0x21f68L, "application_special_canif_tx_pdu_table",
            "One active class-5 CanIf Tx record: generated source PDU F800 to standard CAN 7F8. Adjacent 7F7 is outside count one.");
        labelData(0x221dcL, "application_com_initial_pdu_data",
            "Initial 473-byte COM data image. First 39 bytes initialize the six Tx buffers.");
        labelData(0x223b8L, "application_com_signal_property_table",
            "One-byte generated property/type values for 300 COM signals.");
        labelData(0x224e4L, "application_com_signal_to_pdu_map",
            "300 little-endian COM PDU indexes. Signals 0..57 map to the six Tx PDUs; signals 58..299 map to 47 Rx PDUs.");
        labelData(0x2273cL, "application_com_pdu_config_table",
            "53 8-byte COM PDU descriptors. Entries 0..5 are Tx with cycle counts 4,8,200,60,100,196 and lengths 8,8,4,3,8,8; 6..52 are Rx.");
        labelData(0x228e4L, "application_com_pdu_buffer_offsets",
            "COM data-buffer offsets. Tx entries are 0,8,16,20,23,31 and select contiguous RAM buffers at FEBE4A49.");

        renameFunction(0x4bceeL, "application_pack_can_260",
            "Pack COM signals 0..8 into the 8-byte CAN 0x260 buffer; configured signal 9 occupies the unresolved final byte.");
        renameFunction(0x4be24L, "application_pack_can_262",
            "Pack COM signals 10..36 into the 8-byte CAN 0x262 buffer; configured signal 37 occupies the unresolved final byte.");
        renameFunction(0x4c25cL, "application_pack_can_351",
            "Pack COM signals 38 and 39 into byte 2 of the 4-byte CAN 0x351 buffer.");
        renameFunction(0x4c158L, "application_pack_can_394",
            "Pack COM signals 40..45 across the 3-byte CAN 0x394 buffer.");
        renameFunction(0x4bb1eL, "application_pack_can_4a3",
            "Pack COM signals 46..53 as eight direct bytes for CAN 0x4A3.");
        renameFunction(0x4bc54L, "application_pack_can_4c8",
            "Pack constants 09, bit zero, and BE16 zero as signals 54..56 for CAN 0x4C8; configured signal 57 remains runtime-unresolved.");

        renameFunction(0x7c232L, "application_com_pack_big_endian_signal",
            "Pack an unsigned generated COM signal into a big-endian bit field in the selected I-PDU RAM buffer.");
        renameFunction(0x7c0f0L, "application_com_send_signal",
            "Update a generated COM signal in its I-PDU buffer and activate transmission state when the value/property requires it.");
        renameFunction(0x7d04eL, "application_com_tx_main",
            "COM main function: update cyclic timers and submit pending Tx I-PDUs from the first six COM PDU descriptors.");
        renameFunction(0x7ce28L, "application_com_transmit_pending_pdu",
            "Resolve a pending COM Tx PDU, select its RAM buffer/length, and submit it through the PduR transmit adapter.");
        renameFunction(0x80992L, "application_pdur_com_transmit",
            "COM-to-PduR transmit adapter. Combines the generated base route with COM PDU 0..5 and invokes the transmit router.");
        renameFunction(0x809c6L, "application_pdu_transmit_router",
            "Configuration-driven transmit router selecting the upper route and dispatch table for a generated source PDU.");
        renameFunction(0x7ee0cL, "application_canif_transmit",
            "Resolve an active 8-byte CanIf Tx record, attach CAN ID/controller/confirmation route, and enqueue the frame.");
        renameFunction(0x7ec5aL, "application_canif_enqueue_tx",
            "Copy a classic or CAN-FD frame into the controller software Tx queue and schedule lower-driver submission.");
        renameFunction(0x7e5f2L, "application_canif_get_tx_can_id",
            "Return the CAN-ID word from the generated CanIf Tx record selected by class and PDU index.");
        renameFunction(0x7f070L, "application_can_queue_to_rscfd",
            "Drain one queued CanIf frame into the configured RSCFD hardware transmit route.");
        renameFunction(0x84022L, "application_rscfd_write_dispatch",
            "Select classic or CAN-FD RSCFD write logic for the configured hardware transmit handle.");
        renameFunction(0x842baL, "application_rscfd_write_classic",
            "Copy one standard classic-CAN frame into an RSCFD transmit resource for channel 1.");
        renameFunction(0x84710L, "application_rscfd_tx_confirmation_dispatch",
            "RSCFD channel confirmation dispatcher; releases completed hardware/software Tx resources.");
        renameFunction(0x7f002L, "application_canif_tx_confirmation",
            "Resolve a completed generated CanIf PDU and dispatch its upper-layer confirmation route.");
        renameFunction(0x7e30cL, "application_pdur_tx_confirmation_router",
            "Configuration-driven PduR transmit-confirmation callback and route-state release.");

        eol(0x4bd3cL, "Pack CAN 0x260 signal 0; subsequent calls cover generated signals 1..8.");
        eol(0x4bee4L, "First CAN 0x262 COM-signal pack call; this function emits 27 configured fields.");
        eol(0x4c284L, "Pack CAN 0x351 signal 38 at byte 2 bits 7..5.");
        eol(0x4c198L, "Pack CAN 0x394 signal 40 at byte 0 bits 6..4.");
        eol(0x4bb6aL, "Pack the first of eight direct CAN 0x4A3 bytes.");
        eol(0x4bc7aL, "Pack CAN 0x4C8 byte 0 with constant 0x09.");
    }
}
