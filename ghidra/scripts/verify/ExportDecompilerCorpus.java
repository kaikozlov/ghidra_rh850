//@author kaikozlov
//@category Verification
// Export one deterministic JSONL record for every recovered function's decompilation.
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;

public class ExportDecompilerCorpus extends GhidraScript {
    private static String jsonString(String value) {
        if (value == null) return "null";
        StringBuilder out = new StringBuilder(value.length() + 16);
        out.append('"');
        for (int i = 0; i < value.length(); i++) {
            char ch = value.charAt(i);
            switch (ch) {
                case '"': out.append("\\\""); break;
                case '\\': out.append("\\\\"); break;
                case '\b': out.append("\\b"); break;
                case '\f': out.append("\\f"); break;
                case '\n': out.append("\\n"); break;
                case '\r': out.append("\\r"); break;
                case '\t': out.append("\\t"); break;
                default:
                    if (ch < 0x20) out.append(String.format("\\u%04x", (int) ch));
                    else out.append(ch);
            }
        }
        out.append('"');
        return out.toString();
    }

    private static String errorText(Throwable error) {
        String message = error.getMessage();
        if (message == null || message.isBlank()) return error.getClass().getSimpleName();
        return error.getClass().getSimpleName() + ": " + message;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 1 || args.length > 2) {
            throw new IllegalArgumentException(
                "usage: ExportDecompilerCorpus.java OUTPUT_JSONL [TIMEOUT_SECONDS]"
            );
        }
        Path output = Path.of(args[0]).toAbsolutePath().normalize();
        int timeoutSeconds = args.length == 2 ? Integer.parseInt(args[1]) : 60;
        if (timeoutSeconds < 0) {
            throw new IllegalArgumentException("TIMEOUT_SECONDS must be >= 0");
        }
        if (output.getParent() != null) Files.createDirectories(output.getParent());

        DecompInterface decompiler = new DecompInterface();
        if (!decompiler.openProgram(currentProgram)) {
            throw new IllegalStateException("failed to open program in decompiler");
        }

        int count = 0;
        int completedCount = 0;
        int failedCount = 0;
        try (BufferedWriter writer = Files.newBufferedWriter(
                output, StandardCharsets.UTF_8)) {
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function function = functions.next();
                boolean completed = false;
                String error = "";
                String code = "";
                try {
                    DecompileResults results = decompiler.decompileFunction(
                        function, timeoutSeconds, monitor
                    );
                    completed = results != null && results.decompileCompleted()
                        && results.getDecompiledFunction() != null;
                    if (completed) {
                        code = results.getDecompiledFunction().getC();
                    }
                    else if (results == null) {
                        error = "decompiler returned null results";
                    }
                    else {
                        error = results.getErrorMessage();
                        if (error == null) error = "decompilation did not complete";
                    }
                }
                catch (Throwable throwable) {
                    error = errorText(throwable);
                }

                String signature = null;
                try {
                    signature = function.getPrototypeString(false, false);
                }
                catch (Throwable ignored) {
                    // Preserve the function even if Ghidra cannot render its prototype.
                }

                String callingConvention = function.getCallingConventionName();
                long entry = function.getEntryPoint().getOffset();
                String entryAddress = String.format("0x%08x", entry);
                String addressSpace = function.getEntryPoint().getAddressSpace().getName();
                long bodySize = function.getBody().getNumAddresses();

                StringBuilder record = new StringBuilder(code.length() + 512);
                record.append('{');
                record.append("\"record\":\"function\",");
                record.append("\"entry_addr\":").append(jsonString(entryAddress)).append(',');
                record.append("\"address_space\":").append(jsonString(addressSpace)).append(',');
                record.append("\"name\":").append(jsonString(function.getName())).append(',');
                record.append("\"signature\":").append(jsonString(signature)).append(',');
                record.append("\"calling_convention\":")
                    .append(jsonString(callingConvention)).append(',');
                record.append("\"body_size\":").append(bodySize).append(',');
                record.append("\"is_thunk\":").append(function.isThunk()).append(',');
                record.append("\"decompile_completed\":").append(completed).append(',');
                record.append("\"decompile_error\":").append(jsonString(error)).append(',');
                record.append("\"decompiled_c\":").append(jsonString(code));
                record.append('}');
                writer.write(record.toString());
                writer.newLine();

                count++;
                if (completed) completedCount++;
                else failedCount++;
                if (count % 250 == 0) {
                    println(String.format(
                        "ExportDecompilerCorpus: processed %d functions (%d complete, %d failed)",
                        count, completedCount, failedCount
                    ));
                }
            }
        }
        finally {
            decompiler.dispose();
        }

        println(String.format(
            "ExportDecompilerCorpus: wrote %d functions to %s (%d complete, %d failed)",
            count, output, completedCount, failedCount
        ));
    }
}
