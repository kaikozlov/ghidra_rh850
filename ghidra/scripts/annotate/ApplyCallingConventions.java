//@author kaikozlov
//@category Analysis
// Assign the selected compiler's default prototype only to functions with an
// unknown/default convention. Preserve ISR, compiler-helper, analyzer policy,
// and explicitly assigned conventions; thunks inherit their destination.
// Run after entry/helper analysis and again after the final rebuild reopen.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;

public class ApplyCallingConventions extends GhidraScript {
    private static final String ISR = "__interrupt";

    @Override
    public void run() throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager();
        String abi = currentProgram.getCompilerSpec().getDefaultCallingConvention().getName();
        int stdcall = 0;
        int interrupt = 0;
        int skipped = 0;
        int failed = 0;

        FunctionIterator it = fm.getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            String current = f.getCallingConventionName();
            if (ISR.equals(current)) {
                interrupt++;
                continue;
            }
            if (!Function.UNKNOWN_CALLING_CONVENTION_STRING.equals(current) &&
                !Function.DEFAULT_CALLING_CONVENTION_STRING.equals(current)) {
                skipped++;
                continue;
            }
            // Thunks inherit their destination's convention; skip to avoid
            // fighting Ghidra's thunk bookkeeping.
            if (f.isThunk()) {
                skipped++;
                continue;
            }
            try {
                f.setCallingConvention(abi);
                stdcall++;
            } catch (Exception ex) {
                failed++;
                println("WARN: could not set " + abi + " on " + f.getName()
                        + " @ " + f.getEntryPoint() + ": " + ex.getMessage());
            }
        }

        println(String.format(
                "ApplyCallingConventions: set %s=%d preserved %s=%d already_ok/skipped=%d failed=%d",
                abi, stdcall, ISR, interrupt, skipped, failed));
        if (failed > 0) {
            throw new IllegalStateException(failed + " calling-convention apply failures");
        }
        if (stdcall + interrupt + skipped == 0) {
            throw new IllegalStateException("no functions found to assign conventions");
        }
    }
}
