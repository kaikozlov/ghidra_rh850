//@author kaikozlov
//@category Analysis
// Persist function entries reached through firmware-proven indirect dispatches.
// Names are deliberately structural: the seed proves graph membership, not
// OEM-level behavior.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Set;

public class SeedDispatchProvenFunctionTables extends GhidraScript {
    private static final class Table {
        final String id;
        final long base;
        final int count;
        final int stride;
        final int[] pointerOffsets;
        final String sha256;
        final long dispatcher;
        final long indirectCall;

        Table(String id, long base, int count, int stride, int[] pointerOffsets,
                String sha256, long dispatcher, long indirectCall) {
            this.id = id;
            this.base = base;
            this.count = count;
            this.stride = stride;
            this.pointerOffsets = pointerOffsets;
            this.sha256 = sha256;
            this.dispatcher = dispatcher;
            this.indirectCall = indirectCall;
        }
    }

    private static final Table[] TABLES = {
        new Table("application_command", 0x22c30L, 18, 4, new int[] {0},
            "0d5982c30c111f079745d833d32c019b790d41ef3c7aa255deb916f5d1a93ab2",
            0x810eaL, 0x8114cL),
        new Table("application_wdbi_precondition", 0x25804L, 19, 12, new int[] {4},
            "bb72da6fb416c6fc47cb87cf2c060bb99f6bdb95499254bfbbfe960f1ccc979c",
            0x8d472L, 0x8d4b0L),
        new Table("application_wdbi_action", 0x25804L, 19, 12, new int[] {8},
            "bb72da6fb416c6fc47cb87cf2c060bb99f6bdb95499254bfbbfe960f1ccc979c",
            0x8d4ccL, 0x8d50aL),
        new Table("application_operation", 0x28098L, 10, 16, new int[] {8, 12},
            "2a24560a040e67c0ae2e7a7cc09a7b5eecbeeb7b13002e9c8aeea2df3aeb0eea",
            0x348b4L, 0x34914L),
        new Table("packet_high_selector", 0x26cccL, 8, 4, new int[] {0},
            "620b661f727c8aeb0b5bd3248c23428dfc0da74f3a8f5bed9c750bf16884282b",
            0x96c30L, 0x96caaL),
        new Table("packet_low_selector", 0x26cecL, 45, 4, new int[] {0},
            "86f5706aae7c22343992c59dacc54a349f82178dbf90e511b2b14eeb9d585ed7",
            0x96c30L, 0x96caaL),
        new Table("timer_expiry", 0x26da0L, 9, 4, new int[] {0},
            "95aea80c4a784c8b0fef996421474a4e4fb0df00c0c99e4a3032f47b698e392b",
            0x96dceL, 0x96e16L),
        new Table("record_operation", 0x26218L, 6, 28, new int[] {0},
            "c135d4aa2b912fbd2200569d10bbc9b4288bb0a1a749d2a26f4f459bd5df7c76",
            0x92810L, 0x92850L),
    };

