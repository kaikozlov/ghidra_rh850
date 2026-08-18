//@author kaikozlov
//@category Analysis
// Classify recovered function-owned computed calls by tracing the call-target
// register backwards to its nearest definitions. This is intentionally a
// conservative provenance aid rather than a full data-flow proof.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.lang.Register;
import ghidra.program.model.symbol.FlowType;
import ghidra.program.model.symbol.Reference;

public class ClassifyComputedCallTargets extends GhidraScript {
    private boolean writesRegister(Instruction ins, Register wanted) {
        for (Object o : ins.getResultObjects()) {
            if (o instanceof Register && ((Register)o).equals(wanted)) return true;
        }
        return false;
    }

    private Register firstInputRegister(Instruction ins) {
        // For RH850 computed jarl/jmp, operand zero owns the target register.
        if (ins.getNumOperands() > 0) {
            for (Object o : ins.getOpObjects(0)) {
                if (o instanceof Register) return (Register)o;
            }
        }
        for (Object o : ins.getInputObjects()) {
            if (o instanceof Register) return (Register)o;
        }
        return null;
    }

    private String refs(Instruction ins) {
        java.util.ArrayList<String> out = new java.util.ArrayList<>();
        for (int op = 0; op < ins.getNumOperands(); op++) {
            for (Reference r : ins.getOperandReferences(op)) {
                out.add(String.format("%s->%s", r.getReferenceType(), r.getToAddress()));
            }
        }
        return String.join(",", out);
    }

    @Override
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        InstructionIterator it = listing.getInstructions(true);
        int calls = 0;
        while (it.hasNext()) {
            Instruction call = it.next();
            FlowType flow = call.getFlowType();
            if (!flow.isCall() || !flow.isComputed()) continue;
            Function f = fm.getFunctionContaining(call.getAddress());
            if (f == null) continue;
            Register target = firstInputRegister(call);
            if (target == null) continue;
            calls++;
            println(String.format("CALL %s %s target=%s | %s",
                call.getAddress(), f.getName(), target.getName(), call));

            Instruction cur = call;
            int seen = 0;
            Register trace = target;
            while (seen < 24) {
                cur = cur.getPrevious();
                if (cur == null || !f.getBody().contains(cur.getAddress())) break;
                seen++;
                if (!writesRegister(cur, trace)) continue;
                String rs = refs(cur);
                println(String.format("  DEF %s %s | refs=%s", cur.getAddress(), cur, rs));

                // Follow simple register copies backwards. Stop after loads,
                // immediates, arithmetic, or any non-copy definition.
                String m = cur.getMnemonicString();
                if ("mov".equals(m)) {
                    Register src = null;
                    if (cur.getNumOperands() > 0) {
                        for (Object o : cur.getOpObjects(0)) {
                            if (o instanceof Register) { src = (Register)o; break; }
                        }
                    }
                    if (src != null) {
                        trace = src;
                        continue;
                    }
                }
                break;
            }
        }
        println("COMPUTED_CALL_COUNT=" + calls);
    }
}
