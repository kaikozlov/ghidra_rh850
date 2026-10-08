//@author kaikozlov
//@category Analysis
// Throwaway: census of control-flow edges inside the yc Venza RPRG block.
// 1. sample jarl/jmp instructions with their Ghidra flow types,
// 2. list every computed (indirect) call/jump with 3 instructions of context.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.pcode.PcodeOp;

public class CensusVenzaRprgHandoff extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address lo = toAddr(0x01000000L);
        Address hi = toAddr(0x01007587L);

        int jarl = 0, jmp = 0, indirect = 0;
        InstructionIterator ii = currentProgram.getListing().getInstructions(lo, true);
        while (ii.hasNext()) {
            Instruction ins = ii.next();
            if (ins.getAddress().getOffset() > 0x01007587L) break;
            String m = ins.getMnemonicString();
            if (!m.equals("jarl") && !m.equals("jmp")) continue;
            boolean isJarl = m.equals("jarl");
            if (isJarl) jarl++; else jmp++;
            boolean computed = ins.getFlowType().isComputed();
            if (computed) {
                indirect++;
                if (indirect <= 40) {
                    StringBuilder sb = new StringBuilder();
                    sb.append(ins.getAddress()).append(" [").append(ins.getFlowType())
                      .append("] ").append(ins.toString()).append("\n");
                    Instruction prev = ins.getPrevious();
                    for (int k = 0; k < 3 && prev != null; k++) {
                        sb.append("   ").append(prev.getAddress()).append(": ").append(prev.toString()).append("\n");
                        prev = prev.getPrevious();
                    }
                    println(sb.toString());
                }
            }
        }
        println("jarl=" + jarl + " jmp=" + jmp + " computed=" + indirect);
    }
}
