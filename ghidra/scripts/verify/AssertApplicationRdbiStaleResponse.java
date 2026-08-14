//@author kaikozlov
//@category Verification
// Read-only assertion for the fixed Dcm response-buffer lifetime used by the
// 45-byte no-op RDBI disclosure family.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationRdbiStaleResponse extends GhidraScript {
    private void requireFunction(long address) {
        if (getFunctionAt(toAddr(address)) == null) {
            throw new IllegalStateException(String.format("missing function at %s", toAddr(address)));
        }
    }

    @Override
    public void run() throws Exception {
        requireFunction(0x8f6faL);
        requireFunction(0x91da4L);
        requireFunction(0x91f84L);
        requireFunction(0x91fd0L);
        requireFunction(0x941c6L);
        requireFunction(0x9429eL);
        requireFunction(0x9361aL);
        requireFunction(0x8a374L);

        Set<String> expected = new TreeSet<>(Arrays.asList(
            "00091dac:WRITE",
            "00091f8a:WRITE",
            "00091fee:DATA"
        ));
        Set<String> actual = new TreeSet<>();
        for (Reference reference : getReferencesTo(toAddr(0xfebe59f8L))) {
            actual.add(reference.getFromAddress() + ":" + reference.getReferenceType());
        }
        if (!actual.equals(expected)) {
            throw new IllegalStateException("FEBE59F8 xref topology changed; expected="
                + expected + " actual=" + actual);
        }

        println("ASSERT application-rdbi-stale-response: fixed_buffer=febe59f8 direct_xrefs=3 clears=2 pointer_refs=1 unexpected=0");
    }
}
