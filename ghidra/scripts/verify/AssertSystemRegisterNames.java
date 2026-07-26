//@author kaikozlov
//@category Verification
// Assert every ldsr/stsr operand is a named system register (no blank/"_").
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

public class AssertSystemRegisterNames extends GhidraScript {
    private static final Set<String> EXPECTED = Set.of(
        "PSW", "EIPC", "EIPSW", "FEPC", "FEPSW", "CTPC", "CTPSW",
        "EIIC", "FEIC", "EIWR", "FEWR", "CTBP", "BSEL",
        "EBASE", "INTBP", "MCTL", "SCCFG", "SCBP", "SPID", "FPIPR",
        "MEA", "MEI", "ASID", "IMSR", "INTCFG",
        "ICTAGL", "ICTAGH", "ICDATL", "ICDATH", "ICCTRL", "ICERR",
        "MPM", "MPRC", "MCA", "MCS", "MCR",
        "MPAT0", "MPAT1", "MPAT2", "MPAT3", "MPAT4", "MPAT5", "MPAT6", "MPAT7",
        "MPAT8", "MPAT9", "MPAT10", "MPAT11", "MPAT12", "MPAT13", "MPAT14", "MPAT15",
        "MPLA0", "MPLA1", "MPLA2", "MPLA3", "MPLA4", "MPLA5", "MPLA6", "MPLA7",
        "MPLA8", "MPLA9", "MPLA10", "MPLA11", "MPLA12", "MPLA13", "MPLA14", "MPLA15",
        "MPUA0", "MPUA1", "MPUA2", "MPUA3", "MPUA4", "MPUA5", "MPUA6", "MPUA7",
        "MPUA8", "MPUA9", "MPUA10", "MPUA11", "MPUA12", "MPUA13", "MPUA14", "MPUA15",
        "RDBCR", "FPSR", "FPEC", "FPEPC"
    );

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
            List<String> reps = new ArrayList<>();
            int namedSystemRegisters = 0;
            for (int op = 0; op < ins.getNumOperands(); op++) {
                String rep = ins.getDefaultOperandRepresentation(op);
                reps.add(rep);
                if (rep == null || rep.isBlank() || "_".equals(rep)) {
                    bad++;
                    println("BAD " + ins.getAddress() + " " + m
                            + " op" + op + "='" + rep + "'");
                }
                if (rep != null && EXPECTED.contains(rep.trim())) {
                    namedSystemRegisters++;
                }
            }
            if (namedSystemRegisters != 1) {
                bad++;
                println("BAD " + ins.getAddress() + " " + m
                        + " expected exactly one audited system-register operand, got "
                        + namedSystemRegisters + " in " + reps);
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
