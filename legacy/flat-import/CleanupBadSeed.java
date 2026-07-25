//@author kaikozlov
//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;

public class CleanupBadSeed extends GhidraScript {
    @Override
    public void run() throws Exception {
        // 0x1F2 decoded as erased flash (0x0000 0xffffffff...) — not a real
        // reset handler in this dump. Remove the bogus function + its code units.
        Address a = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x1f2L);
        int removed = 0;
        ghidra.program.model.listing.Function f =
            currentProgram.getFunctionManager().getFunctionAt(a);
        if (f != null) {
            currentProgram.getFunctionManager().removeFunction(a);
            removed++;
        }
        // clear any instructions we forced over the erased region (0x1f2..0x211)
        currentProgram.getListing().clearCodeUnits(
            a, a.add(0x40), false);
        println("CleanupBadSeed: removed_function_at_0x1f2=" + removed);
    }
}
