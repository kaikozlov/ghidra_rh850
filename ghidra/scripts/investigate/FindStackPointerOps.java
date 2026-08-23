//@author kaikozlov
//@category Analysis
// Enumerate non-prologue/epilogue instructions that explicitly reference SP.
// Used to recover stack/context initialization and switching semantics without
// mistaking raw instruction bytes for pointer literals.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;

public class FindStackPointerOps extends GhidraScript {
    @Override
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        InstructionIterator it = listing.getInstructions(true);
        int count = 0, defs = 0;
        while (it.hasNext()) {
            Instruction ins = it.next();
            String m = ins.getMnemonicString();
            if (m == null || m.equals("prepare") || m.equals("dispose")) continue;
            boolean hasSp = false;
            StringBuilder ops = new StringBuilder();
            for (int i = 0; i < ins.getNumOperands(); i++) {
                String rep = ins.getDefaultOperandRepresentation(i);
                if (rep != null && rep.matches("(?i).*(^|[^a-z0-9_])sp([^a-z0-9_]|$).*$")) hasSp = true;
                if (i > 0) ops.append(" | ");
                ops.append("[").append(i).append("]=").append(rep);
            }
            if (!hasSp) continue;
            Function f = fm.getFunctionContaining(ins.getAddress());
            String fname = f == null ? "<no-func>" : f.getName();
            println(String.format("SPREF %s %-10s %s | %s", ins.getAddress(), m, ops, fname));
            count++;
            if (ins.getNumOperands() > 0) {
                String last = ins.getDefaultOperandRepresentation(ins.getNumOperands() - 1);
                if (last != null && last.equalsIgnoreCase("sp") &&
                    (m.equalsIgnoreCase("mov") || m.equalsIgnoreCase("movea") ||
                     m.equalsIgnoreCase("addi") || m.equalsIgnoreCase("add") ||
                     m.equalsIgnoreCase("sub") || m.equalsIgnoreCase("ori") ||
                     m.equalsIgnoreCase("andi") || m.equalsIgnoreCase("xori") ||
                     m.equalsIgnoreCase("shl") || m.equalsIgnoreCase("shr"))) {
                    println(String.format("SPDEF %s %-10s %s | %s", ins.getAddress(), m, ops, fname));
                    defs++;
                }
            }
        }
        println("SPREF_COUNT=" + count);
        println("SPDEF_COUNT=" + defs);
    }
}
