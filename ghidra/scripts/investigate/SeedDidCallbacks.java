//@author kaikozlov
//@category Analysis
// Seed all DID table callbacks as functions, then decompile the monitor-bridged ones.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;

public class SeedDidCallbacks extends GhidraScript {

    private void ensureFunction(long value, String name) throws Exception {
        Address a = toAddr(value);
        Listing listing = currentProgram.getListing();
        Instruction containing = listing.getInstructionContaining(a);
        if (containing != null && !containing.getMinAddress().equals(a)) {
            listing.clearCodeUnits(containing.getMinAddress(), containing.getMaxAddress(), false);
        }
        CodeUnit unit = listing.getCodeUnitContaining(a);
        if (unit != null && !(unit instanceof Instruction)) {
            listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(), false);
        }
        if (listing.getInstructionAt(a) == null && !disassemble(a)) {
            println("WARN: disassembly failed at " + a + " (" + name + ")");
            return;
        }
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) {
            f = createFunction(a, name);
        }
        if (f == null) {
            println("WARN: function creation failed at " + a + " (" + name + ")");
            return;
        }
        f.setCallingConvention("__stdcall");
    }

    private void decompileAndPrint(long value, String label) throws Exception {
        Address a = toAddr(value);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) {
            println("=== " + label + ": no function at " + a + " ===");
            return;
        }
        DecompInterface decomp = new DecompInterface();
        decomp.openProgram(currentProgram);
        DecompileResults results = decomp.decompileFunction(f, 30, monitor);
        String code = results.getDecompiledFunction() != null
            ? results.getDecompiledFunction().getC() : "(decompilation failed)";
        println("=== " + label + " @ " + a + " ===");
        println(code);
        decomp.dispose();
    }

    @Override
    public void run() throws Exception {
        // DID table: 242 entries at 0x2941C, 16 bytes each
        // Record: <H did, <H flags, <I callback, <I extra1, <I extra2
        long tableBase = 0x2941CL;
        int count = 0xF2;

        // Seed all unique callback addresses
        java.util.Set<Long> seen = new java.util.HashSet<>();
        for (int i = 0; i < count; i++) {
            long offset = tableBase + i * 16L;
            short did = (short) currentProgram.getMemory().getShort(toAddr(offset));
            int callback = currentProgram.getMemory().getInt(toAddr(offset + 4)) & 0xFFFFFFFF;
            if (callback == 0) continue;
            long cbLong = callback & 0xFFFFFFFFL;
            if (seen.contains(cbLong)) continue;
            seen.add(cbLong);
            String name = String.format("did_%04x_callback", did & 0xFFFF);
            try {
                ensureFunction(cbLong, name);
            } catch (Exception e) {
                // Already inside a function — skip
            }
        }
        println("Seeded " + seen.size() + " unique DID callbacks");

        // Decompile seq-derived candidate DIDs for independent semantic evidence.
        decompileAndPrint(0x4E98EL, "DID 0x0101 (Diagnosis codes when FFD stored)");
        decompileAndPrint(0x4CBFCL, "DID 0x0102 (Vehicle speed)");
        decompileAndPrint(0x4CC76L, "DID 0x0103 (Engine revolution speed)");
        decompileAndPrint(0x4CCC4L, "DID 0x0105 (Motor Actual Current)");
        decompileAndPrint(0x4CD38L, "DID 0x0109 (Steering torque)");
        decompileAndPrint(0x4CD74L, "DID 0x010B (Output of torque sensor 2)");
        decompileAndPrint(0x4CDD4L, "DID 0x0110 (IG switch status)");
        decompileAndPrint(0x4CDFCL, "DID 0x0111 (Torque sensor power supply)");
        decompileAndPrint(0x4CE00L, "DID 0x0112 (No. of diagnosis codes)");
    }
}
