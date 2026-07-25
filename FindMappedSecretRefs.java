//@author optskug
//@category Analysis
// Scan correctly mapped CodeFlash for direct/resolved/scalar references to
// PAYLOAD_BUILD_SECRET @ 0xBFD8 and SEED_KEY_SECRET @ 0xBFE8.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;

public class FindMappedSecretRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] targets = {0xBFD8L, 0xBFE8L};
        String[] names = {"PAYLOAD_BUILD_SECRET", "SEED_KEY_SECRET"};
        int[] refs = new int[2], scalars = new int[2];
        java.util.List<String> lines = new java.util.ArrayList<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        int total = 0;
        while (it.hasNext()) {
            Instruction ins = it.next(); total++;
            for (int op = 0; op < ins.getNumOperands(); op++) {
                for (Reference r : ins.getOperandReferences(op)) {
                    long dst = r.getToAddress().getOffset();
                    for (int i=0; i<targets.length; i++) if (dst == targets[i]) {
                        refs[i]++;
                        lines.add(String.format("REF    %-20s %s -> %s | %s",
                            names[i], ins.getAddress(), r.getToAddress(), ins));
                    }
                }
                for (Object o : ins.getOpObjects(op)) {
                    if (!(o instanceof Scalar)) continue;
                    Scalar s = (Scalar)o;
                    long uv = s.getUnsignedValue();
                    long sv = s.getSignedValue();
                    for (int i=0; i<targets.length; i++) if (uv == targets[i] || sv == targets[i]) {
                        scalars[i]++;
                        lines.add(String.format("SCALAR %-20s %s op%d unsigned=0x%x signed=%d | %s",
                            names[i], ins.getAddress(), op, uv, sv, ins));
                    }
                }
            }
        }
        println("FindMappedSecretRefs: scanned " + total + " instructions");
        for (int i=0; i<targets.length; i++) {
            println(String.format("  %s @0x%x: resolved=%d scalar=%d",
                names[i], targets[i], refs[i], scalars[i]));
        }
        for (String line : lines) println("    " + line);
    }
}
