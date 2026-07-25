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
        ensureFunction(0x4E8E4L,"application_read_f181");
        ensureFunction(0x4E90AL,"application_read_f186");
        ensureFunction(0x4E918L,"application_read_f18c");
        ensureFunction(0x93FF6L,"application_session_default_callback");
        ensureFunction(0x94006L,"application_session_programming_callback");
        ensureFunction(0x94016L,"application_session_extended_callback");
        ensureFunction(0x93F9AL,"application_session_transition_background_poll");
        ensureFunction(0xB20EAL,"system_programming_shutdown_mode_entry");
    }
}
