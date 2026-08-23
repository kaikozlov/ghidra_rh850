//@author kaikozlov
//@category Analysis
// Census exception-return instructions and direct flow references into the
// unauthenticated application XCP LocalRAM placement window.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class FindExceptionAndXcpFlowOps extends GhidraScript {
  public void run() throws Exception {
    Listing l = currentProgram.getListing();
    FunctionManager fm = currentProgram.getFunctionManager();
    long lo = 0xFEBF7C00L, hi = 0xFEBFFBFFL;
    int ret = 0, flow = 0;
    InstructionIterator it = l.getInstructions(true);
    while (it.hasNext()) {
      Instruction ins = it.next();
      String m = ins.getMnemonicString().toLowerCase();
      if (m.equals("eiret") || m.equals("feret") || m.equals("ctret")) {
        Function f=fm.getFunctionContaining(ins.getAddress());
        println("RET " + ins.getAddress() + " " + m + " " + (f==null?"<no-func>":f.getName()));
        ret++;
      }
      for (Reference r: ins.getReferencesFrom()) {
        if (!r.getReferenceType().isFlow()) continue;
        Address a=r.getToAddress();
        if (!a.getAddressSpace().isMemorySpace()) continue;
        long v=a.getUnsignedOffset();
        if (Long.compareUnsigned(v,lo)>=0 && Long.compareUnsigned(v,hi)<=0) {
          Function f=fm.getFunctionContaining(ins.getAddress());
          println("FLOW " + ins.getAddress() + " -> " + a + " " + r.getReferenceType() + " " + (f==null?"<no-func>":f.getName()));
          flow++;
        }
      }
    }
    println("RET_COUNT="+ret);
    println("XCP_DIRECT_FLOW_COUNT="+flow);
  }
}
