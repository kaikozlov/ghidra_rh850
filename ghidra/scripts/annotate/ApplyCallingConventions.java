//@author kaikozlov
//@category Analysis
// Apply the RH850/G3 ABI prototype (__stdcall) to every recovered function that
// is not already an ISR wrapper (__interrupt). The cspec default_proto is
// named __stdcall, but Ghidra leaves newly created functions on "unknown"
// until a convention is set explicitly — which is why landmark decompiler
// signatures previously reported unknown even after the cspec rewrite.
//
// Run AFTER RecoverVectorHandlers so true ISR wrappers keep __interrupt.
// Idempotent: already-correct conventions are left alone.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;

public class ApplyCallingConventions extends GhidraScript {
    private static final String ABI = "__stdcall";
    private static final String ISR = "__interrupt";

    @Override
    public void run() throws Exception {
        FunctionManager fm = currentProgram.getFunctionManager();
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
            if (ABI.equals(current)) {
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
                f.setCallingConvention(ABI);
                stdcall++;
            } catch (Exception ex) {
                failed++;
                println("WARN: could not set " + ABI + " on " + f.getName()
                        + " @ " + f.getEntryPoint() + ": " + ex.getMessage());
            }
        }

        println(String.format(
                "ApplyCallingConventions: set %s=%d preserved %s=%d already_ok/skipped=%d failed=%d",
                ABI, stdcall, ISR, interrupt, skipped, failed));
        if (failed > 0) {
            throw new IllegalStateException(failed + " calling-convention apply failures");
        }
        if (stdcall + interrupt + skipped == 0) {
            throw new IllegalStateException("no functions found to assign conventions");
        }
    }
}
