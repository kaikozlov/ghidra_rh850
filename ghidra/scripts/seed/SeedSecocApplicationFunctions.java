//@author kaikozlov
//@category Analysis
// Seed application SecOC, freshness, CryptoIf, and ICU-S functions missed by auto-analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;

public class SeedSecocApplicationFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] entries={
            0x680F8L,0x68218L,0x682A6L,0x6875EL,0x68B42L,0x68BC2L,0x68D0EL,
            0x68F0CL,0x68F92L,0x68FC2L,0x69018L,0x69068L,0x69246L,0x6926AL,
            0x87A94L,0x87B46L,0x87BBAL,0x87C14L,0x87C70L,0x87CCCL,0x87DD0L,
            0x87ED0L,0x88028L,0x88080L,0x880DCL,0x881DCL,
            0x88302L,0x88350L,0x88508L,0x88556L,
            0x88B5CL,0x88B6AL,0x88B9CL,0x88BA8L,0x88C0AL,
            0x8DB22L,0x8DB84L,0x8DC64L,0x8DE8EL,0x8DEBCL,
            0x8DF0EL,0x8DF84L,0x8E024L,0x8E0BEL,0x8E1A8L,
            0x8E3EAL,0x8E4BAL,0x8E80AL,0x8E8E6L,0x8E942L,
            0x8EA4CL,0x8EBC2L,0x8EECAL,0x8EF9EL,0x8F084L,
            0x8F112L,0x89630L,0x897F4L
        };
        Listing listing=currentProgram.getListing();
        FunctionManager fm=currentProgram.getFunctionManager();
        for(long value: entries) {
            Address a=toAddr(value);
            Instruction containing=listing.getInstructionContaining(a);
            if(containing!=null && !containing.getMinAddress().equals(a))
                listing.clearCodeUnits(containing.getMinAddress(),containing.getMaxAddress(),false);
            if(listing.getInstructionAt(a)==null && !disassemble(a))
                throw new IllegalStateException("disassembly failed at "+a);
            Function f=fm.getFunctionAt(a);
            if(f==null) f=createFunction(a,null);
            if(f==null) throw new IllegalStateException("function creation failed at "+a);
            println(a+" "+f.getName());
        }
    }
}
