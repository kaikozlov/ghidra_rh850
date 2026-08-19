//@author kaikozlov
//@category Analysis
// Read-only inventory of instructions that write the RH850 gp or tp registers.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class FindGpTpWrites extends GhidraScript {
    @Override
    public void run() throws Exception {
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        int count = 0;
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            boolean writes = false;
            StringBuilder registers = new StringBuilder();
            for (Object result : instruction.getResultObjects()) {
                if (!(result instanceof Register)) continue;
                Register register = (Register) result;
                String name = register.getName();
                if (!(name.equalsIgnoreCase("gp") || name.equalsIgnoreCase("tp"))) continue;
                if (registers.length() != 0) registers.append(',');
                registers.append(name);
                writes = true;
            }
            if (!writes) continue;
            Function containing = getFunctionContaining(instruction.getAddress());
            println(String.format(
                "WRITE address=%s registers=%s instruction=%s function=%s",
                instruction.getAddress(), registers, instruction,
                containing == null ? "<no-function>" : containing.getName() + "@" + containing.getEntryPoint()
            ));
            count++;
        }
        println("WRITE_COUNT " + count);
    }
}
