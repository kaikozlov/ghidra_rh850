//@author kaikozlov
//@category Analysis
// Seed valid SecOC-associated NvM functions missed by auto-analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class SeedSecocNvmFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] entries={0x65C84L,0x66DB2L};
        for (long value: entries) {
            Address a=toAddr(value);
            if (getInstructionAt(a)==null && !disassemble(a))
                throw new IllegalStateException("disassembly failed at "+a);
            Function f=getFunctionAt(a);
            if (f==null) f=createFunction(a,null);
            if (f==null) throw new IllegalStateException("function creation failed at "+a);
            println(a+" "+f.getName());
        }
    }
}
