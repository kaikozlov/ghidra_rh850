//@author kaikozlov
//@category Analysis
// Seed boot/application startup, interrupt wrappers, and application CAN routing functions.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class SeedArchitectureFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] entries = {
            // Boot startup and EIINT dispatch.
            0x1b0L, 0x748L, 0x13b0L,
            0x1e1eL, 0x1e2aL, 0x1e36L,
            0x1e44L, 0x1e50L, 0x1e5eL, 0x1e6cL,
            0x1e7aL, 0x1e88L, 0x1e96L, 0x1ea4L,

            // Application entry, startup, foreground loop, and vector handlers.
            0x20880L, 0x62758L, 0x64fccL, 0x70524L,
            0x61d88L, 0x64b3eL, 0x70a54L,
            0x70320L, 0x703caL, 0x70476L,
            0x65028L, 0x6506aL, 0x650acL, 0x650eeL, 0x65130L,
            0x64f18L, 0x64f54L, 0x64f90L,

            // RSCFD receive/confirmation path and upper receive routing.
            0x82e40L, 0x8474eL, 0x7fa56L,
            0x80006L, 0x80114L, 0x7ff86L, 0x80c44L
        };

        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        Listing listing = currentProgram.getListing();
        int disassembled = 0;
        int created = 0;
        for (long ea : entries) {
            Address address = space.getAddress(ea);
            // Drop false pointer data that can land on code entries when SFR
            // windows are mapped, and fix mid-instruction starts.
            if (listing.getDataContaining(address) != null) {
                listing.clearCodeUnits(address, address.add(7), false);
            }
            Instruction containing = listing.getInstructionContaining(address);
            if (containing != null && !containing.getMinAddress().equals(address)) {
                listing.clearCodeUnits(containing.getMinAddress(), containing.getMaxAddress(), false);
            }
            if (listing.getInstructionAt(address) == null) {
                disassemble(address);
                disassembled++;
            }
            if (currentProgram.getFunctionManager().getFunctionAt(address) == null) {
                if (createFunction(address, null) != null) {
                    created++;
                }
            }
        }
        println("SeedArchitectureFunctions: entries=" + entries.length
                + " disasm_seeded=" + disassembled + " funcs_created=" + created);
    }
}
