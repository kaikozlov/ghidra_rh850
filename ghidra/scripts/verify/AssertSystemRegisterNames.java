//@author kaikozlov
//@category Verification
// Assert every ldsr/stsr operand is a named system register (no blank/"_").
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;

public class AssertSystemRegisterNames extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] pats = {"ldsr", "stsr", "ldtc", "sttc", "ldvc", "stvc"};
        int total = 0;
        int bad = 0;
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            String m = ins.getMnemonicString();
            if (m == null) continue;
            boolean hit = false;
            for (String p : pats) {
                if (m.contains(p)) { hit = true; break; }
            }
            if (!hit) continue;
            total++;
            for (int op = 0; op < ins.getNumOperands(); op++) {
                String rep = ins.getDefaultOperandRepresentation(op);
                if (rep == null || rep.isBlank() || "_".equals(rep)) {
                    bad++;
                    println("BAD " + ins.getAddress() + " " + m
                            + " op" + op + "='" + rep + "'");
                }
            }
        }
        println("ASSERT system-register-ops: total=" + total + " unnamed=" + bad);
        if (bad != 0) {
            throw new IllegalStateException("unnamed system-register operands: " + bad);
        }
        if (total < 1) {
            throw new IllegalStateException("expected at least one ldsr/stsr in firmware project");
        }
    }
}
