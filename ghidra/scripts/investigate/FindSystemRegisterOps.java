//@author kaikozlov
//@category Analysis
// Enumerate every system-register transfer instruction (ldsr/stsr/ldtc/sttc/
// ldvc/stvc) across the whole program and report its address, mnemonic,
// operand display, and containing function. Used to verify the selID register
// tables in v850e3.sinc against actual P1M-E firmware usage: an unnamed ("_")
// or mis-named system register shows up as a blank/raw operand here.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;

public class FindSystemRegisterOps extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] pats = {"ldsr", "stsr", "ldtc", "sttc", "ldvc", "stvc"};
        java.util.Map<String, Integer> counts = new java.util.TreeMap<>();
        java.util.List<String> lines = new java.util.ArrayList<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            String m = ins.getMnemonicString();
            if (m == null) continue;
            boolean hit = false;
            for (String p : pats) if (m.contains(p)) { hit = true; break; }
            if (!hit) continue;
            counts.merge(m, 1, Integer::sum);
            Function f = currentProgram.getFunctionManager().getFunctionContaining(ins.getAddress());
            StringBuilder ops = new StringBuilder();
            for (int op = 0; op < ins.getNumOperands(); op++) {
                if (op > 0) ops.append(" | ");
                ops.append("[").append(op).append("]=").append(ins.getDefaultOperandRepresentation(op));
            }
            lines.add(String.format("%-10s %-10s %s | %s",
                ins.getAddress(), m, ops,
                f == null ? "<no-func>" : f.getName()));
        }
        println("== system-register instruction counts ==");
        for (var e : counts.entrySet()) println(String.format("  %-12s %d", e.getKey(), e.getValue()));
        println("== all occurrences ==");
        for (String s : lines) println("  " + s);
    }
}
