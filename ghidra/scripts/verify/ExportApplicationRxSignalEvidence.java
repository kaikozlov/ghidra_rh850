//@author kaikozlov
//@category Investigation
// Read-only export of COM Rx signal extraction evidence. One row per recovered
// bitfield call to application_com_receive_signal @ 0x7C03E, plus opaque
// property-4 signals proved from CodeFlash tables 0x25902/0x2591E.
// Does not invent OEM names. Output is consumed by generate_application_rx_map.py
// and independently re-checked by tests/verify_application_receive.py against
// raw CodeFlash bytes.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class ExportApplicationRxSignalEvidence extends GhidraScript {
    private static final long RECEIVE_SIGNAL = 0x7c03eL;
    private static final long RECEIVE_BYTES = 0x7d63eL;
    private static final long GP = 0xfebeb800L;
    private static final long OPAQUE_SID_TABLE = 0x25902L;
    private static final long OPAQUE_OFF_TABLE = 0x2591eL;
    private static final long COM_PDU = 0x2273cL;
    private static final int OPAQUE_COUNT = 14;

    private static final String HEADER = String.join(",",
            "signal_id",
            "extract_kind",
            "unpacker",
            "body_size",
            "body_sha256",
            "call_site",
            "buf_off",
            "bit_len",
            "start_arg",
            "signed",
            "dest",
            "dest_width",
            "first_consumer",
            "window_lo",
            "window_hi");

    private static final Pattern IMM = Pattern.compile("(-?0x[0-9a-fA-F]+|-?\\d+)");

    private static final class Row {
        int signalId;
        String extractKind;
        long unpacker;
        int bodySize;
        String bodySha;
        long callSite;
        int bufOff;
        int bitLen;
        int startArg;
        int signed;
        String dest;
        int destWidth;
        String firstConsumer;
        long windowLo;
        long windowHi;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected absolute CSV output path");
        }
        Path out = Path.of(args[0]);
        if (!out.isAbsolute()) {
            throw new IllegalArgumentException("output path must be absolute: " + out);
        }

        List<Row> rows = new ArrayList<>();
        rows.addAll(exportBitfieldRows());
        rows.addAll(exportOpaqueRows());
        rows.sort(Comparator.comparingInt(r -> r.signalId));

        // Keep one row per signal_id (first call site wins; duplicates are errors).
        Map<Integer, Row> bySid = new TreeMap<>();
        for (Row r : rows) {
            Row prev = bySid.putIfAbsent(r.signalId, r);
            if (prev != null && !sameExtraction(prev, r)) {
                throw new IllegalStateException(String.format(
                        "conflicting evidence for signal %d: %s vs %s",
                        r.signalId, summarize(prev), summarize(r)));
            }
        }

        Files.createDirectories(out.getParent());
        try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out, StandardCharsets.UTF_8))) {
            w.println(HEADER);
            for (Row r : bySid.values()) {
                w.printf(Locale.ROOT,
                        "%d,%s,0x%X,%d,%s,0x%X,%d,%d,%d,%d,%s,%d,%s,0x%X,0x%X%n",
                        r.signalId, r.extractKind, r.unpacker, r.bodySize, r.bodySha,
                        r.callSite, r.bufOff, r.bitLen, r.startArg, r.signed,
                        r.dest, r.destWidth, csvEscape(r.firstConsumer),
                        r.windowLo, r.windowHi);
            }
        }
        println("ExportApplicationRxSignalEvidence: wrote " + bySid.size()
                + " rows to " + out);
    }

    private List<Row> exportBitfieldRows() throws Exception {
        List<Row> rows = new ArrayList<>();
        Address target = toAddr(RECEIVE_SIGNAL);
        ReferenceManager refs = currentProgram.getReferenceManager();
        ReferenceIterator it = refs.getReferencesTo(target);
        while (it.hasNext()) {
            Reference ref = it.next();
            if (!ref.getReferenceType().isCall()) continue;
            long callSite = ref.getFromAddress().getOffset();
            Function fn = getFunctionContaining(ref.getFromAddress());
            if (fn == null) {
                println("skip call with no function @" + String.format("0x%x", callSite));
                continue;
            }
            Row parsed = parseCallSite(fn, callSite);
            if (parsed == null) {
                println("WARN: could not parse args at " + String.format("0x%x", callSite));
                continue;
            }
            rows.add(parsed);
        }
        return rows;
    }

    private List<Row> exportOpaqueRows() throws Exception {
        List<Row> rows = new ArrayList<>();
        // Opaque helpers copy whole PDUs; prove membership from tables and body hashes.
        long[] helpers = {0x68368L, 0x6875eL};
        Map<Long, String> helperSha = new HashMap<>();
        Map<Long, Integer> helperSize = new HashMap<>();
        for (long ea : helpers) {
            Function fn = getFunctionAt(toAddr(ea));
            if (fn == null) {
                throw new IllegalStateException("missing opaque helper function at 0x"
                        + Long.toHexString(ea));
            }
            int size = (int) fn.getBody().getNumAddresses();
            helperSize.put(ea, size);
            helperSha.put(ea, sha256(ea, size));
        }
        for (int i = 0; i < OPAQUE_COUNT; i++) {
            int sid = readU16(OPAQUE_SID_TABLE + 2L * i);
            int bufOff = readU16(OPAQUE_OFF_TABLE + 2L * i);
            int pdu = readU16(0x224e4L + 2L * sid);
            int comLen = readU16(COM_PDU + 8L * pdu + 4);
            long unpacker = (i < 8) ? 0x68368L : 0x6875eL;
            Row r = new Row();
            r.signalId = sid;
            r.extractKind = "opaque_pdu_bytes";
            r.unpacker = unpacker;
            r.bodySize = helperSize.get(unpacker);
            r.bodySha = helperSha.get(unpacker);
            r.callSite = unpacker; // whole-function evidence; no single receive_signal call
            r.bufOff = bufOff;
            r.bitLen = comLen * 8;
            r.startArg = 0;
            r.signed = 0;
            r.dest = String.format("COM+0x%X/opaque-shadow", bufOff);
            r.destWidth = comLen;
            r.firstConsumer = "configured-unresolved; bound=opaque PDU shadow compare; no stable per-signal RAM dest";
            r.windowLo = OPAQUE_SID_TABLE;
            r.windowHi = OPAQUE_OFF_TABLE + 2L * OPAQUE_COUNT;
            rows.add(r);
        }
        return rows;
    }

    private Row parseCallSite(Function fn, long callSite) throws Exception {
        long entry = fn.getEntryPoint().getOffset();
        int bodySize = (int) fn.getBody().getNumAddresses();
        long windowLo = Math.max(entry, callSite - 0x40);
        long windowHi = callSite;

        Integer signalId = null;
        Integer bufOff = null;
        Integer bitLen = null;
        Integer startArg = null;
        Integer signed = null;
        Long dest = null;

        Listing listing = currentProgram.getListing();
        InstructionIterator insts = listing.getInstructions(toAddr(windowLo), true);
        while (insts.hasNext()) {
            Instruction ins = insts.next();
            long ea = ins.getAddress().getOffset();
            if (ea >= callSite) break;
            String mnem = ins.getMnemonicString().toLowerCase(Locale.ROOT);
            String ops = ins.toString(); // includes mnemonic+operands
            // Prefer operand strings.
            String op0 = (ins.getNumOperands() > 0) ? ins.getDefaultOperandRepresentation(0) : "";
            String op1 = (ins.getNumOperands() > 1) ? ins.getDefaultOperandRepresentation(1) : "";
            String op2 = (ins.getNumOperands() > 2) ? ins.getDefaultOperandRepresentation(2) : "";

            if (mnem.equals("movea")) {
                Integer imm = parseImm(op0);
                if (imm == null) continue;
                // movea imm, r0, rN
                if (op1.equalsIgnoreCase("r0") && op2.equalsIgnoreCase("r6")) {
                    signalId = imm & 0xffff;
                } else if (op1.equalsIgnoreCase("r0") && op2.equalsIgnoreCase("r7")) {
                    bufOff = imm & 0xffff;
                } else if (op1.equalsIgnoreCase("r0") && op2.equalsIgnoreCase("r8")) {
                    bitLen = imm & 0xff;
                } else if (op1.equalsIgnoreCase("gp") && op2.equalsIgnoreCase("r1")) {
                    dest = (GP + (long) imm) & 0xffffffffL;
                }
            } else if (mnem.equals("mov")) {
                // mov r8, r9 copies the current bit-length into start_arg.
                if (op0.equalsIgnoreCase("r8") && op1.equalsIgnoreCase("r9") && bitLen != null) {
                    startArg = bitLen;
                    continue;
                }
                Integer imm = parseImm(op0);
                if (imm == null) continue;
                if (op1.equalsIgnoreCase("r8")) bitLen = imm & 0xff;
                if (op1.equalsIgnoreCase("r9")) startArg = imm & 0xff;
                if (op1.equalsIgnoreCase("r1") && imm == 1) {
                    // preparative mov 1,r1 before sst.w signed=1
                    signed = 1;
                }
            } else if (mnem.equals("sst.w")) {
                // sst.w 0x0, ep, rX  -> signed flag on stack slot 0
                if (op0.equals("0x0") || op0.equals("0")) {
                    if (op2.equalsIgnoreCase("r0")) signed = 0;
                    if (op2.equalsIgnoreCase("r1")) signed = 1;
                }
            }
        }
        if (signalId == null || bufOff == null || bitLen == null || startArg == null
                || signed == null || dest == null) {
            return null;
        }

        Row r = new Row();
        r.signalId = signalId;
        r.extractKind = "bitfield";
        r.unpacker = entry;
        r.bodySize = bodySize;
        r.bodySha = sha256(entry, bodySize);
        r.callSite = callSite;
        r.bufOff = bufOff;
        r.bitLen = bitLen;
        r.startArg = startArg;
        r.signed = signed;
        r.dest = String.format("0x%X", dest);
        r.destWidth = widthFor(bitLen);
        r.firstConsumer = firstConsumer(dest, entry);
        r.windowLo = windowLo;
        r.windowHi = windowHi;
        return r;
    }

    private String firstConsumer(long dest, long unpackerEntry) {
        Address a = toAddr(dest);
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(a);
        long best = Long.MAX_VALUE;
        while (it.hasNext()) {
            Reference ref = it.next();
            RefType rt = ref.getReferenceType();
            if (!rt.isRead()) continue;
            Function fn = getFunctionContaining(ref.getFromAddress());
            if (fn == null) continue;
            long ea = fn.getEntryPoint().getOffset();
            // Exclude COM unpacker cluster and the receive helper itself.
            if (ea == RECEIVE_SIGNAL || ea == RECEIVE_BYTES) continue;
            if (ea >= 0x4a200L && ea <= 0x4b700L) continue;
            if (ea == unpackerEntry) continue;
            if (ea < best) best = ea;
        }
        if (best == Long.MAX_VALUE) {
            return "configured-unresolved; bound=Ghidra READ xref of dest excluding COM unpacker cluster 0x4A200-0x4B700";
        }
        return String.format("0x%X", best);
    }

    private static int widthFor(int bitLen) {
        if (bitLen <= 8) return 1;
        if (bitLen % 8 == 0) return bitLen / 8;
        return 4;
    }

    private Integer parseImm(String tok) {
        if (tok == null) return null;
        Matcher m = IMM.matcher(tok.trim());
        if (!m.matches()) return null;
        return (int) Long.decode(m.group(1)).longValue();
    }

    private int readU16(long addr) throws MemoryAccessException {
        byte[] b = new byte[2];
        currentProgram.getMemory().getBytes(toAddr(addr), b);
        return (b[0] & 0xff) | ((b[1] & 0xff) << 8);
    }

    private String sha256(long addr, int size) throws Exception {
        byte[] b = new byte[size];
        currentProgram.getMemory().getBytes(toAddr(addr), b);
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        byte[] dig = md.digest(b);
        StringBuilder sb = new StringBuilder(dig.length * 2);
        for (byte v : dig) sb.append(String.format("%02x", v));
        return sb.toString();
    }

    private static boolean sameExtraction(Row a, Row b) {
        return a.extractKind.equals(b.extractKind)
                && a.unpacker == b.unpacker
                && a.bufOff == b.bufOff
                && a.bitLen == b.bitLen
                && a.startArg == b.startArg
                && a.signed == b.signed
                && a.dest.equals(b.dest);
    }

    private static String summarize(Row r) {
        return String.format(Locale.ROOT, "unp=0x%x call=0x%x buf=%d len=%d start=%d signed=%d dest=%s",
                r.unpacker, r.callSite, r.bufOff, r.bitLen, r.startArg, r.signed, r.dest);
    }

    private static String csvEscape(String s) {
        if (s.indexOf(',') < 0 && s.indexOf('"') < 0) return s;
        return "\"" + s.replace("\"", "\"\"") + "\"";
    }
}
