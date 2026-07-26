//@author kaikozlov
//@category Analysis
// Names/comments for completed bootloader SIDs 10/11/28/3E/85 and RIDs 10F1..10F3.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class AnnotateBootloaderDiagnostics extends GhidraScript {
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
        fn(0x614AL,"uds_diagnostic_session_control",
            "Bootloader SID 10. Support sessions 1/2/3; queue valid transitions for 0x6244. Default->programming and programming->extended return NRC 0x7E.");
        fn(0x60C2L,"uds_ecu_reset",
            "Bootloader SID 11. Accept hardReset 1 only in unlocked programming session; coordinate reset with response completion through 0x67DA.");
        fn(0x688AL,"uds_communication_control",
            "Bootloader SID 28, functional-only. Accept 28 01 01 in extended session; acknowledge only, with no communication-manager state consumer.");
        fn(0x4FF8L,"uds_tester_present",
            "Bootloader SID 3E, functional-only. Accept exact subfunction 00/80 in sessions 1/2/3; no service-local S3 timer state.");
        fn(0x693AL,"uds_control_dtc_setting",
            "Bootloader SID 85, functional-only. Accept DTCSettingOff 02 in extended session; acknowledge only, with no DTC-manager state consumer.");
        fn(0x567EL,"uds_routine_control",
            "Bootloader SID 31. StartRoutine-only RIDs 10F0/10F1 RAM verify, 10F2 CodeFlash verify+marker, 10F3 arm compare mode, and FF00 erase path.");

        fn(0x159EL,"bootloader_hard_reset_wait",
            "Non-returning bootloader reset path: disable interrupts, set low-level boot state 3, enter hardware wait/halt sequence, and loop forever.");
        fn(0x67DAL,"bootloader_reset_after_response",
            "If transport is idle, reset immediately; otherwise set pending-reset FEBF2BBD. Successful Tx confirmation resets; failed confirmation clears pending state.");
        fn(0x6084L,"ecu_reset_negative_response","Build a negative response for SID 11.");
        fn(0x6098L,"ecu_reset_positive_response","Emit 51 plus the accepted hardReset subfunction, honoring suppress-positive-response.");
        fn(0x51D8L,"bootloader_set_diagnostic_session","Atomically update the current bootloader diagnostic session and run session/security cleanup.");

        fn(0x4FBAL,"tester_present_negative_response","Build a negative response for SID 3E.");
        fn(0x4FCEL,"tester_present_positive_response","Emit 7E 00 unless the accepted request had suppress-positive-response bit 7 set.");
        fn(0x684CL,"communication_control_negative_response","Build a negative response for SID 28.");
        fn(0x6860L,"communication_control_positive_response","Emit 68 01 only; accepted byte FEBF2BC3 has no other instruction consumer.");
        fn(0x68FCL,"control_dtc_setting_negative_response","Build a negative response for SID 85.");
        fn(0x6910L,"control_dtc_setting_positive_response","Emit C5 02 only; accepted byte FEBF2BC4 has no other instruction consumer.");

        fn(0x5630L,"routine_control_negative_response","Build a negative response for SID 31.");
        fn(0x5644L,"routine_control_positive_response","Emit 71, accepted subfunction, RID, and configured result bytes.");
        fn(0x4188L,"flash_program_start","Start asynchronous flash programming for caller-supplied address and length; used for CodeFlash validity markers.");
        fn(0x4276L,"flash_program_queue_bytes","Queue bytes into the active flash-program buffer.");
        fn(0x5286L,"program_region_validity_marker","Start a four-byte flash operation and queue marker bytes 5A A5 A5 5A at the selected region marker address.");

        fn(0x4B38L,"transfer_data_negative_response_and_abort","Emit a TransferData NRC and force an active transfer state to terminal state 15.");
        fn(0x4CA2L,"transfer_data_compare_request","Alternate TransferData path armed by RID 10F3: compare tester block data against the target CodeFlash range.");
        fn(0x4E92L,"transfer_data_compare_task","Advance asynchronous compare/decrypt work, then update remaining length/address and acknowledge a matching block.");
        fn(0x4F1CL,"transfer_data_task_dispatch","Dispatch ordinary transfer state 2 or compare transfer state 10 to its asynchronous worker.");
        fn(0x6C6CL,"memory_compare_enqueue","Queue source, target, and length for asynchronous byte comparison; refuse if another comparison is active.");
        fn(0x6C8EL,"memory_compare_task","Compare up to 16 queued source/target bytes per invocation and report completion or mismatch.");

        label(0x8EF4L,"boot_ecu_reset_session_policy","Required current session for SID 11: programming (2).");
        label(0x8EF6L,"boot_communication_control_session_policy","Required current session for SID 28: extended (3).");
        label(0x8EF7L,"boot_control_dtc_setting_session_policy","Required current session for SID 85: extended (3).");
        label(0x8EF9L,"boot_routine_control_session_policy","Required current session for SID 31: programming (2).");
        label(0x8EFDL,"boot_tester_present_session_allowlist","Three allowed sessions for SID 3E: default, programming, extended (1,2,3).");
        label(0x17E00L,"codeflash_region0_validity_marker","RID 10F2 programs 5A A5 A5 5A here after region 0x10000..0x17DFF verifies.");
        label(0xFFE00L,"codeflash_region1_validity_marker","RID 10F2 programs 5A A5 A5 5A here after region 0x18000..0xFFDFF verifies.");

        comment(0x5924L,"RID 10F3 sets shared transfer state 8, arming operation-bit-5 RequestDownload/TransferData compare mode.");
        comment(0x5EC2L,"Armed RequestDownload validates memory-access operation bit 5 and class 0 (CodeFlash only).");
        comment(0x4D66L,"Queue tester block versus target CodeFlash comparison; this path does not program the supplied bytes.");
        comment(0x5AAAL,"Program the selected CodeFlash region's four-byte validity marker after CRC/CMAC success.");
    }
}
