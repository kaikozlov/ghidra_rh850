//@author kaikozlov
//@category Analysis
// Enumerate computed/indirect control transfers with local instruction context.
// This is an analysis aid; call-target provenance still requires reviewing the
// producer instructions and any pointed-to descriptor/table.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.FlowType;

public class ExportIndirectControlTransfers extends GhidraScript {
    @Override
    public void run() throws Exception {
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        InstructionIterator it = listing.getInstructions(true);
        int count = 0;
        while (it.hasNext()) {
            Instruction ins = it.next();
            FlowType flow = ins.getFlowType();
            if (!(flow.isCall() || flow.isJump()) || !flow.isComputed()) {
                continue;
            }
            Function f = fm.getFunctionContaining(ins.getAddress());
            // Ignore decoded bytes that are not owned by a recovered function and
            // compiler switch-table dispatch. The latter is index control, not a
            // function-pointer/control-target primitive.
            if (f == null || "switch".equals(ins.getMnemonicString())) {
                continue;
            }
            count++;
            String fn = f.getName();
            println(String.format("INDIRECT %s %s | %s | flow=%s",
                ins.getAddress(), fn, ins, flow));

            Instruction cur = ins;
            java.util.ArrayList<Instruction> ctx = new java.util.ArrayList<>();
            for (int i = 0; i < 8; i++) {
                cur = cur.getPrevious();
                if (cur == null) break;
                if (f != null && !f.getBody().contains(cur.getAddress())) break;
                ctx.add(cur);
            }
            java.util.Collections.reverse(ctx);
            for (Instruction prev : ctx) {
                println(String.format("  %s | %s", prev.getAddress(), prev));
            }
            println(String.format("  %s | %s", ins.getAddress(), ins));
        }
        println("INDIRECT_COUNT=" + count);
    }
}
