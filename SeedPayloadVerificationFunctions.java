//@author optskug
//@category Analysis
// Seed valid payload-verification code missed by auto-analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

public class SeedPayloadVerificationFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] entries={0x780L,0x51ACL,0x5936L,0x5A04L,0x5B70L,0x5C06L,0x6A06L,0x6EAEL,0x6EBAL,0x7122L};
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
