//@author kaikozlov
//@category Verification
// Export every distinct instruction mnemonic used in the program with counts,
// a representative address, flow type, and p-code userops. Writes CSV to the
// first script argument (absolute path).
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.pcode.PcodeOp;
import java.io.PrintWriter;
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
        if (args.length != 1) {
            throw new IllegalArgumentException("expected absolute CSV output path");
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
    }

    private static String bytesHex(Instruction ins) throws Exception {
        byte[] b = ins.getBytes();
        StringBuilder sb = new StringBuilder();
        for (byte value : b) sb.append(String.format("%02x", value & 0xff));
        return sb.toString();
    }

    private static String userOps(Instruction ins) {
        Set<String> ops = new TreeSet<>();
        for (PcodeOp op : ins.getPcode()) {
            if (op.getOpcode() == PcodeOp.CALLOTHER) {
                ops.add(op.getMnemonic());
            }
        }
        return String.join("|", ops);
    }

    private static String csv(String s) {
        if (s == null) return "";
        if (s.contains(",") || s.contains("\"") || s.contains("\n")) {
            return "\"" + s.replace("\"", "\"\"") + "\"";
        }
        return s;
    }
}
