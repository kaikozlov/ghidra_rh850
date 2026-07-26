//@author kaikozlov
//@category Analysis
// Seed application-mode diagnostic callbacks missed by auto-analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;

public class SeedApplicationDiagnosticFunctions extends GhidraScript {
    private Function ensureFunction(long value, String name) throws Exception {
        Address a=toAddr(value);
        Listing listing=currentProgram.getListing();
        Instruction containing=listing.getInstructionContaining(a);
        if (containing!=null && !containing.getMinAddress().equals(a)) {
            listing.clearCodeUnits(containing.getMinAddress(),containing.getMaxAddress(),false);
        }
        CodeUnit unit=listing.getCodeUnitContaining(a);
        if (unit!=null && !(unit instanceof Instruction)) {
            listing.clearCodeUnits(unit.getMinAddress(),unit.getMaxAddress(),false);
        }
        if (listing.getInstructionAt(a)==null && !disassemble(a))
            throw new IllegalStateException("disassembly failed at "+a);
        Function f=currentProgram.getFunctionManager().getFunctionAt(a);
        if (f==null) f=createFunction(a,name);
        if (f==null) throw new IllegalStateException("function creation failed at "+a);
        println(a+" "+f.getName());
        return f;
    }

    @Override
    public void run() throws Exception {
        // Identification DIDs / session control (existing).
        ensureFunction(0x4E8E4L,"application_read_f181");
        ensureFunction(0x4E90AL,"application_read_f186");
        ensureFunction(0x4E918L,"application_read_f18c");
        ensureFunction(0x93FF6L,"application_session_default_callback");
        ensureFunction(0x94006L,"application_session_programming_callback");
        ensureFunction(0x94016L,"application_session_extended_callback");
        ensureFunction(0x93F9AL,"application_session_transition_background_poll");
        ensureFunction(0xB20EAL,"system_programming_shutdown_mode_entry");

        // Stage-2 primary service handlers / workers.
        ensureFunction(0x8B1F0L,"application_ecu_reset_callback");
        ensureFunction(0x8B144L,"application_ecu_reset_request_start");
        ensureFunction(0x8AF28L,"application_ecu_reset_prepare_stage");
        ensureFunction(0x8B014L,"application_ecu_reset_commit_stage");
        ensureFunction(0x945DCL,"application_read_dtc_callback");
        ensureFunction(0x8B5AAL,"application_read_dtc_subfunction_01");
        ensureFunction(0x8BA2AL,"application_read_dtc_subfunction_02");
        ensureFunction(0x8BD94L,"application_read_dtc_subfunction_03");
        ensureFunction(0x8C326L,"application_read_dtc_subfunction_04");
        ensureFunction(0x948AAL,"application_rdbi_callback");
        ensureFunction(0x9479AL,"application_rdbi_request_start");
        ensureFunction(0x946FAL,"application_rdbi_request_poll");
        ensureFunction(0x94E32L,"application_security_access_subfunction_01");
        ensureFunction(0x94E46L,"application_security_access_subfunction_02");
        ensureFunction(0x94E5AL,"application_security_access_subfunction_03");
        ensureFunction(0x94E6EL,"application_security_access_subfunction_04");
        ensureFunction(0x9497CL,"application_security_access_request_seed");
        ensureFunction(0x94A72L,"application_security_access_send_key");
        ensureFunction(0x93C62L,"application_communication_control_callback");
        ensureFunction(0x9542CL,"application_communication_control_subfunction_00");
        ensureFunction(0x9543CL,"application_communication_control_subfunction_01");
        ensureFunction(0x9544CL,"application_communication_control_subfunction_03");
        ensureFunction(0x95154L,"application_communication_control_request_start");
        ensureFunction(0x95DCEL,"application_wdbi_callback");
        ensureFunction(0x95C8CL,"application_wdbi_request_start");
        ensureFunction(0x93CFEL,"application_tester_present_subfunction_00");
        ensureFunction(0x8CCDCL,"application_control_dtc_setting_subfunction_01");
        ensureFunction(0x8CCFAL,"application_control_dtc_setting_subfunction_02");
        ensureFunction(0x8D344L,"application_proprietary_ab_callback");
        ensureFunction(0x96A34L,"application_proprietary_ab_subfunction_01");
        ensureFunction(0x96A56L,"application_proprietary_ab_subfunction_02");
        ensureFunction(0x96A78L,"application_proprietary_ab_subfunction_03");
        ensureFunction(0x8D3CCL,"application_routine_id_lookup");
        ensureFunction(0x4F928L,"application_did_table_getter");
        ensureFunction(0x93910L,"application_uds_negative_response");
        ensureFunction(0x938F8L,"application_uds_request_busy_set");
    }
}
