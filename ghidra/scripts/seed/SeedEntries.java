//@author kaikozlov
//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class SeedEntries extends GhidraScript {
    @Override
    public void run() throws Exception {
        // Known entry points from RESEARCH_REPORT_EN.md
        // (reset handler + SecOC/CSM cyclic and factory-arming chain)
        long[] entries = {
            0x1F2L,
            0x679d6L, 0x78504L, 0x758a0L, 0x77e98L,
            0x65f5cL, 0x67282L, 0x78bd0L,
            0x730d4L, 0x71e5aL, 0x71de0L, 0x70d96L,
            0x65c60L, 0x66374L, 0x674a8L
        };
        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        Listing list = currentProgram.getListing();
        int ds = 0, fc = 0;
        for (long ea : entries) {
            Address addr = space.getAddress(ea);
            Instruction ci = list.getInstructionContaining(addr);
            if (ci != null && !ci.getMinAddress().equals(addr)) {
                // clear a mid-stream instruction so we can re-align on addr
                list.clearCodeUnits(ci.getMinAddress(), ci.getMaxAddress(), false);
            }
            if (list.getInstructionAt(addr) == null) {
                disassemble(addr);
                ds++;
            }
            if (currentProgram.getFunctionManager().getFunctionAt(addr) == null) {
                if (createFunction(addr, null) != null) {
                    fc++;
                }
            }
        }
        println("SeedEntries: entries=" + entries.length + " disasm_seeded=" + ds
                + " funcs_created=" + fc);
    }
}
