// Force-disassemble and create functions at addresses passed as args.
// @category Analysis
// @args-off
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;

public class ForceFunctions extends GhidraScript {
    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        AddressFactory af = currentProgram.getAddressFactory();
        AddressSpace space = af.getDefaultAddressSpace();
        FunctionManager fm = currentProgram.getFunctionManager();
        Listing listing = currentProgram.getListing();
        
        for (String arg : args) {
            long addr = Long.parseLong(arg.replace("0x", "").replace("0X", ""), 16);
            Address a = space.getAddress(addr);
            
            Function f = fm.getFunctionAt(a);
            if (f != null && listing.getInstructionAt(a) == null) {
                fm.removeFunction(a);
                f = null;
            }
            Instruction containing = listing.getInstructionContaining(a);
            if (containing != null && !containing.getMinAddress().equals(a)) {
                listing.clearCodeUnits(
                    containing.getMinAddress(), containing.getMaxAddress(), false);
            }
            CodeUnit unit = listing.getCodeUnitContaining(a);
            if (unit != null && !(unit instanceof Instruction)) {
                listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(), false);
            }
            if (listing.getInstructionAt(a) == null && !disassemble(a)) {
                println("Failed to disassemble at 0x" + Long.toHexString(addr));
                continue;
            }
            if (f == null) {
                f = createFunction(a, null);
            }
            if (f != null) {
                println("Created function at 0x" + Long.toHexString(addr) + ": " + f.getName() + " (" + f.getBody().getNumAddresses() + " bytes)");
            } else {
                println("Failed to create function at 0x" + Long.toHexString(addr));
            }
        }
    }
}
