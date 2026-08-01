//@author kaikozlov
//@category Analysis
// Seed only the seven DID callbacks whose Techstream monitor names have
// independent firmware data-flow evidence and are eligible for structural
// auto-naming.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;

public class SeedDidCallbacks extends GhidraScript {
    private static final long[] STRUCTURAL_CALLBACKS = {
        0x4cbfcL, // DID 0x0102: vehicle speed
        0x4cc76L, // DID 0x0103: engine revolution speed
        0x4ccc4L, // DID 0x0105: motor instruction current
        0x4cd38L, // DID 0x0109: steering torque
        0x4cd74L, // DID 0x010B: output of torque sensor 2
        0x4cdd4L, // DID 0x0110: IG switch status
        0x4ce00L, // DID 0x0112: number of diagnosis codes
    };

    @Override
    public void run() throws Exception {
        FunctionManager functions = currentProgram.getFunctionManager();
        int created = 0;
        int existing = 0;

        for (long callback : STRUCTURAL_CALLBACKS) {
            Address address = toAddr(callback);
            Function function = functions.getFunctionAt(address);
            if (function == null) {
                disassemble(address);
                function = createFunction(address, null);
                if (function == null) {
                    throw new IllegalStateException(String.format(
                        "failed to create structural DID callback at 0x%x", callback
                    ));
                }
                created++;
            } else {
                existing++;
            }
            if (!"__stdcall".equals(function.getCallingConventionName())) {
                function.setCallingConvention("__stdcall");
            }
        }

        println(String.format(
            "SeedDidCallbacks: structural=%d created=%d existing=%d",
            STRUCTURAL_CALLBACKS.length, created, existing
        ));
    }
}
