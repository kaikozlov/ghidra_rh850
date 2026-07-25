//@author optskug
//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;

public class FindHandlerRegistrations extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] vals={0x4b38,0x5630,0x5c54,0x5d2c,0x6136};
        String[] names={"SID36","SID31","SID37","SID34","SID10"};
        int[] n=new int[vals.length];
        InstructionIterator it=currentProgram.getListing().getInstructions(toAddr(0),true);
        while(it.hasNext()) {
            Instruction ins=it.next();
            if(ins.getAddress().getOffset()>=0x20000L) break;
            for(int op=0;op<ins.getNumOperands();op++) for(Object o:ins.getOpObjects(op)) {
                if(!(o instanceof Scalar)) continue;
                Scalar s=(Scalar)o; long u=s.getUnsignedValue();
                for(int i=0;i<vals.length;i++) if(u==vals[i]) {
                    n[i]++; Function f=currentProgram.getFunctionManager().getFunctionContaining(ins.getAddress());
                    println(String.format("%s target=0x%x used at %s in %s | %s",names[i],vals[i],
                        ins.getAddress(),f==null?"<none>":f.getName(),ins));
                }
            }
        }
        for(int i=0;i<vals.length;i++) println(names[i]+" count="+n[i]);
    }
}
