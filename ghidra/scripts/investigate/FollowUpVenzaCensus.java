//@author kaikozlov
//@category Analysis
// Follow-up to CensusVenzaSecureService: resolve the two newly found
// secure-service request builders (descriptor bases FEFF01E8 / FEFF0250),
// extract each adapter's opcode stores, and enumerate direct callers of all
// five lower adapters plus the queue/trigger helpers. Read-only.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.List;

public class FollowUpVenzaCensus extends GhidraScript {
    private void disasmRange(long lo, long hi) {
        Address a = toAddr(lo);
        while (a.getOffset() < hi) {
            Instruction ins = getInstructionAt(a);
            if (ins == null) {
                a = a.add(2);
                continue;
            }
            println("D " + ins.getAddress() + " " + ins);
            a = ins.getMaxAddress().add(1);
        }
    }

    private void callersOf(long dest, String label) {
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(dest));
        println("CALLERS " + label + " (" + String.format("0x%x", dest) + "):");
        boolean any = false;
        while (it.hasNext()) {
            Reference r = it.next();
            Function f = getFunctionContaining(r.getFromAddress());
            println("  " + r.getFromAddress() + " [" + r.getReferenceType() + "] "
                + (f == null ? "None" : f.getName() + "@" + f.getEntryPoint()));
            any = true;
        }
        if (!any) println("  (none)");
    }

    @Override
    public void run() throws Exception {
        // Function containment of the new call sites after the closure pass.
        for (long site : new long[]{0xbd98cL, 0xbdb2cL, 0xbdd50L, 0xbdfa4L, 0xbe1b8L}) {
            Function f = getFunctionContaining(toAddr(site));
            println("SITE " + String.format("0x%x", site) + " -> "
                + (f == null ? "None" : f.getName() + "@" + f.getEntryPoint() + " body=" + f.getBody()));
        }

        // New builder #1: expect function body roughly 0xbd900..0xbd9b6.
        println("== disasm 0xbd8f0..0xbd9c0 ==");
        disasmRange(0xbd8f0L, 0xbd9c0L);
        // New builder #2: roughly 0xbda90..0xbdb5a.
        println("== disasm 0xbda80..0xbdb5a ==");
        disasmRange(0xbda80L, 0xbdb5aL);

        // Adapter entry callers for the ownership map.
        callersOf(0xbdc7aL, "MAC-generate adapter");
        callersOf(0xbde88L, "MAC-verify adapter");
        callersOf(0xbe0ccL, "key-update adapter");
        callersOf(0xbd69eL, "convergence");
        callersOf(0x8a18aL, "enqueue");
        // Resolve callers of the new builders once their entries are known:
        // probe both possible entries discovered from SITE lines.
        for (long probe : new long[]{0xbd920L, 0xbd936L, 0xbd94eL, 0xbda90L, 0xbdaaeL, 0xbdac6L}) {
            ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(probe));
            int n = 0;
            while (it.hasNext()) {
                Reference r = it.next();
                Function f = getFunctionContaining(r.getFromAddress());
                println("PROBE " + String.format("0x%x", probe) + " <- " + r.getFromAddress()
                    + " [" + r.getReferenceType() + "] "
                    + (f == null ? "None" : f.getName() + "@" + f.getEntryPoint()));
                n++;
            }
            if (n == 0) println("PROBE " + String.format("0x%x", probe) + " <- (none)");
        }
        println("FOLLOWUP complete");
    }
}
