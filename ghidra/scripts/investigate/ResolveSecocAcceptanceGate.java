//@author kaikozlov
//@category Analysis
// Calibration-independent structural resolver for the SecOC authenticated-delivery gate.
//
// This script deliberately contains no known calibration patch VA and no known
// MAC-result RAM address. It searches the current RH850 program for the recovered
// machine-level data-flow shape:
//
//   byte READ(result) -> cmp 0 -> cmovne 1 (boolean := result != 0)
//     ... call state/freshness helper ...
//   cmp 0, same_boolean -> bne mismatch
//     fallthrough (result == 0): one or more calls -> forward join
//     branch target (result != 0): one or more calls -> same join
//
// The ICU-S verify-result convention is zero == verified OK and nonzero == not
// verified. That polarity is independently pinned in the analyzed firmware by the
// command-7 KAT; this Level-1 resolver therefore accepts only the local BNE shape
// where result == 0 is the fallthrough edge. The synthesized patch neutralizes the
// CMP immediately before the BNE (cmp A,B -> cmp A,A), making the BNE impossible
// while leaving its displacement and both arm bodies untouched.
//
// When RAM references are mapped, the source global must also be passed by address
// somewhere in the program, distinguishing a crypto result cell from ordinary
// status bytes. A bare CodeFlash-only import may leave the GP-relative result cell
// unmapped; the resolver retains the candidate on machine/CFG invariants and records
// that provenance gap explicitly. The script fails closed unless exactly one
// candidate survives.
//
// Usage: ResolveSecocAcceptanceGate.java [output-json]

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.RefType;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ResolveSecocAcceptanceGate extends GhidraScript {
    private static final int MAX_BOOL_TO_GATE_INSNS = 24;

    private static class Candidate {
        Function function;
        Address sourceGlobal;
        boolean sourcePassedByAddress;
        Address loadAddr;
        String loadReg;
        Address boolAddr;
        String boolReg;
        Address stateCall;
        Address gateCmpAddr;
        Address branchAddr;
        Address verifiedFallthroughAddr;
        Address mismatchBranchTarget;
        Address joinAddr;
        int verifiedCalls;
        int mismatchCalls;
        byte[] originalBytes;
        byte[] replacementBytes;
        byte[] branchBytes;
    }

    private String op(Instruction ins, int index) {
        return ins.getDefaultOperandRepresentation(index).replace(" ", "").toLowerCase();
    }

    private boolean isZero(String s) {
        return s.equals("r0") || s.equals("0x0") || s.equals("0");
    }

    private Integer registerNumber(String operand) {
        if (operand == null || !operand.matches("r(?:[12]?[0-9]|3[01])")) return null;
        return Integer.parseInt(operand.substring(1));
    }

    private Address singleMemoryReadTarget(Instruction ins) {
        Address found = null;
        for (Reference r : ins.getReferencesFrom()) {
            if (!r.getReferenceType().isRead()) continue;
            Address to = r.getToAddress();
            if (to == null || to.getAddressSpace().isRegisterSpace()) continue;
            if (found != null && !found.equals(to)) return null;
            found = to;
        }
        return found;
    }

    private boolean hasParamReference(Address target) {
        ReferenceIterator it = currentProgram.getReferenceManager().getReferencesTo(target);
        while (it.hasNext()) {
            Reference r = it.next();
            if (r.getReferenceType() == RefType.PARAM ||
                r.getReferenceType().toString().equalsIgnoreCase("PARAM")) {
                return true;
            }
        }
        return false;
    }

    private Address flowTarget(Instruction ins) {
        Address[] flows = ins.getFlows();
        if (flows == null || flows.length != 1) return null;
        return flows[0];
    }

    private boolean isCall(Instruction ins) {
        return ins.getFlowType().isCall();
    }

    private boolean isUnconditionalJump(Instruction ins) {
        return ins.getFlowType().isJump() && !ins.getFlowType().isConditional();
    }

    private int countCalls(Address start, Address endExclusive, Function fn) {
        int count = 0;
        Instruction ins = getInstructionAt(start);
        while (ins != null && fn.getBody().contains(ins.getAddress()) &&
               ins.getAddress().compareTo(endExclusive) < 0) {
            if (isCall(ins)) count++;
            ins = ins.getNext();
        }
        return count;
    }

    private Address findFallthroughJoin(Address fallthrough, Address branchTarget, Function fn) {
        Instruction ins = getInstructionAt(fallthrough);
        while (ins != null && fn.getBody().contains(ins.getAddress()) &&
               ins.getAddress().compareTo(branchTarget) < 0) {
            if (isUnconditionalJump(ins)) {
                Address target = flowTarget(ins);
                if (target != null && target.compareTo(branchTarget) > 0 && fn.getBody().contains(target)) {
                    return target;
                }
            }
            ins = ins.getNext();
        }
        return null;
    }

    /**
     * RH850 Format-II two-register instructions encode operand 0 in bits [4:0]
     * and operand 1 in bits [15:11], preserving the six opcode bits [10:5].
     * Verify those fields against Ghidra's decoded CMP operands before changing
     * operand 1 to operand 0. This synthesizes cmp A,A without embedding any
     * calibration-specific bytes or register number.
     */
    private byte[] neutralizeCmp(Instruction cmp) throws MemoryAccessException {
        if (!cmp.getMnemonicString().equalsIgnoreCase("cmp") || cmp.getNumOperands() != 2) return null;
        String left = op(cmp, 0), right = op(cmp, 1);
        Integer leftReg = registerNumber(left), rightReg = registerNumber(right);
        if (leftReg == null || rightReg == null) return null;
        byte[] original = cmp.getBytes();
        if (original.length != 2) return null;

        int halfword = (original[0] & 0xff) | ((original[1] & 0xff) << 8);
        int encodedLeft = halfword & 0x1f;
        int encodedRight = (halfword >>> 11) & 0x1f;
        if (encodedLeft != leftReg || encodedRight != rightReg) return null;

        int replacementHalfword = (halfword & 0x07ff) | (leftReg << 11);
        byte[] replacement = new byte[] {
            (byte)(replacementHalfword & 0xff),
            (byte)((replacementHalfword >>> 8) & 0xff),
        };
        if (replacement[0] == original[0] && replacement[1] == original[1]) return null;
        return replacement;
    }

    private Candidate matchAt(Instruction load, Function fn) throws Exception {
        if (!load.getMnemonicString().equalsIgnoreCase("ld.bu")) return null;
        if (load.getNumOperands() < 2) return null;

        Address sourceGlobal = singleMemoryReadTarget(load);
        boolean sourcePassedByAddress = sourceGlobal != null && hasParamReference(sourceGlobal);
        if (sourceGlobal != null && !sourcePassedByAddress) return null;

        String loadReg = op(load, load.getNumOperands() - 1);
        Instruction cmp1 = load.getNext();
        if (cmp1 == null || !fn.getBody().contains(cmp1.getAddress()) ||
            !cmp1.getMnemonicString().equalsIgnoreCase("cmp") || cmp1.getNumOperands() != 2) return null;
        String c10 = op(cmp1, 0), c11 = op(cmp1, 1);
        if (!((isZero(c10) && c11.equals(loadReg)) || (isZero(c11) && c10.equals(loadReg)))) return null;

        Instruction boolize = cmp1.getNext();
        if (boolize == null || !fn.getBody().contains(boolize.getAddress()) ||
            !boolize.getMnemonicString().equalsIgnoreCase("cmovne") || boolize.getNumOperands() != 3) return null;
        String b0 = op(boolize, 0), b1 = op(boolize, 1), boolReg = op(boolize, 2);
        if (!(b0.equals("0x1") || b0.equals("1")) || !b1.equals(loadReg)) return null;

        Instruction cursor = boolize.getNext();
        Address lastCall = null;
        for (int n = 0; cursor != null && n < MAX_BOOL_TO_GATE_INSNS; n++, cursor = cursor.getNext()) {
            if (!fn.getBody().contains(cursor.getAddress())) break;
            if (isCall(cursor)) lastCall = cursor.getAddress();
            if (!cursor.getMnemonicString().equalsIgnoreCase("cmp") || cursor.getNumOperands() != 2) continue;

            String c0 = op(cursor, 0), c1 = op(cursor, 1);
            if (!((isZero(c0) && c1.equals(boolReg)) || (isZero(c1) && c0.equals(boolReg)))) continue;
            if (lastCall == null) continue;

            // Fail closed unless nonzero(result) takes the branch and zero(result)
            // falls through. Other compiler polarities require a different patch
            // synthesis and must not be guessed by this Level-1 resolver.
            Instruction branch = cursor.getNext();
            if (branch == null || !fn.getBody().contains(branch.getAddress()) ||
                !branch.getMnemonicString().equalsIgnoreCase("bne")) continue;
            Address mismatchTarget = flowTarget(branch);
            if (mismatchTarget == null || mismatchTarget.compareTo(branch.getAddress()) <= 0 ||
                !fn.getBody().contains(mismatchTarget)) continue;

            Instruction fall = branch.getNext();
            if (fall == null) continue;
            Address join = findFallthroughJoin(fall.getAddress(), mismatchTarget, fn);
            if (join == null || join.compareTo(mismatchTarget) <= 0) continue;

            int verifiedCalls = countCalls(fall.getAddress(), mismatchTarget, fn);
            int mismatchCalls = countCalls(mismatchTarget, join, fn);
            if (verifiedCalls < 1 || mismatchCalls < 1) continue;

            byte[] replacement = neutralizeCmp(cursor);
            if (replacement == null) continue;

            Candidate c = new Candidate();
            c.function = fn;
            c.sourceGlobal = sourceGlobal;
            c.sourcePassedByAddress = sourcePassedByAddress;
            c.loadAddr = load.getAddress();
            c.loadReg = loadReg;
            c.boolAddr = boolize.getAddress();
            c.boolReg = boolReg;
            c.stateCall = lastCall;
            c.gateCmpAddr = cursor.getAddress();
            c.branchAddr = branch.getAddress();
            c.verifiedFallthroughAddr = fall.getAddress();
            c.mismatchBranchTarget = mismatchTarget;
            c.joinAddr = join;
            c.verifiedCalls = verifiedCalls;
            c.mismatchCalls = mismatchCalls;
            c.originalBytes = cursor.getBytes();
            c.replacementBytes = replacement;
            c.branchBytes = branch.getBytes();
            return c;
        }
        return null;
    }

    private String hexBytes(byte[] data) {
        StringBuilder sb = new StringBuilder();
        for (byte b : data) sb.append(String.format("%02x", b & 0xff));
        return sb.toString();
    }

    private String jesc(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private String json(Candidate c, int count) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        sb.append("  \"schema\": \"toyota-secoc-semantic-target-v2\",\n");
        sb.append("  \"candidate_count\": ").append(count).append(",\n");
        sb.append("  \"resolution\": \"unique\",\n");
        sb.append("  \"program_sha256\": \"").append(currentProgram.getExecutableSHA256()).append("\",\n");
        sb.append("  \"verify_result_polarity\": \"zero-is-verified-ok-nonzero-is-not-verified\",\n");
        sb.append("  \"function\": {\"name\": \"").append(jesc(c.function.getName())).append("\", \"entry\": \"0x")
          .append(c.function.getEntryPoint().toString()).append("\"},\n");
        sb.append("  \"mac_result_source\": {");
        if (c.sourceGlobal == null) {
            sb.append("\"address\": null, \"resolution\": \"unmapped-on-current-import\", ");
        } else {
            sb.append("\"address\": \"0x").append(c.sourceGlobal.toString()).append("\", \"resolution\": \"mapped\", ");
        }
        sb.append("\"load_site\": \"0x").append(c.loadAddr.toString())
          .append("\", \"passed_by_address_elsewhere\": ").append(c.sourcePassedByAddress).append("},\n");
        sb.append("  \"boolean_materialization\": {\"site\": \"0x").append(c.boolAddr.toString())
          .append("\", \"register\": \"").append(jesc(c.boolReg)).append("\", \"meaning\": \"verify-result-nonzero\"},\n");
        sb.append("  \"pre_gate_state_call\": \"0x").append(c.stateCall.toString()).append("\",\n");
        sb.append("  \"patch\": {\"address\": \"0x").append(c.gateCmpAddr.toString())
          .append("\", \"original\": \"").append(hexBytes(c.originalBytes))
          .append("\", \"replacement\": \"").append(hexBytes(c.replacementBytes))
          .append("\", \"operation\": \"cmp-second-register-to-first-force-fallthrough\"},\n");
        sb.append("  \"control_flow\": {\"gate_cmp\": \"0x").append(c.gateCmpAddr.toString())
          .append("\", \"bne\": \"0x").append(c.branchAddr.toString())
          .append("\", \"bne_bytes\": \"").append(hexBytes(c.branchBytes))
          .append("\", \"verified_delivery_fallthrough\": \"0x").append(c.verifiedFallthroughAddr.toString())
          .append("\", \"mismatch_branch_target\": \"0x").append(c.mismatchBranchTarget.toString())
          .append("\", \"join\": \"0x").append(c.joinAddr.toString())
          .append("\", \"verified_fallthrough_calls\": ").append(c.verifiedCalls)
          .append(", \"mismatch_branch_calls\": ").append(c.mismatchCalls).append("},\n");
        sb.append("  \"invariants\": [\n");
        if (c.sourcePassedByAddress) {
            sb.append("    \"mapped-byte-result-global-is-also-passed-by-address\",\n");
        } else {
            sb.append("    \"byte-result-load-structurally-resolved-global-unmapped\",\n");
        }
        sb.append("    \"zero-test-and-cmovne-materialize-result-nonzero-boolean\",\n");
        sb.append("    \"same-boolean-survives-through-pre-gate-call\",\n");
        sb.append("    \"bne-taken-means-result-nonzero-fallthrough-means-result-zero\",\n");
        sb.append("    \"verified-and-mismatch-arms-both-call-and-converge\",\n");
        sb.append("    \"patch-neutralizes-cmp-registers-and-preserves-bne\"\n");
        sb.append("  ]\n");
        sb.append("}\n");
        return sb.toString();
    }

    private void writeFile(String path, String text) throws IOException {
        File f = new File(path);
        File parent = f.getParentFile();
        if (parent != null) parent.mkdirs();
        try (FileWriter w = new FileWriter(f)) { w.write(text); }
    }

    @Override
    public void run() throws Exception {
        List<Candidate> candidates = new ArrayList<>();
        FunctionIterator funcs = currentProgram.getFunctionManager().getFunctions(true);
        while (funcs.hasNext()) {
            Function fn = funcs.next();
            if (fn.isThunk()) continue;
            InstructionIterator it = currentProgram.getListing().getInstructions(fn.getBody(), true);
            while (it.hasNext()) {
                Instruction ins = it.next();
                Candidate c = matchAt(ins, fn);
                if (c != null) candidates.add(c);
            }
        }

        println("SECOC_GATE_RESOLVER candidate_count=" + candidates.size());
        for (Candidate c : candidates) {
            println(String.format(
                "CANDIDATE function=%s entry=%s result=%s load=%s bool=%s state_call=%s cmp=%s original=%s replacement=%s bne=%s bne_bytes=%s verified_fallthrough=%s mismatch_target=%s join=%s verified_calls=%d mismatch_calls=%d",
                c.function.getName(), c.function.getEntryPoint(),
                c.sourceGlobal == null ? "<unmapped>" : c.sourceGlobal.toString(), c.loadAddr,
                c.boolAddr, c.stateCall, c.gateCmpAddr, hexBytes(c.originalBytes),
                hexBytes(c.replacementBytes), c.branchAddr, hexBytes(c.branchBytes),
                c.verifiedFallthroughAddr, c.mismatchBranchTarget, c.joinAddr,
                c.verifiedCalls, c.mismatchCalls));
        }

        if (candidates.size() != 1) {
            printerr("FAIL_CLOSED expected exactly one semantic acceptance-gate candidate; found " + candidates.size());
            return;
        }

        String result = json(candidates.get(0), candidates.size());
        println("RESOLUTION_JSON_BEGIN");
        println(result.trim());
        println("RESOLUTION_JSON_END");

        String[] args = getScriptArgs();
        if (args.length >= 1 && !args[0].isBlank()) {
            writeFile(args[0], result);
            println("WROTE " + args[0]);
        }
    }
}
