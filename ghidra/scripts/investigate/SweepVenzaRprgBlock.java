//@author kaikozlov
//@category Analysis
// Throwaway: linear-sweep disassemble the yc Venza RPRG extended-user block
// (0x01000000..0x01007588), create functions at direct jarl call targets
// (bounded closure), mirroring the CensusVenzaSecureService approach for the
// MainPE image. Then report instruction/function counts.

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.cmd.function.CreateFunctionCmd;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.LinkedHashSet;
import java.util.Set;

public class SweepVenzaRprgBlock extends GhidraScript {
    @Override
    public void run() throws Exception {
        Address lo = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x01000000L);
        Address hi = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(0x01007587L);

        // Linear sweep of the extended-user block (no flow following).
        AddressSet sweep = new AddressSet(toAddr(0x01000000L), toAddr(0x01007587L));
        DisassembleCommand cmd = new DisassembleCommand(sweep, null, false);
        cmd.applyTo(currentProgram, monitor);
        println("SWEEP done");

        // Function closure over direct call targets.
        int created = 0;
        for (int round = 0; round < 200; round++) {
            Set<Address> unique = new LinkedHashSet<>();
            InstructionIterator ait = currentProgram.getListing().getInstructions(lo, true);
            while (ait.hasNext()) {
                monitor.checkCancelled();
                Instruction bins = ait.next();
                if (bins.getAddress().getOffset() > 0x01007587L) break;
                if (!bins.getFlowType().isCall()) continue;
                for (Address target : bins.getFlows()) {
                    if (target.getOffset() < 0x01000000L || target.getOffset() > 0x01007587L) continue;
                    if (!currentProgram.getMemory().contains(target)) continue;
                    if (currentProgram.getFunctionManager().getFunctionAt(target) == null) {
                        unique.add(target);
                    }
                }
            }
            var functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                var source = functions.next();
                InstructionIterator it = currentProgram.getListing()
                    .getInstructions(source.getBody(), true);
                while (it.hasNext()) {
                    Instruction ins = it.next();
                    if (!ins.getFlowType().isCall()) continue;
                    for (Address target : ins.getFlows()) {
                        if (target.getOffset() < 0x01000000L || target.getOffset() > 0x01007587L) continue;
                        if (!currentProgram.getMemory().contains(target)) continue;
                        if (currentProgram.getFunctionManager().getFunctionAt(target) == null) {
                            unique.add(target);
                        }
                    }
                }
            }
            if (unique.isEmpty()) {
                println("CLOSURE created=" + created + " rounds=" + round);
                break;
            }
            for (Address target : unique) {
                if (getInstructionAt(target) == null && !disassemble(target)) continue;
                if (createFunction(target, null) != null) created++;
            }
        }
        InstructionIterator ci = currentProgram.getListing().getInstructions(lo, true);
        int cnt = 0;
        while (ci.hasNext()) {
            Instruction ins = ci.next();
            if (ins.getAddress().getOffset() > 0x01007587L) break;
            cnt++;
        }
        println("instructions in block: " + cnt);
    }
}
