//@author kaikozlov
//@category Verification
// Read-only assertion for WDBI DIDs 0x2013/0x2014 bounded control cones.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationWdbi2013And2014Controls extends GhidraScript {
    @Override
    public void run() throws Exception {
        assertExactRefs(0xfebeb434L, "000b7646:READ", "000b76a8:WRITE", "000bd036:READ", "000bd906:WRITE");
        assertExactRefs(0xfebeb448L, "000b750a:WRITE", "000b7664:WRITE", "000b7686:WRITE", "000b76a4:WRITE", "000b76d4:READ", "000bd900:WRITE");
        assertExactRefs(0xfebeb452L, "000b7314:READ", "000b76ba:WRITE", "000b7746:WRITE", "000b7778:WRITE", "000b778a:WRITE", "000bd914:WRITE", "000bd922:READ", "000be820:READ");
        assertExactRefs(0xfebeb41aL, "000b72e4:WRITE", "000b7428:WRITE", "000b7434:WRITE", "000bcb1c:READ", "000bd886:WRITE");
        assertExactRefs(0xfebee416L, "00035758:READ", "0005b684:READ", "0005c09c:READ", "0005c64c:READ", "000bcb20:WRITE", "000be378:WRITE");
        assertExactRefs(0xfebe6aceL, "000357be:WRITE", "00037ffc:READ", "0005ab3a:WRITE");
        assertExactRefs(0xfebe6dcaL, "00038000:WRITE", "0005abee:WRITE", "0005ac1e:READ", "0005bd96:READ", "0005c4be:READ");
        assertExactRefs(0xfebe6dccL, "00038002:WRITE", "0005abec:WRITE", "0005ac1c:READ", "0005bd9c:READ", "0005c4c4:READ");
        assertExactRefs(0xfebe66ceL, "0005ac58:WRITE", "0005c4c0:WRITE");
        assertExactRefs(0xfebe66d0L, "0005ac5a:WRITE", "0005c4c6:WRITE");
        assertExactRefs(0xfebe63ceL, "0005ac84:WRITE", "0005bd98:WRITE");
        assertExactRefs(0xfebe63d0L, "0005ac80:WRITE", "0005bd9e:WRITE");
        assertExactRefs(0xfebeb3eeL, "000b693c:READ", "000b70dc:READ", "000b71fe:WRITE", "000bd03c:READ", "000bd850:WRITE");
        assertExactRefs(0xfebeb3ecL, "000b6938:READ", "000b698c:WRITE", "000b69ba:READ", "000b70aa:WRITE", "000bd84a:WRITE");
        assertExactRefs(0xfebeb3e7L, "000b1d32:READ", "000b1d58:READ", "000b6a10:WRITE", "000b6faa:WRITE", "000b709e:WRITE", "000b7214:WRITE", "000b7222:WRITE", "000bd83c:WRITE");
        assertExactRefs(0xfebeb3a4L, "000b64c6:READ", "000b6508:READ", "000b6562:WRITE", "000b65aa:WRITE", "000b65bc:READ", "000b65d0:WRITE", "000b65da:WRITE", "000bd02e:READ", "000bd8a2:WRITE");
        assertExactRefs(0xfebeb3a6L, "000b6536:WRITE", "000b65cc:WRITE", "000bd020:READ", "000bd89e:WRITE", "000fd55a:READ", "000fd626:READ");

        long[] boundaryFunctions = {
            0xb763cL,0xb76c0L,0xb72ecL,0xb73d0L,0xbcaceL,0x3572cL,0x37fb6L,
            0xb692cL,0xb6994L,0xb70d0L,0xb7114L,0xb65bcL
        };
        Set<Long> actuationStates = new HashSet<>(Arrays.asList(
            0xfebe6d18L,0xfebe6d1cL,0xfebe6d28L,0xfebe6d2aL
        ));
        Set<Long> actuationFunctions = new HashSet<>(Arrays.asList(
            0x36148L,0x36902L,0x36a44L,0x365d8L,0xa7234L
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

        // The 2013-derived motor-worker fields are staging-only: their four RTE/task
        // mirrors have no read/param xrefs in the accepted project.
        assertNoRuntimeReaders(0xfebe66ceL);
        assertNoRuntimeReaders(0xfebe66d0L);
        assertNoRuntimeReaders(0xfebe63ceL);
        assertNoRuntimeReaders(0xfebe63d0L);

        println("ASSERT application-wdbi-2013-2014-controls: states=17 direct_actuation_refs=0 direct_actuation_calls=0 staging_mirrors_without_readers=4 unexpected=0");
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
