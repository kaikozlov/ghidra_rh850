//@author kaikozlov
//@category Verification
// Read-only structural floor for callback-table recovery and direct-call graph
// closure.  Optional --mutation-self-test deletes one callback in a rolled-back
// transaction and requires this verifier to detect the regression.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.scalar.Scalar;

import java.util.ArrayList;
import java.util.List;

public class AssertFunctionDiscoveryFloor extends GhidraScript {
    private static final class PointerTable {
        final String id;
        final long base;
        final int count;
        final int stride;
        final int[] pointerOffsets;

        PointerTable(String id, long base, int count, int stride, int... pointerOffsets) {
            this.id = id;
            this.base = base;
            this.count = count;
            this.stride = stride;
            this.pointerOffsets = pointerOffsets;
        }
    }

    private static final PointerTable[] TABLES = {
        new PointerTable("xcp_command", 0x2b3f0L, 7, 8, 4),
        new PointerTable("application_command", 0x22c30L, 18, 4, 0),
        new PointerTable("application_routine_control", 0x25804L, 19, 12, 4, 8),
        new PointerTable("application_rdbi_callback", 0x2941cL, 242, 16, 4),
        new PointerTable("application_operation", 0x28098L, 10, 16, 8, 12),
        new PointerTable("packet_high_selector", 0x26cccL, 8, 4, 0),
        new PointerTable("packet_low_selector", 0x26cecL, 45, 4, 0),
        new PointerTable("timer_expiry", 0x26da0L, 9, 4, 0),
        new PointerTable("record_operation", 0x26218L, 6, 28, 0),
        new PointerTable("deadline_monitor_d_a", 0x28524L, 1, 52,
            0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48),
        new PointerTable("deadline_monitor_simple", 0x28558L, 28, 12, 0, 4, 8),
        new PointerTable("deadline_monitor_d_b", 0x286d0L, 1, 52,
            0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48),
    };
    private static final long[] BOUNDED_POINTERS = {
        0x21e4cL, 0x21e50L, 0x21e54L, 0x21e58L, 0x21e5cL, 0x21e44L,
    };
    private static final long[] BOUNDED_TARGETS = {
        0x7adc8L, 0x7addcL, 0x7adeeL, 0x7ae00L, 0x7ae14L, 0x7ae28L,
    };

    @Override
    public void run() throws Exception {
        List<String> failures = collectFailures();
        if (!failures.isEmpty()) fail(failures);

        boolean mutationSelfTest = false;
        for (String argument : getScriptArgs()) {
            if ("--mutation-self-test".equals(argument)) mutationSelfTest = true;
        }
        if (mutationSelfTest) runMutationSelfTest();

        int pointers = 0;
        for (PointerTable table : TABLES) {
            for (int index = 0; index < table.count; index++) {
                for (int offset : table.pointerOffsets) {
                    long target = currentProgram.getMemory().getInt(
                        toAddr(table.base + (long) index * table.stride + offset)) & 0xffffffffL;
                    if (target != 0) pointers++;
                }
            }
        }
        println(String.format(
            "ASSERT function-discovery-floor: tables=%d pointers=%d bounded_wrappers=%d direct_call_gaps=0 constant_veneer_gaps=0%s",
            TABLES.length, pointers, BOUNDED_TARGETS.length,
            mutationSelfTest ? " mutation_self_test=passed" : ""));
    }

