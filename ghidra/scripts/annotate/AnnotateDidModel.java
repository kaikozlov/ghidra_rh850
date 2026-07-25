//@author kaikozlov
//@category Analysis
// Apply the complete bootloader DID model recovered from 0x5FB8/0x4948.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateDidModel extends GhidraScript {
    private void fn(long value, String name, String comment) throws Exception {
        Address a=toAddr(value);
        Function f=currentProgram.getFunctionManager().getFunctionAt(a);
        if (f==null) throw new IllegalStateException("no function at "+a+" for "+name);
        f.setName(name,SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }
    private void label(long value, String name, String comment) throws Exception {
        Address a=toAddr(value);
        SymbolTable st=currentProgram.getSymbolTable();
        Symbol s=st.getPrimarySymbol(a);
        if (s!=null) {
            if (!s.getName().equals(name)) s.setName(name,SourceType.USER_DEFINED);
        } else {
            s=st.createLabel(a,name,SourceType.USER_DEFINED);
            s.setPrimary();
        }
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }
    @Override public void run() throws Exception {
        fn(0x4900L,"uds_write_did_negative_response",
            "Build a 0x7F 0x2E NRC response for WriteDataByIdentifier.");
        fn(0x4914L,"uds_write_did_positive_response",
            "Build 0x6E || DID for the current four-entry descriptor index.");
        fn(0x4948L,"uds_write_data_by_identifier",
            "Only DIDs 0201/0202/0203 are writable. Requires programming session 2, SecurityAccess state 2, exact length, and order 0203 -> 0201 -> 0202. 0203's five data bytes are ignored.");
        fn(0x4A90L,"uds_write_did_state_reset",
            "Clear the payload-DID sequence state and asynchronous-write pending flag.");
        fn(0x4A9AL,"uds_write_did_completion_task",
            "Complete asynchronous 0201/0202 writes; emit 0x6E on success or NRC 0x72/0x10 on worker failure.");

        fn(0x5F3EL,"bootloader_read_did_fill_placeholder",
            "Generate descriptor.data_length bytes of literal 0x21. The sole readable descriptor is F181, so its 32-byte software-ID body is all exclamation bytes.");
        fn(0x5F68L,"uds_read_did_negative_response",
            "Build a 0x7F 0x22 NRC response for ReadDataByIdentifier.");
        fn(0x5F7CL,"uds_read_did_positive_response",
            "Build 0x62 || DID || optional descriptor prefix || generated data.");
        fn(0x5FB8L,"uds_read_data_by_identifier",
            "Search exactly four descriptors. F181 is the sole readable DID and returns 02 || 32*0x21; no VIN, part-number, serial, or config DID is exposed by this bootloader handler.");
        fn(0x6D3AL,"bootloader_did_direct_ram_copy",
            "Direct-copy descriptor.data_length bytes to descriptor.destination; used by volatile DIDs 0201 and 0202.");
        fn(0x6D5EL,"bootloader_did_write_dispatch",
            "Dispatch descriptor write_mode 0 to queued memory service or mode 1 to direct RAM copy; configured writable 0201/0202 use mode 1, while 0203 bypasses this function.");

        label(0x8F00L,"uds_read_did_allowed_sessions",
            "Three permitted session values for SID 0x22: default 1, programming 2, extended 3.");
        label(0x8F14L,"bootloader_did_descriptor_table",
            "Exactly four 12-byte descriptors: destination u32, length u16, DID u16, access u8, write_mode u8, read_prefix u8, reserved u8.");
        label(0x8F20L,"did_0201_descriptor",
            "Write-only len16, mode1 direct copy to FEBF2D08; payload key-derivation input.");
        label(0x8F2CL,"did_0202_descriptor",
            "Write-only len16, mode1 direct copy to FEBF2CF8; AES-CBC IV and first CMAC block.");
        label(0x8F38L,"did_0203_descriptor",
            "Write-only len5, no pointer. Handler ignores the five bytes and uses the request only to arm sequence state 0 -> 1.");

        label(0xFEBF2AB0L,"uds_write_did_descriptor_index",
            "Selected index in the four-entry DID descriptor table.");
        label(0xFEBF2AB1L,"uds_write_did_pending",
            "Asynchronous 0201/0202 write pending flag.");
        label(0xFEBF2AB2L,"payload_did_sequence_state",
            "Required WDBI order: 0 accepts 0203, 1 accepts 0201, 2 accepts 0202, then returns to 0.");
        label(0xFEBF2B0EL,"uds_current_session",
            "Current UDS session: 1 default, 2 programming, 3 extended.");
        label(0xFEBF2B0FL,"uds_security_access_state",
            "SecurityAccess state. WDBI and protected download/routine paths require value 2.");
        label(0xFEBF2B16L,"payload_did_crypto_ready",
            "Set after successful DID 0202; RequestDownload requires this flag before payload crypto/download paths.");
        label(0xFEBF2B6CL,"uds_read_did_response_length",
            "ReadDID response payload length excluding positive SID 0x62.");
        label(0xFEBF2B6EL,"uds_read_did_response_data",
            "Scratch response beginning with DID high/low; F181 appends prefix 02 and 32 literal 0x21 bytes.");
        label(0xFEBF2D08L,"payload_did_0201_key_material",
            "Volatile 16-byte DID 0201 buffer; AES-ECB encrypted under PAYLOAD_BUILD_SECRET to derive the payload key.");
        label(0xFEBF2CF8L,"payload_did_0202_iv",
            "Volatile 16-byte DID 0202 buffer; AES-CBC IV and first block fed to payload CMAC.");
    }
}
