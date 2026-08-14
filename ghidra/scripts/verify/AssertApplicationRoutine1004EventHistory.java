//@author kaikozlov
//@category Verification
// Read-only topology assertion for RoutineControl RID 0x1004 event-history maintenance rewrite.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationRoutine1004EventHistory extends GhidraScript {
    @Override
    public void run() throws Exception {
        assertExactRefs(0x00050864L,
            "0004f17e:UNCONDITIONAL_CALL", "000509e2:UNCONDITIONAL_CALL");
        assertExactRefs(0x00050858L, "00050876:UNCONDITIONAL_CALL");
        assertExactRefs(0x0005449eL, "0005085c:UNCONDITIONAL_CALL");
        assertExactRefs(0x00053fc4L, "00054148:UNCONDITIONAL_CALL");
        assertExactRefs(0x00053f5eL, "000540b0:UNCONDITIONAL_CALL");
        assertExactRefs(0xfebe8156L,
            "0004c47c:READ", "0004f154:READ", "0004f18e:WRITE", "0004f19c:READ");

        Set<Long> forbidden = new HashSet<>(Arrays.asList(
            0xfebe7f94L,0xfebef184L,0xfebeae20L,0xfebebf80L,0xfebebf84L,0xfebebf9aL,
            0xfebebfa2L,0xfebeacffL,0xfebeae60L,0xfebebff0L,0xfebec0beL,0xfebec0c8L,
            0xfebec0d6L,0xfebec144L,0xfebec170L,0xfebec1b8L,0xfebec1b4L,0xfebec1bcL,
            0xfebec1d4L,0xfebeb788L,0xfebeb87eL,0xfebeae16L,0xfebeae6eL,
            0xfebe6d18L,0xfebe6d1cL,0xfebe6d28L,0xfebe6d2aL
        ));
        long[] functions = {
            0x4f12cL,0x4f170L,0x50864L,0x50858L,0x5449eL,0x5436eL,0x54416L,
            0x53dacL,0x54140L,0x53fc4L,0x53ef2L,0x53f5eL,0x53b70L,0x50a1cL,
            0x4c474L,0x50996L,0x54150L,0x54228L,0x53a14L,0x53a30L,0x690e4L,0x55f0aL
        };
        for (long entry : functions) {
            Function f = getFunctionAt(toAddr(entry));
            if (f == null) throw new IllegalStateException(String.format("missing function %06X", entry));
            InstructionIterator it = currentProgram.getListing().getInstructions(f.getBody(), true);
            while (it.hasNext()) {
                monitor.checkCancelled();
                Instruction ins = it.next();
                for (Reference ref : ins.getReferencesFrom()) {
                    Address target = ref.getToAddress();
                    if (target != null && target.isMemoryAddress() && forbidden.contains(target.getOffset())) {
                        throw new IllegalStateException(String.format(
                            "%06X gained direct conditioned-command/dq ref %s -> %s", entry, ins.getAddress(), target));
                    }
                }
            }
        }
        println("ASSERT application-routine-1004-event-history: op5_callers=2 op5_initializer_callers=1 event_initializer_callers=1 persist_worker_callers=1 history_persist_callers=1 selector3_refs=4 direct_actuation_refs=0 unexpected=0");
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