    private List<String> collectFailures() throws Exception {
        List<String> failures = new ArrayList<>();
        for (PointerTable table : TABLES) {
            for (int index = 0; index < table.count; index++) {
                for (int offset : table.pointerOffsets) {
                    Address pointer = toAddr(table.base + (long) index * table.stride + offset);
                    long targetOffset = currentProgram.getMemory().getInt(pointer) & 0xffffffffL;
                    if (targetOffset == 0) continue;
                    Address target = toAddr(targetOffset);
                    Function function = getFunctionAt(target);
                    if (function == null) {
                        failures.add(String.format("%s[%d]+%d missing function %s",
                            table.id, index, offset, target));
                    }
                    if (!hasUserDataReference(pointer, target)) {
                        failures.add(String.format("%s[%d]+%d missing USER_DEFINED reference",
                            table.id, index, offset));
                    }
                }
            }
        }
        for (int index = 0; index < BOUNDED_TARGETS.length; index++) {
            Address pointer = toAddr(BOUNDED_POINTERS[index]);
            Address target = toAddr(BOUNDED_TARGETS[index]);
            long raw = currentProgram.getMemory().getInt(pointer) & 0xffffffffL;
            if (raw != BOUNDED_TARGETS[index]) {
                failures.add(String.format("bounded pointer 0x%x changed", BOUNDED_POINTERS[index]));
            }
            if (getFunctionAt(target) == null) {
                failures.add("bounded wrapper missing function " + target);
            }
            if (!hasUserDataReference(pointer, target)) {
                failures.add("bounded wrapper missing reference " + pointer);
            }
        }

        var functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            monitor.checkCancelled();
            Function source = functions.next();
            if (source.getBody().getNumAddresses() == 8) {
                Instruction first = getInstructionAt(source.getEntryPoint());
                Instruction second = first == null ? null : first.getNext();
                if (first != null && second != null && source.getBody().contains(second.getAddress())
                        && "mov".equals(first.getMnemonicString())
                        && "jmp".equals(second.getMnemonicString())) {
                    Object[] immediate = first.getOpObjects(0);
                    Object[] jumpOperand = second.getOpObjects(0);
                    if (immediate.length == 1 && immediate[0] instanceof Scalar
                            && jumpOperand.length == 1 && "r12".equals(jumpOperand[0].toString())) {
                        long targetOffset = ((Scalar) immediate[0]).getUnsignedValue();
                        if ((targetOffset & 1L) == 0 && targetOffset <= 0xfffffL
                                && getFunctionAt(toAddr(targetOffset)) == null) {
                            failures.add(String.format(
                                "constant veneer %s targets missing function %s",
                                source.getEntryPoint(), toAddr(targetOffset)));
                        }
                    }
                }
            }
            InstructionIterator instructions = currentProgram.getListing().getInstructions(
                source.getBody(), true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                if (!instruction.getFlowType().isCall()
                        || instruction.getFlowType().isComputed()) continue;
                for (Address target : instruction.getFlows()) {
                    if (target.getAddressSpace().equals(toAddr(0).getAddressSpace())
                            && target.getOffset() <= 0xfffffL
                            && getFunctionAt(target) == null) {
                        failures.add(String.format(
                            "direct call %s in %s targets missing function %s",
                            instruction.getAddress(), source.getEntryPoint(), target));
                    }
                }
            }
        }
        return failures;
    }

    private boolean hasUserDataReference(Address from, Address to) {
        for (Reference reference : currentProgram.getReferenceManager().getReferencesFrom(from)) {
            if (reference.getToAddress().equals(to)
                    && reference.getReferenceType().isData()
                    && reference.getSource() == SourceType.USER_DEFINED) return true;
        }
        return false;
    }

    private void runMutationSelfTest() throws Exception {
        Address victim = toAddr(0x9729aL);
        int transaction = currentProgram.startTransaction("function discovery mutation self-test");
        try {
            if (!currentProgram.getFunctionManager().removeFunction(victim)) {
                throw new IllegalStateException("mutation self-test could not delete " + victim);
            }
            List<String> failures = collectFailures();
            boolean detected = false;
            for (String failure : failures) {
                if (failure.contains("missing function 0009729a")) detected = true;
            }
            if (!detected) {
                throw new IllegalStateException(
                    "mutation self-test deletion was not detected: " + failures);
            }
        } finally {
            currentProgram.endTransaction(transaction, false);
        }
        // FunctionManager retains a stale negative cache in this script after
        // rollback; the enclosing read-only headless session is the disposable
        // boundary and cannot persist the deletion.
    }

    private void fail(List<String> failures) {
        for (String failure : failures) println("FAIL: " + failure);
        throw new IllegalStateException(
            "function-discovery floor failed: " + String.join("; ", failures));
    }
}
