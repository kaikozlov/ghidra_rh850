//@category Verification
// Compare CC-RH V2.08.00's own assembler listing with the vendored decoder.
// Args: <expected-tsv> <recorded-disagreements-tsv>
import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class AssertV850CcrhListing extends GhidraScript {
    private static final Pattern NUMBER = Pattern.compile(
        "(?<![a-z0-9_])(?:0x[0-9a-f]+|[0-9a-f]*[a-f][0-9a-f]*|-?[0-9]+)(?![a-z0-9_])",
        Pattern.CASE_INSENSITIVE);

    private record Expected(long address, byte[] bytes, String listingMnemonic,
                            String listingOperands, String oracleMnemonic,
                            String oracleOperands, String comparisonClass,
                            String comparisonRule) {}

    private byte[] decodeBytes(String text) {
        byte[] result = new byte[text.length() / 2];
        for (int index = 0; index < result.length; index++) {
            result[index] = (byte) Integer.parseInt(text.substring(index * 2, index * 2 + 2), 16);
        }
        return result;
    }

    private List<Expected> readExpected(Path path) throws Exception {
        List<Expected> result = new ArrayList<>();
        for (String line : Files.readAllLines(path)) {
            if (line.isBlank() || line.startsWith("#")) continue;
            String[] fields = line.split("\\t", -1);
            if (fields.length != 8) throw new IllegalArgumentException("malformed oracle row: " + line);
            result.add(new Expected(Long.parseUnsignedLong(fields[0], 16), decodeBytes(fields[1]),
                fields[2], fields[3], fields[4], fields[5], fields[6], fields[7]));
        }
        return result;
    }

    private List<String> readDisagreements(Path path) throws Exception {
        List<String> result = new ArrayList<>();
        for (String line : Files.readAllLines(path)) {
            if (!line.isBlank() && !line.startsWith("#")) result.add(line);
        }
        return result;
    }

    private String operands(Instruction instruction) {
        List<String> result = new ArrayList<>();
        for (int index = 0; index < instruction.getNumOperands(); index++) {
            result.add(instruction.getDefaultOperandRepresentation(index));
        }
        return String.join(", ", result);
    }

    private String normalize(String text) {
        String value = text.toLowerCase(Locale.ROOT)
            .replace("ram:", "")
            .replaceAll("\\bsp\\b", "r3")
            .replaceAll("\\bgp\\b", "r4")
            .replaceAll("\\btp\\b", "r5")
            .replaceAll("\\bep\\b", "r30")
            .replaceAll("\\blp\\b", "r31")
            .replaceAll("\\s+", "")
            .replace("#", "");
        Matcher matcher = NUMBER.matcher(value);
        StringBuffer output = new StringBuffer();
        while (matcher.find()) {
            String token = matcher.group();
            long number;
            try {
                if (token.startsWith("0x")) number = Long.parseUnsignedLong(token.substring(2), 16);
                else if (token.matches(".*[a-f].*")) number = Long.parseUnsignedLong(token, 16);
                else number = Long.parseLong(token);
                if (number >= 0x80000000L && number <= 0xffffffffL) number -= 0x100000000L;
                matcher.appendReplacement(output, Long.toString(number));
            } catch (NumberFormatException exception) {
                matcher.appendReplacement(output, Matcher.quoteReplacement(token));
            }
        }
        matcher.appendTail(output);
        return output.toString();
    }

    private String canonicalOperands(Expected row, String operands, boolean compiler) {
        String value = normalize(operands);
        return switch (row.comparisonRule()) {
            case "", "apply-r-v850-pc9-and-condition-alias" -> value;
            case "memory-displacement-base-operands" -> {
                if (!compiler) yield value;
                Matcher load = Pattern.compile("(-?[0-9]+)\\[(r[0-9]+)\\],(r[0-9]+)").matcher(value);
                if (load.matches()) yield load.group(1) + "," + load.group(2) + "," + load.group(3);
                Matcher store = Pattern.compile("(r[0-9]+),(-?[0-9]+)\\[(r[0-9]+)\\]").matcher(value);
                if (store.matches()) yield store.group(1) + "," + store.group(2) + "," + store.group(3);
                throw new AssertionError("unrecognized compiler memory operand at "
                    + String.format("0x%x: ", row.address()) + row.oracleOperands());
            }
            case "indirect-lp-register" -> value.replace("[", "").replace("]", "");
            case "dispose-byte-count-mask-list" -> {
                if (!compiler) yield value;
                Matcher dispose = Pattern.compile("([0-9]+),0,\\[(r[0-9]+)\\]").matcher(value);
                if (!dispose.matches()) throw new AssertionError("unrecognized compiler dispose operand at "
                    + String.format("0x%x: ", row.address()) + row.oracleOperands());
                long byteCount = Long.parseLong(dispose.group(1));
                if ((byteCount & 3) != 0) throw new AssertionError("unaligned dispose byte count");
                yield (byteCount / 4) + ",{}," + dispose.group(2);
            }
            default -> throw new AssertionError("unknown comparison rule: " + row.comparisonRule());
        };
    }

    private String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte value : bytes) result.append(String.format("%02x", value & 0xff));
        return result.toString();
    }

    private String display(String mnemonic, String operands) {
        return operands.isBlank() ? mnemonic : mnemonic + " " + operands;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) throw new IllegalArgumentException(
            "usage: AssertV850CcrhListing.java <expected-tsv> <disagreements-tsv>");
        Path oraclePath = Path.of(args[0]);
        Path disagreementsPath = Path.of(args[1]);
        List<Expected> expected = readExpected(oraclePath);
        List<String> actualDisagreements = new ArrayList<>();
        int renderingConventions = 0;

        for (Expected row : expected) {
            Address address = toAddr(row.address());
            if (currentProgram.getListing().getInstructionAt(address) == null) {
                DisassembleCommand command = new DisassembleCommand(address, null, true);
                if (!command.applyTo(currentProgram, monitor)) {
                    throw new AssertionError(String.format("cannot decode CC-RH instruction at 0x%x", row.address()));
                }
            }
            Instruction instruction = currentProgram.getListing().getInstructionAt(address);
            if (instruction == null) {
                throw new AssertionError(String.format("no instruction at CC-RH offset 0x%x", row.address()));
            }
            if (instruction.getLength() != row.bytes().length) {
                throw new AssertionError(String.format(
                    "CC-RH 0x%x length=%d expected=%d", row.address(), instruction.getLength(), row.bytes().length));
            }
            byte[] actualBytes = new byte[row.bytes().length];
            currentProgram.getMemory().getBytes(address, actualBytes);
            if (!java.util.Arrays.equals(actualBytes, row.bytes())) {
                throw new AssertionError(String.format("CC-RH bytes drift at 0x%x", row.address()));
            }
            String actualMnemonic = instruction.getMnemonicString().toLowerCase(Locale.ROOT);
            String actualOperands = operands(instruction);
            boolean mnemonicMatches = actualMnemonic.equals(row.oracleMnemonic());
            boolean operandsMatch = canonicalOperands(row, actualOperands, false)
                .equals(canonicalOperands(row, row.oracleOperands(), true));
            if ("rendering-convention".equals(row.comparisonClass())) renderingConventions++;
            else if (!row.comparisonClass().isEmpty()) {
                throw new AssertionError("unknown comparison class: " + row.comparisonClass());
            }
            if (!mnemonicMatches || !operandsMatch) {
                String disagreement = String.format("%08x\t%s\tdecoder-defect\t%s\t%s",
                    row.address(), hex(row.bytes()),
                    display(row.listingMnemonic(), row.listingOperands()),
                    display(actualMnemonic, actualOperands));
                actualDisagreements.add(disagreement);
                println("DECODER-DEFECT " + disagreement);
            }
        }

        List<String> recorded = readDisagreements(disagreementsPath);
        if (!actualDisagreements.equals(recorded)) {
            throw new AssertionError("CC-RH listing disagreements changed: actual=" + actualDisagreements.size()
                + " recorded=" + recorded.size());
        }
        println("ASSERT v850-ccrh-listing: passed instructions=" + expected.size()
            + " rendering-conventions=" + renderingConventions
            + " decoder-defects=" + actualDisagreements.size());
    }
}
