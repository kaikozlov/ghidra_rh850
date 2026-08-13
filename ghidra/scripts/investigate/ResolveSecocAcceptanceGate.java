//@author kaikozlov
//@category Analysis
// Calibration-independent structural resolver for the SecOC authenticated-delivery gate.
//
// This script deliberately contains no known Sienna patch VA and no known MAC-result
// RAM address. It searches the current RH850 program for the machine-level data-flow
// shape recovered from the acceptance gate:
//
//   byte READ(global) -> cmp 0 -> cmovne 1 (materialize boolean)
//     ... call state/freshness helper ...
//   cmp 0, same_boolean -> bne success
//     false path: one or more calls -> unconditional forward join
//     success path: one or more calls -> same join
//
// When the import has a RAM model, the source global must also be passed by address
// somewhere in the program (PARAM reference), which strongly distinguishes a crypto/
// result output cell from ordinary status bytes. On a bare CodeFlash-only import the
// GP-relative global may be unmapped; the resolver then retains the candidate on the
// machine/CFG invariants and records the missing provenance explicitly. The script
// fails closed unless exactly one candidate survives. If an output path is supplied,
// it writes a small JSON resolver result.
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
        Address branchAddr;
        Address successAddr;
        Address joinAddr;
        int falseCalls;
        int successCalls;
        byte[] originalBytes;
        byte[] replacementBytes;
    }

    private String op(Instruction ins, int index) {
        return ins.getDefaultOperandRepresentation(index).replace(" ", "").toLowerCase();
    }

    private boolean isZero(String s) {
        return s.equals("r0") || s.equals("0x0") || s.equals("0");
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

    private Address findFalsePathJoin(Address fallthrough, Address success, Function fn) {
        Instruction ins = getInstructionAt(fallthrough);
        while (ins != null && fn.getBody().contains(ins.getAddress()) &&
               ins.getAddress().compareTo(success) < 0) {
            if (isUnconditionalJump(ins)) {
                Address target = flowTarget(ins);
                if (target != null && target.compareTo(success) > 0 && fn.getBody().contains(target)) {
                    return target;
                }
            }
            ins = ins.getNext();
        }
        return null;
    }

    private byte[] unconditionalizeBne(Instruction branch) throws MemoryAccessException {
        if (!branch.getMnemonicString().equalsIgnoreCase("bne")) return null;
        byte[] original = branch.getBytes();
        if (original.length != 2) return null;
        // RH850 Bcond cc0003 lives in the low nibble of the first little-endian byte.
        // cc=0xA is NE; cc=0x5 is the unconditional BR condition. Preserve all
        // displacement/opcode bits and change only the condition nibble.
        if ((original[0] & 0x0f) != 0x0a) return null;
        byte[] replacement = original.clone();
        replacement[0] = (byte)((replacement[0] & 0xf0) | 0x05);
        return replacement;
    }

    private Candidate matchAt(Instruction load, Function fn) throws Exception {
        if (!load.getMnemonicString().equalsIgnoreCase("ld.bu")) return null;
        if (load.getNumOperands() < 2) return null;

        Address sourceGlobal = singleMemoryReadTarget(load);
        boolean sourcePassedByAddress = sourceGlobal != null && hasParamReference(sourceGlobal);
        // A bare CodeFlash import may not yet have RAM/GP-relative references mapped.
        // In that case, keep the candidate alive on machine/CFG structure alone.
        // If Ghidra *does* resolve the load to a memory cell, require the stronger
        // passed-by-address result provenance rather than accepting an ordinary
        // mapped status byte.
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

            Instruction branch = cursor.getNext();
            if (branch == null || !fn.getBody().contains(branch.getAddress()) ||
                !branch.getMnemonicString().equalsIgnoreCase("bne")) continue;
            Address success = flowTarget(branch);
            if (success == null || success.compareTo(branch.getAddress()) <= 0 || !fn.getBody().contains(success)) continue;

            Instruction fall = branch.getNext();
            if (fall == null) continue;
            Address join = findFalsePathJoin(fall.getAddress(), success, fn);
            if (join == null || join.compareTo(success) <= 0) continue;

            int falseCalls = countCalls(fall.getAddress(), success, fn);
            int successCalls = countCalls(success, join, fn);
            if (falseCalls < 1 || successCalls < 1) continue;

            byte[] replacement = unconditionalizeBne(branch);
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
            c.branchAddr = branch.getAddress();
            c.successAddr = success;
            c.joinAddr = join;
            c.falseCalls = falseCalls;
            c.successCalls = successCalls;
            c.originalBytes = branch.getBytes();
            c.replacementBytes = replacement;
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
        sb.append("  \"schema\": \"toyota-secoc-semantic-target-v1\",\n");
        sb.append("  \"candidate_count\": ").append(count).append(",\n");
        sb.append("  \"resolution\": \"unique\",\n");
        sb.append("  \"program_sha256\": \"").append(currentProgram.getExecutableSHA256()).append("\",\n");
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
          .append("\", \"register\": \"").append(jesc(c.boolReg)).append("\"},\n");
        sb.append("  \"pre_gate_state_call\": \"0x").append(c.stateCall.toString()).append("\",\n");
        sb.append("  \"patch\": {\"address\": \"0x").append(c.branchAddr.toString())
          .append("\", \"original\": \"").append(hexBytes(c.originalBytes))
          .append("\", \"replacement\": \"").append(hexBytes(c.replacementBytes))
          .append("\", \"operation\": \"bne-to-unconditional-br-preserve-target\"},\n");
        sb.append("  \"control_flow\": {\"success_target\": \"0x").append(c.successAddr.toString())
          .append("\", \"join\": \"0x").append(c.joinAddr.toString())
          .append("\", \"failure_path_calls\": ").append(c.falseCalls)
          .append(", \"success_path_calls\": ").append(c.successCalls).append("},\n");
        sb.append("  \"invariants\": [\n");
        if (c.sourcePassedByAddress) {
            sb.append("    \"mapped-byte-result-global-is-also-passed-by-address\",\n");
        } else {
            sb.append("    \"byte-result-load-structurally-resolved-global-unmapped\",\n");
        }
        sb.append("    \"zero-test-and-cmovne-materialize-boolean\",\n");
        sb.append("    \"same-boolean-survives-through-pre-gate-call\",\n");
        sb.append("    \"same-boolean-controls-forward-bne\",\n");
        sb.append("    \"failure-and-success-arms-both-call-and-converge\",\n");
        sb.append("    \"patch-only-changes-rh850-condition-nibble\"\n");
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
                "CANDIDATE function=%s entry=%s result=%s load=%s bool=%s state_call=%s branch=%s original=%s replacement=%s success=%s join=%s false_calls=%d success_calls=%d",
                c.function.getName(), c.function.getEntryPoint(),
                c.sourceGlobal == null ? "<unmapped>" : c.sourceGlobal.toString(), c.loadAddr,
                c.boolAddr, c.stateCall, c.branchAddr, hexBytes(c.originalBytes),
                hexBytes(c.replacementBytes), c.successAddr, c.joinAddr, c.falseCalls, c.successCalls));
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
