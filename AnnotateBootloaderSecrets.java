//@author optskug
//@category Analysis
// Apply names/comments recovered from the correctly mapped bootloader analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateBootloaderSecrets extends GhidraScript {
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

    @Override
    public void run() throws Exception {
        labelData(0xBFD8L,"PAYLOAD_BUILD_SECRET",
            "Family-shared AES-128 payload-build secret. Directly loaded at 0x7070. " +
            "Original combined-file offset 0x13FD8; corrected CodeFlash VA 0xBFD8.");
        labelData(0xBFE8L,"SEED_KEY_SECRET",
            "Family-shared AES-128 UDS SecurityAccess secret. Directly loaded at 0x6FF8. " +
            "Original combined-file offset 0x13FE8; corrected CodeFlash VA 0xBFE8.");
        labelData(0x8E54L,"uds_service_table",
            "20 entries x 8 bytes: SID, session mask, reserved u16, handler pointer u32.");

        renameFunction(0x5328L,"uds_security_access_request_seed",
            "UDS SID 0x27 request-seed path. Saves the tester's 16-byte data record and prepares/returns the ECU seed.");
        renameFunction(0x53F2L,"uds_security_access_send_key",
            "UDS SID 0x27 send-key path. Computes the expected 16-byte response and compares it to tester input; emits NRC 0x35/0x36 on failure.");
        renameFunction(0x6FECL,"security_access_derive_stage1_key",
            "derived_key = AES-128-ECB-DECRYPT(SEED_KEY_SECRET, tester_data_record). The secret is loaded from CodeFlash 0xBFE8 at instruction 0x6FF8.");
        renameFunction(0x701EL,"aes128_ecb_encrypt_with_runtime_key",
            "Initialize AES-128 with caller-supplied key, encrypt one 16-byte block, then clear the context.");
        renameFunction(0x704CL,"security_access_compute_expected_key",
            "expected_key = AES-128-ECB-ENCRYPT(AES-128-ECB-DECRYPT(SEED_KEY_SECRET, tester_data_record), ecu_seed).");
        renameFunction(0x7068L,"payload_build_derive_key",
            "derived_payload_key = AES-128-ECB-ENCRYPT(PAYLOAD_BUILD_SECRET, DID 0x201 key material). The secret is loaded from CodeFlash 0xBFD8 at instruction 0x7070.");
        renameFunction(0x7352L,"aes128_ecb_encrypt_block",
            "AES-128 single-block encryption (10 forward rounds) using an initialized context.");
        renameFunction(0x7470L,"aes128_ecb_decrypt_block",
            "AES-128 single-block decryption (10 inverse rounds) using an initialized context.");
        renameFunction(0x7594L,"aes128_expand_key",
            "AES-128 key expansion: copy 16-byte key and generate 44 32-bit round-key words using S-box/Rcon at 0x8FF1/0x8FE1.");
        renameFunction(0x7680L,"aes128_init_context",
            "Initialize AES-128 context from r6 key pointer, r7 key length (must be 16), r8 context pointer.");
        renameFunction(0x76C6L,"aes128_clear_context",
            "Clear AES context after use.");
    }
}
