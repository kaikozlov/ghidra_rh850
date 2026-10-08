//@author kaikozlov
//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;

public class FollowUpVenzaOpcodes extends GhidraScript {
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
        disasmRange(0xbdcc0L, 0xbdd60L);  // MAC-generate adapter tail
        disasmRange(0xbe130L, 0xbe1c0L);  // key-update adapter tail
        println("OPCODES complete");
    }
}
