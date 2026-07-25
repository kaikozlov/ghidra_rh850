//@author optskug
//@category Analysis
// Seed valid CAN/CanIf/CanTp callback and RSCFD receive code missed by auto-analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class SeedCanTransportFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        // 0x3FB0 is a missing basic block within the existing RSCFD receive helper.
        Address block=toAddr(0x3FB0L);
        if (getInstructionAt(block)==null && !disassemble(block))
            throw new IllegalStateException("disassembly failed at "+block);

        long[] entries={0x1EEEL,0x1F0CL,0x2F1CL,0x400AL};
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
