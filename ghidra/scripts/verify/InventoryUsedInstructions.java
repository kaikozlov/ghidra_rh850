//@author kaikozlov
//@category Verification
// Export every distinct instruction mnemonic used in the program with counts,
// a representative address, flow type, and p-code userops. Writes CSV to the
// first script argument (absolute path).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.PcodeOp;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;

public class InventoryUsedInstructions extends GhidraScript {
    static class Row {
        String mnemonic;
        long count;
        String sampleAddr;
        String flow;
        String userops;
        String bytes;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 2) {
            throw new IllegalArgumentException(
                    "expected absolute CSV output path and user-op allowlist path");
        }
        Map<String, Row> rows = new TreeMap<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            String m = ins.getMnemonicString();
            if (m == null) continue;
            Row row = rows.get(m);
            if (row == null) {
                row = new Row();
                row.mnemonic = m;
                row.count = 0;
                row.sampleAddr = ins.getAddress().toString();
                row.flow = String.valueOf(ins.getFlowType());
                row.bytes = bytesHex(ins);
                row.userops = userOps(ins);
                rows.put(m, row);
            }
            row.count++;
        }
        try (PrintWriter out = new PrintWriter(args[0])) {
            out.println("mnemonic,count,sample_addr,flow,bytes,userops");
            for (Row row : rows.values()) {
                out.printf("%s,%d,%s,%s,%s,%s%n",
                    csv(row.mnemonic), row.count, csv(row.sampleAddr),
                    csv(row.flow), csv(row.bytes), csv(row.userops));
            }
        }
        println("InventoryUsedInstructions: wrote " + rows.size()
                + " mnemonics to " + args[0]);
        enforceAllowlist(rows.values(), Path.of(args[1]));
    }

    private static String bytesHex(Instruction ins) throws Exception {
        byte[] b = ins.getBytes();
        StringBuilder sb = new StringBuilder();
        for (byte value : b) sb.append(String.format("%02x", value & 0xff));
        return sb.toString();
    }

    private String userOps(Instruction ins) {
        Set<String> ops = new TreeSet<>();
        for (PcodeOp op : ins.getPcode()) {
            if (op.getOpcode() == PcodeOp.CALLOTHER) {
                int index = (int) op.getInput(0).getOffset();
                String name = currentProgram.getLanguage().getUserDefinedOpName(index);
                ops.add(name == null ? "CALLOTHER#" + index : name);
            }
        }
        return String.join("|", ops);
    }

    private void enforceAllowlist(Collection<Row> rows, Path path) throws Exception {
        Set<String> allowed = new TreeSet<>();
        for (String raw : Files.readAllLines(path)) {
            String line = raw.trim();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] parts = line.split("\\t", 2);
            if (parts.length != 2 || parts[0].isBlank() || parts[1].isBlank()) {
                throw new IllegalStateException("invalid processor user-op allowlist line: " + raw);
            }
            if (!allowed.add(parts[0])) {
                throw new IllegalStateException("duplicate allowlisted user-op " + parts[0]);
            }
        }
        Set<String> used = new TreeSet<>();
        for (Row row : rows) {
            if (row.userops == null || row.userops.isBlank()) continue;
            used.addAll(Arrays.asList(row.userops.split("\\|")));
        }
        Set<String> unapproved = new TreeSet<>(used);
        unapproved.removeAll(allowed);
        Set<String> stale = new TreeSet<>(allowed);
        stale.removeAll(used);
        if (!unapproved.isEmpty() || !stale.isEmpty()) {
            throw new IllegalStateException("user-op allowlist mismatch: unapproved="
                    + unapproved + " stale=" + stale);
        }
        println("ASSERT processor-userops: approved=" + used);
    }

    private static String csv(String s) {
        if (s == null) return "";
        if (s.contains(",") || s.contains("\"") || s.contains("\n")) {
            return "\"" + s.replace("\"", "\"\"") + "\"";
        }
        return s;
    }
}
