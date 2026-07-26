//@author kaikozlov
//@category Analysis
// Seed application COM/PduR/CanIf/RSCFD transmit functions missed by recursive analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class SeedApplicationTransmitFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] entries = {
            // Six generated COM transmit packers.
            0x4bb1eL, 0x4bc54L, 0x4bceeL, 0x4be24L, 0x4c158L, 0x4c25cL,

            // COM packing and cyclic-transmit machinery.
            0x7c0f0L, 0x7c232L, 0x7ce28L, 0x7d04eL,

            // PduR/CanIf routing, queueing, and confirmation.
            0x80992L, 0x809c6L, 0x7e30cL, 0x7e5f2L,
            0x7ec5aL, 0x7ee0cL, 0x7f002L, 0x7f070L,

            // RSCFD classic-frame submission and Tx confirmation.
            0x84022L, 0x842baL, 0x84710L, 0x8474eL
        };

        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        Listing listing = currentProgram.getListing();
        int disassembled = 0;
        int created = 0;
        for (long ea : entries) {
            Address address = space.getAddress(ea);
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
        println("SeedApplicationTransmitFunctions: entries=" + entries.length
                + " disasm_seeded=" + disassembled + " funcs_created=" + created);
    }
}
