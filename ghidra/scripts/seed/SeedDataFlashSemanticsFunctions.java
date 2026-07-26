//@author kaikozlov
//@category Analysis
// Seed DataFlash/RAM range validators missed by automatic analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;

public class SeedDataFlashSemanticsFunctions extends GhidraScript {
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

    @Override public void run() throws Exception {
        ensureFunction(0x4EA78L,"application_ram_range_allowed");
        ensureFunction(0x4EAD8L,"application_dataflash_range_allowed");
    }
}
