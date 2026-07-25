//@author kaikozlov
//@category Analysis
// Find bootloader (<0x20000) instructions using distinctive UDS service/DID constants.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;

public class FindBootloaderDiagnostics extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] vals={0x10,0x27,0x2e,0x31,0x34,0x36,0x37,0x201,0x202,0x203,0xf0,0xf1,0xf186};
        String[] names={"SID_10","SID_27","SID_2E","SID_31","SID_34","SID_36","SID_37","DID_201","DID_202","DID_203","SUB_F0","SUB_F1","DID_F186"};
        int[] counts=new int[vals.length];
        java.util.List<String> lines=new java.util.ArrayList<>();
        InstructionIterator it=currentProgram.getListing().getInstructions(toAddr(0),true);
        while(it.hasNext()) {
            Instruction ins=it.next();
            if(ins.getAddress().getOffset()>=0x20000L) break;
            for(int op=0;op<ins.getNumOperands();op++) for(Object o:ins.getOpObjects(op)) {
                if(!(o instanceof Scalar)) continue;
                long u=((Scalar)o).getUnsignedValue();
                for(int i=0;i<vals.length;i++) if(u==vals[i]) {
                    counts[i]++;
                    Function f=currentProgram.getFunctionManager().getFunctionContaining(ins.getAddress());
                    lines.add(String.format("%-8s %s %-18s | %s", names[i],ins.getAddress(),
                        f==null?"<no-func>":f.getName(),ins));
                }
            }
        }
        for(int i=0;i<vals.length;i++) println(names[i]+" count="+counts[i]);
        for(String s:lines) println("  "+s);
    }
}
