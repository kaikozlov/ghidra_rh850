//@author kaikozlov
//@category Analysis
// Read-only xref inspector for one or more addresses.
// Usage: InspectAddressReferences.java <address> [address...]

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

public class InspectAddressReferences extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length == 0) {
            throw new IllegalArgumentException(
                "usage: InspectAddressReferences.java <address> [address...]"
            );
        }
        for (String arg : args) {
            long raw = Long.decode(arg);
            Address target = currentProgram.getAddressFactory()
                .getDefaultAddressSpace().getAddress(raw);
            println("TARGET " + target);
            int count = 0;
            ReferenceIterator refs = currentProgram.getReferenceManager().getReferencesTo(target);
            while (refs.hasNext()) {
                Reference ref = refs.next();
                Function containing = getFunctionContaining(ref.getFromAddress());
                String function = containing == null
                    ? "<no-function>"
                    : containing.getName() + "@" + containing.getEntryPoint();
                println(String.format(
                    "REF from=%s type=%s primary=%s source=%s function=%s",
                    ref.getFromAddress(), ref.getReferenceType(), ref.isPrimary(),
                    ref.getSource(), function
                ));
                count++;
            }
            println("REF_COUNT " + count);
        }
    }
}
