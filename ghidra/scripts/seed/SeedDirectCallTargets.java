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
import ghidra.program.model.scalar.Scalar;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class SeedDirectCallTargets extends GhidraScript {
    @Override
    public void run() throws Exception {
        int created = 0;
        int veneerCreated = 0;
        for (int round = 0; round < 64; round++) {
            List<Address> targets = collectMissingTargets();
            Set<Address> veneerTargets = new HashSet<>(collectMissingVeneerTargets());
            for (Address target : veneerTargets) {
                if (!targets.contains(target)) targets.add(target);
            }
            targets.sort(Address::compareTo);
            if (targets.isEmpty()) {
                println("SeedDirectCallTargets: created=" + created
                    + " constant_veneer_targets=" + veneerCreated + " rounds=" + round);
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
                boolean veneerTarget = veneerTargets.contains(target);
                Function function = createFunction(target,
                    (veneerTarget ? "constant_veneer_target_" : "direct_call_target_")
                    + target.toString());
                if (function == null) {
                    throw new IllegalStateException("failed to create direct target " + target);
                }
                if (!"__stdcall".equals(function.getCallingConventionName())) {
                    function.setCallingConvention("__stdcall");
                }
                roundCreated++;
                created++;
                if (veneerTarget) veneerCreated++;
            }
            if (roundCreated == 0) {
                throw new IllegalStateException("direct-call closure made no progress: " + targets);
            }
        }
        throw new IllegalStateException("direct-call closure exceeded 64 rounds");
    }

    private List<Address> collectMissingVeneerTargets() throws Exception {
        Set<Address> unique = new HashSet<>();
        var functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            monitor.checkCancelled();
            Function source = functions.next();
            if (source.getBody().getNumAddresses() != 8) continue;
            Instruction first = getInstructionAt(source.getEntryPoint());
            if (first == null || !"mov".equals(first.getMnemonicString())) continue;
            Instruction second = first.getNext();
            if (second == null || !source.getBody().contains(second.getAddress())
                    || !"jmp".equals(second.getMnemonicString())) continue;
            Object[] immediate = first.getOpObjects(0);
            Object[] jumpOperand = second.getOpObjects(0);
            if (immediate.length != 1 || !(immediate[0] instanceof Scalar)
                    || jumpOperand.length != 1 || !"r12".equals(jumpOperand[0].toString())) continue;
            long targetOffset = ((Scalar) immediate[0]).getUnsignedValue();
            if ((targetOffset & 1L) != 0 || targetOffset > 0xfffffL) continue;
            Address target = toAddr(targetOffset);
            Function containing = getFunctionContaining(target);
            if (containing != null && !containing.getEntryPoint().equals(target)) {
                throw new IllegalStateException(String.format(
                    "constant veneer %s targets alternate entry %s in %s @ %s",
                    source.getEntryPoint(), target, containing.getName(), containing.getEntryPoint()));
            }
            if (getFunctionAt(target) == null) unique.add(target);
        }
        List<Address> result = new ArrayList<>(unique);
        result.sort(Address::compareTo);
        return result;
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
