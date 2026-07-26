//@author kaikozlov
//@category Analysis
// Seed helper functions used by the completed bootloader diagnostic services.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;

public class SeedBootloaderDiagnosticFunctions extends GhidraScript {
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
        ensureFunction(0x159EL,"bootloader_hard_reset_wait");
        ensureFunction(0x4188L,"flash_program_start");
        ensureFunction(0x4276L,"flash_program_queue_bytes");
        ensureFunction(0x4B38L,"transfer_data_negative_response_and_abort");
        ensureFunction(0x4CA2L,"transfer_data_compare_request");
        ensureFunction(0x4E92L,"transfer_data_compare_task");
        ensureFunction(0x4F1CL,"transfer_data_task_dispatch");
        ensureFunction(0x4FBAL,"tester_present_negative_response");
        ensureFunction(0x4FCEL,"tester_present_positive_response");
        ensureFunction(0x51D8L,"bootloader_set_diagnostic_session");
        ensureFunction(0x5286L,"program_region_validity_marker");
        ensureFunction(0x5630L,"routine_control_negative_response");
        ensureFunction(0x5644L,"routine_control_positive_response");
        ensureFunction(0x6084L,"ecu_reset_negative_response");
        ensureFunction(0x6098L,"ecu_reset_positive_response");
        ensureFunction(0x67DAL,"bootloader_reset_after_response");
        ensureFunction(0x684CL,"communication_control_negative_response");
        ensureFunction(0x6860L,"communication_control_positive_response");
        ensureFunction(0x68FCL,"control_dtc_setting_negative_response");
        ensureFunction(0x6910L,"control_dtc_setting_positive_response");
        ensureFunction(0x6C6CL,"memory_compare_enqueue");
        ensureFunction(0x6C8EL,"memory_compare_task");
    }
}
