//@author kaikozlov
//@category Analysis
// Calibration-independent discovery seeder for the SecOC acceptance-gate resolver.
//
// Fresh bare-CodeFlash imports can leave the small Gate-2 owner undiscovered as a
// function even though the bytes disassemble cleanly.  This script uses a
// cross-calibration machine-code anchor only to seed the containing function;
// ResolveSecocAcceptanceGate.java remains the authority for the semantic match.
//
// The anchor is the stable local sequence at the final verify-result predicate:
//   cmp r0,r26 ; bne <mismatch> ; jarl <verified-arm helper>,lp
// All currently retained P1M-E variants have exactly one occurrence, and the CMP
// sits 0x4c bytes after the owner entry.  We additionally require the recovered
// owner prologue bytes before creating a function.  Zero or multiple anchors fail
// closed so this script cannot silently choose among ambiguous candidates.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.mem.MemoryBlock;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class SeedSecocAcceptanceGateCandidates extends GhidraScript {
    private static final byte[] GATE_ANCHOR = new byte[] {
        (byte)0xe0, (byte)0xd1, (byte)0x9a, (byte)0x0d,
        (byte)0x1a, (byte)0x38, (byte)0xbf, (byte)0xff,
    };
    private static final byte[] OWNER_PROLOGUE = new byte[] {
        (byte)0x80, (byte)0x07, (byte)0xe1, (byte)0x30,
    };
    private static final long GATE_OFFSET_FROM_OWNER = 0x4cL;

    private boolean bytesEqual(Address address, byte[] expected) throws MemoryAccessException {
        byte[] actual = new byte[expected.length];
        if (currentProgram.getMemory().getBytes(address, actual) != expected.length) return false;
        return Arrays.equals(actual, expected);
    }

    private List<Address> findAnchors() throws MemoryAccessException {
        List<Address> hits = new ArrayList<>();
        Memory memory = currentProgram.getMemory();
        for (MemoryBlock block : memory.getBlocks()) {
            if (!block.isInitialized() || !block.isExecute()) continue;
            Address cursor = block.getStart();
            Address end = block.getEnd();
            while (cursor.compareTo(end) <= 0) {
                Address hit = memory.findBytes(cursor, end, GATE_ANCHOR, null, true, monitor);
                if (hit == null) break;
                hits.add(hit);
                cursor = hit.add(2);
            }
        }
        return hits;
    }

    @Override
    public void run() throws Exception {
        List<Address> hits = findAnchors();
        println("SECOC_GATE_SEED anchor_count=" + hits.size());
        if (hits.size() != 1) {
            throw new IllegalStateException(
                "FAIL_CLOSED expected exactly one SecOC Gate-2 machine anchor; found " + hits.size());
        }

        Address gate = hits.get(0);
        Address owner = gate.subtract(GATE_OFFSET_FROM_OWNER);
        if (!bytesEqual(owner, OWNER_PROLOGUE)) {
            throw new IllegalStateException(
                "FAIL_CLOSED Gate-2 anchor owner prologue mismatch at 0x" + owner.toString());
        }

        Listing listing = currentProgram.getListing();
        FunctionManager functions = currentProgram.getFunctionManager();
        Function containing = functions.getFunctionContaining(gate);
        if (containing != null) {
            if (!containing.getEntryPoint().equals(owner)) {
                throw new IllegalStateException(
                    "FAIL_CLOSED Gate-2 anchor belongs to unexpected function entry 0x" +
                    containing.getEntryPoint().toString());
            }
            println("SECOC_GATE_SEED existing_owner=0x" + owner.toString());
            return;
        }

        Instruction atOwner = listing.getInstructionAt(owner);
        if (atOwner == null && !disassemble(owner)) {
            throw new IllegalStateException(
                "FAIL_CLOSED unable to disassemble Gate-2 owner at 0x" + owner.toString());
        }

        Function ownerFunction = functions.getFunctionAt(owner);
        if (ownerFunction == null) ownerFunction = createFunction(owner, null);
        if (ownerFunction == null || !ownerFunction.getBody().contains(gate)) {
            throw new IllegalStateException(
                "FAIL_CLOSED unable to create Gate-2 owner containing anchor 0x" + gate.toString());
        }

        println("SECOC_GATE_SEED created_owner=0x" + owner.toString() +
                " gate=0x" + gate.toString() +
                " size=" + ownerFunction.getBody().getNumAddresses());
    }
}
