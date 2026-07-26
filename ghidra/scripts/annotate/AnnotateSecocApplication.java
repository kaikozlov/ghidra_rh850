//@author kaikozlov
//@category Analysis
// Annotate the application SecOC receive profile, freshness packing, and ICU-S slot-4 path.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateSecocApplication extends GhidraScript {
    private void rename(long value,String name,String comment) throws Exception {
        Address a=toAddr(value);
        Function f=currentProgram.getFunctionManager().getFunctionAt(a);
        if(f==null) throw new IllegalStateException("no function at "+a);
        f.setName(name,SourceType.USER_DEFINED);
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }
    private void label(long value,String name,String comment) throws Exception {
        Address a=toAddr(value);
        SymbolTable st=currentProgram.getSymbolTable();
        Symbol s=st.getPrimarySymbol(a);
        if(s!=null && s.getSource()!=SourceType.USER_DEFINED) s.setName(name,SourceType.USER_DEFINED);
        else if(s==null) { s=st.createLabel(a,name,SourceType.USER_DEFINED); s.setPrimary(); }
        currentProgram.getListing().setComment(a,CodeUnit.PLATE_COMMENT,comment);
        println(a+" -> "+name);
    }
    @Override public void run() throws Exception {
        rename(0x680F8L,"secoc_icus_slot4_known_answer_sync",
            "Synchronous ICU-S CMAC-verify known-answer check: CMAC of 16 zero bytes under slot 4 must equal B290FA2E...E540, the FF*16-key vector.");
        rename(0x68218L,"secoc_icus_slot4_kat_commit",
            "Commit the ICU slot-4 known-answer result into the generated SecOC crypto configuration state.");
        rename(0x682A6L,"secoc_icus_slot4_known_answer_async",
            "Asynchronous phase of the slot-4 known-answer check through lower CryptoIf record 1.");

        rename(0x8DB84L,"secoc_rx_init",
            "Initialize generated SecOC RX state and install crypto config type 1 / ICU-S slot selector 4 from 0x25950.");
        rename(0x8DC64L,"secoc_rx_indication",
            "Application SecOC receive ingress. Resolve application RX PDU to one of six records and queue secured-PDU verification.");
        rename(0x8E024L,"secoc_rx_record_lookup",
            "Map secured/authentic PDU ID to one of six 0x50-byte SecOC receive records at 0x25970.");
        rename(0x8E0BEL,"secoc_rx_queue_secured_pdu",
            "Clamp received length to configured buffer size and queue a secured PDU for generated SecOC processing.");
        rename(0x8E1A8L,"secoc_rx_split_freshness_and_tag",
            "Split the packed trailer into transmitted FreshnessValue and the 28-bit authenticator according to the selected profile.");
        rename(0x8E4BAL,"secoc_rx_verify_worker",
            "Reconstruct full freshness, build DataID||payload||freshness, and submit 28-bit AES-CMAC verification through CryptoIf handle 0.");
        rename(0x8DB22L,"secoc_build_authenticated_input",
            "Build big-endian DataID followed by authentic payload and reconstructed full freshness. Classic protected records produce 12 bytes.");

        rename(0x8DE8EL,"secoc_crypto_config_clear",
            "Clear the generated 20-byte SecOC crypto configuration and status fields.");
        rename(0x8DEBCL,"secoc_crypto_config_set",
            "Install generated crypto type/key-selector bytes. Initial config at 0x25950 selects ICU-S slot 4; no AES key bytes are copied to ICU.");
        rename(0x8DF0EL,"secoc_crypto_config_get",
            "Copy the current type/key-selector record for a SecOC crypto job.");
        rename(0x8DF84L,"secoc_crypto_config_validate",
            "Validate generated crypto configuration and complement bytes before SecOC processing.");
        rename(0x8E3EAL,"secoc_submit_cmac_verify",
            "Submit authenticated input and 28-bit tag through generated CSM/CryptoIf wrappers using configured handle 0.");
        rename(0x88B6AL,"cryptoif_job_begin",
            "Check lower crypto driver availability and retain the per-job key/type configuration pointer.");
        rename(0x88B9CL,"cryptoif_job_update",
            "Retain authenticated-input pointer and byte length for the pending crypto job.");
        rename(0x88BA8L,"cryptoif_job_finish",
            "Dispatch the retained config/input plus output tag and bit length to lower crypto driver, then poll completion.");
        rename(0x88508L,"crypto_driver_record_lookup",
            "Resolve lower crypto driver ID 0 or 1. SecOC profiles use ID 0; the asynchronous slot-4 KAT uses ID 1.");
        rename(0x88556L,"crypto_driver_dispatch",
            "Serialize lower crypto jobs and invoke the configured driver callback; records 0/1 both target the ICU-S verify adapter.");
        rename(0x88C0AL,"cryptoif_job_completion",
            "Publish completion status to the generated polling wrapper.");

        rename(0x87ED0L,"icus_cmac_verify_prepare",
            "Prepare ICU-S CMAC verification: copy message/tag, retain bit lengths, and read the key-slot selector from config+4.");
        rename(0x880DCL,"icus_cmac_verify_adapter",
            "Lower crypto adapter for ICU-S CMAC verify. It accepts CPU message/tag buffers but not plaintext key bytes.");
        rename(0x88080L,"icus_cmac_verify_start",
            "Start ICU-S command 7 using the prepared request descriptor.");
        rename(0x897F4L,"icus_command7_cmac_verify",
            "Program ICU-S command register FFC5D000 with (key_slot<<16)|7 and start AES-CMAC verification.");

        rename(0x8E80AL,"secoc_freshness_profile_lookup",
            "Resolve synchronization versus ordinary freshness state for a configured freshness ID.");
        rename(0x8E8E6L,"secoc_get_rx_freshness",
            "Generated freshness callback: reconstruct full freshness from transmitted bits and retained receiver state.");
        rename(0x8E942L,"secoc_commit_rx_freshness",
            "Commit reconstructed freshness only after successful authentication.");
        rename(0x8EA4CL,"secoc_pack_full_freshness",
            "Pack normal full freshness as trip16/reset20/message8/reset-low2/two-zero-pad-bits (46 meaningful bits in six bytes).");
        rename(0x8EBC2L,"secoc_unpack_truncated_freshness",
            "Decode ordinary transmitted FV4 as message-counter-low2 plus reset-counter-low2; decode sync FV36 separately.");
        rename(0x8EECAL,"secoc_reconstruct_normal_freshness",
            "Use FV4 and retained state/counter window to construct a candidate 46-bit normal freshness value.");
        rename(0x8EF9EL,"secoc_reconstruct_sync_freshness",
            "Validate and reconstruct the 36-bit synchronization freshness value.");
        rename(0x8F084L,"secoc_commit_normal_freshness",
            "Commit authenticated ordinary-message freshness state.");
        rename(0x8F112L,"secoc_commit_sync_freshness",
            "Commit authenticated trip/reset synchronization state and reset dependent message windows when required.");

        label(0x25950L,"secoc_icus_slot4_config",
            "Generated crypto config: type word 1 and ICU-S key-slot selector 4, followed by zeros.");
        label(0x25970L,"secoc_rx_profile_table",
            "Six 0x50-byte RX profiles for Data/CAN IDs 00F,2E4,131,132,090,0D7. Normal trailer is FV4+CMAC28; sync is FV36+CMAC28.");
        label(0x215E4L,"secoc_slot4_kat_zero_message",
            "Sixteen zero bytes used by the ICU-S slot-4 CMAC known-answer check.");
        label(0x215F4L,"secoc_slot4_kat_ff_key_tag",
            "B290FA2EA7B6B52EB124134522A6E540: AES-CMAC of 16 zero bytes under FF*16.");
        label(0x21604L,"secoc_slot4_kat_config",
            "Known-answer config type 1 / ICU-S key selector 4; byte-identical to 0x25950.");
        label(0x27FBCL,"crypto_driver_record_0",
            "Lower crypto driver record 0, used by all six SecOC receive profiles; callback 0x880DC.");
        label(0x27FDCL,"crypto_driver_record_1",
            "Lower crypto driver record 1, used by asynchronous slot-4 known-answer processing; callback 0x880DC.");
        label(0xFEBF0B08L,"secoc_nvm_triplicate_workbuf_root",
            "Correct application-GP-derived root for four generic 3x32-byte NvM work groups. The old FEBFEB08 label was wrong.");
        label(0xFEBF0C28L,"secoc_nvm_object15_raw_workbuf",
            "Object-15 restore group (15&3): raw block-41 destination.");
        label(0xFEBF0C48L,"secoc_nvm_object15_xor55_workbuf",
            "Object-15 restore group: XOR55 block-45 destination.");
        label(0xFEBF0C68L,"secoc_nvm_object15_xoraa_workbuf",
            "Object-15 restore group: XORAA block-49 destination.");
    }
}
