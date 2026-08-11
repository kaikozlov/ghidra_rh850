//@author kaikozlov
//@category Verification
// Read-only whole-CodeFlash audit of decoded instructions, direct flow targets,
// aligned pointer targets, and explicitly validated callback tables outside the
// current FunctionManager.  This script never creates code, functions, data, or
// references.  Undefined pointer targets are decoded with PseudoDisassembler.
import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.lang.InsufficientBytesException;
import ghidra.program.model.lang.UnknownContextException;
import ghidra.program.model.lang.UnknownInstructionException;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

public class ExportOutsideFunctionCandidates extends GhidraScript {
    private static final long CODEFLASH_START = 0x00000000L;
    private static final long CODEFLASH_END = 0x000fffffL;
    private static final int MAX_PSEUDO_INSTRUCTIONS = 1024;
    private static final long MAX_PSEUDO_SPAN = 0x10000L;

    private static final long DISPATCH_2B3F0 = 0x97160L;
    private static final long TABLE_2B3F0 = 0x2b3f0L;
    private static final int[] SELECTORS_2B3F0 = {
        0xfb, 0xfa, 0xf5, 0xf3, 0xeb, 0xea, 0xe4,
    };
    private static final long[] TARGETS_2B3F0 = {
        0x9729aL, 0x972faL, 0x97432L, 0x97546L,
        0x975eeL, 0x97668L, 0x976f4L,
    };

    private static final String HEADER = String.join(",",
        "target_addr",
        "decoded_instruction_count",
        "decoded_byte_count",
        "run_start",
        "run_end",
        "incoming_call_refs",
        "incoming_data_refs",
        "incoming_computed_refs",
        "source_pointer_addrs",
        "source_function_entries",
        "starts_at_instruction_boundary",
        "starts_with_prepare",
        "contains_dispose",
        "terminating_flow_count",
        "overlaps_defined_data",
        "overlaps_existing_function",
        "candidate_class",
        "adjudication_state");

    private static final class Candidate {
        final long target;
        int incomingCallRefs;
        int incomingDataRefs;
        int incomingComputedRefs;
        final Set<Long> sourcePointers = new TreeSet<>();
        final Set<Long> sourceFunctions = new TreeSet<>();
        boolean dispatchProven;
        boolean listingDecoded;
        CodeFacts facts;

        Candidate(long target) {
            this.target = target;
        }
    }

    private static final class CodeFacts {
        int instructionCount;
        long byteCount;
        long runStart;
        long runEnd;
        boolean instructionBoundary;
        boolean startsWithPrepare;
        boolean containsDispose;
        int terminatingFlowCount;
        boolean overlapsDefinedData;
        boolean overlapsExistingFunction;
    }

    private FunctionManager functions;
    private Listing listing;
    private Memory memory;
    private ReferenceManager references;
    private PseudoDisassembler pseudo;
    private AddressSetView codeFlash;
    private final Map<Long, Candidate> candidates = new HashMap<>();

