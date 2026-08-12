//@author kaikozlov
//@category Analysis
// Name and document the verified application COM receive map.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateApplicationReceive extends GhidraScript {
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
        labelData(0x22018L, "application_normal_rx_can_ids",
            "47 eight-byte normal Rx descriptors: software CAN ID (with optional 0x40000000 FD marker) and length.");
        labelData(0x231a0L, "application_can1_acceptance_rules",
            "51 sixteen-byte RSCAN acceptance rules plus 0xFFFFFFFF terminator. Rules 0..46 are the 47 normal Rx IDs; 47..50 are 7A1/777/7A0/7F7.");
        labelData(0x2273cL, "application_com_pdu_config_table",
            "53 8-byte COM PDU descriptors. Entries 6..52 are Rx with flags 0x0C; cycle field is raw timeout/period ticks.");
        labelData(0x228e4L, "application_com_pdu_buffer_offsets",
            "COM data-buffer offsets into FEBE4A49. Rx entries begin at offset 39.");
        labelData(0x224e4L, "application_com_signal_to_pdu_map",
            "300 little-endian COM PDU indexes. Signals 58..299 map to the 47 Rx PDUs 6..52.");
        labelData(0x223b8L, "application_com_signal_property_table",
            "One-byte generated property/type values for 300 COM signals. Rx uses classes 0/3/4.");
        labelData(0x25902L, "application_com_opaque_rx_signal_ids",
            "Fourteen opaque Rx signal IDs 87..100 (property class 4) copied as whole PDU payloads.");
        labelData(0x2591eL, "application_com_opaque_rx_buffer_offsets",
            "Matching COM buffer offsets for opaque Rx signals 87..100.");
        labelData(0xfebe4a49L, "application_com_pdu_data_ram",
            "COM I-PDU data image base. Tx occupies the first 39 bytes; Rx follows using buffer offsets.");
        labelData(0xfebe52ccL, "application_com_rx_validity_bytes",
            "Per-COM-PDU validity bytes. Initialized to 0x5A; cleared by RxIndication on receive.");
        labelData(0xfebe532cL, "application_com_rx_update_counters",
            "Per-COM-PDU update generation counters incremented by RxIndication and watched by generated unpackers.");

        renameFunction(0x7c640L, "application_com_rx_indication",
            "COM RxIndication: optional filter, copy frame into FEBE4A49+offset, refresh validity/update counters, notify timeout helper.");
        renameFunction(0x7c03eL, "application_com_receive_signal",
            "Extract an unsigned/signed generated COM signal from a big-endian bit field in the selected I-PDU RAM buffer.");
        renameFunction(0x7d63eL, "application_com_receive_signal_group_bytes",
            "Copy a contiguous byte span from the COM I-PDU buffer for opaque/group receive signals.");
        renameFunction(0x8d682L, "application_com_rx_timeout_on_indication",
            "On RxIndication for PDUs < 0x60: clear validity byte FEBE52CC[pdu] and increment update counter FEBE532C[pdu].");
        renameFunction(0x8d65eL, "application_com_rx_timeout_init",
            "Initialize COM Rx validity/update/shadow state for 96 PDU slots to the erased-compatible 0x5A pattern.");
        renameFunction(0x48cc8L, "application_com_rx_timeout_poll_slot",
            "Poll one logical timeout slot against FEBE52CC via the 0x29178 slot-to-PDU table.");
        renameFunction(0x4a244L, "application_unpack_can_2e4",
            "Generated unpacker for COM PDU 6 / CAN 0x2E4. Watches FEBE5332 and extracts signals 58..63 via receive_signal.");
        renameFunction(0x4b23cL, "application_unpack_can_090_secoc_fd",
            "Generated unpacker for SecOC CAN-FD PDU 46 / CAN 0x090. Extracts three centered 10-bit measurement channels and protected status/freshness fields.");
        renameFunction(0x4b3aaL, "application_unpack_can_0d7_secoc_fd",
            "Generated unpacker for SecOC CAN-FD PDU 47 / CAN 0x0D7. Signal 280 uses a stack temporary persisted to FEBE8076; signal 283 supplies the protected vehicle-speed source.");
        renameFunction(0xbbf0eL, "fd090_primary_measurement_plausibility",
            "Process the first two protected 0x090 normalized measurement channels and status bits into bounded measurement state FEBEB6AA plus 0/0x5A plausibility flags. Exact physical sensor names remain unresolved.");
        renameFunction(0xbc766L, "fd090_third_measurement_plausibility",
            "Process the third protected 0x090 normalized measurement channel and paired status bits into bounded state FEBEB714 plus 0/0x5A plausibility flags. Exact physical sensor name remains unresolved.");
        renameFunction(0xbc484L, "fd0d7_vehicle_speed_normalize",
            "Normalize protected CAN-FD 0x0D7 signal 283 from FEBEF1B6 into FEBEB6F2, the shared live source later published as application_vehicle_speed_raw.");
        renameFunction(0xb6396L, "fd0d7_status_fault_monitor",
            "Monitor protected 0x0D7 status staged at FEBEF094 together with companion validity state; an asserted invalidity while healthy forces the local fault state and raises system-mode event 0x2D.");
        renameFunction(0x68368L, "application_com_opaque_rx_shadow_bank0",
            "Opaque property-4 Rx consumer: copy whole 8-byte PDUs for signals 87..94 into a stack shadow and compare.");
        renameFunction(0x6875eL, "crypto_test_bank1_can_input_collect",
            "Collect stable crypto-test inputs from property-4 signals 95..100: selector/mode on CAN 0x01B, chosen input on 0x01C/0x01D, and expected result on 0x01E/0x01F.");
        renameFunction(0x56fc2L, "application_rx_signal_consumer_56fc2",
            "First recovered non-unpacker reader for many COM Rx destinations around FEBE7F94; structural consumer only.");

        eol(0x4a276L, "Unpack CAN 0x2E4 signal 61 (first receive_signal call in this generated unpacker).");
        eol(0x7c6c0L, "COM RxIndication copies received bytes into FEBE4A49 + buffer offset.");
        eol(0x8d68eL, "Clear FEBE52CC[pdu] validity byte on indication.");
    }
}
