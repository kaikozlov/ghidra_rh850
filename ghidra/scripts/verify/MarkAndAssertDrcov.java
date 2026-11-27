// Load one single-module P1M-E drcov trace, highlight its instructions, and assert exactness.
// @category Verification
// Args: <absolute-drcov-path>

import java.io.BufferedReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;

public class MarkAndAssertDrcov extends GhidraScript {
    private static final Pattern TABLE = Pattern.compile("BB Table: ([0-9]+) bbs");
    private static final Pattern BLOCK =
        Pattern.compile("module\\[ *([0-9]+)\\]:[ \\t]*0x([0-9a-fA-F]+),[ \\t]*([0-9]+)");

    private static long parseUnsigned(String value) {
        return Long.parseUnsignedLong(value.trim().replaceFirst("^0[xX]", ""), 16);
    }

    private void require(boolean condition, String detail) {
        if (!condition) throw new IllegalStateException(detail);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args.length == 1, "expected one absolute drcov path");
        Path path = Path.of(args[0]);
        AddressSet tracedBytes = new AddressSet();
        Set<Long> tracedStarts = new HashSet<>();
        long base;
        long end;
        int count;
        try (BufferedReader input = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
            require("DRCOV VERSION: 3".equals(input.readLine()), "unsupported drcov version");
            require("DRCOV FLAVOR: drcov".equals(input.readLine()), "unsupported drcov flavor");
            require("Module Table: version 5, count 1".equals(input.readLine()),
                "expected one version-5 module");
            require(("Columns: id, containing_id, start, end, entry, offset, "
                + "preferred_base, path").equals(input.readLine()),
                "unexpected module columns");
            String[] module = input.readLine().split(", ", 8);
            require(module.length == 8 && module[0].trim().equals("0")
                && module[1].trim().equals("0"), "invalid module row");
            base = parseUnsigned(module[2]);
            end = parseUnsigned(module[3]);
            require(base == currentProgram.getMinAddress().getOffset(),
                "drcov module base does not match the program");
            require(end > base, "empty drcov module");
            require(parseUnsigned(module[5]) == 0
                && parseUnsigned(module[6]) == base,
                "unsupported module offset or preferred base");
            Matcher table = TABLE.matcher(input.readLine());
            require(table.matches(), "missing basic-block table");
            count = Integer.parseInt(table.group(1));
            require("module id, start, size:".equals(input.readLine()),
                "invalid basic-block text heading");
            for (int index = 0; index < count; index++) {
                String line = input.readLine();
                require(line != null, "truncated drcov instruction table");
                Matcher block = BLOCK.matcher(line);
                require(block.matches(), "invalid instruction record " + index);
                int moduleId = Integer.parseInt(block.group(1));
                long pc = base + Long.parseUnsignedLong(block.group(2), 16);
                int size = Integer.parseInt(block.group(3));
                require(moduleId == 0 && size > 0 && pc + size <= end,
                    "invalid instruction record " + index);
                require(tracedStarts.add(pc), "duplicate instruction record at " + toAddr(pc));
                Address address = toAddr(pc);
                Instruction instruction = currentProgram.getListing().getInstructionAt(address);
                require(instruction != null, "no instruction at " + address);
                require(instruction.getLength() == size,
                    "instruction size mismatch at " + address + ": trace=" + size
                    + " listing=" + instruction.getLength());
                tracedBytes.add(address, address.add(size - 1L));
            }
            require(input.readLine() == null, "trailing rows after drcov instruction table");
        }

        setCurrentHighlight(tracedBytes);
        require(currentHighlight != null && currentHighlight.xor(tracedBytes).isEmpty(),
            "highlighted byte set differs from traced instruction bytes");
        Set<Long> markedStarts = new HashSet<>();
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(currentHighlight, true);
        while (instructions.hasNext()) {
            markedStarts.add(instructions.next().getAddress().getOffset());
        }
        require(markedStarts.equals(tracedStarts),
            "highlighted instruction starts differ from the traced set");
        println("PASS MarkAndAssertDrcov: records=" + count
            + " unique_instructions=" + tracedStarts.size()
            + " highlighted_bytes=" + tracedBytes.getNumAddresses());
    }
}
