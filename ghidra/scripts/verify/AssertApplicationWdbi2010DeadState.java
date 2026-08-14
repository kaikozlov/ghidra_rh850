//@author kaikozlov
//@category Verification
// Read-only assertion for WDBI DID 0x2010 write-only diagnostic residue.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationWdbi2010DeadState extends GhidraScript {
    @Override
    public void run() throws Exception {
        assertExactRefs(0xfebeb48eL, "000b7c16:WRITE", "000bd694:WRITE");
        assertExactRefs(0xfebeb49cL, "000b7c1a:WRITE", "000bd696:WRITE");
        assertExactRefs(0xfebeb4a0L, "000b7c1c:WRITE", "000bd698:WRITE");
        assertNoRuntimeReaders(0xfebeb48eL);
        assertNoRuntimeReaders(0xfebeb49cL);
        assertNoRuntimeReaders(0xfebeb4a0L);
        assertExactRefs(0xfe09cL, "0004ef2e:UNCONDITIONAL_CALL");
        assertExactRefs(0xb7c0eL, "000fe0a2:COMPUTED_CALL");

        long[] boundaryFunctions = {0x4ef04L, 0xfe09cL, 0xb7c0eL, 0x4c4a4L};
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
        println("ASSERT application-wdbi-2010-dead-state: residue_fields=3 runtime_readers=0 writer_callers=1 direct_actuation_refs=0 direct_actuation_calls=0 unexpected=0");
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

    private void assertNoRuntimeReaders(long targetOffset) {
        Address target = toAddr(targetOffset);
        for (Reference reference : getReferencesTo(target)) {
            if (reference.getReferenceType().isRead()) {
                throw new IllegalStateException(String.format(
                    "%s gained runtime reader at %s", target, reference.getFromAddress()));
            }
        }
    }
}
