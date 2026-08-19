//@author kaikozlov
//@category Verification
// Export address-independent instruction-shape fingerprints for cross-variant matching.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.RefType;
import java.io.BufferedWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.TreeSet;

public class ExportFunctionStructuralFingerprints extends GhidraScript {
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

    private static String stringArrayJson(List<String> values) {
        StringBuilder out = new StringBuilder(values.size() * 12 + 2);
        out.append('[');
        for (int i = 0; i < values.size(); i++) {
            if (i != 0) out.append(',');
            out.append(jsonString(values.get(i)));
        }
        out.append(']');
        return out.toString();
    }

    private static String longArrayJson(TreeSet<Long> values) {
        StringBuilder out = new StringBuilder(values.size() * 14 + 2);
        out.append('[');
        boolean first = true;
        for (long value : values) {
            if (!first) out.append(',');
            first = false;
            out.append(jsonString(String.format(Locale.ROOT, "0x%08x", value)));
        }
        out.append(']');
        return out.toString();
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException(
                "usage: ExportFunctionStructuralFingerprints.java OUTPUT_JSONL"
            );
        }
        Path output = Path.of(args[0]).toAbsolutePath().normalize();
        if (output.getParent() != null) Files.createDirectories(output.getParent());

        int functionCount = 0;
        int instructionCount = 0;
        try (BufferedWriter writer = Files.newBufferedWriter(output, StandardCharsets.UTF_8)) {
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function function = functions.next();
                List<String> mnemonics = new ArrayList<>();
                List<String> lengths = new ArrayList<>();
                TreeSet<Long> directCalls = new TreeSet<>();
                int conditionalBranches = 0;
                int unconditionalBranches = 0;
                int indirectCalls = 0;
                int returns = 0;

                InstructionIterator instructions = currentProgram.getListing().getInstructions(
                    function.getBody(), true
                );
                while (instructions.hasNext()) {
                    Instruction instruction = instructions.next();
                    String mnemonic = instruction.getMnemonicString();
                    mnemonics.add(mnemonic == null ? "" : mnemonic.toLowerCase(Locale.ROOT));
                    lengths.add(Integer.toString(instruction.getLength()));
                    instructionCount++;

                    RefType flow = instruction.getFlowType();
                    if (flow != null) {
                        if (flow.isCall()) {
                            Address[] flows = instruction.getFlows();
                            if (flows.length == 0) {
                                indirectCalls++;
                            }
                            else {
                                for (Address target : flows) {
                                    if (target != null && target.isMemoryAddress()) {
                                        directCalls.add(target.getOffset());
                                    }
                                }
                            }
                        }
                        if (flow.isJump()) {
                            if (flow.isConditional()) conditionalBranches++;
                            else unconditionalBranches++;
                        }
                        if (flow.isTerminal()) returns++;
                    }
                }

                long entry = function.getEntryPoint().getOffset();
                StringBuilder record = new StringBuilder(mnemonics.size() * 12 + 512);
                record.append('{');
                record.append("\"record\":\"function-structural-fingerprint\",");
                record.append("\"entry_addr\":")
                    .append(jsonString(String.format(Locale.ROOT, "0x%08x", entry))).append(',');
                record.append("\"address_space\":")
                    .append(jsonString(function.getEntryPoint().getAddressSpace().getName())).append(',');
                record.append("\"name\":").append(jsonString(function.getName())).append(',');
                record.append("\"body_size\":").append(function.getBody().getNumAddresses()).append(',');
                record.append("\"instruction_count\":").append(mnemonics.size()).append(',');
                record.append("\"mnemonics\":").append(stringArrayJson(mnemonics)).append(',');
                record.append("\"instruction_lengths\":").append(stringArrayJson(lengths)).append(',');
                record.append("\"direct_call_targets\":").append(longArrayJson(directCalls)).append(',');
                record.append("\"direct_call_target_count\":").append(directCalls.size()).append(',');
                record.append("\"indirect_call_count\":").append(indirectCalls).append(',');
                record.append("\"conditional_branch_count\":").append(conditionalBranches).append(',');
                record.append("\"unconditional_branch_count\":").append(unconditionalBranches).append(',');
                record.append("\"return_count\":").append(returns);
                record.append('}');
                writer.write(record.toString());
                writer.newLine();
                functionCount++;
            }
        }
        println(String.format(
            Locale.ROOT,
            "ExportFunctionStructuralFingerprints: wrote %d functions / %d instructions to %s",
            functionCount, instructionCount, output
        ));
    }
}
