//@author kaikozlov
//@category Analysis
// Close the direct-call graph from already validated function bodies.  A
// literal, non-computed call is primary entry evidence; orphan decoded runs are
// deliberately not used as roots.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.SourceType;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class SeedDirectCallTargets extends GhidraScript {
    @Override
    public void run() throws Exception {
        int created = 0;
        for (int round = 0; round < 64; round++) {
            List<Address> targets = collectMissingTargets();
            if (targets.isEmpty()) {
                println("SeedDirectCallTargets: created=" + created + " rounds=" + round);
                return;
            }
            int roundCreated = 0;
            for (Address target : targets) {
                if (getFunctionContaining(target) != null) continue;
                Data data = getDataContaining(target);
                if (data != null && data.isDefined()) {
                    if (!data.getMinAddress().equals(target) || data.getLength() > 8) {
                        throw new IllegalStateException(String.format(
                            "direct target %s overlaps non-entry data %s..%s",
                            target, data.getMinAddress(), data.getMaxAddress()));
                    }
                    clearListing(data.getMinAddress(), data.getMaxAddress());
                }
                if (getInstructionAt(target) == null && !disassemble(target)) {
                    throw new IllegalStateException("failed to disassemble direct target " + target);
                }
                Instruction first = getInstructionAt(target);
                if (first == null || !first.getAddress().equals(target)) {
                    throw new IllegalStateException("direct target is not an instruction boundary " + target);
                }
                Function function = createFunction(target,
                    "direct_call_target_" + target.toString());
                if (function == null) {
                    throw new IllegalStateException("failed to create direct target " + target);
                }
                if (!"__stdcall".equals(function.getCallingConventionName())) {
                    function.setCallingConvention("__stdcall");
                }
                roundCreated++;
                created++;
            }
            if (roundCreated == 0) {
                throw new IllegalStateException("direct-call closure made no progress: " + targets);
            }
        }
        throw new IllegalStateException("direct-call closure exceeded 64 rounds");
    }

    private List<Address> collectMissingTargets() throws Exception {
        Set<Address> unique = new HashSet<>();
        var functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            monitor.checkCancelled();
            Function source = functions.next();
            InstructionIterator instructions = currentProgram.getListing().getInstructions(
                source.getBody(), true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                if (!instruction.getFlowType().isCall()
                        || instruction.getFlowType().isComputed()) continue;
                for (Address target : instruction.getFlows()) {
                    if (target.getAddressSpace().equals(toAddr(0).getAddressSpace())
                            && target.getOffset() <= 0xfffffL
                            && getFunctionContaining(target) == null) {
                        unique.add(target);
                    }
                }
            }
        }
        List<Address> result = new ArrayList<>(unique);
        result.sort(Address::compareTo);
        return result;
    }
}
