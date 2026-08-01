//@author kaikozlov
//@category Analysis
// Decompile ALL unique DID callbacks and emit JSON for vocabulary enrichment.
// This runs against the rebuilt work project and prints a JSON array to stdout.
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;

public class DecompileAllDidCallbacks extends GhidraScript {

    private DecompInterface decomp;

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
            return;
        }
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        if (f == null) {
            createFunction(a, name);
        }
    }

    @Override
    public void run() throws Exception {
        decomp = new DecompInterface();
        decomp.openProgram(currentProgram);

        // DID table: 242 entries at 0x2941C, 16 bytes each
        long tableBase = 0x2941CL;
        int count = 0xF2;

        // Collect unique callbacks with their DID numbers
        LinkedHashMap<Long, List<Short>> cbToDids = new LinkedHashMap<>();
        for (int i = 0; i < count; i++) {
            long offset = tableBase + i * 16L;
            short did = (short) currentProgram.getMemory().getShort(toAddr(offset));
            int callback = currentProgram.getMemory().getInt(toAddr(offset + 4)) & 0xFFFFFFFF;
            if (callback == 0) continue;
            long cbLong = callback & 0xFFFFFFFFL;
            cbToDids.computeIfAbsent(cbLong, k -> new ArrayList<>()).add(did);
        }

        println("===DID_CALLBACK_JSON_BEGIN===");

        // Build JSON array
        StringBuilder sb = new StringBuilder();
        sb.append("[");

        int processed = 0;
        boolean first = true;
        for (Map.Entry<Long, List<Short>> entry : cbToDids.entrySet()) {
            long cbAddr = entry.getKey();
            List<Short> dids = entry.getValue();

            // Ensure function exists
            String fnName = String.format("did_%04x_callback", dids.get(0) & 0xFFFF);
            try {
                ensureFunction(cbAddr, fnName);
            } catch (Exception e) {
                // already inside a function, skip
            }

            Function f = currentProgram.getFunctionManager().getFunctionAt(toAddr(cbAddr));
            String code = "";
            int size = 0;
            if (f != null) {
                size = (int) f.getBody().getNumAddresses();
                DecompileResults results = decomp.decompileFunction(f, 30, monitor);
                if (results.getDecompiledFunction() != null) {
                    code = results.getDecompiledFunction().getC();
                }
            }

            if (!first) sb.append(",");
            first = false;

            // Escape code for JSON
            String escaped = code.replace("\\", "\\\\")
                                 .replace("\"", "\\\"")
                                 .replace("\n", "\\n")
                                 .replace("\r", "")
                                 .replace("\t", "  ");

            // Build DID list string
            StringBuilder didStr = new StringBuilder();
            for (int j = 0; j < dids.size(); j++) {
                if (j > 0) didStr.append(",");
                didStr.append(String.format("0x%04x", dids.get(j) & 0xFFFF));
            }

            sb.append(String.format(
                "{\"callback\":\"0x%05x\",\"dids\":\"%s\",\"size\":%d,\"code\":\"%s\"}",
                cbAddr, didStr.toString(), size, escaped
            ));

            processed++;
            if (processed % 50 == 0) {
                println("Processed " + processed + "/" + cbToDids.size());
            }
        }

        sb.append("]");
        println(sb.toString());
        println("===DID_CALLBACK_JSON_END===");
        println("Processed " + processed + " unique callbacks");

        decomp.dispose();
    }
}