    @Override
    public void run() throws Exception {
        Set<Long> seenTargets = new HashSet<>();
        int created = 0;
        int existing = 0;
        int references = 0;

        for (Table table : TABLES) {
            requireRegionHash(table);
            requireDispatcher(table);
            ensureLabel(table.base, table.id + "_table");
            for (int index = 0; index < table.count; index++) {
                for (int field = 0; field < table.pointerOffsets.length; field++) {
                    long pointerOffset = table.base + (long) index * table.stride
                        + table.pointerOffsets[field];
                    Address pointer = toAddr(pointerOffset);
                    long targetOffset = currentProgram.getMemory().getInt(pointer) & 0xffffffffL;
                    if (targetOffset == 0) continue;
                    if ((targetOffset & 1L) != 0 || targetOffset > 0xfffffL) {
                        throw new IllegalStateException(String.format(
                            "%s slot %d field %d has non-CodeFlash pointer 0x%x",
                            table.id, index, field, targetOffset));
                    }
                    Address target = toAddr(targetOffset);
                    Function containing = getFunctionContaining(target);
                    if (containing != null && !containing.getEntryPoint().equals(target)) {
                        throw new IllegalStateException(String.format(
                            "%s slot %d target 0x%x is alternate entry into %s @ %s",
                            table.id, index, targetOffset, containing.getName(),
                            containing.getEntryPoint()));
                    }

                    String role = table.pointerOffsets.length == 1 ? "callback"
                        : (field == 0 ? "start" : "completion");
                    String name = String.format("%s_%02d_%s",
                        table.id, index, role);
                    Function function = getFunctionAt(target);
                    if (function == null) {
                        clearValidatedEntryData(target);
                        if (getInstructionAt(target) == null && !disassemble(target)) {
                            throw new IllegalStateException("failed to disassemble " + target);
                        }
                        Instruction first = getInstructionAt(target);
                        if (first == null || !first.getAddress().equals(target)) {
                            throw new IllegalStateException(String.format(
                                "%s slot %d target 0x%x is not an instruction boundary",
                                table.id, index, targetOffset));
                        }
                        function = createFunction(target, name);
                        if (function == null) {
                            throw new IllegalStateException("failed to create function " + target);
                        }
                        created++;
                    } else {
                        existing++;
                    }
                    if (seenTargets.add(targetOffset)
                            && !"__stdcall".equals(function.getCallingConventionName())) {
                        function.setCallingConvention("__stdcall");
                    }
                    addUserDataReference(pointer, target);
                    ensureLabel(pointerOffset, name + "_ptr");
                    references++;
                }
            }
        }
        println(String.format(
            "SeedDispatchProvenFunctionTables: tables=%d created=%d existing=%d refs=%d unique_targets=%d",
            TABLES.length, created, existing, references, seenTargets.size()));
    }

    private void requireDispatcher(Table table) {
        if (getFunctionAt(toAddr(table.dispatcher)) == null) {
            throw new IllegalStateException(String.format(
                "%s missing dispatcher function 0x%x", table.id, table.dispatcher));
        }
        Instruction call = getInstructionAt(toAddr(table.indirectCall));
        if (call == null || !"jarl".equals(call.getMnemonicString())
                || !call.getFlowType().isCall() || !call.getFlowType().isComputed()) {
            throw new IllegalStateException(String.format(
                "%s missing computed jarl at 0x%x", table.id, table.indirectCall));
        }
    }

    private void requireRegionHash(Table table) throws Exception {
        int size = table.count * table.stride;
        byte[] bytes = new byte[size];
        currentProgram.getMemory().getBytes(toAddr(table.base), bytes);
        StringBuilder actual = new StringBuilder();
        for (byte value : MessageDigest.getInstance("SHA-256").digest(bytes)) {
            actual.append(String.format("%02x", value & 0xff));
        }
        if (!table.sha256.equals(actual.toString())) {
            throw new IllegalStateException(String.format(
                "%s table hash=%s expected=%s",
                table.id, actual, table.sha256));
        }
    }

    private void clearValidatedEntryData(Address target) throws Exception {
        Data data = getDataContaining(target);
        if (data == null || !data.isDefined()) return;
        if (!data.getMinAddress().equals(target) || data.getLength() > 8) {
            throw new IllegalStateException(String.format(
                "refusing to clear non-entry data %s..%s for %s",
                data.getMinAddress(), data.getMaxAddress(), target));
        }
        clearListing(data.getMinAddress(), data.getMaxAddress());
    }

    private void addUserDataReference(Address from, Address to) {
        for (var reference : currentProgram.getReferenceManager().getReferencesFrom(from)) {
            if (reference.getToAddress().equals(to)
                    && reference.getReferenceType().isData()) {
                currentProgram.getReferenceManager().delete(reference);
            }
        }
        currentProgram.getReferenceManager().addMemoryReference(
            from, to, RefType.DATA, SourceType.USER_DEFINED, 0);
    }

    private void ensureLabel(long address, String name) throws Exception {
        for (Symbol symbol : currentProgram.getSymbolTable().getSymbols(toAddr(address))) {
            if (name.equals(symbol.getName())) return;
        }
        currentProgram.getSymbolTable().createLabel(toAddr(address), name, SourceType.USER_DEFINED);
    }
}
