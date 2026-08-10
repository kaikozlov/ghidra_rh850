// Disassemble and create a function at a raw-payload entry point.
// @category Analysis
// @args-off
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSpace;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.symbol.SourceType;

public class SeedRawPayload extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1 || args.length > 2) {
            throw new IllegalArgumentException(
                "usage: SeedRawPayload.java <hex-entry> [function-name]");
        }

        long value = Long.parseUnsignedLong(
            args[0].replace("0x", "").replace("0X", ""), 16);
        String name = args.length == 2 ? args[1] : null;
        AddressSpace space = currentProgram.getAddressFactory().getDefaultAddressSpace();
        Address entry = space.getAddress(value);
        Listing listing = currentProgram.getListing();

        Instruction containing = listing.getInstructionContaining(entry);
        if (containing != null && !containing.getMinAddress().equals(entry)) {
            listing.clearCodeUnits(
                containing.getMinAddress(), containing.getMaxAddress(), false);
        }
        if (listing.getInstructionAt(entry) == null && !disassemble(entry)) {
            throw new IllegalStateException("failed to disassemble " + entry);
        }

        FunctionManager functions = currentProgram.getFunctionManager();
        Function function = functions.getFunctionAt(entry);
        if (function == null) {
            function = createFunction(entry, name);
        } else if (name != null) {
            function.setName(name, SourceType.USER_DEFINED);
        }
        if (function == null) {
            throw new IllegalStateException("failed to create function " + entry);
        }

        println("SeedRawPayload: entry=" + entry + " name=" + function.getName()
            + " body_bytes=" + function.getBody().getNumAddresses());
    }
}
