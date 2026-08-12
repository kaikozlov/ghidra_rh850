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
    private static final long SIG2PDU = 0x224e4L;
    private static final long ACCEPTANCE = 0x231a0L;
    private static final long SECOC_RECORDS = 0x25970L;
    private static final int SECOC_RECORD_SIZE = 0x50;
    private static final int OPAQUE_COUNT = 14;
    private static final int RX_SIGNAL_FIRST = 58;
    private static final int SIGNAL_COUNT = 300;

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
            "window_hi",
            "classification",
            "classification_basis");

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
        String classification;
        String classificationBasis;
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

        // Keep one positive row per signal_id (first equivalent call site wins).
        Map<Integer, Row> bySid = new TreeMap<>();
        for (Row r : rows) {
            Row prev = bySid.putIfAbsent(r.signalId, r);
            if (prev != null && !sameExtraction(prev, r)) {
                throw new IllegalStateException(String.format(
                        "conflicting evidence for signal %d: %s vs %s",
                        r.signalId, summarize(prev), summarize(r)));
            }
        }

        // Classify every configured Rx signal. A negative row means the signal ID is
        // present in generated COM configuration but absent from the complete stock
        // receive-signal/group-byte extraction census. This is intentionally a COM
        // extraction negative, not a claim that the corresponding wire bits are unused
        // by every possible direct-buffer consumer.
        Map<Integer, Boolean> pduHasExtraction = new HashMap<>();
        for (Row r : bySid.values()) {
            int pdu = readU16(SIG2PDU + 2L * r.signalId);
            pduHasExtraction.put(pdu, true);
        }
        for (int sid = RX_SIGNAL_FIRST; sid < SIGNAL_COUNT; sid++) {
            if (bySid.containsKey(sid)) continue;
            int pdu = readU16(SIG2PDU + 2L * sid);
            Row r = negativeRow(sid, pdu, Boolean.TRUE.equals(pduHasExtraction.get(pdu)));
            bySid.put(sid, r);
        }

        Files.createDirectories(out.getParent());
        try (PrintWriter w = new PrintWriter(Files.newBufferedWriter(out, StandardCharsets.UTF_8))) {
            w.println(HEADER);
            for (Row r : bySid.values()) {
                w.printf(Locale.ROOT,
                        "%d,%s,0x%X,%d,%s,0x%X,%d,%d,%d,%d,%s,%d,%s,0x%X,0x%X,%s,%s%n",
                        r.signalId, r.extractKind, r.unpacker, r.bodySize, r.bodySha,
                        r.callSite, r.bufOff, r.bitLen, r.startArg, r.signed,
                        r.dest, r.destWidth, csvEscape(r.firstConsumer),
                        r.windowLo, r.windowHi, r.classification,
                        csvEscape(r.classificationBasis));
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
            r.firstConsumer = "opaque PDU bytes consumed by crypto-test shadow/stability logic; no stable per-signal RAM dest";
            r.windowLo = OPAQUE_SID_TABLE;
            r.windowHi = OPAQUE_OFF_TABLE + 2L * OPAQUE_COUNT;
            r.classification = "extracted_group_bytes";
            r.classificationBasis = "signal-ID/offset tables 0x25902/0x2591E plus application_com_receive_signal_group_bytes callers";
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
        Long r1DirectDest = null;
        Integer r1StackOffset = null;
        Integer stackDestOffset = null;

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
                    // Track the current r1 pointer, but do not call it the receive
                    // destination until generated code stores r1 into stack argument
                    // slot +4. Otherwise a later stack-temporary call can inherit a
                    // stale GP pointer from the previous receive_signal call.
                    r1DirectDest = (GP + (long) imm) & 0xffffffffL;
                    r1StackOffset = null;
                } else if (op1.equalsIgnoreCase("sp") && op2.equalsIgnoreCase("r1")) {
                    r1StackOffset = imm;
                    r1DirectDest = null;
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
                Integer slot = parseImm(op0);
                // sst.w 0x0, ep, rX  -> signed flag on stack slot 0
                if (slot != null && slot == 0) {
                    if (op2.equalsIgnoreCase("r0")) signed = 0;
                    if (op2.equalsIgnoreCase("r1")) signed = 1;
                }
                // Generated receive_signal callers pass the destination pointer in
                // stack argument slot +4. Capture the pointer value *here*, rather
                // than using whichever GP-relative movea happened to appear last.
                if (slot != null && slot == 4 && op2.equalsIgnoreCase("r1")) {
                    dest = r1DirectDest;
                    stackDestOffset = r1StackOffset;
                }
            }
        }
        if (signalId == null || bufOff == null || bitLen == null || startArg == null
                || signed == null) {
            return null;
        }
        boolean stackPersisted = false;
        if (dest == null && stackDestOffset != null) {
            dest = findPersistedStackDest(fn, callSite, stackDestOffset, widthFor(bitLen));
            stackPersisted = dest != null;
        }
        if (dest == null) return null;

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
        r.classification = "extracted_bitfield";
        r.classificationBasis = stackPersisted
                ? "application_com_receive_signal writes a generated stack temporary that is persisted to a uniquely recovered GP-relative RAM destination"
                : "direct application_com_receive_signal call with recoverable immediate signal/offset/width/destination arguments";
        return r;
    }

    private Long findPersistedStackDest(Function fn, long callSite, int stackOffset, int width) {
        Listing listing = currentProgram.getListing();
        InstructionIterator insts = listing.getInstructions(fn.getBody(), true);
        String loadedReg = null;
        int instructionsSinceLoad = 0;
        while (insts.hasNext()) {
            Instruction ins = insts.next();
            long ea = ins.getAddress().getOffset();
            if (ea <= callSite) continue;

            String mnem = ins.getMnemonicString().toLowerCase(Locale.ROOT);
            String op0 = (ins.getNumOperands() > 0) ? ins.getDefaultOperandRepresentation(0) : "";
            String op1 = (ins.getNumOperands() > 1) ? ins.getDefaultOperandRepresentation(1) : "";
            String op2 = (ins.getNumOperands() > 2) ? ins.getDefaultOperandRepresentation(2) : "";

            boolean matchingLoad = switch (width) {
                case 1 -> mnem.equals("ld.b") || mnem.equals("ld.bu");
                case 2 -> mnem.equals("ld.h") || mnem.equals("ld.hu");
                case 4 -> mnem.equals("ld.w");
                default -> false;
            };
            Integer loadOff = parseImm(op0);
            if (matchingLoad && loadOff != null && loadOff == stackOffset
                    && op1.equalsIgnoreCase("sp")) {
                loadedReg = op2;
                instructionsSinceLoad = 0;
                continue;
            }

            if (loadedReg == null) continue;
            instructionsSinceLoad++;
            if (instructionsSinceLoad > 8) {
                loadedReg = null;
                continue;
            }

            String expectedStore = switch (width) {
                case 1 -> "st.b";
                case 2 -> "st.h";
                case 4 -> "st.w";
                default -> "";
            };
            Integer storeOff = parseImm(op1);
            if (mnem.equals(expectedStore) && op0.equalsIgnoreCase(loadedReg)
                    && storeOff != null && op2.equalsIgnoreCase("gp")) {
                return (GP + (long) storeOff) & 0xffffffffL;
            }
        }
        return null;
    }

    private Row negativeRow(int sid, int pdu, boolean pduHasExtraction) throws Exception {
        Row r = new Row();
        r.signalId = sid;
        r.extractKind = "none";
        r.unpacker = 0;
        r.bodySize = 0;
        r.bodySha = "none";
        r.callSite = 0;
        r.bufOff = readU16(0x228e4L + 2L * pdu);
        r.bitLen = 0;
        r.startArg = 0;
        r.signed = 0;
        r.dest = "none";
        r.destWidth = 0;
        r.windowLo = SIG2PDU + 2L * sid;
        r.windowHi = r.windowLo + 2;
        if (pduHasExtraction) {
            r.classification = "configured_not_extracted_by_pdu_handler";
            r.classificationBasis = "same PDU has recovered generated extraction calls, but this configured signal ID is absent from the complete receive-signal/group-byte API census";
            r.firstConsumer = "none as configured COM signal; PDU handler extracts other signal IDs";
        } else if (isSecocPdu(pdu)) {
            r.classification = "configured_no_com_unpacker_secoc_pdu";
            r.classificationBasis = "PDU has no generated COM unpacker; its CAN ID is present in the six-record SecOC receive table";
            r.firstConsumer = "none as configured COM signal; containing PDU is consumed by SecOC path";
        } else {
            r.classification = "configured_no_com_unpacker";
            r.classificationBasis = "PDU has no recovered COM receive-signal/group-byte extraction caller";
            r.firstConsumer = "none as configured COM signal; no PDU unpacker recovered";
        }
        return r;
    }

    private boolean isSecocPdu(int pdu) throws Exception {
        if (pdu < 6 || pdu >= 53) return false;
        long canId = readU32(ACCEPTANCE + 16L * (pdu - 6)) & 0x7ffL;
        for (int i = 0; i < 6; i++) {
            if ((readU16(SECOC_RECORDS + (long)i * SECOC_RECORD_SIZE + 0x0a) & 0x7ffL) == canId) {
                return true;
            }
        }
        return false;
    }

    private long readU32(long addr) throws MemoryAccessException {
        byte[] b = new byte[4];
        currentProgram.getMemory().getBytes(toAddr(addr), b);
        return (b[0] & 0xffL) | ((b[1] & 0xffL) << 8) | ((b[2] & 0xffL) << 16) | ((b[3] & 0xffL) << 24);
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
        // application_com_receive_signal @ 0x7C03E stores by extracted width:
        // <=8 bits -> byte, 9..16 -> halfword, 17..32 -> word.
        if (bitLen <= 8) return 1;
        if (bitLen <= 16) return 2;
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
