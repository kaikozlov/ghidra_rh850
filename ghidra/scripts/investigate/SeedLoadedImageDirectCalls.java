//@author kaikozlov
//@category Analysis
// Recursively create functions for direct call targets that remain inside the
// current program's initialized memory. Intended for disposable raw payload imports
// whose load address is not the canonical 0..1MiB CodeFlash range.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.Memory;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class SeedLoadedImageDirectCalls extends GhidraScript {
    @Override
    public void run() throws Exception {
        Memory memory = currentProgram.getMemory();
        int created = 0;
        for (int round = 0; round < 64; round++) {
            Set<Address> unique = new HashSet<>();
            var functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function source = functions.next();
                InstructionIterator it = currentProgram.getListing().getInstructions(source.getBody(), true);
                while (it.hasNext()) {
                    Instruction ins = it.next();
                    if (!ins.getFlowType().isCall() || ins.getFlowType().isComputed()) continue;
                    for (Address target : ins.getFlows()) {
                        if (!memory.contains(target)) continue;
                        if (currentProgram.getFunctionManager().getFunctionContaining(target) == null) unique.add(target);
                    }
                }
            }
            if (unique.isEmpty()) {
                println("SeedLoadedImageDirectCalls: created=" + created + " rounds=" + round);
                return;
            }
            List<Address> targets = new ArrayList<>(unique);
            targets.sort(Address::compareTo);
            int roundCreated = 0;
            for (Address target : targets) {
                if (getFunctionContaining(target) != null) continue;
                if (getInstructionAt(target) == null && !disassemble(target)) {
                    throw new IllegalStateException("failed to disassemble direct target " + target);
                }
                Function f = createFunction(target, null);
                if (f == null) throw new IllegalStateException("failed to create direct target " + target);
                roundCreated++; created++;
            }
            if (roundCreated == 0) throw new IllegalStateException("direct-call closure made no progress");
        }
        throw new IllegalStateException("direct-call closure exceeded 64 rounds");
    }
}
