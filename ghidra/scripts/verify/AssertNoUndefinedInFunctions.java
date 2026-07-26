//@author kaikozlov
//@category Verification
// Assert: zero undefined bytes inside function bodies. Throws on failure so
// headless/CLI exits nonzero. Companion to FindUndefinedInFunctions.java.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class AssertNoUndefinedInFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        long totalFuncs = 0, funcsWithUndef = 0, totalUndef = 0;
        Address first = null;
        while (it.hasNext()) {
            Function f = it.next();
            totalFuncs++;
            int funcUndef = 0;
            for (AddressRange r : f.getBody()) {
                Address a = r.getMinAddress();
                Address max = r.getMaxAddress();
                while (a.compareTo(max) <= 0) {
                    CodeUnit cu = listing.getCodeUnitAt(a);
                    if (cu == null) {
                        funcUndef++;
                        if (first == null) first = a;
                        a = a.add(1);
                    } else {
                        a = cu.getMaxAddress().add(1);
                    }
                }
            }
            if (funcUndef > 0) {
                funcsWithUndef++;
                totalUndef += funcUndef;
            }
        }
        println("ASSERT undefined-in-functions: funcs=" + totalFuncs
                + " bad_funcs=" + funcsWithUndef + " undef_bytes=" + totalUndef);
        if (totalUndef != 0) {
            throw new IllegalStateException(
                "undefined bytes inside function bodies: " + totalUndef
                + " (first @ " + first + ")");
        }
    }
}
