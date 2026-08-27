//@author ghidra_rh850
//@category Analysis
// Report every recovered Ghidra reference whose destination lies in an inclusive range.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

public class InspectRangeReferences extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException("usage: InspectRangeReferences.java <low> <high-inclusive>");
        }
        long low = Long.decode(args[0]);
        long high = Long.decode(args[1]);
        if (low > high) {
            throw new IllegalArgumentException("low must be <= high");
        }

        ReferenceManager refs = currentProgram.getReferenceManager();
        FunctionManager functions = currentProgram.getFunctionManager();
        int total = 0;
        int application = 0;
        ReferenceIterator it = refs.getReferenceIterator(toAddr(0));
        while (it.hasNext()) {
            Reference ref = it.next();
            Address target = ref.getToAddress();
            long value = target.getOffset();
            if (value < low || value > high) {
                continue;
            }
            total++;
            if (ref.getFromAddress().getOffset() >= 0x20880) {
                application++;
            }
            Function owner = functions.getFunctionContaining(ref.getFromAddress());
            println(String.format(
                "REF from=%s to=%s type=%s fn=%s",
                ref.getFromAddress(), target, ref.getReferenceType(),
                owner == null ? "<none>" : owner.getName() + "@" + owner.getEntryPoint()));
        }
        println("COUNT=" + total + " APP_COUNT=" + application);
    }
}
