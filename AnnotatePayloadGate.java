//@author optskug
//@category Analysis
// Names/comments for the verified bootloader payload acceptance/execution path.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotatePayloadGate extends GhidraScript {
    private void fn(long addr,String name,String comment) throws Exception {
        Address a=toAddr(addr);
        Function f=currentProgram.getFunctionManager().getFunctionAt(a);
        if (f==null) throw new IllegalStateException("no function at "+a+" for "+name);
        f.setName(name,SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(String.format("function 0x%x -> %s",addr,name));
    }
    private void label(long addr,String name,String comment) throws Exception {
        Address a=toAddr(addr);
        SymbolTable st=currentProgram.getSymbolTable();
        Symbol s=st.getPrimarySymbol(a);
        if (s!=null) s.setName(name,SourceType.USER_DEFINED);
        else { s=st.createLabel(a,name,SourceType.USER_DEFINED); s.setPrimary(); }
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(String.format("data 0x%x -> %s",addr,name));
    }
    private void comment(long addr,String text) {
        currentProgram.getListing().setComment(toAddr(addr),CodeUnit.PRE_COMMENT,text);
    }
    @Override public void run() throws Exception {
        label(0x8DA0L,"boot_memory_access_table","3 x 16-byte allowed-range records used by RequestDownload/RoutineControl.");
        label(0x8DD0L,"boot_crc_descriptor_table","CRC descriptors for two CodeFlash regions and the 4 KiB RAM payload region.");
        label(0x8E00L,"boot_memory_region_table","3 x 28-byte region records containing CMAC tag address and CRC metadata.");
        label(0x8F14L,"boot_did_table","DID backing records including 0x201 key, 0x202 IV, and 0x203 state.");
        label(0x8F44L,"boot_routine_table","RoutineControl records for 0x10F0..0x10F3 and 0xFF00.");

        fn(0x32D2L,"boot_memory_range_check_access","Validate address/length and operation bit against boot_memory_access_table; return memory class.");
        fn(0x3318L,"boot_memory_range_get_auth_bit","Return the authorization-bit index for a validated memory range.");
        fn(0x335EL,"boot_memory_region_find","Find the region-table index containing an address range.");
        fn(0x3392L,"boot_memory_region_get_cmac_tag","Return the firmware-owned CMAC tag address for a contained range.");
        fn(0x33CCL,"boot_memory_region_get_marker_address","Return region field used by programming-marker setup.");
        fn(0x3438L,"boot_memory_region_get_crc_count","Return CRC descriptor count for a region.");
        fn(0x344CL,"boot_memory_region_get_crc_descriptors","Return CRC descriptor pointer for a region.");

        fn(0x47BAL,"memory_crc_verify_enqueue","Queue asynchronous region CRC/metadata verification.");
        fn(0x47DEL,"memory_crc_verify_result","Return the most recent asynchronous CRC verification result.");
        fn(0x47E4L,"memory_crc_verify_busy","Return whether asynchronous CRC verification is pending.");
        fn(0x47EAL,"crc32_hardware_compute","Feed 32-bit words through the RH850 CRC peripheral with caller-supplied seed.");
        fn(0x481AL,"memory_crc_verify_descriptors","Validate embedded address/length fields and CRC for all descriptors in a region.");
        fn(0x4874L,"memory_crc_verify_task","Periodic asynchronous CRC verification worker.");

        fn(0x780L,"bootloader_service_periodic","Periodic entry that drives active bootloader diagnostic state machines.");
        fn(0x51ACL,"bootloader_diagnostics_periodic","Periodic diagnostic state-machine task, including RoutineControl and TransferData workers.");
        fn(0x6A06L,"bootloader_service_periodic_wrapper","Guarded wrapper around bootloader_diagnostics_periodic.");
        fn(0x5936L,"routine_verify_crc_cmac_task","Routine 0x10F0/0x10F1 worker: wait for CRC, run CMAC, authorize region only on success.");
        fn(0x5A04L,"routine_program_verify_task","Routine 0x10F2 worker: CRC/CMAC validation followed by programming-marker setup.");
        fn(0x5B70L,"routine_erase_task","Routine 0xFF00 worker: wait for the flash operation and produce final status if execution is not hijacked.");
        fn(0x5C06L,"routine_control_task_dispatch","Dispatch pending routines to 0x10F0/1, 0x10F2, or 0xFF00 asynchronous workers.");

        fn(0x6BB4L,"payload_decrypt_enqueue","Queue ciphertext source, plaintext destination, and byte count for asynchronous CBC decryption.");
        fn(0x6BDEL,"payload_decrypt_transfer_task","Decrypt one AES-CBC block per periodic invocation and copy plaintext to download destination.");
        fn(0x6EAEL,"payload_crypto_reinitialize","Re-derive the payload key and initialize CBC/CMAC contexts before authentication.");
        fn(0x6EBAL,"payload_cmac_verify_enqueue","Queue asynchronous CMAC verification for an address range.");
        fn(0x6F04L,"payload_crypto_clear_after_verify","Clear payload CBC and CMAC contexts after verification.");
        fn(0x709AL,"payload_crypto_init_cbc_cmac","Initialize AES-CBC with DID 0x202 IV and AES-CMAC with the derived payload key.");
        fn(0x70D4L,"payload_crypto_initialize","Derive payload key from PAYLOAD_BUILD_SECRET and initialize CBC/CMAC contexts.");
        fn(0x70E4L,"payload_crypto_clear","Clear CBC and CMAC contexts.");
        fn(0x70FCL,"payload_crypto_finalize","Wrapper used by TransferExit and verify cleanup.");
        fn(0x7108L,"payload_aes_cbc_decrypt_block","Decrypt one 16-byte transfer block using the active payload CBC context.");
        fn(0x7122L,"payload_cmac_verify_setup","Get tag address, feed DID 0x202 IV into CMAC, and establish message/tag boundaries.");
        fn(0x7170L,"payload_cmac_verify_step","Process one 16-byte CMAC block; on final block compare computed tag byte-for-byte.");

        fn(0x7D50L,"aes_cmac_generate_subkeys","Generate RFC 4493 K1/K2 by AES(0) and GF(2^128) doubling with Rb 0x87.");
        fn(0x7E0CL,"aes_cmac_process_block","AES-CMAC block update/finalization engine.");
        fn(0x7FB4L,"aes_cmac_init","Initialize CMAC context with a 16-byte AES key.");
        fn(0x7FFCL,"aes_cmac_clear","Clear CMAC context.");
        fn(0x8162L,"aes128_cbc_decrypt_block","AES-decrypt one block, XOR previous ciphertext/IV, then update chaining value.");
        fn(0x82B6L,"aes128_cbc_decrypt_init","Initialize AES-CBC decryption context with key and IV.");
        fn(0x834EL,"aes128_cbc_clear","Clear AES-CBC context.");

        fn(0x41E0L,"flash_erase_start","Validate a CodeFlash range and start asynchronous erase operation type 2.");
        fn(0x4332L,"flash_driver_call_block_operation","Flash engine block operation that calls the function pointer stored at RAM 0xFEBF0FD0.");
        fn(0x43BEL,"flash_driver_program_chunk","Flash programming helper; also calls the function pointer stored at RAM 0xFEBF0FD0.");
        fn(0x4428L,"flash_operation_task","Periodic flash erase/program state machine, run after diagnostics in the main loop.");

        comment(0x4350L,"Loads *(uint32_t *)0xFEBF0FD0. Authenticated payloads place 0xFEBF0000 here.");
        comment(0x435EL,"Indirect call through payload-controlled flash callback; transfers execution to uploaded shellcode.");
        comment(0x440AL,"Second load of the callback at RAM 0xFEBF0FD0 in the programming path.");
        comment(0x440EL,"Second indirect call through the payload-controlled flash callback.");
    }
}
