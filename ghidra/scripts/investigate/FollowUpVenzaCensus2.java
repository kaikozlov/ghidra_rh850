//@author kaikozlov
//@category Analysis
// Final airbag follow-up: consumers of the two newly identified secure services
// (opcode 0x10 @ entry 0xBD8C8, opcode 0x04 @ entry 0xBDA6E), their registry
// records, and their completion callbacks. Read-only.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class FollowUpVenzaCensus2 extends GhidraScript {
    private void refsTo(long dest) {
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(dest));
        println("REFS " + String.format("0x%x", dest) + ":");
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

    private void disasmRange(long lo, long hi) {
        Address a = toAddr(lo);
        while (a.getOffset() < hi) {
            Instruction ins = getInstructionAt(a);
            if (ins == null) { a = a.add(2); continue; }
            println("D " + ins.getAddress() + " " + ins);
            a = ins.getMaxAddress().add(1);
        }
    }

    @Override
    public void run() throws Exception {
        // Registry records and sync-pointer cells for the five services.
        long[] cells = {0x1c7fcL, 0x1c840L, 0x1c884L, 0x1c8a8L, 0x1c8c8L,
                        0x1c7e4L, 0x1c828L, 0x1c86cL, 0x1c8b0L, 0x1c8f4L};
        for (long c : cells) refsTo(c);
        // New service entries and their step partners.
        refsTo(0xbd8c8L);
        refsTo(0xbd776L);
        refsTo(0xbda6eL);
        refsTo(0xbd9beL);
        // Known dispatchers (from the prior session) for ownership cross-check.
        refsTo(0xbccf4L);
        refsTo(0xbcefaL);
        refsTo(0xbd2ecL);
        // Completion callbacks embedded in the two new descriptors.
        println("== callback 0xbd86c (opcode 0x10 record) ==");
        disasmRange(0xbd86cL, 0xbd8c8L);
        println("== callback 0xbda32 (opcode 0x04 record) ==");
        disasmRange(0xbda32L, 0xbda6eL);
        println("FOLLOWUP2 complete");
        // Runner-layer callers (runner pointer table lives at 0x1c7c0..0x1c7e0).
        long[] runners = {0xbd24aL, 0xbcd8aL, 0xbcf8eL, 0xbd17cL, 0xbd37cL,
                          0xbce20L, 0xbd024L, 0xbd212L, 0xbd412L};
        for (long r : runners) {
            ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(toAddr(r));
            StringBuilder sb = new StringBuilder();
            boolean any = false;
            while (it.hasNext()) {
                Reference ref = it.next();
                Function f = getFunctionContaining(ref.getFromAddress());
                sb.append(" ").append(ref.getFromAddress()).append("[")
                  .append(ref.getReferenceType()).append(":")
                  .append(f == null ? "None" : f.getName() + "@" + f.getEntryPoint()).append("]");
                any = true;
            }
            println("RUNNER " + String.format("0x%x", r) + (any ? sb : " (no refs)"));
        }
        println("FOLLOWUP2 complete");
    }
}