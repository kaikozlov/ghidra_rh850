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
        f.setCallingConvention("__stdcall");
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
        ensureFunction(0x8B1F0L,"application_clear_diagnostic_information_callback");
        ensureFunction(0x8B144L,"application_clear_diagnostic_information_request_start");
        ensureFunction(0x8AF28L,"application_clear_diagnostic_information_prepare_stage");
        ensureFunction(0x8B014L,"application_clear_diagnostic_information_commit_stage");
        ensureFunction(0x945DCL,"application_rdbi_callback");
        ensureFunction(0x8B5AAL,"application_read_dtc_subfunction_01");
        ensureFunction(0x8BA2AL,"application_read_dtc_subfunction_02");
        ensureFunction(0x8BD94L,"application_read_dtc_subfunction_03");
        ensureFunction(0x8C326L,"application_read_dtc_subfunction_04");
        ensureFunction(0x948AAL,"application_read_memory_by_address_callback");
        ensureFunction(0x9479AL,"application_read_memory_by_address_request_start");
        ensureFunction(0x946FAL,"application_read_memory_by_address_request_poll");
        ensureFunction(0x94E32L,"application_security_access_subfunction_01");
        ensureFunction(0x94E46L,"application_security_access_subfunction_02");
        ensureFunction(0x94E5AL,"application_security_access_subfunction_03");
        ensureFunction(0x94E6EL,"application_security_access_subfunction_04");
        ensureFunction(0x9497CL,"application_security_access_request_seed");
        ensureFunction(0x94A72L,"application_security_access_send_key");
        ensureFunction(0x93C62L,"application_wdbi_callback");
        ensureFunction(0x9542CL,"application_communication_control_subfunction_00");
        ensureFunction(0x9543CL,"application_communication_control_subfunction_01");
        ensureFunction(0x9544CL,"application_communication_control_subfunction_03");
        ensureFunction(0x95154L,"application_communication_control_request_start");
        ensureFunction(0x95DCEL,"application_routine_control_callback");
        ensureFunction(0x95C8CL,"application_routine_control_request_start");
        ensureFunction(0x93CFEL,"application_tester_present_subfunction_00");
        ensureFunction(0x8CCDCL,"application_control_dtc_setting_subfunction_01");
        ensureFunction(0x8CCFAL,"application_control_dtc_setting_subfunction_02");
        ensureFunction(0x8D344L,"application_proprietary_ba_callback");
        ensureFunction(0x96A34L,"application_proprietary_ab_subfunction_01");
        ensureFunction(0x96A56L,"application_proprietary_ab_subfunction_02");
        ensureFunction(0x96A78L,"application_proprietary_ab_subfunction_03");
        ensureFunction(0x8D3CCL,"application_routine_id_lookup");

        // The dormant RoutineControl worker's 13 bounded RID callback pairs.
        // Auto-analysis does not treat all table words as entry-point seeds, so
        // create the functions explicitly before semantic annotation/decompilation.
        long[][] routineCallbacks={
            {0x0204L,0x4EC16L,0x4EC2AL},
            {0x2001L,0x4EC46L,0x4EC78L},
            {0x2002L,0x4ECBCL,0x4ECD0L},
            {0x2005L,0x4ED2CL,0x4ED40L},
            {0x2006L,0x4ED76L,0x4ED8AL},
            {0x2007L,0x4EDC0L,0x4EDD4L},
            {0x2008L,0x4EE0AL,0x4EE1EL},
            {0x2009L,0x4EE54L,0x4EE68L},
            {0x200DL,0x4EEA6L,0x4EEBAL},
            {0x2010L,0x4EEF0L,0x4EF04L},
            {0x2012L,0x4EF4AL,0x4EF4EL},
            {0x2013L,0x4EF68L,0x4EF90L},
            {0x2014L,0x4EFACL,0x4EFD4L},
        };
        for (long[] row:routineCallbacks) {
            String rid=String.format("%04x",row[0]);
            ensureFunction(row[1],"application_routine_"+rid+"_start");
            ensureFunction(row[2],"application_routine_"+rid+"_result");
        }

        // Direct descendants referenced by those callbacks but missed as
        // function entries by the base analysis.
        long[] diagnosticHelpers={
            0x4EC5AL,0x4EC68L,0x4C4A4L,
            0xFDE58L,0xFDED0L,
            0xFE04CL,0xFE060L,0xFE09CL,0xFE0C4L,
            0xFE1B4L,0xFE1C8L,0xFE2A4L,
            0xB5D0CL,0xB28A2L,0xB39BEL,0xB47A6L,0xB7C0EL,
            0xB55C4L,0xB71FEL,0xB76A8L,0xB5644L,
            0x936AAL,0x936D6L,0x8A482L,0x8A542L,0x8A630L,0x8D416L,
            0x34B74L,0x34B9AL,0xB201AL,
        };
        for (long address:diagnosticHelpers) {
            ensureFunction(address,String.format("application_diagnostic_helper_%05x",address));
        }

        ensureFunction(0x4F928L,"application_did_table_getter");
        ensureFunction(0x93910L,"application_uds_negative_response");
        ensureFunction(0x938F8L,"application_uds_request_busy_set");
    }
}
