//@author kaikozlov
//@category Verification
// Read-only topology/assertion for the remaining application RoutineControl controls.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import java.util.*;

public class AssertApplicationRoutineRemainingControls extends GhidraScript {
    @Override
    public void run() throws Exception {
        assertExactRefs(0x00050760L,
            "0004f4ca:UNCONDITIONAL_CALL", "000509ce:UNCONDITIONAL_CALL");
        assertExactRefs(0x0005070cL, "00050772:UNCONDITIONAL_CALL");
        assertExactRefs(0x000fde6cL, "0004f454:UNCONDITIONAL_CALL");
        assertExactRefs(0x000fde30L,
            "00034f12:UNCONDITIONAL_CALL", "000356c4:UNCONDITIONAL_CALL", "0004f584:UNCONDITIONAL_CALL");
        assertExactRefs(0x000fe038L,
            "000352e0:UNCONDITIONAL_CALL", "0004f640:UNCONDITIONAL_CALL",
            "0004f712:UNCONDITIONAL_CALL", "0004f7c8:UNCONDITIONAL_CALL");

        Set<Long> forbiddenState = new HashSet<>(Arrays.asList(
            0xfebe7f94L,0xfebef184L,0xfebeae20L,0xfebebf80L,0xfebebf84L,0xfebebf9aL,
            0xfebebfa2L,0xfebeacffL,0xfebeae60L,0xfebebff0L,0xfebec0beL,0xfebec0c8L,
            0xfebec0d6L,0xfebec144L,0xfebec170L,0xfebec1b8L,0xfebec1b4L,0xfebec1bcL,
            0xfebec1d4L,0xfebeb788L,0xfebeb87eL,0xfebeae16L,0xfebeae6eL,
            0xfebe6d18L,0xfebe6d1cL,0xfebe6d28L,0xfebe6d2aL
        ));
        long[] boundaryFunctions = {
            0x4c5aeL,
            0x4f0eaL,0xb7e6eL,0xb79f8L,0xb7a36L,0xb5560L,0xb484eL,0xb5ee6L,0xb7c2cL,0xb5fd2L,
            0x354e6L,0x35576L,0x352a0L,0xb1f34L,0xb1cfeL,
            0xb3974L,0xb47d2L,0xb5cf4L,0xb7c04L,0xb38c0L,
            0x50760L,0x5070cL,0x50a1cL,0x4c474L,
            0xb7d26L,0x3547eL,0xb7cc6L,0xb7c4aL
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
        println("ASSERT application-routine-remaining-controls: op2_callers=2 op2_initializer_callers=1 mode1_callers=4 op1106_thunk_callers=1 op1109_thunk_callers=3 direct_actuation_refs=0 unexpected=0");
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
