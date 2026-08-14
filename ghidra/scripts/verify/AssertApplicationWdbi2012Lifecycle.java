//@author kaikozlov
//@category Verification
// Read-only assertion for WDBI DID 0x2012 lifecycle-inhibit and calibration-state boundary.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationWdbi2012Lifecycle extends GhidraScript {
    @Override
    public void run() throws Exception {
        assertExactRefs(0xfebeb18fL,
            "000b24ce:READ", "000b2684:READ", "000b2c7e:READ",
            "000b28a6:WRITE", "000bbdc2:READ", "000bccfc:READ", "000bda68:WRITE");
        assertExactRefs(0xfebeb18eL,
            "000b23ca:PARAM", "000b23e4:PARAM", "000b2656:PARAM",
            "000b2840:PARAM", "000b285a:PARAM", "000b2864:READ", "000b2942:READ",
            "000b2e50:READ", "000bcf84:READ", "000bda66:WRITE", "000fd610:READ");
        assertExactRefs(0xfebeb192L,
            "000b2548:WRITE", "000b2870:WRITE", "000b318c:READ", "000bda74:WRITE");
        assertExactRefs(0xfebeb1d1L,
            "000b26bc:READ", "000b2c82:READ", "000b2ee4:READ", "000b3100:READ",
            "000b31ac:WRITE", "000b992e:READ", "000bcd26:READ", "000bda28:WRITE");
        assertExactRefs(0xfebeb54cL,
            "000bdce6:WRITE", "000bdd08:READ", "000be94c:READ");
        assertExactRefs(0xfebe8ae0L,
            "00056248:READ", "000562d8:DATA", "0005895e:WRITE");

        long[] boundaryFunctions = {0xb2642L,0xb2912L,0xb30e0L,0xb98bcL,0xb8e0cL};
        Set<Long> actuationStates = new HashSet<>(Arrays.asList(
            0xfebe6d18L, 0xfebe6d1cL, 0xfebe6d28L, 0xfebe6d2aL
        ));
        Set<Long> actuationFunctions = new HashSet<>(Arrays.asList(
            0x36148L, 0x36902L, 0x36a44L, 0x365d8L, 0xa7234L
        ));
        for (long entry : boundaryFunctions) {
            Function function = getFunctionAt(toAddr(entry));
            if (function == null) throw new IllegalStateException(String.format("missing function %06X", entry));
            InstructionIterator it = currentProgram.getListing().getInstructions(function.getBody(), true);
            while (it.hasNext()) {
                monitor.checkCancelled();
                Instruction ins = it.next();
                for (Reference ref : ins.getReferencesFrom()) {
                    Address target = ref.getToAddress();
                    if (target == null || !target.isMemoryAddress()) continue;
                    long off = target.getOffset();
                    if (actuationStates.contains(off)) {
                        throw new IllegalStateException(String.format(
                            "%06X gained direct actuation-state ref %s -> %s", entry, ins.getAddress(), target));
                    }
                    if (ref.getReferenceType().isCall() && actuationFunctions.contains(off)) {
                        throw new IllegalStateException(String.format(
                            "%06X gained direct actuation-function call %s -> %s", entry, ins.getAddress(), target));
                    }
                }
            }
        }

        println("ASSERT application-wdbi-2012-lifecycle: refs_18f=7 refs_18e=11 refs_192=4 refs_1d1=8 refs_54c=3 refs_signal=3 direct_actuation_refs=0 direct_actuation_calls=0 unexpected=0");
    }

    private void assertExactRefs(long targetOffset, String... expectedEntries) {
        Set<String> expected = new TreeSet<>(Arrays.asList(expectedEntries));
        Set<String> actual = new TreeSet<>();
        Address target = toAddr(targetOffset);
        for (Reference reference : getReferencesTo(target)) {
            actual.add(reference.getFromAddress().toString() + ":" + reference.getReferenceType());
        }
        if (!actual.equals(expected)) {
            Set<String> missing = new TreeSet<>(expected); missing.removeAll(actual);
            Set<String> extra = new TreeSet<>(actual); extra.removeAll(expected);
            throw new IllegalStateException(String.format(
                "xref topology changed for %s missing=%s extra=%s", target, missing, extra));
        }
    }
}
