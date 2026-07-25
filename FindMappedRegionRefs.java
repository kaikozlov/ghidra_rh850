//@author optskug
//@category Analysis
// Report all instruction references/scalars into the correctly mapped constant
// table around the two family secrets.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;

public class FindMappedRegionRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        long lo=0xBF80L, hi=0xC040L;
        int refs=0, scalars=0;
        java.util.List<String> lines=new java.util.ArrayList<>();
        InstructionIterator it=currentProgram.getListing().getInstructions(true);
        while(it.hasNext()) {
            Instruction ins=it.next();
            for(int op=0;op<ins.getNumOperands();op++) {
                for(Reference r:ins.getOperandReferences(op)) {
                    long v=r.getToAddress().getOffset();
                    if(v>=lo && v<=hi) {
                        refs++; lines.add(String.format("REF %s -> 0x%04x (%s) | %s",
                            ins.getAddress(),v,r.getReferenceType(),ins));
                    }
                }
                for(Object o:ins.getOpObjects(op)) if(o instanceof Scalar) {
                    Scalar s=(Scalar)o; long v=s.getUnsignedValue();
                    if(v>=lo && v<=hi) {
                        scalars++; lines.add(String.format("SCALAR %s =0x%04x | %s",
                            ins.getAddress(),v,ins));
                    }
                }
            }
        }
        println(String.format("region [0x%x..0x%x]: resolved=%d scalar=%d",lo,hi,refs,scalars));
        for(String s:lines) println("  "+s);
    }
}
