//@author kaikozlov
//@category Analysis
// Throwaway: dump every cmp-with-immediate and every register-target jarl/jmp
// in the venza RPRG extended-user block (boot.bin @ 0x01000000..0x01007587).

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;

public class CensusVenzaRprgSidBytes extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address lo = toAddr(0x01000000L);
        Address hi = toAddr(0x01007587L);
        InstructionIterator it = currentProgram.getListing().getInstructions(new AddressSet(lo, hi), true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            String m = ins.getMnemonicString();
            if (m.equals("cmp") || m.equals("cmp.i") || m.equals("setf")) {
                for (int i = 0; i < ins.getNumOperands(); i++) {
                    for (Object o : ins.getOpObjects(i)) {
                        if (o instanceof Scalar && ins.getAddress().getOffset() < 0x01008000L) {
                            long v = ((Scalar) o).getValue();
                            if (v >= 0x10 && v <= 0x7f) {
                                println("CMP " + ins.getAddress() + " " + ins);
                            }
                        }
                    }
                }
            }
            if (m.equals("jarl") || m.equals("jmp")) {
                String rep = ins.toString();
                // indirect: destination operand is a register, not 0x address
                String dst = rep.contains(",") ? rep.substring(rep.lastIndexOf(",") + 1).trim() : "";
                boolean hasAddrTarget = false;
                for (int i = 0; i < ins.getNumOperands(); i++) {
                    for (Object o : ins.getOpObjects(i)) {
                        if (o instanceof ghidra.program.model.address.Address) hasAddrTarget = true;
                    }
                }
                if (!hasAddrTarget) println("IND " + ins.getAddress() + " " + rep);
            }
        }
    }
}
