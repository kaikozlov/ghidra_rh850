//@author optskug
//@category Analysis
// Brute-force scan: find every instruction that references the secrets region
// [0x13f00..0x14100] either by a resolved xref, a scalar operand equal to a
// full address in that range, or a movea/addi-style low-16 immediate
// (0x3f00..0x3fff, i.e. the low half of 0x13fxx, which is how movhi+movea
// builds these addresses). Prints counts + sample lines.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.Reference;

public class FindSecretRefs extends GhidraScript {
    @Override
    public void run() throws Exception {
        long lo = 0x13f00L, hi = 0x14100L;
        Listing listing = currentProgram.getListing();
        InstructionIterator it = listing.getInstructions(true);
        int xrefHits = 0, regionScalar = 0, low16 = 0, totalIns = 0;
        java.util.List<String> lines = new java.util.ArrayList<>();
        while (it.hasNext()) {
            Instruction ins = it.next();
            totalIns++;
            // 1. resolved operand references into the region
            int n = ins.getNumOperands();
            for (int op = 0; op < n; op++) {
                for (Reference r : ins.getOperandReferences(op)) {
                    long ta = r.getToAddress().getOffset();
                    if (ta >= lo && ta <= hi) {
                        xrefHits++;
                        if (lines.size() < 50) lines.add(String.format(
                            "XREF   %s  op%d -> 0x%06x  | %s",
                            ins.getAddress(), op, ta, ins.toString()));
                    }
                }
                // 2. scalar operands
                for (Object o : ins.getOpObjects(op)) {
                    if (!(o instanceof Scalar)) continue;
                    long v = ((Scalar) o).getValue();
                    if (v >= lo && v <= hi) {
                        regionScalar++;
                        if (lines.size() < 50) lines.add(String.format(
                            "SCALAR %s  val=0x%06x  | %s",
                            ins.getAddress(), v, ins.toString()));
                    } else if (v >= 0x3f00 && v <= 0x3fff) {
                        low16++;
                        if (lines.size() < 50) lines.add(String.format(
                            "LOW16  %s  imm=0x%04x  | %s",
                            ins.getAddress(), v, ins.toString()));
                    }
                }
            }
        }
        println("FindSecretRefs: scanned " + totalIns + " instructions");
        println("  resolved xrefs into [0x13f00..0x14100]: " + xrefHits);
        println("  scalar operand == full addr in region : " + regionScalar);
        println("  low-16 immediate in 0x3f00..0x3fff     : " + low16);
        for (String s : lines) println("    " + s);
    }
}
