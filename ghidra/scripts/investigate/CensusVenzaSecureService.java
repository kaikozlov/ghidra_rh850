//@author kaikozlov
//@category Analysis
// Exhaustive census of the yc Venza airbag (RH850 P1x-C family) MainPE
// secure-service boundary: the local ICUMC-style request queue reached through
// 0xBD69E -> 0x8A18A -> 0x89E60 (shared-RAM ring) and triggered at 0xFF1F0044.
//
// Intended for the disposable ad-hoc raw import of community/yc/venza/cflash.bin
// (BinaryLoader, base 0x0, v850e3). The script:
//   1. linear-sweep disassembles the meaningful CodeFlash code region,
//   2. creates functions at every direct-call target (bounded closure),
//   3. prints every reference to the secure-boundary watch addresses,
//   4. prints disassembly context around each call into the submit path plus
//      one caller level, so request-builder opcodes are directly readable,
//   5. prints every reference into the FEFF0000..FEFF0FFF request-descriptor
//      window.
//
// Read-only: performs no patching and defines no persistent labels.

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

public class CensusVenzaSecureService extends GhidraScript {
    private static final long CODE_START = 0x0L;
    private static final long CODE_END = 0x180000L; // meaningful code ends ~0x17FFFF

    private static final long[] SEED_FUNCTIONS = {
        0x8A18AL, // secure request enqueue wrapper
        0x89E60L, // shared-RAM queue / 0xFF1F0014 reader
        0x89F6EL, // 0xFF1F0044 service trigger writer
        0xBD69EL, // lower-adapter convergence
        0x864E4L, // boundary initialization
        0x86510L, // boundary initialization
    };

    private static final long[] WATCH = {
        0xFF1F0014L, // secure-service shared-RAM pointer
        0xFF1F0044L, // secure-service trigger
        0x8A18AL, // enqueue wrapper
        0xBD69EL, // adapter convergence
    };

    private static final long DESC_START = 0xFEFF0000L;
    private static final long DESC_END = 0xFEFF0FFFL;

    private String fnName(Address a) {
        Function f = getFunctionContaining(a);
        return f == null ? "None" : f.getName() + "@" + f.getEntryPoint();
    }

    private void printRefsTo(long dest) {
        ReferenceIterator it = currentProgram.getReferenceManager()
            .getReferencesTo(toAddr(dest));
        List<String> rows = new ArrayList<>();
        while (it.hasNext()) {
            Reference r = it.next();
            rows.add(String.format("REF 0x%x <- %s [%s] %s", dest,
                r.getFromAddress(), r.getReferenceType(), fnName(r.getFromAddress())));
        }
        rows.sort(String::compareTo);
        for (String row : rows) println(row);
        if (rows.isEmpty()) println(String.format("REF 0x%x <- (none)", dest));
    }

    private void printContext(Address site, int before, int after) {
        List<Instruction> window = new ArrayList<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(site, true);
        for (int i = 0; i < before && it.hasNext(); i++) {
            window.add(it.next());
        }
        List<Instruction> tail = new ArrayList<>();
        for (int i = 0; i <= after && it.hasNext(); i++) {
            tail.add(it.next());
        }
        int drop = window.size() + tail.size() - (before + after + 1);
        for (int i = 0; i < drop; i++) window.remove(0);
        for (Instruction ins : window) println("    " + ins.getAddress() + " " + ins);
        for (Instruction ins : tail) println("    " + ins.getAddress() + " " + ins);
    }

    @Override
    public void run() throws Exception {
        // 1. Seed known boundary functions before the sweep so their bodies exist.
        for (long seed : SEED_FUNCTIONS) {
            Address a = toAddr(seed);
            if (getInstructionAt(a) == null) disassemble(a);
            if (getFunctionAt(a) == null) createFunction(a, null);
        }

        // 2. Linear sweep of the meaningful code region (no flow following).
        AddressSet sweep = new AddressSet(toAddr(CODE_START), toAddr(CODE_END - 1));
        DisassembleCommand cmd = new DisassembleCommand(sweep, null, false);
        cmd.applyTo(currentProgram, monitor);
        println("SWEEP done");

        // 3. Function closure over direct call targets.
        int created = 0;
        for (int round = 0; round < 200; round++) {
            Set<Address> unique = new LinkedHashSet<>();
            var functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function source = functions.next();
                InstructionIterator it = currentProgram.getListing()
                    .getInstructions(source.getBody(), true);
                while (it.hasNext()) {
                    Instruction ins = it.next();
                    if (!ins.getFlowType().isCall()) continue;
                    for (Address target : ins.getFlows()) {
                        if (!currentProgram.getMemory().contains(target)) continue;
                        if (currentProgram.getFunctionManager().getFunctionAt(target) == null) {
                            unique.add(target);
                        }
                    }
                }
            }
            if (unique.isEmpty()) {
                println("CLOSURE created=" + created + " rounds=" + round);
                break;
            }
            for (Address target : unique) {
                if (getInstructionAt(target) == null && !disassemble(target)) continue;
                if (createFunction(target, null) != null) created++;
            }
        }

        // 4. Reference census at the boundary.
        println("== boundary references ==");
        for (long w : WATCH) printRefsTo(w);
        println("== descriptor window references FEFF0000..FEFF0FFF ==");
        TreeSet<Long> sites = new TreeSet<>();
        for (long cell = DESC_START; cell <= DESC_END; cell += 4) {
            ReferenceIterator it = currentProgram.getReferenceManager()
                .getReferencesTo(toAddr(cell));
            while (it.hasNext()) {
                sites.add(it.next().getToAddress().getOffset());
            }
        }
        for (long cell : sites) printRefsTo(cell);
        println("== call sites into 0x8A18A / 0xBD69E with context ==");
        for (long dest : new long[]{0x8A18AL, 0xBD69EL}) {
            ReferenceIterator rit = currentProgram.getReferenceManager()
                .getReferencesTo(toAddr(dest));
            while (rit.hasNext()) {
                Reference r = rit.next();
                if (!r.getReferenceType().isCall()) continue;
                Address site = r.getFromAddress();
                println("CALLSITE into " + String.format("0x%x", dest) + " at " + site
                    + " in " + fnName(site));
                printContext(site, 10, 4);
                Function caller = getFunctionContaining(site);
                if (caller != null) {
                    ReferenceIterator cit = currentProgram.getReferenceManager()
                        .getReferencesTo(caller.getEntryPoint());
                    while (cit.hasNext()) {
                        Reference cr = cit.next();
                        println("   CALLER-OF-CALLER " + cr.getFromAddress() + " ["
                            + cr.getReferenceType() + "] " + fnName(cr.getFromAddress()));
                    }
                }
            }
        }
        println("CENSUS complete");
    }
}
