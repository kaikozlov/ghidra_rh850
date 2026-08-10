//@author kaikozlov
//@category Analysis
// Read-only semantic triage for a raw blurbdust/yc SecOC egg match.
// Usage: AnalyzeCommunityPatchTarget.java <target-va>

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.LinkedHashSet;
import java.util.Set;

public class AnalyzeCommunityPatchTarget extends GhidraScript {
    private boolean inIcusWindow(Address a) {
        long v = a.getOffset();
        return v >= 0xFFC5D000L && v <= 0xFFC5D0FFL;
    }

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            printerr("usage: AnalyzeCommunityPatchTarget.java <target-va>");
            return;
        }

        long raw = Long.decode(args[0]);
        Address target = currentProgram.getAddressFactory().getDefaultAddressSpace().getAddress(raw);
        Function fn = getFunctionContaining(target);
        println("PATCH_TARGET " + target);
        if (fn == null) {
            println("CONTAINING_FUNCTION none");
            return;
        }

        println(String.format("CONTAINING_FUNCTION %s entry=%s size=%d", fn.getName(), fn.getEntryPoint(), fn.getBody().getNumAddresses()));
        println("TARGET_IS_ENTRY " + target.equals(fn.getEntryPoint()));

        Set<String> callers = new LinkedHashSet<>();
        ReferenceIterator incoming = currentProgram.getReferenceManager().getReferencesTo(fn.getEntryPoint());
        while (incoming.hasNext()) {
            Reference r = incoming.next();
            Function caller = getFunctionContaining(r.getFromAddress());
            String callerName = caller == null ? "<no-function>" : caller.getName();
            callers.add(String.format("CALLER %s site=%s type=%s", callerName, r.getFromAddress(), r.getReferenceType()));
        }
        for (String line : callers) println(line);
        println("CALLER_COUNT " + callers.size());

        Set<String> calls = new LinkedHashSet<>();
        Set<String> icusRefs = new LinkedHashSet<>();
        InstructionIterator insns = currentProgram.getListing().getInstructions(fn.getBody(), true);
        while (insns.hasNext()) {
            Instruction ins = insns.next();
            for (Reference r : ins.getReferencesFrom()) {
                if (r.getReferenceType().isCall()) {
                    Function callee = getFunctionAt(r.getToAddress());
                    String name = callee == null ? "<no-function>" : callee.getName();
                    calls.add(String.format("CALLEE %s target=%s site=%s", name, r.getToAddress(), ins.getAddress()));
                }
                if (inIcusWindow(r.getToAddress())) {
                    icusRefs.add(String.format("ICUS_REF site=%s target=%s type=%s", ins.getAddress(), r.getToAddress(), r.getReferenceType()));
                }
            }
        }
        for (String line : calls) println(line);
        println("CALLEE_COUNT " + calls.size());
        for (String line : icusRefs) println(line);
        println("DIRECT_ICUS_REF_COUNT " + icusRefs.size());

        DecompInterface decompiler = new DecompInterface();
        decompiler.openProgram(currentProgram);
        DecompileResults result = decompiler.decompileFunction(fn, 30, monitor);
        if (result.decompileCompleted() && result.getDecompiledFunction() != null) {
            println("DECOMPILATION_BEGIN");
            println(result.getDecompiledFunction().getC());
            println("DECOMPILATION_END");
        } else {
            println("DECOMPILATION unavailable");
        }
        decompiler.dispose();

        println("SEMANTIC_RULE egg-match-is-location-only; classify from function/callers/data-flow before claiming SecOC");
    }
}
