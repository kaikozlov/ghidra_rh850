//@author kaikozlov
//@category Verification
// Read-only topology assertion for the application WDBI DID 0x0204 maintenance cone.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationWdbi0204Maintenance extends GhidraScript {
    @Override
    public void run() throws Exception {
        assertExactRefs(0xfebe8167L,
            "0004c322:WRITE", "0004ebc0:READ", "0004ebee:WRITE",
            "0004ebfa:READ", "0004ec0e:WRITE", "000590e6:WRITE", "0004ec3c:WRITE");
        assertExactRefs(0xfebeaf47L,
            "000b7e78:READ", "000b7f1c:WRITE", "000bd5a4:WRITE", "000b7f7c:WRITE");
        assertExactRefs(0xfebeaf48L,
            "000b7e66:WRITE", "000b7f54:READ", "000b7f6c:READ", "000b7f74:WRITE", "000bd5a6:WRITE");
        assertExactRefs(0x00050922L,
            "0004ec0a:UNCONDITIONAL_CALL", "000509ec:UNCONDITIONAL_CALL");
        assertExactRefs(0x000508e6L, "00050934:UNCONDITIONAL_CALL");
        assertExactRefs(0x000b7e4aL, "000b7efc:UNCONDITIONAL_CALL");

        Set<Long> forbiddenState = new HashSet<>(Arrays.asList(
            0xfebe7f94L,0xfebef184L,0xfebeae20L,0xfebebf80L,0xfebebf84L,0xfebebf9aL,
            0xfebebfa2L,0xfebeacffL,0xfebeae60L,0xfebebff0L,0xfebec0beL,0xfebec0c8L,
            0xfebec0d6L,0xfebec144L,0xfebec170L,0xfebec1b8L,0xfebec1b4L,0xfebec1bcL,
            0xfebec1d4L,0xfebeb788L,0xfebeb87eL,0xfebeae16L,0xfebeae6eL,
            0xfebe6d18L,0xfebe6d1cL,0xfebe6d28L,0xfebe6d2aL
        ));
        long[] boundaryFunctions = {
            0x4ec2aL,0x4ebbcL,0x35582L,0xb7f7cL,0xb7e6eL,0xb7e4aL,0xb7f4cL,0xb7f24L,
            0x4ebf6L,0x50922L,0x508e6L,0xbb210L,0x539a8L,0x390e6L,0x453a2L,0xbb5ecL,
            0xbb3c6L,0x546e2L,0x505f8L,0x51524L,0x52016L,0x53626L,0x5062aL
        };
        for (long entry : boundaryFunctions) {
            Function function = getFunctionAt(toAddr(entry));
            if (function == null) throw new IllegalStateException(String.format("missing function %06X", entry));
            InstructionIterator it = currentProgram.getListing().getInstructions(function.getBody(), true);
            while (it.hasNext()) {
                monitor.checkCancelled();
                Instruction ins = it.next();
                for (Reference ref : ins.getReferencesFrom()) {
                    Address target = ref.getToAddress();
                    if (target != null && target.isMemoryAddress() && forbiddenState.contains(target.getOffset())) {
                        throw new IllegalStateException(String.format(
                            "%06X gained direct conditioned-command/dq ref %s -> %s", entry, ins.getAddress(), target));
                    }
                }
            }
        }
        println("ASSERT application-wdbi-0204-maintenance: pending_states=2 object7_handshake=1 op6_initiator=1 op6_fanout=12 direct_actuation_refs=0 unexpected=0");
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
