//@author kaikozlov
//@category Analysis
// Seed application COM/PduR/CanIf receive functions missed by recursive analysis.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class SeedApplicationReceiveFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        long[] entries = {
            // COM RxIndication, receive-signal, and opaque byte copy.
            0x7c640L, 0x7c03eL, 0x7d63eL, 0x7c5faL, 0x7c714L,

            // Timeout/validity helpers.
            0x8d682L, 0x8d6b4L, 0x8d65eL, 0x8d6a0L, 0x48cc8L, 0x48d14L,

            // Landmark generated unpackers and opaque PDU shadow consumers.
            0x4a244L, 0x4a312L, 0x4a35aL, 0x4a91cL, 0x4b23cL,
            0x68368L, 0x6875eL,

            // First semantic consumer cluster for many Rx destinations.
            0x56fc2L
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
        println("SeedApplicationReceiveFunctions: entries=" + entries.length
                + " disasm_seeded=" + disassembled + " funcs_created=" + created);
    }
}