    @Override
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length != 1) {
            throw new IllegalArgumentException("expected absolute CSV output path");
        }
        Path output = Path.of(args[0]);
        if (!output.isAbsolute()) {
            throw new IllegalArgumentException("CSV output path must be absolute: " + output);
        }
        if (output.getParent() != null) {
            Files.createDirectories(output.getParent());
        }

        functions = currentProgram.getFunctionManager();
        listing = currentProgram.getListing();
        memory = currentProgram.getMemory();
        references = currentProgram.getReferenceManager();
        pseudo = new PseudoDisassembler(currentProgram);
        pseudo.setRespectExecuteFlag(true);
        pseudo.setMaxInstructions(MAX_PSEUDO_INSTRUCTIONS);
        codeFlash = new AddressSet(toAddr(CODEFLASH_START), toAddr(CODEFLASH_END));

        collectListingFlowTargets();
        collectReferenceTargets();
        collectAlignedPointerTargets();
        collectDecodedOrphanRuns();
        collectValidatedDispatch2B3F0();

        List<Candidate> rows = new ArrayList<>();
        for (Candidate candidate : candidates.values()) {
            if (!isOutsideFunctions(candidate.target)) {
                continue;
            }
            candidate.facts = decodeCandidate(candidate.target);
            if (candidate.facts.instructionCount == 0) {
                continue;
            }
            rows.add(candidate);
        }
        rows.sort(Comparator.comparingLong(row -> row.target));

        try (PrintWriter out = new PrintWriter(Files.newBufferedWriter(output))) {
            out.println(HEADER);
            for (Candidate row : rows) {
                CodeFacts facts = row.facts;
                out.printf(
                    "%s,%d,%d,%s,%s,%d,%d,%d,%s,%s,%s,%s,%s,%d,%s,%s,%s,unresolved%n",
                    addr(row.target),
                    facts.instructionCount,
                    facts.byteCount,
                    addr(facts.runStart),
                    addr(facts.runEnd),
                    row.incomingCallRefs,
                    row.incomingDataRefs,
                    row.incomingComputedRefs,
                    joinAddresses(row.sourcePointers),
                    joinAddresses(row.sourceFunctions),
                    bool(facts.instructionBoundary),
                    bool(facts.startsWithPrepare),
                    bool(facts.containsDispose),
                    facts.terminatingFlowCount,
                    bool(facts.overlapsDefinedData),
                    bool(facts.overlapsExistingFunction),
                    candidateClass(row));
            }
        }

        println(String.format(
            "ExportOutsideFunctionCandidates: wrote %d candidates to %s",
            rows.size(), output));
    }

    private Candidate candidate(long target) {
        return candidates.computeIfAbsent(target, Candidate::new);
    }

    private boolean inCodeFlash(Address address) {
        return address != null && address.getAddressSpace().equals(toAddr(0).getAddressSpace())
            && address.getOffset() >= CODEFLASH_START && address.getOffset() <= CODEFLASH_END;
    }

    private boolean isOutsideFunctions(long target) {
        Address address = toAddr(target);
        return inCodeFlash(address) && functions.getFunctionContaining(address) == null;
    }

    private void addSourceFunction(Candidate candidate, Address source) {
        if (source == null) return;
        Function function = functions.getFunctionContaining(source);
        if (function != null) {
            candidate.sourceFunctions.add(function.getEntryPoint().getOffset());
        }
    }

    private void collectListingFlowTargets() throws Exception {
        InstructionIterator iterator = listing.getInstructions(codeFlash, true);
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = iterator.next();
            for (Address target : instruction.getFlows()) {
                if (!inCodeFlash(target) || !isOutsideFunctions(target.getOffset())) continue;
                Candidate candidate = candidate(target.getOffset());
                if (instruction.getFlowType().isCall() && !instruction.getFlowType().isComputed()) {
                    candidate.incomingCallRefs++;
                } else if (instruction.getFlowType().isComputed()) {
                    candidate.incomingComputedRefs++;
                }
                addSourceFunction(candidate, instruction.getAddress());
            }
        }
    }

    private void collectReferenceTargets() throws Exception {
        var sources = references.getReferenceSourceIterator(codeFlash, true);
        while (sources.hasNext()) {
            monitor.checkCancelled();
            Address source = sources.next();
            for (Reference reference : references.getReferencesFrom(source)) {
                Address target = reference.getToAddress();
                if (!inCodeFlash(target) || !isOutsideFunctions(target.getOffset())) continue;
                if (!reference.getReferenceType().isData() && !reference.getReferenceType().isCall()) {
                    continue;
                }
                if (reference.getReferenceType().isData()
                        && !credibleDataReferencedTarget(target)) {
                    continue;
                }
                Candidate candidate = candidate(target.getOffset());
                if (reference.getReferenceType().isCall()) {
                    candidate.incomingCallRefs++;
                } else {
                    candidate.incomingDataRefs++;
                }
                addSourceFunction(candidate, source);
            }
        }
    }

    private boolean credibleDataReferencedTarget(Address target) {
        if (listing.getInstructionAt(target) != null) return true;
        PseudoInstruction first = pseudoAt(target);
        if (first == null || !"prepare".equals(first.getMnemonicString())) return false;
        return pseudo.checkValidSubroutine(target, true, false, true)
            && pseudo.getLastCheckValidInstructionCount() >= 2;
    }

    private void collectAlignedPointerTargets() throws Exception {
        for (long sourceOffset = CODEFLASH_START; sourceOffset <= CODEFLASH_END - 3; sourceOffset += 4) {
            if ((sourceOffset & 0x3fffL) == 0) monitor.checkCancelled();
            Address source = toAddr(sourceOffset);
            if (listing.getInstructionContaining(source) != null
                    || functions.getFunctionContaining(source) != null) {
                continue;
            }
            long target = memory.getInt(source) & 0xffffffffL;
            if ((target & 1L) != 0 || target < CODEFLASH_START || target > CODEFLASH_END
                    || !isOutsideFunctions(target)) {
                continue;
            }
            PseudoInstruction first = pseudoAt(toAddr(target));
            // An aligned word that happens to point into CodeFlash is only a
            // pointer-shaped value.  Retain raw-scan candidates when the target
            // also has the compiler prologue shape and PseudoDisassembler can
            // follow a bounded subroutine.  This is candidate evidence only;
            // it never upgrades a row to dispatch-proven or seeds a function.
            if (first == null || !"prepare".equals(first.getMnemonicString())) continue;
            if (!pseudo.checkValidSubroutine(toAddr(target), true, false, true)
                    || pseudo.getLastCheckValidInstructionCount() < 2) {
                continue;
            }
            Candidate candidate = candidate(target);
            if (candidate.sourcePointers.add(sourceOffset)) {
                candidate.incomingDataRefs++;
            }
            for (Reference reference : references.getReferencesTo(source)) {
                addSourceFunction(candidate, reference.getFromAddress());
            }
        }
    }

    private void collectDecodedOrphanRuns() throws Exception {
        InstructionIterator iterator = listing.getInstructions(codeFlash, true);
        Address previousEnd = null;
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = iterator.next();
            if (functions.getFunctionContaining(instruction.getAddress()) != null) {
                previousEnd = instruction.getMaxAddress();
                continue;
            }
            boolean beginsRun = previousEnd == null
                || !previousEnd.next().equals(instruction.getAddress())
                || functions.getFunctionContaining(previousEnd) != null;
            if (beginsRun) {
                Candidate candidate = candidate(instruction.getAddress().getOffset());
                candidate.listingDecoded = true;
            }
            previousEnd = instruction.getMaxAddress();
        }
    }

    private void collectValidatedDispatch2B3F0() throws Exception {
        requireBytes(0x9718cL, "01f0c3f225960c75d2f16090f2998a0d02ed");
        requireBytes(0x9719eL, "1b301a38fdc760f901eac505410a670af6ed");
        Function dispatcher = functions.getFunctionAt(toAddr(DISPATCH_2B3F0));
        if (dispatcher == null) {
            throw new IllegalStateException("missing validated dispatcher function 0x97160");
        }
        Instruction indirect = listing.getInstructionAt(toAddr(0x971a2L));
        if (indirect == null || !"jarl".equals(indirect.getMnemonicString())
                || !indirect.getFlowType().isCall() || !indirect.getFlowType().isComputed()) {
            throw new IllegalStateException("0x971a2 is not the expected computed jarl");
        }

        for (int index = 0; index < TARGETS_2B3F0.length; index++) {
            Address record = toAddr(TABLE_2B3F0 + index * 8L);
            int selector = memory.getByte(record) & 0xff;
            if (selector != SELECTORS_2B3F0[index]
                    || memory.getByte(record.add(1)) != 0
                    || memory.getByte(record.add(2)) != 0
                    || memory.getByte(record.add(3)) != 0) {
                throw new IllegalStateException(String.format(
                    "unexpected selector record %d at 0x%x", index, record.getOffset()));
            }
            long target = memory.getInt(record.add(4)) & 0xffffffffL;
            if (target != TARGETS_2B3F0[index]) {
                throw new IllegalStateException(String.format(
                    "unexpected target 0x%x in record %d", target, index));
            }
            if (!isOutsideFunctions(target)) continue;
            Candidate candidate = candidate(target);
            candidate.dispatchProven = true;
            candidate.incomingComputedRefs++;
            if (candidate.sourcePointers.add(record.add(4).getOffset())) {
                candidate.incomingDataRefs++;
            }
            candidate.sourceFunctions.add(DISPATCH_2B3F0);
        }
    }

    private void requireBytes(long address, String expectedHex) throws Exception {
        byte[] expected = new byte[expectedHex.length() / 2];
        for (int i = 0; i < expected.length; i++) {
            expected[i] = (byte) Integer.parseInt(expectedHex.substring(i * 2, i * 2 + 2), 16);
        }
        byte[] actual = new byte[expected.length];
        memory.getBytes(toAddr(address), actual);
        for (int i = 0; i < expected.length; i++) {
            if (actual[i] != expected[i]) {
                throw new IllegalStateException(String.format(
                    "byte mismatch at 0x%x", address + i));
            }
        }
    }

    private PseudoInstruction pseudoAt(Address address) {
        try {
            return pseudo.disassemble(address);
        } catch (InsufficientBytesException | UnknownInstructionException
                | UnknownContextException exception) {
            return null;
        }
    }

    private CodeFacts decodeCandidate(long target) throws Exception {
        CodeFacts facts = new CodeFacts();
        facts.runStart = target;
        facts.runEnd = target;
        Address targetAddress = toAddr(target);
        Instruction containing = listing.getInstructionContaining(targetAddress);
        facts.instructionBoundary = (containing == null && (target & 1L) == 0)
            || (containing != null && containing.getAddress().equals(targetAddress));

        ArrayDeque<Address> pending = new ArrayDeque<>();
        Set<Long> visited = new HashSet<>();
        AddressSet decodedBytes = new AddressSet();
        pending.add(targetAddress);

        while (!pending.isEmpty() && visited.size() < MAX_PSEUDO_INSTRUCTIONS) {
            monitor.checkCancelled();
            Address address = pending.removeFirst();
            if (!inCodeFlash(address) || visited.contains(address.getOffset())) continue;
            if (functions.getFunctionContaining(address) != null) {
                facts.overlapsExistingFunction = true;
                continue;
            }
            PseudoInstruction instruction = pseudoAt(address);
            if (instruction == null) continue;
            visited.add(address.getOffset());
            decodedBytes.add(instruction.getMinAddress(), instruction.getMaxAddress());

            if (facts.instructionCount == 0) {
                facts.startsWithPrepare = "prepare".equals(instruction.getMnemonicString());
            }
            facts.instructionCount++;
            facts.runStart = Math.min(facts.runStart, instruction.getMinAddress().getOffset());
            facts.runEnd = Math.max(facts.runEnd, instruction.getMaxAddress().getOffset());
            if ("dispose".equals(instruction.getMnemonicString())) {
                facts.containsDispose = true;
            }
            Data data = listing.getDataContaining(address);
            if (data != null && data.isDefined()) {
                facts.overlapsDefinedData = true;
                // Preserve the ambiguity without treating a typed data region
                // as an unbounded pseudo-CFG.
                continue;
            }

            boolean followed = false;
            if (!instruction.getFlowType().isCall()) {
                for (Address flow : instruction.getFlows()) {
                    if (inCodeFlash(flow)
                            && Math.abs(flow.getOffset() - target) <= MAX_PSEUDO_SPAN) {
                        pending.add(flow);
                        followed = true;
                    }
                }
            }
            Address fallThrough = instruction.getFallThrough();
            if (fallThrough != null && inCodeFlash(fallThrough)
                    && Math.abs(fallThrough.getOffset() - target) <= MAX_PSEUDO_SPAN) {
                pending.add(fallThrough);
                followed = true;
            }
            if (instruction.getFlowType().isTerminal()
                    || (!followed && instruction.getFlowType().isJump())) {
                facts.terminatingFlowCount++;
            }
        }
        facts.byteCount = decodedBytes.getNumAddresses();
        return facts;
    }

    private String candidateClass(Candidate candidate) {
        if (candidate.dispatchProven) return "table-callback-target";
        if (candidate.incomingCallRefs > 0) return "direct-call-target";
        if (candidate.facts.overlapsDefinedData) return "ambiguous-data";
        if (!candidate.sourcePointers.isEmpty() || candidate.incomingDataRefs > 0) {
            return "pointer-referenced-code-run";
        }
        return "orphan-decoded-run";
    }

    private static String addr(long value) {
        return String.format("0x%08x", value);
    }

    private static String bool(boolean value) {
        return value ? "true" : "false";
    }

    private static String joinAddresses(Set<Long> addresses) {
        StringBuilder result = new StringBuilder();
        for (long address : addresses) {
            if (result.length() != 0) result.append(';');
            result.append(addr(address));
        }
        return result.toString();
    }
}
