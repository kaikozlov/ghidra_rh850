//@author kaikozlov
//@category Verification
// Read-only ownership/topology assertion for the application async operation queue.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationAsyncOperationQueue extends GhidraScript {
    @Override
    public void run() throws Exception {
        assertExactRefs(0x00050698L,
            "0004c9da:UNCONDITIONAL_CALL", "000509c4:UNCONDITIONAL_CALL");
        assertExactRefs(0x00050760L,
            "0004f4ca:UNCONDITIONAL_CALL", "000509ce:UNCONDITIONAL_CALL");
        assertExactRefs(0x000507eaL,
            "0003568c:UNCONDITIONAL_CALL", "000509d8:UNCONDITIONAL_CALL");
        assertExactRefs(0x00050864L,
            "0004f17e:UNCONDITIONAL_CALL", "000509e2:UNCONDITIONAL_CALL");
        assertExactRefs(0x00050922L,
            "0004ec0a:UNCONDITIONAL_CALL", "000509ec:UNCONDITIONAL_CALL");
        assertExactRefs(0x00035658L,
            "0005e1b8:UNCONDITIONAL_CALL", "0005e1de:UNCONDITIONAL_CALL", "0005e7d0:UNCONDITIONAL_CALL");
        assertExactRefs(0x00050660L,
            "000506aa:UNCONDITIONAL_CALL", "000507fc:UNCONDITIONAL_CALL");
        assertExactRefs(0xfebe828cL,
            "000505a0:WRITE",
            "0005069c:READ", "000506a6:WRITE", "000506ae:READ_WRITE",
            "00050764:READ", "0005076e:WRITE", "00050776:READ_WRITE",
            "000507ee:READ", "000507f8:WRITE", "00050800:READ_WRITE",
            "00050868:READ", "00050872:WRITE", "0005087a:READ_WRITE",
            "00050926:READ", "00050930:WRITE", "00050938:READ_WRITE",
            "000509a6:WRITE", "00050a20:READ", "00050b26:READ",
            "00050bf6:READ", "00050c86:READ", "00050cea:READ",
            "00058e8a:WRITE");
        println("ASSERT application-async-operation-queue: operations=5 values=1,2,4,5,6 op3=absent diagnostic_owned=4 internal_owned=1 op4_selectorless=1 unexpected=0");
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
