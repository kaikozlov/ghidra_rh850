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
        rename(0x680F8L,"secoc_icus_slot4_kat_disabled_sync",
            "Compiled-out synchronous ICU-S slot-4 CMAC KAT. The crypto body runs only when fixed CodeFlash byte 0x30EF3 is 0x5A; this calibration stores 0x00, so execution branches directly to the report-only tail.");
        rename(0x68218L,"secoc_icus_slot4_kat_commit",
            "Commit the generated KAT status. In this calibration both KAT crypto bodies are compiled out by CodeFlash gate 0x30EF3=0x00.");
        rename(0x682A6L,"secoc_icus_slot4_kat_disabled_async",
            "Compiled-out asynchronous ICU-S slot-4 CMAC KAT. It uses the same fixed 0x30EF3==0x5A gate as the synchronous twin; command 7 is not submitted in this calibration.");

        rename(0x6875EL,"crypto_test_bank1_can_input_collect",
            "Collect stable application COM inputs for crypto-test bank 1. CAN 0x01B supplies selector/mode; 0x01C/0x01D supply 16 input bytes; 0x01E/0x01F supply 16 expected-result bytes. Three identical updates are required before committing the bank.");
        rename(0x68B42L,"icus_crypto_test_submit",
            "Generated application crypto-test harness. Mode 1 submits ICU-S command 5 with a runtime key selector from FEBE5098, 16 input bytes at FEBE517A, and a 16-byte output buffer at FEBE51AA.");
        rename(0x68BC2L,"crypto_test_bank1_state_step",
            "Advance dormant crypto-test bank 1. State 0x11 collects stable COM inputs; state 0x22 submits the configured crypto operation. Execution requires activation byte FEBE508F==1.");
        rename(0x68D0EL,"crypto_test_bank1_finalize",
            "Finalize crypto-test bank 1: result 0x33 disables the bank cleanly; result 0x44 latches failure at FEBE5097. No generated MAC bytes are transmitted.");
        rename(0x68F0CL,"crypto_test_bank0_update_counter_snapshot",
            "Snapshot the eight COM update counters used by crypto-test bank 0.");
        rename(0x68F92L,"crypto_test_bank0_activate",
            "Crypto-test bank-0 activator. Application RoutineControl RID 0x100E startRoutine reaches it through action wrapper 0x8A774; it initializes state and update-counter snapshots.");
        rename(0x68FC2L,"crypto_test_bank1_update_counter_snapshot",
            "Snapshot the five COM update counters for CAN 0x01B..0x01F before crypto-test bank 1 begins.");
        rename(0x69018L,"crypto_test_bank1_activate",
            "Crypto-test bank-1 activator reached by application RoutineControl RID 0x100F startRoutine through action wrapper 0x8A782. It sets FEBE508F=1, initializes state 0x11, clears bank RAM, and snapshots CAN 0x01B..0x01F update counters.");
        rename(0x69068L,"icus_command5_test_result_compare",
            "Compare all 16 command-5 output bytes at FEBE51AA with the expected bytes at FEBE518A; return 0x33 on equality and 0x44 on mismatch.");
        rename(0x68E16L,"icus_key_update_diagnostic_start",
            "RoutineControl control-type-1 diagnostic start: accept the fixed 64-byte command-8 envelope, report status 0x01, clear the 48-byte result bank, and arm key-update state 0x22. A second start while pending returns internal result 8.");
        rename(0x68EA8L,"icus_key_update_diagnostic_read_result",
            "RoutineControl control-type-3 diagnostic result read: return status 0x01/0x02/0xFF and 48 bytes from FEBE523A only for 0x02; zero-fill otherwise and clear request/result banks after terminal 0x02 or 0xFF is read.");
        rename(0x6823CL,"icus_key_update_submit",
            "Submit the 64-byte diagnostic key-update envelope through driver record 0 and provide a 48-byte result buffer. Success advances the state from 0x22 to 0x33 while completion is pending.");
        rename(0x6920AL,"icus_key_update_completion_callback",
            "Command-8 diagnostic completion callback. Hardware success advances the active key-update bank to state 0x44; failure advances it to 0x66.");
        rename(0x6922CL,"icus_command1_3_test_completion",
            "Asynchronous completion callback for the neighboring command-1/3 AES test record; this is not a command-13 persistent-key export path.");
        rename(0x8783CL,"icus_command1_3_test_submit",
            "Submit the dormant command-1/3 AES test record through the shared ICU-S driver and arm its asynchronous completion state.");
        rename(0x8954CL,"icus_command1_3_aes_transform",
            "Low-level ICU-S AES wrapper: accept selector 0..14, map operation flag 0/1 to command 1/3, stream caller input/output, and write (selector << 16) | command to ICUSCMD. Slot policy remains hardware-enforced.");
        rename(0x69246L,"icus_command7_test_completion",
            "Asynchronous command-7 test completion callback; record failure and advance the generated test state.");
        rename(0x6926AL,"icus_command5_test_completion",
            "Asynchronous command-5 test completion callback; on success compare the full 16-byte generated result through 0x69068.");

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

        rename(0x87A94L,"icus_command5_mac_generate_prepare",
            "Prepare ICU-S command 5: stage up to 80 input bytes, retain caller output pointer and output-length pointer, clamp generated output to 16 bytes, and load the runtime key selector from config+4.");
        rename(0x87B46L,"icus_command5_mac_generate_copy_result",
            "On successful command-5 completion, clamp *output_length to 16 and copy the generated 16-byte ICU result into the caller-provided output buffer.");
        rename(0x87BBAL,"icus_command5_mac_generate_finish",
            "Finish command-5 processing and publish completion through the selected lower-driver callback.");
        rename(0x87C14L,"icus_command5_interrupt_completion",
            "ICU-S command-5 interrupt callback. Poll hardware completion, translate status, release the shared lower-driver state, and publish the generated result through 0x87BBA.");
        rename(0x87C70L,"icus_command5_mac_generate_start",
            "Start the prepared ICU-S command-5 request through hardware engine 0x89630.");
        rename(0x87CCCL,"icus_command5_mac_generate_adapter",
            "Lower-driver adapter for ICU-S command 5. Accepts config, input pointer/length, output pointer, output-length pointer, and truncation mode; no plaintext key bytes cross the interface.");
        rename(0x87DD0L,"icus_command5_mac_generate_completion",
            "Command-5 asynchronous completion worker paired with the command-7 worker at 0x881DC.");
        rename(0x88302L,"crypto_generate_driver_record_lookup",
            "Resolve command-5 lower-driver record ID 0 or 1 from the two records at 0x27F78/0x27F98.");
        rename(0x88350L,"crypto_generate_driver_dispatch",
            "Serialize a command-5 job and invoke the configured ICU-S MAC-generation adapter.");
        rename(0x88B5CL,"cryptoif_generate_completion",
            "Publish synchronous command-5 completion status to the generated polling wrapper.");
        rename(0x89630L,"icus_command5_mac_generate",
            "Program ICUSCMD with (runtime_key_selector<<16)|5. The paired adapter stages message input and returns up to 16 generated bytes; the only configured caller is the application crypto-test harness.");

        rename(0x86E62L,"icus_command8_key_update_prepare",
            "Prepare ICU-S command 8. Require exactly 64 input bytes and at least 48 output bytes; stage input as 16+32+16 and retain the caller output pointer for a 32+16-byte result.");
        rename(0x86EE8L,"icus_command8_key_update_copy_result",
            "On successful command-8 completion, copy 32+16 bytes from the ICU staging buffers to the caller and set the returned length to 48; clear all 64-byte input and 48-byte result staging.");
        rename(0x8704CL,"icus_command8_key_update_start",
            "Start a prepared ICU-S command-8 authenticated key-update request through hardware engine 0x8997A.");
        rename(0x870A8L,"icus_command8_key_update_adapter",
            "Serialized command-8 lower-driver adapter. It accepts the 64-byte authenticated update envelope and a 48-byte proof/result destination.");
        rename(0x871A0L,"icus_command8_key_update_completion",
            "Command-8 asynchronous completion worker; poll the shared ICU driver, recover on timeout, copy the 48-byte result, and publish the configured callback.");
        rename(0x888FAL,"icus_key_update_driver_record_lookup",
            "Resolve the sole command-8 driver record at 0x28024 (record ID 0).");
        rename(0x88936L,"icus_key_update_driver_dispatch",
            "Serialize and dispatch the configured command-8 key-update job through lower adapter 0x870A8.");
        rename(0x889CCL,"icus_key_update_driver_completion",
            "Release command-8 upper-driver state and publish completion through callback 0x6920A.");
        rename(0x8997AL,"icus_command8_authenticated_key_update",
            "Program ICUSCMD with literal command 8 after staging the 64-byte authenticated update request. The request itself carries the protected target/authentication metadata; no plaintext key argument crosses this API.");

        rename(0x8913CL,"icus_interrupt_pair_set_enabled",
            "Mask or unmask ICU-S EIINT 292 and 293 together, then synchronize the write.");
        rename(0x8917AL,"icus_abort_and_recover",
            "Disable the ICU interrupt pair, issue command 0x3F when busy, poll for idle/completion, reset ICUSCTL, and restore the interrupt masks.");
        rename(0x892F2L,"icus_register_self_test",
            "Exercise ICU-S staging/register windows with alternating AAAAAAAA/55555555 patterns during driver initialization.");
        rename(0x89360L,"icus_driver_state_initialize",
            "Clear ICU-S driver callback, descriptor, complement, and state fields in application RAM.");
        rename(0x893B8L,"icus_hardware_initialize",
            "Initialize ICU-S control/staging registers and set ICUSCTL=3 before normal application jobs.");
        rename(0x893DEL,"icus_driver_initialize",
            "Application ICU-S initialization entry: recover/abort stale hardware state, run the register self-test, clear driver RAM, initialize control registers, and publish ready state 0xE1.");
        rename(0x89424L,"icus_write_128",
            "Write one 128-bit block as four words through the ICUSDAT input register.");
        rename(0x89448L,"icus_input_fifo_step",
            "Command-engine input callback: stream the next 16-byte block to ICUSDAT and advance pointer/count state.");
        rename(0x8949AL,"icus_read_128",
            "Read one 128-bit block as four words through the ICU-S output-data register.");
        rename(0x894BEL,"icus_output_fifo_step",
            "Command-engine output callback: read the next 16-byte result block and advance pointer/count state.");
        rename(0x89510L,"icus_command_finalize",
            "Finalize an ICU-S command-engine request and translate ready/error state for the asynchronous driver.");
        rename(0x88C4CL,"crypto_icus_initialize",
            "Application startup initializer for the generated crypto stack and ICU-S lower driver.");
        rename(0x8A6C8L,"icus_key_update_operation_reset",
            "Reset the generated RID-1010 operation wrapper and clear its request/result scratch banks.");
        rename(0x8A860L,"icus_key_update_result_read_wrapper",
            "Generated RoutineControl result wrapper: request 49 status/result bytes from 0x68EA8 and copy them to the Dcm output field.");
        rename(0x8A93CL,"icus_key_update_result_operation",
            "Run the RoutineControl result-read wrapper and translate generated operation results to the application Dcm return/NRC convention.");
        rename(0x8AA1EL,"icus_key_update_start_wrapper",
            "Generated RoutineControl start wrapper: clamp input/output to 64/49 bytes, invoke 0x68E16, and copy its immediate status/result field to Dcm.");
        rename(0x8AB5AL,"icus_key_update_start_operation",
            "Run the RoutineControl start wrapper after generated readiness handling and translate its result to Dcm return/NRC convention.");
        rename(0x955DCL,"application_routine_control_type_supported",
            "Validate RoutineControl control type 1, 2, or 3 against the selected RID's generated configuration.");
        rename(0x95624L,"application_routine_control_input_length_invalid",
            "Compute the configured control-type/RID input-field width plus the three-byte control-type/RID header and reject unequal request length.");
        rename(0x956C6L,"application_routine_control_output_capacity_invalid",
            "Compute the configured control-type/RID output-field width plus the three-byte control-type/RID header and reject insufficient response capacity.");
        rename(0x95F82L,"application_routine_control_1010_read_result",
            "RoutineControl control-type-3 RID-1010 callback. Request exactly 49 bytes from the key-update status/result operation; non-start phases reset the generated wrapper.");
        rename(0x96354L,"application_routine_control_1010_start_key_update",
            "RoutineControl control-type-1 RID-1010 callback. Submit exactly 64 M1/M2/M3 bytes and return a 49-byte status/result field; non-start phases reset the generated wrapper.");
        rename(0x965CEL,"application_routine_control_type3_dispatch",
            "Dispatch RoutineControl control type 3 callbacks by RoutineControl RID table index; entry 9 routes to the RID-1010 status/result read.");
        rename(0x96764L,"application_routine_control_type1_dispatch",
            "Dispatch RoutineControl control type 1 callbacks by RoutineControl RID table index; entry 9 routes to the RID-1010 authenticated key-update start.");

        rename(0x87ED0L,"icus_cmac_verify_prepare",
            "Prepare ICU-S CMAC verification: copy message/tag, retain bit lengths, and read the key-slot selector from config+4.");
        rename(0x880DCL,"icus_cmac_verify_adapter",
            "Lower crypto adapter for ICU-S CMAC verify. It accepts CPU message/tag buffers but not plaintext key bytes.");
        rename(0x88080L,"icus_cmac_verify_start",
            "Start ICU-S command 7 using the prepared request descriptor.");
        rename(0x88028L,"icus_command7_interrupt_completion",
            "ICU-S command-7 interrupt callback paired with command-5 callback 0x87C14; poll completion and publish verification status.");
        rename(0x881DCL,"icus_cmac_verify_completion",
            "Command-7 asynchronous completion worker paired with command-5 worker 0x87DD0.");
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
            "Latent sixteen-zero-byte KAT input. Both functions that reference it are compiled out by gate byte 0x30EF3=0x00.");
        label(0x215F4L,"secoc_slot4_kat_ff_key_tag",
            "Latent dead-data vector B290FA2EA7B6B52EB124134522A6E540 (CMAC of 16 zero bytes under FF*16); it places no constraint on the live slot-4 key.");
        label(0x21604L,"secoc_slot4_kat_config",
            "Latent KAT config type 1 / ICU-S key selector 4; byte-identical to 0x25950, but unreachable in this calibration because 0x30EF3 is 0x00.");
        label(0x30EF3L,"secoc_slot4_kat_enable_gate",
            "Fixed compile-time gate for both slot-4 KAT bodies. Required value is 0x5A; this calibration stores 0x00, so both crypto bodies are disabled.");
        label(0x27F78L,"crypto_generate_driver_record_0",
            "Command-5 lower-driver record 0: synchronous completion callback 0x88B5C, adapter 0x87CCC, worker 0x87DD0.");
        label(0x27F98L,"crypto_generate_driver_record_1",
            "Command-5 lower-driver record 1: application-test callback 0x6926A, adapter 0x87CCC, worker 0x87DD0.");
        label(0x28024L,"icus_key_update_driver_record",
            "Command-8 record ID 0: completion callback 0x6920A, lower adapter 0x870A8, completion worker 0x871A0, state root 0x28020.");
        label(0x26B34L,"application_routine_control_1010_record",
            "Enabled application RoutineControl record for RID 0x1010. Extended session 0x03, no Dcm SecurityAccess level; control type 1 starts and control type 3 reads status/result.");
        label(0x2670CL,"application_routine_control_1010_type3_output",
            "RoutineControl control-type-3 RID-1010 output descriptor: one 392-bit (49-byte) status/result field.");
        label(0x26790L,"application_routine_control_1010_type1_input",
            "RoutineControl control-type-1 RID-1010 input descriptor: one 512-bit (64-byte) M1/M2/M3 field.");
        label(0x267B4L,"application_routine_control_1010_type1_output",
            "RoutineControl control-type-1 RID-1010 output descriptor: one 392-bit (49-byte) immediate status/result field.");
        label(0xFEBE51BAL,"icus_key_update_m1_m2_m3",
            "Sixty-four-byte diagnostic command-8 input bank, staged as 16+32+16 bytes (SHE-compatible M1/M2/M3 shape).");
        label(0xFEBE523AL,"icus_key_update_m4_m5",
            "Forty-eight-byte command-8 result bank, returned as 32+16 bytes (SHE-compatible M4/M5 proof shape).");
        label(0x258F8L,"crypto_test_bank1_update_counter_indices",
            "Five COM update-counter indices 20..24 for the CAN 0x01B..0x01F crypto-test inputs.");
        label(0x25912L,"crypto_test_bank1_signal_ids",
            "Signal IDs 95..100: two scalar selector/mode inputs followed by four opaque eight-byte input/expected-result groups.");
        label(0xFEBE508FL,"crypto_test_bank1_active",
            "Crypto-test bank-1 activation state. Activator 0x69018 writes value 1 and is reachable from application RoutineControl RID 0x100F via startRoutine wrapper 0x8A782.");
        label(0xFEBE5090L,"crypto_test_bank1_state",
            "Crypto-test bank-1 state/result byte: collect 0x11, submit 0x22, success 0x33, failure 0x44.");
        label(0xFEBE5098L,"crypto_test_runtime_key_selector",
            "Runtime ICU-S key selector committed from the stable CAN 0x01B input.");
        label(0xFEBE5099L,"crypto_test_runtime_mode",
            "Runtime crypto-test mode committed from CAN 0x01B; mode 1 selects the command-5 generation dispatcher.");
        label(0xFEBE517AL,"crypto_test_message",
            "Sixteen-byte chosen-message input assembled from CAN 0x01C and 0x01D.");
        label(0xFEBE518AL,"crypto_test_expected_result",
            "Sixteen-byte expected-result input assembled from CAN 0x01E and 0x01F.");
        label(0xFEBE51AAL,"crypto_test_generated_result",
            "Sixteen-byte command-5 output. The stock harness compares it locally and never transmits these bytes.");
        label(0x27FBCL,"crypto_driver_record_0",
            "Lower crypto driver record 0, used by all six SecOC receive profiles; callback 0x880DC.");
        label(0x27FDCL,"crypto_driver_record_1",
            "Lower command-7 driver record 1, referenced only by the compiled-out asynchronous slot-4 KAT; callback 0x880DC.");
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
