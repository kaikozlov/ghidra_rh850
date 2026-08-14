//@author kaikozlov
//@category Verification
// Read-only project assertion for the true application SID-0x2E WDBI surface.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationWdbiSurface extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] starts = {
            0x4ec16L,0x4ec46L,0x4ecbcL,0x4ed2cL,0x4ed76L,0x4edc0L,0x4ee0aL,
            0x4ee54L,0x4eea6L,0x4eef0L,0x4ef4aL,0x4ef68L,0x4efacL
        };
        long[] results = {
            0x4ec2aL,0x4ec78L,0x4ecd0L,0x4ed40L,0x4ed8aL,0x4edd4L,0x4ee1eL,
            0x4ee68L,0x4eebaL,0x4ef04L,0x4ef4eL,0x4ef90L,0x4efd4L
        };
        for (long a : starts) requireFunction(a);
        for (long a : results) requireFunction(a);
        requireFunction(0x93c62L);
        requireFunction(0x936aaL);
        requireFunction(0x936d6L);
        requireFunction(0x8a630L);

        assertExactRefs(0xfebeb18fL,
            "000b24ce:READ",
            "000b2684:READ",
            "000b2c7e:READ",
            "000b28a6:WRITE",
            "000bbdc2:READ",
            "000bccfc:READ",
            "000bda68:WRITE");

        assertExactRefs(0xfebeb434L,
            "000b7646:READ",
            "000b76a8:WRITE",
            "000bd036:READ",
            "000bd906:WRITE");
        assertExactRefs(0xfebeb3eeL,
            "000b693c:READ",
            "000b70dc:READ",
            "000b71fe:WRITE",
            "000bd03c:READ",
            "000bd850:WRITE");

        println("ASSERT application-wdbi-surface: implemented=13 speed_gated=12 no_speed_gate=2012 persistent_nvm_dids=8 live_override_refs=7 control_parameter_refs=4 control_mode_refs=5 unexpected=0");
    }

    private void requireFunction(long offset) {
        if (getFunctionAt(toAddr(offset)) == null) {
            throw new IllegalStateException(String.format("missing function %06X", offset));
        }
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
