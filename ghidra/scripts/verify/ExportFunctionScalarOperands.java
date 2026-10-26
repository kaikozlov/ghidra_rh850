//@author kaikozlov
//@category Verification
// Export per-instruction scalar operands for homologous-function security diffs.
import ghidra.app.script.GhidraScript;
import ghidra.framework.Application;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.scalar.Scalar;
import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

public class ExportFunctionScalarOperands extends GhidraScript {
    private static String jsonString(String value) {
        if (value == null) return "null";
        StringBuilder out = new StringBuilder(value.length() + 16).append('"');
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
        return out.append('"').toString();
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("usage: ExportFunctionScalarOperands.java OUTPUT_JSONL");
        }
        Path output = Path.of(args[0]).toAbsolutePath().normalize();
        if (output.getParent() != null) Files.createDirectories(output.getParent());

        int functionCount = 0;
        int instructionCount = 0;
        try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            writer.write("{\"record\":\"metadata\",\"schema_version\":1," +
                "\"ghidra_version\":" + jsonString(Application.getApplicationVersion()) + "," +
                "\"program_name\":" + jsonString(currentProgram.getName()) + "," +
                "\"executable_sha256\":" + jsonString(currentProgram.getExecutableSHA256()) + "," +
                "\"language_id\":" + jsonString(currentProgram.getLanguageID().getIdAsString()) + "}");
            writer.newLine();

            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function function = functions.next();
                long entry = function.getEntryPoint().getOffset();
                StringBuilder record = new StringBuilder(2048);
                record.append("{\"record\":\"function-scalar-operands\",\"entry_addr\":")
                    .append(jsonString(String.format(Locale.ROOT, "0x%08x", entry)))
                    .append(",\"name\":").append(jsonString(function.getName()))
                    .append(",\"instructions\":[");
                boolean firstInstruction = true;
                InstructionIterator instructions = currentProgram.getListing().getInstructions(
                    function.getBody(), true
                );
                while (instructions.hasNext()) {
                    Instruction instruction = instructions.next();
                    if (!firstInstruction) record.append(',');
                    firstInstruction = false;
                    long address = instruction.getAddress().getOffset();
                    record.append("{\"address\":")
                        .append(jsonString(String.format(Locale.ROOT, "0x%08x", address)))
                        .append(",\"mnemonic\":")
                        .append(jsonString(instruction.getMnemonicString().toLowerCase(Locale.ROOT)))
                        .append(",\"flow\":")
                        .append(jsonString(instruction.getFlowType().toString()))
                        .append(",\"operands\":[");
                    for (int operand = 0; operand < instruction.getNumOperands(); operand++) {
                        if (operand != 0) record.append(',');
                        record.append("{\"index\":").append(operand)
                            .append(",\"text\":")
                            .append(jsonString(instruction.getDefaultOperandRepresentation(operand)))
                            .append(",\"scalars\":[");
                        boolean firstScalar = true;
                        for (Object object : instruction.getOpObjects(operand)) {
                            if (!(object instanceof Scalar)) continue;
                            Scalar scalar = (Scalar)object;
                            if (!firstScalar) record.append(',');
                            firstScalar = false;
                            record.append("{\"bits\":").append(scalar.bitLength())
                                .append(",\"unsigned\":")
                                .append(jsonString(String.format(Locale.ROOT, "0x%x", scalar.getUnsignedValue())))
                                .append(",\"signed\":").append(scalar.getSignedValue())
                                .append('}');
                        }
                        record.append("]}");
                    }
                    record.append("]}");
                    instructionCount++;
                }
                record.append("]}");
                writer.write(record.toString());
                writer.newLine();
                functionCount++;
            }
        }
        println(String.format(
            Locale.ROOT,
            "ExportFunctionScalarOperands: wrote %d functions / %d instructions to %s",
            functionCount, instructionCount, output
        ));
    }
}
