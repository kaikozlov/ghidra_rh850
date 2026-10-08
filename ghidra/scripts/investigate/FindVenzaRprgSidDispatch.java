//@author kaikozlov
//@category Analysis
// Throwaway: climb references from the known RPRG service handlers up to the
// SID dispatcher, and census which SID bytes the top dispatcher compares.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.RefType;

public class FindVenzaRprgSidDispatch extends GhidraScript {
    private Function fnAt(long a) {
        return getFunctionAt(toAddr(a));
    }
    private String fnName(long a) {
        Function f = fnAt(a);
        return f == null ? "?" : f.getName();
    }
    private void climb(long a, int depth) {
        if (depth > 8) return;
        Address addr = toAddr(a);
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(addr);
        boolean any = false;
        while (it.hasNext()) {
            Reference r = it.next();
            if (r.getReferenceType().isCall() || r.getReferenceType().isJump()) {
                any = true;
                Function caller = getFunctionContaining(r.getFromAddress());
                println(String.format("depth=%d ref %s -> %s (from fn %s)",
                    depth, r.getFromAddress(), addr,
                    caller == null ? "?" : caller.getName() + "@" + caller.getEntryPoint()));
                if (caller != null && r.getReferenceType().isCall()) {
                    climb(caller.getEntryPoint().getOffset(), depth + 1);
                }
            }
        }
        if (!any) println(String.format("depth=%d no call/jump refs to %s", depth, addr));
    }
    @Override
    public void run() throws Exception {
        long[] handlers = {0x0100450eL, 0x01003ee0L, 0x01003f6aL, 0x010063b2L, 0x01004226L, 0x01004382L};
        for (long h : handlers) {
            println("== climb from 0x" + Long.toHexString(h) + " (" + fnName(h) + ")");
            climb(h, 0);
        }
    }
}
