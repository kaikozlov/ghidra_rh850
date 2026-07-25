//@author optskug
//@category Analysis
// Find instructions whose rendered operands contain any requested substring.
// Usage: FindOperandRefs.java -0x6c97 -0x8830 0xfebf0fd0
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;

public class FindOperandRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args=getScriptArgs();
        if (args.length==0) {
            println("usage: FindOperandRefs.java <substring> [substring ...]");
            return;
        }
        Listing listing=currentProgram.getListing();
        FunctionManager fm=currentProgram.getFunctionManager();
        for (Instruction ins: listing.getInstructions(true)) {
            String text=ins.toString().toLowerCase();
            for (String raw: args) {
                String needle=raw.toLowerCase();
                if (text.contains(needle)) {
                    Function f=fm.getFunctionContaining(ins.getAddress());
                    println(ins.getAddress()+"  "+(f==null?"<no-function>":f.getName())+"  "+ins);
                    break;
                }
            }
        }
    }
}
